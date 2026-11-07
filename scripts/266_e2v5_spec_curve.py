"""ESSAY 2 v5 — specification curve on abnormal returns + parent-level
permutation test (committee item 7, last bullet).

Nodes (3 x 4 x 3 x 2 x 2 = 144 specifications, all anchored on the v3 agency
reporting date, 80% coverage rule, model M4):
  pre      [-25,-5], [-45,-11], [-60,-11]
  post     [+1,+5], [+1,+10], [+1,+20], [+5,+25]
  bench    market-adjusted, market model, FF3 (models on [-250,-30])
  returns  simple, log
  winsor   raw, 1/99 (outcome winsorized at its 1st/99th percentiles)
PRIMARY = pre [-60,-11] / post [+1,+20] / market-adjusted / simple / raw.

Observed curve: coefficient, CV3 SE and p for every specification.
Permutation (Simonsohn, Simmons & Nelson 2020, step 3): treatment permuted at
the parent filer entity level, 12 of 82 treated in every draw, 1,000 draws,
seed 499. Statistics: S1 median estimate (two-sided on |median|), S2
dominant-sign count, S3 count significant in the dominant direction. As in
scripts/181, the per-draw p-values are CV1 (parent) by a Frisch-Waugh fast path
validated against statsmodels; CV3 inside 144,000 draws is not run.
Writes outputs/essay2_v5/v5_t15_spec_curve.csv, v5_t15b_spec_curve_permutation.csv,
constants_parts/266.json.
"""
import importlib.util as _ilu
import itertools
import json
import sys

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
_s = _ilu.spec_from_file_location('e2v5', 'scripts/263_e2v5_lib.py')
L = _ilu.module_from_spec(_s)
_s.loader.exec_module(L)
OUT, TREAT = L.OUT, L.TREAT
PRES = {'pre25_5': (-25, -5), 'pre45_11': (-45, -11), 'pre60_11': (-60, -11)}
POSTS = {'post1_5': (1, 5), 'post1_10': (1, 10), 'post1_20': (1, 20), 'post5_25': (5, 25)}
BENCH = ['mkt_adj', 'mm', 'ff3']
RTYPE = ['simple', 'log']
WINS = ['raw', 'w1_99']
PRIMARY = 'pre60_11/post1_20/mkt_adj/simple/raw'
ZCOLS = [c for c in L.XS4 if c != TREAT]

fin = L.load_sample()
M = L.Market(permnos=fin['permno'].unique())
anchors = [M.anchor(p, d) for p, d in zip(fin['permno'], fin['rdt'])]

# per-event window SDs for every (bench, rtype, window)
sd = {}
for b, rt in itertools.product(BENCH, RTYPE):
    for i, (p, pos) in enumerate(zip(fin['permno'], anchors)):
        ar = M.abnormal(p, pos, b, rt) if pos is not None else None
        for nm, w in {**PRES, **POSTS}.items():
            sd[(b, rt, nm, i)] = M.window_sd(ar, pos, w)[0] if ar is not None else np.nan

T_act = fin[TREAT].astype(float).to_numpy()
ginv_all = np.unique(fin['final_cik'], return_inverse=True)[1]
specs = []
for pre, post, b, rt, w in itertools.product(PRES, POSTS, BENCH, RTYPE, WINS):
    pre_v = np.array([sd[(b, rt, pre, i)] for i in range(len(fin))])
    post_v = np.array([sd[(b, rt, post, i)] for i in range(len(fin))])
    dv = post_v - pre_v
    if w == 'w1_99':
        lo, hi = np.nanquantile(dv, [.01, .99])
        dv = np.clip(dv, lo, hi)
    d = fin.copy()
    d['dv'], d['pre_sd'] = dv, pre_v
    ok = d[['dv'] + L.XS4].notna().all(axis=1).to_numpy()
    Z = sm.add_constant(d.loc[ok, ZCOLS].astype(float), has_constant='add').to_numpy()
    P = Z @ np.linalg.pinv(Z)
    y = d.loc[ok, 'dv'].to_numpy(float)
    gi = np.unique(ginv_all[ok], return_inverse=True)[1]
    specs.append(dict(label=f'{pre}/{post}/{b}/{rt}/{w}', pre=pre, post=post, bench=b, rtype=rt,
                      winsor=w, ok=ok, P=P, yp=y - P @ y, ginv=gi, G=gi.max() + 1,
                      n=int(ok.sum()), k=Z.shape[1] + 1, frame=d))
assert len(specs) == 144


def est(sp, T):
    t = T[sp['ok']]
    tp = t - sp['P'] @ t
    den = float(tp @ tp)
    if den < 1e-12:
        return np.nan, np.nan
    b = float(tp @ sp['yp']) / den
    e = sp['yp'] - b * tp
    sg = np.bincount(sp['ginv'], weights=tp * e, minlength=sp['G'])
    c = (sp['G'] / (sp['G'] - 1)) * ((sp['n'] - 1) / (sp['n'] - sp['k']))
    se = np.sqrt(c * float(sg @ sg)) / den
    return b, 2 * stats.t.sf(abs(b / se), sp['G'] - 1)


# validate the fast path on the primary spec against statsmodels CV1
sp0 = [s for s in specs if s['label'] == PRIMARY][0]
d0 = sp0['frame'].dropna(subset=['dv'] + L.XS4)
f0 = sm.OLS(d0['dv'], sm.add_constant(d0[L.XS4].astype(float))).fit(
    cov_type='cluster', cov_kwds={'groups': d0['final_cik']}, use_t=True)
