import os
import sys
import json
import argparse
import hashlib
import yaml
import numpy as np
import pandas as pd

def load_config(config_path: str) -> dict:
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def compute_file_sha256(filepath: str) -> str:
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

def run_single_etl_seed(seed: int, config: dict, output_dir: str) -> dict:
    print(f"\n--- Running ETL v3 with Seed: {seed} ---")
    rng = np.random.default_rng(seed)
    
    raw_path = config.get("raw_dataset_path", "datasets/raw/DataCoSupplyChainDataset_archive/DataCoSupplyChainDataset.csv")
    if not os.path.exists(raw_path):
        raise FileNotFoundError(f"Raw DataCo dataset not found at {raw_path}")
        
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Load Raw Dataset and Initialize Audit Counters (§4.1 REQ-2)
    df_raw = pd.read_csv(raw_path, encoding='ISO-8859-1')
    raw_total_rows = len(df_raw)
    
    loaded_records = 0
    rejected_records = 0
    flagged_records = 0
    rejection_log = []
    flag_log = []
    
    # Validation check: Filter out invalid dates or corrupted rows
    valid_rows = []
    for idx, row in df_raw.iterrows():
        # Check required fields
        if pd.isna(row.get('Order Id')) or pd.isna(row.get('Order Item Id')):
            rejected_records += 1
            rejection_log.append(f"Row {idx}: Missing Order Id or Order Item Id")
            continue
            
        # Check item quantity and price
        qty = row.get('Order Item Quantity', 0)
        price = row.get('Order Item Product Price', 0.0)
        if qty < config['validation']['min_item_quantity'] or price < config['validation']['min_item_price']:
            rejected_records += 1
            rejection_log.append(f"Row {idx}: Invalid quantity ({qty}) or price ({price})")
            continue
            
        # Check customer zipcode missing (flagged for median fill)
        if pd.isna(row.get('Customer Zipcode')):
            flagged_records += 1
            flag_log.append(f"Row {idx}: Missing Customer Zipcode filled with median")
            
        valid_rows.append(row)
        loaded_records += 1
        
    df_clean = pd.DataFrame(valid_rows)
    print(f"Validation summary: Loaded={loaded_records}, Rejected={rejected_records}, Flagged={flagged_records}")
    
    # Parse datetime fields
    df_clean['order_date'] = pd.to_datetime(df_clean['order date (DateOrders)'])
    df_clean['shipping_date'] = pd.to_datetime(df_clean['shipping date (DateOrders)'])
    df_clean['delivery_delay_days'] = (df_clean['shipping_date'] - df_clean['order_date']).dt.days - df_clean['Days for shipment (scheduled)']
    df_clean['order_month'] = df_clean['order_date'].dt.month
    df_clean['order_weekday'] = df_clean['order_date'].dt.weekday
    df_clean['order_is_weekend'] = df_clean['order_weekday'].isin([5, 6]).astype(int)
    
    # Country translation mapping
    country_map = config.get('country_translation', {})
    df_clean['Order Country Clean'] = df_clean['Order Country'].map(lambda c: country_map.get(str(c).strip(), str(c).strip()))
    
    # 2. Build Customers Table (§4.1 REQ-3, REQ-4)
    df_cust = df_clean[[
        'Customer Id', 'Customer Fname', 'Customer Lname', 'Customer Country',
        'Customer City', 'Customer State', 'Customer Segment', 'Customer Zipcode'
    ]].drop_duplicates(subset=['Customer Id']).copy()
    
    df_cust['Customer Lname'] = df_cust['Customer Lname'].fillna('Unknown')
    median_zip = df_cust['Customer Zipcode'].median()
    df_cust['Customer Zipcode'] = df_cust['Customer Zipcode'].fillna(median_zip)
    
    df_cust.rename(columns={
        'Customer Id': 'customer_id',
        'Customer Fname': 'first_name',
        'Customer Lname': 'last_name',
        'Customer Country': 'country',
        'Customer City': 'city',
        'Customer State': 'state',
        'Customer Segment': 'segment',
        'Customer Zipcode': 'zipcode'
    }, inplace=True)
    
    df_cust['global_id'] = df_cust['customer_id'].apply(lambda x: f"customer:{int(x)}")
    df_cust.to_csv(os.path.join(output_dir, 'customers.csv'), index=False)
    
    # 3. Build Products Table (§4.1 REQ-3)
    df_prod = df_clean[[
        'Product Card Id', 'Product Name', 'Category Id', 'Category Name',
        'Product Price'
    ]].drop_duplicates(subset=['Product Card Id']).copy()
    
    df_prod.rename(columns={
        'Product Card Id': 'product_id',
        'Product Name': 'name',
        'Category Id': 'category_id',
        'Category Name': 'category',
        'Product Price': 'price'
    }, inplace=True)
    
    df_prod['global_id'] = df_prod['product_id'].apply(lambda x: f"product:{int(x)}")
    df_prod.to_csv(os.path.join(output_dir, 'products.csv'), index=False)
    
    # 4. Build Warehouses Table (§4.4 REQ-4)
    unique_regions = sorted(df_clean['Order Region'].unique())
    warehouses_list = []
    warehouse_coords = config.get('warehouse_region_coords', {})
    
    for w_idx, region in enumerate(unique_regions, start=1):
        coords = warehouse_coords.get(region, [0.0, 0.0])
        warehouses_list.append({
            'warehouse_id': w_idx,
            'global_id': f"warehouse:{w_idx}",
            'name': f"Warehouse {region}",
            'region': region,
            'latitude': coords[0],
            'longitude': coords[1],
            'capacity': 100000,
            'is_synthetic': True
        })
    df_warehouses = pd.DataFrame(warehouses_list)
    df_warehouses.to_csv(os.path.join(output_dir, 'warehouses.csv'), index=False)
    
    region_to_wid = {r['region']: r['warehouse_id'] for r in warehouses_list}
    
    # 5. Build Orders & Shipments Tables (§4.1 REQ-3, REQ-4, REQ-5)
    df_orders_base = df_clean[[
        'Order Id', 'Customer Id', 'order_date', 'Order Status', 'Market',
        'Order Region', 'Order Country Clean', 'Order City', 'Order State',
        'Latitude', 'Longitude'
    ]].drop_duplicates(subset=['Order Id']).copy()
    
    df_orders_base.rename(columns={
        'Order Id': 'order_id',
        'Customer Id': 'customer_id',
        'Order Status': 'order_status',
        'Market': 'market',
        'Order Region': 'order_region',
        'Order Country Clean': 'destination_country',
        'Order City': 'destination_city',
        'Order State': 'destination_state',
        'Latitude': 'customer_latitude',
        'Longitude': 'customer_longitude'
    }, inplace=True)
    
    df_orders_base['global_id'] = df_orders_base['order_id'].apply(lambda x: f"order:{int(x)}")
    df_orders_base['customer_global_id'] = df_orders_base['customer_id'].apply(lambda x: f"customer:{int(x)}")
    df_orders_base['assigned_warehouse_id'] = df_orders_base['order_region'].map(region_to_wid)
    df_orders_base['assigned_warehouse_id_is_synthetic'] = True
    df_orders_base['is_simulated'] = False
    
    df_orders_base.to_csv(os.path.join(output_dir, 'orders.csv'), index=False)
    
    # Build Shipments (1:1 with Orders)
    df_shipments_base = df_clean[[
        'Order Id', 'Shipping Mode', 'Days for shipment (scheduled)',
        'Days for shipping (real)', 'Delivery Status', 'shipping_date'
    ]].drop_duplicates(subset=['Order Id']).copy()
    
    df_shipments_base.rename(columns={
        'Order Id': 'shipment_id',
        'Shipping Mode': 'shipping_mode',
        'Days for shipment (scheduled)': 'days_scheduled',
        'Days for shipping (real)': 'days_real',
        'Delivery Status': 'delivery_status',
        'shipping_date': 'shipping_date'
    }, inplace=True)
    
    df_shipments_base['order_id'] = df_shipments_base['shipment_id']
    df_shipments_base['global_id'] = df_shipments_base['shipment_id'].apply(lambda x: f"shipment:{int(x)}")
    df_shipments_base['order_global_id'] = df_shipments_base['global_id']
    df_shipments_base['is_simulated'] = False
    df_shipments_base.to_csv(os.path.join(output_dir, 'shipments.csv'), index=False)
    
    # 6. Build Order Items Table (§4.1 REQ-3, REQ-5)
    df_items = df_clean[[
        'Order Item Id', 'Order Id', 'Product Card Id', 'Order Item Quantity',
        'Order Item Product Price', 'Order Item Discount', 'Order Item Total',
        'Order Item Profit Ratio', 'Sales per customer', 'Benefit per order'
    ]].copy()
    
    df_items.rename(columns={
        'Order Item Id': 'item_id',
        'Order Id': 'order_id',
        'Product Card Id': 'product_id',
        'Order Item Quantity': 'quantity',
        'Order Item Product Price': 'unit_price',
        'Order Item Discount': 'discount',
        'Order Item Total': 'total',
        'Order Item Profit Ratio': 'profit_ratio',
        'Sales per customer': 'sales_per_customer',
        'Benefit per order': 'benefit_per_order'
    }, inplace=True)
    
    df_items['global_id'] = df_items['item_id'].apply(lambda x: f"item:{int(x)}")
    df_items['order_global_id'] = df_items['order_id'].apply(lambda x: f"order:{int(x)}")
    df_items['product_global_id'] = df_items['product_id'].apply(lambda x: f"product:{int(x)}")
    df_items['is_simulated'] = False
    df_items.to_csv(os.path.join(output_dir, 'order_items.csv'), index=False)
    
    # 7. Build Suppliers & Supplier Products (§4.4 REQ-2, DECISIONS §3.2)
    categories = sorted(df_clean['Category Id'].unique())
    cat_to_name = df_clean.set_index('Category Id')['Category Name'].to_dict()
    
    # Measure historical late delivery rate per category as ground-truth proxy
    cat_late_rates = df_clean.groupby('Category Id')['Late_delivery_risk'].mean().to_dict()
    
    suppliers_list = []
    supplier_products_list = []
    
    sup_counter = 1
    
    # Generate 1 Primary Supplier + 2 Alternate Suppliers per Category (150 total)
    for cat_id in categories:
        cat_name = cat_to_name[cat_id]
        base_late_rate = cat_late_rates.get(cat_id, 0.55)
        primary_ontime = float(np.clip(1.0 - base_late_rate, 0.35, 0.98))
        
        # Primary Supplier
        p_sup_id = sup_counter
        sup_counter += 1
        suppliers_list.append({
            'supplier_id': p_sup_id,
            'global_id': f"supplier:{p_sup_id}",
            'name': f"Primary Supplier - {cat_name}",
            'category_id': cat_id,
            'category': cat_name,
            'country': 'United States',
            'is_primary': True,
            'on_time_rate': round(primary_ontime, 4),
            'defect_rate': round(float(rng.beta(2, 50)), 4),
            'lead_time_days': int(rng.integers(3, 8)),
            'rating': round(float(rng.uniform(4.0, 4.9)), 2),
            'is_synthetic': True
        })
        
        # Link Primary Supplier to ALL category products
        cat_product_ids = df_prod[df_prod['category_id'] == cat_id]['product_id'].tolist()
        for pid in cat_product_ids:
            supplier_products_list.append({
                'supplier_id': p_sup_id,
                'product_id': pid,
                'is_primary': True,
                'unit_cost_multiplier': 1.0,
                'lead_time_days': int(rng.integers(3, 8)),
                'on_time_rate': round(primary_ontime, 4),
                'defect_rate': round(float(rng.beta(2, 50)), 4),
                'is_synthetic': True
            })
            
        # 2 Alternate Suppliers per Category
        for alt_idx in [1, 2]:
            a_sup_id = sup_counter
            sup_counter += 1
            
            # Perturb metrics with trade-offs (e.g. higher cost, variable on-time)
            alt_ontime = float(np.clip(primary_ontime + rng.normal(0.0, 0.08), 0.30, 0.96))
            alt_defect = float(np.clip(rng.beta(2.5, 45.0), 0.005, 0.14))
            alt_lead = int(rng.integers(2, 14))
            
            suppliers_list.append({
                'supplier_id': a_sup_id,
                'global_id': f"supplier:{a_sup_id}",
                'name': f"Alt Supplier {alt_idx} - {cat_name}",
                'category_id': cat_id,
                'category': cat_name,
                'country': rng.choice(['Germany', 'China', 'Japan', 'Mexico', 'India', 'United Kingdom']),
                'is_primary': False,
                'on_time_rate': round(alt_ontime, 4),
                'defect_rate': round(alt_defect, 4),
                'lead_time_days': alt_lead,
                'rating': round(float(rng.uniform(3.2, 4.6)), 2),
                'is_synthetic': True
            })
            
            # Alternate suppliers have PARTIAL coverage (~80% of category products)
            coverage_count = max(1, int(len(cat_product_ids) * config['supplier_synthesis']['alternate_coverage_ratio']))
            supplied_pids = rng.choice(cat_product_ids, size=coverage_count, replace=False)
            
            niche_pids = config['supplier_synthesis'].get('niche_product_ids', [])
            
            for pid in supplied_pids:
                is_niche = pid in niche_pids
                # Niche products have poor trade-off metrics across alternates
                cost_mult = round(float(rng.uniform(1.4, 1.8) if is_niche else rng.uniform(1.05, 1.25)), 2)
                item_lead = int(rng.integers(12, 21) if is_niche else alt_lead)
                item_ontime = round(float(rng.uniform(0.30, 0.45) if is_niche else alt_ontime), 4)
                
                supplier_products_list.append({
                    'supplier_id': a_sup_id,
                    'product_id': pid,
                    'is_primary': False,
                    'unit_cost_multiplier': cost_mult,
                    'lead_time_days': item_lead,
                    'on_time_rate': item_ontime,
                    'defect_rate': round(alt_defect, 4),
                    'is_synthetic': True
                })

    df_suppliers = pd.DataFrame(suppliers_list)
    df_suppliers.to_csv(os.path.join(output_dir, 'suppliers.csv'), index=False)
    
    df_sup_prod = pd.DataFrame(supplier_products_list)
    df_sup_prod.to_csv(os.path.join(output_dir, 'supplier_products.csv'), index=False)
    
    # 8. Build Warehouse Inventory Table (§4.4 REQ-4, DECISIONS §3.3)
    # Calculate historical regional demand per product
    df_merged_demand = df_clean.groupby(['Order Region', 'Product Card Id'])['Order Item Quantity'].sum().reset_index()
    demand_lookup = {(row['Order Region'], row['Product Card Id']): row['Order Item Quantity'] for _, row in df_merged_demand.iterrows()}
    
    inventory_list = []
    inv_counter = 1
    
    all_product_ids = df_prod['product_id'].tolist()
    
    for wid, region in region_to_wid.items():
        for pid in all_product_ids:
            hist_qty = demand_lookup.get((wid, pid), 0)
            avg_daily_demand = round(max(0.5, hist_qty / 1095.0), 2)  # ~3 years history
            reorder_point = int(np.ceil(avg_daily_demand * rng.uniform(7, 14)))
            current_stock = int(reorder_point * rng.uniform(0.5, 2.5))
            
            inventory_list.append({
                'inventory_id': inv_counter,
                'global_id': f"inventory:{inv_counter}",
                'warehouse_id': region,
                'product_id': pid,
                'stock': current_stock,
                'reorder_point': reorder_point,
                'avg_daily_demand': avg_daily_demand,
                'restock_lead_days': int(rng.integers(3, 10)),
                'is_synthetic': True
            })
            inv_counter += 1
            
    df_inventory = pd.DataFrame(inventory_list)
    df_inventory.to_csv(os.path.join(output_dir, 'warehouse_inventory.csv'), index=False)
    
    # 9. Build Synthetic Vehicles Fleet Pool
    vehicles_list = []
    for v_id in range(1, 31):
        vehicles_list.append({
            'vehicle_id': v_id,
            'global_id': f"vehicle:{v_id}",
            'license_plate': f"TRK-{v_id:03d}",
            'vehicle_type': rng.choice(['Semi-Trailer', 'Box Truck', 'Cargo Van']),
            'capacity_kg': rng.choice([5000, 12000, 24000]),
            'status': 'available',
            'is_synthetic': True
        })
    df_vehicles = pd.DataFrame(vehicles_list)
    df_vehicles.to_csv(os.path.join(output_dir, 'vehicles.csv'), index=False)
    
    # 10. Build Graph Relationships Table
    rel_list = []
    
    # Order PLACED_BY Customer
    for _, r in df_orders_base.iterrows():
        rel_list.append({'source_global_id': r['global_id'], 'relation': 'PLACED', 'target_global_id': r['customer_global_id']})
        rel_list.append({'source_global_id': r['global_id'], 'relation': 'FULFILLED_FROM', 'target_global_id': f"warehouse:{r['assigned_warehouse_id']}"})
        
    # Order CONTAINS Product
    for _, r in df_items.iterrows():
        rel_list.append({'source_global_id': r['order_global_id'], 'relation': 'CONTAINS', 'target_global_id': r['product_global_id']})
        
    # Supplier SUPPLIES Product
    for _, r in df_sup_prod.iterrows():
        rel_list.append({'source_global_id': f"supplier:{r['supplier_id']}", 'relation': 'SUPPLIES', 'target_global_id': f"product:{r['product_id']}"})
        
    # Product STOCKED_AT Warehouse
    for _, r in df_inventory.iterrows():
        rel_list.append({'source_global_id': f"product:{r['product_id']}", 'relation': 'STOCKED_AT', 'target_global_id': f"warehouse:{r['warehouse_id']}"})
        
    df_relationships = pd.DataFrame(rel_list).drop_duplicates()
    df_relationships.to_csv(os.path.join(output_dir, 'relationships.csv'), index=False)
    
    # 11. Build Geocoding Lookup JSON (§4.4 REQ-5)
    default_countries = config.get('default_country_centroids', {})
    region_coords = config.get('warehouse_region_coords', {})
    
    # Ensure 100% of destination countries in the dataset have valid centroid entries
    all_dest_countries = df_orders_base['destination_country'].dropna().unique()
    final_country_centroids = dict(default_countries)
    
    for c_name in all_dest_countries:
        if c_name not in final_country_centroids:
            # Fallback to general regional coordinates or default
            final_country_centroids[c_name] = [20.0, 0.0]
            
    geo_lookup = {
        'countries': final_country_centroids,
        'warehouses': region_coords,
        'translations': country_map
    }
    with open(os.path.join(output_dir, 'geo_lookup.json'), 'w', encoding='utf-8') as f:
        json.dump(geo_lookup, f, indent=2)
        
    # 12. Generate Validation Report (§4.1 REQ-2, §4.9 REQ-1)
    report = {
        'seed': seed,
        'raw_rows': raw_total_rows,
        'loaded_records': loaded_records,
        'rejected_records': rejected_records,
        'flagged_records': flagged_records,
        'rejection_samples': rejection_log[:10],
        'flag_samples': flag_log[:10],
        'counts': {
            'customers': len(df_cust),
            'products': len(df_prod),
            'orders': len(df_orders_base),
            'shipments': len(df_shipments_base),
            'order_items': len(df_items),
            'suppliers': len(df_suppliers),
            'supplier_products': len(df_sup_prod),
            'warehouses': len(df_warehouses),
            'warehouse_inventory': len(df_inventory),
            'vehicles': len(df_vehicles),
            'relationships': len(df_relationships)
        },
        'file_hashes': {
            fname: compute_file_sha256(os.path.join(output_dir, fname))
            for fname in [
                'customers.csv', 'products.csv', 'orders.csv', 'shipments.csv',
                'order_items.csv', 'suppliers.csv', 'supplier_products.csv',
                'warehouses.csv', 'warehouse_inventory.csv', 'vehicles.csv',
                'relationships.csv'
            ]
        }
    }
    
    with open(os.path.join(output_dir, 'etl_v3_validation_report.json'), 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
        
    print(f"ETL v3 seed {seed} completed successfully. Report written to {output_dir}/etl_v3_validation_report.json")
    return report

def main():
    parser = argparse.ArgumentParser(description="SupplyTwinAI ETL v3 Execution Pipeline")
    parser.add_argument("--config", default="database/etl/etl_config.yaml", help="Path to ETL config YAML")
    parser.add_argument("--seeds", nargs="+", type=int, default=[42, 43, 44], help="List of seeds to execute for determinism testing")
    args = parser.parse_args()
    
    config = load_config(args.config)
    
    seed_reports = {}
    for seed in args.seeds:
        out_dir = f"datasets/v3_etl/seed_{seed}" if len(args.seeds) > 1 else config.get("output_directory", "datasets/v3_etl")
        report = run_single_etl_seed(seed, config, out_dir)
        seed_reports[seed] = report
        
    # Also write primary output to datasets/v3_etl/ if multi-seed
    if len(args.seeds) > 1:
        run_single_etl_seed(args.seeds[0], config, "datasets/v3_etl")
        
    print("\n==========================================")
    print("All requested seeds completed successfully.")
    print("==========================================")

if __name__ == "__main__":
    main()
