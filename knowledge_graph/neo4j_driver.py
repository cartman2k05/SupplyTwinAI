import os
import logging
from typing import List, Dict, Any, Optional
from backend.app.config import settings

logger = logging.getLogger(__name__)

try:
    from neo4j import GraphDatabase, Driver
    HAS_NEO4J_DRIVER = True
except ImportError:
    HAS_NEO4J_DRIVER = False

class MemoryGraphStore:
    """In-memory fallback graph store when Neo4j database is offline."""
    def __init__(self):
        self.nodes: Dict[str, Dict[str, Any]] = {}
        self.relationships: List[Dict[str, Any]] = []

    def clear(self):
        self.nodes.clear()
        self.relationships.clear()

    def add_node(self, label: str, global_id: str, properties: Dict[str, Any]):
        self.nodes[global_id] = {
            "label": label,
            "global_id": global_id,
            "properties": properties
        }

    def add_relationship(self, source_id: str, target_id: str, rel_type: str, properties: Optional[Dict[str, Any]] = None):
        self.relationships.append({
            "source": source_id,
            "target": target_id,
            "type": rel_type,
            "properties": properties or {}
        })

class Neo4jDriver:
    """Neo4j driver manager with automatic fallback to memory store for test environments."""

    def __init__(self):
        self.uri = getattr(settings, "NEO4J_URI", os.getenv("NEO4J_URI", "bolt://localhost:7687"))
        self.user = getattr(settings, "NEO4J_USER", os.getenv("NEO4J_USER", "neo4j"))
        self.password = getattr(settings, "NEO4J_PASSWORD", os.getenv("NEO4J_PASSWORD", "supplytwin123"))
        
        self.driver: Optional[Any] = None
        self.is_connected = False
        self.memory_store = MemoryGraphStore()

        self._connect()

    def _connect(self):
        if not HAS_NEO4J_DRIVER:
            logger.warning("[Neo4j] Python neo4j package not installed. Using in-memory fallback graph.")
            self.is_connected = False
            return

        try:
            self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
            # Test connectivity
            self.driver.verify_connectivity()
            self.is_connected = True
            logger.info(f"[Neo4j] Successfully connected to Neo4j cluster at {self.uri}")
        except Exception as e:
            logger.warning(f"[Neo4j] Could not connect to Neo4j at {self.uri} ({e}). Operating in memory fallback mode.")
            self.driver = None
            self.is_connected = False

    def close(self):
        if self.driver:
            self.driver.close()

    def execute_query(self, cypher: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Execute read Cypher query with parameters."""
        if self.is_connected and self.driver:
            with self.driver.session() as session:
                result = session.run(cypher, parameters or {})
                return [record.data() for record in result]
        else:
            # Fallback memory query handler
            return self._execute_memory_query(cypher, parameters or {})

    def execute_write(self, cypher: str, parameters: Optional[Dict[str, Any]] = None) -> Any:
        """Execute write Cypher query with parameters."""
        if self.is_connected and self.driver:
            with self.driver.session() as session:
                return session.execute_write(lambda tx: tx.run(cypher, parameters or {}).data())
        else:
            return self._execute_memory_write(cypher, parameters or {})

    def _execute_memory_write(self, cypher: str, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Simulate Cypher MERGE/CREATE writes in memory fallback store."""
        if "MERGE (n:" in cypher or "CREATE (n:" in cypher:
            # Extract label
            label = cypher.split("(n:")[1].split(" ")[0].split("{")[0]
            global_id = params.get("global_id")
            if global_id:
                self.memory_store.add_node(label, global_id, params)
        elif "-[:" in cypher:
            source_id = params.get("source_id") or params.get("from_id")
            target_id = params.get("target_id") or params.get("to_id")
            rel_type = cypher.split("-[:")[1].split("]->")[0].split(" ")[0]
            if source_id and target_id:
                self.memory_store.add_relationship(source_id, target_id, rel_type, params)
        return []

    def _execute_memory_query(self, cypher: str, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Simulate graph queries in memory fallback store."""
        if "count(" in cypher.lower():
            if "node" in cypher.lower() or "labels" in cypher.lower() or "n" in cypher.lower():
                return [{"node_count": len(self.memory_store.nodes)}]
            return [{"rel_count": len(self.memory_store.relationships)}]

        if "RETURN n, r, m" in cypher or "MATCH" in cypher:
            nodes_list = [
                {"id": n["global_id"], "label": n["label"], "properties": n["properties"]}
                for n in self.memory_store.nodes.values()
            ]
            edges_list = [
                {"source": r["source"], "target": r["target"], "type": r["type"]}
                for r in self.memory_store.relationships
            ]
            return [{"nodes": nodes_list, "relationships": edges_list}]
        return []

graph_driver = Neo4jDriver()
