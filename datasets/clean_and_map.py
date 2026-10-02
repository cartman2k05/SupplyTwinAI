"""
SupplyTwinAI — Data Cleaning & Schema Mapping Script
=====================================================

INPUT:
    DataCoSupplyChainDataset.csv
    (Download from: https://www.kaggle.com/datasets/shashwatwork/dataco-smart-supply-chain-for-big-data-analysis)
    Place it in the same folder as this script.

OUTPUT (written to ./cleaned_data/):
    - raw_profile_report.html   -> full data quality report (nulls, correlations, distributions)
    - customers.csv             -> maps to your Customers table
    - products.csv              -> maps to your Products table
    - orders.csv                -> maps to your Orders table
    - shipments.csv             -> maps to your Shipments table
    - suppliers.csv             -> synthesized (DataCo has no supplier table)
    - warehouses.csv            -> synthesized (DataCo has no warehouse table)
    - vehicles.csv              -> synthesized (DataCo has no vehicle table)
    - relationships.csv         -> edge list for Neo4j Knowledge Graph import
    - cleaning_log.md           -> what was cleaned/dropped/imputed and why

WHY SYNTHETIC SUPPLIERS/WAREHOUSES/VEHICLES:
    DataCo is an order/shipping/customer dataset — it does not include a native
    supplier, warehouse, or vehicle table. To keep your CRUD system and Knowledge
    Graph fully populated for the demo, this script generates realistic synthetic
    entities derived from existing categories/regions in the real data. Document
    this clearly in your report as an assumption.

USAGE:
    pip install pandas numpy ydata-profiling
    python clean_and_map.py
"""

import os
from datetime import datetime

import numpy as np
import pandas as pd

RAW_PATH = "DataCoSupplyChainDataset.csv"
OUT_DIR = "cleaned_data"
os.makedirs(OUT_DIR, exist_ok=True)

log_lines = []


def log(msg):
    print(msg)
    log_lines.append(msg)


# ---------------------------------------------------------------------------
# 1. LOAD
# ---------------------------------------------------------------------------
log("Loading raw dataset...")
# DataCo's CSV is encoded in latin-1, not utf-8 — this trips up almost everyone.
df = pd.read_csv(RAW_PATH, encoding="latin-1")
log(f"Raw shape: {df.shape[0]} rows, {df.shape[1]} columns")

# ---------------------------------------------------------------------------
# 2. AUTOMATED PROFILING REPORT (optional but recommended)
# ---------------------------------------------------------------------------
try:
    from ydata_profiling import ProfileReport

    profile = ProfileReport(df, title="DataCo Raw Data Profiling", minimal=True)
    profile.to_file(os.path.join(OUT_DIR, "raw_profile_report.html"))
    log("Saved raw_profile_report.html — open it in a browser to inspect data quality.")
except ImportError:
    log("ydata-profiling not installed — skipped report. Run: pip install ydata-profiling")

# ---------------------------------------------------------------------------
# 3. STANDARDIZE COLUMN NAMES
# ---------------------------------------------------------------------------
df.columns = [
    c.strip().replace(" ", "_").replace("(", "").replace(")", "") for c in df.columns
]

# ---------------------------------------------------------------------------
# 4. BASIC CLEANING
# ---------------------------------------------------------------------------
before = len(df)
df = df.drop_duplicates()
log(f"Removed {before - len(df)} duplicate rows.")

null_ratio = df.isnull().mean()
drop_cols = null_ratio[null_ratio > 0.6].index.tolist()
if drop_cols:
    df = df.drop(columns=drop_cols)
    log(f"Dropped columns with >60% missing values: {drop_cols}")

# Parse date columns
for col in ["order_date_DateOrders", "shipping_date_DateOrders"]:
    if col in df.columns:
        df[col] = pd.to_datetime(df[col], errors="coerce")
        log(f"Parsed '{col}' as datetime.")

# Fix impossible negative values in numeric columns that must be >= 0
non_negative_cols = [
    "Days_for_shipping_real",
    "Days_for_shipment_scheduled",
    "Order_Item_Quantity",
    "Sales",
    "Order_Item_Product_Price",
]
for col in non_negative_cols:
    if col in df.columns:
        bad = (df[col] < 0).sum()
        if bad:
            df.loc[df[col] < 0, col] = np.nan
            log(f"Flagged {bad} negative values in '{col}' as missing.")

