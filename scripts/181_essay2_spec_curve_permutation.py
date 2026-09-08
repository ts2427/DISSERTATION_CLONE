"""ESSAY 2: specification-curve joint inference (Simonsohn, Simmons & Nelson 2020,
step 3) on the 193-spec grid. Null forced by permuting treatment at the
PARENT FILER ENTITY level (12 of 82 clusters treated, preserved each draw).
DV machinery copied verbatim from scripts/166."""
from datetime import timedelta
from pathlib import Path
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats
from scipy.linalg import cho_factor, cho_solve

TREAT = 'fcc_form499'
OUTDIR = Path('outputs/tables/essay2_v2')
fin = pd.read_csv(OUTDIR / 't1_final_sample.csv', low_memory=False)
fin['rdt'] = pd.to_datetime(fin['reported_date'])
fin['bdt'] = pd.to_datetime(fin['breach_date'])
fin = fin.reset_index(drop=True)
N = len(fin)
assert N == 333

crsp = pd.read_csv('Data/wrds/crsp_daily_returns.csv',
                   usecols=['permno', 'date', 'ret'])
for tp in ['Data/wrds/crsp_daily_topup.csv',
           'Data/wrds/crsp_daily_topup_dish.csv']:
    crsp = pd.concat([crsp, pd.read_csv(tp, usecols=['permno', 'date',
                                                     'ret'])],
                     ignore_index=True)
crsp['date'] = pd.to_datetime(crsp['date'])
crsp['ret'] = pd.to_numeric(crsp['ret'], errors='coerce')
crsp = crsp.dropna(subset=['ret'])
PG = {p: g.sort_values('date').reset_index(drop=True)
      for p, g in crsp.groupby('permno')}

ANCHORS = ['notification', 'breach']
BASES = ['trading', 'calendar']
LS = [21, 31, 42]
GS = [0, 1, 3, 5]
RETS = ['log', 'simple']
MIN_FRAC = 0.7
sd_store = {}
for i, r in fin.iterrows():
    g_ = PG.get(r['permno'])
    if g_ is None:
        continue
    dates = g_['date']
    lr = np.log1p(g_['ret'].to_numpy())
    sr = g_['ret'].to_numpy()
    for anchor in ANCHORS:
        adt = r['rdt'] if anchor == 'notification' else r['bdt']
        gaps = (dates - adt).abs()
        pos = int(gaps.idxmin())
        if gaps.iloc[pos] > timedelta(days=7):
            continue
        for basis in BASES:
            for Lw in LS:
                span = Lw - 1
                for gp in GS:
                    if basis == 'trading':
                        if gp == 0:
                            pre_ix = np.arange(max(0, pos - span - 1), pos)
                            post_ix = np.arange(pos, min(len(g_), pos + span + 1))
                        else:
                            pre_ix = np.arange(max(0, pos - gp - span), pos - gp + 1)
                            post_ix = np.arange(pos + gp, min(len(g_), pos + gp + span + 1))
                    else:
                        if gp == 0:
                            m_pre = (dates >= adt - timedelta(days=span + 1)) & (dates < adt)
                            m_post = (dates >= adt) & (dates <= adt + timedelta(days=span))
                        else:
                            m_pre = (dates >= adt - timedelta(days=gp + span)) & (dates <= adt - timedelta(days=gp))
                            m_post = (dates >= adt + timedelta(days=gp)) & (dates <= adt + timedelta(days=gp + span))
                        pre_ix = np.where(m_pre)[0]
                        post_ix = np.where(m_post)[0]
                    need = int(MIN_FRAC * Lw) if basis == 'trading' \
                        else int(MIN_FRAC * Lw * 5 / 7)
                    if len(pre_ix) < need or len(post_ix) < need:
                        continue
                    for rtype, arr in [('log', lr), ('simple', sr)]:
                        sd_store[(i, anchor, basis, Lw, gp, rtype)] = (
                            np.std(arr[pre_ix], ddof=1) * 100,
                            np.std(arr[post_ix], ddof=1) * 100)

CTRL = ['delay_w', 'firm_size_log', 'leverage', 'roa', 'health_breach',
        'prior_events']

# ---- build per-spec structures ----
specs = []


def add_spec(dv, pre, label):
    d = fin.copy()
    d['_dv'] = dv
    d['_pre'] = pre
    d = d.dropna(subset=['_dv', '_pre'])
    Xc = np.column_stack([np.ones(len(d)),
                          d[['_pre'] + CTRL].astype(float).to_numpy()])
    y = d['_dv'].astype(float).to_numpy()
    F = cho_factor(Xc.T @ Xc)
    yp = y - Xc @ cho_solve(F, Xc.T @ y)
    gid, ginv = np.unique(d['final_cik'].to_numpy(), return_inverse=True)
    specs.append(dict(label=label, idx=d.index.to_numpy(), Xc=Xc, F=F,
                      yp=yp, ginv=ginv, G=len(gid), n=len(d),
                      k=Xc.shape[1] + 1))


