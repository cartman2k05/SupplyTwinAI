import pytest
import concurrent.futures
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.db.database import SessionLocal, engine
from backend.app.db.base import Base
from backend.app.db_loader_helper import ensure_db_initialized

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        ensure_db_initialized(db)
    finally:
        db.close()

def get_auth_token(username: str, password: str) -> str:
    res = client.post("/api/v1/auth/login", data={"username": username, "password": password})
    if res.status_code == 200:
        return res.json()["access_token"]
    return ""

def test_csv_report_export_endpoints():
    token = get_auth_token("manager@supplytwin.ai", "ManagerPassword123!")
    headers = {"Authorization": f"Bearer {token}"}

    resources = ["orders", "shipments", "inventory", "suppliers", "recommendations", "audit"]
    for res_name in resources:
        res = client.get(f"/api/v1/reports/export/{res_name}", headers=headers)
        assert res.status_code == 200
        assert "text/csv" in res.headers["content-type"]
        assert "attachment" in res.headers["content-disposition"]
        assert len(res.text) > 0

def test_unsupported_csv_report_resource():
    token = get_auth_token("manager@supplytwin.ai", "ManagerPassword123!")
    res = client.get("/api/v1/reports/export/invalid_resource", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 400
    assert "Unsupported report resource" in res.json()["detail"]

def test_admin_config_weight_and_threshold_validation():
    token = get_auth_token("admin@supplytwin.ai", "AdminPassword123!")
    headers = {"Authorization": f"Bearer {token}"}

    # Test invalid weight sum != 1.0
    bad_weights = {
        "risk_weight_supplier": 0.50,
        "risk_weight_shipment": 0.50,
        "risk_weight_inventory": 0.50,
        "risk_weight_external": 0.50,
        "threshold_low_medium": 33.0,
        "threshold_medium_high": 66.0,
        "alert_threshold_recommendation": 60.0
    }
    res_bad_weights = client.put("/api/v1/admin/config", json=bad_weights, headers=headers)
    assert res_bad_weights.status_code == 400
    assert "Risk weights must sum to 1.0" in res_bad_weights.json()["detail"]

    # Test invalid threshold bounds (low_medium > medium_high)
    bad_thresholds = {
        "risk_weight_supplier": 0.30,
        "risk_weight_shipment": 0.30,
        "risk_weight_inventory": 0.20,
        "risk_weight_external": 0.20,
        "threshold_low_medium": 80.0,
        "threshold_medium_high": 50.0,
        "alert_threshold_recommendation": 60.0
    }
    res_bad_thresh = client.put("/api/v1/admin/config", json=bad_thresholds, headers=headers)
    assert res_bad_thresh.status_code == 400
    assert "Thresholds must satisfy" in res_bad_thresh.json()["detail"]

    # Test valid config update
    valid_config = {
        "risk_weight_supplier": 0.30,
        "risk_weight_shipment": 0.30,
        "risk_weight_inventory": 0.20,
        "risk_weight_external": 0.20,
        "threshold_low_medium": 30.0,
        "threshold_medium_high": 65.0,
        "alert_threshold_recommendation": 55.0
    }
    res_valid = client.put("/api/v1/admin/config", json=valid_config, headers=headers)
    assert res_valid.status_code == 200
    assert res_valid.json()["threshold_low_medium"] == 30.0

def test_concurrent_5_users_load():
    token = get_auth_token("manager@supplytwin.ai", "ManagerPassword123!")
    headers = {"Authorization": f"Bearer {token}"}

    def make_request(user_idx):
        if user_idx % 2 == 0:
            return client.get("/api/v1/shipments/", headers=headers).status_code
        else:
            return client.get("/api/v1/suppliers/", headers=headers).status_code

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(make_request, i) for i in range(5)]
        status_codes = [f.result() for f in concurrent.futures.as_completed(futures)]

    assert all(code == 200 for code in status_codes)
