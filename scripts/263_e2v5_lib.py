"""ESSAY 2 v5 — shared library (imported by scripts/264-270; writes nothing).

Frozen sample: the v3 analytical sample, outputs/tables/essay2_v2/t1_final_sample.csv
(N = 333, 104 treated events, 82 parent filer entities, 12 treated). Every v5
script asserts it on load.

Outcome machinery (committee changes, Dr. Zeng):
  * Calendar: CRSP trading days from Data/wrds/market_indices.csv
    (2005-05-02 .. 2024-12-31). Windows are counted in MARKET trading days, so a
    day the stock did not trade counts as a missing day.
  * Anchor: the agency reporting date (v3 reported_date) mapped to the nearest
    market trading day; the stock must have a return within +/-7 calendar days
    of the reporting date (the scripts/163 rule).
  * Abnormal return (benchmarks):
      mkt_adj  r_it - vwretd_t                                   (PRIMARY)
      mm       r_it - (a + b vwretd_t), (a, b) by OLS on [-250, -30]
      ff3      (r_it - rf_t) - (a + b' [MKT-RF, SMB, HML]_t), OLS on [-250, -30]
    Model benchmarks need >= 80% of the 221 estimation days.
  * Returns: 'simple' (PRIMARY) or 'log' (log1p of every return / factor).
  * Window SD: sample SD (ddof = 1) x 100 = daily percentage points; a window
    needs >= ceil(0.8 x its length) non-missing abnormal returns.
  * DV = SD(post) - SD(pre). The pre-window SD is the control that replaces
    e2_pre_sd ("same controls"): the outcome's own pre-period level.

Inference: the statements of scripts/165 (CV1, CV3, WCR/WCU/Webb, WCR CI
inversion, MDE) are lifted verbatim through the ast module, as scripts/249
does; ladder() adds OLS and HC1 rows from statsmodels. gate_ladder()
re-runs the lifted code on 165's own design and must reproduce t26 / t28
exactly before any v5 estimate is trusted.
"""
import ast
import importlib.util as _ilu
import math
from datetime import timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats

T2 = Path('outputs/tables/essay2_v2')
OUT = Path('outputs/essay2_v5')
TREAT = 'fcc_form499'
SEED = 499
COVERAGE = 0.80
EST_WIN = (-250, -30)
PRE_PRIMARY, POST_PRIMARY = (-60, -11), (1, 20)
CONTROLS = ['delay_w', 'firm_size_log', 'leverage', 'roa', 'health_breach', 'prior_events']
NESTED = {   # scripts/163 SPECS, with the v5 pre-window SD in place of e2_pre_sd
    'M1': ['delay_w', 'pre_sd'],
    'M2': ['delay_w', 'pre_sd', 'firm_size_log', 'leverage', 'roa'],
    'M3': ['delay_w', 'pre_sd', 'firm_size_log', 'leverage', 'roa', TREAT],
    'M4': ['delay_w', 'pre_sd', 'firm_size_log', 'leverage', 'roa', TREAT,
           'health_breach', 'prior_events'],
}
XS4 = NESTED['M4']


def load_sample():
    fin = pd.read_csv(T2 / 't1_final_sample.csv', low_memory=False)
    assert len(fin) == 333, f'sample {len(fin)} != 333'
    assert int(fin[TREAT].sum()) == 104, 'treated events != 104'
    assert fin['final_cik'].nunique() == 82, 'G != 82'
    assert fin.loc[fin[TREAT] == 1, 'final_cik'].nunique() == 12, 'G1 != 12'
    fin['rdt'] = pd.to_datetime(fin['reported_date'])
    fin['permno'] = fin['permno'].astype(int)
    return fin


# ---------------------------------------------------------------- market data
_s = _ilu.spec_from_file_location('crsp_daily', 'scripts/254_crsp_daily.py')
crsp_daily = _ilu.module_from_spec(_s)
_s.loader.exec_module(crsp_daily)


