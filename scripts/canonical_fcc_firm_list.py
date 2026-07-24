"""
CANONICAL FCC FIRM RECONCILIATION
One authoritative list of FCC firms from the corrected dataset
Check for CIK type inconsistencies and Sprint/T-Mobile recoding issues
"""

import pandas as pd
import numpy as np

print("=" * 80)
print("CANONICAL FCC FIRM LIST RECONCILIATION")
print("=" * 80)

# Load the corrected dataset
df = pd.read_csv('Data/processed/FINAL_DISSERTATION_DATASET_DEDUPLICATED_ENRICHED.csv')
df = df.dropna(subset=['car_30d', 'firm_size_log', 'leverage', 'roa'])

print(f"\nDataset: {len(df)} total observations")
print(f"FCC observations: {df['fcc_reportable'].sum()}")

# Get all distinct FCC firms with full information
fcc_all = df[df['fcc_reportable'] == True].copy()

# Check CIK data types
print(f"\nCIK data type check:")
print(f"  df['cik'] dtype: {df['cik'].dtype}")
print(f"  fcc_all['cik'] dtype: {fcc_all['cik'].dtype}")

# Get canonical firm list
fcc_firms_canonical = fcc_all.groupby('cik').agg({
    'org_name': lambda x: list(set(x)),  # All unique org_names for this CIK
    'sic': 'first',
    'car_30d': ['count', 'mean'],
    'breach_date': ['min', 'max']
}).reset_index()

fcc_firms_canonical.columns = ['cik', 'org_names', 'sic', 'n_breaches', 'mean_car', 'first_breach', 'last_breach']
fcc_firms_canonical = fcc_firms_canonical.sort_values('n_breaches', ascending=False)

print(f"\n" + "=" * 80)
print(f"CANONICAL FCC FIRM LIST (from corrected dataset)")
print(f"=" * 80)
print(f"\nTotal unique FCC CIKs: {len(fcc_firms_canonical)}")
print(f"Total FCC observations: {fcc_firms_canonical['n_breaches'].sum()}")

print(f"\n{'Rank':<5} {'CIK':<15} {'SIC':<8} {'N Obs':>8} {'Mean CAR':>10} {'Org Names (all variants)':<50}")
print("-" * 130)

for i, (_, row) in enumerate(fcc_firms_canonical.iterrows(), 1):
    cik = int(row['cik']) if isinstance(row['cik'], (int, np.integer)) else row['cik']
    sic = int(row['sic']) if pd.notna(row['sic']) else 'N/A'
    n_obs = int(row['n_breaches'])
    mean_car = row['mean_car']
    org_names = '; '.join(row['org_names'])[:48]

    print(f"{i:<5} {cik:<15} {sic:<8} {n_obs:>8} {mean_car:>10.2f}% {org_names:<50}")

# Check for CIK collisions (multiple distinct org_names for same CIK)
print(f"\n" + "=" * 80)
print(f"CIK COLLISION CHECK")
print(f"=" * 80)

collisions = fcc_firms_canonical[fcc_firms_canonical['org_names'].apply(len) > 1]
if len(collisions) > 0:
    print(f"\n⚠ ALERT: {len(collisions)} CIKs have multiple organization names")
    for _, row in collisions.iterrows():
        cik = int(row['cik']) if isinstance(row['cik'], (int, np.integer)) else row['cik']
        print(f"\nCIK {cik}:")
        for name in row['org_names']:
            count = len(fcc_all[(fcc_all['cik'] == row['cik']) & (fcc_all['org_name'] == name)])
            print(f"  - {name}: {count} observations")
else:
    print(f"\n✓ No CIK collisions found")

# Check Sprint/T-Mobile recoding
print(f"\n" + "=" * 80)
print(f"SPRINT/T-MOBILE RECODING CHECK")
print(f"=" * 80)

sprint_mask = fcc_all['org_name'].str.contains('Sprint', case=False, na=False)
tmobile_mask = fcc_all['org_name'].str.contains('T-Mobile|TMO', case=False, na=False)

print(f"\nBreaches with 'Sprint' in org_name: {sprint_mask.sum()}")
print(f"Breaches with 'T-Mobile' in org_name: {tmobile_mask.sum()}")

# Check if they map to same CIK
sprint_ciks = fcc_all[sprint_mask]['cik'].unique()
tmobile_ciks = fcc_all[tmobile_mask]['cik'].unique()

print(f"\nUnique CIKs for Sprint breaches: {sprint_ciks}")
print(f"Unique CIKs for T-Mobile breaches: {tmobile_ciks}")

if len(sprint_ciks) > 0 and len(tmobile_ciks) > 0:
    if any(cik in tmobile_ciks for cik in sprint_ciks):
        print(f"\n⚠ ALERT: Sprint and T-Mobile share CIK(s)")
        shared = [cik for cik in sprint_ciks if cik in tmobile_ciks]
        for cik in shared:
            sprint_count = len(fcc_all[(fcc_all['cik'] == cik) & (fcc_all['org_name'].str.contains('Sprint', na=False))])
            tmobile_count = len(fcc_all[(fcc_all['cik'] == cik) & (fcc_all['org_name'].str.contains('T-Mobile', na=False))])
            print(f"  CIK {cik}: {sprint_count} Sprint obs + {tmobile_count} T-Mobile obs")
    else:
        print(f"\n✓ Sprint and T-Mobile use separate CIKs")

# Check for string/integer CIK inconsistencies
print(f"\n" + "=" * 80)
print(f"DATA TYPE CONSISTENCY CHECK")
print(f"=" * 80)

cik_types = df['cik'].apply(lambda x: type(x).__name__).value_counts()
print(f"\nCIK types in full dataset:")
for dtype, count in cik_types.items():
    print(f"  {dtype}: {count}")

# Final summary
print(f"\n" + "=" * 80)
print(f"CANONICAL FCC TREATMENT GROUP")
print(f"=" * 80)
print(f"\nFinal firm count: {len(fcc_firms_canonical)} unique FCC CIKs")
print(f"Total FCC observations: {int(fcc_firms_canonical['n_breaches'].sum())}")
print(f"\nFirms:")
for idx, (_, row) in enumerate(fcc_firms_canonical.iterrows(), 1):
    cik = int(row['cik']) if isinstance(row['cik'], (int, np.integer)) else row['cik']
    primary_name = row['org_names'][0]
    print(f"  {idx}. CIK {cik} | {primary_name} | {int(row['n_breaches'])} obs")

# Save canonical list
fcc_firms_canonical.to_csv('outputs/defense_prep/canonical_fcc_firm_list.csv', index=False)
print(f"\nSaved to: outputs/defense_prep/canonical_fcc_firm_list.csv")

print("\n" + "=" * 80)
print("NEXT STEP: Reconcile discrepancies and document classification decisions")
print("=" * 80)
