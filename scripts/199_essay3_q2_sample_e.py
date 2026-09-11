"""
ESSAY 3 QUERY 2 — STAGE 2 PART E: SAMPLE, OUTCOME-DATA REQUIREMENT, LEDGER, ANCHOR DIAGNOSTIC (NEW)
===================================================================================================
Runs on today's CANONICAL_V3 (Tim, 2026-09-11: Essay 3 on the current file; constants_v3.json untouched).
Outcome = final classifier v2 (scripts/195, commit 6f7be7a) via outputs/essay3_q2/c2_outcomes_events.csv.

E1  Outcome-data requirement: an event enters only if its resolved (outcome) CIK filed >= 1 8-K of any kind in
    [t0 - 730d, t0 + 180d], t0 = reported_date. The four Query 1 structural zeros are resolved first:
      Nokia (924613)      foreign private issuer (20-F/6-K; files no 8-K)          -> EXCLUDED (no 8-K filer exists)
      Walt Disney (926480) no-action-letter entry only (13 NO ACT, 2001-2006)       -> FIXED: outcome CIK 1001039
      Aon plc (1808065) x2 2020 Irish entity used for registrations only           -> FIXED: outcome CIK 315293
    For fixed events the 5.02 filings of the correct filer are fetched, classified with the frozen v2 and turned
    into outcomes by the same rules as scripts/195 (helper validated: it reproduces v2's committed outcomes for
    every T-Mobile event exactly).
    Prior 12-month market-adjusted return ending t0 - 1: buy-and-hold CRSP return minus buy-and-hold CRSP VW
    index over trading days in [t0 - 365d, t0 - 1d]; missing if fewer than 150 daily returns.
E2  Ledger from 1,054 records to the analysis sample, with treated events, parent CIKs and pre-rule counts at
    every event level; the 341st event is named.
E3  Anchor diagnostic: share of events whose breach-anchored 180-day window ends before reported_date.
Outputs: outputs/essay3_q2/e1_cik_resolution.csv, e_ledger.csv, e_analysis_sample.csv, 199_sample.log
"""

import sys
import json
import time
import importlib.util
from datetime import timedelta
from pathlib import Path
import numpy as np
import pandas as pd
import requests

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
OUT = Path('outputs/essay3_q2')
TXT = Path('Data/edgar/item5_02_text')
OCC = Path('Data/edgar/essay3_q2_outcome_cik_cache')
OCC.mkdir(parents=True, exist_ok=True)
H = {'User-Agent': 'Academic Research (University of South Alabama) timothy.spivey@southalabama.edu'}
RULE = pd.Timestamp('2007-12-08')
L = []


def log(m=''):
    print(m, flush=True)
    L.append(str(m))


def hdr(t):
    log('\n' + '=' * 100 + '\n' + t + '\n' + '=' * 100)


spec = importlib.util.spec_from_file_location('clf2', 'scripts/195_essay3_q2_classifier_v2.py')
clf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(clf)

ev = pd.read_csv('Data/processed/rebuild/CANONICAL_V3.csv', low_memory=False)
ev['bdt'] = pd.to_datetime(ev['breach_date'])
ev['rdt'] = pd.to_datetime(ev['reported_date'], errors='coerce')
sc = pd.read_csv(OUT / 'b_scope_events.csv', low_memory=False)
O2 = pd.read_csv(OUT / 'c2_outcomes_events.csv')
KEY = ['final_cik', 'breach_date']

RESOLVE = {924613: ('EXCLUDE', None, 'Nokia Corp: foreign private issuer (20-F/6-K); files no Form 8-K, so Item 5.02 '
                                     'departures are never reported; no correct 8-K filer exists'),
           926480: ('FIX', 1001039, 'CIK 926480 holds only 13 no-action letters (2001-2006); The Walt Disney Company '
                                    'filed its 8-Ks in 2008 under CIK 1001039 (later TWDC Enterprises 18 Corp)'),
           1808065: ('FIX', 315293, 'CIK 1808065 (Aon plc, Ireland, 2020) is used for securities registrations only; '
                                    'Aon files its 8-Ks under CIK 315293')}


