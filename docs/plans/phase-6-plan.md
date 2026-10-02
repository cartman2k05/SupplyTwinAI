# SupplyTwinAI — Phase 6 Execution Plan (GraphRAG and AI Assistant)

**Document Path:** `docs/plans/phase-6-plan.md`  
**Status:** Pending Approval  
**Author:** Lead Engineer (AI Pair Programmer)  
**Date:** 2026-10-01  

---

## 1. Goal

Implement the GraphRAG subgraph context retriever, Gemini API integration via LangChain (`langchain-google-genai`), stored context traceability per answer, strict fallback for unanswerable queries ("cannot answer from available context"), prompt-injection safety sanitization, versioned REST endpoints (`/api/v1/chat/`), interactive Chat Panel UI with Configuration A (Base LLM) vs Configuration B (GraphRAG) evaluation toggle, and first Configuration A vs B benchmark comparison (§4.3 REQ-1 to REQ-6, §4.7 REQ-4, §5.1 NFR-P1).

---

## 2. SRS Requirements Covered

* **§4.3 REQ-1 & REQ-2:** GraphRAG Context Retriever extracting top-N ranked subgraphs surrounding target entity `global_id`s from Neo4j.
* **§4.3 REQ-3:** LLM reasoning layer using Gemini API via LangChain (`langchain-google-genai`). Model ID configured in settings (`gemini-1.5-flash` or from `.env`).
* **§4.3 REQ-4:** Answer Traceability: Every assistant answer stores the exact `retrieved_context` in PostgreSQL database (`chat_messages` table).
* **§4.3 REQ-5:** Strict Fallback: The AI Assistant responds with *"Cannot answer from available context"* when retrieved facts are insufficient, preventing hallucinations.
* **§4.3 REQ-6:** Safety & Governance: Prompt-injection sanitization, PII stripping (no customer personal names; uses global IDs and aggregates only).
* **§4.7 REQ-4:** Interactive AI Assistant Chat Panel in frontend with message thread, context drawer showing retrieved facts, Config A vs B toggle, and latency timer.
* **§5.1 NFR-P1:** Response latency $< 8.0$ seconds under normal load.

---

## 3. Files and Modules to Create or Change

```text
SupplyTwinAI/
├── graph_rag/
│   ├── retriever.py                # GraphRAG retriever extracting top-N ranked subgraphs from Neo4j
│   └── chain.py                    # LangChain Gemini RAG pipeline with safety prompts & fallback
├── backend/
│   ├── app/
│   │   ├── models/
│   │   │   └── chat.py             # ChatMessage ORM model storing queries, answers, & retrieved_context
│   │   ├── api/v1/
│   │   │   ├── chat.py             # REST endpoints (/query, /history, /clear)
│   │   │   └── router.py           # Includes chat router under /api/v1
│   │   └── services/
│   │       └── chat_service.py    # Chat orchestration, latency timing, & injection safety
│   └── tests/
│       └── test_graph_rag.py       # Test suite for GraphRAG retriever, Gemini chain, fallback, & APIs
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   └── AIAssistant.jsx     # Interactive Chat Panel page with Config A/B toggle & context drawer
│   │   └── App.jsx                 # Mount /chat route
```

---

## 4. Schema and API Changes

### 4.1 Table Operations (`chat_messages` table in PostgreSQL)
* `message_id` (Integer PK)
* `user_query` (Text)
* `assistant_response` (Text)
* `retrieved_context` (Text JSON)
* `config_mode` (String: `'A'` [Base LLM] or `'B'` [GraphRAG])
* `model_id` (String)
* `latency_ms` (Float)
* `is_fallback` (Boolean)
* `created_at` (DateTime)

### 4.2 Versioned REST Endpoints (`/api/v1/chat`)
* `POST /api/v1/chat/query` $\rightarrow$ Accepts `{ "message": str, "config_mode": "A"|"B", "top_n": int }`, executes chain, returns answer + context + latency
* `GET /api/v1/chat/history` $\rightarrow$ Retrieves past chat messages with stored context
* `DELETE /api/v1/chat/history` $\rightarrow$ Clears conversation history

---

## 5. Test List (Phase 6)

* `test_graph_rag_retriever`: Verify extracting top-N ranked subgraphs from Neo4j for entity global IDs.
* `test_gemini_chain_execution`: Verify executing LangChain RAG pipeline with Gemini API (or mock response when offline).
* `test_stored_context_traceability`: Verify assistant answers save full `retrieved_context` in `chat_messages` table.
* `test_unanswerable_query_fallback`: Verify asking an out-of-context question returns *"Cannot answer from available context"*.
* `test_prompt_injection_safety`: Verify malicious prompt injection attempts (e.g. "Ignore prior instructions") are sanitized or safely declined.
* `test_chat_response_latency`: Verify total response time is $< 8.0$ seconds (§5.1 NFR-P1).

---

## 6. Measurable Acceptance Criteria

* Assistant answers queries within 8 seconds (§5.1 NFR-P1).
* Every answer stores its exact `retrieved_context` in PostgreSQL database.
* Asking unanswerable questions triggers explicit *"Cannot answer from available context"* fallback.
* Prompt-injection attempts are sanitized without leaking database or instructions.
* Config A (Base LLM) vs Config B (GraphRAG) toggle is functional and benchmarked.
* All backend pytest unit tests pass.
* Frontend production build compiles cleanly.

---

## 7. Risks and Technical Mitigations

1. **Gemini API Rate Limits or API Key Missing in Test Environment:**
   * *Mitigation:* Implement graceful mock LLM provider in `chain.py` when `GEMINI_API_KEY` is not present or when rate-limited during pytest runs.
2. **Slow Graph Retrieval Impacting 8s Latency Target:**
   * *Mitigation:* Enforce top-N limits (default 5-10 nodes/edges max) and parameterized Cypher lookup timeouts.

---

## 8. Open Questions

None. Model ID resides in `.env` and fallback behavior was confirmed in `DECISIONS.md`.

---

## 9. Paper Artifacts to Capture (Phase 6)

* `paper/artifacts/phase6/graph_rag_retrieval_design.md` (Retriever architecture, Cypher pattern, top-N ranking logic)
* `paper/artifacts/phase6/graph_rag_latency_log.json` (Response latency benchmarks < 8s)
* `paper/artifacts/phase6/config_a_vs_b_comparison.json` (First comparison of Config A [Base LLM] vs Config B [GraphRAG])

---

## 10. Explicit List of What is Out of Scope for Phase 6

* Multi-agent LangGraph orchestration (Deferred to Phase 7)
* Persistent disruption memory vector store (Deferred to Phase 8)
* Formal evaluation harness benchmark automation across 60+ scenarios (Deferred to Phase 9)
