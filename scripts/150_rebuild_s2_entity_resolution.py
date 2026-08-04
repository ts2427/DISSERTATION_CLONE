"""
REBUILD DIRECTIVE v2 — STAGES 1-2: UNIVERSE + ENTITY RESOLUTION
================================================================
Stage 1: assert the 1,054-record universe (the only inherited artifact).
Stage 2: resolve every organization's identity fresh — exact-and-abstain against
the SEC EDGAR historical name file, then the documented reasoning-pass layer,
then documented subsidiary adjudications. The legacy cik column in the universe
is treated as a LEGACY ANNOTATION to be compared against, never trusted.
Verification pass grades every org; suspect token-collision sink CIKs reported
by name. NO fuzzy matching anywhere. The mutate-while-iterating subsidiary bug
from the retired matcher does not exist here (clean reimplementation). PERMNO
selection is Stage 5's concern, not this script's.

Grades:
  VERIFIED            exact-and-abstain hit; org name is an EDGAR name of the CIK
  VERIFIED-REASONING  reasoning-pass CIK independently confirmed against EDGAR
                      names or SEC company_tickers titles
  ADJUDICATED         documented subsidiary/brand mapping (listed, with rationale)
  REVIEW              resolved but not independently confirmable — Gate 1 eyes
  AMBIGUOUS           name normalizes to multiple CIKs — Gate 1 eyes
  EXCLUDED-UNRESOLVED no match in any layer (FISC precedent: no valid
                      public-market observation unless Gate 1 overturns)

Outputs:
  outputs/rebuild/GATE1_ENTITY_VERIFICATION_LEDGER.csv  (one row per org)
  outputs/rebuild/GATE1_SUMMARY.md                       (sign-off package)
  outputs/rebuild/GATE1_suspect_cik_report.csv
  Data/processed/rebuild/stage2_entity_verified.csv      (record-level, graded)
"""

import sys
import re
import json
from collections import defaultdict
from pathlib import Path

import pandas as pd

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
OUT = Path('outputs/rebuild')
OUT.mkdir(parents=True, exist_ok=True)
DOUT = Path('Data/processed/rebuild')
DOUT.mkdir(parents=True, exist_ok=True)
L = []


def log(m=''):
    print(m)
    L.append(str(m))


def normalize(name):
    """Normalizer from the exact-and-abstain chain (apply_exact_matching ll.24-41),
    with two suffix-gap fixes found 8/4 (rewire bug-fix class, documented):
    CORP and INCORPORATED added — the original stripped CORPORATION but not its
    abbreviation or long form, so 'X Corporation' could never meet EDGAR's 'X CORP'."""
    if not isinstance(name, str):
        return ""
    n = name.upper().strip()
    n = re.sub(r'[^\w\s]', ' ', n)
    n = re.sub(r'\s+', ' ', n)
    for s in [r'\bINC\b', r'\bINCORPORATED\b', r'\bCORPORATION\b', r'\bCORP\b',
              r'\bLLC\b', r'\bLLP\b', r'\bLP\b',
              r'\bCO\b', r'\bCOMPANY\b', r'\bLTD\b', r'\bLIMITED\b', r'\bNA\b',
              r'\bNOT FOR PROFIT\b', r'\bTHE\b']:
        n = re.sub(s, '', n)
    return re.sub(r'\s+', ' ', n).strip()


log('=' * 90)
log('REBUILD STAGES 1-2: UNIVERSE + ENTITY RESOLUTION')
log('=' * 90)

# ---------------------------------------------------------------------------
# STAGE 1 — Universe
# ---------------------------------------------------------------------------
u = pd.read_excel('Data/processed/master_breach_dataset.xlsx')
assert len(u) == 1054, f'STAGE 1 HALT: universe is {len(u)} rows, expected 1,054'
log(f'\nStage 1: universe = {len(u)} records, {u["org_name"].nunique()} unique organizations. PASS')

