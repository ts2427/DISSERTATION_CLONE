"""
ESSAY 3 QUERY 2 — PART G1, G2, G5: T-MOBILE / SPRINT DATA COLLECTION (NEW; print, do not interpret)
==================================================================================================
G1  T-Mobile (CIK 1283699) and T-Mobile + Sprint (CIK 101830) events as a share of treated
    events at every sample level.
G2  For each T-Mobile event: every 8-K / 8-K/A in [reported_date - 30d, reported_date + 30d]
    with its items; for 8-Ks listing 7.01, 8.01 or 1.05, the primary document and its EX-99
    exhibits are fetched (gzip cache Data/edgar/tmobile_filings/8-K/) and the sentences that
    describe a security incident are printed; PRC source type of every underlying record
    (stage2_signed incident_details, rule-classified). One row per event.
G5  Sprint (CIK 101830) events in the Query 2 scope: every Item 5.02 filing in (breach_date,
    breach_date + 180d] (the Query 1 E2 anchor; days from reported_date also shown), with the
    frozen classifier's codes and flags. Codes of filings on the blind validation sheet are
    MASKED until Tim has coded it.
Outputs: outputs/essay3_q2/g1_weights.csv, g2_disclosure_channel.csv, g2_8k_passages.csv,
         g5_sprint_502.csv, 190_case.log
"""

import re
import sys
import gzip
import json
import time
from datetime import timedelta
from pathlib import Path
import pandas as pd
import requests

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
OUT = Path('outputs/essay3_q2')
H = {'User-Agent': 'Academic Research (University of South Alabama) timothy.spivey@southalabama.edu'}
TM, SP = 1283699, 101830
L = []


def log(m=''):
    print(m, flush=True)
    L.append(str(m))


TREAT = 'fcc_form499'
CONTROLS = [TREAT, 'immediate_disclosure', 'prior_breaches_1yr', 'health_breach', 'firm_size_log', 'leverage', 'roa']
ev = pd.read_csv('Data/processed/rebuild/CANONICAL_V3.csv', low_memory=False)
ev['bdt'] = pd.to_datetime(ev['breach_date'])
ev['rdt'] = pd.to_datetime(ev['reported_date'], errors='coerce')
crsp = ev[ev['has_crsp_data'] == 1]
scope = pd.read_csv(OUT / 'b_scope_events.csv', low_memory=False)
skeys = set(zip(scope['final_cik'], scope['breach_date']))

# ---------------- G1 ----------------
log('G1 — T-Mobile weight in the treated set')
g1 = []
for name, d in [('489-event universe', ev), ('CRSP', crsp),
                ('Q2 scope (Essay 3 sample without the timing requirement)',
                 ev[[k in skeys for k in zip(ev['final_cik'], ev['breach_date'])]]),
                ('Q1 Essay 3 regression sample', crsp.dropna(subset=CONTROLS))]:
    t = d[d[TREAT] == 1]
    tm = int((t['final_cik'] == TM).sum())
    sp = int((t['final_cik'] == SP).sum())
    g1.append(dict(level=name, treated_events=len(t), tmobile_events=tm,
                   tmobile_share=round(tm / len(t), 4), sprint_cik_events=sp,
                   tmobile_plus_sprint=tm + sp, tmobile_plus_sprint_share=round((tm + sp) / len(t), 4),
                   treated_parent_ciks=t['final_cik'].nunique()))
G1 = pd.DataFrame(g1)
G1.to_csv(OUT / 'g1_weights.csv', index=False)
log(G1.to_string(index=False))

# ---------------- G2 ----------------
log('\nG2 — disclosure channel per T-Mobile event')
pages = json.loads(Path(f'Data/edgar/rebuild_submissions_cache/{TM}.json').read_text())
k8 = []
for pg in pages:
    n = len(pg.get('form', []))
    for i in range(n):
        if pg['form'][i].startswith('8-K'):
            k8.append(dict(form=pg['form'][i], filing_date=pg['filingDate'][i], items=(pg.get('items') or [''] * n)[i],
                           accession=pg['accessionNumber'][i], primary_doc=pg['primaryDocument'][i]))
