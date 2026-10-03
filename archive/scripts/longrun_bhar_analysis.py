"""
LONG-RUN BHAR ANALYSIS
========================================================================

Tests whether FCC regulation penalty persists, reverts, or exhibits
long-run drift. Converts "persistence beyond scope" limitation into finding.

BHAR windows: 90-day, 180-day, 365-day
Compares to 30-day CAR baseline (main result)
"""

import pandas as pd
import numpy as np
import statsmodels.api as sm
import warnings
warnings.filterwarnings('ignore')

print("=" * 90)
print("LONG-RUN BHAR ANALYSIS")
print("=" * 90)

# Load data
df = pd.read_csv('Data/processed/FINAL_DISSERTATION_DATASET_DEDUPLICATED_ENRICHED.csv')
df = df.dropna(subset=['firm_size_log', 'leverage', 'roa'])

# Check for available BHAR windows
bhar_cols = [c for c in df.columns if 'bhar' in c.lower()]
print(f"\nAvailable BHAR columns: {bhar_cols}")

# Canonical specification for comparison
controls = ['immediate_disclosure', 'fcc_reportable', 'prior_breaches_1yr',
            'health_breach', 'firm_size_log', 'leverage', 'roa']

# Collect results across windows
results = []

# Try different BHAR windows
windows = ['bhar_5d', 'bhar_30d', 'bhar_60d', 'bhar_90d', 'bhar_180d']
windows_available = [w for w in windows if w in df.columns]

if not windows_available:
    print("\nNo BHAR windows found in dataset.")
    print("Available columns suggest BHAR may not be pre-calculated.")
    print("Using CAR as proxy for long-run analysis.")
    windows_available = ['car_30d']

print(f"\nAnalyzing windows: {windows_available}\n")

for window in windows_available:
    df_clean = df.dropna(subset=[window] + controls)

    X = sm.add_constant(df_clean[controls].astype(float))
    y = df_clean[window]
    m = sm.OLS(y, X).fit(cov_type='HC3')

    results.append({
        'Window': window,
        'N': int(m.nobs),
        'FCC_Coef': m.params['fcc_reportable'],
        'FCC_SE': m.bse['fcc_reportable'],
        'FCC_P': m.pvalues['fcc_reportable'],
        'H1_Coef': m.params['immediate_disclosure'],
        'H1_P': m.pvalues['immediate_disclosure'],
        'R_squared': m.rsquared
    })

results_df = pd.DataFrame(results)

print("LONG-RUN RESULTS")
print("=" * 90)
print(results_df.to_string(index=False))

print(f"\n{'=' * 90}")
print("INTERPRETATION")
print(f"{'=' * 90}\n")

if len(results) > 1:
    baseline_fcc = results[0]['FCC_Coef']
    print(f"30-day FCC effect (baseline): {baseline_fcc:.4f}%")

    for i in range(1, len(results)):
        window = results[i]['Window']
        fcc_coef = results[i]['FCC_Coef']
        change = fcc_coef - baseline_fcc

        print(f"{window:12s} FCC effect: {fcc_coef:>7.4f}% (change from baseline: {change:+.4f}pp)")

    # Test for persistence vs reversion
    print(f"\nPersistence assessment:")
    if all(results[i]['FCC_Coef'] < 0 for i in range(len(results))):
        print("  Pattern: FCC penalty persists across all windows")
        if abs(results[-1]['FCC_Coef']) < abs(baseline_fcc):
            print("  Trajectory: Partial mean reversion (penalty decays)")
        else:
            print("  Trajectory: Stable or increasing penalty")
    else:
        print("  Pattern: Mixed - some windows show reversal or positive return")

print(f"\n{'=' * 90}\n")

# Save results
results_df.to_csv('outputs/longrun_bhar_results.csv', index=False)
print(f"Results saved to outputs/longrun_bhar_results.csv")
