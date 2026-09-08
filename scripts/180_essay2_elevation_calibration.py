"""ESSAY 2: elevation-measure calibration. c4(n) bias correction,
parent-preserving placebo dates (200 draws, seed 499), earnings
benchmark. Emits outputs/tables/essay2_v2/t51_elevation_calibration.csv (Table 21 Panel C source).
1. c4(n) bias correction; 2. placebo dates (200 draws); 3. earnings
magnitude benchmark. Machinery copied from scripts/169/175 verbatim where
it defines the measure."""
from datetime import timedelta
from pathlib import Path
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats
from scipy.special import gammaln

pd.set_option('display.width', 250)
TREAT = 'fcc_form499'
OUTDIR = Path('outputs/tables/essay2_v2')
BETA_W, PRE, ANN = (-250, -46), (-25, -5), (-4, 4)

fin = pd.read_csv(OUTDIR / 't42_final_sample_with_repairs.csv',
                  low_memory=False)
fin['rdt'] = pd.to_datetime(fin['reported_date'])
CTRL = ['delay_w', 'firm_size_log', 'leverage', 'roa', 'health_breach',
        'prior_events']
crsp = pd.read_csv('Data/wrds/crsp_daily_returns.csv',
                   usecols=['permno', 'date', 'ret'])
for tp in ['Data/wrds/crsp_daily_topup.csv',
           'Data/wrds/crsp_daily_topup_dish.csv']:
    crsp = pd.concat([crsp, pd.read_csv(tp, usecols=['permno', 'date',
                                                     'ret'])],
                     ignore_index=True)
crsp['date'] = pd.to_datetime(crsp['date'])
mkt = pd.read_csv('Data/wrds/market_indices.csv', usecols=['date', 'vwretd'])
mkt['date'] = pd.to_datetime(mkt['date'])
crsp = crsp.merge(mkt, on='date').dropna()
PG = {p: g.sort_values('date').reset_index(drop=True)
      for p, g in crsp.groupby('permno')}


def windows_at(g, pos, want_counts=False):
    """abn_ann, abn_pre at index pos; 169's rules exactly."""
    r, m = g['ret'].to_numpy(), g['vwretd'].to_numpy()

    def seg(lo, hi):
        a, b = pos + lo, pos + hi + 1
        a, b = max(0, a), min(len(g), b)
        return r[a:b], m[a:b]
    rb, mb = seg(*BETA_W)
    if len(rb) < 100:
        return (np.nan,) * 4
    ab = np.linalg.lstsq(np.column_stack([np.ones(len(mb)), mb]), rb,
                         rcond=None)[0]
    out = []
    for (lo, hi), minn in [(ANN, 7), (PRE, 15)]:
        rs, ms = seg(lo, hi)
        if len(rs) < minn:
            return (np.nan,) * 4
        resid = rs - ab[0] - ab[1] * ms
        out += [np.std(resid, ddof=1) * 100, len(resid)]
    return tuple(out)   # ann_sd, n_ann, pre_sd, n_pre


def c4(n):
    n = np.asarray(n, dtype=float)
    return np.exp(0.5 * np.log(2 / (n - 1))
                  + gammaln(n / 2) - gammaln((n - 1) / 2))


def cv3_p(d, ycol, xcols):
    """CV3 jackknife over final_cik; returns coef, se, p, G."""
    X = sm.add_constant(d[xcols].astype(float)).to_numpy()
    Y = d[ycol].astype(float).to_numpy()
    gid, ginv = np.unique(d['final_cik'], return_inverse=True)
    G, k = len(gid), X.shape[1]
    beta = np.linalg.lstsq(X, Y, rcond=None)[0]
    bd = np.zeros((G, k))
    for gi in range(G):
        mask = ginv != gi
        bd[gi] = np.linalg.lstsq(X[mask], Y[mask], rcond=None)[0]
    V = (G - 1) / G * (bd - bd.mean(0)).T @ (bd - bd.mean(0))
    se = np.sqrt(V[1, 1])
    p = 2 * (1 - stats.t.cdf(abs(beta[1] / se), G - 1))
    return beta[1], se, p, G


