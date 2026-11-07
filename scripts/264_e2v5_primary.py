"""ESSAY 2 v5 — primary outcome, dynamic path, benchmarks, alternatives,
nested models + full ladder, design resolution, v4 date sensitivity.
(Committee changes, Dr. Zeng: items 1-6 and 9.)

Primary H1 outcome: SD of market-adjusted daily abnormal returns
(r - vwretd) over [+1,+20] minus over [-60,-11], trading days around the v3
agency reporting date, daily percentage points; >= 80% of window days in
each window. Model M4 (scripts/163 controls, the pre-window SD of the same
outcome in place of e2_pre_sd), CV3 cluster jackknife on parent filer entity.

Writes outputs/essay2_v5/:
  v5_event_panel.csv          per-event outcomes for every window/benchmark used here
  v5_t01_coverage.csv         80%-rule drops by treated/control, per window pair
  v5_t02_nested_models.csv    M1-M4, every coefficient, CV3 SE/p, R2
  v5_t03_ladder.csv           eight-rung ladder, primary (survivors and full-333 flagged)
  v5_t04_design_resolution.csv
  v5_t05_dynamic_path.csv     [+1,+5] / [+1,+10] / [+1,+20], BH family of 3
  v5_t06_benchmarks.csv       market model, FF3 on the same windows
  v5_t06b_estimation_contamination.csv
  v5_t07_alternatives.csv     pre [-45,-11]; bridge rows to the raw-return DV
  v5_t08_v4_dates.csv         v4 re-anchoring (12 events) and Sprint's corrected date
  constants_parts/264.json
"""
import importlib.util as _ilu
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
_s = _ilu.spec_from_file_location('e2v5', 'scripts/263_e2v5_lib.py')
L = _ilu.module_from_spec(_s)
_s.loader.exec_module(L)
OUT = L.OUT
(OUT / 'constants_parts').mkdir(parents=True, exist_ok=True)
TREAT = L.TREAT
C = {}


def log(m=''):
    print(m)


log('=' * 88)
log('ESSAY 2 v5 — PRIMARY (scripts/264)')
log('=' * 88)
r_gate = L.gate_ladder()
log(f'Gate PASS: lifted 165 ladder reproduces t26/t28 and PART_DE G*/size CV '
    f'(coef {r_gate["coef"]:+.4f}, CV3 p {r_gate["p_cv3"]:.4f}, G* {r_gate["G_star"]:.1f}).')

fin = L.load_sample()
M = L.Market(permnos=fin['permno'].unique())
PRE, POST = L.PRE_PRIMARY, L.POST_PRIMARY
POSTS = {'p1_5': (1, 5), 'p1_10': (1, 10), 'p1_20': (1, 20)}


def outcome(pre, post, bench='mkt_adj', rtype='simple', date_col='rdt', frame=None):
    f = fin if frame is None else frame
    return L.build_dv(f, M, pre, post, bench, rtype, date_col)


def with_dv(o, frame=None):
    d = (fin if frame is None else frame).copy()
    d['dv'], d['pre_sd'], d['post_sd'] = o['dv'], o['pre_sd'], o['post_sd']
    return d


def cv3_all(d, y, xs):
    """Every coefficient with its CV3 jackknife SE (scripts/165 formula)."""
    d = d.dropna(subset=[y] + xs).reset_index(drop=True)
    X = sm.add_constant(d[xs].astype(float), has_constant='add')
    Y = d[y].astype(float).to_numpy()
    f = sm.OLS(Y, X.to_numpy()).fit()
    gid, ginv = np.unique(d['final_cik'], return_inverse=True)
    G = len(gid)
    bd = np.array([np.linalg.lstsq(X.to_numpy()[ginv != g], Y[ginv != g], rcond=None)[0]
                   for g in range(G)])
    se = np.sqrt(np.diag((G - 1) / G * (bd - bd.mean(0)).T @ (bd - bd.mean(0))))
    p = 2 * stats.t.sf(np.abs(f.params / se), G - 1)
    return pd.DataFrame(dict(variable=X.columns, coef=f.params, se_cv3=se, p_cv3=p)), f, len(d)


# ---------------------------------------------------------------- 1. primary
prim = outcome(PRE, POST)
panel = fin[['final_cik', 'org_name', 'breach_date', 'reported_date', 'permno', TREAT]].copy()
panel['anchor_date'] = prim.get('anchor_date')
for c in ['pre_sd', 'post_sd', 'dv', 'n_pre', 'n_post', 'drop_reason']:
    panel['prim_' + c] = prim[c]
