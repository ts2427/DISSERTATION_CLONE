"""
ESSAY 3 QUERY 2 — STAGE 2 PART F (+ I): H6 ESTIMATION ON THE v2 EXECUTIVE-DEPARTURE OUTCOME (NEW)
================================================================================================
Sample: outputs/essay3_q2/e_analysis_sample.csv, in_analysis_sample == 1 (N = 338; scripts/199). Today's CANONICAL_V3;
constants_v3.json untouched; results go to outputs/essay3_q2/constants_essay3_q2.json (assertion baseline: the first
run writes it, later runs assert against it).
Outcome: final classifier v2 (scripts/195, 6f7be7a), one departure per person within parent CIK, dated to its earliest
disclosing filing (ruling 1). Treatment fcc_form499. Anchor: reported_date (primary).
F1  LPM exec_departure_{30,90,180}_rd ~ fcc_form499 + prior_breaches_1yr + health_breach + firm_size_log + leverage + roa
    + baseline_exec_rate_py_rd (F2) + prior12m_mktadj_ret_rd. Inference ladder, as Essay 2 (scripts/165, ported
    unchanged): HC3; CV1 and CV3 (cluster jackknife) on parent CIK with t(G-1); restricted wild cluster bootstrap
    (Rademacher, B = 99,999, CV1 t) with the 95% CI by inversion (B = 9,999). G, G1, G* (Carter-Schnepel-Steigerwald on
    treatment partial leverage), cluster-size CV. Logit AME (cluster-robust) as corroboration. MDE80 = (t.975 + t.80) at
    df G-1 times the CV3 SE.
F4  Placebo: the primary specification with exec departure in (t0 - 180d, t0].
F2  Baseline departure rate distribution, treated vs control.
F3  Sensitivities, one row each per window (CV3 inference + WCR p with B = 9,999): year FE; two-digit SIC FE (cell
    composition reported); breach_date anchor; excluding pre-announced departures; excluding the F2 control;
    restatement-dated outcome (ruling 1 sensitivity); misclassification correction from the recall audit (outcome
    divided by the stratum's measured executive-departure recall; point and CI-endpoint scenarios); leave-one-parent-
    CIK-out (range, sign flips, T-Mobile and Sprint deletions named).
F5  CEO-only: counts by group; LPM (CV3) only where both groups have >= 10 events.
F6  Director-only: counts.
I   Test ledger; Benjamini-Hochberg within families (primary H6, sensitivities, placebo, CEO-only) on CV3 p-values.
Outputs: outputs/essay3_q2/f1_ladder.csv, f1_logit_ame.csv, f1_cluster_diagnostics.csv, f4_placebo.csv, f2_baseline.csv,
         f3_sensitivities.csv, f3_sic2_cells.csv, f3_loco.csv, f5_ceo.csv, f6_director.csv, i_tests.csv,
         constants_essay3_q2.json, 202_estimation.log
"""

import sys
import json
from pathlib import Path
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats
from statsmodels.stats.multitest import multipletests

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
OUT = Path('outputs/essay3_q2')
L = []
rng = np.random.default_rng(3)  # seed: Essay 3


def log(m=''):
    print(m, flush=True)
    L.append(str(m))


def hdr(t):
    log('\n' + '=' * 100 + '\n' + t + '\n' + '=' * 100)


TREAT = 'fcc_form499'
BASE = ['prior_breaches_1yr', 'health_breach', 'firm_size_log', 'leverage', 'roa']
d0 = pd.read_csv(OUT / 'e_analysis_sample.csv', low_memory=False)
d0 = d0[d0['in_analysis_sample'] == 1].reset_index(drop=True)
CTRL = {'rd': BASE + ['baseline_exec_rate_py_rd', 'prior12m_mktadj_ret_rd'],
        'bd': BASE + ['baseline_exec_rate_py_bd', 'prior12m_mktadj_ret_bd']}
names = {1283699: 'T-Mobile', 101830: 'Sprint'}


