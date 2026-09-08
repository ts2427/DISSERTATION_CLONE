"""
ESSAY 2 CONSOLIDATED RUN-ALL (Query 5 Part G5)
===============================================
Regenerates every Essay 2 number from the canonical dataset in one
invocation, in dependency order, with each script's own reconciliation
assertions active (a failure anywhere aborts the chain). scripts/167
requires the cached WRDS quotes file (or an interactive WRDS login to
create it) and is skipped with a loud warning if neither is available.

    python scripts/172_essay2_run_all.py
"""

import subprocess
import sys
from pathlib import Path

CHAIN = [
    ('scripts/163_essay2_rerun_form499.py', 'ground truth: DV, ledger, nested models, quartiles, diagnostics'),
    ('scripts/164_essay2_rule_delay_classification.py', 'rule text, delay tests, classification audits, census'),
    ('scripts/165_essay2_inference_ladder.py', 'inference ladder, cluster diagnostics, wild bootstrap, design resolution'),
    ('scripts/166_essay2_spec_grid.py', 'measurement grid, gradient decomposition'),
    ('scripts/167_essay2_microstructure.py', 'microstructure channel (needs Data/wrds/crsp_quotes_topup.csv or WRDS login)'),
    ('scripts/169_essay2_spec_repairs.py', 'abnormal-vol DV, leakage tests, calendar clustering, balance'),
    ('scripts/170_essay2_scope_and_bounds.py', 'intent-scope restriction, equivalence bounds'),
    ('scripts/171_essay2_figures.py', 'exhibit figures'),
]

# ---- WRONG-COLUMN TRIPWIRE (volatility_change) ------------------------------
# volatility_change is the RETIRED breach-anchored annualized DV (script 155),
# disqualified on construct validity (163 Phase E). The canonical Essay 2 DV
# is e2_vol_change. The old draft was rewritten once because code silently
# regressed on the wrong column; this check fails loud if any Essay 2 script
# grows a new reference outside the labeled forensic/sensitivity blocks.
# Allowlist = per-file occurrence counts audited 2026-09-02:
#   163: Phase E DV-convention sensitivity + forensic provenance (6)
#   164: B2b misclassified-composition forensics on old data (was 12;
#        9 after the 9/4 MECHANISM VERDICT rewrite dropped three prose
#        references, replacing them with appendix Table 5 figures)
#   166: DV-variant correlation matrix + B1 four-panel decomposition (5)
#   174: one Q6 display line (1)
VOLCHANGE_ALLOW = {
    '163_essay2_rerun_form499.py': 6,
    '164_essay2_rule_delay_classification.py': 9,
    '166_essay2_spec_grid.py': 5,
    '174_q6_closeout.py': 1,
}


def volatility_change_tripwire():
    bad = []
    for f in sorted(Path('scripts').glob('*.py')):
        n = int(f.stem.split('_')[0]) if f.stem.split('_')[0].isdigit() else 0
        if not 163 <= n <= 177 or f.name == '172_essay2_run_all.py':
            continue
        hits = [i + 1 for i, ln in
                enumerate(f.read_text(encoding='utf-8',
                                      errors='replace').splitlines())
                if 'volatility_change' in ln and 'VOLCHANGE' not in ln]
        expect = VOLCHANGE_ALLOW.get(f.name, 0)
        if len(hits) != expect:
            bad.append(f'{f.name}: {len(hits)} occurrence(s) of the retired '
                       f'DV column at lines {hits} (allowlisted: {expect})')
    if bad:
        sys.exit('WRONG-COLUMN TRIPWIRE: volatility_change (retired breach-'
                 'anchored DV) referenced outside the audited forensic '
                 'blocks — use e2_vol_change, or update the allowlist with '
                 'a labeled justification:\n  ' + '\n  '.join(bad))
    print('volatility_change tripwire: all references match the audited '
          'forensic-block allowlist.')


volatility_change_tripwire()

for script, desc in CHAIN:
    if '167' in script and not Path('Data/wrds/crsp_quotes_topup.csv').exists():
        print(f'!! SKIPPING {script} — quotes cache absent and WRDS login is '
              f'interactive; run it manually once.')
        continue
    print(f'\n{"=" * 80}\nRUNNING {script} — {desc}\n{"=" * 80}')
    r = subprocess.run([sys.executable, script])
    if r.returncode != 0:
        sys.exit(f'ABORT: {script} failed (assertions are loud by design).')
volatility_change_tripwire()
print('\nESSAY 2 CHAIN COMPLETE — all reconciliation assertions passed.')
