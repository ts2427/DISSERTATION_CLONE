"""
CVSS Imbalance Diagnostic Script
==================================

Priority 1: Investigate vendor-matching bias
  - Do telecom vendors (FCC firms) match to more CVEs per breach?
  - Are large vendors (Verizon, AT&T, Charter) pulling inflated CVSS scores?

Priority 2: Check for concentrated influence
  - Is imbalance driven by a few mega-firms, or systemic?
  - Which FCC firms contribute most to the high mean CVSS?

Priority 3: Characterize the imbalance
  - CVSS distribution by FCC status
  - Vendor-level breakdown
  - Firm-level breakdown

Run diagnostics in order; stop after Priority 1 if Scenario B (matching artifact) is confirmed.
"""

import pandas as pd
import numpy as np
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Load data
df = pd.read_csv('Data/processed/FINAL_DISSERTATION_DATASET_WITH_CVSS.csv')

print("\n" + "="*80)
print("CVSS IMBALANCE DIAGNOSTIC: HIGH-COMPLEXITY BREACHES (CVSS >= 7.0)")
print("="*80)

# Focus on high-complexity only (where the imbalance was detected)
high_complex = df[df['has_high_complexity'] == 1].copy()

print(f"\nTotal high-complexity breaches: N = {len(high_complex)}")
print(f"  FCC: {(high_complex['fcc_reportable']==1).sum()}")
print(f"  Non-FCC: {(high_complex['fcc_reportable']==0).sum()}")

# ============================================================================
# PRIORITY 1: MATCHING BIAS CHECK (Run this first)
# ============================================================================

print("\n" + "="*80)
print("PRIORITY 1: MATCHING BIAS CHECK - Do telecom firms match to more CVEs?")
print("="*80)

# Check if we have CVE count data
if 'total_cves' in high_complex.columns:
    print("\nCVE Count Distribution (per breach):")
    print("\nFCC-reportable firms:")
    fcc_cves = high_complex[high_complex['fcc_reportable']==1]['total_cves'].dropna()
    print(f"  N = {len(fcc_cves)}")
    print(f"  Mean CVEs per breach: {fcc_cves.mean():.2f}")
    print(f"  Median CVEs per breach: {fcc_cves.median():.1f}")
    print(f"  SD: {fcc_cves.std():.2f}")
    print(f"  Range: [{fcc_cves.min():.0f}, {fcc_cves.max():.0f}]")
    print(f"  Q1-Q3: [{fcc_cves.quantile(0.25):.0f}, {fcc_cves.quantile(0.75):.0f}]")

    print("\nNon-FCC firms:")
    non_fcc_cves = high_complex[high_complex['fcc_reportable']==0]['total_cves'].dropna()
    print(f"  N = {len(non_fcc_cves)}")
    print(f"  Mean CVEs per breach: {non_fcc_cves.mean():.2f}")
    print(f"  Median CVEs per breach: {non_fcc_cves.median():.1f}")
    print(f"  SD: {non_fcc_cves.std():.2f}")
    print(f"  Range: [{non_fcc_cves.min():.0f}, {non_fcc_cves.max():.0f}]")
    print(f"  Q1-Q3: [{non_fcc_cves.quantile(0.25):.0f}, {non_fcc_cves.quantile(0.75):.0f}]")

    # T-test
    if len(fcc_cves) > 0 and len(non_fcc_cves) > 0:
        t_stat, p_val = stats.ttest_ind(fcc_cves, non_fcc_cves)
        print(f"\nT-test (FCC vs Non-FCC CVE counts):")
        print(f"  t = {t_stat:.3f}, p = {p_val:.4f}")
        if p_val < 0.05:
            direction = "higher" if fcc_cves.mean() > non_fcc_cves.mean() else "lower"
            print(f"  [!] SIGNIFICANT: FCC firms match to {direction} CVE counts (p < 0.05)")
            print(f"  [!] This suggests SCENARIO B: matching bias — telecom vendors have")
            print(f"      larger product catalogs, pulling more CVE entries per breach.")
        else:
            print(f"  [OK] No significant difference in CVE matching volume (p >= 0.05)")
else:
    print("\n[!] total_cves column not found. Checking vendor_max_cvss directly...")

# Check if vendor matching is the issue
print("\n" + "-"*80)
print("Vendor Coverage Analysis:")
print("-"*80)

if 'nvd_vendor' in high_complex.columns:
    print("\nFCC firms - vendors with most high-complexity breaches:")
    fcc_vendors = high_complex[high_complex['fcc_reportable']==1]['nvd_vendor'].value_counts().head(15)
    for vendor, count in fcc_vendors.items():
        vendor_mean_cvss = high_complex[
            (high_complex['fcc_reportable']==1) &
            (high_complex['nvd_vendor']==vendor)
        ]['vendor_max_cvss'].mean()
        print(f"  {vendor:25s}: {count:3d} breaches, mean CVSS {vendor_mean_cvss:.2f}")

    print("\nNon-FCC firms - vendors with most high-complexity breaches:")
    non_fcc_vendors = high_complex[high_complex['fcc_reportable']==0]['nvd_vendor'].value_counts().head(15)
    for vendor, count in non_fcc_vendors.items():
        vendor_mean_cvss = high_complex[
            (high_complex['fcc_reportable']==0) &
            (high_complex['nvd_vendor']==vendor)
        ]['vendor_max_cvss'].mean()
        print(f"  {vendor:25s}: {count:3d} breaches, mean CVSS {vendor_mean_cvss:.2f}")

