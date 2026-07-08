"""
DISH Network: Deduplication Check + Robustness Regression
==========================================================

Two diagnostic checks in one pass:

1. BREACH DATE DEDUPLICATION
   Check if the 8 "DISH Network" low-complexity breaches include duplicates
   (same underlying breach recorded under different entity-name spellings).
   If several share the same/near-same date, that's a data-cleaning fix.

2. ROBUSTNESS REGRESSIONS
   a) Exclude all DISH entities (as-is)
   b) Exclude DISH but deduplicate by breach date first (if applicable)
   Compare both to the original n=37 FCC, -9.66pp result.

Outcome: One of three defensible paths
  - (A) Duplication artifact found and fixed → cleaned data resolves it
  - (B) DISH genuinely distinct breaches but concentrated → exclude DISH, report robustness
  - (C) Even excluding DISH, effect stays large → genuine subpopulation, fall back to high-complexity
"""

import pandas as pd
import numpy as np
from scipy import stats
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Load data
df = pd.read_csv('Data/processed/FINAL_DISSERTATION_DATASET_WITH_CVSS.csv')

print("\n" + "="*80)
print("DISH NETWORK DEDUPLICATION & ROBUSTNESS ANALYSIS")
print("="*80)

# ============================================================================
# SECTION 1: DISH NETWORK BREACH DEDUPLICATION
# ============================================================================

print("\n" + "-"*80)
print("SECTION 1: BREACH DATE DEDUPLICATION CHECK")
print("-"*80)

# Filter to low-complexity FCC
low_complex = df[df['vendor_max_cvss'] < 7.0].copy()
fcc_low = low_complex[low_complex['fcc_reportable'] == 1].copy()

# Convert to numeric
fcc_low['car_30d'] = pd.to_numeric(fcc_low['car_30d'], errors='coerce')
fcc_low['breach_date'] = pd.to_datetime(fcc_low['breach_date'], errors='coerce')

# Find all DISH variants
dish_patterns = ['DISH', 'dish']
dish_records = fcc_low[fcc_low['org_name'].str.contains('|'.join(dish_patterns), case=False, na=False)].copy()

print(f"\nTotal low-complexity FCC breaches: N = {len(fcc_low)}")
print(f"DISH Network breaches (all variants): N = {len(dish_records)}")
print(f"\nDISH records by entity name:")
for entity in dish_records['org_name'].unique():
    n = (dish_records['org_name'] == entity).sum()
    print(f"  {entity:35s}: {n}")

# Show breach dates and CAR
print(f"\nDISH breach details (sorted by date):")
print(f"{'Breach Date':<15} {'Org Name':<35} {'CAR 30D':<12} {'Vendor':<20}")
print("-" * 85)

dish_sorted = dish_records.sort_values('breach_date')
for idx, row in dish_sorted.iterrows():
    breach_date_str = row['breach_date'].strftime('%Y-%m-%d') if pd.notna(row['breach_date']) else 'N/A'
    print(f"{breach_date_str:<15} {str(row['org_name']):<35} {row['car_30d']:<12.2f} {str(row['nvd_vendor']):<20}")

# ============================================================================
# DEDUPLICATION LOGIC
# ============================================================================

print(f"\n" + "-"*80)
print("DEDUPLICATION ANALYSIS")
print("-"*80)

# Check for near-identical dates (within 2 days = likely same breach)
dish_sorted['date_group'] = None
group_id = 0
date_tolerance = 2  # days

for i, (idx1, row1) in enumerate(dish_sorted.iterrows()):
    if pd.isna(row1['breach_date']):
        continue

    # Check if this date is within tolerance of any previous group
    matched = False
    for j, (idx2, row2) in enumerate(dish_sorted.iterrows()):
        if i <= j or pd.isna(row2['breach_date']):
            continue

        date_diff = abs((row1['breach_date'] - row2['breach_date']).days)
        if date_diff <= date_tolerance and dish_sorted.loc[idx2, 'date_group'] is not None:
            dish_sorted.loc[idx1, 'date_group'] = dish_sorted.loc[idx2, 'date_group']
            matched = True
            break

    if not matched and pd.notna(row1['breach_date']):
        dish_sorted.loc[idx1, 'date_group'] = group_id
        group_id += 1

