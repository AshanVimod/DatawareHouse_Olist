import pandas as pd
from pathlib import Path

RAW_DIR = Path(__file__).parent.parent / "data" / "raw"
STAGING_DIR = Path(__file__).parent.parent / "data" / "staging"

# --- Step 1: Find the full date range we need to cover ---
# DIM_TIME must include every date that FACT_ORDERS could ever reference:
# purchase date, delivery dates, estimated delivery date, etc.
# Unlike the other dimensions, we are not cleaning existing rows here -
# we are GENERATING one row per calendar day across the whole range.
orders = pd.read_csv(
    RAW_DIR / "olist_orders_dataset.csv",
    parse_dates=[
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ],
)

date_columns = [
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date",
]

min_date = orders[date_columns].min().min().normalize()
max_date = orders[date_columns].max().max().normalize()
print(f"Date range needed: {min_date.date()} to {max_date.date()}")

# --- Step 2: Generate one row per calendar day in that range ---
all_dates = pd.date_range(start=min_date, end=max_date, freq="D")
dim_time = pd.DataFrame({"full_date": all_dates})

# --- Step 3: Compute the analytical columns your DDL requires ---
dim_time["year"] = dim_time["full_date"].dt.year
dim_time["quarter"] = "Q" + dim_time["full_date"].dt.quarter.astype(str)
dim_time["month"] = dim_time["full_date"].dt.month
dim_time["month_name"] = dim_time["full_date"].dt.strftime("%B")
dim_time["week_of_year"] = dim_time["full_date"].dt.isocalendar().week.astype(int)
dim_time["day_of_month"] = dim_time["full_date"].dt.day
dim_time["day_name"] = dim_time["full_date"].dt.strftime("%A")
dim_time["is_weekend"] = dim_time["full_date"].dt.dayofweek.isin([5, 6])  # Sat=5, Sun=6

# Brazil's major public holidays are not built into pandas, so this stays
# False for every row unless a specific holiday calendar is added later.
# (This limitation is worth noting in your Part D reflection.)
dim_time["is_holiday"] = False

# --- Step 4: Sanity checks ---
print(f"\nFinal DIM_TIME shape: {dim_time.shape}")
print(f"Nulls:\n{dim_time.isnull().sum()}")
print(f"\nSample rows:\n{dim_time.head()}")

# --- Step 5: Save to staging ---
STAGING_DIR.mkdir(exist_ok=True)
output_path = STAGING_DIR / "dim_time.csv"
dim_time.to_csv(output_path, index=False)
print(f"\nSaved cleaned DIM_TIME to: {output_path}")
