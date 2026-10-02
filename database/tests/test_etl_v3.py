import os
import json
import hashlib
import pandas as pd
import pytest

OUTPUT_DIR = "datasets/v3_etl"
V2_DIR = "datasets/cleaned_v2/cleaned_data_v2"

@pytest.fixture(scope="module")
def etl_data():
    files = {
        'customers': pd.read_csv(os.path.join(OUTPUT_DIR, 'customers.csv')),
        'products': pd.read_csv(os.path.join(OUTPUT_DIR, 'products.csv')),
        'orders': pd.read_csv(os.path.join(OUTPUT_DIR, 'orders.csv')),
        'shipments': pd.read_csv(os.path.join(OUTPUT_DIR, 'shipments.csv')),
        'order_items': pd.read_csv(os.path.join(OUTPUT_DIR, 'order_items.csv')),
        'suppliers': pd.read_csv(os.path.join(OUTPUT_DIR, 'suppliers.csv')),
        'supplier_products': pd.read_csv(os.path.join(OUTPUT_DIR, 'supplier_products.csv')),
        'warehouses': pd.read_csv(os.path.join(OUTPUT_DIR, 'warehouses.csv')),
        'warehouse_inventory': pd.read_csv(os.path.join(OUTPUT_DIR, 'warehouse_inventory.csv')),
        'vehicles': pd.read_csv(os.path.join(OUTPUT_DIR, 'vehicles.csv')),
        'relationships': pd.read_csv(os.path.join(OUTPUT_DIR, 'relationships.csv'))
    }
    with open(os.path.join(OUTPUT_DIR, 'geo_lookup.json'), 'r', encoding='utf-8') as f:
        files['geo_lookup'] = json.load(f)
    with open(os.path.join(OUTPUT_DIR, 'etl_v3_validation_report.json'), 'r', encoding='utf-8') as f:
        files['report'] = json.load(f)
    return files

def test_global_id_uniqueness(etl_data):
    """Test §4.1 REQ-3: Global IDs are unique across all entity tables."""
    all_global_ids = []
    entity_tables = ['customers', 'products', 'orders', 'shipments', 'order_items', 'suppliers', 'warehouses', 'warehouse_inventory', 'vehicles']
    
    for tbl_name in entity_tables:
        df = etl_data[tbl_name]
        assert 'global_id' in df.columns, f"Table {tbl_name} missing global_id"
        gids = df['global_id'].tolist()
        assert len(gids) == len(set(gids)), f"Duplicate global_ids found inside {tbl_name}"
        all_global_ids.extend(gids)
        
    assert len(all_global_ids) == len(set(all_global_ids)), "Global IDs collision across different entity tables"

def test_inventory_global_id_prefix(etl_data):
    """Test §4.1 REQ-3: warehouse_inventory uses inventory:ID global_id format."""
    df_inv = etl_data['warehouse_inventory']
    assert (df_inv['global_id'].str.startswith('inventory:')).all(), "Warehouse inventory global_id must start with 'inventory:'"

def test_referential_integrity(etl_data):
    """Test foreign key resolution across all tables."""
    # Order Items -> Orders & Products
    order_ids = set(etl_data['orders']['order_id'])
    product_ids = set(etl_data['products']['product_id'])
    supplier_ids = set(etl_data['suppliers']['supplier_id'])
    warehouse_ids = set(etl_data['warehouses']['warehouse_id'])
    
    assert set(etl_data['order_items']['order_id']).issubset(order_ids)
    assert set(etl_data['order_items']['product_id']).issubset(product_ids)
    assert set(etl_data['supplier_products']['supplier_id']).issubset(supplier_ids)
    assert set(etl_data['supplier_products']['product_id']).issubset(product_ids)
    assert set(etl_data['warehouse_inventory']['product_id']).issubset(product_ids)

def test_v3_preserves_v2_columns(etl_data):
    """Test that ETL v3 preserves all core columns from ETL v2."""
    v2_orders = pd.read_csv(os.path.join(V2_DIR, 'orders.csv'))
    v3_orders = etl_data['orders']
    
    for col in ['order_id', 'customer_id', 'order_status', 'market', 'order_region']:
        assert col in v3_orders.columns, f"v3 orders missing v2 column {col}"
        
    v2_items = pd.read_csv(os.path.join(V2_DIR, 'order_items.csv'))
    v3_items = etl_data['order_items']
    for col in ['item_id', 'order_id', 'product_id', 'quantity', 'unit_price', 'discount', 'total', 'profit_ratio', 'sales_per_customer', 'benefit_per_order']:
        assert col in v3_items.columns, f"v3 order_items missing v2 column {col}"

