"""ESSAY 2 v5 — closed-essay guard (hash snapshot / verify).

Essays 1 and 3 are closed. Before the v5 Essay 2 rerun this script records a
SHA-256 for every file under outputs/, Data/, docs/ and scripts/ (tracked or
not), and afterwards asserts that none of them changed.

    python scripts/262_e2v5_guard.py snapshot
    python scripts/262_e2v5_guard.py verify

Rules enforced by `verify`:
  * no file in the snapshot may be modified or deleted (any essay);
  * new files are allowed only under the v5 paths (ALLOWED_NEW);
  * the Essay 1 / Essay 3 subset (E13 pattern) is reported separately and must
    be byte-identical — that is the closed-essay assertion.
The snapshot lives at outputs/essay2_v5/guard/snapshot.json.
"""
import hashlib
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
ROOTS = ['outputs', 'Data', 'docs', 'scripts']
# scripts/274 (inline Results tables) and its outputs are edited per set; excluded 2026-11-18 (Tim)
# so the snapshot is not re-taken per set. outputs/essay2_v5/ already covers outputs/essay2_v5/inline/.
SKIP = re.compile(r'^(outputs/essay2_v5/|outputs/essay2_v5/inline/|outputs/essay2_check/|'
                  r'scripts/274_e2v5_inline_tables\.py$)|/__pycache__/|\.pyc$')
ALLOWED_NEW = re.compile(r'^(outputs/essay2_v5/|outputs/essay2_check/|Data/wrds_e2v5/|outputs/defense_audit/|'
                         r'scripts/2(6[2-9]|7[0-9])_e2v5_[a-z0-9_]+\.py$|'
                         r'scripts/27[3-8]_[a-z0-9_]+\.py$)')
# Accepted changes to snapshot files (Tim, 2026-11-19; snapshot NOT re-taken):
#  * outputs/defense_audit/ (incl. graphics/, final/) and scripts 273-278 may change;
#  * scripts 210 and 217 may differ only by the one-line SCRIPT_HI edits of 3cce615 and the
#    defense-audit-final commit (210 allowlist bound 274 -> 275 -> 278; 217 test rows to match). Each is pinned to the SHA-256 of
#    that exact version, so any further edit to either file fails the guard.
#  * this guard file itself, whose accepted-change list is edited here (it cannot pin its own hash).
ACCEPTED_MOD = re.compile(r'^(outputs/defense_audit/|scripts/27[3-8]_[a-z0-9_]+\.py$|scripts/262_e2v5_guard\.py$)')
ACCEPTED_PIN = {
    # Tim, 2026-11-19 (approved): line 430 reworded (it called 64.2011 a seven-day rule); pinned to that version only.
    'scripts/260_essay1_chair_tables.py': 'f07d2ce0958ec6dee979b3141ce2d51f2536684dc6701f50f68de5dab7bdcef4',
    # Same rewording in the definition line only: 260 re-run (variable_definitions.csv line 6) and a
    # hand edit of the find-list (line 90). ESSAY1_CHAIR_TABLES.md kept at its committed version.
    'outputs/essay1_chair/variable_definitions.csv': 'c2198d4d5d5c857f9a7e539f2dcb2ba2cae709cb2901948027a5023608cb9fa2',
    'outputs/essay1_chair/ESSAY1_CHAIR_NOTES_AND_FINDLIST.md': 'd74f1c9e398392427a403ec304357d7bc0114b62f6713fa00c80ced5a052cf09',
    'scripts/210_verify_v3_frozen.py': '7d89c7b7a4114e7603348cc78ee5e89cac98cb4ff74f1db755c8e59321da60ce',
    'scripts/217_v4_offline_tests.py': 'e7c47a080fac65f5806c7fb173815df97222d22b5de290dc55d5638be51f8b1a',
}
# Essay 1 / Essay 3 outputs and constants (the closed essays)
E13 = re.compile(r'(essay1|essay3|ESSAY1|ESSAY3|e1_|e3_|constants_v3|CONSTANTS_BLOCK|'
                 r'constants_essay3|rebuild_v4|essay3_v4|defense_supplement|'
                 r'APPENDIX_V3|INTEXT_TABLES|essay1_chair)', re.I)
SNAP = Path('outputs/essay2_v5/guard/snapshot.json')


def digest(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def scan():
    out = {}
    for r in ROOTS:
        for p in Path(r).rglob('*'):
            if p.is_file():
                rel = p.as_posix()
                if not SKIP.search(rel):
                    out[rel] = digest(p)
    return out


def main(mode):
    if mode == 'snapshot':
        assert not SNAP.exists(), f'{SNAP} exists; refusing to overwrite a baseline'
        cur = scan()
        SNAP.parent.mkdir(parents=True, exist_ok=True)
        SNAP.write_text(json.dumps(cur, indent=0, sort_keys=True), encoding='utf-8')
        n13 = sum(1 for k in cur if E13.search(k))
        print(f'snapshot: {len(cur)} files hashed ({n13} Essay 1 / Essay 3 files) -> {SNAP}')
        return
    base = json.loads(SNAP.read_text(encoding='utf-8'))
    cur = scan()
    changed = sorted(k for k in base if k in cur and cur[k] != base[k])
    accepted = [k for k in changed if ACCEPTED_MOD.search(k) or ACCEPTED_PIN.get(k) == cur[k]]
    modified = [k for k in changed if k not in accepted]
    deleted = sorted(k for k in base if k not in cur)
    for k in accepted:
        print('  accepted change:', k)
    new = sorted(k for k in cur if k not in base)
    bad_new = [k for k in new if not ALLOWED_NEW.search(k)]
    e13 = [k for k in base if E13.search(k)]
    e13_bad = [k for k in modified + deleted if E13.search(k)]
    print(f'baseline files {len(base)}; Essay 1 / Essay 3 files {len(e13)}')
    print(f'modified {len(modified)}, deleted {len(deleted)}, new {len(new)} '
          f'(outside allowed v5 paths: {len(bad_new)})')
    for k in modified + deleted:
        print('  CHANGED:', k)
    for k in bad_new:
        print('  NEW OUTSIDE V5 PATHS:', k)
    for k in new:
        if k not in bad_new:
            print('  new (allowed):', k)
    assert not e13_bad, f'ESSAY 1/3 FILES CHANGED: {e13_bad}'
    assert not modified and not deleted, 'files changed outside the v5 paths'
    assert not bad_new, 'new files outside the v5 paths'
    print(f'PASS: all {len(e13)} Essay 1 / Essay 3 files byte-identical; '
          f'no other baseline file changed.')


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'verify')
