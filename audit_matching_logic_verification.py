"""
VERIFY DUPLICATE MATCHING LOGIC
================================

Inspect the criteria used to mark records as duplicates.
Show 20 sample "duplicate" pairs to check if they look like genuine duplicates
(identical CAR, same date, entity-name variants) or false positives
(legitimately different breaches caught by overly-loose matching).

Original validation check used:
  - Exact org_name match
  - Exact breach_date match
  - Exact total_affected match
  → Flagged ~44 duplicates

This audit used:
  - Fuzzy org_name match (similarity > 0.85)
  - Date proximity (within 2 days)
  → Flagged 1,349 pairs, dropped 282 records

Question: Are the 282 dropped records genuine duplicates (like DISH) or false positives?
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
print("DUPLICATE MATCHING LOGIC VERIFICATION")
print("="*100)

# Recreate the matching logic from master_duplicate_audit.py
def string_similarity(a, b):
    """Calculate similarity ratio between two strings (0-1)"""
    return SequenceMatcher(None, str(a).lower(), str(b).lower()).ratio()

# Find duplicates using the same criteria
duplicates_found = []

for i, row1 in df.iterrows():
    for j, row2 in df.iterrows():
        if i >= j:
            continue

        # Fuzzy name matching (0.85 threshold)
        name_sim = string_similarity(row1['org_name'], row2['org_name'])
        if name_sim < 0.85:
            continue

        # Date proximity (within 2 days)
        if pd.notna(row1['breach_date']) and pd.notna(row2['breach_date']):
            date_diff = abs((row1['breach_date'] - row2['breach_date']).days)
            if date_diff > 2:
                continue
        else:
            continue

        duplicates_found.append({
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
            'vendor_1': row1['nvd_vendor'],
            'vendor_2': row2['nvd_vendor'],
        })

print(f"\nMatching Criteria Used in Master Audit:")
print(f"  1. Org name fuzzy match: similarity > 0.85 (SequenceMatcher ratio)")
print(f"  2. Date proximity: within 2 days")
print(f"  3. At least one date must be non-null")
print(f"\nTotal duplicate pairs detected: {len(duplicates_found)}")

# ============================================================================
# SECTION 1: CATEGORIZE THE DUPLICATES
# ============================================================================

print("\n" + "-"*100)
print("SECTION 1: CATEGORIZING DUPLICATE PAIRS BY CONFIDENCE")
print("-"*100)

# Classify each pair
genuine_pattern = []  # Identical CAR, same/1-day date diff, high name sim
likely_pattern = []   # Same date, same vendor, high name sim
uncertain_pattern = [] # Everything else

for dup in duplicates_found:
    if (abs(dup['car_1'] - dup['car_2']) < 0.01 and  # Identical CAR (within 0.01pp)
        dup['date_diff'] <= 1 and  # Same or 1 day apart
        dup['name_sim'] > 0.95):   # Very high name similarity
        genuine_pattern.append(dup)
    elif (dup['date_diff'] == 0 and  # Exact same date
          dup['vendor_1'] == dup['vendor_2'] and  # Same vendor
          dup['name_sim'] > 0.95):  # High name similarity
        likely_pattern.append(dup)
    else:
        uncertain_pattern.append(dup)

print(f"\nDuplicate classification:")
print(f"  GENUINE PATTERN (identical CAR, same/1d date, high name sim):  {len(genuine_pattern):4d} pairs")
print(f"  LIKELY PATTERN (same date, same vendor, high name sim):        {len(likely_pattern):4d} pairs")
print(f"  UNCERTAIN PATTERN (other combinations):                        {len(uncertain_pattern):4d} pairs")

print(f"\nGENUINE pattern details:")
for dup in genuine_pattern[:5]:
    print(f"  [{dup['idx_1']:4d}] {dup['org_1']:35s} | {dup['date_1'].strftime('%Y-%m-%d')} | CAR={dup['car_1']:7.2f}%")
    print(f"  [{dup['idx_2']:4d}] {dup['org_2']:35s} | {dup['date_2'].strftime('%Y-%m-%d')} | CAR={dup['car_2']:7.2f}% (name_sim={dup['name_sim']:.3f})")
    print()

# ============================================================================
# SECTION 2: SAMPLE 20 UNCERTAIN PAIRS (LIKELY FALSE POSITIVES)
# ============================================================================

print("\n" + "-"*100)
print("SECTION 2: SAMPLE OF 20 'UNCERTAIN' PAIRS (Potential False Positives)")
print("-"*100)
print("\nThese pairs matched on fuzzy name + date proximity, but don't follow the GENUINE pattern.")
print("Do they look like actual duplicates or distinct breaches at the same company?")
print()

sample_uncertain = uncertain_pattern[:20]

for idx, dup in enumerate(sample_uncertain, 1):
    print(f"Pair {idx:2d}:")
    print(f"  Org 1 [{dup['idx_1']:4d}]: {dup['org_1']:40s}")
    print(f"  Org 2 [{dup['idx_2']:4d}]: {dup['org_2']:40s}")
    print(f"    Name similarity: {dup['name_sim']:.3f}")
    print(f"    Date 1: {dup['date_1'].strftime('%Y-%m-%d')}")
    print(f"    Date 2: {dup['date_2'].strftime('%Y-%m-%d')}")
    print(f"    Date diff: {dup['date_diff']} days")
    print(f"    CAR 1: {dup['car_1']:7.2f}% | CAR 2: {dup['car_2']:7.2f}% | Diff: {abs(dup['car_1'] - dup['car_2']):7.2f}pp")
    print(f"    Vendor match: {dup['vendor_1'] == dup['vendor_2']} ({dup['vendor_1']} vs {dup['vendor_2']})")
    print(f"    Affected 1: {int(dup['affected_1']):8d} | Affected 2: {int(dup['affected_2']):8d}")
    print()

# ============================================================================
# SECTION 3: COMPARISON TO ORIGINAL VALIDATION CHECK
# ============================================================================

print("\n" + "-"*100)
print("SECTION 3: COMPARISON TO ORIGINAL VALIDATION CHECK (44 flagged pairs)")
print("-"*100)

# Original check: exact org_name, exact breach_date, exact total_affected
original_style_matches = 0
for i, row1 in df.iterrows():
    for j, row2 in df.iterrows():
        if i >= j:
            continue

        # Exact matches only
        if (row1['org_name'] == row2['org_name'] and
            row1['breach_date'] == row2['breach_date'] and
            row1['total_affected'] == row2['total_affected']):
            original_style_matches += 1

print(f"\nUsing ORIGINAL matching criteria (exact name, exact date, exact affected):")
print(f"  Exact duplicate pairs found: {original_style_matches}")
print(f"\nUsing NEW matching criteria (fuzzy name 0.85+, date within 2 days):")
print(f"  Fuzzy duplicate pairs found: {len(duplicates_found)}")
print(f"\nRatio: {len(duplicates_found) / max(original_style_matches, 1):.1f}x more pairs with fuzzy matching")

# ============================================================================
# SECTION 4: RECOMMENDATION
# ============================================================================

print("\n" + "="*100)
print("RECOMMENDATION")
print("="*100)

confident_count = len(genuine_pattern) + len(likely_pattern)
uncertain_count = len(uncertain_pattern)

print(f"""
Of the {len(duplicates_found)} total pairs flagged:
  - {confident_count} follow the GENUINE or LIKELY pattern (high confidence duplicates)
  - {uncertain_count} are uncertain (may be false positives)

INTERPRETATION:
If most of the 282 dropped records come from UNCERTAIN pairs, the audit
was overly aggressive and should be re-calibrated to match the original
44-duplicate baseline (which used exact matching).

NEXT STEP:
Rerun the deduplication using ONLY the GENUINE + LIKELY patterns, not
the UNCERTAIN ones. This will produce a conservative deduplication that
aligns with the original validation check's intent.

Alternatively, manually inspect a larger sample of the UNCERTAIN pairs to
determine a better similarity threshold (currently 0.85).
""")

print("="*100 + "\n")
