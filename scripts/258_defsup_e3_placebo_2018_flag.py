"""
ESSAY 3 - placebo sensitivity to one miscoded filing (OUTSIDE THE ANALYSIS PLAN)
================================================================================
The classifier coded two executive departures from T-Mobile's 8-K of April 30, 2018 (accession
0001104659-18-028086). The filing text describes neither as a departure: one sentence passes the
title of President from the chief executive, who stays chief executive, to the chief operating
officer; the other is a severance clause in the chief operating officer's term sheet. See
docs/claude/KNOWN_LIMITATIONS.md.

This script reports, and changes nothing:

  Panel "placebo sensitivity"  the committed placebo specification, re-run, and the same
                               specification with the placebo outcome of the one event whose flag
                               rests on that filing (breach 2018-08-20) set to 0.
  Panel "filing windows"       every event for which the filing's two coded departures fall in an
                               outcome window, the placebo window or the baseline window.

It is a sensitivity outside the analysis plan. It does not enter the test ledger or any constants
file, and the committed placebo estimate (outputs/essay3_v4/f4_placebo.csv) is unchanged: the
re-run must reproduce every analytic value of that file or the script stops.

The estimator is ladder() of scripts/227, lifted unchanged. The wild cluster bootstrap is seeded
here (SEED), the same stream for both rows, so its p-values are reproducible; the committed
bootstrap p came from a different point in 227's stream and differs in the third decimal.

Output: outputs/defense_supplement/e3_placebo_2018_flag.csv
"""

import ast
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
V4 = Path('outputs/essay3_v4')
OUT = Path('outputs/defense_supplement')
SRC227 = Path('scripts/227_essay3_v4_estimation.py')
SEED, B = 258, 99_999
TM, ACC, FILED, EVENT = 1283699, '0001104659-18-028086', pd.Timestamp('2018-04-30'), '2018-08-20'
STATUS = 'outside the analysis plan; not in the test ledger; committed placebo estimate unchanged'
Y = 'placebo_exec_departure_rd'


def stop(msg):
    print('STOP: ' + msg)
    sys.exit(1)


def borrow_from_227():
    """Lift ladder() / pub() and their constants out of scripts/227, unchanged."""
    src = SRC227.read_text(encoding='utf-8')
    want_fn, want_const, pieces = {'ladder'}, {'TREAT', 'BASE', 'CTRL', 'pub', 'rng'}, []
    for node in ast.parse(src).body:
        if isinstance(node, ast.FunctionDef) and node.name in want_fn:
            pieces.append(ast.get_source_segment(src, node))
        elif isinstance(node, ast.Assign) and {t.id for t in node.targets if isinstance(t, ast.Name)} & want_const:
            pieces.append(ast.get_source_segment(src, node))
    ns = {'np': np, 'pd': pd, 'sm': sm, 'stats': stats}
    exec('\n'.join(pieces), ns)
    if (want_fn | want_const) - set(ns):
        stop('could not lift ladder() and its constants from scripts/227')
    return ns


ns = borrow_from_227()
TREAT, X = ns['TREAT'], [ns['TREAT']] + ns['CTRL']['rd']

allev = pd.read_csv(V4 / 'e_analysis_sample.csv', low_memory=False)
allev['bd'] = allev['breach_date'].astype(str).str[:10]
d = allev[allev['in_analysis_sample'] == 1].copy()
if (len(d), int(d[TREAT].sum()), d['final_cik'].nunique()) != (405, 109, 119):
    stop('analysis sample is not 405 events / 109 treated / 119 parent CIKs')

# ------------------------------------------------------------------ what the filing was coded as
dep = pd.read_csv(V4 / 'c2_departure_events.csv', dtype={'first_accession': str})
ex = dep[(dep['cik'] == TM) & (dep['grp'] == 'exec')].copy()
ex['fd'] = pd.to_datetime(ex['first_date'])
coded = ex[ex['first_accession'] == ACC]
if sorted(coded['pkey']) != ['legere', 'sievert'] or set(coded['fd']) != {FILED} or (dep['first_accession'] == ACC).sum() != 2:
    stop('the filing is not coded as exactly two executive departures (Legere, Sievert) dated 2018-04-30')

# ------------------------------------------------------------------ panel: filing windows
# windows as scripts/224 builds them: outcome (t0, t0 + w], placebo (t0 - 180, t0],
# baseline [t0 - 730, t0 - 181]


def window(days):
    if 0 < days <= 180:
        return 'outcome (%s)' % '/'.join(str(w) for w in (30, 90, 180) if days <= w)
    if -180 < days <= 0:
        return 'placebo'
    if -730 <= days <= -181:
        return 'baseline'
    return ''


rows = []
for _, e in allev[allev['outcome_cik'] == TM].sort_values('reported_date').iterrows():
    dn = (FILED - pd.Timestamp(e['reported_date'])).days
    db = (FILED - pd.Timestamp(e['breach_date'])).days
    if window(dn) or window(db):
        rows.append(dict(panel='filing windows', final_cik=int(e['final_cik']), breach_date=e['bd'],
                         reported_date=str(e['reported_date'])[:10],
                         in_analysis_sample=int(e['in_analysis_sample']), treated=int(e[TREAT]),
                         days_filing_minus_notification=dn, window_notification_anchor=window(dn),
                         days_filing_minus_breach=db, window_breach_anchor=window(db),
                         coded_departures_from_filing=len(coded),
                         placebo_exec_departure_rd=int(e[Y]),
                         baseline_exec_departures_rd=int(e['baseline_exec_departures_rd']),
                         baseline_exec_rate_py_rd=e['baseline_exec_rate_py_rd'], status=STATUS))
