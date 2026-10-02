"""
DEFENSE SUPPLEMENT 251 — ESSAY 1: NOTIFICATION-ANCHORED CARs
=============================================================
Re-anchors the Essay 1 event study on the NOTIFICATION date (reported_date)
instead of the breach date, on the frozen Essay 1 regression sample
(CANONICAL_V3; N 340 / 106 treated events / 12 treated parent CIKs).

Return and market series: identical to scripts/155 — Data/wrds/crsp_daily_returns.csv
+ crsp_daily_topup.csv + crsp_daily_topup_dish.csv (permno, date, ret), merged to
Data/wrds/market_indices.csv vwretd; AR = (ret - vwretd) x 100, summed over CRSP
trading days. PERMNO = the committed CANONICAL_V3 permno (155's date-aware mapping).

Correctness check: the breach-anchored (0,+30) CAR is recomputed with 155's exact
convention (trading day NEAREST breach_date within a +/-50 calendar-day pull,
window truncated at the pull edge, NaN ARs skipped) and must reproduce the
committed car_30d; otherwise the script stops.

D1  Market-adjusted CARs, day 0 = first CRSP trading day ON OR AFTER reported_date
    (reported_date must parse and delay_invalid != 1, the signed wrong-field flag
    158 also excludes; day 0 must fall within 10 calendar days of reported_date);
    windows (0,+1), (0,+5), (0,+30). A window is usable only if every trading day
    in it exists with a non-missing AR; otherwise the event is dropped for that
    window only (counted and listed).
D2  Baseline Essay 1 spec (158): CAR ~ fcc_form499 + immediate_disclosure +
    prior_breaches_1yr + health_breach + firm_size_log + leverage + roa, HC3;
    z-based CIs (statsmodels default as in 158); TOST vs +/-2.10pp with
    dof = len(reg) - 7 - 1; MDE80 = 2.8*SE; parent-CIK (final_cik) clustered
    p (statsmodels cov_type='cluster', 158's table_8 'Firm-clustered' row).
    immediate_disclosure kept as committed.
D3  Mean / median CAR by fcc_form499 per window, with n.

Writes ONLY to outputs/defense_supplement/. No random draws.
"""

import sys
from datetime import timedelta
from pathlib import Path
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
OUT = Path('outputs/defense_supplement')
OUT.mkdir(parents=True, exist_ok=True)
L = []


def log(m=''):
    print(m)
    L.append(str(m))


log('=' * 90)
log('251 DEFENSE SUPPLEMENT: ESSAY 1 NOTIFICATION-ANCHORED CARs')
log('=' * 90)

# ---------------- sample (158 definition, frozen) ----------------
ev = pd.read_csv('Data/processed/rebuild/CANONICAL_V3.csv', low_memory=False)
ev['bdt'] = pd.to_datetime(ev['breach_date'])
TREAT = 'fcc_form499'
HVARS = [TREAT, 'immediate_disclosure', 'prior_breaches_1yr', 'health_breach']
CONTROLS = HVARS + ['firm_size_log', 'leverage', 'roa']
crsp_s = ev[ev['has_crsp_data'] == 1]
reg = crsp_s.dropna(subset=['car_30d'] + CONTROLS).copy().reset_index(drop=True)
n_reg = len(reg)
n_tr = int(reg[TREAT].sum())
n_tr_cik = int(reg.loc[reg[TREAT] == 1, 'final_cik'].nunique())
assert n_reg == 340, f'N_regression {n_reg} != 340'
assert n_tr == 106, f'treated events {n_tr} != 106'
assert n_tr_cik == 12, f'treated parent CIKs {n_tr_cik} != 12'
n_clu = reg['final_cik'].nunique()
log(f'Sample assert PASS: Essay 1 regression sample N={n_reg}; treated {n_tr} events / '
    f'{n_tr_cik} parent CIKs; {n_clu} parent-CIK clusters')

# ---------------- return / market series (155) ----------------
import importlib.util as _ilu
_s = _ilu.spec_from_file_location('crsp_daily', 'scripts/254_crsp_daily.py')
crsp_daily = _ilu.module_from_spec(_s); _s.loader.exec_module(crsp_daily)
# De-duplicated on (permno, date) by the shared loader (2026-10-02): the top-ups repeat
# 405 permno-dates already in the main file, which positional windows double-counted.
crsp = crsp_daily.load(['permno', 'date', 'ret'])
log('  main CRSP file + both top-ups, de-duplicated on (permno, date) (scripts/254)')
mkt = pd.read_csv('Data/wrds/market_indices.csv', usecols=['date', 'vwretd'])
crsp['date'] = pd.to_datetime(crsp['date'])
mkt['date'] = pd.to_datetime(mkt['date'])
crsp = crsp.merge(mkt, on='date', how='left')
crsp['ar'] = (crsp['ret'] - crsp['vwretd']) * 100
pg = {p: g.sort_values('date').reset_index(drop=True) for p, g in crsp.groupby('permno')}


