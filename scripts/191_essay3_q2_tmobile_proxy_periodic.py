"""
ESSAY 3 QUERY 2 — PARTS G3/G4: T-MOBILE PROXIES AND PERIODIC REPORTS (NEW)
=========================================================================
Scope: CIK 1283699 only. Print, do not interpret. EDGAR only.
  G3  every DEF 14A filed 2013-01-01..2026-08-04: controlled-company status,
      director roster (independence / holder designation as the proxy states
      it), committee cybersecurity/privacy mentions, CD&A passages.
  G4  every 10-K and 10-Q filed 2013-01-01 onward (originals parsed; /A listed):
      incident passages, charges/settlements/reserves, 10-K Item 1C.
Filing list from the committed submissions cache
(Data/edgar/rebuild_submissions_cache/1283699.json). DEFA14A/DEFR14A/DEFC14A/
DEFM14A are listed in the inventory but not parsed.
Firewall: no Item 5.02 8-K is read here (validation set stays blind).

Raw documents cached gzip at Data/edgar/tmobile_filings/<form>/<acc>_<doc>.gz.
Outputs (outputs/essay3_q2/): g34_filing_inventory.csv, g3_controlled_company.csv,
  g3_director_roster.csv, g3_committee_cyber.csv, g3_cdna_passages.csv,
  g4_incident_passages.csv, g4_charges_settlements.csv, g4_item1c.csv,
  g34_timeline_rows.csv, 191_tmobile_proxy_periodic.log
"""

import re
import sys
import gzip
import html
import json
import time
from pathlib import Path
import pandas as pd
import requests

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
CIK = 1283699
OUT = Path('outputs/essay3_q2')
OUT.mkdir(parents=True, exist_ok=True)
RAW = Path('Data/edgar/tmobile_filings')
H = {'User-Agent': 'Academic Research (University of South Alabama) timothy.spivey@southalabama.edu'}
DELAY = 0.30
L = []


def log(m=''):
    print(m)
    L.append(str(m))


# ------------------------------------------------------------------ inventory
pages = json.load(open(f'Data/edgar/rebuild_submissions_cache/{CIK}.json'))
rows = []
for p in pages:
    for f, d, a, doc in zip(p['form'], p['filingDate'], p['accessionNumber'], p['primaryDocument']):
        rows.append({'form': f, 'filing_date': d, 'accession': a, 'primary_doc': doc})
inv = pd.DataFrame(rows)
inv = inv[(inv['filing_date'] >= '2013-01-01') & (inv['filing_date'] <= '2026-08-04')]
inv = inv[inv['form'].str.startswith('DEF') | inv['form'].str.startswith('10-K') |
          inv['form'].str.startswith('10-Q')].sort_values('filing_date').reset_index(drop=True)
PARSE = {'DEF 14A', '10-K', '10-Q'}
inv['parsed'] = inv['form'].isin(PARSE)
inv['url'] = [f"https://www.sec.gov/Archives/edgar/data/{CIK}/{a.replace('-', '')}/{d}"
              for a, d in zip(inv['accession'], inv['primary_doc'])]
log(f'Inventory (2013-01-01..2026-08-04): {inv["form"].value_counts().to_dict()}')
log(f'Parsed forms: {sorted(PARSE)}; listed only: '
    f'{sorted(set(inv["form"]) - PARSE)}')


def fetch(r):
    d = RAW / r['form'].replace(' ', '_').replace('/', '-')
    d.mkdir(parents=True, exist_ok=True)
    fp = d / f"{r['accession']}_{r['primary_doc']}.gz"
    if fp.exists():
        return fp, True, None
    for attempt in range(2):
        try:
            resp = requests.get(r['url'], headers=H, timeout=60)
            time.sleep(DELAY)
            if resp.status_code == 200:
                fp.write_bytes(gzip.compress(resp.content))
                return fp, True, len(resp.content)
        except Exception:
            time.sleep(2)
    return fp, False, None


stat = []
for i, r in inv[inv['parsed']].iterrows():
    fp, ok, nraw = fetch(r)
    raw_b = len(gzip.decompress(fp.read_bytes())) if ok else None
    stat.append({'idx': i, 'local': str(fp), 'fetched_ok': ok, 'raw_bytes': raw_b,
                 'gz_bytes': fp.stat().st_size if ok else None})
