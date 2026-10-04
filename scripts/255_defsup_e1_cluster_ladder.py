"""
DEFENSE SUPPLEMENT - Essay 1: cluster-robust rungs for the four hypothesis coefficients
======================================================================================
Essay 1 reports its baseline regression (30-day CAR on H1-H4 and three controls) with HC3
standard errors, and parent-CIK clustered p-values alongside (appendix tables 4 and 8).
This supplement adds the rungs Essays 2 and 3 use, for the SAME specification and sample:
CV1, the CV3 cluster jackknife (t with G-1 df) and the restricted wild cluster bootstrap
(Rademacher, null imposed, B = 99,999), plus CV3 95% and 90% CIs, the CV3 MDE80, and TOST
against +/-2.10 pp computed from the CV3 SE.

It does NOT change Essay 1's primary specification or any Essay 1 output. It reads the
committed sample and writes one new file.

Reuse, not reimplementation: the ladder statements are lifted verbatim from
scripts/165_essay2_inference_ladder.py through the ast module, exactly as scripts/249 does
(165 estimates and writes at module level, so it cannot be imported). They are executed once
per hypothesis variable, with that variable in 165's treatment position.

Two conventions, both reported:
  - Essay 1's committed tables use the NORMAL distribution: HC3 p (table 4) and the
    parent-CIK clustered p (table 8) are statsmodels defaults. Those values are recomputed
    here and must reproduce tables 4 and 8 exactly, or the script stops.
  - The ladder rungs (CV1, CV3) use t with G-1 degrees of freedom, as in scripts/165.

TOST on the CV3 rung: max(1 - T((b + 2.10)/se_cv3), T((b - 2.10)/se_cv3)) with G-1 df, the
CV3 analogue of scripts/158:83 (which uses the HC3 SE and n-k-1 df). The status rule is
158's: BOUNDED NULL if TOST p < .05, else NULL-INCONCLUSIVE if the rung's p > .05.

Seed: numpy default_rng(499), re-created for each hypothesis variable.
Output: outputs/defense_supplement/e1_cluster_ladder.csv (+ .log)
"""

import ast
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
SRC = Path('scripts/165_essay2_inference_ladder.py')
APP = Path('outputs/rebuild/appendix_v3')
OUT = Path('outputs/defense_supplement')
OUT.mkdir(parents=True, exist_ok=True)
SEED = 499
EQ = 2.10
L = []


def log(m=''):
    print(m)
    L.append(str(m))


# ---------------- sample: exactly scripts/158:55-60 ----------------
TREAT = 'fcc_form499'
HVARS = [TREAT, 'immediate_disclosure', 'prior_breaches_1yr', 'health_breach']
CONTROLS = HVARS + ['firm_size_log', 'leverage', 'roa']
LABEL = {TREAT: 'H2_FCC', 'immediate_disclosure': 'H1_timing',
         'prior_breaches_1yr': 'H3_prior', 'health_breach': 'H4_health'}
ev = pd.read_csv('Data/processed/rebuild/CANONICAL_V3.csv', low_memory=False)
reg = ev[ev['has_crsp_data'] == 1].dropna(subset=['car_30d'] + CONTROLS).reset_index(drop=True)
C1 = json.loads(Path('outputs/rebuild/constants_v3.json').read_text())
N, G = len(reg), reg['final_cik'].nunique()
G1 = reg.loc[reg[TREAT] == 1, 'final_cik'].nunique()
assert N == C1['N_regression'] == 340, f'Essay 1 sample is {N}, expected 340'
assert int(reg[TREAT].sum()) == C1['treated_regression'] == 106, 'treated events, expected 106'
assert G == 83, f'parent-CIK clusters {G}, expected 83'
assert G1 == C1['treated_parent_ciks_regression'] == 12, f'treated parent CIKs {G1}, expected 12'

# ---------------- lift 165's ladder statements (as scripts/249) ----------------
KEEP = {'XtX', 'XtX_inv', 'beta', 'resid', 'b_t', 'adj', 'V1', 'se_cv1', 'bbar', 'V3', 'se_cv3',
        'others', 'Sg_X', 'a_row', 'B_MAIN', 'p_wcr', 'p_wcu', 'p_webb', 'ci_lo', 'ci_hi',
        'fit_hc3', 'se_hc3', 'p_hc3', 'p_cv1', 'p_cv3', 'tcrit', 'mult', 'mde', 'meat', 'betas_del'}
