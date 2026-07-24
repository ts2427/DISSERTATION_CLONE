"""
DIAGNOSTIC: TOP FIVE FIRMS BY NEAR-DUPLICATE PAIR COUNT
Extract all rows and classify by CAR pattern
"""

import pandas as pd
import numpy as np

# Load data
df = pd.read_csv('Data/processed/FINAL_DISSERTATION_DATASET_DEDUPLICATED_ENRICHED.csv')
df['breach_date'] = pd.to_datetime(df['breach_date'])
near_dups = pd.read_csv('outputs/defense_prep/near_duplicate_pairs_7day.csv')

# Top 5 CIKs by pair count
top_5_ciks = [896878, 732717, 1136893, 1283699, 713676]

# Map CIK to firm name
firm_names = {
    896878: "Intuit Inc.",
    732717: "AT&T Services, Inc.",
    1136893: "Fidelity National Information Services, Inc.",
    1283699: "Sprint / T-Mobile",
    713676: "Financial Services (multiple entities)"
}

print("=" * 100)
print("DIAGNOSTIC: TOP 5 FIRMS BY NEAR-DUPLICATE PAIR COUNT")
print("=" * 100)
print("\nDiagnostic approach: Identical CARs = duplicate filing of one incident; Different CARs = separate incidents\n")

for rank, cik in enumerate(top_5_ciks, 1):
    firm_name = firm_names[cik]
    cik_data = df[df['cik'] == cik].sort_values('breach_date').copy()
    cik_pairs = near_dups[near_dups['cik'] == cik]

    print("\n" + "=" * 100)
    print(f"RANK {rank}: CIK {cik} | {firm_name}")
    print(f"Total near-duplicate pairs: {len(cik_pairs)}")
    print(f"Total observations for this CIK: {len(cik_data)}")
    print("=" * 100)

    # Show all rows with key fields
    print(f"\nALL {len(cik_data)} OBSERVATIONS (sorted by breach_date):")
    print("-" * 100)
    print(f"{'Date':<12} {'Org Name':<40} {'CAR (30d)':<12} {'Notes':<20}")
    print("-" * 100)

    display_cols = cik_data[['breach_date', 'org_name', 'car_30d']].copy()
    display_cols['breach_date'] = display_cols['breach_date'].dt.strftime('%Y-%m-%d')

    for idx, (_, row) in enumerate(display_cols.iterrows(), 1):
        date_str = row['breach_date']
        org = row['org_name'][:38]
        car = row['car_30d']

        # Mark if this row is part of a pair
        in_pair = False
        pair_info = ""
        for _, pair_row in cik_pairs.iterrows():
            if pd.to_datetime(pair_row['breach_date_1']).strftime('%Y-%m-%d') == date_str:
                in_pair = True
                gap = int(pair_row['days_apart'])
                car2 = pair_row['car_2']
                pair_info = f"→{gap}d, CAR₂={car2:.2f}%"
                break

        marker = "**" if in_pair else "  "
        print(f"{marker} {date_str:<12} {org:<40} {car:>11.2f}% {pair_info:<20}")

    # Show pair details
    print(f"\nNEAR-DUPLICATE PAIRS ({len(cik_pairs)} pairs):")
    print("-" * 100)

    for idx, (_, pair_row) in enumerate(cik_pairs.iterrows(), 1):
        date1 = pd.to_datetime(pair_row['breach_date_1']).strftime('%Y-%m-%d')
        date2 = pd.to_datetime(pair_row['breach_date_2']).strftime('%Y-%m-%d')
        gap = int(pair_row['days_apart'])
        car1 = pair_row['car_1']
        car2 = pair_row['car_2']
        org1 = pair_row['org_name_1'][:35]
        org2 = pair_row['org_name_2'][:35]

        car_diff = abs(car2 - car1)
        same_car = "IDENTICAL" if car_diff < 0.01 else f"DIFFERENT (Δ={car_diff:.2f}pp)"

        print(f"\nPair {idx}: {gap}-day gap | CAR: {same_car}")
        print(f"  Date1: {date1} | Org: {org1}")
        print(f"  Date2: {date2} | Org: {org2}")
        print(f"  CAR1: {car1:.2f}% | CAR2: {car2:.2f}%")

print("\n" + "=" * 100)
print("CLASSIFICATION GUIDE")
print("=" * 100)
print("""
IDENTICAL CARs (Δ < 0.5%):
  → Very likely the same incident reported/disclosed on different dates
  → Example: Initial disclosure on Feb 22, regulatory filing on Feb 23 (DISH ransomware)
  → Action: Dedup as one observation

SIMILAR CARs (0.5% ≤ Δ < 2%):
  → Likely same incident, but slight market movement between dates
  → Example: Disclosure on Feb 22, updated filing on Feb 23 with additional detail
  → Action: Likely dedup, but review context

DIFFERENT CARs (Δ ≥ 2%):
  → Likely genuinely separate incidents (market reaction was separate)
  → Example: AT&T incident on June 5 vs separate incident on June 11
  → Action: Keep both, these are separate breaches

CRITICAL OBSERVATION:
  - Intuit with 29 pairs: If most are identical CAR, this is a massive filing-duplication problem
  - AT&T with 7 pairs: If spread across a decade with different CARs, likely separate incidents
  - Sprint/T-Mobile merger handling: Some pairs may be pre/post-merger entity name changes
""")

print("\n" + "=" * 100)
print("OUTPUT FILE LOCATION")
print("=" * 100)
print("\nThis diagnostic should be reviewed manually to classify pair types.")
print("Once classified, the dedup rule can be narrowed or widened appropriately.")
