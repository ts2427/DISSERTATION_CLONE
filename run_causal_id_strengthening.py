"""
ESSAY 3: CAUSAL IDENTIFICATION STRENGTHENING ANALYSES
Run: Placebo tests + Dose-response heterogeneity
Date: June 30, 2026

NOTE: Uses scipy.stats for logistic regressions (statsmodels unavailable)
"""

import pandas as pd
import numpy as np
from scipy.stats import norm
import warnings
warnings.filterwarnings('ignore')

# Load data
df = pd.read_csv('Data/processed/FINAL_DISSERTATION_DATASET_DEDUPLICATED_ENRICHED.csv')

print("=" * 100)
print("CAUSAL IDENTIFICATION STRENGTHENING: PLACEBO TESTS & DOSE-RESPONSE")
print("=" * 100)

# Newton-Raphson logit regression (manual, no dependencies)
def logit_regression(X, y, max_iter=100, tol=1e-6):
    """Logit regression using Newton-Raphson"""

    # Ensure float type
    X = np.asarray(X, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)

    n, k = X.shape
    X_with_const = np.column_stack([np.ones(n), X])

    # Initialize coefficients
    beta = np.zeros(k + 1, dtype=np.float64)

    # Newton-Raphson iterations
    for iteration in range(max_iter):
        # Linear predictor
        eta = np.asarray(X_with_const @ beta, dtype=np.float64)

        # Predicted probabilities (with clipping for numerical stability)
        eta_clipped = np.clip(eta, -500, 500)
        p = 1.0 / (1.0 + np.exp(-eta_clipped))

        # Gradient
        residuals = y - p
        gradient = X_with_const.T @ residuals

        # Hessian (diagonal of weights matrix)
        w = p * (1 - p)
        w = np.maximum(w, 1e-8)  # Avoid singular matrix

        # Hessian matrix
        H = X_with_const.T @ (X_with_const * w[:, np.newaxis])

        # Update step
        try:
            delta = np.linalg.solve(H, gradient)
            beta_new = beta + delta

            # Check convergence
            if np.max(np.abs(delta)) < tol:
                beta = beta_new
                break
            beta = beta_new
        except np.linalg.LinAlgError:
            break

    # Final predictions for SE calculation
    eta = np.asarray(X_with_const @ beta, dtype=np.float64)
    eta_clipped = np.clip(eta, -500, 500)
    p = 1.0 / (1.0 + np.exp(-eta_clipped))

    # Variance-covariance matrix
    w = p * (1 - p)
    w = np.maximum(w, 1e-8)
    H = X_with_const.T @ (X_with_const * w[:, np.newaxis])

    try:
        vcov = np.linalg.inv(H)
        se = np.sqrt(np.diag(vcov))
    except np.linalg.LinAlgError:
        se = np.full(len(beta), np.nan)

    z_stats = beta / (se + 1e-8)
    p_vals = 2 * (1 - norm.cdf(np.abs(z_stats)))

    return {
        'beta': beta,
        'se': se,
        'z_stat': z_stats,
        'p_val': p_vals,
        'coef_names': ['Intercept', 'fcc_reportable', 'firm_size_log', 'leverage', 'roa'][:len(beta)]
    }

# ============================================================================
# PART 1: PLACEBO TESTS
# ============================================================================
print("\n" + "=" * 100)
print("PART 1: PLACEBO TESTS (outcomes that should NOT respond to fcc_reportable)")
print("=" * 100)

# Prepare sample
sample = df[['fcc_reportable', 'firm_size_log', 'leverage', 'roa',
             'executive_change_30d', 'num_changes_180d',
             'weak_governance', 'governance_weakness_score']].dropna()

print(f"\nSample size: {len(sample)}")
print(f"FCC firms: {(sample['fcc_reportable'] == 1).sum()}")
print(f"Non-FCC firms: {(sample['fcc_reportable'] == 0).sum()}")

# Test 1: Multiple Executive Changes (should be null if effect is specific to CEO)
print("\n" + "-" * 100)
print("PLACEBO TEST 1: Multiple Executive Changes (num_changes_180d > 0)")
print("Hypothesis: fcc_reportable should NOT predict multiple changes if effect is CEO-specific")

