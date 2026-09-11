"""
ESSAY 3 QUERY 1 — PART E: HAND-READ CODES FOR THE 35 T-MOBILE-CIK 5.02 FILINGS (NEW)
=====================================================================================
Codes below were assigned by reading the Item 5.02 section of each filing
(text via scripts/184; URLs in outputs/essay3_q1/e2_tmobile_502_text.csv), 2026-09-11.
The rules tags emitted by scripts/184 are NOT used: every Item 5.02 caption reads
"Departure of Directors or Certain Officers; ... Compensatory Arrangements ...",
so the departure and compensation rules fire on the caption itself (35/35).

sub_items: the 5.02 paragraph(s) the text reports. departure: whose service ends
(none / director / officer / CEO). ceo_departure: the principal executive officer
leaves the CEO role in this filing.

Output: outputs/essay3_q1/e2_tmobile_502_handcoded.csv (one row per filing) and
        outputs/essay3_q1/e2_tmobile_events_x_filings.csv (one row per event-filing pair)
"""

import sys
from pathlib import Path
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
OUT = Path('outputs/essay3_q1')

# accession: (sub_items, person / role / what the text says, departure, ceo_departure)
CODES = {
    '0001193125-10-050196': ('e', 'NEO option and restricted-stock grants (Linquist CEO, Keys, Carter, Stachiw)', 'none', 0),
    '0001193125-12-056765': ('e', 'NEO option and restricted-stock grants (incl. Lorang, SVP & Chief Technology Officer)', 'none', 0),
    '0001445305-12-001909': ('e', 'Severance Pay Plan amendment (President/COO; CFO/Vice Chairman)', 'none', 0),
    '0001283699-12-000010': ('b', 'C. Kevin Landry, director: will not stand for reelection (no disagreement; health)', 'director', 0),
    '0001283699-12-000027': ('e', 'Restricted stock / change-in-control agreement amendments (merger)', 'none', 0),
    '0001283699-13-000011': ('e', 'NEO option and restricted-stock grants', 'none', 0),
    '0001283699-13-000134': ('b,d', 'Rene Obermann resigned as director; Thomas Dannenfeldt appointed director', 'director', 0),
    '0001193125-13-448555': ('b,d', 'Srikant Datar resigned and was re-appointed the same day (DT designation mechanics)', 'director (technical; re-appointed)', 0),
    '0001193125-14-058782': ('b', 'James N. Perry Jr., director: will not stand for reelection', 'director', 0),
    '0001193125-16-470124': ('b,e', 'Gary A. King, EVP & Chief Information Officer: employment terminates 2016-03-18; one year base salary for release', 'officer (CIO)', 0),
    '0001193125-17-377654': ('e', 'J. Braxton Carter, EVP & CFO: amended and restated employment agreement', 'none', 0),
    '0001193125-18-051913': ('d', 'G. Michael Sievert (COO) elected director; board enlarged 11 to 12', 'none', 0),
    '0001283699-18-000063': ('b', 'Thomas Dannenfeldt, director: resigns effective 2018-12-01 (leaving Deutsche Telekom)', 'director', 0),
    '0001283699-18-000071': ('d', 'Christian P. Illek elected director to fill Dannenfeldt vacancy', 'none', 0),
    '0001193125-20-041926': ('e', 'David Carey, EVP Corporate Services: comp term-sheet amendment; employment terminates on position elimination (by 2020-07-01)', 'officer (anticipated; filed as comp)', 0),
    '0001193125-20-071678': ('b', 'David Carey, EVP Corporate Services: will retire effective 2020-04-30', 'officer', 0),
    '0001283699-20-000064': ('e', 'Neville Ray, President Technology: special PRSU award', 'none', 0),
    '0001193125-20-093622': ('b,c,d,e', 'CEO transition at Sprint merger close: John Legere employment as CEO terminated; G. Michael Sievert named CEO; Bruno Jacobfeuerborn resigned as director; SoftBank designees appointed; Legere/Sievert agreement amendments', 'CEO + director', 1),
    '0001193125-20-109354': ('b,e', 'David Carey departs effective 2020-04-13; severance per existing agreements', 'officer', 0),
    '0001193125-20-119230': ('b', 'John Legere resigned from the Board (text: departed as CEO on 2020-04-01)', 'director (former CEO)', 0),
    '0001140361-20-014081': ('b,c', 'J. Braxton Carter, EVP & CFO: retires effective 2020-07-01; Peter Osvaldik appointed CFO; Dara Bazzano appointed CAO', 'officer (principal financial officer)', 0),
    '0001140361-20-014470': ('b', 'Ronald D. Fisher resigned as director (Second A&R Stockholders Agreement)', 'director', 0),
    '0001193125-20-291827': ('b,d', 'Srini Gopalan resigned as director; Leroy, Tazi, Wilkens appointed', 'director', 0),
    '0001193125-21-076354': ('e', 'PRSU grants to Sievert (CEO), Osvaldik (CFO), Ray', 'none', 0),
    '0001193125-21-113210': ('b', 'Stephen Kappes resigned as director (also National Security Director, per 2021-06-24 filing)', 'director (National Security Director role)', 0),
    '0001193125-21-198692': ('d', 'Letitia Long appointed director and National Security Director (merger national-security commitments)', 'none', 0),
    '0001193125-21-275230': ('b', 'David A. Miller, EVP General Counsel & Secretary: retires 2022-04-01; leaves GC role 2021-10-11', 'officer', 0),
    '0001193125-22-115091': ('b', 'Michael Wilkens, director: will not stand for re-election (leaving Deutsche Telekom)', 'director', 0),
    '0001193125-23-024130': ('b', 'Bavan Holloway, director: will not stand for re-election', 'director', 0),
    '0001193125-23-035719': ('e', 'Neville Ray, President Technology: retirement letter agreement (retirement on or about 2023-10-01)', 'officer (announced retirement; filed as comp)', 0),
    '0001193125-23-066908': ('e', 'G. Michael Sievert, CEO: A&R employment agreement extending term five years', 'none (CEO retention)', 0),
    '0001193125-23-171171': ('e', '2023 Incentive Award Plan and ESPP approved at annual meeting (with 5.07)', 'none', 0),
    '0001193125-23-185341': ('e', 'PRSU grant to Peter Osvaldik (CFO)', 'none', 0),
    '0001193125-23-190499': ('d', 'James J. Kavanaugh elected director', 'none', 0),
    '0001193125-23-231377': ('e', 'Peter Ewens, EVP Corporate Strategy: retirement letter agreement (retires 2024-02-01)', 'officer (announced retirement; filed as comp)', 0),
}

