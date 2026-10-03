"""
BOOST MOBILE FORENSICS
Pull all Boost Mobile observations and examine: CARs, dates, SIC code, CIK assignment
"""

import pandas as pd

df = pd.read_csv('Data/processed/FINAL_DISSERTATION_DATASET_DEDUPLICATED_ENRICHED.csv')

# Pull all Boost Mobile observations
boost = df[df['org_name'].str.contains('Boost', case=False, na=False)][
    ['cik', 'org_name', 'breach_date', 'car_30d', 'sic', 'fcc_reportable', 'firm_size_log', 'immediate_disclosure']
].copy()

print("=" * 80)
print("BOOST MOBILE FORENSICS")
print("=" * 80)
print(f"\nTotal Boost Mobile observations: {len(boost)}")
print(f"Unique CIKs: {boost['cik'].nunique()}")
print(f"FCC reportable: {boost['fcc_reportable'].sum()}")

print("\n" + "-" * 80)
print("ALL BOOST MOBILE OBSERVATIONS:")
print("-" * 80)
print(boost.to_string(index=False))

print("\n" + "-" * 80)
print("SUMMARY STATISTICS:")
print("-" * 80)
print(f"\nCIK assignments:")
for cik, count in boost['cik'].value_counts().items():
    print(f"  CIK {cik}: {count} observations")

print(f"\nCAR Statistics:")
print(f"  Mean CAR: {boost['car_30d'].mean():.2f}%")
print(f"  Median CAR: {boost['car_30d'].median():.2f}%")
print(f"  Min CAR: {boost['car_30d'].min():.2f}%")
print(f"  Max CAR: {boost['car_30d'].max():.2f}%")
print(f"  Std Dev: {boost['car_30d'].std():.2f}%")

print(f"\nDate range: {boost['breach_date'].min()} to {boost['breach_date'].max()}")

print(f"\nSIC codes:")
for sic, count in boost['sic'].value_counts().items():
    print(f"  SIC {sic}: {count} observations")

print(f"\nFCC reportable: {boost['fcc_reportable'].value_counts().to_dict()}")

print(f"\nImmediate disclosure: {boost['immediate_disclosure'].value_counts().to_dict()}")

# Save to CSV for reference
boost.to_csv('outputs/defense_prep/boost_mobile_all_observations.csv', index=False)

print("\n" + "=" * 80)
print("REGULATORY QUESTION:")
print("=" * 80)
print("\nBoost Mobile is an MVNO (Mobile Virtual Network Operator) that resells capacity.")
print("It does NOT own network infrastructure or own part 64 facilities.")
print(f"\nSIC Code in data: {boost['sic'].iloc[0] if len(boost) > 0 else 'N/A'}")
print("\nFCC Part 64 CPNI obligations apply to 'common carriers' that own facilities.")
print("Whether Boost Mobile qualifies is a genuine regulatory question, not a coding issue.")
print("\nCurrent classification (fcc_reportable): Based on SIC code matching")
print(f"  - SIC 4813 (Telephone): YES")
print(f"  - SIC 4841 (Cable): YES")
print(f"  - SIC 4899 (VoIP/other telecom): YES")
print(f"\nBoost Mobile's SIC: {boost['sic'].iloc[0] if len(boost) > 0 else 'N/A'}")

print("\n" + "=" * 80)
print("DATA SAVED TO: outputs/defense_prep/boost_mobile_all_observations.csv")
print("=" * 80)
