# Admin Configuration Validation & Governance Specification

**Document Path:** `paper/artifacts/phase10/admin_config_validation_spec.md`  
**System Module:** System Administration & Agent Configuration (`/api/v1/admin/config`)  
**SRS Reference:** §4.9 REQ-1 & REQ-2, §5.3 Security Controls  

---

## 1. Overview

The System Administration Configuration module enables authorized System Administrators (`admin` role) to modify multi-agent risk scoring weights, risk band thresholds, and recommendation alert triggers dynamically at runtime without requiring application restart or code redeployment.

---

## 2. Dynamic Parameters & Validation Rules

| Parameter Name | Data Type | Default Value | Validation Constraint | Description |
|---|---|---|---|---|
| `risk_weight_supplier` | `FLOAT` | `0.30` | $[0.0, 1.0]$, $\sum w_i = 1.0 \pm 0.01$ | Composite risk weight allocated to `SupplierAgent` |
| `risk_weight_shipment` | `FLOAT` | `0.30` | $[0.0, 1.0]$, $\sum w_i = 1.0 \pm 0.01$ | Composite risk weight allocated to `ShipmentAgent` |
| `risk_weight_inventory` | `FLOAT` | `0.20` | $[0.0, 1.0]$, $\sum w_i = 1.0 \pm 0.01$ | Composite risk weight allocated to `InventoryAgent` |
| `risk_weight_external` | `FLOAT` | `0.20` | $[0.0, 1.0]$, $\sum w_i = 1.0 \pm 0.01$ | Composite risk weight allocated to `ExternalIntelligenceAgent` |
| `threshold_low_medium` | `FLOAT` | `33.0` | $0.0 \le \text{Low/Med} \le \text{Med/High} \le 100.0$ | Upper risk score bound for `LOW` risk classification |
| `threshold_medium_high` | `FLOAT` | `66.0` | $\text{Low/Med} \le \text{Med/High} \le 100.0$ | Upper risk score bound for `MEDIUM` risk classification |
| `alert_threshold_recommendation` | `FLOAT` | `60.0` | $[0.0, 100.0]$ | Minimum composite risk score triggering candidate recommendations |

---

## 3. RBAC Access Control Matrix

| Endpoint Route | HTTP Method | Viewer Role | Supply Chain Manager Role | System Administrator Role |
|---|---|---|---|---|
| `/api/v1/admin/config` | `GET` | 403 Forbidden | 403 Forbidden | 200 OK |
| `/api/v1/admin/config` | `PUT` | 403 Forbidden | 403 Forbidden | 200 OK |
| `/api/v1/etl/history` | `GET` | 403 Forbidden | 403 Forbidden | 200 OK |
| `/api/v1/etl/run` | `POST` | 403 Forbidden | 403 Forbidden | 200 OK |
| `/api/v1/reports/export/{resource}` | `GET` | 403 Forbidden | 200 OK | 200 OK |
| `/api/v1/recommendations/{id}/approve` | `POST` | 403 Forbidden | 200 OK | 200 OK |

---

## 4. Enforcement Verification

1. **Weight Sum Enforcement:** Any configuration update where $\sum w_i \neq 1.0$ returns `400 Bad Request` with detail message: `"Risk weights must sum to 1.0"`.
2. **Threshold Bound Enforcement:** Any configuration update where `threshold_low_medium > threshold_medium_high` returns `400 Bad Request`.
3. **Audit Logging:** Every successful configuration update logs an immutable entry to `audit_log` with administrator identity and updated weights payload.
