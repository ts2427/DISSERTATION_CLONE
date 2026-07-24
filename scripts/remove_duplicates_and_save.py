"""
REMOVE DUPLICATE ROWS AND SAVE CORRECTED DATASET
Removes 4 identified duplicates and saves to FINAL_DISSERTATION_DATASET_DEDUPLICATED_ENRICHED.csv
"""

import pandas as pd
import numpy as np

print("=" * 100)
print("REMOVE DUPLICATES AND SAVE CORRECTED DATASET")
print("=" * 100)

# Load data
df = pd.read_csv('Data/processed/FINAL_DISSERTATION_DATASET_DEDUPLICATED_ENRICHED.csv')
df['breach_date'] = pd.to_datetime(df['breach_date'])

initial_count = len(df)
print(f"\nInitial dataset size: {initial_count} rows")

# ============================================================================
# STEP 0: REASSIGN BOOST MOBILE FROM DISH TO SPRINT
# ============================================================================
print("\n" + "=" * 100)
print("BOOST MOBILE CIK REASSIGNMENT")
print("=" * 100)

boost_mask = (df['org_name'] == 'Boost Mobile') & (df['cik'] == 1001082)
boost_count = boost_mask.sum()

if boost_count > 0:
    print(f"\nBoost Mobile found: {boost_count} row(s) under CIK 1001082 (DISH)")
    print(f"  Breach date: {df[boost_mask]['breach_date'].iloc[0]}")
    print(f"  Reassigning to CIK 1283699 (Sprint)...")
    df.loc[boost_mask, 'cik'] = 1283699
    print(f"  ✓ Reassignment complete")
else:
    print("\nNo Boost Mobile rows found under CIK 1001082")

# ============================================================================
# STEP 1: REMOVE DUPLICATE ROWS
# ============================================================================
print("\n" + "=" * 100)
print("DUPLICATE REMOVAL")
print("=" * 100)

rows_to_remove = []

# Candidate 1: Intuit 2019-03-21/26
print("\n1. Intuit 2019-03-21 vs 2019-03-26")
intuit_dups = df[
    (df['cik'] == 896878) &
    (df['breach_date'].isin([pd.Timestamp('2019-03-21'), pd.Timestamp('2019-03-26')]))
]
print(f"   Found {len(intuit_dups)} rows")
if len(intuit_dups) >= 2:
    # Keep the one with immediate_disclosure=1 (the formal filing)
    keep_idx = intuit_dups[intuit_dups['immediate_disclosure'] == 1].index[0]
    remove_idx = intuit_dups[intuit_dups.index != keep_idx].index[0]
    rows_to_remove.append(remove_idx)
    print(f"   Keeping row with immediate_disclosure=1 (2019-03-26)")
    print(f"   Removing row 2019-03-21 (index {remove_idx})")

# Candidate 2: Corebridge 2023-05-29/30
print("\n2. Corebridge 2023-05-29 vs 2023-05-30")
core_dups = df[
    (df['cik'] == 713676) &
    (df['breach_date'].isin([pd.Timestamp('2023-05-29'), pd.Timestamp('2023-05-30')]))
]
print(f"   Found {len(core_dups)} rows")
if len(core_dups) >= 2:
    # Keep the first (earliest date)
    keep_idx = core_dups.iloc[0].name
    for idx in core_dups.index[1:]:
        rows_to_remove.append(idx)
    print(f"   Keeping 2023-05-29 row")
    print(f"   Removing 2023-05-30 row(s)")

# Candidate 3: Fidelity 2023-10-04/06
print("\n3. Fidelity 2023-10-04 vs 2023-10-06")
fid_dups = df[
    (df['cik'] == 1136893) &
    (df['breach_date'].isin([pd.Timestamp('2023-10-04'), pd.Timestamp('2023-10-06')]))
]
print(f"   Found {len(fid_dups)} rows")
if len(fid_dups) >= 2:
    # Keep the first (earliest date)
    keep_idx = fid_dups.iloc[0].name
    for idx in fid_dups.index[1:]:
        rows_to_remove.append(idx)
    print(f"   Keeping 2023-10-04 row")
    print(f"   Removing 2023-10-06 row(s)")

# Candidate 4: Sprint/T-Mobile 2021-08-17/18
print("\n4. Sprint/T-Mobile 2021-08-17 vs 2021-08-18")
tmobile_dups = df[
    (df['cik'] == 1283699) &
    (df['breach_date'].isin([pd.Timestamp('2021-08-17'), pd.Timestamp('2021-08-18')]))
]
print(f"   Found {len(tmobile_dups)} rows")
if len(tmobile_dups) >= 2:
    # Remove all 2021-08-18 rows (consolidate to 08-17)
    remove_idx_list = tmobile_dups[tmobile_dups['breach_date'] == pd.Timestamp('2021-08-18')].index
    for idx in remove_idx_list:
        rows_to_remove.append(idx)
    # Also remove duplicate 08-17 entries (T-Mobile USA vs T-Mobile USA, Inc.)
    rows_08_17 = tmobile_dups[tmobile_dups['breach_date'] == pd.Timestamp('2021-08-17')]
    if len(rows_08_17) > 1:
        # Keep first, remove others
        for idx in rows_08_17.index[1:]:
            rows_to_remove.append(idx)
    print(f"   Keeping one 2021-08-17 row")
    print(f"   Removing 2021-08-18 row(s) and duplicate 2021-08-17 variant(s)")

# Remove duplicates
rows_to_remove_unique = list(set(rows_to_remove))
print(f"\nTotal rows to remove: {len(rows_to_remove_unique)}")

df_cleaned = df.drop(rows_to_remove_unique)
final_count = len(df_cleaned)

print(f"Final dataset size: {final_count} rows (removed {initial_count - final_count})")

# ============================================================================
# STEP 2: VERIFY FCC COUNT
# ============================================================================
print("\n" + "=" * 100)
print("FCC COUNT VERIFICATION")
print("=" * 100)

fcc_before = (df['fcc_reportable'] == True).sum()
fcc_after = (df_cleaned['fcc_reportable'] == True).sum()

print(f"\nFCC observations before: {fcc_before}")
print(f"FCC observations after: {fcc_after}")
print(f"FCC observations removed: {fcc_before - fcc_after}")

# ============================================================================
# STEP 3: SAVE CORRECTED DATASET
# ============================================================================
print("\n" + "=" * 100)
print("SAVING CORRECTED DATASET")
print("=" * 100)

output_path = 'Data/processed/FINAL_DISSERTATION_DATASET_DEDUPLICATED_ENRICHED.csv'
df_cleaned.to_csv(output_path, index=False)

print(f"\n✓ Saved to: {output_path}")
print(f"  Rows: {final_count}")
print(f"  Columns: {len(df_cleaned.columns)}")

print("\n" + "=" * 100)
print("STATUS: READY FOR PIPELINE RERUN")
print("=" * 100)
