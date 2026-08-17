"""
REBUILD DIRECTIVE v2 — STAGE 6: COVARIATES AND ASSEMBLY (no positional joins)
==============================================================================
Every enrichment regenerated from the rebuilt event set or joined on keys:
  - Compustat prior-fiscal-year covariates joined by ticker (tic) at the latest
    datadate strictly before the breach date (<=550 days stale):
    firm_size_log=ln(at), leverage=lt/at, roa=ni/at, and op_margin =
    (sale-cogs-xsga)/sale [AMENDMENT NOTE: oiadp absent from the committed
    extract; OIBDP-based margin documented as the data-constrained proxy].
  - prior_breaches_total / _1yr recomputed from the event set per parent CIK.
  - disclosure_delay_days = reported_date - breach_date; immediate <= 7 days.
    Signed fixes (8/17/2026): (i) where reported_date precedes breach_date the
    delay is a source-data anomaly, not information — recoded to 0 with
    delay_recoded = 1; (ii) immediate_disclosure is MISSING where the delay is
    missing (unparseable reported_date), never 0 via a NaN<=7 comparison.
  - health_breach derived (documented): information_affected contains
    medical|health (case-insensitive) OR organization_type == 'MED'.
  - Item 5.02 turnover: live SEC EDGAR submissions (recent + historical pages),
    cached under Data/edgar/rebuild_submissions_cache/; executive_change_30/90/
    180d = any 8-K listing item 5.02 in (breach, +Nd]; days_to_first recorded.
    (Committed 46-cache pickle is unreadable under current pandas - noted.)
Output: Data/processed/rebuild/CANONICAL_V3.csv (+ lineage header sidecar),
        outputs/rebuild/STAGE6_REPORT.md
"""

import sys
import json
import time
from datetime import timedelta
from pathlib import Path
import pandas as pd
import numpy as np
import requests

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
L = []


def log(m=''):
    print(m)
    L.append(str(m))


log('=' * 90)
log('REBUILD STAGE 6: COVARIATES AND ASSEMBLY')
log('=' * 90)

ev = pd.read_csv('Data/processed/rebuild/stage5_outcomes.csv', low_memory=False)
ev['bdt'] = pd.to_datetime(ev['breach_date'])
log(f'\nInput: {len(ev)} events')

# ---- Compustat covariates (key join by ticker, prior fiscal year) ----
cs = pd.read_csv('Data/wrds/compustat_annual.csv',
                 usecols=['tic', 'datadate', 'at', 'lt', 'ni', 'sale', 'cogs', 'xsga'])
# WRDS coverage top-up addendum (DIRECTIVE_AMENDMENT_WRDS_TOPUP.md): Sprint and
# CenturyLink fundamentals, gvkey-exact (010984, 002884), keyed to matched tickers.
tp_cs = Path('Data/wrds/compustat_annual_topup.csv')
if tp_cs.exists():
    cs = pd.concat([cs, pd.read_csv(tp_cs)], ignore_index=True)
    log('  Compustat top-up merged (Sprint, CenturyLink)')
cs['datadate'] = pd.to_datetime(cs['datadate'])
cs = cs.dropna(subset=['tic', 'at'])
by_tic = {t: g.sort_values('datadate') for t, g in cs.groupby('tic')}


def covars(ticker, bdt):
    g = by_tic.get(ticker)
    if g is None:
        return {}
    prior = g[(g['datadate'] < bdt) & (g['datadate'] >= bdt - timedelta(days=550))]
    if len(prior) == 0:
        return {}
    r = prior.iloc[-1]
    out = {}
    if pd.notna(r['at']) and r['at'] > 0:
        out['firm_size_log'] = round(np.log(r['at']), 4)
        if pd.notna(r['lt']):
            out['leverage'] = round(r['lt'] / r['at'], 4)
        if pd.notna(r['ni']):
            out['roa'] = round(r['ni'] / r['at'], 4)
    if pd.notna(r['sale']) and r['sale'] > 0 and pd.notna(r['cogs']):
        xs = r['xsga'] if pd.notna(r['xsga']) else 0
        out['op_margin'] = round((r['sale'] - r['cogs'] - xs) / r['sale'], 4)
    return out


