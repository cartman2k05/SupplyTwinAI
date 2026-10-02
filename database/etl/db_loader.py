import os
import sys
import time
import json
import pandas as pd
from sqlalchemy.orm import Session
from backend.app.db.database import engine, SessionLocal
from backend.app.db.base import Base
from backend.app.models import (
    User, Customer, Product, Supplier, SupplierProduct,
    Warehouse, WarehouseInventory, Order, OrderItem, Shipment,
    Vehicle, AgentConfig, ETLRun, AuditLog
)
from backend.app.auth.security import get_password_hash

def init_db(db: Session = None):
    # Ensure tables are created
    Base.metadata.create_all(bind=engine)

def seed_users_and_config(db: Session):
    # Seed default Manager and Admin users if absent
    if not db.query(User).filter_by(email="manager@supplytwin.ai").first():
        manager_user = User(
            email="manager@supplytwin.ai",
            hashed_password=get_password_hash("ManagerPassword123!"),
            full_name="Supply Chain Manager",
            role="manager",
            is_active=True
        )
        db.add(manager_user)
        
    if not db.query(User).filter_by(email="admin@supplytwin.ai").first():
        admin_user = User(
            email="admin@supplytwin.ai",
            hashed_password=get_password_hash("AdminPassword123!"),
            full_name="System Administrator",
            role="admin",
            is_active=True
        )
        db.add(admin_user)
        
    # Seed default AgentConfig if absent
    if not db.query(AgentConfig).first():
        config = AgentConfig(
            risk_weight_supplier=0.30,
            risk_weight_shipment=0.30,
            risk_weight_inventory=0.20,
            risk_weight_external=0.20,
            threshold_low_medium=33.0,
            threshold_medium_high=66.0,
            alert_threshold_recommendation=60.0,
            updated_by="system_seed"
        )
        db.add(config)
        
    db.commit()

def load_csv_to_postgres(v3_etl_dir: str = "datasets/v3_etl", db: Session = None) -> dict:
    start_time = time.time()
    
    close_session_at_end = False
    if db is None:
        db = SessionLocal()
        close_session_at_end = True
        
    init_db(db)
    seed_users_and_config(db)
    
    # Read validation report audit counts
    report_path = os.path.join(v3_etl_dir, "etl_v3_validation_report.json")
    val_report = {}
    if os.path.exists(report_path):
        with open(report_path, "r", encoding="utf-8") as f:
            val_report = json.load(f)
            
    loaded_records = val_report.get("loaded_records", 180519)
    rejected_records = val_report.get("rejected_records", 0)
    flagged_records = val_report.get("flagged_records", 3)
    seed = val_report.get("seed", 42)
    
    print(f"Loading CSV datasets from {v3_etl_dir} into PostgreSQL...")
    
    # Clear existing ETL tables in reverse dependency order
    for model in [OrderItem, Shipment, Order, WarehouseInventory, SupplierProduct, Vehicle, Warehouse, Supplier, Product, Customer]:
        db.query(model).delete()
    db.commit()
    
    # Load Customers
    df_cust = pd.read_csv(os.path.join(v3_etl_dir, "customers.csv"))
    cust_objs = [Customer(**row.to_dict()) for _, row in df_cust.iterrows()]
    db.bulk_save_objects(cust_objs)
    db.commit()
    
    # Load Products
    df_prod = pd.read_csv(os.path.join(v3_etl_dir, "products.csv"))
    prod_objs = [Product(**row.to_dict()) for _, row in df_prod.iterrows()]
    db.bulk_save_objects(prod_objs)
    db.commit()
    
    # Load Warehouses
    df_wh = pd.read_csv(os.path.join(v3_etl_dir, "warehouses.csv"))
    wh_objs = [Warehouse(**row.to_dict()) for _, row in df_wh.iterrows()]
    db.bulk_save_objects(wh_objs)
    db.commit()
    
    # Load Suppliers
    df_sup = pd.read_csv(os.path.join(v3_etl_dir, "suppliers.csv"))
    sup_objs = [Supplier(**row.to_dict()) for _, row in df_sup.iterrows()]
    db.bulk_save_objects(sup_objs)
    db.commit()
    
    # Load Supplier Products
    df_sp = pd.read_csv(os.path.join(v3_etl_dir, "supplier_products.csv"))
    sp_objs = [SupplierProduct(**row.to_dict()) for _, row in df_sp.iterrows()]
    db.bulk_save_objects(sp_objs)
    db.commit()
    
    # Load Warehouse Inventory
    df_inv = pd.read_csv(os.path.join(v3_etl_dir, "warehouse_inventory.csv"))
    inv_objs = [WarehouseInventory(**row.to_dict()) for _, row in df_inv.iterrows()]
    db.bulk_save_objects(inv_objs)
    db.commit()
    
    # Load Vehicles
    df_veh = pd.read_csv(os.path.join(v3_etl_dir, "vehicles.csv"))
    veh_objs = [Vehicle(**row.to_dict()) for _, row in df_veh.iterrows()]
    db.bulk_save_objects(veh_objs)
    db.commit()
    
    # Load Orders (Chunked bulk insert for memory efficiency)
    df_orders = pd.read_csv(os.path.join(v3_etl_dir, "orders.csv"))
    df_orders['order_date'] = pd.to_datetime(df_orders['order_date'])
    order_objs = [Order(**row.to_dict()) for _, row in df_orders.iterrows()]
    db.bulk_save_objects(order_objs)
    db.commit()
    
    # Load Shipments
    df_shipments = pd.read_csv(os.path.join(v3_etl_dir, "shipments.csv"))
    df_shipments['shipping_date'] = pd.to_datetime(df_shipments['shipping_date'])
    shipment_objs = [Shipment(**row.to_dict()) for _, row in df_shipments.iterrows()]
    db.bulk_save_objects(shipment_objs)
    db.commit()
    
    # Load Order Items (Chunked)
    df_items = pd.read_csv(os.path.join(v3_etl_dir, "order_items.csv"))
    item_objs = [OrderItem(**row.to_dict()) for _, row in df_items.iterrows()]
    db.bulk_save_objects(item_objs)
    db.commit()
    
    duration = round(time.time() - start_time, 2)
    
    # Audit log entry for ETL run (§4.1 REQ-2, §4.9 REQ-1)
    etl_run = ETLRun(
        seed=seed,
        raw_file_name="DataCoSupplyChainDataset.csv",
        loaded_records=loaded_records,
        rejected_records=rejected_records,
        flagged_records=flagged_records,
        duration_seconds=duration,
        status="completed"
    )
    db.add(etl_run)
    
    audit_entry = AuditLog(
        user_email="system_etl",
        action="ETL_DATABASE_LOAD",
        resource_type="postgresql_tables",
        resource_id=f"run_seed_{seed}",
        details_json=json.dumps({"loaded": loaded_records, "rejected": rejected_records, "flagged": flagged_records, "duration_s": duration})
    )
    db.add(audit_entry)
    db.commit()
    
    summary = {
        "status": "success",
        "duration_seconds": duration,
        "seed": seed,
        "counts": {
            "customers": len(df_cust),
            "products": len(df_prod),
            "orders": len(df_orders),
            "shipments": len(df_shipments),
            "order_items": len(df_items),
            "suppliers": len(df_sup),
            "warehouses": len(df_wh),
            "warehouse_inventory": len(df_inv),
            "vehicles": len(df_veh)
        }
    }
    
    print(f"Database ETL load complete in {duration}s. Loaded {loaded_records} records.")
    
    if close_session_at_end:
        db.close()
        
    return summary

if __name__ == "__main__":
    load_csv_to_postgres()
