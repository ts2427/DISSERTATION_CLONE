"""
MASTER DUPLICATE AUDIT & RESOLUTION
====================================

Comprehensive audit of all flagged duplicate breach records across the dataset.
Determines which flagged pairs are genuine duplicates (same event, different entity names)
vs. coincidental metadata overlap.

Output:
1. Detailed audit report (flagged pairs, deduplication decision, reasoning)
2. Cleaned master dataset with duplicates removed (keeping first record per unique breach)
3. Deduplication summary (before/after sample sizes, affected firms, breach counts)
"""

import pandas as pd
import numpy as np
from difflib import SequenceMatcher
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Load data
df = pd.read_csv('Data/processed/FINAL_DISSERTATION_DATASET_WITH_CVSS.csv')

print("\n" + "="*80)
print("MASTER DUPLICATE AUDIT: ALL FLAGGED DUPLICATE PAIRS")
print("="*80)

# ============================================================================
# SECTION 1: IDENTIFY POTENTIAL DUPLICATES
# ============================================================================

print("\n" + "-"*80)
print("SECTION 1: DUPLICATE DETECTION")
print("-"*80)

# Convert dates to datetime
df['breach_date'] = pd.to_datetime(df['breach_date'], errors='coerce')

# Function to check string similarity
def string_similarity(a, b):
    """Calculate similarity ratio between two strings (0-1)"""
    return SequenceMatcher(None, str(a).lower(), str(b).lower()).ratio()

# Find potential duplicates by org_name similarity + date proximity
duplicates_found = []

for i, row1 in df.iterrows():
    for j, row2 in df.iterrows():
        if i >= j:  # Only check each pair once
            continue

        # Check org_name similarity (threshold: 0.85 = very similar but allows for spelling variations)
        name_sim = string_similarity(row1['org_name'], row2['org_name'])

        if name_sim < 0.85:
            continue

        # Check date proximity (within 2 days)
        if pd.notna(row1['breach_date']) and pd.notna(row2['breach_date']):
            date_diff = abs((row1['breach_date'] - row2['breach_date']).days)
            if date_diff > 2:
                continue
        else:
            # If dates are missing, can't confirm, skip
            continue

        # This is a potential duplicate pair
        duplicates_found.append({
            'record_1_idx': i,
            'record_2_idx': j,
            'org_name_1': row1['org_name'],
            'org_name_2': row2['org_name'],
            'name_similarity': name_sim,
            'date_1': row1['breach_date'],
            'date_2': row2['breach_date'],
            'date_diff_days': date_diff,
            'car_1': row1['car_30d'],
            'car_2': row2['car_30d'],
            'vendor_1': row1['nvd_vendor'],
            'vendor_2': row2['nvd_vendor'],
            'affected_1': row1['total_affected'],
            'affected_2': row2['total_affected'],
        })

print(f"\nPotential duplicate pairs detected: {len(duplicates_found)}")

# ============================================================================
# SECTION 2: DETAILED AUDIT BY FIRM
# ============================================================================

print("\n" + "-"*80)
print("SECTION 2: DUPLICATE AUDIT BY FIRM")
print("-"*80)

# Group duplicates by firm
firm_groups = {}
for dup in duplicates_found:
    firm_key = dup['org_name_1'].split()[0]  # First word as firm identifier
    if firm_key not in firm_groups:
        firm_groups[firm_key] = []
    firm_groups[firm_key].append(dup)

print(f"\nFirms with detected duplicate pairs:")
for firm, pairs in sorted(firm_groups.items(), key=lambda x: len(x[1]), reverse=True):
    print(f"  {firm:20s}: {len(pairs):2d} duplicate pairs")

# Detailed report per firm
for firm in sorted(firm_groups.keys()):
    pairs = firm_groups[firm]

    print(f"\n" + "="*80)
    print(f"{firm} — {len(pairs)} Duplicate Pair(s)")
    print("="*80)

    # Get all records for this firm
    firm_records = df[df['org_name'].str.contains(firm, case=False, na=False)].copy()
    print(f"\nTotal {firm} records in dataset: {len(firm_records)}")

    # Show all records sorted by date
    print(f"\nAll {firm} records (sorted by date):")
    firm_records = firm_records.sort_values('breach_date')
    for idx, (rec_idx, row) in enumerate(firm_records.iterrows(), 1):
        date_str = row['breach_date'].strftime('%Y-%m-%d') if pd.notna(row['breach_date']) else 'N/A'
        print(f"  {idx}. [{rec_idx:4d}] {row['org_name']:40s} | {date_str} | CAR={row['car_30d']:7.2f}% | " +
              f"Vendor={row['nvd_vendor']}")

    # Show flagged pairs
    print(f"\nFlagged duplicate pairs:")
    for pair_idx, pair in enumerate(pairs, 1):
        print(f"\n  Pair {pair_idx}:")
        print(f"    Record 1 [{pair['record_1_idx']:4d}]: {pair['org_name_1']:40s} | {pair['date_1']} | CAR={pair['car_1']:7.2f}%")
        print(f"    Record 2 [{pair['record_2_idx']:4d}]: {pair['org_name_2']:40s} | {pair['date_2']} | CAR={pair['car_2']:7.2f}%")
        print(f"    Name similarity: {pair['name_similarity']:.3f} | Date diff: {pair['date_diff_days']} days")
        print(f"    Same vendor: {pair['vendor_1'] == pair['vendor_2']} ({pair['vendor_1']})")
        print(f"    Same affected count: {pair['affected_1'] == pair['affected_2']} ({int(pair['affected_1'])} vs {int(pair['affected_2'])})")

        # Deduplication decision
        if pair['date_diff_days'] == 0 and pair['name_similarity'] > 0.95:
            print(f"    [GENUINE DUPLICATE] Same date, very similar names - KEEP FIRST, DROP SECOND")
            dup_type = "GENUINE"
        elif pair['date_diff_days'] <= 1 and pair['vendor_1'] == pair['vendor_2'] and pair['affected_1'] == pair['affected_2']:
            print(f"    [LIKELY DUPLICATE] Date within 1 day, same vendor, same affected count - KEEP FIRST, DROP SECOND")
            dup_type = "LIKELY"
        else:
            print(f"    [UNCERTAIN] Multiple factors, manual review needed")
            dup_type = "UNCERTAIN"

