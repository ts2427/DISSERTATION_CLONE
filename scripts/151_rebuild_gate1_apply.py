"""
REBUILD DIRECTIVE v2 — GATE 1 VERDICT APPLICATION
==================================================
Applies the signed Gate 1 second-pass verdicts (8/4/2026) to the Stage 2
entity-verified set. Standing rule implemented: ticker-named verdicts resolve
their final CIK via SEC company_tickers.json (authoritative); EDGAR-history
verifications performed 8/4 are recorded in the evidence strings:
  - Sprint-era registrant = CIK 101830 (SEC submissions: "SPRINT LLC", former
    names SPRINT CORP / SPRINT NEXTEL CORP, 10-Ks 2014-2019). Candidate 1585689
    is Hilton — the filings-history check the verdict required caught this.
  - AeroGrow operating registrant = 1316644 (13 10-Ks, 2008-2020).
  - CWGS Holding LLC (1683140) files nothing; reporting entity = Camping World
    Holdings 1669779.
  - USA Waste-Management Resources LLC = Waste Management family (1/2021
    employee-breach litigation names WMR + WM Inc. together) -> 823768.
Stop-and-report: leftover AMBIGUOUS/REVIEW orgs not covered by a verdict, and
any date-guard trips (Sirius post-9/2024, Change pre-10/2022, First American
pre-6/2010, LPL pre-11/2010) are LISTED, not resolved.

Outputs: Data/processed/rebuild/stage2_signed.csv
         outputs/rebuild/GATE1_APPLIED_LEDGER.csv
         outputs/rebuild/GATE1_APPLICATION_REPORT.md
"""

import sys
import re
import json
from pathlib import Path
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
OUT = Path('outputs/rebuild')
L = []


def log(m=''):
    print(m)
    L.append(str(m))


log('=' * 90)
log('GATE 1 VERDICT APPLICATION')
log('=' * 90)

u2 = pd.read_csv('Data/processed/rebuild/stage2_entity_verified.csv', low_memory=False)
assert len(u2) == 1054
u2['bdt'] = pd.to_datetime(u2['breach_date'])

with open('Data/edgar/company_tickers.json', encoding='utf-8') as f:
    ct = json.load(f)
T2C = {}
for _, rec in (ct.items() if isinstance(ct, dict) else enumerate(ct)):
    T2C.setdefault(rec['ticker'], int(rec['cik_str']))


def tk(ticker):
    assert ticker in T2C, f'HALT: ticker {ticker} not in company_tickers.json'
    return T2C[ticker]


D = pd.Timestamp
flags = []

# Each rule: (regex on org_name, function(record)->(cik|None, grade, evidence) or None to pass)
def fix(cik, ev):
    return lambda r: (cik, 'VERIFIED-GATE1', ev)


def tick(t, ev):
    c = tk(t)
    return lambda r: (c, 'VERIFIED-GATE1', f'{ev} (ticker {t} -> CIK {c})')


def excl(label, ev):
    return lambda r: (None, label, ev)


