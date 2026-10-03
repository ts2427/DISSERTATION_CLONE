"""
H2 ROBUSTNESS ANALYSIS: THREE CRITICAL TESTS
1. Leave-one-out sensitivity (FCC firm-level influence)
2. Randomization inference (plausibility against random assignment)
3. Winsorized CARs (outlier robustness)
"""

import pandas as pd
import numpy as np
import statsmodels.api as sm
from scipy.stats.mstats import winsorize
import warnings
warnings.filterwarnings('ignore')

print("=" * 80)
print("H2 ROBUSTNESS ANALYSIS: THREE CRITICAL TESTS")
print("=" * 80)

# Load data
df = pd.read_csv('Data/processed/FINAL_DISSERTATION_DATASET_DEDUPLICATED_ENRICHED.csv')
df = df.dropna(subset=['car_30d', 'firm_size_log', 'leverage', 'roa'])

controls = ['immediate_disclosure', 'prior_breaches_1yr', 'health_breach',
            'firm_size_log', 'leverage', 'roa']

# ============================================================================
# BASELINE
# ============================================================================
X_base = sm.add_constant(df[['fcc_reportable'] + controls].astype(float))
y_base = df['car_30d']
baseline = sm.OLS(y_base, X_base).fit(cov_type='HC3')

print(f"\nBASELINE H2 RESULT")
print("=" * 80)
print(f"Coefficient: {baseline.params['fcc_reportable']:.4f}%")
print(f"Standard error: {baseline.bse['fcc_reportable']:.4f}")
print(f"P-value: {baseline.pvalues['fcc_reportable']:.4f}")
print(f"95% CI: [{baseline.params['fcc_reportable'] - 1.96*baseline.bse['fcc_reportable']:.4f}%, {baseline.params['fcc_reportable'] + 1.96*baseline.bse['fcc_reportable']:.4f}%]")
print(f"N total: {len(df)}")
print(f"N FCC firms: {df[df['fcc_reportable'] == True]['cik'].nunique()}")
print(f"N FCC observations: {int(df['fcc_reportable'].sum())}")

# ============================================================================
# ANALYSIS 1: LEAVE-ONE-OUT SENSITIVITY
# ============================================================================
print("\n" + "=" * 80)
print("ANALYSIS 1: LEAVE-ONE-OUT SENSITIVITY (FCC FIRM-LEVEL INFLUENCE)")
print("=" * 80)

fcc_firms = df[df['fcc_reportable'] == True].groupby('cik')['org_name'].first()
print(f"\nLeaving out each of {len(fcc_firms)} FCC firms (10 total):")
print(f"{'Firm':<40} {'N FCC':>6} {'Coef':>10} {'p-val':>9} {'Sig':>4}")
print("-" * 75)

loo_results = []
for cik, name in fcc_firms.items():
    df_loo = df[df['cik'] != cik]
    X_loo = sm.add_constant(df_loo[['fcc_reportable'] + controls].astype(float))
    y_loo = df_loo['car_30d']
    m = sm.OLS(y_loo, X_loo).fit(cov_type='HC3')
    n_fcc = int(df_loo['fcc_reportable'].sum())
    coef = m.params['fcc_reportable']
    pval = m.pvalues['fcc_reportable']
    sig = '***' if pval < 0.01 else '**' if pval < 0.05 else '*' if pval < 0.10 else 'ns'

    loo_results.append({'firm': name, 'cik': cik, 'n_fcc': n_fcc,
                        'coef': coef, 'se': m.bse['fcc_reportable'],
                        'pvalue': pval, 'significant': pval < 0.05})
    print(f"{name[:39]:<40} {n_fcc:>6} {coef:>10.4f} {pval:>9.4f} {sig:>4}")

loo_df = pd.DataFrame(loo_results)

print("\n" + "-" * 75)
print(f"Coefficient range: [{loo_df['coef'].min():.4f}%, {loo_df['coef'].max():.4f}%]")
print(f"All coefficients negative: {(loo_df['coef'] < 0).all()}")
print(f"All coefficients significant at p<0.05: {loo_df['significant'].all()}")
print(f"Firms significant at p<0.05: {loo_df['significant'].sum()} of {len(loo_df)}")
print(f"Firms significant at p<0.10: {(loo_df['pvalue'] < 0.10).sum()} of {len(loo_df)}")

