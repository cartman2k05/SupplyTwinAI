# Operational CSV Report Export Specification & Sample Data

**Document Path:** `paper/artifacts/phase10/csv_export_schema_sample.md`  
**System Module:** Operational Report Export Engine (`/api/v1/reports/export/{resource}`)  
**SRS Reference:** §4.10 REQ-1 & REQ-2  

---

## 1. Supported Report Resources

The CSV export engine provides streaming downloadable operational data attachments (`media_type="text/csv"`) across six primary domain resources:
1. `orders`: Order transaction history, customer global IDs, scheduled vs real shipping days, delivery delay metrics, order total USD.
2. `shipments`: Shipment execution state, shipping mode risk, scheduled days, delay days, assigned vehicle global IDs.
3. `inventory`: Warehouse inventory stock balances, reorder points, average daily demand, restock lead days, synthetic flags.
4. `suppliers`: Supplier reliability metrics, on-time delivery rates, defect rates, lead times, country/region centroids, alternate pool flags.
5. `recommendations`: Multi-agent mitigation recommendation candidate history, confidence scores, human approval statuses (`pending`, `accepted`, `rejected`).
6. `audit`: Immutable audit log trail for system events, user identities, action types, resource IDs, and decision rationales.

---

## 2. Sample Output Snippets

### 2.1 Orders Report (`supplytwin_orders_report.csv`)
```csv
order_id,global_id,customer_global_id,category_name,order_status,days_for_shipping_real,days_for_shipment_scheduled,delivery_delay_days,order_total_usd,created_at
1,order:1,customer:101,Cleats,COMPLETE,3,3,0,129.99,2026-10-01T12:00:00
2,order:2,customer:102,Men's Footwear,LATE_DELIVERY,5,3,2,245.50,2026-10-01T12:15:00
```

### 2.2 Recommendations Report (`supplytwin_recommendations_report.csv`)
```csv
recommendation_id,global_id,entity_global_id,action_type,title,description,confidence_score,status,created_at
1,recommendation:a1f8c92e,supplier:1,SWITCH_SUPPLIER,Activate Alternate Component Supplier Pool,Reallocate order volume to vetted alternate suppliers with higher on-time delivery rates to mitigate supplier disruption.,0.88,accepted,2026-10-01T14:20:00
2,recommendation:b7d4e11a,shipment:77202,REROUTE_SHIPMENT,Reroute Inland Container Shipping Lane,Bypass congested port bottleneck and reassign shipment to secondary ground logistics corridor.,0.75,rejected,2026-10-01T14:35:00
```

### 2.3 Audit Log Report (`supplytwin_audit_report.csv`)
```csv
log_id,user_id,user_email,action,resource_type,resource_id,details_json,timestamp
101,2,manager@supplytwin.ai,RECOMMENDATION_ACCEPTED,recommendation,recommendation:a1f8c92e,"{""action_type"": ""SWITCH_SUPPLIER"", ""notes"": ""Approved after reviewing alternate capacity""}",2026-10-01T14:20:05
```