T = pd.read_csv(OUT / 'e2_tmobile_502_text.csv', dtype={'accession': str})
assert set(T['accession']) == set(CODES), 'hand codes must cover exactly the 35 filings'
H = pd.DataFrame([{'accession': a, 'sub_items': c[0], 'what_the_text_says': c[1],
                   'departure': c[2], 'ceo_departure': c[3]} for a, c in CODES.items()])
H = T[['filing_date', 'accession', 'filer_vintage', 'items', 'url']].merge(H, on='accession')
H['is_502b'] = H['sub_items'].str.contains('b').astype(int)
H['officer_departure'] = H['departure'].str.startswith(('officer', 'CEO')).astype(int)
H.to_csv(OUT / 'e2_tmobile_502_handcoded.csv', index=False)

P = pd.read_csv(OUT / 'e2_tmobile_502_filings.csv', dtype={'accession': str})
X = P[['breach_date', 'org_name', 'in_essay3_sample', 'filing_date', 'days_from_t0', 'accession']].merge(
    H[['accession', 'sub_items', 'departure', 'ceo_departure', 'is_502b', 'officer_departure',
       'what_the_text_says']], on='accession')
X = X.sort_values(['breach_date', 'filing_date'])
X.to_csv(OUT / 'e2_tmobile_events_x_filings.csv', index=False)

print(f'Filings: {len(H)} | with 5.02(b) in text: {int(H["is_502b"].sum())} | officer departures '
      f'(incl. CEO): {int(H["officer_departure"].sum())} | CEO departures: {int(H["ceo_departure"].sum())}')
ev = pd.read_csv(OUT / 'e1_tmobile_events.csv')
for _, e in ev.iterrows():
    x = X[X['breach_date'] == e['breach_date']]
    flag = 'IN Essay 3 sample' if e['in_essay3_sample'] == 1 else 'not in sample'
    print(f"\n{e['breach_date']} ({e['org_name']}; {flag}; {e['cik_vintage_at_t0']}) — "
          f"{len(x)} 5.02 filings in (t0, t0+180d]; 5.02(b) {int(x['is_502b'].sum())}; officer "
          f"{int(x['officer_departure'].sum())}; CEO {int(x['ceo_departure'].sum())}")
    for _, r in x.iterrows():
        print(f"   +{r['days_from_t0']:>3}d {r['filing_date']} [{r['sub_items']}] {r['what_the_text_says']}")
s = X[X['in_essay3_sample'] == 1]
print(f"\nEssay 3 sample events (26): with any 5.02(b) filing in 180d: "
      f"{s.loc[s['is_502b'] == 1, 'breach_date'].nunique()}; with officer departure: "
      f"{s.loc[s['officer_departure'] == 1, 'breach_date'].nunique()}; with CEO departure: "
      f"{s.loc[s['ceo_departure'] == 1, 'breach_date'].nunique()}")
