"""
ESSAY 3 QUERY 1 — DISCOVERY COMPUTATIONS (NEW; read-only on every existing artifact)
====================================================================================
Supports outputs/ESSAY3_QUERY1_REPORT.md. Changes NOTHING upstream: no dataset
column, no committed table, no constant. Offline (reads committed caches only).

  B2  cache schemas (script-46 pickle, v3 submissions cache) + raw examples
  B3  flags-only verdict; re-pull scope for the Essay 3 sample (8-K and 5.02
      counts in the event windows, bytes, request-time estimate); co-listed
      item tallies (descriptive); base rates re-derived from the cache
  C1-C4  first-stage vintages; zero-delay shares; reconciliation vs Essay 2
  D1-D3  attrition ledger, treatment counts by level, pre-rule events
  E1-E2  T-Mobile (CIK 1283699) events and every in-window 5.02 filing
  F1-F3  FE / clustering / controls facts
  G   reconciliation of the v3 H6 constants (t, p, MDE) + re-estimation

Outputs: outputs/essay3_q1/*.csv + outputs/essay3_q1/183_discovery.log
"""

import sys
import json
import glob
import pickle
from datetime import timedelta
from pathlib import Path
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
OUT = Path('outputs/essay3_q1')
OUT.mkdir(parents=True, exist_ok=True)
L = []


def log(m=''):
    print(m)
    L.append(str(m))


def hdr(t):
    log('\n' + '=' * 90)
    log(t)
    log('=' * 90)


TREAT = 'fcc_form499'
HVARS = [TREAT, 'immediate_disclosure', 'prior_breaches_1yr', 'health_breach']
CONTROLS = HVARS + ['firm_size_log', 'leverage', 'roa']          # 158:54-55
X_NOTIME = ['prior_breaches_1yr', 'health_breach', 'firm_size_log', 'leverage', 'roa']
RULE = pd.Timestamp('2007-12-08')
TMUS = 1283699
METRO_END = pd.Timestamp('2013-04-29')   # CIK 1283699 = MetroPCS through this date
CACHE = Path('Data/edgar/rebuild_submissions_cache')

ev = pd.read_csv('Data/processed/rebuild/CANONICAL_V3.csv', low_memory=False)
ev['bdt'] = pd.to_datetime(ev['breach_date'])
crsp = ev[ev['has_crsp_data'] == 1].copy()
reg1 = crsp.dropna(subset=['car_30d'] + CONTROLS).copy()        # Essay 1 level (158:60)
reg3 = crsp.dropna(subset=CONTROLS).copy()                       # Essay 3 level (158:131)
C = json.load(open('outputs/rebuild/constants_v3.json'))


def lvl(d):
    t = d[d[TREAT] == 1]
    return len(d), len(t), t['org_name'].nunique(), t['final_cik'].nunique()


# =============================== D1 =========================================
hdr('D1 — ESSAY 3 ATTRITION LEDGER (NEW, scripts/183)')
s2 = pd.read_csv('Data/processed/rebuild/stage2_signed.csv', low_memory=False)
s3 = pd.read_csv('Data/processed/rebuild/stage3_events.csv', low_memory=False)
s4 = pd.read_csv('Data/processed/rebuild/stage4_input.csv', low_memory=False)
s5 = pd.read_csv('Data/processed/rebuild/stage5_outcomes.csv', low_memory=False)
led = [('PRC notification records (stage2_signed.csv rows)', len(s2)),
       ('Gate 1: records with a signed parent CIK (final_cik non-null)', int(s2['final_cik'].notna().sum())),
       ('Stage 3: CIK+date firm-day events (stage3_events.csv)', len(s3)),
       ('Gate 2 chain collapse (stage4_input.csv)', len(s4)),
       ('Stage 4/5 event set (stage5_outcomes.csv = CANONICAL_V3.csv rows)', len(ev)),
       ('has_crsp_data == 1', len(crsp))]
d = crsp.copy()
for c in CONTROLS:
    d = d.dropna(subset=[c])
    led.append((f'  non-missing {c}', len(d)))
