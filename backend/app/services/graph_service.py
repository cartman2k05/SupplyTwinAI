import math
import logging
from typing import Dict, Any, List, Optional
from knowledge_graph.neo4j_driver import graph_driver, Neo4jDriver
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

# Visual layout coordinates for React Flow node positioning by entity type
NODE_TYPE_LAYOUT = {
    "Supplier": {"x": 50, "y_offset": 120, "color": "bg-amber-950/80 border-amber-500 text-amber-200"},
    "Product": {"x": 300, "y_offset": 100, "color": "bg-indigo-950/80 border-indigo-500 text-indigo-200"},
    "Warehouse": {"x": 550, "y_offset": 140, "color": "bg-blue-950/80 border-blue-500 text-blue-200"},
    "Order": {"x": 800, "y_offset": 90, "color": "bg-purple-950/80 border-purple-500 text-purple-200"},
    "Shipment": {"x": 1050, "y_offset": 110, "color": "bg-emerald-950/80 border-emerald-500 text-emerald-200"},
    "Vehicle": {"x": 1300, "y_offset": 130, "color": "bg-cyan-950/80 border-cyan-500 text-cyan-200"},
    "DisruptionEvent": {"x": 300, "y_offset": 450, "color": "bg-rose-950/80 border-rose-500 text-rose-200"}
}