b0, p0 = est(sp0, T_act)
assert np.isclose(f0.params[TREAT], b0, atol=1e-9) and np.isclose(f0.pvalues[TREAT], p0, atol=1e-9)
C0 = json.loads((OUT / 'constants_parts' / '264.json').read_text(encoding='utf-8'))
assert abs(b0 - C0['primary_coef']) < 1e-10, 'primary spec differs from scripts/264'
print(f'fast path == statsmodels CV1 on {PRIMARY}: {b0:+.6f}, p {p0:.6f}; equals scripts/264 primary')

rows = []
for sp in specs:
    r = L.ladder(sp['frame'], 'dv', L.XS4, full=False)
    b, p1 = est(sp, T_act)
    rows.append(dict(spec=sp['label'], pre=sp['pre'], post=sp['post'], benchmark=sp['bench'],
                     returns=sp['rtype'], winsor=sp['winsor'], N=r['N'], coef=r['coef'],
                     se_cv3=r['se_cv3'], p_cv3=r['p_cv3'], ci3_lo=r['ci3_lo'], ci3_hi=r['ci3_hi'],
                     p_cv1=p1, primary=sp['label'] == PRIMARY))
curve = pd.DataFrame(rows).sort_values('coef').reset_index(drop=True)
curve.to_csv(OUT / 'v5_t15_spec_curve.csv', index=False)
ob = curve['coef'].to_numpy()
S1 = float(np.median(ob))
npos, nneg = int((ob > 0).sum()), int((ob < 0).sum())
S2 = max(npos, nneg)
pos_dom = npos >= nneg
S3 = int(((curve['p_cv1'] < .05) & ((ob > 0) if pos_dom else (ob < 0))).sum())
S3_cv3 = int(((curve['p_cv3'] < .05) & ((ob > 0) if pos_dom else (ob < 0))).sum())
print(f'OBSERVED: {len(ob)} specs; median {S1:+.4f}; range [{ob.min():+.4f}, {ob.max():+.4f}]; '
      f'positive {npos}; CV3 CI excludes 0 in {int((curve["p_cv3"] < .05).sum())}; '
      f'CV1-significant in dominant direction {S3}')

rng = np.random.default_rng(L.SEED)
parents = fin['final_cik'].astype(int).to_numpy()
upar = np.unique(parents)
G1 = int(fin.loc[fin[TREAT] == 1, 'final_cik'].nunique())
assert (len(upar), G1) == (82, 12)
B = 1000
S1s, S2s, S3s, allpos = [], [], [], []
for _ in range(B):
    Tp = np.isin(parents, rng.choice(upar, size=G1, replace=False)).astype(float)
    r_ = np.array([est(sp, Tp) for sp in specs])
    bb, pp = r_[:, 0], r_[:, 1]
    keep = ~np.isnan(bb)
    bb, pp = bb[keep], pp[keep]
    np_, nn_ = int((bb > 0).sum()), int((bb < 0).sum())
    S1s.append(float(np.median(bb)))
    S2s.append(max(np_, nn_))
    S3s.append(int(((pp < .05) & ((bb > 0) if np_ >= nn_ else (bb < 0))).sum()))
    allpos.append(np_ == len(bb) or nn_ == len(bb))
S1s, S2s, S3s = map(np.array, (S1s, S2s, S3s))
p1 = (int((np.abs(S1s) >= abs(S1)).sum()) + 1) / (B + 1)
p2 = (int((S2s >= S2).sum()) + 1) / (B + 1)
p3 = (int((S3s >= S3).sum()) + 1) / (B + 1)
perm = pd.DataFrame([
    dict(statistic='S1 median estimate', observed=S1, perm_p=p1, null_mean=S1s.mean(),
         percentile=float(stats.percentileofscore(np.abs(S1s), abs(S1))), detail='two-sided on |median|'),
    dict(statistic='S2 dominant-sign count', observed=S2, perm_p=p2, null_mean=S2s.mean(),
         percentile=float(stats.percentileofscore(S2s, S2)),
         detail=f'unanimous-sign curves in {np.mean(allpos):.3f} of draws'),
    dict(statistic='S3 significant in dominant direction (CV1)', observed=S3, perm_p=p3,
         null_mean=S3s.mean(), percentile=float(stats.percentileofscore(S3s, S3)),
         detail=f'observed CV3-significant: {S3_cv3}'),
])
perm['draws'] = B
perm.to_csv(OUT / 'v5_t15b_spec_curve_permutation.csv', index=False)
print(perm.round(4).to_string(index=False))
by_node = {c: curve.groupby(c)['coef'].median().to_dict()
           for c in ['pre', 'post', 'benchmark', 'returns', 'winsor']}
print('median coef by node:', json.dumps(by_node, indent=0, default=float))
C = dict(spec_n=len(ob), spec_median=S1, spec_min=float(ob.min()), spec_max=float(ob.max()),
         spec_positive=npos, spec_cv3_sig=int((curve['p_cv3'] < .05).sum()),
         spec_cv3_ci_contains_zero=int((curve['p_cv3'] >= .05).sum()),
         spec_cv1_sig_dominant=S3, perm_p_median=p1, perm_p_sign=p2, perm_p_sig=p3,
         perm_unanimous_share=float(np.mean(allpos)), perm_S3_null_mean=float(S3s.mean()),
         spec_median_by_node=by_node,
         bh_families={}, tests={'specification-curve permutation (joint)': 3})
(OUT / 'constants_parts' / '266.json').write_text(json.dumps(C, indent=1, default=float), encoding='utf-8')
print('Saved v5_t15 + v5_t15b + constants_parts/266.json')
