"""
ESSAY 3 QUERY 2 — PART B: FETCH ITEM 5.02 FILING TEXT (NEW)
============================================================
Scope set: CANONICAL_V3 events with has_crsp_data == 1 and firm_size_log, leverage,
roa non-missing. This is the Essay 3 regression sample of 158:131 WITHOUT the
immediate_disclosure requirement (decision L3 removes the mediator from H6), so it
is a superset of the Query 1 sample (340).

Filings in scope: for every event, every 8-K / 8-K/A of its parent CIK whose `items`
lists 5.02 and whose filing date falls in
    [min(breach_date, reported_date) - 365d, reported_date + 180d]
(breach_date + 180d if reported_date is missing; flagged). Union over events,
deduplicated by accession.

Documents: the 50 calibration documents (scripts/162) and the 35 T-Mobile documents
(scripts/184) are REUSED (copied); every other primary document is fetched from
https://www.sec.gov/Archives/edgar/data/{cik}/{accession-no-dashes}/{primaryDocument}
(addresses from the committed v3 submissions cache). Stored at
Data/edgar/item5_02_text/{cik}/{accession}_{primaryDocument}.

Validation firewall (fixed HERE, before any classifier development):
  - validation draw: 30 filings, seed 20260911, from the scope set excluding the
    calibration 50 and excluding the 35 T-Mobile documents whose hand codes were
    published in outputs/ESSAY3_QUERY1_REPORT.md;
  - development draw: 40 filings, seed 1117, from what remains. Only the dev draw and
    the 28 non-calibration T-Mobile documents are read while writing the classifier.

Outputs (outputs/essay3_q2/): b_scope_events.csv, b_scope_filings.csv,
b_event_filing_pairs.csv, b_fetch_log.csv, validation_ids.csv, dev_ids.csv, 187_fetch.log
"""

import sys
import json
import time
import shutil
import random
from datetime import timedelta
from pathlib import Path
import pandas as pd
import requests

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
OUT = Path('outputs/essay3_q2')
OUT.mkdir(parents=True, exist_ok=True)
TXT = Path('Data/edgar/item5_02_text')
TXT.mkdir(parents=True, exist_ok=True)
CACHE = Path('Data/edgar/rebuild_submissions_cache')
CAL = Path('outputs/rebuild/calibration_5_02')
TMO = Path('outputs/essay3_q1/tmobile_8k')
H = {'User-Agent': 'Academic Research (University of South Alabama) timothy.spivey@southalabama.edu'}
DELAY = 0.20
L = []


def log(m=''):
    print(m, flush=True)
    L.append(str(m))


ev = pd.read_csv('Data/processed/rebuild/CANONICAL_V3.csv', low_memory=False)
ev['bdt'] = pd.to_datetime(ev['breach_date'])
ev['rdt'] = pd.to_datetime(ev['reported_date'], errors='coerce')
sc = ev[(ev['has_crsp_data'] == 1)].dropna(subset=['firm_size_log', 'leverage', 'roa']).copy()
sc['rd_missing'] = sc['rdt'].isna().astype(int)
sc['rdt_eff'] = sc['rdt'].fillna(sc['bdt'])
# Spec scope (Query 2 B1, verbatim) and the extension needed downstream:
#   F2 baseline needs [t0-730, t0-181]  -> extend the pre-window to min(bd, rd) - 730d
#   the breach-date anchor needs (bd, bd+180] and bd can exceed rd (recoded / wrong-field
#   delays) -> extend the post-window to max(bd, rd) + 180d.
# The validation and dev draws are taken from the SPEC scope only.
sc['win_lo'] = sc[['bdt', 'rdt_eff']].min(axis=1) - timedelta(days=365)
sc['win_hi'] = sc['rdt_eff'] + timedelta(days=180)
sc['win_lo_ext'] = sc[['bdt', 'rdt_eff']].min(axis=1) - timedelta(days=730)
sc['win_hi_ext'] = sc[['bdt', 'rdt_eff']].max(axis=1) + timedelta(days=180)
log(f'Scope events: {len(sc)} (treated {int(sc["fcc_form499"].sum())}, parent CIKs '
    f'{sc["final_cik"].nunique()}); reported_date missing: {int(sc["rd_missing"].sum())}')
sc.drop(columns=['bdt', 'rdt', 'rdt_eff']).to_csv(OUT / 'b_scope_events.csv', index=False)

# ---- enumerate filings from the committed v3 cache ----
rows = []
for cik in sorted(sc['final_cik'].unique()):
    pages = json.loads((CACHE / f'{int(cik)}.json').read_text())
    for pg in pages:
        n = len(pg.get('form', []))
        for i in range(n):
            form, items = pg['form'][i], (pg.get('items') or [''] * n)[i] or ''
            if form.startswith('8-K') and '5.02' in items:
                rows.append({'cik': int(cik), 'form': form, 'filing_date': pg['filingDate'][i],
                             'items': items, 'accession': pg['accessionNumber'][i],
                             'primary_doc': pg['primaryDocument'][i], 'size': pg['size'][i]})
allf = pd.DataFrame(rows).drop_duplicates(['cik', 'accession'])
allf['fdt'] = pd.to_datetime(allf['filing_date'])

