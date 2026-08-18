"""
Parses the 2 example rows from the Expected Output CSV as ground truth.

These 2 rows (Frigidaire dishwasher + Whirlpool dishwasher) are your
reference for what a correct completed output looks like. Use them to:
  - Verify your pipeline output format matches the schema
  - Manually inspect what each field should look like when filled
  - Compare agent output against a known-good answer
"""
import pandas as pd
from pipeline.config import EXPECTED_OUTPUT_CSV, GROUND_TRUTH_PARQUET


def load_ground_truth(force_reload: bool = False) -> pd.DataFrame:
    """
    Returns the 2 sample rows from the Expected Output CSV as a DataFrame.
    Only non-header rows with actual data are returned.
    Caches to data/processed/ground_truth.parquet.
    """
    if GROUND_TRUTH_PARQUET.exists() and not force_reload:
        return pd.read_parquet(GROUND_TRUTH_PARQUET)

    if not EXPECTED_OUTPUT_CSV.exists():
        raise FileNotFoundError(
            f"Expected output CSV not found at {EXPECTED_OUTPUT_CSV}.\n"
            "Place 'Unihack__Expected_Output_-_Delivery_Format.csv' in data/raw/."
        )

    df = pd.read_csv(EXPECTED_OUTPUT_CSV, dtype=str)
    df.columns = [c.strip() for c in df.columns]

    # Drop rows where ALL cells are empty
    df = df.dropna(how="all").reset_index(drop=True)

    df.to_parquet(GROUND_TRUTH_PARQUET, index=False)
    print(f"[ground_truth] Loaded {len(df)} ground truth rows.")
    return df


def get_field(row_index: int, field: str) -> str | None:
    """
    Quick helper: returns the value of one field from one ground truth row.

    Args:
        row_index: 0 = Frigidaire dishwasher, 1 = Whirlpool dishwasher
        field: exact column name e.g. "SHORT_DESC", "BRAND_NAME"
    """
    df = load_ground_truth()
    if row_index >= len(df):
        raise IndexError(f"Only {len(df)} ground truth rows available.")
    val = df.iloc[row_index].get(field)
    if pd.isna(val) if val is not None else True:
        return None
    return str(val).strip() if val else None


def preview_ground_truth() -> None:
    """Prints a human-readable side-by-side of the 2 example rows."""
    df = load_ground_truth()
    key_fields = [
        "Mfg_Part_Num", "Part_Desc", "Part_Manuf",
        "MANUFACTURER_NAME", "BRAND_NAME",
        "Classpath",
        "INVOICE_DESC", "MOBILE_DESC",
        "SHORT_DESC", "LONG_DESC1", "RETAIL_DESC",
        "MARKETING_DESCRIPTION",
        "ATTRIBUTE_LABEL 1", "ATTRIBUTE_VALUE 1",
        "ATTRIBUTE_LABEL 2", "ATTRIBUTE_VALUE 2",
        "ATTRIBUTE_LABEL 3", "ATTRIBUTE_VALUE 3",
        "Warranty", "Country Of Origin",
        "MFR URL",
    ]
    for i, (_, row) in enumerate(df.iterrows(), start=1):
        print(f"\n{'='*60}")
        print(f"GROUND TRUTH ROW {i+1}")
        print(f"{'='*60}")
        for field in key_fields:
            val = row.get(field, "")
            if pd.notna(val) and str(val).strip():
                print(f"  {field}: {val}")


if __name__ == "__main__":
    preview_ground_truth()