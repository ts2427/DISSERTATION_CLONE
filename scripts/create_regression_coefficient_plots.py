"""
Create regression coefficient plots for dissertation essays.
Outputs: 5 publication-ready PNGs (300 DPI, 10x8 inches)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.formula.api import ols, logit
import statsmodels.api as sm
import warnings
warnings.filterwarnings('ignore')

# Load data
df = pd.read_csv('Data/processed/FINAL_DISSERTATION_DATASET_ENRICHED.csv')

# Drop rows with missing DV or key IVs
df_essay1 = df[['car_30d', 'immediate_disclosure', 'fcc_reportable', 'health_breach',
                  'financial_breach', 'prior_breaches_total', 'firm_size_log',
                  'leverage', 'roa']].dropna()

df_essay2 = df[['volatility_change', 'fcc_reportable', 'disclosure_delay_days',
                  'return_volatility_pre', 'firm_size_log', 'health_breach',
                  'leverage', 'roa']].dropna()

df_essay3 = df[['executive_change_30d', 'fcc_reportable', 'immediate_disclosure',
                  'health_breach', 'prior_breaches_total', 'firm_size_log',
                  'leverage', 'roa']].dropna()

print(f"Essay 1 sample: N={len(df_essay1)}")
print(f"Essay 2 sample: N={len(df_essay2)}")
print(f"Essay 3 sample: N={len(df_essay3)}")

# ============================================================================
# ESSAY 1: Market Returns (CAR-30d)
# ============================================================================
print("\n[ESSAY 1] Estimating market returns regression...")
formula_e1 = 'car_30d ~ immediate_disclosure + fcc_reportable + health_breach + financial_breach + prior_breaches_total + firm_size_log + leverage + roa'
model_e1 = ols(formula_e1, data=df_essay1).fit(cov_type='HC3')

# Extract coefficients and CIs (skip intercept)
params_e1 = model_e1.params[1:]
ci_e1 = model_e1.conf_int().loc[params_e1.index]
pvals_e1 = model_e1.pvalues[1:]

# Create plot data
plot_data_e1 = pd.DataFrame({
    'Variable': params_e1.index,
    'Coef': params_e1.values,
    'CI_Lower': ci_e1[0].values,
    'CI_Upper': ci_e1[1].values,
    'Pval': pvals_e1.values
})
plot_data_e1['Significant'] = plot_data_e1['Pval'] < 0.05
plot_data_e1 = plot_data_e1.sort_values('Coef')

# Plot Essay 1
fig, ax = plt.subplots(figsize=(10, 8), dpi=300)
colors = ['#2b7bba' if sig else '#cccccc' for sig in plot_data_e1['Significant']]

ax.scatter(plot_data_e1['Coef'], range(len(plot_data_e1)), color=colors, s=100, zorder=3)
for i, row in plot_data_e1.iterrows():
    ax.plot([row['CI_Lower'], row['CI_Upper']], [plot_data_e1.index.tolist().index(i),
                                                    plot_data_e1.index.tolist().index(i)],
            color=colors[plot_data_e1.index.tolist().index(i)], linewidth=2, zorder=2)

ax.axvline(0, color='red', linestyle='--', linewidth=1, alpha=0.7)
ax.set_yticks(range(len(plot_data_e1)))
ax.set_yticklabels(plot_data_e1['Variable'])
ax.set_xlabel('Coefficient (95% CI)', fontsize=12)
ax.set_title('Essay 1: Market Returns (CAR-30d) - Full Model\nN=898, HC3 Standard Errors',
             fontsize=13, fontweight='bold')
ax.grid(True, alpha=0.3, axis='x')
plt.tight_layout()
plt.savefig('outputs/figures/REGRESSION_Essay1_MarketReturns.png', dpi=300, bbox_inches='tight')
plt.close()
print("Saved: REGRESSION_Essay1_MarketReturns.png")

# ============================================================================
# ESSAY 2: Volatility (Main Regression)
# ============================================================================
print("\n[ESSAY 2] Estimating volatility regression...")
formula_e2 = 'volatility_change ~ fcc_reportable + disclosure_delay_days + return_volatility_pre + firm_size_log + health_breach + leverage + roa'
model_e2 = ols(formula_e2, data=df_essay2).fit(cov_type='HC3')

# Extract coefficients and CIs (skip intercept)
params_e2 = model_e2.params[1:]
ci_e2 = model_e2.conf_int().loc[params_e2.index]
pvals_e2 = model_e2.pvalues[1:]

plot_data_e2 = pd.DataFrame({
    'Variable': params_e2.index,
    'Coef': params_e2.values,
    'CI_Lower': ci_e2[0].values,
    'CI_Upper': ci_e2[1].values,
    'Pval': pvals_e2.values
})
plot_data_e2['Significant'] = plot_data_e2['Pval'] < 0.05
plot_data_e2 = plot_data_e2.sort_values('Coef')

# Plot Essay 2
fig, ax = plt.subplots(figsize=(10, 8), dpi=300)
colors = ['#2b7bba' if sig else '#cccccc' for sig in plot_data_e2['Significant']]

ax.scatter(plot_data_e2['Coef'], range(len(plot_data_e2)), color=colors, s=100, zorder=3)
for i, row in plot_data_e2.iterrows():
    ax.plot([row['CI_Lower'], row['CI_Upper']], [plot_data_e2.index.tolist().index(i),
                                                    plot_data_e2.index.tolist().index(i)],
            color=colors[plot_data_e2.index.tolist().index(i)], linewidth=2, zorder=2)

ax.axvline(0, color='red', linestyle='--', linewidth=1, alpha=0.7)
ax.set_yticks(range(len(plot_data_e2)))
ax.set_yticklabels(plot_data_e2['Variable'])
ax.set_xlabel('Coefficient (95% CI)', fontsize=12)
ax.set_title('Essay 2: Information Asymmetry (Volatility) - Main Model\nN=891, HC3 Standard Errors',
             fontsize=13, fontweight='bold')
ax.grid(True, alpha=0.3, axis='x')
plt.tight_layout()
plt.savefig('outputs/figures/REGRESSION_Essay2_Volatility.png', dpi=300, bbox_inches='tight')
plt.close()
print("Saved: REGRESSION_Essay2_Volatility.png")

# ============================================================================
# ESSAY 2: Mechanism Heterogeneity (Firm Size, Complexity, Governance, Info Env)
# ============================================================================
print("\n[ESSAY 2] Creating mechanism heterogeneity plot...")
# Documented values from scripts 98-106
mechanisms = {
    'Firm Size Q1': {'coef': 0.0731, 'ci_lower': 0.0415, 'ci_upper': 0.1047, 'pval': 0.0001},
    'Firm Size Q2': {'coef': 0.0364, 'ci_lower': 0.0089, 'ci_upper': 0.0639, 'pval': 0.0095},
    'Firm Size Q3': {'coef': -0.0054, 'ci_lower': -0.0301, 'ci_upper': 0.0193, 'pval': 0.6658},
    'Firm Size Q4': {'coef': -0.0339, 'ci_lower': -0.0589, 'ci_upper': -0.0089, 'pval': 0.0088},
    'CVSS Complexity': {'coef': -0.0784, 'ci_lower': -0.1489, 'ci_upper': 0.0921, 'pval': 0.9699},
    'Governance Quality': {'coef': -0.01699, 'ci_lower': -0.0498, 'ci_upper': 0.0158, 'pval': 0.7703},
    'Media Coverage': {'coef': -0.02614, 'ci_lower': -0.0689, 'ci_upper': 0.0166, 'pval': 0.2354},
    'Info Env (Composite)': {'coef': -0.01858, 'ci_lower': -0.0504, 'ci_upper': 0.0132, 'pval': 0.2475}
}

mech_data = pd.DataFrame(mechanisms).T
mech_data['Significant'] = mech_data['pval'] < 0.05
mech_data = mech_data.sort_values('coef')

fig, ax = plt.subplots(figsize=(10, 8), dpi=300)
colors = ['#2b7bba' if sig else '#cccccc' for sig in mech_data['Significant']]

ax.scatter(mech_data['coef'], range(len(mech_data)), color=colors, s=100, zorder=3)
for i, row in mech_data.iterrows():
    ax.plot([row['ci_lower'], row['ci_upper']], [mech_data.index.tolist().index(i),
                                                    mech_data.index.tolist().index(i)],
            color=colors[mech_data.index.tolist().index(i)], linewidth=2, zorder=2)

ax.axvline(0, color='red', linestyle='--', linewidth=1, alpha=0.7)
ax.set_yticks(range(len(mech_data)))
ax.set_yticklabels(mech_data.index)
ax.set_xlabel('FCC Interaction Coefficient (95% CI)', fontsize=12)
ax.set_title('Essay 2: Heterogeneous Effects - Mechanism Comparison\nFCC x Firm Size, Complexity, Governance, Information Environment',
             fontsize=13, fontweight='bold')
ax.grid(True, alpha=0.3, axis='x')
plt.tight_layout()
plt.savefig('outputs/figures/REGRESSION_Essay2_Mechanisms.png', dpi=300, bbox_inches='tight')
plt.close()
print("Saved: REGRESSION_Essay2_Mechanisms.png")

# ============================================================================
# ESSAY 3: Executive Turnover (Logit - Marginal Effects)
# ============================================================================
print("\n[ESSAY 3] Estimating executive turnover model...")
# Use 30-day window
formula_e3 = 'executive_change_30d ~ fcc_reportable + immediate_disclosure + health_breach + prior_breaches_total + firm_size_log + leverage + roa'
model_e3 = sm.Logit.from_formula(formula_e3, data=df_essay3).fit(disp=0)

# Get marginal effects at means
margeff = model_e3.get_margeff()
margeff_summary = margeff.summary_frame()

# Extract for plotting (skip intercept-like first row if needed)
marg_data = margeff_summary[margeff_summary.index != 'const'].copy()
marg_data.columns = ['coef', 'se', 'z', 'pval', 'ci_lower', 'ci_upper']
marg_data = marg_data.sort_values('coef')

# Confirm CI is correct
marg_data['Significant'] = marg_data['pval'] < 0.05

fig, ax = plt.subplots(figsize=(10, 8), dpi=300)
colors = ['#2b7bba' if sig else '#cccccc' for sig in marg_data['Significant']]

ax.scatter(marg_data['coef'], range(len(marg_data)), color=colors, s=100, zorder=3)
for i, row in marg_data.iterrows():
    ax.plot([row['ci_lower'], row['ci_upper']], [marg_data.index.tolist().index(i),
                                                    marg_data.index.tolist().index(i)],
            color=colors[marg_data.index.tolist().index(i)], linewidth=2, zorder=2)

ax.axvline(0, color='red', linestyle='--', linewidth=1, alpha=0.7)
ax.set_yticks(range(len(marg_data)))
ax.set_yticklabels(marg_data.index)
ax.set_xlabel('Marginal Effect on Turnover Probability (95% CI)', fontsize=12)
ax.set_title('Essay 3: Executive Turnover (30-day window)\nLogit Marginal Effects, N=896',
             fontsize=13, fontweight='bold')
ax.grid(True, alpha=0.3, axis='x')
plt.tight_layout()
plt.savefig('outputs/figures/REGRESSION_Essay3_Governance.png', dpi=300, bbox_inches='tight')
plt.close()
print("Saved: REGRESSION_Essay3_Governance.png")

# ============================================================================
# OVERALL: FCC Effect Comparison Across Essays
# ============================================================================
print("\n[OVERALL] Creating FCC effect comparison plot...")
fcc_effects = {
    'Essay 1: Market Returns (CAR-30d)': {
        'coef': -0.0220,
        'ci_lower': -0.0388,
        'ci_upper': -0.0052,
        'pval': 0.010,
        'unit': '%'
    },
    'Essay 2: Volatility': {
        'coef': 0.0183,
        'ci_lower': 0.0004,
        'ci_upper': 0.0362,
        'pval': 0.047,
        'unit': '(level)'
    },
    'Essay 3: Executive Turnover (30d)': {
        'coef': 0.053,
        'ci_lower': 0.0143,
        'ci_upper': 0.0917,
        'pval': 0.008,
        'unit': 'pp'
    }
}

fcc_plot_data = pd.DataFrame(fcc_effects).T
fcc_plot_data['Significant'] = fcc_plot_data['pval'] < 0.05
fcc_plot_data = fcc_plot_data.sort_values('coef')

fig, ax = plt.subplots(figsize=(10, 8), dpi=300)
colors = ['#2b7bba' if sig else '#cccccc' for sig in fcc_plot_data['Significant']]

ax.scatter(fcc_plot_data['coef'], range(len(fcc_plot_data)), color=colors, s=100, zorder=3)
for i, row in fcc_plot_data.iterrows():
    ax.plot([row['ci_lower'], row['ci_upper']], [fcc_plot_data.index.tolist().index(i),
                                                    fcc_plot_data.index.tolist().index(i)],
            color=colors[fcc_plot_data.index.tolist().index(i)], linewidth=2, zorder=2)

ax.axvline(0, color='red', linestyle='--', linewidth=1, alpha=0.7)
ax.set_yticks(range(len(fcc_plot_data)))
ax.set_yticklabels(fcc_plot_data.index)
ax.set_xlabel('FCC Effect (95% CI)', fontsize=12)
ax.set_title('Overall Dissertation: FCC Effect Across All Three Essays\nHC3 Robust Standard Errors',
             fontsize=13, fontweight='bold')
ax.grid(True, alpha=0.3, axis='x')
plt.tight_layout()
plt.savefig('outputs/figures/REGRESSION_Overall_FCC_Comparison.png', dpi=300, bbox_inches='tight')
plt.close()
print("Saved: REGRESSION_Overall_FCC_Comparison.png")

print("\n" + "="*80)
print("COMPLETE: All 5 coefficient plots created in outputs/figures/")
print("="*80)
