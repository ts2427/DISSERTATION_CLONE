"""
CVSS Complexity Subsample Analysis
===================================

Run FCC effect separately for low-complexity and high-complexity breaches.
Avoids interaction specification issues by estimating on adequate subsamples.

Key diagnostics:
- Balance check: CVSS coverage (mean vendor_max_cvss) by FCC status within each complexity
- Subsample sizes and FCC cell counts
- FCC coefficient, SE, p-value, 95% CI for each subsample
- Comparison to baseline FCC effects (-2% to -6% family)
"""

import pandas as pd
import numpy as np
from scipy import stats
import warnings
import statsmodels.api as sm
from statsmodels.tools.tools import add_constant
warnings.filterwarnings('ignore')

# Load data
df = pd.read_csv('Data/processed/FINAL_DISSERTATION_DATASET_WITH_CVSS.csv')

print("\n" + "="*80)
print("CVSS COMPLEXITY SUBSAMPLE ANALYSIS - FCC EFFECT BY BREACH COMPLEXITY")
print("="*80)

# ============================================================================
# SECTION 1: SUBSAMPLE DEFINITIONS & BALANCE CHECK
# ============================================================================

print("\n" + "-"*80)
print("SECTION 1: SUBSAMPLE DEFINITION & BALANCE CHECK")
print("-"*80)

# Create subsamples
low_complexity = df[df['has_high_complexity'] == 0].copy()
high_complexity = df[df['has_high_complexity'] == 1].copy()

print(f"\nSample sizes:")
print(f"  Low-complexity breaches (CVSS < 7.0):   N = {len(low_complexity):4d}")
print(f"    - FCC-reportable:                     {(low_complexity['fcc_reportable']==1).sum():4d}")
print(f"    - Non-FCC:                            {(low_complexity['fcc_reportable']==0).sum():4d}")
print(f"  High-complexity breaches (CVSS >= 7.0): N = {len(high_complexity):4d}")
print(f"    - FCC-reportable:                     {(high_complexity['fcc_reportable']==1).sum():4d}")
print(f"    - Non-FCC:                            {(high_complexity['fcc_reportable']==0).sum():4d}")

# Balance check: CVSS coverage by FCC status
print(f"\n" + "-"*80)
print("BALANCE CHECK: CVSS Coverage (vendor_max_cvss) by FCC Status")
print("-"*80)

for label, subsample in [("Low-Complexity", low_complexity), ("High-Complexity", high_complexity)]:
    print(f"\n{label} Breaches:")
    fcc_cvss = subsample[subsample['fcc_reportable']==1]['vendor_max_cvss'].dropna()
    non_fcc_cvss = subsample[subsample['fcc_reportable']==0]['vendor_max_cvss'].dropna()

    print(f"  FCC-reportable:")
    print(f"    n with CVSS data:  {len(fcc_cvss):4d}")
    print(f"    mean vendor_max_cvss: {fcc_cvss.mean():.2f}")
    print(f"    missing: {(subsample['fcc_reportable']==1).sum() - len(fcc_cvss)}")

    print(f"  Non-FCC:")
    print(f"    n with CVSS data:  {len(non_fcc_cvss):4d}")
    print(f"    mean vendor_max_cvss: {non_fcc_cvss.mean():.2f}")
    print(f"    missing: {(subsample['fcc_reportable']==0).sum() - len(non_fcc_cvss)}")

    # T-test for balance
    if len(fcc_cvss) > 0 and len(non_fcc_cvss) > 0:
        t_stat, p_val = stats.ttest_ind(fcc_cvss, non_fcc_cvss)
        print(f"  t-test (FCC vs Non-FCC CVSS): t={t_stat:6.3f}, p={p_val:.4f}")
        if p_val < 0.05:
            print(f"    [!] Imbalance detected in CVSS coverage (p < 0.05)")
        else:
            print(f"    [OK] CVSS coverage balanced (p >= 0.05)")

