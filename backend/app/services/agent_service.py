import json
import logging
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from backend.app.models.recommendation import AgentOutput
from agents.orchestrator import multi_agent_orchestrator

logger = logging.getLogger(__name__)

class AgentService:
    """Service wrapping multi-agent orchestration and agent output persistence queries."""

    def trigger_pipeline(self, db: Session, target_global_id: str) -> Dict[str, Any]:
        """Trigger multi-agent pipeline execution for a given entity global_id."""
        return multi_agent_orchestrator.run_pipeline(db, target_global_id)

    def get_stored_outputs(self, db: Session, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieve stored agent reasoning trail records from PostgreSQL agent_outputs table."""
        records = db.query(AgentOutput).order_by(AgentOutput.output_id.desc()).limit(limit).all()
        result = []
        for r in records:
            try:
                parsed_data = json.loads(r.output_data)
            except Exception:
                parsed_data = r.output_data

            result.append({
                "output_id": r.output_id,
                "agent_name": r.agent_name,
                "entity_global_id": r.entity_global_id,
                "output_data": parsed_data,
                "execution_time_ms": r.execution_time_ms,
                "created_at": r.created_at.isoformat()
            })
        return result

agent_service = AgentService()
