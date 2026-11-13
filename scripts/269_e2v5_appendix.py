"""ESSAY 2 v5 — appendix generator (committee item 10).

ONE script that rebuilds every Essay 2 appendix table from committed inputs:
  * classification / data tables that until now existed only as tombstoned CSVs
    (archive/outputs/tables/essay2_appendix/ and outputs/tables/essay2_appendix/,
    whose emitter `emit_appendix.py` was never committed) are RECOMPUTED here from
    committed data (CANONICAL_V3, stage2_signed, the 1,054-record prior-spec
    dataset, Compustat, the Form 499 registry snapshot, scripts/154 rules,
    scripts/164 family keywords) and GATED cell by cell against the tombstones;
  * results tables are read from the v5 outputs (scripts/264-268) and the live
    essay2_v2 chain (scripts/163/164/166), never recomputed here.

    python scripts/269_e2v5_appendix.py                  # needs v5_t16_spreads.csv
    python scripts/269_e2v5_appendix.py --allow-pending  # spreads table -> PENDING stub

TABLE_ORDER below is the single place the numbering comes from: reorder it and
every file name, heading and cross-reference follows.
Writes outputs/essay2_v5/appendix/<NN>_<key>.csv, ESSAY2_V5_APPENDIX.md,
reproduction_report.md, and outputs/essay2_v5/constants_parts/269.json.
"""
import ast
import importlib.util as _ilu
import json
import re
import sys
import xml.etree.ElementTree as ET
from datetime import timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
_s = _ilu.spec_from_file_location('e2v5', 'scripts/263_e2v5_lib.py')
L = _ilu.module_from_spec(_s)
_s.loader.exec_module(L)

# --------------------------------------------------------------------- order
# Citation order (Table 1 = first cited), set 2026-11-07. Each entry is one
# appendix table; a table with several keys is printed as Panels A, B, ...
# Reordering this list renumbers everything.
TABLE_GROUPS = [
    ['sample_attrition'],                                                         # 1
    ['descriptives_v5', 'descriptives_v5_differences'],                           # 2
    ['correlations_v5'],                                                          # 3
    ['events_by_year'],                                                           # 4
    ['four_panel_decomposition', 'records_per_event'],                            # 5
    ['q1_transition_components', 'q1_transition_records'],                        # 6
    ['misclassified_records'],                                                    # 7
    ['misclassified_group_comparisons', 'misclassified_group_contrasts'],         # 8
    ['gradient_grid'],                                                            # 9
    ['identifier_collisions', 'recycled_tickers', 'size_variable_reconciliation'],  # 10
    ['missingness_precase'],                                                      # 11
    ['form499_registry_matches'],                                                 # 12
    ['treatment_adjudications'],                                                  # 13
    ['sic_conventions_vs_form499'],                                               # 14
    ['sic_convention_errors'],                                                    # 15
    ['treated_outside_comparison'],                                               # 16
    ['sich_vs_curated_sic'],                                                      # 17
    ['nested_models'],                                                            # 18
    ['inference_ladder'],                                                         # 19
    ['design_resolution'],                                                        # 20
    ['dynamic_path'],                                                             # 21
    ['benchmarks', 'estimation_contamination', 'coverage_drops'],                 # 22
    ['alternatives_bridge'],                                                      # 23
    ['announcement_family', 'announcement_ladder', 'announcement_buildup',
     'placebo_dates', 'earnings_benchmark'],                                      # 24
    ['disclosure_delay', 'delay_nonzero', 'delay_quantiles', 'delay_distribution',
     'delay_distribution_tests'],                                                 # 25
    ['spreads'],                                                                  # 26
    ['size_quartiles'],                                                           # 27
    ['prerule_events'],                                                           # 28
    ['specification_curve', 'specification_curve_permutation'],                   # 29
    ['leave_one_parent_out', 'influence'],                                        # 30
    ['fixed_effects'],                                                            # 31
    ['v4_date_sensitivity'],                                                      # 32
    ['program_test_enumeration', 'bh_families'],                                  # 33
]
TABLE_ORDER = [k for g in TABLE_GROUPS for k in g]
assert len(TABLE_ORDER) == len(set(TABLE_ORDER))
ALLOW_PENDING = '--allow-pending' in sys.argv
OUT = L.OUT
AP = OUT / 'appendix'
AP.mkdir(parents=True, exist_ok=True)
T2 = L.T2
TOMB = [Path('archive/outputs/tables/essay2_appendix'), Path('outputs/tables/essay2_appendix')]
TREAT = L.TREAT
TABLES = {}
GATES = []
K = {}          # constants for constants_parts/269.json


def add(key, df, title, level, source, note=''):
    assert key in TABLE_ORDER, f'{key} missing from TABLE_ORDER'
    TABLES[key] = dict(df=df.reset_index(drop=True), title=title, level=level, source=source,
                       note=note)


def tomb(name):
    for d in TOMB:
        p = d / name
        if p.exists():
            return p
    raise FileNotFoundError(name)


def _dec(s):
    s = str(s)
    if re.fullmatch(r'-?\d+\.\d+', s):
        return len(s.split('.')[1])
    return 0 if re.fullmatch(r'-?\d+', s) else None


def gate_join(key, tname, on, cols, reasons, mine=None):
    """Like gate(), but aligns rows by joining on `on` (rows in both only)."""
    mine = (TABLES[key]['df'] if mine is None else mine).astype({on: str})
    old = pd.read_csv(tomb(tname), dtype=str, keep_default_na=False)
    j = old.merge(mine, on=on, how='inner', suffixes=('_t', '_n'))
    diffs, match = [], 0
    for _, r in j.iterrows():
        for c in cols:
            o, m = r[c + '_t'], r[c + '_n']
            m = '' if (m is None or (isinstance(m, float) and np.isnan(m))) else str(m)
            if o.strip() == m.strip():
                match += 1
            else:
                diffs.append((r[on], c, o, m))
    GATES.append(dict(key=key, tombstone=str(tomb(tname)), rows_tomb=len(old), rows_new=len(mine),
                      cells=len(j) * len(cols), match=match, diffs=diffs,
                      reasons=reasons + f' (joined on {on}: {len(j)} rows in both)'))
    print(f'  GATE {key:32s} joined {len(j)}/{len(old)}  cells {match}/{len(j) * len(cols)} match')


def gate(key, tname, cols=None, reasons=None, sort_by=None):
    """Cell-by-cell comparison of TABLES[key] against a tombstoned CSV, at the
    tombstone's printed precision. Rows are aligned by position after sorting on
    `sort_by` (both sides) when given."""
    mine = TABLES[key]['df'].copy()
    old = pd.read_csv(tomb(tname), dtype=str, keep_default_na=False)
    cols = cols or [c for c in old.columns if c in mine.columns]
    if sort_by:
        old = old.sort_values(sort_by).reset_index(drop=True)
        mine = mine.astype({c: str for c in sort_by}).sort_values(sort_by).reset_index(drop=True)
    n = min(len(old), len(mine))
    match, diffs = 0, []
    for i in range(n):
        for c in cols:
            o, m = old.loc[i, c], mine.loc[i, c]
            d = _dec(o)
            if d is not None and pd.notna(m) and str(m) != '':
                try:
                    ok = abs(round(float(m), d) - float(o)) <= 10 ** -d * 0.51
                except (TypeError, ValueError):
                    ok = str(m) == o
            else:
                ms = '' if (m is None or (isinstance(m, float) and np.isnan(m))) else str(m)
                ok = ms.strip() == o.strip() or (o in ('', 'nan') and ms in ('', 'nan', 'None'))
            if ok:
                match += 1
            else:
                diffs.append((i, c, o, m))
    GATES.append(dict(key=key, tombstone=str(tomb(tname)), rows_tomb=len(old), rows_new=len(mine),
                      cells=n * len(cols), match=match, diffs=diffs,
                      reasons=reasons or '(no documented reason; investigate)'))
    print(f'  GATE {key:32s} rows {len(mine)}/{len(old)}  cells {match}/{n * len(cols)} match')



def to_md(df):
    """Pipe table without the optional tabulate dependency (not in requirements.txt)."""
    def f(v):
        if isinstance(v, float):
            return '' if np.isnan(v) else f'{v:.4f}'
        return str(v).replace('|', '/').replace('\n', ' ')
    head = '| ' + ' | '.join(map(str, df.columns)) + ' |'
    sep = '|' + '---|' * len(df.columns)
    return '\n'.join([head, sep] + ['| ' + ' | '.join(f(v) for v in r) + ' |' for r in df.itertuples(index=False)])


