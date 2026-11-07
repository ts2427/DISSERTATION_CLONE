"""ESSAY 2 v5 — WRDS pull of the daily quote fields missing for the v5 spreads
(committee item 8). Licensed data; run interactively with the author's login:

    python scripts/267_e2v5_quotes_pull.py

The committed quote extract (Data/wrds/crsp_quotes_topup.csv, scripts/167)
was pulled for the pre-DISH sample and has no rows for DISH (permno 81696),
whose two 2023 events are treated in the frozen 333 / 104 / 12 sample. Every
other event has >= 80% quote-day coverage of [-60,+20] in that file. This
script pulls the same crsp.dsf fields as scripts/167 for every sample permno
lacking that coverage, over [first anchor - 130 days, last anchor + 60 days],
into a NEW file; no existing data file is modified.
Output: Data/wrds_e2v5/crsp_quotes_topup_e2v5.csv
"""
import importlib.util as _ilu
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
_s = _ilu.spec_from_file_location('e2v5', 'scripts/263_e2v5_lib.py')
L = _ilu.module_from_spec(_s)
_s.loader.exec_module(L)
OUTF = Path('Data/wrds_e2v5/crsp_quotes_topup_e2v5.csv')
assert not OUTF.exists(), f'{OUTF} exists; delete it deliberately to re-pull'

fin = L.load_sample()
q = pd.read_csv('Data/wrds/crsp_quotes_topup.csv', usecols=['permno', 'date'])
q['date'] = pd.to_datetime(q['date'])
have = {p: set(g['date'].values) for p, g in q.groupby('permno')}
cal = pd.to_datetime(pd.read_csv('Data/wrds/market_indices.csv', usecols=['date'])['date']).to_numpy()
need = {}
for _, r in fin.iterrows():
    pos = int(np.argmin(np.abs(cal - np.datetime64(r['rdt']))))
    days = set(cal[max(0, pos - 60):pos + 21])
    if len(days & have.get(r['permno'], set())) / len(days) < 0.8:
        need.setdefault(r['permno'], []).append(r['rdt'])
print('permnos to pull:', {p: [str(d.date()) for d in v] for p, v in need.items()})
assert need, 'nothing to pull'

import wrds  # noqa: E402

db = wrds.Connection(wrds_username='tispivey')
frames = []
for p, dts in need.items():
    lo = (min(dts) - pd.Timedelta(days=130)).date()
    hi = (max(dts) + pd.Timedelta(days=60)).date()
    frames.append(db.raw_sql(f"""
        select permno, date, bid, ask, prc, openprc, bidlo, askhi, vol, shrout, hexcd
        from crsp.dsf where permno = {int(p)} and date between '{lo}' and '{hi}'"""))
db.close()
df = pd.concat(frames, ignore_index=True)
OUTF.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(OUTF, index=False)
print(f'Pulled {len(df):,} rows for {df["permno"].nunique()} permno(s) -> {OUTF}')
