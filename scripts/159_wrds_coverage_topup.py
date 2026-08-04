"""
REBUILD — WRDS COVERAGE TOP-UP (pre-specified: DIRECTIVE_AMENDMENT_WRDS_TOPUP.md)
==================================================================================
One licensed CRSP pull for the two securities the retired-identity extract never
requested: Sprint (ticker S era) and CenturyLink (ticker CTL era). Daily returns
and volume 2008-01-01..2021-01-31 (covers all 16 affected events' +/-50-day and
volatility windows). Writes SEPARATE top-up files; the committed extract is not
touched. Names history rows pulled for the same permnos so Stage 5's date-aware
windows work identically.

Outputs: Data/wrds/crsp_daily_topup.csv, Data/wrds/ticker_permno_topup.csv
"""

import sys
from pathlib import Path
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Idempotent: if the committed top-up artifacts already exist, do nothing —
# a fresh clone with the CSVs present never needs WRDS credentials.
outs = [Path('Data/wrds/crsp_daily_topup.csv'),
        Path('Data/wrds/ticker_permno_topup.csv'),
        Path('Data/wrds/compustat_annual_topup.csv')]
if all(p.exists() for p in outs):
    print('WRDS top-up artifacts already present — skip (idempotent). '
          'Delete the three *_topup.csv files to force a re-pull.')
    sys.exit(0)

import wrds

print('Connecting to WRDS (pgpass, user tispivey)...')
db = wrds.Connection(wrds_username='tispivey')

names = db.raw_sql("""
    select permno, ticker, comnam, namedt, nameenddt
    from crsp.stocknames
    where (ticker = 'S' and comnam like 'SPRINT%%')
       or (ticker = 'CTL' and (comnam like 'CENTURYLINK%%' or comnam like 'CENTURYTEL%%'))
""")
names = names.rename(columns={'nameenddt': 'nameendt'})
print(names.to_string(index=False))
permnos = sorted(names['permno'].unique())
assert len(permnos) >= 2, f'HALT: expected Sprint + CenturyLink permnos, got {permnos}'

dsf = db.raw_sql(f"""
    select permno, date, ret, vol
    from crsp.dsf
    where permno in ({','.join(str(int(p)) for p in permnos)})
      and date between '2008-01-01' and '2021-01-31'
""")
print(f'Daily rows pulled: {len(dsf):,} for permnos {permnos}')
assert len(dsf) > 1000, 'HALT: implausibly small pull'

tkmap = {int(r['permno']): r['ticker'] for _, r in names.iterrows()}
dsf['ticker'] = dsf['permno'].astype(int).map(tkmap)
dsf.to_csv('Data/wrds/crsp_daily_topup.csv', index=False)
names.to_csv('Data/wrds/ticker_permno_topup.csv', index=False)
print('Saved: Data/wrds/crsp_daily_topup.csv, Data/wrds/ticker_permno_topup.csv')

# Compustat addendum (same pre-specification): gvkey-exact — 010984 Sprint,
# 002884 Lumen/CenturyLink. tic is CURRENT vintage in Compustat (Sprint='S.4');
# name/ticker lookups are the token-collision trap; gvkeys only.
f = db.raw_sql("""
    select gvkey, conm, datadate, at, lt, ni, sale, cogs, xsga
    from comp.funda
    where gvkey in ('010984','002884')
      and datadate between '2007-01-01' and '2020-12-31'
      and indfmt='INDL' and datafmt='STD' and popsrc='D' and consol='C'
""")
f['tic'] = f['gvkey'].map({'010984': 'S', '002884': 'CTL'})
f[['tic', 'datadate', 'at', 'lt', 'ni', 'sale', 'cogs', 'xsga']].to_csv(
    'Data/wrds/compustat_annual_topup.csv', index=False)
print(f'Saved: Data/wrds/compustat_annual_topup.csv ({len(f)} rows)')
db.close()