# Impute numeric nulls with median (robust to outliers)
for col in df.select_dtypes(include=[np.number]).columns:
    n_missing = df[col].isnull().sum()
    if n_missing > 0:
        median_val = df[col].median()
        df[col] = df[col].fillna(median_val)
        log(f"Filled {n_missing} missing values in '{col}' with median ({median_val}).")

# Impute categorical nulls
for col in df.select_dtypes(include=["object"]).columns:
    n_missing = df[col].isnull().sum()
    if n_missing > 0:
        df[col] = df[col].fillna("Unknown")
        log(f"Filled {n_missing} missing values in '{col}' with 'Unknown'.")

# Standardize inconsistent text casing (e.g. "usa" vs "USA" vs "Usa")
text_cols = [
    "Customer_Country", "Customer_City", "Order_Country", "Order_Region",
    "Market", "Shipping_Mode", "Category_Name", "Department_Name",
]
for col in text_cols:
    if col in df.columns:
        df[col] = df[col].astype(str).str.strip().str.title()

log(f"Cleaned shape: {df.shape[0]} rows, {df.shape[1]} columns")

# ---------------------------------------------------------------------------
# 5. FEATURE ENGINEERING
# ---------------------------------------------------------------------------
if "Days_for_shipping_real" in df.columns and "Days_for_shipment_scheduled" in df.columns:
    df["delivery_delay_days"] = df["Days_for_shipping_real"] - df["Days_for_shipment_scheduled"]
    log("Engineered feature: delivery_delay_days")

if "order_date_DateOrders" in df.columns:
    df["order_month"] = df["order_date_DateOrders"].dt.month
    df["order_weekday"] = df["order_date_DateOrders"].dt.day_name()
    df["order_is_weekend"] = df["order_date_DateOrders"].dt.weekday >= 5
    log("Engineered features: order_month, order_weekday, order_is_weekend")

# ---------------------------------------------------------------------------
# 6. MAP CLEANED DATA TO YOUR PROJECT'S DATABASE SCHEMA
# ---------------------------------------------------------------------------

# --- Customers ---
customer_cols = [c for c in [
    "Customer_Id", "Customer_Fname", "Customer_Lname", "Customer_City",
    "Customer_State", "Customer_Country", "Customer_Segment",
] if c in df.columns]
customers = df[customer_cols].drop_duplicates(subset=["Customer_Id"]) if "Customer_Id" in customer_cols else pd.DataFrame()
customers.to_csv(os.path.join(OUT_DIR, "customers.csv"), index=False)

# --- Products ---
product_cols = [c for c in [
    "Product_Card_Id", "Product_Name", "Category_Id", "Category_Name",
    "Department_Id", "Department_Name", "Product_Price",
] if c in df.columns]
products = df[product_cols].drop_duplicates(subset=["Product_Card_Id"]) if "Product_Card_Id" in product_cols else pd.DataFrame()
products = products.rename(columns={
    "Product_Card_Id": "product_id",
    "Product_Name": "name",
    "Category_Name": "category",
    "Product_Price": "price",
})
products.to_csv(os.path.join(OUT_DIR, "products.csv"), index=False)

# --- Orders ---
order_cols = [c for c in [
    "Order_Id", "order_date_DateOrders", "Customer_Id", "Order_Region",
    "Order_Country", "Market", "Sales", "Order_Item_Quantity",
    "order_month", "order_weekday", "order_is_weekend",
] if c in df.columns]
orders = df[order_cols].drop_duplicates(subset=["Order_Id"]) if "Order_Id" in order_cols else pd.DataFrame()
orders = orders.rename(columns={"Order_Id": "order_id", "order_date_DateOrders": "order_date"})
orders.to_csv(os.path.join(OUT_DIR, "orders.csv"), index=False)