# ---- rebuild the d3 sample with counts, verify against t42 ----
rows = []
for i, r in fin.iterrows():
    g = PG.get(int(r['permno']) if pd.notna(r['permno']) else -1)
    if g is None:
        rows.append((np.nan,) * 4 + (None,))
        continue
    gaps = (g['date'] - r['rdt']).abs()
    pos = int(gaps.idxmin())
    if gaps.iloc[pos] > timedelta(days=7):
        rows.append((np.nan,) * 4 + (None,))
        continue
    rows.append(windows_at(g, pos) + (pos,))
W = pd.DataFrame(rows, columns=['ann_sd', 'n_ann', 'pre_sd', 'n_pre',
                                'pos'], index=fin.index)
fin2 = fin.join(W)
chk = fin2.dropna(subset=['abn_ann', 'ann_sd'])
assert np.allclose(chk['abn_ann'], chk['ann_sd'], atol=1e-6), 'machinery drift'
assert np.allclose(chk['abn_pre'], chk['pre_sd'], atol=1e-6)
d3 = fin2.dropna(subset=['ann_sd', 'pre_sd', TREAT] + CTRL).reset_index(
    drop=True)
assert len(d3) == 331
d3['elev'] = d3['ann_sd'] - d3['pre_sd']

print('== 1. c4(n) BIAS CORRECTION ==')
print(f"actual return counts: ann mean {d3['n_ann'].mean():.2f} "
      f"(min {int(d3['n_ann'].min())}, max {int(d3['n_ann'].max())}); "
      f"pre mean {d3['n_pre'].mean():.2f} (min {int(d3['n_pre'].min())})")
print(f'c4(9) = {float(c4(9)):.6f}, c4(21) = {float(c4(21)):.6f}; implied '
      f'mechanical offset at sigma 1.5: '
      f'{1.5 * (float(c4(9)) - float(c4(21))):+.4f} daily pp')
d3['elev_c'] = (d3['ann_sd'] / c4(d3['n_ann'])
                - d3['pre_sd'] / c4(d3['n_pre']))
for nm, m in [('full', d3.index), ('treated', d3[TREAT] == 1),
              ('control', d3[TREAT] == 0)]:
    g_ = d3.loc[m]
    print(f'  {nm:8s} raw mean {g_["elev"].mean():+.4f} -> corrected '
          f'{g_["elev_c"].mean():+.4f} (N={len(g_)})')
d3['abn_pre_c'] = d3['pre_sd'] / c4(d3['n_pre'])
b, se, p, G = cv3_p(d3, 'elev_c', [TREAT, 'abn_pre_c'] + CTRL)
print(f'  base spec on CORRECTED measure: coef {b:+.4f}  CV3 SE {se:.4f}  '
      f'p {p:.6f}  (N={len(d3)}, G={G})')
b0, se0, p0, _ = cv3_p(d3, 'elev', [TREAT, 'abn_pre'] + CTRL)
print(f'  base spec on RAW measure (check): coef {b0:+.4f}  CV3 SE '
      f'{se0:.4f}  p {p0:.6f}')

print('\n== 2. PLACEBO DATES ==')
ev_all = pd.read_csv('Data/processed/rebuild/CANONICAL_V3.csv',
                     low_memory=False)
ev_all['rdt'] = pd.to_datetime(ev_all['reported_date'], errors='coerce')
notif = ev_all.dropna(subset=['permno', 'rdt']).groupby('permno')['rdt'] \
    .apply(list).to_dict()
rdq = pd.read_csv('Data/wrds/q6_rdq.csv', low_memory=False)
rdq['rdq'] = pd.to_datetime(rdq['rdq'])
t2p = (fin.dropna(subset=['permno'])
       .groupby('matched_ticker')['permno'].first().to_dict())
rdq['permno'] = rdq['tic'].map(t2p)
earn = rdq.dropna(subset=['permno']).groupby('permno')['rdq'] \
    .apply(list).to_dict()

