import time
import logging
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from agents.base_agent import BaseSupplyAgent
from backend.app.models.shipment import Shipment, LiveShipment
from backend.app.models.event import DisruptionEvent

logger = logging.getLogger(__name__)

# Empirical delay risk by shipping mode from DataCo findings
MODE_RISK_MAP = {
    "First Class": 95.0,    # 100% late pattern in historical dataset
    "Second Class": 75.0,   # 79.8% late pattern
    "Same Day": 45.0,       # 47.9% late pattern
    "Standard Class": 35.0  # 39.8% late pattern
}

class ShipmentAgent(BaseSupplyAgent):
    """Evaluates shipment transit route delay predictions and shipping mode patterns."""

    def __init__(self):
        super().__init__(agent_name="ShipmentAgent")

    def run(self, db: Session, target_global_id: str) -> Dict[str, Any]:
        start_time = time.time()

        ship_id = target_global_id if target_global_id.startswith("shipment:") else "shipment:1"
        shipment = db.query(Shipment).filter(Shipment.global_id == ship_id).first()

        if not shipment:
            shipment = db.query(Shipment).first()

        if not shipment:
            exec_time = (time.time() - start_time) * 1000
            res = self.format_output(target_global_id, 40.0, {"warning": "Shipment record not found"}, exec_time, status="DEGRADED", stale=True)
            self.persist_output(db, target_global_id, res, exec_time)
            return res

        live = db.query(LiveShipment).filter(LiveShipment.shipment_id == shipment.shipment_id).first()
        active_disruption = db.query(DisruptionEvent).filter(
            DisruptionEvent.target_global_id == shipment.global_id,
            DisruptionEvent.status == "active"
        ).first()

        base_mode_risk = MODE_RISK_MAP.get(shipment.shipping_mode, 40.0)
        if live and live.current_status == "DELAYED":
            base_mode_risk += 30.0
        if active_disruption:
            base_mode_risk += float(active_disruption.severity or 0.7) * 30.0

        risk_score = min(100.0, max(0.0, base_mode_risk))

        reasoning = {
            "shipment_global_id": shipment.global_id,
            "shipping_mode": shipment.shipping_mode,
            "days_scheduled": shipment.days_scheduled,
            "days_real": shipment.days_real,
            "delivery_status": shipment.delivery_status,
            "current_status": live.current_status if live else "IN_TRANSIT",
            "eta": live.eta.isoformat() if live and live.eta else None,
            "assigned_vehicle_id": live.assigned_vehicle_id if live else None,
            "has_route_disruption": active_disruption is not None
        }

        exec_time = (time.time() - start_time) * 1000
        res = self.format_output(target_global_id, risk_score, reasoning, exec_time, status="SUCCESS")
        self.persist_output(db, target_global_id, res, exec_time)
        return res

shipment_agent = ShipmentAgent()
