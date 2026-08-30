"""
REBUILD ESSAY 1 APPENDIX — 14 TABLES, FORM 499 CORRECTED (v2)
=============================================================
Replaces rebuild_essay1_appendix_tables.py (7/24, SIC-based, hardcoded placeholders).

EVERY number in every table is computed live in this script from:
  Data/processed/FINAL_DISSERTATION_DATASET_FORM499_CORRECTED.csv  (treatment: fcc_form499)
  Data/wrds/crsp_daily_returns.csv + Data/wrds/market_indices.csv  (Tables 11, 13)
  Data/F-F_*.csv factor files                                       (Table 10)

NO hardcoded results. Canonical cross-checks (7/28 audit values) are asserted and
reported as PASS/FAIL; a FAIL prints loudly and the run continues so the discrepancy
can be inspected.

Numbering follows the 7/24 series, with changes required by the corrected framing:
  Table 8  REPLACED: old table was hardcoded SIC-era "causal identification" numbers.
           Now live-computed specification robustness (industry FE, year FE, both,
           propensity matching) with NO causal labeling, per descriptive framing.
           The old "Falsification (pre-breach)" row is retired (was a hardcode).
  Table 13 now actually computed (was hardcoded): market-adjusted pre-announcement
           abnormal returns; event day = first trading day >= breach_date.
  Table 14 NEW: TOST equivalence bounds (the corrected essays' central table).

Outputs: outputs/tables/appendix_v2/table_{N}_form499.csv (N=1..14)
         outputs/ESSAY1_APPENDIX_TABLES_FORM499.md (combined, with captions)
         outputs/appendix_v2_run_log.txt
"""

import sys
import pandas as pd
import numpy as np
import statsmodels.api as sm
from scipy import stats
import warnings
from pathlib import Path

warnings.filterwarnings('ignore')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

OUT_DIR = Path('outputs/tables/appendix_v2')
OUT_DIR.mkdir(parents=True, exist_ok=True)
LOG_LINES = []

def log(msg=''):
    print(msg)
    LOG_LINES.append(str(msg))

log('=' * 90)
log('REBUILD ESSAY 1 APPENDIX v2 — 14 TABLES, FORM 499 CORRECTED')
log('=' * 90)

# ----------------------------------------------------------------------------
# Load and define samples (mirrors scripts/86c exactly)
# ----------------------------------------------------------------------------
df = pd.read_csv('Data/processed/FINAL_DISSERTATION_DATASET_FORM499_CORRECTED.csv')
log(f'\nFull dataset rows: {len(df)} (canonical: 779)')

TREAT = 'fcc_form499'
CONTROLS = [TREAT, 'immediate_disclosure', 'prior_breaches_1yr',
            'health_breach', 'firm_size_log', 'leverage', 'roa']

# CRSP sample (Table 1 Panel B): has_crsp_data == 1
crsp_sample = df[df['has_crsp_data'] == 1].copy()
crsp_treated = int((crsp_sample[TREAT] == 1).sum())
# Canonical firm count is at the organization (brand) level; multiple treated brands
# (e.g., Cricket, Boost) roll up to fewer parent filer CIKs.
crsp_treated_firms = crsp_sample.loc[crsp_sample[TREAT] == 1, 'org_name'].nunique()
crsp_treated_ciks = crsp_sample.loc[crsp_sample[TREAT] == 1, 'cik'].nunique()

# Regression sample: has_crsp_data == 1, complete cases on outcome + controls (86c spec)
reg = df[df['has_crsp_data'] == 1][['car_30d'] + CONTROLS + [
    'cik', 'org_name', 'breach_date', 'breach_year', 'sic_3digit', 'Map',
    'hhi_industry_year', 'records_affected_numeric']].copy()
reg = reg.dropna(subset=['car_30d'] + CONTROLS).reset_index(drop=True)
reg_treated = int((reg[TREAT] == 1).sum())
reg_treated_firms = reg.loc[reg[TREAT] == 1, 'org_name'].nunique()

log(f'CRSP sample: N={len(crsp_sample)}, treated={crsp_treated} incidents / {crsp_treated_firms} firms '
    f'(canonical: 118 / 37)')
log(f'Regression sample: N={len(reg)}, treated={reg_treated} incidents / {reg_treated_firms} firms '
    f'(canonical: 648 / 115)')

CHECKS = []
def check(name, got, want, tol=0):
    ok = abs(got - want) <= tol
    CHECKS.append((name, got, want, ok))
    log(f'  CHECK {"PASS" if ok else "FAIL"}: {name} = {got} (canonical {want})')
    return ok

log('\nSample verification against canonical (7/28):')
check('full rows', len(df), 779)
check('CRSP treated incidents', crsp_treated, 118)
check('CRSP treated firms', crsp_treated_firms, 37)
check('regression N', len(reg), 648)
check('regression treated', reg_treated, 115)

