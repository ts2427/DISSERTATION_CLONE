"""
ESSAY 3 QUERY 2 — PART A: CHAIN AND TREATMENT RECONCILIATION (NEW)
===================================================================
A1  chain / regression N / treated events / parent CIKs per essay, from committed files.
A2  DISH (CIK 1001082) status in every chain and every essay sample.
A3  Effect of the DISH top-up on the committed v3 constants: script 158 is re-run in a
    throwaway sandbox (temp directory; `Data` is a directory junction to the repo's
    Data, read-only use; 158 writes only under the sandbox's outputs/rebuild), so the
    committed constants_v3.json and appendix_v3 are NOT touched and NOT rebaselined.
    Every committed key is printed old vs new.
A4  Consumers of Data/enrichment/executive_changes*.csv and
    FINAL_DISSERTATION_DATASET_DEDUPLICATED_ENRICHED.csv, with run_all status.

Outputs: outputs/essay3_q2/a1_chain_table.csv, a3_constants_diff.csv,
         a4_consumers.csv, 186_chain.log
"""

import os
import re
import sys
import json
import subprocess
import tempfile
from pathlib import Path
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
ROOT = Path.cwd()
OUT = Path('outputs/essay3_q2')
OUT.mkdir(parents=True, exist_ok=True)
L = []


def log(m=''):
    print(m, flush=True)
    L.append(str(m))


def hdr(t):
    log('\n' + '=' * 90 + '\n' + t + '\n' + '=' * 90)


TREAT = 'fcc_form499'
CONTROLS = [TREAT, 'immediate_disclosure', 'prior_breaches_1yr', 'health_breach',
            'firm_size_log', 'leverage', 'roa']
ev = pd.read_csv('Data/processed/rebuild/CANONICAL_V3.csv', low_memory=False)
crsp = ev[ev['has_crsp_data'] == 1]
reg1 = crsp.dropna(subset=['car_30d'] + CONTROLS)
reg3 = crsp.dropna(subset=CONTROLS)
C = json.load(open('outputs/rebuild/constants_v3.json'))

# family map used ONLY for the labeled alternative count (Sprint folds into T-Mobile)
FAMILY = {101830: 1283699}


def counts(d):
    t = d[d[TREAT] == 1]
    return (len(d), len(t), t['final_cik'].nunique(),
            t['final_cik'].map(lambda c: FAMILY.get(c, c)).nunique(), t['org_name'].nunique())


hdr('A1 — CHAINS')
rows = [
    dict(essay='Essay 1 (7/28 appendix, outputs/ESSAY1_APPENDIX_TABLES_FORM499.md, untracked)',
         chain='7/28 audit (1,054->784->779->672->648)', regression_N=648, treated=115,
         parent_ciks=11, family_entities='n/a', org_name_strings=35,
         status='retired: generator scripts/141 commented out of run_all 2026-08-30'),
    dict(essay='Essay 1 (v3, constants_v3.json)', chain='v3 (1,054->758->524->489)',
         regression_N=C['N_regression'], treated=C['treated_regression'],
         parent_ciks=C['treated_parent_ciks_regression'], family_entities='',
         org_name_strings=C['treated_orgs_regression'], status='committed constants (8/17-8/30 vintage)'),
    dict(essay='Essay 2 (outputs/ESSAY2_SAMPLE_ATTRITION_LEDGER.md)', chain='v3', regression_N=333,
         treated=104, parent_ciks=12, family_entities='', org_name_strings=36,
         status='committed b11e884 (post DISH top-up)'),
    dict(essay='Essay 3 (v3, constants_v3.json)', chain='v3', regression_N=C['N_essay3'], treated=104,
         parent_ciks='(not stored)', family_entities='', org_name_strings='(not stored)',
         status='committed constants (pre-top-up)'),
]
for name, d in [('Essay 1 regression, today\'s CANONICAL_V3', reg1),
                ('Essay 3 regression, today\'s CANONICAL_V3', reg3)]:
    n, t, p, fam, o = counts(d)
    rows.append(dict(essay=name, chain='v3', regression_N=n, treated=t, parent_ciks=p,
                     family_entities=fam, org_name_strings=o, status='NEW recount (scripts/186)'))