fin = L.load_sample()
panel = pd.read_csv(OUT / 'v5_event_panel.csv')
assert (panel['final_cik'].values == fin['final_cik'].values).all()
fin['dv'], fin['pre_sd'], fin['post_sd'] = panel['prim_dv'], panel['prim_pre_sd'], panel['prim_post_sd']
can = pd.read_csv('Data/processed/rebuild/CANONICAL_V3.csv', low_memory=False)
can['bdt'] = pd.to_datetime(can['breach_date'])
CP = {}
for f in sorted((OUT / 'constants_parts').glob('26[4-8].json')):
    CP[f.stem] = json.loads(f.read_text(encoding='utf-8'))

# =================================================================== A. sample
print('== A. sample and data')
led = Path('outputs/ESSAY2_SAMPLE_ATTRITION_LEDGER.md').read_text(encoding='utf-8').splitlines()
rec, evr = [], []
led = led[:next(i for i, ln in enumerate(led) if ln.startswith('## Decomposition'))]
for ln in led:
    cells = [c.strip() for c in ln.strip().strip('|').split('|')]
    if len(cells) == 4 and re.fullmatch(r'[\d,]+', cells[1] or 'x'):
        rec.append(dict(panel='A_record', step=cells[0], removed=cells[2].replace('—', '').replace('â€”', ''),
                        N=int(cells[1].replace(',', ''))))
    if len(cells) == 10 and cells[1] == 'events':
        evr.append(dict(panel='B_event', step=cells[0], N=int(cells[2]), treated=int(cells[3]),
                        t_orgs=int(cells[4]), t_parents=int(cells[5]), control=int(cells[6])))
att = pd.DataFrame(rec + evr)
att['removed'] = [np.nan if i in (0, len(rec)) else
                  (att.loc[i - 1, 'N'] - att.loc[i, 'N']) for i in range(len(att))]
assert list(att['N']) == [1054, 758, 524, 489, 489, 361, 361, 355, 351, 336, 335, 333], list(att['N'])
last = att.iloc[-1]
assert (last['N'], last['treated'], last['t_orgs'], last['t_parents']) == (333, 104, 36, 12)
assert (len(fin), int(fin[TREAT].sum()), fin.loc[fin[TREAT] == 1, 'org_name'].nunique(),
        fin.loc[fin[TREAT] == 1, 'final_cik'].nunique()) == (333, 104, 36, 12)
add('sample_attrition', att, 'Sample attrition', 'record 1,054 -> analytical 333',
    'outputs/ESSAY2_SAMPLE_ATTRITION_LEDGER.md (scripts/163 Phase A); cross-checked against t1',
    'Treated counts are defined on events only (treatment is assigned at Stage 4).')
gate('sample_attrition', 'sample_attrition.csv',
     cols=['N', 'removed', 'treated', 't_orgs', 't_parents', 'control'],
     reasons='step labels are the ledger\'s own wording')
for _, r in att.iterrows():
    k_ = re.sub(r'[^a-z0-9]+', '_', r['step'].lower()).strip('_')[:40]
    K[f'attr_{k_}_N'] = int(r['N'])
    for c in ['treated', 't_orgs', 't_parents', 'control']:
        if pd.notna(r.get(c)):
            K[f'attr_{k_}_{c}'] = int(r[c])

V = ['pre_sd', 'post_sd', 'dv', 'delay_w', 'firm_size_log', 'leverage', 'roa', 'health_breach',
     'prior_events']
drows = []
for grp, m in [('full', fin[TREAT] >= 0), ('treated', fin[TREAT] == 1), ('control', fin[TREAT] == 0)]:
    for v in V:
        s = fin.loc[m, v].astype(float).dropna()
        drows.append(dict(group=grp, variable=v, N=len(s), mean=s.mean(), sd=s.std(), median=s.median(),
                          p25=s.quantile(.25), p75=s.quantile(.75), min=s.min(), max=s.max()))
desc = pd.DataFrame(drows)
add('descriptives_v5', desc, 'Descriptive statistics (v5 outcome)', 'analytical 333',
    'scripts/269 from outputs/essay2_v5/v5_event_panel.csv (scripts/264) + t1',
    'pre_sd / post_sd: SD of market-adjusted daily abnormal returns over [-60,-11] / [+1,+20] '
    '(daily pp); dv = post_sd - pre_sd.')
wr = []
for v in V:
    a = fin.loc[fin[TREAT] == 1, v].astype(float).dropna()
    b = fin.loc[fin[TREAT] == 0, v].astype(float).dropna()
    t_ = stats.ttest_ind(a, b, equal_var=False)
    va, vb = a.var() / len(a), b.var() / len(b)
    dfw = (va + vb) ** 2 / (va ** 2 / (len(a) - 1) + vb ** 2 / (len(b) - 1))
    wr.append(dict(variable=v, diff=a.mean() - b.mean(), se=np.sqrt(va + vb), t=t_.statistic,
                   welch_df=dfw, p=t_.pvalue))
wdf = pd.DataFrame(wr)
add('descriptives_v5_differences', wdf, 'Treated minus control (Welch)', 'analytical 333',
    'scripts/269', 'Welch unequal-variance t tests; descriptive, not in the test ledger.')
for _, r in wdf.iterrows():
    K.update({f'desc_diff_{r["variable"]}': r['diff'], f'desc_diff_{r["variable"]}_p': r['p'],
              f'desc_diff_{r["variable"]}_t': r['t'], f'desc_diff_{r["variable"]}_df': r['welch_df']})
for _, r in desc.iterrows():
    K[f'desc_{r["group"]}_{r["variable"]}_mean'] = r['mean']
    K[f'desc_{r["group"]}_{r["variable"]}_sd'] = r['sd']
CV = ['dv', TREAT, 'pre_sd', 'delay_w', 'firm_size_log', 'leverage', 'roa', 'health_breach',
      'prior_events']
corr = fin[CV].astype(float).corr().reset_index().rename(columns={'index': 'variable'})
add('correlations_v5', corr, 'Correlation matrix (v5 outcome)', 'analytical 333', 'scripts/269',
    'Pearson correlations.')
K['corr_treat_size'] = float(fin[[TREAT, 'firm_size_log']].astype(float).corr().iloc[0, 1])
K['corr_dv_treat'] = float(fin[['dv', TREAT]].astype(float).corr().iloc[0, 1])

fin['nyear'] = pd.to_datetime(fin['reported_date']).dt.year
eby = fin.groupby('nyear')[TREAT].agg(total='size', treated='sum').reset_index().rename(columns={'nyear': 'year'})
eby['control'] = eby['total'] - eby['treated']
add('events_by_year', eby, 'Events by year (notification year)', 'analytical 333', 'scripts/269 from t1')
gate('events_by_year', 'events_by_year.csv')
for _, r in eby.iterrows():
    K[f'year_{int(r["year"])}_total'], K[f'year_{int(r["year"])}_treated'] = int(r['total']), int(r['treated'])
one_kind = eby[(eby['treated'] == 0) | (eby['control'] == 0)]
K.update(years_single_kind=len(one_kind), years_single_kind_events=int(one_kind['total'].sum()),
         years_single_kind_treated=int(one_kind['treated'].sum()))

# missingness on the 355 base (permno-matched, notified by 2024-12-31)
base = can[can['permno'].notna() & (pd.to_datetime(can['reported_date'], errors='coerce') <= '2024-12-31')]
assert len(base) == 355, len(base)
lost_win = int(att.loc[att['step'].str.contains('Volatility'), 'N'].pipe(
    lambda s: att.loc[att['step'].str.contains('2024'), 'N'].iloc[0] - s.iloc[0]))
art = base['org_name'].str.contains('ATT-Breach|ATT-Security', regex=True, na=False)
mrows = [dict(variable='e2_vol_change (volatility windows)', missing=lost_win)]
for v in ['firm_size_log', 'leverage', 'roa']:
    mrows.append(dict(variable=v, missing=int(base[v].isna().sum())))
mrows += [dict(variable='disclosure_delay_days', missing=int(base['disclosure_delay_days'].isna().sum())),
          dict(variable='health_breach', missing=int(base['health_breach'].isna().sum())),
          dict(variable='prior_breaches_total', missing=int(base['prior_breaches_total'].isna().sum())),
          dict(variable='ATT_artifact_records (excluded at final step)', missing=int(art.sum()))]
