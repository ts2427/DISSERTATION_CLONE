"""
DEFENSE AUDIT — FINAL ITEM 2: DESCRIPTIVE STATISTICS BY TREATMENT GROUP (script 277)
=====================================================================================
Read-only on every committed result. For each essay sample and group (treated = Form 499
registrant events, control, all) reports N and the mean and median of firm size (log total
assets, ln(Compustat at), as all three essays define firm_size_log), total assets in $M
(exp(firm_size_log), Compustat at is in $M), market capitalisation in $M, leverage, ROA and the
essay's outcome.

Committed values are used where a committed table holds them; everything else is computed from
the committed sample file, and every computed value that overlaps a committed table is asserted
against it before anything is written.

  Essay 1 (N = 340, 106 treated): sample = CANONICAL_V3, has_crsp_data == 1, complete on car_30d +
    the 158 controls (scripts/158 lines 51-60). Committed: outputs/rebuild/appendix_v3/table_3.csv
    (30-day CAR by group), deck_exhibits.csv E1_dollar (market cap by group, scripts/252).
  Essay 2 v5 (N = 333, 104 treated): sample = outputs/essay2_v5/v5_event_panel.csv; covariates
    joined from CANONICAL_V3 for the dollar values only. Committed: appendix/02A_descriptives_v5.csv.
  Essay 3 v4 (N = 405, 109 treated): sample = outputs/essay3_v4/e_analysis_sample.csv,
    in_analysis_sample == 1. Committed: outputs/essay3_q4/table04.csv (covariates by group),
    table06.csv (departure rates by group and pooled).

Market cap for Essays 2 and 3 follows scripts/252 (Essay 1 deck exhibit): |prc| x shrout x 1000
from Data/wrds/crsp_daily_returns.csv (the top-ups carry no prc/shrout), last row strictly before
day 0. Day 0 = the essay's anchor: Essay 2 v5 anchor_date; Essay 3 v4 reported_date (the _rd
outcomes). Events without such a row are counted as missing.

Writes ONLY outputs/defense_audit/final/item2_descriptives.csv and item2_descriptives.log.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
OUT = Path('outputs/defense_audit/final')
CANON = 'Data/processed/rebuild/CANONICAL_V3.csv'
CRSP = 'Data/wrds/crsp_daily_returns.csv'
L, ROWS = [], []
TOL = 5e-4      # committed tables round to 3-6 dp


def log(m=''):
    print(m, flush=True)
    L.append(str(m))


def add(essay, group, var, stat, value, source, kind):
    ROWS.append(dict(essay=essay, group=group, variable=var, stat=stat,
                     value=(round(float(value), 6) if isinstance(value, (int, float, np.floating, np.integer))
                            and not isinstance(value, bool) else value),
                     source=source, computed_or_committed=kind))


def check(what, got, ref, tol=TOL):
    ok = abs(float(got) - float(ref)) <= tol
    log(f'  assert {what}: computed {float(got):.6f} vs committed {float(ref):.6f} -> {"PASS" if ok else "FAIL"}')
    assert ok, f'computed value disagrees with committed table: {what}'


GROUPS = [('treated', 1), ('control', 0), ('all', None)]


def split(d, t):
    return [(g, d if v is None else d[d[t] == v]) for g, v in GROUPS]


# ---------------------------------------------------------------- market cap (scripts/252 convention)
crsp = pd.read_csv(CRSP, usecols=['permno', 'date', 'prc', 'shrout'], low_memory=False)
crsp['date'] = pd.to_datetime(crsp['date'])
crsp = crsp.dropna(subset=['prc', 'shrout'])
crsp['permno'] = crsp['permno'].astype(int)
crsp = crsp.sort_values('date')


def mcap_m(d, day0_col):
    """$M market cap from the last main-file CRSP row strictly before day 0 (NaN if none)."""
    q = d[['permno', day0_col]].copy()
    q['_i'] = np.arange(len(q))
    q['day0'] = pd.to_datetime(q[day0_col])
    ok = q.permno.notna()
    q2 = q[ok].assign(permno=lambda x: x.permno.astype(int)).sort_values('day0')
    m = pd.merge_asof(q2, crsp, left_on='day0', right_on='date', by='permno', direction='backward',
                      allow_exact_matches=False)
    out = pd.Series(np.nan, index=range(len(q)))
    out[m._i.to_numpy()] = (m.prc.abs() * m.shrout * 1000 / 1e6).to_numpy()
    return out.to_numpy()


def stats_rows(essay, d, t, var, label, source_txt, kind='computed'):
    for g, s in split(d, t):
        x = s[var].dropna()
        add(essay, g, label, 'n', len(x), source_txt, kind)
        add(essay, g, label, 'mean', x.mean(), source_txt, kind)
        add(essay, g, label, 'median', x.median(), source_txt, kind)


# ================================================================ Essay 1
log('=' * 90)
log('ESSAY 1 (regression sample)')
can = pd.read_csv(CANON, low_memory=False)
TREAT = 'fcc_form499'
CONTROLS = [TREAT, 'immediate_disclosure', 'prior_breaches_1yr', 'health_breach', 'firm_size_log', 'leverage', 'roa']
e1 = can[can['has_crsp_data'] == 1].dropna(subset=['car_30d'] + CONTROLS).copy()
c3 = json.load(open('outputs/rebuild/constants_v3.json'))
log(f'  N = {len(e1)}, treated = {int(e1[TREAT].sum())}')
assert len(e1) == c3['N_regression'] == 340 and int(e1[TREAT].sum()) == c3['treated_regression'] == 106
S1 = 'computed from Data/processed/rebuild/CANONICAL_V3.csv (has_crsp_data==1, complete on car_30d + scripts/158 CONTROLS)'
for g, s in split(e1, TREAT):
    add('Essay 1', g, 'events', 'n', len(s), S1 + '; = constants_v3.json N_regression / treated_regression', 'computed')
e1['total_assets_musd'] = np.exp(e1['firm_size_log'])
for var, lab in [('firm_size_log', 'firm size: log total assets ln(at)'),
                 ('total_assets_musd', 'total assets, $M = exp(firm_size_log)'),
                 ('leverage', 'leverage (LT/AT)'), ('roa', 'ROA (NI/AT)')]:
    stats_rows('Essay 1', e1, TREAT, var, lab, S1 + ' (no committed by-group table on the 340)')
# outcome: committed table_3 for treated/control; 'all' computed; asserted
t3 = pd.read_csv('outputs/rebuild/appendix_v3/table_3.csv')
t3 = t3[t3.Comparison == 'Form 499'].set_index('Group')
for g, row in [('treated', 'Filer'), ('control', 'Non-filer')]:
    s = e1[e1[TREAT] == (1 if g == 'treated' else 0)]
    check(f'E1 {g} mean car_30d', s.car_30d.mean(), t3.loc[row, 'Mean CAR'])
    check(f'E1 {g} median car_30d', s.car_30d.median(), t3.loc[row, 'Median CAR'])
    assert int(t3.loc[row, 'N']) == len(s)
    src = f'outputs/rebuild/appendix_v3/table_3.csv, Comparison=Form 499, Group={row}'
    add('Essay 1', g, 'outcome: 30-day CAR (pp)', 'n', int(t3.loc[row, 'N']), src, 'committed')
    add('Essay 1', g, 'outcome: 30-day CAR (pp)', 'mean', t3.loc[row, 'Mean CAR'], src, 'committed')
    add('Essay 1', g, 'outcome: 30-day CAR (pp)', 'median', t3.loc[row, 'Median CAR'], src, 'committed')
add('Essay 1', 'all', 'outcome: 30-day CAR (pp)', 'n', len(e1), S1, 'computed')
add('Essay 1', 'all', 'outcome: 30-day CAR (pp)', 'mean', e1.car_30d.mean(), S1, 'computed')
add('Essay 1', 'all', 'outcome: 30-day CAR (pp)', 'median', e1.car_30d.median(), S1, 'computed')
# market cap: committed deck exhibit E1_dollar ($B -> $M)
dx = pd.read_csv('outputs/defense_supplement/deck_exhibits.csv')
dx = dx[dx.exhibit == 'E1_dollar'].set_index('key')
for g in ['treated', 'control', 'all']:
    src = f'outputs/defense_supplement/deck_exhibits.csv, E1_dollar / mcap_{g}_*  (scripts/252; $B x 1000)'
    add('Essay 1', g, 'market cap, $M (day before day 0)', 'n', float(dx.loc[f'mcap_{g}_n_covered', 'value']), src, 'committed')
    add('Essay 1', g, 'market cap, $M (day before day 0)', 'n_missing', float(dx.loc[f'mcap_{g}_n_missing', 'value']), src, 'committed')
    add('Essay 1', g, 'market cap, $M (day before day 0)', 'mean', float(dx.loc[f'mcap_{g}_mean', 'value']) * 1000, src, 'committed')
    add('Essay 1', g, 'market cap, $M (day before day 0)', 'median', float(dx.loc[f'mcap_{g}_median', 'value']) * 1000, src, 'committed')

# validate the market-cap function against the committed Essay 1 values (scripts/252): same coverage, and
# mean/median within 0.5% (252 anchors on the nearest trading day to the breach date, which can precede it)
e1['mcap_musd'] = mcap_m(e1, 'breach_date')
for g, s in split(e1, TREAT):
    x = s.mcap_musd.dropna()
    assert len(x) == int(float(dx.loc[f'mcap_{g}_n_covered', 'value'])), f'E1 mcap coverage {g}'
    refm = float(dx.loc[f'mcap_{g}_median', 'value'])
    log(f'  E1 {g} mcap median ($B): mcap_m (day before breach_date) {x.median() / 1000:.6f} vs E1_dollar {refm:.6f} '
        f'(relative gap {abs(x.median() / 1000 - refm) / refm:.4%})')
    assert abs(x.median() / 1000 - refm) / refm < 0.005
    # 252's day 0 is the nearest CRSP trading day to the breach date (it can precede it), so a few events take an
    # earlier price row here; the gap is reported, and Essay 1 cites the committed E1_dollar values.
    ref = float(dx.loc[f'mcap_{g}_mean', 'value'])
    log(f'  E1 {g} mcap mean ($B): mcap_m (day before breach_date) {x.mean() / 1000:.6f} vs E1_dollar {ref:.6f} '
        f'(relative gap {abs(x.mean() / 1000 - ref) / ref:.4%}); committed value used')
    assert abs(x.mean() / 1000 - ref) / ref < 0.005

# ================================================================ Essay 2 v5
log('=' * 90)
log('ESSAY 2 v5 (analytical sample)')
p = pd.read_csv('outputs/essay2_v5/v5_event_panel.csv', low_memory=False)
p = p[p.prim_dv.notna()].copy()
assert len(p) == 333 and int(p[TREAT].sum()) == 104
key = ['final_cik', 'breach_date', 'reported_date']
cc = can[key + ['firm_size_log', 'leverage', 'roa']].copy()
for k in key[1:]:                     # compare as the committed text (some canonical dates are 'YYYY-MM')
    cc[k] = cc[k].astype(str).str[:10]
    p[k] = p[k].astype(str).str[:10]
assert not cc.duplicated(key).any()
p = p.merge(cc, on=key, how='left', validate='one_to_one')
assert p[['firm_size_log', 'leverage', 'roa']].notna().all(axis=None), 'E2 covariate join incomplete'
a2 = pd.read_csv('outputs/essay2_v5/appendix/02A_descriptives_v5.csv').set_index(['group', 'variable'])
GMAP = {'treated': 'treated', 'control': 'control', 'all': 'full'}
for g, s in split(p, TREAT):
    # assert the join reproduces 02A, then cite 02A
    for v in ['firm_size_log', 'leverage', 'roa']:
        check(f'E2 {g} mean {v} (join vs 02A)', s[v].mean(), a2.loc[(GMAP[g], v), 'mean'], 1e-6)
    check(f'E2 {g} mean dv (panel prim_dv vs 02A)', s.prim_dv.mean(), a2.loc[(GMAP[g], 'dv'), 'mean'], 1e-9)
    for v, lab in [('firm_size_log', 'firm size: log total assets ln(at)'), ('leverage', 'leverage (LT/AT)'),
                   ('roa', 'ROA (NI/AT)'),
                   ('dv', 'outcome: change in abnormal return volatility, daily pp ([+1,+20] minus [-60,-11])')]:
        r = a2.loc[(GMAP[g], v)]
        src = f'outputs/essay2_v5/appendix/02A_descriptives_v5.csv, group={GMAP[g]}, variable={v}'
        add('Essay 2 v5', g, lab, 'n', int(r.N), src, 'committed')
        add('Essay 2 v5', g, lab, 'mean', r['mean'], src, 'committed')
        add('Essay 2 v5', g, lab, 'median', r['median'], src, 'committed')
    add('Essay 2 v5', g, 'events', 'n', len(s), 'outputs/essay2_v5/appendix/02A_descriptives_v5.csv (N)', 'committed')
p['total_assets_musd'] = np.exp(p['firm_size_log'])
S2 = ('computed: outputs/essay2_v5/v5_event_panel.csv joined 1:1 to CANONICAL_V3 on (final_cik, breach_date, '
      'reported_date); join asserted against 02A means')
stats_rows('Essay 2 v5', p, TREAT, 'total_assets_musd', 'total assets, $M = exp(firm_size_log)', S2)
p['mcap_musd'] = mcap_m(p, 'anchor_date')
SM2 = 'computed (scripts/252 convention): crsp_daily_returns.csv |prc| x shrout, last row before anchor_date'
for g, s in split(p, TREAT):
    x = s.mcap_musd.dropna()
    add('Essay 2 v5', g, 'market cap, $M (day before day 0)', 'n', len(x), SM2, 'computed')
    add('Essay 2 v5', g, 'market cap, $M (day before day 0)', 'n_missing', len(s) - len(x), SM2, 'computed')
    add('Essay 2 v5', g, 'market cap, $M (day before day 0)', 'mean', x.mean(), SM2, 'computed')
    add('Essay 2 v5', g, 'market cap, $M (day before day 0)', 'median', x.median(), SM2, 'computed')
    log(f'  E2 {g}: mcap covered {len(x)} of {len(s)}')

# ================================================================ Essay 3 v4
log('=' * 90)
log('ESSAY 3 v4 (analysis sample)')
e3 = pd.read_csv('outputs/essay3_v4/e_analysis_sample.csv', low_memory=False)
e3 = e3[e3.in_analysis_sample == 1].copy()
assert len(e3) == 405 and int(e3[TREAT].sum()) == 109
t4 = pd.read_csv('outputs/essay3_q4/table04.csv')
t4 = t4[t4.part == 'C3'].set_index(['group', 'variable'])
t6 = pd.read_csv('outputs/essay3_q4/table06.csv')
S3 = 'computed from outputs/essay3_v4/e_analysis_sample.csv (in_analysis_sample == 1)'
for g, s in split(e3, TREAT):
    add('Essay 3 v4', g, 'events', 'n', len(s), 'outputs/essay3_q4/table06.csv n' if g != 'all' else S3,
        'committed' if g != 'all' else 'computed')
    for v, lab in [('firm_size_log', 'firm size: log total assets ln(at)'), ('leverage', 'leverage (LT/AT)'),
                   ('roa', 'ROA (NI/AT)')]:
        if g == 'all':
            stats_rows_one = s[v].dropna()
            add('Essay 3 v4', g, lab, 'n', len(stats_rows_one), S3, 'computed')
            add('Essay 3 v4', g, lab, 'mean', stats_rows_one.mean(), S3, 'computed')
            add('Essay 3 v4', g, lab, 'median', stats_rows_one.median(), S3, 'computed')
            continue
        r = t4.loc[(g, v)]
        check(f'E3 {g} mean {v} (sample vs table04)', s[v].mean(), r['mean'], 1e-6)
        check(f'E3 {g} median {v} (sample vs table04)', s[v].median(), r['median'], 1e-6)
        src = f'outputs/essay3_q4/table04.csv, part=C3, group={g}, variable={v}'
        add('Essay 3 v4', g, lab, 'n', int(r.n), src, 'committed')
        add('Essay 3 v4', g, lab, 'mean', r['mean'], src, 'committed')
        add('Essay 3 v4', g, lab, 'median', r['median'], src, 'committed')
    for w in [30, 90, 180]:
        col = f'exec_departure_{w}_rd'
        lab = f'outcome: executive departure within {w} days of reporting date (share)'
        tg = 'POOLED' if g == 'all' else g
        r = t6[(t6.window == w) & (t6.group == tg)].iloc[0]
        check(f'E3 {g} exec departure rate {w}d (sample vs table06)', s[col].mean(), r.exec_rate)
        src = f'outputs/essay3_q4/table06.csv, window={w}, group={tg}, exec_rate (exec_departure / n)'
        add('Essay 3 v4', g, lab, 'n', int(r.n), src, 'committed')
        add('Essay 3 v4', g, lab, 'mean', r.exec_rate, src, 'committed')
        add('Essay 3 v4', g, lab, 'median', s[col].median(), S3 + ' (binary outcome; median is 0 or 1)', 'computed')
e3['total_assets_musd'] = np.exp(e3['firm_size_log'])
stats_rows('Essay 3 v4', e3, TREAT, 'total_assets_musd', 'total assets, $M = exp(firm_size_log)', S3)
e3['mcap_musd'] = mcap_m(e3, 'reported_date')
SM3 = 'computed (scripts/252 convention): crsp_daily_returns.csv |prc| x shrout, last row before reported_date'
for g, s in split(e3, TREAT):
    x = s.mcap_musd.dropna()
    add('Essay 3 v4', g, 'market cap, $M (day before day 0)', 'n', len(x), SM3, 'computed')
    add('Essay 3 v4', g, 'market cap, $M (day before day 0)', 'n_missing', len(s) - len(x), SM3, 'computed')
    add('Essay 3 v4', g, 'market cap, $M (day before day 0)', 'mean', x.mean(), SM3, 'computed')
    add('Essay 3 v4', g, 'market cap, $M (day before day 0)', 'median', x.median(), SM3, 'computed')
    log(f'  E3 {g}: mcap covered {len(x)} of {len(s)}')

# ================================================================ write
OUT.mkdir(parents=True, exist_ok=True)
R = pd.DataFrame(ROWS)
R.to_csv(OUT / 'item2_descriptives.csv', index=False, lineterminator='\n', encoding='utf-8')
piv = R[R.stat.isin(['n', 'mean', 'median'])].pivot_table(index=['essay', 'variable', 'stat'], columns='group',
                                                           values='value', aggfunc='first')
log('\n' + piv.to_string())
log(f'\nwrote {OUT / "item2_descriptives.csv"} ({len(R)} rows)')
(OUT / 'item2_descriptives.log').write_text('\n'.join(L) + '\n', encoding='utf-8')
