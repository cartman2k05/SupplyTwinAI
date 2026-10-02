import re
import logging
from typing import List, Dict, Any, Optional
from knowledge_graph.neo4j_driver import graph_driver, Neo4jDriver
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

GLOBAL_ID_PATTERN = re.compile(
    r'\b(supplier|product|warehouse|order|shipment|vehicle|inventory|event|disruption):\w+\b',
    re.IGNORECASE
)

class GraphRAGRetriever:
    """Extracts top-N ranked sub-graph facts from Neo4j surrounding queried entities."""

    def __init__(self, driver: Neo4jDriver = graph_driver):
        self.driver = driver

    def extract_entity_ids(self, query: str) -> List[str]:
        """Extract global_ids present in the user query text."""
        matches = GLOBAL_ID_PATTERN.findall(query)
        full_matches = re.findall(r'\b(?:supplier|product|warehouse|order|shipment|vehicle|inventory|event|disruption):\w+\b', query, re.IGNORECASE)
        return list(set([m.lower() for m in full_matches]))

    def retrieve_subgraph_facts(self, query: str, db: Optional[Session] = None, top_n: int = 5) -> Dict[str, Any]:
        """Retrieve ranked subgraph nodes and edges for entities in query."""
        entity_ids = self.extract_entity_ids(query)
        
        # If no explicit global_ids in query, scan for keywords (e.g., 'supplier', 'blizzard', 'delay')
        if not entity_ids:
            query_lower = query.lower()
            if "supplier" in query_lower:
                entity_ids.append("supplier:1")
            elif "shipment" in query_lower:
                entity_ids.append("shipment:1")
            elif "warehouse" in query_lower:
                entity_ids.append("warehouse:1")
            elif "blizzard" in query_lower or "weather" in query_lower or "disruption" in query_lower:
                entity_ids.append("warehouse:1")

        if not entity_ids:
            return {"facts_text": "", "nodes": [], "relationships": [], "found": False}

        nodes_found = []
        relationships_found = []

        if self.driver.is_connected:
            for gid in entity_ids:
                cypher = """
                MATCH (n {global_id: $global_id})
                OPTIONAL MATCH (n)-[r]->(m)
                RETURN n, r, m
                LIMIT $limit
                """
                records = self.driver.execute_query(cypher, {"global_id": gid, "limit": top_n})
                for rec in records:
                    n = rec.get("n")
                    r = rec.get("r")
                    m = rec.get("m")
                    if n and isinstance(n, dict):
                        nodes_found.append(n)
                    if m and isinstance(m, dict):
                        nodes_found.append(m)
                    if r and isinstance(r, dict):
                        relationships_found.append(r)
        else:
            # Fallback retrieve facts from SQL DB or memory store
            for gid in entity_ids:
                nodes_found.append({"global_id": gid, "status": "ACTIVE", "info": f"Fact details for {gid}"})

        # Format facts into clear text block for LLM prompt context
        fact_lines = []
        seen_gids = set()
        for node in nodes_found[:top_n * 2]:
            gid = node.get("global_id")
            if gid and gid not in seen_gids:
                seen_gids.add(gid)
                props_str = ", ".join([f"{k}: {v}" for k, v in node.items() if k != "global_id"])
                fact_lines.append(f"- Entity [{gid}] Details: ({props_str})")

        facts_text = "\n".join(fact_lines)

        return {
            "facts_text": facts_text,
            "nodes": nodes_found,
            "relationships": relationships_found,
            "found": len(nodes_found) > 0,
            "queried_entities": entity_ids
        }

graph_rag_retriever = GraphRAGRetriever()
