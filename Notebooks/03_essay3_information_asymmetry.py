# %% [markdown]
# # Essay 3: Disclosure Timing and Information Asymmetry
# ## Volatility Analysis with Governance Moderators

# %%
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # No popups!
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.iolib.summary2 import summary_col
import warnings
import os
warnings.filterwarnings('ignore')

plt.style.use('seaborn-v0_8-darkgrid')

# %%
# Smart path handling
if os.path.exists('Data/processed/FINAL_DISSERTATION_DATASET_ENRICHED.csv'):
    data_path = 'Data/processed/FINAL_DISSERTATION_DATASET_ENRICHED.csv'
    output_base = 'outputs'
elif os.path.exists('../Data/processed/FINAL_DISSERTATION_DATASET_ENRICHED.csv'):
    data_path = '../Data/processed/FINAL_DISSERTATION_DATASET_ENRICHED.csv'
    output_base = '../outputs'
else:
    raise FileNotFoundError("Cannot find enriched dataset")

# Create output directories
os.makedirs(f'{output_base}/tables', exist_ok=True)
os.makedirs(f'{output_base}/figures', exist_ok=True)

# Load data
df = pd.read_csv(data_path)

# Filter to Essay 3 sample (has volatility data)
essay3_df = df[
    (df['return_volatility_pre'].notna()) & 
    (df['return_volatility_post'].notna())
].copy()

# Create change variables
essay3_df['volatility_change_return'] = essay3_df['return_volatility_post'] - essay3_df['return_volatility_pre']
essay3_df['volatility_change_volume'] = essay3_df['volume_volatility_post'] - essay3_df['volume_volatility_pre']

print(f"Essay 3 Sample: {len(essay3_df)} breaches with volatility data")
print(f"Mean volatility change (return): {essay3_df['volatility_change_return'].mean():.6f}")

# %% [markdown]
# ## Model 1: Baseline Volatility Change

# %%
formula1 = """volatility_change_return ~ immediate_disclosure + fcc_reportable + 
              immediate_disclosure:fcc_reportable + firm_size_log + leverage + roa"""

model1_data = essay3_df.dropna(subset=['volatility_change_return', 'immediate_disclosure', 
                                        'fcc_reportable', 'firm_size_log', 'leverage', 'roa'])

print(f"\nModel 1: Baseline - n={len(model1_data)}")
model1 = smf.ols(formula=formula1, data=model1_data).fit(cov_type='HC3')

print("\n" + "="*80)
print("MODEL 1: BASELINE - Volatility Change")
print("="*80)
print(model1.summary())

# %% [markdown]
# ## Model 2: Governance Moderation

# %%
# Create governance composite
essay3_df['governance_score'] = (
    (essay3_df['firm_size_log'] - essay3_df['firm_size_log'].mean()) / essay3_df['firm_size_log'].std() +
    (essay3_df['leverage'] - essay3_df['leverage'].mean()) / essay3_df['leverage'].std() * -1 +  # Lower leverage = better
    (essay3_df['roa'] - essay3_df['roa'].mean()) / essay3_df['roa'].std()
) / 3

essay3_df['strong_governance'] = (essay3_df['governance_score'] > essay3_df['governance_score'].median()).astype(int)

formula2 = """volatility_change_return ~ immediate_disclosure + strong_governance + 
              immediate_disclosure:strong_governance + fcc_reportable + leverage + roa"""

model2_data = essay3_df.dropna(subset=['volatility_change_return', 'immediate_disclosure', 
                                        'strong_governance', 'fcc_reportable', 'leverage', 'roa'])

print(f"\nModel 2: Governance - n={len(model2_data)}")
model2 = smf.ols(formula=formula2, data=model2_data).fit(cov_type='HC3')

print("\n" + "="*80)
print("MODEL 2: GOVERNANCE MODERATION")
print("="*80)
print(model2.summary())

# %% [markdown]
# ## Model 3: Prior Breaches as Governance Proxy

# %%
formula3 = """volatility_change_return ~ immediate_disclosure + is_repeat_offender + 
              immediate_disclosure:is_repeat_offender + fcc_reportable + 
              firm_size_log + leverage + roa"""

model3_data = essay3_df.dropna(subset=['volatility_change_return', 'immediate_disclosure', 
                                        'is_repeat_offender', 'fcc_reportable',
                                        'firm_size_log', 'leverage', 'roa'])

print(f"\nModel 3: Prior Breaches - n={len(model3_data)}")
model3 = smf.ols(formula=formula3, data=model3_data).fit(cov_type='HC3')

print("\n" + "="*80)
print("MODEL 3: PRIOR BREACHES AS GOVERNANCE")
print("="*80)
print(model3.summary())

# %% [markdown]
# ## Model 4: Executive Turnover as Accountability Signal