drop = prim['dv'].isna()
cov_rows = []


def coverage_row(label, o):
    dd = o['dv'].isna()
    return dict(window=label, n_events=len(o), dropped=int(dd.sum()),
                dropped_treated=int((dd & (fin[TREAT] == 1)).sum()),
                dropped_control=int((dd & (fin[TREAT] == 0)).sum()),
                surviving=int((~dd).sum()),
                surviving_treated=int((~dd & (fin[TREAT] == 1)).sum()),
                surviving_parents_treated=int(fin.loc[~dd & (fin[TREAT] == 1), 'final_cik'].nunique()),
                surviving_G=int(fin.loc[~dd, 'final_cik'].nunique()),
                reasons='; '.join(f'{fin.loc[i, "org_name"]} {fin.loc[i, "reported_date"][:10]}: '
                                  f'{o.loc[i, "drop_reason"]}' for i in o.index[dd]))


cov_rows.append(coverage_row('PRIMARY pre [-60,-11] / post [+1,+20], market-adjusted', prim))
log(f'\n## 1. Primary outcome: 80% coverage rule drops {int(drop.sum())} of 333 '
    f'({int((drop & (fin[TREAT] == 1)).sum())} treated, {int((drop & (fin[TREAT] == 0)).sum())} control)')
for i in fin.index[drop]:
    log(f'   drop: {fin.loc[i, "org_name"]} ({fin.loc[i, "reported_date"][:10]}, '
        f'treated={fin.loc[i, TREAT]}): {prim.loc[i, "drop_reason"]}')
d_prim = with_dv(prim)

# ---------------------------------------------------------------- 5. nested + ladder
nest_rows = []
for name, xs in L.NESTED.items():
    tab, f, n_ = cv3_all(d_prim, 'dv', xs)
    tab.insert(0, 'model', name)
    tab['N'] = n_
    tab['r2'] = f.rsquared
    tab['adj_r2'] = f.rsquared_adj
    nest_rows.append(tab)
nested = pd.concat(nest_rows)
nested.to_csv(OUT / 'v5_t02_nested_models.csv', index=False)
log('\n## 5. Nested models (CV3 SE / p):')
log(nested[nested['variable'] == TREAT].to_string(index=False))

R = L.ladder(d_prim, 'dv', L.XS4)
lad = L.ladder_rows(R, 'PRIMARY M4, surviving events')
log(f'\n## 5. PRIMARY H1 (M4): coef {R["coef"]:+.4f} daily pp; CV3 SE {R["se_cv3"]:.4f}; '
    f'CV3 p {R["p_cv3"]:.4f}; 95% CI [{R["ci3_lo"]:+.4f}, {R["ci3_hi"]:+.4f}]; '
    f'N {R["N"]}, treated {R["n_treated"]}, G {R["G"]}, G1 {R["G1"]}')
log(f'   G* (CSS) {R["G_star"]:.1f}; cluster-size CV {R["cv_sizes_ddof1"]:.4f} (ddof=1) / '
    f'{R["cv_sizes_ddof0"]:.4f} (ddof=0)')

full = None
if drop.any():
    # full 333: relaxed coverage (any 2 returns) for the dropped events, flagged
    rel = prim.copy()
    for i in fin.index[drop]:
        pos = M.anchor(fin.loc[i, 'permno'], fin.loc[i, 'rdt'])
        if pos is None:
            continue
        ar = M.abnormal(fin.loc[i, 'permno'], pos)
        sds = []
        for w in (PRE, POST):
            v = ar[max(0, pos + w[0]):pos + w[1] + 1]
            v = v[np.isfinite(v)]
            sds.append(np.std(v, ddof=1) * 100 if len(v) >= 2 else np.nan)
        rel.loc[i, ['pre_sd', 'post_sd']] = sds
        rel.loc[i, 'dv'] = sds[1] - sds[0]
    d_full = with_dv(rel)
    d_full['coverage_flag'] = drop.astype(float)
    full = L.ladder(d_full, 'dv', L.XS4 + ['coverage_flag'])
    lad += L.ladder_rows(full, 'M4 + coverage_flag, full sample (dropped events at relaxed coverage)')
    log(f'   full-sample flagged version: coef {full["coef"]:+.4f}, CV3 p {full["p_cv3"]:.4f}, '
        f'N {full["N"]}')
