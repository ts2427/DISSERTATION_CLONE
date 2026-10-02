"""Defense supplement: deck exhibits as arithmetic on committed outputs.

Usage:
    python scripts/252_defsup_deck_exhibits.py

Writes ONLY:
    outputs/defense_supplement/deck_exhibits.csv   long format: exhibit,key,value,unit,sample,n,formula,source
    outputs/defense_supplement/deck_exhibits.json  same rows keyed by exhibit
    outputs/defense_supplement/deck_exhibits.log

No estimation. Every number is arithmetic on git-tracked inputs. The arithmetic was first
ported from the scratchpad helpers documented in outputs/RESULTS_COMPLETENESS_REPORT.md Part D
(provenance only): that report is NOT read and no expected value is transcribed from it.

ASSERT POLICY (G8 ruling). Every assert compares a value computed here against an independent
value from a committed input, or against an independent recomputation path from committed
inputs. Nothing is compared to a typed number except the sample sizes in section 1 (the
author-mandated sample definitions) and design constants that are themselves verified (the
TOST bound 2.10 is confirmed by reproducing the committed TOST p-values from it).
Tolerances are stated per assert and follow one rule:
    tol = half a unit in the last committed digit of the reference value
        + the worst-case propagation of the committed rounding of every input, evaluated over
          all corners of the input-rounding box (prop())
        + 1e-9 float slack.
    Exact identities between two computation paths on the same full-precision data use 1e-9
    (or 1e-12 where no summation is involved); counts and labels are exact.
Quantities that have no committed counterpart (dollar values, departures, CAAR by day) are
checked as identities computed two independent ways or as invariants (nesting, symmetry);
the log says so on each line. Any failed assert exits 1 before anything is written. There are
no soft (FLAG) paths.

Inputs (all git-tracked; crsp_quotes_topup.csv is untracked and is deliberately NOT read):
    Data/processed/rebuild/CANONICAL_V3.csv
    Data/wrds/crsp_daily_returns.csv, crsp_daily_topup.csv, crsp_daily_topup_dish.csv
    Data/wrds/market_indices.csv
    outputs/rebuild/constants_v3.json
    outputs/rebuild/appendix_v3/table_3.csv, table_4.csv
    outputs/tables/essay2_v2/t1_final_sample.csv, t2_descriptives_by_treatment.csv,
        t26_inference_ladder.csv, t28_design_resolution.csv
    outputs/essay3_v4/constants_essay3_v4.json, f1_ladder.csv, f1_se_diagnostics.csv

Market cap comes from crsp_daily_returns.csv only (the top-up files carry ret, not prc/shrout);
coverage is computed and logged, not assumed.

Duplicate-row diagnostic (section 3): the top-up files repeat 405 permno-dates already present
in crsp_daily_returns.csv (identical ret). Until 2026-10-02 scripts/155 summed its windows
positionally over the concatenated panel, so events whose 31-row window touched those dates
summed duplicated rows. FIXED 2026-10-02: every consumer now loads through the shared
de-duplicating loader (scripts/254). This script reads the same de-duplicated panel, so its
exhibits match the regenerated car_30d and table_3. Exhibit E1_dup_diagnostic records the
defect: the raw duplicate count, the affected events identified two independent ways, and
each one's pre-fix (double-counted) CAR beside the committed, fixed one.
"""
import itertools
import json
import subprocess
import sys
from datetime import timedelta
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs' / 'defense_supplement'

INPUTS = {
    'canon': 'Data/processed/rebuild/CANONICAL_V3.csv',
    'crsp': 'Data/wrds/crsp_daily_returns.csv',
    'top1': 'Data/wrds/crsp_daily_topup.csv',
    'top2': 'Data/wrds/crsp_daily_topup_dish.csv',
    'mkt': 'Data/wrds/market_indices.csv',
    'c1': 'outputs/rebuild/constants_v3.json',
    't3': 'outputs/rebuild/appendix_v3/table_3.csv',
    't4': 'outputs/rebuild/appendix_v3/table_4.csv',
    'e2s': 'outputs/tables/essay2_v2/t1_final_sample.csv',
    'e2d': 'outputs/tables/essay2_v2/t2_descriptives_by_treatment.csv',
    'e2l': 'outputs/tables/essay2_v2/t26_inference_ladder.csv',
    'e2r': 'outputs/tables/essay2_v2/t28_design_resolution.csv',
    'c3': 'outputs/essay3_v4/constants_essay3_v4.json',
    'f1': 'outputs/essay3_v4/f1_ladder.csv',
    'f1d': 'outputs/essay3_v4/f1_se_diagnostics.csv',
}

LOG = []


def log(msg=''):
    print(msg)
    LOG.append(str(msg))


def stop(msg):
    log(f'STOP: {msg} Nothing written.')
    sys.exit(1)


ASSERTS = []  # (name, got, ref, tol, |diff|/tol, why)

H4 = 5e-5    # half a unit at 4 dp (committed rounding of constants/f1/t26/t28/t2)
H3 = 5e-4    # half a unit at 3 dp (appendix table_3)
H2 = 5e-3    # half a unit at 2 dp
EPS = 1e-9   # float slack


def prop(f, xs, hs):
    """Worst-case |f(corner) - f(xs)| over every corner of the box xs +/- hs (input rounding)."""
    f0 = f(*xs)
    return max(abs(f(*[x + s * h for x, s, h in zip(xs, signs, hs)]) - f0)
               for signs in itertools.product((-1, 1), repeat=len(xs)))


def check(name, got, ref, tol, why):
    got, ref = float(got), float(ref)
    diff = abs(got - ref)
    ratio = diff / tol if tol else (0.0 if diff == 0 else np.inf)
    ok = bool(diff <= tol)
    ASSERTS.append((name, got, ref, tol, ratio, why))
    log(f"  {'PASS' if ok else 'FAIL'}  {name}: got {got:.10g}, ref {ref:.10g} +/- {tol:.3g} "
        f"(|diff|/tol = {ratio:.3f}) [{why}]")
    if not ok:
        stop(f'assert failed on {name}.')


def eq(name, got, ref, why='exact'):
    ok = got == ref
    ASSERTS.append((name, got, ref, 0, 0.0, why))
    log(f"  {'PASS' if ok else 'FAIL'}  {name}: got {got}, ref {ref} (exact) [{why}]")
    if not ok:
        stop(f'assert failed on {name}.')


def true(name, cond, why):
    ok = bool(cond)
    ASSERTS.append((name, ok, True, 0, 0.0, why))
    log(f"  {'PASS' if ok else 'FAIL'}  {name} [{why}]")
    if not ok:
        stop(f'assert failed on {name}.')


