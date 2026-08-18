"""
Central configuration: all file paths in one place.
Nothing else in the codebase should hardcode a filename.
"""
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_RAW = ROOT_DIR / "data" / "raw"
DATA_PROCESSED = ROOT_DIR / "data" / "processed"
DATA_PROCESSED.mkdir(parents=True, exist_ok=True)

# --- Raw input files ---
INPUT_CSV = DATA_RAW / "Unihack__Sample_Dataset_-_Input.csv"
EXPECTED_OUTPUT_CSV = DATA_RAW / "Unihack__Expected_Output_-_Delivery_Format.csv"

# --- Processed outputs ---
CLEANED_INPUT_PARQUET = DATA_PROCESSED / "cleaned_input.parquet"
GROUND_TRUTH_PARQUET = DATA_PROCESSED / "ground_truth.parquet"
OUTPUT_SCHEMA_JSON = DATA_PROCESSED / "output_schema.json"

# --- Placeholder strings that mean "field is empty" ---
PLACEHOLDER_VALUES = {
    "-- Unbranded --",
    "-- No Unilog Brand --",
    "-- No DIB Brand --",
    "-- No Brand --",
    "-- No E1 Brand --",
    "",
    "N/A",
    "n/a",
    "nan",
}

def is_placeholder(value) -> bool:
    """Returns True if a cell value is a known empty placeholder."""
    if value is None:
        return True
    import math
    if isinstance(value, float) and math.isnan(value):
        return True
    return str(value).strip() in PLACEHOLDER_VALUES