# ---------------------------------------------------------------------------
# STAGE 2 — Entity resolution
# ---------------------------------------------------------------------------
log('\nStage 2: building EDGAR name index...')
sec_names = defaultdict(set)      # normalized name -> {cik}
cik_names = defaultdict(list)     # cik -> [official names]
with open('Data/edgar/cik-lookup-data.txt', encoding='utf-8', errors='replace') as f:
    for line in f:
        line = line.strip()
        if not line or ':' not in line:
            continue
        if line.endswith(':'):
            line = line[:-1]
        p = line.rfind(':')
        nm, cs = line[:p].strip(), line[p + 1:].strip()
        try:
            cik = int(cs)
        except ValueError:
            continue
        nn = normalize(nm)
        if nn:
            sec_names[nn].add(cik)
            cik_names[cik].append(nm)
log(f'  EDGAR index: {len(sec_names):,} normalized names, {len(cik_names):,} CIKs')

# SEC company_tickers.json as secondary evidence (current registrants)
with open('Data/edgar/company_tickers.json', encoding='utf-8') as f:
    ct = json.load(f)
ct_titles = defaultdict(list)     # cik -> [(title, ticker)]
for _, rec in (ct.items() if isinstance(ct, dict) else enumerate(ct)):
    ct_titles[int(rec['cik_str'])].append((rec['title'], rec.get('ticker', '')))

# Reasoning pass — CHARACTERIZED 8/4 (stop-and-report finding): 390 of 391
# MEDIUM entries are UNWORKED PLACEHOLDERS ('Requires individual research')
# echoing the legacy fuzzy CIK. Those are a worklist, NOT resolutions, and are
# EXCLUDED from the resolution chain here. Only substantive entries qualify.
rp_all = json.load(open('outputs/reasoning_pass_254_results.json'))
rp = {e['org_name']: e for e in rp_all
      if e.get('reasoning', '').strip() != 'Requires individual research'}
n_placeholder = len(rp_all) - len(rp)
log(f'  Reasoning pass: {len(rp_all)} entries; {n_placeholder} unworked placeholders '
    f'EXCLUDED from resolution (echo fuzzy CIKs); {len(rp)} substantive entries retained')

# Documented subsidiary/brand adjudications (each carries its rationale; Boost is
# a GATE 1 DECISION because ownership changed inside the sample window).
ADJUDICATED = {
    'cricket wireless': (732717, 'AT&T Inc. — Cricket Communications FRN 0004321139; LLC variant; 7/28 adjudication'),
    'at&t services': (732717, 'AT&T Inc. — same filing entity, services variant'),
    'sprint': (1283699, 'T-Mobile US, Inc. — successor-equity convention for Sprint entities (merger 4/2020); FLAGGED for Gate 1: pre-2020 events arguably belong to Sprint Corp equity'),
}
GATE1_DECISIONS = {
    'boost mobile': 'Single breach 2019-03-14 (Sprint era). Options: (a) successor-equity convention -> 1283699 (consistent with Sprint rows); (b) Sprint-era equity CIK; (c) exclude as brand without own listing. Legacy canonical carried 1283699.',
}

