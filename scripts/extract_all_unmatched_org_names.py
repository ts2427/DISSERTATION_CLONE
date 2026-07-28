"""
Extract ALL unmatched org_names (not just ambiguous ones)
"""

import pandas as pd
from pathlib import Path

print("=" * 100)
print("EXTRACT ALL UNMATCHED ORG_NAMES FROM FULL DATASET")
print("=" * 100)

# Load full dataset
prc_path = Path("Data/processed/FINAL_DISSERTATION_DATASET_DEDUPLICATED_ENRICHED.csv")
df_prc = pd.read_csv(prc_path)

# Get all unique org_names
all_org_names = sorted(df_prc['org_name'].unique())
print(f"\nTotal unique org_names in dataset: {len(all_org_names)}")

# Load resolution summary (only includes matched org_names)
summary_path = Path("outputs/full_dataset_resolution_summary.csv")
df_summary = pd.read_csv(summary_path)
matched_org_names = set(df_summary['org_name'].unique())

print(f"Matched org_names in summary: {len(matched_org_names)}")

# Find unmatched (those NOT in the summary)
unmatched_org_names = sorted([org for org in all_org_names if org not in matched_org_names])
print(f"Unmatched org_names: {len(unmatched_org_names)}")

# Get record counts
record_counts = {}
for org_name in unmatched_org_names:
    count = len(df_prc[df_prc['org_name'] == org_name])
    record_counts[org_name] = count

total_unmatched_records = sum(record_counts.values())
print(f"Total unmatched records: {total_unmatched_records} ({total_unmatched_records/len(df_prc)*100:.1f}%)")

# Sort by record count
unmatched_sorted = sorted(
    [(org, record_counts[org]) for org in unmatched_org_names],
    key=lambda x: x[1],
    reverse=True
)

print(f"\nTop 30 unmatched org_names by record count:")
for idx, (org_name, count) in enumerate(unmatched_sorted[:30], 1):
    print(f"  {idx:2d}. {org_name[:60]:60s} ({count:3d} records)")

if len(unmatched_sorted) > 30:
    print(f"  ... and {len(unmatched_sorted) - 30} more")

# Save list
unmatched_list = pd.DataFrame([
    {'org_name': org, 'record_count': count}
    for org, count in unmatched_sorted
])

output_path = Path("outputs/all_unmatched_org_names.csv")
unmatched_list.to_csv(output_path, index=False)

print(f"\nSaved: {output_path}")
print(f"Total org_names to resolve: {len(unmatched_sorted)}")
print(f"Total records to fix: {total_unmatched_records}")
