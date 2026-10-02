from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from backend.app.models.shipment import Shipment, LiveShipment
from backend.app.models.order import Order
from backend.app.models.warehouse import Warehouse
from backend.app.models.event import DisruptionEvent
from simulation.events import EmpiricalEventSampler

class SimulationEngine:
    """Discrete-time simulation clock engine for logistics twin."""

    def __init__(self, seed: int = 42, start_time: Optional[datetime] = None):
        self.seed = seed
        self.sampler = EmpiricalEventSampler(seed=seed)
        self.sim_time = start_time or datetime(2026, 10, 1, 0, 0, 0)
        self.is_running = False
        self.speed_multiplier = 1.0
        self.total_ticks = 0

    def start(self):
        self.is_running = True

    def pause(self):
        self.is_running = False

    def set_speed(self, speed: float):
        self.speed_multiplier = max(0.1, min(10.0, speed))

    def reset(self, seed: Optional[int] = None):
        if seed is not None:
            self.seed = seed
            self.sampler = EmpiricalEventSampler(seed=seed)
        self.sim_time = datetime(2026, 10, 1, 0, 0, 0)
        self.total_ticks = 0
        self.is_running = False

    def init_live_shipments(self, db: Session, limit: int = 100) -> int:
        """Ensure live_shipments table is populated from shipments table."""
        existing_count = db.query(LiveShipment).count()
        if existing_count >= limit:
            return existing_count

        shipments = (
            db.query(Shipment, Order, Warehouse)
            .join(Order, Shipment.order_id == Order.order_id)
            .outerjoin(Warehouse, Order.assigned_warehouse_id == Warehouse.warehouse_id)
            .limit(limit)
            .all()
        )

        for ship, order, wh in shipments:
            existing = db.query(LiveShipment).filter(LiveShipment.shipment_id == ship.shipment_id).first()
            if existing:
                continue

            origin_lat = wh.latitude if wh else 37.7749
            origin_lon = wh.longitude if wh else -122.4194
            eta = self.sim_time + timedelta(days=ship.days_scheduled or 3)
            vehicle_id = (ship.shipment_id % 50) + 1

            live = LiveShipment(
                shipment_id=ship.shipment_id,
                current_latitude=origin_lat,
                current_longitude=origin_lon,
                current_status="IN_TRANSIT",
                eta=eta,
                assigned_vehicle_id=vehicle_id,
                updated_at=datetime.utcnow()
            )
            db.add(live)

        db.commit()
        return db.query(LiveShipment).count()

    def tick(self, db: Session, hours_elapsed: float = 1.0) -> Dict[str, Any]:
        """Advance simulation clock by hours_elapsed and update live shipment positions & status."""
        self.total_ticks += 1
        effective_hours = hours_elapsed * self.speed_multiplier
        self.sim_time += timedelta(hours=effective_hours)

        # 1. Guarantee live shipments initialized
        self.init_live_shipments(db)

        # 2. Get active disruptions
        active_disruptions = db.query(DisruptionEvent).filter(DisruptionEvent.status == "active").all()
        disrupted_global_ids = {d.target_global_id for d in active_disruptions}

        # 3. Query all live shipments with full route info
        records = (
            db.query(LiveShipment, Shipment, Order, Warehouse)
            .join(Shipment, LiveShipment.shipment_id == Shipment.shipment_id)
            .join(Order, Shipment.order_id == Order.order_id)
            .outerjoin(Warehouse, Order.assigned_warehouse_id == Warehouse.warehouse_id)
            .all()
        )

        for live, ship, order, wh in records:
            origin_lat = wh.latitude if wh else 37.7749
            origin_lon = wh.longitude if wh else -122.4194
            dest_lat = order.customer_latitude or 37.7749
            dest_lon = order.customer_longitude or -122.4194

            # Check if affected by active disruption
            is_disrupted = (
                ship.global_id in disrupted_global_ids or
                (wh and wh.global_id in disrupted_global_ids) or
                order.customer_global_id in disrupted_global_ids
            )

            if is_disrupted:
                live.current_status = "DELAYED"
                if live.eta and live.eta < self.sim_time + timedelta(hours=24):
                    live.eta += timedelta(hours=12)
            elif live.current_status == "DELAYED" and not is_disrupted:
                live.current_status = "IN_TRANSIT"

            # Progress position along linear interpolation
            total_duration_hours = max(24.0, float(ship.days_scheduled or 3) * 24.0)
            elapsed_sim_hours = self.total_ticks * effective_hours
            progress = min(1.0, max(0.0, elapsed_sim_hours / total_duration_hours))

            if progress >= 1.0:
                live.current_status = "DELIVERED"
                live.current_latitude = dest_lat
                live.current_longitude = dest_lon
            else:
                live.current_latitude = origin_lat + progress * (dest_lat - origin_lat)
                live.current_longitude = origin_lon + progress * (dest_lon - origin_lon)

            live.updated_at = datetime.utcnow()

        db.commit()

        # Aggregate telemetry snapshot
        live_count = db.query(LiveShipment).count()
        delayed_count = db.query(LiveShipment).filter(LiveShipment.current_status == "DELAYED").count()
        in_transit_count = db.query(LiveShipment).filter(LiveShipment.current_status == "IN_TRANSIT").count()
        delivered_count = db.query(LiveShipment).filter(LiveShipment.current_status == "DELIVERED").count()

        return {
            "sim_time": self.sim_time.isoformat(),
            "is_running": self.is_running,
            "speed_multiplier": self.speed_multiplier,
            "total_ticks": self.total_ticks,
            "live_shipments_count": live_count,
            "delayed_shipments": delayed_count,
            "in_transit_shipments": in_transit_count,
            "delivered_shipments": delivered_count,
            "active_disruptions_count": len(active_disruptions),
            "recent_disruptions": [
                {
                    "event_id": d.event_id,
                    "global_id": d.global_id,
                    "scenario_id": d.scenario_id,
                    "event_type": d.event_type,
                    "severity": d.severity,
                    "target_global_id": d.target_global_id,
                    "acceptable_action_class": d.acceptable_action_class,
                    "description": d.description,
                    "status": d.status,
                    "created_at": d.created_at.isoformat() if d.created_at else None
                }
                for d in active_disruptions[:5]
            ]
        }

# Global singleton simulation engine instance
sim_engine = SimulationEngine(seed=42)
