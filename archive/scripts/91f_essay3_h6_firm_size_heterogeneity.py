"""
ESSAY 3: H6 FIRM SIZE HETEROGENEITY (All Windows)

Tests whether FCC effect on executive turnover varies by firm size across 30d/90d/180d windows.
Addresses the key defense challenge: "Does Q2 persist or fade?"

Produces:
  - Quartile-level FCC effects for all three windows
  - Temporal decay pattern (persistence → decay tells theoretical story via Mitchell et al.)
  - Defensible answer to Affuso's likely challenge on single-window heterogeneity

Writes to: outputs/tables/essay3_governance/h6_firm_size_heterogeneity_full.csv
"""

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
import warnings
warnings.filterwarnings('ignore')

print("=" * 100)
print("ESSAY 3: H6 FIRM SIZE HETEROGENEITY ACROSS ALL WINDOWS (30d/90d/180d)")
print("=" * 100)

# ============================================================================
# LOAD DATA (match sample from scripts 91/91b exactly: N=651)
# ============================================================================

print("\n[Step 1/3] Loading data and preparing analysis sample...")
df = pd.read_csv('Data/processed/FINAL_DISSERTATION_DATASET_DEDUPLICATED_ENRICHED.csv')

# Filter to match canonical H6 sample (N=651)
analysis_df = df[df['has_crsp_data'] == True].copy()
analysis_df = analysis_df[
    (analysis_df['executive_change_30d'].notna()) &
    (analysis_df['immediate_disclosure'].notna()) &
    (analysis_df['fcc_reportable'].notna())
].copy().dropna(subset=['firm_size_log', 'leverage', 'roa'])

print(f"  [OK] N = {len(analysis_df):,} (canonical H6 mediation sample)")

# Convert booleans
bool_cols = analysis_df.select_dtypes(include=['bool']).columns
for col in bool_cols:
    analysis_df[col] = analysis_df[col].astype(int)

# ============================================================================
# CREATE FIRM SIZE QUARTILES
# ============================================================================

print("\n[Step 2/3] Creating firm size quartiles...")
analysis_df['size_quartile'] = pd.qcut(analysis_df['firm_size_log'], q=4,
                                       labels=['Q1 (Smallest)', 'Q2', 'Q3', 'Q4 (Largest)'],
                                       duplicates='drop')

quartile_labels = ['Q1 (Smallest)', 'Q2', 'Q3', 'Q4 (Largest)']
print(f"  Quartile sizes:")
for q in quartile_labels:
    n_q = (analysis_df['size_quartile'] == q).sum()
    print(f"    {q}: n={n_q:,}")

# ============================================================================
# HETEROGENEITY ANALYSIS: FCC EFFECT BY QUARTILE × WINDOW
# ============================================================================

print("\n[Step 3/3] Running heterogeneity analysis (12 models: 4 quartiles × 3 windows)...")

windows = {
    '30d': 'executive_change_30d',
    '90d': 'executive_change_90d',
    '180d': 'executive_change_180d'
}
controls = ['health_breach', 'prior_breaches_total', 'firm_size_log', 'leverage', 'roa']

def discrete_ame_pp(res, data, var):
    """FCC AME in percentage points for a subgroup."""
    d0 = data.copy()
    d0[var] = 0
    d1 = data.copy()
    d1[var] = 1
    return 100.0 * (res.predict(d1) - res.predict(d0)).mean()

rows = []

print("\n" + "=" * 100)
print("RESULTS BY FIRM SIZE QUARTILE AND WINDOW")
print("=" * 100)