class Market:
    """Calendar-aligned returns for every permno, plus market and FF3 factors."""

    def __init__(self, permnos=None, verbose=False):
        mkt = pd.read_csv('Data/wrds/market_indices.csv', usecols=['date', 'vwretd'])
        mkt['date'] = pd.to_datetime(mkt['date'])
        mkt = mkt.sort_values('date').reset_index(drop=True)
        ff = pd.read_csv('Data/wrds/fama_french_factors.csv')
        ff['date'] = pd.to_datetime(ff['date'])
        ff = ff.rename(columns={'MKT-RF': 'mktrf', 'SMB': 'smb', 'HML': 'hml', 'RF_FF3': 'rf'})
        cal = mkt.merge(ff[['date', 'mktrf', 'smb', 'hml', 'rf']], on='date', how='left')
        for c in ['mktrf', 'smb', 'hml', 'rf']:
            cal[c] = cal[c] / 100.0          # Ken French files are in percent
        assert cal[['mktrf', 'smb', 'hml', 'rf']].notna().all().all(), 'FF3 gap on a CRSP day'
        self.cal = cal
        self.dates = cal['date'].to_numpy()
        self.idx = {d: i for i, d in enumerate(cal['date'])}
        crsp = crsp_daily.load(['permno', 'date', 'ret'], verbose=verbose)
        crsp['date'] = pd.to_datetime(crsp['date'])
        crsp['ret'] = pd.to_numeric(crsp['ret'], errors='coerce')
        crsp = crsp.dropna(subset=['ret'])
        if permnos is not None:
            crsp = crsp[crsp['permno'].isin(set(permnos))]
        self.R = {}
        n = len(cal)
        for p, g in crsp.groupby('permno'):
            a = np.full(n, np.nan)
            pos = g['date'].map(self.idx)
            ok = pos.notna()
            a[pos[ok].astype(int).to_numpy()] = g.loc[ok, 'ret'].to_numpy()
            self.R[int(p)] = a

    def anchor(self, permno, when):
        """Calendar position of the trading day nearest `when`, or None."""
        a = self.R.get(int(permno))
        if a is None or pd.isna(when):
            return None
        when = np.datetime64(pd.Timestamp(when))
        gaps = np.abs(self.dates - when)
        pos = int(np.argmin(gaps))
        if gaps[pos] > np.timedelta64(7, 'D'):
            return None
        near = np.abs(self.dates - when) <= np.timedelta64(7, 'D')
        if not np.isfinite(a[near]).any():           # stock not trading near the date
            return None
        return pos

    def abnormal(self, permno, pos, bench='mkt_adj', rtype='simple'):
        """Abnormal-return vector over the whole calendar for one event, or None
        when a model benchmark lacks 80% of its estimation window."""
        r = self.R[int(permno)]
        c = self.cal
        tr = np.log1p if rtype == 'log' else (lambda x: x)
        if bench == 'mkt_adj':
            return tr(r) - tr(c['vwretd'].to_numpy())
        lo, hi = pos + EST_WIN[0], pos + EST_WIN[1]
        if lo < 0:
            return None
        sl = slice(lo, hi + 1)
        if bench == 'mm':
            y = tr(r)
            F = tr(c['vwretd'].to_numpy())[:, None]
        elif bench == 'ff3':
            y = tr(r) - tr(c['rf'].to_numpy())
            F = np.column_stack([tr(c[k].to_numpy()) for k in ['mktrf', 'smb', 'hml']])
        else:
            raise ValueError(bench)
        ok = np.isfinite(y[sl])
        if ok.sum() < math.ceil(COVERAGE * (hi - lo + 1)):
            return None
        Xe = np.column_stack([np.ones(ok.sum()), F[sl][ok]])
        coef = np.linalg.lstsq(Xe, y[sl][ok], rcond=None)[0]
        return y - np.column_stack([np.ones(len(y)), F]) @ coef

    @staticmethod
    def window_sd(ar, pos, win):
        lo, hi = pos + win[0], pos + win[1]
        length = hi - lo + 1
        if ar is None or lo < 0 or hi >= len(ar):
            v = ar[max(lo, 0):min(hi, len(ar) - 1) + 1] if ar is not None else np.array([])
            n_ok = int(np.isfinite(v).sum())
            return np.nan, n_ok, length
        v = ar[lo:hi + 1]
        n_ok = int(np.isfinite(v).sum())
        if n_ok < math.ceil(COVERAGE * length):
            return np.nan, n_ok, length
        return float(np.nanstd(v, ddof=1) * 100.0), n_ok, length