st = pd.DataFrame(stat).set_index('idx')
inv = inv.join(st)
inv.to_csv(OUT / 'g34_filing_inventory.csv', index=False)
p = inv[inv['parsed']]
log(f'Fetch: {int(p["fetched_ok"].sum())} ok / {int((~p["fetched_ok"].astype(bool)).sum())} failed; '
    f'raw {p["raw_bytes"].sum() / 1e6:.1f} MB, gz {p["gz_bytes"].sum() / 1e6:.1f} MB')

if len(sys.argv) > 1 and sys.argv[1] == 'fetch-only':
    Path(OUT / '191_tmobile_proxy_periodic.log').write_text('\n'.join(L) + '\n', encoding='utf-8')
    sys.exit(0)

# ================================================================ helpers
def text_of(fp):
    b = gzip.decompress(Path(fp).read_bytes())
    try:
        s = b.decode('utf-8')
    except UnicodeDecodeError:
        s = b.decode('cp1252', errors='replace')
    s = re.sub(r'(?is)<(script|style|ix:header).*?</\1>', ' ', s)
    s = re.sub(r'(?s)<[^>]+>', ' ', s)
    return re.sub(r'\s+', ' ', html.unescape(s).replace('\xa0', ' ')).strip()


SPLIT = re.compile(r'(?<=[.;!?])\s+(?=[A-Z“"(])|\s+(?=[■∎◾•⬛▪●])')


def sentences_with_pos(t):
    out, pos = [], 0
    for s in SPLIT.split(t):
        i = t.find(s, pos)
        pos = i + len(s) if i >= 0 else pos
        s2 = s.strip(' ■∎◾•⬛▪●')
        if len(s2) > 15:
            out.append((i, s2[:600]))
    return out


PCT = re.compile(r'\d{1,3}(?:\.\d+)?\s?%|\d{1,3}(?:\.\d+)?\s?percent', re.I)
HOLDER = re.compile(r'Deutsche Telekom|SoftBank', re.I)
OWN = re.compile(r'own|hold|beneficial|voting control|outstanding shares|stock ownership', re.I)
CYB = re.compile(r'cybersecurity|cyber security|cyber-security|privacy|information security|data security', re.I)
COMM = re.compile(r'((?:Audit|Compensation|Nominating and Corporate Governance|Nominating|Executive|'
                  r'Transaction|CEO Selection|Cybersecurity|Privacy|Technology|Risk|Finance|Special|'
                  r'Independent|Governance)[A-Za-z,& ]{0,40}?Committee)')
CDA_TERM = re.compile(r'cyber|breach|security incident|\bdata\b|privacy', re.I)
PAY = re.compile(r'bonus|PRSU|RSU|award|payout|incentive|adjust|reduc|modif|forfeit|clawback|discretion', re.I)
INC = re.compile(r'cyberattack|cyber-attack|cyber attack|cybersecurity incident|breach|unauthorized access|'
                 r'malicious|threat actor', re.I)
CYBER_ONLY = re.compile(r'cyber|unauthori[sz]ed access|threat actor|malicious|data breach|security breach|'
                        r'security incident|breach of (?:our|its|the company)', re.I)
AMT = re.compile(r'\$\s?\d[\d,\.]*(?:\s?(?:million|billion))?|\d[\d,\.]*\s(?:million|billion)', re.I)
CHG = re.compile(r'cyber|breach|incident|settlement|class action|litigation|accrual|reserve|security', re.I)
ROLE = re.compile(r'Chief Information Security Officer|\bCISO\b|Chief Security Officer|Chief Cyber\w*|'
                  r'Chief Information Officer|\bCIO\b|Chief Technology Officer|\bCTO\b|Chief Privacy Officer|'
                  r'Chief Trust Officer|Chief Digital Officer', re.I)
MRS = re.compile(r'\b(?:Mr|Ms|Mrs|Dr)\.\s+([A-Z][\w’\'\-]+(?:\s+[A-Z][\w’\'\-]+)?)')


def first_body(t, pat, gap=20000, nxt=None):
    """Start of the body occurrence of a heading (TOC entries are followed closely by the next entry)."""
    for m in re.finditer(pat, t, re.I):
        if nxt is None:
            return m.start()
        n = re.search(nxt, t[m.end():], re.I)
        if n is None or n.start() > gap:
            return m.start()
    return None