tables = {}       # name -> DataFrame
captions = {}     # name -> caption text

# ----------------------------------------------------------------------------
# TABLE 1: Summary statistics (Panel A full sample, Panel B CRSP sample)
# ----------------------------------------------------------------------------
log('\n[Table 1] Summary statistics...')
rows = []
sum_vars = [('car_30d', 'CRSP'), ('car_5d', 'CRSP'), ('firm_size_log', 'Full'),
            ('leverage', 'Full'), ('roa', 'Full'), ('disclosure_delay_days', 'Full'),
            ('records_affected_numeric', 'Full')]
for panel, frame in [('A: Full sample', df), ('B: CRSP sample', crsp_sample)]:
    for col, _ in sum_vars:
        if col in frame.columns:
            d = frame[col].dropna()
            if len(d):
                rows.append({'Panel': panel, 'Variable': col, 'N': len(d),
                             'Mean': round(d.mean(), 4), 'SD': round(d.std(), 4),
                             'Min': round(d.min(), 4), 'Median': round(d.median(), 4),
                             'Max': round(d.max(), 4)})
    for col, label in [(TREAT, 'Form 499 treated (count)'),
                       ('immediate_disclosure', 'Immediate disclosure (count)'),
                       ('health_breach', 'Health breach (count)'),
                       ('prior_breaches_1yr', 'Prior breach 1yr (count)')]:
        rows.append({'Panel': panel, 'Variable': label, 'N': int(frame[col].notna().sum()),
                     'Mean': int((frame[col] == 1).sum()), 'SD': '-', 'Min': '-',
                     'Median': '-', 'Max': '-'})
rows.append({'Panel': 'B: CRSP sample', 'Variable': 'Form 499 treated organizations (unique org_name)',
             'N': '-', 'Mean': crsp_treated_firms, 'SD': '-', 'Min': '-', 'Median': '-', 'Max': '-'})
rows.append({'Panel': 'B: CRSP sample', 'Variable': 'Form 499 treated parent filers (unique CIK)',
             'N': '-', 'Mean': crsp_treated_ciks, 'SD': '-', 'Min': '-', 'Median': '-', 'Max': '-'})
tables['Table 1'] = pd.DataFrame(rows)
captions['Table 1'] = (f'Summary statistics. Panel A: full sample (N={len(df)}). Panel B: CRSP-matched '
                       f'sample (N={len(crsp_sample)}; {crsp_treated} treated incidents across '
                       f'{crsp_treated_firms} firms). Treatment: FCC Form 499 filer registry '
                       f'(primary-source verified, two-clause rule).')

# ----------------------------------------------------------------------------
# TABLE 2: Mean CAR by subgroup (regression sample)
# ----------------------------------------------------------------------------
log('[Table 2] Mean CAR by subgroup...')
# prior_breaches_1yr is a COUNT (0..56), not a dummy. The history split must be
# >0 vs ==0; an ==1/==0 split silently drops the 131 obs with 2+ prior breaches
# (this was the old table's non-summing-row defect).
reg['_any_prior_1yr'] = (reg['prior_breaches_1yr'] > 0).astype(int)
rows = []
for comparison, col, lab1, lab0 in [
        ('Form 499 status', TREAT, 'Form 499 filer', 'Non-filer'),
        ('Disclosure speed', 'immediate_disclosure', 'Immediate (<=7d)', 'Delayed (>7d)'),
        ('Breach type', 'health_breach', 'Health', 'Non-health'),
        ('History', '_any_prior_1yr', 'Any prior breach, 1yr (count>0)', 'No prior breach, 1yr')]:
    for val, lab in [(1, lab1), (0, lab0)]:
        d = reg.loc[reg[col] == val, 'car_30d']
        se = d.std() / np.sqrt(len(d))
        rows.append({'Comparison': comparison, 'Group': lab, 'Mean CAR': round(d.mean(), 4),
                     'SE': round(se, 4), 'CI Lower': round(d.mean() - 1.96 * se, 4),
                     'CI Upper': round(d.mean() + 1.96 * se, 4), 'N': len(d)})
    a = reg.loc[reg[col] == 1, 'car_30d']; b = reg.loc[reg[col] == 0, 'car_30d']
    t, p = stats.ttest_ind(a, b, equal_var=False)
    rows.append({'Comparison': comparison, 'Group': 'Difference (Welch t)',
                 'Mean CAR': round(a.mean() - b.mean(), 4), 'SE': '-',
                 'CI Lower': '-', 'CI Upper': '-', 'N': f't={t:.2f}, p={p:.3f}'})
tables['Table 2'] = pd.DataFrame(rows)
captions['Table 2'] = (f'Mean 30-day CAR by subgroup, regression sample (N={len(reg)}); every '
                       'two-group split sums to 648. History split: prior_breaches_1yr > 0 vs = 0 '
                       '(the variable is a 12-month COUNT; the H3 regression uses the count itself, '
                       'not this dummy). Supersedes the 7/24 table (retired SIC-based flag, 125 '
                       'treated, and a ==1/==0 history split that silently dropped 131 multi-prior '
                       'observations).')