ROWS = []


def emit(exhibit, key, value, unit, sample, n, formula, source):
    ROWS.append(dict(exhibit=exhibit, key=key, value=value, unit=unit, sample=sample, n=n,
                     formula=formula, source=source))


# ---------------------------------------------------------------- 0. inputs are tracked
log('== 0. inputs are git-tracked ==')
tracked = set(subprocess.run(['git', 'ls-files', *INPUTS.values()], cwd=ROOT, capture_output=True,
                             text=True, check=True).stdout.split())
for k, p in INPUTS.items():
    if p not in tracked:
        stop(f'input {p} is not git-tracked.')
    head = (ROOT / p).read_bytes()[:64]
    if head.startswith(b'version https://git-lfs'):
        stop(f'input {p} is an LFS pointer, not data.')
log(f'  all {len(INPUTS)} inputs tracked and materialised')


def rd(k, **kw):
    return pd.read_csv(ROOT / INPUTS[k], **kw)


C1 = json.loads((ROOT / INPUTS['c1']).read_text())
C3 = json.loads((ROOT / INPUTS['c3']).read_text())

# ---------------------------------------------------------------- 1. sample asserts
log('== 1. sample asserts ==')
ev = rd('canon', low_memory=False)
ev['bdt'] = pd.to_datetime(ev['breach_date'])
COV = ['fcc_form499', 'immediate_disclosure', 'prior_breaches_1yr', 'health_breach',
       'firm_size_log', 'leverage', 'roa']
reg = ev[ev.has_crsp_data == 1].dropna(subset=['car_30d'] + COV).copy()
eq('E1 constants N_regression', C1['N_regression'], 340, 'author-mandated sample')
eq('E1 constants treated_regression', C1['treated_regression'], 106, 'author-mandated sample')
eq('E1 rebuilt filter N == constants', len(reg), C1['N_regression'])
eq('E1 rebuilt filter treated == constants', int(reg.fcc_form499.sum()), C1['treated_regression'])
eq('E1 rebuilt treated parent CIKs == constants',
   int(reg.loc[reg.fcc_form499 == 1, 'final_cik'].nunique()), C1['treated_parent_ciks_regression'])
N1, T1 = len(reg), int(reg.fcc_form499.sum())

e2 = rd('e2s', low_memory=False)
eq('E2 N', len(e2), 333, 'author-mandated sample')
eq('E2 treated', int(e2.fcc_form499.sum()), 104, 'author-mandated sample')
eq('E2 G (parent CIKs)', int(e2.final_cik.nunique()), 82, 'author-mandated sample')
eq('E2 G1 (treated parent CIKs)', int(e2.loc[e2.fcc_form499 == 1, 'final_cik'].nunique()), 12,
   'author-mandated sample')
e2d = rd('e2d').set_index('variable')
eq('E2 t2 n_treated == t1 treated', int(e2d.loc['e2_pre_sd', 'n_treated']), int(e2.fcc_form499.sum()))
eq('E2 t2 n_control == t1 control', int(e2d.loc['e2_pre_sd', 'n_control']), int((e2.fcc_form499 == 0).sum()))
G2 = int(e2.final_cik.nunique())

f1 = rd('f1').set_index('window')
f1d = rd('f1d').set_index('window')
eq('E3 constants N', C3['N'], 405, 'author-mandated sample')
eq('E3 constants treated', C3['treated'], 109, 'author-mandated sample')
eq('E3 constants G', C3['parent_ciks'], 119, 'author-mandated sample')
eq('E3 constants G1', C3['treated_parent_ciks'], 13, 'author-mandated sample')
for w in (30, 90, 180):
    eq(f'E3 f1_ladder w{w} n/G/G1 == constants', tuple(int(x) for x in f1.loc[w, ['n', 'G', 'G1']]),
       (C3['N'], C3['parent_ciks'], C3['treated_parent_ciks']))
    eq(f'E3 f1_se_diagnostics w{w} treated_n/control_n == constants',
       (int(f1d.loc[w, 'treated_n']), int(f1d.loc[w, 'control_n'])), (C3['treated'], C3['control']))
N3, T3, G3 = C3['N'], C3['treated'], C3['parent_ciks']
S1 = f'E1 regression N={N1} ({T1} treated)'
S2 = f'E2 analytical N={len(e2)} ({int(e2.fcc_form499.sum())} treated; G={G2}, G1=12)'
S3 = f'E3 v4 N={N3} ({T3} treated; G={G3}, G1=13)'

# ---------------------------------------------------------------- 2. E1/E3 90% CIs (D1)
log('== 2. 90% CIs (D1) ==')
t4 = rd('t4')
t4 = t4[t4.Variable != 'CAPTION'].set_index('Variable')
z90 = stats.norm.ppf(0.95)
z95 = stats.norm.ppf(0.975)
check('z90 defines Phi=0.95', stats.norm.cdf(z90), 0.95, 1e-12, 'quantile inversion')
HYP = {'H1_timing': 'immediate_disclosure', 'H2_FCC': 'fcc_form499',
       'H3_prior': 'prior_breaches_1yr', 'H4_health': 'health_breach'}
