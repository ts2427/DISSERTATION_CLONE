"""ESSAY 2 v5 — trading-cost measures (committee item 8): scripts/167's three
measures rebuilt on the frozen 333 / 104 / 12 sample with the v5 windows.

Measures (definitions from archive/scripts/167, unchanged):
  CPQS  closing percent quoted spread (ask - bid) / midpoint; valid uncrossed
        quotes only; values > 0.5 set missing (Chung & Zhang 2014)
  EDGE  Ardia, Guidotti & Kroencke (2024) via the authors' `bidask` package,
        signed estimates kept
  OCAM  open-to-close Amihud |C - O| / O / dollar volume (x 1e6), window mean,
        winsorized 1/99 within window across events, then logged
        (Barardehi et al. 2021)
Windows (v5): trading days [-60,-11] pre and [+1,+20] post around the v3
agency reporting date (nearest market trading day; stock trading within 7
calendar days), days with PRC > 0 and VOL > 0, >= 80% of window days.
Outcome: post minus pre. Model: Form 499 + the scripts/167 controls with the
v5 pre-window abnormal-return SD in place of e2_pre_sd, notification
calendar-month fixed effects (167), CV3 on parent filer entity (primary)
and CV1 (167's rung). BH within the family of three.
Inputs: Data/wrds/crsp_quotes_topup.csv (scripts/167) + Data/wrds_e2v5/
crsp_quotes_topup_e2v5.csv (scripts/267, DISH). Fails if either is missing.
Writes outputs/essay2_v5/v5_t16_spreads.csv, constants_parts/268.json.
"""
import importlib.util as _ilu
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
_s = _ilu.spec_from_file_location('e2v5', 'scripts/263_e2v5_lib.py')
L = _ilu.module_from_spec(_s)
_s.loader.exec_module(L)
from bidask import edge  # noqa: E402

OUT, TREAT = L.OUT, L.TREAT
F1, F2 = Path('Data/wrds/crsp_quotes_topup.csv'), Path('Data/wrds_e2v5/crsp_quotes_topup_e2v5.csv')
assert F1.exists() and F2.exists(), 'quote inputs missing; run scripts/267 with the WRDS login first'
qd = pd.concat([pd.read_csv(F1, low_memory=False), pd.read_csv(F2, low_memory=False)])
qd['date'] = pd.to_datetime(qd['date'])
qd = qd.drop_duplicates(subset=['permno', 'date'], keep='first')   # main extract wins
for c in ['bid', 'ask', 'prc', 'openprc', 'bidlo', 'askhi', 'vol']:
    qd[c] = pd.to_numeric(qd[c], errors='coerce')
valid = qd['bid'].notna() & qd['ask'].notna() & (qd['ask'] > qd['bid']) & (qd['bid'] > 0)
qd['cpqs'] = np.where(valid, (qd['ask'] - qd['bid']) / ((qd['ask'] + qd['bid']) / 2), np.nan)
qd.loc[qd['cpqs'] > 0.5, 'cpqs'] = np.nan

fin = L.load_sample()
panel = pd.read_csv(OUT / 'v5_event_panel.csv')
assert (panel['final_cik'].values == fin['final_cik'].values).all()
fin['pre_sd'] = panel['prim_pre_sd'].values
M = L.Market(permnos=fin['permno'].unique())
cal = M.dates
QG = {p: g.set_index('date').sort_index() for p, g in qd.groupby('permno')}
WIN = {'pre': L.PRE_PRIMARY, 'post': L.POST_PRIMARY}
rows = []
for i, r in fin.iterrows():
    pos = M.anchor(r['permno'], r['rdt'])
    g = QG.get(r['permno'])
    out = {}
    for lab, (lo, hi) in WIN.items():
        if pos is None or g is None:
            continue
        days = pd.DatetimeIndex(cal[max(0, pos + lo):pos + hi + 1])
        w = g.reindex(days)
        w = w[(w['prc'] > 0) & (w['vol'] > 0)]
        if len(w) < math.ceil(0.8 * (hi - lo + 1)):
            continue
        out[f'cpqs_{lab}'] = w['cpqs'].mean()
        try:
            out[f'edge_{lab}'] = edge(w['openprc'], w['askhi'], w['bidlo'], w['prc'].abs(), sign=True)
        except Exception:
            out[f'edge_{lab}'] = np.nan
        dvol = w['prc'].abs() * w['vol']
        out[f'ocam_{lab}'] = ((w['prc'].abs() - w['openprc']).abs() / w['openprc'] / dvol).mean() * 1e6
    rows.append(out)
ms = pd.DataFrame(rows, index=fin.index)
for lab in WIN:
    s = ms.get(f'ocam_{lab}')
    if s is not None:
        ms[f'ocam_{lab}'] = np.log(s.clip(s.quantile(.01), s.quantile(.99)))
for v in ['cpqs', 'edge', 'ocam']:
    fin[f'{v}_chg'] = ms.get(f'{v}_post') - ms.get(f'{v}_pre')
fin['month'] = fin['rdt'].dt.to_period('M').astype(str)
res = []
for v, lab in [('cpqs_chg', 'CPQS change'), ('edge_chg', 'EDGE change'), ('ocam_chg', 'log-OCAM change')]:
    d = fin.dropna(subset=[v] + L.XS4).copy()
    mfe = pd.get_dummies(d['month'], drop_first=True, dtype=float)
    d = pd.concat([d, mfe], axis=1)
    r = L.ladder(d, v, L.XS4 + list(mfe.columns), full=False)
    res.append(dict(outcome=lab, coef=r['coef'], se_cv3=r['se_cv3'], p_cv3=r['p_cv3'],
                    se_cv1=r['se_cv1'], p_cv1=r['p_cv1'], N=r['N'], n_treated=r['n_treated'],
                    G=r['G'], G1=r['G1'],
                    corr_with_primary_dv=float(fin[[v]].join(panel['prim_dv']).corr().iloc[0, 1])))
R = pd.DataFrame(res)
R['bh_adj_p'], R['bh_reject_05'] = L.bh(R['p_cv3'])
R.to_csv(OUT / 'v5_t16_spreads.csv', index=False)
print(R.round(5).to_string(index=False))
C = {f'spread_{r["outcome"].split()[0].lower().replace("log-", "")}_{k}': r[k]
     for _, r in R.iterrows() for k in ['coef', 'p_cv3', 'bh_adj_p', 'N', 'n_treated', 'corr_with_primary_dv']}
C['bh_families'] = {'spreads': 3}
C['tests'] = {'spreads': 3}
(OUT / 'constants_parts' / '268.json').write_text(json.dumps(C, indent=1, default=float), encoding='utf-8')
print('Saved v5_t16_spreads.csv + constants_parts/268.json')
