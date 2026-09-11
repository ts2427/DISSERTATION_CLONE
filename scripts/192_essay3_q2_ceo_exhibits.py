"""
ESSAY 3 QUERY 2 — PART B1 (exhibits): EX-99 FOR CEO-DEPARTURE FILINGS (NEW)
===========================================================================
For every filing the frozen classifier (scripts/188) codes ceo_departure == 1, plus
the two filings Part G6 names (King 0001193125-16-470124; Legere-to-Sievert
0001193125-20-093622), read the filing directory listing
  https://www.sec.gov/Archives/edgar/data/{cik}/{accession-no-dashes}/index.json
and fetch every document whose name marks it as Exhibit 99 (ex99, ex-99, dex99,
exhibit99). Stored at Data/edgar/item5_02_text/{cik}/exhibits/{accession}_{file}.
Output: outputs/essay3_q2/b_exhibits_log.csv
"""

import re
import sys
import time
from pathlib import Path
import pandas as pd
import requests

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
OUT = Path('outputs/essay3_q2')
TXT = Path('Data/edgar/item5_02_text')
H = {'User-Agent': 'Academic Research (University of South Alabama) timothy.spivey@southalabama.edu'}
EX99 = re.compile(r'(?i)(ex[-_]?99|dex99|exhibit[-_]?99)')
G6 = {'0001193125-16-470124': 1283699, '0001193125-20-093622': 1283699}

F = pd.read_csv(OUT / 'c_filing_codes.csv', dtype={'accession': str})
want = {r['accession']: int(r['cik']) for _, r in F[F['ceo_departure'] == 1].iterrows()}
want.update(G6)
rows = []
for acc, cik in sorted(want.items()):
    base = f'https://www.sec.gov/Archives/edgar/data/{cik}/{acc.replace("-", "")}/'
    try:
        idx = requests.get(base + 'index.json', headers=H, timeout=30)
        time.sleep(0.2)
        items = idx.json()['directory']['item'] if idx.status_code == 200 else []
    except Exception:
        items = []
    ex = [it['name'] for it in items if EX99.search(it['name']) and it['name'].lower().endswith(('.htm', '.html', '.txt'))]
    if not ex:
        rows.append(dict(accession=acc, cik=cik, exhibit='', status='no EX-99 in index' if items else 'index FAILED'))
    for name in ex:
        dest = TXT / str(cik) / 'exhibits' / f'{acc}_{name}'
        dest.parent.mkdir(parents=True, exist_ok=True)
        st = 'already_on_disk'
        if not dest.exists():
            st = 'FAILED (timeout)'
            for attempt in range(3):
                try:
                    r = requests.get(base + name, headers=H, timeout=60)
                    time.sleep(0.2)
                    if r.status_code == 200:
                        dest.write_bytes(r.content)
                        st = 'fetched'
                    else:
                        st = f'FAILED {r.status_code}'
                    break
                except requests.exceptions.RequestException:
                    time.sleep(3)
        rows.append(dict(accession=acc, cik=cik, exhibit=name, status=st, local_file=str(dest),
                         g6_named=int(acc in G6)))
E = pd.DataFrame(rows)
E.to_csv(OUT / 'b_exhibits_log.csv', index=False)
print(f'CEO-departure filings: {len(want) - len(G6)} (+{len(G6)} named in G6) | exhibit rows {len(E)}')
print(E['status'].value_counts().to_string())
