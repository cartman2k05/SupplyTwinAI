import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

@pytest.fixture
def auth_headers():
    res = client.post("/api/v1/auth/login", data={"username": "admin@supplytwin.ai", "password": "AdminPassword123!"})
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_admin_config_update(auth_headers):
    # Retrieve current config
    res_get = client.get("/api/v1/admin/config", headers=auth_headers)
    assert res_get.status_code == 200
    
    # Update config with valid weights (sum to 1.0)
    valid_payload = {
        "risk_weight_supplier": 0.35,
        "risk_weight_shipment": 0.25,
        "risk_weight_inventory": 0.20,
        "risk_weight_external": 0.20,
        "threshold_low_medium": 35.0,
        "threshold_medium_high": 70.0,
        "alert_threshold_recommendation": 65.0
    }
    res_put = client.put("/api/v1/admin/config", json=valid_payload, headers=auth_headers)
    assert res_put.status_code == 200
    data = res_put.json()
    assert data["risk_weight_supplier"] == 0.35
    assert data["updated_by"] == "admin@supplytwin.ai"
    
    # Test invalid weights (sum != 1.0) returns 400 Bad Request
    invalid_payload = valid_payload.copy()
    invalid_payload["risk_weight_supplier"] = 0.50
    res_invalid = client.put("/api/v1/admin/config", json=invalid_payload, headers=auth_headers)
    assert res_invalid.status_code == 400

def test_openapi_docs():
    res = client.get("/docs")
    assert res.status_code == 200
    res_json = client.get("/openapi.json")
    assert res_json.status_code == 200
    spec = res_json.json()
    assert "paths" in spec
    assert "/api/v1/auth/login" in spec["paths"]
    assert "/api/v1/admin/config" in spec["paths"]
