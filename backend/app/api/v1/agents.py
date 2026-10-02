from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.services.agent_service import agent_service

router = APIRouter(prefix="/agents", tags=["agents"])

class TriggerAgentsRequest(BaseModel):
    target_global_id: str = Field(..., description="Target entity global ID (e.g. supplier:1, shipment:77202, warehouse:1)")

@router.post("/trigger")
def trigger_agent_pipeline(req: TriggerAgentsRequest, db: Session = Depends(get_db)):
    """Trigger the 6 specialized agents in LangGraph orchestration sequence."""
    try:
        result = agent_service.trigger_pipeline(db, target_global_id=req.target_global_id)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error executing multi-agent pipeline: {str(e)}"
        )

@router.get("/outputs")
def get_agent_outputs(
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """Retrieve stored agent reasoning trail records from agent_outputs table (SRS §4.4 REQ-7)."""
    outputs = agent_service.get_stored_outputs(db, limit=limit)
    return {"status": "success", "count": len(outputs), "outputs": outputs}