led.append(('Essay 3 regression sample (158:131 rule, current CANONICAL_V3)', len(reg3)))
led.append(('  [succession/outcome-data requirement: NONE imposed — see below]', len(reg3)))
prev = None
rows = []
for name, n in led:
    lost = '' if prev is None else prev - n
    rows.append({'step': name, 'n': n, 'lost': lost})
    log(f'  {name:<70} {n:>5}  {"" if prev is None else f"(-{prev - n})"}')
    prev = n
pd.DataFrame(rows).to_csv(OUT / 'd1_attrition_ledger.csv', index=False)
assert len(reg3) == prev
log(f'  CLOSING CHECK: ledger end {prev} == len(reg3) {len(reg3)}: {prev == len(reg3)}')
log(f'  Essay 1 level on the same file (adds car_30d): {len(reg1)}; Essay 3 - Essay 1 = {len(reg3) - len(reg1)}')
log(f'  constants_v3.json N_essay3 = {C["N_essay3"]} (stale vintage); current file gives {len(reg3)}')
dish = reg3[reg3['final_cik'] == 1001082]
log(f'  DISH (CIK 1001082) rows in current Essay 3 sample: {len(dish)} '
    f'{dish[["breach_date", TREAT]].values.tolist()}')
r338 = reg3[reg3['final_cik'] != 1001082]
log(f'  Current sample minus DISH: N={len(r338)}, treated {int(r338[TREAT].sum())}')

# outcome-data requirement: events where the CIK shows no 8-K activity at all
cache_mtime = pd.Timestamp.fromtimestamp(max(p.stat().st_mtime for p in CACHE.glob('*.json')))
pages_by_cik = {}
for p in CACHE.glob('*.json'):
    pages_by_cik[int(p.stem)] = json.loads(p.read_text())


def filings(cik):
    out = []
    for pg in pages_by_cik.get(int(cik), []):
        n = len(pg.get('form', []))
        for i in range(n):
            out.append({k: (pg[k][i] if k in pg and i < len(pg[k]) else None)
                        for k in ['form', 'filingDate', 'items', 'accessionNumber',
                                  'primaryDocument', 'size', 'primaryDocDescription']})
    f = pd.DataFrame(out)
    if len(f):
        f['fdt'] = pd.to_datetime(f['filingDate'])
    return f


FIL = {c: filings(c) for c in ev['final_cik'].unique()}
no8k = []
for _, r in reg3.iterrows():
    f = FIL[r['final_cik']]
    if len(f) == 0:
        no8k.append(r)
        continue
    k = f[f['form'].str.startswith('8-K') &
          (f['fdt'] > r['bdt'] - timedelta(days=730)) & (f['fdt'] <= r['bdt'] + timedelta(days=180))]
    if len(k) == 0:
        no8k.append(r)
log(f'  Events whose CIK filed NO 8-K of any kind in (t0-730d, t0+180d] (outcome structurally 0, '
    f'not missing): {len(no8k)}')
for r in no8k:
    log(f'    {r["org_name"]} | CIK {r["final_cik"]} | {r["breach_date"]} | treated {r[TREAT]}')
cens = reg3[reg3['bdt'] + timedelta(days=180) > cache_mtime]
log(f'  Cache written {cache_mtime:%Y-%m-%d}; events with t0+180d after that date (right-censored): {len(cens)}')

# =============================== D2 =========================================
hdr('D2 — TREATMENT BY SAMPLE LEVEL (NEW, scripts/183; fcc_form499 from scripts/154)')
for name, dd in [('489-event universe', ev), ('CRSP (has_crsp_data)', crsp),
                 ('Essay 1 regression (adds car_30d)', reg1), ('Essay 3 regression', reg3)]:
    n, t, o, p = lvl(dd)
    log(f'  {name:<38} N={n:>4} | treated events {t:>3} | orgs {o:>2} | parent CIKs {p:>2}')
tl = (reg3[reg3[TREAT] == 1].groupby(['final_cik', 'org_name']).size()
      .reset_index(name='events').sort_values(['final_cik', 'org_name']))
tl.to_csv(OUT / 'd2_treated_orgs_essay3.csv', index=False)
log('  Treated organizations at the Essay 3 level (org_name | parent CIK | events):')
for _, r in tl.iterrows():
    log(f'    {r["org_name"]:<45} {int(r["final_cik"]):>8}  {r["events"]}')

