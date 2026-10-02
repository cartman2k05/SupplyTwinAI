import json
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.models.recommendation import Recommendation
from backend.app.models.audit import AuditLog
from backend.app.models.user import User
from backend.app.auth.dependencies import get_current_user, require_manager
from backend.app.schemas.recommendation import (
    RecommendationResponse,
    RecommendationDecisionRequest,
    DisruptionMemoryResponse
)
from backend.app.services.memory_service import memory_service

router = APIRouter(prefix="/recommendations", tags=["recommendations"])

@router.get("", response_model=List[RecommendationResponse])
def list_recommendations(
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status: pending, accepted, rejected"),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """
    List recommendations from DB. Allows filtering by status ('pending', 'accepted', 'rejected').
    """
    query = db.query(Recommendation)
    if status_filter:
        query = query.filter(Recommendation.status == status_filter)
    
    recs = query.order_by(Recommendation.created_at.desc()).limit(limit).all()
    return recs

@router.post("/{rec_id}/approve", response_model=RecommendationResponse)
def approve_recommendation(
    rec_id: int,
    body: Optional[RecommendationDecisionRequest] = None,
    current_user: User = Depends(require_manager),
    db: Session = Depends(get_db)
):
    """
    Human Supply Chain Manager approves candidate recommendation.
    Updates status to 'accepted', logs to audit_log, and saves disruption memory.
    """
    rec = db.query(Recommendation).filter(Recommendation.recommendation_id == rec_id).first()
    if not rec:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recommendation not found")

    notes = body.notes if body else f"Approved by manager {current_user.email}"
    rec.status = "accepted"

    # Audit Trail Logging (NFR-S1)
    audit_entry = AuditLog(
        user_id=current_user.id,
        user_email=current_user.email,
        action="RECOMMENDATION_ACCEPTED",
        resource_type="recommendation",
        resource_id=rec.global_id,
        details_json=json.dumps({
            "action_type": rec.action_type,
            "entity_global_id": rec.entity_global_id,
            "notes": notes
        })
    )
    db.add(audit_entry)

    # Persist in Disruption Memory for Configuration C retrieval
    memory_service.store_memory(
        db,
        event_type=rec.action_type,
        entity_global_id=rec.entity_global_id,
        action_taken=rec.action_type,
        outcome_score=min(98.0, rec.confidence_score * 100.0 + 5.0),
        root_cause=rec.title,
        resolution_notes=notes
    )

    db.commit()
    db.refresh(rec)
    return rec

@router.post("/{rec_id}/reject", response_model=RecommendationResponse)
def reject_recommendation(
    rec_id: int,
    body: Optional[RecommendationDecisionRequest] = None,
    current_user: User = Depends(require_manager),
    db: Session = Depends(get_db)
):
    """
    Human Supply Chain Manager rejects candidate recommendation.
    Updates status to 'rejected', logs to audit_log.
    """
    rec = db.query(Recommendation).filter(Recommendation.recommendation_id == rec_id).first()
    if not rec:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recommendation not found")

    notes = body.notes if body else f"Rejected by manager {current_user.email}"
    rec.status = "rejected"

    # Audit Trail Logging (NFR-S1)
    audit_entry = AuditLog(
        user_id=current_user.id,
        user_email=current_user.email,
        action="RECOMMENDATION_REJECTED",
        resource_type="recommendation",
        resource_id=rec.global_id,
        details_json=json.dumps({
            "action_type": rec.action_type,
            "entity_global_id": rec.entity_global_id,
            "notes": notes
        })
    )
    db.add(audit_entry)

    db.commit()
    db.refresh(rec)
    return rec

@router.get("/memories/search")
def search_memories(
    target_global_id: str = Query(..., description="Target entity global ID (e.g. supplier:1)"),
    event_type: Optional[str] = Query(None, description="Disruption event type"),
    limit: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db)
):
    """
    Search past disruption memories for given target entity or event type.
    """
    memories = memory_service.search_similar_memories(
        db,
        entity_global_id=target_global_id,
        event_type=event_type,
        limit=limit
    )
    return {"status": "success", "count": len(memories), "memories": memories}