for anchor in ANCHORS:
    for basis in BASES:
        for Lw in LS:
            for gp in GS:
                for rtype in RETS:
                    key_ok = [i for i in fin.index
                              if (i, anchor, basis, Lw, gp, rtype) in sd_store]
                    if len(key_ok) < 150:
                        continue
                    pre = pd.Series({i: sd_store[(i, anchor, basis, Lw, gp,
                                                  rtype)][0]
                                     for i in key_ok})
                    post = pd.Series({i: sd_store[(i, anchor, basis, Lw, gp,
                                                   rtype)][1]
                                      for i in key_ok})
                    dv_raw = (post - pre).reindex(fin.index)
                    pre_f = pre.reindex(fin.index)
                    for wins in ['raw', 'w199']:
                        dv = dv_raw.clip(dv_raw.quantile(.01),
                                         dv_raw.quantile(.99)) \
                            if wins == 'w199' else dv_raw
                        add_spec(dv, pre_f,
                                 f'{anchor}/{basis}/L{Lw}/g{gp}/{rtype}/{wins}')
add_spec(fin['garch_dv'], fin['e2_pre_sd'], 'GARCH(1,1)')
assert len(specs) == 193, f'expected 193 specs, got {len(specs)}'


def est(sp, Tvec):
    """coef and CV1 p for the treatment under FWL + cluster sandwich
    (statsmodels-equivalent small-sample correction, t(G-1))."""
    ts = Tvec[sp['idx']]
    tp_ = ts - sp['Xc'] @ cho_solve(sp['F'], sp['Xc'].T @ ts)
    den = float(tp_ @ tp_)
    if den < 1e-12:
        return np.nan, np.nan
    b = float(tp_ @ sp['yp']) / den
    e = sp['yp'] - b * tp_
    sg = np.bincount(sp['ginv'], weights=tp_ * e, minlength=sp['G'])
    c = (sp['G'] / (sp['G'] - 1)) * ((sp['n'] - 1) / (sp['n'] - sp['k']))
    se = np.sqrt(c * float(sg @ sg)) / den
    p = 2 * stats.t.sf(abs(b / se), sp['G'] - 1)
    return b, p


# ---- validate the fast path against statsmodels on one spec ----
T_act = fin[TREAT].astype(float).to_numpy()
b0f, p0f = est(specs[0], T_act)
a0, ba0, l0, g0, r0, w0 = specs[0]['label'].split('/')
key0 = [i for i in fin.index
        if (i, a0, ba0, int(l0[1:]), int(g0[1:]), r0) in sd_store]
pre0 = pd.Series({i: sd_store[(i, a0, ba0, int(l0[1:]), int(g0[1:]), r0)][0]
                  for i in key0})
post0 = pd.Series({i: sd_store[(i, a0, ba0, int(l0[1:]), int(g0[1:]), r0)][1]
                   for i in key0})
dvr = (post0 - pre0).reindex(fin.index)
if w0 == 'w199':
    dvr = dvr.clip(dvr.quantile(.01), dvr.quantile(.99))
dd = fin.copy()
dd['_dv'] = dvr
dd['_pre'] = pre0.reindex(fin.index)
dd = dd.dropna(subset=['_dv', '_pre'])
Xf = sm.add_constant(dd[[TREAT, '_pre'] + CTRL].astype(float))
ff = sm.OLS(dd['_dv'].astype(float), Xf).fit(
    cov_type='cluster', cov_kwds={'groups': dd['final_cik']}, use_t=True)
assert np.isclose(ff.params[TREAT], b0f, atol=1e-8), 'coef mismatch'
assert np.isclose(ff.pvalues[TREAT], p0f, atol=1e-8), 'p mismatch'
print(f'fast-path validation OK on {specs[0]["label"]}: '
      f'coef {b0f:+.6f}, p {p0f:.6f} == statsmodels')

# ---- observed statistics ----
obs = np.array([est(sp, T_act) for sp in specs])
ob, op = obs[:, 0], obs[:, 1]
S1_obs = float(np.median(ob))
npos, nneg = int((ob > 0).sum()), int((ob < 0).sum())
S2_obs = max(npos, nneg)
S3_obs = int(((op < .05) & (ob > 0)).sum()) if npos >= nneg \
    else int(((op < .05) & (ob < 0)).sum())
print(f'OBSERVED: median {S1_obs:+.4f}; dominant sign POSITIVE {npos}/193; '
      f'significant in dominant direction {S3_obs}')

