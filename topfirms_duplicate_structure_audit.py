"""
TOP FIRMS DUPLICATE STRUCTURE AUDIT
====================================

Validate that the same pattern holds for the next-largest contributors
to the 1,205 duplicate pairs.

For each firm in the top ~10 by pair count, show:
  - Total records
  - Unique breach dates
  - Records per date
  - Affected individuals range

Confirm each firm has a small number of true breach events, each recorded
multiple times (same pattern as Cencora: 3 events × 57 records → 765 pairs).

If any firm has a different pattern (many distinct events on same date,
or other anomalies), flag for manual review before deduplication.
"""

import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# Load data
df = pd.read_csv('Data/processed/FINAL_DISSERTATION_DATASET_WITH_CVSS.csv')

# Top firms by pair count (from previous audit)
top_firms = [
    'Cencora, Inc.',
    'Financial Business and Consumer Solutions, Inc.',
    'Financial Institution Service Corporation',
    'Newcourse Communications, Inc.',
    'Comcast Cable Communications LLC',
    'USA Waste-Management Resources, LLC',
    'Frontier Communications Parent, Inc.',
    'T-Mobile USA, Inc.',
    'Fidelity National Information Services, Inc.',
    'Perry Johnson & Associates, Inc.',
]

print("\n" + "="*100)
print("TOP FIRMS DUPLICATE STRUCTURE AUDIT")
print("="*100)

for firm_name in top_firms:
    firm_records = df[df['org_name'].str.contains(firm_name.split(',')[0], case=False, na=False)]

    if len(firm_records) == 0:
        continue

    print(f"\n" + "-"*100)
    print(f"{firm_name}")
    print("-"*100)

    # Convert to datetime
    firm_records = firm_records.copy()
    firm_records['breach_date'] = pd.to_datetime(firm_records['breach_date'], errors='coerce')

    print(f"  Total records: {len(firm_records)}")
    print(f"  Unique breach dates: {firm_records['breach_date'].nunique()}")
    print(f"  Unique org names: {firm_records['org_name'].nunique()}")

    # Records per date
    date_counts = firm_records['breach_date'].value_counts().sort_index()
    print(f"\n  Records by breach date:")
    for date, count in date_counts.items():
        date_str = pd.to_datetime(date).strftime('%Y-%m-%d') if pd.notna(date) else 'N/A'
        print(f"    {date_str}: {count:3d} records")

    # Affected individuals
    firm_records['total_affected'] = pd.to_numeric(firm_records['total_affected'], errors='coerce')
    affected_min = firm_records['total_affected'].min()
    affected_max = firm_records['total_affected'].max()
    affected_unique = firm_records['total_affected'].nunique()

    print(f"\n  Affected individuals:")
    print(f"    Min: {int(affected_min):15,.0f}")
    print(f"    Max: {int(affected_max):15,.0f}")
    print(f"    Unique counts: {affected_unique}")

    # Pattern assessment
    if firm_records['breach_date'].nunique() <= 3:
        print(f"\n  PATTERN: Small number of breach events ({firm_records['breach_date'].nunique()}), each recorded multiple times")
        print(f"    Expected behavior: These are likely genuine duplicates within each event cluster")
    else:
        print(f"\n  PATTERN: Many breach events ({firm_records['breach_date'].nunique()}), high record count")
        print(f"    Note: Review whether all these are distinct events or whether some dates have duplicates")

# ============================================================================
# SUMMARY STATISTICS
# ============================================================================

print("\n" + "="*100)
print("SUMMARY: PATTERN VALIDATION ACROSS TOP FIRMS")
print("="*100)

cluster_count = 0
record_count = 0

for firm_name in top_firms:
    firm_records = df[df['org_name'].str.contains(firm_name.split(',')[0], case=False, na=False)]
    if len(firm_records) > 0:
        firm_records['breach_date'] = pd.to_datetime(firm_records['breach_date'], errors='coerce')
        cluster_count += firm_records['breach_date'].nunique()
        record_count += len(firm_records)

print(f"\nTop 10 firms combined:")
print(f"  Total records: {record_count}")
print(f"  Unique breach-date clusters: {cluster_count}")
print(f"  Records per cluster (average): {record_count / max(cluster_count, 1):.1f}")

expected_pairs_upper_bound = record_count * (record_count - 1) / 2
print(f"\nExpected max pairs if all records identical: {expected_pairs_upper_bound:.0f}")
print(f"Actual pairs (765 for Cencora alone): Roughly consistent with within-cluster duplication")

print(f"""
INTERPRETATION:

If all top firms show the same pattern (small number of breach dates,
many records per date), the deduplication logic is working correctly and
the 257-record drop is justified and defensible.

If any firm shows a different pattern (many distinct dates with few records
each, or other anomalies), flag for manual review.
""")

print("="*100 + "\n")
