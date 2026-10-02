# SupplyTwinAI — Roadmap v2

Principle: build a real, demoable system first; AI is layered on a foundation that already works; evaluation is designed early, not bolted on at the end. Every phase ends with a gate that can be demonstrated and a set of paper artifacts.

Effort sizes: S (a few days), M (about a week), L (1.5 to 2 weeks) for a four-person team. Map to real dates once the deadline is confirmed. Each phase starts with a plan file in `docs/plans/` and waits for approval.

Suggested review split (adjust to actual review dates): **Review 1 = Phases 0 to 5. Review 2 = Phases 6 to 11.**

---

## Phase 0 — Setup (S)
Repo, folder layout, `.env.example`, Docker for local Postgres and Neo4j, README with real commands, `docs/` populated, decision log started. Both agent instruction files in place.
**Gate:** clean checkout runs an empty backend and an empty frontend; databases reachable locally.
**Paper artifacts:** repo structure, tool versions.

## Phase 1 — Data enrichment, ETL v3 (M)
Implement the spec in `DECISIONS.md` §3: reproduce v2, verify coordinate and leakage findings, add global IDs, alternate suppliers, warehouse inventory, geography lookup. Produce data dictionary v3 and a validation report.
**Gate:** deterministic regeneration (same seed, same output); validation report shows zero referential-integrity breaks, unique global IDs, all synthetic columns flagged.
**Paper artifacts:** data dictionary v3, cleaning log, synthetic-versus-real table, distribution plots.

## Phase 2 — Database, API foundation, auth (M)
Postgres schema (target tables), migrations, ETL loader with reject/flag counts (SRS §4.1), JWT auth, role-based access (Manager and Admin), versioned REST API with OpenAPI docs, `etl_runs` and `audit_log`.
**Gate:** ETL run loads data and reports loaded/rejected/flagged; a Manager token gets 403 on admin endpoints; Swagger shows every endpoint.
**Paper artifacts:** ER diagram, table counts.

## Phase 3 — Frontend shell and manager dashboard (M)
Login, role-aware navigation, Manager Dashboard KPIs and risk chart (initially fed by the historical and simulated data), Shadcn/Tailwind consistency, responsive from 768 px.
**Gate:** login works; dashboard KPIs visible without scrolling at 1366×768; admin area hidden from managers.
**Paper artifacts:** screenshots.

## Phase 4 — Simulation engine and live updates (M)
Simulation clock, empirical-distribution event generator, vehicle assignment, live shipment state, disruption injection with ground-truth labels, WebSocket push with reconnect and polling fallback.
**Gate:** dashboard updates without reload; injected disruptions are recorded with ground truth; same seed reproduces the same event stream.
**Paper artifacts:** simulator description, event-distribution comparison against history, scenario catalog v1.

## Phase 5 — Knowledge graph (M)
Neo4j schema per `DECISIONS.md` §3.8, load and incremental sync from Postgres, unique-ID constraints, multi-hop queries (three or more hops), Digital Twin graph view in React Flow.
**Gate:** sync within 30 s of a Postgres change (measured); multi-hop query "shipments affected if Supplier X fails" returns correct results verified against SQL; graph view shows node status.
**Paper artifacts:** graph schema figure, node/edge counts, sync latency measurements.
**Evaluation design starts here:** scenario ground-truth definitions and metric definitions drafted in `evaluation/`.

## Phase 6 — GraphRAG and AI Assistant (L)
Retrieval of ranked subgraph context, top-N limits, stored context per answer, Gemini via LangChain, chat panel, explicit "cannot answer from context" behavior, injection-safe query handling.
**Gate:** assistant answers within 8 s under normal load; every answer stores its context; an unanswerable question is declined; a prompt-injection attempt is handled.
**Paper artifacts:** retrieval design, latency measurements, first Configuration A vs B comparison on a small scenario set.

## Phase 7 — Multi-agent layer (L)
Six LangGraph agents with the SRS orchestration order (four in parallel, then Risk, then Recommendation), config-driven thresholds and weights, persisted agent outputs, External Intelligence with Open-Meteo and NewsAPI plus record-and-replay, graceful degradation.
**Gate:** disrupting a supplier triggers all agents; Risk waits for all four upstream outputs; one agent failing does not stop the others; full reasoning trail reconstructable from stored outputs.
**Paper artifacts:** orchestration diagram, per-agent latency, config table.

## Phase 8 — Memory, recommendations and approval workflow (M)
Disruption memory in Postgres, retrieval of similar past events into recommendations, Recommendation Center with Accept/Reject and filters, audit trail of decisions.
**Gate:** recommendations never change status automatically; decisions persist across restart; a repeated scenario visibly uses prior memory.
**Paper artifacts:** memory schema, worked example of a repeated disruption.

## Phase 9 — Evaluation (L)
Full harness: scenario generation, Configurations A/B/C (and optional D), metrics, repeated runs, result logging, analysis notebooks or scripts, figures and tables for the paper.
**Gate:** all metrics reproducible from a single command; results folder contains raw logs with run IDs; null and negative results are included.
**Paper artifacts:** all result tables and figures.

## Phase 10 — Admin, reports, hardening (M)
ETL monitor, agent configuration screen with validation (weights sum to 1.0, thresholds 0 to 100), CSV report export, security review against SRS §5.3, error handling, load check for 5 concurrent users.
**Gate:** config changes apply without redeploy; RBAC verified; SRS NFR checklist walked through with evidence.

## Phase 11 — Deployment, documentation, paper finalization (M)
Backend on Render, frontend on Vercel, Supabase and Aura connected, README and user guidance, SRS-to-implementation traceability table, final paper draft, demo script.
**Gate:** deployed system runs end to end; traceability table shows every SRS requirement as met, partial (with reason), or deferred.

---

## Paper workstream (continuous)
- After Phase 1: draft Data and Simulation section.
- After Phase 5: draft System Design (twin and graph).
- After Phase 7: draft Agents section.
- After Phase 9: write Results, Discussion, Limitations; finalize Abstract and Introduction last.
- Keep `docs/decision_log.md` current; it is the raw material for the methodology.

## Cuts if time runs short (in this order)
1. Leaflet route map (keep graph view)
2. PDF export (keep CSV)
3. Optional rule-based baseline D
4. Extra scenario types (keep supplier failure, delay cluster, weather)
Never cut: approval workflow, traceability, evaluation of A vs B vs C.