miss = pd.DataFrame(mrows)
miss['share'] = miss['missing'] / len(base)
add('missingness_precase', miss, 'Missingness before the complete-case restriction', 'CRSP-matched 355',
    'scripts/269 from CANONICAL_V3; window losses from the attrition ledger (scripts/163)',
    '355 - 4 - 15 - 1 - 2 = 333 (a missing covariate is missing for all three Compustat variables).')
gate('missingness_precase', 'missingness_precase.csv', cols=['missing', 'share'],
     reasons='variable label for the window row reworded')
K.update(miss_base=355, miss_windows=lost_win, miss_compustat=int(base['firm_size_log'].isna().sum()),
         miss_delay=int(base['disclosure_delay_days'].isna().sum()), miss_att=int(art.sum()))
tr7 = fin  # placeholder to keep names stable
cov = pd.read_csv(OUT / 'v5_t01_coverage.csv')
add('coverage_drops', cov, '80% coverage rule: events dropped by window', 'analytical 333',
    'outputs/essay2_v5/v5_t01_coverage.csv (scripts/264)')

# ============================================== B. prior-spec decomposition
print('== B. prior-specification decomposition')
OXS = ['return_volatility_pre', 'firm_size_log', 'leverage', 'roa', 'disclosure_delay_days',
       'prior_breaches_total', 'health_breach']
old = pd.read_csv('Data/processed/FINAL_DISSERTATION_DATASET_ENRICHED.csv', low_memory=False)
s2 = pd.read_csv('Data/processed/rebuild/stage2_signed.csv', low_memory=False)
key = ['org_name', 'breach_date', 'reported_date']
for df_ in (old, s2):
    for c in ['breach_date', 'reported_date']:
        df_[c] = pd.to_datetime(df_[c], errors='coerce').dt.strftime('%Y-%m-%d')
old2 = old.merge(s2.drop_duplicates(subset=key)[key + ['final_cik']], on=key, how='left')
EQUITY_PARENT = {1040573: 1166691, 1512267: 1166691, 1457937: 1105705}   # scripts/154:185
old2['final_cik_rep'] = old2['final_cik'].map(
    lambda c: EQUITY_PARENT.get(int(c), int(c)) if pd.notna(c) else np.nan)
treated_ciks = set(can.loc[can[TREAT] == 1, 'final_cik'].astype(int))
old2['form499_family'] = old2['final_cik_rep'].isin(treated_ciks).astype(float)
old2['form499_unrepaired'] = old2['final_cik'].isin(treated_ciks).astype(float)
old2['sic_ind'] = pd.to_numeric(old2['sic'], errors='coerce').isin([4813, 4841, 4899]).astype(float)
old2['name_token'] = old2['fcc_reportable'].astype(float)
oc = old2[old2['has_crsp_data'] == True].dropna(subset=['volatility_change'] + OXS).copy()
oc['q'] = pd.qcut(oc['firm_size_log'], 4, labels=[1, 2, 3, 4]).astype(int)
oc['ev_key'] = np.where(oc['final_cik_rep'].notna(), 'c' + oc['final_cik_rep'].astype('Int64').astype(str),
                        'o' + oc['org_name'].astype(str)) + ' ' + oc['breach_date']
assert len(oc) == 891, len(oc)

# event level (scripts/166 B1 (iii)/(iv): record-modal SIC within 3 days)
s2['sic_num'] = pd.to_numeric(s2['sic'], errors='coerce')
s2['bdt'] = pd.to_datetime(s2['breach_date'], errors='coerce')
sic_map = {c: g.dropna(subset=['sic_num']) for c, g in s2.dropna(subset=['final_cik']).groupby('final_cik')}


def event_sic_treated(cik, bdt):
    g = sic_map.get(cik)
    if g is None or not len(g):
        return np.nan
    g = g.assign(_d=(g['bdt'] - bdt).abs())
    near = g[g['_d'] <= timedelta(days=3)]
    pool = near if len(near) else g.nsmallest(1, '_d')
    return float(any(int(s_) in {4813, 4841, 4899} for s_ in pool['sic_num'].dropna()))


ev = can.copy()
ev['sic_treated'] = [event_sic_treated(c, b) for c, b in zip(ev['final_cik'], ev['bdt'])]
ev['_f'] = ev[TREAT].astype(float)
ev['final_cik_rep'] = ev['final_cik']


def fourpanel(d, tcol, label):
    d = d.dropna(subset=[tcol, 'volatility_change'] + OXS).copy()
    if 'q' not in d or label.startswith(('iii', 'iv')):
        d['q'] = pd.qcut(d['firm_size_log'], 4, labels=[1, 2, 3, 4]).astype(int)
    rows = []
    for cell, sub in [('main', d)] + [(f'Q{q}', d[d['q'] == q]) for q in (1, 2, 3, 4)]:
        X = sm.add_constant(sub[[tcol] + OXS].astype(float))
        f = sm.OLS(sub['volatility_change'].astype(float), X).fit(cov_type='HC3', use_t=True)
        tr = sub[sub[tcol] == 1]
        rows.append(dict(panel=label, cell=cell, coef=f.params[tcol], se=f.bse[tcol],
                         t=f.tvalues[tcol], p=f.pvalues[tcol], cellN=len(sub), treatedN=len(tr),
                         t_orgs=tr['org_name'].nunique(), t_parents=tr['final_cik'].nunique()))
    rows.append(dict(panel=label, cell='Q1_minus_Q4_spread', coef=rows[1]['coef'] - rows[4]['coef']))
    return rows


fp = pd.DataFrame(fourpanel(oc, 'sic_ind', 'i_industry_codes_records')
                  + fourpanel(oc, 'form499_family', 'ii_form499_repaired')
                  + fourpanel(ev, 'sic_treated', 'iii_dedup_sic')
                  + fourpanel(ev, '_f', 'iv_dedup_form499')
                  + fourpanel(oc, 'name_token', 'footnote_prior_name_token')
                  + fourpanel(oc, 'form499_unrepaired', 'footnote_ii_unrepaired'))
add('four_panel_decomposition', fp, 'Four-panel decomposition: industry codes against Form 499',
    'prior-spec 891 records / 339 dedup events',
    'scripts/269 (scripts/166 B1 machinery; industry-code panel = record SIC in {4813, 4841, 4899})',
    'HC3, prior-specification controls; quartiles of the prior dataset\'s firm_size_log (market '
    'value, see size-variable reconciliation) for panels i/ii and footnotes; panels iii/iv use '
    'CANONICAL_V3 events and its legacy breach-anchored volatility_change.')
gate('four_panel_decomposition', 'four_panel_decomposition.csv',
     reasons='panels iii/iv use CANONICAL_V3 volatility_change, which the 10/2 CRSP de-duplication fix '
             '(dd8b564) changed for three treated events (CenturyLink 2020, DISH x2); panels i/ii and '
             'the footnotes read the 1,054-record prior dataset, which the fix did not touch')
for _, r in fp.iterrows():
    if pd.notna(r['coef']):
        K[f'fp_{r["panel"]}_{r["cell"]}_coef'] = r['coef']
    if pd.notna(r.get('p')):
        K[f'fp_{r["panel"]}_{r["cell"]}_p'] = r['p']
        K[f'fp_{r["panel"]}_{r["cell"]}_treatedN'] = int(r['treatedN'])
        K[f'fp_{r["panel"]}_{r["cell"]}_t_parents'] = int(r['t_parents'])

rpe = oc.groupby('ev_key').size()
rp = [('summary', 'records', len(oc)), ('summary', 'events', len(rpe)),
      ('summary', 'mean_records_per_event', rpe.mean()), ('summary', 'median_records_per_event', rpe.median()),
      ('summary', 'max_records_per_event', rpe.max()),
      ('summary', 'events_with_more_than_one_record', int((rpe > 1).sum())),
      ('summary', 'records_in_multi_record_events', int(rpe[rpe > 1].sum()))]
rp += [('distribution', f'events_with_{k}_records', int(v)) for k, v in rpe.value_counts().sort_index().items()]
rp += [('largest', k, int(v)) for k, v in rpe.sort_values(ascending=False, kind='stable').head(25).items()]
rpt = pd.DataFrame(rp, columns=['panel', 'item', 'value'])
add('records_per_event', rpt, 'Records per event (prior-spec panel)', 'prior-spec 891 records',
    'scripts/269', 'Event key: post-reparenting parent CIK (c...) or, if unresolved, organization (o...), plus breach date.')