EQ = 2.10                       # TOST bound, scripts/158 EQ; verified below against committed TOST p
DOF1 = N1 - len(t4)             # residual df of the 158 OLS (const + 7 regressors)
ci90 = {}
for h, var in HYP.items():
    b = C1[f'{h}_coef']
    se = float(t4.loc[var, 'SE'])
    check(f'{h} coef constants == table_4', b, float(t4.loc[var, 'Coef']), EPS, 'same 4-dp value in two committed files')
    check(f'{h} p constants == table_4', C1[f'{h}_p'], float(t4.loc[var, 'p']), EPS, 'same 4-dp value in two committed files')
    lo95, hi95 = C1[f'{h}_ci']
    tol = H4 + prop(lambda b_, s_: b_ - z95 * s_, (b, se), (H4, H4)) + EPS
    check(f'{h} committed 95% lo == coef - z.975*SE', b - z95 * se, lo95, tol,
          'CI at 4 dp; coef, SE at 4 dp propagated')
    check(f'{h} committed 95% hi == coef + z.975*SE', b + z95 * se, hi95, tol,
          'CI at 4 dp; coef, SE at 4 dp propagated')

    def tost(b_, s_):
        return max(stats.t.sf((b_ + EQ) / s_, DOF1), stats.t.cdf((b_ - EQ) / s_, DOF1))
    check(f'{h} committed TOST p reproduced at bound {EQ}', tost(b, se), C1[f'{h}_tost_p'],
          H4 + prop(tost, (b, se), (H4, H4)) + EPS, f'verifies the 2.10 bound; t({DOF1}); p at 4 dp')
    check(f'{h} committed mde80 == 2.8*SE', 2.8 * se, C1[f'{h}_mde80'], H4 + 2.8 * H4 + EPS,
          'mde80 at 4 dp; SE at 4 dp propagated')
    lo, hi = b - z90 * se, b + z90 * se
    c95, hw95 = (lo95 + hi95) / 2, (hi95 - lo95) / 2
    tol90 = (H4 + z90 * H4) + H4 * (1 + z90 / z95) + EPS
    check(f'{h} 90% lo == from committed 95% CI (center - hw*z.95/z.975)', lo, c95 - hw95 * z90 / z95, tol90,
          'two paths; coef/SE and CI endpoints at 4 dp propagated')
    check(f'{h} 90% hi == from committed 95% CI (center + hw*z.95/z.975)', hi, c95 + hw95 * z90 / z95, tol90,
          'two paths; coef/SE and CI endpoints at 4 dp propagated')
    true(f'{h} 90% CI strictly inside committed 95% CI', lo95 < lo < b < hi < hi95, 'nesting invariant')
    check(f'{h} 90% CI symmetric about coef', (lo + hi) / 2, b, 1e-12, 'symmetry invariant')
    ci90[h] = (lo, hi)
    for k, v in (('coef', b), ('se_hc3', se), ('ci90_lo', lo), ('ci90_hi', hi)):
        emit('E1_ci90_essay1', f'{h}_{k}', round(v, 6), 'pp of 30d CAR', S1, N1,
             'coef +/- z(.95)*HC3 SE, z=1.644854 (158 conf_int convention: normal)',
             f"{INPUTS['c1']}; {INPUTS['t4']}")

df3 = int(f1.loc[30, 'G']) - 1
t3_90, t3_95, t3_80 = stats.t.ppf(0.95, df3), stats.t.ppf(0.975, df3), stats.t.ppf(0.8, df3)
for w in (30, 90, 180):
    row = f1.loc[w]
    for col in ('coef', 'se_cv3', 'ci_cv3_lo', 'ci_cv3_hi', 'mde80_cv3', 'treated_mean', 'control_mean'):
        check(f'E3 w{w} {col} f1_ladder == constants_essay3_v4', row[col], C3[f'F1_{w}_{col}'], 1e-12,
              'same 4-dp value in two committed files')
    for col in ('coef', 'se_hc3', 'se_cv1', 'se_cv3'):
        check(f'E3 w{w} {col} f1_ladder == f1_se_diagnostics', row[col], f1d.loc[w, col], EPS,
              'same 4-dp value in two committed files')
    b, se = float(row.coef), float(row.se_cv3)
    tol = H4 + prop(lambda b_, s_: b_ - t3_95 * s_, (b, se), (H4, H4)) + EPS
    check(f'E3 w{w} committed CV3 95% lo == coef - t(.975,{df3})*se_cv3', b - t3_95 * se, row.ci_cv3_lo, tol,
          'CI at 4 dp; coef, SE at 4 dp propagated')
    check(f'E3 w{w} committed CV3 95% hi == coef + t(.975,{df3})*se_cv3', b + t3_95 * se, row.ci_cv3_hi, tol,
          'CI at 4 dp; coef, SE at 4 dp propagated')
    lo, hi = b - t3_90 * se, b + t3_90 * se
    lo95, hi95 = float(row.ci_cv3_lo), float(row.ci_cv3_hi)
    c95, hw95 = (lo95 + hi95) / 2, (hi95 - lo95) / 2
    tol90 = (H4 + t3_90 * H4) + H4 * (1 + t3_90 / t3_95) + EPS
    check(f'E3 w{w} 90% lo == from committed 95% CI', lo, c95 - hw95 * t3_90 / t3_95, tol90,
          'two paths; coef/SE and CI endpoints at 4 dp propagated')
    check(f'E3 w{w} 90% hi == from committed 95% CI', hi, c95 + hw95 * t3_90 / t3_95, tol90,
          'two paths; coef/SE and CI endpoints at 4 dp propagated')
    true(f'E3 w{w} 90% CI strictly inside committed 95% CI', lo95 < lo < b < hi < hi95, 'nesting invariant')
    check(f'E3 w{w} 90% CI symmetric about coef', (lo + hi) / 2, b, 1e-12, 'symmetry invariant')
    lo, hi = 100 * lo, 100 * hi
    for k, v in (('coef', 100 * b), ('se_cv3', 100 * se), ('ci90_lo', lo), ('ci90_hi', hi)):
        emit('E1_ci90_essay3', f'w{w}_{k}', round(v, 6), 'pp (exec departure probability)', S3, N3,
             f'coef +/- t(.95, G-1={df3})*CV3 SE (227 convention), x100', INPUTS['f1'])

# ---------------------------------------------------------------- 3. CRSP ARs + mcap (D2)
log('== 3. CRSP ARs, anchor check, market cap (D2) ==')
main = rd('crsp', usecols=['permno', 'date', 'ret', 'prc', 'shrout'])
main['date'] = pd.to_datetime(main.date)
tops = pd.concat([rd('top1', usecols=['permno', 'date', 'ret']),
                  rd('top2', usecols=['permno', 'date', 'ret'])], ignore_index=True)
tops['date'] = pd.to_datetime(tops.date)
eq('main CRSP file has no duplicate permno-date', int(main.duplicated(['permno', 'date']).sum()), 0)
# raw = the pre-fix concatenation (diagnostic only); d = the shared de-duplicated loader (scripts/254).
raw = pd.concat([main, tops], ignore_index=True)
import importlib.util as _ilu
_s = _ilu.spec_from_file_location('crsp_daily', 'scripts/254_crsp_daily.py')
crsp_daily = _ilu.module_from_spec(_s)
_s.loader.exec_module(crsp_daily)
d = crsp_daily.load(['permno', 'date', 'ret'], verbose=False)
d['date'] = pd.to_datetime(d.date)
d['ret'] = pd.to_numeric(d.ret, errors='coerce')
eq('loader drops exactly the raw duplicates', len(raw) - len(d),
   int(raw.duplicated(['permno', 'date']).sum()))
