"""
H1 TIMING ROBUSTNESS ON 648-OBSERVATION REGRESSION SAMPLE
=========================================================

Focuses on immediate_disclosure coefficient across:
1. Five timing thresholds (days to disclosure)
2. Three event windows
3. Eight sample restrictions
4. Six SE methods
5. Four firm-size quartiles (already have)
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
print("H1 TIMING ROBUSTNESS SUMMARY (N={})".format(n_reg))
print("=" * 90)

# Canonical specification for reference
X_canon = sm.add_constant(df_reg[controls].astype(float))
y_canon = df_reg['car_30d']
m_canon = sm.OLS(y_canon, X_canon).fit(cov_type='HC3')

print("\nCANONICAL SPECIFICATION (H1 - immediate_disclosure):")
print(f"  Coefficient: {m_canon.params['immediate_disclosure']:8.4f}%")
print(f"  SE (HC3):    {m_canon.bse['immediate_disclosure']:8.4f}")
print(f"  P-value:     {m_canon.pvalues['immediate_disclosure']:8.4f}")

# ============================================================================
# 1. FIVE TIMING THRESHOLDS
# ============================================================================
print("\n" + "=" * 90)
print("1. FIVE TIMING THRESHOLDS (H1: immediate_disclosure)")
print("=" * 90)
print("\nNote: Using immediate_disclosure binary. Exact thresholds require disclosure_date.")
print("\nTiming threshold results:")
print(f"  Days <=7 (canonical): coef={m_canon.params['immediate_disclosure']:8.4f}%, SE={m_canon.bse['immediate_disclosure']:.4f}, p={m_canon.pvalues['immediate_disclosure']:.4f}")
print("\nOther thresholds would require disclosure_date variable for precise calculation.")
print("(Using canonical <=7 days as primary threshold)")

# ============================================================================
# 2. THREE EVENT WINDOWS
# ============================================================================
print("\n" + "=" * 90)
print("2. THREE EVENT WINDOWS (H1: immediate_disclosure)")
print("=" * 90)

car_cols = ['car_5d', 'car_10d', 'car_30d']
print("\nEvent window results:")
for car_col in car_cols:
    if car_col in df_reg.columns:
        df_w = df_reg[df_reg[car_col].notna()].copy()
        if len(df_w) > 100:
            X_w = sm.add_constant(df_w[controls].astype(float))
            y_w = df_w[car_col]
            m_w = sm.OLS(y_w, X_w).fit(cov_type='HC3')

            window_name = car_col.replace('car_', '')
            coef = m_w.params['immediate_disclosure']
            se = m_w.bse['immediate_disclosure']
            p = m_w.pvalues['immediate_disclosure']

            print(f"  CAR {window_name:3s}: coef={coef:8.4f}%, SE={se:.4f}, p={p:.4f}")

# ============================================================================
# 3. EIGHT SAMPLE RESTRICTIONS
# ============================================================================
print("\n" + "=" * 90)
print("3. EIGHT SAMPLE RESTRICTIONS (H1: immediate_disclosure)")
print("=" * 90)

# Define restrictions
df_reg['size_quartile'] = pd.qcut(df_reg['firm_size_log'], q=4, labels=['Q1', 'Q2', 'Q3', 'Q4'], duplicates='drop')
df_reg['outlier'] = np.abs(df_reg['car_30d'] - df_reg['car_30d'].mean()) > 3 * df_reg['car_30d'].std()

restrictions = [
    ('Full sample', df_reg),
    ('Exclude largest decile', df_reg[df_reg['firm_size_log'] <= df_reg['firm_size_log'].quantile(0.90)]),
    ('Exclude smallest decile', df_reg[df_reg['firm_size_log'] >= df_reg['firm_size_log'].quantile(0.10)]),
    ('Exclude outliers (3 SD)', df_reg[~df_reg['outlier']]),
    ('FCC firms only', df_reg[df_reg['fcc_reportable'] == True]),
    ('Non-FCC firms only', df_reg[df_reg['fcc_reportable'] == False]),
    ('Non-health breaches', df_reg[df_reg['health_breach'] == False]),
    ('Prior breach history', df_reg[df_reg['prior_breaches_total'] > 0]),
]

print("\nSample restriction results:")
for name, df_s in restrictions:
    if len(df_s) > 20:
        try:
            X_s = sm.add_constant(df_s[controls].astype(float))
            y_s = df_s['car_30d']
            m_s = sm.OLS(y_s, X_s).fit(cov_type='HC3')

            coef = m_s.params['immediate_disclosure']
            se = m_s.bse['immediate_disclosure']
            p = m_s.pvalues['immediate_disclosure']

            print(f"  {name:30s} (N={len(df_s):3d}): coef={coef:8.4f}%, SE={se:.4f}, p={p:.4f}")
        except:
            print(f"  {name:30s} (N={len(df_s):3d}): [failed]")

# ============================================================================
# 4. SIX STANDARD ERROR METHODS
# ============================================================================
print("\n" + "=" * 90)
print("4. SIX STANDARD ERROR METHODS (H1: immediate_disclosure)")
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

        coef = m_se.params['immediate_disclosure']
        se = m_se.bse['immediate_disclosure']
        p = m_se.pvalues['immediate_disclosure']

        print(f"  {method_name:20s}: coef={coef:8.4f}%, SE={se:.4f}, p={p:.4f}")
    except Exception as e:
        print(f"  {method_name:20s}: [failed - {str(e)[:30]}]")

# ============================================================================
# 5. FIRM-SIZE QUARTILES
# ============================================================================
print("\n" + "=" * 90)
print("5. FIRM-SIZE QUARTILES (H1: immediate_disclosure by size)")
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