A1 = pd.DataFrame(rows)
A1.to_csv(OUT / 'a1_chain_table.csv', index=False)
log(A1.to_string(index=False))

hdr('A2 — DISH (CIK 1001082)')
d = ev[ev['final_cik'] == 1001082][['org_name', 'breach_date', TREAT, 'has_crsp_data', 'firm_size_log']]
log('CANONICAL_V3 DISH events:\n' + d.to_string(index=False))
for name, dd in [('489 universe', ev), ('CRSP', crsp), ('Essay 1/3 regression today', reg3)]:
    x = dd[dd['final_cik'] == 1001082]
    log(f'  {name}: DISH events {len(x)}, treated {int(x[TREAT].sum())}')

hdr('A3 — CONSTANTS: committed vs 158 re-run on today\'s CANONICAL_V3 (sandbox)')
sb = Path(tempfile.mkdtemp(prefix='q2_158_'))
(sb / 'outputs' / 'rebuild' / 'appendix_v3').mkdir(parents=True)
subprocess.run(['cmd', '/c', 'mklink', '/J', str(sb / 'Data'), str(ROOT / 'Data')],
               check=True, capture_output=True)
r = subprocess.run([sys.executable, str(ROOT / 'scripts/158_rebuild_s8_regenerate.py')],
                   cwd=sb, capture_output=True, text=True, encoding='utf-8', errors='replace')
log(f'158 sandbox exit code {r.returncode}; sandbox {sb}')
new = json.load(open(sb / 'outputs/rebuild/constants_v3.json'))
os.rmdir(sb / 'Data')  # removes the junction only, never its target
diff = []
for k in C:
    o, n = C[k], new.get(k)
    ch = (o != n)
    delta = (round(n - o, 4) if isinstance(o, (int, float)) and isinstance(n, (int, float))
             and not isinstance(o, bool) else '')
    diff.append(dict(key=k, committed=o, today=n, changed=ch, delta=delta))
D = pd.DataFrame(diff)
D.to_csv(OUT / 'a3_constants_diff.csv', index=False)
log(f'{int(D["changed"].sum())} of {len(D)} committed keys change')
log(D[D['changed']].to_string(index=False))
Path(OUT / '186_158_sandbox_stdout.txt').write_text(r.stdout, encoding='utf-8')

hdr('A4 — CONSUMERS OF SCRIPT 46 / 53 OUTPUTS')
ra = Path('run_all.py').read_text(encoding='utf-8').splitlines()
active = {}
for i, line in enumerate(ra, 1):
    for m in re.finditer(r"scripts/[A-Za-z0-9_]+\.py", line):
        active[m.group(0)] = ('commented' if line.strip().startswith('#') else 'active', i)
cons = []
for p in sorted(Path('scripts').rglob('*.py')):
    t = p.read_text(encoding='utf-8', errors='replace')
    reads_ec = bool(re.search(r'executive_changes(_item5_02)?\.csv', t))
    reads_de = 'DEDUPLICATED_ENRICHED' in t
    uses_cols = bool(re.search(r'executive_change_\d+d|days_to_first_item_5_02', t))
    if reads_ec or reads_de:
        key = p.as_posix()
        st, ln = active.get(key, ('not in run_all', ''))
        cons.append(dict(script=key, reads_executive_changes_csv=reads_ec,
                         reads_DEDUPLICATED_ENRICHED=reads_de, uses_executive_change_columns=uses_cols,
                         run_all=st, run_all_line=ln))
A4 = pd.DataFrame(cons)
A4.to_csv(OUT / 'a4_consumers.csv', index=False)
log(f'{len(A4)} scripts read one of the two files; active in run_all: {int((A4.run_all == "active").sum())}')
log('executive_changes*.csv readers: ' + ', '.join(A4.loc[A4.reads_executive_changes_csv, 'script']))
v3 = A4[A4['script'].str.match(r'scripts/1[5-8]\d_')]
log(f'v3-chain scripts (150-189) among them: {len(v3)}')
(OUT / '186_chain.log').write_text('\n'.join(L) + '\n', encoding='utf-8')
