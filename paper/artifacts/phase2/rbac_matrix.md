# SupplyTwinAI Role-Based Access Control (RBAC) Permissions Matrix

**Document Path:** `paper/artifacts/phase2/rbac_matrix.md`  
**SRS Reference:** §4.2 REQ-2, §5.3 NFR-S2  
**Date:** 2026-10-01  

---

## Role Permissions Matrix

| Endpoint Path | HTTP Method | Minimum Required Role | Description |
|---|---|---|---|
| `/api/v1/auth/login` | POST | Public | User authentication & JWT token generation |
| `/api/v1/auth/me` | GET | Manager / Admin | Get authenticated user profile |
| `/api/v1/orders/` | GET | Manager / Admin | List historical & simulated orders |
| `/api/v1/orders/{id}` | GET | Manager / Admin | Get order details |
| `/api/v1/shipments/` | GET | Manager / Admin | List shipment tracking status |
| `/api/v1/shipments/{id}` | GET | Manager / Admin | Get shipment tracking details |
| `/api/v1/inventory/` | GET | Manager / Admin | View warehouse stock & reorder points |
| `/api/v1/suppliers/` | GET | Manager / Admin | View supplier performance metrics |
| `/api/v1/suppliers/{id}` | GET | Manager / Admin | Get detailed supplier profile |
| `/api/v1/etl/load` | POST | System Administrator | Trigger CSV database import (§4.1 REQ-2) |
| `/api/v1/etl/history` | GET | System Administrator | View historical ETL run audit logs (§4.9 REQ-1) |
| `/api/v1/admin/config` | GET | System Administrator | Read agent risk weights & thresholds (§4.9 REQ-2) |
| `/api/v1/admin/config` | PUT | System Administrator | Update agent risk weights & thresholds (§4.9 REQ-2) |
