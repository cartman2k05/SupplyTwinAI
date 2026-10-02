import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.db.database import SessionLocal, engine
from backend.app.db.base import Base
from backend.app.models.recommendation import Recommendation, DisruptionMemory
from backend.app.models.audit import AuditLog
from backend.app.models.user import User
from backend.app.services.memory_service import memory_service
from agents.recommendation_agent import recommendation_agent

client = TestClient(app)

from backend.app.db_loader_helper import ensure_db_initialized

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        ensure_db_initialized(db)
    finally:
        db.close()

def get_auth_header(email: str = "manager@supplytwin.ai", password: str = "ManagerPassword123!"):
    response = client.post("/api/v1/auth/login", data={"username": email, "password": password})
    if response.status_code == 200:
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    return {}

def test_store_and_search_disruption_memory():
    db = SessionLocal()
    try:
        mem = memory_service.store_memory(
            db,
            event_type="SUPPLIER_OUTAGE",
            entity_global_id="supplier:99",
            action_taken="SWITCH_SUPPLIER",
            outcome_score=92.0,
            root_cause="Factory power failure",
            resolution_notes="Switched to alternate pool supplier 102"
        )
        assert mem.memory_id is not None
        assert mem.entity_global_id == "supplier:99"

        results = memory_service.search_similar_memories(db, target_global_id="supplier:99", limit=5)
        matched = [r for r in results if r["entity_global_id"] == "supplier:99"]
        assert len(matched) >= 1
        assert matched[0]["action_taken"] == "SWITCH_SUPPLIER"
        assert matched[0]["outcome_score"] == 92.0
    finally:
        db.close()

def test_recommendation_agent_memory_enrichment():
    db = SessionLocal()
    try:
        # Pre-seed a memory
        memory_service.store_memory(
            db,
            event_type="SWITCH_SUPPLIER",
            entity_global_id="supplier:88",
            action_taken="SWITCH_SUPPLIER",
            outcome_score=95.0
        )

        risk_out = {
            "risk_score": 78.0,
            "reasoning_output": {"requires_recommendation": True, "risk_band": "HIGH"}
        }

        rec_out = recommendation_agent.run(db, "supplier:88", risk_out)
        assert rec_out["agent_name"] == "RecommendationAgent"
        assert rec_out["reasoning_output"]["prior_memory_applied"] is True
        assert len(rec_out["reasoning_output"]["prior_memories"]) >= 1

        rec_id = rec_out["reasoning_output"]["recommendation_global_id"]
        rec_db = db.query(Recommendation).filter(Recommendation.global_id == rec_id).first()
        assert rec_db is not None
        assert rec_db.status == "pending"  # Recommendation MUST start as pending (Human Governance)
        assert rec_db.memory_citations_json is not None
    finally:
        db.close()

def test_recommendation_approval_workflow():
    headers = get_auth_header()
    db = SessionLocal()
    try:
        # Create a pending recommendation
        rec = Recommendation(
            global_id="recommendation:test_app_1",
            entity_global_id="supplier:1",
            action_type="SWITCH_SUPPLIER",
            title="Test Mitigation",
            description="Test Description",
            confidence_score=0.88,
            status="pending"
        )
        db.add(rec)
        db.commit()
        db.refresh(rec)
        rec_id = rec.recommendation_id

        # Approve recommendation
        res = client.post(
            f"/api/v1/recommendations/{rec_id}/approve",
            json={"notes": "Approved after reviewing alternate capacity"},
            headers=headers
        )
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "accepted"

        # Verify audit trail logged
        audit = db.query(AuditLog).filter(AuditLog.resource_id == rec.global_id).first()
        assert audit is not None
        assert "RECOMMENDATION_ACCEPTED" in audit.action

        # Verify disruption memory created
        mem = db.query(DisruptionMemory).filter(DisruptionMemory.entity_global_id == "supplier:1").first()
        assert mem is not None
    finally:
        db.close()

def test_recommendation_rejection_workflow():
    headers = get_auth_header()
    db = SessionLocal()
    try:
        rec = Recommendation(
            global_id="recommendation:test_rej_1",
            entity_global_id="shipment:1",
            action_type="REROUTE_SHIPMENT",
            title="Test Reroute",
            description="Test Description",
            confidence_score=0.75,
            status="pending"
        )
        db.add(rec)
        db.commit()
        db.refresh(rec)
        rec_id = rec.recommendation_id

        res = client.post(
            f"/api/v1/recommendations/{rec_id}/reject",
            json={"notes": "Cost of rerouting exceeds threshold"},
            headers=headers
        )
        assert res.status_code == 200
        assert res.json()["status"] == "rejected"

        audit = db.query(AuditLog).filter(AuditLog.resource_id == rec.global_id).first()
        assert audit is not None
        assert "RECOMMENDATION_REJECTED" in audit.action
    finally:
        db.close()

def test_search_memories_api():
    res = client.get("/api/v1/recommendations/memories/search?target_global_id=supplier:1")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert "memories" in data
