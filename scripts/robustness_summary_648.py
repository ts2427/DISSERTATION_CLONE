"""
ROBUSTNESS SUMMARY ON 648-OBSERVATION REGRESSION SAMPLE
========================================================

Five categories:
1. Timing thresholds (H1 effect at different disclosure lags)
2. Event windows (CAR windows of different lengths)
3. Sample restrictions (results across subsets)
4. Standard error methods (inference robustness)
5. Firm-size quartile timing effects (H1 by size)
"""

import pandas as pd
import numpy as np
import statsmodels.api as sm
import warnings
warnings.filterwarnings('ignore')

# Load data
df = pd.read_csv('Data/processed/FINAL_DISSERTATION_DATASET_DEDUPLICATED_ENRICHED.csv')

# Regression sample
controls = ['immediate_disclosure', 'fcc_reportable', 'prior_breaches_1yr',
            'health_breach', 'firm_size_log', 'leverage', 'roa']
df_reg = df[df['car_30d'].notna()].dropna(subset=controls).copy()
n_reg = len(df_reg)

print("=" * 90)
print("ESSAY 1 ROBUSTNESS SUMMARY (N={})".format(n_reg))
print("=" * 90)

# Canonical specification for reference
X_canon = sm.add_constant(df_reg[controls].astype(float))
y_canon = df_reg['car_30d']
m_canon = sm.OLS(y_canon, X_canon).fit(cov_type='HC3')

print("\nCANONICAL SPECIFICATION (baseline):")
print(f"  H1 (immediate_disclosure):  coef={m_canon.params['immediate_disclosure']:8.4f}%, p={m_canon.pvalues['immediate_disclosure']:.4f}")
print(f"  H2 (fcc_reportable):        coef={m_canon.params['fcc_reportable']:8.4f}%, p={m_canon.pvalues['fcc_reportable']:.4f}")
print(f"  H3 (prior_breaches_1yr):    coef={m_canon.params['prior_breaches_1yr']:8.4f}%, p={m_canon.pvalues['prior_breaches_1yr']:.4f}")
print(f"  H4 (health_breach):         coef={m_canon.params['health_breach']:8.4f}%, p={m_canon.pvalues['health_breach']:.4f}")

# ============================================================================
# 1. TIMING THRESHOLDS (using immediate_disclosure as proxy)
# ============================================================================
print("\n" + "=" * 90)
print("1. TIMING THRESHOLD ROBUSTNESS (H1)")
print("=" * 90)
print("\nNote: Exact timing thresholds require disclosure_date. Using immediate_disclosure:")
print(f"  Immediate (<=7d) vs Delayed (>7d):")
print(f"    H1 coefficient: {m_canon.params['immediate_disclosure']:8.4f}%")
print(f"    Standard error: {m_canon.bse['immediate_disclosure']:8.4f}")
print(f"    P-value:        {m_canon.pvalues['immediate_disclosure']:8.4f}")

# ============================================================================
# 2. FIVE EVENT WINDOWS
# ============================================================================
print("\n" + "=" * 90)
print("2. FIVE EVENT WINDOWS (CAR windows)")
print("=" * 90)

car_cols = [c for c in df_reg.columns if c.startswith('car_')]
car_cols_sorted = sorted(car_cols, key=lambda x: int(x.split('_')[1].rstrip('d')))

window_results = []
print("\nEvent window results (H2: FCC coefficient):")
for i, car_col in enumerate(car_cols_sorted[:5]):  # First 5 windows
    df_w = df_reg[df_reg[car_col].notna()].copy()
    if len(df_w) > 100:
        X_w = sm.add_constant(df_w[controls].astype(float))
        y_w = df_w[car_col]
        m_w = sm.OLS(y_w, X_w).fit(cov_type='HC3')

        window_days = int(car_col.split('_')[1].rstrip('d'))
        n_w = len(df_w)
        coef = m_w.params['fcc_reportable']
        se = m_w.bse['fcc_reportable']
        p = m_w.pvalues['fcc_reportable']

        print(f"  CAR {window_days:3d}d (N={n_w:3d}): coef={coef:8.4f}%, SE={se:.4f}, p={p:.4f}")
        window_results.append({'days': window_days, 'coef': coef, 'p': p})

# ============================================================================
# 3. EIGHT SAMPLE RESTRICTIONS
# ============================================================================
print("\n" + "=" * 90)
print("3. EIGHT SAMPLE RESTRICTIONS (H2: FCC coefficient)")
print("=" * 90)