# ================================================================ G3 proxies
cc_rows, ros_rows, com_rows, cda_rows, tl = [], [], [], [], []
px = inv[(inv['form'] == 'DEF 14A') & inv['fetched_ok'].astype(bool)]
ETH = r'(?:White|Caucasian|Asian|Hispanic|Latino|Latina|Latinx|Black|African American|Middle Eastern|' \
      r'Native American|Two or More Races|Other|—|-|N/A|\*+)'
DESIG = r'(Deutsche Telekom|SoftBank|Nom & Gov|NCG Committee|NCG|Nominating and Corporate Governance Committee|' \
        r'Nominating Committee|CEO|N/A|None|—|-)'
MARK = re.compile(r'\*+|\((?:C|L|VC)\)')
for _, r in px.iterrows():
    t = text_of(r['local'])
    d, acc = r['filing_date'], r['accession']
    S = sentences_with_pos(t)
    # (a) controlled company
    pcts, holders = set(), set()
    for _, s in S:
        is_cc = 'controlled company' in s.lower()
        is_own = bool(HOLDER.search(s) and PCT.search(s) and OWN.search(s))
        if is_cc or is_own:
            ps = PCT.findall(s)
            hs = sorted(set(h.title() if h.lower() != 'softbank' else 'SoftBank' for h in HOLDER.findall(s)))
            if is_cc and is_own:
                pcts.update(ps)
                holders.update(hs)
            cc_rows.append({'proxy_date': d, 'accession': acc, 'controlled_company_sentence': is_cc,
                            'holder_ownership_sentence': is_own, 'holders_named': '; '.join(hs),
                            'percentages': '; '.join(ps), 'sentence': s})
    tl.append({'date': d, 'event_type': 'proxy_controlled_status',
               'description': f"controlled-company sentences {sum(1 for x in cc_rows if x['accession'] == acc and x['controlled_company_sentence'])}; "
                              f"holders named with % in those sentences: {', '.join(sorted(holders)) or 'none'}; "
                              f"% stated: {', '.join(sorted(pcts)) or 'none'}",
               'form': 'DEF 14A', 'accession': acc})
    # (b) roster
    surnames = {m.group(1).split()[-1] for m in MRS.finditer(t)} | {m.group(1) for m in MRS.finditer(t)}
    parsed_rows = []
    hdr = re.search(r'Age\s+Director Since\s+Independent.{0,80}?Designation', t)
    if hdr:
        seg = t[hdr.end():hdr.end() + 12000]
        anchors = list(re.finditer(r'(\d{2})\s+(\d{4}|N/A|—|-|New|Nominee)\s+(Yes|No)\s+(M|F|Male|Female)\s+', seg))
        prev_end = 0
        for j, a in enumerate(anchors):
            chunk = seg[prev_end:a.start()].strip()
            toks = [x for x in chunk.split() if not re.fullmatch(r'\((?:C|L|VC)\)|\*+', x)]
            name = None
            for k in range(2, min(6, len(toks)) + 1):
                if MARK.sub('', toks[k - 1]).strip(',') in surnames:
                    name = MARK.sub('', ' '.join(toks[:k])).strip(', ')
                    break
            tail_end = anchors[j + 1].start() if j + 1 < len(anchors) else len(seg)
            tail = seg[a.end():tail_end]
            mt = re.match(rf'((?:{ETH}\s*/?\s*)+)\s*{DESIG}', tail)
            desig = mt.group(2) if mt else None
            prev_end = a.end() + (mt.end() if mt else 0)
            parsed_rows.append({'name': name, 'age': a.group(1), 'director_since': a.group(2),
                                'independent': 'Y' if a.group(3) == 'Yes' else 'N',
                                'affiliation_as_stated': desig})
            if j + 1 < len(anchors) and not mt:
                break
        n_bio = len(re.findall(r'Director Since:|Director Nominee\s+Age:', t))
        ok = (len(parsed_rows) > 0 and all(x['name'] and x['affiliation_as_stated'] for x in parsed_rows)
              and (n_bio == 0 or len(parsed_rows) == n_bio))
        for x in parsed_rows:
            ros_rows.append({'proxy_date': d, 'accession': acc, 'method': 'nominee table', **x,
                             'roster_parsed': ok, 'bio_blocks_counted': n_bio, 'verbatim_evidence': ''})
        if not ok:
            log(f'  roster table parse incomplete {d}: rows {len(parsed_rows)} vs bio blocks {n_bio}')
    else:
        ind_s = [s for _, s in S if re.search(r'determined that .{0,300}(are|is) independent', s)
                 and re.search(r'Messrs\.|Mses\.|Ms\.|Mr\.|[A-Z][a-z]+ [A-Z]\. [A-Z][a-z]+', s)]
        ind_s += [s for _, s in S if s not in ind_s and re.search(r'\bindependent\b', s)
                  and re.search(r'\b(director|Board)\b', s) and re.search(r'Messrs\.|Mses\.', s)]
        des_s = [s for _, s in S if re.search(r'(Deutsche Telekom|SoftBank) designees? (are|is|include)|'
                                             r'designated by (Deutsche Telekom|SoftBank)|'
                                             r'(Deutsche Telekom|SoftBank) (has|had) (the right to )?designated?', s)]
        bios = re.findall(r'([A-Z][A-Za-z\.’\'\- ]{3,40}?)\s*,\s*age (\d{2}),\s*(?:has served|has been|is)\s[^.]{0,120}?director', t)
        if not bios:   # 2021+ layout: "Biography: Mr. Surname ..." blocks, age stated as "Age: NN"
            bios = [(m.group(1), '') for m in re.finditer(r'Biography:\s*(?:Mr|Ms|Mrs|Dr)\.\s+([A-Z][\w’\'\-]+)', t)]
        names = []
        for nm, age in bios:
            nm = nm.strip()
            if nm not in [x[0] for x in names]:
                names.append((nm, age))
        ind_names = set()
        for s in ind_s:
            seg2 = re.search(r'(?:Messrs\.|Mses\.|Ms\.|Mr\.)(.+?)(?:are|is) independent', s)
            if seg2:
                ind_names |= {w.strip(' .,') for w in re.split(r',|\band\b|Ms\.|Mr\.|Mses\.|Messrs\.', seg2.group(1)) if w.strip(' .,')}
        for nm, age in names:
            last = nm.split()[-1].strip(',')
            if last in ('Jr.', 'Sr.', 'III', 'II'):
                last = nm.split()[-2].strip(',')
            ros_rows.append({'proxy_date': d, 'accession': acc, 'method': 'bio + independence sentence',
                             'name': nm, 'age': age, 'director_since': None,
                             'independent': ('Y' if last in ind_names else 'N') if ind_names else None,
                             'affiliation_as_stated': None, 'roster_parsed': False,
                             'bio_blocks_counted': len(names),
                             'verbatim_evidence': ' || '.join(ind_s + des_s)[:3000]})
        if not names:
            ros_rows.append({'proxy_date': d, 'accession': acc, 'method': 'none', 'name': None, 'age': None,
                             'director_since': None, 'independent': None, 'affiliation_as_stated': None,
                             'roster_parsed': False, 'bio_blocks_counted': 0,
                             'verbatim_evidence': ' || '.join(ind_s + des_s)[:3000]})
    # (c) committees x cyber terms
    for _, s in S:
        if CYB.search(s) and COMM.search(s):
            for cm in sorted({c.strip() for c in COMM.findall(s)}):
                for term in sorted({x.lower() for x in CYB.findall(s)}):
                    com_rows.append({'proxy_date': d, 'accession': acc, 'committee': cm, 'term': term,
                                     'sentence': s})
    # (d) CD&A
    # body CD&A = first CD&A heading after the TOC's "Compensation Committee Report" entry,
    # ending at the last (body) "Compensation Committee Report"
    ccr = [m.start() for m in re.finditer(r'Compensation Committee Report', t, re.I)]
    cdas = [m.start() for m in re.finditer(r'Compensation Discussion and Analysis', t, re.I)]
    if len(ccr) >= 2 and [c for c in cdas if ccr[0] < c < ccr[-1]]:
        a0 = min(c for c in cdas if ccr[0] < c < ccr[-1])
        cda = t[a0:ccr[-1]]
    else:
        a0 = first_body(t, r'Compensation Discussion and Analysis', 20000,
                        r'Compensation Committee Report|Summary Compensation Table')
        if a0 is None:
            log(f'  CD&A body not located {d}')
            continue
        e = re.search(r'Compensation Committee Report|Summary Compensation Table', t[a0 + 1000:])
        cda = t[a0:a0 + 1000 + e.start()] if e else t[a0:a0 + 200000]
    for _, s in sentences_with_pos(cda):
        if CDA_TERM.search(s):
            cda_rows.append({'proxy_date': d, 'accession': acc, 'pay_link': bool(PAY.search(s)),
                             'terms': '; '.join(sorted({x.lower() for x in CDA_TERM.findall(s)})),
                             'sentence': s})
    log(f'G3 {d}: sentences {len(S)}, CD&A chars {len(cda)}')

