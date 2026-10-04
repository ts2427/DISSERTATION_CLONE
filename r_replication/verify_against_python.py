"""
Compare r_results.csv (written by replicate.R) with the committed Python outputs and write
VERIFICATION.md.   Run from the repository root:   python r_replication/verify_against_python.py

Rules
  analytic values (coefficients, SEs, analytic p-values, CIs, TOST, MDE): must match to 4 decimal
      places, i.e. the R value rounded to 4 dp equals the committed Python value (which the
      pipeline stores at 4 dp).
  bootstrap p-values: |R - Python| <= 3 * sqrt(p (1 - p) / B), p = the Python value, B = draws.
Exit code 1 if any analytic value fails.
"""
import json
import math
import sys
from pathlib import Path

import pandas as pd

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
HERE = Path('r_replication')
r = pd.read_csv(HERE / 'r_results.csv')
R = {(a, b, c, d): v for a, b, c, d, v in r.itertuples(index=False)}
rows = []


def analytic(essay, model, term, stat, py, source, note=''):
    rv = R[(essay, model, term, stat)]
    ok = abs(round(rv, 4) - py) < 1e-9 or abs(rv - py) <= 5.0001e-5
    rows.append(dict(kind='analytic', essay=essay, model=model, term=term, statistic=stat, r=rv,
                     python=py, diff=rv - py, tol='4 dp', ok=ok, source=source, note=note))


def derived(essay, model, term, stat, py, source, tol, note):
    """Python value that was itself computed from 4-dp rounded inputs: compared at a stated tolerance."""
    rv = R[(essay, model, term, stat)]
    rows.append(dict(kind='analytic (from rounded inputs)', essay=essay, model=model, term=term,
                     statistic=stat, r=rv, python=py, diff=rv - py, tol=f'{tol:g}', ok=abs(rv - py) <= tol,
                     source=source, note=note))


def boot(essay, model, term, stat, py, B, source):
    rv = R[(essay, model, term, stat)]
    tol = 3 * math.sqrt(py * (1 - py) / B)
    rows.append(dict(kind='bootstrap', essay=essay, model=model, term=term, statistic=stat, r=rv,
                     python=py, diff=rv - py, tol=f'{tol:.5f} (B={B:,})', ok=abs(rv - py) <= tol,
                     source=source, note=''))


# ------------------------------------------------------------------ Essay 1
c = json.loads(Path('outputs/rebuild/constants_v3.json').read_text())
t4 = pd.read_csv('outputs/rebuild/appendix_v3/table_4.csv').set_index('Variable')
t8 = pd.read_csv('outputs/rebuild/appendix_v3/table_8.csv').set_index('Method')
dx = pd.read_csv('outputs/defense_supplement/deck_exhibits.csv')
ci90 = dx[dx.exhibit == 'E1_ci90_essay1'].set_index('key')['value'].astype(float)
E1, M1 = 'Essay 1', '30-day CAR, baseline OLS'
VAR = {'H1_timing': 'immediate_disclosure', 'H2_FCC': 'fcc_form499', 'H3_prior': 'prior_breaches_1yr',
       'H4_health': 'health_breach'}
S1 = 'outputs/rebuild/constants_v3.json'
for h, var in VAR.items():
    analytic(E1, M1, h, 'coef', c[f'{h}_coef'], S1)
    analytic(E1, M1, h, 'se_hc3', float(t4.loc[var, 'SE']), 'outputs/rebuild/appendix_v3/table_4.csv')
    analytic(E1, M1, h, 'p_hc3', c[f'{h}_p'], S1)
    analytic(E1, M1, h, 'ci95_lo', c[f'{h}_ci'][0], S1)
    analytic(E1, M1, h, 'ci95_hi', c[f'{h}_ci'][1], S1)
    analytic(E1, M1, h, 'tost_p', c[f'{h}_tost_p'], S1)
    analytic(E1, M1, h, 'mde80', c[f'{h}_mde80'], S1)
    for side in ('lo', 'hi'):
        derived(E1, M1, h, f'ci90_{side}', float(ci90[f'{h}_ci90_{side}']),
                'outputs/defense_supplement/deck_exhibits.csv', 2e-4,
                'Python 90% CI = committed 4-dp coef +/- 1.645 x committed 4-dp SE; R uses full precision')
analytic(E1, M1, 'H1_timing', 'p_cluster', float(t8.loc['Firm-clustered', 'Timing p']),
         'outputs/rebuild/appendix_v3/table_8.csv')
analytic(E1, M1, 'H2_FCC', 'p_cluster', float(t8.loc['Firm-clustered', 'FCC p']),
         'outputs/rebuild/appendix_v3/table_8.csv')

