"""
FIRM COUNT RECONCILIATION
Compare FCC firm lists across: baseline regression, SCM, leave-one-out
Reconcile CIK assignments and identify discrepancies
"""

import pandas as pd

df = pd.read_csv('Data/processed/FINAL_DISSERTATION_DATASET_DEDUPLICATED_ENRICHED.csv')
df = df.dropna(subset=['car_30d', 'firm_size_log', 'leverage', 'roa'])

# Get baseline FCC firms
fcc_baseline = df[df['fcc_reportable'] == True].copy()
fcc_firms_baseline = fcc_baseline.groupby('cik').agg({
    'org_name': 'first',
    'car_30d': ['count', 'mean']
}).reset_index()
fcc_firms_baseline.columns = ['cik', 'org_name', 'n_obs', 'mean_car']
fcc_firms_baseline = fcc_firms_baseline.sort_values('n_obs', ascending=False)

print("=" * 80)
print("FIRM COUNT RECONCILIATION: FCC FIRMS IN REGRESSION SAMPLE")
print("=" * 80)

print(f"\nBaseline FCC firms (from regression sample, n={len(df)} total):")
print(f"  Total FCC observations: {len(fcc_baseline)}")
print(f"  Unique FCC firms: {fcc_baseline['cik'].nunique()}")
print(f"\n{'Rank':<5} {'CIK':<12} {'Firm':<35} {'N Obs':>8} {'Mean CAR':>10}")
print("-" * 75)

for i, (_, row) in enumerate(fcc_firms_baseline.iterrows(), 1):
    print(f"{i:<5} {int(row['cik']):<12} {str(row['org_name'])[:34]:<35} {int(row['n_obs']):>8} {row['mean_car']:>10.2f}%")

print("\n" + "-" * 75)
print("KNOWN FIRM DISCREPANCIES:")
print("-" * 75)

print("\n1. BOOST MOBILE ISSUE:")
print("   - Leave-one-out: showed CIK 1001082 with 6 observations")
print("   - Forensics: shows only 1 'Boost Mobile' observation in dataset")
print("   - Status: ** CONTRADICTION - needs investigation **")

print("\n2. DISH NETWORK:")
print("   - SCM results: shows DISH with -40.6% effect (3 breaches)")
print("   - Leave-one-out: no DISH listed among the 9 firms removed")
print("   - Status: ** MISSING from regression sample **")

print("\n3. ALTICE:")
print("   - SCM reported 10 firms including Altice")
print("   - Leave-one-out reports 9 firms, no Altice")
print("   - Status: ** MISSING from regression sample **")

print("\n4. NAME/CIK VARIANTS:")
print("   Checking for naming variations in FCC firm names:")

org_names = fcc_baseline.groupby('cik')['org_name'].unique()
for cik, names in org_names.items():
    if len(names) > 1:
        print(f"   CIK {cik}: {names}")

# List all firms with their exact names and CIKs
print("\n" + "=" * 80)
print("COMPLETE FCC FIRM ROSTER (from regression sample):")
print("=" * 80)
for _, row in fcc_firms_baseline.iterrows():
    print(f"CIK {int(row['cik']):<12} | {row['org_name']:<40} | {int(row['n_obs']):>3} obs")

print("\n" + "=" * 80)
print("DATA INTEGRITY ISSUES:")
print("=" * 80)
print("\n⚠ Issue #1: Boost Mobile shows 1 obs in forensics but 6 in leave-one-out")
print("  This suggests CIK 1001082 may encompass multiple org_name variants")
print("  or the leave-one-out is aggregating T-Mobile's observations under Boost Mobile label")

print("\n⚠ Issue #2: DISH and Altice appear in SCM but not in regression sample")
print("  This suggests SCM is using a different sample or firm list than the OLS")

print("\n⚠ Issue #3: Firm count = 9 vs 10 vs uncertainty about which is correct")
print("  Cannot interpret Leave-one-out or SCM results until this is resolved")

# Save roster
fcc_firms_baseline.to_csv('outputs/defense_prep/fcc_firm_roster_regression_sample.csv', index=False)
print("\n\nSaved to: outputs/defense_prep/fcc_firm_roster_regression_sample.csv")
