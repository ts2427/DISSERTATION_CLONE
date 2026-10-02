"""
DEFENSE SUPPLEMENT — PART A: Essay 2 inference ladder for DISCLOSURE DELAY
==========================================================================
t16_delay_on_treatment.csv (scripts/164) reports the Form 499 coefficient on
disclosure delay with CV1 only. This script completes the ladder that 165
reports for the volatility change: HC3, CV1, CV3 jackknife t(G-1), restricted
wild cluster bootstrap (Rademacher, B=99,999; CI by inversion, B=9,999), the
unrestricted bootstrap, Webb six-point (B=9,999), and MDE80 on the CV3 rung.

Reuse, not reimplementation: the ladder code is lifted verbatim from
scripts/165_essay2_inference_ladder.py through the ast module (165 cannot be
imported - it estimates and writes t25-t28 at module level). Only the
statements that compute the ladder are executed; 165's logging and file
writes are not. Before any delay estimate, the lifted code is run on 165's own
outcome and design and must reproduce t26_inference_ladder.csv and
t28_design_resolution.csv to the committed decimals.

Design: the canonical Essay 2 sample (t1_final_sample.csv; N=333, 104 treated
events, G=82 parent-CIK clusters, G1=12 treated parent CIKs) and the t16
specification: delay ~ fcc_form499 + e2_pre_sd + firm_size_log + leverage +
roa + health_breach + prior_events.

Seed: numpy default_rng(499), re-created for each outcome so every outcome's
bootstrap draws in the same order 165 uses (WCR, WCU, Webb, then CI).

Output: outputs/defense_supplement/e2_delay_ladder.csv (+ .log)
"""

import ast
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
SRC = Path('scripts/165_essay2_inference_ladder.py')
T = Path('outputs/tables/essay2_v2')
OUT = Path('outputs/defense_supplement')
OUT.mkdir(parents=True, exist_ok=True)
SEED = 499
L = []


def log(m=''):
    print(m)
    L.append(str(m))


TREAT = 'fcc_form499'
CONTROLS_X = ['e2_pre_sd', 'firm_size_log', 'leverage', 'roa',
              'health_breach', 'prior_events']   # scripts/164, t16
XS4 = ['delay_w', 'e2_pre_sd', 'firm_size_log', 'leverage', 'roa', TREAT,
       'health_breach', 'prior_events']          # scripts/165, t26

fin = pd.read_csv(T / 't1_final_sample.csv', low_memory=False)
assert len(fin) == 333, 'Essay 2 sample is %d, expected 333' % len(fin)
assert int(fin[TREAT].sum()) == 104, 'treated events %d, expected 104' % int(fin[TREAT].sum())
assert fin['final_cik'].nunique() == 82, 'G %d, expected 82' % fin['final_cik'].nunique()
assert fin.loc[fin[TREAT] == 1, 'final_cik'].nunique() == 12, 'G1 expected 12'
fin['delay_log'] = np.log1p(fin['disclosure_delay_days'])

# ---------------- lift 165's ladder statements ----------------
KEEP = {'XtX', 'XtX_inv', 'beta', 'resid', 'b_t', 'adj', 'V1', 'se_cv1',
        'bbar', 'V3', 'se_cv3', 'others', 'Sg_X', 'a_row', 'B_MAIN',
        'p_wcr', 'p_wcu', 'p_webb', 'ci_lo', 'ci_hi', 'fit_hc3', 'se_hc3',
        'p_hc3', 'p_cv1', 'p_cv3', 'tcrit', 'mult', 'mde', 'meat', 'betas_del'}
KEEP_DEFS = {'wcb_p', 'invert_ci'}


def _targets(node):
    out = set()
    tg = node.targets if isinstance(node, ast.Assign) else [node.target]
    for t in tg:
        for n in ast.walk(t):
            if isinstance(n, ast.Name):
                out.add(n.id)
    return out


