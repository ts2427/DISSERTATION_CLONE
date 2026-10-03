import pandas as pd
import numpy as np
from scpi_pkg.scdataMulti import scdataMulti
from scpi_pkg.scest import scest
from scpi_pkg.scpi import scpi
import warnings
warnings.filterwarnings('ignore')

print("=" * 80)
print("SCPI SYNTHETIC CONTROL ANALYSIS")
print("=" * 80)

# Load data
df = pd.read_csv('Data/processed/FINAL_DISSERTATION_DATASET_DEDUPLICATED_ENRICHED.csv')
df['breach_year'] = pd.to_datetime(df['breach_date']).dt.year

# Recode Sprint to T-Mobile post-April 1, 2020
sprint_mask = (df['org_name'].str.contains('Sprint', case=False, na=False)) & (pd.to_datetime(df['breach_date']) >= '2020-04-01')
if sprint_mask.sum() > 0:
    tmo_cik = df[df['org_name'].str.contains('T-Mobile', case=False, na=False)]['cik'].iloc[0]
    df.loc[sprint_mask, 'cik'] = tmo_cik
    print(f"Recoded {sprint_mask.sum()} Sprint breaches to T-Mobile\n")

# Filter to 2006 (pre) and 2008+ (post)
df_analysis = df[(df['breach_year'] == 2006) | (df['breach_year'] >= 2008)].copy()
df_analysis = df_analysis.dropna(subset=['car_30d'])

print(f"Raw sample size: {len(df_analysis)}")
print(f"Before aggregation - FCC breaches: {df_analysis['fcc_reportable'].sum()}\n")

# CRITICAL: Aggregate to one observation per unit-period
# Some firms have multiple breaches in the same year
# Take mean of car_30d within each unit-period combination
df_agg = df_analysis.groupby(['cik', 'breach_year']).agg({
    'car_30d': 'mean',
    'fcc_reportable': 'first',
    'firm_size_log': 'first',
    'leverage': 'first',
    'roa': 'first'
}).reset_index()

df_agg.rename(columns={'breach_year': 'period'}, inplace=True)

print(f"After aggregation: {len(df_agg)} observations")
print(f"Unique units: {df_agg['cik'].nunique()}")
print(f"FCC firms (treated): {df_agg['fcc_reportable'].sum()}")
print(f"Non-FCC firms (control): {(df_agg['fcc_reportable'] == 0).sum()}")
print(f"Time periods: {sorted(df_agg['period'].unique())}\n")

# Run scdataMulti
print("Running scdataMulti...")
try:
    data_out = scdataMulti(
        df=df_agg,
        id_var='cik',
        time_var='period',
        outcome_var='car_30d',
        treatment_var='fcc_reportable',
        features=None,
        verbose=False
    )
    print("✓ scdataMulti complete\n")
except Exception as e:
    print(f"✗ scdataMulti failed: {e}\n")
    exit(1)

# Run scest
print("Running scest (point estimation)...")
try:
    est_out = scest(data_out)
    print("✓ scest complete\n")
except Exception as e:
    print(f"✗ scest failed: {e}\n")
    exit(1)

# Run scpi
print("Running scpi (permutation inference)...")
try:
    pi_out = scpi(data_out, est_out)
    print("✓ scpi complete\n")
except Exception as e:
    print(f"✗ scpi failed: {e}\n")
    exit(1)

# Report results
print("=" * 80)
print("RESULTS")
print("=" * 80)

print("\nEstimation Output Keys:", list(est_out.keys()))
print("Inference Output Keys:", list(pi_out.keys()))

# Extract and display key results
print("\n--- TREATMENT EFFECTS ---")

if 'tau' in est_out:
    tau = est_out['tau']
    if isinstance(tau, (int, float, np.number)):
        print(f"Mean treatment effect: {tau:.4f}%")
    elif isinstance(tau, dict):
        print(f"Treatment effects by unit:")
        for uid, te in sorted(list(tau.items())[:10]):
            print(f"  CIK {uid}: {te:.4f}%")
        if len(tau) > 10:
            print(f"  ... and {len(tau)-10} more units")
    else:
        print(f"Treatment effects: {type(tau)}")

if 'sigma2_u' in est_out:
    print(f"\nOutcome variance (sigma2_u): {est_out['sigma2_u']:.6f}")

if 'sigma2_v' in est_out:
    print(f"Residual variance (sigma2_v): {est_out['sigma2_v']:.6f}")

print("\n--- INFERENCE RESULTS ---")

if 'est' in pi_out:
    print(f"Point estimate: {pi_out['est']:.4f}%")

if 'ci' in pi_out:
    ci = pi_out['ci']
    if isinstance(ci, (list, tuple)) and len(ci) >= 2:
        print(f"95% confidence interval: [{ci[0]:.4f}%, {ci[1]:.4f}%]")
    else:
        print(f"CI: {ci}")

if 'pval' in pi_out:
    print(f"Permutation p-value: {pi_out['pval']:.4f}")

print("\n--- SUMMARY STATISTICS ---")
print(f"Number of treated units: {(df_agg['fcc_reportable'] == 1).sum()}")
print(f"Number of control units: {(df_agg['fcc_reportable'] == 0).sum()}")
print(f"Pre-treatment periods: 1 (2006)")
print(f"Post-treatment periods: {len(df_agg[df_agg['period'] >= 2008]['period'].unique())}")
print(f"Total observations in analysis: {len(df_agg)}")

print("\n" + "=" * 80)
print("Complete")
print("=" * 80)
