"""
DEFENSE SUPPLEMENT — ESSAY 3 v4: PARENT-CIK RANDOMIZATION INFERENCE (script 250)
================================================================================
Reads (committed, frozen): outputs/essay3_v4/e_analysis_sample.csv (in_analysis_sample == 1),
                           outputs/essay3_v4/f1_ladder.csv, outputs/essay3_v4/f4_placebo.csv,
                           scripts/227_essay3_v4_estimation.py (source only; ladder() is extracted with ast and
                           exec'd, 227 itself is never imported or run).
Writes ONLY: outputs/defense_supplement/e3_randomization_inference.csv
             outputs/defense_supplement/e3_randomization_inference.log

Specification (identical to 227 F1/F4): LPM  y ~ const + fcc_form499 + prior_breaches_1yr + health_breach
  + firm_size_log + leverage + roa + baseline_exec_rate_py_rd + prior12m_mktadj_ret_rd, y in
  exec_departure_{30,90,180}_rd and placebo_exec_departure_rd. Clusters: final_cik (parent CIK).
  CV3 = 227's cluster jackknife: delete-one-cluster betas, centred on their mean, (G-1)/G scaling.

Sample asserted before estimation: N = 405 events, 109 treated events, G = 119 parent CIKs, G1 = 13 treated
parent CIKs.

C1  Randomization inference at the parent-CIK level. Each draw picks 13 of the 119 parent CIKs uniformly without
    replacement and sets fcc_form499 = 1 for ALL events of those parents, 0 otherwise. Same controls, same sample.
    B = 9,999 draws. SEED = 250 (numpy default_rng(250)); one set of draws per variant, shared by all four outcomes.
    Per draw: OLS coefficient and the CV3 jackknife t, computed exactly by assembling X'X / X'y from per-cluster
    blocks (treatment is constant within a cluster under every draw) and solving the 119 leave-one-cluster-out
    systems in batch. A spot check compares the fast path against direct lstsq refits for several draws.
C2  RI p = (#{|stat*| >= |stat_obs|} + 1) / (B + 1) for the coefficient and for the CV3 t; treated-event
    distribution across draws vs the observed 109.
C3  Variant: draws restricted to parent CIKs whose event count lies within [min, max] of the observed treated
    parents' event counts; 13 drawn from that eligible set.

NOTE: in the observed data 3 treated parent CIKs also carry untreated events (treatment is event-level), so the
observed 13 parents hold 115 events of which 109 are treated. The RI draws treat whole parents, as specified; the
observed assignment is therefore not exactly a point of the draw support. This is reported in the log.
"""

import ast
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
T0 = time.time()
SEED = 250
B = 9_999
OUT = Path('outputs/defense_supplement')
SRC = Path('outputs/essay3_v4')
L = []


def log(m=''):
    print(m, flush=True)
    L.append(str(m))


# ---------------------------------------------------------------- extract 227's ladder() without running 227
src227 = Path('scripts/227_essay3_v4_estimation.py').read_text(encoding='utf-8')
tree = ast.parse(src227)
fn = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'ladder']
assert len(fn) == 1, 'ladder() not found in scripts/227'
NS = dict(np=np, pd=pd, sm=sm, stats=stats, TREAT='fcc_form499', rng=np.random.default_rng(3))
exec(compile(ast.Module(body=fn, type_ignores=[]), 'scripts/227::ladder', 'exec'), NS)
ladder227 = NS['ladder']

TREAT = 'fcc_form499'
BASE = ['prior_breaches_1yr', 'health_breach', 'firm_size_log', 'leverage', 'roa']
CTRL = BASE + ['baseline_exec_rate_py_rd', 'prior12m_mktadj_ret_rd']
OUTCOMES = [('exec_departure_30_rd', '30'), ('exec_departure_90_rd', '90'), ('exec_departure_180_rd', '180'),
            ('placebo_exec_departure_rd', 'placebo (t0-180d, t0]')]
YS = [o[0] for o in OUTCOMES]