src = SRC.read_text(encoding='utf-8')
picked = []
for node in ast.parse(src).body:
    if isinstance(node, ast.FunctionDef) and node.name in KEEP_DEFS:
        picked.append(node)
    elif isinstance(node, (ast.Assign, ast.AugAssign)) and _targets(node) & KEEP:
        picked.append(node)
    elif isinstance(node, ast.For):
        body_t = set()
        for s in node.body:
            if isinstance(s, (ast.Assign, ast.AugAssign)):
                body_t |= _targets(s)
        if body_t & {'meat', 'betas_del'}:
            picked.append(node)
names = set()
for n in picked:
    if isinstance(n, ast.FunctionDef):
        names.add(n.name)
    elif not isinstance(n, ast.For):
        names |= _targets(n)
for need in ['wcb_p', 'invert_ci', 'se_cv1', 'se_cv3', 'p_wcr', 'ci_lo', 'ci_hi', 'mde']:
    assert need in names, '165 statement %s not found - 165 changed?' % need
LADDER = compile(ast.Module(body=picked, type_ignores=[]), str(SRC), 'exec')


def run_ladder(df, ycol, xcols):
    """Execute 165's ladder statements on (df[ycol], const + xcols)."""
    ns = dict(np=np, sm=sm, stats=stats, rng=np.random.default_rng(SEED))
    Y = df[ycol].astype(float).to_numpy()
    X = sm.add_constant(df[xcols].astype(float)).to_numpy()
    cols = ['const'] + xcols
    G_ids, G_inv = np.unique(df['final_cik'].to_numpy(), return_inverse=True)
    ns.update(Y=Y, X=X, ti=cols.index(TREAT), G_inv=G_inv, G=len(G_ids),
              G1=df.loc[df[TREAT] == 1, 'final_cik'].nunique(),
              n=X.shape[0], k=X.shape[1])
    exec(LADDER, ns)
    return ns


def rows_for(ns, label):
    n, k, G = ns['n'], ns['k'], ns['G']
    b, tq = ns['b_t'], ns['tcrit']
    base = dict(outcome=label, coef=b, N=n, n_treated_events=104, G=G, G1=ns['G1'])
    hc3t = stats.t.ppf(.975, n - k)
    return [
        dict(base, rung='HC3', se=ns['se_hc3'], ci_lo=b - hc3t * ns['se_hc3'],
             ci_hi=b + hc3t * ns['se_hc3'], p=ns['p_hc3'], B=np.nan, df=n - k),
        dict(base, rung='CV1 parent CIK', se=ns['se_cv1'], ci_lo=b - tq * ns['se_cv1'],
             ci_hi=b + tq * ns['se_cv1'], p=ns['p_cv1'], B=np.nan, df=G - 1),
        dict(base, rung='CV3 jackknife', se=ns['se_cv3'], ci_lo=b - tq * ns['se_cv3'],
             ci_hi=b + tq * ns['se_cv3'], p=ns['p_cv3'], B=np.nan, df=G - 1),
        dict(base, rung='WCR restricted Rademacher', se=np.nan, ci_lo=ns['ci_lo'],
             ci_hi=ns['ci_hi'], p=ns['p_wcr'], B=ns['B_MAIN'], df=np.nan,
             note='p B=99,999; CI by inversion B=9,999 per evaluation'),
        dict(base, rung='WCU unrestricted Rademacher', se=np.nan, ci_lo=np.nan,
             ci_hi=np.nan, p=ns['p_wcu'], B=ns['B_MAIN'], df=np.nan),
        dict(base, rung='WCR Webb six-point', se=np.nan, ci_lo=np.nan, ci_hi=np.nan,
             p=ns['p_webb'], B=9_999, df=np.nan),
    ]


log('=' * 90)
log('DEFSUP A - Essay 2 disclosure-delay inference ladder (N=333 events; 104 treated '
    'events; G=82 parent-CIK clusters; G1=12 treated parent CIKs)')
log('=' * 90)