# Check for any firm that kills the effect
kills_effect = loo_df[loo_df['coef'] > 0]
if len(kills_effect) > 0:
    print(f"\n*** ALERT: {len(kills_effect)} firm(s) produce POSITIVE coefficient when removed ***")
    for _, row in kills_effect.iterrows():
        print(f"    {row['firm']}: {row['coef']:.4f}%")
else:
    print(f"\n✓ No firm reverses the effect direction (all leave-one-out coefficients negative)")

# Check for any firm that makes effect insignificant
kills_significance = loo_df[~loo_df['significant']]
if len(kills_significance) > 0:
    print(f"\n*** ALERT: {len(kills_significance)} firm(s) make H2 INSIGNIFICANT when removed ***")
    for _, row in kills_significance.iterrows():
        print(f"    {row['firm']}: {row['coef']:.4f}% (p={row['pvalue']:.4f})")
else:
    print(f"\n✓ No single firm removal makes H2 insignificant (all p<0.05)")

loo_df.to_csv('outputs/defense_prep/h2_leave_one_out_sensitivity.csv', index=False)

# ============================================================================
# ANALYSIS 2: RANDOMIZATION INFERENCE
# ============================================================================
print("\n" + "=" * 80)
print("ANALYSIS 2: RANDOMIZATION INFERENCE (PLAUSIBILITY UNDER RANDOM ASSIGNMENT)")
print("=" * 80)

np.random.seed(42)
n_iterations = 1000

actual_coef = baseline.params['fcc_reportable']
print(f"\nActual H2 coefficient: {actual_coef:.4f}%")
print(f"Placebo iterations: {n_iterations}")

nonfcc_firms = df[df['fcc_reportable'] == False].groupby('cik').size()
n_fcc_firms = df[df['fcc_reportable'] == True]['cik'].nunique()
target_obs = int(df['fcc_reportable'].sum())

print(f"Treatment assignment: {n_fcc_firms} firms treated (10 non-FCC firms drawn per iteration)")
print(f"Target observations: ~{target_obs} treated observations")

placebo_coefs = []
df_ri = df.copy()

for iteration in range(n_iterations):
    # Randomly select the same NUMBER OF FIRMS (10) as placebo treated
    placebo_firms = np.random.choice(nonfcc_firms.index, size=n_fcc_firms, replace=False)

    # Create placebo: assign these non-FCC firms to treatment, exclude actual FCC firms
    df_placebo = df_ri[df_ri['fcc_reportable'] == False].copy()
    df_placebo['placebo_fcc'] = df_placebo['cik'].isin(placebo_firms).astype(float)

    X_p = sm.add_constant(df_placebo[['placebo_fcc'] + controls].astype(float))
    y_p = df_placebo['car_30d']
    try:
        m_p = sm.OLS(y_p, X_p).fit(cov_type='HC3')
        placebo_coefs.append(m_p.params['placebo_fcc'])
    except Exception:
        continue

placebo_coefs = np.array(placebo_coefs)

# RI p-values
ri_pvalue_onesided = np.mean(placebo_coefs <= actual_coef)
ri_pvalue_twosided = np.mean(np.abs(placebo_coefs) >= np.abs(actual_coef))
percentile = np.mean(placebo_coefs < actual_coef) * 100

print(f"\nPlacebo distribution (n={len(placebo_coefs)} successful iterations):")
print(f"  Mean: {placebo_coefs.mean():.4f}%")
print(f"  Std Dev: {placebo_coefs.std():.4f}%")
print(f"  Min: {placebo_coefs.min():.4f}%")
print(f"  5th percentile: {np.percentile(placebo_coefs, 5):.4f}%")
print(f"  10th percentile: {np.percentile(placebo_coefs, 10):.4f}%")
print(f"  Median: {np.percentile(placebo_coefs, 50):.4f}%")
print(f"  90th percentile: {np.percentile(placebo_coefs, 90):.4f}%")
print(f"  95th percentile: {np.percentile(placebo_coefs, 95):.4f}%")
print(f"  Max: {placebo_coefs.max():.4f}%")

