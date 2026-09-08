import pandas as pd
from pathlib import Path

RAW_DIR = Path(__file__).parent.parent / "data" / "raw"
STAGING_DIR = Path(__file__).parent.parent / "data" / "staging"

# --- Step 1: Load the source file ---
customers = pd.read_csv(RAW_DIR / "olist_customers_dataset.csv")
print(f"Customers loaded: {customers.shape}")

# --- Step 2: Select and rename columns to match DIM_CUSTOMER ---
dim_customer = customers[[
    "customer_id",
    "customer_unique_id",
    "customer_city",
    "customer_state",
    "customer_zip_code_prefix",
]].rename(columns={
    "customer_zip_code_prefix": "customer_zip_prefix",
})

# --- Step 3: Sanity checks ---
print(f"\nFinal DIM_CUSTOMER shape: {dim_customer.shape}")
print(f"Nulls:\n{dim_customer.isnull().sum()}")
print(f"\nSample rows:\n{dim_customer.head()}")

# --- Step 4: Save to staging ---
STAGING_DIR.mkdir(exist_ok=True)
output_path = STAGING_DIR / "dim_customer.csv"
dim_customer.to_csv(output_path, index=False)
print(f"\nSaved cleaned DIM_CUSTOMER to: {output_path}")
