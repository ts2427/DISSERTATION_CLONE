"""
REBUILD DIRECTIVE v2 — STAGE 4: TREATMENT CLASSIFICATION
=========================================================
Form 499 classification on the Gate 2 event set, from the COMMITTED registry
snapshot (Data/edgar/form499_registry.xml — never the live endpoint).
Clause (a): any of the event's name variants matches a registry filer
(Legal_Name / DBA / other_trade_name, normalized exact) whose coverage is valid
at the breach date (start<=breach; end absent, sentinel 1997-01-01, or
non-terminating). Clause (b) and signed adjudications applied as documented
pattern rules over the variants (treated-if-any-variant). No target counts:
whatever the numbers are, they are.

Output: Data/processed/rebuild/stage4_treated.csv + outputs/rebuild/STAGE4_TREATMENT_REPORT.md
"""

import sys
import re
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
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
log('REBUILD STAGE 4: TREATMENT CLASSIFICATION (Form 499)')
log('=' * 90)

snap = Path('Data/edgar/form499_registry.xml')
import datetime
mtime = datetime.datetime.fromtimestamp(snap.stat().st_mtime)
tree = ET.parse(snap)
filers = tree.getroot().findall('.//Filer')
log(f'\nRegistry snapshot: {snap} | file date {mtime:%Y-%m-%d} | {len(filers)} filer records '
    f'(committed artifact; live endpoint NOT queried)')

TERMINATING = ["This company has gone out of business",
               "no longer providing", "Chapter 7"]
NON_TERMINATING = ["assets of this company have been sold", "consolidated basis",
                   "absorbed by another filing entity"]

reg = defaultdict(list)      # normalized name -> [(frn, start, end, end_reason, legal, field)]
for f in filers:
    info = f.find('Filer_ID_Info')
    if info is None:
        continue

    def gx(tag):
        e = info.find(tag)
        return e.text.strip() if e is not None and e.text else None
    legal, dba, trade = gx('Legal_Name'), gx('doing_business_as'), gx('other_trade_name')
    holding = gx('holding_company')
    frn, sd, ed, er = gx('FRN'), gx('start_date'), gx('end_date'), gx('end_reason_desc')
    for nm, field in ((legal, 'Legal_Name'), (dba, 'dba'), (trade, 'trade_name')):
        if nm:
            reg[normalize(nm)].append((frn, sd, ed, er, legal, field))
    # holding_company: the registry's own parent-brand field — clause (b) mechanized
    if holding:
        reg[normalize(holding)].append((frn, sd, ed, er, legal, 'holding_company'))
log(f'  Registry index: {len(reg):,} normalized names (incl. holding_company entries)')
assert len(reg) > 10000, 'HALT: registry parse produced implausibly few names'


def coverage_valid(sd, ed, er, bdt):
    """Valid iff start<=breach<=end (open end = valid). DIVERGENCE from 121b,
    documented: 121b treated non-terminating ends (consolidation/absorption) as
    open-ended coverage, which false-positived HBO's 1997-2003 division record
    onto 2017 breaches. Here EVERY ended record covers only through its end
    date — successor entities carry their own registry records, which this
    index already searches under their own names."""
    try:
        if sd and sd != '1997-01-01' and pd.Timestamp(sd) > bdt:
            return False
    except Exception:
        pass
    if not ed:
        return True
    try:
        return pd.Timestamp(ed) >= bdt
    except Exception:
        return True


