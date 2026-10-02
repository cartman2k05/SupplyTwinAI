import time
import logging
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from knowledge_graph.neo4j_driver import graph_driver, Neo4jDriver
from knowledge_graph.schema import ensure_graph_schema
from backend.app.models.supplier import Supplier, SupplierProduct
from backend.app.models.product import Product
from backend.app.models.warehouse import Warehouse, WarehouseInventory
from backend.app.models.order import Order, OrderItem
from backend.app.models.shipment import Shipment, LiveShipment
from backend.app.models.event import DisruptionEvent

logger = logging.getLogger(__name__)

class GraphETLSyncEngine:
    """ETL & Incremental Sync Engine for PostgreSQL to Neo4j Graph Database."""

    def __init__(self, driver: Neo4jDriver = graph_driver):
        self.driver = driver

    def sync_all(self, db: Session, limit: int = 500) -> Dict[str, Any]:
        """Perform full or incremental sync from Postgres database to Neo4j graph."""
        start_time = time.time()
        
        # 1. Ensure constraints
        ensure_graph_schema(self.driver)

        nodes_synced = 0
        relationships_synced = 0

        # 2. Sync Suppliers
        suppliers = db.query(Supplier).limit(limit).all()
        for sup in suppliers:
            cypher = """
            MERGE (s:Supplier {global_id: $global_id})
            SET s.name = $name,
                s.on_time_rate = $on_time_rate,
                s.defect_rate = $defect_rate,
                s.region = $region,
                s.is_synthetic = $is_synthetic
            """
            self.driver.execute_write(cypher, {
                "global_id": sup.global_id,
                "name": sup.name,
                "on_time_rate": float(sup.on_time_rate or 0.9),
                "defect_rate": float(sup.defect_rate or 0.02),
                "region": getattr(sup, "country", "USCA") or "USCA",
                "is_synthetic": bool(sup.is_synthetic)
            })
            nodes_synced += 1

        # 3. Sync Products
        products = db.query(Product).limit(limit).all()
        for prod in products:
            cypher = """
            MERGE (p:Product {global_id: $global_id})
            SET p.product_name = $product_name,
                p.category = $category,
                p.unit_price = $unit_price
            """
            self.driver.execute_write(cypher, {
                "global_id": prod.global_id,
                "product_name": getattr(prod, "name", f"Product #{prod.product_id}"),
                "category": prod.category,
                "unit_price": float(getattr(prod, "price", 0.0))
            })
            nodes_synced += 1

        # 4. Sync Supplier -> Product (SUPPLIES)
        sup_prods = db.query(SupplierProduct).limit(limit * 2).all()
        for sp in sup_prods:
            sup_gid = f"supplier:{sp.supplier_id}"
            prod_gid = f"product:{sp.product_id}"
            cypher = """
            MATCH (s:Supplier {global_id: $supplier_global_id})
            MATCH (p:Product {global_id: $product_global_id})
            MERGE (s)-[r:SUPPLIES]->(p)
            SET r.is_primary = $is_primary
            """
            self.driver.execute_write(cypher, {
                "supplier_global_id": sup_gid,
                "product_global_id": prod_gid,
                "is_primary": bool(sp.is_primary)
            })
            relationships_synced += 1

        # 5. Sync Warehouses
        warehouses = db.query(Warehouse).limit(limit).all()
        for wh in warehouses:
            cypher = """
            MERGE (w:Warehouse {global_id: $global_id})
            SET w.name = $name,
                w.region = $region,
                w.latitude = $latitude,
                w.longitude = $longitude,
                w.capacity = $capacity
            """
            self.driver.execute_write(cypher, {
                "global_id": wh.global_id,
                "name": wh.name,
                "region": wh.region,
                "latitude": float(wh.latitude or 0.0),
                "longitude": float(wh.longitude or 0.0),
                "capacity": int(wh.capacity or 10000)
            })
            nodes_synced += 1

        # 6. Sync Product -> Warehouse (STOCKED_AT)
        inventory_items = db.query(WarehouseInventory).limit(limit * 2).all()
        for inv in inventory_items:
            # Reconstruct warehouse global ID if needed
            wh_gid = f"warehouse:{inv.warehouse_id}" if not str(inv.warehouse_id).startswith("warehouse:") else inv.warehouse_id
            prod_gid = f"product:{inv.product_id}"
            cypher = """
            MATCH (p:Product {global_id: $product_global_id})
            MATCH (w:Warehouse {global_id: $warehouse_global_id})
            MERGE (p)-[r:STOCKED_AT]->(w)
            SET r.stock = $stock,
                r.reorder_point = $reorder_point
            """
            self.driver.execute_write(cypher, {
                "product_global_id": prod_gid,
                "warehouse_global_id": wh_gid,
                "stock": int(inv.stock or 0),
                "reorder_point": int(inv.reorder_point or 0)
            })
            relationships_synced += 1

        # 7. Sync Orders
        orders = db.query(Order).limit(limit).all()
        for ord_rec in orders:
            cypher = """
            MERGE (o:Order {global_id: $global_id})
            SET o.order_status = $order_status,
                o.market = $market,
                o.order_region = $order_region
            """
            self.driver.execute_write(cypher, {
                "global_id": ord_rec.global_id,
                "order_status": ord_rec.order_status,
                "market": ord_rec.market,
                "order_region": ord_rec.order_region
            })
            nodes_synced += 1

            # Order -> Warehouse (FULFILLED_FROM)
            if ord_rec.assigned_warehouse_id:
                wh_gid = f"warehouse:{ord_rec.assigned_warehouse_id}"
                cypher_ff = """
                MATCH (o:Order {global_id: $order_global_id})
                MATCH (w:Warehouse {global_id: $warehouse_global_id})
                MERGE (o)-[:FULFILLED_FROM]->(w)
                """
                self.driver.execute_write(cypher_ff, {
                    "order_global_id": ord_rec.global_id,
                    "warehouse_global_id": wh_gid
                })
                relationships_synced += 1

        # 8. Sync Order -> Product (CONTAINS)
        order_items = db.query(OrderItem).limit(limit * 2).all()
        for item in order_items:
            cypher = """
            MATCH (o:Order {global_id: $order_global_id})
            MATCH (p:Product {global_id: $product_global_id})
            MERGE (o)-[r:CONTAINS]->(p)
            SET r.quantity = $quantity,
                r.unit_price = $unit_price
            """
            self.driver.execute_write(cypher, {
                "order_global_id": item.order_global_id,
                "product_global_id": item.product_global_id,
                "quantity": int(item.quantity or 1),
                "unit_price": float(item.unit_price or 0.0)
            })
            relationships_synced += 1

        # 9. Sync Shipments & Vehicles (SHIPS_VIA)
        shipments = db.query(Shipment).limit(limit).all()
        for ship in shipments:
            cypher = """
            MERGE (sh:Shipment {global_id: $global_id})
            SET sh.shipping_mode = $shipping_mode,
                sh.days_scheduled = $days_scheduled,
                sh.delivery_status = $delivery_status
            """
            self.driver.execute_write(cypher, {
                "global_id": ship.global_id,
                "shipping_mode": ship.shipping_mode,
                "days_scheduled": int(ship.days_scheduled or 3),
                "delivery_status": ship.delivery_status
            })
            nodes_synced += 1

            # Check assigned vehicle
            live = db.query(LiveShipment).filter(LiveShipment.shipment_id == ship.shipment_id).first()
            vehicle_id = live.assigned_vehicle_id if (live and live.assigned_vehicle_id) else ((ship.shipment_id % 50) + 1)
            vehicle_gid = f"vehicle:{vehicle_id}"

            cypher_v = """
            MERGE (v:Vehicle {global_id: $vehicle_global_id})
            SET v.vehicle_type = "Cargo Truck", v.status = "ACTIVE"
            """
            self.driver.execute_write(cypher_v, {"vehicle_global_id": vehicle_gid})

            cypher_sv = """
            MATCH (sh:Shipment {global_id: $shipment_global_id})
            MATCH (v:Vehicle {global_id: $vehicle_global_id})
            MERGE (sh)-[:SHIPS_VIA]->(v)
            """
            self.driver.execute_write(cypher_sv, {
                "shipment_global_id": ship.global_id,
                "vehicle_global_id": vehicle_gid
            })
            relationships_synced += 1

        # 10. Sync Disruption Events (AFFECTS)
        disruptions = db.query(DisruptionEvent).limit(limit).all()
        for d in disruptions:
            cypher_d = """
            MERGE (de:DisruptionEvent {global_id: $global_id})
            SET de.scenario_id = $scenario_id,
                de.event_type = $event_type,
                de.severity = $severity,
                de.status = $status,
                de.description = $description
            """
            self.driver.execute_write(cypher_d, {
                "global_id": d.global_id,
                "scenario_id": d.scenario_id,
                "event_type": d.event_type,
                "severity": float(d.severity or 0.5),
                "status": d.status,
                "description": d.description
            })
            nodes_synced += 1

            if d.target_global_id:
                # Dynamically link DisruptionEvent -> Target (AFFECTS)
                cypher_aff = """
                MATCH (de:DisruptionEvent {global_id: $event_global_id})
                MATCH (target {global_id: $target_global_id})
                MERGE (de)-[:AFFECTS]->(target)
                """
                self.driver.execute_write(cypher_aff, {
                    "event_global_id": d.global_id,
                    "target_global_id": d.target_global_id
                })
                relationships_synced += 1

        duration = time.time() - start_time
        logger.info(f"[Graph Sync] Completed sync of {nodes_synced} nodes and {relationships_synced} relationships in {duration:.2f}s")

        return {
            "status": "success",
            "nodes_synced": nodes_synced,
            "relationships_synced": relationships_synced,
            "sync_duration_seconds": round(duration, 3),
            "nfr_p3_compliant": duration < 30.0
        }

graph_sync_engine = GraphETLSyncEngine()