RULES = [
    # --- A: mechanical ticker-bearing registrant ---
    (r'^AT&T(,? Inc\.?)?$', tick('T', 'Gate1-A: active registrant; 5907 is pre-2005 AT&T Corp')),
    (r'^Adobe Systems Incorporated$', fix(796343, 'Gate1-A (ADBE)')),
    (r'^American Electric Power$', fix(4904, 'Gate1-A (AEP)')),
    (r'^Audacy', fix(1067837, 'Gate1-A: formerly Entercom, active registrant')),
    (r'^Carnival Corporation$', fix(815097, 'Gate1-A (CCL)')),
    (r'^Comcast$', fix(1166691, 'Gate1-A: 2002 AT&T-Comcast merger entity IS Comcast Corp; 22301 pre-2002')),
    (r'^Deluxe Corporation$', fix(27996, 'Gate1-A (DLX); legacy IDEX ticker was fuzzy noise')),
    (r'^DISH Network', fix(1001082, 'Gate1-A (DISH equity; 920436 is operating LLC)')),
    (r'^Duke Energy', fix(1326160, 'Gate1-A (DUK 2006 holdco; 30371 is Carolinas utility sub)')),
    (r'Fidelity National Information Services', fix(1136893, 'Gate1-A (FIS; Certegy renamed 2006 - legitimately FIS despite sink history)')),
    (r'^Freeport-McMoRan', fix(831259, 'Gate1-A (FCX)')),
    (r'^Oracle Corporation$', fix(1341439, 'Gate1-A (ORCL 2005 holdco)')),
    (r'^Roku', fix(1428439, 'Gate1-A (ROKU)')),
    (r'^Seagate Technology', fix(1137789, 'Gate1-A (STX)')),
    (r'^Sirius', lambda r: ((908937, 'VERIFIED-GATE1', 'Gate1-A (SIRI continuous registrant)')
                            if r['bdt'] < D('2024-09-01') else
                            (None, 'FLAG', 'Sirius record post-Sept-2024: Liberty split holdco question — REPORT'))),
    (r'^Snap Inc', fix(1564408, 'Gate1-A (SNAP)')),
    (r'^The J\.?M\.? Smucker', fix(91419, 'Gate1-A (SJM)')),
    (r'^W\.?\s?W\.? Grainger', fix(277135, 'Gate1-A (GWW)')),
    (r'^Aon Corporation$', fix(315293, 'Gate1-A (plain-name record, pre-redomiciliation registrant)')),
    # --- B: date splits ---
    (r'^Aon (Corporation )?PLC$|^Aon plc$', lambda r: ((315293, 'VERIFIED-GATE1', 'Gate1-B: pre-4/2020 US registrant')
                                                       if r['bdt'] < D('2020-04-01') else
                                                       (1808065, 'VERIFIED-GATE1', 'Gate1-B: Ireland redomiciliation entity'))),
    (r'^Caesars Entertainment', lambda r: ((858339, 'VERIFIED-GATE1', 'Gate1-B: old Caesars')
                                           if r['bdt'] < D('2020-07-01') else
                                           (1590895, 'VERIFIED-GATE1', 'Gate1-B: CZR Eldorado-merger entity'))),
    (r'^Google', lambda r: ((1288776, 'VERIFIED-GATE1', 'Gate1-B: Google Inc IPO registrant')
                            if r['bdt'] < D('2015-10-01') else
                            (tk('GOOGL'), 'VERIFIED-GATE1', 'Gate1-B: Alphabet Inc (ticker GOOGL)'))),
    (r'^Yahoo', lambda r: ((1011006, 'VERIFIED-GATE1', 'Gate1-B: YHOO registrant (later Altaba)')
                           if r['bdt'] < D('2017-06-01') else
                           ((732712, 'VERIFIED-GATE1', 'Gate1-B/E: Verizon Media window 6/2017-8/2021')
                            if r['bdt'] < D('2021-09-01') else
                            (None, 'EXCLUDED-PRIVATE', 'Gate1-B: post-Apollo sale, no public equity')))),
    (r'^The Walt Disney', lambda r: ((926480, 'VERIFIED-GATE1', 'Gate1-B: pre-2019-reorg registrant')
                                     if r['bdt'] < D('2019-03-20') else
                                     (1744489, 'VERIFIED-GATE1', 'Gate1-B: DIS holdco'))),
    (r'^Time ?Warner', lambda r: ((1105705, 'VERIFIED-GATE1', 'Gate1-B: TWX registrant 2009-6/2018')
                                  if r['bdt'] < D('2018-06-15') else
                                  (732717, 'VERIFIED-GATE1', 'Gate1-B: AT&T ownership, parent-mapped with rationale'))),
    (r'^Warner Music Group', lambda r: ((1319161, 'VERIFIED-GATE1', 'Gate1-B: WMG public window')
                                        if (r['bdt'] < D('2011-07-20') or r['bdt'] >= D('2020-06-03')) else
                                        (None, 'EXCLUDED-PRIVATE-WINDOW', 'Gate1-B: Access Industries private window 2011-2020'))),
    (r'^Nuance Communications', lambda r: ((1002517, 'VERIFIED-GATE1', 'Gate1-B: pre-3/2022 registrant')
                                           if r['bdt'] < D('2022-03-04') else
                                           (tk('MSFT'), 'VERIFIED-GATE1', 'Gate1-B: Microsoft subsidiary, parent-mapped'))),
    (r'^First American Financial', lambda r: ((1472787, 'VERIFIED-GATE1', 'Gate1-B (FAF post-2010 spinoff; ex-placeholder victim of PNC sink)')
                                              if r['bdt'] >= D('2010-06-01') else
                                              (None, 'FLAG', 'First American record pre-6/2010 spinoff — REPORT'))),
    # --- C: outside candidate list ---
    (r'T-Mobile', lambda r: (1283699, 'VERIFIED-GATE1',
                             'Gate1-C: TMUS public parent' + (' | NOTE: pre-5/2013 no US public equity — will fail CRSP naturally'
                                                              if r['bdt'] < D('2013-05-01') else ''))),
    (r'^Charter Communication', tick('CHTR', 'Gate1-C: traded registrant via ticker')),
    (r'^CyrusOne', fix(1553023, 'Gate1-C: CYRUSONE INC. via EDGAR names (CONE delisted 2022, ticker-file fallback documented)')),
    (r'^Change Healthcare', lambda r: ((tk('UNH'), 'VERIFIED-GATE1', 'Gate1-C: UnitedHealth parent post-10/2022 acquisition; legacy GEHC was fuzzy error')
                                       if r['bdt'] >= D('2022-10-03') else
                                       (None, 'FLAG', 'Change Healthcare record pre-10/2022 (CHNG era) — REPORT'))),
    (r'^FedEx Ground', tick('FDX', 'Gate1-C: wholly owned subsidiary, parent-mapped')),
    (r'^LPL Financial', lambda r: ((tk('LPLA'), 'VERIFIED-GATE1', 'Gate1-C: LPL Financial Holdings post-11/2010 IPO; legacy PNC was placeholder error')
                                   if r['bdt'] >= D('2010-11-01') else
                                   (None, 'FLAG', 'LPL record pre-11/2010 IPO — REPORT'))),
    # --- F: Sprint family (BEFORE generic patterns; overrides Stage 2 adjudication) ---
    (r'Sprint|Boost Mobile|Virgin Mobile', lambda r: ((101830, 'VERIFIED-GATE1',
                                                       'Gate1-F: Sprint-era equity (SEC-verified: SPRINT LLC fka SPRINT CORP/NEXTEL, 10-Ks 2014-2019)')
                                                      if r['bdt'] < D('2020-04-01') else
                                                      (1283699, 'VERIFIED-GATE1', 'Gate1-F: TMUS post-merger'))),
    # --- D: exclusions and the AeroGrow exception ---
    (r'^Aladdin Capital', excl('EXCLUDED-PRIVATE', 'Gate1-D: private; legacy COF was noise')),
    (r'^Eagle Capital Management', excl('EXCLUDED-PRIVATE', 'Gate1-D: private; legacy COF was noise')),
    (r'MSX International', excl('EXCLUDED-PRIVATE', 'Gate1-D: PE-owned; legacy AIG was noise')),
    (r'^AeroGrow', lambda r: ((1316644, 'VERIFIED-GATE1', 'Gate1-D exception: SEC-verified operating registrant (10-Ks 2008-2020); legacy AIG carried American International Group returns')
                              if D('2006-01-01') <= r['bdt'] <= D('2022-02-28') else
                              (None, 'EXCLUDED-UNLISTED-WINDOW', 'Gate1-D: outside listed window'))),
    # --- E: review pile ---
    (r'^NBC Sports Group$', fix(1166691, 'Gate1-E: identity=Comcast equity; treatment classification independent (clause rules at Stage 4)')),
    (r'^Verizon Corporate Services', fix(732712, 'Gate1-E: operating subsidiary')),
    (r'^Verizon Media', lambda r: ((732712, 'VERIFIED-GATE1', 'Gate1-E: Verizon ownership window 7/2017-8/2021')
                                   if D('2017-07-01') <= r['bdt'] < D('2021-09-01') else
                                   (None, 'EXCLUDED-PRIVATE', 'Gate1-E: post-Apollo sale'))),
    # --- G: rescues ---
    (r'^GoDaddy', lambda r: ((tk('GDDY'), 'VERIFIED-GATE1', 'Gate1-G rescue: GoDaddy Inc post-4/2015 IPO (Form 499 relevant)')
                             if r['bdt'] >= D('2015-04-01') else
                             (None, 'EXCLUDED-PRE-IPO', 'Gate1-G: pre-IPO'))),
    (r'^IBM$', tick('IBM', 'Gate1-G rescue: acronym defeated exact match; documented acronym mapping')),
    (r'^CenturyLink Communications$', tick('LUMN', 'Gate1-G rescue: CenturyLink/Lumen parent (Form 499 relevant carrier)')),
    (r'Est.?.?e Lauder|Estee Lauder', tick('EL', 'Gate1-G rescue: text-encoding artifact defeated matching; legacy 1001250 was correct')),
    (r'^ATT-Breach Notification', fix(732717, 'Gate1-G rescue: artifact-name record, AT&T equity (same class as ATT-SecurityBreach)')),
    (r'^Gallagher NAC$', tick('AJG', 'Gate1-G rescue: Arthur J. Gallagher subsidiary; legacy 354190 was right')),
    (r'^Paramount', lambda r: ((813828, 'VERIFIED-GATE1', 'Gate1-G: Paramount Global pre-Skydance close (PARA delisted from current ticker file; EDGAR-name fallback documented, CyrusOne class)')
                               if r['bdt'] < D('2025-08-07') else
                               (2041610, 'VERIFIED-GATE1', 'Gate1-G: post-close merged registrant'))),
    (r'^CWGS Group', fix(1669779, 'Gate1-G rescue: Camping World Holdings (EDGAR-verified: CWGS Holding LLC 1683140 files nothing; CWH is reporting entity)')),
    (r'^Flutter International', lambda r: ((1635327, 'VERIFIED-GATE1', 'Gate1-G: Flutter Entertainment plc, NYSE-listed 1/2024')
                                           if r['bdt'] >= D('2024-01-29') else
                                           (None, 'EXCLUDED-NO-US-LISTING', 'Gate1-G: pre-US-listing'))),
    (r'USA Waste-Management Resources', fix(823768, 'Gate1-G rescue: Waste Management family (public-record verified: 1/2021 WMR+WM employee-breach litigation)')),
]

