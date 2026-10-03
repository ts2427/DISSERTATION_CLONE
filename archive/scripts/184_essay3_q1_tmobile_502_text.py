"""
ESSAY 3 QUERY 1 — PART E TEXT: T-MOBILE ITEM 5.02 FILINGS (NEW)
===============================================================
Scope is Part E ONLY: the 35 unique 8-K filings listing Item 5.02 that fall
within 180 days of any CIK-1283699 event (outputs/essay3_q1/e2_tmobile_502_filings.csv,
scripts/183). This is NOT the sample-wide re-pull scoped in Part B3.

Text source: the 7 primary documents already on disk (scripts/162 calibration
package); the remaining primary documents fetched once from EDGAR Archives and
cached under outputs/essay3_q1/tmobile_8k/. Nothing upstream is modified.

Rules-based tags on the Item 5.02 section (for hand-checking, not a classifier
of record): departure verb + officer/director noun in one sentence -> 5.02(b);
CEO/principal-executive-officer noun + departure verb in one sentence -> CEO
departure; appointment/election/compensation cues -> (c)/(d)/(e). The report
prints the excerpts so every call can be read against the text.
Also scans full text of these filings and of the 50 calibration documents for
information-security officer titles.

Outputs: outputs/essay3_q1/e2_tmobile_502_text.csv, e3_security_title_scan.csv,
         outputs/essay3_q1/184_tmobile_text.log
"""

import re
import sys
import html
import time
from pathlib import Path
import pandas as pd
import requests

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
OUT = Path('outputs/essay3_q1')
DOCS = OUT / 'tmobile_8k'
DOCS.mkdir(parents=True, exist_ok=True)
CAL = Path('outputs/rebuild/calibration_5_02')
H = {'User-Agent': 'Academic Research (University of South Alabama) timothy.spivey@southalabama.edu'}
CIK = 1283699
L = []


def log(m=''):
    print(m)
    L.append(str(m))


def text_of(raw):
    s = raw.decode('utf-8', errors='replace') if isinstance(raw, bytes) else raw
    s = re.sub(r'(?is)<(script|style).*?</\1>', ' ', s)
    s = re.sub(r'(?s)<[^>]+>', ' ', s)
    s = html.unescape(s).replace('\xa0', ' ')
    return re.sub(r'\s+', ' ', s).strip()


def section_502(t):
    """Longest 'Item 5.02 ...' span up to the next Item header or SIGNATURE."""
    best = ''
    for m in re.finditer(r'(?i)item\s*5\.02', t):
        rest = t[m.start():]
        nxt = re.search(r'(?i)(item\s*(?!5\.02)\d\.\d\d|signatures?\b)', rest[10:])
        seg = rest[:10 + nxt.start()] if nxt else rest[:4000]
        if len(seg) > len(best):
            best = seg
    return best


DEPART = r'(resign|retire|retirement|terminat|step(?:ping|ped)? down|depart|will leave|separat|' \
         r'not (?:to )?stand for re-?election|decided not to seek|succeeded by|transition)'
OFFICER = r'(chief executive officer|\bceo\b|principal executive officer|president|chief financial officer|' \
          r'\bcfo\b|principal financial officer|principal accounting officer|chief accounting officer|' \
          r'chief operating officer|\bcoo\b|principal operating officer|named executive officer|' \
          r'executive vice president|chief [a-z ]{2,30}officer|director|board)'
CEO = r'(chief executive officer|\bceo\b|principal executive officer)'
APPOINT = r'(appoint|named|promot|will become|will serve as|to serve as|hired)'
ELECT = r'(elected .{0,40}(director|board)|board .{0,60}(increase|expand)|appointed to the board)'
COMP = r'(compensat|bonus|salary|equity award|restricted stock|severance|retention|incentive plan|' \
       r'employment agreement|letter agreement)'
SEC_TITLES = r'(chief information security officer|\bciso\b|chief security officer|\bcso\b|' \
             r'chief information officer|\bcio\b|chief technology officer|\bcto\b|chief privacy officer|' \
             r'chief cyber|information security)'


def sentences(s):
    return [x.strip() for x in re.split(r'(?<=[.;])\s+(?=[A-Z(])', s) if x.strip()]