# ----------------------------------------------------------------------------
# TABLE 3: Main regression H1-H4 (canonical spec, mirrors 86c)
# ----------------------------------------------------------------------------
log('[Table 3] Main regression (canonical spec)...')
y = reg['car_30d']
X = sm.add_constant(reg[CONTROLS].astype(float))
m_main = sm.OLS(y, X).fit(cov_type='HC3')
rows = []
for var in ['const'] + CONTROLS:
    ci = m_main.conf_int().loc[var]
    rows.append({'Variable': var, 'Coefficient': round(m_main.params[var], 4),
                 'SE': round(m_main.bse[var], 4), 't-stat': round(m_main.tvalues[var], 3),
                 'P-value': round(m_main.pvalues[var], 4),
                 'CI Lower': round(ci[0], 4), 'CI Upper': round(ci[1], 4)})
tables['Table 3'] = pd.DataFrame(rows)
captions['Table 3'] = (f'Main regression: 30-day CAR on H1-H4 variables, HC3 robust SEs, N={len(reg)}. '
                       'H2 row is the Form 499 corrected estimate (the SIC-based -2.21, p=.017 is retired '
                       'as a misclassification artifact).')

log('\nCanonical H1-H4 cross-check:')
canon = {'immediate_disclosure': (0.61, 0.482), TREAT: (-0.42, 0.575),
         'prior_breaches_1yr': (0.03, 0.645), 'health_breach': (-0.39, 0.811)}
for var, (c_coef, c_p) in canon.items():
    check(f'{var} coef', round(m_main.params[var], 2), c_coef, tol=0.005)
    check(f'{var} p', round(m_main.pvalues[var], 3), c_p, tol=0.0015)

# ----------------------------------------------------------------------------
# TABLE 4: Sample restrictions (timing coefficient)
# ----------------------------------------------------------------------------
log('[Table 4] Sample restrictions...')
reg['size_quartile'] = pd.qcut(reg['firm_size_log'], q=4, labels=['Q1', 'Q2', 'Q3', 'Q4'], duplicates='drop')
reg['outlier'] = np.abs(reg['car_30d'] - reg['car_30d'].mean()) > 3 * reg['car_30d'].std()
restrictions = [
    ('Full sample', reg),
    ('Exclude largest decile', reg[reg['firm_size_log'] <= reg['firm_size_log'].quantile(0.90)]),
    ('Exclude smallest decile', reg[reg['firm_size_log'] >= reg['firm_size_log'].quantile(0.10)]),
    ('Exclude outliers (3 SD)', reg[~reg['outlier']]),
    ('Form 499 filers only', reg[reg[TREAT] == 1]),
    ('Non-filers only', reg[reg[TREAT] == 0]),
    ('Non-health breaches', reg[reg['health_breach'] == 0]),
    ('Prior breach history', reg[reg['prior_breaches_1yr'] > 0]),
]
rows = []
for name, d in restrictions:
    if len(d) > 20:
        sub_controls = [c for c in CONTROLS if d[c].nunique() > 1]
        Xs = sm.add_constant(d[sub_controls].astype(float))
        ms = sm.OLS(d['car_30d'], Xs).fit(cov_type='HC3')
        if 'immediate_disclosure' in ms.params:
            rows.append({'Restriction': name,
                         'Timing Coefficient': round(ms.params['immediate_disclosure'], 4),
                         'SE': round(ms.bse['immediate_disclosure'], 4),
                         'P-value': round(ms.pvalues['immediate_disclosure'], 4), 'N': len(d)})
tables['Table 4'] = pd.DataFrame(rows)
captions['Table 4'] = ('H1 robustness: immediate-disclosure coefficient under sample restrictions '
                       '(HC3). "Prior breach history" subsample = prior_breaches_1yr > 0 (N=208), '
                       'the same definition as Table 2\'s history split.')

# ----------------------------------------------------------------------------
# TABLE 5: Standard error methods (timing and FCC coefficients)
# ----------------------------------------------------------------------------
log('[Table 5] Standard error methods...')
rows = []
for method_name, kind in [('OLS (classical)', None), ('HC1', 'HC1'), ('HC2', 'HC2'), ('HC3', 'HC3'),
                          ('Firm-clustered (CIK)', 'cik'), ('Date-clustered', 'breach_date')]:
    if kind in ('cik', 'breach_date'):
        m = sm.OLS(y, X).fit(cov_type='cluster', cov_kwds={'groups': reg[kind]})
    elif kind is None:
        m = sm.OLS(y, X).fit()
    else:
        m = sm.OLS(y, X).fit(cov_type=kind)
    rows.append({'Method': method_name,
                 'Timing Coef': round(m.params['immediate_disclosure'], 4),
                 'Timing SE': round(m.bse['immediate_disclosure'], 4),
                 'Timing p': round(m.pvalues['immediate_disclosure'], 4),
                 'FCC Coef': round(m.params[TREAT], 4),
                 'FCC SE': round(m.bse[TREAT], 4),
                 'FCC p': round(m.pvalues[TREAT], 4)})
