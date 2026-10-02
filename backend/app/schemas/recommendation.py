from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class RecommendationDecisionRequest(BaseModel):
    notes: Optional[str] = Field(None, description="Optional notes or rationale for manager decision")

class RecommendationResponse(BaseModel):
    recommendation_id: int
    global_id: str
    entity_global_id: str
    action_type: str
    title: str
    description: str
    confidence_score: float
    status: str
    reasoning_json: Optional[str] = None
    memory_citations_json: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class DisruptionMemoryResponse(BaseModel):
    memory_id: int
    event_type: str
    entity_global_id: str
    scenario_fingerprint: str
    root_cause: str
    action_taken: str
    outcome_score: float
    resolution_notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
