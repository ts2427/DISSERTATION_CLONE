"""
QUERY 6 — WRDS PULL (run interactively; prompts for the password once)
=======================================================================
    python scripts/173_q6_wrds_pull.py

Pulls three small tables into Data/wrds/ (separate top-up files; committed
extracts untouched, house convention):
  q6_rdq.csv        comp.fundq earnings announcement dates (RDQ) for the
                    sample firms' tickers, 2005-2025  [positive control]
  q6_stocknames.csv crsp.stocknames full name history (permno, ticker,
                    comnam, siccd, exchcd, namedt, nameendt)
                    [listed-carrier denominator, SIC definition]
  q6_gics.csv       comp.company current GICS codes (gvkey, conm, tic,
                    gsector, ggroup, gind, sic)  [GICS definition; current
                    codes only — the historical co_hgic table is attempted
                    and skipped with a note if unsubscribed]
"""

import sys
from pathlib import Path
import pandas as pd
import wrds

fin = pd.read_csv('outputs/tables/essay2_v2/t1_final_sample.csv',
                  low_memory=False)
tickers = sorted({str(t) for t in fin['matched_ticker'].dropna()})
tl = ','.join(f"'{t}'" for t in tickers)

db = wrds.Connection(wrds_username='tispivey')

if not Path('Data/wrds/q6_rdq.csv').exists():
    rdq = db.raw_sql(f"""
        select gvkey, tic, datadate, fyearq, fqtr, rdq
        from comp.fundq
        where tic in ({tl}) and rdq is not null
          and rdq between '2005-01-01' and '2025-12-31'
    """)
    rdq.to_csv('Data/wrds/q6_rdq.csv', index=False)
    print(f'q6_rdq.csv: {len(rdq):,} firm-quarters, {rdq["tic"].nunique()} tickers')
else:
    print('q6_rdq.csv already pulled — skipping')

if Path('Data/wrds/q6_stocknames.csv').exists():
    print('q6_stocknames.csv already pulled — skipping')
    sn = None
else:
  sn = db.raw_sql("""
    select permno, ticker, comnam, siccd, exchcd, shrcd, namedt,
           nameenddt as nameendt
    from crsp.stocknames
  """)
if sn is not None:
    sn.to_csv('Data/wrds/q6_stocknames.csv', index=False)
    print(f'q6_stocknames.csv: {len(sn):,} name rows')

gics = db.raw_sql("""
    select gvkey, conm, gsector, ggroup, gind, sic, fic
    from comp.company
""")
gics.to_csv('Data/wrds/q6_gics.csv', index=False)
print(f'q6_gics.csv: {len(gics):,} companies (CURRENT GICS codes)')

try:
    hg = db.raw_sql("select gvkey, indfrom, indthru, gsector, ggroup, gind "
                    "from comp.co_hgic")
    hg.to_csv('Data/wrds/q6_gics_hist.csv', index=False)
    print(f'q6_gics_hist.csv: {len(hg):,} historical GICS rows')
except Exception as e:
    print(f'co_hgic unavailable ({e}) — GICS series will use current codes '
          f'with the limitation stated.')

db.close()
print('DONE — now run: python scripts/174_q6_closeout.py')
