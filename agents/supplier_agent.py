import time
import logging
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from agents.base_agent import BaseSupplyAgent
from backend.app.models.supplier import Supplier, SupplierProduct
from backend.app.models.event import DisruptionEvent

logger = logging.getLogger(__name__)

class SupplierAgent(BaseSupplyAgent):
    """Evaluates supplier reliability, defect rates, outage events, and alternate options."""

    def __init__(self):
        super().__init__(agent_name="SupplierAgent")

    def run(self, db: Session, target_global_id: str) -> Dict[str, Any]:
        start_time = time.time()
        
        # Query target supplier or default to supplier:1
        sup_id = target_global_id if target_global_id.startswith("supplier:") else "supplier:1"
        supplier = db.query(Supplier).filter(Supplier.global_id == sup_id).first()

        if not supplier:
            supplier = db.query(Supplier).first()

        if not supplier:
            # Degraded fallback if no supplier records found
            exec_time = (time.time() - start_time) * 1000
            res = self.format_output(target_global_id, 50.0, {"warning": "Supplier record not found"}, exec_time, status="DEGRADED", stale=True)
            self.persist_output(db, target_global_id, res, exec_time)
            return res

        # Check active disruptions targeting this supplier
        active_disruption = db.query(DisruptionEvent).filter(
            DisruptionEvent.target_global_id == supplier.global_id,
            DisruptionEvent.status == "active"
        ).first()

        # Compute risk score (0-100)
        base_risk = (1.0 - (supplier.on_time_rate or 0.9)) * 50.0 + (supplier.defect_rate or 0.02) * 500.0
        if active_disruption:
            base_risk += float(active_disruption.severity or 0.8) * 40.0

        risk_score = min(100.0, max(0.0, base_risk))

        # Query alternate suppliers for supplied products
        alternates = (
            db.query(Supplier)
            .filter(Supplier.supplier_id != supplier.supplier_id, Supplier.is_primary == False)
            .limit(3)
            .all()
        )

        reasoning = {
            "supplier_global_id": supplier.global_id,
            "supplier_name": supplier.name,
            "on_time_rate": float(supplier.on_time_rate or 0.9),
            "defect_rate": float(supplier.defect_rate or 0.02),
            "lead_time_days": supplier.lead_time_days,
            "has_active_outage": active_disruption is not None,
            "disruption_type": active_disruption.event_type if active_disruption else None,
            "available_alternates": [
                {
                    "global_id": alt.global_id,
                    "name": alt.name,
                    "on_time_rate": alt.on_time_rate,
                    "lead_time_days": alt.lead_time_days
                }
                for alt in alternates
            ]
        }

        exec_time = (time.time() - start_time) * 1000
        res = self.format_output(target_global_id, risk_score, reasoning, exec_time, status="SUCCESS")
        self.persist_output(db, target_global_id, res, exec_time)
        return res

supplier_agent = SupplierAgent()
