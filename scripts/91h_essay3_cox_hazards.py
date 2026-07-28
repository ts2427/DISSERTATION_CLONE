"""
ESSAY 3: COX PROPORTIONAL HAZARDS MODEL
Alternative functional form robustness check for H6

Outcome variable: Time-to-executive-turnover in days, from breach date to first
Item 5.02 filing. Right-censor at 180 days if no turnover.

Treatment variable: fcc_form499 (Form 499 filer registry, same as primary specification)
Controls: firm_size_log, leverage, roa, industry fixed effects (SIC 2-digit)

Fixes relative to prior version:
  - Treatment is fcc_form499 (was fcc_reportable, SIC-based)
  - Event defined as executive_change_180d == 1 (was days_to_first_change.notna(),
    which coded any non-missing day count as an event)
  - Duration uses days_to_first_item_5_02 when available (Item 5.02 measure)
  - Industry FE coarsened to 2-digit SIC with sparse-dummy pruning (<10 obs dropped)
    and ridge penalization (penalizer=0.1) to prevent the singular Hessian that
    crashed the 3-digit specification
  - Schoenfeld test p-value actually computed and reported (was hardcoded 0.05)
"""

import pandas as pd
import numpy as np
import warnings
from pathlib import Path
warnings.filterwarnings('ignore')

print("=" * 90)
print("ESSAY 3: COX PROPORTIONAL HAZARDS ROBUSTNESS CHECK")
print("Alternative functional form: continuous time-to-turnover")
print("=" * 90)

# Load data - Form 499 corrected dataset is primary
DATA_PATH = Path('Data/processed/FINAL_DISSERTATION_DATASET_FORM499_CORRECTED.csv')
if not DATA_PATH.exists():
    raise FileNotFoundError(f"{DATA_PATH} not found - run Form 499 classification chain first (121a-122)")

df = pd.read_csv(DATA_PATH)

if 'fcc_form499' not in df.columns:
    raise ValueError("fcc_form499 not in dataset - treatment variable missing")

# Filter to CRSP sample with turnover data and complete controls
turnover_df = df[
    (df['has_crsp_data'] == 1) &
    (df['executive_change_180d'].notna()) &
    (df['fcc_form499'].notna())
].copy().dropna(subset=['firm_size_log', 'leverage', 'roa'])

# ============================================================================
# EVENT AND DURATION DEFINITION (consistent with primary logistic spec)
# ============================================================================
# Event: executive change within 180 days (Item 5.02 based when merged)
# Duration: days to first Item 5.02 filing if available; censored obs get 180

turnover_df['event'] = (turnover_df['executive_change_180d'] == 1).astype(int)

duration_col_source = None
if 'days_to_first_item_5_02' in turnover_df.columns and turnover_df['days_to_first_item_5_02'].notna().any():
    duration_col_source = 'days_to_first_item_5_02'
elif 'days_to_first_change' in turnover_df.columns:
    duration_col_source = 'days_to_first_change'

turnover_df['time_to_turnover'] = 180.0  # censored default
if duration_col_source is not None:
    has_days = turnover_df[duration_col_source].notna() & (turnover_df['event'] == 1)
    turnover_df.loc[has_days, 'time_to_turnover'] = turnover_df.loc[has_days, duration_col_source]

# Events with missing duration: boundary-code at 180 (kept as events, noted below)
events_missing_duration = int(((turnover_df['event'] == 1) &
                               (turnover_df['time_to_turnover'] >= 180)).sum())

turnover_df['time_to_turnover'] = turnover_df['time_to_turnover'].clip(lower=1, upper=180)

print(f"\n[SAMPLE] {len(turnover_df):,} breaches with complete data")
print(f"[DURATION SOURCE] {duration_col_source}")
print(f"[EVENTS] {turnover_df['event'].sum():,} turnover events ({turnover_df['event'].mean()*100:.1f}%)")
if turnover_df['event'].sum() > 0:
    mean_days = turnover_df.loc[turnover_df['event'] == 1, 'time_to_turnover'].mean()
    print(f"[TIME] Mean days to turnover (events only): {mean_days:.1f}")
print(f"[NOTE] Events boundary-coded at 180d (missing duration): {events_missing_duration}")

# ============================================================================
# COX MODEL - Using lifelines
# ============================================================================

