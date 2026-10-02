# SupplyTwinAI — Phase 9 Execution Plan (Evaluation Harness & Comparative Benchmarking)

**Document Path:** `docs/plans/phase-9-plan.md`  
**Status:** Pending Approval  
**Author:** Lead Engineer (AI Pair Programmer)  
**Date:** 2026-10-01  

---

## 1. Goal

Build and execute the reproducible automated evaluation harness (`evaluation/run_eval.py` and `evaluation/metrics.py`) comparing system Configurations A (Base LLM), B (LLM + GraphRAG), and C (LLM + GraphRAG + Persistent Memory) across 60+ synthetic disruption scenarios with simulator ground truth labels (§5 Configuration A/B/C, DECISIONS.md §5, ROADMAP_v2.md Phase 9). Compute programmatic precision, recall, hallucination rate, grounding rate, recommendation validity rate, memory effect, and latency metrics; output raw execution logs to `evaluation/results/`; generate comparative analysis tables and paper figures.

---

## 2. SRS Requirements Covered

* **§5 Configuration Comparative Benchmark:**
  - **Configuration A (Base LLM):** Zero-shot direct LLM prompt without Graph Context or Disruption Memory.
  - **Configuration B (LLM + GraphRAG):** Gemini LLM with Neo4j 3-hop subgraph context retrieval.
  - **Configuration C (LLM + GraphRAG + Persistent Memory):** Full system with Neo4j subgraph context + PostgreSQL disruption memory citations.
* **DECISIONS.md §5 Evaluation Metrics & Reproducibility Protocol:**
  - Programmatic measurement of Entity Precision ($P_{\text{entity}}$), Entity Recall ($R_{\text{entity}}$), Hallucinated-ID Rate ($H_{\text{rate}}$), Grounding Rate ($G_{\text{rate}}$), Recommendation Action Validity ($V_{\text{action}}$), Memory Effect, and Latency/Token costs.
  - Deterministic evaluation using recorded seeds, Open-Meteo & NewsAPI record-and-replay cache, and automated "oracle manager" approval simulation.
  - Save all raw evaluation runs into `evaluation/results/<run_id>/` with config hash and execution timestamps.

---

## 3. Files and Modules to Create or Change

```text
SupplyTwinAI/
├── evaluation/
│   ├── run_eval.py                   # Automated evaluation harness script running Configs A, B, C across scenario catalog
│   ├── metrics.py                    # Programmatic metric calculation engine (precision, recall, hallucination, grounding)
│   ├── scenario_generator.py          # Scenario catalog generator producing 60+ ground-truth labeled disruption scenarios
│   ├── oracle_manager.py              # Simulated human manager policy for automated approval workflow testing
│   └── results/                       # Output directory for raw JSON/CSV evaluation run logs
├── backend/
│   └── tests/
│       └── test_evaluation_harness.py # Unit test verifying metric calculation functions & evaluation runner sanity
└── paper/
    └── artifacts/
        └── phase9/
            ├── evaluation_summary_table.md    # Full comparative metrics summary matrix (A vs B vs C)
            ├── scenario_ground_truth_catalog.json # Catalog of 60 evaluation scenarios with ground-truth labels
            └── ablation_and_latency_charts.json   # Precision/recall, hallucination, and latency distribution benchmarks
```

---

## 4. Schema and API Changes

None. Evaluation harness runs as a standalone Python test suite and CLI script (`python -m evaluation.run_eval`) calling existing backend REST endpoints (`/api/v1/agents/trigger`, `/api/v1/recommendations`, `/api/v1/chat/query`) and database services.

---

## 5. Test List (Phase 9)

* `test_scenario_generator_ground_truth`: Verify scenario generator creates valid ground-truth scenario schemas with unique IDs and acceptable action classes.
* `test_metric_precision_recall_calculation`: Verify `metrics.py` accurately calculates precision, recall, and F1-score against ground truth entity lists.
* `test_hallucination_rate_calculation`: Verify `metrics.py` detects non-existent entity IDs cited in agent outputs against database records.
* `test_oracle_manager_approval_simulation`: Verify `oracle_manager.py` evaluates candidate recommendations against ground truth action classes and submits approve/reject API calls.
* `test_full_eval_run_reproducibility`: Verify running `evaluation/run_eval.py` twice with fixed seed yields identical metric outputs.

---

## 6. Measurable Acceptance Criteria

* 60+ synthetic evaluation disruption scenarios generated across 5 disruption categories (`SUPPLIER_OUTAGE`, `SHIPMENT_DELAY`, `INVENTORY_DEFICIT`, `WEATHER_EVENT`, `GEOPOLITICAL_NEWS`).
* Complete automated evaluation run executes Configurations A, B, and C with 3 repetitions per scenario type.
* Raw prompt, context, response, and metric logs saved into `evaluation/results/eval_run_<timestamp>.json`.
* Comparative results demonstrate:
  - Configuration B (GraphRAG) reduces hallucination rate ($H_{\text{rate}}$) significantly compared to Configuration A (Base LLM).
  - Configuration C (Memory) increases recommendation confidence and validity ($V_{\text{action}}$) on repeated disruption scenarios compared to Configuration B.
* All backend pytest unit tests pass (49 original + new evaluation harness tests).
* Frontend production build compiles cleanly.

---

## 7. Risks and Technical Mitigations

1. **LLM Execution Latency & Quota Rate Limits during 180+ Evaluation Calls:**
   - *Mitigation:* `run_eval.py` implements configurable request pacing delay (e.g. 1.0 s between LLM calls) and fallback to recorded response cache if Gemini API rate limits occur.
2. **Evaluation Metric Non-Determinism:**
   - *Mitigation:* Fix random seeds for scenario generation and compute mean $\pm$ standard deviation across 3 repeated evaluation passes.

---

## 8. Open Questions

None. Evaluation metric definitions and Configuration A/B/C comparison parameters are locked in `DECISIONS.md` §5 and `ROADMAP_v2.md` Phase 9.

---

## 9. Paper Artifacts to Capture (Phase 9)

* `paper/artifacts/phase9/evaluation_summary_table.md` (Full benchmark metrics matrix across Configs A vs B vs C)
* `paper/artifacts/phase9/scenario_ground_truth_catalog.json` (Catalog of 60 evaluation scenarios with ground-truth labels)
* `paper/artifacts/phase9/ablation_and_latency_charts.json` (Precision/recall, hallucination, and latency distribution benchmarks)

---

## 10. Explicit List of What is Out of Scope for Phase 9

* System Admin config screen & CSV report export UI (Phase 10)
* Cloud deployment to Render / Vercel (Phase 11)

---

**STOP & WAIT:** Plan written. Awaiting user approval before proceeding to implementation.
