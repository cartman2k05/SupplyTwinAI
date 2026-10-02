import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def get_tokens():
    res_mgr = client.post("/api/v1/auth/login", data={"username": "manager@supplytwin.ai", "password": "ManagerPassword123!"})
    res_adm = client.post("/api/v1/auth/login", data={"username": "admin@supplytwin.ai", "password": "AdminPassword123!"})
    return res_mgr.json()["access_token"], res_adm.json()["access_token"]

def test_rbac_manager_access():
    mgr_token, _ = get_tokens()
    headers = {"Authorization": f"Bearer {mgr_token}"}
    
    # Managers should be able to access general endpoints
    assert client.get("/api/v1/orders/", headers=headers).status_code == 200
    assert client.get("/api/v1/shipments/", headers=headers).status_code == 200
    assert client.get("/api/v1/inventory/", headers=headers).status_code == 200
    assert client.get("/api/v1/suppliers/", headers=headers).status_code == 200

def test_rbac_admin_enforcement():
    mgr_token, adm_token = get_tokens()
    
    # Manager token accessing admin endpoints should get 403 Forbidden
    res_mgr_etl = client.get("/api/v1/etl/history", headers={"Authorization": f"Bearer {mgr_token}"})
    assert res_mgr_etl.status_code == 403
    
    res_mgr_config = client.get("/api/v1/admin/config", headers={"Authorization": f"Bearer {mgr_token}"})
    assert res_mgr_config.status_code == 403
    
    # Admin token should succeed
    res_adm_config = client.get("/api/v1/admin/config", headers={"Authorization": f"Bearer {adm_token}"})
    assert res_adm_config.status_code == 200