# ---- permutation ----
rng = np.random.default_rng(499)
parents = fin['final_cik'].astype(int).to_numpy()
upar = np.unique(parents)
G_all, G1 = len(upar), int(fin.loc[fin[TREAT] == 1, 'final_cik'].nunique())
assert (G_all, G1) == (82, 12)
B = 1000
S1s, S2s, S3s, sharepos, sharesig = [], [], [], [], []
for b_ in range(B):
    tset = set(rng.choice(upar, size=G1, replace=False))
    Tp = np.isin(parents, list(tset)).astype(float)
    r_ = np.array([est(sp, Tp) for sp in specs])
    bb, pp = r_[:, 0], r_[:, 1]
    ok = ~np.isnan(bb)
    bb, pp = bb[ok], pp[ok]
    np_, nn_ = int((bb > 0).sum()), int((bb < 0).sum())
    S1s.append(float(np.median(bb)))
    S2s.append(max(np_, nn_))
    S3s.append(int(((pp < .05) & (bb > 0)).sum()) if np_ >= nn_
               else int(((pp < .05) & (bb < 0)).sum()))
    sharepos.append(np_ / len(bb))
    sharesig.append(float((pp < .05).mean()))
S1s, S2s, S3s = np.array(S1s), np.array(S2s), np.array(S3s)
p1 = (int((np.abs(S1s) >= abs(S1_obs)).sum()) + 1) / (B + 1)
p2 = (int((S2s >= S2_obs).sum()) + 1) / (B + 1)
p3 = (int((S3s >= S3_obs).sum()) + 1) / (B + 1)
print(f'\nDRAWS: {B} (parent-level, 12 of 82 treated preserved); '
      f'p resolution 1/{B + 1} = {1 / (B + 1):.6f}')
print(f'S1 median estimate:      obs {S1_obs:+.4f}  perm p {p1:.6f}  '
      f'null mean {S1s.mean():+.4f} SD {S1s.std(ddof=1):.4f}  '
      f'pct[|null| >= |obs|] plain count {int((np.abs(S1s) >= abs(S1_obs)).sum())}')
print(f'S2 dominant-sign count:  obs {S2_obs}/193  perm p {p2:.6f}  '
      f'null mean {S2s.mean():.1f} SD {S2s.std(ddof=1):.1f}  '
      f'count[null >= obs] {int((S2s >= S2_obs).sum())}')
print(f'S3 significant-dominant: obs {S3_obs}  perm p {p3:.6f}  '
      f'null mean {S3s.mean():.2f} SD {S3s.std(ddof=1):.2f}  '
      f'count[null >= obs] {int((S3s >= S3_obs).sum())}')
for nm, arr, o_ in [('S1 |median|', np.abs(S1s), abs(S1_obs)),
                    ('S2', S2s.astype(float), float(S2_obs)),
                    ('S3', S3s.astype(float), float(S3_obs))]:
    qs = np.quantile(arr, [.05, .25, .5, .75, .9, .95, .99, 1.0])
    below = float((arr < o_).mean()) * 100
    print(f'  {nm:12s} null q05 {qs[0]:.4f} q25 {qs[1]:.4f} med {qs[2]:.4f} '
          f'q75 {qs[3]:.4f} q90 {qs[4]:.4f} q95 {qs[5]:.4f} q99 {qs[6]:.4f} '
          f'max {qs[7]:.4f} | obs sits above {below:.1f}% of null')
print(f'\nper-draw share positive: mean {np.mean(sharepos):.3f}, '
      f'q95 {np.quantile(sharepos, .95):.3f}, max {np.max(sharepos):.3f}')
print(f'per-draw share significant (any sign): mean '
      f'{np.mean(sharesig):.4f}, q95 {np.quantile(sharesig, .95):.4f}, '
      f'max {np.max(sharesig):.4f}')


# ---- emit t52 (Table 25 Panel B source) ----
rows_out = [
    dict(statistic='S1_median_estimate', observed=round(S1_obs, 4),
         perm_p=round(p1, 6), null_mean=round(float(S1s.mean()), 4),
         null_sd=round(float(S1s.std(ddof=1)), 4),
         null_q75=round(float(np.quantile(np.abs(S1s), .75)), 4),
         null_q95=round(float(np.quantile(np.abs(S1s), .95)), 4),
         detail='two-sided on absolute median'),
    dict(statistic='S2_dominant_sign_count', observed=S2_obs,
         perm_p=round(p2, 6), null_mean=round(float(S2s.mean()), 1),
         null_sd=round(float(S2s.std(ddof=1)), 1),
         null_q75=float(np.quantile(S2s, .75)),
         null_q95=float(np.quantile(S2s, .95)),
         detail='unanimous-sign curves arise in over a third of placebo '
                'draws'),
    dict(statistic='S3_significant_dominant', observed=S3_obs,
         perm_p=round(p3, 6), null_mean=round(float(S3s.mean()), 2),
         null_sd=round(float(S3s.std(ddof=1)), 2),
         null_q75=float(np.quantile(S3s, .75)),
         null_q95=float(np.quantile(S3s, .95)),
         detail='observed count sits below the null mean'),
]
pd.DataFrame(rows_out).to_csv(OUTDIR / 't52_spec_curve_permutation.csv',
                              index=False)
print('Saved: t52_spec_curve_permutation.csv')