m = rd('mkt', usecols=['date', 'vwretd'])
m['date'] = pd.to_datetime(m.date)
CAL = pd.DatetimeIndex(m.date.sort_values().unique())
d = d.merge(m, on='date', how='left')
d['ar'] = (d.ret - d.vwretd) * 100
raw = raw.merge(m, on='date', how='left')
raw['ar'] = (raw.ret - raw.vwretd) * 100
dupmask = raw.duplicated(['permno', 'date'], keep=False)
dd_spread = raw[dupmask].groupby(['permno', 'date']).ret.agg(lambda s: s.max() - s.min())
check('duplicated permno-dates carry identical ret', float(dd_spread.abs().max()) if len(dd_spread) else 0.0,
      0.0, 0.0, 'duplicates are copies, so only the positional window is affected')
n_dup_rows = int(raw.duplicated(['permno', 'date']).sum())
log(f'  NOTE  {n_dup_rows} top-up rows duplicate a main-file permno-date '
    f'(permnos {sorted(raw.loc[dupmask, "permno"].astype(int).unique().tolist())}); removed by the shared '
    'loader, see E1_dup_diagnostic')
# scripts/155 convention: positional window over the (now de-duplicated) panel.
pg = {p: g.sort_values('date', kind='mergesort').reset_index(drop=True) for p, g in d.groupby('permno')}
pgr = {p: g.sort_values('date', kind='mergesort').reset_index(drop=True) for p, g in raw.groupby('permno')}
dupdates = {p: set(g.date[g.date.duplicated()]) for p, g in pgr.items()}

recs, caar_rows = [], []
for i, r in reg.iterrows():
    g = pg[int(r.permno)]
    w = g[(g.date >= r.bdt - timedelta(days=50)) & (g.date <= r.bdt + timedelta(days=50))].reset_index(drop=True)
    pos = (w.date - r.bdt).abs().idxmin()
    d0 = w.date[pos]
    win = w.iloc[pos:min(len(w) - 1, pos + 30) + 1]
    car, car5 = win.ar.sum(), w.iloc[pos:min(len(w) - 1, pos + 5) + 1].ar.sum()
    # pre-fix value: the same positional rule over the RAW (duplicated) panel
    gr = pgr[int(r.permno)]
    wr = gr[(gr.date >= r.bdt - timedelta(days=50)) & (gr.date <= r.bdt + timedelta(days=50))].reset_index(drop=True)
    pr = (wr.date - r.bdt).abs().idxmin()
    winr = wr.iloc[pr:min(len(wr) - 1, pr + 30) + 1]
    touches_dup = bool(set(winr.date) & dupdates[int(r.permno)])
    recs.append(dict(idx=i, day0=d0, car_chk=car, car5_chk=car5, car_prefix=winr.ar.sum(),
                     touches_dup=touches_dup))
    p0 = g.index[g.date == d0][0]
    for k in range(-10, 31):
        if 0 <= p0 + k < len(g):
            caar_rows.append((i, int(r.fcc_form499), k, g.ar.iloc[p0 + k]))
reg = reg.join(pd.DataFrame(recs).set_index('idx'))
check(f'E1 anchor: max |re-summed CAR(0,30) - committed car_30d| over {N1}',
      float((reg.car_chk - reg.car_30d).abs().max()), 0.0, EPS, 'car_30d stored at 4 dp of a 4-dp-ret sum')
check(f'E1 anchor: max |re-summed CAR(0,5) - committed car_5d| over {N1}',
      float((reg.car5_chk - reg.car_5d).abs().max()), 0.0, EPS, 'car_5d stored at 4 dp of a 4-dp-ret sum')

# Duplicate diagnostic: affected events identified two independent ways must coincide.
aff_val = set(reg.index[(reg.car_prefix - reg.car_30d).abs() > EPS])
aff_win = set(reg.index[reg.touches_dup])
eq('dup diagnostic: events whose pre-fix CAR differs == events whose raw window touches a duplicate',
   sorted(aff_val), sorted(aff_win), 'two independent definitions')
log(f'  NOTE  {len(aff_val)} of {N1} car_30d values summed duplicated rows before the 2026-10-02 fix')
srcd = f"{INPUTS['canon']}; {INPUTS['crsp']}; {INPUTS['top1']}; {INPUTS['top2']}; {INPUTS['mkt']}"
emit('E1_dup_diagnostic', 'n_duplicate_rows', n_dup_rows, 'rows', 'CRSP concat', n_dup_rows,
     'top-up rows whose permno-date already exists in crsp_daily_returns.csv', srcd)
emit('E1_dup_diagnostic', 'n_events_affected', len(aff_val), 'events', S1, N1,
     'events whose pre-fix 31-row window summed duplicated rows', srcd)
for i in sorted(aff_val):
    r = reg.loc[i]
    tag = f"{int(r.permno)}_{str(r.breach_date)[:10]}"
    emit('E1_dup_diagnostic', f'{tag}_car_30d_prefix', round(float(r.car_prefix), 6), 'pp', S1, 1,
         'pre-fix car_30d: 31-row positional window over the duplicated raw panel', srcd)
    emit('E1_dup_diagnostic', f'{tag}_car_30d_committed', round(float(r.car_30d), 6), 'pp', S1, 1,
         f'committed (fixed) car_30d ({r.org_name}; fcc_form499={int(r.fcc_form499)})', INPUTS['canon'])
    log(f'    {r.org_name} {str(r.breach_date)[:10]} (permno {int(r.permno)}, t={int(r.fcc_form499)}): '
        f'pre-fix {r.car_prefix:+.4f} -> committed {r.car_30d:+.4f}')

# Market cap: path A = per-permno groups of the main file, last row before day 0;
# path B = pd.merge_asof on the main file (strictly before day 0). Must agree event by event.
mg = {p: g.sort_values('date').reset_index(drop=True) for p, g in main.groupby('permno')}
mcA, mdate = [], []
for i, r in reg.iterrows():
    g = mg.get(int(r.permno))
    pre = g[g.date < r.day0].tail(1) if g is not None else g
    if g is not None and len(pre) and pd.notna(pre.prc.iloc[0]) and pd.notna(pre.shrout.iloc[0]):
        mcA.append(abs(pre.prc.iloc[0]) * pre.shrout.iloc[0] * 1000)
        mdate.append(pre.date.iloc[0])
    else:
        mcA.append(np.nan)
        mdate.append(pd.NaT)
reg['mcap'], reg['mcap_date'] = mcA, mdate
q = reg[['permno', 'day0']].reset_index().assign(permno=lambda x: x.permno.astype(int)).sort_values('day0')
mb = pd.merge_asof(q, main.assign(permno=main.permno.astype(int)).sort_values('date')[['permno', 'date', 'prc', 'shrout']],
                   left_on='day0', right_on='date', by='permno', direction='backward', allow_exact_matches=False)
