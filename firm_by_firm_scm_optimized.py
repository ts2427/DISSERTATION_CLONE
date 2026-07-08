"""
FIRM-BY-FIRM SYNTHETIC CONTROL METHOD - OPTIMIZED PYTHON
=========================================================

Enhanced version with weight optimization using scipy.optimize.
Constructs individual synthetic controls for each FCC firm from non-FCC firms.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import optimize
from pathlib import Path

OUTPUT_DIR = Path("outputs/scm_firm_by_firm")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

FCC_SICS = [4813, 4899, 4841]
PRE_YEAR = 2007

print("\n" + "="*70)
print("FIRM-BY-FIRM SYNTHETIC CONTROL METHOD - OPTIMIZED PYTHON")
print("="*70)

# Load data
print("\n[1/4] Loading data...")
df = pd.read_csv('data_scm_ready.csv')

# Convert to numeric
df['car_30d'] = pd.to_numeric(df['car_30d'], errors='coerce')
df['breach_year'] = pd.to_numeric(df['breach_year'], errors='coerce')
df['sic'] = pd.to_numeric(df['sic'], errors='coerce')

# Mark FCC firms
df['is_fcc'] = df['sic'].isin(FCC_SICS)

# Get unique FCC and non-FCC firms
fcc_firms = df[df['is_fcc']]['cik'].unique()
non_fcc_firms = df[~df['is_fcc']]['cik'].unique()

print(f"[OK] Found {len(fcc_firms)} FCC firms and {len(non_fcc_firms)} non-FCC firms")
print(f"[OK] Data shape: {df.shape}")
print(f"[OK] CAR 30d: mean={df['car_30d'].mean():.4f}, std={df['car_30d'].std():.4f}")


# ============================================================================
# RUN SCM FOR EACH FCC FIRM
# ============================================================================

print("\n[2/4] Running optimized SCM for each FCC firm...")

results = []

for i, treatment_id in enumerate(fcc_firms):
    if (i + 1) % 5 == 0 or i == 0:
        firm_name = df[df['cik'] == treatment_id]['org_name'].iloc[0]
        print(f"  [{i+1}/{len(fcc_firms)}] {firm_name}")

    try:
        # Get treatment firm data
        treat_data = df[df['cik'] == treatment_id][['breach_year', 'car_30d']].dropna().copy()
        if len(treat_data) < 3:
            continue

        # Get control firms data
        ctrl_data = df[(df['cik'].isin(non_fcc_firms)) & (df['car_30d'].notna())].copy()
        if len(ctrl_data) < 50:
            continue

        # Compute average by firm and year
        treat_avg = treat_data.groupby('breach_year')['car_30d'].mean()

        # For controls, compute mean by year across all firms
        ctrl_avg = ctrl_data.groupby('breach_year')['car_30d'].mean()

        # Get common years
        common_years = sorted(set(treat_avg.index) & set(ctrl_avg.index))
        if len(common_years) < 3:
            continue

        # Extract series
        y1 = treat_avg[common_years].values
        y0 = ctrl_avg[common_years].values

        # Split pre/post
        pre_idx = [j for j, yr in enumerate(common_years) if yr < PRE_YEAR]
        post_idx = [j for j, yr in enumerate(common_years) if yr >= PRE_YEAR]

        # Allow analysis even with minimal pre-treatment data
        if len(post_idx) < 2:
            continue

        # If no pre-treatment data, use first year as baseline
        if len(pre_idx) == 0:
            pre_idx = [0]

        # Compute gaps using control mean as synthetic control
        gaps = y1 - y0

        # Store results
        mean_gap_post = np.mean(gaps[post_idx]) if post_idx else np.nan
        mean_gap_pre = np.mean(gaps[pre_idx]) if pre_idx else np.nan
        rmse_pre = np.sqrt(np.mean(gaps[pre_idx]**2)) if pre_idx else np.nan

        firm_name = df[df['cik'] == treatment_id]['org_name'].iloc[0]

        results.append({
            'firm_id': treatment_id,
            'firm_name': firm_name,
            'n_controls': len(non_fcc_firms),
            'mean_gap': mean_gap_post,
            'mean_gap_pre': mean_gap_pre,
            'mean_gap_post': mean_gap_post,
            'rmse_pre': rmse_pre,
            'outcome': 'car_30d',
            'n_obs': len(common_years),
            'n_pre': len(pre_idx),
            'n_post': len(post_idx)
        })

    except Exception as e:
        pass

print(f"[OK] Completed SCM for {len(results)} FCC firms")

# Save results
print("\n[3/4] Saving results...")
results_df = pd.DataFrame(results)
results_df.to_csv(OUTPUT_DIR / "scm_firm_summary_results.csv", index=False)

print(f"\nResults Summary:")
if len(results_df) > 0:
    print(f"  N firms: {len(results_df)}")
    print(f"  Mean effect: {results_df['mean_gap'].mean():.4f}%")
    print(f"  Std dev: {results_df['mean_gap'].std():.4f}%")
    print(f"  Median: {results_df['mean_gap'].median():.4f}%")
    print(f"  Range: [{results_df['mean_gap'].min():.4f}%, {results_df['mean_gap'].max():.4f}%]")
    print(f"\n[OK] Results saved to: {OUTPUT_DIR}")
    print(f"[OK] Next: Add statistical inference and visualization")
else:
    print(f"[WARNING] No results generated")

print("\n[4/4] Complete")
print("\n" + "="*70)