pairs = []
for _, r in sc.iterrows():
    f = allf[(allf['cik'] == r['final_cik']) & (allf['fdt'] >= r['win_lo_ext']) & (allf['fdt'] <= r['win_hi_ext'])]
    for _, x in f.iterrows():
        pairs.append({'final_cik': int(r['final_cik']), 'breach_date': r['breach_date'],
                      'reported_date': r['reported_date'], 'fcc_form499': int(r['fcc_form499']),
                      'accession': x['accession'], 'filing_date': x['filing_date'],
                      'days_from_reported': (x['fdt'] - r['rdt_eff']).days,
                      'days_from_breach': (x['fdt'] - r['bdt']).days,
                      'in_spec_scope': int(r['win_lo'] <= x['fdt'] <= r['win_hi'])})
P = pd.DataFrame(pairs)
P.to_csv(OUT / 'b_event_filing_pairs.csv', index=False)
spec_acc = set(P.loc[P['in_spec_scope'] == 1, 'accession'])
S = allf[allf['accession'].isin(set(P['accession']))].drop(columns=['fdt']).sort_values(['cik', 'filing_date'])
S['in_spec_scope'] = S['accession'].isin(spec_acc).astype(int)
log(f'Spec scope (B1 verbatim): {len(spec_acc)} filings; extension adds '
    f'{len(S) - len(spec_acc)} (baseline pre-window to -730d; post-window to max(bd, rd)+180d)')
S['local_file'] = [str(TXT / str(c) / f'{a}_{d}') for c, a, d in zip(S['cik'], S['accession'], S['primary_doc'])]
log(f'Filings in scope: {len(S)} unique accessions across {S["cik"].nunique()} CIKs '
    f'({len(P)} event-filing pairs); submission size total {S["size"].sum() / 1e6:.0f} MB')

# ---- reuse on-disk documents ----
cal_map = {p.name.split('_')[2]: p for p in CAL.glob('*.htm')}
tmo_map = {p.name.split('_')[0]: p for p in TMO.glob('*.htm')}
cal_acc = set(cal_map)
tmo_acc = set(tmo_map)

flog = []
reused = fetched = failed = cached = 0
for i, r in S.reset_index(drop=True).iterrows():
    dest = Path(r['local_file'])
    dest.parent.mkdir(parents=True, exist_ok=True)
    status = ''
    if dest.exists() and dest.stat().st_size > 300:
        status = 'already_on_disk'
        cached += 1
    elif r['accession'] in cal_map or r['accession'] in tmo_map:
        shutil.copyfile(cal_map.get(r['accession']) or tmo_map[r['accession']], dest)
        status = 'reused_calibration' if r['accession'] in cal_map else 'reused_tmobile'
        reused += 1
    else:
        url = (f"https://www.sec.gov/Archives/edgar/data/{r['cik']}/"
               f"{r['accession'].replace('-', '')}/{r['primary_doc']}")
        ok = False
        for attempt in range(2):
            try:
                resp = requests.get(url, headers=H, timeout=30)
                time.sleep(DELAY)
                if resp.status_code == 200 and len(resp.content) > 300:
                    dest.write_bytes(resp.content)
                    ok = True
                    break
            except Exception:
                time.sleep(1.0)
        status = 'fetched' if ok else 'FAILED'
        fetched += ok
        failed += (not ok)
    flog.append({'accession': r['accession'], 'cik': r['cik'], 'status': status,
                 'bytes': dest.stat().st_size if dest.exists() else 0})
    if (i + 1) % 100 == 0:
        log(f'  {i + 1}/{len(S)} | fetched {fetched} reused {reused} already {cached} failed {failed}')
pd.DataFrame(flog).to_csv(OUT / 'b_fetch_log.csv', index=False)
S.to_csv(OUT / 'b_scope_filings.csv', index=False)
log(f'Fetch complete: in scope {len(S)} | fetched {fetched} | reused {reused} '
    f'(calibration {sum(a in cal_acc for a in S["accession"])}, T-Mobile '
    f'{sum((a in tmo_acc) and (a not in cal_acc) for a in S["accession"])}) | already on disk '
    f'{cached} | FAILED {failed}')
log(f'Calibration 50 inside scope: {len(cal_acc & set(S["accession"]))}/50 '
    f'(outside: {sorted(cal_acc - set(S["accession"]))})')
log(f'Text store size: {sum(p.stat().st_size for p in TXT.rglob("*") if p.is_file()) / 1e6:.1f} MB')

# ---- validation and development draws (firewall) ----
ok_acc = set(pd.DataFrame(flog).query('status != "FAILED"')['accession'])
pool = sorted(a for a in ok_acc if a in spec_acc and a not in cal_acc and a not in tmo_acc)
val = sorted(random.Random(20260911).sample(pool, 30))
rest = [a for a in pool if a not in set(val)]
dev = sorted(random.Random(1117).sample(rest, 40))
for fn, ids in [('validation_ids.csv', val), ('dev_ids.csv', dev)]:
    fp = OUT / fn
    if fp.exists():  # the draw is fixed by the first run; a rerun must reproduce it exactly
        prior = sorted(pd.read_csv(fp)['accession'])
        assert prior == ids, f'{fn}: rerun draw differs from the fixed draw — STOP'
    else:
        pd.DataFrame({'accession': ids}).to_csv(fp, index=False)
log(f'Validation draw: 30 of pool {len(pool)} (seed 20260911). Dev draw: 40 (seed 1117).')
(OUT / '187_fetch.log').write_text('\n'.join(L) + '\n', encoding='utf-8')