reg['mcap_B'] = (mb.set_index('index').eval('abs(prc) * shrout * 1000')).reindex(reg.index)
eq('mcap path A vs B: same events covered', sorted(reg.index[reg.mcap.notna()]), sorted(reg.index[reg.mcap_B.notna()]),
   'two independent lookups')
check('mcap path A vs B: max relative diff', float(((reg.mcap - reg.mcap_B).abs() / reg.mcap).max()), 0.0, 1e-12,
      'two independent lookups on the same rows')
prev_td = reg.day0.map(lambda x: CAL[CAL.get_loc(x) - 1])
stale = reg.mcap.notna() & (reg.mcap_date != prev_td)
eq('mcap price date == previous market trading day for every covered event', int(stale.sum()), 0,
   'no stale prices (market_indices calendar)')
for lab, s in (('all', reg), ('treated', reg[reg.fcc_form499 == 1]), ('control', reg[reg.fcc_form499 == 0])):
    mc = s.mcap.dropna() / 1e9
    eq(f'mcap {lab}: covered + missing == group N', len(mc) + int(s.mcap.isna().sum()), len(s))
    check(f'mcap {lab} median path A == path B', mc.median(), s.mcap_B.median() / 1e9, EPS, 'two paths')
    check(f'mcap {lab} mean path A == path B', mc.mean(), s.mcap_B.mean() / 1e9, EPS, 'two paths')
    log(f'    {lab}: covered {len(mc)} of {len(s)}; median ${mc.median():.4f}B; mean ${mc.mean():.4f}B')
    src = f"{INPUTS['canon']}; {INPUTS['crsp']} (prc, shrout)"
    f = '|prc| x shrout x 1000 on last trading day before scripts/155 day 0'
    emit('E1_dollar', f'mcap_{lab}_n_covered', len(mc), 'events', S1, len(s), f, src)
    emit('E1_dollar', f'mcap_{lab}_n_missing', int(s.mcap.isna().sum()), 'events', S1, len(s), f, src)
    emit('E1_dollar', f'mcap_{lab}_median', round(mc.median(), 6), '$B', S1, len(mc), f, src)
    emit('E1_dollar', f'mcap_{lab}_mean', round(mc.mean(), 6), '$B', S1, len(mc), f, src)
miss_t = reg[(reg.fcc_form499 == 1) & reg.mcap.isna()]
log(f'    treated without mcap: {len(miss_t)} events: '
    + '; '.join(f'{o} x{n}' for o, n in miss_t.org_name.value_counts().items()))

med = reg.mcap.median()  # dollars, path A
med_B = reg.mcap_B.median()
n_mc = int(reg.mcap.notna().sum())
DOLLAR = [('tost_bound_pos', EQ), ('tost_bound_neg', -EQ),
          ('H1_coef', C1['H1_timing_coef']),
          ('H1_ci95_lo', C1['H1_timing_ci'][0]), ('H1_ci95_hi', C1['H1_timing_ci'][1]),
          ('H1_ci90_lo', ci90['H1_timing'][0]), ('H1_ci90_hi', ci90['H1_timing'][1]),
          ('H2_coef', C1['H2_FCC_coef']),
          ('H2_ci95_lo', C1['H2_FCC_ci'][0]), ('H2_ci95_hi', C1['H2_FCC_ci'][1]),
          ('H2_ci90_lo', ci90['H2_FCC'][0]), ('H2_ci90_hi', ci90['H2_FCC'][1])]
USD = {}
for key, pp in DOLLAR:
    usd_m = pp / 100 * med / 1e6
    check(f'dollar {key} $M: pp/100 x median(A) == pp x median(B)/1e8', usd_m, pp * med_B / 1e8, 1e-9 * max(1, abs(usd_m)),
          'identity, two mcap paths (no committed counterpart)')
    USD[key] = usd_m
    emit('E1_dollar', f'{key}_at_median_mcap', round(usd_m, 4), '$M', S1, n_mc,
         f'pp/100 x N={N1} median mcap ({med / 1e6:.2f} $M); pp = {pp:.6g}',
         f"{INPUTS['c1']}; {INPUTS['crsp']}")
check('dollar TOST bounds symmetric', USD['tost_bound_pos'] + USD['tost_bound_neg'], 0.0, 1e-9, 'symmetry invariant')
for hh in ('H1', 'H2'):
    true(f'dollar {hh} 90% CI strictly inside dollar 95% CI',
         USD[f'{hh}_ci95_lo'] < USD[f'{hh}_ci90_lo'] < USD[f'{hh}_coef'] < USD[f'{hh}_ci90_hi'] < USD[f'{hh}_ci95_hi'],
         'nesting invariant')
tmed = reg.loc[reg.fcc_form499 == 1, 'mcap'].median()
n_tmc = int(reg.loc[reg.fcc_form499 == 1, 'mcap'].notna().sum())
tval = EQ / 100 * tmed / 1e9
check('TOST bound at treated median $B: path A == path B', tval,
      EQ / 100 * reg.loc[reg.fcc_form499 == 1, 'mcap_B'].median() / 1e9, EPS, 'identity, two mcap paths')
emit('E1_dollar', 'tost_bound_at_treated_median_mcap', round(tval, 6), '$B', S1, n_tmc,
     f'2.10/100 x treated median mcap ({n_tmc} of {T1} covered)', INPUTS['crsp'])