# =============================== D3 =========================================
hdr('D3 — PRE-RULE EVENTS (breach_date < 2007-12-08) (NEW, scripts/183)')
for name, dd in [('489-event universe', ev), ('CRSP', crsp), ('Essay 3 regression', reg3)]:
    pre = dd[dd['bdt'] < RULE]
    log(f'  {name:<22} pre-rule {len(pre):>3} | treated pre-rule {int(pre[TREAT].sum())}')
log(f'  Essay 3 breach_date range: {reg3["bdt"].min():%Y-%m-%d} .. {reg3["bdt"].max():%Y-%m-%d}')

# =============================== B2 =========================================
hdr('B2 — CACHE SCHEMAS (NEW inspection, scripts/183)')
try:
    pickle.load(open('Data/edgar/8k_item5_02_cache/submissions_cache.pkl', 'rb'))
    log('  script-46 submissions_cache.pkl: loaded')
except Exception as e:
    log(f'  script-46 submissions_cache.pkl: UNREADABLE under current pandas '
        f'({type(e).__name__}); by construction (46:99-122) each value is a DataFrame '
        f'with columns [form, filing_date, items] only.')
ci = pickle.load(open('Data/edgar/8k_item5_02_cache/cache_index.pkl', 'rb'))
log(f'  script-46 cache_index.pkl: dict, {len(ci)} entries; three raw entries:')
for k in list(ci)[:3]:
    log(f'    {k}: {ci[k]}')
pg0 = pages_by_cik[TMUS][0]
log(f'  v3 cache Data/edgar/rebuild_submissions_cache/<cik>.json: list of submissions-API '
    f'filing pages; {len(pages_by_cik)} CIK files; page keys = {list(pg0.keys())}')
f = FIL[TMUS]
ex = f[f['form'].str.startswith('8-K') & f['items'].fillna('').str.contains('5.02', regex=False)].head(3)
log('  Three raw 8-K/5.02 entries (CIK 1283699):')
for _, r in ex.iterrows():
    log('    ' + json.dumps({k: r[k] for k in ['form', 'filingDate', 'items', 'accessionNumber',
                                              'primaryDocument', 'size', 'primaryDocDescription']},
                             default=str))
log('  NO page carries filing text. The `items` field is item-level ("5.02"); EDGAR '
    'metadata has no sub-item (a)-(f) field.')

# =============================== B3 =========================================
hdr('B3 — FLAGS ONLY: RE-PULL SCOPE + DESCRIPTIVES (NEW, scripts/183)')
win = []
for _, r in reg3.iterrows():
    f = FIL[r['final_cik']]
    if len(f) == 0:
        continue
    k = f[f['form'].str.startswith('8-K') & (f['fdt'] > r['bdt']) &
          (f['fdt'] <= r['bdt'] + timedelta(days=180))].copy()
    k['final_cik'] = r['final_cik']
    k['breach_date'] = r['breach_date']
    k['days'] = (k['fdt'] - r['bdt']).dt.days
    k['treated'] = r[TREAT]
    win.append(k)
W = pd.concat(win, ignore_index=True)
W['is502'] = W['items'].fillna('').str.contains('5.02', regex=False)
W.drop(columns=['fdt']).to_csv(OUT / 'b3_window_8k_filings.csv', index=False)
u_all = W.drop_duplicates('accessionNumber')
u502 = W[W['is502']].drop_duplicates('accessionNumber')
log(f'  Essay 3 sample events: {len(reg3)}; event-filing pairs in (t0, t0+180d]: 8-K {len(W)}, '
    f'of which 5.02 {int(W["is502"].sum())}')
log(f'  UNIQUE filings (accessions): all 8-K {len(u_all)}; 8-K listing 5.02 {len(u502)}')
for w in (30, 90):
    log(f'    within {w}d: unique 8-K {W[W["days"] <= w]["accessionNumber"].nunique()}, '
        f'unique 5.02 {W[W["is502"] & (W["days"] <= w)]["accessionNumber"].nunique()}')
log(f'  Submission `size` field (whole filing, bytes): all-8-K {u_all["size"].sum() / 1e6:.0f} MB; '
    f'5.02-only {u502["size"].sum() / 1e6:.0f} MB. Primary document only is smaller.')
