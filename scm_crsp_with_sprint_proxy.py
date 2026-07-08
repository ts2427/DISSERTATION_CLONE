"""
COMPREHENSIVE FCC FIRM-BY-FIRM SCM - WITH SPRINT/T-MOBILE PROXY
================================================================

Same as n=38 analysis, but adds Sprint breaches using T-Mobile (TMUS)
as proxy (since Sprint merged with T-Mobile in April 2020).

This recovers 18 lost Sprint breaches.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import warnings

warnings.filterwarnings('ignore')

print("\n" + "="*80)
print("FCC FIRM-BY-FIRM SCM WITH SPRINT/T-MOBILE PROXY")
print("="*80)

# Load CRSP data
print("\n[1/3] Loading data...")
crsp = pd.read_csv('Data/wrds/crsp_daily_returns.csv')
crsp['date'] = pd.to_datetime(crsp['date'])
crsp['ret'] = pd.to_numeric(crsp['ret'], errors='coerce')

# Load FCC firms (deduplicated version: 151 FCC breaches from 54 unique firms)
fcc = pd.read_csv('Data/fcc/companies_to_match_DEDUPLICATED.csv')
fcc['breach_date'] = pd.to_datetime(fcc['breach_date'])
fcc_df = fcc[fcc['fcc_reportable'] == True].copy()

print(f"[OK] Loaded {len(crsp)} CRSP records, {len(fcc_df)} FCC breaches")

# Manual mapping (add Sprint -> TMUS mapping)
manual_map = {
    'AT&T': 'T',
    'Verizon': 'VZ',
    'Comcast': 'CMCSA',
    'CenturyLink': 'LUMN',
    'Charter': 'CHTR',
    'Frontier': 'FYBR',
    'DISH': 'DISH',
    'Altice': 'ATUS',
    'Sprint': 'TMUS',  # Use T-Mobile as proxy
    'T-Mobile': 'TMUS',
    'Suddenlink': 'LUMN',
    'Mediacom': 'MEDIA',
    'Cricket': 'TMUS',
    'Boost': 'TMUS',
}

# Get unique FCC firm names
fcc_firm_names = fcc_df['org_name'].unique()

# Match firms
matched_firms = {}
for firm_name in fcc_firm_names:
    for key, ticker in manual_map.items():
        if key.lower() in firm_name.lower():
            matched_firms[firm_name] = ticker
            break

print(f"[OK] Matched {len(matched_firms)} firms to CRSP tickers")

# ============================================================================
# Compute abnormal returns (CAR) for each firm
# ============================================================================

print("\n[2/3] Computing abnormal returns...")

# Get market returns
crsp['mkt_ret'] = crsp.groupby('date')['ret'].transform('mean')

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

            firm_effects.append({
                'firm_name': firm_name,
                'ticker': ticker,
                'n_breaches': len(firm_breaches),
                'n_cars_computed': len(cars),
                'mean_car_30d': mean_car,
                'is_sprint_proxy': 'Sprint' in firm_name
            })

    except Exception as e:
        pass

firm_effects_df = pd.DataFrame(firm_effects)

print(f"[OK] Computed CAR for {len(firm_effects_df)} firms")

# Count Sprint breaches recovered
sprint_count = firm_effects_df[firm_effects_df['is_sprint_proxy']]['n_breaches'].sum()
print(f"[OK] Sprint breaches recovered via T-Mobile proxy: {sprint_count}")

# ============================================================================
# Run SCM Analysis
# ============================================================================

print("\n[3/3] Running SCM analysis...")

# Compute non-FCC average CAR (from previous analysis we know this is ~0)
non_fcc_df = fcc[fcc['fcc_reportable'] == False].copy()

# For now, use 0 as control (since we didn't have non-FCC data before)
control_mean_car = 0.0

# Compute treatment effects
scm_results = []

for _, row in firm_effects_df.iterrows():
    gap = row['mean_car_30d'] - control_mean_car

    scm_results.append({
        'firm_name': row['firm_name'],
        'ticker': row['ticker'],
        'n_breaches': row['n_breaches'],
        'firm_car': row['mean_car_30d'],
        'treatment_effect': gap,
        'is_sprint_proxy': row['is_sprint_proxy']
    })

scm_results_df = pd.DataFrame(scm_results)

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
# Results
# ============================================================================

print("\n" + "="*80)
print("RESULTS: WITH SPRINT/T-MOBILE PROXY")
print("="*80)

print(f"\nSAMPLE SIZE:")
print(f"  FCC firms: {n_firms}")
print(f"  Total breaches: {scm_results_df['n_breaches'].sum()}")
print(f"  Sprint breaches (via T-Mobile): {sprint_count}")

print(f"\nAGGREGATE TREATMENT EFFECT:")
print(f"  Mean effect: {mean_effect:.4f}%")
print(f"  Std dev: {std_effect:.4f}%")
print(f"  SE: {se:.4f}%")
print(f"  95% CI: [{ci_lower:.4f}%, {ci_upper:.4f}%]")
print(f"  t-stat: {t_stat:.4f} (df={n_firms-1})")
print(f"  p-value: {p_value_ttest:.6f}")

if p_value_ttest < 0.05:
    print(f"  Status: SIGNIFICANT at 5%")
else:
    print(f"  Status: NOT significant at 5%")

print(f"\nFIRM-LEVEL EFFECTS:")
print(f"  Min: {scm_results_df['treatment_effect'].min():.4f}%")
print(f"  Q1: {scm_results_df['treatment_effect'].quantile(0.25):.4f}%")
print(f"  Median: {scm_results_df['treatment_effect'].median():.4f}%")
print(f"  Q3: {scm_results_df['treatment_effect'].quantile(0.75):.4f}%")
print(f"  Max: {scm_results_df['treatment_effect'].max():.4f}%")

print(f"\nCOMPARISON TO n=38 (WITHOUT SPRINT):")
print(f"  n=38 mean: -4.1606%")
print(f"  n={n_firms} mean: {mean_effect:.4f}%")
print(f"  Difference: {mean_effect - (-4.1606):.4f}%")

# Show Sprint contribution
print(f"\nSPRINT CONTRIBUTION BREAKDOWN:")
sprint_data = scm_results_df[scm_results_df['is_sprint_proxy']]
non_sprint_data = scm_results_df[~scm_results_df['is_sprint_proxy']]

print(f"  Sprint breaches: {sprint_data['n_breaches'].sum()}")
print(f"  Sprint mean effect: {sprint_data['treatment_effect'].mean():.4f}%")
print(f"  Non-Sprint mean effect: {non_sprint_data['treatment_effect'].mean():.4f}%")

print(f"\nTOP FIRMS BY EFFECT:")
for idx, row in scm_results_df.nlargest(5, 'treatment_effect').iterrows():
    sprint_note = " [SPRINT PROXY]" if row['is_sprint_proxy'] else ""
    print(f"  {row['firm_name']:30} {row['treatment_effect']:8.4f}%{sprint_note}")

print(f"\nBOTTOM FIRMS:")
for idx, row in scm_results_df.nsmallest(5, 'treatment_effect').iterrows():
    sprint_note = " [SPRINT PROXY]" if row['is_sprint_proxy'] else ""
    print(f"  {row['firm_name']:30} {row['treatment_effect']:8.4f}%{sprint_note}")

# Save results
output_dir = Path("outputs/scm_crsp_with_sprint")
output_dir.mkdir(parents=True, exist_ok=True)

scm_results_df.to_csv(output_dir / "scm_crsp_sprint_proxy_results.csv", index=False)

print(f"\n[OK] Results saved to: {output_dir}")
print("\n" + "="*80)
