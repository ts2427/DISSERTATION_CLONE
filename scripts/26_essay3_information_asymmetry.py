import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
from statsmodels.formula.api import logit
import warnings
warnings.filterwarnings('ignore')

print("=" * 60)
print("ESSAY 3: INFORMATION ASYMMETRY ANALYSIS (REVISED)")
print("Post-Breach Volatility and Disclosure Timing")
print("=" * 60)

# Load data
df = pd.read_excel('Data/processed/FINAL_DISSERTATION_DATASET.xlsx')

# Analysis sample: Has volatility data
analysis_df = df[(df['return_volatility_pre'].notna()) & 
                 (df['return_volatility_post'].notna()) &
                 (df['firm_size_log'].notna())].copy()

# Convert booleans
bool_cols = ['fcc_reportable', 'immediate_disclosure', 'delayed_disclosure', 'large_firm']
for col in bool_cols:
    if col in analysis_df.columns:
        analysis_df[col] = analysis_df[col].astype(int)

# Create additional variables
analysis_df['volatility_increased'] = (analysis_df['return_volatility_post'] > analysis_df['return_volatility_pre']).astype(int)
analysis_df['volatility_change'] = analysis_df['return_volatility_post'] - analysis_df['return_volatility_pre']

print(f"\n✓ Total breach records: {len(df)}")
print(f"✓ Analysis sample: {len(analysis_df)} records ({len(analysis_df)/len(df)*100:.1f}% of total)")

import os
os.makedirs('outputs/essay3_revised/tables', exist_ok=True)
os.makedirs('outputs/essay3_revised/figures', exist_ok=True)

# ============================================================
# SECTION 1: DESCRIPTIVE STATISTICS
# ============================================================

print("\n" + "=" * 60)
print("SECTION 1: DESCRIPTIVE STATISTICS")
print("=" * 60)

desc_vars = ['return_volatility_pre', 'return_volatility_post', 'volatility_change',
             'disclosure_delay_days', 'firm_size_log', 'leverage', 'roa']

desc_stats = analysis_df[desc_vars].describe().T
desc_stats['median'] = analysis_df[desc_vars].median()
desc_stats = desc_stats[['count', 'mean', 'median', 'std', 'min', 'max']]

print("\n✓ Table 1: Descriptive Statistics")
print(desc_stats.round(4))

desc_stats.to_csv('outputs/essay3_revised/tables/TABLE1_descriptives.csv')

# Volatility summary
print(f"\n📊 VOLATILITY SUMMARY:")
print(f"   Pre-breach mean: {analysis_df['return_volatility_pre'].mean():.2f}%")
print(f"   Post-breach mean: {analysis_df['return_volatility_post'].mean():.2f}%")
print(f"   Mean change: {analysis_df['volatility_change'].mean():.2f}%")
print(f"   % with INCREASED volatility: {analysis_df['volatility_increased'].mean()*100:.1f}%")

# Sample composition
composition = pd.DataFrame({
    'Category': ['Total Sample', 'FCC-Regulated', 'Non-FCC', 
                 'Immediate Disclosure', 'Delayed Disclosure',
                 'Large Firms', 'Small Firms',
                 'Volatility Increased', 'Volatility Decreased'],
    'N': [
        len(analysis_df),
        analysis_df['fcc_reportable'].sum(),
        len(analysis_df) - analysis_df['fcc_reportable'].sum(),
        analysis_df['immediate_disclosure'].sum(),
        analysis_df['delayed_disclosure'].sum(),
        analysis_df['large_firm'].sum(),
        len(analysis_df) - analysis_df['large_firm'].sum(),
        analysis_df['volatility_increased'].sum(),
        len(analysis_df) - analysis_df['volatility_increased'].sum()
    ],
    'Percentage': [
        100.0,
        analysis_df['fcc_reportable'].mean() * 100,
        (1 - analysis_df['fcc_reportable'].mean()) * 100,
        analysis_df['immediate_disclosure'].mean() * 100,
        analysis_df['delayed_disclosure'].mean() * 100,
        analysis_df['large_firm'].mean() * 100,
        (1 - analysis_df['large_firm'].mean()) * 100,
        analysis_df['volatility_increased'].mean() * 100,
        (1 - analysis_df['volatility_increased'].mean()) * 100
    ]
})

