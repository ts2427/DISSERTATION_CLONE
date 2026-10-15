"""
ESSAY 1 - VINTAGE DIFF FOR THE WORD DRAFT (October 2026)
========================================================
The Essay 1 Word draft quotes the pre-DISH-top-up vintage of the v3 outputs (commit
67e7c60, 2026-08-30: N = 338, 104 treated, 11 parent CIKs). The frozen numbers of record
are commit dd8b564 (2026-10-02, identical to tag defense-final 902a8ea for these files:
N = 340, 106 treated, 12 parent CIKs).

This script reads both versions straight from git (`git show <commit>:<path>`) and lists
every value that differs, so each find-and-replace in the draft has a committed old value,
a committed new value and a file. It computes nothing; it only compares committed files.

  constants_v3.json            every key (lists compared element-wise)
  appendix_v3/table_{1..16}    every cell, matched on the table's row label(s);
                               caption rows compared as text

Output: outputs/essay1_chair/vintage_diff_67e7c60_dd8b564.csv
        columns: file, key, column, old, new, changed
"""

import io
import json
import subprocess
import sys
from pathlib import Path

import pandas as pd

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
OLD, NEW = '67e7c60', 'dd8b564'
OUT = Path('outputs/essay1_chair')
OUT.mkdir(parents=True, exist_ok=True)


def show(commit, path):
    r = subprocess.run(['git', 'show', f'{commit}:{path}'], capture_output=True)
    if r.returncode != 0:
        sys.exit(f'git show {commit}:{path} failed: {r.stderr.decode(errors="replace")}')
    return r.stdout.decode('utf-8')


# the frozen tag must hold the same bytes as NEW for every file compared here
for p in ['outputs/rebuild/constants_v3.json'] + [f'outputs/rebuild/appendix_v3/table_{i}.csv' for i in range(1, 17)]:
    assert show(NEW, p) == show('defense-final', p), f'{p} differs between {NEW} and defense-final'

rows = []
cp = 'outputs/rebuild/constants_v3.json'
co, cn = json.loads(show(OLD, cp)), json.loads(show(NEW, cp))
for k in sorted(set(co) | set(cn)):
    o, n = co.get(k, '(absent)'), cn.get(k, '(absent)')
    rows.append({'file': cp, 'key': k, 'column': '', 'old': json.dumps(o) if isinstance(o, list) else o,
                 'new': json.dumps(n) if isinstance(n, list) else n, 'changed': o != n})

# row keys per table: the label columns that identify a row
KEYS = {3: ['Comparison', 'Group'], 6: ['Specification', 'Term'], 16: ['Panel', 'Window', 'Group']}
for i in range(1, 17):
    p = f'outputs/rebuild/appendix_v3/table_{i}.csv'
    to, tn = (pd.read_csv(io.StringIO(show(c, p)), dtype=str) for c in (OLD, NEW))
    kc = KEYS.get(i, [to.columns[0]])
    for t in (to, tn):
        t['_k'] = t[kc].fillna('').agg(' | '.join, axis=1)
        # table 14 carries "N=319 (...)" as a row label; key it by position so the N change is a diff
        t.loc[t['_k'].str.startswith('N='), '_k'] = 'N row'
    mo, mn = to.set_index('_k'), tn.set_index('_k')
    for k in list(dict.fromkeys(list(mo.index) + list(mn.index))):
        for c in [c for c in tn.columns if c not in kc + ['_k']] + (kc[:1] if k == 'N row' else []):
            o = mo.at[k, c] if k in mo.index else '(absent)'
            n = mn.at[k, c] if k in mn.index else '(absent)'
            o = '' if pd.isna(o) else o
            n = '' if pd.isna(n) else n
            if k.startswith('CAPTION') and o == n == '':
                continue
            rows.append({'file': p, 'key': k, 'column': c, 'old': o, 'new': n, 'changed': o != n})

D = pd.DataFrame(rows)
D.to_csv(OUT / f'vintage_diff_{OLD}_{NEW}.csv', index=False)
print(f'{len(D)} values compared; {int(D["changed"].sum())} differ')
print(D[D['changed']].groupby('file').size().to_string())
