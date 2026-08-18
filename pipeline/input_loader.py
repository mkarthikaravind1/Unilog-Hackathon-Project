"""
Loads and cleans the 1000-row input CSV.

Input columns:
    Mfg_Part_Num, Part_Desc, E1_Brand, Unilog_Brand, DIB_Brand, Part_Manuf

Cleaning steps:
  1. Strip whitespace from all string columns
  2. Replace placeholder brand values with None
  3. Extract clean manufacturer name (strip the code suffix like "(2435)")
  4. Drop fully empty rows
  5. Cache to parquet
"""
import re
import pandas as pd
from pipeline.config import (
    INPUT_CSV,
    CLEANED_INPUT_PARQUET,
    is_placeholder,
)

# Matches trailing codes like " (2435)" or " (APPDE)" in Part_Manuf
MFR_CODE_PATTERN = re.compile(r"\s*\([^)]+\)\s*$")


def clean_manufacturer_name(raw: str) -> str:
    """Strips trailing distributor codes from Part_Manuf field.
    
    Example:
        'Freud Inc (2435)'        -> 'Freud Inc'
        'Appliance Dealers (APPDE)' -> 'Appliance Dealers'
    """
    if not raw or is_placeholder(raw):
        return "None"
    return MFR_CODE_PATTERN.sub("", str(raw).strip()).strip()


def load_input(force_reload: bool = False) -> pd.DataFrame:
    """
    Returns cleaned input DataFrame with columns:
        Mfg_Part_Num, Part_Desc, E1_Brand, Unilog_Brand,
        DIB_Brand, Part_Manuf, Manufacturer_Clean

    Caches result to data/processed/cleaned_input.parquet.
    """
    if CLEANED_INPUT_PARQUET.exists() and not force_reload:
        return pd.read_parquet(CLEANED_INPUT_PARQUET)

    if not INPUT_CSV.exists():
        raise FileNotFoundError(
            f"Input CSV not found at {INPUT_CSV}.\n"
            "Place 'Unihack__Sample_Dataset_-_Input.csv' in data/raw/."
        )

    df = pd.read_csv(INPUT_CSV, dtype=str)

    # Normalize column names
    df.columns = [c.strip() for c in df.columns]

    # Strip whitespace from all cells
    df = df.apply(lambda col: col.str.strip() if col.dtype == object else col)

    # Replace placeholder brand values with None
    brand_cols = ["E1_Brand", "Unilog_Brand", "DIB_Brand"]
    for col in brand_cols:
        if col in df.columns:
            df[col] = df[col].apply(
                lambda v: None if is_placeholder(v) else v
            )

    # Add clean manufacturer name column
    df["Manufacturer_Clean"] = df["Part_Manuf"].apply(clean_manufacturer_name)

    # Drop fully empty rows
    df = df.dropna(how="all").reset_index(drop=True)

    df.to_parquet(CLEANED_INPUT_PARQUET, index=False)
    print(f"[input_loader] Loaded {len(df)} rows, {len(df.columns)} columns.")
    return df


def get_sample_rows(n: int = 5) -> pd.DataFrame:
    """Returns n sample rows for quick inspection."""
    df = load_input()
    return df.head(n)


if __name__ == "__main__":
    df = load_input(force_reload=True)
    print(df.head(5).to_string())
    print(f"\nPlaceholder brand stats:")
    print(f"  E1_Brand None count:     {df['E1_Brand'].isna().sum()}/{len(df)}")
    print(f"  Unilog_Brand None count: {df['Unilog_Brand'].isna().sum()}/{len(df)}")
    print(f"  DIB_Brand None count:    {df['DIB_Brand'].isna().sum()}/{len(df)}")
    print(f"  Mfr clean sample:")
    print(df[["Part_Manuf", "Manufacturer_Clean"]].head(10).to_string())