KEEP_DEFS = {'wcb_p', 'invert_ci'}


def _targets(node):
    out = set()
    for t in (node.targets if isinstance(node, ast.Assign) else [node.target]):
        out |= {n.id for n in ast.walk(t) if isinstance(n, ast.Name)}
    return out


picked, names = [], set()
for node in ast.parse(SRC.read_text(encoding='utf-8')).body:
    if isinstance(node, ast.FunctionDef) and node.name in KEEP_DEFS:
        picked.append(node)
        names.add(node.name)
    elif isinstance(node, (ast.Assign, ast.AugAssign)) and _targets(node) & KEEP:
        picked.append(node)
        names |= _targets(node)
    elif isinstance(node, ast.For):
        body_t = set()
        for s in node.body:
            if isinstance(s, (ast.Assign, ast.AugAssign)):
                body_t |= _targets(s)
        if body_t & {'meat', 'betas_del'}:
            picked.append(node)
for need in ['wcb_p', 'invert_ci', 'se_cv1', 'se_cv3', 'p_wcr', 'ci_lo', 'ci_hi', 'mde']:
    assert need in names, '165 statement %s not found - 165 changed?' % need
LADDER = compile(ast.Module(body=picked, type_ignores=[]), str(SRC), 'exec')

Y = reg['car_30d'].astype(float).to_numpy()
Xdf = sm.add_constant(reg[CONTROLS].astype(float))
X = Xdf.to_numpy()
cols = list(Xdf.columns)
G_ids, G_inv = np.unique(reg['final_cik'].to_numpy(), return_inverse=True)
n, k = X.shape


def run_ladder(var):
    """Execute 165's ladder statements with `var` in the treatment position."""
    ns = dict(np=np, sm=sm, stats=stats, rng=np.random.default_rng(SEED),
              Y=Y, X=X, ti=cols.index(var), G_inv=G_inv, G=len(G_ids), G1=G1, n=n, k=k)
    exec(LADDER, ns)
    return ns


# ---------------- Essay 1's own conventions, for the reproduction gate ----------------
fit_hc3_z = sm.OLS(Y, X).fit(cov_type='HC3')                                  # scripts/158:74
fit_cl_z = sm.OLS(Y, X).fit(cov_type='cluster', cov_kwds={'groups': reg['final_cik']})  # 158:286
t4 = pd.read_csv(APP / 'table_4.csv').set_index('Variable')
t8 = pd.read_csv(APP / 'table_8.csv').set_index('Method')
T8COL = {'immediate_disclosure': 'Timing p', TREAT: 'FCC p'}

log('=' * 96)
log(f'DEFSUP - Essay 1 cluster ladder (N={N} events; {int(reg[TREAT].sum())} treated events; '
    f'G={G} parent-CIK clusters; G1={G1} treated parent CIKs)')
log('=' * 96)