def car_breach_155(permno, bdt):
    """Exact 155 convention for car_30d."""
    g = pg.get(permno)
    if g is None:
        return np.nan
    w = g[(g['date'] >= bdt - timedelta(days=50)) & (g['date'] <= bdt + timedelta(days=50))].reset_index(drop=True)
    if len(w) < 10:
        return np.nan
    pos = (w['date'] - bdt).abs().idxmin()
    p5, p30 = min(len(w) - 1, pos + 5), min(len(w) - 1, pos + 30)
    if p5 <= pos:
        return np.nan
    return round(w.iloc[pos:p30 + 1]['ar'].sum(), 4)


# ---------------- reproduction check ----------------
reg['car30_recomp'] = [car_breach_155(int(r['permno']), r['bdt']) for _, r in reg.iterrows()]
diff = (reg['car30_recomp'] - reg['car_30d']).abs()
n_nan = int(reg['car30_recomp'].isna().sum())
maxd = float(diff.max())
n_off = int((diff > 1e-3).sum())
log(f'\nReproduction check (breach-anchored (0,+30), 155 convention) on N={n_reg}: '
    f'max |diff| = {maxd:.6f} pp; events with |diff|>0.001: {n_off}; recompute NaN: {n_nan}')
if n_nan > 0 or maxd > 1e-3:
    log('REPRODUCTION FAILED — stopping before estimation.')
    for _, r in reg[(diff > 1e-3) | reg['car30_recomp'].isna()].iterrows():
        log(f"  {r['org_name']} | {r['breach_date']} | permno {r['permno']} | "
            f"committed {r['car_30d']} recomputed {r['car30_recomp']}")
    (OUT / 'e1_notification_anchored.log').write_text('\n'.join(L) + '\n', encoding='utf-8')
    sys.exit(1)
log('Reproduction check PASS')

# ---------------- D1: notification-anchored CARs ----------------
WINDOWS = [(0, 1), (0, 5), (0, 30)]
MAX_GAP = 10  # calendar days from reported_date to day 0
reg['rdt'] = pd.to_datetime(reg['reported_date'], errors='coerce')
bad_rdt = reg['rdt'].isna() | (reg['delay_invalid'] == 1)
log(f'\nD1: events lacking a usable reported_date (unparseable/missing or delay_invalid=1): '
    f'{int(bad_rdt.sum())}')
for _, r in reg[bad_rdt].iterrows():
    log(f"  no usable reported_date: {r['org_name']} | breach {r['breach_date']} | "
        f"reported {r['reported_date']} | treated {int(r[TREAT])}")

drop_reason = {}
for i, r in reg.iterrows():
    for a, b in WINDOWS:
        reg.loc[i, f'ncar_{a}_{b}'] = np.nan
    if bad_rdt[i]:
        drop_reason[i] = 'no usable reported_date'
        continue
    g = pg.get(int(r['permno']))
    if g is None:
        drop_reason[i] = 'no returns for permno'
        continue
    pos = int(g['date'].searchsorted(r['rdt'], side='left'))
    if pos >= len(g) or (g.loc[pos, 'date'] - r['rdt']).days > MAX_GAP:
        drop_reason[i] = 'no trading day within 10d on/after reported_date'
        continue
    reg.loc[i, 'day0'] = g.loc[pos, 'date']
    miss = []
    for a, b in WINDOWS:
        sl = g['ar'].iloc[pos + a:pos + b + 1]
        if len(sl) == b - a + 1 and sl.notna().all():
            reg.loc[i, f'ncar_{a}_{b}'] = sl.sum()
        else:
            miss.append(f'({a},+{b})')
    if miss:
        drop_reason[i] = 'incomplete returns for windows ' + ','.join(miss)

for i, why in drop_reason.items():
    r = reg.loc[i]
    if why != 'no usable reported_date':
        log(f"  dropped: {r['org_name']} | reported {r['reported_date']} | permno {r['permno']} | "
            f"treated {int(r[TREAT])} | {why}")
lag = (reg['day0'] - reg['rdt']).dt.days
log(f'  day-0 lag from reported_date (calendar days): 0 for {int((lag == 0).sum())}, '
    f'1-3 for {int(lag.between(1, 3).sum())}, >3 for {int((lag > 3).sum())}')
day0_vs_breach = (reg['day0'] - reg['bdt']).dt.days
log(f'  notification day-0 minus breach date (calendar days): median {day0_vs_breach.median():.0f}, '
    f'share same-day (<=3d) {(day0_vs_breach.abs() <= 3).mean():.3f}')
for a, b in WINDOWS:
    c = f'ncar_{a}_{b}'
    ok = reg[c].notna()
    log(f'  window ({a},+{b}): usable {int(ok.sum())}/{n_reg}; dropped {int((~ok).sum())} '
        f'(treated dropped {int((~ok & (reg[TREAT] == 1)).sum())})')