CC = pd.DataFrame(cc_rows)
CC.to_csv(OUT / 'g3_controlled_company.csv', index=False)
RO = pd.DataFrame(ros_rows)
RO.to_csv(OUT / 'g3_director_roster.csv', index=False)
CM = pd.DataFrame(com_rows)
if len(CM):
    first = CM.groupby(['committee', 'term'])['proxy_date'].min().rename('first_proxy_date')
    CM = CM.merge(first, on=['committee', 'term'])
    for (cm, term), g in CM.groupby(['committee', 'term']):
        f0 = g.sort_values('proxy_date').iloc[0]
        tl.append({'date': f0['proxy_date'], 'event_type': 'committee_cyber_mention',
                   'description': f'first proxy mention: {cm} x "{term}": {f0["sentence"][:300]}',
                   'form': 'DEF 14A', 'accession': f0['accession']})
CM.to_csv(OUT / 'g3_committee_cyber.csv', index=False)
CD = pd.DataFrame(cda_rows)
CD.to_csv(OUT / 'g3_cdna_passages.csv', index=False)
if len(CD):
    for s, g in CD[CD['pay_link']].groupby('sentence'):
        f0 = g.sort_values('proxy_date').iloc[0]
        tl.append({'date': f0['proxy_date'], 'event_type': 'comp_statement',
                   'description': f'CD&A pay-linked sentence (first of {len(g)} proxies): {s[:300]}',
                   'form': 'DEF 14A', 'accession': f0['accession']})


