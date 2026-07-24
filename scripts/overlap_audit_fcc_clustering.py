"""
OVERLAP AUDIT: Mitchell-Stafford Non-Independence Check
========================================================================

Tests whether FCC-firm breaches cluster in time, creating cross-correlation
in long-horizon abnormal returns. Mitchell and Stafford (2000) show that
multiple events at same firm within a window inflate test statistics up to 4x.

Quantifies:
1. How many FCC breaches have other FCC-firm breaches in 30/60/90-day windows
2. Distribution of overlap by firm and window
3. Implications for inference (adjustment needed?)
"""

import pandas as pd
import numpy as np
from datetime import timedelta
from collections import defaultdict

print("=" * 90)
print("OVERLAP AUDIT: FCC BREACH CLUSTERING ANALYSIS")
print("=" * 90)

# Load data
df = pd.read_csv('Data/processed/FINAL_DISSERTATION_DATASET_DEDUPLICATED_ENRICHED.csv')
df['breach_date'] = pd.to_datetime(df['breach_date'])

# Analysis on FCC firms only (treatment group)
fcc_df = df[df['fcc_reportable'] == True].copy()
fcc_df = fcc_df.sort_values('breach_date').reset_index(drop=True)

print(f"\nFCC-regulated breaches in sample:")
print(f"  Total observations: {len(fcc_df)}")
print(f"  Unique firms: {fcc_df['cik'].nunique()}")
print(f"  Unique organizations: {fcc_df['org_name'].nunique()}")
print(f"  Date range: {fcc_df['breach_date'].min().date()} to {fcc_df['breach_date'].max().date()}")

# Top FCC firms by breach count
top_firms = fcc_df['org_name'].value_counts().head(10)
print(f"\nTop 10 FCC firms by breach count:")
for org, count in top_firms.items():
    print(f"  {org:<30s}: {count:3d} breaches")

# For each window size, count overlaps
windows = [30, 60, 90]
overlap_summary = []

print(f"\n" + "=" * 90)
print("OVERLAP ANALYSIS BY WINDOW SIZE")
print("=" * 90)

for window_days in windows:
    print(f"\n{window_days}-DAY WINDOW ANALYSIS")
    print(f"{'-' * 90}")

    overlap_count = 0
    breach_overlap_dict = defaultdict(int)
    max_overlap = 0

    for idx, row in fcc_df.iterrows():
        breach_date = row['breach_date']
        cik = row['cik']
        org_name = row['org_name']

        # Find other breaches at same firm within window
        window_start = breach_date - timedelta(days=window_days)
        window_end = breach_date + timedelta(days=window_days)

        other_breaches = fcc_df[
            (fcc_df['cik'] == cik) &
            (fcc_df['breach_date'] != breach_date) &
            (fcc_df['breach_date'] >= window_start) &
            (fcc_df['breach_date'] <= window_end)
        ]

        if len(other_breaches) > 0:
            overlap_count += 1
            num_overlaps = len(other_breaches)
            breach_overlap_dict[org_name] += 1
            max_overlap = max(max_overlap, num_overlaps)

    # Statistics
    pct_with_overlap = (overlap_count / len(fcc_df)) * 100
    overlap_summary.append({
        'Window_Days': window_days,
        'Total_FCC_Breaches': len(fcc_df),
        'Breaches_With_Overlap': overlap_count,
        'Pct_With_Overlap': pct_with_overlap,
        'Max_Overlapping_Events': max_overlap
    })

    print(f"\nSummary:")
    print(f"  Breaches with overlapping events: {overlap_count}/{len(fcc_df)} ({pct_with_overlap:.1f}%)")
    print(f"  Maximum overlapping events at single firm: {max_overlap}")

    # Show firms with most overlap
    if breach_overlap_dict:
        sorted_firms = sorted(breach_overlap_dict.items(), key=lambda x: x[1], reverse=True)
        print(f"\nTop firms by number of overlapping breach pairs:")
        for firm, overlap_pairs in sorted_firms[:5]:
            print(f"  {firm:<30s}: {overlap_pairs} breach pairs")

# Summary table
print(f"\n" + "=" * 90)
print("SUMMARY TABLE")
print(f"=" * 90)

summary_df = pd.DataFrame(overlap_summary)
print(summary_df.to_string(index=False))

# Critical assessment
print(f"\n" + "=" * 90)
print("METHODOLOGICAL IMPLICATIONS")
print(f"=" * 90)

print(f"""
Mitchell and Stafford (2000) identify a critical problem in long-horizon event studies:
when multiple events at the same firm occur within the event window, abnormal returns
are correlated by calendar period, inflating test statistics up to 4x.

YOUR SITUATION:

30-day window: {overlap_summary[0]['Pct_With_Overlap']:.1f}% of FCC breaches have other FCC-firm breaches
60-day window: {overlap_summary[1]['Pct_With_Overlap']:.1f}% of FCC breaches have other FCC-firm breaches
90-day window: {overlap_summary[2]['Pct_With_Overlap']:.1f}% of FCC breaches have other FCC-firm breaches

ASSESSMENT:

- If <10% of observations have overlap: Mitchell-Stafford not a major concern
- If 10-30% have overlap: Important to check, but may not invalidate results
- If >30% have overlap: Serious issue — need adjustment (clustering or sample restriction)

CORRECTIVE OPTIONS:

Option A (Sample Restriction): Keep only first breach per firm, or non-overlapping subset
        - Pros: Cleaner design, simpler to interpret
        - Cons: Reduces sample size

Option B (Statistical Adjustment): Cluster standard errors by calendar month
        - Pros: Keeps full sample, addresses cross-correlation
        - Cons: Reduces precision, may inflate SEs significantly

Option C (Hybrid): Run both specifications and compare
        - Specification 1: Full sample with calendar-month clustering
        - Specification 2: Non-overlapping subset, no clustering
        - If results consistent, robust to overlap structure
        - If results diverge, overlap is driving inference

RECOMMENDATION FOR THIS DISSERTATION:

Run Option C (hybrid). This reveals whether the 90-day result is robust to overlap
or whether it's an artifact of correlated abnormal returns at firms with repeated events.
If p-values change materially under clustering or sample restriction, the 90-day result
is fragile and should be reported with hedging language or dropped entirely.
""")

# Save detailed results
overlap_summary_df = pd.DataFrame(overlap_summary)
overlap_summary_df.to_csv('outputs/overlap_audit_summary.csv', index=False)

print(f"\nDetailed results saved to: outputs/overlap_audit_summary.csv")