cov_rows = [covars(r['matched_ticker'], r['bdt']) for _, r in ev.iterrows()]
for col in ['firm_size_log', 'leverage', 'roa', 'op_margin']:
    ev[col] = [c.get(col, np.nan) for c in cov_rows]
log(f'Compustat coverage: size {int(ev["firm_size_log"].notna().sum())}, '
    f'leverage {int(ev["leverage"].notna().sum())}, roa {int(ev["roa"].notna().sum())}, '
    f'op_margin {int(ev["op_margin"].notna().sum())} (of {len(ev)})')

# ---- prior breaches from the event set (parent-CIK level, documented) ----
ev = ev.sort_values(['final_cik', 'bdt']).reset_index(drop=True)
ev['prior_breaches_total'] = ev.groupby('final_cik').cumcount()
p1 = []
for _, r in ev.iterrows():
    p1.append(int(((ev['final_cik'] == r['final_cik']) & (ev['bdt'] < r['bdt']) &
                   (ev['bdt'] >= r['bdt'] - timedelta(days=365))).sum()))
ev['prior_breaches_1yr'] = p1

# ---- disclosure timing ----
ev['reported_dt'] = pd.to_datetime(ev['reported_date'], errors='coerce')
ev['disclosure_delay_days'] = (ev['reported_dt'] - ev['bdt']).dt.days
# Signed fix (8/17/2026): reported_date < breach_date is a source-data anomaly;
# floor the delay at 0 and flag it, so anomalous rows stay in the sample
# without carrying a negative (information-free) delay.
neg = ev['disclosure_delay_days'] < 0
ev['delay_recoded'] = neg.astype(int)
if neg.any():
    for _, r in ev[neg].iterrows():
        log(f'  delay_recoded: {r["org_name"]} | breach {r["breach_date"]} | '
            f'reported {r["reported_dt"]:%Y-%m-%d} | delay {int(r["disclosure_delay_days"])} -> 0')
    ev.loc[neg, 'disclosure_delay_days'] = 0
# Signed fix (8/17/2026): immediate_disclosure is missing where the delay is
# missing — NaN<=7 silently coded such rows 0; they are now NaN and excluded
# by every downstream dropna/mean.
ev['immediate_disclosure'] = (ev['disclosure_delay_days'] <= 7).astype(float)
ev.loc[ev['disclosure_delay_days'].isna(), 'immediate_disclosure'] = np.nan
n_imm = int(ev['immediate_disclosure'].sum())
n_known = int(ev['immediate_disclosure'].notna().sum())
log(f'Immediate disclosure: {n_imm}/{n_known} known '
    f'({100 * ev["immediate_disclosure"].mean():.1f}%; '
    f'{int(ev["immediate_disclosure"].isna().sum())} missing)')

# ---- health flag (documented derivation; OCR cross-check at Stage 7) ----
ia = ev['information_affected'].astype(str).str.contains('medical|health', case=False, na=False)
ot = ev['organization_type'].astype(str).str.upper().eq('MED')
ev['health_breach'] = (ia | ot).astype(int)
log(f'Health events (derived): {int(ev["health_breach"].sum())}')

# ---- Item 5.02 via live EDGAR submissions (cached) ----
CACHE = Path('Data/edgar/rebuild_submissions_cache')
CACHE.mkdir(exist_ok=True)
H = {'User-Agent': 'Academic Research (University of South Alabama) timothy.spivey@southalabama.edu'}


