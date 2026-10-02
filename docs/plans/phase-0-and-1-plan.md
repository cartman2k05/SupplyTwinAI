# SupplyTwinAI — Phase 0 & Phase 1 Execution Plan

**Document Path:** `docs/plans/phase-0-and-1-plan.md`  
**Status:** Approved (with modifications)  
**Author:** Lead Engineer (AI Pair Programmer)  
**Date:** 2026-10-01  

---

## 1. Project Understanding

SupplyTwinAI is a final-year capstone (Team 12) delivered as both a functional multi-agent software system and an academic research paper. It extends the four-layer Digital Twin architecture of Jesus et al. (IEEE TEM 2024) by introducing an autonomous reasoning layer powered by a Neo4j Knowledge Graph, GraphRAG context retrieval, six LangGraph-orchestrated Gemini agents, persistent PostgreSQL disruption memory, and human-approved recommendation workflows. The project unifies historical e-commerce logistics (DataCo: 65,752 orders, 180,519 order items) with grounded synthetic extensions (150 suppliers, warehouse inventory, live simulated disruptions, external weather/news signals) to evaluate autonomous decision support. All system metrics and evaluations are strictly empirical, logged, and reproducible for paper publication.

---

## 2. Conflicts, Gaps, and Ambiguities Across Project Documents

| # | Conflict / Gap / Ambiguity | Document Sources | Proposed Resolution |
|---|---|---|---|
| **1** | **Agent Count and Taxonomy** | `report.docx` / old roadmap listed 7 agents. `SRS` §4.4 and `DECISIONS.md` §1 lock agent count to 6. | **Enforce SRS §4.4 list of 6 agents:** Supplier Agent (§4.4 REQ-2), Shipment Agent (§4.4 REQ-3), Inventory Agent (§4.4 REQ-4), External Intelligence Agent (§4.4 REQ-5), Risk Agent (§4.4 REQ-6), and Recommendation Agent (§4.4 REQ-8). Demand forecasting is excluded from paper claims. |
| **2** | **LLM Stack & Execution** | Older roadmap referenced GPT-4.1 / Llama 3. `AGENTS.md` §3 & `DECISIONS.md` §1 require Gemini via LangChain/LangGraph. | **Use Google Gemini API** via `langchain-google-genai` and `langgraph`. Model ID is read strictly from `.env` (never hardcoded). Direct LLM calls outside LangChain/LangGraph are prohibited. |
| **3** | **Memory Store Architecture** | Older roadmap mentioned Redis + PostgreSQL. `AGENTS.md` §3 & `DECISIONS.md` §1 state "No Redis." | **Remove Redis entirely.** All state, session data, agent outputs, audit logs, and disruption memory reside in PostgreSQL (§4.5 REQ-1). |
| **4** | **Destination Geolocation & Coordinates** | Raw DataCo `Latitude` / `Longitude` do not reflect destination locations (averaging ~29.7°N, -84.9°W across all destination countries). | **Rename raw coordinates to `customer_latitude` and `customer_longitude`** to mark them explicitly as origin points (§4.1 REQ-4). Build an offline geocoding lookup (`geo_lookup.json`) mapping destination countries, supplier countries, and warehouse regions to centroid coordinates for External Intelligence matching (§4.4 REQ-5). |
| **5** | **Supplier Entity & Risk Score Uniformity** | DataCo has no native supplier table. ETL v2 created 50 category-proxy suppliers, but risk scores lack variance (std dev = 0.028, mean = 0.554), rendering multi-supplier re-sourcing trivial. | **Implement ETL v3 spec (§4.4 REQ-2, DECISIONS §3.2):** Retain 50 primary suppliers, add 100 seeded alternate suppliers (2 per category, 150 total), and build a `supplier_products` junction table. Parameter distributions (defect rate, lead time, on-time rate) are synthetic, deterministically seeded, and explicitly flagged (`is_synthetic=True`). |
| **6** | **Delay Modeling & Data Leakage** | Including `Days for shipping (real)` or `delivery_delay_days` creates 1.0 AUC leakage. Additionally, DataCo First Class shipping is 100% late by design. | **Enforce strict feature isolation:** Exclude outcome fields (`days_for_shipping_real`, `delivery_delay_days`, `delivery_status`) and canceled shipments from delay models. Treat shipping-mode lateness patterns as dataset properties (§4.4 REQ-3). |
| **7** | **Knowledge Graph Schema Taxonomy** | Superseded docs used `STORED_IN` and `DELIVERED_TO`. SRS §4.3 and DECISIONS §3.8 lock edge names. | **Lock Neo4j edge taxonomy to SRS §4.3 / DECISIONS §3.8 spec:** `SUPPLIES`, `SHIPS_VIA`, `STOCKED_AT` (renaming `STORED_IN`), `DELAYED_BY`, `AFFECTS`, plus data-derived `PLACED`, `CONTAINS`, `FULFILLED_FROM`. Enforce namespaced global IDs (§4.1 REQ-3) as Neo4j primary keys. |