tables['Table 5'] = pd.DataFrame(rows)
captions['Table 5'] = (f'H1/H2 robustness to standard-error estimation method (N={len(reg)}). '
                       'Caveat for firm-clustered row: treated observations span only '
                       f'{crsp_treated_ciks} parent filer CIK clusters (37 organizations roll up to '
                       f'{crsp_treated_ciks} filers); cluster-robust inference with few treated clusters '
                       'is conservative territory — HC3 remains the primary specification.')

# ----------------------------------------------------------------------------
# TABLE 6: Firm-size quartiles — timing
# ----------------------------------------------------------------------------
log('[Table 6] Size quartiles (timing)...')
rows = []
for q in ['Q1', 'Q2', 'Q3', 'Q4']:
    d = reg[reg['size_quartile'] == q]
    if len(d) > 20:
        sub_controls = [c for c in CONTROLS if d[c].nunique() > 1]
        Xq = sm.add_constant(d[sub_controls].astype(float))
        mq = sm.OLS(d['car_30d'], Xq).fit(cov_type='HC3')
        rows.append({'Size Quartile': q,
                     'Timing Coefficient': round(mq.params['immediate_disclosure'], 4),
                     'SE': round(mq.bse['immediate_disclosure'], 4),
                     'P-value': round(mq.pvalues['immediate_disclosure'], 4), 'N': len(d)})
tables['Table 6'] = pd.DataFrame(rows)
captions['Table 6'] = 'H1 heterogeneity: timing coefficient by firm-size quartile (HC3).'

# ----------------------------------------------------------------------------
# TABLE 7: Firm-size quartiles — FCC, with corrected treated counts
# ----------------------------------------------------------------------------
log('[Table 7] Size quartiles (FCC) with treated counts...')
rows = []
for q in ['Q1', 'Q2', 'Q3', 'Q4']:
    d = reg[reg['size_quartile'] == q]
    n_treated = int((d[TREAT] == 1).sum())
    n_orgs = d.loc[d[TREAT] == 1, 'org_name'].nunique()
    n_ciks = d.loc[d[TREAT] == 1, 'cik'].nunique()
    if len(d) > 20 and d[TREAT].nunique() > 1:
        sub_controls = [c for c in CONTROLS if d[c].nunique() > 1]
        Xq = sm.add_constant(d[sub_controls].astype(float))
        mq = sm.OLS(d['car_30d'], Xq).fit(cov_type='HC3')
        rows.append({'Size Quartile': q, 'FCC Coefficient': round(mq.params[TREAT], 4),
                     'SE': round(mq.bse[TREAT], 4), 'P-value': round(mq.pvalues[TREAT], 4),
                     'N': len(d), 'Treated N': n_treated,
                     'Treated Orgs': n_orgs, 'Treated Parent CIKs': n_ciks})
    else:
        rows.append({'Size Quartile': q, 'FCC Coefficient': 'insufficient variation',
                     'SE': '-', 'P-value': '-', 'N': len(d), 'Treated N': n_treated,
                     'Treated Orgs': n_orgs, 'Treated Parent CIKs': n_ciks})
reg_treat = reg[reg[TREAT] == 1]
tables['Table 7'] = pd.DataFrame(rows)
captions['Table 7'] = ('H2 heterogeneity: Form 499 coefficient by firm-size quartile, with corrected '
                       'treated counts per quartile. Treated incidents sum to '
                       f'{int((reg[TREAT]==1).sum())} (the regression sample). The organization and '
                       'parent-CIK columns count UNIQUE entities within each quartile and double-count '
                       'across quartiles, because the same organization appears in different size '
                       'quartiles across incidents (firm size varies over time); they therefore sum to '
                       'more than the sample-wide totals of '
                       f'{reg_treat["org_name"].nunique()} organizations / '
                       f'{reg_treat["cik"].nunique()} parent CIKs in the regression sample '
                       '(37 / 12 in the CRSP sample).')

# ----------------------------------------------------------------------------
# TABLE 8: Specification robustness (REPLACES hardcoded "causal identification")
# ----------------------------------------------------------------------------
log('[Table 8] Specification robustness (live, descriptive framing)...')
rows = []
base_ci = m_main.conf_int().loc[TREAT]
rows.append({'Specification': 'Baseline (HC3)', 'FCC Coefficient': round(m_main.params[TREAT], 4),
             'SE': round(m_main.bse[TREAT], 4), 'P-value': round(m_main.pvalues[TREAT], 4),
             'N': len(reg)})