for window_label, dv_col in windows.items():
    print(f"\n[{window_label.upper()} WINDOW]")
    print("-" * 100)

    for q in quartile_labels:
        # Subset to this quartile
        q_data = analysis_df[analysis_df['size_quartile'] == q].copy()

        # Prepare model data
        needed = [dv_col, 'fcc_reportable'] + controls
        model_data = q_data[needed].dropna().copy()
        model_data[dv_col] = model_data[dv_col].astype(int)

        n_q = len(model_data)
        baseline_rate = model_data[dv_col].mean() * 100

        if n_q < 15:
            print(f"  {q} (n={n_q}): TOO SMALL (skipped)")
            continue

        # Run logistic regression
        formula = f"{dv_col} ~ fcc_reportable + " + " + ".join(controls)

        try:
            res = smf.logit(formula, data=model_data).fit(disp=0, maxiter=1000)

            # Extract FCC coefficient and AME
            fcc_coef = res.params.get('fcc_reportable', np.nan)
            fcc_se = res.bse.get('fcc_reportable', np.nan)
            fcc_p = res.pvalues.get('fcc_reportable', np.nan)
            fcc_ame = discrete_ame_pp(res, model_data, 'fcc_reportable')
            pseudo_r2 = res.prsquared

            # Significance marker
            sig = "***" if fcc_p < 0.01 else "**" if fcc_p < 0.05 else "*" if fcc_p < 0.10 else "ns"

            print(f"  {q} (n={n_q:,}, baseline={baseline_rate:.1f}%):")
            print(f"    FCC effect (logit): {fcc_coef:.4f} (SE={fcc_se:.4f}, p={fcc_p:.4f}) {sig}")
            print(f"    FCC effect (AME):   {fcc_ame:+.2f}pp")
            print(f"    Pseudo R²:          {pseudo_r2:.4f}")

            # Store result
            rows.append({
                'window': window_label,
                'quartile': q,
                'n': n_q,
                'baseline_rate_pct': baseline_rate,
                'fcc_logit_coef': fcc_coef,
                'fcc_logit_se': fcc_se,
                'fcc_logit_p': fcc_p,
                'fcc_ame_pp': fcc_ame,
                'pseudo_r2': pseudo_r2
            })

        except Exception as e:
            print(f"  {q}: FAILED - {str(e)[:50]}")
            continue

# ============================================================================
# SAVE RESULTS
# ============================================================================

print("\n" + "=" * 100)
print("SUMMARY TABLE: FCC EFFECT BY FIRM SIZE QUARTILE AND WINDOW")
print("=" * 100)

results_df = pd.DataFrame(rows)
output_path = 'outputs/tables/essay3_governance/h6_firm_size_heterogeneity_full.csv'
results_df.to_csv(output_path, index=False)
print(f"\n[OK] Saved: {output_path}")

# Print pivot table for prose
print("\nPivot View (FCC AME in percentage points):")
print("-" * 100)
pivot = results_df.pivot(index='quartile', columns='window', values='fcc_ame_pp')
print(pivot.to_string())

print("\nPivot View (P-values):")
print("-" * 100)
pivot_p = results_df.pivot(index='quartile', columns='window', values='fcc_logit_p')
print(pivot_p.to_string())

print("\nKey Findings:")
print("-" * 100)

# Identify significant effects
sig_results = results_df[results_df['fcc_logit_p'] < 0.05]
if len(sig_results) > 0:
    print(f"Significant effects (p<0.05): {len(sig_results)}")
    for _, row in sig_results.iterrows():
        print(f"  {row['quartile']:15} × {row['window']:4}: {row['fcc_ame_pp']:+6.2f}pp (p={row['fcc_logit_p']:.4f})")
else:
    print("No significant effects at p<0.05")

# Identify Q2 pattern (the question Affuso will ask)
q2_results = results_df[results_df['quartile'] == 'Q2'].sort_values('window')
if len(q2_results) > 0:
    print(f"\nQ2 (Mid-size Firms) Temporal Pattern:")
    for _, row in q2_results.iterrows():
        print(f"  {row['window']:4}: {row['fcc_ame_pp']:+6.2f}pp (p={row['fcc_logit_p']:.4f})")

    # Check for persistence vs. decay
    if len(q2_results) == 3:
        q2_30d = q2_results[q2_results['window'] == '30d']['fcc_ame_pp'].values[0]
        q2_90d = q2_results[q2_results['window'] == '90d']['fcc_ame_pp'].values[0]
        q2_180d = q2_results[q2_results['window'] == '180d']['fcc_ame_pp'].values[0]

        decay_30_90 = abs(q2_90d) < abs(q2_30d)
        decay_90_180 = abs(q2_180d) < abs(q2_90d)

        if decay_30_90 and decay_90_180:
            print(f"\n  Pattern: DECAY (consistent with stakeholder salience mechanism)")
            print(f"           30d→90d: {q2_30d:.2f} → {q2_90d:.2f}")
            print(f"           90d→180d: {q2_90d:.2f} → {q2_180d:.2f}")
        else:
            print(f"\n  Pattern: PERSISTENCE or NO DECAY (consistent with structural firm response)")

print("\n" + "=" * 100)
print("Analysis complete. Results ready for dissertation heterogeneity section.")
print("=" * 100)
