import pandas as pd
from pathlib import Path
from sqlalchemy import text
from db_connection import get_engine

STAGING_DIR = Path(__file__).parent.parent / "data" / "staging"


def clear_existing_data(engine):
    """
    Delete any previously loaded rows so this script can be re-run safely.
    FACT_ORDERS must be cleared first since it has foreign keys pointing
    to the dimension tables.
    """
    print("Clearing existing data (if any)...")
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM FACT_ORDERS"))
        conn.execute(text("DELETE FROM DIM_CUSTOMER"))
        conn.execute(text("DELETE FROM DIM_PRODUCT"))
        conn.execute(text("DELETE FROM DIM_SELLER"))
        conn.execute(text("DELETE FROM DIM_TIME"))
    print("Cleared.\n")


def load_dim_customer(engine):
    df = pd.read_csv(STAGING_DIR / "dim_customer.csv")
    df.to_sql("DIM_CUSTOMER", engine, if_exists="append", index=False, chunksize=1000)
    print(f"Loaded DIM_CUSTOMER: {len(df)} rows")


def load_dim_product(engine):
    df = pd.read_csv(STAGING_DIR / "dim_product.csv")
    df.to_sql("DIM_PRODUCT", engine, if_exists="append", index=False, chunksize=1000)
    print(f"Loaded DIM_PRODUCT: {len(df)} rows")


def load_dim_seller(engine):
    df = pd.read_csv(STAGING_DIR / "dim_seller.csv")
    df["effective_date"] = pd.to_datetime(df["effective_date"])
    df["end_date"] = pd.to_datetime(df["end_date"])  # stays NaT -> NULL
    # Oracle has no native boolean; is_current is NUMBER(1) with CHECK(0,1)
    df["is_current"] = df["is_current"].astype(int)
    df.to_sql("DIM_SELLER", engine, if_exists="append", index=False, chunksize=1000)
    print(f"Loaded DIM_SELLER: {len(df)} rows")


def load_dim_time(engine):
    df = pd.read_csv(STAGING_DIR / "dim_time.csv")
    df["full_date"] = pd.to_datetime(df["full_date"])
    # Oracle has no native boolean; these are NUMBER(1) with CHECK(0,1)
    df["is_weekend"] = df["is_weekend"].astype(int)
    df["is_holiday"] = df["is_holiday"].astype(int)
    df.to_sql("DIM_TIME", engine, if_exists="append", index=False, chunksize=1000)
    print(f"Loaded DIM_TIME: {len(df)} rows")


def build_lookup(engine, table, key_col, natural_col):
    """Reads back the surrogate keys Oracle generated, as a lookup DataFrame."""
    query = f"SELECT {key_col}, {natural_col} FROM {table}"
    lookup = pd.read_sql(query, engine)
    print(f"Built lookup for {table}: {len(lookup)} rows")
    return lookup


def load_fact_orders(engine):
    fact = pd.read_csv(STAGING_DIR / "fact_orders.csv")
    fact["order_date"] = pd.to_datetime(fact["order_date"])
    print(f"\nFACT_ORDERS staging rows: {len(fact)}")

    # --- Resolve surrogate keys via lookups against the now-loaded dims ---
    customer_lookup = build_lookup(engine, "DIM_CUSTOMER", "customer_key", "customer_id")
    product_lookup = build_lookup(engine, "DIM_PRODUCT", "product_key", "product_id")
    seller_lookup = build_lookup(engine, "DIM_SELLER", "seller_key", "seller_id")
    time_lookup = build_lookup(engine, "DIM_TIME", "time_key", "full_date")
    time_lookup["full_date"] = pd.to_datetime(time_lookup["full_date"])

    fact = fact.merge(customer_lookup, on="customer_id", how="left")
    fact = fact.merge(product_lookup, on="product_id", how="left")
    fact = fact.merge(seller_lookup, on="seller_id", how="left")
    fact = fact.merge(time_lookup, left_on="order_date", right_on="full_date", how="left")

    # --- Sanity check: every row must have resolved all 4 surrogate keys ---
    missing = fact[["customer_key", "product_key", "seller_key", "time_key"]].isnull().any(axis=1)
    if missing.sum() > 0:
        print(f"WARNING: {missing.sum()} rows failed to resolve a surrogate key - dropping them.")
        fact = fact[~missing]

    # --- Select final columns matching FACT_ORDERS table structure ---
    fact_final = fact[[
        "order_id", "order_item_id",
        "customer_key", "product_key", "seller_key", "time_key",
        "price", "freight_value", "payment_value", "review_score", "delivery_days",
    ]].copy()

    fact_final.to_sql("FACT_ORDERS", engine, if_exists="append", index=False, chunksize=1000)
    print(f"Loaded FACT_ORDERS: {len(fact_final)} rows")


if __name__ == "__main__":
    engine = get_engine()

    clear_existing_data(engine)

    print("--- Loading dimensions ---")
    load_dim_customer(engine)
    load_dim_product(engine)
    load_dim_seller(engine)
    load_dim_time(engine)

    print("\n--- Loading fact table ---")
    load_fact_orders(engine)

    print("\nLoad complete.")