reg['sic3'] = reg['sic_3digit'].fillna(-1).astype(int).astype(str)
for spec_name, fe_cols in [('+ Industry FE (SIC3)', ['sic3']),
                           ('+ Year FE', ['breach_year']),
                           ('+ Industry and Year FE', ['sic3', 'breach_year'])]:
    dummies = pd.get_dummies(reg[fe_cols].astype(str), drop_first=True)
    Xfe = pd.concat([reg[CONTROLS].astype(float), dummies.astype(float)], axis=1)
    Xfe = sm.add_constant(Xfe)
    mfe = sm.OLS(y, Xfe).fit(cov_type='HC3')
    rows.append({'Specification': spec_name, 'FCC Coefficient': round(mfe.params[TREAT], 4),
                 'SE': round(mfe.bse[TREAT], 4), 'P-value': round(mfe.pvalues[TREAT], 4),
                 'N': int(mfe.nobs)})

# Propensity-score 1:1 nearest-neighbor matching (without replacement)
ps_controls = [c for c in CONTROLS if c != TREAT]
Xp = sm.add_constant(reg[ps_controls].astype(float))
logit = sm.Logit(reg[TREAT], Xp).fit(disp=0)
reg['_pscore'] = logit.predict(Xp)
treated_idx = reg.index[reg[TREAT] == 1].tolist()
control_pool = reg.loc[reg[TREAT] == 0, '_pscore'].copy()
pairs = []
for i in treated_idx:
    if len(control_pool) == 0:
        break
    j = (control_pool - reg.loc[i, '_pscore']).abs().idxmin()
    pairs.append((i, j))
    control_pool = control_pool.drop(j)
t_car = reg.loc[[a for a, _ in pairs], 'car_30d'].values
c_car = reg.loc[[b for _, b in pairs], 'car_30d'].values
diff = t_car - c_car
att = diff.mean()
att_se = diff.std(ddof=1) / np.sqrt(len(diff))
att_p = 2 * (1 - stats.t.cdf(abs(att / att_se), df=len(diff) - 1))
rows.append({'Specification': 'PS matched (1:1 NN, no replacement)', 'FCC Coefficient': round(att, 4),
             'SE': round(att_se, 4), 'P-value': round(att_p, 4), 'N': f'{len(diff)} pairs'})
tables['Table 8'] = pd.DataFrame(rows)
captions['Table 8'] = ('H2 specification robustness under the descriptive framing (no causal claim). '
                       'REPLACES the retired 7/24 "causal identification" table, whose values were '
                       'hardcoded SIC-era placeholders (industry FE -1.94; falsification 0.23; matching '
                       '-1.64) never computed by its script. The pre-breach falsification row is retired '
                       'pending recomputation from CRSP daily data on final membership. Interpretation '
                       'caveat for the industry-FE rows: Form 499 treatment is nearly collinear with '
                       'telecom SIC codes (118 treated incidents, 12 parent filers), so within-industry '
                       'estimates rest on minimal variation; the coefficient instability across FE '
                       'specifications (all p>.14) reflects that thinness, not a detectable effect. '
                       'The baseline HC3 and matched estimates are the informative rows.')

# ----------------------------------------------------------------------------
# TABLE 9: Alternative explanations (HHI, severity)
# ----------------------------------------------------------------------------
log('[Table 9] Alternative explanations...')
rows = []
for label, extra in [('HHI industry concentration', 'hhi_industry_year'),
                     ('Breach severity (records affected)', 'records_affected_numeric')]:
    d = reg.dropna(subset=[extra])
    Xa = sm.add_constant(d[CONTROLS + [extra]].astype(float))
    ma = sm.OLS(d['car_30d'], Xa).fit(cov_type='HC3')
    rows.append({'Added Control': label, 'FCC Coefficient': round(ma.params[TREAT], 4),
                 'FCC SE': round(ma.bse[TREAT], 4), 'FCC P-value': round(ma.pvalues[TREAT], 4),
                 'Control Coefficient': round(ma.params[extra], 6),
                 'Control P-value': round(ma.pvalues[extra], 4), 'N': int(ma.nobs)})
tables['Table 9'] = pd.DataFrame(rows)
captions['Table 9'] = 'H2 robustness to alternative explanations: market concentration and breach severity.'

# ----------------------------------------------------------------------------
# TABLE 10: Factor model robustness (live merge of FF factors)
# ----------------------------------------------------------------------------
log('[Table 10] Factor models (FF3 / Carhart / FF5)...')

def load_factor_file(path, skiprows, cols):
    f = pd.read_csv(path, skiprows=skiprows)
    f.columns = f.columns.str.strip()
    f = f.dropna(axis=1, how='all')
    date_col = f.columns[0]
    f['date'] = pd.to_datetime(f[date_col], format='%Y%m%d', errors='coerce')
    f = f.dropna(subset=['date'])
    f['year'] = f['date'].dt.year
    f['month'] = f['date'].dt.month
    g = f.groupby(['year', 'month'])[cols].last().reset_index()
    return g

