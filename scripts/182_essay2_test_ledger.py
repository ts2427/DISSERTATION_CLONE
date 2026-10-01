"""
ESSAY 2: PROGRAM-WIDE TEST ENUMERATION (concatenated N_TESTS ledgers)
=====================================================================
Executes scripts 164, 169, 170, 174, 175, 176 unmodified via runpy and
captures each one's N_TESTS ledger at exit: one row per hypothesis test,
(script, family, test name). No test is added, altered, or re-counted by
new logic; this concatenates the ledgers the scripts already keep. The
scripts regenerate their own artifacts as a side effect (deterministic,
seeded).

Output: outputs/tables/essay2_v2/t53_test_ledger.csv
"""

import runpy
import sys
import tempfile
from contextlib import redirect_stdout
from pathlib import Path
import pandas as pd

SCRIPTS = ['scripts/164_essay2_rule_delay_classification.py',
           'scripts/169_essay2_spec_repairs.py',
           'scripts/170_essay2_scope_and_bounds.py',
           'scripts/174_q6_closeout.py',
           'scripts/175_essay2_announcement_contrast.py',
           'scripts/176_q7_composition_check.py']

out = Path('outputs/tables/essay2_v2/t53_test_ledger.csv')

# CARRIED, not executed (2026-10-01). scripts/170 reads
# Data/wrds/crsp_quotes_topup.csv, a CRSP-licensed quote extract that cannot be
# committed, so it is a declared reproducibility exception
# (docs/claude/REPRODUCE_ESSAY2.md). Executing it here made 182 fail on every clean
# clone - the exception was not self-contained. Its ledger rows are therefore carried
# from the committed t53_test_ledger.csv, which is the output of the run in which 170
# did execute, with its licensed input present.
#
# This is read BEFORE the file is rewritten, and the rows are inserted at 170's own
# position in SCRIPTS, so the output is unchanged.
CARRIED = {'170_essay2_scope_and_bounds.py': out}

_carried_rows = {}
for _name, _src in CARRIED.items():
    assert _src.exists(), f'{_name}: carried ledger missing at {_src}'
    _prev = pd.read_csv(_src)
    _sel = _prev[_prev['script'] == _name]
    assert len(_sel) > 0, f'{_name}: no rows for it in {_src}'
    _carried_rows[_name] = _sel[['script', 'family', 'test']].to_dict('records')

rows = []
for sp in SCRIPTS:
    name = Path(sp).name
    if name in _carried_rows:
        carried = _carried_rows[name]
        rows.extend(carried)
        print(f'  {name}: {len(carried)} tests (CARRIED from the committed ledger; '
              f'170 needs a CRSP-licensed input and is a declared exception)', flush=True)
        continue
    print(f'running {name} (ledger capture)...', flush=True)
    # a real file handle: the scripts call sys.stdout.reconfigure(),
    # which StringIO does not provide
    with tempfile.TemporaryFile(mode='w+', encoding='utf-8',
                                suffix='.log') as buf:
        with redirect_stdout(buf):
            g = runpy.run_path(sp, run_name='__main__')
    led = g.get('N_TESTS')
    assert led is not None and len(led) > 0, f'{name}: no N_TESTS ledger'
    for entry in led:
        if isinstance(entry, tuple):
            fam, nm = entry
        else:
            fam, nm = 'Q7-composition', str(entry)
        rows.append(dict(script=name, family=fam, test=nm))
    print(f'  {name}: {len(led)} tests', flush=True)

df = pd.DataFrame(rows)
df.to_csv(out, index=False)
print(f'\nSaved: {out} ({len(df)} rows)')
print(f'\nTOTAL TESTS: {len(df)}')
print('\nPER-FAMILY BREAKDOWN:')
print(df.groupby('family').size().sort_values(ascending=False)
      .to_string())
print('\nPER-SCRIPT:')
print(df.groupby('script').size().to_string())