gate('records_per_event', 'records_per_event.csv', cols=['value'],
     reasons='ordering of tied "largest" rows may differ')
K.update(rpe_records=len(oc), rpe_events=len(rpe), rpe_multi_events=int((rpe > 1).sum()),
         rpe_multi_records=int(rpe[rpe > 1].sum()), rpe_max=int(rpe.max()))

q1 = oc[oc['q'] == 1]
comp = []
for lab, m in [('stayed', (q1['sic_ind'] == 1) & (q1['form499_family'] == 1)),
               ('dropped', (q1['sic_ind'] == 1) & (q1['form499_family'] == 0)),
               ('added', (q1['sic_ind'] == 0) & (q1['form499_family'] == 1)),
               ('never_treated', (q1['sic_ind'] == 0) & (q1['form499_family'] == 0))]:
    s = q1.loc[m]
    comp.append(dict(component=lab, N_records=len(s), N_events=s['ev_key'].nunique(),
                     mean=s['volatility_change'].mean() if len(s) else np.nan,
                     sd=s['volatility_change'].std() if len(s) > 1 else np.nan))
add('q1_transition_components', pd.DataFrame(comp), 'The Q1 transition (prior market-cap partition)',
    'prior-spec 891 records', 'scripts/269')
gate('q1_transition_components', 'q1_transition_components.csv',
     reasons='N_records, means and SDs match; the never-treated event count differs by one (142 vs 141) under every '
             'committed event key (post-reparenting CIK, stage-2 CIK, legacy CIK); the retired emitter event key '
             'was never committed and cannot be recovered')
qr = q1.loc[(q1['sic_ind'] != q1['form499_family'])].assign(
    direction=lambda d: np.where(d['form499_family'] == 1, 'added', 'dropped'))
qrt = pd.DataFrame(dict(direction=qr['direction'], organization=qr['org_name'],
                        parent_cik=qr['final_cik_rep'].astype('Int64'),
                        volatility_change=qr['volatility_change'])).sort_values(['direction', 'organization'])
add('q1_transition_records', qrt, 'Q1 transition records', 'prior-spec 891 records', 'scripts/269')
gate('q1_transition_records', 'q1_transition_records.csv', sort_by=['organization', 'volatility_change'],
     reasons='row order')
K.update(q1_added_records=int((qrt['direction'] == 'added').sum()),
         q1_added_parents=int(qrt.loc[qrt['direction'] == 'added', 'parent_cik'].nunique()),
         q1_added_mean=float(comp[2]['mean']), q1_never_mean=float(comp[3]['mean']))

mis = oc[(oc['sic_ind'] == 1) & (oc['form499_family'] == 0)]
mrec = pd.DataFrame(dict(organization=mis['org_name'], source_sic=pd.to_numeric(mis['sic']).astype(int),
                         parent_cik=mis['final_cik_rep'].astype('Int64').astype(str).replace('<NA>', 'unresolved'),
                         prior_spec_quartile_mktcap=mis['q'], ln_mktcap_as_found=mis['firm_size_log'],
                         volatility_change=mis['volatility_change'], breach_date=mis['breach_date']))
add('misclassified_records', mrec, 'The misclassified group, per record', 'prior-spec 891 records', 'scripts/269')
gate('misclassified_records', 'misclassified_records.csv', sort_by=['organization'])
groups = {
    'misclassified_repaired': (oc['sic_ind'] == 1) & (oc['form499_family'] == 0),
    'concordant_registrants': (oc['sic_ind'] == 1) & (oc['form499_family'] == 1),
    'control': (oc['sic_ind'] == 0) & (oc['form499_family'] == 0),
    'missed_by_industry_codes': (oc['sic_ind'] == 0) & (oc['form499_family'] == 1),
    'misclassified_prerepair_SENSITIVITY': (oc['sic_ind'] == 1) & (oc['form499_unrepaired'] == 0),
}
gc = []
for g_, m in groups.items():
    s = oc.loc[m]
    gc.append(dict(group=g_, N=len(s), orgs=s['org_name'].nunique(), mean_ln_mktcap=s['firm_size_log'].mean(),
                   sd_ln_mktcap=s['firm_size_log'].std(), mean_vol_change=s['volatility_change'].mean(),
                   sd_vol_change=s['volatility_change'].std()))
add('misclassified_group_comparisons', pd.DataFrame(gc), 'Group comparisons', 'prior-spec 891 records', 'scripts/269')
gate('misclassified_group_comparisons', 'misclassified_group_comparisons.csv')
ct = []
for a_, b_ in [('misclassified_repaired', 'concordant_registrants'), ('misclassified_repaired', 'control')]:
    for v in ['firm_size_log', 'volatility_change']:
        A, B = oc.loc[groups[a_], v], oc.loc[groups[b_], v]
        t_ = stats.ttest_ind(A, B, equal_var=False)
        ct.append(dict(contrast=f'misclassified_vs_{b_.split("_")[0]}', variable=v, diff=A.mean() - B.mean(),
                       se=np.sqrt(A.var() / len(A) + B.var() / len(B)), t=t_.statistic, p=t_.pvalue))
add('misclassified_group_contrasts', pd.DataFrame(ct), 'Group comparison contrasts (Welch)',
    'prior-spec 891 records', 'scripts/269', 'Two records; the tests have about two degrees of freedom.')
gate('misclassified_group_contrasts', 'misclassified_group_contrasts.csv')
K.update(mis_records=len(mis), missed_records=int(groups['missed_by_industry_codes'].sum()),
         missed_mean_vol=float(oc.loc[groups['missed_by_industry_codes'], 'volatility_change'].mean()),
         disagree_records=int((oc['sic_ind'] != oc['form499_family']).sum()),
         missed_q4_records=int((groups['missed_by_industry_codes'] & (oc['q'] == 4)).sum()))

gg = pd.read_csv(T2 / 't31_gradient_grid.csv')
ggs = gg.groupby('anchor').agg(n_specs=('q1', 'size'), q1_gt_q4=('q1_gt_q4', 'sum'),
                               monotone_stepdown=('monotone_down', 'sum')).reset_index()
ggs = pd.concat([ggs, pd.DataFrame([dict(anchor='TOTAL', n_specs=ggs['n_specs'].sum(),
                                          q1_gt_q4=ggs['q1_gt_q4'].sum(),
                                          monotone_stepdown=ggs['monotone_stepdown'].sum())])])
add('gradient_grid', ggs, 'Gradient across the corrected-data specification grid',
    'analytical (48 window-specs, committed raw-return DV)', 'outputs/tables/essay2_v2/t31_gradient_grid.csv (scripts/166)')
gate('gradient_grid', 'gradient_grid.csv')
K['gradient_q1_gt_q4'] = int(ggs['q1_gt_q4'].iloc[-1])

# size-variable reconciliation: the prior dataset's firm_size_log against
# ln total assets (the prior dataset's own `assets` column) and ln market value
# (CRSP |PRC| x SHROUT on the last trading day on/before the breach; legacy CIK ->
# ticker via the committed cik_ticker_map, ticker -> permno by name-date window)
o3 = old[old['firm_size_log'].notna() & (old['has_crsp_data'] == True)].copy()
o3['bdt'] = pd.to_datetime(o3['breach_date'])
cmap = pd.read_csv('Data/edgar/cik_ticker_map_normalized.csv').drop_duplicates('cik').set_index('cik')['ticker']
tpm0 = pd.read_csv('Data/wrds/ticker_permno_mapping.csv', parse_dates=['namedt', 'nameendt'])
tg0 = {t: g for t, g in tpm0.groupby('ticker')}
crsp_pm = L.crsp_daily.load(['permno', 'date', 'prc', 'shrout'], verbose=False)
crsp_pm['date'] = pd.to_datetime(crsp_pm['date'])
cpg = {p: g.sort_values('date') for p, g in crsp_pm.groupby('permno')}
mv = []
for c, b in zip(o3['cik'], o3['bdt']):
    val = np.nan
    g = tg0.get(cmap.get(c))
    if g is not None:
        w = g[(g['namedt'] <= b) & (g['nameendt'] >= b)]
        cc = cpg.get(int(w.iloc[0]['permno'])) if len(w) else None
        if cc is not None:
            pr = cc[cc['date'] <= b]
            if len(pr) and pr.iloc[-1]['shrout'] > 0 and abs(pr.iloc[-1]['prc']) > 0:
                val = np.log(abs(pr.iloc[-1]['prc']) * pr.iloc[-1]['shrout'] / 1000)
    mv.append(val)
