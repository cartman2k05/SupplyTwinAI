# SupplyTwinAI Master Data Dictionary (ETL v3 Specification)

**Version:** 3.0  
**Generated:** 2026-10-01  
**Source Dataset:** DataCo Supply Chain Dataset (Jan 2015 – Jan 2018) + Grounded Synthetic Extensions  

---

## Overview & Synthetic Flag Legend

* `is_synthetic = False`: Real historical record extracted directly from the DataCo dataset.
* `is_synthetic = True`: Grounded synthetic record or column introduced to fulfill SRS requirements (§4.1, §4.4) and enable multi-agent decision support.

---

## Table Schemas

### 1. `customers`
* **Source:** Real (DataCo)
* **Grain:** One row per customer (`customer_id`).
* **Columns:**
  | Column Name | Type | PK/FK | Global ID Format | Description | Is Synthetic |
  |---|---|---|---|---|---|
  | `customer_id` | Integer | PK | — | Internal integer primary key | `False` |
  | `global_id` | String | Unique | `customer:ID` | Namespaced global ID (§4.1 REQ-3) | `False` |
  | `first_name` | String | — | — | Customer first name | `False` |
  | `last_name` | String | — | — | Customer last name (nulls filled with 'Unknown') | `False` |
  | `country` | String | — | — | Customer country | `False` |
  | `city` | String | — | — | Customer city | `False` |
  | `state` | String | — | — | Customer state | `False` |
  | `segment` | String | — | — | Customer segment (Consumer, Corporate, Home Office) | `False` |
  | `zipcode` | Float | — | — | Customer zipcode (nulls filled with median 19380.0) | `False` |

### 2. `products`
* **Source:** Real (DataCo)
* **Grain:** One row per product (`product_id`).
* **Columns:**
  | Column Name | Type | PK/FK | Global ID Format | Description | Is Synthetic |
  |---|---|---|---|---|---|
  | `product_id` | Integer | PK | — | Internal product primary key | `False` |
  | `global_id` | String | Unique | `product:ID` | Namespaced global ID (§4.1 REQ-3) | `False` |
  | `name` | String | — | — | Product name | `False` |
  | `category_id` | Integer | — | — | Product category ID | `False` |
  | `category` | String | — | — | Category name | `False` |
  | `price` | Float | — | — | Product unit price (USD) | `False` |

### 3. `orders`
* **Source:** Real + Synthetic Warehouse Assignment
* **Grain:** One row per order (`order_id`).
* **Columns:**
  | Column Name | Type | PK/FK | Global ID Format | Description | Is Synthetic |
  |---|---|---|---|---|---|
  | `order_id` | Integer | PK | — | Internal order primary key | `False` |
  | `global_id` | String | Unique | `order:ID` | Namespaced global ID (§4.1 REQ-3) | `False` |
  | `customer_id` | Integer | FK | — | FK to `customers.customer_id` | `False` |
  | `customer_global_id` | String | FK | `customer:ID` | Global ID FK to customer | `False` |
  | `order_date` | Datetime | — | — | Order placement datetime | `False` |
  | `order_status` | String | — | — | Order status (COMPLETE, PENDING, CANCELED, etc.) | `False` |
  | `market` | String | — | — | Order market region (USCA, Europe, LATAM, etc.) | `False` |
  | `order_region` | String | — | — | Order sub-region | `False` |
  | `destination_country` | String | — | — | Delivery destination country (normalized English) | `False` |
  | `destination_city` | String | — | — | Delivery destination city | `False` |
  | `destination_state` | String | — | — | Delivery destination state | `False` |
  | `customer_latitude` | Float | — | — | Customer origin latitude (§4.1 REQ-4) | `False` |
  | `customer_longitude` | Float | — | — | Customer origin longitude (§4.1 REQ-4) | `False` |
  | `assigned_warehouse_id` | Integer | FK | — | Assigned regional warehouse (§4.4 REQ-4) | `True` |
  | `assigned_warehouse_id_is_synthetic` | Boolean | — | — | Explicit column synthetic flag | `True` |
  | `is_simulated` | Boolean | — | — | Simulation state flag (§4.1 REQ-5) | `False` (for historical) |

