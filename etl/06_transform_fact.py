import pandas as pd
from pathlib import Path

RAW_DIR = Path(__file__).parent.parent / "data" / "raw"
STAGING_DIR = Path(__file__).parent.parent / "data" / "staging"

# --- Step 1: Load all source files needed for the fact table ---
orders = pd.read_csv(
    RAW_DIR / "olist_orders_dataset.csv",
    parse_dates=["order_purchase_timestamp", "order_delivered_customer_date"],
)
order_items = pd.read_csv(RAW_DIR / "olist_order_items_dataset.csv")
payments = pd.read_csv(RAW_DIR / "olist_order_payments_dataset.csv")
reviews = pd.read_csv(RAW_DIR / "olist_order_reviews_dataset.csv")

print(f"orders: {orders.shape}, order_items: {order_items.shape}, "
      f"payments: {payments.shape}, reviews: {reviews.shape}")

# --- Step 2: Handle grain mismatches BEFORE joining ---
# Grain of FACT_ORDERS = one row per product line item within an order.
# But payments and reviews are recorded at the ORDER level, not item level,
# and some orders have multiple payment rows (e.g. split installments) or
# multiple review rows. We must collapse these to one row per order first,
# otherwise joining them onto order_items would duplicate rows and inflate
# totals (a classic fan-out / double-counting bug).

# Payments: an order can have several payment rows (e.g. partial payments,
# different payment types). Sum them to get one total per order.
payments_per_order = payments.groupby("order_id", as_index=False)["payment_value"].sum()

# Reviews: a small number of orders have more than one review. Average the
# score to get one value per order (review_score is non-additive, so
# averaging here - not summing - is the correct treatment).
reviews_per_order = reviews.groupby("order_id", as_index=False)["review_score"].mean()

# --- Step 3: Join everything onto order_items (this sets our grain) ---
fact = order_items.merge(orders, on="order_id", how="left")
fact = fact.merge(payments_per_order, on="order_id", how="left")
fact = fact.merge(reviews_per_order, on="order_id", how="left")

print(f"\nAfter joins: {fact.shape}")

# --- Step 4: Compute delivery_days measure ---
# NULL when the order was never delivered (cancelled, in transit, etc.) -
# this is expected, not an error (2,965 orders found missing this in Step 7).
fact["delivery_days"] = (
    fact["order_delivered_customer_date"] - fact["order_purchase_timestamp"]
).dt.days

# --- Step 5: Select and rename columns to match FACT_ORDERS ---
# Surrogate keys (customer_key, product_key, seller_key, time_key) are NOT
# resolved here - that happens in the Load step, where we look them up
# against the dimension tables already sitting in Oracle. For now we keep
# the natural keys and a plain date, ready for that lookup.
fact_orders = fact[[
    "order_id",
    "order_item_id",
    "customer_id",
    "product_id",
    "seller_id",
    "order_purchase_timestamp",
    "price",
    "freight_value",
    "payment_value",
    "review_score",
    "delivery_days",
]].copy()

fact_orders["order_date"] = fact_orders["order_purchase_timestamp"].dt.normalize()
fact_orders = fact_orders.drop(columns=["order_purchase_timestamp"])

# --- Step 6: Sanity checks ---
print(f"\nFinal FACT_ORDERS (staging) shape: {fact_orders.shape}")
print(f"Nulls:\n{fact_orders.isnull().sum()}")
print(f"\nSample rows:\n{fact_orders.head()}")

# --- Step 7: Save to staging ---
STAGING_DIR.mkdir(exist_ok=True)
output_path = STAGING_DIR / "fact_orders.csv"
fact_orders.to_csv(output_path, index=False)
print(f"\nSaved staged FACT_ORDERS to: {output_path}")
