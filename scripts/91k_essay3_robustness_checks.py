"""
ESSAY 3: THREE ROBUSTNESS CHECKS
Check 1: Alternative Turnover Definitions
Check 2: Alternative Disclosure Thresholds
Check 3: Restricted Samples
"""

import pandas as pd
import numpy as np
import statsmodels.api as sm
from scipy.stats import norm
import warnings
warnings.filterwarnings('ignore')

print("=" * 90)
print("ESSAY 3: ROBUSTNESS CHECKS 1-3")
print("=" * 90)

# Load data
DATA_PATH = 'Data/processed/FINAL_DISSERTATION_DATASET_DEDUPLICATED_ENRICHED.csv'
df = pd.read_csv(DATA_PATH)

# Filter to CRSP sample
analysis_df = df[df['has_crsp_data'] == True].copy()
base_df = analysis_df[
    (analysis_df['executive_change_30d'].notna()) &
    (analysis_df['fcc_reportable'].notna())
].copy().dropna(subset=['firm_size_log', 'leverage', 'roa'])

# Convert bool to int
bool_cols = base_df.select_dtypes(include=['bool']).columns
for col in bool_cols:
    base_df[col] = base_df[col].astype(int)

windows = {'30d': 'executive_change_30d', '90d': 'executive_change_90d', '180d': 'executive_change_180d'}
controls = ['health_breach', 'prior_breaches_total', 'firm_size_log', 'leverage', 'roa']

# ============================================================================
# CHECK 1: ALTERNATIVE TURNOVER DEFINITIONS
# ============================================================================
print("\n" + "=" * 90)
print("CHECK 1: ALTERNATIVE TURNOVER DEFINITIONS")
print("=" * 90)

check1_results = []

# Check if successor origin data exists
has_successor_origin = 'successor_origin' in base_df.columns or 'external_hire' in base_df.columns

if not has_successor_origin:
    print("\nExternal Succession Indicator:")
    print("  Status: NOT AVAILABLE in current dataset")
    print("  Note: BoardEx successor origin data not imported in current pipeline")
    check1_results.append({
        'definition': 'External Succession',
        'status': 'Data not available',
        'result': 'Cannot be estimated'
    })
else:
    print("\nExternal Succession Analysis:")
    # If data exists, run analysis
    pass

# Long-tenure departure analysis
if 'ceo_tenure_years' in base_df.columns:
    print("\nLong-Tenure Departure (≥3 years tenure):")

    for window_label, dv_col in windows.items():
        long_tenure_df = base_df[base_df['ceo_tenure_years'] >= 3].copy()

        model_data = long_tenure_df[[dv_col] + ['fcc_reportable'] + controls].dropna().copy()
        model_data[dv_col] = model_data[dv_col].astype(int)

        if len(model_data) > 0:
            formula = f"{dv_col} ~ fcc_reportable + " + " + ".join(controls)
            res = sm.formula.logit(formula, data=model_data).fit(disp=0, maxiter=1000)

            # Calculate AME
            d0 = model_data.copy()
            d0['fcc_reportable'] = 0
            d1 = model_data.copy()
            d1['fcc_reportable'] = 1
            ame_pp = 100.0 * (res.predict(d1) - res.predict(d0)).mean()

            me = res.get_margeff(at="overall", method="dydx")
            exog_names = [n for n in res.model.exog_names if n != "Intercept"]
            se_ame_pp = me.margeff_se[exog_names.index('fcc_reportable')] * 100

            check1_results.append({
                'definition': f'Long-Tenure Departure (≥3 years)',
                'window': window_label,
                'n': len(model_data),
                'fcc_coef': round(res.params['fcc_reportable'], 4),
                'fcc_se': round(res.bse['fcc_reportable'], 4),
                'fcc_p': round(res.pvalues['fcc_reportable'], 4),
                'ame_pp': round(ame_pp, 2)
            })

            print(f"  {window_label.upper()}: N={len(model_data)}, coef={res.params['fcc_reportable']:.4f}, p={res.pvalues['fcc_reportable']:.4f}, AME={ame_pp:.2f}pp")
else:
    print("\nLong-Tenure Departure:")
    print("  Status: CEO tenure data not available in current dataset")
    check1_results.append({
        'definition': 'Long-Tenure Departure (≥3 years)',
        'status': 'Data not available',
        'result': 'Cannot be estimated'
    })

check1_df = pd.DataFrame(check1_results)
check1_df.to_csv('outputs/tables/essay3_governance/robustness_check1_turnover_definitions.csv', index=False)
print(f"\n[OK] Saved Check 1 results")

# ============================================================================
# CHECK 2: ALTERNATIVE DISCLOSURE THRESHOLDS
# ============================================================================
print("\n" + "=" * 90)
print("CHECK 2: ALTERNATIVE DISCLOSURE THRESHOLDS")
print("=" * 90)

check2_results = []