composition.to_csv('outputs/essay3_revised/tables/TABLE2_composition.csv', index=False)
print("\n✓ Table 2: Sample Composition")
print(composition.to_string(index=False))

# ============================================================
# SECTION 2: UNIVARIATE ANALYSIS
# ============================================================

print("\n" + "=" * 60)
print("SECTION 2: UNIVARIATE ANALYSIS")
print("=" * 60)

# H1: Disclosure timing effects
immediate = analysis_df[analysis_df['immediate_disclosure'] == 1]
delayed = analysis_df[analysis_df['delayed_disclosure'] == 1]

print(f"\n--- H1: DISCLOSURE TIMING EFFECTS ---")
print(f"\nImmediate Disclosure (≤7 days, n={len(immediate)}):")
print(f"  Post-breach volatility: {immediate['return_volatility_post'].mean():.2f}%")
print(f"  Volatility change: {immediate['volatility_change'].mean():.2f}%")
print(f"  % with increased volatility: {immediate['volatility_increased'].mean()*100:.1f}%")

print(f"\nDelayed Disclosure (>30 days, n={len(delayed)}):")
print(f"  Post-breach volatility: {delayed['return_volatility_post'].mean():.2f}%")
print(f"  Volatility change: {delayed['volatility_change'].mean():.2f}%")
print(f"  % with increased volatility: {delayed['volatility_increased'].mean()*100:.1f}%")

# Test on POST-BREACH volatility
ttest_post = stats.ttest_ind(immediate['return_volatility_post'].dropna(), 
                              delayed['return_volatility_post'].dropna())
print(f"\nPost-breach volatility difference: {immediate['return_volatility_post'].mean() - delayed['return_volatility_post'].mean():.2f}%")
print(f"T-test: t={ttest_post[0]:.3f}, p={ttest_post[1]:.4f}")

# Test on CHANGE
ttest_change = stats.ttest_ind(immediate['volatility_change'].dropna(), 
                               delayed['volatility_change'].dropna())
print(f"\nVolatility change difference: {immediate['volatility_change'].mean() - delayed['volatility_change'].mean():.2f}%")
print(f"T-test: t={ttest_change[0]:.3f}, p={ttest_change[1]:.4f}")

# H2: Governance moderation
large_firms = analysis_df[analysis_df['large_firm'] == 1]
small_firms = analysis_df[analysis_df['large_firm'] == 0]

print(f"\n--- H2: GOVERNANCE (FIRM SIZE) EFFECTS ---")
print(f"\nLarge Firms (n={len(large_firms)}):")
print(f"  Post-breach volatility: {large_firms['return_volatility_post'].mean():.2f}%")
print(f"  Volatility change: {large_firms['volatility_change'].mean():.2f}%")

print(f"\nSmall Firms (n={len(small_firms)}):")
print(f"  Post-breach volatility: {small_firms['return_volatility_post'].mean():.2f}%")
print(f"  Volatility change: {small_firms['volatility_change'].mean():.2f}%")

ttest_gov = stats.ttest_ind(large_firms['return_volatility_post'].dropna(), 
                            small_firms['return_volatility_post'].dropna())
print(f"\nPost-breach volatility difference: {large_firms['return_volatility_post'].mean() - small_firms['return_volatility_post'].mean():.2f}%")
print(f"T-test: t={ttest_gov[0]:.3f}, p={ttest_gov[1]:.4f}")

# FCC effects
fcc_firms = analysis_df[analysis_df['fcc_reportable'] == 1]
nonfcc_firms = analysis_df[analysis_df['fcc_reportable'] == 0]

print(f"\n--- FCC REGULATORY EFFECTS ---")
print(f"\nFCC-Regulated (n={len(fcc_firms)}):")
print(f"  Post-breach volatility: {fcc_firms['return_volatility_post'].mean():.2f}%")

print(f"\nNon-FCC (n={len(nonfcc_firms)}):")
print(f"  Post-breach volatility: {nonfcc_firms['return_volatility_post'].mean():.2f}%")

ttest_fcc = stats.ttest_ind(fcc_firms['return_volatility_post'].dropna(), 
                            nonfcc_firms['return_volatility_post'].dropna())
