"""
ESSAY 1 - TABLE REVISIONS FOR CHAIR FEEDBACK (October 2026)
===========================================================
Labels, notes, group tests and display format for the Essay 1 appendix tables, on the
frozen defense-final sample (constants_v3.json at dd8b564: N = 340 regression events,
106 treated, 12 treated parent CIKs). No sample changes, no estimate changes: every
appendix cell this script displays is read from outputs/rebuild/appendix_v3/, and every
recomputed input is first asserted against the committed value it reproduces.

Read-only on Data/processed/rebuild/CANONICAL_V3.csv. Does not import or run 158.

  Part A  sample gate: the regression sample reproduces constants_v3.json
  Part B  Table 2 group tests. The per-event gaps are recomputed with 158's method
          (first 8-K in (breach, +90d] from the cached EDGAR submissions) and must
          reproduce the committed T2 constants before any test runs. Then: Welch t on
          mean days, Mann-Whitney U on the distribution, two-proportion z-test on the
          share with an 8-K (Fisher's exact reported alongside, because the treated
          group has a single event without a filing).
  Part C  Table 16 in six panels (A-C breach-anchored, D-F announcement-anchored).
          Per-event leakage CARs are recomputed with 158's method and must reproduce
          outputs/rebuild/appendix_v3/table_16.csv cell for cell.
  Part D  covariate formulas checked against the code's raw inputs: firm size, leverage
          and ROA recomputed from the Compustat extract for every event and compared to
          the canonical columns.
  Part E  Tables 1-16 relabelled (plain names, p in parentheses, star legend), plus the
          variable-definitions table.

Outputs: outputs/essay1_chair/
  t2_event_gaps.csv              per-event gap (days) behind Table 2
  t2_group_tests.csv             Welch / Mann-Whitney / two-proportion / Fisher
  t16_event_cars.csv             per-event leakage CARs behind Table 16
  t16_panels.csv                 Table 16, Panels A-F
  covariate_formula_check.csv    Part D
  variable_definitions.csv       Part E
  table_{1..16}_relabelled.csv   Part E
  ESSAY1_CHAIR_TABLES.md         all relabelled tables with their source paths
  260_run.log
"""

import importlib.util
import json
import sys
from datetime import timedelta
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.proportion import proportions_ztest

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
OUT = Path('outputs/essay1_chair')
OUT.mkdir(parents=True, exist_ok=True)
APP = Path('outputs/rebuild/appendix_v3')
CONST = json.loads(Path('outputs/rebuild/constants_v3.json').read_text())
L = []


def log(m=''):
    print(m)
    L.append(str(m))


def app(i):
    """Committed appendix table without its trailing CAPTION row."""
    t = pd.read_csv(APP / f'table_{i}.csv')
    t = t[t.iloc[:, 0] != 'CAPTION'].reset_index(drop=True)
    for c in t.columns:  # the CAPTION row forces object dtype; restore numeric columns
        conv = pd.to_numeric(t[c], errors='coerce')
        if conv.notna().sum() == t[c].notna().sum():
            t[c] = conv
    return t


def stars(p):
    if p is None or pd.isna(p):
        return ''
    return '***' if p < .001 else '**' if p < .01 else '*' if p < .05 else ''


def fp(p):
    """p-value for display: three decimals, '<.001' below that."""
    if p is None or pd.isna(p) or p == '':
        return ''
    p = float(p)
    return '<.001' if p < .001 else f'{p:.3f}'.replace('0.', '.', 1)


def cell(b, p, nd=3):
    """Coefficient with stars and the p-value in parentheses."""
    if b is None or pd.isna(b) or b == '':
        return ''
    return f'{float(b):.{nd}f}{stars(float(p))} ({fp(p)})'


log('=' * 90)
log('260 ESSAY 1 CHAIR TABLES')
log('=' * 90)

ev = pd.read_csv('Data/processed/rebuild/CANONICAL_V3.csv', low_memory=False)
ev['bdt'] = pd.to_datetime(ev['breach_date'])
TREAT = 'fcc_form499'
HVARS = [TREAT, 'immediate_disclosure', 'prior_breaches_1yr', 'health_breach']
CONTROLS = HVARS + ['firm_size_log', 'leverage', 'roa']

