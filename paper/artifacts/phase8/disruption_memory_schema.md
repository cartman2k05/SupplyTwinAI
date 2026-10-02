# Disruption Memory Architecture & Schema Specification (Configuration C)

**Document Path:** `paper/artifacts/phase8/disruption_memory_schema.md`  
**System Layer:** Memory & Reasoning Augmentation (Configuration C)  
**Database:** PostgreSQL (`disruption_memory` table)  

---

## 1. Overview

Disruption Memory provides persistent long-term memory for recurring supply chain disruptions. In **Configuration C** (LLM + GraphRAG + Persistent Memory), when `RecommendationAgent` generates candidate mitigations for an active disruption event, it queries `DisruptionMemory` for top-$K$ historical disruption episodes matching the target entity or event type. The retrieved historical actions and outcome metrics are injected as ground-truth evidence into the agent's prompt, boosting recommendation confidence and accuracy for recurring disruption patterns.

---

## 2. PostgreSQL Relational Schema (`disruption_memory`)

| Column Name | Data Type | Constraints | Description |
|---|---|---|---|
| `memory_id` | `INTEGER` | Primary Key, Auto Increment | Unique record identifier for the disruption memory episode |
| `event_type` | `VARCHAR(64)` | Indexed, Not Null | Classification of disruption (e.g. `SUPPLIER_OUTAGE`, `WEATHER_DELAY`, `INVENTORY_DEFICIT`, `TRANSPORT_DISRUPTION`) |
| `entity_global_id` | `VARCHAR(128)` | Indexed, Not Null | Target entity unique identifier (e.g. `supplier:12`, `shipment:77202`, `warehouse:1`) |
| `scenario_fingerprint` | `VARCHAR(128)` | Indexed, Not Null | Hashed structural feature fingerprint for similarity matching |
| `root_cause` | `TEXT` | Not Null | Descriptive root cause of the disruption event |
| `action_taken` | `VARCHAR(128)` | Not Null | Approved mitigation action class (`SWITCH_SUPPLIER`, `REROUTE_SHIPMENT`, `EXPEDITE_SHIPPING`, `REALLOCATE_INVENTORY`) |
| `outcome_score` | `FLOAT` | Not Null | Quantified success score (0.0 to 100.0) based on recovery time and cost efficiency |
| `resolution_notes` | `TEXT` | Nullable | Supply Chain Manager rationale and resolution details |
| `created_at` | `TIMESTAMP` | Default UTC | Timestamp when memory episode was committed |

---

## 3. Memory Retrieval & Similarity Engine

The similarity search algorithm uses a tiered matching policy:
1. **Tier 1 (Exact Entity Match):** Matches `entity_global_id == target_global_id`.
2. **Tier 2 (Entity Namespace Match):** Matches `entity_global_id LIKE 'supplier:%'` or `shipment:%`.
3. **Tier 3 (Event Type Match):** Matches `event_type == active_event_type`.

Results across tiers are deduplicated, ranked by `outcome_score` descending, and capped at top $K=3$ citations.

---

## 4. Human Governance & Audit Coupling

Recommendations default strictly to status `pending`. When a Supply Chain Manager accepts or rejects a recommendation:
- The decision status (`accepted` or `rejected`) is updated.
- An immutable entry is written to `audit_log` with `user_id`, `user_email`, `timestamp`, `resource_id`, and manager rationale notes.
- Upon approval, a new `DisruptionMemory` entry is committed, feeding future memory retrieval cycles.
