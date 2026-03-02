"""
EXTENDED GOVERNANCE WINDOWS ANALYSIS
Analysis #5: Long-Horizon Executive Turnover Response

Tests whether governance response (executive turnover) is immediate (30 days, Essay 3)
or delayed (90 and 180 days).

Hypothesis: Governance response strengthens at longer windows because:
1. 30 days: Immediate crisis response, few changes
2. 90 days: Board begins deliberation, more changes
3. 180 days: Full governance cycle, maximum changes

Alternative: FCC effect diminishes over time as crisis fades (recency bias).

This validates Essay 3's mechanism and shows whether governance response is
immediate/temporary or sustained/structural.
"""

import pandas as pd
import numpy as np
import warnings

warnings.filterwarnings('ignore')

print("=" * 90)
print("EXTENDED GOVERNANCE WINDOWS ANALYSIS - Analysis #5")
print("=" * 90)

# ============================================================================
# SECTION 1: DATA LOADING
# ============================================================================

print("\n[1/6] Loading data...")

df = pd.read_csv('Data/processed/FINAL_DISSERTATION_DATASET_WITH_CVSS.csv')
print(f"  [OK] {len(df):,} breach observations")

# ============================================================================
# SECTION 2: GOVERNANCE WINDOW ANALYSIS
# ============================================================================

print("\n[2/6] Analyzing executive turnover across windows...")

exec_windows = {
    '30d': 'executive_change_30d',
    '90d': 'executive_change_90d',
    '180d': 'executive_change_180d'
}

print("\n  Executive turnover by window:")
for window, col in exec_windows.items():
    if col in df.columns:
        count = df[col].sum()
        pct = df[col].mean() * 100
        print(f"    {window:5s}: {count:>4.0f} ({pct:>5.1f}%)")

print("\n  Executive turnover by FCC and window:")
for window, col in exec_windows.items():
    if col in df.columns:
        fcc_rate = df[df['fcc_reportable']==1][col].mean() * 100
        non_fcc_rate = df[df['fcc_reportable']==0][col].mean() * 100
        diff = fcc_rate - non_fcc_rate
        print(f"\n    {window}:")
        print(f"      Non-FCC: {non_fcc_rate:>5.1f}%")
        print(f"      FCC: {fcc_rate:>5.1f}%")
        print(f"      Difference: {diff:>+5.1f}pp")

# ============================================================================
# SECTION 3: REGRESSION MODELS - COMPARE WINDOWS
# ============================================================================

print("\n[3/6] Running logistic regression models by window...")

try:
    import statsmodels.api as sm
    from statsmodels.formula.api import logit
except ImportError:
    print("  Installing statsmodels...")
    import subprocess
    subprocess.check_call(['pip', 'install', '-q', 'statsmodels'])
    import statsmodels.api as sm
    from statsmodels.formula.api import logit

# Results storage
results_by_window = {}

for window_label, col_name in exec_windows.items():
    print(f"\n  ===== {window_label.upper()} WINDOW =====")

    # Prepare data
    reg_data = df[
        (df[col_name].notna()) &
        (col_name in df.columns)
    ].copy()

    reg_data['outcome'] = reg_data[col_name].astype(int)
    reg_data['fcc'] = reg_data['fcc_reportable'].astype(int)
    reg_data['health'] = reg_data['health_breach'].astype(int)
    reg_data['financial'] = reg_data['financial_breach'].astype(int)
    reg_data['prior_breaches'] = reg_data['prior_breaches_total'].fillna(0)

    print(f"    Sample: {len(reg_data):,} breaches")
    print(f"    Outcome rate: {reg_data['outcome'].mean()*100:.1f}%")

    # Model: Simple logistic regression
    model = logit('outcome ~ fcc + health + financial + prior_breaches + firm_size_log',
                  data=reg_data).fit(disp=0, cov_type='HC3')

    coef_fcc = model.params['fcc[T.1]'] if 'fcc[T.1]' in model.params.index else model.params['fcc']
    pval_fcc = model.pvalues['fcc[T.1]'] if 'fcc[T.1]' in model.params.index else model.pvalues['fcc']

    # Convert log-odds to probability percentage points
    # For binary FCC (0→1), effect is approximately: exp(coef) - 1 in log-odds
    # Approximate percentage point effect: coef * 25 (rule of thumb for logit)
    pp_effect = coef_fcc * 25

    print(f"    FCC Log-Odds Coefficient: {coef_fcc:.4f} (p={pval_fcc:.4f})")
    print(f"    Approximate PP Effect: {pp_effect:.4f}pp")
    print(f"    AIC: {model.aic:.0f}")

    results_by_window[window_label] = {
        'coef': coef_fcc,
        'pval': pval_fcc,
        'pp_effect': pp_effect,
        'n': len(reg_data),
        'outcome_rate': reg_data['outcome'].mean() * 100
    }

