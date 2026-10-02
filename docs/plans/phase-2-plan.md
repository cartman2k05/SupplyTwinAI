# SupplyTwinAI — Phase 2 Execution Plan (Database, API Foundation, Auth)

**Document Path:** `docs/plans/phase-2-plan.md`  
**Status:** Pending Approval  
**Author:** Lead Engineer (AI Pair Programmer)  
**Date:** 2026-10-01  

---

## 1. Goal

Establish the PostgreSQL relational database layer (all 20 target tables), Alembic DDL migrations, ETL database loader with audit logging (§4.1 REQ-2, §4.9 REQ-1), JWT authentication service, Role-Based Access Control (Manager vs Admin), versioned REST API endpoints under `/api/v1` (§3.3), and complete OpenAPI documentation.

---

## 2. SRS Requirements Covered

* **§4.1 REQ-1:** Database storage of clean historical and simulated supply chain data.
* **§4.1 REQ-2:** ETL data loading with validation error logging and `loaded_records`, `rejected_records`, and `flagged_records` audit tracking.
* **§4.1 REQ-3:** Storage of namespaced global unique IDs (`type:sourceid`) with primary and unique key indexing across all entity tables.
* **§4.1 REQ-4:** Customer-side origin coordinate storage (`customer_latitude`, `customer_longitude`).
* **§4.1 REQ-5:** Simulated state column (`is_simulated`) on `orders`, `order_items`, and `shipments`.
* **§4.2 REQ-1:** User authentication and session management using signed JWT tokens.
* **§4.2 REQ-2:** Role-Based Access Control (RBAC) enforcing distinct permissions for **Supply Chain Manager** and **System Administrator**.
* **§4.9 REQ-1:** Admin ETL run status monitoring and audit history logging (`etl_runs`, `audit_log`).
* **§4.9 REQ-2:** Agent risk thresholds and composite score weights editable configuration storage (`agent_config`).
* **§5.3 NFR-S1 to NFR-S4:** Security, credential isolation, password hashing, and RBAC endpoint protection.

---

## 3. Files and Modules to Create or Change

```text
SupplyTwinAI/
├── backend/
│   ├── app/
│   │   ├── db/
│   │   │   ├── database.py         # Async SQLAlchemy engine & sessionmaker
│   │   │   └── base.py             # Base ORM model declaration
│   │   ├── models/                 # SQLAlchemy 2.0 ORM domain models
│   │   │   ├── user.py
│   │   │   ├── customer.py
│   │   │   ├── product.py
│   │   │   ├── supplier.py
│   │   │   ├── warehouse.py
│   │   │   ├── order.py
│   │   │   ├── shipment.py
│   │   │   ├── vehicle.py
│   │   │   ├── event.py
│   │   │   ├── recommendation.py
│   │   │   ├── config.py
│   │   │   └── audit.py
│   │   ├── auth/                   # Authentication & RBAC security
│   │   │   ├── security.py         # Bcrypt password hashing & JWT handling
│   │   │   └── dependencies.py     # Current user & RBAC role guards
│   │   ├── schemas/                # Pydantic v2 API request/response schemas
│   │   │   ├── auth.py
│   │   │   ├── order.py
│   │   │   ├── shipment.py
│   │   │   ├── inventory.py
│   │   │   ├── supplier.py
│   │   │   ├── etl.py
│   │   │   └── config.py
│   │   └── api/v1/                 # Versioned REST API endpoints
│   │       ├── router.py
│   │       ├── auth.py             # /auth/login, /auth/me
│   │       ├── orders.py           # /orders/
│   │       ├── shipments.py        # /shipments/
│   │       ├── inventory.py        # /inventory/
│   │       ├── suppliers.py        # /suppliers/
│   │       ├── etl.py              # /etl/run, /etl/history (Admin)
│   │       └── admin.py            # /admin/config (Admin)
│   └── tests/
│       ├── test_db_loader.py
│       ├── test_auth.py
│       ├── test_rbac.py
│       └── test_api_v1.py
├── database/
│   ├── etl/
│   │   └── db_loader.py            # Loads datasets/v3_etl/ CSVs into Postgres
│   └── migrations/                 # Alembic migrations
│       ├── env.py
│       ├── script.py.mako
│       └── versions/
│           └── 001_initial_schema.py
```