---

## 3. Empirical Verification of Data Claims

All four claims regarding the DataCo dataset and v2 cleaned tables were empirically verified using Python scripts (`datasets/raw/DataCoSupplyChainDataset_archive/DataCoSupplyChainDataset.csv` and `datasets/cleaned_v2/cleaned_data_v2/`). The verification scripts and raw outputs are committed to `evaluation/analysis/`:

### (a) Raw Latitude / Longitude do not vary by destination country
* **Status:** **CONFIRMED**
* **Empirical Findings:** Grouping raw `Latitude` and `Longitude` by destination country (`Order Country`) reveals global averages of **29.7200° N, -84.9157° W**. Across 100+ destination countries, the country-level mean Latitude standard deviation is **3.13°**, and mean Longitude standard deviation is **8.27°**. The raw coordinates correspond to customer order placement locations (predominantly Puerto Rico at lat ~18.4° N, lon ~ -66.6° W, and US mainland at lat ~36.78° N, lon ~ -96.34° W), not destination delivery coordinates. Renamed to `customer_latitude` and `customer_longitude`.

### (b) `late_delivery_risk` is fully determined by delivery status and delay
* **Status:** **CONFIRMED**
* **Empirical Findings:** Crosstab analysis of `Delivery Status` versus `Late_delivery_risk` shows a 100% exact mapping:
  * `Late delivery` (98,977 rows) $\rightarrow$ `Late_delivery_risk = 1` (100.0%)
  * `Advance shipping` (41,592 rows) $\rightarrow$ `Late_delivery_risk = 0` (100.0%)
  * `Shipping on time` (32,196 rows) $\rightarrow$ `Late_delivery_risk = 0` (100.0%)
  * `Shipping canceled` (7,754 rows) $\rightarrow$ `Late_delivery_risk = 0` (100.0%)
  Furthermore, `delay = Days for shipping (real) - Days for shipment (scheduled)`. When `delay > 0`, `Late_delivery_risk` is strictly 1; when `delay <= 0`, it is strictly 0.

### (c) A leak-free lateness model performs modestly (~0.74 AUC)
* **Status:** **CONFIRMED**
* **Empirical Findings:** A Random Forest classifier trained on leak-free features (`Shipping Mode`, `Days for shipment (scheduled)`, `Market`, `Order Region`, `Category Id`, `order_month`, `order_weekday`), excluding outcome variables and canceled orders, achieved an ROC AUC of **0.7603** on a 20% holdout test set.
  Per-mode late delivery breakdown:
  * **First Class:** 100.0% late (1.0000)
  * **Second Class:** 79.83% late
  * **Same Day:** 47.93% late
  * **Standard Class:** 39.77% late (60.23% on time)

### (d) Supplier risk scores are nearly identical across categories
* **Status:** **CONFIRMED**
* **Empirical Findings:** Inspecting `datasets/cleaned_v2/cleaned_data_v2/suppliers.csv` (50 category proxy suppliers) shows:
  * Mean risk score: **0.5537**
  * Standard deviation: **0.0281**
  * Min risk score: **0.4770**, Max risk score: **0.6890**, Median: **0.5520**
  This tight clustering (std dev < 0.03) confirms that alternate suppliers with broader, controlled parameter distributions are required.

---

## 4. Phase 0 Plan: Setup & Infrastructure

### 4.1 Directory Layout Guidelines
* Phase 0 creates **empty directories only** (no stub modules or mock code files).
* Layout:
```text
SupplyTwinAI/
├── AGENTS.md
├── MASTER_PROMPT.md
├── README.md
├── .env.example
├── docker/
│   └── docker-compose.yml
├── backend/
│   ├── app/
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   └── package.json
├── database/
│   ├── etl/
│   │   ├── run_etl.py
│   │   └── etl_config.yaml
│   ├── migrations/
│   └── seeds/
├── knowledge_graph/
├── agents/
├── graph_rag/
├── simulation/
├── evaluation/
│   └── analysis/
├── datasets/
│   ├── raw/
│   ├── cleaned_v2/
│   └── v3_etl/
├── docs/
│   ├── SupplyTwinAI_SRS.docx
│   ├── DECISIONS.md
│   ├── ROADMAP_v2.md
│   ├── decision_log.md
│   ├── data_dictionary/
│   └── plans/
└── paper/
    ├── draft/
    └── artifacts/
```