# ---------------------------------------------------------------- 4. E2 volatility scaling (D3)
log('== 4. Essay 2 volatility scaling (D3) ==')
lad = rd('e2l')
cv3 = lad[lad.procedure.str.startswith('CV3')].iloc[0]
e2r = rd('e2r').iloc[0]
eq('E2 t26 one coef across all procedures', lad.coef.nunique(), 1, 'one estimate, several SEs')
b2, se2 = float(cv3.coef), float(cv3.se)
df2 = G2 - 1
t2_95, t2_90, t2_80 = stats.t.ppf(0.975, df2), stats.t.ppf(0.95, df2), stats.t.ppf(0.8, df2)
tol = H4 + prop(lambda b_, s_: b_ - t2_95 * s_, (b2, se2), (H4, H4)) + EPS
check(f'E2 t26 CV3 95% lo == coef - t(.975,{df2})*se', b2 - t2_95 * se2, cv3.ci_lo, tol, 'CI at 4 dp; inputs at 4 dp')
check(f'E2 t26 CV3 95% hi == coef + t(.975,{df2})*se', b2 + t2_95 * se2, cv3.ci_hi, tol, 'CI at 4 dp; inputs at 4 dp')
tol = H4 + prop(lambda b_, s_: b_ - t2_90 * s_, (b2, se2), (H4, H4)) + EPS
check(f'E2 t28 ci90_lo == t26 coef - t(.95,{df2})*se_cv3', b2 - t2_90 * se2, e2r.ci90_lo, tol, 'two committed files; 4 dp')
check(f'E2 t28 ci90_hi == t26 coef + t(.95,{df2})*se_cv3', b2 + t2_90 * se2, e2r.ci90_hi, tol, 'two committed files; 4 dp')
mde = float(e2r.mde_daily)
check(f'E2 t28 mde_daily == (t.975+t.8)({df2}) x t26 se_cv3', (t2_95 + t2_80) * se2, mde,
      H4 + (t2_95 + t2_80) * H4 + EPS, 'two committed files; 4 dp')
check('E2 t28 mde_annualized == mde_daily x sqrt(252)', mde * np.sqrt(252), e2r.mde_annualized,
      H2 + np.sqrt(252) * H4 + EPS, 'annualized at 2 dp; daily at 4 dp')
pre_t2 = float(e2d.loc['e2_pre_sd', 'mean_pooled'])
pre = float(e2['e2_pre_sd'].mean())                         # full precision, t1 sample
pre_c = float(e2.loc[e2.fcc_form499 == 0, 'e2_pre_sd'].mean())
check('E2 t2 e2_pre_sd mean_pooled == t1 mean', pre, pre_t2, H4 + EPS, 't2 at 4 dp')
check('E2 t2 e2_pre_sd mean_control == t1 control mean', pre_c, e2d.loc['e2_pre_sd', 'mean_control'], H4 + EPS, 't2 at 4 dp')
check('E2 t2 e2_pre_sd mean_treated == t1 treated mean', e2.loc[e2.fcc_form499 == 1, 'e2_pre_sd'].mean(),
      e2d.loc['e2_pre_sd', 'mean_treated'], H4 + EPS, 't2 at 4 dp')
check('E2 t2 e2_pre_sd sd_pooled == t1 sd (ddof=1)', e2['e2_pre_sd'].std(), e2d.loc['e2_pre_sd', 'sd_pooled'], H4 + EPS,
      't2 at 4 dp')
PCT = {}
for key, num in (('coef_pct_of_pre_sd', b2), ('cv3_ci_lo_pct', float(cv3.ci_lo)), ('cv3_ci_hi_pct', float(cv3.ci_hi)),
                 ('mde_pct_of_pre_sd', mde), ('sesoi_pct_of_pre_sd', float(e2r.sesoi_daily))):
    v = num / pre * 100
    check(f'E2 {key}: t1 full-precision denominator vs t2 committed denominator', v, num / pre_t2 * 100,
          abs(num) * 100 * H4 / (pre_t2 - H4) / pre_t2 + EPS, 'two denominators; t2 at 4 dp propagated')
    PCT[key] = v
    emit('E2_vol_scaling', key, round(v, 6), '% of mean pooled pre-window daily vol', S2, len(e2),
         f'{num} / e2_pre_sd pooled mean (t1, full precision {pre:.6f}) x 100',
         f"{INPUTS['e2l']}; {INPUTS['e2r']}; {INPUTS['e2s']}")
true('E2 pct CI brackets pct coef', PCT['cv3_ci_lo_pct'] < PCT['coef_pct_of_pre_sd'] < PCT['cv3_ci_hi_pct'], 'nesting invariant')
v_ctrl = b2 / pre_c * 100
emit('E2_vol_scaling', 'coef_pct_of_control_pre_sd', round(v_ctrl, 6), '% of control pre-window daily vol',
     S2, int((e2.fcc_form499 == 0).sum()), f'coef / e2_pre_sd control mean (t1, full precision {pre_c:.6f}) x 100',
     f"{INPUTS['e2l']}; {INPUTS['e2s']}")
for key, v, u in (('coef', b2, 'daily pp'), ('cv3_p', float(cv3.p), 'p'),
                  ('mde80', mde, 'daily pp'), ('pre_sd_pooled', pre_t2, 'daily pp')):
    emit('E2_vol_scaling', key, v, u, S2, len(e2), 'committed value', f"{INPUTS['e2l']}; {INPUTS['e2r']}; {INPUTS['e2d']}")

# ---------------------------------------------------------------- 5. E3 MDEs as departures (D4)
log('== 5. Essay 3 MDEs as departures (D4) ==')
for w in (30, 90, 180):
    mde3 = float(f1.loc[w, 'mde80_cv3'])
    se3 = float(f1.loc[w, 'se_cv3'])
    check(f'E3 w{w} mde80 f1_ladder == f1_se_diagnostics', mde3, f1d.loc[w, 'mde80'], EPS, 'two committed files')
    check(f'E3 w{w} mde80 == (t.975+t.8)({df3}) x se_cv3', (t3_95 + t3_80) * se3, mde3,
          H4 + (t3_95 + t3_80) * H4 + EPS, 'mde80, se at 4 dp')
    tn, ce, cn, te = (int(f1d.loc[w, c]) for c in ('treated_n', 'control_events', 'control_n', 'treated_events'))
    cm = ce / cn                                             # full precision
    check(f'E3 w{w} control rate events/n == committed control_mean', cm, f1.loc[w, 'control_mean'], H4 + EPS,
          'f1_se_diagnostics counts vs f1_ladder 4-dp mean')
    check(f'E3 w{w} treated rate events/n == committed treated_mean', te / tn, f1.loc[w, 'treated_mean'], H4 + EPS,
          'f1_se_diagnostics counts vs f1_ladder 4-dp mean')
    check(f'E3 w{w} pooled rate == committed y_mean', (te + ce) / (tn + cn), f1d.loc[w, 'y_mean'], H4 + EPS,
          'counts vs 4-dp y_mean')
    extra, trate, ctrl_dep, ratio = mde3 * tn, 100 * (cm + mde3), cm * tn, (cm + mde3) / cm
    check(f'E3 w{w} extra departures == (treated rate - control rate)/100 x treated_n', extra,
          (trate - 100 * cm) / 100 * tn, EPS, 'identity, two paths (no committed counterpart)')
    check(f'E3 w{w} departures at control rate == control_events x treated_n/control_n', ctrl_dep,
          ce * tn / cn, EPS, 'identity, two paths')
    check(f'E3 w{w} rate ratio == implied rate / control rate', ratio, trate / (100 * cm), 1e-12, 'identity, two paths')
    src = f"{INPUTS['f1']}; {INPUTS['f1d']}"
    for key, v, u, fml in (
            ('mde80_pp', 100 * mde3, 'pp', 'committed mde80_cv3 x100'),
            ('extra_departures', extra, f'departures among {tn} treated', f'mde80 x {tn}'),
            ('implied_treated_rate_pct', trate, '%', '(control_events/control_n + mde80) x 100'),
            ('control_rate_pct', 100 * cm, '%', 'control_events/control_n x 100 (full precision)'),
            ('implied_rate_ratio', ratio, 'x', '(control rate + mde80)/control rate, full precision'),
            ('departures_at_control_rate', ctrl_dep, 'departures', f'control_events/control_n x {tn}'),
            ('committed_treated_departures', te, 'departures', 'committed')):
        emit('E3_mde_departures', f'w{w}_{key}', round(v, 6), u, S3, tn, fml, src)