o3['ln_market_cap'] = mv
o3['ln_total_assets'] = np.log(o3['assets'].where(o3['assets'] > 0))
sv = []
for c in ['ln_market_cap', 'ln_total_assets']:
    d = o3.dropna(subset=[c])
    f = sm.OLS(d['firm_size_log'], sm.add_constant(d[c])).fit()
    gap = (d['firm_size_log'] - d[c]).abs()
    sv.append(dict(candidate=c, N=len(d), slope=f.params[c], intercept=f.params['const'], R2=f.rsquared,
                   share_within_010=(gap <= .10).mean(), share_within_025=(gap <= .25).mean()))
add('size_variable_reconciliation', pd.DataFrame(sv), 'Size-variable reconciliation',
    'prior-spec CRSP records with a firm_size_log',
    'scripts/269 (prior dataset assets; CRSP |PRC| x SHROUT via cik_ticker_map and ticker_permno_mapping)')
gate('size_variable_reconciliation', 'size_variable_reconciliation.csv',
     reasons='ln_total_assets: N, slope, intercept and R2 reproduce exactly (prior dataset assets column, CRSP '
             'records); the within-0.10/0.25 shares differ because the retired emitter compared on an undocumented '
             'scale. ln_market_cap: the retired CIK-to-security link was never committed; the committed '
             'cik_ticker_map resolves fewer records (674 vs 845), so its row is a re-derivation (same conclusion: '
             'firm_size_log is market value, slope ~1, R2 ~.86)')
K.update(sizerec_mktcap_slope=sv[0]['slope'], sizerec_mktcap_r2=sv[0]['R2'], sizerec_assets_slope=sv[1]['slope'],
         sizerec_assets_r2=sv[1]['R2'])

# identifier collisions: the six verified sinks (legacy CIKs from the Gate 1 audit,
# outputs/rebuild/GATE1_SUMMARY.md), with organizations and canonical status recomputed
SINKS = [200406, 1034054, 1437107, 1004980, 1841666, 732717]
idr = []
can_ciks = set(can['final_cik'].astype(int))
for c in SINKS:
    orgs = sorted(old.loc[old['cik'] == c, 'org_name'].dropna().unique())
    in_can = can['org_name'].isin(orgs).sum()
    idr.append(dict(legacy_cik=c, organizations_absorbed='; '.join(orgs), n_records=int((old['cik'] == c).sum()),
                    ticker_for_cik=cmap.get(c, ''), canonical_events_with_these_names=int(in_can),
                    legacy_cik_is_canonical_parent=c in can_ciks))
add('identifier_collisions', pd.DataFrame(idr), 'Identifier-collision inventory (legacy CIKs)',
    'legacy annotation (six verified sinks; floor, not census)',
    'scripts/269 from the 1,054-record prior dataset, CANONICAL_V3 and cik_ticker_map; sink list from '
    'outputs/rebuild/GATE1_SUMMARY.md', 'The descriptive columns of the retired table (returns drawn, detection '
    'route) were hand annotations and are not regenerated; the organizations and canonical status are.')
gate('identifier_collisions', 'identifier_collisions.csv', cols=['legacy_cik', 'organizations_absorbed'],
     reasons='organization lists here are every prior-dataset name on the CIK; the retired table listed a curated subset')
K['collision_sinks'] = len(SINKS)
K['collision_max_orgs'] = int(max(len(r['organizations_absorbed'].split('; ')) for r in idr))

# recycled tickers: the scripts/155 pre-guard fallback (last earlier name row)
tpm = pd.read_csv('Data/wrds/ticker_permno_mapping.csv', parse_dates=['namedt', 'nameendt'])
tg = {t: g.sort_values('namedt') for t, g in tpm.groupby('ticker')}
rr = []
for _, e in can.iterrows():
    t = cmap.get(int(e['final_cik']))
    g = tg.get(t)
    if g is None:
        continue
    b = e['bdt']
    if ((g['namedt'] <= b) & (g['nameendt'] >= b)).any():
        continue
    prev = g[g['nameendt'] < b]
    if not len(prev):
        continue
    p = prev.iloc[-1]
    if p['nameendt'] >= b - timedelta(days=7) or p['nameendt'] == tpm['nameendt'].max():
        continue
    later = g[g['namedt'] > b]
    rr.append(dict(organization=e['org_name'], event_date=e['breach_date'], assigned_permno=int(p['permno']),
                   assigned_security=p['comnam'], ticker=t, ticker_end_for_assigned=p['nameendt'].date(),
                   later_owner_in_mapping=(f'{int(later.iloc[0]["permno"])} ({later.iloc[0]["comnam"]})'
                                           if len(later) else 'none'),
                   permno_now=e['permno'], has_crsp_data=e['has_crsp_data']))
rrt = pd.DataFrame(rr)
add('recycled_tickers', rrt, 'Ticker-recycling misidentifications (blocked by the 9/6 fallback guard)',
    'canonical 489', 'scripts/269 (scripts/155 fallback rule re-applied to the committed ticker map)',
    'Each row is an event the pre-guard fallback would have matched to an earlier, unrelated owner of the '
    'ticker; permno_now / has_crsp_data show all are unresolved in the committed chain.')
gate('recycled_tickers', 'identifier_collisions_recycled_tickers.csv',
     cols=['organization', 'event_date', 'assigned_permno', 'assigned_security', 'ticker'],
     sort_by=['event_date'], reasons='the retired table\'s correct_permno column was a hand annotation')
K['recycled_ticker_events'] = len(rrt)

# ============================================== C. classification
print('== C. classification and treatment')
root = ET.parse('Data/edgar/form499_registry.xml').getroot()
recs = []
for f_ in root:
    info = f_.find('Filer_ID_Info')
    if info is None:
        continue
    recs.append(dict(legal_name=info.findtext('Legal_Name') or '', dba=(info.findtext('doing_business_as') or ''),
                     holding=info.findtext('holding_company') or '', FRN=info.findtext('FRN') or '',
                     start=info.findtext('start_date') or '', end=info.findtext('end_date') or 'open',
                     type=info.findtext('Principal_Communications_Type') or '',
                     usf=info.findtext('USF_Contributor') or ''))
reg = pd.DataFrame(recs)
K['registry_records'] = len(reg)
src164 = Path('scripts/164_essay2_rule_delay_classification.py').read_text(encoding='utf-8')
FAMILY = None
for node in ast.parse(src164).body:
    if isinstance(node, ast.Assign) and any(getattr(t, 'id', '') == 'FAMILY' for t in node.targets):
        FAMILY = ast.literal_eval(node.value)
assert FAMILY and len(FAMILY) == 12
fam_rows = []
for cik, kws in FAMILY.items():
    pat = '|'.join(re.escape(k.strip()) for k in kws)
    m = reg[reg[['legal_name', 'dba', 'holding']].apply(lambda c: c.str.upper().str.contains(pat, regex=True)).any(axis=1)]
    evs = fin[(fin[TREAT] == 1) & (fin['final_cik'] == cik)]
    span = f'{evs["breach_date"].min()}..{evs["breach_date"].max()}'
    for _, r in m.iterrows():
        fam_rows.append(dict(parent_cik=cik, legal_name=r['legal_name'], FRN=r['FRN'], start=r['start'],
                             end=r['end'], type=r['type'], usf=r['usf'], holding=r['holding'],
                             end_before_start=(r['end'] != 'open' and r['end'] < r['start']) or '',
                             events_in_sample=len(evs), event_span=span))
frm = pd.DataFrame(fam_rows)
assert frm.groupby('parent_cik')['events_in_sample'].first().sum() == 104
add('form499_registry_matches', frm, 'Form 499 registry matches for treated parent entities',
    'analytical 333 (12 parents, 104 events)',
    'scripts/269: Data/edgar/form499_registry.xml x scripts/164 FAMILY keywords (lifted by ast)',
    'Family = registry records whose legal name, dba or holding company contains a scripts/164 keyword.')
gate('form499_registry_matches', 'form499_registry_matches.csv', cols=['parent_cik'],
     reasons='family keyword sets: the retired table used a scratchpad heuristic (FAMS, never committed); this '
             'table uses the committed scripts/164 FAMILY lists, so per-parent record counts differ')
K['registry_family_records'] = len(frm)

