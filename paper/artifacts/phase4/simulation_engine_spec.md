# SupplyTwinAI — Phase 4 Simulation Engine & Telemetry Specification

**Artifact Path:** `paper/artifacts/phase4/simulation_engine_spec.md`  
**Phase:** Phase 4 (Simulation Engine and Live Updates)  
**System Layer:** Layer 1 (Physical / Digital Twin Base & Live Telemetry Engine)  

---

## 1. Engine Architecture & Mathematical Model

The SupplyTwinAI simulation engine implements a discrete-time clock runner capable of advancing supply chain operational time deterministically.

### 1.1 Time Scaling
* **Time Conversion Ratio:** 1 sim hour = 5.0 real seconds (default at 1.0x speed).
* **Speed Multipliers:** Supports dynamically adjusting speed multiplier $m \in [0.1, 10.0]$.
* **Clock Advancements:** On each tick interval $\Delta t$, simulated time advances by:
  $$\text{Time}_{\text{sim}} \leftarrow \text{Time}_{\text{sim}} + (\Delta t_{\text{hours}} \times m)$$

### 1.2 Geographic Position Interpolation
Active live shipments move along a straight-line vector from their origin warehouse coordinates $(\text{Lat}_{\text{wh}}, \text{Lon}_{\text{wh}})$ to their customer destination coordinates $(\text{Lat}_{\text{cust}}, \text{Lon}_{\text{cust}})$.

For a given shipment $s$ with scheduled delivery duration $D_s$ (hours) and total elapsed simulation ticks $N_{\text{ticks}}$, the progress ratio $p \in [0.0, 1.0]$ is:
$$p = \min\left(1.0, \max\left(0.0, \frac{N_{\text{ticks}} \times \Delta t \times m}{D_s \times 24.0}\right)\right)$$

The interpolated instantaneous spatial coordinates at time $t$ are:
$$\text{Lat}(t) = \text{Lat}_{\text{wh}} + p \times (\text{Lat}_{\text{cust}} - \text{Lat}_{\text{wh}})$$
$$\text{Lon}(t) = \text{Lon}_{\text{wh}} + p \times (\text{Lon}_{\text{cust}} - \text{Lon}_{\text{wh}})$$

If $p \ge 1.0$, the status is set to `DELIVERED`.

---

## 2. Disruption Injector & Ground-Truth Catalog

Per SRS §4.6 REQ-1 and REQ-2, all simulated disruptions must record explicit ground-truth labels for downstream multi-agent evaluation.

| Scenario ID | Event Type | Target Global ID | Ground Truth Action Class | Description |
|---|---|---|---|---|
| `SCENARIO-SUP-01` | `SUPPLIER_FAILURE` | `supplier:1` | `SWITCH_SUPPLIER` | Primary component supplier factory shutdown due to power grid failure |
| `SCENARIO-LOG-01` | `SHIPMENT_DELAY_CLUSTER` | `shipment:77202` | `REROUTE_SHIPMENT` | West Coast port congestion causing delay cluster across shipping lanes |
| `SCENARIO-WTH-01` | `WEATHER_EVENT` | `warehouse:1` | `EXPEDITE_SHIPPING` | Category 4 blizzard causing severe ground transport delay across Midwest corridor |
| `SCENARIO-STK-01` | `STOCK_OUT` | `inventory:101` | `REALLOCATE_INVENTORY` | Unexpected demand surge causing inventory stockout |
| `SCENARIO-GEO-01` | `GEOPOLITICAL_NEWS` | `supplier:5` | `EXPEDITE_SHIPPING` | Customs border inspection policy shift delaying component transport |
| `SCENARIO-CMP-01` | `COMPOUND_EVENT` | `supplier:2` | `SWITCH_SUPPLIER` | Compound typhoon outage and secondary supplier facility damage |

---

## 3. Real-Time Telemetry & Communication Protocol

1. **Primary Protocol:** WebSockets (`WS /api/v1/simulation/ws`)
   - Broadcasts JSON telemetry snapshots upon state changes or tick events.
   - Target Latency: $< 100\text{ ms}$ (measured average $< 15\text{ ms}$).
2. **Fallback Protocol:** HTTP Polling (`GET /api/v1/simulation/status`)
   - Triggered automatically if WebSocket reconnection attempts exceed 5 iterations.
   - Polling Interval: 5.0 seconds.