def ladder(d, ycol, xcols, B=99_999, B_ci=9_999, full=True, fe=None):
    d = d.dropna(subset=[ycol] + xcols).reset_index(drop=True)
    Xdf = d[xcols].astype(float)
    if fe is not None:
        Xdf = pd.concat([Xdf, pd.get_dummies(d[fe].astype(str), prefix=fe, drop_first=True).astype(float)], axis=1)
        Xdf = Xdf.loc[:, Xdf.std() > 0]
    Xdf = sm.add_constant(Xdf, has_constant='add')
    X, Y = Xdf.to_numpy(), d[ycol].astype(float).to_numpy()
    cols = list(Xdf.columns)
    ti = cols.index(TREAT)
    G_ids, G_inv = np.unique(d['final_cik'].to_numpy(), return_inverse=True)
    G = len(G_ids)
    G1 = d.loc[d[TREAT] == 1, 'final_cik'].nunique()
    n, k = X.shape
    XtX_inv = np.linalg.pinv(X.T @ X)
    beta = XtX_inv @ (X.T @ Y)
    resid = Y - X @ beta
    b_t = beta[ti]
    meat = np.zeros((k, k))
    for g in range(G):
        sg = X[G_inv == g].T @ resid[G_inv == g]
        meat += np.outer(sg, sg)
    adj = (G / (G - 1)) * ((n - 1) / (n - k))
    se_cv1 = np.sqrt((adj * XtX_inv @ meat @ XtX_inv)[ti, ti])
    betas_del = np.zeros((G, k))
    for g in range(G):
        m = G_inv != g
        betas_del[g] = np.linalg.lstsq(X[m], Y[m], rcond=None)[0]
    bbar = betas_del.mean(0)
    se_cv3 = np.sqrt(((G - 1) / G * (betas_del - bbar).T @ (betas_del - bbar))[ti, ti])
    fit_hc3 = sm.OLS(Y, X).fit(cov_type='HC3', use_t=True)
    tcrit = stats.t.ppf(0.975, G - 1)
    res = dict(y=ycol, n=n, G=G, G1=G1, coef=round(b_t, 4),
               se_hc3=round(fit_hc3.bse[ti], 4), p_hc3=round(fit_hc3.pvalues[ti], 4),
               se_cv1=round(se_cv1, 4), p_cv1=round(2 * (1 - stats.t.cdf(abs(b_t / se_cv1), G - 1)), 4),
               se_cv3=round(se_cv3, 4), p_cv3=round(2 * (1 - stats.t.cdf(abs(b_t / se_cv3), G - 1)), 4),
               ci_cv3_lo=round(b_t - tcrit * se_cv3, 4), ci_cv3_hi=round(b_t + tcrit * se_cv3, 4),
               mde80_cv3=round((stats.t.ppf(.975, G - 1) + stats.t.ppf(.80, G - 1)) * se_cv3, 4),
               treated_mean=round(d.loc[d[TREAT] == 1, ycol].mean(), 4),
               control_mean=round(d.loc[d[TREAT] == 0, ycol].mean(), 4))
    others = [i for i in range(k) if i != ti]
    Sg_X = [X[G_inv == g] for g in range(G)]
    a_row = XtX_inv[ti]

    def wcb_p(beta0, BB, restricted=True):
        if restricted:
            Xr = X[:, others]
            br = np.linalg.lstsq(Xr, Y - beta0 * X[:, ti], rcond=None)[0]
            fit = Xr @ br + beta0 * X[:, ti]
        else:
            fit = X @ beta
        u = Y - fit
        V = rng.choice([-1.0, 1.0], size=(G, BB))
        S = np.stack([Sg_X[g].T @ u[G_inv == g] for g in range(G)], axis=1)
        XtY = (X.T @ fit)[:, None] + S @ V
        Bs = XtX_inv @ XtY
        aq = np.array([a_row @ (Sg_X[g].T @ fit[G_inv == g]) for g in range(G)])
        a_s = a_row @ S
        Pm = np.stack([a_row @ (Sg_X[g].T @ Sg_X[g]) for g in range(G)])
        W = aq[:, None] + a_s[:, None] * V - Pm @ Bs
        t_star = (Bs[ti] - beta0) / np.sqrt(adj * np.sum(W ** 2, axis=0))
        t_obs = (b_t - beta0) / se_cv1
        return (np.sum(np.abs(t_star) >= abs(t_obs)) + 1) / (BB + 1)

    res['p_wcr'] = round(wcb_p(0.0, B), 4)
    res['B_wcr'] = B
    if full:
        def bisect(lo, hi, side):
            for _ in range(24):
                mid = (lo + hi) / 2
                if wcb_p(mid, B_ci) < 0.05:
                    lo, hi = (mid, hi) if side == 'low' else (lo, mid)
                else:
                    lo, hi = (lo, mid) if side == 'low' else (mid, hi)
            return (lo + hi) / 2
        res['ci_wcr_lo'] = round(bisect(b_t - 8 * se_cv1, b_t, 'low'), 4)
        res['ci_wcr_hi'] = round(bisect(b_t, b_t + 8 * se_cv1, 'high'), 4)
        xt_res = X[:, ti] - X[:, others] @ np.linalg.lstsq(X[:, others], X[:, ti], rcond=None)[0]
        plev = np.array([np.sum(xt_res[G_inv == g] ** 2) for g in range(G)])
        Gamma = np.sum((plev - plev.mean()) ** 2) / (G * plev.mean() ** 2)
        sizes = np.bincount(G_inv)
        res['G_star'] = round(G / (1 + Gamma), 1)
        res['cluster_size_cv'] = round(sizes.std(ddof=0) / sizes.mean(), 3)
        del_t = betas_del[:, ti]
        res['_loco'] = pd.DataFrame(dict(deleted_parent_cik=G_ids, coef_without=np.round(del_t, 4),
                                         cluster_size=sizes, partial_leverage_share=np.round(plev / plev.sum(), 4)))
    return res


