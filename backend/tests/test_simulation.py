import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.db.database import SessionLocal, engine
from backend.app.db.base import Base
from backend.app.models.event import DisruptionEvent
from backend.app.models.shipment import LiveShipment, Shipment
from backend.app.models.order import Order
from backend.app.models.customer import Customer
from backend.app.models.warehouse import Warehouse
from simulation.events import EmpiricalEventSampler
from simulation.disruptions import DisruptionInjector, SCENARIO_CATALOG
from simulation.engine import SimulationEngine

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(Customer).count() == 0:
            cust = Customer(
                global_id="customer:1", first_name="John", last_name="Doe",
                segment="Consumer", country="EE. UU.", city="Caguas", state="PR",
                zipcode="00725"
            )
            db.add(cust)
            db.commit()
            db.refresh(cust)

            wh = Warehouse(
                global_id="warehouse:1", name="San Juan Warehouse", region="USCA",
                latitude=18.4655, longitude=-66.1057, capacity=50000, is_synthetic=True
            )
            db.add(wh)
            db.commit()
            db.refresh(wh)

            order = Order(
                global_id="order:1", customer_id=cust.customer_id, customer_global_id=cust.global_id,
                order_date=datetime.utcnow(), order_status="COMPLETE", market="USCA", order_region="CARIBBEAN",
                destination_country="EE. UU.", destination_city="Caguas", destination_state="PR",
                customer_latitude=18.4655, customer_longitude=-66.1057, assigned_warehouse_id=wh.warehouse_id,
                assigned_warehouse_id_is_synthetic=True, is_simulated=False
            )
            db.add(order)
            db.commit()
            db.refresh(order)

            ship = Shipment(
                global_id="shipment:1", order_id=order.order_id, order_global_id=order.global_id,
                shipping_mode="Standard Class", days_scheduled=3, days_real=3, delivery_status="Shipping on time",
                shipping_date=datetime.utcnow(), is_simulated=False
            )
            db.add(ship)
            db.commit()
    finally:
        db.close()

def test_empirical_event_sampler():
    sampler = EmpiricalEventSampler(seed=42)
    mode = sampler.sample_shipping_mode()
    assert mode in sampler.shipping_mode_probs
    is_late = sampler.sample_is_late('First Class')
    assert is_late is True
    delay_hours = sampler.sample_delay_hours('First Class')
    assert 24 <= delay_hours <= 72

def test_disruption_ground_truth_labeling():
    db = SessionLocal()
    try:
        scenario = SCENARIO_CATALOG[0]
        event = DisruptionInjector.inject_scenario(db, scenario_id=scenario["scenario_id"])
        assert event.event_id is not None
        assert event.scenario_id == scenario["scenario_id"]
        assert event.target_global_id == scenario["target_global_id"]
        assert event.acceptable_action_class == scenario["acceptable_action_class"]

        fetched = db.query(DisruptionEvent).filter(DisruptionEvent.global_id == event.global_id).first()
        assert fetched is not None
        assert fetched.event_type == "SUPPLIER_FAILURE"
        assert fetched.acceptable_action_class == "SWITCH_SUPPLIER"
    finally:
        db.close()

def test_simulation_clock_ticks():
    db = SessionLocal()
    try:
        engine_inst = SimulationEngine(seed=42)
        initial_time = engine_inst.sim_time
        snapshot = engine_inst.tick(db, hours_elapsed=2.0)
        assert engine_inst.sim_time == initial_time + timedelta(hours=2.0)
        assert snapshot["total_ticks"] == 1
        assert snapshot["live_shipments_count"] >= 1
    finally:
        db.close()

def test_seed_reproducibility():
    s1 = EmpiricalEventSampler(seed=42)
    s2 = EmpiricalEventSampler(seed=42)
    res1 = [s1.sample_shipping_mode() for _ in range(10)]
    res2 = [s2.sample_shipping_mode() for _ in range(10)]
    assert res1 == res2

def test_simulation_api_endpoints():
    response = client.get("/api/v1/simulation/scenarios")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["count"] == 6

    response = client.get("/api/v1/simulation/status")
    assert response.status_code == 200
    status_data = response.json()
    assert status_data["status"] == "success"

    control_res = client.post("/api/v1/simulation/control", json={"action": "step"})
    assert control_res.status_code == 200
    assert control_res.json()["status"] == "success"

    inject_res = client.post("/api/v1/simulation/inject", json={"scenario_id": "SCENARIO-SUP-01"})
    assert inject_res.status_code == 200
    inject_data = inject_res.json()
    assert inject_data["status"] == "success"
    assert inject_data["event"]["acceptable_action_class"] == "SWITCH_SUPPLIER"

def test_websocket_endpoint():
    with client.websocket_connect("/api/v1/simulation/ws") as websocket:
        data = websocket.receive_json()
        assert data["type"] == "telemetry"
        assert "sim_time" in data["data"]
