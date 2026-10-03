"""
SYNTHETIC CONTROL METHOD - BREACH EVENT LEVEL
Single treated unit (aggregate FCC) vs donor pool (non-FCC breaches)
Uses scdata (single unit) instead of scdataMulti (multiple units)
"""

import pandas as pd
import numpy as np
from scpi_pkg.scdata import scdata
from scpi_pkg.scest import scest
from scpi_pkg.scpi import scpi
import warnings
warnings.filterwarnings('ignore')

print("=" * 80)
print("SYNTHETIC CONTROL METHOD - BREACH EVENT LEVEL ANALYSIS")
print("=" * 80)

# Load corrected deduplicated dataset
print("\n[1/4] Loading data...")
df = pd.read_csv('Data/processed/FINAL_DISSERTATION_DATASET_DEDUPLICATED_ENRICHED.csv')

# Each breach event is an observation
# Drop missing values for outcome and covariates
df_clean = df.dropna(subset=['car_30d', 'firm_size_log', 'leverage', 'roa']).copy()

# Create year variable for time dimension
df_clean['year'] = pd.to_datetime(df_clean['breach_date']).dt.year

# Separate FCC and non-FCC breaches
fcc_breaches = df_clean[df_clean['fcc_reportable'] == True].copy()
nonfcc_breaches = df_clean[df_clean['fcc_reportable'] == False].copy()

print(f"  - Total breach events: {len(df_clean)}")
print(f"  - FCC breach events: {len(fcc_breaches)}")
print(f"  - Non-FCC breach events: {len(nonfcc_breaches)}")
print(f"  - FCC firms: {fcc_breaches['cik'].nunique()}")
print(f"  - Non-FCC firms: {nonfcc_breaches['cik'].nunique()}")
print(f"  - Year range: {df_clean['year'].min()} to {df_clean['year'].max()}")

# Aggregate FCC breaches by year (treated unit)
print("\n[2/4] Preparing treated unit (aggregate FCC breaches)...")
fcc_annual = fcc_breaches.groupby('year').agg(
    car_30d=('car_30d', 'mean'),
    firm_size_log=('firm_size_log', 'mean'),
    leverage=('leverage', 'mean'),
    roa=('roa', 'mean'),
    n_breaches=('cik', 'count')
).reset_index()

# Add ID column for scdata
fcc_annual['id'] = 'FCC'

print(f"  - FCC annual observations: {len(fcc_annual)}")
print(f"\n  FCC Aggregate by Year:")
print(fcc_annual.to_string(index=False))

# Prepare donor pool (non-FCC breaches by year, split into size quartiles)
print("\n[3/4] Preparing donor pool (non-FCC breaches)...")

# Create size quartiles for non-FCC breaches (for stratified donors)
q1, q2, q3 = nonfcc_breaches['firm_size_log'].quantile([0.25, 0.5, 0.75])

def assign_size_group(size):
    if size <= q1:
        return 'Q1_Small'
    elif size <= q2:
        return 'Q2_Med-Small'
    elif size <= q3:
        return 'Q3_Med-Large'
    else:
        return 'Q4_Large'

nonfcc_breaches['size_group'] = nonfcc_breaches['firm_size_log'].apply(assign_size_group)

# Split non-FCC by size to create multiple donor units
nonfcc_donors_list = []
for i, size_group in enumerate(['Q1_Small', 'Q2_Med-Small', 'Q3_Med-Large', 'Q4_Large']):
    group_data = nonfcc_breaches[nonfcc_breaches['size_group'] == size_group].copy()
    if len(group_data) > 0:
        donor_agg = group_data.groupby('year').agg(
            car_30d=('car_30d', 'mean'),
            firm_size_log=('firm_size_log', 'mean'),
            leverage=('leverage', 'mean'),
            roa=('roa', 'mean'),
            n_breaches=('cik', 'count')
        ).reset_index()
        donor_agg['id'] = size_group
        nonfcc_donors_list.append(donor_agg)

nonfcc_donors = pd.concat(nonfcc_donors_list, ignore_index=True)

print(f"  - Non-FCC donors created: {nonfcc_donors['id'].nunique()}")
print(f"  - Donor units: {sorted(nonfcc_donors['id'].unique())}")
print(f"  - Total donor observations: {len(nonfcc_donors)}")

print("\n[4/4] Running SCM analysis...")

try:
    # Run scdata for single treated unit (aggregate FCC)
    # Pre-treatment: 2006 only (sparse but documented constraint)
    # Post-treatment: 2007 onwards

    # Combine treated and control units into single dataframe
    df_scm = pd.concat([fcc_annual, nonfcc_donors], ignore_index=True)

    # Fill in missing year-unit combinations with NaN (required for scdata)
    # scdata expects a complete rectangular panel
    all_years = np.arange(df_scm['year'].min(), df_scm['year'].max() + 1)
    all_units = df_scm['id'].unique()

    df_complete = []
    for unit in all_units:
        for year in all_years:
            row_data = df_scm[(df_scm['id'] == unit) & (df_scm['year'] == year)]
            if len(row_data) > 0:
                df_complete.append(row_data.iloc[0])
            else:
                # Add missing row with NaN outcome, but keep covariates as NaN
                df_complete.append({'id': unit, 'year': year,
                                   'car_30d': np.nan, 'firm_size_log': np.nan,
                                   'leverage': np.nan, 'roa': np.nan, 'n_breaches': np.nan})

    df_scm = pd.DataFrame(df_complete)

    print("\n  Combined data for scdata:")
    print(f"    - Total rows (after fill): {len(df_scm)}")
    print(f"    - Unique units: {sorted(df_scm['id'].unique())}")
    print(f"    - Year range: {df_scm['year'].min()} to {df_scm['year'].max()}")

    # Get list of control unit IDs
    control_units = [u for u in df_scm['id'].unique() if u != 'FCC']

    print("\n  Running scdata (single treated unit with multiple control units)...")
    print("    Note: No feature matching (sparse pre-treatment period constraints)")
    sc_data = scdata(
        df=df_scm,
        id_var='id',  # Unit identifier
        time_var='year',
        outcome_var='car_30d',
        period_pre=np.array([2006]),  # Pre-treatment: 2006 only
        period_post=np.arange(2007, 2025),  # Post-treatment: 2007+
        unit_tr='FCC',  # Treated unit label
        unit_co=control_units,  # Control units (donor pool by size)
        features=None,  # No feature matching (sparse pre-period)
        cointegrated_data=False,
        constant=True,
        verbose=True
    )
    print("  ✓ scdata completed")

    print("\n  Running scest (point estimation)...")
    sc_est = scest(sc_data, w_constr={'name': 'simplex'})
    print("  ✓ scest completed")

    print("\n  Running scpi (inference with permutation test)...")
    sc_pi = scpi(sc_data, w_constr={'name': 'simplex'})
    print("  ✓ scpi completed")

    # Report results
    print("\n" + "=" * 80)
    print("RESULTS")
    print("=" * 80)

    try:
        print("\nPoint Estimation Summary:")
        print(sc_est.summary())
    except Exception as e:
        print(f"Summary not available: {e}")
        print(f"\nAvailable attributes: {[a for a in dir(sc_est) if not a.startswith('_')][:20]}")

    try:
        print("\nInference Summary:")
        print(sc_pi.summary())
    except Exception as e:
        print(f"Inference summary not available: {e}")

    print("\n" + "=" * 80)
    print("COMPLETE")
    print("=" * 80)

except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
