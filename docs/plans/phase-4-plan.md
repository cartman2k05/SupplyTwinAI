# SupplyTwinAI — Phase 4 Execution Plan (Simulation Engine and Live Updates)

**Document Path:** `docs/plans/phase-4-plan.md`  
**Status:** Pending Approval  
**Author:** Lead Engineer (AI Pair Programmer)  
**Date:** 2026-10-01  

---

## 1. Goal

Implement the discrete-time simulation clock engine, empirical event generator, disruption injector with recorded ground-truth labels, vehicle fleet assignment pool, and real-time WebSocket telemetry push updates with automatic reconnection and polling fallback (§4.4 REQ-5, §4.6).

---

## 2. SRS Requirements Covered

* **§4.1 REQ-5:** Simulated shipment state tracking, current location, ETA, and vehicle assignment.
* **§4.4 REQ-5:** External signal and simulated disruption event generation.
* **§4.6 REQ-1 & REQ-2:** Disruption scenario catalog & ground-truth labeling (`scenario_id`, `target_global_id`, `acceptable_action_class`).
* **§4.7 REQ-1:** Real-time live dashboard telemetry updates without manual browser refresh.
* **§5.1 NFR-P2:** Real-time WebSocket push updates with reconnection logic and polling fallback.

---

## 3. Files and Modules to Create or Change

```text
SupplyTwinAI/
├── simulation/
│   ├── engine.py                   # Simulation clock runner, time scaling & tick generator
│   ├── events.py                   # Empirical event sampling from DataCo distributions
│   └── disruptions.py              # Disruption injector with ground-truth labels
├── backend/
│   ├── app/
│   │   ├── api/v1/
│   │   │   └── simulation.py       # WS /ws/simulation, POST /simulation/inject, /control
│   │   └── services/
│   │       └── websocket.py        # ConnectionManager for WebSocket broadcasting
│   └── tests/
│       └── test_simulation.py      # Simulation clock & WebSocket unit test suite
├── frontend/
│   ├── src/
│   │   ├── services/
│   │   │   └── websocket.js        # Reconnecting WebSocket client + polling fallback
│   │   ├── components/
│   │   │   └── dashboard/
│   │   │       └── SimulationControl.jsx # Play/Pause & manual disruption trigger
│   │   └── pages/
│   │       └── Dashboard.jsx       # Updated to listen for live WebSocket telemetry
```

---

## 4. Schema and API Changes

### 4.1 Table Operations
* Populates `live_shipments` (current_latitude, current_longitude, current_status, eta, assigned_vehicle_id, updated_at).
* Populates `disruption_events` (event_id, global_id, event_type, severity, target_global_id, description, status).

### 4.2 Versioned REST & WebSocket Endpoints (`/api/v1/`)
* `WS /api/v1/simulation/ws` $\rightarrow$ Real-time WebSocket telemetry stream
* `POST /api/v1/simulation/control` $\rightarrow$ Control clock (play, pause, speed multiplier)
* `POST /api/v1/simulation/inject` $\rightarrow$ Manually inject disruption scenario with ground truth
* `GET /api/v1/simulation/status` $\rightarrow$ Retrieve current clock state and active disruptions

---

## 5. Test List (Phase 4)

* `test_simulation_clock_ticks`: Verify simulation clock advances deterministically and emits periodic tick events.
* `test_seed_reproducibility`: Verify running simulation engine twice with `seed=42` produces identical event streams and vehicle assignments.
* `test_disruption_ground_truth_labeling`: Verify injected disruptions record true affected entity global IDs and acceptable action classes in `disruption_events`.
* `test_websocket_broadcasting`: Verify WebSocket connection manager broadcasts tick and disruption messages to connected clients.
* `test_websocket_polling_fallback`: Verify frontend client degrades gracefully to HTTP polling if WebSocket connection is closed.

---

## 6. Measurable Acceptance Criteria

* Simulation clock advances live shipment positions and ETAs deterministically at 1 sim hour = 5 real seconds.
* WebSocket messages delivered to connected browser clients in under 100ms.
* Injected disruption events record exact ground-truth affected entities and action classes in PostgreSQL.
* Identical random seed (`seed=42`) reproduces identical event stream across runs.

---

## 7. Risks and Technical Mitigations

1. **High Memory Overhead from Concurrent WebSocket Connections:**
   * *Mitigation:* Single singleton `ConnectionManager` broadcasting shared state snapshots rather than per-connection database queries.
2. **WebSocket Connection Drops in Browser:**
   * *Mitigation:* Exponential backoff reconnect handler + automatic HTTP polling fallback (`GET /api/v1/simulation/status`) every 5 seconds if WebSocket fails.

---

## 8. Open Questions

None. Simulation clock speed (1h = 5s) and ground-truth logging were approved during review.

---

## 9. Paper Artifacts to Capture (Phase 4)

* `paper/artifacts/phase4/scenario_catalog_v1.json` (Disruption scenario definitions & ground-truth labels)
* `paper/artifacts/phase4/simulation_engine_spec.md` (Simulation architecture specification)
* `paper/artifacts/phase4/websocket_latency_log.json` (WebSocket broadcast latency benchmarks)

---

## 10. Explicit List of What is Out of Scope for Phase 4

* Neo4j Graph loading and sync (Deferred to Phase 5)
* LangGraph multi-agent reasoning (Deferred to Phases 6 & 7)
* Recommendation approval center workflow (Deferred to Phase 8)