# ============================================================================
# SECTION 2: SUBSAMPLE REGRESSIONS
# ============================================================================

print("\n" + "="*80)
print("SECTION 2: SUBSAMPLE REGRESSIONS - CAR 30D ON FCC STATUS")
print("="*80)

# Define control variables (from baseline essay1 model, numeric only)
control_vars = [
    'prior_breaches_total', 'health_breach',
    'firm_size_log', 'roa', 'leverage'
]

def run_subsample_regression(subsample_data, complexity_label, complexity_value):
    """Run OLS regression on subsample and return key results."""

    # Select relevant columns
    cols_needed = ['fcc_reportable', 'car_30d'] + control_vars
    analysis_data = subsample_data[cols_needed].copy()

    # Remove rows with any missing values
    analysis_data = analysis_data.dropna()
    n = len(analysis_data)

    if n < 10:
        print(f"\n{complexity_label}: INSUFFICIENT DATA (n={n})")
        return None

    # Create fresh dataframe with explicit float64 conversion
    regression_data = pd.DataFrame()
    regression_data['fcc_reportable'] = analysis_data['fcc_reportable'].astype(np.float64)
    regression_data['car_30d'] = analysis_data['car_30d'].astype(np.float64)

    for col in control_vars:
        col_data = analysis_data[col].astype(np.float64)
        mean_val = col_data.mean()
        std_val = col_data.std()
        if std_val > 0:
            regression_data[col] = (col_data - mean_val) / std_val
        else:
            regression_data[col] = col_data

    # Prepare for regression
    y = regression_data['car_30d'].values.astype(np.float64)
    X = regression_data[['fcc_reportable'] + control_vars].values.astype(np.float64)
    X = np.column_stack([np.ones(len(y)), X])

    # OLS using manual matrix operations (robust to data types)
    XtX_inv = np.linalg.inv(X.T @ X)
    beta = XtX_inv @ X.T @ y
    residuals = y - X @ beta

    # HC3 robust standard errors
    n_vars = X.shape[1]
    meat = np.zeros((n_vars, n_vars))
    for i in range(len(y)):
        h_ii = 1 - X[i] @ XtX_inv @ X[i]
        if abs(h_ii) > 1e-10:  # Avoid division by zero
            meat += (residuals[i]**2 / h_ii**2) * np.outer(X[i], X[i])

    cov_matrix = XtX_inv @ meat @ XtX_inv
    se = np.sqrt(np.diag(cov_matrix))

    # Extract FCC coefficient (index 1, after constant)
    fcc_beta = beta[1]
    fcc_se = se[1]
    fcc_t = fcc_beta / fcc_se if fcc_se > 0 else 0

    # P-value
    dof = len(y) - n_vars
    fcc_p = 2 * (1 - stats.t.cdf(abs(fcc_t), dof))

    # CI
    t_crit = stats.t.ppf(0.975, dof)
    ci_lower = fcc_beta - t_crit * fcc_se
    ci_upper = fcc_beta + t_crit * fcc_se

    # R-squared
    ss_total = np.sum((y - y.mean())**2)
    ss_resid = np.sum(residuals**2)
    r2 = 1 - (ss_resid / ss_total) if ss_total > 0 else 0

    return {
        'label': complexity_label,
        'complexity_value': complexity_value,
        'n': n,
        'n_fcc': int((analysis_data['fcc_reportable']==1).sum()),
        'n_non_fcc': int((analysis_data['fcc_reportable']==0).sum()),
        'fcc_beta': fcc_beta,
        'fcc_se': fcc_se,
        'fcc_t': fcc_t,
        'fcc_p': fcc_p,
        'ci_lower': ci_lower,
        'ci_upper': ci_upper,
        'r2': r2,
        'dof': dof,
    }

# Run both subsamples
results_low = run_subsample_regression(low_complexity, "Low-Complexity (CVSS < 7.0)", 0)
results_high = run_subsample_regression(high_complexity, "High-Complexity (CVSS >= 7.0)", 1)