K8 = pd.DataFrame(k8)
K8['fdt'] = pd.to_datetime(K8['filing_date'])
CACHE8 = Path('Data/edgar/tmobile_filings/8-K')
CACHE8.mkdir(parents=True, exist_ok=True)
# Security-incident language only (a first version matched "compromise on quality", "attacked this pain
# point" and "breaches of certain representations" and was replaced before any result was used).
INC = re.compile(r'(?i)\b(cyber-?\w*|(?:data|security)\s+breach\w*|unauthori[sz]ed\s+(?:access|acquisition|party|'
                 r'parties|individual)|security\s+incident|bad\s+actor|threat\s+actor|malicious|hack(?:er|ers|ed|ing)\b|'
                 r'(?:data|information|accounts?|systems?)\s+(?:was|were|had\s+been|has\s+been)\s+(?:compromised|accessed|'
                 r'exposed|stolen)|compromised\s+(?:data|information|systems?|accounts?))')
NOT_INC = re.compile(r'(?i)breach(?:es)?\s+of\s+(?:certain\s+)?(?:representations|covenants|contract|the\s+agreement)')


def get_gz(url, dest):
    if dest.exists():
        return gzip.decompress(dest.read_bytes())
    r = requests.get(url, headers=H, timeout=30)
    time.sleep(0.2)
    if r.status_code != 200:
        return b''
    dest.write_bytes(gzip.compress(r.content))
    return r.content


def text_of(raw):
    s = raw.decode('utf-8', errors='replace')
    s = re.sub(r'(?is)<(script|style)\b.*?</\1\s*>', ' ', s)
    s = re.sub(r'(?s)<[^>]+>', ' ', s)
    import html as _h
    return re.sub(r'\s+', ' ', _h.unescape(s).replace('\xa0', ' ')).strip()


def src_type(txt):
    t = str(txt)
    if re.search(r'(?i)attorney\s+general|office\s+of\s+the\s+attorney|department\s+of\s+justice', t):
        return 'state AG'
    if re.search(r'(?i)health\s+and\s+human\s+services|\bHHS\b|office\s+for\s+civil\s+rights', t):
        return 'HHS/OCR'
    if re.search(r'(?i)securities\s+and\s+exchange|\b8-K\b|SEC\s+filing', t):
        return 'SEC filing'
    if re.search(r'(?i)press\s+release|news|media|reported\s+by|publicly\s+announced|announced', t):
        return 'press/media'
    if re.search(r'(?i)department\s+of|division\s+of|commission|bureau|agency', t):
        return 'other state agency'
    return 'other'


s2 = pd.read_csv('Data/processed/rebuild/stage2_signed.csv', low_memory=False)
s2 = s2[s2['final_cik'] == TM]
psg, chan = [], []
for _, e in ev[ev['final_cik'] == TM].sort_values('bdt').iterrows():
    rd = e['rdt']
    recs = s2[s2['breach_date'].astype(str).str[:10] == e['breach_date']]
    srcs = [src_type(x) for x in recs['incident_details']]
    w = K8[(K8['fdt'] >= rd - timedelta(days=30)) & (K8['fdt'] <= rd + timedelta(days=30))].sort_values('fdt')
    hit_acc, hit_days = '', ''
    for _, k in w.iterrows():
        rel = bool(re.search(r'\b(7\.01|8\.01|1\.05)\b', str(k['items'])))
        passages = []
        if rel:
            base = f"https://www.sec.gov/Archives/edgar/data/{TM}/{k['accession'].replace('-', '')}/"
            docs = [(k['primary_doc'], base + k['primary_doc'])]
            try:
                ij = requests.get(base + 'index.json', headers=H, timeout=30)
                time.sleep(0.2)
                for it in ij.json()['directory']['item'] if ij.status_code == 200 else []:
                    if re.search(r'(?i)ex[-_]?99|dex99', it['name']) and it['name'].lower().endswith(('.htm', '.txt')):
                        docs.append((it['name'], base + it['name']))
            except Exception:
                pass
            for name, url in docs:
                t = text_of(get_gz(url, CACHE8 / f"{k['accession']}_{name}.gz"))
                for sent in re.split(r'(?<=[.!?])\s+(?=[A-Z])', t):
                    if INC.search(sent) and not NOT_INC.search(sent) and len(sent) < 900:
                        passages.append((name, sent.strip()))
            if passages and not hit_acc:
                hit_acc, hit_days = k['accession'], (k['fdt'] - rd).days
        psg.append(dict(breach_date=e['breach_date'], reported_date=str(rd.date()), accession=k['accession'],
                        filing_date=k['filing_date'], days_from_reported=(k['fdt'] - rd).days, items=k['items'],
                        items_7_01_8_01_1_05=int(rel), incident_sentences=len(passages),
                        first_incident_passages=' || '.join(f'[{n}] {s[:600]}' for n, s in passages[:4])))
    chan.append(dict(breach_date=e['breach_date'], reported_date=str(rd.date()), org_name=e['org_name'],
                     n_source_records=len(recs), prc_source_types='; '.join(sorted(set(srcs))),
                     prc_source_first_record=str(recs['incident_details'].iloc[0])[:220] if len(recs) else '',
                     n_8k_in_window=len(w), incident_8k_accession=hit_acc, days_8k_minus_reported=hit_days,
                     in_q2_scope=int((TM, e['breach_date']) in skeys),
                     cik_vintage='MetroPCS' if e['bdt'] <= pd.Timestamp('2013-04-29') else 'T-Mobile US'))