def build_dv(fin, M, pre=PRE_PRIMARY, post=POST_PRIMARY, bench='mkt_adj',
             rtype='simple', date_col='rdt'):
    """Per-event pre_sd, post_sd, dv, coverage counts and a drop reason."""
    rows = []
    for _, r in fin.iterrows():
        pos = M.anchor(r['permno'], r[date_col])
        if pos is None:
            rows.append(dict(pre_sd=np.nan, post_sd=np.nan, n_pre=0, n_post=0,
                             drop_reason='no trading day within 7 days of the reporting date'))
            continue
        ar = M.abnormal(r['permno'], pos, bench, rtype)
        if ar is None:
            rows.append(dict(pre_sd=np.nan, post_sd=np.nan, n_pre=0, n_post=0,
                             drop_reason='estimation window < 80% of [-250,-30]'))
            continue
        a, na, la = M.window_sd(ar, pos, pre)
        b, nb, lb = M.window_sd(ar, pos, post)
        why = ''
        if np.isnan(a) and np.isnan(b):
            why = f'pre {na}/{la} and post {nb}/{lb} below 80%'
        elif np.isnan(a):
            why = f'pre {na}/{la} below 80%'
        elif np.isnan(b):
            why = f'post {nb}/{lb} below 80%'
        rows.append(dict(pre_sd=a, post_sd=b, n_pre=na, n_post=nb, drop_reason=why,
                         anchor_date=pd.Timestamp(M.dates[pos]).date()))
    out = pd.DataFrame(rows, index=fin.index)
    out['dv'] = out['post_sd'] - out['pre_sd']
    return out


# ---------------------------------------------------------------- inference
SRC165 = Path('scripts/165_essay2_inference_ladder.py')
_KEEP = {'XtX', 'XtX_inv', 'beta', 'resid', 'b_t', 'adj', 'V1', 'se_cv1',
         'bbar', 'V3', 'se_cv3', 'others', 'Sg_X', 'a_row', 'B_MAIN',
         'p_wcr', 'p_wcu', 'p_webb', 'ci_lo', 'ci_hi', 'fit_hc3', 'se_hc3',
         'p_hc3', 'p_cv1', 'p_cv3', 'tcrit', 'mult', 'mde', 'meat', 'betas_del'}
_KEEP_DEFS = {'wcb_p', 'invert_ci'}


def _targets(node):
    out = set()
    for t in (node.targets if isinstance(node, ast.Assign) else [node.target]):
        for n in ast.walk(t):
            if isinstance(n, ast.Name):
                out.add(n.id)
    return out


def _lift():
    picked = []
    for node in ast.parse(SRC165.read_text(encoding='utf-8')).body:
        if isinstance(node, ast.FunctionDef) and node.name in _KEEP_DEFS:
            picked.append(node)
        elif isinstance(node, (ast.Assign, ast.AugAssign)) and _targets(node) & _KEEP:
            picked.append(node)
        elif isinstance(node, ast.For):
            bt = set()
            for s in node.body:
                if isinstance(s, (ast.Assign, ast.AugAssign)):
                    bt |= _targets(s)
            if bt & {'meat', 'betas_del'}:
                picked.append(node)
    return compile(ast.Module(body=picked, type_ignores=[]), str(SRC165), 'exec')


