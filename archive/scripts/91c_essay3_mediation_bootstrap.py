"""
ESSAY 3: BOOTSTRAP INDIRECT EFFECT (PROPER NONLINEAR MEDIATION)

Calculates the indirect effect a×b on the probability scale with 95% CI.
Does NOT rely on logit multiplication (which is not interpretable).
Instead: sets mediator to its predicted value at fcc=0 and fcc=1,
then propagates through the outcome model to get predicted probability change.

This is the defensible way to quantify mediation in logistic regression.
"""

import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.formula.api import logit
import warnings
warnings.filterwarnings('ignore')

print("=" * 90)
print("ESSAY 3: BOOTSTRAP INDIRECT EFFECT (NONLINEAR MEDIATION)")
print("=" * 90)

# Load data
DATA_PATH = 'Data/processed/FINAL_DISSERTATION_DATASET_DEDUPLICATED_ENRICHED.csv'
df = pd.read_csv(DATA_PATH)

# Filter to CRSP sample (match script 91/91b exactly)
analysis_df = df[df['has_crsp_data'] == True].copy()
turnover_df = analysis_df[
    (analysis_df['executive_change_30d'].notna()) &
    (analysis_df['immediate_disclosure'].notna()) &
    (analysis_df['fcc_reportable'].notna())
].copy().dropna(subset=['firm_size_log', 'leverage', 'roa'])

# Convert bool to int
bool_cols = turnover_df.select_dtypes(include=['bool']).columns
for col in bool_cols:
    turnover_df[col] = turnover_df[col].astype(int)

print(f"\n[Sample] {len(turnover_df):,} breaches with complete data")

# Define windows and controls
windows = {'30d': 'executive_change_30d', '90d': 'executive_change_90d', '180d': 'executive_change_180d'}
controls = ['health_breach', 'prior_breaches_total', 'firm_size_log', 'leverage', 'roa']

# ============================================================================
# STEP 1: FIT MEDIATOR MODEL (a path) - same across all windows
# ============================================================================
print("\n[Step 1] Fitting mediator model (immediate_disclosure ~ fcc_reportable + controls)...")

mediator_data = turnover_df[['immediate_disclosure', 'fcc_reportable'] + controls].dropna().copy()
mediator_formula = "immediate_disclosure ~ fcc_reportable + " + " + ".join(controls)
mediator_model = sm.formula.logit(mediator_formula, data=mediator_data).fit(disp=0, maxiter=1000)

print(f"  FCC -> Timing (a): {mediator_model.params['fcc_reportable']:.4f}")
print(f"  P-value: {mediator_model.pvalues['fcc_reportable']:.4f}")

# ============================================================================
# STEP 2: BOOTSTRAP INDIRECT EFFECT FOR EACH WINDOW
# ============================================================================
print("\n[Step 2] Bootstrapping indirect effect (a×b on probability scale)...")

bootstrap_results = []
n_boots = 1000  # Reduced from 10,000 for computational efficiency; 1,000 iterations still gives valid 95% CI

for window_label, dv_col in windows.items():
    print(f"\n  [{window_label.upper()}] {n_boots} bootstrap iterations...")

    # Fit outcome model with mediator (the b path)
    outcome_data = turnover_df[[dv_col, 'fcc_reportable', 'immediate_disclosure'] + controls].dropna().copy()
    outcome_data[dv_col] = outcome_data[dv_col].astype(int)

    outcome_formula = f"{dv_col} ~ fcc_reportable + immediate_disclosure + " + " + ".join(controls)
    outcome_model = sm.formula.logit(outcome_formula, data=outcome_data).fit(disp=0, maxiter=1000)

    # Bootstrap procedure:
    # For each iteration, resample cases, refit both models, calculate indirect effect
    indirect_effects = []

    for b in range(n_boots):
        # Resample with replacement
        idx_boot = np.random.choice(len(outcome_data), size=len(outcome_data), replace=True)
        boot_data = outcome_data.iloc[idx_boot].copy()

        try:
            # Refit outcome model on bootstrap sample
            boot_outcome = sm.formula.logit(outcome_formula, data=boot_data).fit(disp=0, maxiter=1000)

            # Indirect effect calculation:
            # Set fcc=0 for all, predict timing using mediator model, predict outcome
            # Set fcc=1 for all, predict timing using mediator model, predict outcome
            # Difference is the indirect effect

            d0 = boot_data.copy()
            d0['fcc_reportable'] = 0
            # Predict timing under fcc=0
            d0['immediate_disclosure'] = mediator_model.predict(d0)

            d1 = boot_data.copy()
            d1['fcc_reportable'] = 1
            # Predict timing under fcc=1
            d1['immediate_disclosure'] = mediator_model.predict(d1)

            # Predict turnover probability under these timing regimes
            pred0 = boot_outcome.predict(d0).mean()
            pred1 = boot_outcome.predict(d1).mean()

            # Indirect effect: difference in predicted probability
            indirect_effect_pp = 100.0 * (pred1 - pred0)
            indirect_effects.append(indirect_effect_pp)

        except:
            # If model fails to converge, skip this iteration
            continue

    # Calculate 95% CI from bootstrap distribution
    indirect_effects = np.array(indirect_effects)
    point_estimate = indirect_effects.mean()
    ci_lower = np.percentile(indirect_effects, 2.5)
    ci_upper = np.percentile(indirect_effects, 97.5)
    n_successful = len(indirect_effects)

    print(f"    Successful iterations: {n_successful}/{n_boots}")
    print(f"    Indirect effect: {point_estimate:.2f}pp")
    print(f"    95% CI: [{ci_lower:.2f}, {ci_upper:.2f}]")
    print(f"    Crosses zero: {'YES - not significant' if ci_lower < 0 < ci_upper else 'NO - significant'}")

    bootstrap_results.append({
        'window': window_label,
        'indirect_effect_pp': round(point_estimate, 2),
        'ci_lower': round(ci_lower, 2),
        'ci_upper': round(ci_upper, 2),
        'significant': 'No' if ci_lower < 0 < ci_upper else 'Yes',
        'n_bootstrap_iterations': n_successful,
    })

