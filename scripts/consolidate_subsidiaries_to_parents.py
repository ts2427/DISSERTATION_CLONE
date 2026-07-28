"""
Consolidate subsidiary/variant names to parent companies for better CRSP coverage
"""

import pandas as pd
import numpy as np
from pathlib import Path

print("=" * 100)
print("CONSOLIDATE SUBSIDIARIES TO PARENT COMPANIES")
print("=" * 100)

# Load dataset
df = pd.read_csv('Data/processed/FINAL_DISSERTATION_DATASET_CORRECTED_WITH_RETURNS.csv')

# Define canonical parent company for each subsidiary/variant
# Format: canonical_name -> [list of variant names/subsidiaries]
subsidiary_mappings = {
    'T-Mobile': [
        'T-Mobile USA Inc.',
        'T-Mobile USA, Inc.',
        'T-Mobile USA',
        'T-Mobile, USA',
        'T-Mobile US, Inc.',
        'Sprint Nextel',
        'Sprint',
        'MetroPCS',
    ],
    'AT&T': [
        'AT&T Services',
        'AT&T Services Inc.',
        'AT&T Services, Inc.',
        'AT&T Inc',
        'AT&T Inc.',
        'AT&T, Inc.',
        'Cricket Wireless',
        'DirecTV',
    ],
    'Hewlett Packard Enterprise Company': [
        'Hewlett-Packard Company',
        'Hewlett Packard Company',
        'HP Enterprise Services',
        'HP Enterprise Services LLC',
        'HP Enterprise Services, LLC',
        'HP Inc.',
        'HP Inc',
        'Hewlett Packard',
    ],
    'Sony Interactive Entertainment': [
        'Sony Pictures Entertainment Inc.',
        'Sony Pictures Entertainment, Inc.',
        'Sony Pictures Entertainment Inc',
        'Sony Pictures',
        'Sony Pictures Entertainment',
        'Sony Online Entertainment',
        'Sony Online Entertainment LLC',
        'Sony Electronics Inc.',
        'Sony Corporation of America',
        'Sony Network Entertainment America Inc',
    ],
    'Time Warner Inc.': [
        'Warner Bros. Distributing Inc.',
        'Warner Music Group',
        'Home Box Office, Inc.',
        'HBO',
        'Turner Broadcasting',
    ],
    'Comcast': [
        'Comcast Cable Communications LLC',
        'Comcast Cable Communications, Inc.',
        'Comcast Cable Communications Inc.',
        'NBCUniversal',
        'Xfinity',
    ],
    'Verizon': [
        'Verizon Communications',
        'Verizon Communications Inc',
        'Verizon Communications Inc.',
        'Verizon Communications, Inc.',
        'Verizon Media',
        'Oath',
        'Yahoo (formerly owned)',
    ],
}

print("\nApplying consolidation mappings...")

# For each record, check if it's a subsidiary variant and map to parent
consolidation_count = 0
permno_recovered = 0
car_recovered = 0

for idx, row in df.iterrows():
    org_name = row['org_name']

    # Check if this org_name is a subsidiary variant
    for parent, subsidiaries in subsidiary_mappings.items():
        if org_name in subsidiaries and org_name != parent:
            # Find the parent record's PERMNO
            parent_rec = df[df['org_name'] == parent].iloc[0] if len(df[df['org_name'] == parent]) > 0 else None

            if parent_rec is not None and pd.notna(parent_rec['permno']):
                # Only override if original had no PERMNO or CAR
                if pd.isna(row['permno']) or pd.isna(row['car_30d']):
                    # Map to parent's PERMNO
                    df.at[idx, 'org_name_original'] = org_name
                    df.at[idx, 'org_name'] = parent
                    df.at[idx, 'permno_original'] = row['permno']
                    df.at[idx, 'permno'] = parent_rec['permno']

                    # Copy parent's CAR values if this record doesn't have them
                    if pd.isna(row['car_30d']) and pd.notna(parent_rec['car_30d']):
                        # NOTE: This is a simplification - ideally we'd recalc
                        # For now, mark as consolidated
                        pass

                    consolidation_count += 1
                    if pd.isna(row['permno']):
                        permno_recovered += 1
                    if pd.isna(row['car_30d']):
                        car_recovered += 1
            break

print(f"\n  Records consolidated: {consolidation_count}")
print(f"  PERMNO recovered: {permno_recovered}")

# Check improvement in CRSP coverage
print("\n" + "=" * 100)
print("COVERAGE IMPROVEMENT")
print("=" * 100)

before_permno = len(df[df['permno'].notna()])
before_car = len(df[df['car_30d'].notna()])

print(f"\nBefore consolidation (from corrected dataset):")
print(f"  PERMNO coverage: 706 ({706/779*100:.1f}%)")
print(f"  CAR_30d coverage: 669 ({669/779*100:.1f}%)")

print(f"\nAfter consolidation:")
print(f"  PERMNO coverage: {len(df[df['permno'].notna()])} ({len(df[df['permno'].notna()])/len(df)*100:.1f}%)")
print(f"  CAR_30d coverage: {len(df[df['car_30d'].notna()])} ({len(df[df['car_30d'].notna()])/len(df)*100:.1f}%)")

# Show which records were consolidated
consolidated = df[df['org_name_original'].notna()]
if len(consolidated) > 0:
    print(f"\n\nRecords consolidated to parents:")
    for _, row in consolidated.iterrows():
        print(f"  {row['org_name_original']:50s} -> {row['org_name']:50s}")

# Save consolidated dataset
output_path = Path("Data/processed/FINAL_DISSERTATION_DATASET_CORRECTED_CONSOLIDATED.csv")
df.to_csv(output_path, index=False)

print(f"\nConsolidated dataset saved: {output_path}")
print("=" * 100)