# ------------------------------------------------------------------ submissions + 8-K lists
def pages_for(cik):
    fp = Path(f'Data/edgar/rebuild_submissions_cache/{cik}.json')
    if fp.exists():
        return json.loads(fp.read_text())
    fp = OCC / f'{cik}.json'
    if not fp.exists():
        pages = []
        r = requests.get(f'https://data.sec.gov/submissions/CIK{int(cik):010d}.json', headers=H, timeout=30)
        time.sleep(0.2)
        d = r.json()
        pages.append(d['filings']['recent'])
        for extra in d['filings'].get('files', []):
            r2 = requests.get(f'https://data.sec.gov/submissions/{extra["name"]}', headers=H, timeout=30)
            time.sleep(0.2)
            pages.append(r2.json())
        fp.write_text(json.dumps(pages))
    return json.loads(fp.read_text())


def filings_df(cik):
    rows = []
    for pg in pages_for(cik):
        n = len(pg.get('form', []))
        for i in range(n):
            rows.append(dict(form=pg['form'][i], filing_date=pg['filingDate'][i],
                             items=(pg.get('items') or [''] * n)[i] or '', accession=pg['accessionNumber'][i],
                             primary_doc=pg['primaryDocument'][i]))
    f = pd.DataFrame(rows)
    f['fdt'] = pd.to_datetime(f['filing_date'])
    return f