for n, lab in [(len(u502), '5.02 only'), (len(u_all), 'all 8-K')]:
    log(f'  Request time, {lab}: {n} primary docs; at SEC 10 req/s ceiling {n / 10 / 60:.1f} min; '
        f'at 0.12s delay + ~0.35s latency {n * 0.47 / 60:.1f} min')
log('  Endpoints: data.sec.gov/submissions/CIK##########.json (ALREADY CACHED, carries '
    'accessionNumber + primaryDocument) -> https://www.sec.gov/Archives/edgar/data/{cik}/'
    '{accession-no-dashes}/{primaryDocument}. Exhibits (EX-99 press releases) would need '
    'the {accession}-index.json per filing (doubles requests).')
# co-listed items (descriptive, not a classifier)
co = u502['items'].fillna('').str.split(',')
tags = {'5.02 only (± 9.01)': co.apply(lambda s: set(s) - {'9.01'} == {'5.02'}),
        'with 5.07 (shareholder vote)': co.apply(lambda s: '5.07' in s),
        'with 5.03 (bylaws)': co.apply(lambda s: '5.03' in s),
        'with 1.01 (material agreement)': co.apply(lambda s: '1.01' in s),
        'with 2.02 (earnings)': co.apply(lambda s: '2.02' in s),
        'with 7.01/8.01 (Reg FD / other)': co.apply(lambda s: bool({'7.01', '8.01'} & set(s)))}
log('  Co-listed items on the unique 5.02 filings (descriptive; not a departure classifier):')
for k, v in tags.items():
    log(f'    {k:<34} {int(v.sum()):>4} ({100 * v.mean():.1f}%)')
# base rates re-derived from the cache vs the stored columns
for w in (30, 90, 180):
    flag = reg3.apply(lambda r: int(((W['final_cik'] == r['final_cik']) &
                                     (W['breach_date'] == r['breach_date']) &
                                     W['is502'] & (W['days'] <= w)).any()), axis=1)
    stored = reg3[f'executive_change_{w}d'].astype(int)
    log(f'  any-5.02 base rate {w:>3}d: stored column {100 * stored.mean():.1f}% '
        f'(treated {100 * stored[reg3[TREAT] == 1].mean():.1f}% / control '
        f'{100 * stored[reg3[TREAT] == 0].mean():.1f}%) | re-derived from cache '
        f'{100 * flag.mean():.1f}% | mismatches {int((flag != stored).sum())}')
cal = Path('outputs/rebuild/calibration_5_02')
sheet = pd.read_csv(cal / 'coding_sheet.csv')
log(f'  Text on disk: {len(list(cal.glob("*.htm")))} primary documents in {cal} (scripts/162, '
    f'seed 42, 339-vintage sample); hand-coded cells filled: '
    f'{int(sheet["departure_related (Y/N)"].notna().sum())}/{len(sheet)}')

# =============================== C =========================================
hdr('C — DISCLOSURE TIMING (NEW, scripts/183)')
d1 = ev.dropna(subset=['disclosure_delay_days'])
fs_all = (d1.loc[d1[TREAT] == 1, 'immediate_disclosure'].mean() -
          d1.loc[d1[TREAT] == 0, 'immediate_disclosure'].mean())
d3 = reg3
fs_r3 = (d3.loc[d3[TREAT] == 1, 'immediate_disclosure'].mean() -
         d3.loc[d3[TREAT] == 0, 'immediate_disclosure'].mean())
log(f'  158:150-154 rule re-run on current CANONICAL_V3 (489-level, delay known): {100 * fs_all:+.2f}pp '
    f'(constants_v3 first_stage_pp = {C["first_stage_pp"]})')
log(f'  Same difference in means at the Essay 3 regression level: {100 * fs_r3:+.2f}pp')

