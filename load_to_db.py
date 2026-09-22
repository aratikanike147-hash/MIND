"""
Arati - Day 3: Load mock data into Snowflake/local DB and verify tables.

Uses SQLite as a local stand-in for Snowflake so the pipeline runs
without external credentials. Swap `get_connection()` for a
`snowflake.connector.connect(...)` call to point at real Snowflake -
the rest of the pipeline (dbt models, validation) is unaffected.
"""

import sqlite3
import pandas as pd
import os

DATA_DIR = os.path.dirname(__file__)
CSV_PATH = os.path.join(DATA_DIR, "raw", "sales_raw.csv")
DB_PATH = os.path.join(DATA_DIR, "metricmind.db")

TABLE_NAME = "raw_sales"


def get_connection():
    return sqlite3.connect(DB_PATH)


def load_csv_to_db():
    df = pd.read_csv(CSV_PATH)
    conn = get_connection()
    df.to_sql(TABLE_NAME, conn, if_exists="replace", index=False)
    conn.close()
    print(f"Loaded {len(df)} rows into table '{TABLE_NAME}' at {DB_PATH}")


def verify_table():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(f"SELECT COUNT(*) FROM {TABLE_NAME}")
    row_count = cur.fetchone()[0]

    cur.execute(f"PRAGMA table_info({TABLE_NAME})")
    columns = [row[1] for row in cur.fetchall()]

    conn.close()

    print("\n--- Table verification ---")
    print(f"Table: {TABLE_NAME}")
    print(f"Row count: {row_count}")
    print(f"Columns ({len(columns)}): {columns}")

    assert row_count > 0, "Table is empty!"
    expected_cols = {
        "order_id", "order_date", "region", "country",
        "product_category", "product_name", "sales_channel",
        "units_sold", "unit_price", "revenue",
        "material_cost", "shipping_cost", "other_cost", "total_cost",
    }
    missing = expected_cols - set(columns)
    assert not missing, f"Missing expected columns: {missing}"
    print("Verification passed.")


if __name__ == "__main__":
    load_csv_to_db()
    verify_table()