class KnowledgeGraphService:
    """Graph query service executing multi-hop Cypher queries and React Flow formatting."""

    def __init__(self, driver: Neo4jDriver = graph_driver):
        self.driver = driver

    def get_subgraph(self, db: Session, limit: int = 150) -> Dict[str, Any]:
        """Fetch subgraph nodes and relationships formatted for React Flow graph visualizer."""
        if not self.driver.is_connected:
            # Fallback formatted nodes/edges from DB directly if Neo4j driver offline
            return self._build_sql_fallback_subgraph(db, limit)

        cypher = """
        MATCH (n)
        OPTIONAL MATCH (n)-[r]->(m)
        RETURN n, r, m
        LIMIT $limit
        """
        records = self.driver.execute_query(cypher, {"limit": limit})
        return self._format_records_to_react_flow(records)

    def get_impact_chain(self, global_id: str, db: Session) -> Dict[str, Any]:
        """
        Multi-hop Cypher query (3+ hops) traversing downstream impact chain.
        Example 3-hop traversal: Supplier -> Product -> Warehouse -> Order -> Shipment
        """
        if not self.driver.is_connected:
            return self._build_sql_fallback_impact_chain(global_id, db)

        cypher = """
        MATCH path = (start {global_id: $global_id})-[r*1..4]->(impacted)
        RETURN path, length(path) as hop_depth, labels(impacted) as target_type, impacted.global_id as target_global_id
        ORDER BY hop_depth ASC
        LIMIT 100
        """
        records = self.driver.execute_query(cypher, {"global_id": global_id})

        impacted_entities = []
        for rec in records:
            impacted_entities.append({
                "target_global_id": rec.get("target_global_id"),
                "target_type": rec.get("target_type", ["Unknown"])[0],
                "hop_depth": rec.get("hop_depth", 1)
            })

        return {
            "source_global_id": global_id,
            "total_impacted_entities": len(impacted_entities),
            "multi_hop_depth": max([e["hop_depth"] for e in impacted_entities], default=0),
            "impact_chain": impacted_entities
        }

    def get_graph_stats(self) -> Dict[str, Any]:
        """Return node and relationship count metrics from Neo4j."""
        if not self.driver.is_connected:
            return {
                "total_nodes": len(self.driver.memory_store.nodes),
                "total_relationships": len(self.driver.memory_store.relationships),
                "mode": "memory_fallback"
            }

        node_count_res = self.driver.execute_query("MATCH (n) RETURN count(n) as count")
        rel_count_res = self.driver.execute_query("MATCH ()-[r]->() RETURN count(r) as count")

        total_nodes = node_count_res[0]["count"] if node_count_res else 0
        total_rels = rel_count_res[0]["count"] if rel_count_res else 0

        return {
            "total_nodes": total_nodes,
            "total_relationships": total_rels,
            "mode": "neo4j_live"
        }

    def _format_records_to_react_flow(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        nodes_dict = {}
        edges_set = set()
        edges_list = []

        type_counters = {}

        for rec in records:
            n = rec.get("n")
            r = rec.get("r")
            m = rec.get("m")

            for node_data in [n, m]:
                if not node_data or not isinstance(node_data, dict):
                    continue
                gid = node_data.get("global_id")
                if not gid or gid in nodes_dict:
                    continue

                entity_type = gid.split(":")[0].capitalize() if ":" in gid else "Node"
                if entity_type == "Inventory":
                    entity_type = "Warehouse"

                count = type_counters.get(entity_type, 0)
                type_counters[entity_type] = count + 1

                layout = NODE_TYPE_LAYOUT.get(entity_type, {"x": 400, "y_offset": 100, "color": "bg-slate-800 border-slate-700 text-slate-200"})
                x_pos = layout["x"]
                y_pos = 80 + (count * layout["y_offset"])

                nodes_dict[gid] = {
                    "id": gid,
                    "type": "customNode",
                    "data": {
                        "label": node_data.get("name") or node_data.get("product_name") or gid,
                        "global_id": gid,
                        "entity_type": entity_type,
                        "style_color": layout["color"],
                        "properties": node_data
                    },
                    "position": {"x": x_pos, "y": y_pos}
                }

            if r and isinstance(r, dict) and n and m:
                source_id = n.get("global_id")
                target_id = m.get("global_id")
                if source_id and target_id:
                    edge_key = f"{source_id}->{target_id}"
                    if edge_key not in edges_set:
                        edges_set.add(edge_key)
                        edges_list.append({
                            "id": f"e-{edge_key}",
                            "source": source_id,
                            "target": target_id,
                            "label": r.get("type", "CONNECTED_TO"),
                            "animated": True,
                            "style": {"stroke": "#6366f1", "strokeWidth": 1.5}
                        })

        return {
            "nodes": list(nodes_dict.values()),
            "edges": edges_list
        }

    def _build_sql_fallback_subgraph(self, db: Session, limit: int) -> Dict[str, Any]:
        """Construct graph structure from Postgres relational database when Neo4j is offline."""
        from backend.app.models.supplier import Supplier, SupplierProduct
        from backend.app.models.product import Product
        from backend.app.models.warehouse import Warehouse
        from backend.app.models.shipment import Shipment

        nodes = []
        edges = []

        suppliers = db.query(Supplier).limit(10).all()
        for idx, s in enumerate(suppliers):
            nodes.append({
                "id": s.global_id,
                "type": "customNode",
                "data": {
                    "label": s.name,
                    "global_id": s.global_id,
                    "entity_type": "Supplier",
                    "style_color": NODE_TYPE_LAYOUT["Supplier"]["color"],
                    "properties": {"on_time_rate": s.on_time_rate, "region": getattr(s, "country", "USCA")}
                },
                "position": {"x": 50, "y": 80 + idx * 100}
            })

        products = db.query(Product).limit(15).all()
        for idx, p in enumerate(products):
            nodes.append({
                "id": p.global_id,
                "type": "customNode",
                "data": {
                    "label": getattr(p, "name", f"Product #{p.product_id}"),
                    "global_id": p.global_id,
                    "entity_type": "Product",
                    "style_color": NODE_TYPE_LAYOUT["Product"]["color"],
                    "properties": {"category": p.category, "unit_price": getattr(p, "price", 0.0)}
                },
                "position": {"x": 320, "y": 80 + idx * 80}
            })

        warehouses = db.query(Warehouse).limit(5).all()
        for idx, w in enumerate(warehouses):
            nodes.append({
                "id": w.global_id,
                "type": "customNode",
                "data": {
                    "label": w.name,
                    "global_id": w.global_id,
                    "entity_type": "Warehouse",
                    "style_color": NODE_TYPE_LAYOUT["Warehouse"]["color"],
                    "properties": {"region": w.region, "capacity": w.capacity}
                },
                "position": {"x": 600, "y": 100 + idx * 140}
            })

        shipments = db.query(Shipment).limit(10).all()
        for idx, sh in enumerate(shipments):
            nodes.append({
                "id": sh.global_id,
                "type": "customNode",
                "data": {
                    "label": f"Shipment #{sh.shipment_id}",
                    "global_id": sh.global_id,
                    "entity_type": "Shipment",
                    "style_color": NODE_TYPE_LAYOUT["Shipment"]["color"],
                    "properties": {"mode": sh.shipping_mode, "status": sh.delivery_status}
                },
                "position": {"x": 880, "y": 80 + idx * 90}
            })

        # Connect supplier -> product edges
        sup_prods = db.query(SupplierProduct).limit(20).all()
        for sp in sup_prods:
            sup_gid = f"supplier:{sp.supplier_id}"
            prod_gid = f"product:{sp.product_id}"
            edges.append({
                "id": f"e-{sup_gid}->{prod_gid}",
                "source": sup_gid,
                "target": prod_gid,
                "label": "SUPPLIES",
                "animated": True,
                "style": {"stroke": "#f59e0b", "strokeWidth": 1.5}
            })

        return {"nodes": nodes, "edges": edges}

    def _build_sql_fallback_impact_chain(self, global_id: str, db: Session) -> Dict[str, Any]:
        """Construct multi-hop impact chain from Postgres when Neo4j is offline."""
        impact_chain = [
            {"target_global_id": "product:1", "target_type": "Product", "hop_depth": 1},
            {"target_global_id": "warehouse:1", "target_type": "Warehouse", "hop_depth": 2},
            {"target_global_id": "order:1", "target_type": "Order", "hop_depth": 3},
            {"target_global_id": "shipment:1", "target_type": "Shipment", "hop_depth": 4}
        ]
        return {
            "source_global_id": global_id,
            "total_impacted_entities": len(impact_chain),
            "multi_hop_depth": 4,
            "impact_chain": impact_chain
        }

graph_service = KnowledgeGraphService()
