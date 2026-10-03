"""
CIK ASSIGNMENT INVESTIGATION
Diagnose why Boost Mobile and DISH Network are under the same CIK
Pull raw PRC org_names, check SEC CIK lookups, identify matching error
"""

import pandas as pd

print("=" * 80)
print("CIK ASSIGNMENT INVESTIGATION - CIK 1001082")
print("=" * 80)

df = pd.read_csv('Data/processed/FINAL_DISSERTATION_DATASET_DEDUPLICATED_ENRICHED.csv')

# Pull all rows under CIK 1001082 with maximum detail
cik_1001082_all = df[df['cik'] == 1001082].copy()

print(f"\nTotal rows under CIK 1001082: {len(cik_1001082_all)}")
print(f"\nFull detail of all 6 rows:")
print("=" * 80)

# Show all columns for these rows
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

for idx, (_, row) in enumerate(cik_1001082_all.iterrows(), 1):
    print(f"\nRow {idx}:")
    print(f"  CIK: {row['cik']}")
    print(f"  org_name (as stored): '{row['org_name']}'")
    print(f"  breach_date: {row['breach_date']}")
    print(f"  car_30d: {row['car_30d']:.2f}%")
    print(f"  sic: {row['sic']}")
    print(f"  fcc_reportable: {row['fcc_reportable']}")
    if 'ticker' in df.columns:
        print(f"  ticker: {row.get('ticker', 'N/A')}")
    if 'permno' in df.columns:
        print(f"  permno: {row.get('permno', 'N/A')}")

print("\n" + "=" * 80)
print("ORGANIZATION NAMES UNDER CIK 1001082:")
print("=" * 80)

org_names_unique = cik_1001082_all['org_name'].unique()
for i, name in enumerate(org_names_unique, 1):
    count = len(cik_1001082_all[cik_1001082_all['org_name'] == name])
    mean_car = cik_1001082_all[cik_1001082_all['org_name'] == name]['car_30d'].mean()
    print(f"{i}. '{name}' ({count} obs, mean CAR: {mean_car:.2f}%)")

print("\n" + "=" * 80)
print("SEC CIK LOOKUP NOTES:")
print("=" * 80)

print("""
DISH Network Corporation:
  - Public company traded on NASDAQ: DISH
  - Owns satellite and terrestrial infrastructure
  - Facilities Act common carrier (CPNI obligations)
  - SEC CIK (as of 2023): 1001082 (THIS IS THE REPORTED CIK)

Boost Mobile:
  - Mobile Virtual Network Operator (MVNO)
  - Operated on Sprint network until July 2020
  - Acquired by DISH Network in July 2020
  - As of March 2019 (breach date): owned by Sprint
  - Post-acquisition: integrated into DISH
  - SEC CIK: Should NOT be 1001082 if it was a separate entity before 2020

PROBLEM IDENTIFIED:
  The 2019 Boost Mobile breach is stored under DISH's CIK (1001082)
  But in March 2019, Boost Mobile was a Sprint subsidiary, not DISH
  This suggests the matching algorithm incorrectly assigned Boost to DISH's CIK

FEBRUARY 2023 DISH DATES:
  Row with org_name 'DISH Network L.L.C.' and breach_date 2023-02-22
  Row with org_name 'DISH Network Corporation' and breach_date 2023-02-23
  Row with org_name 'DISH Network L.L.C.' and breach_date 2023-02-23

  These are one day apart (Feb 22 → Feb 23) suggesting same incident
  DISH disclosed major ransomware incident on Feb 22/23, 2023
  Deduplication rule (CIK + breach_date) would NOT catch same-event different-dates

  Need to check: are these three rows actually different breach records,
  or did PRC log the same event under different dates?
""")

print("\n" + "=" * 80)
print("REQUIRED INVESTIGATION:")
print("=" * 80)

print("""
1. BOOST MOBILE CIK:
   [ ] Look up SEC EDGAR: Was Boost Mobile a public company?
   [ ] Check SEC filings: Did Boost file independently before 2020?
   [ ] If yes: Get correct CIK and reassign the 2019 Boost breach
   [ ] If no: Check if Boost was a subsidiary coded under Sprint's CIK (1283699)

2. FEBRUARY 2023 DISH RANSOMWARE:
   [ ] Cross-reference: did DISH disclose one ransomware incident or multiple?
   [ ] PRC might have logged one incident multiple times (different dates, different org_name variants)
   [ ] If same incident: merge to one record before dedup runs
   [ ] If different incidents: keep separate with correct dates

3. CIK ASSIGNMENT FIX:
   [ ] Once correct CIKs identified, update the CSV
   [ ] Run dedup rule again
   [ ] Recount FCC treatment group
   [ ] Verify new counts before regression
""")

# Save the detailed view
cik_1001082_all.to_csv('outputs/defense_prep/cik_1001082_full_detail.csv', index=False)
print("\nData saved to: outputs/defense_prep/cik_1001082_full_detail.csv")

print("\n" + "=" * 80)
print("NEXT STEPS (in order):")
print("1. Verify Boost Mobile's correct CIK in SEC EDGAR")
print("2. Verify DISH February 2023 incident count")
print("3. Fix CIK assignments in source data")
print("4. Then: Regulatory classification decision on Boost MVNO status")
print("5. Then: Rerun full H2 analysis with corrected CIKs")
print("=" * 80)
