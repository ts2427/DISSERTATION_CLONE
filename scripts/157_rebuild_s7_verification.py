"""
REBUILD DIRECTIVE v2 — STAGE 7: VERIFICATION SUPPLEMENTS
=========================================================
(a) Disclosure-date verification: for every treated event and all untreated
    events at CIKs with 3+ events (documented control sample), the gap from the
    PRC breach date to the firm's first 8-K filed in (breach, +90d] — armor
    table from the same cached EDGAR submissions; NO date is changed.
(b) OCR health-flag verification (bounded: Oct 2009+, 500+ individuals):
    HHS OCR portal CSV matched by normalized entity name (exact-and-abstain);
    graceful stop-and-note if the portal blocks the pull.
(c) CRSP-attrition balance table: treated share and available covariates for
    events excluded at the CRSP step vs included (limitations deliverable).
Outputs: outputs/rebuild/STAGE7_VERIFICATION.md (+ three CSVs)
"""

import sys
import json
import re
from datetime import timedelta
from pathlib import Path
import pandas as pd
import numpy as np
import requests

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
OUT = Path('outputs/rebuild')
L = []


def log(m=''):
    print(m)
    L.append(str(m))


def normalize(name):
    if not isinstance(name, str):
        return ""
    n = name.upper().strip()
    n = re.sub(r'[^\w\s]', ' ', n)
    n = re.sub(r'\s+', ' ', n)
    for s in [r'\bINC\b', r'\bINCORPORATED\b', r'\bCORPORATION\b', r'\bCORP\b',
              r'\bLLC\b', r'\bLLP\b', r'\bLP\b', r'\bCO\b', r'\bCOMPANY\b',
              r'\bLTD\b', r'\bLIMITED\b', r'\bNA\b', r'\bNOT FOR PROFIT\b', r'\bTHE\b']:
        n = re.sub(s, '', n)
    return re.sub(r'\s+', ' ', n).strip()


log('=' * 90)
log('REBUILD STAGE 7: VERIFICATION SUPPLEMENTS')
log('=' * 90)

ev = pd.read_csv('Data/processed/rebuild/CANONICAL_V3.csv', low_memory=False)
ev['bdt'] = pd.to_datetime(ev['breach_date'])
CACHE = Path('Data/edgar/rebuild_submissions_cache')

# ---- (a) disclosure-date verification ----
log('\n[a] Disclosure-date verification (PRC date vs first 8-K within +90d)...')


def first_8k_after(cik, bdt):
    cj = CACHE / f'{int(cik)}.json'
    if not cj.exists():
        return None
    dates = []
    for p in json.loads(cj.read_text()):
        for form, dt in zip(p.get('form', []), p.get('filingDate', [])):
            if form.startswith('8-K'):
                d = pd.Timestamp(dt)
                if bdt < d <= bdt + timedelta(days=90):
                    dates.append(d)
    return min(dates) if dates else None


big_ciks = ev.groupby('final_cik').size()
ctrl_ciks = set(big_ciks[big_ciks >= 3].index)
sample = ev[(ev['fcc_form499'] == 1) | (ev['final_cik'].isin(ctrl_ciks))]
rows = []
for _, r in sample.iterrows():
    f8k = first_8k_after(r['final_cik'], r['bdt'])
    rows.append({'org': r['org_name'], 'cik': r['final_cik'], 'breach_date': r['breach_date'],
                 'treated': r['fcc_form499'],
                 'first_8k_after': str(f8k.date()) if f8k is not None else None,
                 'gap_days': (f8k - r['bdt']).days if f8k is not None else np.nan})
dv = pd.DataFrame(rows)
dv.to_csv(OUT / 'stage7_disclosure_date_verification.csv', index=False)
have = dv.dropna(subset=['gap_days'])
log(f'  Sample: {len(dv)} events ({int(dv["treated"].sum())} treated + control CIKs w/3+ events)')
if len(have):
    for t, g in have.groupby('treated'):
        log(f'  treated={t}: n={len(g)}, median gap {g["gap_days"].median():.0f}d, '
            f'mean {g["gap_days"].mean():.1f}d, share w/ 8-K in 90d '
            f'{100 * len(g) / len(dv[dv["treated"] == t]):.0f}%')
log('  (Armor table: an 8-K near the event need not reference the breach; no dates changed.)')

# ---- (b) OCR health verification ----
log('\n[b] OCR health-flag verification (bounded: Oct 2009+, 500+ individuals)...')
try:
    H = {'User-Agent': 'Academic Research (University of South Alabama) timothy.spivey@southalabama.edu'}
    r = requests.get('https://ocrportal.hhs.gov/ocr/breach/breach_report.csv', headers=H, timeout=60)
    r.raise_for_status()
    from io import StringIO
    ocr = pd.read_csv(StringIO(r.text))
    name_col = next(c for c in ocr.columns if 'Covered Entity' in c or 'Name' in c)
    ocr['nn'] = ocr[name_col].map(normalize)
    ocr_names = set(ocr['nn'])
    ev['nn_variants'] = ev['name_variants'].astype(str).apply(
        lambda s: [normalize(v) for v in s.split('|')])
    scope = ev[(ev['bdt'] >= pd.Timestamp('2009-10-01'))]
    hits, health_hits = 0, 0
    for _, e in scope.iterrows():
        m = any(v in ocr_names for v in e['nn_variants'] if v)
        hits += m
        if e['health_breach'] == 1:
            health_hits += m
    n_h = int((scope['health_breach'] == 1).sum())
    log(f'  OCR pull OK: {len(ocr):,} portal records. In-scope events: {len(scope)}.')
    log(f'  Health-flagged in-scope events: {n_h}; with OCR entity-name match: {health_hits}')
    log(f'  All in-scope events with OCR match: {hits} (non-health matches indicate '
        f'healthcare-adjacent entities — review list saved)')
    ocr_flag = scope[[any(v in ocr_names for v in vs if v) for vs in scope['nn_variants']]]
    ocr_flag[['org_name', 'breach_date', 'health_breach']].to_csv(
        OUT / 'stage7_ocr_matches.csv', index=False)
except Exception as e:
    log(f'  OCR pull FAILED ({str(e)[:80]}) — stop-and-note per rider: verification '
        f'claim deferred; health flag remains text-derived with documented rule.')

# ---- (c) CRSP-attrition balance ----
log('\n[c] CRSP-attrition balance table...')
inc = ev[ev['has_crsp_data'] == 1]
exc = ev[ev['has_crsp_data'] == 0]
bal = pd.DataFrame([
    {'Group': 'Included (CRSP)', 'N': len(inc), 'Treated share': round(inc['fcc_form499'].mean(), 4),
     'Mean size (log, where avail.)': round(inc['firm_size_log'].mean(), 3),
     'Median records affected': inc['total_affected_max'].median()},
    {'Group': 'Excluded (no CRSP)', 'N': len(exc), 'Treated share': round(exc['fcc_form499'].mean(), 4),
     'Mean size (log, where avail.)': round(exc['firm_size_log'].mean(), 3),
     'Median records affected': exc['total_affected_max'].median()},
])
bal.to_csv(OUT / 'stage7_crsp_attrition_balance.csv', index=False)
log('  ' + bal.to_string(index=False).replace('\n', '\n  '))

with open(OUT / 'STAGE7_VERIFICATION.md', 'w', encoding='utf-8') as f:
    f.write('# Stage 7 Verification Supplements\n\n' + '\n'.join(L) + '\n')
log('\nSaved: STAGE7_VERIFICATION.md + three CSVs')
