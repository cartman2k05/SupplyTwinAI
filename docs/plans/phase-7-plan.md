# SupplyTwinAI — Phase 7 Execution Plan (Multi-Agent Layer & LangGraph Orchestration)

**Document Path:** `docs/plans/phase-7-plan.md`  
**Status:** Pending Approval  
**Author:** Lead Engineer (AI Pair Programmer)  
**Date:** 2026-10-01  

---

## 1. Goal

Implement the six specialized supply chain agents (`SupplierAgent`, `ShipmentAgent`, `InventoryAgent`, `ExternalIntelligenceAgent`, `RiskAssessmentAgent`, `RecommendationAgent`), LangGraph StateGraph parallel orchestration workflow, config-driven risk weights and threshold evaluation, PostgreSQL `agent_outputs` reasoning trail persistence, Open-Meteo/NewsAPI record-and-replay external signal handling, and graceful degradation (§4.4 REQ-1 to REQ-8, §5.1 NFR-P1).

---

## 2. SRS Requirements Covered

* **§4.4 REQ-1 to REQ-6:** Implementation of the six SRS supply chain agents:
  1. `SupplierAgent` (evaluates supplier reliability, defect rates, outage signals)
  2. `ShipmentAgent` (evaluates shipment route delay predictions, transit status)
  3. `InventoryAgent` (evaluates warehouse inventory stock buffers, reorder points, stockout risk)
  4. `ExternalIntelligenceAgent` (evaluates Open-Meteo weather signals & NewsAPI geopolitical events, with record-and-replay cache for offline/reproducible execution)
  5. `RiskAssessmentAgent` (waits for all 4 Stage 1 outputs, computes composite risk score using `agent_config` weights: supplier 0.30, shipment 0.30, inventory 0.20, external 0.20; assigns Low <33, Medium 33-66, High >66 risk bands)
  6. `RecommendationAgent` (triggered if composite risk > alert_threshold [default 60.0]; generates mitigation action classes like `SWITCH_SUPPLIER`, `REROUTE_SHIPMENT`, `EXPEDITE_SHIPPING`, `REALLOCATE_INVENTORY`)
* **§4.4 Orchestration Order:** LangGraph StateGraph DAG with 4-way parallel Stage 1 execution, Stage 2 Risk aggregation, and Stage 3 conditional Recommendation triggering.
* **§4.4 REQ-7:** Complete reasoning trail persistence in PostgreSQL `agent_outputs` table.
* **§4.4 REQ-8:** Graceful Degradation: If one agent encounters an error or timeout, it emits a degraded output with a `"stale"` or `"degraded"` flag, allowing downstream Risk & Recommendation agents to proceed without failing the execution graph.

---

## 3. Files and Modules to Create or Change

```text
SupplyTwinAI/
├── agents/
│   ├── base_agent.py               # Abstract base agent class, output schema, & DB logging helper
│   ├── supplier_agent.py           # SupplierAgent evaluating supplier reliability & outages
│   ├── shipment_agent.py           # ShipmentAgent evaluating transit delays & shipping modes
│   ├── inventory_agent.py          # InventoryAgent evaluating warehouse inventory stock buffers
│   ├── external_agent.py           # ExternalIntelligenceAgent (Open-Meteo & NewsAPI record/replay)
│   ├── risk_agent.py               # RiskAssessmentAgent calculating weighted composite risk scores
│   ├── recommendation_agent.py     # RecommendationAgent proposing human-approved mitigations
│   └── orchestrator.py             # LangGraph StateGraph DAG parallel runner
├── backend/
│   ├── app/
│   │   ├── api/v1/
│   │   │   ├── agents.py           # REST endpoints (/trigger, /outputs)
│   │   │   └── router.py           # Includes agents router under /api/v1
│   │   └── services/
│   │       └── agent_service.py    # Multi-agent execution service
│   └── tests/
│       └── test_multi_agent.py     # Test suite for parallel execution, risk weights, & degradation
```

---

## 4. Schema and API Changes

### 4.1 Table Operations (`agent_outputs` table in PostgreSQL)
* `output_id` (Integer PK)
* `agent_name` (String: `'SupplierAgent'`, `'ShipmentAgent'`, `'InventoryAgent'`, `'ExternalAgent'`, `'RiskAgent'`, `'RecommendationAgent'`)
* `target_global_id` (String)
* `reasoning_output` (Text JSON)
* `risk_score` (Float)
* `status` (String: `'SUCCESS'`, `'DEGRADED'`, `'FAILED'`)
* `execution_time_ms` (Float)
* `created_at` (DateTime)

### 4.2 Versioned REST Endpoints (`/api/v1/agents`)
* `POST /api/v1/agents/trigger` $\rightarrow$ Triggers multi-agent pipeline for a target entity or event global_id
* `GET /api/v1/agents/outputs` $\rightarrow$ Retrieves stored agent reasoning trails from PostgreSQL `agent_outputs`

---

## 5. Test List (Phase 7)

* `test_langgraph_parallel_orchestration`: Verify triggering multi-agent pipeline executes 4 Stage 1 agents concurrently before RiskAssessmentAgent.
* `test_risk_assessment_composite_weights`: Verify RiskAssessmentAgent computes correct weighted risk score from `agent_config` weights.
* `test_recommendation_conditional_trigger`: Verify RecommendationAgent runs only when composite risk score exceeds the alert threshold (60.0).
* `test_graceful_degradation_handling`: Verify if ExternalIntelligenceAgent fails or times out, it flags `"status": "DEGRADED"` and RiskAssessmentAgent completes successfully using remaining inputs.
* `test_agent_outputs_persistence`: Verify all intermediate reasoning steps and agent outputs are saved in PostgreSQL `agent_outputs` table.
* `test_agent_api_endpoints`: Test REST endpoints (`POST /trigger`, `GET /outputs`).

---

## 6. Measurable Acceptance Criteria

* Disrupting an entity triggers all 6 LangGraph agents in proper sequence.
* RiskAssessmentAgent waits for all four Stage 1 parallel agent outputs before computing risk score.
* One failing agent does not stop the others (graceful degradation verified).
* Full reasoning trail reconstructable from stored outputs in PostgreSQL `agent_outputs` table.
* All backend pytest unit tests pass.
* Frontend production build compiles cleanly.

---

## 7. Risks and Technical Mitigations

1. **External API Failures (Open-Meteo / NewsAPI timeouts or rate limits):**
   * *Mitigation:* Built-in record-and-replay cache in `external_agent.py` serving cached weather/news signals during offline or test runs.
2. **LangGraph State Concurrency Race Conditions:**
   * *Mitigation:* Explicit state reducer dict merging in LangGraph StateGraph state definition.

---

## 8. Open Questions

None. Risk weights (supplier 0.30, shipment 0.30, inventory 0.20, external 0.20) and risk thresholds (33/66/60) were established in `DECISIONS.md` §4.

---

## 9. Paper Artifacts to Capture (Phase 7)

* `paper/artifacts/phase7/agent_orchestration_diagram.md` (LangGraph StateGraph execution DAG)
* `paper/artifacts/phase7/agent_latency_profile.json` (Per-agent execution latency benchmarks)
* `paper/artifacts/phase7/agent_config_weights.json` (Configurable weights and threshold specification)

---

## 10. Explicit List of What is Out of Scope for Phase 7

* Disruption Memory vector store retrieval (Deferred to Phase 8)
* Recommendation Approval Center Accept/Reject decision persistence (Deferred to Phase 8)
* Full evaluation harness benchmark automation across 60+ scenarios (Deferred to Phase 9)