# C3 zero-delay shares
for name, dd in [('489-level (delay known)', d1), ('Essay 3 regression', reg3)]:
    for g, lab in [(1, 'treated'), (0, 'control')]:
        x = dd[dd[TREAT] == g]
        z = int((x['disclosure_delay_days'] == 0).sum())
        rc = int(((x['disclosure_delay_days'] == 0) & (x['delay_recoded'] == 1)).sum())
        log(f'  {name:<24} {lab:<8} zero-delay {z}/{len(x)} ({100 * z / len(x):.1f}%) '
            f'[of which recoded from negative: {rc}]')
    z = int((dd['disclosure_delay_days'] == 0).sum())
    log(f'  {name:<24} pooled   zero-delay {z}/{len(dd)} ({100 * z / len(dd):.1f}%)')


def cv1(y, X, g):
    return sm.OLS(y.astype(float), sm.add_constant(X.astype(float))).fit(
        cov_type='cluster', cov_kwds={'groups': g}, use_t=True)


def row(label, dd, dv, xcols, kind='ols'):
    if kind == 'logit':
        m = sm.Logit(dd[dv].astype(int), sm.add_constant(dd[xcols].astype(float))).fit(disp=0)
        a = m.get_margeff().summary_frame().loc[TREAT]
        return dict(spec=label, dv=dv, n=len(dd), estimator='logit AME (MLE SE)',
                    coef=round(a['dy/dx'], 4), se=round(a['Std. Err.'], 4),
                    p=round(a['Pr(>|z|)'], 4))
    m = cv1(dd[dv], dd[xcols], dd['final_cik'])
    ci = m.conf_int().loc[TREAT]
    return dict(spec=label, dv=dv, n=len(dd), estimator='OLS, CV1 parent-CIK, t(G-1)',
                coef=round(m.params[TREAT], 4), se=round(m.bse[TREAT], 4),
                ci_lo=round(ci[0], 4), ci_hi=round(ci[1], 4), p=round(m.pvalues[TREAT], 4),
                G=dd['final_cik'].nunique(), G1=dd.loc[dd[TREAT] == 1, 'final_cik'].nunique())


r3 = reg3.copy()
r3['delay_log1p'] = np.log1p(r3['disclosure_delay_days'])
r3['delay_log'] = np.log(r3['disclosure_delay_days'].where(r3['disclosure_delay_days'] > 0))
nz3 = r3[r3['disclosure_delay_days'] > 0]
xs = [TREAT] + X_NOTIME
C4 = [row('(1) <=7-day binary, LPM', r3, 'immediate_disclosure', xs),
      row('(1) <=7-day binary, logit', r3, 'immediate_disclosure', xs, 'logit'),
      row('(2) <=7-day binary excl. zero-delay, LPM', nz3, 'immediate_disclosure', xs),
      row('(2) <=7-day binary excl. zero-delay, logit', nz3, 'immediate_disclosure', xs, 'logit'),
      row('(3a) raw delay days', r3, 'disclosure_delay_days', xs),
      row('(3b) log(1+delay)', r3, 'delay_log1p', xs),
      row('(3c) raw delay, non-zero only', nz3, 'disclosure_delay_days', xs),
      row('(3d) log(delay), non-zero only', nz3, 'delay_log', xs)]
log(f'\n  C4 on the Essay 3 regression sample (N={len(r3)}; controls = Essay 3 set minus timing: '
    f'{X_NOTIME}):')
for c in C4:
    log('    ' + ' | '.join(f'{k}={v}' for k, v in c.items()))
# Essay 2 exact specification: first reproduce t16 on Essay 2's own sample, then apply to the
# Essay 3 events that carry Essay 2's controls
e2 = pd.read_csv('outputs/tables/essay2_v2/t1_final_sample.csv', low_memory=False)
e2['delay_log1p'] = np.log1p(e2['disclosure_delay_days'])
X2 = [TREAT, 'e2_pre_sd', 'firm_size_log', 'leverage', 'roa', 'health_breach', 'prior_events']
rep = [row('REPLICATION t16 raw (Essay 2 sample)', e2, 'disclosure_delay_days', X2),
       row('REPLICATION t16 log1p (Essay 2 sample)', e2, 'delay_log1p', X2)]