try:
    from lifelines import CoxPHFitter
    from lifelines.statistics import proportional_hazard_test
except ImportError:
    print("\n[ERROR] lifelines not found. Installing...")
    import subprocess
    subprocess.check_call(['pip', 'install', '-q', 'lifelines'])
    from lifelines import CoxPHFitter
    from lifelines.statistics import proportional_hazard_test

print("\n" + "=" * 90)
print("MODEL A: ALL TURNOVER (Voluntary + Forced Combined)")
print("=" * 90)

cox_data = turnover_df[[
    'time_to_turnover', 'event', 'fcc_form499',
    'firm_size_log', 'leverage', 'roa', 'sic'
]].dropna().copy()

cox_data['fcc_form499'] = cox_data['fcc_form499'].astype(int)

# Industry FE: 2-digit SIC (coarser than 3-digit to avoid singular Hessian)
cox_data['sic_2digit'] = (cox_data['sic'] // 100).astype(int).astype(str)

print(f"\nSample: {len(cox_data):,} observations")
print(f"Events: {cox_data['event'].sum():,}")
print(f"Censored: {(1 - cox_data['event']).sum():,}")

industry_dummies = pd.get_dummies(cox_data['sic_2digit'], prefix='sic', drop_first=True).astype(float)

# Prune sparse dummies (<10 obs) - these drive singularity
sparse_cols = [c for c in industry_dummies.columns if industry_dummies[c].sum() < 10]
if sparse_cols:
    industry_dummies = industry_dummies.drop(columns=sparse_cols)
    print(f"Industry FE: {len(industry_dummies.columns)} 2-digit SIC dummies retained "
          f"({len(sparse_cols)} sparse dummies with <10 obs pruned)")

cox_model_data = pd.concat([
    cox_data[['time_to_turnover', 'event', 'fcc_form499', 'firm_size_log', 'leverage', 'roa']].reset_index(drop=True),
    industry_dummies.reset_index(drop=True)
], axis=1)

# Ridge penalization stabilizes the fit against residual collinearity
cph = CoxPHFitter(penalizer=0.1)
cph.fit(cox_model_data,
        duration_col='time_to_turnover',
        event_col='event',
        show_progress=False)

# Extract FCC results
fcc_coef = cph.params_['fcc_form499']
fcc_se = cph.standard_errors_['fcc_form499']
fcc_ci = cph.confidence_intervals_[cph.confidence_intervals_.index == 'fcc_form499']
fcc_p = cph.summary[cph.summary.index == 'fcc_form499']['p'].values[0]
fcc_hr = np.exp(fcc_coef)
fcc_hr_ci_lower = np.exp(fcc_ci.iloc[0, 0])
fcc_hr_ci_upper = np.exp(fcc_ci.iloc[0, 1])

print(f"\nFCC Treatment Effect (Form 499):")
print(f"  Coefficient (log hazard): {fcc_coef:.4f}")
print(f"  Standard Error: {fcc_se:.4f}")
print(f"  p-value: {fcc_p:.4f}")
print(f"  Hazard Ratio: {fcc_hr:.4f}")
print(f"  95% CI for HR: [{fcc_hr_ci_lower:.4f}, {fcc_hr_ci_upper:.4f}]")
print(f"  Interpretation: FCC firms have {(fcc_hr-1)*100:.2f}% change in hazard of turnover")

# Proportional hazards assumption - compute the actual Schoenfeld p for FCC
print(f"\nProportional Hazards Assumption Test (Schoenfeld Residuals):")
ph_assumption_p = np.nan
try:
    ph_test_result = proportional_hazard_test(cph, cox_model_data, time_transform='rank')
    ph_summary = ph_test_result.summary
    if 'fcc_form499' in ph_summary.index:
        ph_assumption_p = float(ph_summary.loc['fcc_form499', 'p'])
        if isinstance(ph_assumption_p, pd.Series):
            ph_assumption_p = float(ph_assumption_p.iloc[0])
    print(f"  Schoenfeld p (fcc_form499): {ph_assumption_p:.4f}")
    if ph_assumption_p < 0.05:
        print(f"  [WARNING] PH assumption violated for FCC (p < 0.05) - "
              f"logistic regression remains primary specification")
    else:
        print(f"  PH assumption not rejected for FCC (p >= 0.05)")
except Exception as e:
    print(f"  Warning: Could not compute Schoenfeld test ({str(e)})")

print(f"\nModel Fit:")
print(f"  Concordance Index: {cph.concordance_index_:.4f}")
print(f"  (0.5 = random; 1.0 = perfect)")

# Save results
cox_results_a = {
    'model': 'All Turnover',
    'treatment': 'fcc_form499',
    'duration_source': duration_col_source,
    'n_obs': len(cox_model_data),
    'n_events': int(cox_model_data['event'].sum()),
    'fcc_coefficient': round(fcc_coef, 4),
    'fcc_se': round(fcc_se, 4),
    'fcc_p_value': round(fcc_p, 4),
    'fcc_hazard_ratio': round(fcc_hr, 4),
    'fcc_hr_ci_lower': round(fcc_hr_ci_lower, 4),
    'fcc_hr_ci_upper': round(fcc_hr_ci_upper, 4),
    'schoenfeld_p_fcc': round(ph_assumption_p, 4) if not np.isnan(ph_assumption_p) else 'NA',
    'concordance_index': round(cph.concordance_index_, 4),
    'penalizer': 0.1,
    'industry_fe': 'SIC 2-digit (sparse pruned)',
}

print("\n" + "=" * 90)
print("MODEL B: FORCED TURNOVER ONLY")
print("=" * 90)
print("\n[NOTE] Forced turnover classification not available in current pipeline.")
print("[NOTE] Model B cannot be estimated without forced/voluntary distinction.")

# ============================================================================
# SAVE RESULTS
# ============================================================================

out_dir = Path('outputs/tables/essay3_governance')
out_dir.mkdir(parents=True, exist_ok=True)

cox_results_df = pd.DataFrame([cox_results_a])
cox_results_df.to_csv(out_dir / 'cox_model_all_turnover.csv', index=False)
print(f"\n[OK] Saved MODEL A results to: {out_dir / 'cox_model_all_turnover.csv'}")

interpretation = f"""====================================================================================================
H6 ROBUSTNESS: COX PROPORTIONAL HAZARDS MODEL
Alternative functional form: continuous time-to-turnover
====================================================================================================

METHODOLOGY:
----------------------------------------------------------------------------------------------------
Outcome: Time from breach date to first Item 5.02 filing (in days), right-censored at 180 days
Duration source: {duration_col_source}
Treatment: fcc_form499 (1 = Form 499 filer at breach date, 0 = others)
Controls: firm_size_log, leverage, roa, industry fixed effects (SIC 2-digit, sparse dummies pruned)
Estimation: Cox PH with ridge penalizer (0.1) for numerical stability
Sample: {len(cox_model_data):,} observations, {int(cox_model_data['event'].sum()):,} events

Contrast with Primary Specification:
  Primary (logistic AME): Binary turnover at fixed windows (30d, 90d, 180d)
  This model (Cox): Continuous time-to-turnover, censored at 180 days
  Purpose: Test whether functional form (binning vs. continuous) masks or reveals effects

====================================================================================================
RESULTS - MODEL A: ALL TURNOVER
====================================================================================================

FCC (Form 499) hazard ratio: {fcc_hr:.4f}  (95% CI [{fcc_hr_ci_lower:.4f}, {fcc_hr_ci_upper:.4f}])
p-value: {fcc_p:.4f}
Schoenfeld PH test p (FCC): {cox_results_a['schoenfeld_p_fcc']}
Concordance index: {cph.concordance_index_:.4f}

INTERPRETATION:
{'FCC regulation does not significantly change the hazard of executive turnover.' if fcc_p >= 0.05 else 'FCC regulation significantly changes the hazard of executive turnover.'}
{'PH assumption violated for FCC - treat Cox as descriptive; logistic regression is the primary specification.' if (not np.isnan(ph_assumption_p) and ph_assumption_p < 0.05) else ''}

MODEL B (Forced turnover only): Not estimable - succession type not classifiable in pipeline.
====================================================================================================
"""

with open(out_dir / 'H6_Cox_Model_Results.txt', 'w', encoding='utf-8') as f:
    f.write(interpretation)
print(f"[OK] Saved interpretation to: {out_dir / 'H6_Cox_Model_Results.txt'}")

print("\n" + "=" * 90)
print("[COMPLETE] COX PROPORTIONAL HAZARDS ROBUSTNESS CHECK")
print("=" * 90)
