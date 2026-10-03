"""
Merge corrected Item 5.02 executive changes back into main dataset
"""

import pandas as pd
import numpy as np
from pathlib import Path

print("=" * 100)
print("MERGE CORRECTED ITEM 5.02 EXECUTIVE CHANGES INTO DATASET")
print("=" * 100)

# ============================================================================
# STEP 1: Load corrected executive changes
# ============================================================================
print("\n[1/3] Loading corrected executive changes...")

corrected_path = Path("Data/edgar/executive_changes_item5_02_corrected.csv")
if not corrected_path.exists():
    print(f"ERROR: {corrected_path} not found")
    print("First run: python scripts/46_executive_changes_item5_02.py")
    exit(1)

df_corrected = pd.read_csv(corrected_path)
print(f"  Loaded: {len(df_corrected):,} records with corrected Item 5.02 data")
print(f"  Columns: {list(df_corrected.columns)}")

# ============================================================================
# STEP 2: Load current dataset
# ============================================================================
print("\n[2/3] Loading current dataset...")

dataset_path = Path("Data/processed/FINAL_DISSERTATION_DATASET_CORRECTED_WITH_RETURNS.csv")
df = pd.read_csv(dataset_path)
print(f"  Loaded: {len(df):,} records")

# Identify executive change columns to replace
old_exec_cols = [c for c in df.columns if 'executive_change' in c or 'num_changes' in c or 'days_to_first' in c]
print(f"  Executive change columns to replace: {len(old_exec_cols)}")

# ============================================================================
# STEP 3: Merge corrections
# ============================================================================
print("\n[3/3] Merging corrections...")

# Merge on key identifier (should be breach_date + org_name or similar)
# Assuming corrected file has same structure
try:
    # Try to identify common key
    if 'cik' in df_corrected.columns and 'breach_date' in df_corrected.columns:
        merge_keys = ['cik', 'breach_date']
    elif 'org_name' in df_corrected.columns and 'breach_date' in df_corrected.columns:
        merge_keys = ['org_name', 'breach_date']
    else:
        # Assume first columns are identifiers
        merge_keys = list(df_corrected.columns)[:2]

    print(f"  Using merge keys: {merge_keys}")

    # Merge the datasets
    df_merged = df.merge(df_corrected, on=merge_keys, how='left', suffixes=('_old', '_new'))

    # Replace old executive change columns with new ones
    for col in old_exec_cols:
        if f"{col}_new" in df_merged.columns:
            df_merged[col] = df_merged[f"{col}_new"]
            df_merged = df_merged.drop(columns=[f"{col}_new", f"{col}_old"])
        elif f"{col}_old" in df_merged.columns:
            df_merged = df_merged.drop(columns=[f"{col}_old"])

    # ============================================================================
    # STEP 4: Report changes
    # ============================================================================
    print("\n" + "=" * 100)
    print("MERGE COMPLETE")
    print("=" * 100)

    # Check base rates before/after
    print("\nExecutive change base rates - BEFORE vs AFTER correction:")
    for window in [30, 90, 180]:
        col = f'executive_change_{window}d'
        if col in df.columns:
            before = df[col].mean()
            after = df_merged[col].mean()
            print(f"  {window}d: {before:.1%} → {after:.1%} (delta: {after-before:+.1%}pp)")

    # Save merged dataset
    output_path = Path("Data/processed/FINAL_DISSERTATION_DATASET_CORRECTED_TURNOVER.csv")
    df_merged.to_csv(output_path, index=False)

    print(f"\nMerged dataset saved: {output_path}")
    print(f"Records: {len(df_merged):,}")
    print(f"Columns: {len(df_merged.columns)}")

    print("\nNEXT STEP: Re-run H6 regressions")
    print("  python scripts/91_essay3_h6_main_effects.py")

except Exception as e:
    print(f"\nERROR during merge: {e}")
    import traceback
    traceback.print_exc()
    print("\nTroubleshooting:")
    print(f"  1. Check that {corrected_path} exists and is readable")
    print(f"  2. Check merge keys match between files")
    print(f"  3. Verify column names in corrected file")

print("=" * 100)
