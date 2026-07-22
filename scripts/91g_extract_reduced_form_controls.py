"""Quick extraction of control variable coefficients and p-values from reduced-form H6."""

import pandas as pd
import statsmodels.formula.api as smf
import numpy as np

print("Extracting reduced-form H6 control variable significance...")

# Load data
df = pd.read_csv('Data/processed/FINAL_DISSERTATION_DATASET_DEDUPLICATED_ENRICHED.csv')

# Filter to canonical H6 sample
analysis_df = df[df['has_crsp_data'] == True].copy()
analysis_df = analysis_df[
    (analysis_df['executive_change_30d'].notna()) &
    (analysis_df['immediate_disclosure'].notna()) &
    (analysis_df['fcc_reportable'].notna())
].copy().dropna(subset=['firm_size_log', 'leverage', 'roa'])

bool_cols = analysis_df.select_dtypes(include=['bool']).columns
for col in bool_cols:
    analysis_df[col] = analysis_df[col].astype(int)

windows = {
    '30d': 'executive_change_30d',
    '90d': 'executive_change_90d',
    '180d': 'executive_change_180d'
}

controls = ['health_breach', 'prior_breaches_total', 'firm_size_log', 'leverage', 'roa']

rows = []

for window_label, dv_col in windows.items():
    print(f"\n[{window_label.upper()}]")

    needed = [dv_col, 'fcc_reportable'] + controls
    model_data = analysis_df[needed].dropna().copy()
    model_data[dv_col] = model_data[dv_col].astype(int)

    formula = f"{dv_col} ~ fcc_reportable + " + " + ".join(controls)
    res = smf.logit(formula, data=model_data).fit(disp=0, maxiter=1000)

    # Extract all coefficients
    for var in ['fcc_reportable'] + controls:
        coef = res.params.get(var, np.nan)
        se = res.bse.get(var, np.nan)
        pval = res.pvalues.get(var, np.nan)

        sig = "***" if pval < 0.01 else "**" if pval < 0.05 else "*" if pval < 0.10 else ""

        print(f"  {var:25} {coef:+.4f} (SE={se:.4f}, p={pval:.4f}) {sig}")

        rows.append({
            'window': window_label,
            'variable': var,
            'logit_coef': coef,
            'logit_se': se,
            'logit_p': pval
        })

# Save
results_df = pd.DataFrame(rows)
results_df.to_csv('outputs/tables/essay3_governance/h6_reduced_form_all_coefficients.csv', index=False)
print("\n[OK] Saved: h6_reduced_form_all_coefficients.csv")

# Summary: which controls are significant?
print("\n" + "="*80)
print("CONTROL VARIABLE SIGNIFICANCE SUMMARY")
print("="*80)
sig_results = results_df[results_df['logit_p'] < 0.10]
if len(sig_results) > 0:
    print(f"\nVariables significant at p<0.10:")
    for _, row in sig_results.iterrows():
        print(f"  {row['window']:4} × {row['variable']:25} p={row['logit_p']:.4f}")
else:
    print("\nNo control variables reach significance at p<0.10.")

print("\n" + "="*80)