d0 = pd.read_csv(SRC / 'e_analysis_sample.csv', low_memory=False)
d0 = d0[d0['in_analysis_sample'] == 1].reset_index(drop=True)
d = d0.dropna(subset=YS + [TREAT] + CTRL).reset_index(drop=True)
N = len(d)
n_treat = int(d[TREAT].sum())
G_ids, G_inv = np.unique(d['final_cik'].to_numpy(), return_inverse=True)
G = len(G_ids)
G1 = d.loc[d[TREAT] == 1, 'final_cik'].nunique()
log('=' * 100)
log('SCRIPT 250 — Essay 3 v4 parent-CIK randomization inference (defense supplement)')
log(f'Seed {SEED} (numpy default_rng); B = {B:,} draws per variant')
log('=' * 100)
log(f'Sample (event level, Essay 3 v4 analysis sample): N = {N} events; treated = {n_treat} events; '
    f'G = {G} parent CIKs; G1 = {G1} treated parent CIKs')
assert len(d0) == 405 and N == 405, f'N {len(d0)}/{N} != 405'
assert n_treat == 109, f'treated events {n_treat} != 109'
assert G == 119, f'G {G} != 119'
assert G1 == 13, f'G1 {G1} != 13'
log('Sample assert (N=405, treated events 109, G=119, G1=13): PASS')

sizes = np.bincount(G_inv)
par = d.groupby('final_cik')[TREAT].agg(['size', 'sum'])
tpar = par[par['sum'] > 0]
mixed = tpar[tpar['sum'] < tpar['size']]
log(f'Observed treated parents: {len(tpar)} parent CIKs holding {int(tpar["size"].sum())} events, of which '
    f'{int(tpar["sum"].sum())} treated. Mixed parents (treated + untreated events): '
    + '; '.join(f'{c}: {int(r["sum"])}/{int(r["size"])}' for c, r in mixed.iterrows()))
log(f'Observed treated-parent event counts (sorted): {sorted(tpar["size"].astype(int).tolist())}')
log(f'All-parent event counts: min {sizes.min()}, median {np.median(sizes):.0f}, mean {sizes.mean():.2f}, '
    f'max {sizes.max()}; parents with 1 event: {(sizes == 1).sum()}')

# ---------------------------------------------------------------- design
Z = sm.add_constant(d[CTRL].astype(float), has_constant='add').to_numpy()   # (n, m)
Y = d[YS].astype(float).to_numpy()                                           # (n, 4)
tobs = d[TREAT].astype(float).to_numpy()
m = Z.shape[1]
k = m + 1                                                                     # treatment first


def direct_fit(t):
    """Exact 227 formula (lstsq refits) for event-level treatment vector t: coef, CV3 SE, per outcome."""
    X = np.column_stack([t, Z])
    beta = np.linalg.pinv(X.T @ X) @ (X.T @ Y)
    bd = np.zeros((G, Y.shape[1]))
    for g in range(G):
        msk = G_inv != g
        bd[g] = np.linalg.lstsq(X[msk], Y[msk], rcond=None)[0][0]
    se = np.sqrt((G - 1) / G * ((bd - bd.mean(0)) ** 2).sum(0))
    return beta[0], se


# ---------------------------------------------------------------- observed + reproduction assert
log('\nREPRODUCTION ASSERT (observed assignment) vs committed f1_ladder.csv / f4_placebo.csv')
F1 = pd.read_csv(SRC / 'f1_ladder.csv').set_index('y')
F4 = pd.read_csv(SRC / 'f4_placebo.csv').set_index('y')
b_obs, se_obs = direct_fit(tobs)
t_obs = b_obs / se_obs
ok = True
for j, (y, w) in enumerate(OUTCOMES):
    ref = F1.loc[y] if y in F1.index else F4.loc[y]
    p3 = 2 * (1 - stats.t.cdf(abs(t_obs[j]), G - 1))
    r227 = ladder227(d0, y, [TREAT] + CTRL, B=99, full=False)   # 227's own function (WCR B tiny; unused here)
    checks = [(round(b_obs[j], 4), ref['coef']), (round(se_obs[j], 4), ref['se_cv3']), (round(p3, 4), ref['p_cv3']),
              (r227['coef'], ref['coef']), (r227['se_cv3'], ref['se_cv3']), (r227['p_cv3'], ref['p_cv3']),
              (int(ref['n']), N), (int(ref['G']), G), (int(ref['G1']), G1)]
    good = all(abs(a - b) < 1e-9 for a, b in checks)
    ok &= good
    log(f'  [{y}] event level, primary rung (LPM, CV3), N={N}: coef {b_obs[j]:+.6f} (committed {ref["coef"]:+.4f}) | '
        f'CV3 SE {se_obs[j]:.6f} (committed {ref["se_cv3"]:.4f}) | CV3 p {p3:.4f} (committed {ref["p_cv3"]:.4f}) | '
        f'227 ladder(): coef {r227["coef"]:+.4f} SE {r227["se_cv3"]:.4f} p {r227["p_cv3"]:.4f} -> {"PASS" if good else "FAIL"}')
