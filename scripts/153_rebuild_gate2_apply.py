"""
REBUILD DIRECTIVE v2 — GATE 2 APPLICATION
==========================================
Applies the signed Gate 2 verdicts (8/4/2026):
  - Collapse CH-06 (Verizon: one insider incident, two state filings; types are
    state-schema variance), CH-09/CH-10 (Intuit 2016 credential-stuffing
    campaign), and the 25 approved same-type chains. KEEP CH-27 (T-Mobile 2009;
    public record inconclusive; low stakes — pre-2013, dies at CRSP).
  - Fox Entertainment Group (2 records): parent-map to CIK 1308161 (registrant
    named News Corporation in 2009; renamed Twenty-First Century Fox 2013;
    SEC-verified filings end at 3/2019 Disney close).
  - CH-21 TALX: parent-map to Equifax CIK 33185 (TALX filings end 2007;
    2016 breaches occurred under Equifax ownership; FedEx Ground class).
  - CH-04 Sierra Pacific: SEC-verified — CIK 90143 IS Sierra Pacific Industries'
    own registrant (1 ARS 2006, no 10-Ks, no ticker). Identity kept; grade noted
    PRIVATE-REGISTRANT (no equity; fails CRSP legitimately, per CH-31 rule).
  - CH-31 IMA: SEC-verified — 1673769 is IMA Financial Group's own private
    registrant (Form D filer). Identity kept; PRIVATE-REGISTRANT note.
Chain collapse convention: earliest date is the event date (campaign start),
variants and dates concatenated, records-affected max, types unioned,
campaign/multi-filing documented.

Output: Data/processed/rebuild/stage4_input.csv
"""

import sys
from pathlib import Path
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
L = []


def log(m=''):
    print(m)
    L.append(str(m))


log('=' * 90)
log('GATE 2 APPLICATION')
log('=' * 90)

ev = pd.read_csv('Data/processed/rebuild/stage3_events.csv', low_memory=False)
adj = pd.read_csv('outputs/rebuild/GATE2_ADJACENCY_SHEET.csv')
n0 = len(ev)

# 1. Chain collapses: all proposals plus flagged CH-06/09/10; keep CH-27.
todo = adj[(adj['PROPOSED'] == 'COLLAPSE (proposed)') |
           (adj['chain'].isin(['CH-06', 'CH-09', 'CH-10']))]
assert 'CH-27' not in set(todo['chain'])
log(f'\nCollapsing {len(todo)} chains (28 approved + CH-06/09/10 signed; CH-27 kept)...')
ev['bdt'] = pd.to_datetime(ev['breach_date'])
drop_idx = []
for _, ch in todo.iterrows():
    dates = [d.strip() for d in ch['dates'].split(',')]
    m = ev[(ev['final_cik'] == ch['cik']) & (ev['breach_date'].isin(dates))].sort_values('bdt')
    if len(m) < 2:
        continue
    keep = m.index[0]
    note = ('CAMPAIGN' if ch['chain'] in ('CH-09', 'CH-10') or m['n_source_records'].sum() > 3
            else 'NEAR-DUPLICATE CHAIN')
    ev.at[keep, 'name_variants'] = ' | '.join(sorted(set(' | '.join(m['name_variants']).split(' | '))))
    ev.at[keep, 'n_source_records'] = int(m['n_source_records'].sum())
    types = sorted({t for x in m['breach_type'].dropna() for t in x.split('+')})
    ev.at[keep, 'breach_type'] = '+'.join(types)
    ev.at[keep, 'multi_type'] = len(types) > 1
    ev.at[keep, 'total_affected_max'] = m['total_affected_max'].max()
    ev.at[keep, 'multi_filing'] = True
    ev.at[keep, 'chain_note'] = (f'{note} {ch["chain"]}: {len(m)} firm-day events collapsed '
                                 f'[{ch["dates"]}] (Gate 2 signed; record-count gaps not a '
                                 f'distinctness signal)')
    drop_idx += list(m.index[1:])
ev = ev.drop(index=drop_idx)
log(f'  Events: {n0} -> {len(ev)}')

# 2. Fox parent-map (records were held out at Gate 1 as AMBIGUOUS)
s2 = pd.read_csv('Data/processed/rebuild/stage2_signed.csv', low_memory=False)
fox = s2[s2['org_name'].str.contains('Fox Entertainment', na=False)].copy()
log(f'\nFox Entertainment Group: {len(fox)} records -> CIK 1308161 (News Corp 2009 registrant, SEC-verified lineage)')
fox_events = []
for _, r in fox.iterrows():
    fox_events.append({'final_cik': 1308161, 'breach_date': r['breach_date'],
                       'org_name': r['org_name'], 'name_variants': r['org_name'],
                       'n_source_records': 1, 'breach_type': r.get('breach_type'),
                       'multi_type': False,
                       'total_affected_max': pd.to_numeric(str(r.get('total_affected', '')).replace(',', ''), errors='coerce'),
                       'multi_filing': False, 'incident_details': r.get('incident_details'),
                       'reported_date': r.get('reported_date'), 'end_breach_date': r.get('end_breach_date'),
                       'information_affected': r.get('information_affected'),
                       'organization_type': r.get('organization_type'),
                       'final_grade': 'VERIFIED-GATE2',
                       'final_evidence': 'Gate2: News Corp subsidiary 2009 (registrant later 21st Century Fox; FedEx Ground class)'})
ev = pd.concat([ev, pd.DataFrame(fox_events)], ignore_index=True)

# 3. TALX -> Equifax
talx = ev['name_variants'].astype(str).str.contains('TALX', case=False, na=False)
log(f'TALX events re-parented to Equifax 33185: {int(talx.sum())}')
ev.loc[talx, 'final_cik'] = 33185
ev.loc[talx, 'final_evidence'] = ('Gate2 CH-21: TALX filings end 2007 (SEC-verified); 2016 breaches under '
                                  'Equifax ownership; parent-map via EFX')

# 4. Sierra Pacific + IMA: identity kept, private-registrant note
for pat, cik, note in [('Sierra Pacific Industries', 90143,
                        'SEC-verified: own registrant, 1 ARS 2006, no equity — fails CRSP legitimately'),
                       ('IMA Financial', 1673769,
                        'SEC-verified: own private registrant (Form D filer) — fails CRSP legitimately')]:
    m = ev['name_variants'].astype(str).str.contains(pat, case=False, na=False)
    ev.loc[m, 'final_evidence'] = f'Gate2 PRIVATE-REGISTRANT: {note}'
    log(f'{pat}: {int(m.sum())} events noted PRIVATE-REGISTRANT (CIK {cik} kept)')

ev = ev.drop(columns=['bdt']).sort_values(['final_cik', 'breach_date']).reset_index(drop=True)
dup = ev.duplicated(subset=['final_cik', 'breach_date']).sum()
assert dup == 0, f'HALT: {dup} duplicate firm-days after Gate 2'
ev.to_csv('Data/processed/rebuild/stage4_input.csv', index=False)
log(f'\nFinal Gate 2 event set: {len(ev)} events, {ev["final_cik"].nunique()} CIKs '
    f'-> Data/processed/rebuild/stage4_input.csv')