print(f"\nActual coefficient relative to placebo distribution:")
print(f"  Percentile of actual in placebo dist: {percentile:.1f}th")
print(f"  Actual below 10th percentile: {actual_coef < np.percentile(placebo_coefs, 10)}")
print(f"  Actual below 5th percentile: {actual_coef < np.percentile(placebo_coefs, 5)}")

print(f"\nRandomization Inference p-values:")
print(f"  One-sided (coef <= actual): {ri_pvalue_onesided:.4f}")
print(f"  Two-sided (|coef| >= |actual|): {ri_pvalue_twosided:.4f}")

if percentile < 10:
    print(f"\n✓ STRONG: Actual coefficient is in the extreme 10% of placebo distribution")
    print(f"  This suggests the FCC effect is NOT due to random assignment")
else:
    print(f"\n*** ALERT: Actual coefficient is at the {percentile:.1f}th percentile ***")
    print(f"  The effect is NOT extreme under random assignment")
    print(f"  This raises concerns about whether H2 reflects a real causal effect")

np.save('outputs/defense_prep/ri_placebo_distribution.npy', placebo_coefs)

# ============================================================================
# ANALYSIS 3: WINSORIZED CARs
# ============================================================================
print("\n" + "=" * 80)
print("ANALYSIS 3: WINSORIZED CARs (OUTLIER ROBUSTNESS)")
print("=" * 80)

df_w = df.copy()
df_w['car_30d_w'] = winsorize(df_w['car_30d'], limits=[0.01, 0.01])

X_w = sm.add_constant(df_w[['fcc_reportable'] + controls].astype(float))
y_w = df_w['car_30d_w']
m_w = sm.OLS(y_w, X_w).fit(cov_type='HC3')

print(f"\nCAR Distributions:")
print(f"  Raw CAR range: [{df['car_30d'].min():.2f}%, {df['car_30d'].max():.2f}%]")
print(f"  Winsorized CAR range: [{df_w['car_30d_w'].min():.2f}%, {df_w['car_30d_w'].max():.2f}%]")
print(f"  N observations trimmed: {(df['car_30d'] != df_w['car_30d_w']).sum()}")

print(f"\nH2 Coefficient Comparison:")
print(f"  Raw CAR: {baseline.params['fcc_reportable']:.4f}% (p={baseline.pvalues['fcc_reportable']:.4f})")
print(f"  Winsorized: {m_w.params['fcc_reportable']:.4f}% (p={m_w.pvalues['fcc_reportable']:.4f})")
print(f"  Difference: {m_w.params['fcc_reportable'] - baseline.params['fcc_reportable']:.4f}pp")

print(f"\nAll Hypotheses under Winsorization:")
print(f"{'Variable':<30} {'Raw':>12} {'Winsorized':>12} {'Δ':>12}")
print("-" * 70)
for var in ['immediate_disclosure', 'fcc_reportable', 'prior_breaches_1yr', 'health_breach']:
    raw_coef = baseline.params[var]
    win_coef = m_w.params[var]
    delta = win_coef - raw_coef
    print(f"{var:<30} {raw_coef:>12.4f}% {win_coef:>12.4f}% {delta:>12.4f}pp")

print(f"\nP-value Comparison:")
print(f"{'Variable':<30} {'Raw':>12} {'Winsorized':>12}")
print("-" * 55)
for var in ['immediate_disclosure', 'fcc_reportable', 'prior_breaches_1yr', 'health_breach']:
    raw_p = baseline.pvalues[var]
    win_p = m_w.pvalues[var]
    print(f"{var:<30} {raw_p:>12.4f} {win_p:>12.4f}")

if abs(m_w.params['fcc_reportable'] - baseline.params['fcc_reportable']) > 0.5:
    print(f"\n*** ALERT: Winsorization changes H2 by >0.5pp ***")
    print(f"  This suggests H2 is sensitive to outliers")
