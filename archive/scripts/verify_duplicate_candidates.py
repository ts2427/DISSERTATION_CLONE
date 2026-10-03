"""
VERIFY DUPLICATE CANDIDATES
Check incident scope, record counts, breach type for the 4 candidate pairs
"""

import pandas as pd

df = pd.read_csv('Data/processed/FINAL_DISSERTATION_DATASET_DEDUPLICATED_ENRICHED.csv')
df['breach_date'] = pd.to_datetime(df['breach_date'])

print("=" * 100)
print("VERIFICATION OF DUPLICATE CANDIDATES")
print("=" * 100)
print("\nChecking: incident scope, record_count, breach_type for each pair")
print("If incident details differ materially → likely separate events, not duplicates\n")

# Four candidates
candidates = [
    {
        'name': 'Intuit 2019-03-21/26',
        'cik': 896878,
        'dates': ['2019-03-21', '2019-03-26']
    },
    {
        'name': 'Corebridge 2023-05-29/30',
        'cik': 713676,
        'dates': ['2023-05-29', '2023-05-30']
    },
    {
        'name': 'Fidelity 2023-10-04/06',
        'cik': 1136893,
        'dates': ['2023-10-04', '2023-10-06']
    },
    {
        'name': 'Sprint/T-Mobile 2021-08-17/18',
        'cik': 1283699,
        'dates': ['2021-08-17', '2021-08-18']
    }
]

for idx, candidate in enumerate(candidates, 1):
    print("=" * 100)
    print(f"CANDIDATE {idx}: {candidate['name']}")
    print("=" * 100)

    cik = candidate['cik']
    dates = pd.to_datetime(candidate['dates'])

    # Get both rows
    for date in dates:
        row_data = df[(df['cik'] == cik) & (df['breach_date'] == date)]

        if len(row_data) == 0:
            print(f"\n✗ No row found for {date.strftime('%Y-%m-%d')}")
            continue

        for _, row in row_data.iterrows():
            print(f"\nDate: {row['breach_date']}")
            print(f"Org Name: {row['org_name']}")
            print(f"CAR (30d): {row['car_30d']:.2f}%")
            print(f"Breach Type: {row.get('breach_type', 'N/A')}")
            print(f"Record Count: {row.get('record_count', 'N/A')}")
            print(f"Affected Individuals: {row.get('individuals_affected', 'N/A')}")
            print(f"Records Compromised: {row.get('records_compromised', 'N/A')}")
            print(f"Breach Description: {row.get('breach_description', 'N/A')}")
            print(f"Health Breach: {row.get('health_breach', 'N/A')}")
            print(f"Immediate Disclosure: {row.get('immediate_disclosure', 'N/A')}")

print("\n" + "=" * 100)
print("ANALYSIS")
print("=" * 100)
print("""
For each pair:
  - If record_count / affected individuals are identical or near-identical (within 5%)
  - AND breach_type is identical
  - AND breach descriptions are clearly the same incident
    → This is almost certainly a DUPLICATE (same incident, filed twice)

  - If record_count differs significantly (>5%) OR breach descriptions suggest different scope
    → This is likely TWO SEPARATE INCIDENTS at same firm within days (keep both)
""")