e2k = e2[['final_cik', 'breach_date', 'e2_pre_sd', 'prior_events']].copy()
r3k = r3.merge(e2k, on=['final_cik', 'breach_date'], how='inner')
nzk = r3k[r3k['disclosure_delay_days'] > 0]
rep += [row('Essay 2 spec on Essay3∩Essay2 events: <=7 binary LPM', r3k, 'immediate_disclosure', X2),
        row('Essay 2 spec on Essay3∩Essay2 events: <=7 binary excl zero, LPM', nzk, 'immediate_disclosure', X2),
        row('Essay 2 spec on Essay3∩Essay2 events: raw delay', r3k, 'disclosure_delay_days', X2),
        row('Essay 2 spec on Essay3∩Essay2 events: log(1+delay)', r3k, 'delay_log1p', X2)]
log(f'\n  Essay 2 specification (controls {X2[1:]}); intersection N={len(r3k)} of {len(r3)} Essay 3 events:')
for c in rep:
    log('    ' + ' | '.join(f'{k}={v}' for k, v in c.items()))
pd.DataFrame(C4 + rep).to_csv(OUT / 'c4_first_stage_reconciliation.csv', index=False)

# =============================== E =========================================
hdr('E — T-MOBILE, CIK 1283699 (NEW, scripts/183)')
tm = ev[ev['final_cik'] == TMUS].sort_values('bdt')
reg3_keys = set(zip(reg3['final_cik'], reg3['breach_date']))
ecols = ['org_name', 'breach_date', 'reported_date', 'n_source_records', 'has_crsp_data',
         'disclosure_delay_days', 'executive_change_30d', 'executive_change_90d',
         'executive_change_180d', 'days_to_first_item_5_02']
tme = tm[ecols].copy()
tme['in_essay3_sample'] = [int((TMUS, b) in reg3_keys) for b in tm['breach_date']]
tme['cik_vintage_at_t0'] = np.where(tm['bdt'] <= METRO_END, 'MetroPCS-era CIK', 'T-Mobile US')
tme.to_csv(OUT / 'e1_tmobile_events.csv', index=False)
log(f'  Events on CIK 1283699: {len(tm)} (source records collapsed: {int(tm["n_source_records"].sum())}); '
    f'in Essay 3 sample: {int(tme["in_essay3_sample"].sum())}; t0 = breach_date (156:199)')
log(tme.to_string(index=False))
F = FIL[TMUS]
F502 = F[F['form'].str.startswith('8-K') & F['items'].fillna('').str.contains('5.02', regex=False)]
onDisk = {p.name.split('_')[2]: p.name for p in cal.glob('*.htm')}
erow = []
for _, r in tm.iterrows():
    k = F502[(F502['fdt'] > r['bdt']) & (F502['fdt'] <= r['bdt'] + timedelta(days=180))]
    for _, x in k.iterrows():
        erow.append({'breach_date': r['breach_date'], 'org_name': r['org_name'],
                     'in_essay3_sample': int((TMUS, r['breach_date']) in reg3_keys),
                     'filing_date': x['filingDate'], 'days_from_t0': (x['fdt'] - r['bdt']).days,
                     'form': x['form'], 'items': x['items'], 'accession': x['accessionNumber'],
                     'primary_doc': x['primaryDocument'],
                     'filer_vintage': 'MetroPCS' if x['fdt'] <= METRO_END else 'T-Mobile US',
                     'text_on_disk': onDisk.get(x['accessionNumber'], '')})
E2 = pd.DataFrame(erow)
E2.to_csv(OUT / 'e2_tmobile_502_filings.csv', index=False)
log(f'\n  Event-filing pairs (5.02 within 180d): {len(E2)}; unique filings '
    f'{E2["accession"].nunique()}; MetroPCS-vintage filings {int((E2["filer_vintage"] == "MetroPCS").sum())} '
    f'pairs; text already on disk for {E2.loc[E2["text_on_disk"] != "", "accession"].nunique()} filings')

# =============================== F =========================================
hdr('F — MODEL STRUCTURE FACTS (NEW, scripts/183)')
log(f'  CANONICAL_V3 carries no industry column: '
    f'{[c for c in ev.columns if "sic" in c.lower() or "naics" in c.lower() or "industry" in c.lower()]}')
sic = (s2.dropna(subset=['final_cik']).assign(sic=lambda x: pd.to_numeric(x['sic'], errors='coerce'))
       .dropna(subset=['sic']).groupby('final_cik')['sic'].agg(lambda s: s.mode().iloc[0]))
