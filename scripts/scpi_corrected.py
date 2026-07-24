import pandas as pd
import numpy as np
from scpi_pkg.scdataMulti import scdataMulti
from scpi_pkg.scest import scest
from scpi_pkg.scpi import scpi
import warnings
warnings.filterwarnings('ignore')

print("=" * 80)
print("SCM ANALYSIS - CORRECTED IMPLEMENTATION")
print("=" * 80)

# Load corrected deduplicated dataset
print("\n[1/4] Loading data...")
df = pd.read_csv('Data/processed/FINAL_DISSERTATION_DATASET_DEDUPLICATED_ENRICHED.csv')

# Create year variable
df['year'] = pd.to_datetime(df['breach_date']).dt.year

# Sprint/T-Mobile unification post April 1 2020
print("  - Recoding Sprint to T-Mobile post-April 1, 2020")
tmobile_cik = 1273931
sprint_cik = 101830
sprint_mask = (df['cik'] == sprint_cik) & (df['year'] >= 2020)
if sprint_mask.sum() > 0:
    df.loc[sprint_mask, 'cik'] = tmobile_cik
    print(f"    Recoded {sprint_mask.sum()} observations")

# Collapse to one observation per firm per year
print("\n[2/4] Collapsing to firm-year panel...")
df_panel = df.groupby(['cik', 'year']).agg(
    car_30d=('car_30d', 'mean'),
    fcc_reportable=('fcc_reportable', 'first'),
    firm_size_log=('firm_size_log', 'mean'),
    leverage=('leverage', 'mean'),
    roa=('roa', 'mean'),
    org_name=('org_name', 'first')
).reset_index()

# Drop missing values
df_panel = df_panel.dropna(subset=['car_30d', 'firm_size_log', 'leverage', 'roa'])

# Create treatment_var: 1 for FCC firms in post-2007 periods
df_panel['treatment_var'] = (
    (df_panel['fcc_reportable'] == True) &
    (df_panel['year'] >= 2007)
).astype(int)

print(f"  - Panel observations: {len(df_panel)}")
print(f"  - Treated unit-periods: {df_panel['treatment_var'].sum()}")
print(f"  - Unique FCC firms: {df_panel[df_panel['fcc_reportable']==True]['cik'].nunique()}")
print(f"  - Unique non-FCC firms: {df_panel[df_panel['fcc_reportable']==False]['cik'].nunique()}")
print(f"  - Year range: {df_panel['year'].min()} to {df_panel['year'].max()}")

# Run scdataMulti with correct parameters
print("\n[3/4] Running scdataMulti...")

# Get list of treated CIKs as strings
treated_ciks = df_panel[df_panel['fcc_reportable'] == True]['cik'].unique()
treated_ciks_str = [str(cik) for cik in treated_ciks]

print(f"  - Treated CIKs: {treated_ciks_str}")

# Build features dictionary - same features for all treated units
features_dict = {cik: ['firm_size_log', 'leverage', 'roa'] for cik in treated_ciks_str}

print(f"  - Features dict keys: {list(features_dict.keys())}")

# Also need to convert id_var to string for matching
df_panel['cik'] = df_panel['cik'].astype(str)

try:
    sc_data = scdataMulti(
        df=df_panel,
        id_var='cik',
        time_var='year',
        outcome_var='car_30d',
        treatment_var='treatment_var',
        features=features_dict,
        cointegrated_data=False,
        constant=False,
        verbose=True
    )
    print("✓ scdataMulti completed successfully")
except Exception as e:
    print(f"✗ scdataMulti failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# DIAGNOSTIC: Inspect the internal data structure
print("\n[4A] DIAGNOSTIC: Inspecting scdataMulti output structure...")
print("=" * 80)

print("\nType of sc_data:", type(sc_data))
print("\nAttributes of sc_data:")
attrs = dir(sc_data)
print(attrs)

# Check the key dictionaries
if hasattr(sc_data, 'A'):
    print("\n--- sc_data.A ---")
    print("Type:", type(sc_data.A))
    if isinstance(sc_data.A, dict):
        print("Keys:", list(sc_data.A.keys())[:10])
        first_key = list(sc_data.A.keys())[0]
        print(f"First key: {first_key} (type: {type(first_key)})")
    else:
        print("Not a dict, it's a", type(sc_data.A).__name__)
        if hasattr(sc_data.A, 'index'):
            print("Index/columns:", sc_data.A.index[:5] if hasattr(sc_data.A, 'index') else "N/A")
            print("Columns:", sc_data.A.columns if hasattr(sc_data.A, 'columns') else "N/A")

if hasattr(sc_data, 'treated_units'):
    print("\n--- sc_data.treated_units ---")
    print("Type:", type(sc_data.treated_units))
    print("Value:", sc_data.treated_units)
    if sc_data.treated_units:
        print("First element type:", type(sc_data.treated_units[0]))
        print("First element value:", sc_data.treated_units[0])

if hasattr(sc_data, 'units'):
    print("\n--- sc_data.units ---")
    print("Type:", type(sc_data.units))
    print("First 10:", sc_data.units[:10] if len(sc_data.units) > 10 else sc_data.units)
    if sc_data.units:
        print("First element type:", type(sc_data.units[0]))

if hasattr(sc_data, 'Y'):
    print("\n--- sc_data.Y ---")
    print("Type:", type(sc_data.Y))
    print("Shape:", sc_data.Y.shape if hasattr(sc_data.Y, 'shape') else len(sc_data.Y))

print("\n" + "=" * 80)

# Point estimation
print("\n[4B] Running scest (point estimation)...")
try:
    sc_est = scest(sc_data, w_constr={'name': 'simplex'})
    print("✓ scest completed successfully")
except Exception as e:
    print(f"✗ scest failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Report summary
print("\n" + "=" * 80)
print("RESULTS")
print("=" * 80)

try:
    print("\nEstimation Summary:")
    print(sc_est.summary())
except Exception as e:
    print(f"Summary generation: {e}")
    print(f"\nAvailable attributes: {dir(sc_est)}")

# Save results
print("\n" + "=" * 80)
print("Saving results...")

try:
    # Try to extract results
    if hasattr(sc_est, 'fit_post'):
        results_df = pd.DataFrame({
            'fit_post': sc_est.fit_post,
            'pred_post': sc_est.pred_post if hasattr(sc_est, 'pred_post') else np.nan
        })
    else:
        results_df = pd.DataFrame({
            'attribute': list(dir(sc_est)),
            'value': [str(getattr(sc_est, attr)) for attr in dir(sc_est) if not attr.startswith('_')]
        })

    results_df.to_csv('outputs/scm_scpi_results.csv', index=True)
    print("✓ Results saved to outputs/scm_scpi_results.csv")
except Exception as e:
    print(f"✗ Save failed: {e}")

print("\n" + "=" * 80)
print("COMPLETE")
print("=" * 80)