# Signed adjudication pattern rules (variant-level), applied AFTER clause (a):
# (pattern, treat, rationale) — treat=1 forces treated, 0 forces untreated.
ADJ = [
    (r'Cricket', 1, 'Clause (a) adjudicated: Cricket Communications FRN 0004321139; LLC variant missed by exact matcher (7/28 record)'),
    (r'T-Mobile', 1, 'Clause (a) adjudicated 8/4: active open registry record "T-Mobile USA, Inc.- CONSOLIDATED" (499ID 822060, dba T-Mobile, start 1997, no end) — the "- CONSOLIDATED" suffix defeats exact matching for USA/US name variants (Cricket precedent, family-wide)'),
    (r'Boost Mobile', 1, 'Clause (b): prepaid wireless brand of Sprint Spectrum LLC FRN 0006693022; subscriber-data breach (7/28 adjudication)'),
    (r'^Sprint', 1, 'Clause (a) adjudicated 8/4: Sprint Spectrum LLC dba Sprint (499ID 811754, coverage 1997-2024-12-31, replacement 822060) covers all Sprint-family breach dates; dba/suffix variants defeat exact matching'),
    (r'Verizon Media', 0, 'NOT treated (8/4): content division (Yahoo/AOL), not telecom subscriber operations'),
    (r'^Verizon', 1, 'Clause (a) adjudicated 8/4: Verizon carrier filer family (e.g., Verizon-NY FRN 0003469442 through 2021; successor consolidated records active after) — consolidation naming defeats exact matching post-2021'),
    (r'^Comcast|Comcast Cable', 1, 'Clause (b): parent brand of Comcast Telephony filers (7/28)'),
    (r'Charter Communication', 1, 'Clause (b): parent brand of Charter Communications Operating LLC (7/28)'),
    (r'Frontier Communications', 1, 'Clause (b): parent of regional Form 499 filer subsidiaries (7/28)'),
    (r'Altice USA', 1, 'Clause (b): parent of Altice Wireless filer (7/28)'),
    (r'AT&T Services', 1, 'Clause (b): AT&T Inc. filing family (7/28)'),
    (r'CenturyLink', 1, 'Clause (b): CenturyLink/Lumen carrier family (Gate 1 rescue noted Form 499 relevance; regional LEC filers)'),
    (r'DISH Network', 0, 'Adjudicated untreated (7/28): satellite TV not a telecom service under 64.2011; no covered operation at breach dates'),
    (r'NBC Sports', 0, 'No registry match; not a carrier (7/28)'),
    (r'ATT-Breach Notification|ATT-SecurityBreach', 0, 'Artifact system entities — signed 122 rule retained; identity=AT&T equity, treatment excluded'),
    (r'NBCUniversal', 1, 'Clause (a) DOCUMENTED: direct registry filer NBCUniversal, LLC FRN 20940540 (8/4 adjudication comment — identity and treatment both recorded)'),
    # 8/4 rebuild adjudications of holding-company candidates (operations test):
    (r'Mediacom', 1, 'Clause (b) adjudicated 8/4: cable-telephony operator, parent brand of active filer MCC Telephony LLC; subscriber operations — Comcast class'),
    (r'Cisco Systems', 0, 'NOT treated (8/4): holding link to Tropo LLC is anachronistic — Cisco acquired Tropo 2015, breaches 2012; snapshot-era holding data'),
    (r'Citrix', 0, 'NOT treated (8/4): breaches are enterprise-software incidents, not telecom subscriber operations; 2018 event also post-divestiture of Citrix Online'),
    (r'^Google|Alphabet', 0, 'NOT treated (8/4): breaches are consumer web-service incidents (no Google Fiber subscriber data); clause (b) operations test fails'),
    (r'^Time ?Warner', 0, 'NOT treated (8/4): 2006 breach not a telecom-subscriber operation; holding link to HBO filer fails the operations test'),
    (r'Home Box Office', 0, 'NOT treated (8/4): HBO Inc filer TERMINATED 2012-12-31 ("no longer providing telecommunications services") before 2017 breaches — clause (a) fails at breach date'),
]

ev = pd.read_csv('Data/processed/rebuild/stage4_input.csv', low_memory=False)
ev['bdt'] = pd.to_datetime(ev['breach_date'])
log(f'\nClassifying {len(ev)} events (treated-if-any-variant)...')