# Define restrictions
df_reg['size_quartile'] = pd.qcut(df_reg['firm_size_log'], q=4, labels=['Q1', 'Q2', 'Q3', 'Q4'], duplicates='drop')

restrictions = {
    'Full sample': df_reg,
    'FCC firms only': df_reg[df_reg['fcc_reportable'] == True],
    'Non-FCC only': df_reg[df_reg['fcc_reportable'] == False],
    'Large firms (Q4)': df_reg[df_reg['size_quartile'] == 'Q4'],
    'Small firms (Q1)': df_reg[df_reg['size_quartile'] == 'Q1'],
    'Health breaches': df_reg[df_reg['health_breach'] == True],
    'Non-health breaches': df_reg[df_reg['health_breach'] == False],
    'Prior breach history': df_reg[df_reg['prior_breaches_total'] > 0],
}

print("\nSample restriction results:")
for name, df_s in restrictions.items():
    if len(df_s) > 20:
        try:
            X_s = sm.add_constant(df_s[controls].astype(float))
            y_s = df_s['car_30d']
            m_s = sm.OLS(y_s, X_s).fit(cov_type='HC3')

            coef = m_s.params['fcc_reportable']
            se = m_s.bse['fcc_reportable']
            p = m_s.pvalues['fcc_reportable']

            print(f"  {name:25s} (N={len(df_s):3d}): coef={coef:8.4f}%, SE={se:.4f}, p={p:.4f}")
        except:
            print(f"  {name:25s} (N={len(df_s):3d}): [failed]")

# ============================================================================
# 4. SIX STANDARD ERROR METHODS
# ============================================================================
print("\n" + "=" * 90)
print("4. SIX STANDARD ERROR METHODS (H2: FCC coefficient)")
print("=" * 90)

X_all = sm.add_constant(df_reg[controls].astype(float))
y_all = df_reg['car_30d']

se_methods = [
    ('OLS (unadjusted)', None),
    ('HC1 robust', 'HC1'),
    ('HC2 robust', 'HC2'),
    ('HC3 robust', 'HC3'),
    ('Firm-clustered', 'firm'),
    ('Date-clustered', 'date'),
]

print("\nStandard error robustness:")
for method_name, method in se_methods:
    try:
        if method == 'firm':
            m_se = sm.OLS(y_all, X_all).fit(cov_type='cluster', cov_kwds={'groups': df_reg['ticker']})
        elif method == 'date':
            m_se = sm.OLS(y_all, X_all).fit(cov_type='cluster', cov_kwds={'groups': df_reg['breach_date']})
        elif method is None:
            m_se = sm.OLS(y_all, X_all).fit()
        else:
            m_se = sm.OLS(y_all, X_all).fit(cov_type=method)

        coef = m_se.params['fcc_reportable']
        se = m_se.bse['fcc_reportable']
        p = m_se.pvalues['fcc_reportable']

        print(f"  {method_name:20s}: coef={coef:8.4f}%, SE={se:.4f}, p={p:.4f}")
    except Exception as e:
        print(f"  {method_name:20s}: [failed]")

# ============================================================================
# 5. FIRM-SIZE QUARTILES - TIMING EFFECT
# ============================================================================
print("\n" + "=" * 90)
print("5. FIRM-SIZE QUARTILES - TIMING EFFECT (H1: immediate_disclosure by size)")
print("=" * 90)

print("\nTiming effect across firm-size quartiles:")
for q in ['Q1', 'Q2', 'Q3', 'Q4']:
    df_q = df_reg[df_reg['size_quartile'] == q].copy()
    if len(df_q) > 20:
        try:
            X_q = sm.add_constant(df_q[controls].astype(float))
            y_q = df_q['car_30d']
            m_q = sm.OLS(y_q, X_q).fit(cov_type='HC3')

            coef = m_q.params['immediate_disclosure']
            se = m_q.bse['immediate_disclosure']
            p = m_q.pvalues['immediate_disclosure']

            q_label = 'Q1 (Small)' if q == 'Q1' else ('Q4 (Large)' if q == 'Q4' else q)
            print(f"  {q_label:12s} (N={len(df_q):3d}): coef={coef:8.4f}%, SE={se:.4f}, p={p:.4f}")
        except:
            print(f"  {q:12s} (N={len(df_q):3d}): [failed]")

print("\n" + "=" * 90)
