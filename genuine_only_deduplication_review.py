"""
GENUINE-ONLY DEDUPLICATION REVIEW
==================================

Apply only the GENUINE matching criteria:
  - Identical CAR (within 0.01pp)
  - Same or 1-day-apart dates
  - High name similarity (>0.95)

List every record that would be dropped, in readable format.
Verify they all look like DISH (obvious entity-name variants with identical market reactions)
before applying this as the final deduplication rule.
"""

import pandas as pd
import numpy as np
from difflib import SequenceMatcher
import warnings
warnings.filterwarnings('ignore')

# Load data
df = pd.read_csv('Data/processed/FINAL_DISSERTATION_DATASET_WITH_CVSS.csv')
df['breach_date'] = pd.to_datetime(df['breach_date'], errors='coerce')

print("\n" + "="*100)
print("GENUINE-ONLY DEDUPLICATION REVIEW")
print("="*100)

# Matching criteria (GENUINE pattern only)
def string_similarity(a, b):
    return SequenceMatcher(None, str(a).lower(), str(b).lower()).ratio()

genuine_pairs = []

for i, row1 in df.iterrows():
    for j, row2 in df.iterrows():
        if i >= j:
            continue

        # GENUINE criteria:
        # 1. Identical CAR (within 0.01pp)
        # 2. Same or 1-day-apart dates
        # 3. High name similarity (>0.95)

        car_match = abs(row1['car_30d'] - row2['car_30d']) < 0.01
        if not car_match:
            continue

        if pd.isna(row1['breach_date']) or pd.isna(row2['breach_date']):
            continue

        date_diff = abs((row1['breach_date'] - row2['breach_date']).days)
        if date_diff > 1:
            continue

        name_sim = string_similarity(row1['org_name'], row2['org_name'])
        if name_sim < 0.95:
            continue

        # This is a GENUINE duplicate pair
        genuine_pairs.append({
            'idx_1': i,
            'idx_2': j,
            'org_1': row1['org_name'],
            'org_2': row2['org_name'],
            'name_sim': name_sim,
            'date_1': row1['breach_date'],
            'date_2': row2['breach_date'],
            'date_diff': date_diff,
            'car_1': row1['car_30d'],
            'car_2': row2['car_30d'],
            'affected_1': row1['total_affected'],
            'affected_2': row2['total_affected'],
            'fcc_1': row1['fcc_reportable'],
            'fcc_2': row2['fcc_reportable'],
        })

print(f"\nGENUINE duplicate pairs (identical CAR, same/1d date, name sim > 0.95):")
print(f"  Total pairs detected: {len(genuine_pairs)}")

# Find records to drop (keep first of each pair)
records_to_drop = set()
for pair in genuine_pairs:
    records_to_drop.add(pair['idx_2'])  # Drop second record of each pair

records_to_drop = sorted(list(records_to_drop))

print(f"\n" + "-"*100)
print(f"RECORDS TO DROP: {len(records_to_drop)} total")
print("-"*100)

# Group by firm for readability
dropped_by_firm = {}
for idx in records_to_drop:
    firm = df.loc[idx, 'org_name']
    if firm not in dropped_by_firm:
        dropped_by_firm[firm] = []
    dropped_by_firm[firm].append(idx)

print(f"\nRecords by firm (sorted by count):")
for firm in sorted(dropped_by_firm.keys(), key=lambda x: len(dropped_by_firm[x]), reverse=True):
    indices = dropped_by_firm[firm]
    print(f"\n{firm}: {len(indices)} record(s) to drop")
    for idx in indices:
        row = df.loc[idx]
        date_str = row['breach_date'].strftime('%Y-%m-%d') if pd.notna(row['breach_date']) else 'N/A'
        print(f"  [{idx:4d}] {date_str} | CAR={row['car_30d']:7.2f}% | Affected={int(row['total_affected']):8d}")

# ============================================================================
# VERIFICATION: Show actual duplicate pairs (keep + drop) side by side
# ============================================================================

print("\n" + "="*100)
print("DETAILED PAIR VERIFICATION")
print("="*100)

print(f"\nShowing all {len(genuine_pairs)} duplicate pairs (keeping first, dropping second):")
print()

for pair_num, pair in enumerate(genuine_pairs, 1):
    print(f"Pair {pair_num}:")
    print(f"  KEEP   [{pair['idx_1']:4d}] {pair['org_1']:45s} | {pair['date_1'].strftime('%Y-%m-%d')} | CAR {pair['car_1']:7.2f}%")
    print(f"  DROP   [{pair['idx_2']:4d}] {pair['org_2']:45s} | {pair['date_2'].strftime('%Y-%m-%d')} | CAR {pair['car_2']:7.2f}%")
    print(f"  Confidence: Name sim={pair['name_sim']:.3f}, Date diff={pair['date_diff']}d, CAR diff={abs(pair['car_1']-pair['car_2']):.3f}pp")
    print()

# ============================================================================
# DATASET IMPACT SUMMARY
# ============================================================================

print("="*100)
print("DATASET IMPACT SUMMARY")
print("="*100)

df_dedup = df.drop(index=records_to_drop).reset_index(drop=True)

print(f"\nOriginal dataset:  {len(df):4d} rows")
print(f"After dedup:       {len(df_dedup):4d} rows")
print(f"Records removed:   {len(records_to_drop):4d} ({len(records_to_drop)/len(df)*100:.1f}%)")

print(f"\nFCC composition:")
print(f"  Original:  {len(df[df['fcc_reportable']==1]):4d} FCC, {len(df[df['fcc_reportable']==0]):4d} Non-FCC")
print(f"  Dedup:     {len(df_dedup[df_dedup['fcc_reportable']==1]):4d} FCC, {len(df_dedup[df_dedup['fcc_reportable']==0]):4d} Non-FCC")

print(f"\nHigh-complexity (CVSS >= 7.0) subsample:")
hc_orig = df[df['vendor_max_cvss'] >= 7.0]
hc_dedup = df_dedup[df_dedup['vendor_max_cvss'] >= 7.0]
print(f"  Original:  N={len(hc_orig):4d}, FCC={len(hc_orig[hc_orig['fcc_reportable']==1]):4d}")
print(f"  Dedup:     N={len(hc_dedup):4d}, FCC={len(hc_dedup[hc_dedup['fcc_reportable']==1]):4d}")

print(f"\nLow-complexity (CVSS < 7.0) subsample:")
lc_orig = df[df['vendor_max_cvss'] < 7.0]
lc_dedup = df_dedup[df_dedup['vendor_max_cvss'] < 7.0]
print(f"  Original:  N={len(lc_orig):4d}, FCC={len(lc_orig[lc_orig['fcc_reportable']==1]):4d}")
print(f"  Dedup:     N={len(lc_dedup):4d}, FCC={len(lc_dedup[lc_dedup['fcc_reportable']==1]):4d}")

print(f"\nMean CAR 30d:")
print(f"  Original:  {df['car_30d'].mean():7.3f}%")
print(f"  Dedup:     {df_dedup['car_30d'].mean():7.3f}%")
print(f"  Difference: {df_dedup['car_30d'].mean() - df['car_30d'].mean():7.3f}pp")

print("\n" + "="*100)
print("END OF VERIFICATION")
print("="*100)
print(f"\nNext step: Review the pair list above.")
print(f"If all pairs look like DISH (obvious entity variants with identical CAR),")
print(f"proceed with applying this deduplication and rerunning the pipeline.")
print("="*100 + "\n")