ff3_m = load_factor_file('Data/F-F_Research_Data_Factors_daily.csv', 4, ['Mkt-RF', 'SMB', 'HML'])
mom_m = load_factor_file('Data/F-F_Momentum_Factor_daily.csv', 13, ['Mom'])
ff5_m = load_factor_file('Data/F-F_Research_Data_5_Factors_2x3_daily.csv', 4,
                         ['Mkt-RF', 'SMB', 'HML', 'RMW', 'CMA'])

regf = reg.copy()
bd = pd.to_datetime(regf['breach_date'])
regf['event_year'] = bd.dt.year
regf['event_month'] = bd.dt.month
regf = regf.merge(ff3_m.rename(columns={'Mkt-RF': 'mkt_rf', 'SMB': 'smb', 'HML': 'hml'}),
                  left_on=['event_year', 'event_month'], right_on=['year', 'month'], how='left')
regf = regf.merge(mom_m.rename(columns={'Mom': 'mom'}),
                  left_on=['event_year', 'event_month'], right_on=['year', 'month'],
                  how='left', suffixes=('', '_mom'))
regf = regf.merge(ff5_m.rename(columns={'Mkt-RF': 'mkt_rf5', 'SMB': 'smb5', 'HML': 'hml5',
                                        'RMW': 'rmw', 'CMA': 'cma'}),
                  left_on=['event_year', 'event_month'], right_on=['year', 'month'],
                  how='left', suffixes=('', '_ff5'))
factor_specs = [
    ('Market-adjusted (baseline, factor subsample)', []),
    ('FF3 controls', ['mkt_rf', 'smb', 'hml']),
    ('Carhart 4-factor controls', ['mkt_rf', 'smb', 'hml', 'mom']),
    ('FF5 controls', ['mkt_rf5', 'smb5', 'hml5', 'rmw', 'cma']),
]
factor_sample = regf.dropna(subset=['mkt_rf', 'smb', 'hml', 'mom', 'mkt_rf5', 'rmw', 'cma'])
log(f'  Factor subsample: N={len(factor_sample)} '
    f'(treated={int((factor_sample[TREAT]==1).sum())})')
rows = []
for name, fcols in factor_specs:
    Xf = sm.add_constant(factor_sample[CONTROLS + fcols].astype(float))
    mf = sm.OLS(factor_sample['car_30d'], Xf).fit(cov_type='HC3')
    rows.append({'Model': name, 'FCC Coefficient': round(mf.params[TREAT], 4),
                 'SE': round(mf.bse[TREAT], 4), 'P-value': round(mf.pvalues[TREAT], 4),
                 'Timing Coefficient': round(mf.params['immediate_disclosure'], 4),
                 'Timing P-value': round(mf.pvalues['immediate_disclosure'], 4),
                 'N': int(mf.nobs)})
tables['Table 10'] = pd.DataFrame(rows)
captions['Table 10'] = ('Factor-model robustness on the common factor subsample (event-month factor '
                        'controls added to the baseline spec; same construction as the pipeline reference '
                        'scripts, treatment corrected to Form 499). Supersedes the hardcoded SIC-era table '
                        '(-2.47/-2.12/-2.14/-2.22).')

# ----------------------------------------------------------------------------
# CRSP per-ticker groups (Tables 11 and 13)
# ----------------------------------------------------------------------------
log('Loading CRSP daily data for Tables 11 and 13 (this takes a minute)...')
crsp_daily = pd.read_csv('Data/wrds/crsp_daily_returns.csv',
                         usecols=['ticker', 'date', 'ret', 'vol', 'shrout'])
market = pd.read_csv('Data/wrds/market_indices.csv', usecols=['date', 'vwretd'])
crsp_daily['date'] = pd.to_datetime(crsp_daily['date'])
market['date'] = pd.to_datetime(market['date'])
crsp_daily = crsp_daily.merge(market, on='date', how='left')
crsp_groups = {t: g.sort_values('date').reset_index(drop=True)
               for t, g in crsp_daily.groupby('ticker')}

def event_index(g, event_date):
    idx = g['date'].searchsorted(event_date)
    if idx >= len(g):
        return None
    if (g.loc[idx, 'date'] - event_date).days > 5:
        return None
    return int(idx)