# ------------------------------------------------------------------ outcome helper (same rules as scripts/195)
def outcomes_for(cik, fil, events):
    """fil: 5.02 filings (accession, filing_date, local_file) of one outcome CIK; events: rows with bdt, rdt."""
    frows, prow = [], []
    for _, r in fil.iterrows():
        t = clf.to_text(Path(r['local_file']).read_bytes())
        raw = clf.section_502(t)
        sec = clf.strip_caption(raw if raw else t[:20000])
        codes, persons, refs = clf.classify(sec)
        frows.append(dict(accession=r['accession'], fdt=pd.Timestamp(r['filing_date']), ref_list=refs, **codes))
        for p in persons:
            prow.append(dict(accession=r['accession'], fdt=pd.Timestamp(r['filing_date']), **p))
    F = pd.DataFrame(frows)
    PR = pd.DataFrame(prow)
    E = pd.DataFrame(columns=['grp', 'pkey', 'first_date', 'first_accession', 'is_ceo', 'director_only'])
    if len(PR) and (PR['action'] == 'departure').any():
        PR = PR[PR['action'] == 'departure'].copy()
        PR['grp'] = np.where(PR['role_class'].isin(list(clf.EXEC_CLASSES)), 'exec', 'director')
        PR['pkey'] = PR['person'].apply(clf.person_key)
        evs = []
        for grp, g in PR.groupby('grp'):
            for key, gk in g[g['pkey'].notna()].groupby('pkey'):
                cur = None
                for _, r in gk.sort_values('fdt').iterrows():
                    if cur is None or (r['fdt'] - cur['last']).days > 540:
                        if cur is not None:
                            evs.append(cur)
                        cur = dict(grp=grp, pkey=key, first=r['fdt'], last=r['fdt'], rows=[r])
                    else:
                        cur['last'] = r['fdt']
                        cur['rows'].append(r)
                evs.append(cur)
            for _, r in g[g['pkey'].isna()].iterrows():
                evs.append(dict(grp=grp, pkey=None, first=r['fdt'], last=r['fdt'], rows=[r]))
        E = pd.DataFrame([dict(grp=v['grp'], pkey=v['pkey'], first_date=v['first'],
                               first_accession=min(v['rows'], key=lambda r: r['fdt'])['accession'],
                               is_ceo=int(any(r['role_class'] == 'CEO' for r in v['rows']))) for v in evs])
        E['director_only'] = 1
        exk = E[E['grp'] == 'exec']
        for i, r in E[(E['grp'] == 'director') & E['pkey'].notna()].iterrows():
            m = exk[exk['pkey'] == r['pkey']]
            if len(m) and (m['first_date'] - r['first_date']).abs().dt.days.min() <= 540:
                E.at[i, 'director_only'] = 0
    Fx = F.set_index('accession') if len(F) else F
    out = []
    for _, e in events.iterrows():
        rec = {}
        ex = E[E['grp'] == 'exec']
        dr = E[(E['grp'] == 'director') & (E['director_only'] == 1)]
        for anc, t0 in [('rd', e['rdt']), ('bd', e['bdt'])]:
            for w in (30, 90, 180):
                x = F[(F['fdt'] > t0) & (F['fdt'] <= t0 + timedelta(days=w))] if len(F) else F
                rec[f'any_502_{w}_{anc}'] = int(len(x) > 0)
                rec[f'rs_exec_departure_{w}_{anc}'] = int(len(x) and x['exec_departure'].sum() > 0)
                rec[f'rs_ceo_departure_{w}_{anc}'] = int(len(x) and x['ceo_departure'].sum() > 0)
                rec[f'rs_director_departure_{w}_{anc}'] = int(len(x) and x['director_departure'].sum() > 0)
                inw = lambda d: d[(d['first_date'] > t0) & (d['first_date'] <= t0 + timedelta(days=w))]
                xe = inw(ex)
                rec[f'exec_departure_{w}_{anc}'] = int(len(xe) > 0)
                rec[f'ceo_departure_{w}_{anc}'] = int((xe['is_ceo'] == 1).any())
                rec[f'director_departure_{w}_{anc}'] = int(len(inw(dr)) > 0)
                rec[f'exec_departure_nopre_{w}_{anc}'] = int(any(
                    clf.pre_announced(Fx.loc[a], Fx.loc[a, 'ref_list'], t0) == 'N' for a in xe['first_accession']))
            x = ex[(ex['first_date'] > t0) & (ex['first_date'] <= t0 + timedelta(days=180))]
            rec[f'days_to_first_exec_departure_{anc}'] = (x['first_date'].min() - t0).days if len(x) else np.nan
            pl = ex[(ex['first_date'] > t0 - timedelta(days=180)) & (ex['first_date'] <= t0)]
            rec[f'placebo_exec_departure_{anc}'] = int(len(pl) > 0)
            bl = ex[(ex['first_date'] >= t0 - timedelta(days=730)) & (ex['first_date'] <= t0 - timedelta(days=181))]
            rec[f'baseline_exec_departures_{anc}'] = len(bl)
            rec[f'baseline_exec_rate_py_{anc}'] = round(len(bl) / (550 / 365), 4)
        out.append(rec)
    return pd.DataFrame(out, index=events.index)


hdr('E1 — helper validation: rebuild every T-Mobile outcome and compare with v2\'s committed outcomes')
S = pd.read_csv(OUT / 'b_scope_filings.csv', dtype={'accession': str})
tm_ev = sc[sc['final_cik'] == 1283699].copy()
tm_ev['bdt'], tm_ev['rdt'] = pd.to_datetime(tm_ev['breach_date']), pd.to_datetime(tm_ev['reported_date'])
got = outcomes_for(1283699, S[S['cik'] == 1283699], tm_ev)
ref = tm_ev[KEY].merge(O2, on=KEY, how='left')
ref.index = tm_ev.index
cols = [c for c in got.columns if c in ref.columns]
bad = [(c, int((got[c].fillna(-9).values != ref[c].fillna(-9).values).sum())) for c in cols]
bad = [b for b in bad if b[1]]
log(f'T-Mobile events {len(tm_ev)}; columns compared {len(cols)}; mismatching columns: {bad or "none"}')
assert not bad, 'helper does not reproduce scripts/195 — STOP'