print(f"\nPost-breach volatility difference: {fcc_firms['return_volatility_post'].mean() - nonfcc_firms['return_volatility_post'].mean():.2f}%")
print(f"T-test: t={ttest_fcc[0]:.3f}, p={ttest_fcc[1]:.4f}")

# Create univariate table
univariate_results = pd.DataFrame({
    'Comparison': ['Immediate vs Delayed', 'Large vs Small Firms', 'FCC vs Non-FCC'],
    'Group 1 Mean': [
        immediate['return_volatility_post'].mean(),
        large_firms['return_volatility_post'].mean(),
        fcc_firms['return_volatility_post'].mean()
    ],
    'Group 2 Mean': [
        delayed['return_volatility_post'].mean(),
        small_firms['return_volatility_post'].mean(),
        nonfcc_firms['return_volatility_post'].mean()
    ],
    'Difference': [
        immediate['return_volatility_post'].mean() - delayed['return_volatility_post'].mean(),
        large_firms['return_volatility_post'].mean() - small_firms['return_volatility_post'].mean(),
        fcc_firms['return_volatility_post'].mean() - nonfcc_firms['return_volatility_post'].mean()
    ],
    'T-statistic': [ttest_post[0], ttest_gov[0], ttest_fcc[0]],
    'P-value': [ttest_post[1], ttest_gov[1], ttest_fcc[1]]
})

univariate_results.to_csv('outputs/essay3_revised/tables/TABLE3_univariate.csv', index=False)

# ============================================================
# SECTION 3: MULTIVARIATE REGRESSION - POST-BREACH VOLATILITY
# ============================================================

print("\n" + "=" * 60)
print("SECTION 3: REGRESSION ANALYSIS")
print("DV = POST-BREACH VOLATILITY (controlling for pre-breach)")
print("=" * 60)

reg_df = analysis_df[['return_volatility_post', 'return_volatility_pre',
                       'immediate_disclosure', 'fcc_reportable', 'large_firm',
                       'firm_size_log', 'leverage', 'roa']].dropna()

print(f"\n✓ Regression sample: n={len(reg_df)}")

# Create interaction terms
reg_df['disclosure_x_governance'] = reg_df['immediate_disclosure'] * reg_df['large_firm']
reg_df['fcc_x_immediate'] = reg_df['fcc_reportable'] * reg_df['immediate_disclosure']

y = reg_df['return_volatility_post']

# Model 1: Disclosure timing + pre-breach control
X1 = sm.add_constant(reg_df[['return_volatility_pre', 'immediate_disclosure']])
model1 = sm.OLS(y, X1).fit(cov_type='HC3')

# Model 2: Add governance
X2 = sm.add_constant(reg_df[['return_volatility_pre', 'immediate_disclosure', 'large_firm']])
model2 = sm.OLS(y, X2).fit(cov_type='HC3')

# Model 3: Add disclosure × governance interaction
X3 = sm.add_constant(reg_df[['return_volatility_pre', 'immediate_disclosure', 
                              'large_firm', 'disclosure_x_governance']])
model3 = sm.OLS(y, X3).fit(cov_type='HC3')

# Model 4: Add FCC
X4 = sm.add_constant(reg_df[['return_volatility_pre', 'immediate_disclosure', 
                              'large_firm', 'disclosure_x_governance', 'fcc_reportable']])
model4 = sm.OLS(y, X4).fit(cov_type='HC3')

# Model 5: Add FCC interaction
X5 = sm.add_constant(reg_df[['return_volatility_pre', 'immediate_disclosure', 
                              'large_firm', 'disclosure_x_governance', 
                              'fcc_reportable', 'fcc_x_immediate']])
model5 = sm.OLS(y, X5).fit(cov_type='HC3')

# Model 6: Full controls
X6 = sm.add_constant(reg_df[['return_volatility_pre', 'immediate_disclosure', 
                              'large_firm', 'disclosure_x_governance', 
                              'fcc_reportable', 'fcc_x_immediate',
                              'firm_size_log', 'leverage', 'roa']])
model6 = sm.OLS(y, X6).fit(cov_type='HC3')

models_post = [model1, model2, model3, model4, model5, model6]

