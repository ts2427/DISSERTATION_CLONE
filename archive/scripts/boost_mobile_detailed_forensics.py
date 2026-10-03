"""
BOOST MOBILE DETAILED FORENSICS
Pull all observations under CIK 1001082 (Boost Mobile / DISH Network collision)
Examine dates, CARs, SIC codes, and regulatory classification issues
"""

import pandas as pd

print("=" * 80)
print("BOOST MOBILE / DISH NETWORK DETAILED FORENSICS")
print("CIK 1001082 - All Observations")
print("=" * 80)

df = pd.read_csv('Data/processed/FINAL_DISSERTATION_DATASET_DEDUPLICATED_ENRICHED.csv')

# Pull ALL observations under CIK 1001082
cik_1001082 = df[df['cik'] == 1001082][
    ['cik', 'org_name', 'breach_date', 'car_30d', 'sic', 'fcc_reportable',
     'firm_size_log', 'immediate_disclosure']
].copy()

print(f"\nTotal observations under CIK 1001082: {len(cik_1001082)}")
print(f"FCC reportable (fcc_reportable=True): {cik_1001082['fcc_reportable'].sum()}")

print(f"\n" + "-" * 80)
print("ALL OBSERVATIONS UNDER CIK 1001082:")
print("-" * 80)
print(cik_1001082.to_string(index=False))

print(f"\n" + "-" * 80)
print("ORGANIZATION NAME BREAKDOWN:")
print("-" * 80)
for org_name, count in cik_1001082['org_name'].value_counts().items():
    mean_car = cik_1001082[cik_1001082['org_name'] == org_name]['car_30d'].mean()
    print(f"  {org_name:<35} | {count} obs | Mean CAR: {mean_car:>7.2f}%")

print(f"\n" + "-" * 80)
print("SUMMARY STATISTICS:")
print("-" * 80)
print(f"CIK: 1001082")
print(f"SIC code: {cik_1001082['sic'].iloc[0] if len(cik_1001082) > 0 else 'N/A'}")
print(f"\nCAR Statistics:")
print(f"  Mean CAR: {cik_1001082['car_30d'].mean():.2f}%")
print(f"  Median CAR: {cik_1001082['car_30d'].median():.2f}%")
print(f"  Min CAR: {cik_1001082['car_30d'].min():.2f}%")
print(f"  Max CAR: {cik_1001082['car_30d'].max():.2f}%")
print(f"  Std Dev: {cik_1001082['car_30d'].std():.2f}%")

print(f"\nDate range: {cik_1001082['breach_date'].min()} to {cik_1001082['breach_date'].max()}")
print(f"Immediate disclosure: {cik_1001082['immediate_disclosure'].mean():.2%}")

print(f"\n" + "=" * 80)
print("REGULATORY CLASSIFICATION ISSUE")
print("=" * 80)

print(f"""
BOOST MOBILE:
  - Type: Mobile Virtual Network Operator (MVNO)
  - Definition: Resells wireless capacity on other carriers' networks
  - Owns infrastructure: NO
  - Facilities Act applicability: QUESTIONABLE
  - SIC Code in data: 4841 (Cable TV, exc. TV-only)

DISH NETWORK:
  - Type: Satellite and cable television provider
  - Owns infrastructure: YES (satellite and terrestrial)
  - Facilities Act applicability: YES (Part 64 CPNI obligations)
  - SIC Code in data: 4841 (Cable TV, exc. TV-only)

THE PROBLEM:
  Both are classified as FCC-reportable based on SIC 4841
  But Boost Mobile is an MVNO (no facilities = potentially not common carrier)
  And they are stored under the SAME CIK (1001082)

  This is a data quality issue, not a modeling issue.
  The classification decision must be made on regulatory grounds first,
  BEFORE looking at what it does to the H2 coefficient.

OBSERVATIONS:
  - 1 labeled "Boost Mobile" with CAR of +3.55%
  - 5 labeled "DISH Network" (various naming) with mean CAR of -32.34%
  - Together: mean CAR of -26.45%, which is extreme and drives H2 sensitivity

CLASSIFICATION OPTIONS:

  Option A: Keep both as FCC-reportable
    - Consistent with SIC-based classification
    - Treats both as common carriers subject to Part 64 CPNI
    - Includes Boost Mobile's atypical +3.55% return
    - Results in H2 significant at p=0.049

  Option B: Remove Boost Mobile, keep DISH Network
    - Reclassifies Boost as non-FCC (MVNO without facilities)
    - Removes Boost from treatment group
    - Leaves 5 DISH observations (mean CAR -32.34%) under CIK 1001082
    - Changes firm count from 9 to 8 or 10 depending on DISH recoding

  Option C: Separate DISH from Boost Mobile (data correction)
    - Requires finding DISH's true CIK in SEC filings
    - Allows independent classification of each
    - Most data-hygenic approach
    - Requires external regulatory research

The choice must be made on regulatory grounds.
The data shows these six observations are carrying ~1.6pp of the H2 effect.
""")

print("=" * 80)

# Save this detailed data
cik_1001082.to_csv('outputs/defense_prep/cik_1001082_detailed_forensics.csv', index=False)
print(f"\nData saved to: outputs/defense_prep/cik_1001082_detailed_forensics.csv")
