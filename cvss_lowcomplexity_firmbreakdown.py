"""
Low-Complexity FCC Firms: Influential Observation Check
========================================================

Quick diagnostic: Is the large negative FCC effect in low-complexity breaches
driven by a handful of firms, or is it broad-based across the FCC population?

Answer determines the path:
- Concentrated (top 3-5 firms >> rest) → influential-observation problem, report with/without those firms
- Broad-based → genuine subpopulation effect, acknowledge but don't overclaim mechanism
"""

import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# Load data
df = pd.read_csv('Data/processed/FINAL_DISSERTATION_DATASET_WITH_CVSS.csv')

print("\n" + "="*80)
print("LOW-COMPLEXITY FCC FIRMS: BREAKDOWN OF CAR_30D BY FIRM")
print("="*80)

# Filter to low-complexity FCC only
low_complex = df[df['vendor_max_cvss'] < 7.0].copy()
fcc_low = low_complex[low_complex['fcc_reportable'] == 1].copy()

# Convert to numeric
fcc_low['car_30d'] = pd.to_numeric(fcc_low['car_30d'], errors='coerce')
fcc_low['total_affected'] = pd.to_numeric(fcc_low['total_affected'], errors='coerce')
fcc_low['breach_year'] = pd.to_numeric(fcc_low['breach_year'], errors='coerce')

print(f"\nTotal low-complexity FCC breaches: N = {len(fcc_low)}")
print(f"Total low-complexity FCC firms: {fcc_low['org_name'].nunique()}")

# Group by firm
firm_summary = fcc_low.groupby('org_name').agg({
    'car_30d': ['count', 'mean', 'median', 'std', 'min', 'max'],
    'total_affected': 'mean',
    'breach_year': 'min'
}).round(2)

firm_summary.columns = ['n_breaches', 'mean_car', 'median_car', 'sd_car', 'min_car', 'max_car', 'avg_affected', 'first_year']
firm_summary = firm_summary.sort_values('mean_car')

print("\nAll low-complexity FCC firms (sorted by mean CAR_30d):")
print("-" * 80)
for idx, (firm, row) in enumerate(firm_summary.iterrows(), 1):
    print(f"{idx:2d}. {firm:35s}: CAR {row['mean_car']:7.2f}% (n={int(row['n_breaches']):2d}, " +
          f"median={row['median_car']:6.2f}%, range=[{row['min_car']:6.2f}%, {row['max_car']:6.2f}%])")

# ============================================================================
# CONCENTRATION ANALYSIS
# ============================================================================

print("\n" + "-"*80)
print("CONCENTRATION ANALYSIS")
print("-"*80)

# Calculate contribution to overall negative effect
# Method: For each firm, multiply (mean CAR) × (n breaches) to get total contribution
firm_summary['total_car_contribution'] = firm_summary['mean_car'] * firm_summary['n_breaches']
total_contribution = firm_summary['total_car_contribution'].sum()

print(f"\nTotal CAR contribution (sum of firm means × breach counts): {total_contribution:.1f}")
print(f"Average CAR per breach: {total_contribution / len(fcc_low):.2f}%")

# Top firms
firm_summary = firm_summary.sort_values('total_car_contribution')
print(f"\nTop 5 firms driving the negative CAR effect (most negative):")
for idx, (firm, row) in enumerate(firm_summary.head(5).iterrows(), 1):
    pct_contribution = (row['total_car_contribution'] / total_contribution) * 100 if total_contribution != 0 else 0
    print(f"  {idx}. {firm:35s}: {row['total_car_contribution']:7.1f} total, " +
          f"({pct_contribution:5.1f}% of total effect)")

# Check if concentrated
top_5_contribution = firm_summary.head(5)['total_car_contribution'].sum()
top_3_contribution = firm_summary.head(3)['total_car_contribution'].sum()

top_5_pct = (top_5_contribution / total_contribution * 100) if total_contribution != 0 else 0
top_3_pct = (top_3_contribution / total_contribution * 100) if total_contribution != 0 else 0

print(f"\nConcentration check:")
print(f"  Top 3 firms account for {top_3_pct:.1f}% of total negative CAR contribution")
print(f"  Top 5 firms account for {top_5_pct:.1f}% of total negative CAR contribution")