# ---------------- Part A: sample gate ----------------
crsp = ev[ev['has_crsp_data'] == 1]
reg = crsp.dropna(subset=['car_30d'] + CONTROLS)
got = {'events_total': len(ev), 'events_crsp': len(crsp), 'N_regression': len(reg),
       'treated_total': int(ev[TREAT].sum()), 'treated_crsp': int(crsp[TREAT].sum()),
       'treated_regression': int(reg[TREAT].sum()),
       'treated_orgs_regression': int(reg.loc[reg[TREAT] == 1, 'org_name'].nunique()),
       'treated_parent_ciks_regression': int(reg.loc[reg[TREAT] == 1, 'final_cik'].nunique())}
for k, v in got.items():
    assert CONST[k] == v, f'sample gate: {k} = {v}, constants_v3.json has {CONST[k]}'
log(f"Part A sample gate PASS: {got}")

# ---------------- Part B: Table 2 group tests ----------------
CACHE8K = Path('Data/edgar/rebuild_submissions_cache')


def first_8k_after(cik, bdt):  # verbatim method of scripts/158 lines 170-181
    cj = CACHE8K / f'{int(cik)}.json'
    if not cj.exists():
        return None
    dates = []
    for pg in json.loads(cj.read_text()):
        for form, dt in zip(pg.get('form', []), pg.get('filingDate', [])):
            if form.startswith('8-K'):
                d8 = pd.Timestamp(dt)
                if bdt < d8 <= bdt + pd.Timedelta(days=90):
                    dates.append(d8)
    return min(dates) if dates else None


big = ev.groupby('final_cik').size()
ctrl = set(big[big >= 3].index)
ver = ev[(ev[TREAT] == 1) | (ev['final_cik'].isin(ctrl))]
rows = []
for _, r in ver.iterrows():
    f8k = first_8k_after(r['final_cik'], r['bdt'])
    rows.append({'final_cik': int(r['final_cik']), 'org_name': r['org_name'],
                 'breach_date': r['breach_date'], 'treated': int(r[TREAT]),
                 'first_8k_date': f8k.date().isoformat() if f8k is not None else '',
                 'gap_days': (f8k - r['bdt']).days if f8k is not None else np.nan})
g = pd.DataFrame(rows)
g['has_8k_90d'] = g['gap_days'].notna().astype(int)
g.to_csv(OUT / 't2_event_gaps.csv', index=False)
for tv, key in [(1, 'treated'), (0, 'untreated')]:
    a = g[g['treated'] == tv]
    h = a['gap_days'].dropna()
    chk = {f'T2_{key}_N': len(a), f'T2_{key}_median_gap': round(h.median(), 1),
           f'T2_{key}_mean_gap': round(h.mean(), 2),
           f'T2_{key}_share_8k_90d': round(len(h) / len(a), 4)}
    for k, v in chk.items():
        assert CONST[k] == v, f'Table 2 reproduction: {k} = {v}, committed {CONST[k]}'
log('Part B Table 2 reproduces constants_v3.json T2_* exactly')

gt, gu = g[g['treated'] == 1], g[g['treated'] == 0]
ht, hu = gt['gap_days'].dropna(), gu['gap_days'].dropna()
tw, pw = stats.ttest_ind(ht, hu, equal_var=False)
# Welch-Satterthwaite degrees of freedom, reported with the t statistic
vt, vu = ht.var(ddof=1) / len(ht), hu.var(ddof=1) / len(hu)
dfw = (vt + vu) ** 2 / (vt ** 2 / (len(ht) - 1) + vu ** 2 / (len(hu) - 1))
mw = stats.mannwhitneyu(ht, hu, alternative='two-sided')
counts = np.array([int(gt['has_8k_90d'].sum()), int(gu['has_8k_90d'].sum())])
nobs = np.array([len(gt), len(gu)])
z, pz = proportions_ztest(counts, nobs)
_, pf = stats.fisher_exact([[counts[0], nobs[0] - counts[0]], [counts[1], nobs[1] - counts[1]]])
tests = pd.DataFrame([
    {'Test': 'Welch two-sample t-test (mean days to first 8-K)', 'Measure': 'Days to first 8-K',
     'Treated N': len(ht), 'Untreated N': len(hu),
     'Treated value': round(ht.mean(), 2), 'Untreated value': round(hu.mean(), 2),
     'Difference': round(ht.mean() - hu.mean(), 2), 'Statistic': f't = {tw:.3f}',
     'df': round(dfw, 1), 'p': round(pw, 4)},
    {'Test': 'Mann-Whitney U (Wilcoxon rank-sum), distribution of days', 'Measure': 'Days to first 8-K',
     'Treated N': len(ht), 'Untreated N': len(hu),
     'Treated value': round(ht.median(), 1), 'Untreated value': round(hu.median(), 1),
     'Difference': round(ht.median() - hu.median(), 1), 'Statistic': f'U = {mw.statistic:.1f}',
     'df': '', 'p': round(mw.pvalue, 4)},
    {'Test': 'Two-proportion z-test (share with an 8-K within 90 days)', 'Measure': '8-K within 90 days',
     'Treated N': int(nobs[0]), 'Untreated N': int(nobs[1]),
     'Treated value': round(counts[0] / nobs[0], 4), 'Untreated value': round(counts[1] / nobs[1], 4),
     'Difference': round(counts[0] / nobs[0] - counts[1] / nobs[1], 4), 'Statistic': f'z = {z:.3f}',
     'df': '', 'p': round(pz, 4)},
    {'Test': "Fisher's exact test (same share; small-count check)", 'Measure': '8-K within 90 days',
     'Treated N': int(nobs[0]), 'Untreated N': int(nobs[1]),
     'Treated value': f'{counts[0]} of {nobs[0]}', 'Untreated value': f'{counts[1]} of {nobs[1]}',
     'Difference': '', 'Statistic': '', 'df': '', 'p': round(pf, 4)}])