log(f'\nApplying {len(RULES)} verdict rules to 1,054 records...')
applied = 0
u2['final_cik'] = u2['resolved_cik']
u2['final_grade'] = u2['grade']
u2['final_evidence'] = u2['evidence']
for pat, fn in RULES:
    rx = re.compile(pat, re.IGNORECASE)
    mask = u2['org_name'].astype(str).str.contains(rx)
    for idx in u2.index[mask]:
        res = fn(u2.loc[idx]) if not isinstance(fn, tuple) else fn[0](u2.loc[idx])
        if isinstance(res, tuple) and isinstance(res[0], tuple):
            res = res[0]
        cik, grade, ev = res
        u2.at[idx, 'final_cik'] = cik
        u2.at[idx, 'final_grade'] = grade
        u2.at[idx, 'final_evidence'] = ev
        applied += 1
log(f'  Records touched by verdicts: {applied}')

# Confirm-excluded closing paragraph: everything still EXCLUDED-UNRESOLVED is confirmed
u2.loc[u2['final_grade'] == 'EXCLUDED-UNRESOLVED', 'final_evidence'] = \
    'Gate1-confirmed exclusion (FISC precedent; incl. formal Impact Mobile Home Communities closure)'

log('\nFinal grade distribution (records):')
log('  ' + u2['final_grade'].value_counts().to_string().replace('\n', '\n  '))