log('\n  Resolving organizations (exact-and-abstain -> reasoning -> adjudicated)...')
orgs = sorted(u['org_name'].dropna().unique())
rows = []
for org in orgs:
    nn = normalize(org)
    rec_count = int((u['org_name'] == org).sum())
    resolved, method, grade, evidence = None, None, None, ''

    if nn in sec_names:
        ciks = sec_names[nn]
        if len(ciks) == 1:
            resolved = list(ciks)[0]
            method = 'EXACT_UNAMBIGUOUS'
            grade = 'VERIFIED'
            evidence = f'EDGAR name: {cik_names[resolved][0]}'
        else:
            method = 'EXACT_AMBIGUOUS'
            grade = 'AMBIGUOUS'
            cands = []
            for c in sorted(ciks)[:6]:
                tick = ct_titles.get(c, [('', '')])[0][1]
                cands.append(f'{c} ({cik_names[c][0][:40]}{", " + tick if tick else ""})')
            legacy_map = u.loc[u['org_name'] == org, 'Map'].dropna().unique()
            lm = legacy_map[0] if len(legacy_map) else ''
            evidence = f'Candidates: {" | ".join(cands)} || legacy ticker: {lm}'
    if resolved is None and grade != 'AMBIGUOUS' and org in rp:
        e = rp[org]
        resolved = int(e['correct_cik'])
        method = f'REASONING_{e["confidence"]}'
        # independent confirmation: is org name among the CIK's EDGAR names, or
        # does the CIK's SEC title share the org's normalized identity?
        conf = nn in {normalize(x) for x in cik_names.get(resolved, [])}
        if not conf:
            titles = {normalize(t) for t, _ in ct_titles.get(resolved, [])}
            conf = nn in titles or any(nn and t and (nn in t or t in nn) for t in titles)
        if conf:
            grade = 'VERIFIED-REASONING'
            evidence = f'{e["source"]}: {e["reasoning"][:90]} | EDGAR-confirmed'
        else:
            grade = 'REVIEW'
            evidence = f'{e["source"]} ({e["confidence"]}): {e["reasoning"][:90]} | NOT independently confirmed'
    if resolved is None and grade is None:
        low = org.lower()
        hit = next((k for k in ADJUDICATED if k in low), None)
        dec = next((k for k in GATE1_DECISIONS if k in low), None)
        if dec:
            method, grade = 'GATE1_DECISION', 'REVIEW'
            evidence = GATE1_DECISIONS[dec]
        elif hit:
            resolved, why = ADJUDICATED[hit]
            method, grade = 'ADJUDICATED', 'ADJUDICATED'
            evidence = why
        else:
            method, grade = 'NO_MATCH', 'EXCLUDED-UNRESOLVED'
            evidence = 'No EDGAR exact match, no reasoning-pass entry (FISC precedent: exclude unless Gate 1 overturns)'

    legacy = u.loc[u['org_name'] == org, 'cik'].dropna().unique()
    legacy = int(legacy[0]) if len(legacy) else None
    delta = ('SAME' if legacy == resolved else
             ('NEWLY-EXCLUDED' if resolved is None and legacy is not None else
              ('NEWLY-RESOLVED' if legacy is None and resolved is not None else 'CORRECTED')))
    rows.append({'org_name': org, 'n_records': rec_count, 'normalized': nn,
                 'legacy_cik': legacy, 'resolved_cik': resolved, 'method': method,
                 'grade': grade, 'legacy_vs_resolved': delta, 'evidence': evidence})

ledger = pd.DataFrame(rows)
ledger.to_csv(OUT / 'GATE1_ENTITY_VERIFICATION_LEDGER.csv', index=False)

log('\n  Grade distribution (orgs / records):')
for g, gdf in ledger.groupby('grade'):
    log(f'    {g:<22} {len(gdf):>4} orgs   {gdf["n_records"].sum():>5} records')
log('\n  Legacy-vs-resolved (orgs):')
log('    ' + ledger['legacy_vs_resolved'].value_counts().to_string().replace('\n', '\n    '))

# Suspect-CIK report
SUSPECTS = [713676, 927628, 1324404, 19617, 1034054, 1932393, 1755336]
srows = []
for cik in SUSPECTS:
    legacy_orgs = u[u['cik'] == cik]['org_name'].unique()
    for org in legacy_orgs:
        r = ledger[ledger['org_name'] == org].iloc[0]
        srows.append({'suspect_cik': cik, 'org_name': org, 'n_records': r['n_records'],
                      'resolved_cik': r['resolved_cik'], 'grade': r['grade'],
                      'still_maps_to_suspect': r['resolved_cik'] == cik,
                      'evidence': r['evidence'][:100]})