res = []
for _, r in ev.iterrows():
    variants = [v.strip() for v in str(r['name_variants']).split('|')]
    treated, why = 0, ''
    holding_candidate = None
    for v in variants:
        for frn, sd, ed, er, legal, field in reg.get(normalize(v), []):
            if coverage_valid(sd, ed, er, r['bdt']):
                if field == 'holding_company':
                    # Clause (b) is ADJUDICATED, never mechanized: a holding-company
                    # match is candidate evidence only (operations test required).
                    holding_candidate = (v, legal, frn, sd, ed)
                    continue
                treated, why = 1, (f'Clause (a): registry match "{v}" [{field}] -> {legal} '
                                   f'(FRN {frn}, start {sd}, end {ed or "none"})')
                break
        if treated:
            break
    if not treated and holding_candidate:
        v, legal, frn, sd, ed = holding_candidate
        why = (f'CLAUSE-B CANDIDATE (not auto-treated): holding_company match "{v}" -> '
               f'{legal} (FRN {frn}); operations test adjudicated below if a rule exists')
    for pat, t, rationale in ADJ:
        if any(re.search(pat, v, re.IGNORECASE) for v in variants):
            treated, why = t, rationale
            break  # first matching adjudication wins (rules are mutually exclusive by construction)
    res.append((treated, why))
ev['fcc_form499'] = [t for t, _ in res]
ev['treatment_evidence'] = [w for _, w in res]

# Equity-parent map (FedEx Ground class, documented): subsidiary registrants with
# no traded equity re-parented to the public parent for the market layer.
EQUITY_PARENT = {
    1040573: (1166691, 'Comcast Cable Communications registrant has no equity; parent = Comcast Corp (Gate 1 verdict A class)'),
    1512267: (1166691, 'NBCUniversal Media LLC registrant has no equity; parent = Comcast Corp (Gate 1 verdict E class)'),
    1457937: (1105705, 'Home Box Office Inc registrant has no equity; 2017 parent = Time Warner Inc TWX (FedEx Ground class)'),
}
for sub, (parent, note) in EQUITY_PARENT.items():
    m = ev['final_cik'] == sub
    if m.any():
        ev.loc[m, 'final_cik'] = parent
        ev.loc[m, 'final_evidence'] = ev.loc[m, 'final_evidence'].astype(str) + f' | EQUITY-PARENT: {note}'
        log(f'  Equity-parent map: {int(m.sum())} events {sub} -> {parent} ({note[:60]})')
# re-collapse any firm-day dupes created by the re-parenting
dup_mask = ev.duplicated(subset=['final_cik', 'breach_date'], keep=False)
if dup_mask.any():
    log(f'  Re-collapsing {int(dup_mask.sum())} rows sharing firm-days after re-parenting...')
    ev = ev.sort_values(['final_cik', 'breach_date', 'n_source_records'], ascending=[True, True, False])
    keep_first = ~ev.duplicated(subset=['final_cik', 'breach_date'])
    merged_notes = ev[~keep_first].groupby([ev['final_cik'], ev['breach_date']])['org_name'].apply(list)
    ev = ev[keep_first].copy()

n_t = int(ev['fcc_form499'].sum())
t_orgs = ev.loc[ev['fcc_form499'] == 1, 'org_name'].nunique()
t_ciks = ev.loc[ev['fcc_form499'] == 1, 'final_cik'].nunique()
log(f'\nTreated: {n_t} events / {t_orgs} primary orgs / {t_ciks} parent CIKs '
    f'(of {len(ev)} events; counts are what they are — no targets)')
log('\nTreated events by parent CIK:')
for cik, g in ev[ev['fcc_form499'] == 1].groupby('final_cik'):
    log(f'  CIK {int(cik)}: {len(g)} events | {sorted(set(g["org_name"]))[:4]}')

ev.drop(columns=['bdt']).to_csv('Data/processed/rebuild/stage4_treated.csv', index=False)
with open('outputs/rebuild/STAGE4_TREATMENT_REPORT.md', 'w', encoding='utf-8') as f:
    f.write('# Stage 4 Treatment Report\n\n' + '\n'.join(L) + '\n')
log('\nSaved: stage4_treated.csv, STAGE4_TREATMENT_REPORT.md')