pub = lambda r: {k: v for k, v in r.items() if not k.startswith('_')}
C = {}

hdr(f'F1 — PRIMARY: LPM, notification anchor (N={len(d0)}; treated {int(d0[TREAT].sum())}; '
    f'parent CIKs {d0["final_cik"].nunique()}, treated parent CIKs {d0.loc[d0[TREAT] == 1, "final_cik"].nunique()})')
F1, ame, loco = [], [], []
for w in (30, 90, 180):
    r = ladder(d0, f'exec_departure_{w}_rd', [TREAT] + CTRL['rd'])
    r['window'] = w
    F1.append(r)
    lo = r['_loco']
    lo['window'] = w
    loco.append(lo)
    C.update({f'F1_{w}_{k}': v for k, v in pub(r).items() if k not in ('y',)})
    log(f"  {w}d: coef {r['coef']:+.4f} | HC3 p {r['p_hc3']:.4f} | CV1 p {r['p_cv1']:.4f} | CV3 SE {r['se_cv3']:.4f} "
        f"p {r['p_cv3']:.4f} CI [{r['ci_cv3_lo']:+.4f}, {r['ci_cv3_hi']:+.4f}] | WCR p {r['p_wcr']:.4f} CI "
        f"[{r['ci_wcr_lo']:+.4f}, {r['ci_wcr_hi']:+.4f}] | G {r['G']} G1 {r['G1']} G* {r['G_star']} CV {r['cluster_size_cv']} "
        f"| MDE80 {r['mde80_cv3']:.4f} | means T {r['treated_mean']:.3f} C {r['control_mean']:.3f}")
    dd = d0.dropna(subset=CTRL['rd'])
    Xl = sm.add_constant(dd[[TREAT] + CTRL['rd']].astype(float))
    try:
        lg = sm.Logit(dd[f'exec_departure_{w}_rd'].astype(int), Xl).fit(
            disp=0, cov_type='cluster', cov_kwds={'groups': dd['final_cik']})
        mf = lg.get_margeff(at='overall', dummy=True).summary_frame().loc[TREAT]
        ame.append(dict(window=w, ame=round(mf['dy/dx'], 4), se_cluster=round(mf['Std. Err.'], 4),
                        p=round(mf['Pr(>|z|)'], 4), ci_lo=round(mf['Conf. Int. Low'], 4), ci_hi=round(mf['Cont. Int. Hi.'], 4)))
    except Exception as e:
        ame.append(dict(window=w, ame=np.nan, note=f'logit failed: {str(e)[:80]}'))
