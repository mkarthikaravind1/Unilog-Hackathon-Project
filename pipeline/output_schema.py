"""
Defines the 252-column output schema from the Expected Output CSV.

Two jobs:
  1. load_schema()         -> ordered list of all 252 column names
  2. empty_output_row()    -> dict with all 252 keys set to None
                             (fill this dict in your pipeline, then write to CSV)

Also groups columns by category so agents know which fields they own.
"""
import json
import pandas as pd
from pipeline.config import EXPECTED_OUTPUT_CSV, OUTPUT_SCHEMA_JSON


def load_schema(force_reload: bool = False) -> list[str]:
    """Returns the ordered list of 252 output column names."""
    if OUTPUT_SCHEMA_JSON.exists() and not force_reload:
        with open(OUTPUT_SCHEMA_JSON) as f:
            return json.load(f)

    if not EXPECTED_OUTPUT_CSV.exists():
        raise FileNotFoundError(
            f"Expected output CSV not found at {EXPECTED_OUTPUT_CSV}.\n"
            "Place 'Unihack__Expected_Output_-_Delivery_Format.csv' in data/raw/."
        )

    df = pd.read_csv(EXPECTED_OUTPUT_CSV, nrows=0)  # headers only
    columns = [c.strip() for c in df.columns.tolist()]

    with open(OUTPUT_SCHEMA_JSON, "w") as f:
        json.dump(columns, f, indent=2)

    print(f"[output_schema] Loaded {len(columns)} output columns.")
    return columns


def empty_output_row() -> dict:
    """Returns a dict with all 252 output keys set to None.
    
    Your pipeline fills this dict field by field, then passes it
    to the output writer which converts it to a CSV row.
    """
    return {col: None for col in load_schema()}


# --- Column groups (agents know which fields they own) ---

URL_FIELDS = [
    "MFR URL", "Ref URL 1", "Ref URL 2",
    "Ref URL 3", "Ref URL 4", "Ref URL 5",
]

IDENTITY_FIELDS = [
    "PART_NUMBER", "Mfg_Part_Num", "MANUFACTURER_PART_NUMBER",
    "ALTERNATE_PART_NUMBER", "SKU - MY_PART_NUMBER",
    "Dept", "Class", "Fine",
]

BRAND_FIELDS = [
    "MANUFACTURER_NAME", "BRAND_NAME", "TRADE_NAME",
    "E1_Brand", "Unilog_Brand", "DIB_Brand", "Part_Manuf",
]

CLASSIFICATION_FIELDS = ["Classpath", "UNSPSC"]

DESCRIPTION_FIELDS = [
    "MOBILE_DESC",       # 60-80 chars
    "INVOICE_DESC",      # <=40 chars, ALL CAPS
    "SHORT_DESC",        # Product title
    "LONG_DESC1",        # Full long description
    "RETAIL_DESC",       # Retail variant
    "MARKETING_DESCRIPTION",
]

FEATURES_FIELDS = [f"ITEM_FEATURES_{i}" for i in range(1, 21)]

EXTRA_FIELDS = ["With", "Standard/Approvals", "Prop 65",
                "Application", "Includes", "Product Name"]

# Attribute slots: ATTRIBUTE_LABEL n, ATTRIBUTE_VALUE n, ATTRIBUTE_UOM n
ATTRIBUTE_FIELDS = []
for i in range(1, 51):
    ATTRIBUTE_FIELDS.extend([
        f"ATTRIBUTE_LABEL {i}",
        f"ATTRIBUTE_VALUE {i}",
        f"ATTRIBUTE_UOM {i}",
    ])

COMMERCE_FIELDS = [
    "UPC", "EAN", "GTIN", "Warranty",
    "List Price", "Selling Qty", "Selling UOM",
    "Standard Packaging Information",
]

DIMENSION_FIELDS = [
    "LENGTH", "LENGTH_UOM", "HEIGHT", "HEIGHT_UOM",
    "WIDTH", "WIDTH_UOM", "WEIGHT", "WEIGHT_UOM",
    "VOLUME", "VOLUME_UOM",
]

DIGITAL_ASSET_FIELDS = [
    "Product Image", "Alternate Image 1", "Alternate Image 2",
    "Alternate Image 3", "Alternate Image 4",
    "SDS", "SDS_1", "Warranty Information", "Catalog",
    "Specification Sheet", "Instruction/Installation Manual",
    "Service Manual", "Owners/User Manual", "Line Drawing",
    "MTR", "RoHS", "Full Engineering Drawing", "Energy Star Guide",
    "Technical Bulletin", "Submittal", "Compatibility Chart",
    "Size Chart", "Product Label/Insert", "Video Link", "Video Link 1",
]

MISC_FIELDS = ["Country Of Origin", "Discontinued", "Actual Image (Yes/No)"]


COLUMN_GROUPS = {
    "urls": URL_FIELDS,
    "identity": IDENTITY_FIELDS,
    "brand": BRAND_FIELDS,
    "classification": CLASSIFICATION_FIELDS,
    "descriptions": DESCRIPTION_FIELDS,
    "features": FEATURES_FIELDS,
    "extras": EXTRA_FIELDS,
    "attributes": ATTRIBUTE_FIELDS,
    "commerce": COMMERCE_FIELDS,
    "dimensions": DIMENSION_FIELDS,
    "digital_assets": DIGITAL_ASSET_FIELDS,
    "misc": MISC_FIELDS,
}


if __name__ == "__main__":
    cols = load_schema(force_reload=True)
    print(f"\nTotal columns: {len(cols)}")
    for group, fields in COLUMN_GROUPS.items():
        print(f"  {group}: {len(fields)} fields")
    row = empty_output_row()
    print(f"\nEmpty output row keys: {len(row)}")