### 4.2 Stack & Dependency Version Policy
* Dependencies are **not hardcoded from memory**. Current stable package releases are inspected at install time and pinned strictly in lockfiles (`requirements.txt` / `package-lock.json`).
* Baseline targets: Python 3.12+, Node.js v20+, FastAPI, SQLAlchemy 2.0, asyncpg, React 18, Vite 5, Tailwind CSS, Shadcn UI, React Flow 11, Chart.js 4, Leaflet 1.9, LangChain, LangGraph, `langchain-google-genai`, PostgreSQL 16, Neo4j 5.x Python Driver.

### 4.3 Credentials & Environment Policy
* Database and API credentials are sourced **strictly from `.env`**.
* Only `.env.example` is committed to git.
* Local Docker compose file resides in `docker/docker-compose.yml`.

### 4.4 Verified Standard CLI Commands (for README)
* **Backend Install:** `cd backend && python -m venv venv && ./venv/Scripts/activate && pip install -r requirements.txt`
* **Frontend Install:** `cd frontend && npm install`
* **Local DB Start:** `docker-compose -f docker/docker-compose.yml up -d`
* **ETL Run:** `python -m database.etl.run_etl --seeds 42 43 44`
* **Backend Dev Server:** `cd backend && uvicorn app.main:app --reload --port 8000`
* **Frontend Dev Server:** `cd frontend && npm run dev`
* **Run Test Suite:** `pytest`

---

## 5. Phase 1 Plan: Data Enrichment & ETL v3 Implementation

### 5.1 Step-by-Step Implementation Workflow
1. **Single Entry Point & Configuration (§4.1 REQ-1):**
   * Single entry point `database/etl/run_etl.py` reading configuration parameters from `database/etl/etl_config.yaml`.
   * Accepts `--seeds 42 43 44` (runs at least 3 seeds for robustness verification).
2. **ETL Reject/Flag Logic & Audit Logging (§4.1 REQ-2, §4.9 REQ-1):**
   * Implement strict data validation rules during loading (e.g. invalid dates, negative quantities, missing key attributes).
   * Maintain counters for `loaded_records`, `rejected_records`, and `flagged_records`.
   * Log reasons for rejection/flagging and export counts to `datasets/v3_etl/etl_v3_validation_report.json` to feed Admin ETL monitoring (§4.9 REQ-1).
3. **Global Addressable IDs (§4.1 REQ-3):**
   * Assign namespaced `global_id` to every entity:
     * `customer:ID`, `product:ID`, `order:ID`, `item:ID`, `shipment:ID`, `supplier:ID`, `warehouse:ID`, `inventory:ID`, `vehicle:ID`, `event:ID`, `recommendation:ID`.
   * Enforce uniqueness across all entity types.
4. **Coordinate Renaming (§4.1 REQ-4):**
   * Rename raw `Latitude` / `Longitude` to `customer_latitude` and `customer_longitude` on `orders` and `customers` tables.
5. **Simulated State Flag (§4.1 REQ-5, DECISIONS §3.5):**
   * Add `is_simulated` (boolean default `False`) column to `orders`, `order_items`, and `shipments` tables.
6. **Column-Level Synthetic Flagging on Real Tables:**
   * On real tables (`orders`, `shipments`, `customers`, `products`), synthetic assignment columns are explicitly flagged at the column level (e.g., `assigned_warehouse_id_is_synthetic = True` or table column-level synthetic metadata dictionary).
7. **Supplier Parameters & Trade-off Modeling (§4.4 REQ-2, DECISIONS §3.2):**
   * Document explicitly that historical DataCo shipping lateness is used only as a proxy grounding for primary supplier on-time rates.
   * Avoid floor pile-up by using smooth logistic/scaled clipping instead of hard thresholds.
   * Parameterize distributions in `database/etl/etl_config.yaml`:
     * `on_time_rate`, `defect_rate`, `lead_time_days`, `unit_cost_multiplier`.
   * Model multi-dimensional trade-offs: cheap suppliers may have lower reliability or longer lead times; fast suppliers cost more.
   * Include realistic edge cases: specific niche products will have **no good alternate supplier** (e.g. high cost, long lead time, low reliability across all alternates).
   * Assign partial product coverage to alternate suppliers (alternates supply a subset of category products, not 100%).
8. **Warehouse Inventory Modeling (§4.4 REQ-4, DECISIONS §3.3):**
   * Retain 23 regional proxy warehouses.
   * Construct `warehouse_inventory` with `inventory:ID` global ID (`warehouse_id`, `product_id`, `stock`, `reorder_point`, `avg_daily_demand`, `restock_lead_days`, `is_synthetic`).
9. **Geographic Centroid Lookup (§4.4 REQ-5, DECISIONS §3.4):**
   * Build `datasets/v3_etl/geo_lookup.json` mapping destination country names (with explicit ISO Spanish-to-English translation mapping, e.g. "Alemania" $\rightarrow$ "Germany"), supplier countries, and warehouse regions to centroid latitude/longitude.
