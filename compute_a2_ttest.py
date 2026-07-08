#!/usr/bin/env python3
"""Compute t-test for TABLE A2 ΔVolatility row"""

import pandas as pd
import numpy as np
from scipy import stats

df = pd.read_csv('Data/processed/FINAL_DISSERTATION_DATASET_WITH_GOVERNANCE.csv')

df['FCC'] = df['fcc_reportable'].astype(int)
df['firm_size'] = df['firm_size_log']
df['prior_breaches'] = df['prior_breaches_total']
df['pre_breach_volatility'] = df['return_volatility_pre']

df = df.dropna(subset=['volatility_change', 'FCC', 'firm_size', 'leverage', 'roa', 'pre_breach_volatility', 'health_breach', 'prior_breaches'])

fcc_vol = df[df['FCC'] == 1]['volatility_change']
non_fcc_vol = df[df['FCC'] == 0]['volatility_change']

# Independent samples t-test
t_stat, p_val = stats.ttest_ind(fcc_vol, non_fcc_vol)

print(f"FCC mean: {fcc_vol.mean():.3f}%")
print(f"Non-FCC mean: {non_fcc_vol.mean():.3f}%")
print(f"Difference: {fcc_vol.mean() - non_fcc_vol.mean():.3f}pp")
print(f"\nt-statistic: {t_stat:.2f}")
print(f"p-value (two-tailed): {p_val:.4f}")

# Verify other rows
print("\n" + "="*60)
print("VERIFY OTHER DESCRIPTIVE ROWS")
print("="*60)

# Pre-breach volatility
pre_fcc = df[df['FCC'] == 1]['return_volatility_pre']
pre_non = df[df['FCC'] == 0]['return_volatility_pre']
t_pre, p_pre = stats.ttest_ind(pre_fcc, pre_non)
print(f"\nPre-breach volatility:")
print(f"  FCC: {pre_fcc.mean():.2f}% (appendix shows 26.32%)")
print(f"  Non-FCC: {pre_non.mean():.2f}% (appendix shows 26.14%)")
print(f"  t-stat: {t_pre:.2f}, p-value: {p_pre:.4f}")

# Post-breach volatility
post_fcc = df[df['FCC'] == 1]['return_volatility_post']
post_non = df[df['FCC'] == 0]['return_volatility_post']
t_post, p_post = stats.ttest_ind(post_fcc, post_non)
print(f"\nPost-breach volatility:")
print(f"  FCC: {post_fcc.mean():.2f}% (appendix shows 28.13%)")
print(f"  Non-FCC: {post_non.mean():.2f}% (appendix shows 26.96%)")
print(f"  t-stat: {t_post:.2f}, p-value: {p_post:.4f}")

# Firm size
size_fcc = df[df['FCC'] == 1]['firm_size']
size_non = df[df['FCC'] == 0]['firm_size']
t_size, p_size = stats.ttest_ind(size_fcc, size_non)
print(f"\nFirm size (log assets):")
print(f"  FCC: {size_fcc.mean():.2f} (appendix shows 10.79)")
print(f"  Non-FCC: {size_non.mean():.2f} (appendix shows 10.42)")
print(f"  t-stat: {t_size:.2f}, p-value: {p_size:.4f}")

# Leverage
lev_fcc = df[df['FCC'] == 1]['leverage']
lev_non = df[df['FCC'] == 0]['leverage']
t_lev, p_lev = stats.ttest_ind(lev_fcc, lev_non)
print(f"\nLeverage:")
print(f"  FCC: {lev_fcc.mean():.3f} (appendix shows 0.751)")
print(f"  Non-FCC: {lev_non.mean():.3f} (appendix shows 0.748)")
print(f"  t-stat: {t_lev:.2f}, p-value: {p_lev:.4f}")

# ROA
roa_fcc = df[df['FCC'] == 1]['roa']
roa_non = df[df['FCC'] == 0]['roa']
t_roa, p_roa = stats.ttest_ind(roa_fcc, roa_non)
print(f"\nROA:")
print(f"  FCC: {roa_fcc.mean():.3f} (appendix shows 0.012)")
print(f"  Non-FCC: {roa_non.mean():.3f} (appendix shows 0.010)")
print(f"  t-stat: {t_roa:.2f}, p-value: {p_roa:.4f}")

# Health breach
health_fcc = df[df['FCC'] == 1]['health_breach']
health_non = df[df['FCC'] == 0]['health_breach']
t_health, p_health = stats.ttest_ind(health_fcc, health_non)
print(f"\nHealth breach:")
print(f"  FCC: {health_fcc.mean():.3f} (appendix shows 0.120)")
print(f"  Non-FCC: {health_non.mean():.3f} (appendix shows 0.107)")
print(f"  t-stat: {t_health:.2f}, p-value: {p_health:.4f}")

# Prior breaches
pb_fcc = df[df['FCC'] == 1]['prior_breaches']
pb_non = df[df['FCC'] == 0]['prior_breaches']
t_pb, p_pb = stats.ttest_ind(pb_fcc, pb_non)
print(f"\nPrior breaches:")
print(f"  FCC: {pb_fcc.mean():.2f} (appendix shows 3.85)")
print(f"  Non-FCC: {pb_non.mean():.2f} (appendix shows 3.30)")
print(f"  t-stat: {t_pb:.2f}, p-value: {p_pb:.4f}")

# Days to disclosure
days_fcc = df[df['FCC'] == 1]['disclosure_delay_days']
days_non = df[df['FCC'] == 0]['disclosure_delay_days']
t_days, p_days = stats.ttest_ind(days_fcc, days_non)
print(f"\nDays to disclosure:")
print(f"  FCC: {days_fcc.mean():.1f} (appendix shows 124.6)")
print(f"  Non-FCC: {days_non.mean():.1f} (appendix shows 124.8)")
print(f"  t-stat: {t_days:.2f}, p-value: {p_days:.4f}")