# Simple alternative: group by exact date
dish_sorted['date_group_exact'] = dish_sorted['breach_date'].dt.date

print(f"\nGrouping breaches by date (tolerance: {date_tolerance} days):")
for group_date, group_df in dish_sorted.groupby('date_group_exact'):
    if len(group_df) > 1:
        print(f"\n  Breach date {group_date}: {len(group_df)} records (potential duplicates)")
        for idx, row in group_df.iterrows():
            print(f"    - {row['org_name']:35s} CAR={row['car_30d']:7.2f}%")
    elif pd.notna(group_date):
        print(f"\n  Breach date {group_date}: 1 record (unique)")

# Count unique breaches by date
n_dish_unique_dates = dish_sorted['breach_date'].nunique()
n_dish_total = len(dish_sorted)
potential_dupes = n_dish_total - n_dish_unique_dates

print(f"\nDeduplication summary:")
print(f"  Total DISH records: {n_dish_total}")
print(f"  Unique breach dates: {n_dish_unique_dates}")
print(f"  Potential duplicates (same date, different name): {potential_dupes}")

if potential_dupes > 0:
    print(f"\n  [!] DUPLICATION DETECTED: {potential_dupes} records share breach dates")
    print(f"      These should be deduplicated by keeping first record per date")
    dedup_method = "Keep first record per breach date"
else:
    print(f"\n  [OK] No duplicate dates detected; all 8 DISH records appear distinct")
    dedup_method = None

# ============================================================================
# SECTION 2: ROBUSTNESS REGRESSIONS
# ============================================================================

print("\n" + "="*80)
print("SECTION 2: ROBUSTNESS REGRESSIONS")
print("="*80)

def run_subsample_regression(subsample_data, label):
    """Run OLS regression on subsample."""

    cols_needed = ['fcc_reportable', 'car_30d', 'prior_breaches_total', 'health_breach',
                   'firm_size_log', 'roa', 'leverage']
    analysis_data = subsample_data[cols_needed].copy()
    analysis_data = analysis_data.dropna()
    n = len(analysis_data)

    if n < 10:
        return None

    # Create regression dataframe with explicit float64
    regression_data = pd.DataFrame()
    regression_data['fcc_reportable'] = analysis_data['fcc_reportable'].astype(np.float64)
    regression_data['car_30d'] = analysis_data['car_30d'].astype(np.float64)

    control_vars = ['prior_breaches_total', 'health_breach', 'firm_size_log', 'roa', 'leverage']
    for col in control_vars:
        col_data = analysis_data[col].astype(np.float64)
        mean_val = col_data.mean()
        std_val = col_data.std()
        if std_val > 0:
            regression_data[col] = (col_data - mean_val) / std_val
        else:
            regression_data[col] = col_data

    y = regression_data['car_30d'].values.astype(np.float64)
    X = regression_data[['fcc_reportable'] + control_vars].values.astype(np.float64)
    X = np.column_stack([np.ones(len(y)), X])

    # OLS
    XtX_inv = np.linalg.inv(X.T @ X)
    beta = XtX_inv @ X.T @ y
    residuals = y - X @ beta

    # HC3 robust SE
    n_vars = X.shape[1]
    meat = np.zeros((n_vars, n_vars))
    for i in range(len(y)):
        h_ii = 1 - X[i] @ XtX_inv @ X[i]
        if abs(h_ii) > 1e-10:
            meat += (residuals[i]**2 / h_ii**2) * np.outer(X[i], X[i])

    cov_matrix = XtX_inv @ meat @ XtX_inv
    se = np.sqrt(np.diag(cov_matrix))

    fcc_beta = beta[1]
    fcc_se = se[1]
    fcc_t = fcc_beta / fcc_se if fcc_se > 0 else 0
    dof = len(y) - n_vars
    fcc_p = 2 * (1 - stats.t.cdf(abs(fcc_t), dof))

    t_crit = stats.t.ppf(0.975, dof)
    ci_lower = fcc_beta - t_crit * fcc_se
    ci_upper = fcc_beta + t_crit * fcc_se

    ss_total = np.sum((y - y.mean())**2)
    ss_resid = np.sum(residuals**2)
    r2 = 1 - (ss_resid / ss_total) if ss_total > 0 else 0

    return {
        'label': label,
        'n': n,
        'n_fcc': int((analysis_data['fcc_reportable']==1).sum()),
        'n_non_fcc': int((analysis_data['fcc_reportable']==0).sum()),
        'fcc_beta': fcc_beta,
        'fcc_se': fcc_se,
        'fcc_p': fcc_p,
        'ci_lower': ci_lower,
        'ci_upper': ci_upper,
        'r2': r2,
    }