# ================================================================ G4 10-K / 10-Q
def section_map(t, form):
    """Body headings (non-TOC) -> [(pos, label)]."""
    pats = [(r'Item\s*1A\.?\s*Risk Factors', 'risk factors'), (r'Item\s*1B\.', 'other'),
            (r'Item\s*1C\.?\s*Cybersecurity', 'cybersecurity (Item 1C)'),
            (r'Item\s*2\.?\s*Properties', 'other'),
            (r'Item\s*3\.?\s*Legal Proceedings', 'legal proceedings'),
            (r'Item\s*1\.?\s*Legal Proceedings', 'legal proceedings'),
            (r'Item\s*4\.', 'other'), (r'Item\s*5\.', 'other'),
            (r'Item\s*7\.?\s*Management', 'MD&A'), (r'Item\s*2\.?\s*Management', 'MD&A'),
            (r'Item\s*7A\.', 'other'), (r'Item\s*3\.?\s*Quantitative', 'other'),
            (r'Item\s*8\.?\s*Financial Statements', 'financial statements / notes'),
            (r'Item\s*1\.?\s*Financial Statements', 'financial statements / notes'),
            (r'Notes to (?:the )?(?:Condensed )?Consolidated Financial Statements', 'financial statements / notes'),
            (r'Item\s*9A?\.', 'other'), (r'Item\s*4\.?\s*Controls', 'other'), (r'Item\s*6\.', 'other'),
            (r'Item\s*1\.?\s*Business', 'business')]
    hits = []
    for p, lab in pats:
        for m in re.finditer(p, t, re.I):
            hits.append((m.start(), lab, m.end()))
    hits.sort()
    body = []
    for i, (pos, lab, end) in enumerate(hits):
        nxt = hits[i + 1][0] if i + 1 < len(hits) else len(t)
        if nxt - end > 400:           # TOC entries sit within a few characters of the next entry
            body.append((pos, lab))
    return body


def label_at(body, pos):
    lab = 'unknown (before first body heading)'
    for p, l in body:
        if p <= pos:
            lab = l
        else:
            break
    return lab