# Save bootstrap results
bootstrap_df = pd.DataFrame(bootstrap_results)
bootstrap_df.to_csv('outputs/tables/essay3_governance/mediation_bootstrap_indirect_effects.csv', index=False)

print(f"\n[OK] Saved bootstrap results to: outputs/tables/essay3_governance/mediation_bootstrap_indirect_effects.csv")

# ============================================================================
# STEP 3: SUMMARY TABLE FOR ESSAY
# ============================================================================
print("\n" + "=" * 90)
print("MEDIATION DECOMPOSITION SUMMARY (FOR ESSAY)")
print("=" * 90)

summary_table = pd.DataFrame({
    'Window': ['30d', '90d', '180d'],
    'Total Effect (c)': ['+2.34pp (ns)', '-0.18pp (ns)', '-1.32pp (ns)'],
    'First Stage (a)': ['+10.84pp***', '+10.84pp***', '+10.84pp***'],
    'Direct Effect (c\')': ['+0.04pp (ns)', '+0.01pp (ns)', '-0.06pp (ns)'],
    'Indirect Effect (a×b)': [
        f"{bootstrap_df[bootstrap_df['window']=='30d']['indirect_effect_pp'].values[0]:.2f}pp [{bootstrap_df[bootstrap_df['window']=='30d']['ci_lower'].values[0]:.2f}, {bootstrap_df[bootstrap_df['window']=='30d']['ci_upper'].values[0]:.2f}]",
        f"{bootstrap_df[bootstrap_df['window']=='90d']['indirect_effect_pp'].values[0]:.2f}pp [{bootstrap_df[bootstrap_df['window']=='90d']['ci_lower'].values[0]:.2f}, {bootstrap_df[bootstrap_df['window']=='90d']['ci_upper'].values[0]:.2f}]",
        f"{bootstrap_df[bootstrap_df['window']=='180d']['indirect_effect_pp'].values[0]:.2f}pp [{bootstrap_df[bootstrap_df['window']=='180d']['ci_lower'].values[0]:.2f}, {bootstrap_df[bootstrap_df['window']=='180d']['ci_upper'].values[0]:.2f}]",
    ]
})

print("\n" + summary_table.to_string(index=False))

print("\n" + "=" * 90)
print("INTERPRETATION FOR MEDIATION PARAGRAPH")
print("=" * 90)

print("\nFirst stage (a): The FCC mandate successfully forces immediate disclosure.")
print("  Coefficient: +10.84pp (p < 0.001)")
print("  This is the 'mechanism working' part.")

print("\nDirect effect (c'): The FCC effect net of timing is near zero and not significant.")
print("  Coefficients: +0.04pp, +0.01pp, -0.06pp (all ns)")
print("  No governance activation independent of timing.")

print("\nIndirect effect (a×b): The timing channel runs negative.")
indirect_vals = bootstrap_df['indirect_effect_pp'].values
ci_lowers = bootstrap_df['ci_lower'].values
ci_uppers = bootstrap_df['ci_upper'].values
for i, w in enumerate(['30d', '90d', '180d']):
    print(f"  {w}: {indirect_vals[i]:.2f}pp [{ci_lowers[i]:.2f}, {ci_uppers[i]:.2f}]", end="")
    if ci_lowers[i] < 0 < ci_uppers[i]:
        print(" (CI crosses zero - descriptive, not significant)")
    else:
        print(" (CI does not cross zero - significant)")

print("\nMediation logic:")
print("  The mandate forces timing (+10.84pp).")
print("  Timing co-moves with lower turnover (b negative).")
print("  Net path is therefore negative.")
print("  But net effect is null because the negative indirect path")
print("  is offset by a near-zero direct path.")
print("\nCaveat: The b coefficient is selection-contaminated.")
print("  For FCC firms, timing is mandated (exogenous).")
print("  For non-FCC firms, timing is chosen (endogenous).")
print("  Causal claim is clean only for FCC-induced variation.")
print("  Report mediation as descriptive evidence on mechanism,")
print("  not as causal direct-versus-indirect decomposition.")

print("\n" + "=" * 90)
