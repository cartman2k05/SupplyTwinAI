# SupplyTwinAI — Decisions, Data Spec and Evaluation Plan

Status: proposed baseline. Items marked **[CONFIRM]** need the team's confirmation before the relevant phase starts. This file overrides `docs/superseded/*` wherever they conflict. The SRS overrides this file wherever they conflict, except for the explicit deviations listed in section 2.

---

## 1. Reconciliation of conflicting documents

| Topic | Older documents said | Decision |
|---|---|---|
| Project name | "SupplyTwinGPT" (report), "SupplyTwinAI" (roadmap, SRS) | **SupplyTwinAI** everywhere |
| Agents | Report: Supplier, Shipment, Weather, News, Inventory, Risk. Roadmap: Supplier, Inventory, Demand, Logistics, Risk, Sustainability, Supervisor | **SRS six**: Supplier, Shipment, Inventory, External Intelligence (weather + news), Risk, Recommendation. Demand forecasting is an optional stretch, outside the paper's claims |
| LLM | Roadmap: GPT-4.1 / Llama 3 / Mistral | **Gemini** via LangChain/LangGraph, model ID in config **[CONFIRM key/quota]** |
| Memory store | Roadmap: Redis + PostgreSQL | **PostgreSQL only** (per SRS). Redis dropped |
| Graph edge names | Roadmap: SHIPPED_BY, DELIVERED_TO, STORED_IN. Data pass: STORED_IN | **SRS names**: SUPPLIES, SHIPS_VIA, STOCKED_AT, DELAYED_BY, AFFECTS, plus data-derived PLACED, CONTAINS, FULFILLED_FROM. `STORED_IN` is renamed `STOCKED_AT` |
| Timeline | Report: 14 weeks. Roadmap: 9 weeks | Phase gates in `ROADMAP_v2.md`, mapped to real deadline **[CONFIRM deadline and review dates]** |
| Base paper link | Report linked the MDPI URL as the base paper | MDPI URL is the Roman et al. review. Base paper is Jesus et al., IEEE TEM vol. 71, 2024 |
| DataCo scale | Report: "18,000+ orders" | 65,752 orders, 180,519 order lines |
| Performance claims | Report: 34% latency cut, 41% accuracy gain, 72 h lead time, 90 s mitigation "per the abstract" | **Removed.** The abstract contains none of these. Only measured results may appear |
| README | Describes 7 tables and a `clean_and_map.py` not in the repo | Superseded by the v3 pipeline in section 3 |

Edits to make to `report.docx` if it is reused in the paper: rename, replace the agent list, delete the four unsupported claims, correct the base-paper link, correct the dataset scale. It is otherwise superseded by the SRS.

## 2. Deliberate deviations from the base paper (state these in the paper)

- No blockchain convergence layer. A centralized ETL plus relational schema unifies data (already in SRS §2.5). Justify with the base paper's own point that the choice should follow requirements, and that permissioned chains inherit EDI's weaker trust model.
- Addressability is realized through namespaced global IDs in a single system, not a global cross-organization registry.
- No real-world actuation. Read-only with respect to external systems; human approval is mandatory.

## 3. Data enrichment spec (ETL v3)

Goal: keep `cleaned_data_v2` as the historical base and add what the agents and graph need. Specification only; the agent implements it and documents it in a v3 data dictionary.

**3.1 Global IDs.** Add `global_id` to every entity table: types `customer`, `product`, `order`, `item`, `shipment`, `supplier`, `warehouse`, `vehicle`, `event`, `recommendation`. Format `type:sourceid`. Unique-constrain in Postgres and Neo4j.

**3.2 Suppliers.**
- Keep the 50 category-proxy suppliers as the primary supplier of each category.
- Add two alternate suppliers per category (150 total), deterministically seeded, flagged synthetic.
- Introduce a many-to-many `supplier_products` table with an `is_primary` flag. This gives the Supplier Agent real alternatives (SRS §4.4 REQ-2).
- Attributes: `on_time_rate` (primary suppliers: grounded as one minus the category late rate; alternates: seeded perturbation), `defect_rate` (synthetic, documented distribution, required by SRS), `lead_time_days`, `country`, `region`.
- Observation from analysis: category risk scores are nearly identical (about 0.48 to 0.69, standard deviation about 0.03). Alternates must vary enough to make recommendations meaningful, and this must be disclosed as synthetic.

**3.3 Warehouses and inventory.**
- Keep 23 regional proxy warehouses.
- Add `warehouse_inventory` (warehouse × product): `stock`, `reorder_point`, `avg_daily_demand` (grounded in historical quantity shipped to that region), `restock_lead_days`. Stock is seeded relative to demand and flagged synthetic.
- This replaces the single random `current_stock` figure for the Inventory Agent (SRS §4.4 REQ-4).

**3.4 Geography.**
- Analysis found that the raw `Latitude`/`Longitude` do not vary meaningfully by destination country (every destination averages roughly the same southeastern-US point); they appear customer-side. Reproduce this check first.
- If confirmed, rename them as customer-side and do NOT use them for shipment routes.
- Build an offline lookup of country and region centroids for destination, warehouse, and supplier locations. Destination country names in DataCo are mixed Spanish and English; the lookup needs a name-mapping step.
- This lookup is also what External Intelligence uses for geolocation matching (SRS §4.4 REQ-5).