C = pd.DataFrame(chan)
C.to_csv(OUT / 'g2_disclosure_channel.csv', index=False)
pd.DataFrame(psg).to_csv(OUT / 'g2_8k_passages.csv', index=False)
log(C.drop(columns=['prc_source_first_record']).to_string(index=False))
log('\nIncident passages in 7.01/8.01/1.05 8-Ks within +/-30d of reported_date:')
for _, p in pd.DataFrame(psg).query('incident_sentences > 0').iterrows():
    log(f"  {p['breach_date']} | {p['filing_date']} ({p['days_from_reported']:+d}d) {p['accession']} "
        f"items {p['items']}: {p['first_incident_passages'][:1200]}")

# ---------------- G5 ----------------
log('\nG5 — Sprint (CIK 101830) Item 5.02 record, breach anchor as Query 1 E2')
F = pd.read_csv(OUT / 'c_filing_codes.csv', dtype={'accession': str})
PR = pd.read_csv(OUT / 'c_person_rows.csv', dtype={'accession': str})
cal = {p.name.split('_')[2] for p in Path('outputs/rebuild/calibration_5_02').glob('*.htm')}
val = set(pd.read_csv(OUT / 'validation_ids.csv', dtype=str)['accession'])
masked = cal | val
F['fdt'] = pd.to_datetime(F['filing_date'])
g5 = []
for _, e in scope[scope['final_cik'] == SP].iterrows():
    bd, rd = pd.Timestamp(e['breach_date']), pd.Timestamp(e['reported_date'])
    x = F[(F['cik'] == SP) & (F['fdt'] > bd) & (F['fdt'] <= bd + timedelta(days=180))]
    if len(x) == 0:
        g5.append(dict(breach_date=e['breach_date'], reported_date=str(rd.date()), accession='none'))
    for _, f in x.iterrows():
        m = f['accession'] in masked
        pp = PR[(PR['accession'] == f['accession']) & (PR['action'] == 'departure')]
        g5.append(dict(breach_date=e['breach_date'], reported_date=str(rd.date()), accession=f['accession'],
                       filing_date=f['filing_date'], days_from_breach=(f['fdt'] - bd).days,
                       days_from_reported=(f['fdt'] - rd).days, items=f['items'],
                       on_validation_sheet=int(m),
                       **({k: '[masked]' for k in ['exec_departure', 'ceo_departure', 'director_departure',
                                                    'action', 'persons', 'flags']} if m else
                          dict(exec_departure=f['exec_departure'], ceo_departure=f['ceo_departure'],
                               director_departure=f['director_departure'], action=f['action'],
                               persons='; '.join(f"{p['person']} ({p['role_class']}: {p['title']})"
                                                 for _, p in pp.iterrows()),
                               flags=','.join(k[5:] for k in F.columns if k.startswith('flag_') and f[k] == 1)))))
G5 = pd.DataFrame(g5)
G5.to_csv(OUT / 'g5_sprint_502.csv', index=False)
log(G5.to_string(index=False))
(OUT / '190_case.log').write_text('\n'.join(L) + '\n', encoding='utf-8')