def tags(sec):
    ss = sentences(sec)
    hit = lambda pat, ss2=ss: [x for x in ss2 if re.search(pat, x, re.I)]
    dep = [x for x in hit(DEPART) if re.search(OFFICER, x, re.I)]
    ceo = [x for x in dep if re.search(CEO, x, re.I)]
    return {'tag_b_departure': int(bool(dep)), 'tag_ceo_departure': int(bool(ceo)),
            'tag_c_appointment': int(bool([x for x in hit(APPOINT) if re.search(OFFICER, x, re.I)])),
            'tag_d_director_election': int(bool(hit(ELECT))),
            'tag_e_compensation': int(bool(hit(COMP))),
            'departure_sentences': ' || '.join(dep)[:1500]}


f = pd.read_csv(OUT / 'e2_tmobile_502_filings.csv', dtype={'accession': str})
u = f.drop_duplicates('accession').sort_values('filing_date').reset_index(drop=True)
log(f'Unique T-Mobile-CIK 5.02 filings in scope: {len(u)} (event-filing pairs {len(f)})')
rows, fetched = [], 0
for _, r in u.iterrows():
    acc = r['accession']
    disk = r['text_on_disk'] if isinstance(r['text_on_disk'], str) and r['text_on_disk'] else ''
    local = CAL / disk if disk else DOCS / f"{acc}_{r['primary_doc']}"
    src = 'calibration_5_02 (on disk)' if disk else 'EDGAR fetch (cached)'
    url = f"https://www.sec.gov/Archives/edgar/data/{CIK}/{acc.replace('-', '')}/{r['primary_doc']}"
    if not local.exists():
        resp = requests.get(url, headers=H, timeout=30)
        local.write_bytes(resp.content if resp.status_code == 200
                          else f'FETCH FAILED {resp.status_code}: {url}'.encode())
        fetched += 1
        time.sleep(0.15)
    raw = local.read_bytes()
    t = text_of(raw)
    sec = section_502(t)
    tg = tags(sec)
    sect = sorted({m.group(0).lower() for m in re.finditer(SEC_TITLES, t, re.I)})
    rows.append({'filing_date': r['filing_date'], 'accession': acc, 'filer_vintage': r['filer_vintage'],
                 'items': r['items'], 'url': url, 'text_source': src, 'local_file': str(local),
                 'text_chars': len(t), 'sec502_chars': len(sec), **tg,
                 'security_titles_in_filing': '; '.join(sect),
                 'excerpt_502': sec[:1200]})
log(f'Fetched now: {fetched}; read from disk: {len(u) - fetched}')
T = pd.DataFrame(rows)
T.to_csv(OUT / 'e2_tmobile_502_text.csv', index=False)
for _, r in T.iterrows():
    log('\n' + '-' * 90)
    log(f"{r['filing_date']} | {r['accession']} | vintage {r['filer_vintage']} | items {r['items']} | "
        f"{r['text_source']}")
    log(f"  tags: b={r['tag_b_departure']} ceo={r['tag_ceo_departure']} c={r['tag_c_appointment']} "
        f"d={r['tag_d_director_election']} e={r['tag_e_compensation']} | security titles: "
        f"{r['security_titles_in_filing'] or 'none'}")
    log(f"  5.02 section ({r['sec502_chars']} chars): {r['excerpt_502']}")

# information-security titles across the calibration package (full text)
sc = []
for p in sorted(CAL.glob('*.htm')):
    t = text_of(p.read_bytes())
    found = sorted({m.group(0).lower() for m in re.finditer(SEC_TITLES, t, re.I)})
    ctx = [t[max(0, m.start() - 120):m.end() + 120] for m in re.finditer(SEC_TITLES, t, re.I)][:2]
    sc.append({'file': p.name, 'titles': '; '.join(found), 'context': ' || '.join(ctx)})
S = pd.DataFrame(sc)
S.to_csv(OUT / 'e3_security_title_scan.csv', index=False)
log('\n' + '=' * 90)
log(f'Calibration package: {len(S)} documents; with any security-title string: '
    f'{int((S["titles"] != "").sum())}')
for _, r in S[S['titles'] != ''].iterrows():
    log(f"  {r['file']}: {r['titles']} | {r['context'][:400]}")
(OUT / '184_tmobile_text.log').write_text('\n'.join(L) + '\n', encoding='utf-8')
print(f'\nSaved: {OUT}/e2_tmobile_502_text.csv, e3_security_title_scan.csv, 184_tmobile_text.log')
