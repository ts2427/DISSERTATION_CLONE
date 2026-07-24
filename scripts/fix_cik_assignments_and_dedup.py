"""
FIX CIK ASSIGNMENTS AND DEDUPLICATION
1. Check for near-duplicate firm-date pairs (same CIK, dates within 7 days)
2. Reassign Boost Mobile from DISH CIK to Sprint CIK (correction of ownership attribution)
3. Collapse DISH February 2023 (one incident, three rows) to single observation
4. Regenerate canonical FCC firm list
"""

import pandas as pd
import numpy as np
from datetime import timedelta

print("=" * 80)
print("CIK ASSIGNMENT CORRECTIONS AND DEDUPLICATION ANALYSIS")
print("=" * 80)

# Load data
df = pd.read_csv('Data/processed/FINAL_DISSERTATION_DATASET_DEDUPLICATED_ENRICHED.csv')
print(f"\nStarting sample: {len(df)} observations")

# ============================================================================
# STEP 1: FIND NEAR-DUPLICATE FIRM-DATE PAIRS
# ============================================================================
print("\n" + "=" * 80)
print("STEP 1: DETECT NEAR-DUPLICATE FIRM-DATE PAIRS")
print("=" * 80)
print("(Same CIK, breach dates within 7 days)")

df['breach_date'] = pd.to_datetime(df['breach_date'])
df_sorted = df.sort_values(['cik', 'breach_date']).copy()

near_duplicates = []

for cik in df_sorted['cik'].unique():
    cik_data = df_sorted[df_sorted['cik'] == cik].copy()

    if len(cik_data) < 2:
        continue

    cik_data_reset = cik_data.reset_index(drop=True)

    for i in range(len(cik_data_reset) - 1):
        current_row = cik_data_reset.iloc[i]
        next_row = cik_data_reset.iloc[i + 1]

        date_diff = (next_row['breach_date'] - current_row['breach_date']).days

        if 0 < date_diff <= 7:  # Within 7 days, but not exact same date
            near_duplicates.append({
                'cik': cik,
                'org_name_1': current_row['org_name'],
                'breach_date_1': current_row['breach_date'],
                'car_1': current_row['car_30d'],
                'org_name_2': next_row['org_name'],
                'breach_date_2': next_row['breach_date'],
                'car_2': next_row['car_30d'],
                'days_apart': date_diff
            })

if len(near_duplicates) > 0:
    print(f"\nFound {len(near_duplicates)} near-duplicate firm-date pairs:\n")

    near_dup_df = pd.DataFrame(near_duplicates)
    for idx, row in near_dup_df.iterrows():
        print(f"  CIK {int(row['cik'])}: {row['org_name_1']} ({row['breach_date_1'].date()}) → {row['org_name_2']} ({row['breach_date_2'].date()}) [{row['days_apart']} days apart]")
        print(f"    CAR 1: {row['car_1']:.2f}% vs CAR 2: {row['car_2']:.2f}%")

    near_dup_df.to_csv('outputs/defense_prep/near_duplicate_pairs_7day.csv', index=False)
    print(f"\nDetailed output: outputs/defense_prep/near_duplicate_pairs_7day.csv")
else:
    print("\nNo near-duplicate pairs found within 7 days.")

# ============================================================================
# STEP 2: REASSIGN BOOST MOBILE TO SPRINT
# ============================================================================
print("\n" + "=" * 80)
print("STEP 2: REASSIGN BOOST MOBILE FROM DISH TO SPRINT")
print("=" * 80)

print("""
REGULATORY REASONING (documented before correction):

Boost Mobile in March 2019:
  - Status: Prepaid wireless brand owned by Sprint
  - Operations: Reseller on Sprint's network (MVNO)
  - Ownership: Sprint Inc.
  - CPNI Obligation: Belongs to Sprint (facilities-based carrier)
  - FCC Reporting: CPNI breach attributable to Sprint

Correction:
  - Current assignment: CIK 1001082 (DISH Network) - INCORRECT
  - Correct assignment: CIK 1283699 (Sprint) - Ownership at time of breach
  - Rationale: Reassignment is a factual correction, not a discretionary classification
  - Result: Observation stays FCC-reportable (Sprint is FCC-reportable)
""")

# Find and reassign the Boost Mobile row
boost_mobile_mask = (df['cik'] == 1001082) & (df['org_name'] == 'Boost Mobile')
boost_count = boost_mobile_mask.sum()

if boost_count > 0:
    print(f"\nBoost Mobile rows found: {boost_count}")
    print(f"  Reassigning from CIK 1001082 to CIK 1283699 (Sprint)")

    df.loc[boost_mobile_mask, 'cik'] = 1283699

    print(f"  ✓ Reassignment complete")
else:
    print(f"\nNo Boost Mobile rows found under expected criteria")

# ============================================================================
# STEP 3: COLLAPSE DISH FEBRUARY 2023 (ONE INCIDENT, THREE ROWS)
# ============================================================================
print("\n" + "=" * 80)
print("STEP 3: COLLAPSE DISH FEBRUARY 2023 RANSOMWARE INCIDENT")
print("=" * 80)