# eligibility per permno: literal rule first, operative rule second
EXC_BREACH, EXC_EARN = 120, 30
lit_empty = op_sets = 0
elig = {}
for p in d3['permno'].astype(int).unique():
    g = PG[p]
    dates = g['date'].reset_index(drop=True)
    n = len(g)
    ok = np.ones(n, dtype=bool)
    ok[:146] = False           # beta window needs >=100 obs in [-250,-46]
    ok[n - 4:] = False         # ann window needs +4
    didx = {d_: i for i, d_ in enumerate(dates)}

    def pos_of(dt):
        arr = (dates - dt).abs()
        return int(arr.idxmin())
    ok_lit = ok.copy()
    for dt in notif.get(p, []) + notif.get(float(p), []):
        i = pos_of(dt)
        ok[max(0, i - EXC_BREACH):i + EXC_BREACH + 1] = False
        ok_lit[max(0, i - EXC_BREACH):i + EXC_BREACH + 1] = False
    for dt in earn.get(p, []) + earn.get(float(p), []):
        i = pos_of(dt)
        ok[max(0, i - EXC_EARN):i + EXC_EARN + 1] = False
        ok_lit[max(0, i - EXC_BREACH):i + EXC_BREACH + 1] = False
    if not ok_lit.any():
        lit_empty += 1
    elig[p] = np.flatnonzero(ok)
n_perm = len(elig)
print(f'LITERAL RULE (>=120 trading days from breaches AND earnings): '
      f'empties the eligible set for {lit_empty} of {n_perm} securities '
      f'(quarterly earnings are ~63 trading days apart, so no date is 120 '
      f'from all of them). OPERATIVE RULE: >=120 from every breach '
      f'notification, >=30 from every earnings date (keeps the [-25,+4] '
      f'measurement span clear of earnings).')
no_elig = [p for p, v in elig.items() if len(v) == 0]
print(f'securities with zero eligible positions under the operative rule: '
      f'{len(no_elig)}')

rng = np.random.default_rng(499)
B = 200
cache = {}
full_m, tr_m, co_m, diffs, ps, ns = [], [], [], [], [], []
for b_ in range(B):
    vals = np.full(len(d3), np.nan)
    for i, (p, ) in enumerate(zip(d3['permno'].astype(int))):
        e_ = elig[p]
        if not len(e_):
            continue
        pos = int(rng.choice(e_))
        key = (p, pos)
        if key not in cache:
            a_sd, _, p_sd, _ = windows_at(PG[p], pos)
            cache[key] = (a_sd - p_sd if pd.notna(a_sd) else np.nan, p_sd)
        vals[i] = cache[key][0]
        d3.loc[i, '_ppre'] = cache[key][1]
    d3['_pel'] = vals
    dd = d3.dropna(subset=['_pel', '_ppre'])
    full_m.append(dd['_pel'].mean())
    tr_m.append(dd.loc[dd[TREAT] == 1, '_pel'].mean())
    co_m.append(dd.loc[dd[TREAT] == 0, '_pel'].mean())
    bb, ss, pp, _ = cv3_p(dd, '_pel', [TREAT, '_ppre'] + CTRL)
    diffs.append(bb)
    ps.append(pp)
    ns.append(len(dd))
full_m, tr_m, co_m = map(np.array, (full_m, tr_m, co_m))
diffs, ps = np.array(diffs), np.array(ps)
print(f'draws: {B}; mean per-draw N = {np.mean(ns):.1f}')
print(f'PLACEBO ELEVATION mean across draws: full {full_m.mean():+.4f} '
      f'(SD across draws {full_m.std(ddof=1):.4f}); treated '
      f'{tr_m.mean():+.4f}; control {co_m.mean():+.4f}')
print(f'PLACEBO TREATMENT DIFFERENTIAL across {B} draws: mean '
      f'{diffs.mean():+.4f}, SD {diffs.std(ddof=1):.4f}, quantiles '
      f'[q05 {np.quantile(diffs, .05):+.4f}, median '
      f'{np.median(diffs):+.4f}, q95 {np.quantile(diffs, .95):+.4f}], '
      f'max |diff| {np.abs(diffs).max():.4f}')
print(f'draws with |placebo differential| >= 0.4475 (the actual): '
      f'{int((np.abs(diffs) >= 0.4475).sum())} of {B}')
print(f'draws with CV3 p < .05: {int((ps < .05).sum())} of {B} '
      f'({100 * (ps < .05).mean():.1f}%)')

print('\n== 3. EARNINGS-ANNOUNCEMENT MAGNITUDE (same securities) ==')
erows = []
for _, r in rdq.dropna(subset=['permno']).drop_duplicates(
        subset=['permno', 'rdq']).iterrows():
    if not ('2006-01-01' <= str(r['rdq'])[:10] <= '2024-12-31'):
        continue
    g = PG.get(int(r['permno']))
    if g is None:
        continue
    gaps = (g['date'] - r['rdq']).abs()
    pos = int(gaps.idxmin())
    if gaps.iloc[pos] > timedelta(days=7):
        continue
    a_sd, _, p_sd, _ = windows_at(g, pos)
    if pd.notna(a_sd):
        erows.append(dict(permno=int(r['permno']), elev=a_sd - p_sd))
