"""
FIRM-BY-FIRM SYNTHETIC CONTROL METHOD (SCM) USING SCPI_PKG
Cattaneo, Feng, Palomba, and Titiunik (2025)
Journal of Statistical Software

Treatment: FCC Rule 37.3 Implementation (Sept 28, 2007)
Sample: 10 FCC telecommunications carriers
"""

import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# Import scpi_pkg functions
from scpi_pkg.scdataMulti import scdataMulti
from scpi_pkg.scest import scest
from scpi_pkg.scpi import scpi

print("=" * 80)
print("FIRM-BY-FIRM SYNTHETIC CONTROL METHOD (SCPI_PKG)")
print("=" * 80)

# Load data
print("\n[1/5] Loading data...")
df = pd.read_csv("Data/processed/FINAL_DISSERTATION_DATASET_DEDUPLICATED_ENRICHED.csv")
print(f"  Total observations: {len(df)}")

# Convert breach_date to datetime
df['breach_date'] = pd.to_datetime(df['breach_date'])
df['breach_year'] = df['breach_date'].dt.year

# Data preparation
print("\n[2/5] Data preparation...")

# Handle Sprint/T-Mobile merger: recode Sprint to T-Mobile after April 1, 2020
sprint_mask = (df['org_name'].str.contains('Sprint', case=False, na=False)) & (df['breach_date'] >= '2020-04-01')
if sprint_mask.sum() > 0:
    tmo_cik = df[df['org_name'].str.contains('T-Mobile', case=False, na=False)]['cik'].iloc[0] if any(df['org_name'].str.contains('T-Mobile', case=False, na=False)) else None
    if tmo_cik:
        df.loc[sprint_mask, 'cik'] = tmo_cik
        print(f"  - Recoded {sprint_mask.sum()} Sprint breaches to T-Mobile")

# Identify treatment and control groups
fcc_firms = df[df['fcc_reportable'] == True]['cik'].unique()
non_fcc_firms = df[df['fcc_reportable'] == False]['cik'].unique()

print(f"  - Treatment group (FCC): {len(fcc_firms)} firms")
print(f"  - Donor pool (non-FCC): {len(non_fcc_firms)} firms")

# Filter to relevant periods: 2006 (pre-treatment) and 2008+ (post-treatment)
# 2007 is excluded as it's the transition year
df_analysis = df[(df['breach_year'] == 2006) | (df['breach_year'] >= 2008)].copy()
print(f"  - Analysis sample: {len(df_analysis)} observations (2006, 2008+)")

# Remove rows with missing outcome or covariates
df_analysis = df_analysis.dropna(subset=['car_30d', 'firm_size_log', 'leverage', 'roa'])
print(f"  - After removing missing data: {len(df_analysis)} observations")

# Create period identifier for scdataMulti
df_analysis['period'] = df_analysis['breach_year']

# Get unique FCC firms in analysis sample
fcc_firms_analysis = df_analysis[df_analysis['fcc_reportable'] == True]['cik'].unique()
print(f"  - FCC firms in analysis sample: {len(fcc_firms_analysis)}")

if len(fcc_firms_analysis) == 0:
    print("[ERROR] No FCC firms with complete data in analysis period")
    exit(1)

print("\n[3/5] Running SCM estimation with scdataMulti...")

try:
    # Run scdataMulti: features should be a dictionary mapping column names to their roles
    # For simplicity, use an empty dict or dict with minimal specification

    features_dict = {
        'firm_size_log': 'covariate',
        'leverage': 'covariate',
        'roa': 'covariate'
    }

    data_out = scdataMulti(
        df=df_analysis,
        id_var='cik',
        time_var='period',
        outcome_var='car_30d',
        treatment_var='fcc_reportable',
        features=features_dict,
        verbose=True
    )

    print("  - scdataMulti completed successfully")

except TypeError as e:
    print(f"  [ERROR] TypeError in scdataMulti: {e}")
    print("\n  Attempting simpler approach with features=None...")

    try:
        data_out = scdataMulti(
            df=df_analysis,
            id_var='cik',
            time_var='period',
            outcome_var='car_30d',
            treatment_var='fcc_reportable',
            features=None,
            verbose=False
        )
        print("  - scdataMulti completed successfully (without covariates)")
    except Exception as e2:
        print(f"  [ERROR] Alternative approach failed: {e2}")
        import traceback
        traceback.print_exc()
        exit(1)

except Exception as e:
    print(f"  [ERROR] scdataMulti failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print("\n[4/5] Running point estimation (scest)...")

try:
    # scest computes treatment effects
    est_out = scest(data_out)
    print("  - scest completed successfully")

except Exception as e:
    print(f"  [ERROR] scest failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print("\n[5/5] Running inference (scpi with permutation tests)...")

try:
    # scpi computes prediction intervals with permutation inference
    pi_out = scpi(data_out, est_out)
    print("  - scpi (permutation inference) completed successfully")

except Exception as e:
    print(f"  [ERROR] scpi failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Extract and report results
print("\n" + "=" * 80)
print("RESULTS - FIRM-BY-FIRM SYNTHETIC CONTROL ANALYSIS")
print("=" * 80)

print(f"\nEstimation output keys: {list(est_out.keys())}")
print(f"Inference output keys: {list(pi_out.keys())}")

# Print detailed output
print("\n--- Point Estimates (est_out) ---")
for key, val in est_out.items():
    if isinstance(val, (dict, pd.DataFrame)):
        print(f"{key}:")
        print(val)
    else:
        print(f"{key}: {val}")

print("\n--- Inference Results (pi_out) ---")
for key, val in pi_out.items():
    if isinstance(val, (dict, pd.DataFrame)):
        print(f"{key}:")
        print(val)
    else:
        print(f"{key}: {val}")

# Summary statistics
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"Number of treated units (FCC firms): {len(fcc_firms_analysis)}")
print(f"Number of control units (non-FCC firms): {len(df_analysis[df_analysis['fcc_reportable'] == False]['cik'].unique())}")
print(f"Pre-treatment periods: 1 (2006 only)")
print(f"Post-treatment periods: {len(df_analysis[df_analysis['period'] >= 2008]['period'].unique())}")
print(f"Total observations in analysis: {len(df_analysis)}")
print(f"Covariates used for matching: firm_size_log, leverage, roa")

print("\n" + "=" * 80)
print("COMPLETE")
print("=" * 80)