# ------------------------------------------------------------------ Essay 2
E2, T = 'Essay 2', 'fcc_form499'
t26 = pd.read_csv('outputs/tables/essay2_v2/t26_inference_ladder.csv')
t28 = pd.read_csv('outputs/tables/essay2_v2/t28_design_resolution.csv')
row = lambda key: t26[t26.procedure.str.startswith(key)].iloc[0]
MV, S26 = 'Volatility change (daily pp)', 'outputs/tables/essay2_v2/t26_inference_ladder.csv'
analytic(E2, MV, T, 'coef', float(row('CV1').coef), S26)
analytic(E2, MV, T, 'se_cv1', float(row('CV1').se), S26)
analytic(E2, MV, T, 'p_cv1', float(row('CV1').p), S26)
analytic(E2, MV, T, 'se_cv3', float(row('CV3').se), S26)
analytic(E2, MV, T, 'p_cv3', float(row('CV3').p), S26)
analytic(E2, MV, T, 'ci_cv3_lo', float(row('CV3').ci_lo), S26)
analytic(E2, MV, T, 'ci_cv3_hi', float(row('CV3').ci_hi), S26)
analytic(E2, MV, T, 'mde80_cv3', float(t28.mde_daily.iloc[0]), 'outputs/tables/essay2_v2/t28_design_resolution.csv')
boot(E2, MV, T, 'p_wcr', float(row('WCR wild').p), 99_999, S26)

dl = pd.read_csv('outputs/defense_supplement/e2_delay_ladder.csv')
SD = 'outputs/defense_supplement/e2_delay_ladder.csv'
for model, key in [('Disclosure delay, raw days', 'delay (raw days)'),
                   ('Disclosure delay, winsorized p99', 'delay (winsorized p99)')]:
    g = dl[dl.outcome == key].set_index('rung')
    analytic(E2, model, T, 'coef', float(g.loc['CV1 parent CIK', 'coef']), SD)
    analytic(E2, model, T, 'se_cv1', float(g.loc['CV1 parent CIK', 'se']), SD)
    analytic(E2, model, T, 'p_cv1', float(g.loc['CV1 parent CIK', 'p']), SD)
    analytic(E2, model, T, 'se_cv3', float(g.loc['CV3 jackknife', 'se']), SD)
    analytic(E2, model, T, 'p_cv3', float(g.loc['CV3 jackknife', 'p']), SD)
    analytic(E2, model, T, 'ci_cv3_lo', float(g.loc['CV3 jackknife', 'ci_lo']), SD)
    analytic(E2, model, T, 'ci_cv3_hi', float(g.loc['CV3 jackknife', 'ci_hi']), SD)
    analytic(E2, model, T, 'mde80_cv3', float(g.loc['CV3 jackknife', 'mde80_cv3']), SD)
    boot(E2, model, T, 'p_wcr', float(g.loc['WCR restricted Rademacher', 'p']), 99_999, SD)

t50 = pd.read_csv('outputs/tables/essay2_v2/t50_announcement_contrast.csv')
a = t50[t50.level == 'L3'].iloc[0]
MA, S50 = 'Announcement-window elevation (daily pp)', 'outputs/tables/essay2_v2/t50_announcement_contrast.csv'
analytic(E2, MA, T, 'coef', float(a.coef), S50)
analytic(E2, MA, T, 'se_cv1', float(a.se), S50)
analytic(E2, MA, T, 'p_cv1', float(a.p_cv1), S50)
analytic(E2, MA, T, 'se_cv3', float(a.se_cv3), S50)
analytic(E2, MA, T, 'p_cv3', float(a.p_cv3), S50)
boot(E2, MA, T, 'p_wcr', float(a.p_wcr), int(a.B_wcr), S50)

# ------------------------------------------------------------------ Essay 3
E3 = 'Essay 3'
f1 = pd.read_csv('outputs/essay3_v4/f1_ladder.csv').set_index('window')
f4 = pd.read_csv('outputs/essay3_v4/f4_placebo.csv').iloc[0]
for label, src, s in [('30-day', f1.loc[30], 'outputs/essay3_v4/f1_ladder.csv'),
                      ('90-day', f1.loc[90], 'outputs/essay3_v4/f1_ladder.csv'),
                      ('180-day', f1.loc[180], 'outputs/essay3_v4/f1_ladder.csv'),
                      ('Placebo', f4, 'outputs/essay3_v4/f4_placebo.csv')]:
    m = f'Executive departure, {label}'
    for st in ['coef', 'se_hc3', 'p_hc3', 'se_cv1', 'p_cv1', 'se_cv3', 'p_cv3', 'ci_cv3_lo', 'ci_cv3_hi',
               'mde80_cv3']:
        analytic(E3, m, T, st, float(src[st]), s)
    boot(E3, m, T, 'p_wcr', float(src['p_wcr']), int(src['B_wcr']), s)

