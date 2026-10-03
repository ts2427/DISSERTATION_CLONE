"""
H2 FIRM-LEVEL ESTIMATION
Complement breach-level result with firm-level analysis
One observation per firm, aggregating across all breaches
"""

import pandas as pd
import numpy as np
import statsmodels.api as sm

print("=" * 80)
print("H2 FIRM-LEVEL ESTIMATION")
print("=" * 80)

df = pd.read_csv('Data/processed/FINAL_DISSERTATION_DATASET_DEDUPLICATED_ENRICHED.csv')
df = df.dropna(subset=['car_30d', 'firm_size_log', 'leverage', 'roa'])

# Aggregate to firm level: one observation per firm
# Mean outcomes across all breaches for that firm
firm_level = df.groupby('cik').agg(
    car_30d=('car_30d', 'mean'),
    fcc_reportable=('fcc_reportable', 'first'),
    firm_size_log=('firm_size_log', 'mean'),
    leverage=('leverage', 'mean'),
    roa=('roa', 'mean'),
    immediate_disclosure=('immediate_disclosure', 'mean'),
    prior_breaches_1yr=('prior_breaches_1yr', 'mean'),
    health_breach=('health_breach', 'mean'),
    n_breaches=('car_30d', 'count'),
    org_name=('org_name', 'first')
).reset_index()

print("\nFIRM-LEVEL SAMPLE COMPOSITION")
print("=" * 80)
print(f"Total firms: {len(firm_level)}")
print(f"FCC firms: {int(firm_level['fcc_reportable'].sum())}")
print(f"Non-FCC firms: {int((~firm_level['fcc_reportable'].astype(bool)).sum())}")

print(f"\nFCC firms and breach counts:")
print(f"{'Firm':<40} {'N Breaches':>12} {'Mean CAR':>12}")
print("-" * 65)
fcc_firms = firm_level[firm_level['fcc_reportable']==True].sort_values('n_breaches', ascending=False)
for _, row in fcc_firms.iterrows():
    print(f"{str(row['org_name'])[:39]:<40} {int(row['n_breaches']):>12} {row['car_30d']:>12.4f}%")

print(f"\n" + "-" * 65)
print(f"Summary:")
print(f"  Mean breaches per FCC firm: {fcc_firms['n_breaches'].mean():.1f}")
print(f"  Range: {int(fcc_firms['n_breaches'].min())} to {int(fcc_firms['n_breaches'].max())}")

# Firm-level regression
print(f"\n\nFIRM-LEVEL REGRESSION ANALYSIS")
print("=" * 80)

controls = ['immediate_disclosure', 'prior_breaches_1yr', 'health_breach',
            'firm_size_log', 'leverage', 'roa']
X = sm.add_constant(firm_level[['fcc_reportable'] + controls].astype(float))
y = firm_level['car_30d']

model_firm = sm.OLS(y, X).fit(cov_type='HC3')

print(f"\nH2 COEFFICIENT (Firm-Level):")
print(f"  Coefficient: {model_firm.params['fcc_reportable']:.4f}%")
print(f"  Std Error: {model_firm.bse['fcc_reportable']:.4f}")
print(f"  t-statistic: {model_firm.tvalues['fcc_reportable']:.4f}")
print(f"  p-value: {model_firm.pvalues['fcc_reportable']:.4f}")
print(f"  95% CI: [{model_firm.conf_int().loc['fcc_reportable',0]:.4f}%, {model_firm.conf_int().loc['fcc_reportable',1]:.4f}%]")

print(f"\nModel Fit:")
print(f"  N observations: {len(firm_level)}")
print(f"  R-squared: {model_firm.rsquared:.4f}")
print(f"  Adjusted R-squared: {model_firm.rsquared_adj:.4f}")
print(f"  F-statistic: {model_firm.fvalue:.4f}")
print(f"  F p-value: {model_firm.f_pvalue:.4f}")

# All coefficients
print(f"\nAll Coefficients (Firm-Level):")
print(f"{'Variable':<30} {'Coef':>12} {'Std Err':>12} {'p-value':>10} {'Sig':>4}")
print("-" * 70)
for var in model_firm.params.index:
    coef = model_firm.params[var]
    se = model_firm.bse[var]
    pval = model_firm.pvalues[var]
    sig = '***' if pval < 0.01 else '**' if pval < 0.05 else '*' if pval < 0.10 else 'ns'
    print(f"{var:<30} {coef:>12.4f} {se:>12.4f} {pval:>10.4f} {sig:>4}")

# Simple univariate comparison
print(f"\n\nUNIVARIATE FIRM-LEVEL COMPARISON")
print("=" * 80)
fcc_mean = firm_level[firm_level['fcc_reportable']==True]['car_30d'].mean()
nonfcc_mean = firm_level[firm_level['fcc_reportable']==False]['car_30d'].mean()

