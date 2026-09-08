import pandas as pd
from pathlib import Path

RAW_DIR = Path(__file__).parent.parent / "data" / "raw"
STAGING_DIR = Path(__file__).parent.parent / "data" / "staging"

# --- Step 1: Load the source file ---
sellers = pd.read_csv(RAW_DIR / "olist_sellers_dataset.csv")
print(f"Sellers loaded: {sellers.shape}")

# --- Step 2: Select and rename columns to match DIM_SELLER ---
dim_seller = sellers[[
    "seller_id",
    "seller_city",
    "seller_state",
    "seller_zip_code_prefix",
]].rename(columns={
    "seller_zip_code_prefix": "seller_zip_prefix",
})

# --- Step 3: Add SCD Type 2 tracking columns ---
# This is a first-time load, so every seller's current record becomes
# "effective" from the earliest date present in the dataset (2016-09-04).
# In a real incremental load, effective_date would be "today", and any
# seller whose attributes changed would get a NEW row here, while their
# OLD row would have end_date set and is_current set to False.
DATASET_START_DATE = "2016-09-04"

dim_seller["effective_date"] = DATASET_START_DATE
dim_seller["end_date"] = None       # NULL = still current
dim_seller["is_current"] = True

# --- Step 4: Sanity checks ---
print(f"\nFinal DIM_SELLER shape: {dim_seller.shape}")
print(f"Nulls:\n{dim_seller.isnull().sum()}")
print(f"\nSample rows:\n{dim_seller.head()}")

# --- Step 5: Save to staging ---
STAGING_DIR.mkdir(exist_ok=True)
output_path = STAGING_DIR / "dim_seller.csv"
dim_seller.to_csv(output_path, index=False)
print(f"\nSaved cleaned DIM_SELLER to: {output_path}")