# ============================================================================
# PRIORITY 2: CONCENTRATED INFLUENCE CHECK
# ============================================================================

print("\n" + "="*80)
print("PRIORITY 2: CONCENTRATED INFLUENCE - Which FCC firms drive the imbalance?")
print("="*80)

if 'org_name' in high_complex.columns:
    print("\nFCC firms by mean CVSS (high-complexity breaches only):")
    fcc_firms = high_complex[high_complex['fcc_reportable']==1].groupby('org_name').agg({
        'vendor_max_cvss': ['count', 'mean', 'std']
    }).round(2)
    fcc_firms.columns = ['n_breaches', 'mean_cvss', 'sd_cvss']
    fcc_firms = fcc_firms.sort_values('mean_cvss', ascending=False)

    print("\nTop 10 FCC firms by mean CVSS:")
    for idx, (firm, row) in enumerate(fcc_firms.head(10).iterrows(), 1):
        print(f"  {idx:2d}. {firm:30s}: {row['mean_cvss']:5.2f} (n={int(row['n_breaches']):2d})")

    print(f"\nBottom 10 FCC firms by mean CVSS:")
    for idx, (firm, row) in enumerate(fcc_firms.tail(10).iterrows(), 1):
        print(f"  {idx:2d}. {firm:30s}: {row['mean_cvss']:5.2f} (n={int(row['n_breaches']):2d})")

    # Check if top firms are outliers
    print(f"\nInfluential Observations Check:")
    top_firm_contribution = fcc_firms.head(3)['n_breaches'].sum() / fcc_firms['n_breaches'].sum() * 100
    print(f"  Top 3 FCC firms account for {top_firm_contribution:.1f}% of all high-complexity FCC breaches")

    if top_firm_contribution > 40:
        print(f"  [!] Concentrated: Imbalance may be driven by a few mega-firms (AT&T, Verizon, Charter?)")
        print(f"      Suggests influential-observation problem, not systemic matching bias")
    else:
        print(f"  [OK] Distributed: Multiple FCC firms contribute to high mean CVSS")
        print(f"      Suggests systemic matching bias or genuine sector characteristic")

# ============================================================================
# PRIORITY 3: IMBALANCE CHARACTERIZATION
# ============================================================================

print("\n" + "="*80)
print("PRIORITY 3: IMBALANCE CHARACTERIZATION")
print("="*80)

print("\nVendor_max_CVSS Distribution (high-complexity only):")
print("\nFCC-reportable firms:")
fcc_cvss = high_complex[high_complex['fcc_reportable']==1]['vendor_max_cvss'].dropna()
print(f"  N = {len(fcc_cvss)}")
print(f"  Mean = {fcc_cvss.mean():.2f}")
print(f"  Median = {fcc_cvss.median():.2f}")
print(f"  SD = {fcc_cvss.std():.2f}")
print(f"  Skewness = {fcc_cvss.skew():.2f}")
print(f"  Kurtosis = {fcc_cvss.kurtosis():.2f}")

print("\nNon-FCC firms:")
non_fcc_cvss = high_complex[high_complex['fcc_reportable']==0]['vendor_max_cvss'].dropna()
print(f"  N = {len(non_fcc_cvss)}")
print(f"  Mean = {non_fcc_cvss.mean():.2f}")
print(f"  Median = {non_fcc_cvss.median():.2f}")
print(f"  SD = {non_fcc_cvss.std():.2f}")
print(f"  Skewness = {non_fcc_cvss.skew():.2f}")
print(f"  Kurtosis = {non_fcc_cvss.kurtosis():.2f}")

print("\nQuantile Comparison:")
quantiles = [0.05, 0.25, 0.5, 0.75, 0.95]
for q in quantiles:
    fcc_q = fcc_cvss.quantile(q)
    non_fcc_q = non_fcc_cvss.quantile(q)
    diff = fcc_q - non_fcc_q
    print(f"  Q{int(q*100):2d}: FCC {fcc_q:5.2f}, Non-FCC {non_fcc_q:5.2f}, Diff {diff:+5.2f}")

# ============================================================================
# SCENARIO ASSESSMENT
# ============================================================================

print("\n" + "="*80)
print("SCENARIO ASSESSMENT")
print("="*80)

print("\nBased on diagnostics above:")

if 'total_cves' in high_complex.columns and len(fcc_cves) > 0:
    if p_val < 0.05 and fcc_cves.mean() > non_fcc_cves.mean():
        print("\n[SCENARIO B: MATCHING ARTIFACT LIKELY]")
        print("  FCC firms match to significantly more CVEs per breach.")
        print("  Telecom vendors (Verizon, AT&T, Charter) have sprawling product catalogs.")
        print("  Recommendation: Fix the vendor-matching logic to equalize CVE capture.")
        print("  Next step: Investigate the NVD vendor-matching script.")
    else:
        print("\n[SCENARIO A: REAL CHARACTERISTIC LIKELY]")
        print("  CVE matching is balanced across FCC status.")
        print("  FCC firms genuinely face higher-severity breaches.")
        print("  Recommendation: Report imbalance as a characteristic of telecom sector,")
        print("                  potentially control for it in analysis.")

print("\n" + "="*80)
print("END OF DIAGNOSTIC")
print("="*80 + "\n")