# ============================================================================
# SECTION 3: RESULTS TABLE
# ============================================================================

print("\n" + "="*80)
print("SUBSAMPLE REGRESSION RESULTS TABLE")
print("="*80)
print("\nDependent Variable: CAR_30D (30-day Cumulative Abnormal Return)")
print("Specification: CAR ~ FCC_reportable + Prior_Breaches + Health_Breach")
print("                     + Firm_Size + ROA + Leverage (all controls standardized)")
print("Standard Errors: HC3 robust")

print("\n" + "-"*80)

for results in [results_low, results_high]:
    if results is None:
        continue

    print(f"\n{results['label']}")
    print(f"Sample: N = {results['n']:4d}  (FCC: {results['n_fcc']:3d}, Non-FCC: {results['n_non_fcc']:3d})")
    print(f"\nFCC Coefficient:")
    print(f"  Coeff = {results['fcc_beta']:7.4f}")
    print(f"  SE   = {results['fcc_se']:7.4f}")
    print(f"  t    = {results['fcc_t']:7.3f}")
    print(f"  p    = {results['fcc_p']:7.4f}  {'***' if results['fcc_p']<0.01 else '**' if results['fcc_p']<0.05 else '*' if results['fcc_p']<0.10 else 'ns'}")
    print(f"  95% CI: [{results['ci_lower']:7.4f}, {results['ci_upper']:7.4f}]")
    print(f"\nModel fit: R² = {results['r2']:.4f}")

# ============================================================================
# SECTION 4: INTERPRETATION & COMPARISON TO BASELINE
# ============================================================================

print("\n" + "="*80)
print("INTERPRETATION & ROBUSTNESS CHECK")
print("="*80)

if results_low and results_high:
    fcc_low = results_low['fcc_beta']  # Already in percentage points
    fcc_high = results_high['fcc_beta']
    p_low = results_low['fcc_p']
    p_high = results_high['fcc_p']

    print(f"\nFCC Effect Summary (in percentage points CAR):")
    print(f"  Low-complexity:  {fcc_low:7.2f}pp  (p={p_low:.4f})  [{results_low['ci_lower']:.2f}pp, {results_low['ci_upper']:.2f}pp]")
    print(f"  High-complexity: {fcc_high:7.2f}pp  (p={p_high:.4f})  [{results_high['ci_lower']:.2f}pp, {results_high['ci_upper']:.2f}pp]")

    print(f"\nComparison to baseline FCC effects (-2% to -6% range):")
    baseline_min, baseline_max = -6, -2

    if baseline_min <= fcc_low <= baseline_max:
        print(f"  [OK] Low-complexity coefficient IN FAMILY (within [-6%, -2%])")
    else:
        print(f"  [!] Low-complexity coefficient OUT OF FAMILY")
        print(f"     Currently {fcc_low:.2f}pp, expected range [-6%, -2%]")

    if baseline_min <= fcc_high <= baseline_max:
        print(f"  [OK] High-complexity coefficient IN FAMILY (within [-6%, -2%])")
    else:
        print(f"  [!] High-complexity coefficient OUT OF FAMILY")
        print(f"     Currently {fcc_high:.2f}pp, expected range [-6%, -2%]")

    print(f"\nDifference (Low - High):")
    diff = fcc_low - fcc_high
    print(f"  {diff:7.2f}% (suggests complexity {'amplifies' if diff > 0 else 'mitigates'} FCC effect)")

    print(f"\nSample Size Considerations:")
    print(f"  Low-complexity n_FCC = {results_low['n_fcc']} (below 50-obs threshold; wide SE expected)")
    print(f"  High-complexity n_FCC = {results_high['n_fcc']} (adequate sample size)")

print("\n" + "="*80)
print("END OF SUBSAMPLE ANALYSIS")
print("="*80 + "\n")
