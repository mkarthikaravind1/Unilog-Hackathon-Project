"""
Day 1 sanity check. Run this to confirm all loaders work.

    python eval/sanity_check.py

Expected output:
  - Input: 1000 rows loaded, placeholder stats printed
  - Schema: 252 columns confirmed
  - Ground truth: 2 rows printed with key fields
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pipeline.input_loader import load_input
from pipeline.output_schema import load_schema, empty_output_row, COLUMN_GROUPS
from pipeline.ground_truth import load_ground_truth, preview_ground_truth


def check_input():
    print("\n" + "="*50)
    print("CHECKING INPUT LOADER")
    print("="*50)
    df = load_input(force_reload=True)
    print(f"Total rows: {len(df)}")
    print(f"Columns: {list(df.columns)}")
    print(f"\nE1_Brand None:     {df['E1_Brand'].isna().sum()}/{len(df)}")
    print(f"Unilog_Brand None: {df['Unilog_Brand'].isna().sum()}/{len(df)}")
    print(f"DIB_Brand None:    {df['DIB_Brand'].isna().sum()}/{len(df)}")
    print(f"\nSample rows:")
    print(df[["Mfg_Part_Num", "Part_Desc", "Manufacturer_Clean"]].head(5).to_string())


def check_schema():
    print("\n" + "="*50)
    print("CHECKING OUTPUT SCHEMA")
    print("="*50)
    cols = load_schema(force_reload=True)
    print(f"Total output columns: {len(cols)}")
    print(f"\nColumn groups:")
    for group, fields in COLUMN_GROUPS.items():
        print(f"  {group}: {len(fields)} fields")
    row = empty_output_row()
    print(f"\nempty_output_row() keys: {len(row)} ✓")


def check_ground_truth():
    print("\n" + "="*50)
    print("CHECKING GROUND TRUTH")
    print("="*50)
    df = load_ground_truth(force_reload=True)
    print(f"Ground truth rows: {len(df)}")
    preview_ground_truth()


if __name__ == "__main__":
    check_input()
    check_schema()
    check_ground_truth()
    print("\n" + "="*50)
    print("DAY 1 COMPLETE - all loaders working")
    print("="*50)