pd.DataFrame(lad).to_csv(OUT / 'v5_t03_ladder.csv', index=False)
diag = R['jack_coefs']

# ---------------------------------------------------------------- 6. design resolution
sd_ctrl = float(d_prim.loc[d_prim[TREAT] == 0, 'dv'].dropna().std())
DR = L.design_resolution(R, sd_ctrl)
DR['share_treated'] = float(d_prim.dropna(subset=['dv'])[TREAT].mean())
pd.DataFrame([DR]).to_csv(OUT / 'v5_t04_design_resolution.csv', index=False)
log('\n## 6. Design resolution:')
for k_, v_ in DR.items():
    log(f'   {k_}: {v_}')

# ---------------------------------------------------------------- 2. dynamic path
dyn = []
outs = {}
for key, w in POSTS.items():
    o = outcome(PRE, w)
    outs[key] = o
    panel[f'dyn_{key}_dv'] = o['dv']
    cov_rows.append(coverage_row(f'pre [-60,-11] / post {list(w)}, market-adjusted', o))
    r = L.ladder(with_dv(o), 'dv', L.XS4)
    dyn.append(dict(post_window=f'[+{w[0]},+{w[1]}]', coef=r['coef'], se_cv3=r['se_cv3'],
                    p_cv3=r['p_cv3'], ci3_lo=r['ci3_lo'], ci3_hi=r['ci3_hi'], p_wcr=r['p_wcr'],
                    p_hc3=r['p_hc3'], N=r['N'], n_treated=r['n_treated'], G=r['G'], G1=r['G1']))
dyn = pd.DataFrame(dyn)
dyn['bh_adj_p'], dyn['bh_reject_05'] = L.bh(dyn['p_cv3'])
dyn.to_csv(OUT / 'v5_t05_dynamic_path.csv', index=False)
log('\n## 2. Dynamic path (CV3; BH family of 3):')
log(dyn.round(4).to_string(index=False))

# ---------------------------------------------------------------- 3. benchmarks
bench_rows = []
for bench in ['mkt_adj', 'mm', 'ff3']:
    for key, w in POSTS.items():
        o = outcome(PRE, w, bench=bench)
        panel[f'{bench}_{key}_dv'] = o['dv']
        if bench != 'mkt_adj':
            cov_rows.append(coverage_row(f'pre [-60,-11] / post {list(w)}, {bench}', o))
        r = L.ladder(with_dv(o), 'dv', L.XS4, full=False)
        bench_rows.append(dict(benchmark=bench, post_window=f'[+{w[0]},+{w[1]}]', coef=r['coef'],
                               se_cv3=r['se_cv3'], p_cv3=r['p_cv3'], ci3_lo=r['ci3_lo'],
                               ci3_hi=r['ci3_hi'], N=r['N'], n_treated=r['n_treated'],
                               G=r['G'], G1=r['G1']))
bench_t = pd.DataFrame(bench_rows)
bench_t.to_csv(OUT / 'v5_t06_benchmarks.csv', index=False)
log('\n## 3. Benchmarks (market model / FF3 estimated on [-250,-30]):')
log(bench_t.round(4).to_string(index=False))

# estimation-window contamination: an earlier breach notification at the same
# parent filer entity inside [-250,-30] (canonical 489 events)
can = pd.read_csv('Data/processed/rebuild/CANONICAL_V3.csv', low_memory=False)
can['rdt'] = pd.to_datetime(can['reported_date'], errors='coerce')
can['bdt'] = pd.to_datetime(can['breach_date'], errors='coerce')
cont = []
for i, r in fin.iterrows():
    pos = M.anchor(r['permno'], r['rdt'])
    if pos is None or pos + L.EST_WIN[0] < 0:
        cont.append((np.nan, np.nan))
        continue
    lo, hi = M.dates[pos + L.EST_WIN[0]], M.dates[pos + L.EST_WIN[1]]
    same = can[can['final_cik'] == r['final_cik']]
    by_rep = bool(((same['rdt'] >= lo) & (same['rdt'] <= hi)).any())
    by_br = bool(((same['bdt'] >= lo) & (same['bdt'] <= hi)).any())
    cont.append((by_rep, by_br))
panel['est_contaminated_by_notification'] = [c[0] for c in cont]
panel['est_contaminated_by_breach_date'] = [c[1] for c in cont]
crow = []
for lab, m_ in [('treated', fin[TREAT] == 1), ('control', fin[TREAT] == 0), ('all', fin[TREAT] >= 0)]:
    for col in ['est_contaminated_by_notification', 'est_contaminated_by_breach_date']:
        v = panel.loc[m_, col].dropna().astype(bool)
        crow.append(dict(group=lab, definition=col, events=len(v), contaminated=int(v.sum()),
                         share=float(v.mean())))