hdr('E1 — structural zeros: resolution')
res_rows, repl = [], {}
for cik, (act, new, why) in RESOLVE.items():
    evs = sc[sc['final_cik'] == cik].copy()
    evs['bdt'], evs['rdt'] = pd.to_datetime(evs['breach_date']), pd.to_datetime(evs['reported_date'])
    for _, e in evs.iterrows():
        res_rows.append(dict(final_cik=cik, org_name=e['org_name'], breach_date=e['breach_date'],
                             reported_date=e['reported_date'], treated=int(e['fcc_form499']), action=act,
                             outcome_cik=new, reason=why))
    if act != 'FIX':
        continue
    f = filings_df(new)
    lo = min(evs[['bdt', 'rdt']].min()) - timedelta(days=730)
    hi = max(evs[['bdt', 'rdt']].max()) + timedelta(days=180)
    f5 = f[f['form'].str.startswith('8-K') & f['items'].str.contains('5.02', regex=False) &
           (f['fdt'] >= lo) & (f['fdt'] <= hi)].drop_duplicates('accession').copy()
    locs = []
    for _, r in f5.iterrows():
        dest = TXT / str(new) / f"{r['accession']}_{r['primary_doc']}"
        dest.parent.mkdir(parents=True, exist_ok=True)
        if not dest.exists():
            rr = requests.get(f"https://www.sec.gov/Archives/edgar/data/{new}/{r['accession'].replace('-', '')}/"
                              f"{r['primary_doc']}", headers=H, timeout=30)
            time.sleep(0.2)
            dest.write_bytes(rr.content)
        locs.append(str(dest))
    f5['local_file'] = locs
    log(f'{cik} -> {new}: {len(f5)} Item 5.02 filings of the correct filer in [{lo.date()}, {hi.date()}] classified')
    repl.update({(cik, b): row for b, row in zip(evs['breach_date'], outcomes_for(new, f5, evs).to_dict('records'))})
R1 = pd.DataFrame(res_rows)
R1.to_csv(OUT / 'e1_cik_resolution.csv', index=False)
log(R1.to_string(index=False))

# merged outcomes: v2 committed, with the fixed events replaced
OUTC = sc[KEY + ['org_name', 'reported_date', 'fcc_form499', 'permno', 'immediate_disclosure', 'firm_size_log',
                 'leverage', 'roa', 'prior_breaches_1yr', 'health_breach']].merge(
    O2.drop(columns=['reported_date', 'fcc_form499']), on=KEY, how='left')
OUTC['outcome_cik'] = OUTC['final_cik']
for (cik, b), rec in repl.items():
    i = OUTC.index[(OUTC['final_cik'] == cik) & (OUTC['breach_date'] == b)][0]
    for c, v in rec.items():
        if c in OUTC.columns:
            OUTC.at[i, c] = v
    OUTC.at[i, 'outcome_cik'] = RESOLVE[cik][1]
    log(f'  replaced outcomes for {cik} {b}: exec_departure_180_rd={rec["exec_departure_180_rd"]}, '
        f'any_502_180_rd={rec["any_502_180_rd"]}')

# 8-K activity requirement
OUTC['bdt'], OUTC['rdt'] = pd.to_datetime(OUTC['breach_date']), pd.to_datetime(OUTC['reported_date'])
fcache = {}
has8k = []
for _, r in OUTC.iterrows():
    oc = int(r['outcome_cik'])
    if RESOLVE.get(int(r['final_cik']), ('',))[0] == 'EXCLUDE':
        has8k.append(0)
        continue
    if oc not in fcache:
        fcache[oc] = filings_df(oc)
    f = fcache[oc]
    has8k.append(int((f['form'].str.startswith('8-K') & (f['fdt'] >= r['rdt'] - timedelta(days=730)) &
                      (f['fdt'] <= r['rdt'] + timedelta(days=180))).any()))
OUTC['has_8k_activity'] = has8k

