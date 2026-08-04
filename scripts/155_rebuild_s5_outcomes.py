"""
REBUILD DIRECTIVE v2 — STAGE 5: MARKET OUTCOMES (recovered conventions)
========================================================================
Every market-derived column computed fresh on the Gate 2 event set under the
recovered script-20 conventions, stated from code:
  CAR:  sum of daily (ret - vwretd) x100 over TRADING days [0,+30] ([0,+5] for
        car_5d), event day = trading day NEAREST breach_date within a +/-50
        calendar-day pull. BHAR: buy-and-hold difference x100, same windows.
  Volatility: annualized SD of daily raw returns (x sqrt252 x100),
        pre-window calendar days [-40,-1], post [0,+30]; volume vols likewise.
Identity layer: CIK -> candidate tickers (SEC company_tickers.json, the
EDGAR-derived cik_ticker_map, and a documented historical map for delisted
registrants) -> PERMNO via CRSP names date windows (fallback: most recent
prior window, documented). Multi-PERMNO tickers (share classes, GTN/LEN class)
resolve to the PERMNO with the higher mean daily volume — deterministic,
documented. Convention identical to recovered code; identifier corrected.

Output: Data/processed/rebuild/stage5_outcomes.csv + outputs/rebuild/STAGE5_REPORT.md
"""

import sys
import json
from datetime import timedelta
from pathlib import Path
import pandas as pd
import numpy as np

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
L = []


def log(m=''):
    print(m)
    L.append(str(m))


log('=' * 90)
log('REBUILD STAGE 5: MARKET OUTCOMES')
log('=' * 90)

ev = pd.read_csv('Data/processed/rebuild/stage4_treated.csv', low_memory=False)
ev['bdt'] = pd.to_datetime(ev['breach_date'])
log(f'\nInput: {len(ev)} events')

# ---- CIK -> candidate tickers ----
with open('Data/edgar/company_tickers.json', encoding='utf-8') as f:
    ct = json.load(f)
cik2tk = {}
for _, rec in (ct.items() if isinstance(ct, dict) else enumerate(ct)):
    cik2tk.setdefault(int(rec['cik_str']), []).append(rec['ticker'])
edgar_map = pd.read_csv('Data/edgar/cik_ticker_map_normalized.csv')
for _, r in edgar_map.iterrows():
    cik2tk.setdefault(int(r['cik']), [])
    if r['ticker'] not in cik2tk[int(r['cik'])]:
        cik2tk[int(r['cik'])].append(r['ticker'])

# Historical/delisted registrants (documented; verified in Gate 1/2 evidence)
MANUAL = {101830: ['S'], 1288776: ['GOOG'], 1011006: ['YHOO', 'AABA'],
          1308161: ['NWSA', 'NWS'], 1105705: ['TWX'], 858339: ['CZR'],
          1553023: ['CONE'], 1002517: ['NUAN'], 1316644: ['AERO'],
          813828: ['PARA', 'VIAC', 'CBS'], 1067837: ['AUD', 'ETM'],
          18926: ['LUMN', 'CTL'], 20520: ['FTR', 'FYBR'], 823768: ['WM', 'WMI'],
          1098659: ['MCCC'], 926480: ['DIS'], 1166691: ['CMCSA'],
          1590895: ['CZR'], 1808065: ['AON'],
          # Altice: current SEC ticker file says OPTU (2025 Optimum rename) —
          # a rename artifact; the CRSP security is ATUS (permno 16753).
          1702780: ['ATUS']}
for cik, tks in MANUAL.items():
    cur = cik2tk.setdefault(cik, [])
    for t in tks:
        if t not in cur:
            cur.append(t)

# ---- ticker -> PERMNO (date-aware) ----
pmap = pd.read_csv('Data/wrds/ticker_permno_mapping.csv')
# WRDS coverage top-up (pre-specified: DIRECTIVE_AMENDMENT_WRDS_TOPUP.md) —
# Sprint (S) and CenturyLink (CTL) securities the retired-identity extract
# never requested; separate files, committed extract untouched.
tp_names = Path('Data/wrds/ticker_permno_topup.csv')
if tp_names.exists():
    pmap = pd.concat([pmap, pd.read_csv(tp_names)[pmap.columns.intersection(
        ['ticker', 'permno', 'comnam', 'namedt', 'nameendt']).tolist() or
        ['ticker', 'permno', 'comnam', 'namedt', 'nameendt']]], ignore_index=True)
    log('  WRDS top-up names merged (Sprint S, CenturyLink CTL)')
pmap['namedt'] = pd.to_datetime(pmap['namedt'])
pmap['nameendt'] = pd.to_datetime(pmap['nameendt'])
by_ticker = {t: g.sort_values('namedt') for t, g in pmap.groupby('ticker')}

crsp = pd.read_csv('Data/wrds/crsp_daily_returns.csv',
                   usecols=['permno', 'date', 'ret', 'vol'])
tp_daily = Path('Data/wrds/crsp_daily_topup.csv')
if tp_daily.exists():
    crsp = pd.concat([crsp, pd.read_csv(tp_daily, usecols=['permno', 'date', 'ret', 'vol'])],
                     ignore_index=True)
    log('  WRDS top-up daily rows merged')
mkt = pd.read_csv('Data/wrds/market_indices.csv', usecols=['date', 'vwretd'])
crsp['date'] = pd.to_datetime(crsp['date'])
mkt['date'] = pd.to_datetime(mkt['date'])
crsp = crsp.merge(mkt, on='date', how='left')
crsp['ar'] = (crsp['ret'] - crsp['vwretd']) * 100
pgroups = {p: g.sort_values('date').reset_index(drop=True) for p, g in crsp.groupby('permno')}
pvol = {p: g['vol'].mean() for p, g in crsp.groupby('permno')}