# %%
# FIXED: Use correct variable name
formula4 = """volatility_change_return ~ immediate_disclosure + executive_change_30d + 
              immediate_disclosure:executive_change_30d + fcc_reportable + 
              firm_size_log + leverage + roa"""

model4_data = essay3_df.dropna(subset=['volatility_change_return', 'immediate_disclosure', 
                                        'executive_change_30d', 'fcc_reportable',
                                        'firm_size_log', 'leverage', 'roa'])

print(f"\nModel 4: Executive Turnover - n={len(model4_data)}")
model4 = smf.ols(formula=formula4, data=model4_data).fit(cov_type='HC3')

print("\n" + "="*80)
print("MODEL 4: EXECUTIVE TURNOVER")
print("="*80)
print(model4.summary())

# %% [markdown]
# ## Model 5: Full Model

# %%
# FIXED: Use correct variable names
formula5 = """volatility_change_return ~ immediate_disclosure + strong_governance + 
              is_repeat_offender + executive_change_30d + regulatory_enforcement +
              fcc_reportable + firm_size_log + leverage + roa + high_severity_breach"""

model5_data = essay3_df.dropna(subset=['volatility_change_return', 'immediate_disclosure', 
                                        'strong_governance', 'is_repeat_offender',
                                        'executive_change_30d', 'regulatory_enforcement',
                                        'fcc_reportable', 'firm_size_log', 'leverage', 'roa',
                                        'high_severity_breach'])

print(f"\nModel 5: Full Model - n={len(model5_data)}")
model5 = smf.ols(formula=formula5, data=model5_data).fit(cov_type='HC3')

print("\n" + "="*80)
print("MODEL 5: FULL MODEL")
print("="*80)
print(model5.summary())

# %% [markdown]
# ## Table 4: Regression Results - Essay 3

# %%
models_list = [model1, model2, model3, model4, model5]
model_names = ['(1)\nBaseline', '(2)\nGovernance', '(3)\nPrior\nBreaches', 
               '(4)\nExec\nTurnover', '(5)\nFull\nModel']

reg_table = summary_col(models_list,
                         model_names=model_names,
                         stars=True,
                         float_format='%0.6f',
                         info_dict={
                             'N': lambda x: f"{int(x.nobs)}",
                             'R-squared': lambda x: f"{x.rsquared:.4f}",
                             'Adj. R-squared': lambda x: f"{x.rsquared_adj:.4f}"
                         })

print("\n" + "="*80)
print("TABLE 4: INFORMATION ASYMMETRY REGRESSIONS")
print("="*80)
print(reg_table)

# Save
with open(f'{output_base}/tables/table4_essay3_regressions.tex', 'w') as f:
    f.write(reg_table.as_latex())

# Save CSV summary
summary_df = pd.DataFrame({
    'Model': model_names,
    'N': [m.nobs for m in models_list],
    'R-squared': [m.rsquared for m in models_list],
    'Adj R-squared': [m.rsquared_adj for m in models_list]
})
summary_df.to_csv(f'{output_base}/tables/table4_essay3_summary.csv', index=False)

print(f"\n✓ Table 4 saved to {output_base}/tables/")

# %% [markdown]
# ## Figure 5: Volatility Changes

# %%
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Plot 1: Pre vs Post Volatility
pre_vol = essay3_df['return_volatility_pre'].dropna()
post_vol = essay3_df['return_volatility_post'].dropna()

axes[0, 0].hist([pre_vol, post_vol], bins=30, label=['Pre-Breach', 'Post-Breach'], 
                alpha=0.7, color=['steelblue', 'coral'])
axes[0, 0].set_xlabel('Return Volatility', fontsize=11)
axes[0, 0].set_ylabel('Frequency', fontsize=11)
axes[0, 0].set_title('Return Volatility: Pre vs Post Breach', fontsize=12, fontweight='bold')
axes[0, 0].legend()
axes[0, 0].grid(alpha=0.3)

# Plot 2: Volatility Change by Disclosure
immediate_vol = essay3_df[essay3_df['immediate_disclosure'] == 1]['volatility_change_return'].dropna()
delayed_vol = essay3_df[essay3_df['delayed_disclosure'] == 1]['volatility_change_return'].dropna()

bp = axes[0, 1].boxplot([delayed_vol, immediate_vol], labels=['Delayed', 'Immediate'], 
                         patch_artist=True)
bp['boxes'][0].set_facecolor('lightcoral')
bp['boxes'][1].set_facecolor('lightgreen')

axes[0, 1].axhline(0, color='black', linestyle='--', linewidth=1)
axes[0, 1].set_ylabel('Volatility Change', fontsize=11)
axes[0, 1].set_title('Volatility Change by Disclosure Timing', fontsize=12, fontweight='bold')
axes[0, 1].grid(axis='y', alpha=0.3)

# Add means
axes[0, 1].text(1, delayed_vol.mean(), f'{delayed_vol.mean():.2f}', 
                ha='center', va='bottom', fontweight='bold')