src154 = Path('scripts/154_rebuild_s4_treatment.py').read_text(encoding='utf-8')
ADJ = EQP = None
for node in ast.parse(src154).body:
    if isinstance(node, ast.Assign) and getattr(node.targets[0], 'id', '') == 'ADJ':
        ADJ = ast.literal_eval(node.value)
    if isinstance(node, ast.Assign) and getattr(node.targets[0], 'id', '') == 'EQUITY_PARENT':
        EQP = ast.literal_eval(node.value)
adj = [dict(kind='stage4_pattern', pattern=a[0] + (f' (on/after {a[3][1]})' if len(a) == 4 else ''),
            direction='FORCE TREATED' if a[1] else 'FORCE EXCLUDED', basis=a[2]) for a in ADJ]
adj += [dict(kind='equity_parent', pattern=f'{k} -> {v[0]}', direction='RE-PARENT', basis=v[1]) for k, v in EQP.items()]
adjt = pd.DataFrame(adj)
add('treatment_adjudications', adjt, 'Treatment adjudications', 'canonical 489',
    'scripts/154 ADJ and EQUITY_PARENT (lifted verbatim by ast)')
gate('treatment_adjudications', 'treatment_adjudications.csv', cols=['kind', 'direction'],
     reasons='basis text is 154\'s full rationale; the retired table paraphrased it')
K.update(adjudication_rules=len(ADJ), adjudication_names=len({a[0] for a in ADJ}), equity_parent_maps=len(EQP))

# industry-code conventions (scripts/163:188-208 sich rule)
csh = pd.read_csv('Data/wrds/compustat_annual.csv', usecols=['tic', 'datadate', 'sich'])
csh['datadate'] = pd.to_datetime(csh['datadate'])
shg = {t: g.sort_values('datadate') for t, g in csh.dropna(subset=['tic']).groupby('tic')}
MAN = {'S': 4813, 'CTL': 4813}


def sich_for(t, b):
    g = shg.get(t)
    if g is not None:
        p = g[(g['datadate'] < b) & (g['datadate'] >= b - timedelta(days=550))]
        if len(p) and pd.notna(p.iloc[-1]['sich']):
            return int(p.iloc[-1]['sich'])
    return MAN.get(t, np.nan)


can['sich'] = [sich_for(t, b) for t, b in zip(can['matched_ticker'], can['bdt'])]
tt = can.dropna(subset=['sich']).copy()
CONV = {'published_regulated_dummy_4812_4813': (lambda s: s in (4812, 4813), 'misses every cable registrant'),
        'prior_spec_4813_4841_4899': (lambda s: s in (4813, 4841, 4899), 'misses every wireless carrier'),
        'tuned_4812_4813_4841_4899': (lambda s: s in (4812, 4813, 4841, 4899), 'post-hoc; boundary-blind'),
        'full_range_4800_4899': (lambda s: 4800 <= s <= 4899, 'admits broadcasters')}
P = set(tt.loc[tt[TREAT] == 1, 'final_cik'])
cr, er = [], []
for name, (fn, fail) in CONV.items():
    c = tt['sich'].astype(int).map(fn).astype(int)
    tp = set(tt.loc[(c == 1) & (tt[TREAT] == 1), 'final_cik'])
    wrong = set(tt.loc[(c == 1) & (tt[TREAT] == 0), 'final_cik'])
    cr.append(dict(convention=name, N_testable=len(tt), agree=int((c == tt[TREAT]).sum()),
                   agree_pct=100 * (c == tt[TREAT]).mean(), FP=int(((c == 1) & (tt[TREAT] == 0)).sum()),
                   FN=int(((c == 0) & (tt[TREAT] == 1)).sum()), parents_identified=len(tp),
                   parents_missed=len(P - tp), parents_wrongly_included=len(wrong - set(can.loc[can[TREAT] == 1, 'final_cik'])),
                   parent_agree_pct=100 * len(tp) / len(P), characteristic_failure=fail))
    for et, m in [('FALSE_POSITIVE', (c == 1) & (tt[TREAT] == 0)), ('FALSE_NEGATIVE', (c == 0) & (tt[TREAT] == 1))]:
        for (o, p_, s_), g in tt[m].groupby(['org_name', 'final_cik', 'sich']):
            er.append(dict(convention=name, error_type=et, organization=o, parent_cik=p_, sich=int(s_), events=len(g)))
crt = pd.DataFrame(cr)
add('sic_conventions_vs_form499', crt, 'Industry-code conventions against Form 499 registration',
    f'canonical 489 ({len(tt)} testable)', 'scripts/269 (sich rule of scripts/163:188-208)')
gate('sic_conventions_vs_form499', 'sic_conventions_vs_form499.csv',
     cols=['convention', 'N_testable', 'agree', 'agree_pct', 'FP', 'FN', 'parents_identified', 'parents_missed',
           'parent_agree_pct'], reasons='the failure-description column is prose')
for _, r in crt.iterrows():
    k_ = r['convention'].split('_')[0]
    K.update({f'sic_{k_}_agree_pct': r['agree_pct'], f'sic_{k_}_parents_identified': int(r['parents_identified']),
              f'sic_{k_}_FP': int(r['FP']), f'sic_{k_}_FN': int(r['FN'])})
K.update(sic_testable=len(tt), sic_treated_parents_testable=len(P),
         sic_treated_testable=int(tt[TREAT].sum()), sic_treated_total=int(can[TREAT].sum()))
ert = pd.DataFrame(er)
ert = ert[ert['convention'].isin(['published_regulated_dummy_4812_4813', 'tuned_4812_4813_4841_4899'])]
ert = ert.sort_values(['convention', 'error_type', 'organization'], ascending=[True, False, True])
add('sic_convention_errors', ert, 'Classification errors by named organization',
    f'canonical 489 ({len(tt)} testable)', 'scripts/269')
gate('sic_convention_errors', 'sic_convention_errors.csv', sort_by=['convention', 'error_type', 'organization'])

# sich vs the breach records' own (curated) SIC, treated families + Roku
s2['final_cik_rep'] = s2['final_cik'].map(lambda c: EQUITY_PARENT.get(int(c), int(c)) if pd.notna(c) else np.nan)
fam_parents = sorted(set(can.loc[can[TREAT] == 1, 'final_cik'].astype(int))) + [1428439]
svc = []
for p in fam_parents:
    e = can[can['final_cik'] == p]
    sic_cur = sorted(set(pd.to_numeric(s2.loc[s2['final_cik_rep'] == p, 'sic'], errors='coerce').dropna().astype(int)))
    svc.append(dict(parent_cik=p, organization=e['org_name'].value_counts().index[0],
                    tickers='; '.join(sorted(e['matched_ticker'].dropna().unique())),
                    sich='; '.join(str(int(x)) for x in sorted(e['sich'].dropna().unique())),
                    curated_sic='; '.join(map(str, sic_cur)),
                    form499='treated' if e[TREAT].max() == 1 else 'control/excluded'))
svt = pd.DataFrame(svc)
svt['sources_disagree'] = svt['sich'] != svt['curated_sic']
add('sich_vs_curated_sic', svt, 'Compustat sich against the breach records\' own SIC', 'canonical 489',
    'scripts/269 (stage2_signed record SIC; Compustat sich by the scripts/163 rule)')
FAMLAB = {732717: 'AT&T', 1283699: 'T-Mobile', 732712: 'Verizon', 20520: 'Frontier', 1098659: 'Mediacom',
          18926: 'CenturyLink', 1091667: 'Charter', 1632127: 'Cable One', 1609711: 'GoDaddy', 1447669: 'Twilio',
          1001082: 'DISH', 1428439: 'Roku'}
gate_join('sich_vs_curated_sic', 'sich_vs_curated_sic.csv', 'organization', ['sich', 'curated_sic', 'form499'],
          'the retired table grouped 12 families by hand (Comcast merged into the Cable One row, Sprint and '
          'Altice omitted); here one row per canonical treated parent plus Roku',
          mine=svt.assign(organization=svt['parent_cik'].map(FAMLAB)).dropna(subset=['organization']))
tm = svt[svt['parent_cik'] == 1283699].iloc[0]
K.update(tmobile_sich=tm['sich'], tmobile_curated_sic=tm['curated_sic'],
         sich_sources_disagree_treated=int(svt.loc[svt['form499'] == 'treated', 'sources_disagree'].sum()),
         sich_treated_parents=int((svt['form499'] == 'treated').sum()))