# ------------------------------------------------------------------ prior 12-month market-adjusted return
hdr('E1 — prior 12-month market-adjusted return (CRSP daily; VW index)')
perms = set(OUTC['permno'].dropna().astype(int))
chunks = []
for fp in ['Data/wrds/crsp_daily_returns.csv', 'Data/wrds/crsp_daily_topup.csv', 'Data/wrds/crsp_daily_topup_dish.csv']:
    if Path(fp).exists():
        for ch in pd.read_csv(fp, usecols=['permno', 'date', 'ret'], chunksize=2_000_000):
            chunks.append(ch[ch['permno'].isin(perms)])
cd = pd.concat(chunks).drop_duplicates(['permno', 'date'])
cd['date'] = pd.to_datetime(cd['date'])
cd['ret'] = pd.to_numeric(cd['ret'], errors='coerce')
mk = pd.read_csv('Data/wrds/market_indices.csv', usecols=['date', 'vwretd'])
mk['date'] = pd.to_datetime(mk['date'])
mk = mk.set_index('date')['vwretd']
by_p = {p: g.set_index('date')['ret'].sort_index() for p, g in cd.groupby('permno')}


def prior_ret(permno, t0):
    if pd.isna(permno) or int(permno) not in by_p:
        return np.nan, 0
    s = by_p[int(permno)]
    w = s[(s.index >= t0 - timedelta(days=365)) & (s.index <= t0 - timedelta(days=1))].dropna()
    if len(w) < 150:
        return np.nan, len(w)
    m = mk.reindex(w.index).fillna(0.0)
    return float(np.prod(1 + w.values) - np.prod(1 + m.values)), len(w)


for anc, col in [('rd', 'rdt'), ('bd', 'bdt')]:
    vals = [prior_ret(p, t) for p, t in zip(OUTC['permno'], OUTC[col])]
    OUTC[f'prior12m_mktadj_ret_{anc}'] = [v[0] for v in vals]
    OUTC[f'prior12m_ndays_{anc}'] = [v[1] for v in vals]
log(f"prior-return available (rd anchor): {int(OUTC['prior12m_mktadj_ret_rd'].notna().sum())} of {len(OUTC)}; "
    f"(bd anchor): {int(OUTC['prior12m_mktadj_ret_bd'].notna().sum())}")
log(OUTC['prior12m_mktadj_ret_rd'].describe().round(4).to_string())

# SIC2 and year (for F3)
s2 = pd.read_csv('Data/processed/rebuild/stage2_signed.csv', low_memory=False)
sic = (s2.dropna(subset=['final_cik']).assign(sic=lambda x: pd.to_numeric(x['sic'], errors='coerce'))
       .dropna(subset=['sic']).groupby('final_cik')['sic'].agg(lambda s: s.mode().iloc[0]))
