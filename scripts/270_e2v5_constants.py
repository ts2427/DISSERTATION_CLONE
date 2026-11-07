"""ESSAY 2 v5 — constants of record (committee item 11).

Merges outputs/essay2_v5/constants_parts/*.json (written by scripts/264,
265, 266, 268, 269, 271, 272) into outputs/essay2_v5/constants_essay2.json, keyed by
name, with provenance (the script that emitted each key). Requires every
part; `--allow-pending` tolerates a missing 268 (spreads, WRDS) and records
it as pending. BH families and test counts are merged across parts; the
program-wide test count is the one scripts/269's enumeration emits.
"""
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
P = Path('outputs/essay2_v5/constants_parts')
OUTF = Path('outputs/essay2_v5/constants_essay2.json')
REQUIRED = ['264', '265', '266', '268', '269', '271', '272']
allow = '--allow-pending' in sys.argv
parts = {f.stem: json.loads(f.read_text(encoding='utf-8')) for f in sorted(P.glob('*.json'))}
missing = [r for r in REQUIRED if r not in parts]
assert not missing or (allow and missing == ['268']), f'missing constants parts: {missing}'

values, source, families, tests = {}, {}, {}, {}
for name, d in parts.items():
    for k, v in d.items():
        if k == 'bh_families':
            families.update(v)
            continue
        if k == 'tests':
            tests.update({f'{t} [{name}]': n for t, n in v.items()})
            continue
        assert k not in values or values[k] == v, f'key {k} differs between parts ({source.get(k)} vs {name})'
        values[k], source[k] = v, f'scripts/{name}'
doc = dict(
    sample='v3 analytical sample: 333 events / 104 treated / 82 parents / 12 treated parents (frozen)',
    primary_outcome='SD of market-adjusted daily abnormal returns (r - vwretd), [+1,+20] minus [-60,-11] '
                    'trading days around the v3 agency reporting date; daily percentage points',
    inference='CV3 cluster jackknife on parent filer entity (primary); OLS/HC1/HC3/CV1/WCR/WCU/Webb reported',
    pending=['spreads (scripts/267 WRDS pull + scripts/268)'] if '268' in missing else [],
    bh_families=families,
    tests_by_family=tests,
    values=dict(sorted(values.items())),
    source=dict(sorted(source.items())),
)
OUTF.write_text(json.dumps(doc, indent=1, default=float), encoding='utf-8')
print(f'{len(values)} constants from {len(parts)} parts -> {OUTF}')
print('BH families:', families)
print('program tests:', values.get('program_tests_total'), '| pending:', doc['pending'])