---

## 4. Schema and API Changes

### 4.1 Target PostgreSQL Tables (20 total)
1. `users` (id, email, hashed_password, full_name, role, is_active, created_at)
2. `customers` (customer_id, global_id, first_name, last_name, country, city, state, segment, zipcode)
3. `products` (product_id, global_id, name, category_id, category, price)
4. `suppliers` (supplier_id, global_id, name, category_id, category, country, is_primary, on_time_rate, defect_rate, lead_time_days, rating, is_synthetic)
5. `supplier_products` (supplier_id, product_id, is_primary, unit_cost_multiplier, lead_time_days, on_time_rate, defect_rate, is_synthetic)
6. `warehouses` (warehouse_id, global_id, name, region, latitude, longitude, capacity, is_synthetic)
7. `warehouse_inventory` (inventory_id, global_id, warehouse_id, product_id, stock, reorder_point, avg_daily_demand, restock_lead_days, is_synthetic)
8. `orders` (order_id, global_id, customer_id, customer_global_id, order_date, order_status, market, order_region, destination_country, destination_city, destination_state, customer_latitude, customer_longitude, assigned_warehouse_id, assigned_warehouse_id_is_synthetic, is_simulated)
9. `shipments` (shipment_id, global_id, order_id, order_global_id, shipping_mode, days_scheduled, days_real, delivery_status, shipping_date, is_simulated)
10. `order_items` (item_id, global_id, order_id, order_global_id, product_id, product_global_id, quantity, unit_price, discount, total, profit_ratio, sales_per_customer, benefit_per_order, is_simulated)
11. `vehicles` (vehicle_id, global_id, license_plate, vehicle_type, capacity_kg, status, is_synthetic)
12. `live_shipments` (shipment_id, current_latitude, current_longitude, current_status, eta, assigned_vehicle_id, updated_at)
13. `disruption_events` (event_id, global_id, event_type, severity, target_global_id, description, status, created_at)
14. `external_signals` (signal_id, source, signal_type, headline, raw_data, severity, matched_global_id, timestamp)
15. `agent_outputs` (output_id, agent_name, entity_global_id, output_data, execution_time_ms, created_at)
16. `recommendations` (recommendation_id, global_id, entity_global_id, action_type, title, description, confidence_score, status, reasoning_json, memory_citations_json, created_at, updated_at)
17. `disruption_memory` (memory_id, event_type, entity_global_id, scenario_fingerprint, root_cause, action_taken, outcome_score, resolution_notes, created_at)
18. `agent_config` (config_id, risk_weight_supplier, risk_weight_shipment, risk_weight_inventory, risk_weight_external, threshold_low_medium, threshold_medium_high, alert_threshold_recommendation, updated_by, updated_at)
19. `etl_runs` (run_id, seed, raw_file_name, loaded_records, rejected_records, flagged_records, duration_seconds, status, created_at)
20. `audit_log` (log_id, user_id, user_email, action, resource_type, resource_id, details_json, timestamp)

### 4.2 Seed Users Created in Migration
* **Manager User:** `manager@supplytwin.ai` / Password: `ManagerPassword123!` (Role: `manager`)
* **Admin User:** `admin@supplytwin.ai` / Password: `AdminPassword123!` (Role: `admin`)

