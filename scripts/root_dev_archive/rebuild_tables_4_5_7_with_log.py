"""
REBUILD TABLES 4, 5, 7 WITH RECONCILIATION LOGGING
Compute actual values from regressions instead of placeholders
Log all computations for verification
"""

import pandas as pd
import numpy as np
import statsmodels.api as sm
from scipy import stats
import sys

print("=" * 100)
print("REBUILDING TABLES 4, 5, 7 WITH RECONCILIATION LOG")
print("=" * 100)

# Load data
df = pd.read_csv('Data/processed/FINAL_DISSERTATION_DATASET_DEDUPLICATED_ENRICHED.csv')

# Define controls and prepare samples
controls = ['immediate_disclosure', 'fcc_reportable', 'prior_breaches_1yr',
            'health_breach', 'firm_size_log', 'leverage', 'roa']

# 648 sample (main regression)
df_648 = df[df['car_30d'].notna()].dropna(subset=controls).copy()
assert len(df_648) == 648, f"Sample size error: expected 648, got {len(df_648)}"

# ============================================================================
# TABLE 4: TIMING BY REGULATORY REGIME
# ============================================================================
print("\n" + "=" * 100)
print("TABLE 4: TIMING BY REGULATORY REGIME")
print("=" * 100)

# Run separate regressions for FCC and non-FCC
table4_results = []

for fcc_val, label in [(1, 'FCC-Regulated'), (0, 'Non-FCC')]:
    df_s = df_648[df_648['fcc_reportable'] == fcc_val]
    n_s = len(df_s)

    X_s = sm.add_constant(df_s[controls].astype(float))
    y_s = df_s['car_30d']
    m_s = sm.OLS(y_s, X_s).fit(cov_type='HC3')

    coef = m_s.params['immediate_disclosure']
    se = m_s.bse['immediate_disclosure']
    pval = m_s.pvalues['immediate_disclosure']

    print(f"\n{label} (N={n_s}):")
    print(f"  Timing coefficient: {coef:.4f}%")
    print(f"  SE: {se:.4f}")
    print(f"  t-ratio: {coef/se:.4f}")
    print(f"  p-value: {pval:.4f}")

    table4_results.append({
        'label': label,
        'n': n_s,
        'coef': coef,
        'se': se,
        'pval': pval,
    })

# Test interaction (FCC × Timing)
print("\n" + "-" * 100)
print("INTERACTION TEST: FCC × Immediate Disclosure")
print("-" * 100)

X_int = sm.add_constant(df_648[controls + ['fcc_reportable']].astype(float))
# Create interaction term
df_648['fcc_immed_interact'] = df_648['fcc_reportable'] * df_648['immediate_disclosure']
X_int = sm.add_constant(df_648[controls + ['fcc_immed_interact']].astype(float))
y_int = df_648['car_30d']
m_int = sm.OLS(y_int, X_int).fit(cov_type='HC3')

interact_coef = m_int.params['fcc_immed_interact']
interact_se = m_int.bse['fcc_immed_interact']
interact_pval = m_int.pvalues['fcc_immed_interact']

print(f"Interaction coefficient: {interact_coef:.4f}%")
print(f"SE: {interact_se:.4f}")
print(f"p-value: {interact_pval:.4f}")

# ============================================================================
# TABLE 5: SAMPLE RESTRICTIONS
# ============================================================================
print("\n" + "=" * 100)
print("TABLE 5: SAMPLE RESTRICTIONS")
print("=" * 100)

restrictions = [
    ('Full sample', df_648, None),
    ('Exclude largest decile', df_648, lambda x: x['firm_size_log'] < df_648['firm_size_log'].quantile(0.9)),
    ('Exclude smallest decile', df_648, lambda x: x['firm_size_log'] > df_648['firm_size_log'].quantile(0.1)),
    ('Exclude outliers (3 SD)', df_648, lambda x: np.abs(x['car_30d'] - df_648['car_30d'].mean()) <= 3*df_648['car_30d'].std()),
]

table5_results = []

for label, df_base, restriction in restrictions:
    if restriction is None:
        df_r = df_base
    else:
        df_r = df_base[restriction(df_base)].copy()

    n_r = len(df_r)

    X_r = sm.add_constant(df_r[controls].astype(float))
    y_r = df_r['car_30d']
    m_r = sm.OLS(y_r, X_r).fit(cov_type='HC3')

    coef = m_r.params['immediate_disclosure']
    pval = m_r.pvalues['immediate_disclosure']

    print(f"\n{label} (N={n_r}):")
    print(f"  Timing coefficient: {coef:.4f}%")
    print(f"  p-value: {pval:.4f}")

    table5_results.append({
        'label': label,
        'n': n_r,
        'coef': coef,
        'pval': pval,
    })