ut = can[(can[TREAT] == 1) & can['sich'].isna()].copy()
ut['reason'] = np.where(ut['matched_ticker'].isna(), 'no matched ticker',
                        'ticker but no Compustat row in 550-day window')
utt = ut[['org_name', 'final_cik', 'reported_date', 'reason']].rename(
    columns={'org_name': 'organization', 'final_cik': 'parent_cik'}).sort_values(['parent_cik', 'reported_date'])
utt['reported_date'] = utt['reported_date'].astype(str).str[:10]
add('treated_outside_comparison', utt, 'Treated events outside the classification comparison',
    f'canonical 489 (comparison covers {len(tt)}/489, {int(tt[TREAT].sum())}/{int(can[TREAT].sum())} treated)',
    'scripts/269')
gate('treated_outside_comparison', 'sich_unavailable_treated.csv', cols=['organization', 'parent_cik', 'reason'],
     sort_by=['parent_cik', 'reported_date'])
tmo = ut[ut['final_cik'] == 1283699]
K.update(outside_treated=len(ut), outside_parents=ut['final_cik'].nunique(),
         outside_tmobile=len(tmo), outside_tmobile_no_ticker=int(tmo['matched_ticker'].isna().sum()),
         outside_tmobile_no_compustat=int(tmo['matched_ticker'].notna().sum()),
         tmobile_canonical_no_permno=int(((can['final_cik'] == 1283699) & can['permno'].isna()).sum()))

# ============================================== D-F. results (v5 outputs)
print('== D-F. results from scripts/264-268')


def v5(name):
    return pd.read_csv(OUT / name)


RES = [
    ('nested_models', 'v5_t02_nested_models.csv', 'Nested models M1-M4 (v5 outcome)', 'analytical 333'),
    ('inference_ladder', 'v5_t03_ladder.csv', 'Inference ladder, eight rungs (primary M4)', 'analytical 333 (G=82, G1=12)'),
    ('design_resolution', 'v5_t04_design_resolution.csv', 'Design resolution', 'analytical 333'),
    ('dynamic_path', 'v5_t05_dynamic_path.csv', 'Dynamic path (BH family of 3)', 'analytical 333'),
    ('benchmarks', 'v5_t06_benchmarks.csv', 'Benchmark robustness: market model and FF3', 'analytical 333 (model benchmarks need 80% of [-250,-30])'),
    ('estimation_contamination', 'v5_t06b_estimation_contamination.csv', 'Estimation windows containing an earlier event at the same parent', 'analytical 333'),
    ('alternatives_bridge', 'v5_t07_alternatives.csv', 'Alternative windows and the bridge to the raw-return outcome', 'analytical 333'),
    ('v4_date_sensitivity', 'v5_t08_v4_dates.csv', 'v4 date sensitivity (report only)', 'analytical 333 (+1 under the Sprint date)'),
    ('announcement_family', 'v5_t09_announcement.csv', 'Announcement-window family (BH family of 4)', 'analytical 333 / earnings announcements'),
    ('announcement_ladder', 'v5_t09b_announcement_ladder.csv', 'Announcement-window test, full ladder', 'analytical 333'),
    ('announcement_buildup', 'v5_t09c_announcement_buildup.csv', 'Announcement differential: raw-to-adjusted buildup (CV3)', 'analytical 333'),
    ('placebo_dates', 'v5_t11_placebo.csv', 'Placebo dates (200 draws, seed 499)', 'analytical 333'),
    ('earnings_benchmark', 'v5_t10_earnings_benchmark.csv', 'Earnings benchmark', 'sample securities\' earnings dates'),
    ('size_quartiles', 'v5_t12_size_quartiles.csv', 'Size quartiles (ln total assets; BH family of 4)', 'analytical 333'),
    ('fixed_effects', 'v5_t13_fixed_effects.csv', 'Fixed-effects specifications', 'analytical 333'),
    ('influence', 'v5_t14_influence.csv', 'Influence: LOPO range, pre-rule, Cook\'s distance', 'analytical 333'),
    ('leave_one_parent_out', 'v5_t14b_leave_one_parent_out.csv', 'Leave-one-parent-out estimates', 'analytical 333 (G=82)'),
    ('specification_curve', 'v5_t15_spec_curve.csv', 'Specification curve (144 specifications)', 'analytical 333'),
    ('specification_curve_permutation', 'v5_t15b_spec_curve_permutation.csv', 'Specification-curve permutation test', 'analytical 333 (1,000 parent-level draws)'),
]
SRC = {'v5_t02': 264, 'v5_t03': 264, 'v5_t04': 264, 'v5_t05': 264, 'v5_t06': 264, 'v5_t07': 264, 'v5_t08': 264,
       'v5_t09': 265, 'v5_t10': 265, 'v5_t11': 265, 'v5_t12': 265, 'v5_t13': 265, 'v5_t14': 265, 'v5_t15': 266}
for key_, f, title, lvl in RES:
    scr = SRC[f[:6]]
    add(key_, v5(f), title, lvl, f'outputs/essay2_v5/{f} (scripts/{scr}_e2v5_*.py)')
if (OUT / 'v5_t16_spreads.csv').exists():
    add('spreads', v5('v5_t16_spreads.csv'), 'Trading-cost measures (BH family of 3)', 'analytical 333',
        'outputs/essay2_v5/v5_t16_spreads.csv (scripts/268_e2v5_spreads.py)')
else:
    if not ALLOW_PENDING:
        sys.exit('STOP: outputs/essay2_v5/v5_t16_spreads.csv missing. Run scripts/267 (WRDS login) then '
                 'scripts/268, or rerun this script with --allow-pending.')
    add('spreads', pd.DataFrame([dict(status='PENDING', detail='run scripts/267_e2v5_quotes_pull.py (WRDS login) '
                                       'then scripts/268_e2v5_spreads.py')]),
        'Trading-cost measures (PENDING)', 'analytical 333', 'scripts/267 + scripts/268 (not yet run)')
_DN = ('Control: the v5 pre-window abnormal-return SD [-60,-11]; rows labelled BRIDGE use the old control '
       'e2_pre_sd and reproduce t16 / e2_delay_ladder exactly (gated in scripts/271).')
add('disclosure_delay', v5('v5_t17_delay.csv'), 'Disclosure delay on treatment (full ladder)', 'analytical 333',
    'outputs/essay2_v5/v5_t17_delay.csv (scripts/271_e2v5_delay.py)', _DN)
add('delay_nonzero', v5('v5_t17b_delay_nonzero.csv'), 'Disclosure delay, non-zero delays only', 'non-zero delays (216)',
    'outputs/essay2_v5/v5_t17b_delay_nonzero.csv (scripts/271_e2v5_delay.py)', _DN)
add('delay_quantiles', v5('v5_t17c_delay_quantiles.csv'), 'Delay quantile regressions', 'analytical 333',
    'outputs/essay2_v5/v5_t17c_delay_quantiles.csv (scripts/271_e2v5_delay.py)',
    _DN + ' Descriptive; the solver reaches its iteration limit at some quantiles (statsmodels warning).')
add('delay_distribution', pd.read_csv(T2 / 't17_delay_distribution.csv'), 'Delay distribution by group',
    'analytical 333', 'outputs/tables/essay2_v2/t17_delay_distribution.csv (scripts/164; uses no controls)')
add('delay_distribution_tests', v5('v5_t17d_delay_distribution_tests.csv'),
    'Delay distribution tests (no controls)', 'analytical 333',
    'outputs/essay2_v5/v5_t17d_delay_distribution_tests.csv (scripts/271_e2v5_delay.py)')
pre = fin[pd.to_datetime(fin['reported_date']) < '2007-12-08'][['final_cik', 'org_name', 'breach_date', 'reported_date', TREAT]]
add('prerule_events', pre, 'Pre-rule observations (before 2007-12-08)', 'analytical 333 (identical under both anchors)',
    'scripts/269 from t1')
gate('prerule_events', 'prerule_events.csv', cols=['final_cik', 'org_name', 'breach_date', TREAT])
K.update(prerule_events=len(pre), prerule_treated=int(pre[TREAT].sum()),
         prerule_breach_anchor=int((pd.to_datetime(fin['breach_date']) < '2007-12-08').sum()),
         prerule_canonical=int((can['bdt'] < '2007-12-08').sum()),
         prerule_canonical_treated=int(can.loc[can['bdt'] < '2007-12-08', TREAT].sum()))

