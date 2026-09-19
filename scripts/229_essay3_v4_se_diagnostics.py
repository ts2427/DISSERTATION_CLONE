"""
ESSAY 3 QUERY 2 — F1 STANDARD-ERROR DIAGNOSTICS (NEW; scripts/204)
===================================================================
Why the MDE jumps between 30 and 90 days. Same sample and specification as scripts/202 F1:
outputs/essay3_v4/e_analysis_sample.csv, in_analysis_sample == 1 (N = 338); LPM exec_departure_{w}_rd ~ fcc_form499 +
prior_breaches_1yr + health_breach + firm_size_log + leverage + roa + baseline_exec_rate_py_rd + prior12m_mktadj_ret_rd;
clusters = parent CIK (final_cik). Same CV1 / CV3 formulas as 202 (ported); the recomputed HC3, CV1 and CV3 SEs are
asserted equal to the committed f1_ladder.csv.
Per window:
  - SE at each rung: HC3, CV1, CV3. The wild cluster bootstrap (WCR) produces a p-value and an inverted CI, not an SE;
    its CI half-width / t.975(G-1) is shown as an IMPLIED SE (label kept), from the committed f1_ladder.csv.
  - G* (committed), outcome mean and variance.
  - CV3 SE, coefficient and MDE80 with T-Mobile (1283699) deleted.
  - Each parent CIK's share of the CV3 jackknife variance sum_g (b_-g - b_bar)^2; top five named.
  - Executive-departure base rates (events / N) by group, notification anchor.
Outputs: outputs/essay3_v4/f1_se_diagnostics.csv, f1_cv3_variance_shares.csv, 204_se_diagnostics.log

REBUILD V4 NOTE
---------------
Copied from scripts/204_essay3_q2_se_diagnostics.py. Only the data sources move; the method does not.

  event table   -> scripts/236 load_canonical() (CANONICAL_V4, v3's inherited
                   has_crsp_data / permno / covariates dropped and replaced)
  linkage       -> outputs/rebuild_v4/v4_212_links.csv
  covariates    -> outputs/rebuild_v4/219_covariates_v4.csv (gvkey-joined)
  filings       -> outcome_cik from outputs/rebuild_v4/234_outcome_cik.csv
  CRSP          -> Data/wrds_v4/
  outputs       -> outputs/essay3_v4/
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
OUT = Path('outputs/essay3_v4')

# --- REBUILD V4 ---------------------------------------------------------------
# The event table is loaded through scripts/236, never from CANONICAL_V4 directly.
# That file still carries has_crsp_data, permno and the four covariates INHERITED
# from v3; reading them would score the v3 sample under v4 labels. The loader drops
# them and re-attaches v4's own linkage (v4_212_links.csv) and covariates
# (219_covariates_v4.csv). Filings are keyed on outcome_cik, never final_cik.
import importlib.util as _ilu
_spec_v4 = _ilu.spec_from_file_location('v4loader', 'scripts/236_essay3_v4_loader.py')
V4 = _ilu.module_from_spec(_spec_v4)
_spec_v4.loader.exec_module(V4)
# -------------------------------------------------------------------------------

L = []


def log(m=''):
    print(m, flush=True)
    L.append(str(m))


TREAT = 'fcc_form499'
CTRL = ['prior_breaches_1yr', 'health_breach', 'firm_size_log', 'leverage', 'roa',
        'baseline_exec_rate_py_rd', 'prior12m_mktadj_ret_rd']
TM = 1283699
d0 = pd.read_csv(OUT / 'e_analysis_sample.csv', low_memory=False)
d0 = d0[d0['in_analysis_sample'] == 1].reset_index(drop=True)
FL = pd.read_csv(OUT / 'f1_ladder.csv').set_index('window')
ncol = next((c for c in ['org_name', 'company_name', 'organization', 'conm', 'company', 'name'] if c in d0.columns), None)
names = (d0.groupby('final_cik')[ncol].first().to_dict() if ncol else {})


def fit(d, y):
    d = d.dropna(subset=[y, TREAT] + CTRL).reset_index(drop=True)
    Xdf = sm.add_constant(d[[TREAT] + CTRL].astype(float), has_constant='add')
    X, Y = Xdf.to_numpy(), d[y].astype(float).to_numpy()
    ti = list(Xdf.columns).index(TREAT)
    ids, inv = np.unique(d['final_cik'].to_numpy(), return_inverse=True)
    G, (n, k) = len(ids), X.shape
    XtX_inv = np.linalg.pinv(X.T @ X)
    beta = XtX_inv @ (X.T @ Y)
    resid = Y - X @ beta
    meat = np.zeros((k, k))
    for g in range(G):
        sg = X[inv == g].T @ resid[inv == g]
        meat += np.outer(sg, sg)
    adj = (G / (G - 1)) * ((n - 1) / (n - k))
    se_cv1 = np.sqrt((adj * XtX_inv @ meat @ XtX_inv)[ti, ti])
    bd = np.array([np.linalg.lstsq(X[inv != g], Y[inv != g], rcond=None)[0][ti] for g in range(G)])
    dev2 = (bd - bd.mean()) ** 2
    se_cv3 = np.sqrt((G - 1) / G * dev2.sum())
    se_hc3 = sm.OLS(Y, X).fit(cov_type='HC3').bse[ti]
    mde = (stats.t.ppf(.975, G - 1) + stats.t.ppf(.80, G - 1)) * se_cv3
    return dict(n=n, G=G, coef=beta[ti], se_hc3=se_hc3, se_cv1=se_cv1, se_cv3=se_cv3, mde80=mde,
                y_mean=Y.mean(), y_var=Y.var(ddof=1)), pd.DataFrame(dict(final_cik=ids, coef_without=bd, dev2=dev2))


log('=' * 100 + '\nF1 SE DIAGNOSTICS (NEW, scripts/204) — N=%d; treated %d; parent CIKs %d; T-Mobile events in sample %d'
    % (len(d0), d0[TREAT].sum(), d0['final_cik'].nunique(), (d0['final_cik'] == TM).sum()) + '\n' + '=' * 100)
rows, shares = [], []
for w in (30, 90, 180):
    y = f'exec_departure_{w}_rd'
    full, jk = fit(d0, y)
    c = FL.loc[w]
    for s in ('se_hc3', 'se_cv1', 'se_cv3'):
        assert round(full[s], 4) == round(c[s], 4), f'{w}d {s}: recomputed {full[s]:.4f} != committed {c[s]:.4f}'
    assert round(full['coef'], 4) == round(c['coef'], 4)
    noTM, _ = fit(d0[d0['final_cik'] != TM], y)
    tcrit = stats.t.ppf(.975, int(c['G']) - 1)
    wcr_implied = (c['ci_wcr_hi'] - c['ci_wcr_lo']) / (2 * tcrit)
    jk['share'] = jk['dev2'] / jk['dev2'].sum()
    jk['name'] = jk['final_cik'].map(names)
    jk['treated_cluster'] = jk['final_cik'].map(d0.groupby('final_cik')[TREAT].max()).astype(int)
    jk['n_events'] = jk['final_cik'].map(d0['final_cik'].value_counts())
    jk['sign_flip'] = (np.sign(jk['coef_without']) != np.sign(full['coef'])).astype(int)
    jk['window'] = w
    shares.append(jk)
    top = jk.sort_values('share', ascending=False).head(5)
    flips = jk[jk['sign_flip'] == 1]
    # NOTE: these lines used to be logged HERE, before this window's header, so each
    # window's LOCO summary printed under the PREVIOUS window's heading and was read as
    # belonging to it. Every line below is emitted after the header AND carries its own
    # window prefix, so a line can never be attributed to the wrong window.
    ev = {g: (int(d0.loc[d0[TREAT] == g, y].sum()), int((d0[TREAT] == g).sum())) for g in (1, 0)}
    rows.append(dict(window=w, coef=round(full['coef'], 4), se_hc3=round(full['se_hc3'], 4), se_cv1=round(full['se_cv1'], 4),
                     se_cv3=round(full['se_cv3'], 4), wcr_ci_lo=c['ci_wcr_lo'], wcr_ci_hi=c['ci_wcr_hi'],
                     wcr_implied_se=round(wcr_implied, 4), G_star=c['G_star'], cv3_over_hc3=round(full['se_cv3'] / full['se_hc3'], 3),
                     y_mean=round(full['y_mean'], 4), y_var=round(full['y_var'], 4), mde80=round(full['mde80'], 4),
                     coef_noTM=round(noTM['coef'], 4), se_cv3_noTM=round(noTM['se_cv3'], 4), G_noTM=noTM['G'],
                     n_noTM=noTM['n'], mde80_noTM=round(noTM['mde80'], 4),
                     share_TM=round(float(jk.loc[jk['final_cik'] == TM, 'share'].iloc[0]), 4),
                     treated_events=ev[1][0], treated_n=ev[1][1], control_events=ev[0][0], control_n=ev[0][1]))
    r = rows[-1]
    log(f"\n{w}d: coef {r['coef']:+.4f} | SE: HC3 {r['se_hc3']:.4f}, CV1 {r['se_cv1']:.4f}, CV3 {r['se_cv3']:.4f}, "
        f"WCR (no SE; CI [{r['wcr_ci_lo']:+.4f}, {r['wcr_ci_hi']:+.4f}], implied SE {r['wcr_implied_se']:.4f}) | G* {r['G_star']}")
    log(f"     outcome mean {r['y_mean']:.4f}, variance {r['y_var']:.4f} | CV3/HC3 {r['cv3_over_hc3']:.3f} | MDE80 {r['mde80']:.4f}")
    log(f"     T-Mobile deleted (N {r['n_noTM']}, G {r['G_noTM']}): coef {r['coef_noTM']:+.4f}, CV3 SE {r['se_cv3_noTM']:.4f}, "
        f"MDE80 {r['mde80_noTM']:.4f} | T-Mobile's share of the CV3 jackknife variance {r['share_TM']:.4f}")
    log(f"     base rates (notification anchor): treated {r['treated_events']}/{r['treated_n']} = "
        f"{r['treated_events'] / r['treated_n']:.4f}; control {r['control_events']}/{r['control_n']} = "
        f"{r['control_events'] / r['control_n']:.4f}")
    log(f"     {w}d leave-one-cluster-out range [{jk['coef_without'].min():+.4f}, "
        f"{jk['coef_without'].max():+.4f}] (full {full['coef']:+.4f}); sign flips "
        f"{len(flips)}/{len(jk)}: " + '; '.join(
            f"{int(t.final_cik)} {t['name']} ({'treated' if t.treated_cluster else 'control'}, "
            f"{int(t.n_events)} events, b_-g {t.coef_without:+.4f})" for _, t in flips.iterrows()))
    log(f"     {w}d top five contributors to the CV3 jackknife variance: " + '; '.join(
        f"{int(t.final_cik)} {t['name'] if isinstance(t['name'], str) else ''} "
        f"({'treated' if t.treated_cluster else 'control'}, {int(t.n_events)} events, "
        f"b_-g {t.coef_without:+.4f}, share {t.share:.3f})" for _, t in top.iterrows()))
pd.DataFrame(rows).to_csv(OUT / 'f1_se_diagnostics.csv', index=False)
pd.concat(shares)[['window', 'final_cik', 'name', 'treated_cluster', 'n_events', 'coef_without', 'share', 'sign_flip']].round(4).to_csv(
    OUT / 'f1_cv3_variance_shares.csv', index=False)
log('\nRecomputed HC3/CV1/CV3 SEs and coefficients equal committed f1_ladder.csv at all three windows: PASS')
(OUT / '229_se_diagnostics.log').write_text('\n'.join(L) + '\n', encoding='utf-8')