assert ok, 'REPRODUCTION ASSERT FAILED — stopping'
log('Reproduction assert: PASS (own implementation AND 227 ladder() both match committed CSVs to 4 dp)')

# ---------------------------------------------------------------- per-cluster blocks for the fast path
A_g = np.zeros((G, m, m)); s_g = np.zeros((G, m)); c_g = np.zeros((G, m, 4)); e_g = np.zeros((G, 4))
for g in range(G):
    Zg, Yg = Z[G_inv == g], Y[G_inv == g]
    A_g[g] = Zg.T @ Zg; s_g[g] = Zg.sum(0); c_g[g] = Zg.T @ Yg; e_g[g] = Yg.sum(0)
A_tot, s_tot, c_tot, e_tot = A_g.sum(0), s_g.sum(0), c_g.sum(0), e_g.sum(0)
nG = sizes.astype(float)


def fast_stats(T):
    """T: (b, G) 0/1 cluster-level assignment. Returns coef (b,4), CV3 SE (b,4)."""
    b = T.shape[0]
    # full system
    M = np.zeros((b, k, k)); r = np.zeros((b, k, 4))
    M[:, 0, 0] = T @ nG
    M[:, 0, 1:] = T @ s_g; M[:, 1:, 0] = M[:, 0, 1:]
    M[:, 1:, 1:] = A_tot
    r[:, 0, :] = T @ e_g; r[:, 1:, :] = c_tot
    beta = np.linalg.solve(M, r)[:, 0, :]
    # leave-one-cluster-out: subtract cluster g's block
    Md = np.broadcast_to(M[:, None], (b, G, k, k)).copy()
    Md[:, :, 0, 0] -= T * nG
    Md[:, :, 0, 1:] -= T[:, :, None] * s_g[None]
    Md[:, :, 1:, 0] = Md[:, :, 0, 1:]
    Md[:, :, 1:, 1:] -= A_g[None]
    rd = np.broadcast_to(r[:, None], (b, G, k, 4)).copy()
    rd[:, :, 0, :] -= T[:, :, None] * e_g[None]
    rd[:, :, 1:, :] -= c_g[None]
    bd = np.linalg.solve(Md, rd)[:, :, 0, :]                     # (b, G, 4)
    se = np.sqrt((G - 1) / G * ((bd - bd.mean(1, keepdims=True)) ** 2).sum(1))
    return beta, se


# rank sanity: every leave-one-cluster-out control block is well conditioned
cond = max(np.linalg.cond(A_tot - A_g[g]) for g in range(G))
log(f'\nMax condition number of leave-one-cluster-out control blocks: {cond:.3g}')


def draw_sets(rng, pool, B_):
    return np.stack([rng.choice(pool, size=G1, replace=False) for _ in range(B_)])


def to_T(idx):
    T = np.zeros((idx.shape[0], G))
    np.put_along_axis(T, idx, 1.0, axis=1)
    return T