r3f = reg3.assign(sic4=reg3['final_cik'].map(sic))
r3f['sic2'] = (r3f['sic4'] // 100)
log(f'  If SIC were merged from stage2_signed (parent-CIK mode): coverage {int(r3f["sic4"].notna().sum())}/{len(r3f)}')
for lv in ['sic2', 'sic4']:
    g = r3f.dropna(subset=[lv]).groupby(lv)[TREAT].agg(['size', 'sum'])
    cells_t = g[g['sum'] > 0]
    mixed = g[(g['sum'] > 0) & (g['sum'] < g['size'])]
    log(f'    {lv}: {len(g)} cells; cells with treated {len(cells_t)}; cells with BOTH treated and '
        f'control {len(mixed)}; treated events in all-treated cells '
        f'{int(cells_t.loc[cells_t["sum"] == cells_t["size"], "sum"].sum())}')
    if lv == 'sic2':
        log('      treated-containing SIC2 cells (size, treated): ' +
            '; '.join(f'{int(i)}: ({int(a)}, {int(b)})' for i, (a, b) in cells_t.iterrows()))
G = reg3['final_cik'].nunique()
G1 = reg3.loc[reg3[TREAT] == 1, 'final_cik'].nunique()
log(f'  Parent-CIK clusters in the Essay 3 sample: G={G}; containing treated events G1={G1}')
log(f'  Controls as estimated (158:54-55,131-138): {CONTROLS}')

# =============================== G =========================================
hdr('G — RECONCILIATION OF THE v3 H6 CONSTANTS (NEW, scripts/183)')
gro = []
for w in (30, 90, 180):
    ame, p, mde = C[f'H6_{w}d_ame_pp'], C[f'H6_{w}d_p'], C[f'H6_{w}d_mde80_pp']
    se = mde / 2.8
    z = ame / se
    p_imp = 2 * (1 - stats.norm.cdf(abs(z)))
    z_from_p = stats.norm.ppf(1 - p / 2)
    gro.append(dict(window=w, ame_pp=ame, p_stored=p, mde80=mde, se_implied=round(se, 4),
                    z_coef_over_se=round(z, 4), p_implied=round(p_imp, 4),
                    abs_diff=round(abs(p - p_imp), 4), z_from_p=round(z_from_p, 4),
                    ratio_zp_over_zse=round(z_from_p / z, 4)))
    log(f'  {w}d: stored AME {ame:+.2f}pp p={p:.4f} MDE {mde:.2f} -> SE {se:.4f}, z {z:.4f}, '
        f'implied p {p_imp:.4f} (|diff| {abs(p - p_imp):.4f}); z_from_p/z = {z_from_p / z:.4f}')
log('  (MDE stored at 2dp -> SE carries rounding of up to 0.005/2.8 pp)')


def h6(dd, tag):
    out = []
    for w in (30, 90, 180):
        y = dd[f'executive_change_{w}d'].astype(int)
        m = sm.Logit(y, sm.add_constant(dd[CONTROLS].astype(float))).fit(disp=0)
        a = m.get_margeff().summary_frame().loc[TREAT]
        tz = a['dy/dx'] / a['Std. Err.']
        pz = 2 * (1 - stats.norm.cdf(abs(tz)))
        bz = m.params[TREAT] / m.bse[TREAT]
        out.append(dict(sample=tag, window=w, N=len(dd), treated=int(dd[TREAT].sum()),
                        base=round(y.mean(), 4), ame_pp=round(100 * a['dy/dx'], 2),
                        se_pp=round(100 * a['Std. Err.'], 3), z_rep=round(a['z'], 4),
                        z_calc=round(tz, 4), p_rep=round(a['Pr(>|z|)'], 4), p_calc=round(pz, 4),
                        logit_coef=round(m.params[TREAT], 4), logit_se=round(m.bse[TREAT], 4),
                        logit_z_rep=round(m.tvalues[TREAT], 4), logit_z_calc=round(bz, 4),
                        logit_p=round(m.pvalues[TREAT], 4), mde80_pp=round(280 * a['Std. Err.'], 2)))
    return out


G6 = h6(r338, 'current file minus DISH (constants vintage?)') + h6(reg3, 'current CANONICAL_V3')
for g in G6:
    log('  ' + ' | '.join(f'{k}={v}' for k, v in g.items()))
pd.DataFrame(gro).to_csv(OUT / 'g_constants_reconciliation.csv', index=False)
pd.DataFrame(G6).to_csv(OUT / 'g_h6_reestimation.csv', index=False)

# ---- G (supplementary): committed legacy Essay 3 tables that run_all still regenerates ----
hdr('G-LEGACY — t/p/CI/mediation checks on committed 7/28-vintage tables (NEW, scripts/183)')
gd = Path('outputs/tables/essay3_governance')
wm = pd.read_csv(gd / 'with_mediator_model_coefficients.csv')
for _, r in wm.iterrows():
    z = r['logit_coef'] / r['logit_se']
    log(f"  with_mediator {r['window']} {r['variable']}: coef/se {z:+.4f} | reported z {r['logit_z']:+.3f} "
        f"(ratio {r['logit_z'] / z:.4f}) | p calc {2 * (1 - stats.norm.cdf(abs(z))):.4f} vs reported {r['logit_p']}")
rf = pd.read_csv(gd / 'reduced_form_h6_results.csv')
for _, r in rf.iterrows():
    z = r['logit_coef'] / r['logit_se']
    log(f"  reduced_form {r['window']}: z {z:.4f} | p calc {2 * (1 - stats.norm.cdf(abs(z))):.4f} vs reported {r['logit_p']}")
te = pd.read_csv(gd / 'h6_tost_equivalence_results.csv')
for _, r in te.iterrows():
    log(f"  91e TOST {r['window']}: 90% CI calc [{r['ame_pp'] - 1.645 * r['ame_se_pp']:.2f}, "
        f"{r['ame_pp'] + 1.645 * r['ame_se_pp']:.2f}] vs reported [{r['ci_lower_90_pp']}, {r['ci_upper_90_pp']}]")
m91 = pd.read_csv('outputs/h6_form499_corrected_ame_by_window.csv')
for _, r in m91.iterrows():
    t = r['FCC_AME_pp'] / r['AME_SE']
    log(f"  91m {r['Window']}: t {t:.4f} | p calc t(641) {2 * (1 - stats.t.cdf(abs(t), 641)):.6f} vs reported "
        f"{r['p_value']:.6f} (N=646 from the companion legacy files; 91m:94 uses df=N-5)")
cx = pd.read_csv(gd / 'cox_model_all_turnover.csv').iloc[0]
zc = cx['fcc_coefficient'] / cx['fcc_se']
log(f"  Cox: z {zc:.4f} p calc {2 * (1 - stats.norm.cdf(abs(zc))):.4f} vs {cx['fcc_p_value']} | HR "
    f"{np.exp(cx['fcc_coefficient']):.4f} vs {cx['fcc_hazard_ratio']} | CI [{np.exp(cx['fcc_coefficient'] - 1.96 * cx['fcc_se']):.4f}, "
    f"{np.exp(cx['fcc_coefficient'] + 1.96 * cx['fcc_se']):.4f}] vs [{cx['fcc_hr_ci_lower']}, {cx['fcc_hr_ci_upper']}]")
fs_a = pd.read_csv(gd / 'mediator_first_stage_results.csv').iloc[0]
med = pd.read_csv(gd / 'mediation_bootstrap_indirect_effects.csv')
for _, r in med.iterrows():
    b_path = wm[(wm['window'] == r['window']) & (wm['variable'] == 'immediate_disclosure')]['logit_coef'].iloc[0]
    tot = rf[rf['window'] == r['window']]['ame_pp'].iloc[0]
    log(f"  mediation {r['window']}: a (logit) {fs_a['logit_coef']:+.4f} x b (logit) {b_path:+.4f} = "
        f"{fs_a['logit_coef'] * b_path:+.4f} (sign {'-' if fs_a['logit_coef'] * b_path < 0 else '+'}) | reported "
        f"indirect {r['indirect_effect_pp']:+.2f}pp | reduced-form total AME {tot:+.2f}pp")

Path(OUT / '183_discovery.log').write_text('\n'.join(L) + '\n', encoding='utf-8')
print(f'\nSaved: {OUT}/ (log + CSVs)')