print(f"FCC firms (n={int(firm_level['fcc_reportable'].sum())}):")
print(f"  Mean CAR: {fcc_mean:.4f}%")
print(f"  Std Dev: {firm_level[firm_level['fcc_reportable']==True]['car_30d'].std():.4f}%")
print(f"  Range: [{firm_level[firm_level['fcc_reportable']==True]['car_30d'].min():.4f}%, {firm_level[firm_level['fcc_reportable']==True]['car_30d'].max():.4f}%]")

print(f"\nNon-FCC firms (n={int((~firm_level['fcc_reportable'].astype(bool)).sum())}):")
print(f"  Mean CAR: {nonfcc_mean:.4f}%")
print(f"  Std Dev: {firm_level[firm_level['fcc_reportable']==False]['car_30d'].std():.4f}%")
print(f"  Range: [{firm_level[firm_level['fcc_reportable']==False]['car_30d'].min():.4f}%, {firm_level[firm_level['fcc_reportable']==False]['car_30d'].max():.4f}%]")

print(f"\nDifference (FCC - Non-FCC): {fcc_mean - nonfcc_mean:.4f}pp")

# Simple t-test
from scipy import stats
fcc_cars = firm_level[firm_level['fcc_reportable']==True]['car_30d'].values
nonfcc_cars = firm_level[firm_level['fcc_reportable']==False]['car_30d'].values
t_stat, t_pval = stats.ttest_ind(fcc_cars, nonfcc_cars)
print(f"T-test p-value: {t_pval:.4f}")

# Comparison table
print(f"\n\nBREACH-LEVEL vs FIRM-LEVEL COMPARISON")
print("=" * 80)
print(f"{'Specification':<35} {'Coef':>12} {'SE':>10} {'p-value':>10} {'N':>6}")
print("-" * 75)

# Breach-level (from prior analysis)
breach_level_coef = -2.1179
breach_level_se = 1.0776
breach_level_pval = 0.0494
breach_level_n = 653

firm_level_coef = model_firm.params['fcc_reportable']
firm_level_se = model_firm.bse['fcc_reportable']
firm_level_pval = model_firm.pvalues['fcc_reportable']
firm_level_n = len(firm_level)

print(f"{'Breach-level (primary)':<35} {breach_level_coef:>12.4f} {breach_level_se:>10.4f} {breach_level_pval:>10.4f} {breach_level_n:>6}")
print(f"{'Firm-level (robustness)':<35} {firm_level_coef:>12.4f} {firm_level_se:>10.4f} {firm_level_pval:>10.4f} {firm_level_n:>6}")

print(f"\nDifference in point estimate: {abs(firm_level_coef - breach_level_coef):.4f}pp")
print(f"Ratio (firm-level / breach-level): {firm_level_coef / breach_level_coef:.2f}x")

# Save results
firm_level.to_csv('outputs/defense_prep/h2_firm_level_data.csv', index=False)

# Save model summary
with open('outputs/defense_prep/h2_firm_level_model_summary.txt', 'w') as f:
    f.write("=" * 80 + "\n")
    f.write("H2 FIRM-LEVEL REGRESSION SUMMARY\n")
    f.write("=" * 80 + "\n\n")
    f.write(str(model_firm.summary()))
    f.write("\n\n" + "=" * 80 + "\n")
    f.write("INTERPRETATION NOTES\n")
    f.write("=" * 80 + "\n")
    f.write(f"\nH2 Coefficient (Firm-Level): {firm_level_coef:.4f}% (p={firm_level_pval:.4f})\n")
    f.write(f"Breach-Level (Primary): {breach_level_coef:.4f}% (p={breach_level_pval:.4f})\n\n")
    f.write("Sample Notes:\n")
    f.write(f"  - Breach-level: n={breach_level_n} observations, {int(firm_level['fcc_reportable'].sum())} FCC firms\n")
    f.write(f"  - Firm-level: n={firm_level_n} firms total, {int(firm_level['fcc_reportable'].sum())} FCC firms\n")
    f.write(f"  - Each FCC firm averages {fcc_firms['n_breaches'].mean():.1f} breaches\n\n")
    f.write("Key Finding:\n")
    if firm_level_pval < 0.05:
        f.write(f"  H2 is SIGNIFICANT at firm level (p={firm_level_pval:.4f})\n")
    else:
        f.write(f"  H2 is NOT SIGNIFICANT at firm level (p={firm_level_pval:.4f})\n")
        f.write(f"  This is expected with only {int(firm_level['fcc_reportable'].sum())} treated firms (n=9)\n")
        f.write(f"  Breach-level analysis has more power due to larger effective sample size (n={breach_level_n})\n")

print("\n" + "=" * 80)
print("OUTPUT SAVED")
print("=" * 80)
print("  - outputs/defense_prep/h2_firm_level_data.csv")
print("  - outputs/defense_prep/h2_firm_level_model_summary.txt")
