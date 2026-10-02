from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.services.graph_service import graph_service
from knowledge_graph.etl_sync import graph_sync_engine

router = APIRouter(prefix="/graph", tags=["graph"])

@router.get("/subgraph")
def get_subgraph(
    limit: int = Query(150, ge=10, le=1000, description="Maximum graph node limit"),
    db: Session = Depends(get_db)
):
    """Retrieve graph nodes and relationships formatted for React Flow visualizer."""
    data = graph_service.get_subgraph(db, limit=limit)
    return {"status": "success", "data": data}

@router.get("/impact")
def get_impact_chain(
    global_id: str = Query(..., description="Target entity global ID (e.g., supplier:1)"),
    db: Session = Depends(get_db)
):
    """Traverse 3+ hop downstream impact chain for a given entity."""
    impact_data = graph_service.get_impact_chain(global_id, db)
    return {"status": "success", "data": impact_data}

@router.post("/sync")
def sync_knowledge_graph(
    limit: int = Query(500, ge=50, le=5000),
    db: Session = Depends(get_db)
):
    """Trigger Postgres-to-Neo4j graph synchronization (NFR-P3 target < 30s)."""
    sync_result = graph_sync_engine.sync_all(db, limit=limit)
    return {"status": "success", "result": sync_result}

@router.get("/stats")
def get_graph_stats():
    """Retrieve node and relationship count metrics from Neo4j."""
    stats = graph_service.get_graph_stats()
    return {"status": "success", "stats": stats}
