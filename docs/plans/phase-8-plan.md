# SupplyTwinAI — Phase 8 Execution Plan (Disruption Memory, Similar Disruption Search & Recommendation Approval Center)

**Document Path:** `docs/plans/phase-8-plan.md`  
**Status:** Pending Approval  
**Author:** Lead Engineer (AI Pair Programmer)  
**Date:** 2026-10-01  

---

## 1. Goal

Implement persistent PostgreSQL Disruption Memory (`disruption_memory` table and similarity search engine), integrate historical memory retrieval into `RecommendationAgent` to enhance recommendation quality during recurring disruptions, build the human-in-the-loop Recommendation Approval Center UI (`RecommendationCenter.jsx`) with explicit Accept/Reject actions and audit trail logging, enforce human governance safety constraints (recommendations NEVER auto-apply), and capture Phase 8 paper artifacts (§4.4 REQ-6, REQ-7, §5.2 NFR-S1, DECISIONS.md §3.7, §5 Configuration C).

---

## 2. SRS Requirements Covered

* **§4.4 REQ-6 & REQ-7 (Recommendation Generation & Memory Persistence):**
  - Store completed disruption mitigation outcomes, manager actions, recovery times, and cost impacts in PostgreSQL `disruption_memory`.
  - Retrieve similar past disruption memories when generating mitigation proposals for active events.
* **§5.2 NFR-S1 & AGENTS.md §5 (Safety and Human Governance):**
  - Recommendations are NEVER auto-applied regardless of confidence threshold or risk score.
  - Recommendation status transitions (`pending` $\rightarrow$ `accepted` or `rejected`) occur exclusively via explicit human supply chain manager action.
  - Every decision logs user identity, timestamp, decision rationale, and outcome to PostgreSQL `audit_log`.
* **DECISIONS.md §5 (Configuration C Specification):**
  - Configuration C (LLM + GraphRAG + Persistent Memory) evaluation capability enabling comparative measurements against Configuration B (without memory).

---

## 3. Files and Modules to Create or Change

```text
SupplyTwinAI/
├── backend/
│   ├── app/
│   │   ├── models/
│   │   │   └── memory.py              # DisruptionMemory SQLAlchemy ORM model
│   │   ├── services/
│   │   │   └── memory_service.py       # Disruption Memory storage & similarity search engine
│   │   ├── api/v1/
│   │   │   ├── recommendations.py      # Recommendation management REST endpoints (list, approve, reject)
│   │   │   └── router.py              # Include recommendations router under /api/v1
│   │   └── schemas/
│   │       └── recommendation.py      # Pydantic schemas for recommendation responses and decision payloads
│   └── tests/
│       └── test_recommendation_memory.py # Test suite for memory retrieval, approval workflow, & RBAC audit
├── agents/
│   └── recommendation_agent.py        # Enhanced RecommendationAgent querying memory_service before candidate generation
├── frontend/
│   └── src/
│       ├── pages/
│       │   └── RecommendationCenter.jsx # Human-in-the-Loop Recommendation Approval Center UI
│       ├── components/
│       │   └── Navigation.jsx          # Add Recommendation Center link with pending badge count
│       └── App.jsx                     # Add /recommendations route
└── paper/
    └── artifacts/
        └── phase8/
            ├── disruption_memory_schema.md           # Memory data model & retrieval architecture
            ├── worked_disruption_example.json        # Repeated disruption trace comparing memory enrichment
            └── recommendation_audit_trail_sample.json # Sample manager decision audit records
```

---

## 4. Schema and API Changes

### 4.1 Relational DB Schema (`disruption_memory` in PostgreSQL)
* `memory_id` (Integer PK)
* `global_id` (String: target entity global ID e.g. `'supplier:12'`, `'shipment:77202'`)
* `event_type` (String: `'SUPPLIER_OUTAGE'`, `'WEATHER_DELAY'`, `'INVENTORY_DEFICIT'`, `'TRANSPORT_DISRUPTION'`)
* `severity` (String: `'MEDIUM'`, `'HIGH'`, `'CRITICAL'`)
* `feature_vector` (JSON: entity attributes, initial risk score, category, affected region)
* `action_taken` (String: `'SWITCH_SUPPLIER'`, `'REROUTE_SHIPMENT'`, `'EXPEDITE_SHIPPING'`, `'REALLOCATE_INVENTORY'`)
* `outcome_metrics` (JSON: `{"recovery_time_days": 2.5, "cost_impact_usd": 1450.0, "success": true}`)
* `manager_decision` (String: `'ACCEPTED'`, `'REJECTED'`)
* `notes` (Text: manager notes or rationale)
* `created_at` (DateTime)

