# AGENTS.md — SupplyTwinAI

Standing instructions for every agent working in this repository. Keep this file short; detail lives in `docs/`.

## 1. What this project is

SupplyTwinAI is a final-year capstone (Team 12) that must be BOTH implemented as a working system AND published as a research paper. It extends the four-layer "Digital Twin of Supply Chains" architecture (Jesus et al., IEEE TEM 2024) with an autonomous reasoning layer: Knowledge Graph + GraphRAG + six LangGraph agents + persistent disruption memory + human-approved recommendations.

Every engineering choice must also be defensible in a paper. If something cannot be measured, logged, or honestly described, flag it.

## 2. Source of truth (highest priority first)

1. `docs/SupplyTwinAI_SRS.docx` — requirements. Where documents conflict, the SRS wins.
2. `docs/DECISIONS.md` — reconciliations, data-enrichment spec, evaluation plan. It overrides the older roadmap and report.
3. `docs/ROADMAP_v2.md` — phase order and gates.
4. `docs/references/` — papers (background only; do not copy text from them).
5. `docs/superseded/` — old roadmap, old report. Read for history only; never follow them over the above.

If you find a conflict or gap the documents don't resolve, STOP and ask. Do not silently choose.

## 3. Locked stack

- Frontend: React + Vite + Tailwind + Shadcn UI + React Flow + Chart.js + Leaflet
- Backend: Python + FastAPI + SQLAlchemy + WebSockets, versioned API under `/api/v1`
- Relational DB: PostgreSQL (Supabase-hosted in cloud, local Postgres for dev)
- Graph DB: Neo4j (Aura in cloud, local for dev), official Python driver, parameterized Cypher only
- AI: LangChain + LangGraph; LLM = Gemini API. Model ID lives in config/env, never hardcoded. Verify current model names and rate limits in Google's docs before choosing.
- External data: Open-Meteo (weather), NewsAPI (news)
- No Redis. Persistent memory is PostgreSQL only.
- Do not add libraries or services outside this stack without asking.

## 4. Repository layout

`backend/` `frontend/` `database/` `knowledge_graph/` `agents/` `graph_rag/` `simulation/` `evaluation/` `datasets/` `docs/` `paper/` `docker/`

- `datasets/raw/` and large generated files are git-ignored. Only small samples, schemas and data dictionaries are committed.
- `docs/plans/` holds one plan file per phase. `docs/decision_log.md` is append-only.

## 5. Non-negotiable rules

**Data honesty**
- DataCo is real but historical (Jan 2015 to Jan 2018). Suppliers, warehouses, vehicles, warehouse inventory, defect rates, live events and disruptions are SYNTHETIC or SIMULATED. Flag every synthetic table and column in schema and data dictionary.
- Never invent numbers for results, docs, comments, or the paper. Every reported metric must come from a saved, reproducible run.
- All randomness uses a recorded seed. Regeneration must be deterministic.

**Modeling hygiene**
- `days_for_shipping_real`, `delivery_delay_days`, and `delivery_status` are outcome columns. They must never be features for predicting lateness. Canceled shipments are excluded from delay modeling.
- Do not present the shipping-mode-driven lateness pattern as real-world logistics behavior. State it as a property of the dataset.

**Addressability**
- Every entity gets a namespaced, globally unique ID (`type:sourceid`, e.g. `supplier:12`, `shipment:77202`), stored in a `global_id` column and used as the Neo4j unique key. Integer PKs may remain internally.

**Safety and governance**
- Recommendations are NEVER auto-applied. Status changes only through explicit Accept/Reject by a Supply Chain Manager. No confidence threshold changes this.
- Every answer and recommendation stores the GraphRAG context that produced it (traceability).
- The AI Assistant says "cannot answer from available context" rather than guessing.
- Every LLM call goes through the LangChain/LangGraph layer. No direct Gemini calls elsewhere.
- No customer names or other personal fields in prompts. Use IDs and aggregates.
- Secrets only in environment variables. Never commit keys. Provide `.env.example` only.
- Agent thresholds and risk weights are stored in editable config, never hardcoded.
- If an external API fails, degrade gracefully: serve last-known data with a visible "stale" flag. One failing agent must not stop the others.

## 6. Working protocol

1. **Plan before code.** At the start of each phase, write `docs/plans/phase-N-plan.md` (goal, requirements covered by SRS ID, files to create/change, schema changes, tests, risks, open questions, paper artifacts to capture). Then STOP and wait for approval.
2. **One phase at a time.** Do not begin the next phase until the current gate in `docs/ROADMAP_v2.md` passes and the user confirms.
3. **Small steps.** Prefer small commits with clear messages. Never rewrite working modules without saying why.
4. **Test what matters.** Add tests for ETL validation, ID uniqueness, referential integrity, agent orchestration order, approval-workflow rules, and RBAC. Run them before declaring a phase done.
5. **Log decisions.** Append every non-trivial choice (with reason and alternatives) to `docs/decision_log.md`. This feeds the paper's methodology.
6. **Capture paper artifacts** at each phase (counts, schema diagrams, latency logs, screenshots) into `paper/artifacts/` as listed in the phase plan.
7. **Report honestly.** If something failed, was skipped, or is partially working, say so plainly in the phase report.
8. **Ask when unsure.** A wrong assumption baked into the schema is expensive. A question is cheap.

## 7. Definition of done (any phase)

- Gate criteria in `ROADMAP_v2.md` met and demonstrated.
- Tests pass; app starts from a clean checkout following the README.
- README and data dictionary updated for anything changed.
- Decision log and paper artifacts updated.
- Phase report written (what was built, what was verified, what deviates from the SRS, open issues).

## 8. Commands

Fill in during Phase 0 and keep current: install, run backend, run frontend, run tests, run ETL, run simulator, run evaluation.