sdf = pd.DataFrame(srows)
sdf.to_csv(OUT / 'GATE1_suspect_cik_report.csv', index=False)
log('\n  Suspect-CIK sinks (legacy records -> fate under fresh resolution):')
for cik in SUSPECTS:
    g = sdf[sdf['suspect_cik'] == cik]
    keep = g[g['still_maps_to_suspect']]
    log(f'    CIK {cik}: {len(g)} legacy orgs / {g["n_records"].sum()} records; '
        f'retained by fresh resolution: {len(keep)} orgs ({keep["n_records"].sum()} records)')

# Record-level entity-verified set
u2 = u.merge(ledger[['org_name', 'resolved_cik', 'grade', 'method', 'evidence']],
             on='org_name', how='left')
u2 = u2.rename(columns={'cik': 'legacy_cik'})
u2.to_csv(DOUT / 'stage2_entity_verified.csv', index=False)
assert len(u2) == 1054 and u2['grade'].notna().all(), 'STAGE 2 HALT: ungraded records'
log(f'\n  Record-level output: {len(u2)} records, all graded. '
    f'Retained for downstream (non-excluded): '
    f'{int((~u2["grade"].isin(["EXCLUDED-UNRESOLVED"])).sum())}')

# Gate 1 summary package
with open(OUT / 'GATE1_SUMMARY.md', 'w', encoding='utf-8') as f:
    f.write('# GATE 1 — Entity Verification Sign-off Package\n\n')
    f.write('\n'.join(L))
    f.write('\n\n## Items requiring your eyes (everything else is deterministic)\n\n')
    rv = ledger[ledger['grade'] == 'REVIEW']
    am = ledger[ledger['grade'] == 'AMBIGUOUS']
    f.write(f'### REVIEW ({len(rv)} orgs, {rv["n_records"].sum()} records)\n\n')
    for _, r in rv.iterrows():
        f.write(f"- **{r['org_name']}** ({r['n_records']} rec) -> {r['resolved_cik']} | {r['evidence']}\n")
    f.write(f'\n### AMBIGUOUS ({len(am)} orgs, {am["n_records"].sum()} records)\n\n')
    for _, r in am.iterrows():
        f.write(f"- **{r['org_name']}** ({r['n_records']} rec) | {r['evidence']}\n")
    f.write('\n### ADJUDICATED mappings for confirmation\n\n')
    for _, r in ledger[ledger['grade'] == 'ADJUDICATED'].iterrows():
        f.write(f"- **{r['org_name']}** -> {r['resolved_cik']} | {r['evidence']}\n")
    f.write('\n### GATE 1 DECISIONS (options presented, no default taken)\n\n')
    for _, r in ledger[ledger['method'] == 'GATE1_DECISION'].iterrows():
        f.write(f"- **{r['org_name']}**: {r['evidence']}\n")
    f.write('\n### Exclusion scan (top 40 EXCLUDED-UNRESOLVED by record count)\n\n')
    f.write('Scan for recognizable PUBLIC firms only — everything you do not flag '
            'is excluded per the FISC precedent (no valid public-market observation).\n\n')
    ex = ledger[ledger['grade'] == 'EXCLUDED-UNRESOLVED'].nlargest(40, 'n_records')
    otype = u.groupby('org_name')['organization_type'].first()
    for _, r in ex.iterrows():
        f.write(f"- {r['org_name']} ({r['n_records']} rec, type={otype.get(r['org_name'], '?')}, "
                f"legacy_cik={r['legacy_cik']})\n")

log('\nGATE 1 package written: outputs/rebuild/GATE1_SUMMARY.md, '
    'GATE1_ENTITY_VERIFICATION_LEDGER.csv, GATE1_suspect_cik_report.csv')
log('STOPPING at Gate 1 per directive.')