print("""
Incident: DISH Network ransomware disclosure (Feb 22-23, 2023)
Records in dataset: 3 rows (same CIK, near-identical CARs, dates 1 day apart)
Deduplication: Collapsed to 1 record, keeping most complete information
""")

# Find DISH February 2023 rows
dish_feb_mask = (
    (df['cik'] == 1001082) &
    (df['breach_date'].dt.month == 2) &
    (df['breach_date'].dt.year == 2023)
)

dish_feb_rows = df[dish_feb_mask].copy()
print(f"\nDISH February 2023 rows before collapse: {len(dish_feb_rows)}")
print(dish_feb_rows[['cik', 'org_name', 'breach_date', 'car_30d']].to_string(index=False))

if len(dish_feb_rows) > 1:
    # Keep the first occurrence (earliest date), drop the others
    first_idx = dish_feb_rows.index[0]
    indices_to_drop = dish_feb_rows.index[1:]

    print(f"\nKeeping: {dish_feb_rows.loc[first_idx, 'org_name']} ({dish_feb_rows.loc[first_idx, 'breach_date'].date()})")
    print(f"Dropping: {len(indices_to_drop)} duplicate rows")

    df = df.drop(indices_to_drop)

    print(f"✓ Collapse complete")
else:
    print("Only 1 DISH February 2023 row found - no collapse needed")

# ============================================================================
# STEP 4: REGENERATE CANONICAL FCC FIRM LIST
# ============================================================================
print("\n" + "=" * 80)
print("STEP 4: CANONICAL FCC FIRM LIST (AFTER CORRECTIONS)")
print("=" * 80)

print(f"\nPost-correction sample: {len(df)} observations")
print(f"Post-correction FCC observations: {df['fcc_reportable'].sum()}")

fcc_corrected = df[df['fcc_reportable'] == True].copy()

fcc_firms_corrected = fcc_corrected.groupby('cik').agg({
    'org_name': lambda x: list(set(x))[0],  # First unique org_name
    'sic': 'first',
    'car_30d': ['count', 'mean'],
    'fcc_reportable': 'first'
}).reset_index()

fcc_firms_corrected.columns = ['cik', 'org_name', 'sic', 'n_breaches', 'mean_car', 'fcc_reportable']
fcc_firms_corrected = fcc_firms_corrected.sort_values('n_breaches', ascending=False)

print(f"\nCORRECTED FCC FIRM LIST:")
print(f"Total FCC CIKs: {len(fcc_firms_corrected)}")
print(f"Total FCC observations: {int(fcc_firms_corrected['n_breaches'].sum())}")

print(f"\n{'Rank':<5} {'CIK':<12} {'Firm':<35} {'N Obs':>8} {'Mean CAR':>10}")
print("-" * 72)

for i, (_, row) in enumerate(fcc_firms_corrected.iterrows(), 1):
    print(f"{i:<5} {int(row['cik']):<12} {str(row['org_name'])[:34]:<35} {int(row['n_breaches']):>8} {row['mean_car']:>10.2f}%")

# Save corrected list
fcc_firms_corrected.to_csv('outputs/defense_prep/canonical_fcc_firm_list_corrected.csv', index=False)

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 80)
print("CORRECTION SUMMARY")
print("=" * 80)

original_fcc_count = 127
corrected_fcc_count = int(fcc_firms_corrected['n_breaches'].sum())
original_firm_count = 9
corrected_firm_count = len(fcc_firms_corrected)

print(f"\nSample Changes:")
print(f"  Total observations: {len(df)} (down from 784 due to DISH dedup)")
print(f"  FCC observations: {corrected_fcc_count} (down from {original_fcc_count} due to DISH dedup)")
print(f"  FCC CIKs: {corrected_firm_count} (change: {corrected_firm_count - original_firm_count:+d})")

print(f"\nCIK Corrections:")
print(f"  ✓ Boost Mobile: Reassigned from CIK 1001082 (DISH) to CIK 1283699 (Sprint)")
print(f"    Reasoning: Ownership attribution to Sprint (firm that held CPNI at breach date)")

print(f"\nDeduplication:")
print(f"  ✓ DISH February 2023: Collapsed from 3 rows to 1 (one ransomware incident)")
print(f"    Result: {original_fcc_count - corrected_fcc_count} observations removed")

print(f"\nNear-Duplicate Detection:")
if len(near_duplicates) > 0:
    print(f"  ⚠ Found {len(near_duplicates)} additional same-CIK pairs within 7 days")
    print(f"    These may be valid separate incidents or dedup misses")
    print(f"    Manual review recommended before wider dedup rule change")
else:
    print(f"  ✓ No other near-duplicate pairs found (7-day window)")

print(f"\nFiles generated:")
print(f"  - outputs/defense_prep/canonical_fcc_firm_list_corrected.csv")
print(f"  - outputs/defense_prep/near_duplicate_pairs_7day.csv")

print("\n" + "=" * 80)
print("STATUS: Ready for H2 regression with corrected CIKs and dedup")
print("=" * 80)
