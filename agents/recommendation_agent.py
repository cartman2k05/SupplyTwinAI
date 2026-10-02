import uuid
import time
import json
import logging
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from agents.base_agent import BaseSupplyAgent
from backend.app.models.recommendation import Recommendation
from backend.app.services.memory_service import memory_service

logger = logging.getLogger(__name__)

class RecommendationAgent(BaseSupplyAgent):
    """Stage 3 Conditional Agent: Generates human-approved mitigation recommendation candidates with memory enrichment."""

    def __init__(self):
        super().__init__(agent_name="RecommendationAgent")

    def run(
        self,
        db: Session,
        target_global_id: str,
        risk_output: Dict[str, Any]
    ) -> Dict[str, Any]:
        start_time = time.time()

        risk_score = risk_output.get("risk_score", 65.0)
        risk_reasoning = risk_output.get("reasoning_output", {})
        requires_rec = risk_reasoning.get("requires_recommendation", True)

        if not requires_rec and risk_score < 60.0:
            exec_time = (time.time() - start_time) * 1000
            res = self.format_output(
                target_global_id,
                0.0,
                {"notice": "Risk score below alert threshold. No recommendation required."},
                exec_time,
                status="SUCCESS"
            )
            self.persist_output(db, target_global_id, res, exec_time)
            return res

        # Retrieve prior disruption memories (Configuration C)
        prior_memories = memory_service.search_similar_memories(db, target_global_id=target_global_id, limit=3)

        # Determine mitigation action class & description
        target_type = target_global_id.split(":")[0].lower() if ":" in target_global_id else "supplier"

        if target_type == "supplier":
            action_type = "SWITCH_SUPPLIER"
            title = "Activate Alternate Component Supplier Pool"
            desc = "Reallocate order volume to vetted alternate suppliers with higher on-time delivery rates to mitigate supplier disruption."
        elif target_type in ["shipment", "vehicle"]:
            action_type = "REROUTE_SHIPMENT"
            title = "Reroute Inland Container Shipping Lane"
            desc = "Bypass congested port bottleneck and reassign shipment to secondary ground logistics corridor."
        elif target_type == "warehouse":
            action_type = "REALLOCATE_INVENTORY"
            title = "Reallocate Regional Stock Buffers"
            desc = "Transfer safety stock inventory from adjacent regional fulfillment centers to prevent stockout depletion."
        elif target_type in ["event", "disruption"]:
            if "news" in target_global_id.lower() or "news" in str(risk_reasoning).lower():
                action_type = "SWITCH_SUPPLIER"
                title = "Activate Alternate Component Supplier Pool"
                desc = "Reallocate order volume to vetted alternate suppliers due to geopolitical trade route blockade."
            else:
                action_type = "EXPEDITE_SHIPPING"
                title = "Expedite Air Freight Transit"
                desc = "Upgrade pending shipments to expedited air transport mode to bypass severe weather transit corridor disruption."
        else:
            action_type = "SWITCH_SUPPLIER"
            title = "Activate Alternate Component Supplier Pool"
            desc = "Reallocate order volume to vetted alternate suppliers with higher on-time delivery rates."

        # Boost confidence slightly if supported by past successful memory
        confidence_base = (risk_score / 100.0) * 0.95 + 0.1
        if prior_memories:
            confidence_base += 0.05
        confidence_score = round(min(0.98, max(0.65, confidence_base)), 2)

        rec_global_id = f"recommendation:{uuid.uuid4().hex[:8]}"

        # Save recommendation record in DB with 'pending' status (Human-in-the-Loop mandatory, SRS §4.5)
        rec_record = Recommendation(
            global_id=rec_global_id,
            entity_global_id=target_global_id,
            action_type=action_type,
            title=title,
            description=desc,
            confidence_score=confidence_score,
            status="pending",
            reasoning_json=json.dumps({
                "source_agent": "RecommendationAgent",
                "risk_score": risk_score,
                "risk_band": risk_reasoning.get("risk_band", "HIGH"),
                "human_in_the_loop_mandatory": True,
                "prior_memories_count": len(prior_memories)
            }),
            memory_citations_json=json.dumps(prior_memories) if prior_memories else None
        )
        db.add(rec_record)
        db.commit()
        db.refresh(rec_record)

        reasoning = {
            "recommendation_global_id": rec_global_id,
            "target_global_id": target_global_id,
            "action_type": action_type,
            "title": title,
            "description": desc,
            "confidence_score": confidence_score,
            "status": "pending",
            "human_approval_required": True,
            "prior_memory_applied": len(prior_memories) > 0,
            "prior_memories": prior_memories
        }

        exec_time = (time.time() - start_time) * 1000
        res = self.format_output(target_global_id, risk_score, reasoning, exec_time, status="SUCCESS")
        self.persist_output(db, target_global_id, res, exec_time)
        return res

recommendation_agent = RecommendationAgent()