rows, changes = [], []
for var in HVARS:
    lab = LABEL[var]
    i = cols.index(var)
    ns = run_ladder(var)
    b, se1, se3, tq = ns['b_t'], ns['se_cv1'], ns['se_cv3'], ns['tcrit']
    # --- gate: HC3 and CV1 must reproduce tables 4 and 8 exactly ---
    hz_se, hz_p = fit_hc3_z.bse[i], fit_hc3_z.pvalues[i]
    cz_p = fit_cl_z.pvalues[i]
    assert round(b, 4) == float(t4.loc[var, 'Coef']), f'{lab} coef {round(b, 4)} vs table_4 {t4.loc[var, "Coef"]}'
    assert round(hz_se, 4) == float(t4.loc[var, 'SE']), f'{lab} HC3 SE {round(hz_se, 4)} vs table_4'
    assert round(hz_p, 4) == float(t4.loc[var, 'p']), f'{lab} HC3 p {round(hz_p, 4)} vs table_4'
    assert round(ns['se_hc3'], 4) == round(hz_se, 4), f'{lab}: 165 HC3 SE differs from 158 HC3 SE'
    assert abs(fit_cl_z.bse[i] - se1) < 1e-9, f'{lab}: 165 CV1 SE differs from statsmodels cluster SE'
    if var in T8COL:
        assert round(cz_p, 4) == float(t8.loc['Firm-clustered', T8COL[var]]), \
            f'{lab} clustered p {round(cz_p, 4)} vs table_8 {t8.loc["Firm-clustered", T8COL[var]]}'
    # --- CV3 extras ---
    t90 = stats.t.ppf(0.95, G - 1)
    tost3 = max(1 - stats.t.cdf((b + EQ) / se3, G - 1), stats.t.cdf((b - EQ) / se3, G - 1))
    status_hc3 = C1[f'{lab}_status']
    status_cv3 = ('BOUNDED NULL' if tost3 < .05 else
                  ('NULL-INCONCLUSIVE' if ns['p_cv3'] > .05 else 'REJECTS ON CV3'))
    if status_cv3 != status_hc3:
        changes.append((lab, status_hc3, status_cv3))
    base = dict(hypothesis=lab, variable=var, coef=b, N=N, n_treated_events=int(reg[TREAT].sum()),
                G=G, G1_treated_parent_ciks=G1, seed=SEED)
    rows += [
        dict(base, rung='HC3 (normal; Essay 1 table 4)', se=hz_se, p=hz_p,
             ci95_lo=b - 1.959963984540054 * hz_se, ci95_hi=b + 1.959963984540054 * hz_se,
             tost_p=C1[f'{lab}_tost_p'], status=status_hc3, note='committed primary rung'),
        dict(base, rung='CV1 parent CIK (normal; Essay 1 table 8)', se=se1, p=cz_p),
        dict(base, rung='CV1 parent CIK, t(G-1)', se=se1, p=ns['p_cv1'],
             ci95_lo=b - tq * se1, ci95_hi=b + tq * se1, df=G - 1),
        dict(base, rung='CV3 jackknife, t(G-1)', se=se3, p=ns['p_cv3'],
             ci95_lo=b - tq * se3, ci95_hi=b + tq * se3,
             ci90_lo=b - t90 * se3, ci90_hi=b + t90 * se3, df=G - 1,
             mde80=ns['mde'], tost_p=tost3, status=status_cv3),
        dict(base, rung='WCR restricted Rademacher', p=ns['p_wcr'], B=ns['B_MAIN'],
             ci95_lo=ns['ci_lo'], ci95_hi=ns['ci_hi'],
             note='p B=99,999; CI by inversion B=9,999 per evaluation'),
    ]
    log(f'\n## {lab} ({var}): coef {b:+.4f}  [HC3 and CV1 reproduce tables 4 and 8 exactly]')
    log(f'  HC3 (normal)        se {hz_se:8.4f}  p {hz_p:.4f}   TOST p {C1[f"{lab}_tost_p"]:.4f}  -> {status_hc3}')
    log(f'  CV1 (normal)        se {se1:8.4f}  p {cz_p:.4f}')
    log(f'  CV1, t({G - 1})          se {se1:8.4f}  p {ns["p_cv1"]:.4f}')
    log(f'  CV3 jackknife, t({G - 1}) se {se3:8.4f}  p {ns["p_cv3"]:.4f}   95% CI [{b - tq * se3:+.4f}, {b + tq * se3:+.4f}]'
        f'   90% CI [{b - t90 * se3:+.4f}, {b + t90 * se3:+.4f}]')
    log(f'  WCR (B={ns["B_MAIN"]:,})                    p {ns["p_wcr"]:.4f}   95% CI [{ns["ci_lo"]:+.4f}, {ns["ci_hi"]:+.4f}]')
    log(f'  CV3 MDE80 {ns["mde"]:.4f} | TOST(+/-{EQ}) on CV3 SE p {tost3:.4f}  -> {status_cv3}')

log('\n' + '=' * 96)
if changes:
    log('STATUS CHANGES under CV3 (HC3 call -> CV3 call):')
    for lab, a, c in changes:
        log(f'  {lab}: {a} -> {c}')
else:
    log('No bounded/inconclusive call changes under CV3: every hypothesis keeps its HC3 status.')

out = pd.DataFrame(rows)
front = ['hypothesis', 'variable', 'rung', 'coef', 'se', 'p', 'ci95_lo', 'ci95_hi', 'ci90_lo', 'ci90_hi',
         'df', 'B', 'mde80', 'tost_p', 'status', 'N', 'n_treated_events', 'G', 'G1_treated_parent_ciks',
         'seed', 'note']
out = out[front]
num = out.select_dtypes('number').columns
out[num] = out[num].round(4)
out.to_csv(OUT / 'e1_cluster_ladder.csv', index=False)
(OUT / 'e1_cluster_ladder.log').write_text('\n'.join(L) + '\n', encoding='utf-8')
log(f'\nwrote {OUT / "e1_cluster_ladder.csv"} ({len(out)} rows)')