**3.5 Time and simulation.**
- Historical data spans 2015-01 to 2018-01. Do not pretend it is current.
- The simulator runs on its own simulation clock. Synthetic events are sampled from empirical distributions computed from the historical data (regional order volume, weekday pattern, shipping-mode mix, per-mode delay distribution). Injected disruptions sit on top with recorded ground-truth labels.
- Live state lives in separate tables (live shipment status, location, ETA, assigned vehicle), never mixed into the historical tables without an `is_simulated` flag.
- Historical delay is in whole days; SRS thresholds are in hours. Simulated shipments carry hour-level ETAs.

**3.6 Delay modeling policy.**
- Allowed features: shipping mode, scheduled days, market/region, order month/weekday, product category, active disruptions.
- Forbidden: real shipping days, delay days, delivery status.
- Observations to reproduce, not to trust: a leaky model reaches AUC 1.0; a legitimate baseline reaches about 0.74 and adding region/month/category does not improve it; First Class is 100% late by construction and Standard Class about 40%.
- Consequence: the Shipment Agent's predicted delay is a transparent baseline (mode, schedule, active disruptions), not the paper's headline result.

**3.7 Target Postgres tables (minimum, final list fixed in Phase 2).** users, customers, products, suppliers, supplier_products, warehouses, warehouse_inventory, orders, order_items, shipments, vehicles, live_shipments, disruption_events, external_signals, agent_outputs, recommendations, disruption_memory, agent_config, etl_runs, audit_log. This exceeds the SRS minimum of nine.

**3.8 Graph scope.** Postgres holds everything. Neo4j gets a defined subset if hosted limits require it (for example: all suppliers, products, warehouses, vehicles, disruptions, plus orders/shipments from a configurable time window). Check current Aura free-tier limits before choosing the load size **[CONFIRM]**. Graph schema:
- (Supplier)-[:SUPPLIES]->(Product)
- (Product)-[:STOCKED_AT]->(Warehouse)
- (Order)-[:CONTAINS]->(Product)
- (Order)-[:FULFILLED_FROM]->(Warehouse)
- (Shipment)-[:SHIPS_VIA]->(Vehicle)
- (Shipment)-[:DELAYED_BY]->(DisruptionEvent)
- (DisruptionEvent)-[:AFFECTS]->(Supplier | Warehouse | Shipment | Product)
Shipment nodes are 1:1 with orders. Customers may be omitted from the graph.

## 4. Initial defaults for SRS "TBD" items (tunable, disclosed as placeholders)

- Composite risk weights: supplier 0.30, shipment 0.30, inventory 0.20, external 0.20. Tune on simulated data; report how.
- Risk bands: Low below 33, Medium 33 to 66, High above 66. Alert threshold for recommendations: 60.
- Shipment at-risk threshold: predicted delay over 24 hours (SRS default).
- Report export: CSV required, PDF stretch.
- Concurrent users: 5 (SRS baseline).

## 5. Evaluation plan (this is what makes it a paper)

**Scenarios.** The simulator generates injected disruptions with ground truth: supplier failure, shipment-delay cluster, regional weather event, stock-out, geopolitical news event, and compound events. Each records the true affected entities and an acceptable action class. Fixed seeds. Start with 10 or more per type; the exact count is chosen after measuring variance.

**Configurations compared.**
- A: LLM only (no graph context)
- B: LLM + GraphRAG
- C: LLM + GraphRAG + persistent memory
- D (optional reference): rule-based, no LLM

**Metrics (programmatic first).**
- Affected-entity precision and recall against ground truth
- Hallucinated-ID rate: cited entities absent from the retrieved context or database
- Grounding rate: fraction of recommendation claims traceable to stored retrieved facts
- Recommendation validity: the suggested alternative supplier really supplies the product and has better reliability
- Memory effect: quality and time-to-recommendation across repeated occurrences of the same scenario type (C vs B)
- Latency and token use against SRS targets (assistant 8 s, graph sync 30 s, risk score 5 s)
- LLM-as-judge only as a secondary measure, with the judge model and prompt disclosed

**Protocol rules.**
- Log raw prompts, retrieved context and outputs to `evaluation/results/` with a run ID and config hash. Never hand-edit results.
- Repeat runs (at least 3) because LLM output varies; report spread.
- Memory episodes come from prior simulated runs. Accept/Reject decisions in evaluation come from a scripted "oracle manager" policy, declared as such.
- Record-and-replay for Open-Meteo and NewsAPI so evaluation is reproducible.
- Report negative and null results. A modest honest result is publishable; an unsupported one is not.

## 6. Paper plan (parallel to build)

Contribution claims (each backed by something built and measured):
1. Concrete instantiation of the base paper's higher-level applications layer using GraphRAG plus six orchestrated agents.
2. A realization of the addressability requirement via namespaced global IDs, with an honest scope statement.
3. Persistent disruption memory and its measured effect on repeated disruptions.
4. A reproducible evaluation methodology using simulator-injected ground truth.

Limitations to state up front: historical dataset; synthetic suppliers, warehouses, inventory and events; simulated live feed; no blockchain layer; no real actuation; single-domain (e-commerce) data.

| Paper section | Built from |
|---|---|
| Related work | Jesus et al., Roman et al., SRS references [2] to [10] |
| System design | SRS, this file, phase plans |
| Data and simulation | ETL v3 spec, cleaning log, data dictionary v3, decision log |
| Experiments and results | `evaluation/results/` |
| Discussion and limitations | Sections 2 and 6 above |

Target venue and deadline: **[CONFIRM]**. They decide how much evaluation to build.