axes[0, 1].text(2, immediate_vol.mean(), f'{immediate_vol.mean():.2f}', 
                ha='center', va='bottom', fontweight='bold')

# Plot 3: By Governance
if 'strong_governance' in essay3_df.columns:
    weak_gov = essay3_df[essay3_df['strong_governance'] == 0]['volatility_change_return'].dropna()
    strong_gov = essay3_df[essay3_df['strong_governance'] == 1]['volatility_change_return'].dropna()

    axes[1, 0].boxplot([weak_gov, strong_gov], labels=['Weak Gov', 'Strong Gov'])
    axes[1, 0].axhline(0, color='black', linestyle='--', linewidth=1)
    axes[1, 0].set_ylabel('Volatility Change', fontsize=11)
    axes[1, 0].set_title('Volatility Change by Governance Quality', fontsize=12, fontweight='bold')
    axes[1, 0].grid(axis='y', alpha=0.3)

# Plot 4: By Prior Breaches
if 'is_first_breach' in essay3_df.columns and 'is_repeat_offender' in essay3_df.columns:
    first_vol = essay3_df[essay3_df['is_first_breach'] == 1]['volatility_change_return'].dropna()
    repeat_vol = essay3_df[essay3_df['is_repeat_offender'] == 1]['volatility_change_return'].dropna()

    axes[1, 1].boxplot([first_vol, repeat_vol], labels=['First-Time', 'Repeat'])
    axes[1, 1].axhline(0, color='black', linestyle='--', linewidth=1)
    axes[1, 1].set_ylabel('Volatility Change', fontsize=11)
    axes[1, 1].set_title('Volatility Change by Prior Breach History', fontsize=12, fontweight='bold')
    axes[1, 1].grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig(f'{output_base}/figures/fig5_volatility_analysis.png', dpi=300, bbox_inches='tight')
print(f"✓ Saved {output_base}/figures/fig5_volatility_analysis.png")
plt.close()

# %% [markdown]
# ## Robustness: Volume Volatility

# %%
formula_vol = """volatility_change_volume ~ immediate_disclosure + strong_governance + 
                 immediate_disclosure:strong_governance + fcc_reportable + 
                 firm_size_log + leverage + roa"""

model_vol_data = essay3_df.dropna(subset=['volatility_change_volume', 'immediate_disclosure', 
                                           'strong_governance', 'fcc_reportable',
                                           'firm_size_log', 'leverage', 'roa'])

print(f"\nRobustness: Volume Volatility - n={len(model_vol_data)}")
model_vol = smf.ols(formula=formula_vol, data=model_vol_data).fit(cov_type='HC3')

print("\n" + "="*80)
print("ROBUSTNESS: VOLUME VOLATILITY")
print("="*80)
print(model_vol.summary())

# %% [markdown]
# ## Key Findings Summary

# %%
print("\n" + "="*80)
print("KEY FINDINGS SUMMARY - ESSAY 3")
print("="*80)

def print_coef(model, var_name, hypothesis):
    """Print coefficient with significance stars"""
    if var_name in model.params:
        coef = model.params[var_name]
        pval = model.pvalues[var_name]
        se = model.bse[var_name]
        
        sig = '***' if pval < 0.01 else '**' if pval < 0.05 else '*' if pval < 0.10 else ''
        
        print(f"\n{hypothesis}")
        print(f"  Coefficient: {coef:7.6f}{sig}")
        print(f"  Std. Error: ({se:7.6f})")
        print(f"  p-value: {pval:10.4f}")
        
        if pval < 0.10:
            direction = "reduces" if coef < 0 else "increases"
            print(f"  ✓ SUPPORTED: {hypothesis.split(':')[1].strip()} {direction} volatility change by {abs(coef):.6f}")
        else:
            print(f"  ✗ NOT SUPPORTED at p<0.10")
    else:
        print(f"\n{hypothesis}")
        print(f"  Variable not in model")

# Print key findings
print_coef(model1, 'immediate_disclosure', 'H1: Immediate Disclosure Effect on Volatility')
print_coef(model2, 'immediate_disclosure:strong_governance', 'H2: Governance Moderation Effect')
print_coef(model3, 'immediate_disclosure:is_repeat_offender', 'H3: Prior Breach Moderation')
print_coef(model4, 'immediate_disclosure:executive_change_30d', 'H4: Executive Turnover Moderation')
print_coef(model1, 'fcc_reportable[T.True]', 'H5: FCC Regulation Effect on Volatility')

print("\n" + "="*80)
print("✅ ESSAY 3 ANALYSIS COMPLETE!")
print("="*80)
print(f"\nOutput files saved to {output_base}/")
print("\nGenerated:")
print("  ✓ Table 4: Information asymmetry regressions (5 models)")
print("  ✓ Figure 5: Volatility analysis")
print("  ✓ Robustness check: Volume volatility")
print("="*80)