# ---------------- reproduction gate: 165 on its own design ----------------
log('\n## Gate: lifted 165 code reproduces t26 / t28 (volatility change, XS4)')
ns = run_ladder(fin, 'e2_vol_change', XS4)
t26 = pd.read_csv(T / 't26_inference_ladder.csv')
t28 = pd.read_csv(T / 't28_design_resolution.csv')
got = [ns['se_hc3'], ns['se_cv1'], ns['se_cv3']]
for i, g in enumerate(got):
    assert round(g, 4) == t26.loc[i, 'se'], ('t26 se row %d: %s vs %s' % (i, round(g, 4), t26.loc[i, 'se']))
for i, key in enumerate(['p_hc3', 'p_cv1', 'p_cv3', 'p_wcr', 'p_wcu', 'p_webb']):
    assert round(ns[key], 4) == t26.loc[i, 'p'], ('t26 p row %d: %s vs %s' % (i, round(ns[key], 4), t26.loc[i, 'p']))
assert round(ns['b_t'], 4) == t26.loc[0, 'coef']
assert (round(ns['ci_lo'], 4), round(ns['ci_hi'], 4)) == (t26.loc[3, 'ci_lo'], t26.loc[3, 'ci_hi']), \
    'WCR CI %s vs %s' % ((round(ns['ci_lo'], 4), round(ns['ci_hi'], 4)), (t26.loc[3, 'ci_lo'], t26.loc[3, 'ci_hi']))
assert round(ns['mde'], 4) == t28.loc[0, 'mde_daily'], 'MDE %s vs %s' % (round(ns['mde'], 4), t28.loc[0, 'mde_daily'])
log('  PASS: coef, HC3/CV1/CV3 SE, all six p-values, WCR CI and MDE match t26/t28 exactly.')

# ---------------- delay ladders ----------------
t16 = pd.read_csv(T / 't16_delay_on_treatment.csv')
rows = []
for dv, lab in [('disclosure_delay_days', 'delay (raw days)'),
                ('delay_w', 'delay (winsorized p99)'),
                ('delay_log', 'log(1+delay)')]:
    ns = run_ladder(fin, dv, [TREAT] + CONTROLS_X)
    # A3: CV1 must reproduce t16 exactly
    r16 = t16.loc[t16['dv'] == lab].iloc[0]
    cv1 = dict(coef=round(ns['b_t'], 3), se=round(ns['se_cv1'], 3),
               ci_lo=round(ns['b_t'] - ns['tcrit'] * ns['se_cv1'], 3),
               ci_hi=round(ns['b_t'] + ns['tcrit'] * ns['se_cv1'], 3),
               p=round(ns['p_cv1'], 4))
    for kk, vv in cv1.items():
        assert vv == r16[kk], 'A3 FAIL %s %s: %s vs t16 %s' % (lab, kk, vv, r16[kk])
    mean_dv = fin[dv].astype(float).mean()
    rr = rows_for(ns, lab)
    for r in rr:
        r.update(mde80_cv3=ns['mde'], mean_outcome=mean_dv,
                 mde80_share_of_mean=ns['mde'] / mean_dv, seed=SEED)
    rows += rr
    log(f'\n## {lab}: coef {ns["b_t"]:+.3f} (A3: CV1 reproduces t16 exactly)')
    for r in rr:
        log(f'  {r["rung"]:<30} se {r["se"]:>9.3f}  CI [{r["ci_lo"]:+.3f}, {r["ci_hi"]:+.3f}]'
            f'  p {r["p"]:.4f}')
    log(f'  MDE80 (CV3, 165 formula: (t.975+t.80, df={ns["G"] - 1}) x SE_CV3) = '
        f'{ns["mde"]:.3f}; mean outcome {mean_dv:.3f}; MDE/mean = {ns["mde"] / mean_dv:.1%}')

out = pd.DataFrame(rows)
num = out.select_dtypes('number').columns
out[num] = out[num].round(4)
out.to_csv(OUT / 'e2_delay_ladder.csv', index=False)
(OUT / 'e2_delay_ladder.log').write_text('\n'.join(L) + '\n', encoding='utf-8')
log(f'\nwrote {OUT / "e2_delay_ladder.csv"} ({len(out)} rows)')