EA = pd.DataFrame(erows)
X = np.ones((len(EA), 1))
f = sm.OLS(EA['elev'].astype(float), X).fit(
    cov_type='cluster', cov_kwds={'groups': EA['permno'].astype(int)},
    use_t=True)
print(f'earnings elevation: mean {EA["elev"].mean():+.4f} daily pp '
      f'(cluster SE {float(f.bse.iloc[0]):.4f}, t '
      f'{float(f.tvalues.iloc[0]):+.1f}, N={len(EA):,} announcements, '
      f'{EA["permno"].nunique()} securities); median '
      f'{EA["elev"].median():+.4f}, SD {EA["elev"].std(ddof=1):.4f}')
print(f'reference points on the same measure: breach mean '
      f'{d3["elev"].mean():+.4f}; placebo mean {full_m.mean():+.4f}')


# ---- emit t51 (Table 21 Panel C source) ----
from pathlib import Path as _P
_OUT = _P('outputs/tables/essay2_v2')
_b, _se, _p, _G = cv3_p(d3, 'elev_c', [TREAT, 'abn_pre_c'] + CTRL)
rows_out = [
    dict(panel='c4_correction', item='corrected_mean_full',
         value=round(d3['elev_c'].mean(), 4),
         detail='raw -0.0935; c4(9) = .969311, c4(21) = .987583; every '
                'event has exactly 9 and 21 returns'),
    dict(panel='c4_correction', item='corrected_mean_treated',
         value=round(d3.loc[d3[TREAT] == 1, 'elev_c'].mean(), 4),
         detail='raw -0.0289'),
    dict(panel='c4_correction', item='corrected_mean_control',
         value=round(d3.loc[d3[TREAT] == 0, 'elev_c'].mean(), 4),
         detail='raw -0.1231'),
    dict(panel='c4_correction', item='corrected_spec_coef',
         value=round(_b, 4),
         detail=f'CV3 SE {_se:.4f}, p {_p:.6f}; the correction is an '
                'affine reparametrization at constant counts, so '
                'inference is invariant'),
    dict(panel='placebo', item='placebo_mean_full',
         value=round(full_m.mean(), 4),
         detail=f'SD across draws {full_m.std(ddof=1):.4f}; 200 draws, '
                f'seed 499, mean per-draw N {np.mean(ns):.0f}'),
    dict(panel='placebo', item='placebo_mean_treated',
         value=round(tr_m.mean(), 4), detail=''),
    dict(panel='placebo', item='placebo_mean_control',
         value=round(co_m.mean(), 4), detail=''),
    dict(panel='placebo', item='placebo_differential_mean',
         value=round(diffs.mean(), 4),
         detail=f'SD {diffs.std(ddof=1):.4f}; q05 '
                f'{np.quantile(diffs, .05):+.4f}, median '
                f'{np.median(diffs):+.4f}, q95 '
                f'{np.quantile(diffs, .95):+.4f}, max abs '
                f'{np.abs(diffs).max():.4f}'),
    dict(panel='placebo', item='draws_reaching_actual',
         value=int((np.abs(diffs) >= 0.4475).sum()),
         detail='of 200; actual differential +0.4475'),
    dict(panel='placebo', item='draws_cv3_rejecting',
         value=int((ps < .05).sum()), detail='of 200 at p < .05'),
    dict(panel='earnings_benchmark', item='earnings_elevation_mean',
         value=round(EA['elev'].mean(), 4),
         detail=f'cluster SE {float(f.bse.iloc[0]):.4f}, t '
                f'{float(f.tvalues.iloc[0]):+.1f}, N={len(EA):,} '
                f'announcements, {EA["permno"].nunique()} securities; '
                f'median {EA["elev"].median():+.4f}'),
    dict(panel='earnings_benchmark', item='breach_minus_placebo',
         value=round(d3['elev'].mean() - full_m.mean(), 4),
         detail='breach dates damp relative to the same securities '
                'quiet periods; the damping is control-side'),
]
pd.DataFrame(rows_out).to_csv(_OUT / 't51_elevation_calibration.csv',
                              index=False)
print('Saved: t51_elevation_calibration.csv')