FL = pd.DataFrame([pub(r) for r in F1])
FL.to_csv(OUT / 'f1_ladder.csv', index=False)
pd.DataFrame(ame).to_csv(OUT / 'f1_logit_ame.csv', index=False)
log('  Logit AME (cluster-robust, corroboration): ' + '; '.join(
    f"{a['window']}d {a['ame']:+.4f} (SE {a['se_cluster']:.4f}, p {a['p']:.4f})" for a in ame if not pd.isna(a['ame'])))
LO = pd.concat(loco)
LO.to_csv(OUT / 'f1_cluster_diagnostics.csv', index=False)

hdr('F4 — PLACEBO: executive departure in (t0 - 180d, t0], primary specification')
r4 = ladder(d0, 'placebo_exec_departure_rd', [TREAT] + CTRL['rd'])
pd.DataFrame([pub(r4)]).to_csv(OUT / 'f4_placebo.csv', index=False)
C.update({f'F4_{k}': v for k, v in pub(r4).items() if k != 'y'})
log(f"  coef {r4['coef']:+.4f} | HC3 p {r4['p_hc3']:.4f} | CV3 p {r4['p_cv3']:.4f} CI [{r4['ci_cv3_lo']:+.4f}, "
    f"{r4['ci_cv3_hi']:+.4f}] | WCR p {r4['p_wcr']:.4f} CI [{r4['ci_wcr_lo']:+.4f}, {r4['ci_wcr_hi']:+.4f}] | means T "
    f"{r4['treated_mean']:.3f} C {r4['control_mean']:.3f}")

hdr('F2 — baseline executive-departure rate [t0 - 730d, t0 - 181d], per year')
f2 = []
for g, gl in [(1, 'treated'), (0, 'control')]:
    x = d0.loc[d0[TREAT] == g, 'baseline_exec_rate_py_rd']
    c = d0.loc[d0[TREAT] == g, 'baseline_exec_departures_rd']
    f2.append(dict(group=gl, n=len(x), mean_rate_py=round(x.mean(), 4), sd=round(x.std(), 4), median=round(x.median(), 4),
                   p75=round(x.quantile(.75), 4), max=round(x.max(), 4), share_zero=round((c == 0).mean(), 4),
                   mean_count=round(c.mean(), 3)))
F2 = pd.DataFrame(f2)
F2.to_csv(OUT / 'f2_baseline.csv', index=False)
log(F2.to_string(index=False))

hdr('F3 — SENSITIVITIES (one row per window; CV3 inference, WCR p with B = 9,999)')
RS = pd.read_csv(OUT / 'd3_audit_recall_by_stratum.csv')
rr = RS[(RS['field'] == 'exec departure (A)') & (RS['scoring'] == 'PRIMARY (verified)')].set_index('stratum')


def ci_bounds(s):
    lo, hi = s.strip('[]').split(', ')
    return float(lo), float(hi)


rec = {g: (float(rr.loc[g, 'recall']), *ci_bounds(rr.loc[g, 'recall_ci95'])) for g in ['treated', 'control']}
log(f"  Audit recall (exec, primary): treated {rec['treated'][0]:.3f} [{rec['treated'][1]:.3f}, {rec['treated'][2]:.3f}], "
    f"control {rec['control'][0]:.3f} [{rec['control'][1]:.3f}, {rec['control'][2]:.3f}]")
sic_cells = d0.groupby('sic2')[TREAT].agg(['size', 'sum']).rename(columns={'size': 'events', 'sum': 'treated'})
sic_cells['control'] = sic_cells['events'] - sic_cells['treated']
sic_cells.to_csv(OUT / 'f3_sic2_cells.csv')
log('  SIC2 cells containing treated events: ' + '; '.join(f"SIC {int(i)}: {int(r['treated'])} treated / {int(r['control'])} control"
                                                          for i, r in sic_cells[sic_cells['treated'] > 0].iterrows()))
