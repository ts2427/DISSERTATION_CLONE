"""
REBUILD DIRECTIVE v2 — STAGE 3: DEDUPLICATION (on the entity-verified base)
===========================================================================
Input: Gate 1-signed record set (retained grades only).
(a) normalized-name + breach-date collapse — with CIK-resolved identity this is
    subsumed by (b); run as a consistency check (any same-name-same-date pair
    at DIFFERENT CIKs would be an entity-resolution error and HALTS).
(b) CIK + breach-date collapse — ALWAYS, per directive: one observation per
    firm-day. Name variants preserved in a variants field (Stage 4 classifies
    treatment across ALL variants, treated-if-any); records-affected takes the
    maximum with multi-filing noted; breach types unioned with multi-type note.
(c) Adjacent-date candidates (chains with gaps <= 3 calendar days at the same
    CIK): PROPOSALS ONLY, revised rules — record-count differences are NOT a
    distinctness signal; same-type chains (incl. rolling campaigns, the Intuit
    pattern) propose COLLAPSE with campaign documented; type-conflict chains
    FLAG for the Gate 2 sitting.

Outputs: Data/processed/rebuild/stage3_events.csv          (post a+b)
         outputs/rebuild/GATE2_ADJACENCY_SHEET.csv / .md   (sitting package)
STOPS AT GATE 2.
"""

import sys
import re
from pathlib import Path
import pandas as pd
import numpy as np

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
OUT = Path('outputs/rebuild')
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
log('REBUILD STAGE 3: DEDUPLICATION')
log('=' * 90)

d = pd.read_csv('Data/processed/rebuild/stage2_signed.csv', low_memory=False)
keep_grades = ['VERIFIED', 'VERIFIED-GATE1', 'VERIFIED-REASONING', 'ADJUDICATED']
r = d[d['final_grade'].isin(keep_grades) & d['final_cik'].notna()].copy()
r['final_cik'] = r['final_cik'].astype(int)
r['bdt'] = pd.to_datetime(r['breach_date'])
log(f'\nInput: {len(r)} retained records, {r["org_name"].nunique()} orgs, '
    f'{r["final_cik"].nunique()} CIKs')

# (a) consistency check
r['nn'] = r['org_name'].map(normalize)
chk = r.groupby(['nn', 'breach_date'])['final_cik'].nunique()
bad = chk[chk > 1]
assert len(bad) == 0, f'HALT: same normalized name+date at different CIKs: {bad.index.tolist()[:5]}'
log('(a) Normalized-name+date consistency: PASS (no name+date pair spans CIKs)')

# (b) CIK + date collapse — always
r['ta_num'] = pd.to_numeric(
    r['total_affected'].astype(str).str.replace(',', '').str.replace('+', '', regex=False),
    errors='coerce')


def collapse(g):
    names = sorted(g['org_name'].unique())
    primary = g['org_name'].mode().sorted_values().iloc[0] if hasattr(g['org_name'].mode(), 'sorted_values') else sorted(g['org_name'].mode())[0]
    types = sorted(set(g['breach_type'].dropna()))
    det = g.loc[g['incident_details'].astype(str).str.len().idxmax(), 'incident_details']
    return pd.Series({
        'org_name': primary,
        'name_variants': ' | '.join(names),
        'n_source_records': len(g),
        'breach_type': '+'.join(types) if types else None,
        'multi_type': len(types) > 1,
        'total_affected_max': g['ta_num'].max(),
        'multi_filing': len(g) > 1,
        'incident_details': det,
        'reported_date': g['reported_date'].min(),
        'end_breach_date': g['end_breach_date'].max(),
        'information_affected': g.loc[g['information_affected'].astype(str).str.len().idxmax(), 'information_affected'],
        'organization_type': g['organization_type'].mode().iloc[0] if g['organization_type'].notna().any() else None,
        'final_grade': '|'.join(sorted(set(g['final_grade']))),
        'final_evidence': g['final_evidence'].iloc[0],
    })


ev = r.groupby(['final_cik', 'breach_date']).apply(collapse, include_groups=False).reset_index()
n_collapsed = len(r) - len(ev)
log(f'(b) CIK+date collapse: {len(r)} records -> {len(ev)} firm-day events '
    f'({n_collapsed} collapsed; {int(ev["multi_filing"].sum())} events carry multi-filing notes)')