OUTC['sic2'] = (OUTC['final_cik'].map(sic) // 100)
OUTC['reported_year'] = OUTC['rdt'].dt.year
OUTC['breach_year'] = OUTC['bdt'].dt.year

# ------------------------------------------------------------------ E2 ledger
hdr('E2 — ATTRITION LEDGER (1,054 records -> Essay 3 analysis sample)')
s3n = len(pd.read_csv('Data/processed/rebuild/stage3_events.csv'))
s4n = len(pd.read_csv('Data/processed/rebuild/stage4_input.csv'))
crsp = ev[ev['has_crsp_data'] == 1]
cov = crsp.dropna(subset=['firm_size_log', 'leverage', 'roa'])
q1 = crsp.dropna(subset=['fcc_form499', 'immediate_disclosure', 'prior_breaches_1yr', 'health_breach',
                         'firm_size_log', 'leverage', 'roa'])
extra = cov[~cov.set_index(KEY).index.isin(q1.set_index(KEY).index)]
A1 = OUTC[OUTC['has_8k_activity'] == 1]
A2 = A1.dropna(subset=['prior12m_mktadj_ret_rd'])
FAM = {101830: 1283699}


def lvl(name, d, note=''):
    t = d[d['fcc_form499'] == 1]
    pre = d[pd.to_datetime(d['breach_date']) < RULE]
    return dict(step=name, N=len(d), treated=len(t), control=len(d) - len(t),
                treated_parent_ciks=t['final_cik'].nunique(),
                treated_corporate_families=t['final_cik'].map(lambda c: FAM.get(c, c)).nunique(),
                pre_rule_treated=int((pre['fcc_form499'] == 1).sum()), pre_rule_control=int((pre['fcc_form499'] == 0).sum()),
                note=note)


led = [dict(step='PRC notification records (master_breach_dataset.xlsx)', N=1054, note='records; treatment undefined'),
       dict(step='Gate 1: signed parent CIK', N=758, note='records'),
       dict(step='Stage 3: CIK+date firm-day events', N=s3n, note='events'),
       dict(step='Gate 2 adjacency collapse', N=s4n, note='events'),
       lvl('Stage 4/5 canonical events (CANONICAL_V3)', ev, 'equity re-parenting re-collapse (-2)'),
       lvl('CRSP data (has_crsp_data)', crsp),
       lvl('Compustat covariates (size, leverage, ROA) = Query 2 scope', cov,
           f'Query 1 sample was {len(q1)}; +{len(extra)}: ' + '; '.join(
               f"{r['org_name']} {r['breach_date']} (immediate_disclosure missing)" for _, r in extra.iterrows())),
       lvl('Outcome-data requirement (>=1 8-K in [t0-730d, t0+180d], outcome CIK)', A1,
           'Nokia excluded (no 8-K filer); Disney, Aon x2 fixed to correct filer CIK'),
       lvl('Prior 12-month market-adjusted return available (>=150 daily returns)', A2, 'ANALYSIS SAMPLE')]
LED = pd.DataFrame(led)
LED.to_csv(OUT / 'e_ledger.csv', index=False)
log(LED.to_string(index=False))
assert len(A2) == LED.iloc[-1]['N']
drop8k = OUTC[OUTC['has_8k_activity'] == 0]
log(f"\nOutcome-data requirement removes {len(drop8k)} (treated {int(drop8k['fcc_form499'].sum())}, control "
    f"{int((drop8k['fcc_form499'] == 0).sum())}): " + '; '.join(f"{r['org_name']} {r['breach_date']}" for _, r in drop8k.iterrows()))
dropr = A1[A1['prior12m_mktadj_ret_rd'].isna()]
log(f"Prior-return requirement removes {len(dropr)} (treated {int(dropr['fcc_form499'].sum())}): " +
    '; '.join(f"{r['org_name']} {r['reported_date'][:10]} ({int(r['prior12m_ndays_rd'])} days)" for _, r in dropr.iterrows()))

# ------------------------------------------------------------------ E3
hdr('E3 — anchor diagnostic: breach-anchored 180-day window ends before reported_date')
A2 = A2.copy()
A2['bd180_before_rd'] = ((A2['bdt'] + timedelta(days=180)) < A2['rdt']).astype(int)
for g, lab in [(1, 'treated'), (0, 'control')]:
    x = A2[A2['fcc_form499'] == g]
    log(f"  {lab}: {int(x['bd180_before_rd'].sum())}/{len(x)} = {x['bd180_before_rd'].mean():.3f}")
OUTC['in_analysis_sample'] = OUTC.set_index(KEY).index.isin(A2.set_index(KEY).index).astype(int)
OUTC['bd180_before_rd'] = ((OUTC['bdt'] + timedelta(days=180)) < OUTC['rdt']).astype(int)
OUTC.drop(columns=['bdt', 'rdt']).to_csv(OUT / 'e_analysis_sample.csv', index=False)
log(f"\nWritten e_analysis_sample.csv: {len(OUTC)} scope events, {int(OUTC['in_analysis_sample'].sum())} in the analysis sample")
(OUT / '199_sample.log').write_text('\n'.join(L) + '\n', encoding='utf-8')