# ---------------------------------------------------------------- 6. T-Mobile (D5)
log('== 6. T-Mobile 2021-08-17 (D5) ==')
tm = reg[(reg.final_cik == 1283699) & (reg.breach_date == '2021-08-17')]
eq('T-Mobile 2021-08-17 rows in E1 sample', len(tm), 1, 'event identifier')
tm = tm.iloc[0]
TMP = int(tm.permno)
true('T-Mobile breach_date is a market trading day and day 0 == breach_date',
     tm.bdt in CAL and tm.day0 == tm.bdt, 'market_indices calendar')
eq('T-Mobile permno has no duplicated rows', len(dupdates[TMP]), 0)
g = pg[TMP]
p0 = g.index[g.date == tm.day0][0]
ww = g.iloc[p0:p0 + 31].copy()
eq('T-Mobile AR rows', len(ww), 31)
eq('T-Mobile 31 AR dates == 31 market trading days from day 0', list(ww.date),
   list(CAL[CAL.get_loc(tm.day0):CAL.get_loc(tm.day0) + 31]), 'market_indices calendar')
# Path B: ARs from the raw main file merged to the index file directly.
rb = main[main.permno == TMP].merge(m, on='date').set_index('date').loc[ww.date]
arB = ((rb.ret - rb.vwretd) * 100).to_numpy()
check('T-Mobile max |AR path A - AR path B| over 31 days', float(np.abs(ww.ar.to_numpy() - arB).max()), 0.0, 1e-12,
      'two paths on the same rows')
ww['day'] = range(31)
ww['cum'] = ww.ar.cumsum()
for k, (_, r) in enumerate(ww.iterrows()):
    emit('E1_tmobile', f'ar_day{k:02d}_{r.date.date()}', round(r.ar, 6), 'pp', 'T-Mobile 2021-08-17', 1,
         '(ret - vwretd) x 100', f"{INPUTS['crsp']}; {INPUTS['mkt']}")
    emit('E1_tmobile', f'cum_day{k:02d}', round(r.cum, 6), 'pp', 'T-Mobile 2021-08-17', 1,
         'cumulative sum of AR from day 0', f"{INPUTS['crsp']}; {INPUTS['mkt']}")
car = float(ww.ar.sum())
check('T-Mobile CAR(0,30) == committed car_30d', car, tm.car_30d, EPS, 'committed 4 dp of a 4-dp-ret sum')
check('T-Mobile cum day 30 == committed car_30d', ww.cum.iloc[30], tm.car_30d, EPS, 'committed')
check('T-Mobile CAR(0,5) == committed car_5d', ww.ar.iloc[:6].sum(), tm.car_5d, EPS, 'committed')
car01 = float(ww.ar.iloc[:2].sum())
check('T-Mobile CAR(0,1) == cum day 1', car01, ww.cum.iloc[1], 1e-12, 'identity (no committed counterpart)')
pre = mg[TMP][mg[TMP].date < tm.day0].tail(1).iloc[0]
eq('T-Mobile mcap date == previous market trading day', pre.date, CAL[CAL.get_loc(tm.day0) - 1], 'market_indices calendar')
mc_tm = abs(pre.prc) * pre.shrout * 1000
check('T-Mobile mcap == event-level mcap (paths A, B)', mc_tm, tm.mcap_B, 1e-6, 'two lookups, dollars')
usd = car / 100 * mc_tm / 1e9
check('T-Mobile dollar CAR: car/100 x mcap == car_30d x |prc| x shrout / 1e8 / 1e9 x 1000', usd,
      float(tm.car_30d) * abs(float(pre.prc)) * float(pre.shrout) * 1000 / 100 / 1e9, 1e-9, 'identity, two paths')
for key, v, u, fml in (('event_date_day0', str(tm.day0.date()), 'date', 'scripts/155 anchor (nearest trading day to breach_date)'),
                       ('reported_date', str(tm.reported_date)[:10], 'date', 'CANONICAL_V3'),
                       ('car_30d', round(car, 6), 'pp', 'sum AR day 0..+30 (== committed car_30d)'),
                       ('car_0_5', round(float(ww.ar.iloc[:6].sum()), 6), 'pp', 'sum AR day 0..+5 (== car_5d)'),
                       ('car_0_1', round(car01, 6), 'pp', 'sum AR day 0..+1'),
                       ('mcap_date', str(pre.date.date()), 'date', 'last trading day before day 0'),
                       ('mcap_prc', float(pre.prc), '$', 'committed prc'),
                       ('mcap_shrout_thousands', float(pre.shrout), 'thousand shares', 'committed shrout'),
                       ('mcap', round(mc_tm / 1e9, 6), '$B', '|prc| x shrout x 1000'),
                       ('dollar_car_30d', round(usd, 6), '$B', 'car_30d/100 x mcap')):
    emit('E1_tmobile', key, v, u, 'T-Mobile 2021-08-17', 1, fml,
         f"{INPUTS['canon']}; {INPUTS['crsp']}; {INPUTS['mkt']}")

# ---------------------------------------------------------------- 7. CAAR (D7)
log('== 7. CAAR -10..+30 by treatment (D7) ==')
A = pd.DataFrame(caar_rows, columns=['idx', 't', 'day', 'ar'])
aar = A.groupby(['t', 'day']).ar.agg(['mean', 'count', 'sum']).reset_index()
t3 = rd('t3')
check('constants car30d_regression_mean == mean committed car_30d', reg.car_30d.mean(),
      C1['car30d_regression_mean'], H4 + EPS, 'constants at 4 dp')