tests.to_csv(OUT / 't2_group_tests.csv', index=False)
log(tests.to_string(index=False))

# ---------------- Part C: Table 16, six panels ----------------
_s = importlib.util.spec_from_file_location('crsp_daily', 'scripts/254_crsp_daily.py')
crsp_daily = importlib.util.module_from_spec(_s)
_s.loader.exec_module(crsp_daily)
cd = crsp_daily.load(['permno', 'date', 'ret'])
mkt = pd.read_csv('Data/wrds/market_indices.csv', usecols=['date', 'vwretd'])
cd['date'] = pd.to_datetime(cd['date'])
mkt['date'] = pd.to_datetime(mkt['date'])
cd = cd.merge(mkt, on='date', how='left')
cd['ar'] = (pd.to_numeric(cd['ret'], errors='coerce') - cd['vwretd']) * 100
P = {p: x.sort_values('date').reset_index(drop=True) for p, x in cd.groupby('permno')}
W = [(-30, -21), (-20, -11), (-10, -1)]


def leak_cars(permno, anchor):  # verbatim method of scripts/158 lines 407-420
    x = P.get(permno)
    if x is None or pd.isna(anchor):
        return None
    pos = (x['date'] - anchor).abs().idxmin()
    if abs((x.loc[pos, 'date'] - anchor).days) > 50 or pos < 30:
        return None
    cars = {}
    for a, b in W:
        sl = x['ar'].iloc[pos + a:pos + b + 1]
        if len(sl) != b - a + 1 or sl.isna().any():
            return None
        cars[f'{a},{b}'] = sl.sum()
    return cars


base = crsp.copy()
base['rdt'] = pd.to_datetime(base['reported_date'], errors='coerce')
base.loc[base['delay_invalid'] == 1, 'rdt'] = pd.NaT
recs = []
for anc_key, anc_col, sub in [('breach', 'bdt', base), ('announcement', 'rdt', base[base['rdt'].notna()])]:
    for _, r in sub.iterrows():
        c = leak_cars(r['permno'], r[anc_col]) if pd.notna(r['permno']) else None
        if c is not None:
            recs.append({'anchor': anc_key, 'final_cik': int(r['final_cik']), 'org_name': r['org_name'],
                         'breach_date': r['breach_date'], 'anchor_date': r[anc_col].date().isoformat(),
                         'treated': int(r[TREAT]), **{f'car_{k}': round(v, 6) for k, v in c.items()}})
E16 = pd.DataFrame(recs)
E16.to_csv(OUT / 't16_event_cars.csv', index=False)

PANELS = [('A', 'breach', (-30, -21)), ('B', 'breach', (-20, -11)), ('C', 'breach', (-10, -1)),
          ('D', 'announcement', (-30, -21)), ('E', 'announcement', (-20, -11)),
          ('F', 'announcement', (-10, -1))]