# Stop-and-report lists
flag_rows = u2[u2['final_grade'] == 'FLAG']
leftover = u2[u2['final_grade'].isin(['AMBIGUOUS', 'REVIEW'])]
log(f'\nSTOP-AND-REPORT: date-guard flags: {len(flag_rows)} records; '
    f'leftover AMBIGUOUS/REVIEW not covered by any verdict: '
    f'{leftover["org_name"].nunique()} orgs / {len(leftover)} records')

retained = u2[u2['final_cik'].notna() & ~u2['final_grade'].isin(
    ['FLAG', 'AMBIGUOUS', 'REVIEW'])]
log(f'\nRetained (resolved, non-flagged): {len(retained)} records, '
    f'{retained["org_name"].nunique()} orgs, {retained["final_cik"].nunique()} unique CIKs')

u2.drop(columns=['bdt']).to_csv('Data/processed/rebuild/stage2_signed.csv', index=False)
led = (u2.groupby(['org_name', 'final_grade'])
       .agg(n=('org_name', 'size'), cik=('final_cik', 'first'),
            evidence=('final_evidence', 'first')).reset_index())
led.to_csv(OUT / 'GATE1_APPLIED_LEDGER.csv', index=False)

with open(OUT / 'GATE1_APPLICATION_REPORT.md', 'w', encoding='utf-8') as f:
    f.write('# Gate 1 Application Report\n\n' + '\n'.join(L) + '\n\n')
    if len(flag_rows):
        f.write('## FLAGGED (unresolved date-guard trips)\n\n')
        for _, r in flag_rows.iterrows():
            f.write(f"- {r['org_name']} | {r['breach_date']} | {r['final_evidence']}\n")
    if len(leftover):
        f.write('\n## LEFTOVER AMBIGUOUS/REVIEW (no verdict covered these)\n\n')
        for org, g in leftover.groupby('org_name'):
            f.write(f"- {org} ({len(g)} rec) | {g['evidence'].iloc[0][:150]}\n")

log('\nSaved: stage2_signed.csv, GATE1_APPLIED_LEDGER.csv, GATE1_APPLICATION_REPORT.md')
