# SupplyTwinAI — Phase 5 Execution Plan (Knowledge Graph Construction & Visualization)

**Document Path:** `docs/plans/phase-5-plan.md`  
**Status:** Pending Approval  
**Author:** Lead Engineer (AI Pair Programmer)  
**Date:** 2026-10-01  

---

## 1. Goal

Construct the Neo4j Knowledge Graph schema, Postgres-to-Neo4j initial ETL loader and background incremental sync module, multi-hop Cypher queries ($\ge 3$ hops), versioned Graph REST API endpoints (`/api/v1/graph/`), interactive React Flow Digital Twin Graph view on the frontend, and initial evaluation metrics specification in `evaluation/` (§4.2 REQ-1 to REQ-4, §4.7 REQ-3, §5.1 NFR-P3).

---

## 2. SRS Requirements Covered

* **§4.2 REQ-1 & REQ-2:** Knowledge Graph node labels (`Supplier`, `Product`, `Warehouse`, `Order`, `Shipment`, `Vehicle`, `DisruptionEvent`) and relationship types (`SUPPLIES`, `STOCKED_AT`, `PLACED`, `CONTAINS`, `FULFILLED_FROM`, `SHIPS_VIA`, `DELAYED_BY`, `AFFECTS`). Parameterized Cypher queries only.
* **§4.2 REQ-3:** Incremental background sync service from PostgreSQL to Neo4j within 30 seconds of PostgreSQL entity/state updates.
* **§4.2 REQ-4:** Parameterized multi-hop graph queries (3+ hops: e.g., Supplier $\rightarrow$ Product $\rightarrow$ Warehouse $\rightarrow$ Order $\rightarrow$ Shipment impact chain).
* **§4.7 REQ-3:** Interactive Digital Twin Graph View component built with React Flow in the frontend displaying entity nodes, directed edges, risk status colors, and filter controls.
* **§5.1 NFR-P3:** Neo4j synchronization latency $< 30$ seconds.

---

## 3. Files and Modules to Create or Change

```text
SupplyTwinAI/
├── knowledge_graph/
│   ├── neo4j_driver.py             # Neo4j driver connection manager with offline fallback handler
│   ├── schema.py                   # Unique constraint creation on global_id for node labels
│   └── etl_sync.py                 # Full & incremental Postgres-to-Neo4j sync engine
├── backend/
│   ├── app/
│   │   ├── api/v1/
│   │   │   ├── graph.py            # REST endpoints (/subgraph, /impact, /sync, /stats)
│   │   │   └── router.py           # Includes graph router under /api/v1
│   │   └── services/
│   │       └── graph_service.py    # Graph query service executing multi-hop Cypher queries
│   └── tests/
│       └── test_knowledge_graph.py # Test suite for schema, loader, sync latency, & Cypher queries
├── frontend/
│   ├── package.json                # Add reactflow dependency
│   ├── src/
│   │   ├── pages/
│   │   │   └── DigitalTwinGraph.jsx # Interactive React Flow graph visualization page
│   │   ├── components/
│   │   │   └── layout/
│   │   │       └── Sidebar.jsx     # Add "Digital Twin Graph" link
│   │   └── App.jsx                 # Add /graph route
├── evaluation/
│   └── metrics_draft.md            # Initial evaluation harness metric definitions & scenario catalog
```

---

## 4. Schema and API Changes

### 4.1 Neo4j Graph Schema Specification
* **Node Labels:**
  - `Supplier` (`global_id`, `name`, `on_time_rate`, `defect_rate`, `region`, `is_synthetic`)
  - `Product` (`global_id`, `product_name`, `category`, `unit_price`)
  - `Warehouse` (`global_id`, `name`, `region`, `latitude`, `longitude`, `capacity`)
  - `Order` (`global_id`, `order_status`, `market`, `order_region`, `order_date`)
  - `Shipment` (`global_id`, `shipping_mode`, `days_scheduled`, `days_real`, `delivery_status`)
  - `Vehicle` (`global_id`, `vehicle_type`, `capacity`, `status`)
  - `DisruptionEvent` (`global_id`, `scenario_id`, `event_type`, `severity`, `status`)