committed16 = app(16)
prow = []
for pl, anc, (a, b) in PANELS:
    d = E16[E16['anchor'] == anc]
    col = f'car_{a},{b}'
    grp = [('All events', d[col]), ('Form 499 filers (treated)', d.loc[d['treated'] == 1, col]),
           ('Non-filers (untreated)', d.loc[d['treated'] == 0, col])]
    for glab, s in grp:
        t1, p1 = stats.ttest_1samp(s, 0)
        prow.append({'Panel': pl, 'Anchor': 'Breach date' if anc == 'breach' else 'Disclosure (reported) date',
                     'Window': f'[{a},{b}]', 'Row': glab, 'N': len(s), 'Mean CAR (pp)': round(s.mean(), 3),
                     'Median CAR (pp)': round(s.median(), 3), 'SD': round(s.std(), 3),
                     't': round(t1, 3), 'p': round(p1, 4), 'Test': 'one-sample t (mean = 0)'})
    st, su = grp[1][1], grp[2][1]
    t2, p2 = stats.ttest_ind(st, su, equal_var=False)
    prow.append({'Panel': pl, 'Anchor': prow[-1]['Anchor'], 'Window': f'[{a},{b}]',
                 'Row': 'Treated minus untreated', 'N': '', 'Mean CAR (pp)': round(st.mean() - su.mean(), 3),
                 'Median CAR (pp)': '', 'SD': '', 't': round(t2, 3), 'p': round(p2, 4),
                 'Test': 'Welch two-sample t'})
T16 = pd.DataFrame(prow)
# cell-for-cell reproduction of the committed table_16.csv
mapg = {'All events': 'All', 'Form 499 filers (treated)': 'Treated', 'Non-filers (untreated)': 'Untreated',
        'Treated minus untreated': 'Difference (Welch)'}
for _, r in T16.iterrows():
    pan = 'Breach-anchored (PRIMARY)' if r['Panel'] in 'ABC' else 'Announcement-anchored (secondary)'
    c = committed16[(committed16['Panel'] == pan) & (committed16['Window'] == r['Window'])
                    & (committed16['Group'] == mapg[r['Row']])]
    assert len(c) == 1
    c = c.iloc[0]
    for mine, theirs in [('Mean CAR (pp)', 'Mean CAR (pp)'), ('t', 't'), ('p', 'p')]:
        assert abs(float(r[mine]) - float(c[theirs])) < 1e-9, (r['Panel'], r['Row'], mine, r[mine], c[theirs])
    if r['N'] != '':
        assert int(r['N']) == int(float(c['N']))
        for col in ['Median CAR (pp)', 'SD']:
            assert abs(float(r[col]) - float(c['Median' if col.startswith('Median') else 'SD'])) < 1e-9
T16.to_csv(OUT / 't16_panels.csv', index=False)
log('Part C Table 16: all 24 rows reproduce outputs/rebuild/appendix_v3/table_16.csv')
for pl in ['C', 'F']:
    r = T16[(T16['Panel'] == pl) & (T16['Row'] == 'Treated minus untreated')].iloc[0]
    log(f"  Panel {pl} [-10,-1] treated - untreated: {r['Mean CAR (pp)']:+.3f} pp, Welch p = {r['p']:.4f}")

# ---------------- Part D: covariate formulas ----------------
cs = pd.read_csv('Data/wrds/compustat_annual.csv')
tp = Path('Data/wrds/compustat_annual_topup.csv')
if tp.exists():
    cs = pd.concat([cs, pd.read_csv(tp)], ignore_index=True)
cs['datadate'] = pd.to_datetime(cs['datadate'])
cs = cs.dropna(subset=['tic', 'at'])
by_tic = {t: x.sort_values('datadate') for t, x in cs.groupby('tic')}
chk = []
for _, r in reg.iterrows():
    x = by_tic.get(r['matched_ticker'])
    pr = x[(x['datadate'] < r['bdt']) & (x['datadate'] >= r['bdt'] - timedelta(days=550))]
    f = pr.iloc[-1]
    chk.append({'final_cik': int(r['final_cik']), 'breach_date': r['breach_date'],
                'fiscal_year_end_used': f['datadate'].date().isoformat(),
                'days_fye_before_breach': (r['bdt'] - f['datadate']).days,
                'at': f['at'], 'lt': f['lt'], 'ni': f['ni'], 'ceq': f.get('ceq', np.nan),
                'firm_size_log': r['firm_size_log'], 'ln_at': round(np.log(f['at']), 4),
                'leverage': r['leverage'], 'lt_over_at': round(f['lt'] / f['at'], 4),
                'roa': r['roa'], 'ni_over_at': round(f['ni'] / f['at'], 4)})
D = pd.DataFrame(chk)
D.to_csv(OUT / 'covariate_formula_check.csv', index=False)
for a_, b_, lab in [('firm_size_log', 'ln_at', 'firm size = ln(at)'),
                    ('leverage', 'lt_over_at', 'leverage = lt / at'),
                    ('roa', 'ni_over_at', 'ROA = ni / at')]:
    mx = (D[a_] - D[b_]).abs().max()
    assert mx < 1e-9, (lab, mx)
    log(f'Part D {lab}: matches the canonical column on all {len(D)} regression events (max |diff| {mx:.1e})')