# ============================================================================
# SECTION 4: COMPARISON ACROSS WINDOWS
# ============================================================================

print("\n[4/6] Comparison across windows...")

print("\n  FCC Effect Strengthening:")
for window in ['30d', '90d', '180d']:
    if window in results_by_window:
        res = results_by_window[window]
        print(f"    {window}: Coef={res['coef']:+.4f}, PP={res['pp_effect']:+.4f}pp (p={res['pval']:.4f})")

print("\n  Pattern Test:")
coef_30 = results_by_window['30d']['coef']
coef_90 = results_by_window['90d']['coef']
coef_180 = results_by_window['180d']['coef']

if coef_30 < coef_90 < coef_180 and coef_180 < 0:
    print("    STRENGTHENING PATTERN: |FCC effect| increases from 30d → 90d → 180d")
    print("    Interpretation: Governance response is SUSTAINED and CUMULATIVE")
elif coef_30 < 0 and coef_90 < coef_30 and coef_180 < coef_90:
    print("    SUSTAINED PATTERN: FCC effect present and consistent across windows")
    print("    Interpretation: Governance response is IMMEDIATE and STABLE")
else:
    print("    NO CLEAR PATTERN: Effects vary across windows")
    print("    Interpretation: Governance response may be crisis-dependent")

# ============================================================================
# SECTION 5: SAVE RESULTS
# ============================================================================

print("\n[5/6] Saving results...")

results_table = pd.DataFrame({
    'Window': list(results_by_window.keys()),
    'N': [results_by_window[w]['n'] for w in results_by_window.keys()],
    'Baseline_Rate': [f"{results_by_window[w]['outcome_rate']:.1f}%" for w in results_by_window.keys()],
    'FCC_Log_Odds': [f"{results_by_window[w]['coef']:.4f}" for w in results_by_window.keys()],
    'Approx_PP_Effect': [f"{results_by_window[w]['pp_effect']:.4f}pp" for w in results_by_window.keys()],
    'P_Value': [f"{results_by_window[w]['pval']:.4f}" for w in results_by_window.keys()]
})

results_table.to_csv('outputs/tables/TABLE_EXTENDED_GOVERNANCE_WINDOWS_RESULTS.csv', index=False)
print(f"  [OK] Saved: TABLE_EXTENDED_GOVERNANCE_WINDOWS_RESULTS.csv")

# Essay 3 comparison
print("\n[6/6] Essay 3 Consistency Check...")

print("\n  Essay 3 Main Result (from README):")
print(f"    FCC effect on 30d turnover: +5.3pp*** (logit equivalent)")
print(f"\n  Analysis #5 Result (30d window):")
print(f"    Coefficient: {results_by_window['30d']['coef']:.4f}")
print(f"    Approx PP: {results_by_window['30d']['pp_effect']:.4f}pp")
print(f"    Status: {'CONSISTENT' if abs(results_by_window['30d']['pp_effect'] - 5.3) < 2.0 else 'DIFFERS'} with Essay 3")

print("\n" + "=" * 90)
print("ANALYSIS #5 COMPLETE")
print("=" * 90)
