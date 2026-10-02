import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.db.database import SessionLocal, engine
from backend.app.db.base import Base
from backend.app.models.recommendation import AgentOutput, Recommendation
from agents.supplier_agent import supplier_agent
from agents.shipment_agent import shipment_agent
from agents.inventory_agent import inventory_agent
from agents.external_agent import external_agent
from agents.risk_agent import risk_agent
from agents.recommendation_agent import recommendation_agent
from agents.orchestrator import multi_agent_orchestrator

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)

def test_individual_agents():
    db = SessionLocal()
    try:
        sup_out = supplier_agent.run(db, "supplier:1")
        assert sup_out["agent_name"] == "SupplierAgent"
        assert "risk_score" in sup_out

        ship_out = shipment_agent.run(db, "shipment:1")
        assert ship_out["agent_name"] == "ShipmentAgent"

        inv_out = inventory_agent.run(db, "inventory:1")
        assert inv_out["agent_name"] == "InventoryAgent"

        ext_out = external_agent.run(db, "supplier:1")
        assert ext_out["agent_name"] == "ExternalIntelligenceAgent"
    finally:
        db.close()

from backend.app.models.config import AgentConfig

def test_risk_assessment_agent_weights():
    db = SessionLocal()
    try:
        sup_out = {"agent_name": "SupplierAgent", "risk_score": 80.0, "status": "SUCCESS"}
        ship_out = {"agent_name": "ShipmentAgent", "risk_score": 70.0, "status": "SUCCESS"}
        inv_out = {"agent_name": "InventoryAgent", "risk_score": 50.0, "status": "SUCCESS"}
        ext_out = {"agent_name": "ExternalIntelligenceAgent", "risk_score": 60.0, "status": "SUCCESS"}

        cfg = db.query(AgentConfig).first()
        w_sup = cfg.risk_weight_supplier if cfg else 0.30
        w_ship = cfg.risk_weight_shipment if cfg else 0.30
        w_inv = cfg.risk_weight_inventory if cfg else 0.20
        w_ext = cfg.risk_weight_external if cfg else 0.20
        expected_score = round(w_sup * 80.0 + w_ship * 70.0 + w_inv * 50.0 + w_ext * 60.0, 2)

        risk_out = risk_agent.run(
            db, "supplier:1",
            supplier_output=sup_out,
            shipment_output=ship_out,
            inventory_output=inv_out,
            external_output=ext_out
        )
        assert risk_out["agent_name"] == "RiskAssessmentAgent"
        assert risk_out["risk_score"] == expected_score
        assert risk_out["reasoning_output"]["risk_band"] in ["HIGH", "CRITICAL", "MEDIUM"]
        assert risk_out["reasoning_output"]["requires_recommendation"] is True
    finally:
        db.close()

def test_recommendation_agent_triggering():
    db = SessionLocal()
    try:
        risk_out = {
            "risk_score": 75.0,
            "reasoning_output": {"requires_recommendation": True, "risk_band": "HIGH"}
        }
        rec_out = recommendation_agent.run(db, "supplier:1", risk_out)
        assert rec_out["agent_name"] == "RecommendationAgent"
        assert rec_out["reasoning_output"]["action_type"] == "SWITCH_SUPPLIER"
        assert rec_out["reasoning_output"]["status"] == "pending"

        # Verify persisted in recommendations table
        rec_db = db.query(Recommendation).filter(Recommendation.global_id == rec_out["reasoning_output"]["recommendation_global_id"]).first()
        assert rec_db is not None
        assert rec_db.status == "pending"
    finally:
        db.close()

def test_multi_agent_orchestrator():
    db = SessionLocal()
    try:
        pipeline_res = multi_agent_orchestrator.run_pipeline(db, "supplier:1")
        assert pipeline_res["pipeline_status"] == "SUCCESS"
        assert "composite_risk_score" in pipeline_res
        assert len(pipeline_res["agent_outputs"]) == 6
    finally:
        db.close()

def test_graceful_degradation():
    db = SessionLocal()
    try:
        ext_degraded = {"agent_name": "ExternalIntelligenceAgent", "risk_score": 50.0, "status": "DEGRADED", "stale": True}
        sup_out = {"agent_name": "SupplierAgent", "risk_score": 40.0, "status": "SUCCESS"}
        ship_out = {"agent_name": "ShipmentAgent", "risk_score": 40.0, "status": "SUCCESS"}
        inv_out = {"agent_name": "InventoryAgent", "risk_score": 30.0, "status": "SUCCESS"}

        risk_out = risk_agent.run(
            db, "supplier:1",
            supplier_output=sup_out,
            shipment_output=ship_out,
            inventory_output=inv_out,
            external_output=ext_degraded
        )
        assert risk_out["status"] == "DEGRADED"
        assert "ExternalIntelligenceAgent" in risk_out["reasoning_output"]["degraded_inputs"]
    finally:
        db.close()

def test_persisted_agent_outputs():
    db = SessionLocal()
    try:
        count_before = db.query(AgentOutput).count()
        multi_agent_orchestrator.run_pipeline(db, "supplier:1")
        count_after = db.query(AgentOutput).count()
        assert count_after >= count_before + 5
    finally:
        db.close()

def test_agents_api_endpoints():
    post_res = client.post("/api/v1/agents/trigger", json={"target_global_id": "supplier:1"})
    assert post_res.status_code == 200
    data = post_res.json()
    assert data["status"] == "success"
    assert "composite_risk_score" in data["data"]

    get_res = client.get("/api/v1/agents/outputs")
    assert get_res.status_code == 200
    assert get_res.json()["status"] == "success"
    assert get_res.json()["count"] >= 1