# ------------------------------------------------------------------ Essay 1 supplement (scripts/255)
el = pd.read_csv('outputs/defense_supplement/e1_cluster_ladder.csv')
SL, ES, ML = 'outputs/defense_supplement/e1_cluster_ladder.csv', 'Essay 1 supplement', '30-day CAR, cluster ladder'
for h in VAR:
    g = el[el.hypothesis == h].set_index('rung')
    cv1r, cv3r, wr = g.loc['CV1 parent CIK, t(G-1)'], g.loc['CV3 jackknife, t(G-1)'], g.loc['WCR restricted Rademacher']
    analytic(ES, ML, h, 'coef', float(cv3r.coef), SL)
    analytic(ES, ML, h, 'se_cv1', float(cv1r.se), SL)
    analytic(ES, ML, h, 'p_cv1', float(cv1r.p), SL)
    analytic(ES, ML, h, 'se_cv3', float(cv3r.se), SL)
    analytic(ES, ML, h, 'p_cv3', float(cv3r.p), SL)
    analytic(ES, ML, h, 'ci_cv3_lo', float(cv3r.ci95_lo), SL)
    analytic(ES, ML, h, 'ci_cv3_hi', float(cv3r.ci95_hi), SL)
    analytic(ES, ML, h, 'ci90_cv3_lo', float(cv3r.ci90_lo), SL)
    analytic(ES, ML, h, 'ci90_cv3_hi', float(cv3r.ci90_hi), SL)
    analytic(ES, ML, h, 'mde80_cv3', float(cv3r.mde80), SL)
    analytic(ES, ML, h, 'tost_p_cv3', float(cv3r.tost_p), SL)
    boot(ES, ML, h, 'p_wcr', float(wr.p), int(wr.B), SL)

# ------------------------------------------------------------------ report
df = pd.DataFrame(rows)
an = df[df.kind == 'analytic']
dr = df[df.kind.str.startswith('analytic (')]
bt = df[df.kind == 'bootstrap']
commit = __import__('subprocess').run(['git', 'rev-parse', '--short', 'defense-final^{commit}'],
                                      capture_output=True, text=True).stdout.strip()
L = ['# Verification: R replication against the committed Python results', '',
     f'R values: `r_results.csv`, written by `replicate.R` (R 4.5.0, seed 499). Python values: the committed '
     f'outputs of the pipeline, frozen at tag `defense-final` (`{commit}`). Generated by '
     '`verify_against_python.py`.', '',
     '## Summary', '',
     '| Check | Values | Match | Rule |', '|---|---|---|---|',
     f'| Analytic values (coefficients, SEs, p-values, CIs, TOST, MDE) | {len(an)} | **{int(an.ok.sum())} of {len(an)}** | R rounded to 4 decimals equals the committed Python value |',
     f'| 90% CIs (Essay 1) | {len(dr)} | **{int(dr.ok.sum())} of {len(dr)}** | within 0.0002: the Python figure was built from 4-decimal inputs |',
     f'| Bootstrap p-values (restricted wild cluster) | {len(bt)} | **{int(bt.ok.sum())} of {len(bt)}** | \\|R − Python\\| ≤ 3·√(p(1−p)/B) |',
     '',
     'Bootstrap p-values cannot match exactly: R and numpy draw different random numbers. The rule above '
     'is the Monte Carlo error of ONE simulation; the difference of two independent simulations has √2 times '
     'that standard error, so the rule is the stricter of the two natural choices.', '']
for title, sub in [('Analytic values', an), ('90% confidence intervals (Essay 1)', dr), ('Bootstrap p-values', bt)]:
    L += [f'## {title}', '', '| Essay | Model | Term | Statistic | R | Python | R − Python | Tolerance | Match | Python source |',
          '|---|---|---|---|---|---|---|---|---|---|']
    for x in sub.itertuples(index=False):
        L.append(f'| {x.essay} | {x.model} | {x.term} | {x.statistic} | {x.r:.6f} | {x.python:.4f} | '
                 f'{x.diff:+.6f} | {x.tol} | {"yes" if x.ok else "**NO**"} | `{x.source}` |')
    notes = sorted(set(n for n in sub.note if n))
    if notes:
        L += [''] + [f'Note: {n}.' for n in notes]
    L.append('')
(HERE / 'VERIFICATION.md').write_text('\n'.join(L), encoding='utf-8', newline='\n')
print(f'analytic {int(an.ok.sum())}/{len(an)} | 90% CI {int(dr.ok.sum())}/{len(dr)} | bootstrap {int(bt.ok.sum())}/{len(bt)}')
bad = df[~df.ok]
if len(bad):
    print(bad[['kind', 'essay', 'model', 'term', 'statistic', 'r', 'python', 'diff', 'tol']].to_string())
sys.exit(1 if (~an.ok).any() else 0)
