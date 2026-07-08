"""
APPLY GENUINE-ONLY DEDUPLICATION
=================================

Create cleaned master dataset by keeping one record per firm-breach-date cluster.

Logic:
- For each unique (org_name, breach_date) combination, keep the FIRST record
- Drop all subsequent duplicates from the same cluster
- This preserves genuine distinct events while collapsing within-event duplicates

Output: FINAL_DISSERTATION_DATASET_DEDUPLICATED.csv
  Original: 1,054 rows
  Cleaned: ~797 rows (keeping 1 per cluster)
"""

import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# Load data
df = pd.read_csv('Data/processed/FINAL_DISSERTATION_DATASET_WITH_CVSS.csv')

print("\n" + "="*100)
print("APPLYING GENUINE-ONLY DEDUPLICATION")
print("="*100)

# Convert to datetime
df['breach_date'] = pd.to_datetime(df['breach_date'], errors='coerce')

print(f"\nOriginal dataset: {len(df)} rows")

# Create deduplication key: (org_name, breach_date)
# Keep first occurrence of each unique key, drop rest
df_dedup = df.drop_duplicates(subset=['org_name', 'breach_date'], keep='first')

print(f"Deduplicated dataset: {len(df_dedup)} rows")
print(f"Records removed: {len(df) - len(df_dedup)} ({(len(df) - len(df_dedup)) / len(df) * 100:.1f}%)")

# Save deduplicated dataset
output_path = 'Data/processed/FINAL_DISSERTATION_DATASET_DEDUPLICATED.csv'
df_dedup.to_csv(output_path, index=False)

print(f"\nCleaned dataset saved: {output_path}")

# Verify composition
print(f"\nFCC composition:")
print(f"  Original:  {len(df[df['fcc_reportable']==1]):4d} FCC, {len(df[df['fcc_reportable']==0]):4d} Non-FCC")
print(f"  Dedup:     {len(df_dedup[df_dedup['fcc_reportable']==1]):4d} FCC, {len(df_dedup[df_dedup['fcc_reportable']==0]):4d} Non-FCC")

print(f"\nHigh-complexity subsample (CVSS >= 7.0):")
hc_orig = df[df['vendor_max_cvss'] >= 7.0]
hc_dedup = df_dedup[df_dedup['vendor_max_cvss'] >= 7.0]
print(f"  Original:  N={len(hc_orig):4d}, FCC={len(hc_orig[hc_orig['fcc_reportable']==1]):4d}")
print(f"  Dedup:     N={len(hc_dedup):4d}, FCC={len(hc_dedup[hc_dedup['fcc_reportable']==1]):4d}")

print(f"\nLow-complexity subsample (CVSS < 7.0):")
lc_orig = df[df['vendor_max_cvss'] < 7.0]
lc_dedup = df_dedup[df_dedup['vendor_max_cvss'] < 7.0]
print(f"  Original:  N={len(lc_orig):4d}, FCC={len(lc_orig[lc_orig['fcc_reportable']==1]):4d}")
print(f"  Dedup:     N={len(lc_dedup):4d}, FCC={len(lc_dedup[lc_dedup['fcc_reportable']==1]):4d}")

print(f"\nMean CAR 30d:")
print(f"  Original:  {df['car_30d'].mean():7.3f}%")
print(f"  Dedup:     {df_dedup['car_30d'].mean():7.3f}%")

print("\n" + "="*100)
print("DEDUPLICATION COMPLETE")
print("="*100 + "\n")