crow = pd.DataFrame(crow)
crow.to_csv(OUT / 'v5_t06b_estimation_contamination.csv', index=False)
log('\n## 3b. Estimation windows [-250,-30] containing an earlier event at the same parent:')
log(crow.round(4).to_string(index=False))

# ---------------------------------------------------------------- 4. alternatives + bridge
alt = []


def alt_row(label, d, ycol='dv', xs=None):
    r = L.ladder(d, ycol, xs or L.XS4, full=False)
    return dict(row=label, coef=r['coef'], se_cv3=r['se_cv3'], p_cv3=r['p_cv3'],
                ci3_lo=r['ci3_lo'], ci3_hi=r['ci3_hi'], N=r['N'], n_treated=r['n_treated'])


for key, w in POSTS.items():
    o = outcome((-45, -11), w)
    panel[f'pre45_{key}_dv'] = o['dv']
    cov_rows.append(coverage_row(f'pre [-45,-11] / post {list(w)}, market-adjusted', o))
    alt.append(alt_row(f'ALT pre [-45,-11] / post [+{w[0]},+{w[1]}], market-adjusted', with_dv(o)))
bridge_x = ['delay_w', 'e2_pre_sd', 'firm_size_log', 'leverage', 'roa', TREAT,
            'health_breach', 'prior_events']
alt.append(alt_row('BRIDGE a: committed raw log-return DV, [-25,-5]/[+5,+25] (t1 e2_vol_change; '
                   'scripts/163 machinery)', fin, 'e2_vol_change', bridge_x))
# raw (unadjusted) log returns on the v5 calendar machinery, old windows
raw_rows = []
for i, r in fin.iterrows():
    pos = M.anchor(r['permno'], r['rdt'])
    if pos is None:
        raw_rows.append((np.nan, np.nan))
        continue
    ar = np.log1p(M.R[r['permno']])
    raw_rows.append((M.window_sd(ar, pos, (-25, -5))[0], M.window_sd(ar, pos, (5, 25))[0]))
d_raw = fin.copy()
d_raw['pre_sd'] = [x[0] for x in raw_rows]
d_raw['post_sd'] = [x[1] for x in raw_rows]
d_raw['dv'] = d_raw['post_sd'] - d_raw['pre_sd']
alt.append(alt_row('BRIDGE b: raw log returns, [-25,-5]/[+5,+25], v5 calendar + 80% rule', d_raw))
o_b = outcome((-25, -5), (5, 25))
alt.append(alt_row('BRIDGE c: market-adjusted simple, [-25,-5]/[+5,+25] (benchmark changed, '
                   'windows old)', with_dv(o_b)))
alt.append(alt_row('BRIDGE d = PRIMARY: market-adjusted simple, [-60,-11]/[+1,+20]', d_prim))
alt = pd.DataFrame(alt)
alt.to_csv(OUT / 'v5_t07_alternatives.csv', index=False)
log('\n## 4. Alternatives and bridge:')
log(alt.round(4).to_string(index=False))

