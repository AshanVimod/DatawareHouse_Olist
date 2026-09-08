import pandas as pd
from pathlib import Path

RAW_DIR = Path(__file__).parent.parent / "data" / "raw"

# --- Step 1: Load the two source files we need ---
products = pd.read_csv(RAW_DIR / "olist_products_dataset.csv")
category_translation = pd.read_csv(RAW_DIR / "product_category_name_translation.csv")

print(f"Products loaded: {products.shape}")
print(f"Category translations loaded: {category_translation.shape}")

# --- Step 2: Join products with the English category names ---
# LEFT JOIN keeps every product, even if its category has no translation match
merged = products.merge(
    category_translation,
    how="left",
    on="product_category_name"
)

# --- Step 3: Handle missing categories ---
# Two separate cases can cause a null category_name_english:
#   (a) product_category_name itself was null (610 rows, found in Step 7)
#   (b) product_category_name existed but had no match in the translation file
merged["product_category_name"] = merged["product_category_name"].fillna("unknown")
merged["product_category_name_english"] = merged["product_category_name_english"].fillna("unknown")

# --- Step 4: Select and rename columns to match DIM_PRODUCT ---
dim_product = merged[[
    "product_id",
    "product_category_name_english",
    "product_category_name",
    "product_weight_g",
    "product_length_cm",
    "product_height_cm",
    "product_width_cm",
]].rename(columns={
    "product_category_name_english": "category_english",
    "product_category_name": "category_portuguese",
})

# --- Step 5: Quick sanity checks ---
print(f"\nFinal DIM_PRODUCT shape: {dim_product.shape}")
print(f"Remaining nulls:\n{dim_product.isnull().sum()}")
print(f"\nSample rows:\n{dim_product.head()}")

# --- Step 6: Save the cleaned result to staging, ready for Step 10 (Load) ---
STAGING_DIR = Path(__file__).parent.parent / "data" / "staging"
STAGING_DIR.mkdir(exist_ok=True)
output_path = STAGING_DIR / "dim_product.csv"
dim_product.to_csv(output_path, index=False)
print(f"\nSaved cleaned DIM_PRODUCT to: {output_path}")
