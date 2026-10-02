# SupplyTwinAI — Phase 10 Execution Plan (Admin, Reports, CSV Export & System Hardening)

**Document Path:** `docs/plans/phase-10-plan.md`  
**Status:** Pending Approval  
**Author:** Lead Engineer (AI Pair Programmer)  
**Date:** 2026-10-02  

---

## 1. Goal

Implement the system administration ETL run monitor UI (`EtlMonitor.jsx`), operational CSV report export endpoints (`/api/v1/reports/export/{resource}`), CSV export UI buttons across operational dashboards, enforce strict weight/threshold validation in Admin Config (§4.9 REQ-2), perform security controls & RBAC audit against SRS §5.3 (JWT expiration, role separation, prompt injection defense, graceful degradation), and run concurrent user load check (NFR-P2 baseline 5 concurrent users).

---

## 2. SRS Requirements Covered

* **§4.1 REQ-4 & §4.9 (ETL Run Monitoring & Data Quality Audit):**
  - Interactive ETL Run Monitor screen displaying historical ETL run seed, raw file name, loaded records, rejected records, flagged records, and execution duration.
* **§4.10 REQ-1 & REQ-2 (CSV Report Export):**
  - Downloadable CSV report export endpoints (`GET /api/v1/reports/export/{resource}`) producing formatted operational CSV reports for Orders, Shipments, Inventory, Suppliers, Recommendations, and Audit Logs.
* **§4.9 REQ-2 (Admin Config Validation):**
  - Validation enforcement: Risk weights must sum to 1.0 ($\pm 0.01$), threshold ranges constrained to $[0.0, 100.0]$, live config persistence without service redeployment.
* **§5.3 Security Review & NFR Checklist:**
  - Audit logging of all administrative and managerial actions (`audit_log`).
  - Verification of RBAC role isolation (Manager token gets 403 Forbidden on `/admin/config` and `/admin/etl`).
  - Graceful degradation under external API timeouts.
  - Concurrency load test supporting 5 concurrent simulated users.

---

## 3. Files and Modules to Create or Change

```text
SupplyTwinAI/
├── backend/
│   ├── app/
│   │   ├── api/v1/
│   │   │   ├── reports.py              # CSV export endpoints (/export/{resource})
│   │   │   └── router.py               # Includes reports router under /api/v1
│   │   └── services/
│   │       └── report_service.py       # CSV formatting engine for operational entities
│   └── tests/
│       └── test_reports_and_admin.py  # Unit tests for CSV report exports, config validation, & 5-user load check
├── frontend/
│   └── src/
│       ├── pages/
│       │   └── EtlMonitor.jsx          # Interactive ETL Run Monitor UI
│       ├── components/
│       │   └── ExportCsvButton.jsx     # Reusable CSV export button component
│       ├── App.jsx                      # Connect /admin/etl route to EtlMonitor component
│       └── services/
│           └── api.js                   # Add export report API helper methods
└── paper/
    └── artifacts/
        └── phase10/
            ├── admin_config_validation_spec.md  # Admin validation rules & RBAC specification
            ├── csv_export_schema_sample.md       # Data dictionary & CSV export sample formats
            └── nfr_security_audit_checklist.md   # SRS §5 NFR compliance checklist with empirical evidence
```

---

## 4. Schema and API Changes

### 4.1 Versioned REST Endpoints (`/api/v1/reports`)
* `GET /api/v1/reports/export/orders` $\rightarrow$ Download CSV report of Order records with status and delivery delay fields.
* `GET /api/v1/reports/export/shipments` $\rightarrow$ Download CSV report of Shipment and LiveShipment records.
* `GET /api/v1/reports/export/inventory` $\rightarrow$ Download CSV report of Warehouse Inventory stock and reorder point metrics.
* `GET /api/v1/reports/export/suppliers` $\rightarrow$ Download CSV report of Supplier reliability, defect rate, and alternate pool data.
* `GET /api/v1/reports/export/recommendations` $\rightarrow$ Download CSV report of generated recommendation candidate status and manager decision logs.
* `GET /api/v1/reports/export/audit` $\rightarrow$ Download CSV report of system Audit Logs.

---

## 5. Test List (Phase 10)

* `test_admin_config_weight_validation`: Verify updating config with weights summing to $\neq 1.0$ returns 400 Bad Request.
* `test_admin_config_threshold_validation`: Verify invalid threshold inputs outside $[0, 100]$ return 400 Bad Request.
* `test_csv_report_export_orders`: Verify `GET /api/v1/reports/export/orders` returns valid `text/csv` header and non-empty CSV rows.
* `test_csv_report_export_recommendations`: Verify exporting recommendation records produces formatted CSV output.
* `test_rbac_admin_route_protection`: Verify manager token receives 403 Forbidden on `/admin/config` and `/admin/etl`.
* `test_concurrent_5_users_load`: Simulate 5 concurrent API clients triggering multi-agent pipeline and graph queries simultaneously without errors or thread lockup.

---

## 6. Measurable Acceptance Criteria

* Admin Config validates that weights sum to 1.0 and thresholds remain within $[0, 100]$.
* ETL Monitor UI (`EtlMonitor.jsx`) renders historical ETL run history with loaded, rejected, and flagged counts.
* CSV export endpoints return valid downloadable `.csv` attachments for all 6 operational entities.
* All backend pytest unit tests pass (53 original + new report & load tests).
* Frontend production build compiles cleanly.

---

## 7. Risks and Technical Mitigations

1. **Large Dataset CSV Streaming Latency:**
   - *Mitigation:* `report_service.py` uses StreamingResponse with Python's built-in `csv.writer` writing chunks directly to the client stream.
2. **Concurrency Resource Exhaustion:**
   - *Mitigation:* SQLite WAL mode and SQLAlchemy thread connection pooling (`pool_size=10`, `max_overflow=20`) to handle 5 concurrent requests without database locking.

---

## 8. Open Questions

None. CSV export requirements (§4.10 REQ-1) and Admin Config constraints (§4.9 REQ-2) are locked.

---

## 9. Paper Artifacts to Capture (Phase 10)

* `paper/artifacts/phase10/admin_config_validation_spec.md` (Admin config validation rules & RBAC specification)
* `paper/artifacts/phase10/csv_export_schema_sample.md` (CSV report export schemas & sample output snippets)
* `paper/artifacts/phase10/nfr_security_audit_checklist.md` (SRS §5 NFR and security audit compliance table with evidence)

---

## 10. Explicit List of What is Out of Scope for Phase 10

* Cloud hosting on Render / Supabase / Vercel (Phase 11)
* Final paper draft writeup & sitemap documentation (Phase 11)

---

**STOP & WAIT:** Plan written. Awaiting user approval before proceeding to implementation.