def eightk_502_dates(cik):
    """All 8-K filing dates listing item 5.02, from recent + historical pages."""
    cj = CACHE / f'{int(cik)}.json'
    if cj.exists():
        pages = json.loads(cj.read_text())
    else:
        pages = []
        try:
            r = requests.get(f'https://data.sec.gov/submissions/CIK{int(cik):010d}.json',
                             headers=H, timeout=30)
            if r.status_code == 200:
                d = r.json()
                pages.append(d['filings']['recent'])
                for extra in d['filings'].get('files', []):
                    time.sleep(0.12)
                    r2 = requests.get(f'https://data.sec.gov/submissions/{extra["name"]}',
                                      headers=H, timeout=30)
                    if r2.status_code == 200:
                        pages.append(r2.json())
            time.sleep(0.12)
        except Exception:
            pass
        cj.write_text(json.dumps(pages))
    dates = []
    for p in pages:
        for form, dt, items in zip(p.get('form', []), p.get('filingDate', []),
                                   p.get('items', [''] * len(p.get('form', [])))):
            if form.startswith('8-K') and items and '5.02' in items:
                dates.append(dt)
    return sorted(set(dates))


log('Item 5.02 extraction (live EDGAR, cached)...')
ciks = sorted(ev['final_cik'].dropna().unique())
cik_dates = {}
for i, c in enumerate(ciks):
    cik_dates[c] = eightk_502_dates(c)
    if (i + 1) % 40 == 0:
        log(f'  {i + 1}/{len(ciks)} CIKs...')
for w in (30, 90, 180):
    ev[f'executive_change_{w}d'] = 0
ev['days_to_first_item_5_02'] = np.nan
for i, r in ev.iterrows():
    ds = [pd.Timestamp(d) for d in cik_dates.get(r['final_cik'], [])]
    after = [d for d in ds if r['bdt'] < d <= r['bdt'] + timedelta(days=180)]
    if after:
        ev.at[i, 'days_to_first_item_5_02'] = (min(after) - r['bdt']).days
        for w in (30, 90, 180):
            ev.at[i, f'executive_change_{w}d'] = int(any(d <= r['bdt'] + timedelta(days=w) for d in after))
log(f'Item 5.02 base rates (all events): 30d {100 * ev["executive_change_30d"].mean():.1f}%, '
    f'90d {100 * ev["executive_change_90d"].mean():.1f}%, 180d {100 * ev["executive_change_180d"].mean():.1f}%')

# ---- assemble canonical v3 ----
ev = ev.drop(columns=['bdt', 'reported_dt'])
out = Path('Data/processed/rebuild/CANONICAL_V3.csv')
ev.to_csv(out, index=False)
CONTROLS = ['fcc_form499', 'immediate_disclosure', 'prior_breaches_1yr', 'health_breach',
            'firm_size_log', 'leverage', 'roa', 'car_30d']
reg = ev[ev['has_crsp_data'] == 1].dropna(subset=CONTROLS)
log(f'\nCANONICAL_V3: {len(ev)} events | CRSP sample {int(ev["has_crsp_data"].sum())} '
    f'| regression sample {len(reg)} ({int(reg["fcc_form499"].sum())} treated, '
    f'{reg.loc[reg["fcc_form499"] == 1, "final_cik"].nunique()} parent CIKs)')

hdr = Path('Data/processed/rebuild/CANONICAL_V3_LINEAGE.md')
hdr.write_text(f"""# CANONICAL_V3 lineage (generated {pd.Timestamp.now():%Y-%m-%d})
1,054 PRC notification records (master_breach_dataset.xlsx, git-tracked)
 -> Stage 2 entity resolution + Gate 1 verdicts (scripts/150-151): 758 records retained
 -> Stage 3 CIK+date dedup (scripts/152): 524 firm-day events
 -> Gate 2 chain verdicts (scripts/153): 489 events
 -> Stage 4 treatment from committed registry snapshot (scripts/154): {int(ev['fcc_form499'].sum())} treated
 -> Stage 5 outcomes, recovered conventions (scripts/155): {int(ev['has_crsp_data'].sum())} with CRSP data
 -> Stage 6 keyed covariates (scripts/156): regression sample {len(reg)}
No positional joins anywhere. Item 5.02 from live EDGAR submissions (cached).
""", encoding='utf-8')

with open('outputs/rebuild/STAGE6_REPORT.md', 'w', encoding='utf-8') as f:
    f.write('# Stage 6 Report\n\n' + '\n'.join(L) + '\n')
log('Saved: CANONICAL_V3.csv, CANONICAL_V3_LINEAGE.md, STAGE6_REPORT.md')