### 4. `shipments`
* **Source:** Real (1:1 with orders)
* **Grain:** One row per shipment (`shipment_id`).
* **Columns:**
  | Column Name | Type | PK/FK | Global ID Format | Description | Is Synthetic |
  |---|---|---|---|---|---|
  | `shipment_id` | Integer | PK | — | Shipment primary key | `False` |
  | `global_id` | String | Unique | `shipment:ID` | Namespaced global ID (§4.1 REQ-3) | `False` |
  | `order_id` | Integer | FK | — | FK to `orders.order_id` | `False` |
  | `order_global_id` | String | FK | `order:ID` | Global ID FK to order | `False` |
  | `shipping_mode` | String | — | — | Shipping mode (First Class, Standard Class, etc.) | `False` |
  | `days_scheduled` | Integer | — | — | Scheduled shipping days | `False` |
  | `days_real` | Integer | — | — | Actual shipping days (Outcome feature) | `False` |
  | `delivery_status` | String | — | — | Delivery status (Outcome feature) | `False` |
  | `shipping_date` | Datetime | — | — | Dispatch datetime | `False` |
  | `is_simulated` | Boolean | — | — | Simulation state flag (§4.1 REQ-5) | `False` |

### 5. `order_items`
* **Source:** Real (DataCo line items)
* **Grain:** One row per order line item (`item_id`).
* **Columns:**
  | Column Name | Type | PK/FK | Global ID Format | Description | Is Synthetic |
  |---|---|---|---|---|---|
  | `item_id` | Integer | PK | — | Line item primary key | `False` |
  | `global_id` | String | Unique | `item:ID` | Namespaced global ID (§4.1 REQ-3) | `False` |
  | `order_id` | Integer | FK | — | FK to `orders.order_id` | `False` |
  | `order_global_id` | String | FK | `order:ID` | Global ID FK to order | `False` |
  | `product_id` | Integer | FK | — | FK to `products.product_id` | `False` |
  | `product_global_id` | String | FK | `product:ID` | Global ID FK to product | `False` |
  | `quantity` | Integer | — | — | Item quantity ordered | `False` |
  | `unit_price` | Float | — | — | Item unit price | `False` |
  | `discount` | Float | — | — | Item discount amount | `False` |
  | `total` | Float | — | — | Item line total price | `False` |
  | `profit_ratio` | Float | — | — | Profit margin ratio | `False` |
  | `sales_per_customer` | Float | — | — | Sales allocation | `False` |
  | `benefit_per_order` | Float | — | — | Net profit per order line | `False` |
  | `is_simulated` | Boolean | — | — | Simulation state flag (§4.1 REQ-5) | `False` |

### 6. `suppliers`
* **Source:** Grounded Synthetic (150 suppliers total: 50 primary + 100 alternates)
* **Grain:** One row per supplier (`supplier_id`).
* **Columns:**
  | Column Name | Type | PK/FK | Global ID Format | Description | Is Synthetic |
  |---|---|---|---|---|---|
  | `supplier_id` | Integer | PK | — | Supplier primary key | `True` |
  | `global_id` | String | Unique | `supplier:ID` | Namespaced global ID (§4.1 REQ-3) | `True` |
  | `name` | String | — | — | Supplier business name | `True` |
  | `category_id` | Integer | FK | — | Primary product category ID | `True` |
  | `category` | String | — | — | Category name | `True` |
  | `country` | String | — | — | Supplier location country | `True` |
  | `is_primary` | Boolean | — | — | Primary supplier flag for category | `True` |
  | `on_time_rate` | Float | — | — | On-time delivery rate [0.30, 0.98] | `True` |
  | `defect_rate` | Float | — | — | Defect rate sampled from Beta(2, 50) | `True` |
  | `lead_time_days` | Integer | — | — | Baseline order lead time in days | `True` |
  | `rating` | Float | — | — | Reliability rating [1.0, 5.0] | `True` |
  | `is_synthetic` | Boolean | — | — | Table synthetic flag | `True` |