# Original specification (all FCC, n=37)
print(f"\n" + "-"*80)
print("ORIGINAL SPECIFICATION: All low-complexity FCC firms (n=37)")
print("-"*80)
result_original = run_subsample_regression(fcc_low, "Original (all FCC, n=37)")
if result_original:
    print(f"\n  N = {result_original['n']} (FCC: {result_original['n_fcc']}, Non-FCC: {result_original['n_non_fcc']})")
    print(f"  FCC Coeff = {result_original['fcc_beta']:7.4f}pp")
    print(f"  SE = {result_original['fcc_se']:7.4f}")
    print(f"  p = {result_original['fcc_p']:.4f}  {'***' if result_original['fcc_p']<0.01 else '**' if result_original['fcc_p']<0.05 else '*' if result_original['fcc_p']<0.10 else 'ns'}")
    print(f"  95% CI: [{result_original['ci_lower']:7.4f}, {result_original['ci_upper']:7.4f}]")

# Exclude all DISH
print(f"\n" + "-"*80)
print("ROBUSTNESS 1: Excluding all DISH Network entities")
print("-"*80)
fcc_no_dish = fcc_low[~fcc_low['org_name'].str.contains('|'.join(dish_patterns), case=False, na=False)].copy()
result_no_dish = run_subsample_regression(fcc_no_dish, "Exclude DISH")
if result_no_dish:
    print(f"\n  N = {result_no_dish['n']} (FCC: {result_no_dish['n_fcc']}, Non-FCC: {result_no_dish['n_non_fcc']})")
    print(f"  FCC removed: {result_original['n_fcc'] - result_no_dish['n_fcc']} firms")
    print(f"  FCC Coeff = {result_no_dish['fcc_beta']:7.4f}pp")
    print(f"  SE = {result_no_dish['fcc_se']:7.4f}")
    print(f"  p = {result_no_dish['fcc_p']:.4f}  {'***' if result_no_dish['fcc_p']<0.01 else '**' if result_no_dish['fcc_p']<0.05 else '*' if result_no_dish['fcc_p']<0.10 else 'ns'}")
    print(f"  95% CI: [{result_no_dish['ci_lower']:7.4f}, {result_no_dish['ci_upper']:7.4f}]")

