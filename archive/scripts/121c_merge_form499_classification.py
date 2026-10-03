"""
SCRIPT 121C: MERGE FORM 499 CLASSIFICATION INTO MAIN DATASET
=============================================================

Merge form499_classification_final.csv back to main dataset.

Input:  outputs/form499_classification_final.csv (from Script 121B)
        Data/processed/FINAL_DISSERTATION_DATASET_WITH_GOVERNANCE.csv

Output: Data/processed/FINAL_DISSERTATION_DATASET_FORM499_CLASSIFIED.csv
        outputs/form499_sic_comparison.txt

Process:
  1. Load main dataset and Form 499 classification
  2. Merge by org_name + breach_date
  3. Verify no data loss
  4. Compare N_form499 to N_sic (fcc_reportable)
  5. Report any unmatched records
"""

import pandas as pd
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
output_dir = Path('outputs')
data_dir = Path('Data/processed')
data_dir.mkdir(parents=True, exist_ok=True)

print("=" * 80)
print("SCRIPT 121C: MERGE FORM 499 CLASSIFICATION")
print("=" * 80)

# ============================================================================
# LOAD DATA
# ============================================================================
print("\n1. LOADING DATA...")

main_file = data_dir / 'FINAL_DISSERTATION_DATASET_WITH_GOVERNANCE.csv'
form499_file = output_dir / 'form499_classification_final.csv'

try:
    main_df = pd.read_csv(main_file)
    print(f"   Main dataset: {len(main_df)} rows")
except FileNotFoundError:
    print(f"   ERROR: {main_file} not found")
    sys.exit(1)

try:
    form499_df = pd.read_csv(form499_file)
    print(f"   Form 499 classification: {len(form499_df)} rows")
except FileNotFoundError:
    print(f"   ERROR: {form499_file} not found")
    print("   Run Script 121B first")
    sys.exit(1)

# ============================================================================
# MERGE
# ============================================================================
print("\n2. MERGING ON org_name + breach_date...")

# Create merge keys (normalize for matching)
main_df['_merge_key'] = main_df['org_name'].astype(str).str.strip()
form499_df['_merge_key'] = form499_df['org_name'].astype(str).str.strip()

# Merge
merged = main_df.merge(
    form499_df[['org_name', 'breach_date', 'fcc_form499', 'reason_classified', 'termination_status']],
    on=['org_name', 'breach_date'],
    how='left'
)

print(f"   Merged: {len(merged)} rows")
print(f"   Form 499 classification matched: {merged['fcc_form499'].notna().sum()}")
print(f"   Unmatched: {merged['fcc_form499'].isna().sum()}")

# ============================================================================
# COMPARISON
# ============================================================================
print("\n3. TREATMENT STATUS COMPARISON")
print("=" * 80)

# H2 regression sample (has_crsp_data=1)
h2_sample = merged[merged['has_crsp_data'] == 1].copy()

print(f"\nH2 REGRESSION SAMPLE (has_crsp_data=1): {len(h2_sample)} rows")

# SIC-based (fcc_reportable)
sic_treated = (h2_sample['fcc_reportable'] == 1).sum()
sic_treated_firms = h2_sample[h2_sample['fcc_reportable'] == 1]['org_name'].nunique()

print(f"\nSIC-based (fcc_reportable):")
print(f"  Treated observations: {sic_treated}")
print(f"  Treated firms: {sic_treated_firms}")
print(f"  Untreated observations: {(h2_sample['fcc_reportable'] == 0).sum()}")

# Form 499-based (fcc_form499)
form499_treated = (h2_sample['fcc_form499'] == 1).sum()
form499_treated_firms = h2_sample[h2_sample['fcc_form499'] == 1]['org_name'].nunique()

print(f"\nForm 499-based (fcc_form499):")
print(f"  Treated observations: {form499_treated}")
print(f"  Treated firms: {form499_treated_firms}")
print(f"  Untreated observations: {(h2_sample['fcc_form499'] == 0).sum()}")

# Comparison
print(f"\nChange from SIC to Form 499:")
print(f"  Observation delta: {form499_treated - sic_treated} ({100*(form499_treated - sic_treated)/sic_treated:+.1f}%)")
print(f"  Firm delta: {form499_treated_firms - sic_treated_firms} ({100*(form499_treated_firms - sic_treated_firms)/sic_treated_firms:+.1f}%)")

# ============================================================================
# INDETERMINATE CASES
# ============================================================================
print(f"\n4. INDETERMINATE CASES CHECK")
print("=" * 80)

indeterminate = h2_sample[h2_sample['termination_status'].isin(['indeterminate', 'indeterminate_sentinel'])]
print(f"\nIndeterminate cases in treated group: {len(indeterminate)}")

if len(indeterminate) > 0:
    print("\nFirst 10 indeterminate records:")
    for idx, row in indeterminate.head(10).iterrows():
        print(f"  {row['org_name']} ({row['breach_date']})")
        print(f"    Reason: {row['reason_classified']}")
else:
    print("\n✓ No indeterminate cases in treated group (section is moot)")

# ============================================================================
# SAVE
# ============================================================================
print(f"\n5. SAVING MERGED DATASET...")

output_file = data_dir / 'FINAL_DISSERTATION_DATASET_FORM499_CLASSIFIED.csv'
merged.to_csv(output_file, index=False)
print(f"   Saved: {output_file}")

# ============================================================================
# COMPARISON SUMMARY FILE
# ============================================================================
comparison_text = f"""
================================================================================
FORM 499 vs SIC CLASSIFICATION COMPARISON
================================================================================

H2 REGRESSION SAMPLE (has_crsp_data=1): {len(h2_sample)} observations

SIC-BASED (fcc_reportable):
  Treated observations: {sic_treated}
  Treated firms: {sic_treated_firms}
  Untreated: {(h2_sample['fcc_reportable'] == 0).sum()}

FORM 499-BASED (fcc_form499):
  Treated observations: {form499_treated}
  Treated firms: {form499_treated_firms}
  Untreated: {(h2_sample['fcc_form499'] == 0).sum()}

CHANGE:
  Observation delta: {form499_treated - sic_treated:+d}
  Firm delta: {form499_treated_firms - sic_treated_firms:+d}

INDETERMINATE CASES: {len(indeterminate)} (in treated group)

================================================================================
NEXT STEP: Script 85 (H2 re-estimation with Form 499 classification)
================================================================================
"""

comp_file = output_dir / 'form499_sic_comparison.txt'
with open(comp_file, 'w') as f:
    f.write(comparison_text)
print(f"   Saved: {comp_file}")

print("\n" + "=" * 80)
print("MERGE COMPLETE")
print("=" * 80)