10. **Data Dictionary v3:**
    * Produce v3 data dictionary matching exact database DDL schemas, detailing tables, primary keys, `global_id` formats, data types, descriptions, and synthetic flags.

---

## 6. Test Plan (Phases 0 & 1)

### 6.1 Phase 0 Infrastructure Verification
* `test_backend_healthcheck`: Verify FastAPI `/api/v1/health` returns `200 OK`.
* `test_postgres_connection`: Verify SQLAlchemy connects to PostgreSQL and executes `SELECT 1`.
* `test_neo4j_connection`: Verify Neo4j driver connects via Bolt and executes `RETURN 1`.

### 6.2 Phase 1 ETL v3 Validation Tests
* `test_etl_determinism`: Run `run_etl.py` with identical seeds (`seed=42`); verify SHA-256 file hashes are identical across runs.
* `test_etl_reject_flag_logic`: Test invalid record inputs; verify reject/flag counters increment accurately and reasons are logged (§4.1 REQ-2).
* `test_v3_preserves_v2_columns`: Verify ETL v3 retains 100% of real historical data columns from v2 without corruption.
* `test_global_id_uniqueness`: Assert zero duplicate `global_id` values across all entity tables, including `inventory:ID` (§4.1 REQ-3).
* `test_referential_integrity`: Assert 100% foreign key validity across `order_items`, `supplier_products`, and `warehouse_inventory`.
* `test_synthetic_column_flagging`: Verify column-level synthetic flags on real tables and `is_synthetic = True` on synthetic tables.
* `test_supplier_coverage_and_tradeoffs`: Verify every product has 1 primary supplier and at least 2 alternate candidates (or partial coverage rules), and verify products with constrained alternate availability exist.
* `test_geo_lookup_coverage`: Verify 100% of destination countries in DataCo resolve to valid centroid coordinates in `geo_lookup.json`.
* `test_data_dictionary_schema_match`: Verify every table and column in `docs/data_dictionary/` matches PostgreSQL DDL schema definitions exactly.
* `test_leakage_feature_isolation`: Assert predictive feature matrices exclude outcome columns.

---

## 7. Risks and Decided Technical Directions

1. **Gemini API Quota & Rate Limits (User Decision: Free Tier):**
   * *Strategy:* Design exponential backoff, rate-limit throttling, full response logging, and a checkpoint/resume mechanism into the agent orchestrator for batch evaluation runs.
2. **Neo4j Deployment & Graph Storage Constraints (User Decision: Hybrid):**
   * *Strategy:* Use local Neo4j Docker for local development and evaluation. Restrict graph load to a configurable recent window for Neo4j Aura demo deployment, while retaining full history in PostgreSQL. Verify Aura limits before Phase 5.
3. **DataCo Shipping Mode Artifacts (User Decision: Agreed):**
   * *Strategy:* Explicitly document First Class 100% lateness in the paper methodology as a dataset property, positioning the Shipment Agent as a transparent baseline.
4. **Supplier Parameter Configuration (User Decision: Approved):**
   * *Strategy:* Maintain all parameter distributions and trade-off matrices in `database/etl/etl_config.yaml`. Run ETL across 3 seeds (`42, 43, 44`) for robustness verification.
5. **Evaluation Non-Determinism (User Decision: Approved):**
   * *Strategy:* Enforce `temperature=0.0`, pin model ID, log raw prompt/response pairs with run IDs, and execute at least 3 evaluation runs per scenario.
6. **Destination Geocoding Translation (User Decision: Approved):**
   * *Strategy:* Include an explicit ISO Spanish-to-English translation map in `geo_lookup.json` and validate with `test_geo_lookup_coverage`.

---

## 8. Paper Artifacts to Capture (Phases 0 & 1)

* `evaluation/analysis/verify_claims.py` & `claim_verification_results.json` (Committed verification scripts & raw outputs)
* `paper/artifacts/phase0/repo_structure_tree.txt` (Directory tree snapshot)
* `paper/artifacts/phase0/environment_versions.json` (Locked python/node dependency versions)
* `paper/artifacts/phase1/data_dictionary_v3.csv` (Complete v3 data dictionary with synthetic flags)
* `paper/artifacts/phase1/synthetic_vs_real_matrix.md` (Table explicitly declaring real vs synthetic tables/columns)
* `paper/artifacts/phase1/etl_v3_validation_report.json` (Automated integrity test output, loaded/rejected/flagged counts)
* `paper/artifacts/phase1/supplier_risk_distribution.png` (Distribution plot showing v2 50-supplier risk vs v3 150-supplier risk variance)
* `paper/artifacts/phase1/leakage_model_roc_curve.png` (ROC curve plot showing leak-free model AUC ~0.76 vs leaky model AUC 1.0)