# ============================================== G. program test enumeration
print('== G. program test enumeration')
led = pd.read_csv(T2 / 't53_test_ledger.csv')
assert len(led) == 62


def status(r):
    s, f, t = r['script'], r['family'], r['test']
    if s.startswith('169') or (s.startswith('170') and (f == 'A' or 'headline' in t)) \
            or (s.startswith('164') and f == 'H1') or (s.startswith('164') and t.startswith('vol-change')):
        return 'RETIRED: raw-return volatility outcome, superseded by the v5 outcome'
    if s.startswith('170'):
        return 'RETIRED: microstructure intent-scope / TOST on the 167 measures, superseded by the v5 spreads family'
    if s.startswith('175'):
        return 'RETIRED: announcement family on the market-model basis, superseded by the v5 announcement family'
    if s.startswith('176'):
        return 'RETIRED: composition checks of the old announcement estimate; not rerun under v5'
    return 'KEPT (outcome does not use the volatility DV)'


led['v5_status'] = led.apply(status, axis=1)
kept = led[led['v5_status'].str.startswith('KEPT')].assign(source='t53 (committed ledger)')
new = []
for part, d in CP.items():
    for fam, n in d.get('tests', {}).items():
        for i in range(n):
            new.append(dict(script=f'{part}_e2v5', family=fam, test=f'{fam} #{i + 1}', v5_status='NEW (v5)', source=f'constants_parts/{part}.json'))
if '268' not in CP:
    new += [dict(script='268_e2v5', family='spreads', test=f'spreads #{i + 1}', v5_status='NEW (v5) - PENDING WRDS',
                 source='scripts/268 not yet run') for i in range(3)]
newdf = pd.DataFrame(new)
# the primary [+1,+20] estimate is a member of the dynamic-path family: count it once
dup = (newdf['family'] == 'H1 primary (M4, CV3)')
newdf = newdf[~dup]
prog = pd.concat([kept, newdf], ignore_index=True)[['script', 'family', 'test', 'v5_status', 'source']]
retired = led[~led['v5_status'].str.startswith('KEPT')]
add('program_test_enumeration', pd.concat([prog, retired.assign(source='t53 (committed ledger)')[prog.columns]],
                                          ignore_index=True),
    f'Program-wide test enumeration (v5: {len(prog)} tests)', 'program-wide',
    'outputs/tables/essay2_v2/t53_test_ledger.csv (scripts/182) + outputs/essay2_v5/constants_parts/*.json',
    'Rows marked RETIRED are listed for the record and not counted. The primary H1 estimate is the [+1,+20] member '
    'of the dynamic-path family and is counted once.')
bhf = {}
for d in CP.values():
    bhf.update(d.get('bh_families', {}))
bhf.setdefault('spreads', 3)
bhf['A2-delay (scripts/164, kept)'] = int((kept['family'] == 'A2-delay').sum())
bhf['A2-delay-nz (scripts/164, kept)'] = int((kept['family'] == 'A2-delay-nz').sum())
bht = pd.DataFrame([dict(family=k, size=v) for k, v in bhf.items()])
add('bh_families', bht, 'Benjamini-Hochberg families', 'program-wide', 'scripts/269 from constants_parts/*.json')
# CV3 rejections among the new v5 tests (p-values from the v5 tables)
rej = []
dyn = v5('v5_t05_dynamic_path.csv')
rej += [('dynamic', p) for p in dyn['p_cv3']]
ann = v5('v5_t09_announcement.csv').iloc[:4]
rej += [('announcement: ' + t, p) for t, p in zip(ann['test'], ann['p'])]
q = v5('v5_t12_size_quartiles.csv')
rej += [('quartile', p) for p in q['p_cv3']]
fe = v5('v5_t13_fixed_effects.csv')
rej += [('fe', p) for p in fe['p_cv3']]
inf_ = v5('v5_t14_influence.csv')
rej += [('influence', p) for p in inf_['p_cv3'].iloc[4:6]]
pm = v5('v5_t15b_spec_curve_permutation.csv')
rej += [('perm', p) for p in pm['perm_p']]
if (OUT / 'v5_t16_spreads.csv').exists():
    rej += [('spreads', p) for p in v5('v5_t16_spreads.csv')['p_cv3']]
nrej = sum(p < .05 for _, p in rej)
calib = sum(p < .05 for n, p in rej if n.startswith('announcement: ') and 'Form 499' not in n)
K.update(program_tests_total=len(prog), program_tests_kept_from_t53=len(kept),
         program_tests_new_v5=len(newdf), program_tests_retired_from_t53=len(retired),
         program_rejections_cv3=int(nrej), program_rejections_cv3_excl_calibration=int(nrej - calib),
         program_rejections_note='p<.05 among v5 tests with p-values in the v5 tables; kept t53 rows were not '
                                 're-tested here; calibration rows = earnings elevation and the breach-earnings contrast',
         bh_families=bhf,
         tests={**{f: int((prog['family'] == f).sum()) for f in prog['family'].unique()}})
print(f'  program-wide tests (v5): {len(prog)} = {len(kept)} kept + {len(newdf)} new; retired {len(retired)}; '
      f'CV3 rejections among new {nrej} ({nrej - calib} excluding calibration rows)')

# ============================================== write
miss_keys = [k for k in TABLE_ORDER if k not in TABLES]
assert not miss_keys, f'tables not built: {miss_keys}'
for f in AP.glob('*.csv'):
    f.unlink()
md = ['# Essay 2 v5 appendix', '',
      'Generated by `scripts/269_e2v5_appendix.py` from committed inputs and the v5 outputs of scripts/264-268. '
      'Numbering follows TABLE_GROUPS in that script (citation order).', '']
man = []
for n_, group in enumerate(TABLE_GROUPS, 1):
    if len(group) > 1:
        md += [f'## Table {n_}: ' + ' / '.join(TABLES[k]['title'] for k in group), '']
    for j, key_ in enumerate(group):
        t = TABLES[key_]
        panel = chr(ord('A') + j) if len(group) > 1 else ''
        fn = f'{n_:02d}{panel}_{key_}.csv'
        t['df'].to_csv(AP / fn, index=False)
        man.append(dict(table=f'{n_}{panel}', key=key_, title=t['title'], csv=fn, sample_level=t['level'],
                        source=t['source']))
        head = f'### Panel {panel}: {t["title"]}' if panel else f'## Table {n_}: {t["title"]}'
        md += [head, '',
               to_md(t['df']) if len(t['df']) <= 80
               else to_md(t['df'].head(80)) + f'\n\n({len(t["df"])} rows; full table in {fn})',
               '', f'> Sample: {t["level"]}. Source: {t["source"]}. {t["note"]}', '']
mdf = pd.DataFrame(man)
mdf.to_csv(AP / 'manifest.csv', index=False)
md += ['# Source manifest', '', to_md(mdf), '']
(AP / 'ESSAY2_V5_APPENDIX.md').write_text('\n'.join(md), encoding='utf-8')

rep = ['# Reproduction report: recomputed classification/data tables vs tombstoned CSVs', '',
       'Each recomputed table is compared cell by cell with the tombstoned CSV at the tombstone\'s printed precision.',
       '', '| table | tombstone | rows new/old | cells matching | differing |', '|---|---|---|---|---|']
for g in GATES:
    rep.append(f'| {g["key"]} | {g["tombstone"]} | {g["rows_new"]}/{g["rows_tomb"]} | {g["match"]}/{g["cells"]} | '
               f'{len(g["diffs"])} |')
for g in GATES:
    rep += ['', f'## {g["key"]}', '', f'Reason for differences: {g["reasons"]}', '']
    if g['diffs']:
        rep += ['| row | column | tombstone | recomputed |', '|---|---|---|---|']
        for i, c, o, m in g['diffs'][:60]:
            rep.append(f'| {i} | {c} | {o} | {m} |')
        if len(g['diffs']) > 60:
            rep.append(f'| ... | {len(g["diffs"]) - 60} more | | |')
    else:
        rep.append('Exact at printed precision.')
(AP / 'reproduction_report.md').write_text('\n'.join(rep), encoding='utf-8')
(OUT / 'constants_parts' / '269.json').write_text(
    json.dumps(K, indent=1, default=lambda x: x.item() if hasattr(x, 'item') else str(x)), encoding='utf-8')
print(f'Saved {len(TABLE_ORDER)} tables -> {AP}; reproduction_report.md; constants_parts/269.json '
      f'({len(K)} keys)')