### 4.2 Versioned REST Endpoints (`/api/v1/recommendations`)
* `GET /api/v1/recommendations` $\rightarrow$ Query stored recommendations with optional status filter (`pending`, `accepted`, `rejected`).
* `POST /api/v1/recommendations/{rec_id}/approve` $\rightarrow$ Manager accepts candidate action. Updates status to `'accepted'`, logs to `audit_log`, and records outcome into `disruption_memory`.
* `POST /api/v1/recommendations/{rec_id}/reject` $\rightarrow$ Manager rejects candidate action with rationale notes. Updates status to `'rejected'`, logs to `audit_log`, and updates `disruption_memory`.
* `GET /api/v1/recommendations/memories/search` $\rightarrow$ Query similar past disruption memories for an entity or event type.

---

## 5. Test List (Phase 8)

* `test_store_and_search_disruption_memory`: Verify storing past disruption events and retrieving top-K similar memory records based on target entity and event type.
* `test_recommendation_agent_memory_enrichment`: Verify `RecommendationAgent` retrieves prior disruption memories and includes cited memory evidence in `reasoning_output`.
* `test_recommendation_approval_workflow`: Verify manager `approve` endpoint transitions status from `pending` to `accepted`, logs `audit_log`, and generates a `disruption_memory` entry.
* `test_recommendation_rejection_workflow`: Verify manager `reject` endpoint transitions status from `pending` to `rejected` with required rationale notes.
* `test_recommendations_never_auto_apply`: Verify recommendation status remains `pending` upon creation regardless of risk score or confidence value.
* `test_recommendation_rbac_protection`: Verify viewer role cannot approve/reject recommendations (403 Forbidden).

---

## 6. Measurable Acceptance Criteria

* Recommendations created by `RecommendationAgent` default strictly to status `pending`.
* Accepting/Rejecting a recommendation updates status, writes an entry to `audit_log`, and persists a record in `disruption_memory`.
* Re-running multi-agent evaluation on a repeated disruption scenario retrieves prior memory records and cites them in the recommendation reasoning.
* Recommendation Center UI renders pending/accepted/rejected tabs with responsive card layouts and action modals.
* All backend pytest unit tests pass (44 original + new memory/recommendation tests).
* Frontend production build compiles cleanly.

---

## 7. Risks and Technical Mitigations

1. **Cold-Start Memory Retrieval (Empty Memory Table):**
   - *Mitigation:* `memory_service.py` gracefully handles empty memory tables by returning empty past memory lists, allowing `RecommendationAgent` to generate default heuristics without error.
2. **Audit Trail Synchronization:**
   - *Mitigation:* Execute recommendation status update, `audit_log` insertion, and `disruption_memory` creation inside a single PostgreSQL database transaction block (`db.commit()`).

---

## 8. Open Questions

None. Human governance rules (no auto-apply) and composite memory requirements are locked in `AGENTS.md` §5 and `DECISIONS.md` §5.

---

## 9. Paper Artifacts to Capture (Phase 8)

* `paper/artifacts/phase8/disruption_memory_schema.md` (Memory data model, similarity retrieval metric, storage layout)
* `paper/artifacts/phase8/worked_disruption_example.json` (Worked trace comparing baseline recommendation vs memory-enriched recommendation)
* `paper/artifacts/phase8/recommendation_audit_trail_sample.json` (Sample audit log records demonstrating human-in-the-loop decision capture)

---

## 10. Explicit List of What is Out of Scope for Phase 8

* Full evaluation harness script across 60+ synthetic scenarios (Phase 9)
* Admin ETL and weight config validation screens (Phase 10)
* Render / Vercel cloud deployment (Phase 11)

---

**STOP & WAIT:** Plan written. Awaiting user approval before proceeding to implementation.
