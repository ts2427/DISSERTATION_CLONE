"""
DISH CRSP TOP-UP (pre-specified, 9/4 directive item 2)
======================================================
One licensed CRSP pull for the single security the committed extract never
requested: DISH Network Corporation (permno 81696, ticker DISH), required by
the two DISH events re-adjudicated treated on 9/4 (breach 2023-02-22 and
2023-05-17, notifications 2023-05-15 and 2023-05-17). Daily returns and
volume 2022-10-01..2023-12-29 (the security's final trading day before the
EchoStar merger) cover every breach- and notification-anchored window the
pipeline computes. Identity evidence: Data/wrds/ticker_permno_mapping.csv
(DISH -> 81696, name row 2017-02-22..2023-12-29) and Data/wrds/
q6_stocknames.csv (same, siccd 4841) agree; no names top-up is needed.
Compustat is NOT pulled: gvkey 60900 (tic DISH) is already in the committed
compustat_annual.csv through fyear 2022, satisfying the prior-fiscal-year
rule for both events.

Output: Data/wrds/crsp_daily_topup_dish.csv (separate file; committed
extract and the 159 top-up untouched).
"""

import sys
from pathlib import Path
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

out = Path('Data/wrds/crsp_daily_topup_dish.csv')
if out.exists():
    print('DISH top-up artifact already present — skip (idempotent). '
          'Delete crsp_daily_topup_dish.csv to force a re-pull.')
    sys.exit(0)

import wrds

print('Connecting to WRDS (pgpass, user tispivey)...')
db = wrds.Connection(wrds_username='tispivey')

names = db.raw_sql("""
    select permno, ticker, comnam, namedt, nameenddt
    from crsp.stocknames
    where permno = 81696
""")
print(names.to_string(index=False))
assert (names['ticker'] == 'DISH').any(), 'HALT: permno 81696 is not DISH'

dsf = db.raw_sql("""
    select permno, date, ret, vol
    from crsp.dsf
    where permno = 81696
      and date between '2022-10-01' and '2023-12-29'
""")
print(f'Daily rows pulled: {len(dsf):,} for permno 81696')
assert len(dsf) > 250, 'HALT: implausibly small pull'
dsf['ticker'] = 'DISH'
dsf.to_csv(out, index=False)
print(f'Saved: {out}')
db.close()