ev.to_csv('Data/processed/rebuild/stage3_events.csv', index=False)

# (c) adjacency chains (<=3-day gaps, same CIK) — proposals only
ev['bdt'] = pd.to_datetime(ev['breach_date'])
rows = []
chain_id = 0
for cik, g in ev.groupby('final_cik'):
    g = g.sort_values('bdt').reset_index(drop=True)
    i = 0
    while i < len(g):
        j = i
        while j + 1 < len(g) and (g.loc[j + 1, 'bdt'] - g.loc[j, 'bdt']).days <= 3:
            j += 1
        if j > i:
            chain_id += 1
            members = g.iloc[i:j + 1]
            types = set()
            for t in members['breach_type'].dropna():
                types.update(t.split('+'))
            same_type = len(types) <= 1
            n_ev = len(members)
            if same_type:
                proposal = 'COLLAPSE (proposed)'
                rule = ('Rolling-campaign/near-duplicate rule: same firm, same type, <=3-day gaps. '
                        'Record-count differences are NOT a distinctness signal (state-resident counts).')
            else:
                proposal = 'FLAG - SITTING'
                rule = f'Breach types conflict within chain ({sorted(types)}); public-record test applies.'
            rows.append({'chain': f'CH-{chain_id:02d}', 'cik': cik,
                         'org': members['org_name'].iloc[0], 'n_events': n_ev,
                         'dates': ', '.join(members['breach_date']),
                         'types': '+'.join(sorted(types)),
                         'variants': ' || '.join(members['name_variants']),
                         'details_first': str(members['incident_details'].iloc[0])[:110],
                         'PROPOSED': proposal, 'rule': rule})
        i = j + 1
adj = pd.DataFrame(rows)
n_collapse_prop = int((adj['PROPOSED'] == 'COLLAPSE (proposed)').sum()) if len(adj) else 0
n_flag = int((adj['PROPOSED'] == 'FLAG - SITTING').sum()) if len(adj) else 0
excess_if_all = int((adj[adj['PROPOSED'] == 'COLLAPSE (proposed)']['n_events'] - 1).sum()) if len(adj) else 0
log(f'(c) Adjacency chains: {len(adj)} chains — {n_collapse_prop} propose COLLAPSE '
    f'({excess_if_all} events would merge away), {n_flag} FLAGGED for the sitting')

adj.to_csv(OUT / 'GATE2_ADJACENCY_SHEET.csv', index=False)
with open(OUT / 'GATE2_ADJACENCY_SHEET.md', 'w', encoding='utf-8') as f:
    f.write('# GATE 2 — Adjudication Sitting Package\n\n')
    f.write('\n'.join(L))
    f.write('\n\n## One unsigned entity resolution (2 records)\n\n')
    f.write('- **Fox Entertainment Group / Fox Entertainment Group Inc.** (2009-04-09, '
            '2009-04-15): in 2009 Fox Entertainment Group was a wholly-owned News '
            'Corporation subsidiary (public minority bought out 2005; legacy ticker FOXA '
            'is anachronistic — Fox Corp exists only from 2019). PROPOSED: parent-map to '
            'News Corporation (CIK 1308161) with subsidiary rationale (FedEx Ground '
            'class), or exclude. Two records ride on the call.\n')
    f.write('\n## FLAGGED chains (your judgment needed)\n\n')
    for _, c in adj[adj['PROPOSED'] == 'FLAG - SITTING'].iterrows():
        f.write(f"### {c['chain']} — {c['org']} (CIK {c['cik']}, {c['n_events']} events)\n")
        f.write(f"- Dates: {c['dates']} | Types: {c['types']}\n")
        f.write(f"- Variants: {c['variants']}\n- First detail: {c['details_first']}\n")
        f.write(f"- Rule: {c['rule']}\n\n")
    f.write('\n## COLLAPSE proposals (confirm by exception)\n\n')
    for _, c in adj[adj['PROPOSED'] == 'COLLAPSE (proposed)'].iterrows():
        f.write(f"- {c['chain']} {c['org']} (CIK {c['cik']}): {c['n_events']} events "
                f"[{c['dates']}] type={c['types']}\n")

log('\nGATE 2 package: outputs/rebuild/GATE2_ADJACENCY_SHEET.md (+csv). '
    'Stage 3 event set: Data/processed/rebuild/stage3_events.csv')
log('STOPPING AT GATE 2 per directive.')
