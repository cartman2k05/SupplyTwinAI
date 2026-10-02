import csv
import io
from typing import Generator
from sqlalchemy.orm import Session

from backend.app.models.order import Order
from backend.app.models.shipment import Shipment
from backend.app.models.warehouse import WarehouseInventory
from backend.app.models.supplier import Supplier
from backend.app.models.recommendation import Recommendation
from backend.app.models.audit import AuditLog

class ReportService:
    """
    CSV Report Formatting & Streaming Engine (§4.10 REQ-1 & REQ-2).
    Streams formatted operational CSV reports for all core system entities.
    """

    def export_orders_csv(self, db: Session) -> str:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "order_id", "global_id", "customer_global_id", "order_status",
            "market", "order_region", "destination_country", "destination_city", "order_date"
        ])

        orders = db.query(Order).limit(1000).all()
        for o in orders:
            writer.writerow([
                o.order_id, o.global_id, o.customer_global_id, o.order_status,
                o.market, o.order_region, o.destination_country, o.destination_city,
                o.order_date.isoformat() if o.order_date else ""
            ])
        return output.getvalue()

    def export_shipments_csv(self, db: Session) -> str:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "shipment_id", "global_id", "order_global_id", "shipping_mode",
            "days_scheduled", "days_real", "delivery_delay_days", "delivery_status", "shipping_date"
        ])

        shipments = db.query(Shipment).limit(1000).all()
        for s in shipments:
            delay = (s.days_real - s.days_scheduled) if (s.days_real is not None and s.days_scheduled is not None) else 0
            writer.writerow([
                s.shipment_id, s.global_id, s.order_global_id, s.shipping_mode,
                s.days_scheduled, s.days_real, delay, s.delivery_status,
                s.shipping_date.isoformat() if s.shipping_date else ""
            ])
        return output.getvalue()

    def export_inventory_csv(self, db: Session) -> str:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "inventory_id", "global_id", "warehouse_id", "product_id",
            "stock", "reorder_point", "avg_daily_demand", "restock_lead_days", "is_synthetic"
        ])

        inv_records = db.query(WarehouseInventory).all()
        for inv in inv_records:
            writer.writerow([
                inv.inventory_id, inv.global_id, inv.warehouse_id, inv.product_id,
                inv.stock, inv.reorder_point, inv.avg_daily_demand,
                inv.restock_lead_days, inv.is_synthetic
            ])
        return output.getvalue()

    def export_suppliers_csv(self, db: Session) -> str:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "supplier_id", "global_id", "name", "on_time_rate",
            "defect_rate", "lead_time_days", "country", "category", "is_primary"
        ])

        suppliers = db.query(Supplier).all()
        for sup in suppliers:
            writer.writerow([
                sup.supplier_id, sup.global_id, sup.name, sup.on_time_rate,
                sup.defect_rate, sup.lead_time_days, sup.country, sup.category,
                sup.is_primary
            ])
        return output.getvalue()

    def export_recommendations_csv(self, db: Session) -> str:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "recommendation_id", "global_id", "entity_global_id", "action_type",
            "title", "description", "confidence_score", "status", "created_at"
        ])

        recs = db.query(Recommendation).order_by(Recommendation.created_at.desc()).all()
        for r in recs:
            writer.writerow([
                r.recommendation_id, r.global_id, r.entity_global_id, r.action_type,
                r.title, r.description, r.confidence_score, r.status,
                r.created_at.isoformat() if r.created_at else ""
            ])
        return output.getvalue()

    def export_audit_csv(self, db: Session) -> str:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "log_id", "user_id", "user_email", "action", "resource_type",
            "resource_id", "details_json", "timestamp"
        ])

        logs = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(1000).all()
        for l in logs:
            writer.writerow([
                l.log_id, l.user_id, l.user_email, l.action, l.resource_type,
                l.resource_id, l.details_json,
                l.timestamp.isoformat() if l.timestamp else ""
            ])
        return output.getvalue()

report_service = ReportService()
