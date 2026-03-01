"""
H6 Analysis: Regulatory Enforcement and Disclosure Timing
Tests whether disclosure timing predicts regulatory enforcement action
NOTE: Very low prevalence (0.6%) limits statistical power
"""

import pandas as pd
import numpy as np
import statsmodels.api as sm
from pathlib import Path

# Load data
data_path = Path('Data/processed/FINAL_DISSERTATION_DATASET_ENRICHED.csv')
df = pd.read_csv(data_path)

# Prepare analysis
analysis_df = df[['cik', 'org_name', 'car_30d', 'immediate_disclosure', 'fcc_reportable',
                  'disclosure_delay_days', 'has_enforcement', 'total_affected',
                  'health_breach', 'prior_breaches_total', 'firm_size_log', 'leverage', 'roa']].copy()

# Rename for consistency
analysis_df.rename(columns={'org_name': 'firm_name'}, inplace=True)

# Create log transformation for total_affected
analysis_df['total_affected'] = pd.to_numeric(analysis_df['total_affected'], errors='coerce')
analysis_df['total_affected_log'] = np.log1p(analysis_df['total_affected'])

print("\n" + "="*80)
print("H6 ANALYSIS: REGULATORY ENFORCEMENT")
print("="*80)

# ============================================================================
# STEP 1: Descriptive Statistics
# ============================================================================
print("\n" + "="*80)
print("STEP 1: DESCRIPTIVE STATISTICS")
print("="*80)

print(f"\nTotal observations: {len(analysis_df)}")
print(f"\nRegulatory Enforcement Events:")
enforcement_count = analysis_df['has_enforcement'].sum()
print(f"  Enforcement actions: {enforcement_count}")
print(f"  Prevalence: {100*enforcement_count/len(analysis_df):.2f}%")

if enforcement_count == 0:
    print("\n[WARNING] NO ENFORCEMENT CASES FOUND IN DATASET")
    print("Analysis cannot proceed. Check data source.")
else:
    # Characteristics of enforcement cases
    enforcement_df = analysis_df[analysis_df['has_enforcement'] == 1]

    print(f"\nCharacteristics of Enforcement Cases (N={enforcement_count}):")
    print(f"  Mean prior breaches: {enforcement_df['prior_breaches_total'].mean():.2f}")
    print(f"  Mean firm size (log): {enforcement_df['firm_size_log'].mean():.2f}")
    print(f"  Health breaches: {(enforcement_df['health_breach'] == 1).sum()} ({100*(enforcement_df['health_breach'] == 1).sum()/enforcement_count:.0f}%)")
    print(f"  FCC-regulated: {(enforcement_df['fcc_reportable'] == 1).sum()} ({100*(enforcement_df['fcc_reportable'] == 1).sum()/enforcement_count:.0f}%)")
    print(f"  Immediate disclosure: {(enforcement_df['immediate_disclosure'] == 1).sum()} ({100*(enforcement_df['immediate_disclosure'] == 1).sum()/enforcement_count:.0f}%)")

    # By timing group
    print(f"\nEnforcement by Disclosure Timing:")
    by_timing = analysis_df.groupby('immediate_disclosure')['has_enforcement'].agg(['sum', 'count'])
    by_timing['rate'] = 100 * by_timing['sum'] / by_timing['count']
    print(by_timing)

    # ========================================================================
    # STEP 2: Power Assessment
    # ========================================================================
    print("\n" + "="*80)
    print("STEP 2: STATISTICAL POWER ASSESSMENT")
    print("="*80)

    print("\n[WARNING] INSUFFICIENT POWER FOR REGRESSION")
    print(f"Enforcement occurs in only {enforcement_count} of {len(analysis_df)} cases ({100*enforcement_count/len(analysis_df):.2f}%)")
    print("Standard minimum for regression: 5-10% prevalence")
    print("Current prevalence: 0.57% (INSUFFICIENT)")
    print("\nConclusion: H6 cannot be tested statistically. Report descriptive findings only.")

    # Save results
    output_file = Path('outputs/tables/H6_ENFORCEMENT_ANALYSIS.txt')
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w') as f:
        f.write("H6 ANALYSIS: REGULATORY ENFORCEMENT AND DISCLOSURE TIMING\n")
        f.write("="*80 + "\n\n")

        f.write("DESCRIPTIVE STATISTICS\n")
        f.write("-"*80 + "\n")
        f.write(f"Total observations: {len(analysis_df)}\n")
        f.write(f"Enforcement cases: {enforcement_count}\n")
        f.write(f"Prevalence: {100*enforcement_count/len(analysis_df):.2f}%\n\n")

        if enforcement_count > 0:
            f.write("Characteristics of Enforcement Cases:\n")
            f.write(f"  Mean prior breaches: {enforcement_df['prior_breaches_total'].mean():.2f}\n")
            f.write(f"  FCC-regulated: {(enforcement_df['fcc_reportable'] == 1).sum()} / {enforcement_count}\n")
            f.write(f"  Health breaches: {(enforcement_df['health_breach'] == 1).sum()} / {enforcement_count}\n")
            f.write(f"  Immediate disclosure: {(enforcement_df['immediate_disclosure'] == 1).sum()} / {enforcement_count}\n\n")

        f.write("STATISTICAL POWER NOTE\n")
        f.write("-"*80 + "\n")
        f.write(f"Outcome prevalence: {100*enforcement_count/len(analysis_df):.2f}%\n")
        f.write("Recommended minimum for regression: 5-10%\n")
        f.write("Current prevalence is BELOW minimum - insufficient power for causal inference.\n\n")

        f.write("CONCLUSION\n")
        f.write("-"*80 + "\n")
        f.write("H6 (Regulatory Enforcement) is insufficiently powered to test.\n")
        f.write(f"Only {enforcement_count} enforcement cases in {len(analysis_df)} observations ({100*enforcement_count/len(analysis_df):.2f}%) limits analysis.\n")
        f.write("Recommend reporting H6 as a descriptive finding, not a causal test.\n\n")

        f.write("MANUSCRIPT LANGUAGE FOR H6:\n")
        f.write("\"H6 (regulatory enforcement) suffers from insufficient statistical power.\n")
        f.write("Enforcement actions occur in only 0.6% of cases (N=6), below the minimum\n")
        f.write("prevalence for valid regression inference. Characteristics of enforcement\n")
        f.write("cases are reported descriptively: enforcement is concentrated among repeat\n")
        f.write("offenders (mean 7.17 prior breaches) rather than disclosure timing. We do not\n")
        f.write("report statistical tests for H6.\"\n")

    print(f"\n[OK] H6 results saved to {output_file}")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "="*80)
print("SUMMARY: H6 STATISTICAL POWER")
print("="*80)

if enforcement_count > 0:
    pct_enforcement = 100 * enforcement_count / len(analysis_df)
    print(f"\nEnforcement prevalence: {pct_enforcement:.2f}%")

    if pct_enforcement < 5:
        print("Status: INSUFFICIENT POWER FOR REGRESSION")
        print("Recommendation: Report as descriptive finding only")
    else:
        print("Status: Adequate power for regression")
        print("Recommendation: Can estimate causal effects")
else:
    print("\nNo enforcement cases found.")
    print("H6 cannot be tested empirically.")

print("\n" + "="*80)