sens = []
for w in (30, 90, 180):
    y = f'exec_departure_{w}_rd'
    rows = [('year FE (reported year)', d0, y, [TREAT] + CTRL['rd'], 'reported_year'),
            ('two-digit SIC FE', d0, y, [TREAT] + CTRL['rd'], 'sic2'),
            ('breach_date anchor', d0, f'exec_departure_{w}_bd', [TREAT] + CTRL['bd'], None),
            ('excluding pre-announced departures', d0, f'exec_departure_nopre_{w}_rd', [TREAT] + CTRL['rd'], None),
            ('excluding the F2 baseline control', d0, y, [TREAT] + BASE + ['prior12m_mktadj_ret_rd'], None),
            ('restatement-dated outcome (rs)', d0, f'rs_exec_departure_{w}_rd', [TREAT] + CTRL['rd'], None)]
    for scen, (rt, rc_) in [('recall-corrected, audit point estimates', (rec['treated'][0], rec['control'][0])),
                            ('recall-corrected, treated recall at CI low / control at CI high', (rec['treated'][1], rec['control'][2])),
                            ('recall-corrected, treated recall at CI high / control at CI low', (rec['treated'][2], rec['control'][1]))]:
        dc = d0.copy()
        dc['y_corr'] = dc[y] / np.where(dc[TREAT] == 1, rt, rc_)
        rows.append((scen + f' (r_T={rt:.3f}, r_C={rc_:.3f})', dc, 'y_corr', [TREAT] + CTRL['rd'], None))
    for lab, dd, yy, xx, fe in rows:
        r = ladder(dd, yy, xx, B=9_999, full=False, fe=fe)
        sens.append(dict(window=w, sensitivity=lab, **pub(r)))
S3 = pd.DataFrame(sens)
S3.to_csv(OUT / 'f3_sensitivities.csv', index=False)
log(S3[['window', 'sensitivity', 'n', 'coef', 'se_cv3', 'p_cv3', 'ci_cv3_lo', 'ci_cv3_hi', 'p_wcr']].to_string(index=False))

log('\n  Leave-one-parent-CIK-out (from the CV3 jackknife):')
lrows = []
for w in (30, 90, 180):
    lo = LO[LO['window'] == w]
    b = [r for r in F1 if r['window'] == w][0]['coef']
    flips = int((np.sign(lo['coef_without']) != np.sign(b)).sum())
    imax = lo.iloc[(lo['coef_without'] - b).abs().argmax()]
    tm = lo[lo['deleted_parent_cik'] == 1283699]['coef_without']
    sp = lo[lo['deleted_parent_cik'] == 101830]['coef_without']
    lrows.append(dict(window=w, full_coef=b, loco_min=lo['coef_without'].min(), loco_max=lo['coef_without'].max(),
                      sign_flips=flips, of_G=len(lo), largest_move_cik=int(imax['deleted_parent_cik']),
                      largest_move_coef=imax['coef_without'],
                      without_TMobile=tm.iloc[0] if len(tm) else np.nan, without_Sprint=sp.iloc[0] if len(sp) else np.nan))
    log(f"  {w}d: full {b:+.4f}; range [{lo['coef_without'].min():+.4f}, {lo['coef_without'].max():+.4f}]; sign flips "
        f"{flips}/{len(lo)}; without T-Mobile {lrows[-1]['without_TMobile']:+.4f}; without Sprint "
        f"{lrows[-1]['without_Sprint']:+.4f}; largest move: deleting {int(imax['deleted_parent_cik'])} -> {imax['coef_without']:+.4f}")
pd.DataFrame(lrows).to_csv(OUT / 'f3_loco.csv', index=False)