LADDER = _lift()


def ladder(df, ycol, xcols, cluster='final_cik', treat=TREAT, full=True):
    """Run 165's ladder statements on df. full=False skips the wild bootstrap
    (point estimate, OLS/HC1/HC3/CV1/CV3 only) for cheap repeated use."""
    d = df.dropna(subset=[ycol] + xcols).reset_index(drop=True)
    # a control constant within a subsample (e.g. no health breach in a size
    # cell) is dropped and recorded; the treatment column is never dropped
    dropped = [c for c in xcols if c != treat and d[c].astype(float).nunique() < 2]
    xcols = [c for c in xcols if c not in dropped]
    Y = d[ycol].astype(float).to_numpy()
    X = sm.add_constant(d[xcols].astype(float), has_constant='add').to_numpy()
    cols = ['const'] + list(xcols)
    G_ids, G_inv = np.unique(d[cluster].to_numpy(), return_inverse=True)
    G = len(G_ids)
    n, k = X.shape
    ti = cols.index(treat)
    res = dict(N=n, k=k, G=G, G1=int(d.loc[d[treat] == 1, cluster].nunique()),
               n_treated=int(d[treat].sum()), coef=None, dropped_constant=';'.join(dropped))
    fit = sm.OLS(Y, X).fit()
    res['coef'] = float(fit.params[ti])
    res['se_ols'], res['p_ols'] = float(fit.bse[ti]), float(fit.pvalues[ti])
    f1 = sm.OLS(Y, X).fit(cov_type='HC1', use_t=True)
    res['se_hc1'], res['p_hc1'] = float(f1.bse[ti]), float(f1.pvalues[ti])
    f3 = sm.OLS(Y, X).fit(cov_type='HC3', use_t=True)
    res['se_hc3'], res['p_hc3'] = float(f3.bse[ti]), float(f3.pvalues[ti])
    res['r2'] = float(fit.rsquared)
    res['df_hc'] = n - k
    if full:
        ns = dict(np=np, sm=sm, stats=stats, rng=np.random.default_rng(SEED),
                  Y=Y, X=X, ti=ti, G_inv=G_inv, G=G, G1=res['G1'], n=n, k=k)
        exec(LADDER, ns)
        assert abs(ns['b_t'] - res['coef']) < 1e-10
        for kk in ['se_cv1', 'p_cv1', 'se_cv3', 'p_cv3', 'p_wcr', 'p_wcu', 'p_webb',
                   'ci_lo', 'ci_hi', 'mde', 'tcrit']:
            res[kk if not kk.startswith('ci_') else 'wcr_' + kk] = float(ns[kk])
        res['B_wcb'] = int(ns['B_MAIN'])
        betas_del = ns['betas_del']
    else:
        betas_del, res = _cv_only(X, Y, G_inv, G, ti, n, k, res)
    res['ci3_lo'] = res['coef'] - res['tcrit'] * res['se_cv3']
    res['ci3_hi'] = res['coef'] + res['tcrit'] * res['se_cv3']
    res['jack_coefs'] = pd.Series(betas_del[:, ti], index=G_ids)
    res.update(cluster_diag(X, G_inv, G, ti))
    return res


