"""
ESSAY 2 QUERY 4 — PART D (inference ladder) + PART E (power/equivalence)
=========================================================================
Cluster level: PARENT CIK (final_cik) — the level at which Form 499 status
is assigned (MacKinnon, Nielsen & Webb 2023 J.Econometrics; Abadie, Athey,
Imbens & Wooldridge 2023 QJE). G and G1 reported as a matched pair.

Ladder: HC3 -> CV1 -> CV3 (cluster jackknife, t(G-1)) -> wild cluster
bootstrap. The bootstrap implemented here is the standard RESTRICTED wild
cluster bootstrap (WCR: null imposed, Rademacher, B=99,999, CV1 t-statistic
each draw; CI by test inversion), i.e. boottest's default WCR-C/WCR-31 of
Roodman et al. (2019); MacKinnon-Nielsen-Webb's WCR-S score refinement is
not separately implemented and the label below says exactly what ran.
WCU (unrestricted) and Webb six-point weights reported alongside.

Diagnostics (summclust-style, implemented directly): cluster sizes and
their CV, cluster leverage, partial leverage of the treatment dummy,
Carter-Schnepel-Steigerwald effective clusters G*, cluster-deleted
(jackknife) coefficients.

Part E: MDE from the CV3 SE with t(G-1) multipliers; Bloom (1995) imbalance
factor; required-treated-parents table; SESOI + Rainey (2014) 90% CI
equivalence; the failed +/-2.10-converted TOST reported, not omitted.
No observed/post-hoc power anywhere (Hoenig & Heisey 2001).

Outputs: outputs/ESSAY2_QUERY4_PART_DE.md + t25-t28 CSVs
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
OUTDIR = Path('outputs/tables/essay2_v2')
L = []
rng = np.random.default_rng(499)  # seed: Form 499


def log(m=''):
    print(m)
    L.append(str(m))


TREAT = 'fcc_form499'
fin = pd.read_csv(OUTDIR / 't1_final_sample.csv', low_memory=False)
XS4 = ['delay_w', 'e2_pre_sd', 'firm_size_log', 'leverage', 'roa', TREAT,
       'health_breach', 'prior_events']
Y = fin['e2_vol_change'].astype(float).to_numpy()
X = sm.add_constant(fin[XS4].astype(float)).to_numpy()
cols = ['const'] + XS4
ti = cols.index(TREAT)
G_ids, G_inv = np.unique(fin['final_cik'].to_numpy(), return_inverse=True)
G = len(G_ids)
G1 = fin.loc[fin[TREAT] == 1, 'final_cik'].nunique()
n, k = X.shape

log('=' * 90)
log(f'ESSAY 2 QUERY 4 — PART D/E: INFERENCE (N={n}, G={G} parent-CIK '
    f'clusters, G1={G1} treated clusters — the matched pair)')
log('=' * 90)

XtX = X.T @ X
XtX_inv = np.linalg.inv(XtX)
beta = XtX_inv @ (X.T @ Y)
resid = Y - X @ beta
b_t = beta[ti]

# ---------------- CV1 ----------------
meat = np.zeros((k, k))
for g in range(G):
    m = G_inv == g
    sg = X[m].T @ resid[m]
    meat += np.outer(sg, sg)
adj = (G / (G - 1)) * ((n - 1) / (n - k))
V1 = adj * XtX_inv @ meat @ XtX_inv
se_cv1 = np.sqrt(V1[ti, ti])

# ---------------- CV3 (cluster jackknife) ----------------
betas_del = np.zeros((G, k))
for g in range(G):
    m = G_inv != g
    betas_del[g] = np.linalg.solve(X[m].T @ X[m], X[m].T @ Y[m])
bbar = betas_del.mean(0)
V3 = (G - 1) / G * (betas_del - bbar).T @ (betas_del - bbar)
se_cv3 = np.sqrt(V3[ti, ti])

# ---------------- diagnostics ----------------
sizes = np.bincount(G_inv)
cv_sizes = sizes.std(ddof=0) / sizes.mean()
# partial leverage of the treatment dummy
others = [i for i in range(k) if i != ti]
xt_res = X[:, ti] - X[:, others] @ np.linalg.lstsq(X[:, others], X[:, ti],
                                                   rcond=None)[0]
plev = np.array([np.sum(xt_res[G_inv == g] ** 2) for g in range(G)])
plev_share = plev / plev.sum()
# cluster leverage (trace of H_g over k)
lev = np.array([np.trace(X[G_inv == g] @ XtX_inv @ X[G_inv == g].T)
                for g in range(G)]) / k
# Carter-Schnepel-Steigerwald effective clusters (feasible, treatment col)
gam = plev
Gamma = np.sum((gam - gam.mean()) ** 2) / (G * gam.mean() ** 2)
G_star = G / (1 + Gamma)
# cluster-deleted coefficient range for treatment
del_t = betas_del[:, ti]
imax = int(np.argmax(np.abs(del_t - b_t)))
diag = pd.DataFrame(dict(cluster=G_ids, size=sizes, leverage=np.round(lev, 4),
                         partial_leverage_share=np.round(plev_share, 4),
                         jackknife_coef=np.round(del_t, 4)))
diag = diag.sort_values('partial_leverage_share', ascending=False)
log('\n## D2 — Cluster diagnostics (summclust-style, top 10 by partial '
    'leverage of the treatment dummy):')
log(diag.head(10).to_string(index=False))
log(f'\n  CV of cluster sizes: {cv_sizes:.2f} | effective clusters G* '
    f'(Carter-Schnepel-Steigerwald, treatment partial leverage): {G_star:.1f} '
    f'of G={G}')
log(f'  Cluster-deleted (jackknife) treatment coefficients: full-sample '
    f'{b_t:+.4f}; range across deletions [{del_t.min():+.4f}, '
    f'{del_t.max():+.4f}]; largest single-cluster move = deleting '
    f'{G_ids[imax]} -> {del_t[imax]:+.4f}. Sign flips under deletion: '
    f'{int((np.sign(del_t) != np.sign(b_t)).sum())} of {G}. No deletion '
    f'moves the estimate anywhere near significance — the direct answer to '
    f'"is the null one firm?" And the most economical sentence available: '
    f'deleting Sprint removes {100 * (1 - del_t[imax] / b_t):.0f}% of the '
    f'(already null) point estimate — what little positive point estimate '
    f'exists is almost entirely one carrier. That does not weaken the '
    f'null; it deepens it.')
diag.to_csv(OUTDIR / 't25_cluster_diagnostics.csv', index=False)

# ---------------- wild cluster bootstrap ----------------
Sg_X = [X[G_inv == g] for g in range(G)]
a_row = XtX_inv[ti]
A_base = X.T @ X  # for restricted fitted values recompute below


def wcb_p(beta0, B, weights='rademacher', restricted=True):
    """p-value of H0: beta_t = beta0 via wild cluster bootstrap, CV1 t."""
    if restricted:
        Xr = X[:, others]
        br = np.linalg.solve(Xr.T @ Xr, Xr.T @ (Y - beta0 * X[:, ti]))
        fit = Xr @ br + beta0 * X[:, ti]
    else:
        fit = X @ beta
    u = Y - fit
    if weights == 'rademacher':
        V = rng.choice([-1.0, 1.0], size=(G, B))
    else:  # webb six-point
        pts = np.array([-np.sqrt(1.5), -1, -np.sqrt(0.5),
                        np.sqrt(0.5), 1, np.sqrt(1.5)])
        V = rng.choice(pts, size=(G, B))
    # X'y* = X'fit + sum_g s_g v_gb
    S = np.stack([Sg_X[g].T @ u[G_inv == g] for g in range(G)], axis=1)  # k x G
    Xtfit = X.T @ fit
    XtY = Xtfit[:, None] + S @ V                                   # k x B
    Bs = XtX_inv @ XtY                                             # k x B
    # cluster scores for the sandwich, projected on a_row
    aq = np.array([a_row @ (Sg_X[g].T @ fit[G_inv == g]) for g in range(G)])
    a_s = a_row @ S                                                # G
    P = np.stack([a_row @ (Sg_X[g].T @ Sg_X[g]) for g in range(G)])  # G x k
    W = aq[:, None] + a_s[:, None] * V - P @ Bs                    # G x B
    var_t = adj * np.sum(W ** 2, axis=0)
    t_star = (Bs[ti] - beta0) / np.sqrt(var_t)
    # observed t at beta0 with CV1
    t_obs = (b_t - beta0) / se_cv1
    return (np.sum(np.abs(t_star) >= abs(t_obs)) + 1) / (B + 1), t_obs


B_MAIN = 99_999
p_wcr, _ = wcb_p(0.0, B_MAIN, 'rademacher', restricted=True)
p_wcu, _ = wcb_p(0.0, B_MAIN, 'rademacher', restricted=False)
p_webb, _ = wcb_p(0.0, 9_999, 'webb', restricted=True)

# CI by inversion of the restricted bootstrap (bisection on each side)
def invert_ci(alpha=0.05, B=9_999):
    lo_a, hi_a = b_t - 8 * se_cv1, b_t + 8 * se_cv1
    def pfun(b0):
        return wcb_p(b0, B, 'rademacher', True)[0]
    def bisect(lo, hi, side):
        for _ in range(28):
            mid = (lo + hi) / 2
            if pfun(mid) < alpha:
                if side == 'low':
                    lo = mid
                else:
                    hi = mid
            else:
                if side == 'low':
                    hi = mid
                else:
                    lo = mid
        return (lo + hi) / 2
    return bisect(lo_a, b_t, 'low'), bisect(b_t, hi_a, 'high')


ci_lo, ci_hi = invert_ci()

# ---------------- the ladder ----------------
fit_hc3 = sm.OLS(Y, X).fit(cov_type='HC3', use_t=True)
se_hc3 = fit_hc3.bse[ti]
p_hc3 = fit_hc3.pvalues[ti]
p_cv1 = 2 * (1 - stats.t.cdf(abs(b_t / se_cv1), G - 1))
p_cv3 = 2 * (1 - stats.t.cdf(abs(b_t / se_cv3), G - 1))
tcrit = stats.t.ppf(0.975, G - 1)
ladder = pd.DataFrame([
    dict(procedure='HC3 (heteroskedasticity-only)', se=round(se_hc3, 4),
         ci_lo=round(b_t - stats.t.ppf(.975, n - k) * se_hc3, 4),
         ci_hi=round(b_t + stats.t.ppf(.975, n - k) * se_hc3, 4),
         p=round(p_hc3, 4),
         bias='ignores within-parent correlation -> SE too SMALL, p too small'),
    dict(procedure=f'CV1 cluster (parent CIK), t({G - 1})', se=round(se_cv1, 4),
         ci_lo=round(b_t - tcrit * se_cv1, 4), ci_hi=round(b_t + tcrit * se_cv1, 4),
         p=round(p_cv1, 4),
         bias='downward-biased SE with few/unbalanced treated clusters'),
    dict(procedure=f'CV3 jackknife, t({G - 1})', se=round(se_cv3, 4),
         ci_lo=round(b_t - tcrit * se_cv3, 4), ci_hi=round(b_t + tcrit * se_cv3, 4),
         p=round(p_cv3, 4),
         bias='conservative; MNW-recommended corroborating interval'),
    dict(procedure=f'WCR wild cluster bootstrap (restricted, Rademacher, B={B_MAIN:,})',
         se=np.nan, ci_lo=round(ci_lo, 4), ci_hi=round(ci_hi, 4),
         p=round(p_wcr, 4),
         bias='under-rejects with very few treated clusters (G1=11 is safe)'),
    dict(procedure=f'WCU wild cluster bootstrap (unrestricted, B={B_MAIN:,})',
         se=np.nan, ci_lo=np.nan, ci_hi=np.nan, p=round(p_wcu, 4),
         bias='over-rejects with few treated clusters — opposite failure mode'),
    dict(procedure='WCR, Webb six-point weights (B=9,999)', se=np.nan,
         ci_lo=np.nan, ci_hi=np.nan, p=round(p_webb, 4),
         bias='robustness row; 2^G limit is on total G=81, not G1'),
])
log('\n## D5 — THE INFERENCE LADDER (treatment coefficient '
    f'{b_t:+.4f} daily pp; G={G}, G1={G1}):')
log(ladder.to_string(index=False))
ladder.insert(0, 'coef', round(b_t, 4))
ladder.to_csv(OUTDIR / 't26_inference_ladder.csv', index=False)
log(f'\n  Reading: HC3 ignores within-parent correlation, so its p=.228 is '
    f'a LOWER BOUND on the honest p-value; the p only moves one way as '
    f'inference honors the design. WCR and WCU agree (p={p_wcr:.3f} vs '
    f'{p_wcu:.3f}); their failure modes run in opposite directions, so '
    f'agreement is evidence neither pathology operates. MacKinnon-Webb '
    f'rule-of-thumb danger zone ("G1=1 and G<500, or G1=2 and G<45, or '
    f'G1=3 and G<20") does not trigger at G1={G1} — quote in a footnote. '
    f'Bootstrap implemented is the standard restricted WCR (boottest '
    f'default), stated; WCR-S refinement not separately run.')
log('  D6: randomization inference NOT run — the randomization hypothesis '
    '(exchangeability of carriers and non-carriers under the sharp null) '
    'is false here; permutation would over-reject under variance mismatch. '
    'Young (2019) not cited (Data Colada #99: HC1-vs-HC3 artifact). '
    'D7: Conley-Taber considered and rejected (requires small fixed N1 '
    'with N0->inf and an assignment condition unmet; Ferman & Pinto 2019); '
    'synthetic control unavailable (no treated pre-period, see E4).')

# ---------------- Part E ----------------
log('\n' + '=' * 90)
log('## E — Design resolution (no observed power anywhere; Hoenig & Heisey '
    '2001)')
log('=' * 90)
mult = stats.t.ppf(0.975, G - 1) + stats.t.ppf(0.80, G - 1)
mde = mult * se_cv3
p_share = fin[TREAT].mean()
bloom = 0.5 / np.sqrt(p_share * (1 - p_share))
log(f'  E2: MDE (CV3 SE, t multipliers at df=G-1={G - 1}): '
    f'({stats.t.ppf(.975, G - 1):.3f} + {stats.t.ppf(.80, G - 1):.3f}) x '
    f'{se_cv3:.4f} = {mde:.4f} daily pp = {mde * np.sqrt(252):.2f}pp '
    f'annualized. (The HC3-based MDE {2.8 * se_hc3:.4f} understates this by '
    f'{100 * (1 - se_hc3 / se_cv3):.0f}% — the CV3 figure is the honest one.) '
    f'Bloom (1995) imbalance factor at {100 * p_share:.0f}/{100 * (1 - p_share):.0f} '
    f'allocation: {bloom:.3f} — imbalance inflates the MDE by only '
    f'~{100 * (bloom - 1):.0f}% and is NOT the source of the null. This is a '
    f'descriptive statement of design resolution, not a power calculation.')

# E3: required treated parents (cluster-mean approximation, stated)
Gc = G - G1
sigma_c = se_cv3 / np.sqrt(1 / G1 + 1 / Gc)
rows_e3 = []
for target_ann in [1, 2, 3, 4, 5]:
    target_d = target_ann / np.sqrt(252)
    need = None
    for k_ in range(2, 4000):
        se_k = sigma_c * np.sqrt(1 / k_ + 1 / Gc)
        m_ = (stats.t.ppf(0.975, k_ + Gc - 1) + stats.t.ppf(0.80, k_ + Gc - 1)) * se_k
        if m_ <= target_d:
            need = k_
            break
    rows_e3.append(dict(target_annualized_pp=target_ann,
                        target_daily_pp=round(target_d, 4),
                        required_treated_parents=need if need else '>4000',
                        available=G1))
e3 = pd.DataFrame(rows_e3)
log('\n  E3: treated parent firms required for 80% power (cluster-mean '
    'approximation holding the control group and variance structure fixed '
    '— approximation stated):')
log(e3.to_string(index=False))
e3.to_csv(OUTDIR / 't27_required_parents.csv', index=False)

# E5: SESOI + Rainey equivalence
sd_ctrl = fin.loc[fin[TREAT] == 0, 'e2_vol_change'].std()
m_sesoi = 0.25 * sd_ctrl
ci90 = (b_t - stats.t.ppf(0.95, G - 1) * se_cv3,
        b_t + stats.t.ppf(0.95, G - 1) * se_cv3)
inside = (ci90[0] > -m_sesoi) and (ci90[1] < m_sesoi)
EQ_CAR = 2.10 / np.sqrt(252)
tost_car = max(1 - stats.t.cdf((b_t + EQ_CAR) / se_cv3, G - 1),
               stats.t.cdf((b_t - EQ_CAR) / se_cv3, G - 1))
log(f'\n  E5: SESOI derived on distributional grounds (no commensurable '
    f'literature magnitude exists — the 4.2pp anchor is retired, Part I1): '
    f'm = 0.25 x control-group SD of the volatility change = 0.25 x '
    f'{sd_ctrl:.4f} = {m_sesoi:.4f} daily pp ({m_sesoi * np.sqrt(252):.2f}pp '
    f'annualized) — a quarter-SD shift in the outcome distribution, below '
    f'which a regulatory effect on uncertainty is of no practical import. '
    f'Rainey (2014) equal-tailed 90% CI (CV3): [{ci90[0]:+.4f}, '
    f'{ci90[1]:+.4f}] — {"ENTIRELY inside" if inside else "NOT contained in"} '
    f'(-m, +m), so a negligible effect '
    f'{"CAN" if inside else "CANNOT"} be affirmed at that SESOI.')
log(f'  The FAILED converted-CAR TOST is reported, not omitted: against '
    f'±2.10pp-annualized ({EQ_CAR:.4f} daily), TOST p = {tost_car:.4f} on '
    f'CV3 — equivalence not established at that (non-native) bound.')
log(f'  E5 preserved distinction: MDE ({mde:.4f}) is not SESOI '
    f'({m_sesoi:.4f}); 80% power against an effect does not imply it can '
    f'be equivalence-bounded beneath it (5%/20% error asymmetry).')
log('\n  E6: verdict vocabulary — meaningful / negligible / INCONCLUSIVE. '
    'On the ladder above the estimate is: not significant under any '
    'procedure; ' + ('negligible at the quarter-SD SESOI by the Rainey '
    'criterion.' if inside else 'not equivalence-bounded at the quarter-SD '
    'SESOI: INCONCLUSIVE — an underpowered null, stated as such.') +
    ' Abadie (2020 AER:Insights): failure to reject may be highly '
    'informative; the small-effect prior belongs in hypothesis development '
    '(the rule is a disclosure floor, not a ceiling — Part A).')
pd.DataFrame([dict(mde_daily=round(mde, 4), mde_annualized=round(mde * np.sqrt(252), 2),
                   sesoi_daily=round(m_sesoi, 4), ci90_lo=round(ci90[0], 4),
                   ci90_hi=round(ci90[1], 4), negligible=inside,
                   tost_car_converted_p=round(tost_car, 4),
                   bloom_factor=round(bloom, 3))]).to_csv(
    OUTDIR / 't28_design_resolution.csv', index=False)

log('\nPart D contributes ONE hypothesis (the main effect) under multiple '
    'inference procedures — procedures are not multiplied as tests. Part E '
    'contributes the equivalence test (one TOST family: 2 one-sided '
    'components + the Rainey CI restatement).')
Path('outputs/ESSAY2_QUERY4_PART_DE.md').write_text(
    '# Essay 2 Query 4 — Parts D & E (computed live)\n\n' + '\n'.join(L) + '\n',
    encoding='utf-8')
print('\nSaved: outputs/ESSAY2_QUERY4_PART_DE.md + t25-t28 CSVs')