# Convert count to binary (any change vs none)
sample['any_executive_change'] = (sample['num_changes_180d'] > 0).astype(int)
n_with_changes = sample['any_executive_change'].sum()
print(f"Any executive changes (180d): {n_with_changes} ({100*n_with_changes/len(sample):.1f}%)")

X_placebo1 = sample[['fcc_reportable', 'firm_size_log', 'leverage', 'roa']].values
y_placebo1 = sample['any_executive_change'].values

result1 = logit_regression(X_placebo1, y_placebo1)
print(f"\nfcc_reportable coef: {result1['beta'][1]:.4f}")
print(f"fcc_reportable SE: {result1['se'][1]:.4f}")
print(f"fcc_reportable z-stat: {result1['z_stat'][1]:.4f}")
print(f"fcc_reportable p-value: {result1['p_val'][1]:.4f}")
if result1['p_val'][1] < 0.05:
    print("*** SIGNIFICANT - suggests fcc effect may be general governance response, not CEO-specific")
else:
    print("*** NULL - consistent with CEO-specific effect hypothesis")

# Test 2: Weak Governance Indicator (should be null if effect is CEO turnover response)
print("\n" + "-" * 100)
print("PLACEBO TEST 2: Weak Governance Indicator")
print("Hypothesis: fcc_reportable should NOT predict weak governance if effect operates through CEO turnover")

n_weak_gov = sample['weak_governance'].sum()
print(f"Weak governance: {n_weak_gov} ({100*n_weak_gov/len(sample):.1f}%)")

X_placebo2 = sample[['fcc_reportable', 'firm_size_log', 'leverage', 'roa']].values
y_placebo2 = sample['weak_governance'].values

result2 = logit_regression(X_placebo2, y_placebo2)
print(f"\nfcc_reportable coef: {result2['beta'][1]:.4f}")
print(f"fcc_reportable SE: {result2['se'][1]:.4f}")
print(f"fcc_reportable z-stat: {result2['z_stat'][1]:.4f}")
print(f"fcc_reportable p-value: {result2['p_val'][1]:.4f}")
if result2['p_val'][1] < 0.05:
    print("*** SIGNIFICANT - suggests regulatory effect on governance structure")
else:
    print("*** NULL - consistent with event-specific CEO turnover hypothesis")

# Test 3: Governance Weakness Score (continuous proxy)
print("\n" + "-" * 100)
print("PLACEBO TEST 3: Governance Weakness Score (continuous)")
print("Hypothesis: fcc_reportable should NOT predict baseline governance weakness")

# Governance weakness is continuous, use linear regression as proxy
sample_gov_score = sample.dropna(subset=['governance_weakness_score'])
X_placebo3 = np.asarray(sample_gov_score[['fcc_reportable', 'firm_size_log', 'leverage', 'roa']].values, dtype=np.float64)
y_placebo3 = np.asarray(sample_gov_score['governance_weakness_score'].values, dtype=np.float64)

# Simple linear regression
X_with_const = np.column_stack([np.ones(len(X_placebo3)), X_placebo3])
try:
    beta_ols = np.linalg.lstsq(X_with_const, y_placebo3, rcond=None)[0]
    residuals = y_placebo3 - (X_with_const @ beta_ols)
    n = len(y_placebo3)
    k = X_with_const.shape[1]
    mse = np.sum(residuals**2) / (n - k)
    vcov_ols = mse * np.linalg.inv(X_with_const.T @ X_with_const)
    se_ols = np.sqrt(np.diag(vcov_ols))
    t_stat_ols = beta_ols / se_ols
    p_val_ols = 2 * (1 - norm.cdf(np.abs(t_stat_ols)))

    print(f"\nfcc_reportable coef: {beta_ols[1]:.4f}")
    print(f"fcc_reportable SE: {se_ols[1]:.4f}")
    print(f"fcc_reportable t-stat: {t_stat_ols[1]:.4f}")
    print(f"fcc_reportable p-value: {p_val_ols[1]:.4f}")
    if p_val_ols[1] < 0.05:
        print("*** SIGNIFICANT - suggests structural governance differences by FCC status")
    else:
        print("*** NULL - FCC firms not structurally weaker on baseline governance")