# ---------------- D2: baseline spec per window ----------------
EQ = 2.10
LAB = {'immediate_disclosure': 'H1_timing', TREAT: 'H2_FCC',
       'prior_breaches_1yr': 'H3_prior', 'health_breach': 'H4_health'}
rows = []
log('\nD2: baseline Essay 1 spec, notification-anchored CAR (HC3; CV1 = parent-CIK clustered)')


def fit_block(d, ycol, window_lab, anchor):
    y = d[ycol]
    X = sm.add_constant(d[CONTROLS].astype(float))
    m = sm.OLS(y, X).fit(cov_type='HC3')
    mc = sm.OLS(y, X).fit(cov_type='cluster', cov_kwds={'groups': d['final_cik']})
    dof = len(d) - len(CONTROLS) - 1
    ci95 = m.conf_int(alpha=.05)
    ci90 = m.conf_int(alpha=.10)
    nt = int(d[TREAT].sum())
    ntc = int(d.loc[d[TREAT] == 1, 'final_cik'].nunique())
    ncl = d['final_cik'].nunique()
    for var, lab in LAB.items():
        b, se, p = m.params[var], m.bse[var], m.pvalues[var]
        tost = max(1 - stats.t.cdf((b + EQ) / se, dof), stats.t.cdf((b - EQ) / se, dof))
        rec = dict(section='D2', anchor=anchor, window=window_lab, variable=var, hypothesis=lab,
                   group='', coef=b, se_hc3=se, p_hc3=p,
                   ci95_lo=ci95.loc[var, 0], ci95_hi=ci95.loc[var, 1],
                   ci90_lo=ci90.loc[var, 0], ci90_hi=ci90.loc[var, 1],
                   tost_p_2_10=tost, mde80=2.8 * se, p_cv1_parentcik=mc.pvalues[var],
                   n_clusters=ncl, mean=np.nan, median=np.nan, n=np.nan,
                   N=len(d), n_treated=nt, n_treated_parent_ciks=ntc)
        rows.append(rec)
        flag = '  <-- p<.05' if (p < .05 or mc.pvalues[var] < .05) else ''
        log(f"  [{anchor} {window_lab}] regression sample N={len(d)} (treated {nt} events / {ntc} parent CIKs; "
            f"{ncl} clusters) {lab}: b={b:+.4f} SE={se:.4f} p_HC3={p:.4f} "
            f"95%[{ci95.loc[var, 0]:+.3f},{ci95.loc[var, 1]:+.3f}] 90%[{ci90.loc[var, 0]:+.3f},{ci90.loc[var, 1]:+.3f}] "
            f"TOST p={tost:.4f} MDE80={2.8 * se:.3f} p_CV1={mc.pvalues[var]:.4f}{flag}")


# reference row: breach-anchored committed baseline (must equal constants_v3)
fit_block(reg, 'car_30d', '(0,+30)', 'breach (committed baseline, reference)')
for a, b in WINDOWS:
    c = f'ncar_{a}_{b}'
    fit_block(reg.dropna(subset=[c]), c, f'({a},+{b})', 'notification')

# ---------------- D3: descriptives ----------------
log('\nD3: CAR by treatment group (notification-anchored)')
for a, b in WINDOWS:
    c = f'ncar_{a}_{b}'
    d = reg.dropna(subset=[c])
    for gv, glab in [(1, 'treated (fcc_form499=1)'), (0, 'control (fcc_form499=0)'), (None, 'all')]:
        s = d[c] if gv is None else d.loc[d[TREAT] == gv, c]
        rows.append(dict(section='D3', anchor='notification', window=f'({a},+{b})', variable=c,
                         hypothesis='', group=glab, mean=s.mean(), median=s.median(), n=len(s),
                         N=len(d), n_treated=int(d[TREAT].sum()),
                         n_treated_parent_ciks=int(d.loc[d[TREAT] == 1, 'final_cik'].nunique())))
        log(f"  [notification ({a},+{b})] N={len(d)} {glab}: n={len(s)} mean={s.mean():+.4f} "
            f"median={s.median():+.4f}")

res = pd.DataFrame(rows)
cols = ['section', 'anchor', 'window', 'variable', 'hypothesis', 'group', 'coef', 'se_hc3', 'p_hc3',
        'ci95_lo', 'ci95_hi', 'ci90_lo', 'ci90_hi', 'tost_p_2_10', 'mde80', 'p_cv1_parentcik',
        'n_clusters', 'mean', 'median', 'n', 'N', 'n_treated', 'n_treated_parent_ciks']
res = res[cols]
num = res.select_dtypes('number').columns
res[num] = res[num].round(6)
res.to_csv(OUT / 'e1_notification_anchored.csv', index=False)
log(f'\nSaved: {OUT / "e1_notification_anchored.csv"} ({len(res)} rows)')
(OUT / 'e1_notification_anchored.log').write_text('\n'.join(L) + '\n', encoding='utf-8')
