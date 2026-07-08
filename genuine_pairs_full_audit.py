"""
FULL AUDIT OF ALL 1,205 GENUINE PAIRS
=====================================

Two key checks before applying deduplication:

1. SIMILARITY DISTRIBUTION
   Sort all pairs by name similarity (ascending).
   Focus on the 0.95-0.97 "danger zone" — these are the marginal cases where
   the rule is doing real discriminating work, not just catching obvious entity typos.
   Check if these low-similarity pairs look like true duplicates or false positives.

2. FIRM CONCENTRATION
   Cross-tab: how many unique firms appear in the 1,205 pairs?
   - If concentrated in a few firms (like DISH): makes sense, entity-variant problem
   - If spread across hundreds: suggests systematic false-positive matching

A 24% data loss is extraordinary for PRC. Need full audit, not spot-check.
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
print("FULL AUDIT OF 1,205 GENUINE DUPLICATE PAIRS")
print("="*100)

# Recreate genuine pairs
def string_similarity(a, b):
    return SequenceMatcher(None, str(a).lower(), str(b).lower()).ratio()

genuine_pairs = []

for i, row1 in df.iterrows():
    for j, row2 in df.iterrows():
        if i >= j:
            continue

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
        })

print(f"\nTotal genuine pairs: {len(genuine_pairs)}")

# ============================================================================
# SECTION 1: SIMILARITY DISTRIBUTION
# ============================================================================

print("\n" + "="*100)
print("SECTION 1: SIMILARITY DISTRIBUTION")
print("="*100)

# Sort by name similarity
genuine_pairs_sorted = sorted(genuine_pairs, key=lambda x: x['name_sim'])

print(f"\nAll pairs sorted by name similarity (ascending):")
print(f"Range: {min(p['name_sim'] for p in genuine_pairs):.3f} - {max(p['name_sim'] for p in genuine_pairs):.3f}")

# Bin into ranges
bins = [(0.95, 0.96), (0.96, 0.97), (0.97, 0.98), (0.98, 0.99), (0.99, 1.00), (1.00, 1.01)]
for lo, hi in bins:
    count = len([p for p in genuine_pairs if lo <= p['name_sim'] < hi])
    print(f"  {lo:.2f}-{hi:.2f}: {count:4d} pairs")

# ============================================================================
# SECTION 2: DANGER ZONE (0.95-0.97) DETAILED REVIEW
# ============================================================================

print("\n" + "-"*100)
print("DANGER ZONE REVIEW: Pairs with name similarity 0.95-0.97")
print("(These are marginal matches where the rule does real discriminating work)")
print("-"*100)

danger_zone = [p for p in genuine_pairs_sorted if 0.95 <= p['name_sim'] < 0.97]
print(f"\nTotal pairs in danger zone (0.95-0.97): {len(danger_zone)}")

if len(danger_zone) > 0:
    print(f"\nShowing all {len(danger_zone)} danger-zone pairs:")
    print()
    for idx, pair in enumerate(danger_zone, 1):
        print(f"Pair {idx}:")
        print(f"  Org 1: {pair['org_1']}")
        print(f"  Org 2: {pair['org_2']}")
        print(f"  Name similarity: {pair['name_sim']:.3f}")
        print(f"  Date 1: {pair['date_1'].strftime('%Y-%m-%d')}, Date 2: {pair['date_2'].strftime('%Y-%m-%d')}, Diff: {pair['date_diff']}d")
        print(f"  CAR 1: {pair['car_1']:7.2f}%, CAR 2: {pair['car_2']:7.2f}%, Diff: {abs(pair['car_1'] - pair['car_2']):.3f}pp")
        print(f"  Affected 1: {int(pair['affected_1']):8d}, Affected 2: {int(pair['affected_2']):8d}")
        print()

# ============================================================================
# SECTION 3: FIRM CONCENTRATION ANALYSIS
# ============================================================================

print("\n" + "="*100)
print("SECTION 3: FIRM CONCENTRATION ANALYSIS")
print("="*100)

# Get unique firms involved in pairs
firms_involved = set()
for pair in genuine_pairs:
    firms_involved.add(pair['org_1'])
    firms_involved.add(pair['org_2'])

print(f"\nFirms involved in genuine pairs:")
print(f"  Total unique firms: {len(firms_involved)}")
print(f"  Total pairs: {len(genuine_pairs)}")
print(f"  Avg pairs per firm: {len(genuine_pairs) / len(firms_involved):.1f}")

# Count pairs per firm (by first org name)
pair_count_by_firm = {}
for pair in genuine_pairs:
    firm = pair['org_1']
    if firm not in pair_count_by_firm:
        pair_count_by_firm[firm] = 0
    pair_count_by_firm[firm] += 1

# Also count by second org name
for pair in genuine_pairs:
    firm = pair['org_2']
    if firm not in pair_count_by_firm:
        pair_count_by_firm[firm] = 0
    # Don't double-count; just track participation

print(f"\nFirm concentration:")
sorted_firms = sorted(pair_count_by_firm.items(), key=lambda x: x[1], reverse=True)

print(f"\nTop 20 firms by pair count:")
for firm, count in sorted_firms[:20]:
    print(f"  {firm:50s}: {count:3d} pairs")

# Distribution analysis
pair_counts = list(pair_count_by_firm.values())
print(f"\nPair count distribution:")
print(f"  Firms with 1 pair: {len([c for c in pair_counts if c == 1])}")
print(f"  Firms with 2-5 pairs: {len([c for c in pair_counts if 2 <= c <= 5])}")
print(f"  Firms with 6-10 pairs: {len([c for c in pair_counts if 6 <= c <= 10])}")
print(f"  Firms with 11+ pairs: {len([c for c in pair_counts if c >= 11])}")

# Check concentration: how many firms drive majority of pairs?
sorted_by_count = sorted(pair_counts, reverse=True)
cumulative = 0
firms_to_reach_50pct = 0
firms_to_reach_80pct = 0
for count in sorted_by_count:
    cumulative += count
    if cumulative >= len(genuine_pairs) * 0.5 and firms_to_reach_50pct == 0:
        firms_to_reach_50pct = len([c for c in sorted_by_count if c >= count])
    if cumulative >= len(genuine_pairs) * 0.8 and firms_to_reach_80pct == 0:
        firms_to_reach_80pct = len([c for c in sorted_by_count if c >= count])

print(f"\nConcentration check:")
print(f"  Firms needed to reach 50% of pairs: ~{firms_to_reach_50pct} out of {len(firms_involved)}")
print(f"  Firms needed to reach 80% of pairs: ~{firms_to_reach_80pct} out of {len(firms_involved)}")

if firms_to_reach_50pct < len(firms_involved) * 0.1:
    print(f"  → CONCENTRATED: A small number of firms drive most pairs (like DISH)")
else:
    print(f"  → DISTRIBUTED: Pairs spread across many firms (suspicious)")

# ============================================================================
# SECTION 4: SUMMARY & RECOMMENDATION
# ============================================================================

print("\n" + "="*100)
print("SUMMARY & RECOMMENDATION")
print("="*100)

print(f"""
KEY FINDINGS:

1. Danger zone (name sim 0.95-0.97): {len(danger_zone)} pairs
   - These are the marginal cases where the rule discriminates
   - Review above to check if they look like true duplicates or false positives

2. Firm concentration:
   - {len(firms_involved)} unique firms involved in pairs
   - Top firm has {sorted_firms[0][1]} pairs
   - Distribution: {'CONCENTRATED' if firms_to_reach_50pct < len(firms_involved) * 0.1 else 'DISTRIBUTED'}

INTERPRETATION:

If danger-zone pairs look like coincidental matches (different companies,
similar names, different affected counts but identical CAR by chance),
the rule is TOO LOOSE.

If danger-zone pairs all look like entity variants (obvious duplicates),
the rule is APPROPRIATELY CALIBRATED.

If the distribution is highly concentrated (top 10 firms drive 50%+ of pairs),
the problem is real but localized (DISH-like issue).

If the distribution is broad (pairs spread across 100+ firms each with 1-2 pairs),
the matching rule is systematically wrong.

BEFORE APPLYING THIS DEDUPLICATION:
- Review the danger-zone pairs above
- Assess whether they look like true duplicates or false positives
- Consider whether a stricter threshold (0.98+ instead of 0.95+) would be safer
""")

print("="*100 + "\n")