else:
    print(f"\n✓ H2 robust to winsorization (change < 0.5pp)")

# ============================================================================
# SAVE COMPREHENSIVE SUMMARY
# ============================================================================
summary_output = []
summary_output.append("=" * 80)
summary_output.append("H2 ROBUSTNESS ANALYSIS: COMPREHENSIVE SUMMARY")
summary_output.append("=" * 80)

summary_output.append(f"\nBASELINE H2 RESULT")
summary_output.append(f"  Coefficient: {baseline.params['fcc_reportable']:.4f}%")
summary_output.append(f"  SE: {baseline.bse['fcc_reportable']:.4f}")
summary_output.append(f"  P-value: {baseline.pvalues['fcc_reportable']:.4f} **")
summary_output.append(f"  95% CI: [{baseline.params['fcc_reportable'] - 1.96*baseline.bse['fcc_reportable']:.4f}%, {baseline.params['fcc_reportable'] + 1.96*baseline.bse['fcc_reportable']:.4f}%]")
summary_output.append(f"  N: {len(df)}, N FCC firms: {df[df['fcc_reportable'] == True]['cik'].nunique()}")

summary_output.append(f"\nANALYSIS 1: LEAVE-ONE-OUT SENSITIVITY")
summary_output.append(f"  Coefficient range: [{loo_df['coef'].min():.4f}%, {loo_df['coef'].max():.4f}%]")
summary_output.append(f"  All negative: {(loo_df['coef'] < 0).all()}")
summary_output.append(f"  All significant (p<0.05): {loo_df['significant'].all()}")
summary_output.append(f"  Result: {'ROBUST - No firm kills effect' if (loo_df['coef'] < 0).all() and loo_df['significant'].all() else 'FRAGILE - Some sensitivity'}")

summary_output.append(f"\nANALYSIS 2: RANDOMIZATION INFERENCE")
summary_output.append(f"  Actual coefficient: {actual_coef:.4f}%")
summary_output.append(f"  Percentile in placebo dist: {percentile:.1f}th")
summary_output.append(f"  Below 10th percentile: {actual_coef < np.percentile(placebo_coefs, 10)}")
summary_output.append(f"  RI p-value (one-sided): {ri_pvalue_onesided:.4f}")
summary_output.append(f"  Result: {'EXTREME - Effect not due to random assignment' if percentile < 10 else 'NOT EXTREME - Assignment plausible'}")

summary_output.append(f"\nANALYSIS 3: WINSORIZED CARs")
summary_output.append(f"  Raw coefficient: {baseline.params['fcc_reportable']:.4f}%")
summary_output.append(f"  Winsorized coefficient: {m_w.params['fcc_reportable']:.4f}%")
summary_output.append(f"  Change: {m_w.params['fcc_reportable'] - baseline.params['fcc_reportable']:.4f}pp")
summary_output.append(f"  Result: {'ROBUST - Outliers do not drive effect' if abs(m_w.params['fcc_reportable'] - baseline.params['fcc_reportable']) < 0.5 else 'SENSITIVE - Outliers matter'}")

summary_output.append(f"\nOVERALL ASSESSMENT")
summary_output.append(f"  Leave-one-out: {'PASS' if (loo_df['coef'] < 0).all() and loo_df['significant'].all() else 'FAIL'}")
summary_output.append(f"  Randomization inference: {'PASS' if percentile < 10 else 'FAIL'}")
summary_output.append(f"  Winsorization: {'PASS' if abs(m_w.params['fcc_reportable'] - baseline.params['fcc_reportable']) < 0.5 else 'FAIL'}")

summary_text = "\n".join(summary_output)
with open('outputs/defense_prep/h2_robustness_comprehensive_summary.txt', 'w') as f:
    f.write(summary_text)

print("\n" + "=" * 80)
print("ALL THREE ANALYSES COMPLETE")
print("=" * 80)
print("\nOutputs saved:")
print("  - outputs/defense_prep/h2_leave_one_out_sensitivity.csv")
print("  - outputs/defense_prep/ri_placebo_distribution.npy")
print("  - outputs/defense_prep/h2_robustness_comprehensive_summary.txt")