print("\n" + "=" * 80)
print("TABLE 4: POST-BREACH VOLATILITY REGRESSIONS")
print("=" * 80)

for i, model in enumerate(models_post, 1):
    print(f"\nModel {i}: N={int(model.nobs)}, R²={model.rsquared:.4f}, Adj R²={model.rsquared_adj:.4f}")
    print(model.summary().tables[1])
    print("\n" + "-" * 80)

# ============================================================
# SECTION 4: ALTERNATIVE SPECIFICATION - VOLATILITY CHANGE
# ============================================================

print("\n" + "=" * 60)
print("SECTION 4: ROBUSTNESS - VOLATILITY CHANGE AS DV")
print("=" * 60)

y_change = reg_df['return_volatility_post'] - reg_df['return_volatility_pre']

# Model with change
X_change = sm.add_constant(reg_df[['immediate_disclosure', 'large_firm', 
                                    'disclosure_x_governance', 'fcc_reportable',
                                    'firm_size_log', 'leverage', 'roa']])
model_change = sm.OLS(y_change, X_change).fit(cov_type='HC3')

print(f"\nVolatility Change Model: N={int(model_change.nobs)}, R²={model_change.rsquared:.4f}")
print(model_change.summary().tables[1])

# ============================================================
# SECTION 5: LOGISTIC REGRESSION - PROBABILITY OF INCREASED VOLATILITY
# ============================================================

print("\n" + "=" * 60)
print("SECTION 5: LOGISTIC REGRESSION")
print("DV = PROBABILITY OF INCREASED VOLATILITY")
print("=" * 60)

reg_df_logit = analysis_df[['volatility_increased', 'immediate_disclosure', 
                             'fcc_reportable', 'large_firm',
                             'firm_size_log', 'leverage', 'roa']].dropna()

reg_df_logit['disclosure_x_governance'] = reg_df_logit['immediate_disclosure'] * reg_df_logit['large_firm']
reg_df_logit['fcc_x_immediate'] = reg_df_logit['fcc_reportable'] * reg_df_logit['immediate_disclosure']

print(f"\n✓ Logit sample: n={len(reg_df_logit)}")

# Logit Model
X_logit = sm.add_constant(reg_df_logit[['immediate_disclosure', 'large_firm', 
                                         'disclosure_x_governance', 'fcc_reportable',
                                         'firm_size_log', 'leverage', 'roa']])
model_logit = sm.Logit(reg_df_logit['volatility_increased'], X_logit).fit(disp=0)

print(f"\nLogit Model: N={int(model_logit.nobs)}, Pseudo R²={model_logit.prsquared:.4f}")
print(model_logit.summary().tables[1])

# Calculate marginal effects
marginal_effects = model_logit.get_margeff()
print("\n" + "=" * 60)
print("MARGINAL EFFECTS (Percentage Point Change in Probability)")
print("=" * 60)
print(marginal_effects.summary())

# ============================================================
# SECTION 6: INTERACTION EFFECTS VISUALIZATION
# ============================================================

print("\n" + "=" * 60)
print("SECTION 6: CREATING FIGURES")
print("=" * 60)

# Set style
sns.set_style("whitegrid")
plt.rcParams['font.size'] = 11

# Figure 1: Post-breach volatility by disclosure timing
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

bp1 = ax1.boxplot([immediate['return_volatility_post'].dropna(), 
                    delayed['return_volatility_post'].dropna()],
                   labels=['Immediate\n(≤7 days)', 'Delayed\n(>30 days)'],
                   patch_artist=True, widths=0.6)

for patch in bp1['boxes']:
    patch.set_facecolor('lightblue')
    patch.set_alpha(0.7)

ax1.set_ylabel('Post-Breach Volatility (%)', fontsize=12, fontweight='bold')
ax1.set_title(f'Post-Breach Volatility by Disclosure Timing\n(p={ttest_post[1]:.3f})', 
              fontsize=12, fontweight='bold')
ax1.grid(axis='y', alpha=0.3)

means1 = [immediate['return_volatility_post'].mean(), delayed['return_volatility_post'].mean()]
ax1.scatter([1, 2], means1, color='darkred', s=200, zorder=3, marker='D', label='Mean')

