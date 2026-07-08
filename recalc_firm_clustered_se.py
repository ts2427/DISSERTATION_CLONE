#!/usr/bin/env python3
"""Recalculate firm-clustered SEs with correct 372 clusters"""

import pandas as pd
import numpy as np
import statsmodels.api as sm
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Load data
df = pd.read_csv('Data/processed/FINAL_DISSERTATION_DATASET_WITH_GOVERNANCE.csv')

# Map columns
df['FCC'] = df['fcc_reportable'].astype(int)
df['firm_size'] = df['firm_size_log']
df['prior_breaches'] = df['prior_breaches_total']
df['pre_breach_volatility'] = df['return_volatility_pre']

# Regression sample
df = df.dropna(subset=['volatility_change', 'FCC', 'firm_size', 'leverage', 'roa', 'pre_breach_volatility', 'health_breach', 'prior_breaches'])

y = df['volatility_change'].values
controls = ['pre_breach_volatility', 'firm_size', 'leverage', 'roa', 'health_breach', 'prior_breaches']

# Main specification with HC3 (baseline)
X_main = df[['FCC'] + controls].copy()
X_main = sm.add_constant(X_main)
m_hc3 = sm.OLS(y, X_main).fit(cov_type='HC3')

print("="*70)
print("FIRM-CLUSTERED STANDARD ERROR CALCULATION")
print("="*70)

# Firm-clustered (correct: 372 clusters, not 8)
groups = df['org_name'].values
n_clusters = len(np.unique(groups))

m_firm = sm.OLS(y, X_main).fit(cov_type='cluster', cov_kwds={'groups': groups})

print(f"\nFirm clusters: {n_clusters}")
print(f"Sample size: {len(df)}")
print(f"Breaches per firm (mean): {len(df) / n_clusters:.2f}")

print(f"\nFCC Coefficient (Firm-clustered):")
print(f"  Coefficient: {m_firm.params['FCC']:.4f}%")
print(f"  Std Error: {m_firm.bse['FCC']:.4f}")
print(f"  t-stat: {m_firm.tvalues['FCC']:.4f}")
print(f"  p-value: {m_firm.pvalues['FCC']:.4f}")

print(f"\nComparison to HC3:")
print(f"  HC3 SE: {m_hc3.bse['FCC']:.4f}")
print(f"  HC3 p-value: {m_hc3.pvalues['FCC']:.4f}")
print(f"  Firm-clustered SE: {m_firm.bse['FCC']:.4f}")
print(f"  Firm-clustered p-value: {m_firm.pvalues['FCC']:.4f}")

print(f"\nR-squared: {m_firm.rsquared:.4f}")

print("\n" + "="*70)
print("SAVE FOR APPENDIX")
print("="*70)

fcc_coeff = m_firm.params['FCC']
fcc_se = m_firm.bse['FCC']
fcc_pval = m_firm.pvalues['FCC']
t_stat = m_firm.tvalues['FCC']

print(f"\nTABLE C5 row - Firm-clustered ({n_clusters} firm clusters):")
print(f"  FCC Coefficient: {fcc_coeff:.3f}%")
print(f"  SE: {fcc_se:.4f}")
print(f"  t-stat: {t_stat:.2f}")
print(f"  p-value: {fcc_pval:.4f}")

# Also calculate year-clustered and announcement-date clustered for comparison
year_groups = df['breach_year'].values
m_year = sm.OLS(y, X_main).fit(cov_type='cluster', cov_kwds={'groups': year_groups})
n_year_clusters = len(np.unique(year_groups))

announcement_groups = df['announcement_date'].values
m_announce = sm.OLS(y, X_main).fit(cov_type='cluster', cov_kwds={'groups': announcement_groups})
n_announce_clusters = len(np.unique(announcement_groups))

print(f"\n\nOTHER CLUSTER SPECIFICATIONS FOR COMPARISON:")
print(f"\nYear-clustered ({n_year_clusters} clusters):")
print(f"  SE: {m_year.bse['FCC']:.4f}, p-value: {m_year.pvalues['FCC']:.4f}")

print(f"\nAnnouncement-date clustered ({n_announce_clusters} clusters):")
print(f"  SE: {m_announce.bse['FCC']:.4f}, p-value: {m_announce.pvalues['FCC']:.4f}")