def find_permno(cik, bdt):
    for t in cik2tk.get(int(cik), []):
        g = by_ticker.get(t)
        if g is None:
            continue
        inwin = g[(g['namedt'] <= bdt) & (bdt <= g['nameendt'])]
        pool = inwin if len(inwin) else g[g['namedt'] <= bdt].tail(1)
        if len(pool) == 0:
            continue
        if len(pool) > 1:  # share classes: higher mean daily volume, documented
            pool = pool.assign(_v=[pvol.get(p, 0) for p in pool['permno']]).nlargest(1, '_v')
        return int(pool['permno'].iloc[0]), t, ('window' if len(inwin) else 'fallback-prior')
    return None, None, None


def outcomes(permno, bdt):
    g = pgroups.get(permno)
    o = dict(car_5d=np.nan, car_30d=np.nan, bhar_5d=np.nan, bhar_30d=np.nan,
             return_volatility_pre=np.nan, return_volatility_post=np.nan,
             volume_volatility_pre=np.nan, volume_volatility_post=np.nan,
             volatility_change=np.nan)
    if g is None:
        return o
    w = g[(g['date'] >= bdt - timedelta(days=50)) & (g['date'] <= bdt + timedelta(days=50))].reset_index(drop=True)
    if len(w) >= 10:
        pos = (w['date'] - bdt).abs().idxmin()
        p5, p30 = min(len(w) - 1, pos + 5), min(len(w) - 1, pos + 30)
        if p5 > pos:
            w5, w30 = w.iloc[pos:p5 + 1], w.iloc[pos:p30 + 1]
            o['car_5d'] = round(w5['ar'].sum(), 4)
            o['car_30d'] = round(w30['ar'].sum(), 4)
            o['bhar_5d'] = round((((1 + w5['ret']).prod() - 1) - ((1 + w5['vwretd']).prod() - 1)) * 100, 4)
            o['bhar_30d'] = round((((1 + w30['ret']).prod() - 1) - ((1 + w30['vwretd']).prod() - 1)) * 100, 4)
    pre = g[(g['date'] >= bdt - timedelta(days=40)) & (g['date'] <= bdt - timedelta(days=1))]
    post = g[(g['date'] >= bdt) & (g['date'] <= bdt + timedelta(days=30))]
    if len(pre) >= 10 and len(post) >= 10:
        o['return_volatility_pre'] = round(pre['ret'].std() * np.sqrt(252) * 100, 4)
        o['return_volatility_post'] = round(post['ret'].std() * np.sqrt(252) * 100, 4)
        o['volatility_change'] = round(o['return_volatility_post'] - o['return_volatility_pre'], 4)
        if pre['vol'].notna().sum() > 5 and post['vol'].notna().sum() > 5:
            o['volume_volatility_pre'] = round(pre['vol'].std(), 2)
            o['volume_volatility_post'] = round(post['vol'].std(), 2)
    return o


log('Resolving PERMNOs and computing outcomes...')
rows = []
for _, r in ev.iterrows():
    permno, tkr, how = find_permno(r['final_cik'], r['bdt'])
    o = outcomes(permno, r['bdt']) if permno else outcomes(-1, r['bdt'])
    o.update(permno=permno, matched_ticker=tkr, permno_match=how)
    rows.append(o)
out = pd.concat([ev.drop(columns=['bdt']).reset_index(drop=True),
                 pd.DataFrame(rows)], axis=1)
out['has_crsp_data'] = out['car_30d'].notna().astype(int)

n_c = int(out['has_crsp_data'].sum())
n_t = int(out.loc[out['has_crsp_data'] == 1, 'fcc_form499'].sum())
log(f'\nCRSP coverage: {n_c}/{len(out)} events with car_30d '
    f'({int(out["permno"].notna().sum())} with PERMNO)')
log(f'Treated with CRSP data: {n_t} events / '
    f'{out.loc[(out["has_crsp_data"]==1)&(out["fcc_form499"]==1),"final_cik"].nunique()} parent CIKs')
nomatch = out[out['permno'].isna()]
log(f'No PERMNO (die at CRSP, expected for private registrants): {len(nomatch)} events, '
    f'{nomatch["final_cik"].nunique()} CIKs')
tt = nomatch[nomatch['fcc_form499'] == 1]
if len(tt):
    log('  TREATED events without PERMNO, classified:')
    NO_EQUITY = {(1283699, True): 'pre-5/2013 T-Mobile: no US public equity at date',
                 (1098659, True): 'Mediacom private since 3/2011: no equity at date'}
    for _, r in tt.iterrows():
        bdt = pd.Timestamp(r['breach_date'])
        if r['final_cik'] == 1283699 and bdt < pd.Timestamp('2013-05-01'):
            why = 'NO-EQUITY-AT-DATE (pre-2013 T-Mobile)'
        elif r['final_cik'] == 1098659 and bdt >= pd.Timestamp('2011-03-01'):
            why = 'NO-EQUITY-AT-DATE (Mediacom private since 2011)'
        else:
            why = 'EXTRACT-GAP (security absent from committed WRDS extract — S/CTL era; NAMED DECISION: optional WRDS top-up pull would restore)'
        log(f'    {r["org_name"]} | {r["breach_date"]} | CIK {r["final_cik"]} | {why}')

out.to_csv('Data/processed/rebuild/stage5_outcomes.csv', index=False)
with open('outputs/rebuild/STAGE5_REPORT.md', 'w', encoding='utf-8') as f:
    f.write('# Stage 5 Report\n\n' + '\n'.join(L) + '\n')
log('\nSaved: stage5_outcomes.csv, STAGE5_REPORT.md')