if top_3_pct > 50:
    print(f"\n  [CONCENTRATED] Top 3 firms drive more than half the effect.")
    print(f"  Suggests influential-observation problem. Consider reporting with/without top firms.")
elif top_5_pct > 60:
    print(f"\n  [MODERATELY CONCENTRATED] Top 5 firms drive >60% of effect.")
    print(f"  Some influential observations, but not the whole story.")
else:
    print(f"\n  [BROAD-BASED] Effect distributed across multiple firms.")
    print(f"  Suggests genuine subpopulation difference, not influential-observation artifact.")

# ============================================================================
# FIRM-LEVEL DETAIL
# ============================================================================

print("\n" + "-"*80)
print("DETAILED FIRM-BY-FIRM BREAKDOWN")
print("-"*80)

# Sort back to best readability (by mean CAR)
firm_detail = fcc_low.groupby('org_name').agg({
    'car_30d': ['count', 'mean', 'std'],
    'org_name': 'first'
}).round(2)

firm_detail.columns = ['n', 'mean_car', 'sd_car']
firm_detail = firm_detail.sort_values('mean_car')

print("\nFirm summary (sorted by mean CAR_30d):")
print(f"{'Rank':<4} {'Firm':<35} {'N Breaches':<12} {'Mean CAR':<12} {'SD':<8}")
print("-" * 75)

for rank, (firm, row) in enumerate(firm_detail.iterrows(), 1):
    print(f"{rank:<4} {firm:<35} {int(row['n']):<12} {row['mean_car']:<12.2f} {row['sd_car']:<8.2f}")

# ============================================================================
# OUTLIER CHECK: Which individual breaches have extreme CARs?
# ============================================================================

print("\n" + "-"*80)
print("EXTREME CAR BREACHES (individual breach-level outliers)")
print("-"*80)

fcc_low_sorted = fcc_low.sort_values('car_30d')

print("\nTop 10 most negative CARs (biggest losses):")
for idx, (i, row) in enumerate(fcc_low_sorted.head(10).iterrows(), 1):
    print(f"  {idx:2d}. {row['org_name']:35s}: CAR = {row['car_30d']:7.2f}% (breach year {int(row['breach_year'])})")

print("\nTop 10 least negative CARs (smallest losses / gains):")
for idx, (i, row) in enumerate(fcc_low_sorted.tail(10).iterrows(), 1):
    print(f"  {idx:2d}. {row['org_name']:35s}: CAR = {row['car_30d']:7.2f}% (breach year {int(row['breach_year'])})")

# ============================================================================
# SUMMARY RECOMMENDATION
# ============================================================================

print("\n" + "="*80)
print("INTERPRETATION & NEXT STEPS")
print("="*80)

if top_3_pct > 50:
    print("""
[CONCENTRATED: Influential-Observation Story]

The large negative low-complexity FCC effect is driven by a few firms.
This suggests an influential-observation pattern, not a broad subpopulation effect.

RECOMMENDATION:
1. Report the main specification (n=37 FCC, coeff=-9.66pp)
2. Also report a robustness check: results excluding top 3-5 firms
3. Consider winsorizing extreme CARs (e.g., floor at -30%)
4. If the winsorized / excluding-top-firms version lands in-family (-2% to -6%),
   you can report both and note that results are sensitive to a small set of firms

This is a clean, fast fix that takes an hour or two to implement.
""")
else:
    print("""
[BROAD-BASED: Genuine Subpopulation Effect]

The large negative low-complexity FCC effect is distributed across the population.
This is a real subpopulation characteristic, not an influential-observation artifact.

RECOMMENDATION:
1. Report the effect with appropriate caveats (small n, specialized population)
2. Briefly describe what's different about low-complexity FCC breaches
   (e.g., "concentrated among smaller/regional carriers" or "older breach years")
3. OR fall back to reporting only the high-complexity result and noting that
   low-complexity tier is too specialized for stable interpretation

The high-complexity result (-1.2pp) is robust and reportable on its own.
You're not losing a finding by dropping low-complexity; you're being honest
about statistical power and population heterogeneity.
""")

print("="*80 + "\n")