except Exception as e:
    print(f"Error in continuous regression: {e}")
    beta_ols = [np.nan, np.nan]
    p_val_ols = [np.nan, np.nan]

# ============================================================================
# PART 2: DOSE-RESPONSE ANALYSIS
# ============================================================================
print("\n" + "=" * 100)
print("PART 2: DOSE-RESPONSE ANALYSIS (CEO Turnover 30d)")
print("Hypothesis: FCC effect should be stronger for more severe breaches")
print("=" * 100)

# Prepare sample with severity indicators
sample_dose = df[['fcc_reportable', 'executive_change_30d', 'firm_size_log', 'leverage', 'roa',
                   'financial_breach', 'health_breach', 'high_severity_breach', 'ransomware',
                   'records_affected_numeric', 'combined_severity_score']].dropna()

print(f"\nDose-response sample size: {len(sample_dose)}")
print(f"CEO Turnover (30d): {sample_dose['executive_change_30d'].sum()} ({100*sample_dose['executive_change_30d'].mean():.1f}%)")

# Dose Test 1: Financial Breach Interaction
print("\n" + "-" * 100)
print("DOSE TEST 1: FCC × Financial Data Breach Interaction")

sample_dose['fcc_x_financial'] = sample_dose['fcc_reportable'] * sample_dose['financial_breach']

X_dose1 = sample_dose[['fcc_reportable', 'financial_breach', 'fcc_x_financial', 'firm_size_log', 'leverage', 'roa']].values
y_dose1 = sample_dose['executive_change_30d'].values

result_dose1 = logit_regression(X_dose1, y_dose1)

print(f"\nfcc_reportable main effect: {result_dose1['beta'][1]:.4f} (p={result_dose1['p_val'][1]:.4f})")
print(f"financial_breach main effect: {result_dose1['beta'][2]:.4f} (p={result_dose1['p_val'][2]:.4f})")
print(f"FCC × Financial INTERACTION: {result_dose1['beta'][3]:.4f} (p={result_dose1['p_val'][3]:.4f})")
print(f"Interpretation: FCC effect {'+' if result_dose1['beta'][3] > 0 else ''}{result_dose1['beta'][3]:.4f} stronger for financial breaches")
if result_dose1['p_val'][3] < 0.10:
    print("*** EVIDENCE of dose-response (at 10% level)")
else:
    print("*** NULL at 10% level (FCC effect uniform across severity)")

# Dose Test 2: Health Breach Interaction
print("\n" + "-" * 100)
print("DOSE TEST 2: FCC × Health Data Breach Interaction")

sample_dose['fcc_x_health'] = sample_dose['fcc_reportable'] * sample_dose['health_breach']

X_dose2 = sample_dose[['fcc_reportable', 'health_breach', 'fcc_x_health', 'firm_size_log', 'leverage', 'roa']].values
y_dose2 = sample_dose['executive_change_30d'].values

result_dose2 = logit_regression(X_dose2, y_dose2)

print(f"\nfcc_reportable main effect: {result_dose2['beta'][1]:.4f} (p={result_dose2['p_val'][1]:.4f})")
print(f"health_breach main effect: {result_dose2['beta'][2]:.4f} (p={result_dose2['p_val'][2]:.4f})")
print(f"FCC × Health INTERACTION: {result_dose2['beta'][3]:.4f} (p={result_dose2['p_val'][3]:.4f})")
print(f"Interpretation: FCC effect {'+' if result_dose2['beta'][3] > 0 else ''}{result_dose2['beta'][3]:.4f} stronger for health breaches")
if result_dose2['p_val'][3] < 0.10:
    print("*** EVIDENCE of dose-response (at 10% level)")
else:
    print("*** NULL at 10% level")

# Dose Test 3: High Severity Interaction
print("\n" + "-" * 100)
print("DOSE TEST 3: FCC × High Severity Breach Interaction")

sample_dose['fcc_x_highsev'] = sample_dose['fcc_reportable'] * sample_dose['high_severity_breach']

X_dose3 = sample_dose[['fcc_reportable', 'high_severity_breach', 'fcc_x_highsev', 'firm_size_log', 'leverage', 'roa']].values
y_dose3 = sample_dose['executive_change_30d'].values