hdr('F5 — CEO-only departures; F6 — director-only departures (counts)')
f5, f6 = [], []
for w in (30, 90, 180):
    t = int(d0.loc[d0[TREAT] == 1, f'ceo_departure_{w}_rd'].sum())
    c = int(d0.loc[d0[TREAT] == 0, f'ceo_departure_{w}_rd'].sum())
    row = dict(window=w, treated_events=t, control_events=c, treated_n=int(d0[TREAT].sum()), control_n=int((d0[TREAT] == 0).sum()))
    if t >= 10 and c >= 10:
        r = ladder(d0, f'ceo_departure_{w}_rd', [TREAT] + CTRL['rd'], B=9_999, full=False)
        row.update(estimated=True, coef=r['coef'], se_cv3=r['se_cv3'], p_cv3=r['p_cv3'])
    else:
        row.update(estimated=False, reason='fewer than 10 CEO departures in at least one group; counts only')
    f5.append(row)
    f6.append(dict(window=w, treated_events=int(d0.loc[d0[TREAT] == 1, f'director_departure_{w}_rd'].sum()),
                   control_events=int(d0.loc[d0[TREAT] == 0, f'director_departure_{w}_rd'].sum())))
F5, F6 = pd.DataFrame(f5), pd.DataFrame(f6)
F5.to_csv(OUT / 'f5_ceo.csv', index=False)
F6.to_csv(OUT / 'f6_director.csv', index=False)
log(F5.to_string(index=False))
log(F6.to_string(index=False))

hdr('I — TEST LEDGER and Benjamini-Hochberg within families (CV3 p-values)')
tests = [dict(family='primary H6', test=f'F1 exec departure {r["window"]}d', p=r['p_cv3'], p_wcr=r['p_wcr']) for r in F1]
tests += [dict(family='placebo', test='F4 pre-notification exec departure', p=r4['p_cv3'], p_wcr=r4['p_wcr'])]
tests += [dict(family='sensitivities', test=f"F3 {s['sensitivity']} {s['window']}d", p=s['p_cv3'], p_wcr=s['p_wcr'])
          for s in sens]
tests += [dict(family='CEO-only', test=f"F5 CEO {r['window']}d", p=r['p_cv3'], p_wcr=np.nan) for r in f5 if r.get('estimated')]
IT = pd.DataFrame(tests)
IT['p_bh'] = np.nan
for fam, g in IT.groupby('family'):
    IT.loc[g.index, 'p_bh'] = np.round(multipletests(g['p'], method='fdr_bh')[1], 4)
IT.to_csv(OUT / 'i_tests.csv', index=False)
log(f'Hypothesis tests in the new Essay 3 code: {len(IT)} (' + ', '.join(f'{k} {v}' for k, v in IT['family'].value_counts().items())
    + '). Descriptive/corroborating, not counted: logit AMEs (3), F2 distribution, F5/F6 counts, leave-one-out.')
log(IT[IT['family'].isin(['primary H6', 'placebo', 'CEO-only'])].to_string(index=False))
log(f"Sensitivity family: min raw CV3 p {IT.loc[IT.family == 'sensitivities', 'p'].min():.4f}; min BH-adjusted "
    f"{IT.loc[IT.family == 'sensitivities', 'p_bh'].min():.4f}")

# ---------------- constants + assertion baseline ----------------
C.update(N=len(d0), treated=int(d0[TREAT].sum()), control=int((d0[TREAT] == 0).sum()),
         parent_ciks=int(d0['final_cik'].nunique()), treated_parent_ciks=int(d0.loc[d0[TREAT] == 1, 'final_cik'].nunique()),
         n_tests=len(IT), classifier='scripts/195 v2 (6f7be7a, blob ec32364)')
C = {k: (v.item() if hasattr(v, 'item') else v) for k, v in C.items()}
cp_ = OUT / 'constants_essay3_q2.json'
if cp_.exists():
    old = json.loads(cp_.read_text())
    mism = {k: (old[k], v) for k, v in C.items() if k in old and old[k] != v}
    assert not mism, f'ASSERTION FAILURE vs Essay 3 baseline: {list(mism.items())[:5]}'
    log('\nAssertion check vs constants_essay3_q2.json: PASS')
else:
    cp_.write_text(json.dumps(C, indent=1))
    log('\nBaseline constants_essay3_q2.json WRITTEN (later runs assert against it)')
(OUT / '202_estimation.log').write_text('\n'.join(L) + '\n', encoding='utf-8')