### 7. `supplier_products`
* **Source:** Grounded Synthetic Junction Table (§4.4 REQ-2)
* **Grain:** Supplier $\times$ Product capability pair.
* **Columns:**
  | Column Name | Type | PK/FK | Global ID Format | Description | Is Synthetic |
  |---|---|---|---|---|---|
  | `supplier_id` | Integer | FK | — | FK to `suppliers.supplier_id` | `True` |
  | `product_id` | Integer | FK | — | FK to `products.product_id` | `True` |
  | `is_primary` | Boolean | — | — | Primary supplier flag for product | `True` |
  | `unit_cost_multiplier` | Float | — | — | Cost factor relative to base price | `True` |
  | `lead_time_days` | Integer | — | — | Specific product lead time | `True` |
  | `on_time_rate` | Float | — | — | Product-specific on-time rate | `True` |
  | `defect_rate` | Float | — | — | Product-specific defect rate | `True` |
  | `is_synthetic` | Boolean | — | — | Table synthetic flag | `True` |

### 8. `warehouses`
* **Source:** Grounded Synthetic (23 regional warehouses)
* **Grain:** One row per regional warehouse (`warehouse_id`).
* **Columns:**
  | Column Name | Type | PK/FK | Global ID Format | Description | Is Synthetic |
  |---|---|---|---|---|---|
  | `warehouse_id` | Integer | PK | — | Warehouse primary key | `True` |
  | `global_id` | String | Unique | `warehouse:ID` | Namespaced global ID (§4.1 REQ-3) | `True` |
  | `name` | String | — | — | Regional warehouse name | `True` |
  | `region` | String | — | — | Associated order region | `True` |
  | `latitude` | Float | — | — | Warehouse centroid latitude | `True` |
  | `longitude` | Float | — | — | Warehouse centroid longitude | `True` |
  | `capacity` | Integer | — | — | Total unit capacity | `True` |
  | `is_synthetic` | Boolean | — | — | Table synthetic flag | `True` |

### 9. `warehouse_inventory`
* **Source:** Grounded Synthetic Inventory State (§4.4 REQ-4)
* **Grain:** Warehouse $\times$ Product inventory stock record.
* **Columns:**
  | Column Name | Type | PK/FK | Global ID Format | Description | Is Synthetic |
  |---|---|---|---|---|---|
  | `inventory_id` | Integer | PK | — | Inventory primary key | `True` |
  | `global_id` | String | Unique | `inventory:ID` | Namespaced global ID (§4.1 REQ-3) | `True` |
  | `warehouse_id` | String | FK | — | Warehouse region identifier | `True` |
  | `product_id` | Integer | FK | — | FK to `products.product_id` | `True` |
  | `stock` | Integer | — | — | Current stock on hand | `True` |
  | `reorder_point` | Integer | — | — | Stock reorder trigger point | `True` |
  | `avg_daily_demand` | Float | — | — | Average daily demand calculated from volume | `True` |
  | `restock_lead_days` | Integer | — | — | Warehouse restock lead time | `True` |
  | `is_synthetic` | Boolean | — | — | Table synthetic flag | `True` |

### 10. `vehicles`
* **Source:** Synthetic Fleet Pool
* **Grain:** One row per fleet vehicle (`vehicle_id`).
* **Columns:**
  | Column Name | Type | PK/FK | Global ID Format | Description | Is Synthetic |
  |---|---|---|---|---|---|
  | `vehicle_id` | Integer | PK | — | Vehicle primary key | `True` |
  | `global_id` | String | Unique | `vehicle:ID` | Namespaced global ID (§4.1 REQ-3) | `True` |
  | `license_plate` | String | — | — | Vehicle registration license plate | `True` |
  | `vehicle_type` | String | — | — | Vehicle class (Semi-Trailer, Box Truck, Cargo Van) | `True` |
  | `capacity_kg` | Integer | — | — | Maximum load capacity (kg) | `True` |
  | `status` | String | — | — | Operational status | `True` |
  | `is_synthetic` | Boolean | — | — | Table synthetic flag | `True` |
