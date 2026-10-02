# SupplyTwinAI — Capstone Presentation & Interactive Demonstration Script

**Document Path:** `docs/DEMO_SCRIPT.md`  
**System Version:** 1.0 (Capstone Release)  
**Estimated Presentation Duration:** 15–20 minutes  
**Target Audience:** Capstone Evaluation Committee & Technical Reviewers  

---

## 1. Demonstration Setup & Prerequisites

### 1.1 Local System Launch Commands
Open three terminal windows to initialize the backend, databases, and frontend:

```bash
# Terminal 1: Initialize Database & Run FastAPI Backend Server
cd backend
python -m uvicorn app.main:app --reload --port 8000

# Terminal 2: Run React / Vite Production Development Server
cd frontend
npm run dev

# Terminal 3: Verification & Interactive API Requests
curl http://localhost:8000/api/v1/health
```

Navigate browser to: `http://localhost:5173`

---

## 2. Step-by-Step Presentation Walkthrough

### Step 1: System Overview & Architecture (2 minutes)
* **Visual:** Open Manager Dashboard (`http://localhost:5173/dashboard`).
* **Talking Points:**
  - Highlight the 4-layer Supply Chain Digital Twin architecture extended with autonomous reasoning.
  - Explain the dual database strategy: PostgreSQL for ACID relational state and Neo4j for multi-hop graph topology.
  - Demonstrate real-time KPI metrics (Active Orders, Late Shipments, On-Time Delivery Rate, High-Risk Suppliers).

---

### Step 2: Digital Twin Knowledge Graph Visualization (3 minutes)
* **Visual:** Navigate to `Network Topology Graph` (`http://localhost:5173/network`).
* **Action:** Click on a Supplier node (`supplier:12`) and inspect its connected nodes (Products, Warehouses, Shipments).
* **Talking Points:**
  - Show how global IDs (`type:sourceid`) maintain 1-to-1 parity between relational rows and graph nodes.
  - Demonstrate 3-hop graph traversal queries in real-time ("Which customer shipments are impacted if Supplier 12 experiences an outage?").

---

### Step 3: Empirical Simulation & Disruption Injection (4 minutes)
* **Visual:** Open `Simulation Controls` panel on the Dashboard.
* **Action:**
  1. Click **Inject Disruption**.
  2. Select Event Category: `SUPPLIER_OUTAGE` (or `WEATHER_EVENT`).
  3. Target Entity: `supplier:12`.
  4. Severity: `High (0.85)`.
  5. Click **Trigger Disruption**.
* **Talking Points:**
  - Emphasize data honesty: live events are synthetically injected over historical DataCo baselines.
  - Show immediate status changes across connected shipments and inventory buffers.

---

### Step 4: Multi-Agent Orchestration & GraphRAG Chat (4 minutes)
* **Visual:** Navigate to `Agent Monitor` (`http://localhost:5173/agents`) and `AI Assistant` (`http://localhost:5173/chat`).
* **Action:**
  1. Observe the 6 LangGraph agents executing in DAG sequence:
     - Parallel execution: `SupplierRiskAgent`, `InventoryAgent`, `LogisticsAgent`, `ExternalIntelAgent`.
     - Sequential convergence: `RiskAssessmentAgent` $\rightarrow$ `RecommendationAgent`.
  2. Open the Chat Assistant panel and query:
     > *"What is the impact of the outage at supplier:12 on active shipments, and what mitigations are recommended?"*
  3. Inspect the response, highlighting the retrieved Neo4j subgraph context citations.
* **Talking Points:**
  - Demonstrate GraphRAG context retrieval: answer generation is strictly grounded in graph context.
  - Test explicit unanswerable query ("What will the weather in Tokyo be next month?") to show the AI says *"Cannot answer from available context"* instead of hallucinating.

---

### Step 5: Persistent Memory & Recommendation Approval Workflow (4 minutes)
* **Visual:** Open `Recommendation Center` (`http://localhost:5173/recommendations`).
* **Action:**
  1. View the newly generated recommendation: *"Reroute shipment:77202 to alternate supplier supplier:99"*.
  2. Point out that the recommendation status is strictly `pending` — human approval is mandatory.
  3. Click **Accept Recommendation**. Observe the status change to `accepted` and log entry creation.
  4. Re-inject a similar disruption to demonstrate **Disruption Memory Recall**: past accepted mitigation strategies are retrieved and ranked higher.
* **Talking Points:**
  - Highlight Safety & Governance: Recommendations are NEVER auto-applied regardless of confidence score.
  - Explain how PostgreSQL disruption memory prevents repeating past supply chain mistakes.

---

### Step 6: Admin Governance, Reports & Capstone Conclusion (3 minutes)
* **Visual:** Navigate to `ETL & Admin Monitor` (`http://localhost:5173/admin/etl`).
* **Action:**
  1. Show Admin Agent Weight and Threshold validation controls.
  2. Click **Export CSV Report** for `Recommendations` and `Audit Logs`.
  3. Show the downloaded RFC 4180 CSV files.
* **Talking Points:**
  - Summarize evaluation results: Configuration C achieves 100% recall, 98% grounding rate, and sub-100ms latency.
  - Field questions from the committee.