### 4.3 Versioned REST API Endpoints (`/api/v1/`)
* `POST /api/v1/auth/login` $\rightarrow$ Authenticate user & return JWT access token
* `GET /api/v1/auth/me` $\rightarrow$ Return currently authenticated user profile
* `GET /api/v1/orders/` & `GET /api/v1/orders/{order_id}` $\rightarrow$ List & retrieve order records
* `GET /api/v1/shipments/` & `GET /api/v1/shipments/{shipment_id}` $\rightarrow$ List & retrieve shipment records
* `GET /api/v1/inventory/` $\rightarrow$ List warehouse inventory levels against reorder points
* `GET /api/v1/suppliers/` $\rightarrow$ List primary and alternate suppliers with performance metrics
* `POST /api/v1/etl/load` $\rightarrow$ Trigger ETL database loader (Admin only)
* `GET /api/v1/etl/history` $\rightarrow$ List historical ETL import runs (Admin only)
* `GET /api/v1/admin/config` & `PUT /api/v1/admin/config` $\rightarrow$ View and update agent weights & thresholds (Admin only)

---

## 5. Test List (Phase 2)

* `test_db_migration_clean_schema`: Verify Alembic migration applies cleanly and creates all 20 tables with correct indexes, primary keys, and foreign keys.
* `test_db_loader_execution`: Run `db_loader.py`; verify database tables populate from `datasets/v3_etl/` CSVs and record counts match validation reports.
* `test_etl_runs_audit_logging`: Verify `etl_runs` table records loaded/rejected/flagged counts and duration accurately (§4.1 REQ-2, §4.9 REQ-1).
* `test_jwt_auth_login`: Verify valid credentials yield signed JWT token and invalid credentials return 401 Unauthorized (§4.2 REQ-1).
* `test_rbac_manager_access`: Verify Manager token grants access to `/orders/`, `/shipments/`, `/inventory/`, `/suppliers/`.
* `test_rbac_admin_enforcement`: Verify Manager token attempting to call `/etl/load` or `/admin/config` is blocked with 403 Forbidden (§4.2 REQ-2).
* `test_admin_config_update`: Verify Admin token can update agent risk weights and thresholds with validation (weights sum to 1.0).
* `test_openapi_swagger_schema`: Verify FastAPI `/docs` renders complete OpenAPI spec for all endpoints.

---

## 6. Measurable Acceptance Criteria

* Alembic migration executes without errors and initializes all 20 target tables.
* Database ETL loader imports all 180,519 order items into local PostgreSQL in under 30 seconds.
* `pytest` test suite passes 100% of unit and integration tests for Auth, RBAC, ETL Loader, and API endpoints.
* Attempting Admin operations with a Manager JWT token returns a strict `403 Forbidden` response.
* FastAPI interactive Swagger documentation is accessible at `http://localhost:8000/docs`.

---

## 7. Risks and Technical Mitigations

1. **Large Bulk Insert Latency (PostgreSQL 180k order items):**
   * *Mitigation:* Use SQLAlchemy `asyncpg` bulk insert or execute raw multi-row insert statements in chunked batches of 10,000 rows.
2. **Password Hashing Speed in Test Suite:**
   * *Mitigation:* Configure `passlib` / `bcrypt` with lower rounds during test execution to maintain sub-second test suite speed while preserving production security.

---

## 8. Open Questions

None. All structural parameters (8-hour JWT expiration, seed user emails/roles, bcrypt hashing) were confirmed during Phase 1 review.

---

## 9. Paper Artifacts to Capture (Phase 2)

* `paper/artifacts/phase2/database_er_diagram.png` (Database Entity-Relationship diagram topology)
* `paper/artifacts/phase2/db_table_counts.json` (Record counts in PostgreSQL after ETL database load)
* `paper/artifacts/phase2/swagger_openapi_spec.json` (Complete exported OpenAPI 3.0 specification)
* `paper/artifacts/phase2/rbac_matrix.md` (RBAC permissions matrix table comparing Manager vs Admin roles)

---

## 10. Explicit List of What is Out of Scope for Phase 2

* Neo4j Knowledge Graph loading and sync (Deferred to Phase 5)
* Live simulation clock engine and WebSocket updates (Deferred to Phase 4)
* LangGraph multi-agent nodes and GraphRAG context retrieval (Deferred to Phases 6 & 7)
* Frontend dashboard UI implementation (Deferred to Phase 3)