de = D[D['ceq'] > 0]
log(f"  Debt fields (dltt, dlc) are absent from the Compustat extract: {sorted(set(['dltt','dlc']) & set(cs.columns)) or 'none'}")
log(f"  Fiscal year used: latest fiscal year-end before the breach date, within 550 days; "
    f"lag median {D['days_fye_before_breach'].median():.0f} d, range {D['days_fye_before_breach'].min()}-"
    f"{D['days_fye_before_breach'].max()} d")
log(f"  For reference, lt / ceq (a liabilities-to-equity ratio) on the same events has median "
    f"{(de['lt'] / de['ceq']).median():.2f}, against the leverage column's median {D['leverage'].median():.3f}")

# ---------------- Part E: relabelled tables + definitions ----------------
NAME = {'const': 'Constant', 'fcc_form499': 'Form 499 filer',
        'immediate_disclosure': 'Disclosed within 7 days',
        'prior_breaches_1yr': 'Prior breaches (past 12 months)', 'health_breach': 'Health data breach',
        'firm_size_log': 'Firm size (log total assets)', 'leverage': 'Leverage (total liabilities / total assets)',
        'roa': 'Return on assets (net income / total assets)', 'car_30d': '30-day CAR (%)',
        'car_5d': '5-day CAR (%)', 'disclosure_delay_days': 'Disclosure delay (days)'}
HYP = {'H1_timing': 'H1: Disclosed within 7 days', 'H2_FCC': 'H2: Form 499 filer',
       'H3_prior': 'H3: Prior breaches (past 12 months)', 'H4_health': 'H4: Health data breach'}
STATUS = {'BOUNDED NULL': 'Bounded null (effect shown to be small)',
          'NULL-INCONCLUSIVE': 'Inconclusive (cannot rule out a 2.10 pp effect)'}
R = {}
t = app(1)
R[1] = pd.DataFrame({'Variable': t['Variable'].map(NAME), 'N': t['N'], 'Mean': t['Mean'],
                     'SD': t['SD'], 'Median': t['Median']})
t = app(2)
R[2] = pd.DataFrame({'Group': ['Form 499 filers (treated)', 'Non-filers at firms with 3+ breaches (control)'],
                     'Events': t['N'], 'Median days to first 8-K': t['Median gap (days)'],
                     'Mean days to first 8-K': t['Mean gap (days)'],
                     'Share with an 8-K within 90 days': t['Share with 8-K in 90d']})
t = app(3)
CMP = {'Form 499': 'Form 499 filer', 'Timing': 'Disclosed within 7 days', 'Health': 'Health data breach',
       'History': 'Any prior breach (past 12 months)'}
GRP = {'Filer': 'Filer', 'Non-filer': 'Non-filer', 'Immediate': 'Within 7 days', 'Delayed': 'After 7 days',
       'Health': 'Health data', 'Non-health': 'Other data', 'Any prior': 'Any prior', 'No prior': 'No prior',
       'Difference': 'Difference (Welch t-test)'}
R[3] = pd.DataFrame({'Comparison': t['Comparison'].map(CMP), 'Group': t['Group'].map(GRP),
                     'N': t['N'].map(lambda v: '' if pd.isna(v) else int(v)),
                     'Mean CAR (%)': [cell(m, p) if g == 'Difference' else f'{m:.3f}'
                                      for m, p, g in zip(t['Mean CAR'], t['Welch p'], t['Group'])],
                     'Median CAR (%)': t['Median CAR'].map(lambda v: '' if pd.isna(v) else f'{v:.3f}'),
                     'Welch t': t['Welch diff'].map(lambda v: '' if pd.isna(v) else f'{v:.3f}')})
t = app(4)
R[4] = pd.DataFrame({'Variable': t['Variable'].map(NAME), 'Coefficient (p)': [cell(b, p, 4) for b, p in zip(t['Coef'], t['p'])],
                     'Robust SE (HC3)': t['SE'].map(lambda v: f'{v:.4f}')})
t = app(5)
R[5] = pd.DataFrame({'Hypothesis': t['Hypothesis'].map(HYP),
                     'Coefficient (p)': [cell(b, p, 4) for b, p in zip(t['Coef'], t['p'])],
                     '95% CI': [f"[{CONST[h + '_ci'][0]:.2f}, {CONST[h + '_ci'][1]:.2f}]" for h in t['Hypothesis']],
                     'TOST p (bound ±2.10 pp)': t['TOST_p_2.10'].map(fp),
                     'MDE80 (pp)': t['MDE80'].map(lambda v: f'{v:.2f}'), 'Status': t['Status'].map(STATUS)})
