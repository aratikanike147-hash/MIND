# MetricMind — Data Pipeline Documentation
**Owner:** Arati (Data track)

## 1. Overview
This pipeline produces the mock corporate dataset that feeds the
Semantic Layer (Sravani) and, downstream, the Agentic AI (Srinivethitha).

```
generate_mock_data.py  →  raw/sales_raw.csv  →  load_to_db.py  →  raw_sales (DB table)
                                                        │
                                                        ▼
                                          dbt: raw_sales → stg_sales → fct_sales / dim_geography / dim_date
```

## 2. Dataset
**Grain:** one row per order line.

| Field | Description |
|---|---|
| order_id | Unique order line identifier |
| order_date | Date of the order |
| region / country | Geography dimension |
| product_category / product_name | Product dimension |
| sales_channel | Online, Retail Store, Distributor, Wholesale |
| units_sold, unit_price | Sales volume/price |
| revenue | units_sold × unit_price |
| material_cost, shipping_cost, other_cost, total_cost | Cost breakdown |

## 3. Pipeline stages
1. **`data/generate_mock_data.py`** — generates 15,000 mock order rows
   plus ~1% intentional duplicate/missing-value noise for QA testing.
2. **`data/load_to_db.py`** — loads the CSV into a local DB table
   (`raw_sales`). SQLite stands in for Snowflake; swap the connection
   in `get_connection()` for real Snowflake credentials.
3. **dbt models** (`dbt_project/models/`):
   - `raw/raw_sales.sql` — passthrough of the source table.
   - `staging/stg_sales.sql` — deduplicates on `order_id`, drops rows
     with missing region/country, casts types.
   - `transformed/fct_sales.sql` — final fact table with `margin` and
     `margin_pct` computed.
   - `transformed/dim_geography.sql`, `dim_date.sql` — dimension tables.

## 4. Data quality
Run `scripts/validate_data.py` to check for duplicates, missing
critical fields, and incorrect values (negative revenue/cost, revenue
math mismatches).

Run `scripts/final_reconciliation.py` to reconcile raw vs. staged row
counts and revenue totals — used for the Day 29 sign-off.

## 5. Known data-quality findings (mock run)
- 149 duplicate `order_id`s (299 rows) — removed in staging.
- 150 rows with blank `region` — removed in staging.
- No negative revenue/cost or revenue-math mismatches found.
- Row counts reconcile: raw CSV count matches loaded DB count.

## 6. How to run end-to-end
```bash
python3 data/generate_mock_data.py
python3 data/load_to_db.py
python3 scripts/validate_data.py
python3 scripts/final_reconciliation.py
# then: dbt run   (once connected to a real warehouse profile)
```
