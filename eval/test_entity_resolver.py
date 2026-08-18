"""
Day 2 test runner for the Entity Resolver agent.

Tests two things:
  1. Ground truth check  - run on the 2 known rows, compare to expected
  2. Sample batch check  - run on 5 rows from the 1000-row input

Run:
    python eval/test_entity_resolver.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pipeline.input_loader import load_input
from pipeline.ground_truth import load_ground_truth
from pipeline.agents.entity_resolver import resolve_entity


def test_ground_truth():
    print("\n" + "="*60)
    print("TEST 1: GROUND TRUTH ROWS")
    print("="*60)

    gt = load_ground_truth()

    for row_num, (_, row) in enumerate(gt.iterrows(), start=1):
        print(f"\n--- Ground Truth Row {row_num} ---")
        input_row = {
            "Mfg_Part_Num": row.get("Mfg_Part_Num"),
            "Part_Desc": row.get("Part_Desc"),
            "E1_Brand": row.get("E1_Brand"),
            "Unilog_Brand": row.get("Unilog_Brand"),
            "DIB_Brand": row.get("DIB_Brand"),
            "Part_Manuf": row.get("Part_Manuf"),
        }

        expected_mfr = row.get("MANUFACTURER_NAME", "")
        expected_brand = row.get("BRAND_NAME", "")

        print(f"  Input Part_Desc : {input_row['Part_Desc']}")
        print(f"  Input Part_Manuf: {input_row['Part_Manuf']}")
        print(f"  Expected MFR    : {expected_mfr}")
        print(f"  Expected BRAND  : {expected_brand}")

        result = resolve_entity(input_row)

        print(f"  Got MFR         : {result['MANUFACTURER_NAME']}")
        print(f"  Got BRAND       : {result['BRAND_NAME']}")
        print(f"  Confidence      : {result['confidence']}")
        print(f"  Needs review    : {result['needs_review']}")
        print(f"  Reasoning       : {result['reasoning']}")

        mfr_match = expected_mfr.lower().strip() in result["MANUFACTURER_NAME"].lower()
        brand_match = (
            expected_brand.replace("®", "").replace("™", "").lower().strip()
            in result["BRAND_NAME"].replace("®", "").replace("™", "").lower()
        )
        print(f"  MFR match  : {'✓' if mfr_match else '✗'}")
        print(f"  Brand match: {'✓' if brand_match else '✗'}")


def test_sample_batch():
    print("\n" + "="*60)
    print("TEST 2: SAMPLE BATCH (5 rows from 1000-row input)")
    print("="*60)

    df = load_input()
    # Pick 5 diverse rows
    sample = df.iloc[[0, 1, 50, 200, 500]].to_dict(orient="records")

    for row in sample:
        print(f"\n  Part: {row['Mfg_Part_Num']} | {row['Part_Desc'][:60]}")
        result = resolve_entity(row)
        print(f"  MFR  : {result['MANUFACTURER_NAME']}")
        print(f"  Brand: {result['BRAND_NAME']}")
        print(f"  Conf : {result['confidence']} | Review: {result['needs_review']}")
        print(f"  Why  : {result['reasoning']}")


if __name__ == "__main__":
    print("Installing groq if needed...")
    import subprocess
    subprocess.run(["pip", "install", "groq", "-q"])

    test_ground_truth()
    test_sample_batch()

    print("\n" + "="*60)
    print("DAY 2 ENTITY RESOLVER TEST COMPLETE")
    print("="*60)