# Figure 1b: By FCC status
bp2 = ax2.boxplot([nonfcc_firms['return_volatility_post'].dropna(), 
                    fcc_firms['return_volatility_post'].dropna()],
                   labels=['Non-FCC', 'FCC-Regulated'],
                   patch_artist=True, widths=0.6)

colors = ['#1f77b4', '#ff7f0e']
for patch, color in zip(bp2['boxes'], colors):
    patch.set_facecolor(color)
    patch.set_alpha(0.7)

ax2.set_ylabel('Post-Breach Volatility (%)', fontsize=12, fontweight='bold')
ax2.set_title(f'Post-Breach Volatility by Regulatory Status\n(p={ttest_fcc[1]:.3f})', 
              fontsize=12, fontweight='bold')
ax2.grid(axis='y', alpha=0.3)

means2 = [nonfcc_firms['return_volatility_post'].mean(), fcc_firms['return_volatility_post'].mean()]
ax2.scatter([1, 2], means2, color='darkred', s=200, zorder=3, marker='D', label='Mean')

plt.suptitle(f'Information Asymmetry Effects (n={len(analysis_df)})', 
             fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig('outputs/essay3_revised/figures/FIGURE1_volatility_comparisons.png', dpi=300, bbox_inches='tight')
plt.close()

print("✓ Figure 1: Volatility comparisons")

# Figure 2: Interaction plot (predicted values)
fig, ax = plt.subplots(figsize=(10, 7))

# Create prediction data that matches Model 6 exactly
# Average values for control variables
mean_pre_vol = reg_df['return_volatility_pre'].mean()
mean_firm_size = reg_df['firm_size_log'].mean()
mean_leverage = reg_df['leverage'].mean()
mean_roa = reg_df['roa'].mean()

# Four scenarios: immediate/delayed × large/small
scenarios = []
for immediate in [0, 1]:
    for large in [0, 1]:
        scenarios.append({
            'return_volatility_pre': mean_pre_vol,
            'immediate_disclosure': immediate,
            'large_firm': large,
            'disclosure_x_governance': immediate * large,
            'fcc_reportable': 0,  # Hold FCC constant at 0
            'fcc_x_immediate': 0,
            'firm_size_log': mean_firm_size,
            'leverage': mean_leverage,
            'roa': mean_roa
        })

pred_df = pd.DataFrame(scenarios)
X_pred = sm.add_constant(pred_df[model6.model.exog_names[1:]])  # Match model's variable order

try:
    predictions = model6.predict(X_pred)
    
    # Extract predictions
    delayed_small = predictions[0]   # immediate=0, large=0
    delayed_large = predictions[1]   # immediate=0, large=1
    immediate_small = predictions[2]  # immediate=1, large=0
    immediate_large = predictions[3]  # immediate=1, large=1
    
    # Plot interaction
    x = [0, 1]
    ax.plot(x, [delayed_small, immediate_small], 'o-', linewidth=3, markersize=10, 
            label='Small Firms', color='#ff7f0e')
    ax.plot(x, [delayed_large, immediate_large], 's-', linewidth=3, markersize=10, 
            label='Large Firms', color='#1f77b4')
    
    ax.set_xticks([0, 1])
    ax.set_xticklabels(['Delayed\nDisclosure', 'Immediate\nDisclosure'])
    ax.set_ylabel('Predicted Post-Breach Volatility (%)', fontsize=12, fontweight='bold')
    ax.set_title('Disclosure Timing × Governance Interaction\n(Model 6 Predictions)', 
                 fontsize=13, fontweight='bold')
    ax.legend(fontsize=11, loc='best')
    ax.grid(alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('outputs/essay3_revised/figures/FIGURE2_interaction_plot.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("✓ Figure 2: Interaction plot")
    
except Exception as e:
    print(f"⚠ Figure 2 skipped due to prediction error: {str(e)}")
    plt.close()

# Figure 3: Coefficient comparison across models
fig, ax = plt.subplots(figsize=(10, 8))

coeffs_compare = pd.DataFrame({
    'Variable': ['Immediate Disclosure', 'Large Firm', 'Disclosure × Governance', 
                 'FCC Regulated', 'FCC × Immediate'],
    'Model3_coef': [
        model3.params['immediate_disclosure'],
        model3.params['large_firm'],
        model3.params['disclosure_x_governance'],
        0, 0
    ],
    'Model3_se': [
        model3.bse['immediate_disclosure'],
        model3.bse['large_firm'],
        model3.bse['disclosure_x_governance'],
        0, 0
    ],
    'Model6_coef': [
        model6.params['immediate_disclosure'],
        model6.params['large_firm'],
        model6.params['disclosure_x_governance'],
        model6.params['fcc_reportable'],
        model6.params['fcc_x_immediate']
    ],
    'Model6_se': [
        model6.bse['immediate_disclosure'],
        model6.bse['large_firm'],
        model6.bse['disclosure_x_governance'],
        model6.bse['fcc_reportable'],
        model6.bse['fcc_x_immediate']
    ]
})

y_pos = np.arange(len(coeffs_compare))

# Model 3
mask3 = coeffs_compare['Model3_coef'] != 0
ax.errorbar(coeffs_compare.loc[mask3, 'Model3_coef'], 
           y_pos[mask3] - 0.15, 
           xerr=coeffs_compare.loc[mask3, 'Model3_se']*1.96, 
           fmt='o', markersize=8, capsize=5, capthick=2, color='blue', 
           label='Model 3 (Base + Interaction)', alpha=0.7)

# Model 6
ax.errorbar(coeffs_compare['Model6_coef'], y_pos + 0.15, 
           xerr=coeffs_compare['Model6_se']*1.96, 
           fmt='s', markersize=8, capsize=5, capthick=2, color='orange', 
           label='Model 6 (Full Controls)', alpha=0.7)

ax.axvline(0, color='red', linestyle='--', linewidth=2, alpha=0.7)
ax.set_yticks(y_pos)
ax.set_yticklabels(coeffs_compare['Variable'])
ax.set_xlabel('Coefficient Estimate (95% CI)', fontsize=12, fontweight='bold')
ax.set_title('Information Asymmetry Effects: Coefficient Comparison', 
             fontsize=13, fontweight='bold')
ax.legend(fontsize=11)
ax.grid(axis='x', alpha=0.3)

plt.tight_layout()
plt.savefig('outputs/essay3_revised/figures/FIGURE3_coefficient_comparison.png', dpi=300, bbox_inches='tight')
plt.close()

print("✓ Figure 3: Coefficient comparison")

# ============================================================
# SAVE ALL OUTPUT
# ============================================================

with open('outputs/essay3_revised/tables/FULL_REGRESSION_OUTPUT.txt', 'w') as f:
    f.write("="*80 + "\n")
    f.write("ESSAY 3: COMPLETE REGRESSION OUTPUT\n")
    f.write("Information Asymmetry and Disclosure Timing\n")
    f.write("="*80 + "\n\n")
    
    f.write("POST-BREACH VOLATILITY MODELS\n")
    f.write("="*80 + "\n")
    for i, model in enumerate(models_post, 1):
        f.write(f"\n{'='*80}\n")
        f.write(f"MODEL {i}\n")
        f.write(f"{'='*80}\n")
        f.write(str(model.summary()))
        f.write("\n\n")
    
    f.write("\n\nVOLATILITY CHANGE MODEL\n")
    f.write("="*80 + "\n")
    f.write(str(model_change.summary()))
    
    f.write("\n\nLOGISTIC REGRESSION\n")
    f.write("="*80 + "\n")
    f.write(str(model_logit.summary()))

print("✓ Full regression output saved")

# Create summary comparison table
summary_table = pd.DataFrame({
    'Hypothesis': [
        'H1: Immediate disclosure reduces volatility',
        'H2: Large firms moderate effect',
        'H3: Disclosure × Governance interaction',
        'FCC regulation increases volatility'
    ],
    'Model 6 Coefficient': [
        model6.params['immediate_disclosure'],
        model6.params['large_firm'],
        model6.params['disclosure_x_governance'],
        model6.params['fcc_reportable']
    ],
    'P-value': [
        model6.pvalues['immediate_disclosure'],
        model6.pvalues['large_firm'],
        model6.pvalues['disclosure_x_governance'],
        model6.pvalues['fcc_reportable']
    ],
    'Supported?': [
        '✓' if model6.pvalues['immediate_disclosure'] < 0.10 and model6.params['immediate_disclosure'] < 0 else '✗',
        '✓' if model6.pvalues['large_firm'] < 0.10 else '✗',
        '✓' if model6.pvalues['disclosure_x_governance'] < 0.10 else '✗',
        '✓' if model6.pvalues['fcc_reportable'] < 0.10 else '✗'
    ]
})

summary_table.to_csv('outputs/essay3_revised/tables/TABLE5_hypothesis_tests.csv', index=False)

# ============================================================
# FINAL SUMMARY
# ============================================================

print("\n" + "=" * 80)
print("✓✓✓ ESSAY 3 REVISED ANALYSIS COMPLETE ✓✓✓")
print("=" * 80)

print(f"\n📊 SAMPLE SIZE: n={len(analysis_df)}")

print(f"\n🔑 MAIN FINDINGS (Model 6 - Post-Breach Volatility):")
print(f"\n  Pre-breach volatility control: {model6.params['return_volatility_pre']:.4f} (p={model6.pvalues['return_volatility_pre']:.4f})")
print(f"  → Strong persistence of volatility (R²={model6.rsquared:.4f})")

print(f"\n  H1 - Immediate disclosure: {model6.params['immediate_disclosure']:.4f} (p={model6.pvalues['immediate_disclosure']:.4f})")
if model6.pvalues['immediate_disclosure'] < 0.05:
    print(f"  → ✓ Supported at p<0.05")
elif model6.pvalues['immediate_disclosure'] < 0.10:
    print(f"  → ✓ Marginally supported at p<0.10")
else:
    print(f"  → ✗ Not supported")

print(f"\n  H2 - Large firm (governance): {model6.params['large_firm']:.4f} (p={model6.pvalues['large_firm']:.4f})")
if model6.pvalues['large_firm'] < 0.05:
    print(f"  → ✓ Supported at p<0.05")
elif model6.pvalues['large_firm'] < 0.10:
    print(f"  → ✓ Marginally supported at p<0.10")
else:
    print(f"  → ✗ Not supported")

print(f"\n  H3 - Disclosure × Governance: {model6.params['disclosure_x_governance']:.4f} (p={model6.pvalues['disclosure_x_governance']:.4f})")
if model6.pvalues['disclosure_x_governance'] < 0.05:
    print(f"  → ✓ Supported at p<0.05")
elif model6.pvalues['disclosure_x_governance'] < 0.10:
    print(f"  → ✓ Marginally supported at p<0.10")
else:
    print(f"  → ✗ Not supported")

print(f"\n  FCC regulation effect: {model6.params['fcc_reportable']:.4f} (p={model6.pvalues['fcc_reportable']:.4f})")

print(f"\n💡 INTERPRETATION:")
if model6.pvalues['return_volatility_pre'] < 0.001:
    print(f"  Strong volatility persistence explains most variation (R²={model6.rsquared:.4f})")
    print(f"  Disclosure timing effects are modest after controlling for baseline volatility")

print(f"\n📊 ROBUSTNESS CHECKS:")
print(f"  Volatility change model R²: {model_change.rsquared:.4f}")
print(f"  Logistic model (increased volatility) Pseudo R²: {model_logit.prsquared:.4f}")

print(f"\n📁 OUTPUT FILES:")
print(f"   Tables: outputs/essay3_revised/tables/")
print(f"   - TABLE1_descriptives.csv")
print(f"   - TABLE2_composition.csv")
print(f"   - TABLE3_univariate.csv")
print(f"   - TABLE4: Full regression results (in .txt file)")
print(f"   - TABLE5_hypothesis_tests.csv")
print(f"   - FULL_REGRESSION_OUTPUT.txt")
print(f"\n   Figures: outputs/essay3_revised/figures/")
print(f"   - FIGURE1_volatility_comparisons.png")
print(f"   - FIGURE2_interaction_plot.png")
print(f"   - FIGURE3_coefficient_comparison.png")

print(f"\n✅ Ready for Essay 3 write-up!")
print(f"   Main DV: Post-breach volatility (controls for pre-breach)")
print(f"   Robustness: Change model + Logistic model")
print(f"   Key finding: {summary_table['Supported?'].sum()} of 4 hypotheses supported")