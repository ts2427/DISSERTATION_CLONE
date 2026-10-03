"""
H1 TIMING ROBUSTNESS - COMPLETE VERSION ON 648-OBSERVATION SAMPLE
==================================================================

Uses existing data fields:
1. disclosure_delay_days for timing thresholds
2. CAR 5d, 10d, 30d, 60d, 90d for event windows
3. cik for firm-level clustering
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
print("H1 TIMING ROBUSTNESS - COMPLETE (N={})".format(n_reg))
print("=" * 90)

# ============================================================================
# 1. FIVE TIMING THRESHOLDS (using disclosure_delay_days)
# ============================================================================
print("\n" + "=" * 90)
print("1. FIVE TIMING THRESHOLDS (H1: immediate_disclosure)")
print("=" * 90)

# Check if disclosure_delay_days exists
if 'disclosure_delay_days' in df_reg.columns:
    thresholds = [3, 5, 7, 14, 30]
    print("\nTiming threshold results:")
    for threshold in thresholds:
        # Create binary: disclosed within threshold days
        threshold_var = (df_reg['disclosure_delay_days'] <= threshold).astype(int)

        X_thresh = sm.add_constant(df_reg[controls].copy().astype(float))
        X_thresh['timing_' + str(threshold)] = threshold_var
        y_thresh = df_reg['car_30d']

        m_thresh = sm.OLS(y_thresh, X_thresh).fit(cov_type='HC3')
        coef = m_thresh.params['timing_' + str(threshold)]
        se = m_thresh.bse['timing_' + str(threshold)]
        p = m_thresh.pvalues['timing_' + str(threshold)]
        n_within = threshold_var.sum()

        print(f"  <=  {threshold:2d} days (N={n_within:3d}): coef={coef:8.4f}%, SE={se:.4f}, p={p:.4f}")
else:
    print("\nwarning: disclosure_delay_days not found")

# ============================================================================
# 2. FIVE EVENT WINDOWS (5d, 10d, 30d, 60d, 90d)
# ============================================================================
print("\n" + "=" * 90)
print("2. FIVE EVENT WINDOWS (H1: immediate_disclosure)")
print("=" * 90)

windows = ['car_5d', 'car_10d', 'car_30d', 'car_60d', 'car_90d']
print("\nEvent window results:")
for car_col in windows:
    if car_col in df_reg.columns:
        df_w = df_reg[df_reg[car_col].notna()].copy()
        if len(df_w) > 50:
            X_w = sm.add_constant(df_w[controls].astype(float))
            y_w = df_w[car_col]
            m_w = sm.OLS(y_w, X_w).fit(cov_type='HC3')

            window_name = car_col.replace('car_', '')
            coef = m_w.params['immediate_disclosure']
            se = m_w.bse['immediate_disclosure']
            p = m_w.pvalues['immediate_disclosure']

            print(f"  CAR {window_name:3s} (N={len(df_w):3d}): coef={coef:8.4f}%, SE={se:.4f}, p={p:.4f}")
    else:
        window_name = car_col.replace('car_', '')
        print(f"  CAR {window_name:3s}: [not in dataset]")

# ============================================================================
# 3. SAMPLE RESTRICTIONS - GET EXACT FCC/NON-FCC RESULTS
# ============================================================================
print("\n" + "=" * 90)
print("3. FCC/NON-FCC SUBSAMPLE RESULTS (for interaction paragraph reconciliation)")
print("=" * 90)

X_all = sm.add_constant(df_reg[controls].astype(float))
y_all = df_reg['car_30d']

print("\nFCC subsample:")
df_fcc = df_reg[df_reg['fcc_reportable'] == True].copy()
X_fcc = sm.add_constant(df_fcc[controls].astype(float))
y_fcc = df_fcc['car_30d']
m_fcc = sm.OLS(y_fcc, X_fcc).fit(cov_type='HC3')
coef_fcc = m_fcc.params['immediate_disclosure']
p_fcc = m_fcc.pvalues['immediate_disclosure']
print(f"  N={len(df_fcc)}, coef={coef_fcc:8.4f}%, p={p_fcc:.4f}")

print("\nNon-FCC subsample:")
df_non_fcc = df_reg[df_reg['fcc_reportable'] == False].copy()
X_non_fcc = sm.add_constant(df_non_fcc[controls].astype(float))
y_non_fcc = df_non_fcc['car_30d']
m_non_fcc = sm.OLS(y_non_fcc, X_non_fcc).fit(cov_type='HC3')
coef_non_fcc = m_non_fcc.params['immediate_disclosure']
p_non_fcc = m_non_fcc.pvalues['immediate_disclosure']
print(f"  N={len(df_non_fcc)}, coef={coef_non_fcc:8.4f}%, p={p_non_fcc:.4f}")

# ============================================================================
# 4. SIX STANDARD ERROR METHODS (with firm-clustered using cik)
# ============================================================================
print("\n" + "=" * 90)
print("4. SIX STANDARD ERROR METHODS (H1: immediate_disclosure)")
print("=" * 90)

se_methods = [
    ('OLS (unadjusted)', None),
    ('HC1 robust', 'HC1'),
    ('HC2 robust', 'HC2'),
    ('HC3 robust', 'HC3'),
    ('Firm-clustered (cik)', 'cik'),
    ('Date-clustered', 'date'),
]

print("\nStandard error robustness:")
for method_name, method in se_methods:
    try:
        if method == 'cik':
            m_se = sm.OLS(y_all, X_all).fit(cov_type='cluster', cov_kwds={'groups': df_reg['cik']})
        elif method == 'date':
            m_se = sm.OLS(y_all, X_all).fit(cov_type='cluster', cov_kwds={'groups': df_reg['breach_date']})
        elif method is None:
            m_se = sm.OLS(y_all, X_all).fit()
        else:
            m_se = sm.OLS(y_all, X_all).fit(cov_type=method)

        coef = m_se.params['immediate_disclosure']
        se = m_se.bse['immediate_disclosure']
        p = m_se.pvalues['immediate_disclosure']

        print(f"  {method_name:25s}: coef={coef:8.4f}%, SE={se:.4f}, p={p:.4f}")
    except Exception as e:
        print(f"  {method_name:25s}: [failed - {str(e)[:40]}]")

print("\n" + "=" * 90)