# ============================================================================
# SECTION 3: GLOBAL DEDUPLICATION LOGIC
# ============================================================================

print("\n" + "="*80)
print("SECTION 3: GLOBAL DEDUPLICATION RESOLUTION")
print("="*80)

# Strategy: For records with identical breach_date AND org_name similarity > 0.95,
# keep only the first record (earliest entry in the dataset)

print(f"\nDeduplication strategy:")
print(f"  Records with identical breach_date AND org_name similarity > 0.95:")
print(f"    - Keep first record, drop subsequent duplicates")
print(f"  Records with date_diff <= 1 day AND same vendor AND same affected count:")
print(f"    - Keep first record, drop subsequent duplicates")
print(f"  All other flagged pairs:")
print(f"    - Keep all records (treat as separate events)")

# Create deduplication key: (breach_date, org_name_normalized)
df['org_name_norm'] = df['org_name'].str.lower().str.strip()

# Find records to drop
records_to_drop = set()

for dup in duplicates_found:
    date_1 = df.loc[dup['record_1_idx'], 'breach_date']
    date_2 = df.loc[dup['record_2_idx'], 'breach_date']

    # Decision logic
    keep_idx = dup['record_1_idx']
    drop_idx = dup['record_2_idx']

    # Check for genuine duplicate (same date, high name similarity)
    if pd.notna(date_1) and pd.notna(date_2):
        if date_1 == date_2 and dup['name_similarity'] > 0.95:
            records_to_drop.add(drop_idx)
            decision = "GENUINE DUPLICATE (same date, high name similarity)"
        elif dup['date_diff_days'] <= 1 and dup['vendor_1'] == dup['vendor_2'] and dup['affected_1'] == dup['affected_2']:
            records_to_drop.add(drop_idx)
            decision = "LIKELY DUPLICATE (date within 1 day, same vendor, same affected)"
        else:
            decision = "UNCERTAIN - keeping both"

# ============================================================================
# SECTION 4: PRODUCE CLEANED DATASET
# ============================================================================

print("\n" + "-"*80)
print("SECTION 4: CLEANED DATASET PRODUCTION")
print("-"*80)

df_cleaned = df.drop(index=list(records_to_drop)).reset_index(drop=True)

print(f"\nDeduplication summary:")
print(f"  Original dataset: {len(df):5d} rows")
print(f"  Records dropped: {len(records_to_drop):5d} rows")
print(f"  Cleaned dataset: {len(df_cleaned):5d} rows")
print(f"  Reduction: {len(records_to_drop) / len(df) * 100:.2f}%")

# Firm-level summary
print(f"\nRecords removed by firm:")
for drop_idx in sorted(records_to_drop):
    firm = df.loc[drop_idx, 'org_name']
    date = df.loc[drop_idx, 'breach_date']
    print(f"  [{drop_idx:4d}] {firm:40s} | {date}")

# Save cleaned dataset
output_path = 'Data/processed/FINAL_DISSERTATION_DATASET_DEDUPLICATED.csv'
df_cleaned.to_csv(output_path, index=False)
print(f"\nCleaned dataset saved: {output_path}")

# ============================================================================
# SECTION 5: IMPACT ON KEY STATISTICS
# ============================================================================

print("\n" + "="*80)
print("SECTION 5: IMPACT ON KEY STATISTICS")
print("="*80)

print(f"\nDataset composition:")
print(f"  Original:  N={len(df):4d}, FCC={len(df[df['fcc_reportable']==1]):4d}, Non-FCC={len(df[df['fcc_reportable']==0]):4d}")
print(f"  Cleaned:   N={len(df_cleaned):4d}, FCC={len(df_cleaned[df_cleaned['fcc_reportable']==1]):4d}, " +
      f"Non-FCC={len(df_cleaned[df_cleaned['fcc_reportable']==0]):4d}")

print(f"\nMean CAR 30d impact:")
print(f"  Original:  {df['car_30d'].mean():7.3f}%")
print(f"  Cleaned:   {df_cleaned['car_30d'].mean():7.3f}%")
print(f"  Difference: {df_cleaned['car_30d'].mean() - df['car_30d'].mean():7.3f}pp")

print(f"\nSCM-relevant (high-complexity) subsample:")
hc_orig = df[df['has_high_complexity'] == 1]
hc_clean = df_cleaned[df_cleaned['has_high_complexity'] == 1]
print(f"  Original:  N={len(hc_orig):4d}, FCC={len(hc_orig[hc_orig['fcc_reportable']==1]):4d}")
print(f"  Cleaned:   N={len(hc_clean):4d}, FCC={len(hc_clean[hc_clean['fcc_reportable']==1]):4d}")

print("\n" + "="*80)
print("END OF DUPLICATE AUDIT")
print("="*80)
print(f"\nNEXT STEP: Rerun full pipeline with cleaned dataset")
print(f"  Input file: {output_path}")
print(f"\n")