# ---------------------------------------------------------------- 9. v4 dates
v3 = pd.read_csv('Data/processed/rebuild/CANONICAL_V3.csv', low_memory=False)
v4 = pd.read_csv('Data/processed/rebuild_v4/CANONICAL_V4.csv', low_memory=False)
assert len(v3) == len(v4) == 489 and (v3['org_name'].values == v4['org_name'].values).all()
key = ['final_cik', 'breach_date', 'org_name']
v3r = v3.reset_index().rename(columns={'index': 'row'})
rowmap = fin[key].merge(v3r[key + ['row']], on=key, how='left')['row']
assert rowmap.notna().all() and not rowmap.duplicated().any()
fin4 = fin.copy()
fin4['rdt'] = pd.to_datetime(v4.loc[rowmap.to_numpy(), 'reported_date'].to_numpy())
moved = (fin4['rdt'] != fin['rdt']).to_numpy()
CAP = float(fin['delay_w'].max())           # the frozen winsorization cap (p99 of 333)
d4 = (fin4['rdt'] - pd.to_datetime(fin4['breach_date'])).dt.days
fin4.loc[moved, 'disclosure_delay_days'] = d4[moved]
fin4.loc[moved, 'delay_w'] = d4[moved].clip(upper=CAP)
o4 = outcome(PRE, POST, frame=fin4)
d4f = fin4.copy()
d4f['dv'], d4f['pre_sd'] = o4['dv'], o4['pre_sd']
r4 = L.ladder(d4f, 'dv', L.XS4)
v4rows = [dict(scenario='v3 dates (PRIMARY)', coef=R['coef'], se_cv3=R['se_cv3'], p_cv3=R['p_cv3'],
               ci3_lo=R['ci3_lo'], ci3_hi=R['ci3_hi'], N=R['N'], n_treated=R['n_treated'],
               events_changed=0),
          dict(scenario='v4 reporting dates for the re-anchored events', coef=r4['coef'],
               se_cv3=r4['se_cv3'], p_cv3=r4['p_cv3'], ci3_lo=r4['ci3_lo'], ci3_hi=r4['ci3_hi'],
               N=r4['N'], n_treated=r4['n_treated'], events_changed=int(moved.sum()),
               detail='; '.join(f'{fin.loc[i, "org_name"]} {fin.loc[i, "reported_date"][:10]}->'
                                f'{fin4.loc[i, "rdt"].date()} (treated={fin.loc[i, TREAT]})'
                                for i in fin.index[moved]))]
log(f'\n## 9. v4 dates: {int(moved.sum())} events re-anchored '
    f'({int(fin.loc[moved, TREAT].sum())} treated)')
# Sprint's corrected breach date (v4: 2012-08-01 -> 2009-01-01)
sp_row = int(v3.index[(v3['final_cik'] == 101830) & (v3['breach_date'] == '2012-08-01')][0])
sp = v3.loc[[sp_row]].copy()
sp['breach_date'] = v4.loc[sp_row, 'breach_date']
sp['rdt'] = pd.to_datetime(sp['reported_date'])
sp['disclosure_delay_days'] = (sp['rdt'] - pd.to_datetime(sp['breach_date'])).dt.days
sp['delay_w'] = sp['disclosure_delay_days'].clip(upper=CAP)
sp['permno'] = sp['permno'].astype(int)
sp['prior_events'] = 0.0                  # first Sprint event once re-dated
gate = dict(permno=bool(pd.notna(v3.loc[sp_row, 'permno'])),
            notified_by_2024=bool(sp['rdt'].iloc[0] <= pd.Timestamp('2024-12-31')),
            delay_valid=bool(sp['disclosure_delay_days'].iloc[0] >= -30),
            covariates=bool(sp[['firm_size_log', 'leverage', 'roa']].notna().all(axis=None)))
osp = L.build_dv(sp, M, PRE, POST)
gate['window_80pct'] = bool(osp['dv'].notna().iloc[0])
enters = all(gate.values())
log(f'   Sprint 2012-08-01 -> {sp["breach_date"].iloc[0]}: delay '
    f'{int(sp["disclosure_delay_days"].iloc[0])} days; gates {gate}; enters={enters}')
if enters:
    fs = fin.copy()
    # Sprint Nextel 2009-02-01 gains the re-dated event as a prior breach
    m09 = (fs['final_cik'] == 101830) & (fs['breach_date'] == '2009-02-01')
    fs.loc[m09, 'prior_events'] = fs.loc[m09, 'prior_events'] + 1
    fs['dv'], fs['pre_sd'] = prim['dv'], prim['pre_sd']
    sp['dv'], sp['pre_sd'] = osp['dv'].to_numpy(), osp['pre_sd'].to_numpy()
    sp['health_breach'] = sp['health_breach'].astype(float)
    fs = pd.concat([fs, sp[fs.columns.intersection(sp.columns)]], ignore_index=True)
    rs = L.ladder(fs, 'dv', L.XS4)
    v4rows.append(dict(scenario="v3 dates + Sprint's corrected breach date (event enters)",
                       coef=rs['coef'], se_cv3=rs['se_cv3'], p_cv3=rs['p_cv3'],
                       ci3_lo=rs['ci3_lo'], ci3_hi=rs['ci3_hi'], N=rs['N'],
                       n_treated=rs['n_treated'], events_changed=1, detail=json.dumps(gate)))
else:
    v4rows.append(dict(scenario="Sprint's corrected breach date", events_changed=0,
                       detail='does not enter: ' + json.dumps(gate)))
