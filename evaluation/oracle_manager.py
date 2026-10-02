from typing import Dict, Any
from sqlalchemy.orm import Session
from backend.app.models.recommendation import Recommendation
from backend.app.models.audit import AuditLog
from backend.app.models.user import User
from backend.app.services.memory_service import memory_service

class OracleManagerPolicy:
    """
    Simulated Expert Supply Chain Manager Oracle Policy (DECISIONS.md §5).
    Evaluates candidate recommendations against ground-truth acceptable action classes
    and executes automated Accept/Reject decisions with audit logging.
    """

    def evaluate_and_decide(
        self,
        db: Session,
        recommendation_id: int,
        acceptable_action_class: str,
        manager_user: User
    ) -> Dict[str, Any]:
        rec = db.query(Recommendation).filter(Recommendation.recommendation_id == recommendation_id).first()
        if not rec:
            return {"decision": "REJECTED", "reason": "Recommendation record not found"}

        is_valid = (rec.action_type == acceptable_action_class)
        decision = "accepted" if is_valid else "rejected"
        notes = f"Oracle Manager evaluated action {rec.action_type} against ground-truth class {acceptable_action_class}."

        rec.status = decision

        # Write Audit Log
        audit_entry = AuditLog(
            user_id=manager_user.id,
            user_email=manager_user.email,
            action=f"RECOMMENDATION_{decision.upper()}",
            resource_type="recommendation",
            resource_id=rec.global_id,
            details_json=f'{{"oracle_eval": true, "action_type": "{rec.action_type}", "acceptable_action": "{acceptable_action_class}"}}'
        )
        db.add(audit_entry)

        # If accepted, store in Disruption Memory (Configuration C feed)
        if decision == "accepted":
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

        return {
            "decision": decision,
            "is_valid": is_valid,
            "action_type": rec.action_type,
            "confidence_score": rec.confidence_score,
            "recommendation_id": rec.recommendation_id
        }

oracle_manager = OracleManagerPolicy()
