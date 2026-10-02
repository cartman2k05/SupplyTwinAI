# SupplyTwinAI — Autonomous Multi-Agent Digital Twin for Supply Chain Resiliency

[![Python 3.12](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-v0.110+-009688.svg)](https://fastapi.tiangolo.com/)
[![React 18](https://img.shields.io/badge/React-18.3-61dafb.svg)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Vite-v5.4+-646cff.svg)](https://vitejs.dev/)
[![Neo4j 5](https://img.shields.io/badge/Neo4j-v5.x-008cc1.svg)](https://neo4j.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791.svg)](https://www.postgresql.org/)
[![LangGraph](https://img.shields.io/badge/LangGraph-v0.0.30+-orange.svg)](https://langchain-ai.github.io/langgraph/)
[![Google Gemini](https://img.shields.io/badge/LLM-Gemini_2.5_Flash-4285F4.svg)](https://deepmind.google/technologies/gemini/)
[![Tests](https://img.shields.io/badge/Tests-47%2F47%20Passed%20(100%25)-brightgreen.svg)]()

**SupplyTwinAI** is a capstone research project (Team 12) and production-grade software platform that extends the 4-layer *Digital Twin of Supply Chains (DTSC)* architecture (*Jesus et al., IEEE TEM 2024*) with an autonomous reasoning and memory layer:
**Neo4j Knowledge Graph + Subgraph GraphRAG + 6 LangGraph Agents (Gemini) + Persistent PostgreSQL Disruption Memory + Human-Approved Recommendations**.

---

## 📋 Table of Contents

- [Key System Capabilities](#-key-system-capabilities)
- [System Architecture](#-system-architecture)
- [Prerequisites](#-prerequisites)
- [Quick Start Guide](#-quick-start-guide)
  - [1. Environment Setup](#1-environment-setup)
  - [2. Local Database Services](#2-local-database-services)
  - [3. Data ETL & Graph Sync](#3-data-etl--graph-sync)
  - [4. Start Backend Server](#4-start-backend-server)
  - [5. Start Frontend Development Server](#5-start-frontend-development-server)
- [Testing & Benchmark Verification](#-testing--benchmark-verification)
- [Evaluation Results & Benchmark](#-evaluation-results--benchmark)
- [API Documentation](#-api-documentation)
- [Capstone Presentation Script](#-capstone-presentation-script)
- [Data Honesty & Ethics Disclosures](#-data-honesty--ethics-disclosures)
- [Repository Structure](#-repository-structure)
- [License & Citation](#-license--citation)

---

## 🚀 Key System Capabilities

- **Dual Relational + Graph Twin Core:** 1-to-1 data parity between PostgreSQL relational records and a Neo4j Knowledge Graph using namespaced global identifiers (`type:sourceid`, e.g., `supplier:12`, `shipment:77202`).
- **Empirical Simulation Engine:** Discrete-event simulation clock with ground-truth disruption injection (`SUPPLIER_OUTAGE`, `SHIPMENT_DELAY`, `INVENTORY_DEFICIT`, `WEATHER_EVENT`, `GEOPOLITICAL_NEWS`).
- **GraphRAG Retrieval Engine:** Subgraph context retriever extracting 3-hop topology around affected nodes, providing explicit graph node citations with non-hallucination guardrails (*"cannot answer from available context"*).
- **6-Agent LangGraph Orchestrator:** Parallel agent execution (`SupplierRiskAgent`, `InventoryAgent`, `LogisticsAgent`, `ExternalIntelAgent`) converging sequentially into `RiskAssessmentAgent` and `RecommendationAgent`.
- **Persistent Disruption Memory:** Cosine-similarity disruption memory storing past accepted mitigation strategies in PostgreSQL for automated recall during recurring disruptions.
- **Human-in-the-Loop (HITL) Safety Governance:** 0% auto-execution. All recommended actions are generated in a `pending` status, requiring explicit Accept/Reject authorization by a Supply Chain Manager.
- **Admin Controls & RFC 4180 CSV Export:** Administrative agent weight normalization ($\sum w_i = 1.0$), risk threshold validation, and audit-compliant CSV data exports for all core domain entities.

---

## 🏗️ System Architecture

```mermaid
flowchart TD
    subgraph Client Layer
        ManagerUI[React 18 / Vite Manager Dashboard]
        NetworkUI[React Flow Knowledge Graph UI]
    end

    subgraph API & Backend Core (FastAPI)
        Auth[OAuth2 JWT Auth & RBAC Guard]
        Endpoints[Versioned REST API /api/v1]
        SimEngine[Discrete-Event Simulation Engine]
    end

    subgraph Intelligence & Graph Layer
        GraphRAG[GraphRAG Subgraph Retriever]
        Agents[6-Agent LangGraph DAG Engine]
        Memory[PostgreSQL Disruption Memory]
    end

    subgraph Data Persistence Tier
        Postgres[(PostgreSQL 16 Relational Core)]
        Neo4j[(Neo4j 5.x Knowledge Graph)]
    end

    ManagerUI --> Endpoints
    NetworkUI --> Endpoints
    Endpoints --> Auth
    Endpoints --> SimEngine
    SimEngine --> GraphRAG
    GraphRAG --> Neo4j
    GraphRAG --> Agents
    Agents --> Memory
    Agents --> Postgres
```

---

## 📦 Prerequisites

Ensure you have the following installed on your system:
- **Python:** `v3.12+`
- **Node.js:** `v20.x+` and `npm v10.x+`
- **Docker Desktop:** Docker 24+ & Docker Compose v2+
- **Google Gemini API Key:** Sourced from [Google AI Studio](https://aistudio.google.com/)

---

## ⚡ Quick Start Guide

### 1. Environment Setup

Clone the repository and copy `.env.example` to `.env`:

```bash
git clone https://github.com/<your-username>/SupplyTwinAI.git
cd SupplyTwinAI
cp .env.example .env
```

Edit `.env` to insert your Google Gemini API key:
```env
GEMINI_API_KEY=your_gemini_api_key_here
ENVIRONMENT=development
JWT_SECRET=supersecretjwtkey_change_in_production
```

---

### 2. Local Database Services

Start local PostgreSQL 16 and Neo4j 5 Community containers via Docker Compose:

```bash
docker-compose -f docker/docker-compose.yml up -d
```

Verify that the containers are healthy:
- **PostgreSQL:** `localhost:5432` (User: `supplytwin_user`, DB: `supplytwin`)
- **Neo4j Browser:** `http://localhost:7474` (Bolt: `bolt://localhost:7687`, User: `neo4j`, Password: `password`)

---

### 3. Data ETL & Graph Sync

Set up the Python virtual environment and run the ETL v3 data ingestion pipeline:

```bash
# Windows PowerShell
python -m venv venv
.\venv\Scripts\activate

# Linux / macOS
# source venv/bin/activate

# Install Dependencies
pip install -r requirements.txt

# Run DataCo Ingestion & Database Population
python -m database.etl.run_etl --seeds 42 43 44

# Populate Neo4j Knowledge Graph Nodes & Edges
python -m knowledge_graph.loader
```

---

### 4. Start Backend Server

Launch the FastAPI backend server:

```bash
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

- **Health Check:** `http://localhost:8000/api/v1/health`
- **Swagger API Docs:** `http://localhost:8000/docs`
- **ReDoc API Specs:** `http://localhost:8000/redoc`

---

### 5. Start Frontend Development Server

In a new terminal window, initialize and run the React / Vite manager dashboard:

```bash
cd frontend
npm install
npm run dev
```

Open your browser to: **`http://localhost:5173`**

Default Login Credentials:
- **Manager Role:** Username: `manager@supplytwin.ai` | Password: `manager123`
- **Admin Role:** Username: `admin@supplytwin.ai` | Password: `admin123`

---

## 🧪 Testing & Benchmark Verification

### Full Backend Pytest Suite
Run the complete unit and integration test suite:

```bash
python -m pytest backend/tests/
```
*Result:* **47 / 47 tests passed (100% pass rate)**.

### 60-Scenario Evaluation Harness
Execute the reproducible 60-scenario comparative benchmark (Configurations A, B, C):

```bash
python -m evaluation.run_eval
```
*Outputs JSON benchmark logs to `evaluation/results/`.*

### Frontend Production Build Check
Verify zero-error bundle compilation for frontend distribution:

```bash
cd frontend
npm run build
```
*Result:* **1,674 modules transformed cleanly in <4.0 seconds**.

---

## 📊 Evaluation Results & Benchmark

SupplyTwinAI was rigorously evaluated across 60 ground-truth labeled scenarios comparing **Configuration A (Base LLM)**, **Configuration B (LLM + GraphRAG)**, and **Configuration C (Full Memory System)**:

| Metric | Config A (Base LLM) | Config B (GraphRAG) | Config C (GraphRAG + Memory) | Delta (C vs A) |
|---|:---:|:---:|:---:|:---:|
| **Entity Precision ($P$)** | 0.3000 | 0.9000 | **0.9000** | **+200.0%** |
| **Entity Recall ($R$)** | 0.1733 | 0.9600 | **1.0000** | **+477.0%** |
| **F1-Score ($F_1$)** | 0.2171 | 0.9206 | **0.9428** | **+334.3%** |
| **Grounding Rate ($G$)** | 0.4200 | 0.9200 | **0.9800** | **+133.3%** |
| **Action Validity ($V$)** | 0.4000 | 0.8000 | **0.8000** | **+100.0%** |
| **Mean Execution Latency ($T$)** | 253.39 ms | 75.14 ms | **72.79 ms** | **-71.3%** |

---

## 📑 API Documentation

The REST API operates under versioned namespace `/api/v1`:

| Endpoint Router | Path | Description | Access |
|---|---|---|---|
| **Auth** | `POST /api/v1/auth/token` | OAuth2 JWT Login & Token Generation | Public |
| **Dashboard** | `GET /api/v1/dashboard/kpis` | Real-time KPIs & Risk Metrics | Manager / Admin |
| **Simulation** | `POST /api/v1/simulation/disrupt` | Inject Ground-Truth Disruption Event | Manager / Admin |
| **Knowledge Graph** | `GET /api/v1/graph/subgraph` | Multi-hop Subgraph Traversal Query | Manager / Admin |
| **AI Assistant** | `POST /api/v1/chat/message` | GraphRAG Multi-Agent Chat Assistant | Manager / Admin |
| **Agent Monitor** | `GET /api/v1/agents/status` | LangGraph Agent DAG Status & Traces | Manager / Admin |
| **Recommendations**| `POST /api/v1/recommendations/{id}/action` | Accept / Reject Mitigation Action | Manager / Admin |
| **CSV Reports** | `GET /api/v1/reports/export/{resource}` | Download RFC 4180 CSV Entities | Manager / Admin |
| **Admin Controls** | `PUT /api/v1/admin/config` | Update Weights & Threshold Bounds | Admin Only |

---

## 🎬 Capstone Presentation Script

A complete, step-by-step presentation walkthrough script designed for the Capstone Evaluation Committee is available in [`docs/DEMO_SCRIPT.md`](file:///c:/Users/nagaa/OneDrive/Desktop/SupplyTwinAI/docs/DEMO_SCRIPT.md).

For complete requirement traceability from `SupplyTwinAI_SRS.docx` to implementation code and unit tests, view [`docs/SRS_TRACEABILITY_MATRIX.md`](file:///c:/Users/nagaa/OneDrive/Desktop/SupplyTwinAI/docs/SRS_TRACEABILITY_MATRIX.md).

---

## 🛡️ Data Honesty & Ethics Disclosures

- **DataCo Dataset:** Transaction data (Jan 2015 – Jan 2018) originates from real historical e-commerce records.
- **Synthetic Extensions:** Alternate suppliers, warehouses, vehicles, defect rates, live events, and injected disruptions are synthetic/simulated, deterministically seeded, and explicitly flagged in the database schema (`is_synthetic = True`).
- **Leakage Prevention:** Predictive features strictly exclude target delay outcomes (`delivery_delay_days`, `delivery_status`).
- **Safety Governance:** AI recommendations are **NEVER** auto-applied. All mitigation status transitions require explicit human Accept/Reject decision making.

---

## 📁 Repository Structure

```text
SupplyTwinAI/
├── AGENTS.md                       # Repository instructions & safety rules
├── README.md                       # Project documentation & quickstart guide
├── render.yaml                     # Render backend cloud deployment manifest
├── .env.example                    # Template environment variables
├── docker/
│   └── docker-compose.yml          # PostgreSQL 16 & Neo4j 5 local containers
├── backend/                        # FastAPI app, SQLAlchemy models & test suites
│   ├── app/                        # REST API routers, auth, services, schemas
│   └── tests/                      # 47 unit & integration pytest files
├── frontend/                       # React 18 + Vite Manager Dashboard SPA
│   ├── src/                        # React Flow, Chart.js, Shadcn components
│   └── vercel.json                 # Vercel SPA cloud deployment manifest
├── database/                       # DDL migrations & ETL v3 ingestion scripts
├── knowledge_graph/                # Neo4j Cypher schemas, loaders & GraphRAG queries
├── agents/                         # 6 LangGraph agent nodes & DAG orchestrator
├── graph_rag/                      # Subgraph retriever & prompt templates
├── simulation/                     # Discrete-event engine & disruption generator
├── evaluation/                     # 60-scenario evaluation harness & metrics
├── datasets/                       # Raw DataCo archive & geocoding lookups
├── docs/                           # SRS, decision log, plans & traceability matrix
│   ├── SRS_TRACEABILITY_MATRIX.md  # 100% SRS requirement to code mapping
│   ├── DEMO_SCRIPT.md              # Capstone presentation walkthrough guide
│   ├── decision_log.md             # Append-only architectural decision log
│   └── plans/                      # Phase 0 through Phase 11 completion reports
└── paper/                          # Research paper LaTeX manuscript & artifacts
    ├── main.tex                    # Camera-ready IEEE TEM LaTeX paper
    └── artifacts/                  # Phase 0 to 11 empirical charts & benchmarks
        └── final_paper_draft.md    # Complete Markdown research paper manuscript
```

---

## 📜 License & Citation

This project is developed as a final-year Capstone Research Project (Team 12). All code and documentation are released for academic research and presentation.

If you use this work or architecture in your research, please cite:

```bibtex
@article{supplytwinai2026,
  title={SupplyTwinAI: An Autonomous Multi-Agent Digital Twin for Supply Chain Resiliency Using Knowledge Graphs and Persistent Disruption Memory},
  author={Team 12 Capstone Research Team},
  journal={IEEE Transactions on Engineering Management (Draft)},
  year={2026}
}
```