inc_rows, chg_rows, c1_rows = [], [], []
pr = inv[inv['form'].isin(['10-K', '10-Q']) & inv['fetched_ok'].astype(bool)]
for _, r in pr.iterrows():
    t = text_of(r['local'])
    body = section_map(t, r['form'])
    for pos, s in sentences_with_pos(t):
        if INC.search(s):
            inc_rows.append({'form': r['form'], 'filing_date': r['filing_date'], 'accession': r['accession'],
                             'section_guess': label_at(body, pos),
                             'cyber_related': bool(CYBER_ONLY.search(s)),
                             'terms': '; '.join(sorted({x.lower() for x in INC.findall(s)})), 'sentence': s})
        if AMT.search(s) and CHG.search(s):
            chg_rows.append({'form': r['form'], 'filing_date': r['filing_date'], 'accession': r['accession'],
                             'section_guess': label_at(body, pos),
                             'cyber_related': bool(CYBER_ONLY.search(s)),
                             'amounts': '; '.join(AMT.findall(s)),
                             'terms': '; '.join(sorted({x.lower() for x in CHG.findall(s)})), 'sentence': s})
    if r['form'] == '10-K' and r['filing_date'] >= '2024-01-01':
        starts = [p for p, l in body if l.startswith('cybersecurity')]
        if not starts:
            log(f'  Item 1C body not located in 10-K {r["filing_date"]}')
            continue
        e = re.search(r'Item\s*2\.?\s*Properties', t[starts[0]:], re.I)
        sec = t[starts[0]:starts[0] + (e.start() if e else 20000)]
        c1_rows.append({'filing_date': r['filing_date'], 'accession': r['accession'], 'kind': 'section_text',
                        'text': sec})
        for _, s in sentences_with_pos(sec):
            kinds = []
            if ROLE.search(s):
                kinds.append('role_named')
            if re.search(r'reports? to|reporting to|reporting line', s, re.I):
                kinds.append('reports_to')
            if re.search(r'Committee', s):
                kinds.append('committee')
            for k in kinds:
                c1_rows.append({'filing_date': r['filing_date'], 'accession': r['accession'], 'kind': k,
                                'text': s})
    log(f'G4 {r["form"]} {r["filing_date"]}: body headings {len(body)}')


def dedupe(df, keys):
    if not len(df):
        return df
    g = df.sort_values('filing_date').groupby('sentence', sort=False)
    out = g.agg(first_filing_date=('filing_date', 'min'), last_filing_date=('filing_date', 'max'),
                n_filings=('accession', 'nunique'), first_accession=('accession', 'first'),
                first_form=('form', 'first'), **{k: (k, 'first') for k in keys}).reset_index()
    return out.sort_values('first_filing_date')


INCD = dedupe(pd.DataFrame(inc_rows), ['section_guess', 'cyber_related', 'terms'])
INCD.to_csv(OUT / 'g4_incident_passages.csv', index=False)
CHGD = dedupe(pd.DataFrame(chg_rows), ['section_guess', 'cyber_related', 'amounts', 'terms'])
CHGD.to_csv(OUT / 'g4_charges_settlements.csv', index=False)
C1 = pd.DataFrame(c1_rows)
C1.to_csv(OUT / 'g4_item1c.csv', index=False)
for _, x in INCD[INCD['cyber_related']].iterrows():
    tl.append({'date': x['first_filing_date'], 'event_type': 'incident_passage_first',
               'description': x['sentence'][:300], 'form': x['first_form'], 'accession': x['first_accession']})
for _, x in CHGD[CHGD['cyber_related']].iterrows():
    kind = 'settlement' if re.search(r'settle', x['sentence'], re.I) else (
        'reserve' if re.search(r'reserve|accru', x['sentence'], re.I) else 'charge')
    tl.append({'date': x['first_filing_date'], 'event_type': kind,
               'description': f"{x['amounts']} | {x['sentence'][:300]}", 'form': x['first_form'],
               'accession': x['first_accession']})
for _, x in C1[C1['kind'] == 'role_named'].iterrows() if len(C1) else []:
    tl.append({'date': x['filing_date'], 'event_type': 'item1c_ciso', 'description': x['text'][:300],
               'form': '10-K', 'accession': x['accession']})
TL = pd.DataFrame(tl).sort_values(['date', 'event_type'])
TL.to_csv(OUT / 'g34_timeline_rows.csv', index=False)

log(f'\nG3 rows: controlled {len(CC)}, roster {len(RO)}, committee x term {len(CM)}, CD&A {len(CD)} '
    f'(pay_link {int(CD["pay_link"].sum()) if len(CD) else 0})')
log(f'G4 unique sentences: incident {len(INCD)} (cyber_related {int(INCD["cyber_related"].sum()) if len(INCD) else 0}), '
    f'charges {len(CHGD)} (cyber_related {int(CHGD["cyber_related"].sum()) if len(CHGD) else 0}), '
    f'Item 1C rows {len(C1)}; timeline rows {len(TL)}')
Path(OUT / '191_tmobile_proxy_periodic.log').write_text('\n'.join(L) + '\n', encoding='utf-8')