def _cv_only(X, Y, G_inv, G, ti, n, k, res):
    XtX_inv = np.linalg.inv(X.T @ X)
    beta = XtX_inv @ (X.T @ Y)
    resid = Y - X @ beta
    meat = np.zeros((k, k))
    for g in range(G):
        m = G_inv == g
        sg = X[m].T @ resid[m]
        meat += np.outer(sg, sg)
    adj = (G / (G - 1)) * ((n - 1) / (n - k))
    se1 = math.sqrt((adj * XtX_inv @ meat @ XtX_inv)[ti, ti])
    bd = np.zeros((G, k))
    for g in range(G):
        m = G_inv != g
        bd[g] = np.linalg.lstsq(X[m], Y[m], rcond=None)[0]
    bb = bd.mean(0)
    se3 = math.sqrt(((G - 1) / G * (bd - bb).T @ (bd - bb))[ti, ti])
    tq = stats.t.ppf(0.975, G - 1)
    b = beta[ti]
    res.update(se_cv1=se1, p_cv1=2 * stats.t.sf(abs(b / se1), G - 1),
               se_cv3=se3, p_cv3=2 * stats.t.sf(abs(b / se3), G - 1), tcrit=tq,
               mde=(tq + stats.t.ppf(0.80, G - 1)) * se3)
    return bd, res


def cluster_diag(X, G_inv, G, ti):
    """165's D2 block: cluster-size CV and Carter-Schnepel-Steigerwald G*."""
    k = X.shape[1]
    sizes = np.bincount(G_inv)
    others = [i for i in range(k) if i != ti]
    xt_res = X[:, ti] - X[:, others] @ np.linalg.lstsq(X[:, others], X[:, ti], rcond=None)[0]
    gam = np.array([np.sum(xt_res[G_inv == g] ** 2) for g in range(G)])
    Gamma = np.sum((gam - gam.mean()) ** 2) / (G * gam.mean() ** 2)
    return dict(G_star=float(G / (1 + Gamma)),
                cv_sizes_ddof0=float(sizes.std(ddof=0) / sizes.mean()),
                cv_sizes_ddof1=float(sizes.std(ddof=1) / sizes.mean()))


def ladder_rows(r, label):
    """The eight-rung ladder as rows."""
    b, n, k, G = r['coef'], r['N'], r['k'], r['G']
    th = stats.t.ppf(0.975, n - k)
    tq = r['tcrit']
    base = dict(spec=label, coef=b, N=n, n_treated=r['n_treated'], G=G, G1=r['G1'])
    rows = [
        dict(base, rung='OLS (classical)', se=r['se_ols'], df=n - k, p=r['p_ols'],
             ci_lo=b - th * r['se_ols'], ci_hi=b + th * r['se_ols']),
        dict(base, rung='HC1', se=r['se_hc1'], df=n - k, p=r['p_hc1'],
             ci_lo=b - th * r['se_hc1'], ci_hi=b + th * r['se_hc1']),
        dict(base, rung='HC3', se=r['se_hc3'], df=n - k, p=r['p_hc3'],
             ci_lo=b - th * r['se_hc3'], ci_hi=b + th * r['se_hc3']),
        dict(base, rung='CV1 parent filer entity', se=r['se_cv1'], df=G - 1, p=r['p_cv1'],
             ci_lo=b - tq * r['se_cv1'], ci_hi=b + tq * r['se_cv1']),
        dict(base, rung='CV3 cluster jackknife (PRIMARY)', se=r['se_cv3'], df=G - 1,
             p=r['p_cv3'], ci_lo=r['ci3_lo'], ci_hi=r['ci3_hi']),
    ]
    if 'p_wcr' in r:
        rows += [
            dict(base, rung=f'WCR restricted Rademacher (B={r["B_wcb"]:,})', se=np.nan,
                 df=np.nan, p=r['p_wcr'], ci_lo=r['wcr_ci_lo'], ci_hi=r['wcr_ci_hi']),
            dict(base, rung=f'WCU unrestricted Rademacher (B={r["B_wcb"]:,})', se=np.nan,
                 df=np.nan, p=r['p_wcu'], ci_lo=np.nan, ci_hi=np.nan),
            dict(base, rung='WCR Webb six-point (B=9,999)', se=np.nan, df=np.nan,
                 p=r['p_webb'], ci_lo=np.nan, ci_hi=np.nan),
        ]
    return rows