t = app(6)
TERM6 = {'immediate_disclosure': 'Disclosed within 7 days',
         'immediate_disclosure (main effect)': 'Disclosed within 7 days (main effect)',
         'fcc_form499 (main effect)': 'Form 499 filer (main effect)',
         'immediate_disclosure x fcc_form499': 'Disclosed within 7 days x Form 499 filer'}
SPEC6 = {'Treated only (fcc_form499=1)': 'Form 499 filers only', 'Untreated only (fcc_form499=0)': 'Non-filers only',
         'Pooled with interaction': 'All events, with interaction'}
R[6] = pd.DataFrame({'Sample': t['Specification'].map(SPEC6), 'Term': t['Term'].map(TERM6),
                     'Coefficient (p)': [cell(b, p, 4) for b, p in zip(t['Coef'], t['p'])],
                     'Robust SE (HC3)': t['SE'].map(lambda v: f'{v:.4f}'), 'N': t['N']})
t = app(7)
REST = {'Full': 'Full regression sample', 'Excl. largest decile': 'Excluding largest 10% of firms by size',
        'Excl. smallest decile': 'Excluding smallest 10% of firms by size', 'Non-health': 'Excluding health data breaches'}
R[7] = pd.DataFrame({'Sample': t['Restriction'].map(REST),
                     'Disclosed within 7 days': [cell(b, p) for b, p in zip(t['Timing coef'], t['Timing p'])],
                     'Form 499 filer': [cell(b, p) for b, p in zip(t['FCC coef'], t['FCC p'])],
                     'Return on assets': [cell(b, p, 2) for b, p in zip(t['ROA coef'], t['ROA p'])], 'N': t['N']})
t = app(8)
METH = {'OLS': 'Classical OLS', 'HC1': 'HC1 (robust)', 'HC3': 'HC3 (robust; primary)',
        'Firm-clustered': 'Clustered by parent company (CIK)'}
R[8] = pd.DataFrame({'Standard-error method': t['Method'].map(METH),
                     'p: Disclosed within 7 days': t['Timing p'].map(fp),
                     'p: Form 499 filer': t['FCC p'].map(fp), 'p: Return on assets': t['ROA p'].map(fp)})
for i, lab in [(9, 'Disclosed within 7 days'), (10, 'Form 499 filer')]:
    t = app(i)
    R[i] = pd.DataFrame({'Firm-size quartile': t['Quartile'].map(lambda q: f'{q} ({"smallest" if q == "Q1" else "largest" if q == "Q4" else "middle"})'),
                         f'{lab}: coefficient (p)': [cell(b, p) for b, p in zip(t['Coef'], t['p'])],
                         'N': t['N'], 'Form 499 filer events': t['Treated N']})
t = app(11)
R[11] = pd.DataFrame({'Specification': ['Baseline (HC3)', 'Baseline + calendar-year fixed effects'],
                      'Form 499 filer: coefficient (p)': [cell(b, p, 4) for b, p in zip(t['FCC coef'], t['p'])]})
t = app(12)
R[12] = pd.DataFrame({'Added control': ['Records affected (largest count across filings)'],
                      'Form 499 filer: coefficient (p)': [cell(t['FCC coef'][0], t['FCC p'][0], 4)],
                      'p: records affected': [fp(t['Control p'][0])], 'N': t['N']})
t = app(13)
R[13] = pd.DataFrame({'Model': ['Baseline (HC3)', 'Baseline + Fama-French three factors'],
                      'p: Form 499 filer': t['FCC p'].map(fp), 'p: Return on assets': t['ROA p'].map(fp)})
t = app(14)
t14 = t[t['Variable'].isin(CONTROLS)]
R[14] = pd.DataFrame({'Variable': t14['Variable'].map(NAME),
                      'Coefficient (p)': [cell(float(b), float(p), 4) for b, p in zip(t14['Coef (log turnover)'], t14['p'])],
                      'Robust SE (HC3)': t14['SE'].map(lambda v: f'{float(v):.4f}')})
t = app(15)
R[15] = pd.DataFrame({'Rank': range(1, len(t) + 1), 'Variable': t['Feature'].map(NAME),
                      'Importance': t['Importance'].map(lambda v: f'{v:.4f}')})
R[16] = pd.DataFrame({'Panel': T16['Panel'], 'Anchor': T16['Anchor'], 'Window (trading days)': T16['Window'],
                      'Group': T16['Row'], 'N': T16['N'],
                      'Mean CAR (%)': [cell(m, p) for m, p in zip(T16['Mean CAR (pp)'], T16['p'])],
                      'Median CAR (%)': T16['Median CAR (pp)'], 'SD': T16['SD'], 't': T16['t']})
