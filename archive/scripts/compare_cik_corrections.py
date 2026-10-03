"""
Compare original CIK vs resolved CIK - identify corrections
"""

import pandas as pd
from pathlib import Path

print("=" * 100)
print("CIK CORRECTIONS REPORT: ORIGINAL vs RESOLVED")
print("=" * 100)

# Load original and corrected datasets
original_path = Path("Data/processed/FINAL_DISSERTATION_DATASET_DEDUPLICATED_ENRICHED.csv")
resolved_path = Path("Data/processed/FINAL_DISSERTATION_DATASET_WITH_RESOLVED_CIK.csv")

df_original = pd.read_csv(original_path)
df_resolved = pd.read_csv(resolved_path)

print(f"\nLoaded datasets:")
print(f"  Original: {len(df_original):,} records")
print(f"  Resolved: {len(df_resolved):,} records")

# ============================================================================
# Compare CIK values
# ============================================================================
print("\n[1/3] Analyzing CIK corrections...")

# Create comparison columns
df_resolved['cik_changed'] = df_resolved.apply(
    lambda row: pd.notna(row['resolved_cik']) and (pd.isna(row['cik']) or row['cik'] != row['resolved_cik']),
    axis=1
)

df_resolved['had_original_cik'] = df_resolved['cik'].notna()
df_resolved['got_resolved_cik'] = df_resolved['resolved_cik'].notna()

# Categorize each record
def categorize_resolution(row):
    if pd.isna(row['cik']) and pd.isna(row['resolved_cik']):
        return 'NO_CIK_EITHER'
    elif pd.isna(row['cik']) and pd.notna(row['resolved_cik']):
        return 'NEWLY_RESOLVED'
    elif pd.notna(row['cik']) and pd.isna(row['resolved_cik']):
        return 'LOST_RESOLUTION'
    elif row['cik'] == row['resolved_cik']:
        return 'CIK_UNCHANGED'
    else:
        return 'CIK_CORRECTED'

df_resolved['resolution_category'] = df_resolved.apply(categorize_resolution, axis=1)

# Summary
print(f"\nResolution categories:")
for category in ['NEWLY_RESOLVED', 'CIK_CORRECTED', 'CIK_UNCHANGED', 'NO_CIK_EITHER', 'LOST_RESOLUTION']:
    count = len(df_resolved[df_resolved['resolution_category'] == category])
    print(f"  {category:20s}: {count:4d} records ({count/len(df_resolved)*100:5.1f}%)")

# ============================================================================
# Show major corrections
# ============================================================================
print("\n[2/3] Major CIK corrections (original → resolved)...")

corrected = df_resolved[df_resolved['resolution_category'] == 'CIK_CORRECTED'].copy()
if len(corrected) > 0:
    print(f"\n  Total corrected: {len(corrected)} records")
    print(f"\n  Sample corrections (first 20):")

    for idx, (_, row) in enumerate(corrected.head(20).iterrows()):
        print(f"    {row['org_name'][:50]:50s} | {int(row['cik']):>10d} → {int(row['resolved_cik']):>10d}")
else:
    print(f"\n  No CIK corrections (exact matcher chose not to override original values)")

# ============================================================================
# Show newly resolved
# ============================================================================
print(f"\n[3/3] Newly resolved records (had no original CIK, now have one)...")

newly_resolved = df_resolved[df_resolved['resolution_category'] == 'NEWLY_RESOLVED'].copy()
if len(newly_resolved) > 0:
    print(f"\n  Total newly resolved: {len(newly_resolved)} records")
    print(f"  Sample newly resolved (first 20):")

    for idx, (_, row) in enumerate(newly_resolved.head(20).iterrows()):
        print(f"    {row['org_name'][:50]:50s} → CIK {int(row['resolved_cik']):>10d}")
else:
    print(f"\n  No newly resolved records")

# ============================================================================
# Impact summary
# ============================================================================
print("\n" + "=" * 100)
print("IMPACT SUMMARY")
print("=" * 100)

print(f"""
DATASET CORRECTIONS:
  Records with changes: {len(corrected):,} (CIK corrected)
  Records newly resolved: {len(newly_resolved):,} (no CIK → now have CIK)
  Records unchanged: {len(df_resolved[df_resolved['resolution_category'] == 'CIK_UNCHANGED']):,}
  Records still unresolved: {len(df_resolved[df_resolved['resolution_category'] == 'NO_CIK_EITHER']):,}

TOTAL CIK COVERAGE IMPROVEMENT:
  Original: {df_resolved['cik'].notna().sum():,} records with CIK ({df_resolved['cik'].notna().sum()/len(df_resolved)*100:.1f}%)
  Resolved: {df_resolved['resolved_cik'].notna().sum():,} records with CIK ({df_resolved['resolved_cik'].notna().sum()/len(df_resolved)*100:.1f}%)
  Coverage gain: +{len(newly_resolved)} records (+{len(newly_resolved)/len(df_resolved)*100:.1f} percentage points)

NEXT STEP: Compare stock returns
  The {len(corrected)} corrected records now use different firm's stock returns
  The {len(newly_resolved)} newly resolved records now have correct stock returns (were NULL before)
  These changes will impact:
    - H1 coefficient (market timing effect)
    - H2 coefficient (FCC regulation effect)
    - All dependent variables (CAR, BHAR, volatility, turnover)
""")

# Save comparison for reference
comparison_output = Path("outputs/cik_corrections_detailed.csv")
df_resolved[['org_name', 'breach_date', 'cik', 'resolved_cik', 'resolution_source', 'resolution_category']].to_csv(
    comparison_output, index=False
)

print(f"Detailed comparison saved: {comparison_output}")
print("=" * 100)
