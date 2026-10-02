# SupplyTwinAI Manager Dashboard UI Layout Specification

**Document Path:** `paper/artifacts/phase3/dashboard_ui_layout.md`  
**SRS Reference:** §3.1, §4.7 UC-01, REQ-1, REQ-2, REQ-3  
**Date:** 2026-10-01  

---

## 1. UI Layout Overview (1366x768 Resolution Target)

The Manager Dashboard is designed to fit all primary summary widgets **above the fold** at 1366x768 resolution without requiring vertical scrolling (§4.7 REQ-2).

```text
+-----------------------------------------------------------------------------------+
|  [Logo] SupplyTwinAI      (o) Digital Twin Active           [User: Manager] [Logout] |
+------------------+----------------------------------------------------------------+
| Operations Center|  Dashboard  | Market Filter: [All Markets v]   [Refresh]        |
|                  |                                                                |
| - Dashboard      |  +---------------+ +---------------+ +---------------+ +----------+ |
| - Shipments      |  | In-Transit    | | At-Risk       | | Supplier      | | Pending  | |
| - Inventory      |  | 65,752        | | 14            | | 94.2%         | | 3        | |
| - Suppliers      |  +---------------+ +---------------+ +---------------+ +----------+ |
| - Digital Twin   |                                                                |
| - AI Assistant   |  +---------------------------+ +----------------------------+ |
| - Recommendations|  | Risk Distribution Chart   | | Delay by Shipping Mode     | |
|                  |  | (Chart.js Doughnut)       | | (Chart.js Bar Chart)       | |
| [Admin Section]  |  +---------------------------+ +----------------------------+ |
| (Hidden for Mgr) |                                                                |
|                  |  +----------------------------------------------------------+ |
|                  |  | Active Disruption Signals Table                          | |
|                  |  +----------------------------------------------------------+ |
+------------------+----------------------------------------------------------------+
```

## 2. Component Design Specifications

1. **KPI Card Grid:** 4 responsive metric widgets rendering key metrics (Active In-Transit Shipments, At-Risk Count, Avg Supplier Reliability, Pending Recommendations).
2. **Chart.js Risk Distribution Doughnut:** Visualizes Low (< 33), Medium (33–66), and High (> 66) composite risk score bands with slate tooltips.
3. **Chart.js Delay Breakdown Bar Chart:** Visualizes average transit delay days across First Class, Second Class, Same Day, and Standard Class shipping modes.
4. **Active Disruptions Table:** Renders active disruption alerts with target entity global IDs, severity progress bars, and status badges.
5. **RBAC Guard Enforcement:** Sidebar Navigation dynamically excludes System Administration links (`/admin/config`, `/admin/etl`) when logged in as a Manager.