# Note: Prior breach row should use lifetime measure, not 1yr
# And only includes firms with prior breaches
df_648_prior = df_648[df_648['prior_breaches_total'] > 0].copy()
n_prior = len(df_648_prior)
X_prior = sm.add_constant(df_648_prior[controls].astype(float))
y_prior = df_648_prior['car_30d']
m_prior = sm.OLS(y_prior, X_prior).fit(cov_type='HC3')

coef_prior = m_prior.params['immediate_disclosure']
pval_prior = m_prior.pvalues['immediate_disclosure']

print(f"\nPrior breach history (N={n_prior}):")
print(f"  Timing coefficient: {coef_prior:.4f}%")
print(f"  p-value: {pval_prior:.4f}")

table5_results.append({
    'label': 'Prior breach history',
    'n': n_prior,
    'coef': coef_prior,
    'pval': pval_prior,
})

# ============================================================================
# TABLE 7: FIRM-SIZE QUARTILES - TIMING
# ============================================================================
print("\n" + "=" * 100)
print("TABLE 7: TIMING BY FIRM-SIZE QUARTILE")
print("=" * 100)

df_648['size_quartile'] = pd.qcut(df_648['firm_size_log'], q=4, labels=['Q1','Q2','Q3','Q4'], duplicates='drop')

table7_results = []
p_values = []

for q in ['Q1', 'Q2', 'Q3', 'Q4']:
    df_q = df_648[df_648['size_quartile'] == q]
    n_q = len(df_q)

    X_q = sm.add_constant(df_q[controls].astype(float))
    y_q = df_q['car_30d']
    m_q = sm.OLS(y_q, X_q).fit(cov_type='HC3')

    coef = m_q.params['immediate_disclosure']
    se = m_q.bse['immediate_disclosure']
    pval = m_q.pvalues['immediate_disclosure']
    p_values.append(pval)

    label = f"{q} (Small)" if q == 'Q1' else (f"{q} (Large)" if q == 'Q4' else q)

    print(f"\n{label} (N={n_q}):")
    print(f"  Timing coefficient: {coef:.4f}%")
    print(f"  SE: {se:.4f}")
    print(f"  t-ratio: {coef/se:.4f}")
    print(f"  p-value: {pval:.4f}")

    table7_results.append({
        'label': label,
        'n': n_q,
        'coef': coef,
        'se': se,
        'pval': pval,
    })

print(f"\nP-value range: {min(p_values):.4f} to {max(p_values):.4f}")
print(f"(Text claims: 0.36 to 0.72)")

# ============================================================================
# SUMMARY FOR EXPORT
# ============================================================================
print("\n" + "=" * 100)
print("SUMMARY: COMPUTED VALUES READY FOR TABLE BUILD")
print("=" * 100)

print("\nTABLE 4 (Regulatory Regime):")
for row in table4_results:
    print(f"  {row['label']:20s} N={row['n']:3d}  Coef={row['coef']:+.4f}%  SE={row['se']:.4f}  p={row['pval']:.4f}")
print(f"  Interaction (FCC × Immediate):  Coef={interact_coef:+.4f}%  SE={interact_se:.4f}  p={interact_pval:.4f}")

print("\nTABLE 5 (Sample Restrictions) - first 4:")
for row in table5_results[:4]:
    print(f"  {row['label']:35s} N={row['n']:3d}  Coef={row['coef']:+.4f}%  p={row['pval']:.4f}")

print("\nTABLE 7 (Firm-Size Quartiles):")
for row in table7_results:
    print(f"  {row['label']:20s} N={row['n']:3d}  Coef={row['coef']:+.4f}%  SE={row['se']:.4f}  p={row['pval']:.4f}")

# Save to CSV for easy reference
pd.DataFrame(table4_results).to_csv('outputs/table4_computed_values.csv', index=False)
pd.DataFrame(table5_results).to_csv('outputs/table5_computed_values.csv', index=False)
pd.DataFrame(table7_results).to_csv('outputs/table7_computed_values.csv', index=False)

print("\n" + "=" * 100)
print("Computed values saved to outputs/table[4,5,7]_computed_values.csv")
print("=" * 100)
