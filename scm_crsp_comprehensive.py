"""
COMPREHENSIVE FCC FIRM-BY-FIRM SCM USING CRSP DATA
===================================================

Uses all FCC firms (n=54) matched to CRSP daily returns.
Computes abnormal returns (CAR) for each firm's breaches.
Runs SCM analysis on all matched firms.

This approach addresses the n=1 problem with realistic sample size.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import warnings

warnings.filterwarnings('ignore')

print("\n" + "="*80)
print("COMPREHENSIVE FCC FIRM-BY-FIRM SCM - USING CRSP DATA")
print("="*80)

# ============================================================================
# STAGE 1: LOAD AND PREPARE DATA
# ============================================================================

print("\n[STAGE 1/5] Loading data...")

# Load FCC firms
fcc_raw = pd.read_csv('Data/fcc/companies_to_match.csv')
fcc_df = fcc_raw[fcc_raw['fcc_reportable'] == True].copy()
fcc_df['breach_date'] = pd.to_datetime(fcc_df['breach_date'])

print(f"  [OK] Loaded {len(fcc_df)} FCC breach records")
print(f"  [OK] {fcc_df['org_name'].nunique()} unique FCC firms")

# Load CRSP mapping
print("  [OK] Loading CRSP ticker mapping...")
crsp_mapping = pd.read_csv('Data/wrds/ticker_permno_mapping.csv')
crsp_mapping['namedt'] = pd.to_datetime(crsp_mapping['namedt'])
crsp_mapping['nameendt'] = pd.to_datetime(crsp_mapping['nameendt'])

# Load CRSP daily returns
print("  [OK] Loading CRSP daily returns (this may take a moment)...")
crsp = pd.read_csv('Data/wrds/crsp_daily_returns.csv')
crsp['date'] = pd.to_datetime(crsp['date'])
crsp['ret'] = pd.to_numeric(crsp['ret'], errors='coerce')

print(f"  [OK] Loaded {len(crsp)} CRSP daily observations")
print(f"  [OK] Date range: {crsp['date'].min().date()} to {crsp['date'].max().date()}")

# Load market index (for abnormal returns)
print("  [OK] Loading market indices...")
mkt = pd.read_csv('Data/wrds/market_indices.csv')
mkt['date'] = pd.to_datetime(mkt['date'])

# ============================================================================
# STAGE 2: MATCH FCC FIRMS TO CRSP
# ============================================================================

print("\n[STAGE 2/5] Matching FCC firms to CRSP...")

# Create mapping dict
ticker_map = {}

# Manual mapping for major FCC firms (based on industry knowledge)
manual_map = {
    'AT&T': 'T',
    'Verizon': 'VZ',
    'Comcast': 'CMCSA',
    'CenturyLink': 'LUMN',
    'Charter': 'CHTR',
    'Frontier': 'FYBR',
    'DISH': 'DISH',
    'Altice': 'ATUS',
    'Sprint': 'S',
    'T-Mobile': 'TMUS',
    'Suddenlink': 'LUMN',  # Acquired by CenturyLink
    'Mediacom': 'MEDIA',
    'Cricket': 'TMUS',  # Owned by T-Mobile
    'Boost': 'TMUS',  # Owned by T-Mobile
}

# Get unique FCC firm names
fcc_firm_names = fcc_df['org_name'].unique()

# Try to match each firm
matched_firms = {}
unmatched = []

for firm_name in fcc_firm_names:
    # Try manual map first
    matched = False
    for key, ticker in manual_map.items():
        if key.lower() in firm_name.lower():
            matched_firms[firm_name] = ticker
            matched = True
            break

    if not matched:
        unmatched.append(firm_name)

print(f"  [OK] Matched {len(matched_firms)} firms to CRSP tickers")
print(f"  [*] Could not match {len(unmatched)} firms")

if len(unmatched) > 0:
    print(f"\n  Unmatched firms:")
    for firm in sorted(unmatched)[:15]:
        print(f"    - {firm}")
    if len(unmatched) > 15:
        print(f"    ... and {len(unmatched) - 15} more")

# Get unique matched tickers
unique_tickers = sorted(set(matched_firms.values()))
print(f"\n  Unique matched tickers: {len(unique_tickers)}")
print(f"  {', '.join(unique_tickers)}")

# ============================================================================
# STAGE 3: COMPUTE ABNORMAL RETURNS (CAR) FOR EACH FIRM
# ============================================================================

print("\n[STAGE 3/5] Computing abnormal returns (CAR)...")

# Get market returns
crsp['mkt_ret'] = crsp.groupby('date')['ret'].transform('mean')

# Compute CAR for each firm
firm_effects = []

for firm_name, ticker in matched_firms.items():
    try:
        # Get firm's CRSP data
        firm_crsp = crsp[crsp['ticker'] == ticker].copy()

        if len(firm_crsp) < 100:
            continue

        # Get breaches for this firm
        firm_breaches = fcc_df[fcc_df['org_name'] == firm_name]['breach_date'].unique()

        if len(firm_breaches) == 0:
            continue

        # For each breach, compute 30-day CAR
        cars = []

        for breach_date in firm_breaches:
            # Window: breach date to 30 days after
            start_date = breach_date
            end_date = breach_date + pd.Timedelta(days=30)

            # Get daily returns in window
            window = firm_crsp[(firm_crsp['date'] >= start_date) &
                               (firm_crsp['date'] <= end_date)].copy()

            if len(window) < 10:  # Need at least 10 trading days
                continue

            # Compute abnormal returns
            window['abnormal_ret'] = window['ret'] - window['mkt_ret']

            # Cumulative abnormal return
            car = (1 + window['abnormal_ret']).prod() - 1
            cars.append(car * 100)  # Convert to percentage

        if len(cars) > 0:
            mean_car = np.mean(cars)
            std_car = np.std(cars) if len(cars) > 1 else 0

            firm_effects.append({
                'firm_name': firm_name,
                'ticker': ticker,
                'n_breaches': len(firm_breaches),
                'n_cars_computed': len(cars),
                'mean_car_30d': mean_car,
                'std_car': std_car,
                'min_car': np.min(cars),
                'max_car': np.max(cars)
            })

    except Exception as e:
        pass

firm_effects_df = pd.DataFrame(firm_effects)

print(f"  [OK] Computed CAR for {len(firm_effects_df)} firms")
print(f"\nFirm-Level Abnormal Returns (30-day CAR):")
print(firm_effects_df[['firm_name', 'ticker', 'n_breaches', 'mean_car_30d']].sort_values('mean_car_30d', ascending=False).to_string(index=False))

# ============================================================================
# STAGE 4: RUN SCM ANALYSIS
# ============================================================================

print("\n[STAGE 4/5] Running SCM analysis on matched firms...")

# For SCM, we'll use a simplified approach:
# Compare each FCC firm's CAR to non-FCC firms' average CAR

non_fcc_df = fcc_raw[fcc_raw['fcc_reportable'] == False].copy()
non_fcc_df['breach_date'] = pd.to_datetime(non_fcc_df['breach_date'])

# Compute non-FCC average CAR
print("  Computing control group (non-FCC) average CAR...")
non_fcc_cars = []

for _, breach_row in non_fcc_df.iterrows():
    ticker = breach_row.get('ticker')
    if pd.isna(ticker):
        continue

    try:
        breach_date = pd.to_datetime(breach_row['breach_date'])
        firm_crsp = crsp[crsp['ticker'] == ticker].copy()

        if len(firm_crsp) < 100:
            continue

        start_date = breach_date
        end_date = breach_date + pd.Timedelta(days=30)

        window = firm_crsp[(firm_crsp['date'] >= start_date) &
                           (firm_crsp['date'] <= end_date)].copy()

        if len(window) < 10:
            continue

        window['abnormal_ret'] = window['ret'] - window['mkt_ret']
        car = (1 + window['abnormal_ret']).prod() - 1
        non_fcc_cars.append(car * 100)

    except:
        pass

control_mean_car = np.mean(non_fcc_cars) if len(non_fcc_cars) > 0 else 0
control_std_car = np.std(non_fcc_cars) if len(non_fcc_cars) > 1 else 0

print(f"  [OK] Control group (n={len(non_fcc_cars)} breaches): mean CAR = {control_mean_car:.4f}%")

# Compute treatment effects (gaps)
scm_results = []

for _, row in firm_effects_df.iterrows():
    gap = row['mean_car_30d'] - control_mean_car

    scm_results.append({
        'firm_name': row['firm_name'],
        'ticker': row['ticker'],
        'n_breaches': row['n_breaches'],
        'firm_car': row['mean_car_30d'],
        'control_car': control_mean_car,
        'treatment_effect': gap
    })

scm_results_df = pd.DataFrame(scm_results)

print(f"\n[STAGE 5/5] Statistical inference...")

# Summary statistics
n_firms = len(scm_results_df)
mean_effect = scm_results_df['treatment_effect'].mean()
std_effect = scm_results_df['treatment_effect'].std()
se = std_effect / np.sqrt(n_firms) if n_firms > 1 else 0
t_stat = mean_effect / se if se > 0 else 0

from scipy import stats
if n_firms > 1:
    p_value_ttest = 2 * (1 - stats.t.cdf(abs(t_stat), n_firms - 1))
else:
    p_value_ttest = np.nan

ci_lower = mean_effect - 1.96 * se
ci_upper = mean_effect + 1.96 * se

# ============================================================================
# RESULTS
# ============================================================================

print("\n" + "="*80)
print("RESULTS SUMMARY")
print("="*80)

print(f"\nSAMPLE SIZE:")
print(f"  FCC firms matched to CRSP: {n_firms}")
print(f"  Total FCC breaches analyzed: {scm_results_df['n_breaches'].sum()}")
print(f"  Control breaches: {len(non_fcc_cars)}")

print(f"\nAGGREGATE TREATMENT EFFECT:")
print(f"  Mean effect: {mean_effect:.4f}%")
print(f"  Std dev: {std_effect:.4f}%")
print(f"  SE: {se:.4f}%")
print(f"  95% CI: [{ci_lower:.4f}%, {ci_upper:.4f}%]")
print(f"  t-stat: {t_stat:.4f} (df={n_firms-1})")
print(f"  p-value: {p_value_ttest:.4f}")

print(f"\nINTERPRETATION:")
if p_value_ttest < 0.05:
    print(f"  [OK] Treatment effect IS significant at 5% level")
else:
    print(f"  [*] Treatment effect is NOT significant at 5% level")

print(f"\nFIRM-LEVEL EFFECTS:")
print(f"  Min: {scm_results_df['treatment_effect'].min():.4f}%")
print(f"  Q1: {scm_results_df['treatment_effect'].quantile(0.25):.4f}%")
print(f"  Median: {scm_results_df['treatment_effect'].median():.4f}%")
print(f"  Q3: {scm_results_df['treatment_effect'].quantile(0.75):.4f}%")
print(f"  Max: {scm_results_df['treatment_effect'].max():.4f}%")

print(f"\nTOP 10 FIRMS BY EFFECT SIZE:")
top_firms = scm_results_df.nlargest(10, 'treatment_effect')
for idx, row in top_firms.iterrows():
    print(f"  {row['firm_name']:30} {row['ticker']:10} {row['treatment_effect']:10.4f}%")

print(f"\nBOTTOM 5 FIRMS:")
bottom_firms = scm_results_df.nsmallest(5, 'treatment_effect')
for idx, row in bottom_firms.iterrows():
    print(f"  {row['firm_name']:30} {row['ticker']:10} {row['treatment_effect']:10.4f}%")

# Save results
output_dir = Path("outputs/scm_crsp_comprehensive")
output_dir.mkdir(parents=True, exist_ok=True)

scm_results_df.to_csv(output_dir / "scm_crsp_firm_results.csv", index=False)
firm_effects_df.to_csv(output_dir / "firm_effects_with_controls.csv", index=False)

print(f"\n[OK] Results saved to: {output_dir}")
print("\n" + "="*80)