# Row-count gate: every relabelled table has exactly the rows of its committed source
# (table 14 drops only its trailing "N=..." label row), and the Table 2 test block has 4.
assert len(tests) == 4, f'Table 2 tests: {len(tests)} rows'
for i, df in R.items():
    src = app(i)
    if i == 14:
        src = src[src['Variable'].isin(CONTROLS)]
    assert len(df) == len(src) > 0, f'table {i}: {len(df)} relabelled rows vs {len(src)} in source'
    assert not df.duplicated().any(), f'table {i}: duplicated rows'
log(f'Row-count gate PASS: {", ".join(f"T{i}={len(df)}" for i, df in R.items())}; Table 2 tests=4')
for i, df in R.items():
    for c in ['N', 'Form 499 filer events']:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors='coerce').astype('Int64').astype(str).replace('<NA>', '')
    df.to_csv(OUT / f'table_{i}_relabelled.csv', index=False)

DEFS = [
    ('30-day CAR', 'car_30d', 'Sum of daily abnormal returns (firm return minus CRSP value-weighted market return) over trading days 0 to +30, where day 0 is the trading day nearest the breach date', 'Percent (percentage points)', 'CRSP daily stock file; CRSP market index', 'Trading days 0 to +30 around the breach date', 'scripts/155:6-7,140-157'),
    ('5-day CAR', 'car_5d', 'Same as the 30-day CAR over trading days 0 to +5', 'Percent', 'CRSP', 'Trading days 0 to +5', 'scripts/155:140-157'),
    ('Pre-event (leakage) CAR', 'Table 16', 'Sum of daily abnormal returns over a window before day 0: [-30,-21], [-20,-11] or [-10,-1]; day 0 is the trading day nearest the breach date (Panels A-C) or the reported disclosure date (Panels D-F)', 'Percent', 'CRSP', 'Trading days before day 0', 'scripts/158:384-461'),
    ('Abnormal log turnover', 'Table 14', 'Mean of log(daily volume / shares outstanding) over trading days -5 to +25, minus its mean over trading days -240 to -60', 'Log points', 'CRSP daily volume and shares outstanding', 'Event window vs. a pre-event baseline', 'scripts/158:334-368'),
    ('Form 499 filer', 'fcc_form499', '1 if the breached organization was a registered FCC Form 499 telecommunications filer with registration covering the breach date (subject to the FCC seven-day rule); 0 otherwise', 'Indicator (0/1)', 'FCC Form 499 filer registry (export of 2026-07-21); 22 documented adjudication rules', 'As of the breach date', 'scripts/154'),
    ('Disclosed within 7 days', 'immediate_disclosure', '1 if the reported (public notification) date is no more than 7 calendar days after the breach date; missing when the delay is missing', 'Indicator (0/1)', 'Privacy Rights Clearinghouse (PRC) breach and reported dates', 'Breach date to reported date', 'scripts/156:135-136'),
    ('Disclosure delay', 'disclosure_delay_days', 'Calendar days from the breach date to the reported date. Reported dates up to 30 days before the breach date are set to 0; more than 30 days before, set to missing (source-data error)', 'Calendar days', 'PRC', 'Breach date to reported date', 'scripts/156:109-131'),
    ('Prior breaches (past 12 months)', 'prior_breaches_1yr', 'Number of other verified breach events at the same parent company (CIK) in the 365 days before this breach', 'Count', 'PRC, after de-duplication to breach events', '12 months before the breach date', 'scripts/156:100-106'),
    ('Any prior breach', 'Table 3', '1 if prior breaches (past 12 months) is greater than zero', 'Indicator (0/1)', 'PRC', '12 months before the breach date', 'scripts/158:218'),
    ('Health data breach', 'health_breach', "1 if the source record's compromised-information field mentions medical or health data, or the organization type is medical (MED)", 'Indicator (0/1)', 'PRC record text fields', 'At the breach', 'scripts/156:144-146'),
    ('Firm size', 'firm_size_log', 'Natural log of total assets (Compustat AT, $ millions)', 'Log of $ millions', 'Compustat annual', 'Latest fiscal year ending before the breach date (within 550 days)', 'scripts/156:71-89'),
    ('Leverage', 'leverage', 'Total liabilities (Compustat LT) divided by total assets (AT)', 'Ratio', 'Compustat annual', 'Latest fiscal year ending before the breach date (within 550 days)', 'scripts/156:83'),
    ('Return on assets', 'roa', 'Net income (Compustat NI) divided by total assets (AT)', 'Ratio', 'Compustat annual', 'Latest fiscal year ending before the breach date (within 550 days)', 'scripts/156:85'),
    ('Operating margin (amendment only)', 'op_margin', '(Sales - cost of goods sold - SG&A) / sales', 'Ratio', 'Compustat annual', 'Latest fiscal year ending before the breach date', 'scripts/156:86-88'),
    ('Records affected', 'total_affected_max', 'Largest number of affected individuals reported across the source filings for the event', 'Count of records', 'PRC', 'As reported', 'scripts/158:312-318'),
    ('Days to first 8-K', 'Table 2', 'Calendar days from the breach date to the first Form 8-K the firm filed in the 90 days after it; events with no 8-K in that window have no gap', 'Calendar days', 'SEC EDGAR submissions (cached)', 'Breach date to +90 days', 'scripts/158:162-209'),
    ('8-K within 90 days', 'Table 2', '1 if the firm filed any Form 8-K in the 90 days after the breach date', 'Indicator (0/1)', 'SEC EDGAR submissions (cached)', 'Breach date to +90 days', 'scripts/158:162-209'),
    ('Fama-French factors', 'Table 13', 'Market excess return (Mkt-RF), size (SMB) and value (HML) factor values for the month of the breach', 'Percent', 'Kenneth French data library', 'Month of the breach date', 'scripts/158:319-333'),
    ('Calendar-year fixed effects', 'Table 11', 'One indicator per calendar year of the breach date', 'Indicators', 'PRC breach date', 'Year of the breach', 'scripts/158:305-311'),
]
pd.DataFrame(DEFS, columns=['Plain name', 'Code name / table', 'Definition', 'Unit', 'Source', 'Timing',
                            'Code reference']).to_csv(OUT / 'variable_definitions.csv', index=False)

