import logging
from typing import List
from knowledge_graph.neo4j_driver import graph_driver, Neo4jDriver

logger = logging.getLogger(__name__)

NODE_LABELS = [
    "Supplier",
    "Product",
    "Warehouse",
    "Order",
    "Shipment",
    "Vehicle",
    "DisruptionEvent"
]

def ensure_graph_schema(driver: Neo4jDriver = graph_driver) -> List[str]:
    """Ensures unique global_id constraints exist for all Neo4j node labels."""
    created_constraints = []
    
    if not driver.is_connected:
        logger.info("[Neo4j Schema] Driver operating in fallback mode. Mocking constraint creation.")
        return [f"constraint_{label.lower()}_global_id" for label in NODE_LABELS]

    for label in NODE_LABELS:
        constraint_name = f"constraint_{label.lower()}_global_id"
        cypher = (
            f"CREATE CONSTRAINT {constraint_name} IF NOT EXISTS "
            f"FOR (n:{label}) REQUIRE n.global_id IS UNIQUE"
        )
        try:
            driver.execute_write(cypher)
            created_constraints.append(constraint_name)
            logger.info(f"[Neo4j Schema] Ensured constraint: {constraint_name}")
        except Exception as e:
            logger.error(f"[Neo4j Schema] Failed creating constraint {constraint_name}: {e}")

    return created_constraints