def run_variant(name, pool):
    rng = np.random.default_rng(SEED)
    t1 = time.time()
    idx = draw_sets(rng, pool, B)
    T = to_T(idx)
    # spot check fast path vs direct lstsq refits
    for i in range(3):
        tev = T[i][G_inv]
        bb, ss = direct_fit(tev)
        fb, fs = fast_stats(T[i:i + 1])
        assert np.allclose(bb, fb[0], atol=1e-9) and np.allclose(ss, fs[0], atol=1e-9), 'fast path mismatch'
    Bc, Sc = [], []
    for lo in range(0, B, 500):
        bb, ss = fast_stats(T[lo:lo + 500])
        Bc.append(bb); Sc.append(ss)
    Bs, Ss = np.vstack(Bc), np.vstack(Sc)
    Ts = Bs / Ss
    tev = T @ sizes
    log(f'\n--- Variant: {name} | eligible parents {len(pool)} of {G} | draws {B:,} | seed {SEED} | '
        f'fast path spot check (3 draws vs lstsq): PASS | {time.time() - t1:.1f}s')
    q = np.percentile(tev, [0, 5, 25, 50, 75, 95, 100])
    log(f'    Treated events per draw (event level; 13 parent CIKs per draw): min {q[0]:.0f}, p5 {q[1]:.0f}, '
        f'p25 {q[2]:.0f}, median {q[3]:.0f}, p75 {q[4]:.0f}, p95 {q[5]:.0f}, max {q[6]:.0f}, mean {tev.mean():.2f} '
        f'| observed 109 treated events (13 parent CIKs; 115 events in those parents); share of draws >= 109: '
        f'{(tev >= 109).mean():.4f}')
    rows = []
    for j, (y, w) in enumerate(OUTCOMES):
        tol = 1e-12
        p_b = (np.sum(np.abs(Bs[:, j]) >= abs(b_obs[j]) - tol) + 1) / (B + 1)
        p_t = (np.sum(np.abs(Ts[:, j]) >= abs(t_obs[j]) - tol) + 1) / (B + 1)
        log(f'    [{y}] event level, RI rung ({name}), N={N}, G={G}, G1={G1} treated parent CIKs (observed '
            f'{n_treat} treated events): coef_obs {b_obs[j]:+.4f}, CV3 SE {se_obs[j]:.4f}, CV3 t {t_obs[j]:+.3f} | '
            f'RI p(coef) {p_b:.4f} | RI p(CV3 t) {p_t:.4f} | draw coef sd {Bs[:, j].std():.4f}')
        rows.append(dict(outcome=y, window=w, variant=name, N=N, G=G, G1=G1, n_eligible_parents=len(pool), B=B,
                         seed=SEED, coef_obs=round(b_obs[j], 6), cv3_se_obs=round(se_obs[j], 6),
                         cv3_t_obs=round(t_obs[j], 4), ri_p_coef=round(p_b, 4), ri_p_t=round(p_t, 4),
                         treated_events_obs=n_treat, treated_events_obs_parents_total=int(tpar['size'].sum()),
                         te_min=int(q[0]), te_p5=q[1], te_p25=q[2], te_median=q[3], te_p75=q[4], te_p95=q[5],
                         te_max=int(q[6]), te_mean=round(tev.mean(), 3), share_draws_te_ge_obs=round((tev >= 109).mean(), 4),
                         draw_coef_sd=round(Bs[:, j].std(), 6)))
    return rows


rows = run_variant('C1 all parents', np.arange(G))
lo_, hi_ = int(tpar['size'].min()), int(tpar['size'].max())
elig = np.where((sizes >= lo_) & (sizes <= hi_))[0]
log(f'\nC3 eligibility: parent event count in [{lo_}, {hi_}] (observed treated parents\' range) -> {len(elig)} of {G} '
    f'parent CIKs eligible ({int(sizes[elig].sum())} events); excluded: {(sizes < lo_).sum()} parents below, '
    f'{(sizes > hi_).sum()} above (sizes above: {sorted(sizes[sizes > hi_].tolist())})')
rows += run_variant('C3 size-matched parents', elig)

R = pd.DataFrame(rows)
R.to_csv(OUT / 'e3_randomization_inference.csv', index=False)
log('\n' + R[['outcome', 'variant', 'n_eligible_parents', 'coef_obs', 'cv3_t_obs', 'ri_p_coef', 'ri_p_t',
              'te_median', 'te_mean']].to_string(index=False))
log(f'\nRuntime {time.time() - T0:.1f}s. Wrote {OUT / "e3_randomization_inference.csv"}')
(OUT / 'e3_randomization_inference.log').write_text('\n'.join(L) + '\n', encoding='utf-8')