TITLES = {1: 'Summary Statistics (CRSP Sample)', 2: 'Disclosure-Date Verification (First 8-K Within 90 Days)',
          3: 'Mean and Median 30-Day CAR by Subgroup', 4: 'Main Regression: 30-Day CAR',
          5: 'Hypothesis Tests: Equivalence (TOST) and Minimum Detectable Effects',
          6: 'Timing Effect by Regulatory Regime', 7: 'Alternative Sample Restrictions',
          8: 'Standard-Error Methods', 9: 'Timing Coefficient by Firm-Size Quartile',
          10: 'Form 499 Coefficient by Firm-Size Quartile', 11: 'Year Fixed Effects', 12: 'Breach Severity Control',
          13: 'Fama-French Factor Controls', 14: 'Abnormal Trading Turnover', 15: 'Random-Forest Importance Ranking',
          16: 'Pre-Event (Leakage) Windows, Panels A-F'}


def md(df):
    cols = list(df.columns)
    s = '| ' + ' | '.join(cols) + ' |\n|' + '---|' * len(cols) + '\n'
    for _, r in df.iterrows():
        s += '| ' + ' | '.join('' if (isinstance(v, float) and pd.isna(v)) else str(v) for v in r) + ' |\n'
    return s


with open(OUT / 'ESSAY1_CHAIR_TABLES.md', 'w', encoding='utf-8') as f:
    f.write('# Essay 1 tables, relabelled (generated by scripts/260)\n\n'
            'Every cell is read from the committed file named under each table; nothing is re-estimated. '
            'Sample: N = 340 regression events (106 Form 499 filer events, 12 parent companies), '
            'constants_v3.json at dd8b564 (= defense-final).\n\n'
            'Star legend: \\* p < .05, \\*\\* p < .01, \\*\\*\\* p < .001; p-values in parentheses.\n\n')
    for i in range(1, 17):
        f.write(f'## Table {i}. {TITLES[i]}\n\nSource: `outputs/rebuild/appendix_v3/table_{i}.csv`'
                + (' (cells reproduced by `outputs/essay1_chair/t16_panels.csv`)' if i == 16 else '')
                + f'; display file `outputs/essay1_chair/table_{i}_relabelled.csv`\n\n' + md(R[i]) + '\n')
        if i == 2:
            f.write('**Group tests** (source: `outputs/essay1_chair/t2_group_tests.csv`)\n\n' + md(tests) + '\n')

(OUT / '260_run.log').write_text('\n'.join(L) + '\n', encoding='utf-8')
log(f'\nWrote {len(list(OUT.iterdir()))} files to {OUT}/')
