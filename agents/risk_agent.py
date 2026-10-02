import time
import logging
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from agents.base_agent import BaseSupplyAgent
from backend.app.models.config import AgentConfig

logger = logging.getLogger(__name__)

class RiskAssessmentAgent(BaseSupplyAgent):
    """Stage 2 Aggregation Agent: Computes composite risk score & risk band from 4 Stage 1 outputs."""

    def __init__(self):
        super().__init__(agent_name="RiskAssessmentAgent")

    def run(
        self,
        db: Session,
        target_global_id: str,
        supplier_output: Dict[str, Any],
        shipment_output: Dict[str, Any],
        inventory_output: Dict[str, Any],
        external_output: Dict[str, Any]
    ) -> Dict[str, Any]:
        start_time = time.time()

        # Load weights and thresholds from agent_config
        config = db.query(AgentConfig).first()
        w_sup = config.risk_weight_supplier if config else 0.30
        w_ship = config.risk_weight_shipment if config else 0.30
        w_inv = config.risk_weight_inventory if config else 0.20
        w_ext = config.risk_weight_external if config else 0.20

        t_low_med = config.threshold_low_medium if config else 33.0
        t_med_high = config.threshold_medium_high if config else 66.0
        t_alert = config.alert_threshold_recommendation if config else 60.0

        s_sup = supplier_output.get("risk_score", 0.0)
        s_ship = shipment_output.get("risk_score", 0.0)
        s_inv = inventory_output.get("risk_score", 0.0)
        s_ext = external_output.get("risk_score", 0.0)

        # Check for degraded inputs
        degraded_inputs = [
            out.get("agent_name") for out in [supplier_output, shipment_output, inventory_output, external_output]
            if out.get("status") == "DEGRADED" or out.get("stale") is True
        ]
        is_degraded = len(degraded_inputs) > 0

        # Calculate composite risk score
        composite_risk = (
            w_sup * s_sup +
            w_ship * s_ship +
            w_inv * s_inv +
            w_ext * s_ext
        )
        composite_risk = round(min(100.0, max(0.0, composite_risk)), 2)

        # Assign risk band
        if composite_risk >= t_med_high:
            risk_band = "HIGH"
        elif composite_risk >= t_low_med:
            risk_band = "MEDIUM"
        else:
            risk_band = "LOW"

        requires_recommendation = composite_risk >= t_alert

        reasoning = {
            "target_global_id": target_global_id,
            "composite_risk_score": composite_risk,
            "risk_band": risk_band,
            "requires_recommendation": requires_recommendation,
            "alert_threshold": t_alert,
            "weights_applied": {
                "supplier": w_sup,
                "shipment": w_ship,
                "inventory": w_inv,
                "external": w_ext
            },
            "upstream_scores": {
                "supplier": s_sup,
                "shipment": s_ship,
                "inventory": s_inv,
                "external": s_ext
            },
            "degraded_inputs": degraded_inputs
        }

        exec_time = (time.time() - start_time) * 1000
        status = "DEGRADED" if is_degraded else "SUCCESS"
        res = self.format_output(target_global_id, composite_risk, reasoning, exec_time, status=status, stale=is_degraded)
        self.persist_output(db, target_global_id, res, exec_time)
        return res

risk_agent = RiskAssessmentAgent()