check('constants car30d_regression_median == median committed car_30d', reg.car_30d.median(),
      C1['car30d_regression_median'], H4 + EPS, 'constants at 4 dp')
for t, lab, grp, ck in ((1, 'treated', 'Filer', 'T3_filer_median'), (0, 'control', 'Non-filer', 'T3_nonfiler_median')):
    sub = reg[reg.fcc_form499 == t]
    row3 = t3[(t3.Comparison == 'Form 499') & (t3.Group == grp)].iloc[0]
    eq(f'table_3 {grp} N == sample', int(row3.N), len(sub))
    check(f'table_3 {grp} Mean CAR == mean committed car_30d', sub.car_30d.mean(), row3['Mean CAR'], H3 + EPS, 'table_3 at 3 dp')
    check(f'table_3 {grp} Median CAR == median committed car_30d', sub.car_30d.median(), row3['Median CAR'], H3 + EPS,
          'table_3 at 3 dp')
    check(f'constants {ck} == median committed car_30d', sub.car_30d.median(), C1[ck], H4 + EPS, 'constants at 4 dp')
    s = aar[aar.t == t].sort_values('day').set_index('day')
    s['caar'] = s['mean'].cumsum()
    eq(f'CAAR {lab} days', list(s.index), list(range(-10, 31)))
    n = len(sub)
    post = s.loc[30, 'caar'] - s.loc[-1, 'caar']
    for hi_day, col, nm in ((30, 'car_30d', 'CAR(0,30)'), (5, 'car_5d', 'CAR(0,5)')):
        win = s.loc[0:hi_day]
        caar_post = s.loc[hi_day, 'caar'] - s.loc[-1, 'caar']
        # AAR sum == mean committed CAR + sum over days of (mean over present events - sum/N): exact identity
        recon = sub[col].mean() + float((win['mean'] - win['sum'] / n).sum())
        check(f'CAAR {lab} {nm} reconciles to mean committed {col} (+ missing-AR correction)', caar_post, recon, EPS,
              'identity on committed car; correction is 0 when every event has every AR')
        short = int((win['count'] < n).sum())
        log(f'    {lab} {nm}: CAAR {caar_post:+.6f}; mean committed {col} {sub[col].mean():+.6f}; '
            f'days with fewer than {n} ARs: {short}')
    if int((s.loc[0:30, 'count'] < n).sum()) == 0:
        check(f'CAAR {lab} (30)-(-1) == table_3 {grp} Mean CAR', post, row3['Mean CAR'], H3 + EPS,
              'complete AR panel, so CAAR == mean CAR; table_3 at 3 dp')
    c01 = s.loc[1, 'caar'] - s.loc[-1, 'caar']
    check(f'CAAR {lab} CAR(0,+1) == AAR(0) + AAR(1)', c01, s.loc[0, 'mean'] + s.loc[1, 'mean'], 1e-12,
          'identity (no committed counterpart)')
    for day, r in s.iterrows():
        emit('E1_caar', f'{lab}_day{int(day):+d}_caar', round(r.caar, 6), 'pp', S1, int(r['count']),
             'cumsum from day -10 of mean AR across events at trading day t (scripts/155 day 0)',
             f"{INPUTS['canon']}; {INPUTS['crsp']}; {INPUTS['top1']}; {INPUTS['top2']}; {INPUTS['mkt']}")
        emit('E1_caar', f'{lab}_day{int(day):+d}_aar', round(r['mean'], 6), 'pp', S1, int(r['count']),
             'mean AR across events at trading day t', INPUTS['crsp'])
    emit('E1_caar', f'{lab}_caar30_minus_caarm1', round(post, 6), 'pp', S1, int(s.loc[30, 'count']),
         'CAAR(+30) - CAAR(-1)', f"{INPUTS['t3']} check: {row3['Mean CAR']}")
    emit('E1_caar', f'{lab}_car_0_1', round(c01, 6), 'pp', S1,
         int(s.loc[1, 'count']), 'CAAR(+1) - CAAR(-1)', INPUTS['crsp'])
    emit('E1_caar', f'{lab}_car_0_5', round(s.loc[5, 'caar'] - s.loc[-1, 'caar'], 6), 'pp', S1,
         int(s.loc[5, 'count']), 'CAAR(+5) - CAAR(-1)', INPUTS['crsp'])

# ---------------------------------------------------------------- 8. write
log('== 8. assert summary ==')
nontrivial = sorted([a for a in ASSERTS if a[3] and a[3] >= 1e-5], key=lambda a: -a[4])
log(f'  {len(ASSERTS)} asserts, all PASS. Tightest (largest |diff|/tol) among rounding-tolerance asserts:')
for a in nontrivial[:10]:
    log(f'    {a[0]}: got {a[1]:.8g} vs {a[2]:.8g} tol {a[3]:.3g} -> {a[4]:.3f}')

OUT.mkdir(parents=True, exist_ok=True)
df = pd.DataFrame(ROWS, columns=['exhibit', 'key', 'value', 'unit', 'sample', 'n', 'formula', 'source'])
df.to_csv(OUT / 'deck_exhibits.csv', index=False)
js = {'_meta': {'script': 'scripts/252_defsup_deck_exhibits.py',
                'assert_policy': 'each value checked against an independent committed input or an independent '
                                 'recomputation path; tol = half-unit of committed rounding + input-rounding '
                                 'propagation + 1e-9; identities at 1e-9/1e-12; hard failure, nothing written',
                'n_asserts': len(ASSERTS), 'inputs': list(INPUTS.values()),
                'note': 'Arithmetic only on git-tracked inputs; crsp_quotes_topup.csv (untracked) not used, so '
                        f'treated mcap covers {n_tmc} of {T1} events. {len(aff_val)} car_30d values summed '
                        'duplicated top-up rows before the 2026-10-02 fix (E1_dup_diagnostic).'}}
for ex, g_ in df.groupby('exhibit', sort=False):
    js[ex] = {r.key: {k: r[k] for k in ('value', 'unit', 'sample', 'n', 'formula', 'source')}
              for _, r in g_.iterrows()}
(OUT / 'deck_exhibits.json').write_text(json.dumps(js, indent=2, default=lambda o: o.item() if hasattr(o, 'item') else str(o)))
log(f'  wrote {len(df)} rows -> outputs/defense_supplement/deck_exhibits.csv / .json')
(OUT / 'deck_exhibits.log').write_text('\n'.join(LOG) + '\n', encoding='utf-8')
