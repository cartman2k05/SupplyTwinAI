# SupplyTwinAI — Phase 3 Execution Plan (Frontend Shell and Manager Dashboard)

**Document Path:** `docs/plans/phase-3-plan.md`  
**Status:** Pending Approval  
**Author:** Lead Engineer (AI Pair Programmer)  
**Date:** 2026-10-01  

---

## 1. Goal

Build the role-aware frontend shell, login view, JWT authentication state management, Shadcn UI / Tailwind CSS design system foundation, and Manager Dashboard KPIs and interactive risk charts fed by backend `/api/v1/` REST endpoints and historical/simulated data (§3.1, §4.7 UC-01).

---

## 2. SRS Requirements Covered

* **§3.1:** User Interface Requirements (modern typography, sleek dark mode theme, responsive layout).
* **§4.2 REQ-1 & REQ-2:** Login interface, JWT token storage in session, role-aware navigation bar hiding Admin areas from Managers.
* **§4.7 REQ-1 (UC-01):** Real-time Manager Dashboard overview: active shipments, at-risk shipment count, risk distribution.
* **§4.7 REQ-2:** Key KPI summary widgets visible without scrolling at 1366x768 resolution.
* **§4.7 REQ-3:** Interactive charts: Risk Distribution chart (Low/Medium/High) and Shipment Delay breakdown by mode.

---

## 3. Files and Modules to Create or Change

```text
SupplyTwinAI/
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── src/
│   │   ├── index.css                   # Tailwind design system, dark mode & HSL tokens
│   │   ├── main.jsx
│   │   ├── App.jsx                     # Router, AuthGuard & RoleGuard
│   │   ├── context/
│   │   │   └── AuthContext.jsx         # Auth state, login/logout, user role helper
│   │   ├── services/
│   │   │   └── api.js                  # Axios/Fetch API client with Bearer token header
│   │   ├── components/
│   │   │   ├── layout/
│   │   │   │   ├── Navbar.jsx          # Header, logo, system status & user profile dropdown
│   │   │   │   └── Sidebar.jsx         # Role-aware navigation links
│   │   │   └── dashboard/
│   │   │       ├── KPICard.jsx         # Metric widget with trend indicator
│   │   │       ├── RiskChart.jsx       # Chart.js Risk Distribution Doughnut chart
│   │   │       ├── DelayChart.jsx      # Chart.js Shipping Mode Delay Bar chart
│   │   │       └── DisruptionsTable.jsx# Recent disruption events table
│   │   └── pages/
│   │       ├── Login.jsx               # Login screen with validation & dev helper
│   │       ├── Dashboard.jsx           # Manager Dashboard page
│   │       ├── Shipments.jsx           # Shipments view placeholder
│   │       ├── Inventory.jsx           # Inventory view placeholder
│   │       ├── Suppliers.jsx           # Suppliers view placeholder
│   │       └── AdminConfig.jsx         # Admin config view placeholder
```

---

## 4. Schema and API Changes

* No database schema changes.
* Frontend consumes backend REST API endpoints:
  * `POST /api/v1/auth/login` (Authentication)
  * `GET /api/v1/auth/me` (Profile retrieval)
  * `GET /api/v1/orders/` & `GET /api/v1/shipments/` (KPI calculations)
  * `GET /api/v1/inventory/` (Inventory alerts)
  * `GET /api/v1/suppliers/` (Supplier reliability averages)
  * `GET /api/v1/admin/config` & `PUT /api/v1/admin/config` (Admin config page)

---

## 5. Test List (Phase 3)

* `test_login_ui_redirection`: Unauthenticated user attempting to view `/dashboard` is redirected to `/login`.
* `test_manager_navigation`: Logging in as `manager@supplytwin.ai` displays Manager Dashboard and hides Admin navigation items (`/admin/config`, `/admin/etl`).
* `test_admin_navigation`: Logging in as `admin@supplytwin.ai` displays Admin navigation items.
* `test_kpi_rendering_1366x768`: Summary KPI cards render above the fold at 1366x768 viewport without vertical scrollbar requirement.
* `test_market_filter_update`: Selecting a Market filter (e.g. Europe) updates dashboard metrics dynamically.
* `test_dashboard_api_integration`: Dashboard fetches live data from backend `/api/v1/orders/` and `/api/v1/shipments/`.

---

## 6. Measurable Acceptance Criteria

* Login page authenticates users via backend `/api/v1/auth/login` and persists JWT token.
* Manager Dashboard displays all 4 primary KPI cards visible at 1366x768 resolution without scrolling.
* Admin area navigation links are completely hidden when logged in as a Manager role.
* Web application passes frontend build (`npm run build`) without compilation or linting errors.

---

## 7. Risks and Technical Mitigations

1. **Visual Layout Clipping at 1366x768:**
   * *Mitigation:* Responsive CSS grid layout using tight padding (`p-4`), compact KPI widgets, and `md:grid-cols-4` breakpoint.
2. **Chart.js Rendering in Dark Mode:**
   * *Mitigation:* Explicit dark theme palette colors (`#3b82f6`, `#10b981`, `#f59e0b`, `#ef4444`) with slate grid lines.

---

## 8. Open Questions

None. Chart.js for dashboard charts and market filtering were approved in previous reviews.

---

## 9. Paper Artifacts to Capture (Phase 3)

* `paper/artifacts/phase3/dashboard_manager_view.png` (Screenshot of Manager Dashboard UI)
* `paper/artifacts/phase3/login_screen.png` (Screenshot of Login screen UI)
* `paper/artifacts/phase3/admin_config_view.png` (Screenshot of Admin Configuration UI)
* `paper/artifacts/phase3/frontend_component_tree.txt` (Frontend component hierarchy tree)

---

## 10. Explicit List of What is Out of Scope for Phase 3

* Live WebSocket push updates (Deferred to Phase 4)
* Neo4j React Flow Digital Twin graph view (Deferred to Phase 5)
* GraphRAG AI Assistant chat panel (Deferred to Phase 6)
* Recommendation approval center workflow (Deferred to Phase 8)
