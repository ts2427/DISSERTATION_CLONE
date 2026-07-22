"""
ESSAY 3: OLS LINEAR PROBABILITY MODEL & NEGATIVE BINOMIAL REGRESSION
Alternative model specifications for robustness
"""

import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.formula.api import ols, logit
from statsmodels.genmod.generalized_linear_model import GLM
from statsmodels.genmod.families import NegativeBinomial
import warnings
warnings.filterwarnings('ignore')

print("=" * 90)
print("ESSAY 3: OLS LPM & NEGATIVE BINOMIAL ROBUSTNESS CHECKS")
print("=" * 90)

# Load data
DATA_PATH = 'Data/processed/FINAL_DISSERTATION_DATASET_DEDUPLICATED_ENRICHED.csv'
df = pd.read_csv(DATA_PATH)

# Filter to CRSP sample with turnover data
analysis_df = df[df['has_crsp_data'] == True].copy()
turnover_df = analysis_df[
    (analysis_df['executive_change_30d'].notna()) &
    (analysis_df['fcc_reportable'].notna())
].copy().dropna(subset=['firm_size_log', 'leverage', 'roa'])

# Convert bool to int
bool_cols = turnover_df.select_dtypes(include=['bool']).columns
for col in bool_cols:
    turnover_df[col] = turnover_df[col].astype(int)

print(f"\n[SAMPLE] {len(turnover_df):,} breaches with complete data")

# Define windows and controls
windows = {'30d': 'executive_change_30d', '90d': 'executive_change_90d', '180d': 'executive_change_180d'}
controls = ['health_breach', 'prior_breaches_total', 'firm_size_log', 'leverage', 'roa']

# ============================================================================
# PART 1: OLS LINEAR PROBABILITY MODEL
# ============================================================================
print("\n" + "=" * 90)
print("PART 1: OLS LINEAR PROBABILITY MODEL (Alternative to Logit)")
print("=" * 90)

ols_results = []

for window_label, dv_col in windows.items():
    print(f"\n[{window_label.upper()} WINDOW]")

    model_data = turnover_df[[dv_col] + ['fcc_reportable'] + controls].dropna().copy()
    model_data[dv_col] = model_data[dv_col].astype(int)

    formula = f"{dv_col} ~ fcc_reportable + " + " + ".join(controls)
    res = sm.formula.ols(formula, data=model_data).fit(cov_type='HC3')

    fcc_coef = res.params['fcc_reportable']
    fcc_se = res.bse['fcc_reportable']
    fcc_t = res.tvalues['fcc_reportable']
    fcc_p = res.pvalues['fcc_reportable']

    print(f"  Sample size: {len(model_data):,}")
    print(f"  FCC coefficient (pp): {fcc_coef:.4f}")
    print(f"  Std Error: {fcc_se:.4f}")
    print(f"  t-statistic: {fcc_t:.4f}")
    print(f"  P-value: {fcc_p:.4f}")
    print(f"  Interpretation: {'SIGNIFICANT' if fcc_p < 0.05 else 'NOT SIGNIFICANT'}")

    ols_results.append({
        'window': window_label,
        'fcc_coefficient_pp': round(fcc_coef, 4),
        'fcc_se': round(fcc_se, 4),
        'fcc_t': round(fcc_t, 4),
        'fcc_p': round(fcc_p, 4),
        'significant': 'Yes' if fcc_p < 0.05 else 'No'
    })

# Save OLS results
ols_df = pd.DataFrame(ols_results)
ols_df.to_csv('outputs/tables/essay3_governance/ols_lpm_h6_results.csv', index=False)
print(f"\n[OK] Saved OLS LPM results to: outputs/tables/essay3_governance/ols_lpm_h6_results.csv")

# ============================================================================
# PART 2: NEGATIVE BINOMIAL REGRESSION
# ============================================================================
print("\n" + "=" * 90)
print("PART 2: NEGATIVE BINOMIAL REGRESSION (Multiple Turnover Events)")
print("=" * 90)

# Check for multiple turnover variable
if 'num_changes_180d' not in turnover_df.columns:
    print("\n[ERROR] num_changes_180d not found in dataset")
else:
    print(f"\nMultiple turnover variable 'num_changes_180d' found")
    print(f"  Mean events: {turnover_df['num_changes_180d'].mean():.2f}")
    print(f"  Range: {turnover_df['num_changes_180d'].min():.0f} to {turnover_df['num_changes_180d'].max():.0f}")

    # Prepare data for negative binomial
    nb_data = turnover_df[['num_changes_180d', 'fcc_reportable'] + controls].dropna().copy()
    nb_data['num_changes_180d'] = nb_data['num_changes_180d'].astype(int)
    nb_data['fcc_reportable'] = nb_data['fcc_reportable'].astype(int)

    # Fit negative binomial model
    formula_nb = "num_changes_180d ~ fcc_reportable + " + " + ".join(controls)

    try:
        # Use generalized linear model with negative binomial family
        nb_model = GLM.from_formula(formula_nb, data=nb_data, family=NegativeBinomial()).fit()

        fcc_coef_nb = nb_model.params['fcc_reportable']
        fcc_se_nb = nb_model.bse['fcc_reportable']
        fcc_z_nb = nb_model.tvalues['fcc_reportable']
        fcc_p_nb = nb_model.pvalues['fcc_reportable']

        # Calculate IRR (Incidence Rate Ratio) = exp(coefficient)
        fcc_irr = np.exp(fcc_coef_nb)

        print(f"\nNegative Binomial Model (Dependent Variable: num_changes_180d)")
        print(f"  Sample size: {len(nb_data):,}")
        print(f"  FCC coefficient: {fcc_coef_nb:.4f}")
        print(f"  Std Error: {fcc_se_nb:.4f}")
        print(f"  z-statistic: {fcc_z_nb:.4f}")
        print(f"  P-value: {fcc_p_nb:.4f}")
        print(f"  Incidence Rate Ratio (exp(coef)): {fcc_irr:.4f}")
        print(f"  Interpretation: FCC firms have {(fcc_irr-1)*100:.2f}% change in expected count of turnover events")
        print(f"  Significant: {'YES' if fcc_p_nb < 0.05 else 'NO'}")

        # Save negative binomial results
        nb_results = pd.DataFrame([{
            'model': 'Negative Binomial (Multiple Turnover Events 180d)',
            'n_obs': len(nb_data),
            'fcc_coefficient': round(fcc_coef_nb, 4),
            'fcc_se': round(fcc_se_nb, 4),
            'fcc_z': round(fcc_z_nb, 4),
            'fcc_p': round(fcc_p_nb, 4),
            'fcc_irr': round(fcc_irr, 4),
            'significant': 'Yes' if fcc_p_nb < 0.05 else 'No'
        }])

        nb_results.to_csv('outputs/tables/essay3_governance/negative_binomial_h6_results.csv', index=False)
        print(f"\n[OK] Saved Negative Binomial results to: outputs/tables/essay3_governance/negative_binomial_h6_results.csv")

    except Exception as e:
        print(f"\n[ERROR] Negative binomial model failed: {str(e)}")

print("\n" + "=" * 90)
print("[COMPLETE] OLS LPM and Negative Binomial analysis finished")
print("=" * 90)
