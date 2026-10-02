import time
import logging
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from agents.base_agent import BaseSupplyAgent
from backend.app.models.warehouse import Warehouse, WarehouseInventory
from backend.app.models.event import DisruptionEvent

logger = logging.getLogger(__name__)

class InventoryAgent(BaseSupplyAgent):
    """Evaluates warehouse inventory stock levels, reorder points, and stockout depletion risks."""

    def __init__(self):
        super().__init__(agent_name="InventoryAgent")

    def run(self, db: Session, target_global_id: str) -> Dict[str, Any]:
        start_time = time.time()

        inv_id = target_global_id if target_global_id.startswith("inventory:") else "inventory:1"
        inventory = db.query(WarehouseInventory).filter(WarehouseInventory.global_id == inv_id).first()

        if not inventory:
            inventory = db.query(WarehouseInventory).first()

        if not inventory:
            exec_time = (time.time() - start_time) * 1000
            res = self.format_output(target_global_id, 30.0, {"warning": "Inventory record not found"}, exec_time, status="DEGRADED", stale=True)
            self.persist_output(db, target_global_id, res, exec_time)
            return res

        warehouse = db.query(Warehouse).filter(Warehouse.warehouse_id == inventory.warehouse_id).first()
        active_disruption = db.query(DisruptionEvent).filter(
            DisruptionEvent.target_global_id == inventory.global_id,
            DisruptionEvent.status == "active"
        ).first()

        stock = inventory.stock or 0
        reorder_point = inventory.reorder_point or 100
        days_of_supply = stock / max(1.0, inventory.avg_daily_demand or 10.0)

        if stock < reorder_point:
            stockout_risk = 85.0 + (1.0 - (stock / max(1.0, reorder_point))) * 15.0
        elif days_of_supply < 3.0:
            stockout_risk = 60.0
        else:
            stockout_risk = 15.0

        if active_disruption:
            stockout_risk += float(active_disruption.severity or 0.8) * 20.0

        risk_score = min(100.0, max(0.0, stockout_risk))

        reasoning = {
            "inventory_global_id": inventory.global_id,
            "warehouse_id": inventory.warehouse_id,
            "warehouse_name": warehouse.name if warehouse else "Regional Facility",
            "product_id": inventory.product_id,
            "current_stock": stock,
            "reorder_point": reorder_point,
            "avg_daily_demand": inventory.avg_daily_demand,
            "days_of_supply": round(days_of_supply, 1),
            "restock_lead_days": inventory.restock_lead_days,
            "is_below_reorder_point": stock < reorder_point,
            "has_stockout_disruption": active_disruption is not None
        }

        exec_time = (time.time() - start_time) * 1000
        res = self.format_output(target_global_id, risk_score, reasoning, exec_time, status="SUCCESS")
        self.persist_output(db, target_global_id, res, exec_time)
        return res

inventory_agent = InventoryAgent()
