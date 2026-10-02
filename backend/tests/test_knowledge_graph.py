import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.db.database import SessionLocal, engine
from backend.app.db.base import Base
from knowledge_graph.neo4j_driver import graph_driver
from knowledge_graph.schema import ensure_graph_schema, NODE_LABELS
from knowledge_graph.etl_sync import graph_sync_engine
from backend.app.services.graph_service import graph_service

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)

def test_neo4j_schema_constraints():
    constraints = ensure_graph_schema(graph_driver)
    assert len(constraints) == len(NODE_LABELS)

def test_postgres_to_neo4j_sync():
    db = SessionLocal()
    try:
        res = graph_sync_engine.sync_all(db, limit=20)
        assert res["status"] == "success"
        assert res["nodes_synced"] >= 0
        assert res["sync_duration_seconds"] < 30.0
        assert res["nfr_p3_compliant"] is True
    finally:
        db.close()

def test_multihop_cypher_queries():
    db = SessionLocal()
    try:
        impact_data = graph_service.get_impact_chain("supplier:1", db)
        assert impact_data["source_global_id"] == "supplier:1"
        assert "total_impacted_entities" in impact_data
        assert impact_data["multi_hop_depth"] >= 1
    finally:
        db.close()

def test_graph_api_endpoints():
    response = client.get("/api/v1/graph/subgraph?limit=50")
    assert response.status_code == 200
    subgraph = response.json()
    assert subgraph["status"] == "success"
    assert "nodes" in subgraph["data"]
    assert "edges" in subgraph["data"]

    impact_res = client.get("/api/v1/graph/impact?global_id=supplier:1")
    assert impact_res.status_code == 200
    impact = impact_res.json()
    assert impact["status"] == "success"

    stats_res = client.get("/api/v1/graph/stats")
    assert stats_res.status_code == 200
    assert stats_res.json()["status"] == "success"

    sync_res = client.post("/api/v1/graph/sync?limit=50")
    assert sync_res.status_code == 200
    assert sync_res.json()["status"] == "success"