v4t = pd.DataFrame(v4rows)
v4t.to_csv(OUT / 'v5_t08_v4_dates.csv', index=False)
log(v4t.drop(columns=['detail'], errors='ignore').round(4).to_string(index=False))

pd.DataFrame(cov_rows).to_csv(OUT / 'v5_t01_coverage.csv', index=False)
panel.to_csv(OUT / 'v5_event_panel.csv', index=False)

# ---------------------------------------------------------------- constants
C.update({
    'sample_N': 333, 'sample_treated': 104, 'sample_G': 82, 'sample_G1': 12,
    'primary_dropped_80pct': int(drop.sum()),
    'primary_dropped_treated': int((drop & (fin[TREAT] == 1)).sum()),
    'primary_dropped_control': int((drop & (fin[TREAT] == 0)).sum()),
    'primary_N': R['N'], 'primary_treated': R['n_treated'], 'primary_G': R['G'],
    'primary_G1': R['G1'], 'primary_coef': R['coef'], 'primary_se_cv3': R['se_cv3'],
    'primary_p_cv3': R['p_cv3'], 'primary_ci95_lo': R['ci3_lo'], 'primary_ci95_hi': R['ci3_hi'],
    'primary_se_ols': R['se_ols'], 'primary_p_ols': R['p_ols'],
    'primary_se_hc1': R['se_hc1'], 'primary_p_hc1': R['p_hc1'],
    'primary_se_hc3': R['se_hc3'], 'primary_p_hc3': R['p_hc3'],
    'primary_se_cv1': R['se_cv1'], 'primary_p_cv1': R['p_cv1'],
    'primary_p_wcr': R['p_wcr'], 'primary_p_wcu': R['p_wcu'], 'primary_p_webb': R['p_webb'],
    'primary_wcr_ci_lo': R['wcr_ci_lo'], 'primary_wcr_ci_hi': R['wcr_ci_hi'],
    'primary_G_star': R['G_star'], 'cluster_size_cv_ddof1': R['cv_sizes_ddof1'],
    'cluster_size_cv_ddof0': R['cv_sizes_ddof0'],
    'primary_r2_M3': float(nested.loc[nested.model == 'M3', 'r2'].iloc[0]),
    'primary_r2_M4': float(nested.loc[nested.model == 'M4', 'r2'].iloc[0]),
    'primary_r2_M2': float(nested.loc[nested.model == 'M2', 'r2'].iloc[0]),
    'M3_coef': float(nested.query('model=="M3" and variable==@TREAT')['coef'].iloc[0]),
    'M3_p_cv3': float(nested.query('model=="M3" and variable==@TREAT')['p_cv3'].iloc[0]),
    'full333_flagged_coef': full['coef'] if full else None,
    'full333_flagged_p_cv3': full['p_cv3'] if full else None,
})
C.update({f'dr_{k}': v for k, v in DR.items()})
for _, r in dyn.iterrows():
    k_ = r['post_window'].strip('[]').replace('+', '').replace(',', '_')
    C.update({f'dyn_{k_}_coef': r['coef'], f'dyn_{k_}_p_cv3': r['p_cv3'],
              f'dyn_{k_}_bh_p': r['bh_adj_p'], f'dyn_{k_}_N': int(r['N'])})
for _, r in bench_t.iterrows():
    k_ = r['post_window'].strip('[]').replace('+', '').replace(',', '_')
    C.update({f'bench_{r["benchmark"]}_{k_}_coef': r['coef'],
              f'bench_{r["benchmark"]}_{k_}_p_cv3': r['p_cv3'],
              f'bench_{r["benchmark"]}_{k_}_N': int(r['N'])})
for _, r in crow.iterrows():
    C[f'contam_{r["group"]}_{r["definition"].split("_by_")[1]}_share'] = r['share']
for i, r in alt.iterrows():
    C[f'alt_{i}_coef'], C[f'alt_{i}_p_cv3'] = r['coef'], r['p_cv3']
for i, r in v4t.iterrows():
    C[f'v4_{i}_coef'], C[f'v4_{i}_p_cv3'] = r.get('coef'), r.get('p_cv3')
C['bh_families'] = {'dynamic_path': 3}
C['tests'] = {'H1 primary (M4, CV3)': 1, 'dynamic path': 3}
(OUT / 'constants_parts' / '264.json').write_text(
    json.dumps(C, indent=1, default=lambda x: None if x is None else float(x)), encoding='utf-8')
log('\nSaved outputs/essay2_v5/v5_t01..t08 + v5_event_panel.csv + constants_parts/264.json')