result_dose3 = logit_regression(X_dose3, y_dose3)

print(f"\nfcc_reportable main effect: {result_dose3['beta'][1]:.4f} (p={result_dose3['p_val'][1]:.4f})")
print(f"high_severity_breach main effect: {result_dose3['beta'][2]:.4f} (p={result_dose3['p_val'][2]:.4f})")
print(f"FCC × High Severity INTERACTION: {result_dose3['beta'][3]:.4f} (p={result_dose3['p_val'][3]:.4f})")
print(f"Interpretation: FCC effect {'+' if result_dose3['beta'][3] > 0 else ''}{result_dose3['beta'][3]:.4f} stronger for high-severity breaches")
if result_dose3['p_val'][3] < 0.10:
    print("*** EVIDENCE of dose-response (at 10% level)")
else:
    print("*** NULL at 10% level")

# Dose Test 4: Ransomware Interaction
print("\n" + "-" * 100)
print("DOSE TEST 4: FCC × Ransomware Interaction")

sample_dose['fcc_x_ransomware'] = sample_dose['fcc_reportable'] * sample_dose['ransomware']

X_dose4 = sample_dose[['fcc_reportable', 'ransomware', 'fcc_x_ransomware', 'firm_size_log', 'leverage', 'roa']].values
y_dose4 = sample_dose['executive_change_30d'].values

result_dose4 = logit_regression(X_dose4, y_dose4)

print(f"\nfcc_reportable main effect: {result_dose4['beta'][1]:.4f} (p={result_dose4['p_val'][1]:.4f})")
print(f"ransomware main effect: {result_dose4['beta'][2]:.4f} (p={result_dose4['p_val'][2]:.4f})")
print(f"FCC × Ransomware INTERACTION: {result_dose4['beta'][3]:.4f} (p={result_dose4['p_val'][3]:.4f})")
print(f"Interpretation: FCC effect {'+' if result_dose4['beta'][3] > 0 else ''}{result_dose4['beta'][3]:.4f} stronger for ransomware breaches")
if result_dose4['p_val'][3] < 0.10:
    print("*** EVIDENCE of dose-response (at 10% level)")
else:
    print("*** NULL at 10% level")

print("\n" + "=" * 100)
print("SUMMARY")
print("=" * 100)
print("\nPLACEBO TESTS (should be NULL for causal specificity):")
print(f"  1. Multiple exec changes:     fcc coef={result1['beta'][1]:.4f}, p={result1['p_val'][1]:.4f} {'[SIGNIFICANT]' if result1['p_val'][1] < 0.05 else '[NULL]'}")
print(f"  2. Weak governance:           fcc coef={result2['beta'][1]:.4f}, p={result2['p_val'][1]:.4f} {'[SIGNIFICANT]' if result2['p_val'][1] < 0.05 else '[NULL]'}")
print(f"  3. Governance weakness score: fcc coef={beta_ols[1]:.4f}, p={p_val_ols[1]:.4f} {'[SIGNIFICANT]' if p_val_ols[1] < 0.05 else '[NULL]'}")

print("\nDOSE-RESPONSE TESTS (should show positive interactions for causal strength):")
print(f"  1. Financial breach:     interaction={result_dose1['beta'][3]:.4f}, p={result_dose1['p_val'][3]:.4f} {'[*]' if result_dose1['p_val'][3] < 0.10 else ''}")
print(f"  2. Health breach:        interaction={result_dose2['beta'][3]:.4f}, p={result_dose2['p_val'][3]:.4f} {'[*]' if result_dose2['p_val'][3] < 0.10 else ''}")
print(f"  3. High severity:        interaction={result_dose3['beta'][3]:.4f}, p={result_dose3['p_val'][3]:.4f} {'[*]' if result_dose3['p_val'][3] < 0.10 else ''}")
print(f"  4. Ransomware:           interaction={result_dose4['beta'][3]:.4f}, p={result_dose4['p_val'][3]:.4f} {'[*]' if result_dose4['p_val'][3] < 0.10 else ''}")

print("\n" + "=" * 100)
print("INTERPRETATION:")
print("Placebo tests validate causal identification if NULL.")
print("Dose-response tests strengthen identification if positive & significant.")
print("=" * 100)