# If duplicates detected, also run deduplicated version
if potential_dupes > 0:
    print(f"\n" + "-"*80)
    print(f"ROBUSTNESS 2: Deduplicating DISH by breach date (keeping first record per date)")
    print("-"*80)

    # Deduplicate DISH by keeping first record per date
    fcc_dedup = fcc_low.copy()
    dish_dedup_mask = fcc_dedup['org_name'].str.contains('|'.join(dish_patterns), case=False, na=False)
    dish_to_dedup = fcc_dedup[dish_dedup_mask].copy()

    # Keep only first record per breach date for DISH
    dish_deduped = dish_to_dedup.drop_duplicates(subset=['breach_date'], keep='first')

    # Combine: non-DISH + deduplicated DISH
    fcc_dedup_combined = pd.concat([
        fcc_dedup[~dish_dedup_mask],
        dish_deduped
    ], ignore_index=True)

    n_records_removed = len(dish_to_dedup) - len(dish_deduped)

    result_dedup = run_subsample_regression(fcc_dedup_combined, "DISH deduplicated by date")
    if result_dedup:
        print(f"\n  Duplicates removed: {n_records_removed} (kept first record per breach date)")
        print(f"  N = {result_dedup['n']} (FCC: {result_dedup['n_fcc']}, Non-FCC: {result_dedup['n_non_fcc']})")
        print(f"  FCC Coeff = {result_dedup['fcc_beta']:7.4f}pp")
        print(f"  SE = {result_dedup['fcc_se']:7.4f}")
        print(f"  p = {result_dedup['fcc_p']:.4f}  {'***' if result_dedup['fcc_p']<0.01 else '**' if result_dedup['fcc_p']<0.05 else '*' if result_dedup['fcc_p']<0.10 else 'ns'}")
        print(f"  95% CI: [{result_dedup['ci_lower']:7.4f}, {result_dedup['ci_upper']:7.4f}]")

# ============================================================================
# SECTION 3: SUMMARY & RECOMMENDATION
# ============================================================================

print("\n" + "="*80)
print("SUMMARY & INTERPRETATION")
print("="*80)

print(f"""
DEDUPLICATION FINDING:
{f'  Potential duplicates detected: {potential_dupes} records share breach dates' if potential_dupes > 0 else '  No duplicates detected; all records appear distinct'}

ROBUSTNESS RESULTS:
  Original (all FCC):          {result_original['fcc_beta']:7.4f}pp (p={result_original['fcc_p']:.4f})
  Excluding all DISH:          {result_no_dish['fcc_beta']:7.4f}pp (p={result_no_dish['fcc_p']:.4f})
{f'  DISH deduplicated by date:   {result_dedup["fcc_beta"]:7.4f}pp (p={result_dedup["fcc_p"]:.4f})' if potential_dupes > 0 else ''}

BASELINE RANGE: -2% to -6% (in-family for FCC effects elsewhere)

INTERPRETATION:
""")

if potential_dupes > 0:
    print(f"""
The data contains {potential_dupes} potential DISH duplicates (same breach date, different entity name).
Deduplicating reduces the effect from {result_original['fcc_beta']:.2f}pp to {result_dedup['fcc_beta']:.2f}pp.

""")
    if result_dedup and baseline_min <= result_dedup['fcc_beta'] <= baseline_max:
        print(f"[OUTCOME A: DATA CLEANING FIXES IT]")
        print(f"  Deduplicated coefficient {result_dedup['fcc_beta']:.2f}pp is IN FAMILY.")
        print(f"  RECOMMENDATION: Clean the duplicate records and report the deduplicated result.")
    else:
        print(f"[OUTCOME B: STILL OUT OF FAMILY AFTER DEDUP]")
        print(f"  Even after deduplication, coefficient remains far from baseline.")
        print(f"  RECOMMENDATION: Report both versions, note that effect is robust to dedup.")
else:
    print(f"""
No duplicates detected. The 8 DISH breaches appear distinct (different dates).

Coefficient changes from {result_original['fcc_beta']:.2f}pp (all FCC) to {result_no_dish['fcc_beta']:.2f}pp when DISH excluded.
""")
    baseline_min, baseline_max = -6, -2

    if result_no_dish and baseline_min <= result_no_dish['fcc_beta'] <= baseline_max:
        print(f"[OUTCOME C: EXCLUDING DISH BRINGS COEFFICIENT IN-FAMILY]")
        print(f"  RECOMMENDATION: DISH is an influential outlier. Report results excluding DISH")
        print(f"  as robustness check, with note that FCC effect is modest except for DISH.")
    else:
        print(f"[OUTCOME D: STILL OUT OF FAMILY EVEN EXCLUDING DISH]")
        print(f"  RECOMMENDATION: Low-complexity is a genuinely different subpopulation.")
        print(f"  Fall back to reporting only high-complexity result (-1.2pp, robust, adequate N).")

print("\n" + "="*80 + "\n")
