"""
FIX SOURCE XLSX FILE AND RESYNC
Apply corrections to the base FINAL_DISSERTATION_DATASET.xlsx, then re-run scripts 53 & 80
"""

import pandas as pd
import openpyxl

print("=" * 100)
print("APPLY CORRECTIONS TO SOURCE XLSX AND RESYNC")
print("=" * 100)

# Load from Excel (the source file script 53 reads)
xlsx_path = 'Data/processed/FINAL_DISSERTATION_DATASET.xlsx'
print(f"\nLoading source file: {xlsx_path}")
df = pd.read_excel(xlsx_path)

print(f"Initial state: {len(df)} rows")
print(f"  FCC obs: {(df['fcc_reportable'] == True).sum()}")
boost = df[df['org_name'] == 'Boost Mobile']
if len(boost) > 0:
    print(f"  Boost Mobile CIK: {boost['cik'].iloc[0]}")

# ============================================================================
# STEP 1: REASSIGN BOOST MOBILE FROM DISH TO SPRINT
# ============================================================================
print("\n" + "=" * 100)
print("STEP 1: REASSIGN BOOST MOBILE")
print("=" * 100)

boost_mask = (df['org_name'] == 'Boost Mobile') & (df['cik'] == 1001082)
boost_count = boost_mask.sum()

if boost_count > 0:
    print(f"\nBoost Mobile found: {boost_count} row(s) under CIK 1001082")
    print(f"  Reassigning to CIK 1283699 (Sprint)...")
    df.loc[boost_mask, 'cik'] = 1283699
    print(f"  ✓ Reassignment complete")

# ============================================================================
# STEP 2: REMOVE DUPLICATE ROWS
# ============================================================================
print("\n" + "=" * 100)
print("STEP 2: REMOVE DUPLICATE ROWS")
print("=" * 100)

rows_to_remove = []

# Candidate 1: Intuit 2019-03-21/26
print("\n1. Intuit 2019-03-21 vs 2019-03-26")
df['breach_date'] = pd.to_datetime(df['breach_date'])
intuit_dups = df[
    (df['cik'] == 896878) &
    (df['breach_date'].isin([pd.Timestamp('2019-03-21'), pd.Timestamp('2019-03-26')]))
]
print(f"   Found {len(intuit_dups)} rows")
if len(intuit_dups) >= 2:
    keep_idx = intuit_dups[intuit_dups['immediate_disclosure'] == 1].index[0]
    remove_idx = intuit_dups[intuit_dups.index != keep_idx].index[0]
    rows_to_remove.append(remove_idx)
    print(f"   Removing 2019-03-21 row (keeping 2019-03-26 with immediate_disclosure=1)")

# Candidate 2: Corebridge 2023-05-29/30
print("\n2. Corebridge 2023-05-29 vs 2023-05-30")
core_dups = df[
    (df['cik'] == 713676) &
    (df['breach_date'].isin([pd.Timestamp('2023-05-29'), pd.Timestamp('2023-05-30')]))
]
print(f"   Found {len(core_dups)} rows")
if len(core_dups) >= 2:
    keep_idx = core_dups.iloc[0].name
    for idx in core_dups.index[1:]:
        rows_to_remove.append(idx)
    print(f"   Removing 2023-05-30 row (keeping 2023-05-29)")

# Candidate 3: Fidelity 2023-10-04/06
print("\n3. Fidelity 2023-10-04 vs 2023-10-06")
fid_dups = df[
    (df['cik'] == 1136893) &
    (df['breach_date'].isin([pd.Timestamp('2023-10-04'), pd.Timestamp('2023-10-06')]))
]
print(f"   Found {len(fid_dups)} rows")
if len(fid_dups) >= 2:
    keep_idx = fid_dups.iloc[0].name
    for idx in fid_dups.index[1:]:
        rows_to_remove.append(idx)
    print(f"   Removing 2023-10-06 row (keeping 2023-10-04)")

# Candidate 4: Sprint/T-Mobile 2021-08-17/18
print("\n4. Sprint/T-Mobile 2021-08-17 vs 2021-08-18")
tmobile_dups = df[
    (df['cik'] == 1283699) &
    (df['breach_date'].isin([pd.Timestamp('2021-08-17'), pd.Timestamp('2021-08-18')]))
]
print(f"   Found {len(tmobile_dups)} rows")
if len(tmobile_dups) >= 2:
    remove_idx_list = tmobile_dups[tmobile_dups['breach_date'] == pd.Timestamp('2021-08-18')].index
    for idx in remove_idx_list:
        rows_to_remove.append(idx)
    rows_08_17 = tmobile_dups[tmobile_dups['breach_date'] == pd.Timestamp('2021-08-17')]
    if len(rows_08_17) > 1:
        for idx in rows_08_17.index[1:]:
            rows_to_remove.append(idx)
    print(f"   Removing 2021-08-18 and duplicate 2021-08-17 variant(s)")

# Remove duplicates
rows_to_remove_unique = list(set(rows_to_remove))
print(f"\nTotal rows to remove: {len(rows_to_remove_unique)}")

df_cleaned = df.drop(rows_to_remove_unique)

print(f"After corrections: {len(df_cleaned)} rows")
print(f"  FCC obs: {(df_cleaned['fcc_reportable'] == True).sum()}")
boost_corrected = df_cleaned[df_cleaned['org_name'] == 'Boost Mobile']
if len(boost_corrected) > 0:
    print(f"  Boost Mobile CIK: {boost_corrected['cik'].iloc[0]}")

# ============================================================================
# STEP 3: SAVE BACK TO XLSX
# ============================================================================
print("\n" + "=" * 100)
print("STEP 3: SAVE CORRECTED DATA TO XLSX")
print("=" * 100)

# Remove the row_id column if it exists (added by script 53)
if 'row_id' in df_cleaned.columns:
    df_cleaned = df_cleaned.drop('row_id', axis=1)

# Save to Excel
output_xlsx = 'Data/processed/FINAL_DISSERTATION_DATASET.xlsx'
df_cleaned.to_excel(output_xlsx, index=False, sheet_name='Data')
print(f"\n✓ Saved corrected data to: {output_xlsx}")
print(f"  Rows: {len(df_cleaned)}")
print(f"  Columns: {len(df_cleaned.columns)}")

print("\n" + "=" * 100)
print("STATUS: SOURCE FILE CORRECTED")
print("=" * 100)
print("\nNext: Run scripts 53 and 80 to regenerate the pipeline with corrections")
