import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_login_success_manager():
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "manager@supplytwin.ai", "password": "ManagerPassword123!"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["role"] == "manager"

def test_login_success_admin():
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "admin@supplytwin.ai", "password": "AdminPassword123!"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["role"] == "admin"

def test_login_invalid_credentials():
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "manager@supplytwin.ai", "password": "WrongPassword!"}
    )
    assert response.status_code == 401

def test_get_me():
    # First login to get token
    res = client.post("/api/v1/auth/login", data={"username": "manager@supplytwin.ai", "password": "ManagerPassword123!"})
    token = res.json()["access_token"]
    
    # Request profile
    response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "manager@supplytwin.ai"
    assert data["role"] == "manager"