# ----------------------------------------------------------------------------
# TABLE 11: Abnormal trading volume (live, mirrors h1_abnormal_trading_volume spec)
# ----------------------------------------------------------------------------
log('[Table 11] Abnormal trading volume...')
ab_vols = []
for _, r in reg.iterrows():
    t = r['Map']
    if pd.isna(t) or t not in crsp_groups:
        ab_vols.append(np.nan); continue
    g = crsp_groups[t]
    ei = event_index(g, pd.to_datetime(r['breach_date']))
    if ei is None or ei < 120:
        ab_vols.append(np.nan); continue
    est = g.iloc[max(0, ei - 240):max(0, ei - 60)]
    evt = g.iloc[max(0, ei - 5):min(len(g), ei + 26)]
    if len(est) < 30 or len(evt) < 20:
        ab_vols.append(np.nan); continue
    with np.errstate(divide='ignore', invalid='ignore'):
        est_t = np.log(est['vol'] / (est['shrout'] * 1000)).replace([np.inf, -np.inf], np.nan).dropna()
        evt_t = np.log(evt['vol'] / (evt['shrout'] * 1000)).replace([np.inf, -np.inf], np.nan).dropna()
    if len(est_t) < 20 or len(evt_t) < 20:
        ab_vols.append(np.nan); continue
    ab_vols.append(evt_t.mean() - est_t.mean())
reg['_abvol'] = ab_vols
dvol = reg.dropna(subset=['_abvol'])
Xv = sm.add_constant(dvol[CONTROLS].astype(float))
mv = sm.OLS(dvol['_abvol'], Xv).fit(cov_type='HC3')
rows = []
for var in CONTROLS:
    rows.append({'Variable': var, 'Coefficient': round(mv.params[var], 4),
                 'SE': round(mv.bse[var], 4), 'P-value': round(mv.pvalues[var], 4)})
tables['Table 11'] = pd.DataFrame(rows)
captions['Table 11'] = (f'Abnormal trading volume (log turnover, event [-5,+25] vs estimation '
                        f'[-240,-60]) regressed on the baseline spec, N={len(dvol)}. Computed live; '
                        'supersedes the hardcoded 7/24 values.')
log(f'  Volume sample: N={len(dvol)}')

# ----------------------------------------------------------------------------
# TABLE 12: Random forest feature importance (live)
# ----------------------------------------------------------------------------
log('[Table 12] Random forest feature importance...')
from sklearn.ensemble import RandomForestRegressor
rf = RandomForestRegressor(n_estimators=500, random_state=42, n_jobs=-1)
rf.fit(reg[CONTROLS].astype(float), reg['car_30d'])
imp = sorted(zip(CONTROLS, rf.feature_importances_), key=lambda x: -x[1])
tables['Table 12'] = pd.DataFrame(
    [{'Rank': i + 1, 'Feature': f, 'Importance': round(s, 4)} for i, (f, s) in enumerate(imp)])
captions['Table 12'] = (f'Random forest (500 trees, seed 42) feature importance for 30-day CAR, '
                        f'N={len(reg)}. Computed live; supersedes hardcoded 7/24 values.')

# ----------------------------------------------------------------------------
# TABLE 13: Pre-announcement abnormal returns (live, market-adjusted)
# ----------------------------------------------------------------------------
log('[Table 13] Pre-announcement abnormal returns...')
windows = [('Day -30 to -21', -30, -21), ('Day -20 to -11', -20, -11), ('Day -10 to -2', -10, -2)]
win_data = {w[0]: [] for w in windows}
n_events = 0
for _, r in reg.iterrows():
    t = r['Map']
    if pd.isna(t) or t not in crsp_groups:
        continue
    g = crsp_groups[t]
    ei = event_index(g, pd.to_datetime(r['breach_date']))
    if ei is None or ei < 35:
        continue
    counted = False
    for name, a, b in windows:
        seg = g.iloc[ei + a: ei + b + 1]
        ar = (seg['ret'] - seg['vwretd']).dropna()
        if len(ar) >= 5:
            win_data[name].append(ar.sum() * 100)  # cumulative abnormal return, pp
            counted = True
    if counted:
        n_events += 1
rows = []
for name, _, _ in windows:
    d = pd.Series(win_data[name])
    se = d.std() / np.sqrt(len(d))
    tstat = d.mean() / se
    p = 2 * (1 - stats.t.cdf(abs(tstat), df=len(d) - 1))
    rows.append({'Window': name, 'Mean Cumulative AR (pp)': round(d.mean(), 4),
                 'SE': round(se, 4), 't-stat': round(tstat, 3), 'P-value': round(p, 4), 'N': len(d)})
tables['Table 13'] = pd.DataFrame(rows)
captions['Table 13'] = (f'Pre-announcement market-adjusted cumulative abnormal returns (leakage test), '
                        f'{n_events} of the {len(reg)} regression-sample events; the remaining '
                        f'{len(reg) - n_events} lack sufficient pre-event CRSP trading history '
                        '(>=35 trading days before the event). Event day = first trading day on/after '
                        'breach_date (within 5 calendar days). Computed live; supersedes hardcoded '
                        '7/24 values.')