* **Relationship Types:**
  - `(Supplier)-[:SUPPLIES]->(Product)`
  - `(Product)-[:STOCKED_AT]->(Warehouse)`
  - `(Customer)-[:PLACED]->(Order)`
  - `(Order)-[:CONTAINS]->(Product)`
  - `(Order)-[:FULFILLED_FROM]->(Warehouse)`
  - `(Shipment)-[:SHIPS_VIA]->(Vehicle)`
  - `(Shipment)-[:DELAYED_BY]->(DisruptionEvent)`
  - `(DisruptionEvent)-[:AFFECTS]->(Supplier | Warehouse | Shipment | Product)`

### 4.2 Versioned REST Endpoints (`/api/v1/graph`)
* `GET /api/v1/graph/subgraph` $\rightarrow$ Returns nodes and edges formatted for React Flow graph rendering
* `GET /api/v1/graph/impact` $\rightarrow$ Traverses 3+ hop impact chain for a target entity `global_id`
* `POST /api/v1/graph/sync` $\rightarrow$ Triggers on-demand Postgres-to-Neo4j sync run
* `GET /api/v1/graph/stats` $\rightarrow$ Returns node and relationship count statistics

---

## 5. Test List (Phase 5)

* `test_neo4j_schema_constraints`: Verify unique `global_id` constraints created for all node labels.
* `test_postgres_to_neo4j_sync`: Verify syncing Postgres entities/relationships into Neo4j nodes and edges.
* `test_multihop_cypher_queries`: Verify 3+ hop impact traversal Cypher queries (Supplier $\rightarrow$ Product $\rightarrow$ Warehouse $\rightarrow$ Order $\rightarrow$ Shipment).
* `test_graph_api_endpoints`: Test REST API endpoints (`/subgraph`, `/impact`, `/sync`, `/stats`).
* `test_sync_latency_benchmark`: Verify background sync completes in $< 30$ seconds.

---

## 6. Measurable Acceptance Criteria

* Neo4j populated with namespaced `global_id` nodes and relationships.
* Multi-hop query ("shipments affected if Supplier X fails") returns correct results verified against SQL.
* Background sync latency measured at $< 30$ seconds (§5.1 NFR-P3).
* Interactive React Flow graph visualization renders nodes, edges, and status colors on frontend.
* All backend pytest unit tests pass.
* Frontend production build compiles cleanly.

---

## 7. Risks and Technical Mitigations

1. **Neo4j Offline in Local / CI Environments:**
   * *Mitigation:* Implement graceful fallback handler in `neo4j_driver.py` with mock memory graph provider for pytest runs when Neo4j container is unreachable.
2. **High Node Count Rendering Performance in React Flow:**
   * *Mitigation:* Apply viewport windowing, sub-graph node limit parameters (default top 200 active nodes), and category filtering.

---

## 8. Open Questions

None. Neo4j schema and 3+ hop Cypher traversal specifications were confirmed in `DECISIONS.md` §3.8.

---

## 9. Paper Artifacts to Capture (Phase 5)

* `paper/artifacts/phase5/graph_schema_diagram.md` (Neo4j Cypher schema & relationship taxonomy)
* `paper/artifacts/phase5/graph_node_edge_counts.json` (Node & relationship count breakdown)
* `paper/artifacts/phase5/graph_sync_latency_log.json` (Measured sync latency benchmark < 30s)

---

## 10. Explicit List of What is Out of Scope for Phase 5

* LangChain GraphRAG retriever integration (Deferred to Phase 6)
* LangGraph multi-agent decision nodes (Deferred to Phase 7)
* Recommendation memory vector store (Deferred to Phase 8)
