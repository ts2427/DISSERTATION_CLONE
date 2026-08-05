"""
CALIBRATION SAMPLE — Item 5.02 content validation (measurement documentation)
==============================================================================
Supports the reframe-vs-refine decision on Essay 3's outcome. Reopens NOTHING:
no dataset column changes, no estimation, no baseline movement. Deliverable is
a hand-coding package: the 50 randomly sampled (seed=42, documented) primary
documents behind the 339-sample's Item 5.02 hits, plus a coding sheet. Tim
hand-classifies departure-related vs not; the resulting share becomes one
table-note sentence ("in a random sample of 50 underlying filings, X% involved
officer or director departures").

Universe: all 8-K filings with item 5.02 filed in (breach_date, +180d] for
regression-sample events with executive_change_180d = 1, enumerated from the
committed submissions cache. Documents fetched from EDGAR once, cached to
outputs/rebuild/calibration_5_02/.

Outputs: outputs/rebuild/calibration_5_02/coding_sheet.csv + the 50 documents
"""

import sys
import json
import random
import time
from datetime import timedelta
from pathlib import Path
import pandas as pd
import requests

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
OUT = Path('outputs/rebuild/calibration_5_02')
OUT.mkdir(parents=True, exist_ok=True)
H = {'User-Agent': 'Academic Research (University of South Alabama) timothy.spivey@southalabama.edu'}
CACHE = Path('Data/edgar/rebuild_submissions_cache')

ev = pd.read_csv('Data/processed/rebuild/CANONICAL_V3.csv', low_memory=False)
ev['bdt'] = pd.to_datetime(ev['breach_date'])
CONTROLS = ['fcc_form499', 'immediate_disclosure', 'prior_breaches_1yr', 'health_breach',
            'firm_size_log', 'leverage', 'roa']
reg = ev[ev['has_crsp_data'] == 1].dropna(subset=['car_30d'] + CONTROLS)
hits = reg[reg['executive_change_180d'] == 1]
print(f'Regression-sample events with a 5.02 hit at 180d: {len(hits)}')

# Enumerate every underlying 5.02 filing in-window
filings = []
for _, r in hits.iterrows():
    cj = CACHE / f"{int(r['final_cik'])}.json"
    if not cj.exists():
        continue
    for pg in json.loads(cj.read_text()):
        n = len(pg.get('form', []))
        for form, dt, items, acc, doc in zip(
                pg.get('form', []), pg.get('filingDate', []),
                pg.get('items', [''] * n), pg.get('accessionNumber', [''] * n),
                pg.get('primaryDocument', [''] * n)):
            if form.startswith('8-K') and items and '5.02' in items:
                d = pd.Timestamp(dt)
                if r['bdt'] < d <= r['bdt'] + timedelta(days=180):
                    filings.append({'org_name': r['org_name'], 'cik': int(r['final_cik']),
                                    'breach_date': r['breach_date'], 'filing_date': dt,
                                    'days_after_breach': (d - r['bdt']).days,
                                    'items': items, 'accession': acc, 'primary_doc': doc,
                                    'treated': int(r['fcc_form499'])})
fdf = pd.DataFrame(filings).drop_duplicates(subset=['cik', 'accession'])
print(f'Underlying 5.02 filings enumerated: {len(fdf)}')

# Seed-fixed random sample of 50
rng = random.Random(42)
idx = sorted(rng.sample(range(len(fdf)), min(50, len(fdf))))
samp = fdf.iloc[idx].reset_index(drop=True)
print(f'Sampled: {len(samp)} filings (seed=42, documented)')

# Fetch primary documents once, cached
rows = []
for i, r in samp.iterrows():
    accn = r['accession'].replace('-', '')
    fname = f"{i+1:02d}_{r['cik']}_{r['accession']}_{Path(str(r['primary_doc'])).name or 'doc.htm'}"
    local = OUT / fname
    if not local.exists():
        url = f"https://www.sec.gov/Archives/edgar/data/{r['cik']}/{accn}/{r['primary_doc']}"
        try:
            resp = requests.get(url, headers=H, timeout=30)
            local.write_bytes(resp.content if resp.status_code == 200
                              else f'FETCH FAILED {resp.status_code}: {url}'.encode())
        except Exception as e:
            local.write_text(f'FETCH ERROR: {e}')
        time.sleep(0.12)
    rows.append({'sample_id': i + 1, 'org_name': r['org_name'], 'treated': r['treated'],
                 'breach_date': r['breach_date'], 'filing_date': r['filing_date'],
                 'days_after_breach': r['days_after_breach'], 'items': r['items'],
                 'accession': r['accession'], 'local_file': fname,
                 'departure_related (Y/N)': '', 'role_if_departure': '', 'notes': ''})
sheet = pd.DataFrame(rows)
sheet.to_csv(OUT / 'coding_sheet.csv', index=False)
print(f'Coding sheet + {len(sheet)} documents -> {OUT}')
print(f'Treated filings in sample: {int(sheet["treated"].sum())}/{len(sheet)}')