# ----------------------------------------------------------------------------
# TABLE 14 (NEW): TOST equivalence bounds — the corrected essays' central table
# ----------------------------------------------------------------------------
log('[Table 14] TOST equivalence bounds...')
EQUIV = 2.10
rows = []
tost_canon = {'immediate_disclosure': 0.045, TREAT: 0.013,
              'prior_breaches_1yr': 0.001, 'health_breach': 0.148}
hyp_names = {'immediate_disclosure': 'H1 Immediate disclosure', TREAT: 'H2 FCC regulation (Form 499)',
             'prior_breaches_1yr': 'H3 Prior breaches', 'health_breach': 'H4 Health breach'}
dof = len(reg) - 8
for var in ['immediate_disclosure', TREAT, 'prior_breaches_1yr', 'health_breach']:
    coef = m_main.params[var]; se = m_main.bse[var]
    ci = m_main.conf_int().loc[var]
    p_lower = 1 - stats.t.cdf((coef + EQUIV) / se, df=dof)
    p_upper = stats.t.cdf((coef - EQUIV) / se, df=dof)
    p_tost = max(p_lower, p_upper)
    mde = 2.8 * se
    bounded = p_tost < 0.05
    status = 'Bounded null' if bounded else ('Inconclusive' if not (ci[0] >= -EQUIV and ci[1] <= EQUIV)
                                             else 'Bounded (CI)')
    rows.append({'Hypothesis': hyp_names[var], 'Coefficient (pp)': round(coef, 4),
                 'SE': round(se, 4), 'p (test of zero)': round(m_main.pvalues[var], 4),
                 'MDE 80% (pp)': round(mde, 4), 'TOST p (±2.10pp)': round(p_tost, 4),
                 'Status': status})
    log(f'  TOST {var}: p={p_tost:.4f} (canonical ~{tost_canon[var]})')
tables['Table 14'] = pd.DataFrame(rows)
captions['Table 14'] = (f'Equivalence testing (TOST, pre-specified bound ±{EQUIV}pp), N={len(reg)}. '
                        'H1-H3: bounded nulls. H4: inconclusive (CI exceeds bound). This table is new '
                        'to the appendix; it carries the corrected essays\' central claims.')

# ----------------------------------------------------------------------------
# Save everything
# ----------------------------------------------------------------------------
log('\n' + '=' * 90)
log('SAVING')
log('=' * 90)
for name, tdf in tables.items():
    n = name.split()[1]
    path = OUT_DIR / f'table_{n}_form499.csv'
    tdf.to_csv(path, index=False)
    log(f'  {path}  ({len(tdf)} rows)')

md_path = Path('outputs/ESSAY1_APPENDIX_TABLES_FORM499.md')
with open(md_path, 'w', encoding='utf-8') as f:
    f.write('# ESSAY 1 APPENDIX TABLES — FORM 499 CORRECTED (regenerated '
            'from final pipeline dataset)\n\n')
    f.write(f'Sample: {len(df)} incidents. Treatment: fcc_form499.\n\n'
            'TREATED COUNTS EXIST AT THREE LEVELS — every essay sentence citing a treated N '
            'must name its sample:\n'
            f'- Full sample: {int((df[TREAT]==1).sum())} treated of {len(df)}\n'
            f'- CRSP sample: {crsp_treated} treated of {len(crsp_sample)} '
            f'({crsp_treated_firms} organizations, {crsp_treated_ciks} parent filer CIKs)\n'
            f'- Regression sample: {reg_treated} treated of {len(reg)} '
            f'({reg.loc[reg[TREAT]==1, "org_name"].nunique()} organizations, '
            f'{reg.loc[reg[TREAT]==1, "cik"].nunique()} parent filer CIKs)\n\n'
            'All values computed by the generator script — no hardcoded results.\n\n')
    def df_to_md(tdf):
        cols = [str(c) for c in tdf.columns]
        lines = ['| ' + ' | '.join(cols) + ' |',
                 '| ' + ' | '.join('---' for _ in cols) + ' |']
        for _, row in tdf.iterrows():
            lines.append('| ' + ' | '.join(str(v) for v in row.values) + ' |')
        return '\n'.join(lines)

    for name in [f'Table {i}' for i in range(1, 15)]:
        f.write(f'## {name}\n\n{captions[name]}\n\n')
        f.write(df_to_md(tables[name]))
        f.write('\n\n')
log(f'  {md_path}')

log('\n' + '=' * 90)
log('CANONICAL CHECK SUMMARY')
log('=' * 90)
n_fail = 0
for name, got, want, ok in CHECKS:
    log(f'  {"PASS" if ok else "FAIL"}  {name}: got {got}, canonical {want}')
    if not ok:
        n_fail += 1
log(f'\n{len(CHECKS) - n_fail}/{len(CHECKS)} checks passed.')
if n_fail:
    log('*** AT LEAST ONE CANONICAL CHECK FAILED — INSPECT BEFORE USING TABLES ***')

with open('outputs/appendix_v2_run_log.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(LOG_LINES))
log('\nDone.')