def design_resolution(r, sd_ctrl, sesoi_mult=0.25, target_ann=5.0):
    """165 Part E formulas, plus the asymptotic floor (k -> inf)."""
    G, G1, b, se = r['G'], r['G1'], r['coef'], r['se_cv3']
    Gc = G - G1
    m = sesoi_mult * sd_ctrl
    t95 = stats.t.ppf(0.95, G - 1)
    sigma_c = se / math.sqrt(1 / G1 + 1 / Gc)
    target = target_ann / math.sqrt(252)
    need = None
    for kk in range(2, 20000):
        se_k = sigma_c * math.sqrt(1 / kk + 1 / Gc)
        if (stats.t.ppf(.975, kk + Gc - 1) + stats.t.ppf(.80, kk + Gc - 1)) * se_k <= target:
            need = kk
            break
    floor = (stats.norm.ppf(.975) + stats.norm.ppf(.80)) * sigma_c / math.sqrt(Gc)
    return dict(sd_control=sd_ctrl, sesoi_daily=m, sesoi_ann=m * math.sqrt(252),
                mde80_daily=r['mde'], mde80_ann=r['mde'] * math.sqrt(252),
                mde_over_sesoi=r['mde'] / m,
                ci90_lo=b - t95 * se, ci90_hi=b + t95 * se,
                ci90_inside_sesoi=bool((b - t95 * se > -m) and (b + t95 * se < m)),
                tost_p_lower=float(1 - stats.t.cdf((b + m) / se, G - 1)),
                tost_p_upper=float(stats.t.cdf((b - m) / se, G - 1)),
                required_parents_5pp_ann=need if need else '>20000',
                floor_daily=floor, floor_ann=floor * math.sqrt(252),
                share_treated=None)


def bh(pvals, q=0.05):
    """Benjamini-Hochberg: (adjusted p, reject) in input order."""
    p = np.asarray(pvals, float)
    m = len(p)
    o = np.argsort(p)
    adj = np.empty(m)
    run = 1.0
    for rank in range(m, 0, -1):
        i = o[rank - 1]
        run = min(run, p[i] * m / rank)
        adj[i] = run
    return adj, adj <= q


def gate_ladder():
    """Lifted 165 code on 165's own design must reproduce t26/t28/t25."""
    fin = pd.read_csv(T2 / 't1_final_sample.csv', low_memory=False)
    xs = ['delay_w', 'e2_pre_sd', 'firm_size_log', 'leverage', 'roa', TREAT,
          'health_breach', 'prior_events']
    r = ladder(fin, 'e2_vol_change', xs)
    t26 = pd.read_csv(T2 / 't26_inference_ladder.csv')
    t28 = pd.read_csv(T2 / 't28_design_resolution.csv')
    assert round(r['coef'], 4) == t26.loc[0, 'coef']
    for i, key in enumerate(['se_hc3', 'se_cv1', 'se_cv3']):
        assert round(r[key], 4) == t26.loc[i, 'se'], (key, r[key], t26.loc[i, 'se'])
    for i, key in enumerate(['p_hc3', 'p_cv1', 'p_cv3', 'p_wcr', 'p_wcu', 'p_webb']):
        assert round(r[key], 4) == t26.loc[i, 'p'], (key, r[key], t26.loc[i, 'p'])
    assert round(r['mde'], 4) == t28.loc[0, 'mde_daily']
    import re
    line = [ln for ln in Path('outputs/ESSAY2_QUERY4_PART_DE.md').read_text(encoding='utf-8').splitlines()
            if 'effective clusters G*' in ln][0]
    cv_c, gs_c = map(float, re.findall(r'sizes: ([\d.]+) .*?: ([\d.]+) of G', line)[0])
    assert round(r['cv_sizes_ddof0'], 2) == cv_c, (r['cv_sizes_ddof0'], cv_c)
    assert round(r['G_star'], 1) == gs_c, (r['G_star'], gs_c)
    return r