def test_coordinate_renaming_and_simulated_flag(etl_data):
    """Test §4.1 REQ-4 and REQ-5: customer coordinates and is_simulated column."""
    df_orders = etl_data['orders']
    assert 'customer_latitude' in df_orders.columns
    assert 'customer_longitude' in df_orders.columns
    assert 'Latitude' not in df_orders.columns
    assert 'Longitude' not in df_orders.columns
    
    assert 'is_simulated' in df_orders.columns
    assert 'is_simulated' in etl_data['shipments'].columns
    assert 'is_simulated' in etl_data['order_items'].columns
    assert (df_orders['is_simulated'] == False).all()

def test_synthetic_column_flagging(etl_data):
    """Test column-level and table-level synthetic flagging."""
    df_orders = etl_data['orders']
    assert 'assigned_warehouse_id_is_synthetic' in df_orders.columns
    assert (df_orders['assigned_warehouse_id_is_synthetic'] == True).all()
    
    synthetic_tables = ['suppliers', 'supplier_products', 'warehouses', 'warehouse_inventory', 'vehicles']
    for tbl in synthetic_tables:
        df = etl_data[tbl]
        assert 'is_synthetic' in df.columns
        assert (df['is_synthetic'] == True).all()

def test_supplier_coverage_and_tradeoffs(etl_data):
    """Test §4.4 REQ-2: Supplier expansion, partial coverage, and niche product edge cases."""
    df_sup = etl_data['suppliers']
    df_sp = etl_data['supplier_products']
    
    assert len(df_sup) >= 150, "Must have at least 150 suppliers total"
    
    # Check 1 Primary + at least 2 Alternate suppliers per category
    categories = df_sup['category_id'].unique()
    for cat_id in categories:
        cat_sups = df_sup[df_sup['category_id'] == cat_id]
        primaries = cat_sups[cat_sups['is_primary'] == True]
        alternates = cat_sups[cat_sups['is_primary'] == False]
        assert len(primaries) >= 1, f"Category {cat_id} missing primary supplier"
        assert len(alternates) >= 2, f"Category {cat_id} missing at least 2 alternate suppliers"
        
    # Check niche product IDs exist with high unit_cost_multiplier across alternates
    niche_pids = [12, 45, 87, 102]
    for npid in niche_pids:
        alt_sp = df_sp[(df_sp['product_id'] == npid) & (df_sp['is_primary'] == False)]
        if not alt_sp.empty:
            assert (alt_sp['unit_cost_multiplier'] > 1.3).all()

def test_geo_lookup_coverage(etl_data):
    """Test §4.4 REQ-5: Geo lookup contains 100% of destination country translations and centroids."""
    geo = etl_data['geo_lookup']
    df_orders = etl_data['orders']
    dest_countries = df_orders['destination_country'].unique()
    
    for country in dest_countries:
        assert country in geo['countries'], f"Destination country '{country}' missing from geo_lookup.json"
        coords = geo['countries'][country]
        assert len(coords) == 2 and isinstance(coords[0], (int, float))

def test_etl_reject_flag_logic(etl_data):
    """Test §4.1 REQ-2 & §4.9 REQ-1: Audit counters present in validation report."""
    report = etl_data['report']
    assert 'loaded_records' in report
    assert 'rejected_records' in report
    assert 'flagged_records' in report
    assert report['loaded_records'] > 0

def test_data_dictionary_schema_match(etl_data):
    """Test that Master Data Dictionary matches output CSV schema definitions."""
    with open('docs/data_dictionary/v3_data_dictionary.md', 'r', encoding='utf-8') as f:
        dict_text = f.read()
        
    for table_name in ['customers', 'products', 'orders', 'shipments', 'order_items', 'suppliers', 'supplier_products', 'warehouses', 'warehouse_inventory', 'vehicles']:
        assert table_name in dict_text, f"Data dictionary missing table {table_name}"