# Create alternative threshold indicators
base_df['immediate_disclosure_5d'] = (base_df['disclosure_delay_days'] <= 5).astype(int)
base_df['immediate_disclosure_10d'] = (base_df['disclosure_delay_days'] <= 10).astype(int)
base_df['immediate_disclosure_14d'] = (base_df['disclosure_delay_days'] <= 14).astype(int)

thresholds = {
    '5-day': 'immediate_disclosure_5d',
    '10-day': 'immediate_disclosure_10d',
    '14-day': 'immediate_disclosure_14d'
}

window_30d = 'executive_change_30d'

for threshold_label, mediator_col in thresholds.items():
    print(f"\n{threshold_label.upper()} threshold:")

    # Mediation model at 30-day window
    model_data = base_df[[window_30d, 'fcc_reportable', mediator_col] + controls].dropna().copy()
    model_data[window_30d] = model_data[window_30d].astype(int)
    model_data['fcc_reportable'] = model_data['fcc_reportable'].astype(int)
    model_data[mediator_col] = model_data[mediator_col].astype(int)

    if len(model_data) > 0:
        formula = f"{window_30d} ~ fcc_reportable + {mediator_col} + " + " + ".join(controls)
        res = sm.formula.logit(formula, data=model_data).fit(disp=0, maxiter=1000)

        print(f"  N={len(model_data)}")
        print(f"  FCC coef={res.params['fcc_reportable']:.4f}, SE={res.bse['fcc_reportable']:.4f}, p={res.pvalues['fcc_reportable']:.4f}")
        print(f"  {mediator_col} coef={res.params[mediator_col]:.4f}, SE={res.bse[mediator_col]:.4f}, p={res.pvalues[mediator_col]:.4f}")

        check2_results.append({
            'threshold': threshold_label,
            'n': len(model_data),
            'fcc_coef': round(res.params['fcc_reportable'], 4),
            'fcc_se': round(res.bse['fcc_reportable'], 4),
            'fcc_p': round(res.pvalues['fcc_reportable'], 4),
            'mediator_coef': round(res.params[mediator_col], 4),
            'mediator_se': round(res.bse[mediator_col], 4),
            'mediator_p': round(res.pvalues[mediator_col], 4)
        })

check2_df = pd.DataFrame(check2_results)
check2_df.to_csv('outputs/tables/essay3_governance/robustness_check2_disclosure_thresholds.csv', index=False)
print(f"\n[OK] Saved Check 2 results")

# ============================================================================
# CHECK 3: RESTRICTED SAMPLES
# ============================================================================
print("\n" + "=" * 90)
print("CHECK 3: RESTRICTED SAMPLES")
print("=" * 90)

check3_results = []

# Define sample restrictions
restrictions = {
    'Unambiguous dates': base_df[base_df['disclosure_delay_days'].notna()].copy(),
    'Large firms (>$100M)': base_df[base_df['firm_size_log'] >= np.log(100)].copy(),
    'Complete data': base_df.copy()  # Already dropna'd on controls
}

for restriction_label, restricted_df in restrictions.items():
    print(f"\n{restriction_label.upper()}:")
    print(f"  N remaining: {len(restricted_df)}")

    for window_label, dv_col in windows.items():
        model_data = restricted_df[[dv_col] + ['fcc_reportable'] + controls].dropna().copy()
        model_data[dv_col] = model_data[dv_col].astype(int)

        if len(model_data) > 10:
            formula = f"{dv_col} ~ fcc_reportable + " + " + ".join(controls)
            res = sm.formula.logit(formula, data=model_data).fit(disp=0, maxiter=1000)

            # Calculate AME
            d0 = model_data.copy()
            d0['fcc_reportable'] = 0
            d1 = model_data.copy()
            d1['fcc_reportable'] = 1
            ame_pp = 100.0 * (res.predict(d1) - res.predict(d0)).mean()

            print(f"  {window_label.upper()}: n={len(model_data)}, coef={res.params['fcc_reportable']:.4f}, p={res.pvalues['fcc_reportable']:.4f}, AME={ame_pp:.2f}pp")

            check3_results.append({
                'restriction': restriction_label,
                'window': window_label,
                'n': len(model_data),
                'fcc_coef': round(res.params['fcc_reportable'], 4),
                'fcc_se': round(res.bse['fcc_reportable'], 4),
                'fcc_p': round(res.pvalues['fcc_reportable'], 4),
                'ame_pp': round(ame_pp, 2)
            })

check3_df = pd.DataFrame(check3_results)
check3_df.to_csv('outputs/tables/essay3_governance/robustness_check3_restricted_samples.csv', index=False)
print(f"\n[OK] Saved Check 3 results")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 90)
print("[COMPLETE] All three robustness checks finished")
print("=" * 90)
print("\nResults saved to:")
print("  1. robustness_check1_turnover_definitions.csv")
print("  2. robustness_check2_disclosure_thresholds.csv")
print("  3. robustness_check3_restricted_samples.csv")
