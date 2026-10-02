import json
import time
import logging
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from backend.app.models.recommendation import AgentOutput

logger = logging.getLogger(__name__)

class BaseSupplyAgent:
    """Abstract base agent for SupplyTwinAI multi-agent reasoning layer."""

    def __init__(self, agent_name: str):
        self.agent_name = agent_name

    def format_output(
        self,
        target_global_id: str,
        risk_score: float,
        reasoning: Dict[str, Any],
        execution_time_ms: float,
        status: str = "SUCCESS",
        stale: bool = False
    ) -> Dict[str, Any]:
        return {
            "agent_name": self.agent_name,
            "target_global_id": target_global_id,
            "status": status,
            "risk_score": round(max(0.0, min(100.0, risk_score)), 2),
            "reasoning_output": reasoning,
            "execution_time_ms": round(execution_time_ms, 2),
            "stale": stale
        }

    def persist_output(
        self,
        db: Session,
        target_global_id: str,
        output_dict: Dict[str, Any],
        execution_time_ms: float
    ) -> AgentOutput:
        """Store agent reasoning trail in PostgreSQL database (SRS §4.4 REQ-7)."""
        record = AgentOutput(
            agent_name=self.agent_name,
            entity_global_id=target_global_id,
            output_data=json.dumps(output_dict),
            execution_time_ms=execution_time_ms
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record