W = pd.DataFrame(rows)
if (W['window_notification_anchor'].tolist() != ['placebo', 'baseline', 'baseline', 'baseline']
        or W['breach_date'].tolist() != [EVENT, '2019-11-26', '2020-04-02', '2020-04-15']
        or set(W['final_cik']) != {TM} or not (W['in_analysis_sample'] == 1).all()):
    stop('the filing does not touch exactly the four expected T-Mobile events:\n' + W.to_string())

# ------------------------------------------------------------------ the one flag that rests on it
tgt = (d['final_cik'] == TM) & (d['bd'] == EVENT)
if tgt.sum() != 1 or int(d.loc[tgt, Y].iloc[0]) != 1:
    stop('the 2018-08-20 T-Mobile event is not in the sample with its placebo flag set')
t0 = pd.Timestamp(d.loc[tgt, 'reported_date'].iloc[0])
inwin = ex[((ex['fd'] - t0).dt.days > -180) & ((ex['fd'] - t0).dt.days <= 0)]
if set(inwin['first_accession']) != {ACC}:
    stop('another coded departure also sets the 2018-08-20 placebo flag: ' + ', '.join(inwin['first_accession']))

# ------------------------------------------------------------------ panel: placebo sensitivity
mod = d.copy()
mod.loc[tgt, Y] = 0
est = []
for label, frame in (('committed specification, re-run', d), ('2018-08-20 placebo flag set to 0', mod)):
    ns['rng'] = np.random.default_rng(SEED)
    r = ns['pub'](ns['ladder'](frame, Y, X, B=B))
    est.append(dict(panel='placebo sensitivity', specification=label, y=Y, n=r['n'], G=r['G'], G1=r['G1'],
                    coef=r['coef'], se_hc3=r['se_hc3'], p_hc3=r['p_hc3'], se_cv1=r['se_cv1'], p_cv1=r['p_cv1'],
                    se_cv3=r['se_cv3'], p_cv3=r['p_cv3'], ci_cv3_lo=r['ci_cv3_lo'], ci_cv3_hi=r['ci_cv3_hi'],
                    p_wcr=r['p_wcr'], B_wcr=B, seed=SEED,
                    treated_flagged=int(frame.loc[frame[TREAT] == 1, Y].sum()), treated_n=int((frame[TREAT] == 1).sum()),
                    control_flagged=int(frame.loc[frame[TREAT] == 0, Y].sum()), control_n=int((frame[TREAT] == 0).sum()),
                    status=STATUS))
S = pd.DataFrame(est)

# the re-run must be the committed estimate: every analytic value, and the bootstrap p within
# Monte Carlo error of the committed one
F4 = pd.read_csv(V4 / 'f4_placebo.csv').iloc[0]
for k in ('n', 'G', 'G1', 'coef', 'se_hc3', 'p_hc3', 'se_cv1', 'p_cv1', 'se_cv3', 'p_cv3', 'ci_cv3_lo', 'ci_cv3_hi'):
    if float(S.loc[0, k]) != float(F4[k]):
        stop(f're-run does not reproduce f4_placebo.csv: {k} {S.loc[0, k]} vs {F4[k]}')
if abs(float(S.loc[0, 'p_wcr']) - float(F4['p_wcr'])) > 0.01:
    stop(f'bootstrap p {S.loc[0, "p_wcr"]} is not within .01 of the committed {F4["p_wcr"]}')
if S['treated_flagged'].tolist() != [25, 24] or S['control_flagged'].tolist() != [70, 70]:
    stop(f'flagged counts are {S["treated_flagged"].tolist()} / {S["control_flagged"].tolist()}, expected 25 then 24 / 70')

OUT.mkdir(parents=True, exist_ok=True)
pd.concat([S, W], ignore_index=True).to_csv(OUT / 'e3_placebo_2018_flag.csv', index=False, lineterminator='\n')

print(f'wrote {OUT / "e3_placebo_2018_flag.csv"}  ({STATUS})')
print(f'bootstrap: B = {B:,}, seed {SEED}, same stream for both rows')
for _, r in S.iterrows():
    print(f'  {r["specification"]}: coef {100 * r["coef"]:.2f} pp, CV3 SE {100 * r["se_cv3"]:.2f}, '
          f'CV3 p {r["p_cv3"]:.4f}, CV1 p {r["p_cv1"]:.4f}, bootstrap p {r["p_wcr"]:.4f}, '
          f'treated {r["treated_flagged"]} of {r["treated_n"]}, control {r["control_flagged"]} of {r["control_n"]}')
print(W[['breach_date', 'reported_date', 'days_filing_minus_notification', 'window_notification_anchor',
         'window_breach_anchor', 'baseline_exec_departures_rd']].to_string(index=False))
