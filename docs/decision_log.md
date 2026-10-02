# SupplyTwinAI — Decision Log

Append-only log of non-trivial architectural, modeling, and system decisions with rationale, alternatives considered, and SRS/paper impacts.

---

## Decision 001: Phase 0 Repository Structure and Locked Technology Stack

**Date:** 2026-10-01  
**Author:** Lead Engineer  
**Status:** Approved  
**SRS Reference:** §2.1, §2.4, §2.5, §3.3  

### Context
SupplyTwinAI requires a dual deliverable: a production-grade software system and an academic research paper. The technology stack must support real-time graph visualization, low-latency agent orchestration, persistent memory, and reproducible evaluation.

### Decision
1. **Frontend:** React 18 + Vite 5 + Tailwind CSS + Shadcn UI + React Flow + Chart.js + Leaflet.
2. **Backend:** Python 3.12 + FastAPI + SQLAlchemy 2.0 (asyncpg) + Pydantic v2.
3. **Database Stack:** PostgreSQL 16 (relational) + Neo4j 5.x (knowledge graph via parameterized Cypher). Redis is completely dropped per AGENTS.md §3.
4. **AI / LLM Layer:** LangChain + LangGraph + Google Gemini API (`gemini-2.5-flash`). Direct Gemini SDK calls outside LangGraph are prohibited.
5. **Containerization:** `docker/docker-compose.yml` orchestrating local PostgreSQL 16 and Neo4j 5 Community Edition for local development and offline evaluation.
6. **Configuration Management:** Sourced strictly from `.env` files; `.env.example` committed to git.

### Alternatives Considered
- *Redis for Caching:* Rejected due to SRS & AGENTS.md §3 mandate restricting persistent memory strictly to PostgreSQL to simplify deployment and transaction safety.
- *Direct Gemini API Calls:* Rejected to enforce LangChain/LangGraph agent trace logging, retry backoff, and graph context injection standardization.

### Impact on Research Paper
- Establishes clear system boundaries for the System Design methodology section.
- Ensures local reproducibility for all benchmark evaluation runs (Phase 9).

---

## Decision 002: Geolocation Coordinate Normalization and Addressability

**Date:** 2026-10-01  
**Author:** Lead Engineer  
**Status:** Approved  
**SRS Reference:** §4.1 REQ-3, §4.1 REQ-4, §4.4 REQ-5  

### Context
Empirical analysis of the raw DataCo dataset revealed that `Latitude` and `Longitude` values do not vary across destination countries (global average ~29.72° N, -84.92° W across 100+ countries). The raw coordinates correspond to customer order placement locations (Puerto Rico and US mainland), not delivery destinations.

### Decision
1. Rename raw `Latitude` / `Longitude` columns to `customer_latitude` and `customer_longitude` in `customers` and `orders` tables (§4.1 REQ-4).
2. Build an offline geocoding lookup table (`geo_lookup.json`) containing centroid coordinates for destination countries, supplier countries, and warehouse regions (§4.4 REQ-5). Include an explicit ISO Spanish-to-English translation mapping (e.g. "Alemania" $\rightarrow$ "Germany").
3. Assign namespaced global IDs formatted as `type:sourceid` (e.g. `customer:12`, `shipment:77202`, `inventory:45`) across PostgreSQL and Neo4j (§4.1 REQ-3).


---

## Decision 003: Administrative Agent Weight Validation and RFC 4180 CSV Export Governance

**Date:** 2026-10-02  
**Author:** Lead Engineer  
**Status:** Approved  
**SRS Reference:** §3.8, §3.9, §3.10  

### Context
Administrative users require dynamic control over agent recommendation weight distributions and risk threshold boundaries without risking runtime divergence or invalid state. Furthermore, reporting compliance requires audit-ready CSV exports across all core domain entities.

### Decision
1. **Agent Weight Normalization:** Enforce strict backend validation where the sum of agent weights $\sum w_i = 1.0$ (within $\epsilon = 10^{-4}$). Reject configuration updates violating this condition with HTTP 400 Bad Request.
2. **Risk Threshold Ordering:** Validate risk threshold bounds strictly as $0 \le \text{low\_medium} \le \text{medium\_high} \le 100$.
3. **CSV Export Standard:** Utilize RFC 4180 CSV formatting with explicit sanitization against formula injection (`=`, `+`, `-`, `@`) on strings. Serve exports under `/api/v1/reports/export/{resource}` with `Content-Disposition: attachment`.
4. **RBAC Isolation:** All configuration changes and export endpoints require authenticated session tokens with appropriate role authorization.

### Impact on Research Paper
- Establishes mathematically sound governance for multi-agent weight updates.
- Ensures reproducible administrative configuration state for ablation studies.

