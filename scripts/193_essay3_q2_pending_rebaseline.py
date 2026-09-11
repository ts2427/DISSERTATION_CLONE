"""
ESSAY 3 QUERY 2 — PENDING REBASELINE LEDGER (NEW; print only, rebaselines nothing)
==================================================================================
Reads outputs/essay3_q2/a3_constants_diff.csv (scripts/186: committed constants_v3.json vs a
sandbox re-run of script 158 on today's CANONICAL_V3) and writes outputs/PENDING_REBASELINE.md:
the vintage gap, Essay 1 H1-H4 and ROA old vs new with verdict-change flags, and every changed
constant. Does NOT modify constants_v3.json and does NOT run run_all or script 158.
"""

import sys
import ast
from pathlib import Path
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
D = pd.read_csv('outputs/essay3_q2/a3_constants_diff.csv')
D['changed'] = D['changed'].astype(str).eq('True')
V = {r['key']: (r['committed'], r['today']) for _, r in D.iterrows()}


def num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def band(p):
    return 'p<.05' if p < .05 else ('p<.10' if p < .10 else 'p>=.10')


rows = []
for lab, name in [('H1_timing', 'H1 timing (immediate disclosure)'), ('H2_FCC', 'H2 Form 499 treatment'),
                  ('H3_prior', 'H3 prior breaches'), ('H4_health', 'H4 health breach')]:
    co, cn = num(V[f'{lab}_coef'][0]), num(V[f'{lab}_coef'][1])
    po, pn = num(V[f'{lab}_p'][0]), num(V[f'{lab}_p'][1])
    so, sn = V[f'{lab}_status']
    to, tn = num(V[f'{lab}_tost_p'][0]), num(V[f'{lab}_tost_p'][1])
    flags = []
    if so != sn:
        flags.append(f'STATUS {so} -> {sn}')
    if band(po) != band(pn):
        flags.append(f'p band {band(po)} -> {band(pn)}')
    if (co > 0) != (cn > 0):
        flags.append('SIGN FLIP')
    if (to < .05) != (tn < .05):
        flags.append(f'TOST(±2.10) crosses .05 ({to} -> {tn})')
    rows.append((name, co, cn, po, pn, so, sn, to, tn, '; '.join(flags) or 'no verdict change'))
co, cn = num(V['ROA_coef'][0]), num(V['ROA_coef'][1])
po, pn = num(V['ROA_p'][0]), num(V['ROA_p'][1])
rf = []
if band(po) != band(pn):
    rf.append(f'p band {band(po)} -> {band(pn)}')
if (co > 0) != (cn > 0):
    rf.append('SIGN FLIP')
rows.append(('ROA (control)', co, cn, po, pn, '—', '—', None, None,
             '; '.join(rf) or f'no verdict change (not significant at .05 or .10 in either vintage: {po} -> {pn})'))

chg = D[D['changed']]
L = []
L.append('# PENDING REBASELINE — constants_v3.json vs today\'s CANONICAL_V3 (NOT APPLIED)\n')
L.append('Generated 2026-09-11 by scripts/193_essay3_q2_pending_rebaseline.py from '
         'outputs/essay3_q2/a3_constants_diff.csv (scripts/186: script 158 re-run in a throwaway sandbox). '
         '**Nothing here has been applied. constants_v3.json is unmodified. Do not run run_all or script 158 '
         'until the rebaseline is decided: 158 asserts against constants_v3.json and will fail on today\'s file.**\n')
L.append('## Vintage gap (logged 2026-09-11)\n')
L.append('- **Essay 3** (Query 2 Stage 2, pending): runs on **today\'s CANONICAL_V3** — Essay 3 regression '
         'sample 340 (106 treated events, 12 treated parent CIKs), DISH (CIK 1001082) treated from 2020-07-01 '
         '(scripts/154:129, 9/4 adjudication; CRSP top-up scripts/179). Results go to a separate Essay 3 '
         'constants file, not constants_v3.json.')
L.append('- **Essay 1 and the v3 Essay 2/3 blocks in constants_v3.json**: the **pre-top-up** file — Essay 1 '
         'regression 338 (104 treated, 11 treated parent CIKs), N_essay2 337, N_essay3 338; DISH\'s two 2023 '
         'events absent (no CRSP data at that vintage).')
L.append('- **Essay 2 authoritative artifacts** (scripts/163 chain, outputs/ESSAY2_SAMPLE_ATTRITION_LEDGER.md, '
         'commit b11e884) are already on the topped-up file (333; 104 treated, 12 parent CIKs) and are not '
         'affected by this ledger.')
L.append(f'- Scope of the gap: **{len(chg)} of {len(D)}** committed constants change; the treated counts '
         'move by exactly DISH\'s two events at every level.\n')
L.append('## Essay 1 H1–H4 and ROA: committed vs today (verdict-change flags)\n')
L.append('| Test | Coef committed | Coef today | p committed | p today | Status committed | Status today | '
         'TOST p committed | TOST p today | Flag |')
L.append('|---|---|---|---|---|---|---|---|---|---|')
for r in rows:
    L.append('| ' + ' | '.join('' if v is None else str(v) for v in r) + ' |')
L.append('')
L.append('Verdict-change rule: a flag is raised if the status label changes, the p-value crosses .05 or .10, the '
         'coefficient changes sign, or the TOST (±2.10pp) p-value crosses .05.\n')
L.append('## Also flagged: script 158\'s Essay 2 volatility block\n')
h5 = {k: V[k] for k in ['N_essay2', 'H5_coef', 'H5_p', 'H5_status']}
L.append(f'- H5 (158\'s breach-anchored annualized volatility spec): N {h5["N_essay2"][0]} -> {h5["N_essay2"][1]}, '
         f'coef {h5["H5_coef"][0]} -> {h5["H5_coef"][1]}, p {h5["H5_p"][0]} -> {h5["H5_p"][1]}, status '
         f'**{h5["H5_status"][0]} -> {h5["H5_status"][1]}**. Essay 2\'s authoritative chain disqualifies this '
         'specification on construct validity (outputs/ESSAY2_APPENDIX_TABLES_FORM499.md:16-21). Retire or relabel '
         'this block before script 158 runs again.\n')
L.append(f'## All {len(chg)} changed constants\n')
L.append('| Key | Committed | Today | Delta |')
L.append('|---|---|---|---|')
for _, r in chg.iterrows():
    L.append(f"| {r['key']} | {r['committed']} | {r['today']} | {'' if pd.isna(r['delta']) else r['delta']} |")
L.append('')
L.append(f'Unchanged keys ({len(D) - len(chg)}): ' + ', '.join(D.loc[~D['changed'], 'key']) + '.')
Path('outputs/PENDING_REBASELINE.md').write_text('\n'.join(L) + '\n', encoding='utf-8')
for r in rows:
    print(r[0], '|', r[-1])
print(f'Written outputs/PENDING_REBASELINE.md ({len(chg)} changed constants)')
