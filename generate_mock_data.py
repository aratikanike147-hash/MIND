"""
Arati - Day 1 & 2: Mock Corporate Dataset Design + Generation
MetricMind - Agentic Semantic BI Engine

Generates a mock corporate sales dataset covering:
  Sales, Revenue, Cost, Geography, Date

Output: data/raw/sales_raw.csv
"""

import csv
import random
import datetime
import os

random.seed(42)  # reproducible mock data

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "raw")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "sales_raw.csv")

# --- Dimension definitions ------------------------------------------------

REGIONS = {
    "North America": ["United States", "Canada", "Mexico"],
    "Europe": ["Germany", "France", "United Kingdom", "Italy", "Spain"],
    "Asia Pacific": ["India", "China", "Japan", "Australia", "Singapore"],
    "Latin America": ["Brazil", "Argentina", "Chile"],
}

PRODUCT_CATEGORIES = {
    "Electronics": ["Laptop", "Smartphone", "Tablet", "Monitor"],
    "Furniture": ["Office Chair", "Desk", "Bookshelf", "Cabinet"],
    "Apparel": ["Jacket", "T-Shirt", "Shoes", "Backpack"],
    "Home Goods": ["Cookware Set", "Bedding", "Lamp", "Rug"],
}

SALES_CHANNELS = ["Online", "Retail Store", "Distributor", "Wholesale"]

START_DATE = datetime.date(2023, 1, 1)
END_DATE = datetime.date(2024, 12, 31)


def daterange(start, end):
    days = (end - start).days
    return [start + datetime.timedelta(days=i) for i in range(days + 1)]


def random_date():
    delta_days = (END_DATE - START_DATE).days
    return START_DATE + datetime.timedelta(days=random.randint(0, delta_days))


def generate_rows(n=15000):
    rows = []
    for i in range(1, n + 1):
        region = random.choice(list(REGIONS.keys()))
        country = random.choice(REGIONS[region])
        category = random.choice(list(PRODUCT_CATEGORIES.keys()))
        product = random.choice(PRODUCT_CATEGORIES[category])
        channel = random.choice(SALES_CHANNELS)
        order_date = random_date()

        units_sold = random.randint(1, 50)
        unit_price = round(random.uniform(15, 1200), 2)
        revenue = round(units_sold * unit_price, 2)

        # Cost breakdown (feeds Sravani's Cost/Margin metrics
        # and Arati's Day 8 Shipping/Material cost breakdown data)
        material_cost = round(revenue * random.uniform(0.25, 0.45), 2)
        shipping_cost = round(revenue * random.uniform(0.03, 0.12), 2)
        other_cost = round(revenue * random.uniform(0.02, 0.08), 2)
        total_cost = round(material_cost + shipping_cost + other_cost, 2)

        rows.append({
            "order_id": f"ORD-{i:06d}",
            "order_date": order_date.isoformat(),
            "region": region,
            "country": country,
            "product_category": category,
            "product_name": product,
            "sales_channel": channel,
            "units_sold": units_sold,
            "unit_price": unit_price,
            "revenue": revenue,
            "material_cost": material_cost,
            "shipping_cost": shipping_cost,
            "other_cost": other_cost,
            "total_cost": total_cost,
        })

    # --- Inject a small amount of intentional data-quality noise ----------
    # (gives Raj / Arati real duplicate & missing-value checks to run,
    # per Day 3 "Check duplicates, missing values and incorrect data")
    noisy_count = max(1, int(n * 0.01))
    for _ in range(noisy_count):
        row = random.choice(rows).copy()
        row["order_id"] = row["order_id"]  # intentional duplicate order_id
        rows.append(row)

    for _ in range(noisy_count):
        idx = random.randint(0, len(rows) - 1)
        rows[idx]["region"] = ""  # missing value

    return rows


def write_csv(rows, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fieldnames = list(rows[0].keys())
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    rows = generate_rows(n=15000)
    write_csv(rows, OUTPUT_FILE)
    print(f"Generated {len(rows)} rows -> {OUTPUT_FILE}")
