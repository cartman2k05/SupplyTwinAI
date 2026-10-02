# SupplyTwinAI — Data Cleaning Setup

## 1. Download the dataset
Get **DataCo Smart Supply Chain Dataset** from Kaggle:
https://www.kaggle.com/datasets/shashwatwork/dataco-smart-supply-chain-for-big-data-analysis

Save `DataCoSupplyChainDataset.csv` in the **same folder** as `clean_and_map.py`.

## 2. Install dependencies
```bash
pip install -r requirements.txt
```

## 3. Run the script
```bash
python clean_and_map.py
```

## 4. What you'll get (inside `cleaned_data/`)

| File | Use it for |
|---|---|
| `raw_profile_report.html` | Open in browser — full data quality overview (nulls, correlations, distributions) |
| `customers.csv` | Import into your Postgres `Customers` table |
| `products.csv` | Import into your Postgres `Products` table |
| `orders.csv` | Import into your Postgres `Orders` table |
| `shipments.csv` | Import into your Postgres `Shipments` table |
| `suppliers.csv` | Synthesized — import into `Suppliers` table |
| `warehouses.csv` | Synthesized — import into `Warehouses` table |
| `vehicles.csv` | Synthesized — import into `Vehicles` table |
| `relationships.csv` | Edge list for Neo4j — Supplier→Product, Order→Warehouse links |
| `cleaning_log.md` | Full record of what was cleaned/dropped/imputed — paste into your report's Data Preprocessing section |

## 5. Loading into PostgreSQL
Quickest way, per table:
```bash
psql -U your_user -d SupplyTwinAI -c "\copy products FROM 'cleaned_data/products.csv' DELIMITER ',' CSV HEADER;"
```
Repeat for each CSV. Make sure your table column names match the CSV headers, or adjust one side.

## 6. Loading relationships into Neo4j
```cypher
LOAD CSV WITH HEADERS FROM 'file:///relationships.csv' AS row
MERGE (a {id: row.from_id})
MERGE (b {id: row.to_id})
MERGE (a)-[r:RELATES {type: row.rel}]->(b);
```
(Refine this once your node labels — `:Supplier`, `:Product`, `:Warehouse`, `:Order` — are set up properly; this is a generic starting query.)

## 7. Why some tables are "synthesized"
DataCo is an order/shipping/customer dataset — it has no native supplier, warehouse,
or vehicle data. The script generates realistic synthetic values for these
(derived from real categories/regions in the dataset) so your full CRUD system and
Knowledge Graph stay populated end-to-end. **State this clearly as an assumption
in your report** — it's normal and expected for student projects combining public
datasets with a broader system design.

## 8. Next step: feed the cleaned data into your models
- `shipments.csv` (`Late_delivery_risk`, `delivery_delay_days`) → train your **Risk Agent** classifier
- `orders.csv` (aggregate `Sales`/`Order_Item_Quantity` by month/product) → train your **Demand Agent** forecaster
- `relationships.csv` → import into Neo4j for your **Knowledge Graph** + GraphRAG retrieval