# --- Shipments ---
shipment_cols = [c for c in [
    "Order_Id", "shipping_date_DateOrders", "Shipping_Mode", "Delivery_Status",
    "Late_delivery_risk", "Days_for_shipping_real", "Days_for_shipment_scheduled",
    "delivery_delay_days",
] if c in df.columns]
shipments = df[shipment_cols].drop_duplicates(subset=["Order_Id"]) if "Order_Id" in shipment_cols else pd.DataFrame()
shipments = shipments.rename(columns={"Order_Id": "shipment_id", "shipping_date_DateOrders": "ship_date"})
shipments.to_csv(os.path.join(OUT_DIR, "shipments.csv"), index=False)

log("Exported customers.csv, products.csv, orders.csv, shipments.csv")

# ---------------------------------------------------------------------------
# 7. SYNTHESIZE MISSING ENTITIES: Suppliers, Warehouses, Vehicles
# ---------------------------------------------------------------------------
np.random.seed(42)

regions = orders["Order_Region"].dropna().unique() if "Order_Region" in orders.columns else np.array(["Region_A", "Region_B"])
categories = products["category"].dropna().unique() if "category" in products.columns else np.array(["Category_A"])

warehouses = pd.DataFrame({
    "warehouse_id": range(1, len(regions) + 1),
    "city": regions,
    "capacity": np.random.randint(5000, 20000, size=len(regions)),
    "current_stock": np.random.randint(500, 5000, size=len(regions)),
})
warehouses.to_csv(os.path.join(OUT_DIR, "warehouses.csv"), index=False)

suppliers = pd.DataFrame({
    "supplier_id": range(1, len(categories) + 1),
    "name": [f"Supplier_{c}" for c in categories],
    "country": np.random.choice(["USA", "China", "India", "Germany", "Brazil"], size=len(categories)),
    "rating": np.round(np.random.uniform(2.5, 5.0, size=len(categories)), 2),
    "lead_time": np.random.randint(2, 20, size=len(categories)),
    "risk_score": np.round(np.random.uniform(0, 1, size=len(categories)), 2),
})
suppliers.to_csv(os.path.join(OUT_DIR, "suppliers.csv"), index=False)

vehicles = pd.DataFrame({
    "vehicle_id": range(1, 21),
    "type": np.random.choice(["Truck", "Van", "Rail", "Air"], size=20),
    "status": np.random.choice(["Available", "In Transit", "Maintenance"], size=20),
})
vehicles.to_csv(os.path.join(OUT_DIR, "vehicles.csv"), index=False)

log("Synthesized suppliers.csv, warehouses.csv, vehicles.csv (not present in raw DataCo data)")

# ---------------------------------------------------------------------------
# 8. BUILD RELATIONSHIP EDGE LIST FOR NEO4J
# ---------------------------------------------------------------------------
rel_rows = []

cat_to_supplier = dict(zip(categories, suppliers["supplier_id"]))
for _, row in products.iterrows():
    sup_id = cat_to_supplier.get(row.get("category"))
    if sup_id and pd.notna(row.get("product_id")):
        rel_rows.append({
            "from_type": "Supplier", "from_id": sup_id,
            "rel": "SUPPLIES",
            "to_type": "Product", "to_id": row["product_id"],
        })

region_to_wh = dict(zip(regions, warehouses["warehouse_id"]))
for _, row in orders.iterrows():
    wh_id = region_to_wh.get(row.get("Order_Region"))
    if wh_id and pd.notna(row.get("order_id")):
        rel_rows.append({
            "from_type": "Order", "from_id": row["order_id"],
            "rel": "FULFILLED_FROM",
            "to_type": "Warehouse", "to_id": wh_id,
        })

relationships = pd.DataFrame(rel_rows).drop_duplicates()
relationships.to_csv(os.path.join(OUT_DIR, "relationships.csv"), index=False)
log(f"Exported relationships.csv with {len(relationships)} edges for Neo4j import")

# ---------------------------------------------------------------------------
# 9. SAVE CLEANING LOG (also useful for your project report)
# ---------------------------------------------------------------------------
with open(os.path.join(OUT_DIR, "cleaning_log.md"), "w") as f:
    f.write(f"# Data Cleaning Log — {datetime.now().isoformat()}\n\n")
    for line in log_lines:
        f.write(f"- {line}\n")

log("\nDone. All cleaned + mapped files are in the 'cleaned_data' folder.")
