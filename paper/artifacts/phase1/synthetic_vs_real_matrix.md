# SupplyTwinAI Data Transparency Matrix: Synthetic vs. Real Grounding

**Document Path:** `paper/artifacts/phase1/synthetic_vs_real_matrix.md`  
**Target Paper Section:** Data & Simulation Methodology  
**Date:** 2026-10-01  

---

## Data Provenance Summary

Every table and column in SupplyTwinAI is explicitly classified as either **Real (DataCo)** or **Synthetic/Simulated**. Synthetic attributes are deterministically generated from empirical distributions of the real historical dataset to maintain physical realism without fabricating ungrounded results.

| Entity Table | Provenance | Total Rows | Key Grounded Basis | Synthetic Columns / Flags |
|---|---|---|---|---|
| `customers` | Real | 20,652 | DataCo customer profiles & segmentations | None (PII email/password stripped) |
| `products` | Real | 118 | DataCo product catalog, category IDs & prices | None |
| `orders` | Real | 65,752 | DataCo historical order placements (2015-2018) | `assigned_warehouse_id` (Mapped to region), `is_simulated` flag |
| `shipments` | Real | 65,752 | DataCo shipping modes, scheduled & real transit days | `is_simulated` flag |
| `order_items` | Real | 180,519 | DataCo order line items, sales, discounts & margins | `is_simulated` flag |
| `suppliers` | Synthetic | 150 | Category proxy grounding (1 primary + 2 alternates / category) | `is_synthetic = True` (all rows) |
| `supplier_products` | Synthetic | 450+ | Category product coverage, cost & lead time trade-offs | `is_synthetic = True` (all rows) |
| `warehouses` | Synthetic | 23 | 1 proxy per DataCo Order Region with region centroids | `is_synthetic = True` (all rows) |
| `warehouse_inventory` | Synthetic | 2,714 | `avg_daily_demand` calculated from historical 3-year volume | `is_synthetic = True` (all rows) |
| `vehicles` | Synthetic | 30 | Fleet logistics pool (Semi-Trailer, Box Truck, Cargo Van) | `is_synthetic = True` (all rows) |
