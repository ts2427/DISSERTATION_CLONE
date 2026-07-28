"""
Parse reasoning pass JSON results and apply to full dataset
"""

import json
import pandas as pd
from pathlib import Path

print("=" * 100)
print("APPLY REASONING PASS RESULTS TO FULL DATASET")
print("=" * 100)

# ============================================================================
# STEP 1: Load reasoning pass results
# ============================================================================
print("\n[1/4] Loading reasoning pass results...")

results_path = Path("outputs/reasoning_pass_254_results.json")
with open(results_path, 'r') as f:
    reasoning_results = json.load(f)

print(f"  Loaded: {len(reasoning_results)} org_name resolutions")

# Build mapping dictionaries
org_name_to_cik = {}
org_name_to_source = {}
org_name_to_confidence = {}

for entry in reasoning_results:
    org_name = entry['org_name']
    org_name_to_cik[org_name] = entry.get('correct_cik')
    org_name_to_source[org_name] = entry.get('source', 'reasoning pass')
    org_name_to_confidence[org_name] = entry.get('confidence', 'UNKNOWN')

print(f"  Mapped org_names: {len(org_name_to_cik)}")

# ============================================================================
# STEP 2: Load current dataset with exact matching results
# ============================================================================
print("\n[2/4] Loading dataset with exact matching results...")

dataset_path = Path("Data/processed/FINAL_DISSERTATION_DATASET_WITH_RESOLVED_CIK.csv")
df = pd.read_csv(dataset_path)

print(f"  Dataset: {len(df):,} records")
print(f"  Current resolved_cik coverage: {df['resolved_cik'].notna().sum():,} ({df['resolved_cik'].notna().sum()/len(df)*100:.1f}%)")

# ============================================================================
# STEP 3: Fill in unresolved records using reasoning pass results
# ============================================================================
print("\n[3/4] Merging reasoning pass results...")

# For records with NULL resolved_cik, try to fill from reasoning pass
unresolved_mask = df['resolved_cik'].isna()
unresolved_count_before = unresolved_mask.sum()

for idx in df[unresolved_mask].index:
    org_name = df.loc[idx, 'org_name']
    if org_name in org_name_to_cik:
        cik = org_name_to_cik[org_name]
        if pd.notna(cik):
            df.loc[idx, 'resolved_cik'] = cik
            df.loc[idx, 'resolution_source'] = org_name_to_source[org_name]
            df.loc[idx, 'resolution_confidence'] = org_name_to_confidence[org_name]

unresolved_count_after = df['resolved_cik'].isna().sum()
newly_resolved = unresolved_count_before - unresolved_count_after

print(f"  Newly resolved from reasoning pass: {newly_resolved:,} records")
print(f"  Unresolved before: {unresolved_count_before:,}")
print(f"  Unresolved after: {unresolved_count_after:,}")

# ============================================================================
# STEP 4: Report final coverage
# ============================================================================
print("\n[4/4] Final coverage report...")

final_resolved = df['resolved_cik'].notna().sum()
final_unresolved = df['resolved_cik'].isna().sum()

print(f"\n  FINAL CIK COVERAGE:")
print(f"    Resolved: {final_resolved:,} records ({final_resolved/len(df)*100:.1f}%)")
print(f"    Unresolved: {final_unresolved:,} records ({final_unresolved/len(df)*100:.1f}%)")

# Confidence breakdown
if 'resolution_confidence' in df.columns:
    high_conf = len(df[df['resolution_confidence'] == 'HIGH'])
    medium_conf = len(df[df['resolution_confidence'] == 'MEDIUM'])
    low_conf = len(df[df['resolution_confidence'] == 'LOW'])

    print(f"\n  CONFIDENCE BREAKDOWN (of resolved records):")
    print(f"    HIGH: {high_conf:,} ({high_conf/final_resolved*100:.1f}%)")
    print(f"    MEDIUM: {medium_conf:,} ({medium_conf/final_resolved*100:.1f}%)")
    print(f"    LOW: {low_conf:,} ({low_conf/final_resolved*100:.1f}%)")

# Save final dataset
output_path = Path("Data/processed/FINAL_DISSERTATION_DATASET_WITH_CORRECTED_CIK.csv")
df.to_csv(output_path, index=False)

print(f"\nFinal dataset saved: {output_path}")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 100)
print("COMPLETION SUMMARY: DATA INTEGRITY REPAIR")
print("=" * 100)

print(f"""
DATASET COVERAGE:
  Total records: {len(df):,}
  Resolved CIKs: {final_resolved:,} ({final_resolved/len(df)*100:.1f}%)
  Unresolved: {final_unresolved:,} ({final_unresolved/len(df)*100:.1f}%)

IMPROVEMENT FROM EXACT MATCHING:
  Before reasoning pass: 349 resolved (44.8%)
  After reasoning pass: {final_resolved:,} ({final_resolved/len(df)*100:.1f}%)
  Gain: +{final_resolved - 349} records (+{(final_resolved - 349)/len(df)*100:.1f} percentage points)

METHODOLOGY:
  1. Exact matching on normalized names: 197 unique org_names (349 records)
  2. Known subsidiaries: 3 unique org_names (3 records)
  3. Reasoning pass (SEC CIK lookups): {newly_resolved:,} records
  4. Total: {final_resolved:,} records with valid CIK

NEXT STEPS:
  1. Validate remaining {final_unresolved:,} unresolved records
  2. Bridge resolved_cik to CRSP PERMNO using crsp.stocknames (date-aware)
  3. Recompute dependent variables (CAR, BHAR, volatility) with correct stock returns
  4. Re-run H1-H6 regressions with corrected data
  5. Document all corrections in methodology section

OUTPUT: {output_path}
""")

print("=" * 100)
