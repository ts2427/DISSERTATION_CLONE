"""ESSAY 2 v5 — inline Results tables (19-table layout).

Renders Essay 2's tables for the Results section in the Essay 1 inline (APA 7)
format. Rendering only: every cell is read from a committed CSV under
outputs/essay2_v5/ or from outputs/essay2_v5/constants_essay2.json; nothing is
estimated here and no number is typed by hand. A cell with no committed source
is printed as [NO SOURCE].

    python scripts/274_e2v5_inline_tables.py --set N
    python scripts/274_e2v5_inline_tables.py --layout     # print the old->new map

Writes outputs/essay2_v5/inline/set_N.md. Deterministic: a rerun on the same
committed inputs writes byte-identical output (UTF-8, LF line endings, sorted
inputs, no timestamps).

Numbered 274 because 273 is scripts/273_defaud_facts.py (Tim, 2026-11-18).
This script is the authoritative numbering for the essay's tables (1-19).
scripts/269 (the appendix generator, 33 tables) is left as it is; both read the
same committed CSVs. LAYOUT below is the old-to-new map: each new table lists
the old appendix tables it merges, and every panel CSV of each old table
(e.g. 22A, 22B, 22C) is carried over, so a merged table keeps every cell of its
sources, laid out as panels. Old Table 28 (pre-rule events) is dropped.

Each set's tables are registered in SETS by that set's prompt. The skeleton
registers none, so --set N exits with an error until set N is added.
"""
import argparse
import json
import math
import re
import sys
from pathlib import Path

import pandas as pd

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT = Path(__file__).resolve().parents[1]
V5 = ROOT / 'outputs' / 'essay2_v5'
APPENDIX = V5 / 'appendix'
CONSTANTS = V5 / 'constants_essay2.json'
OUT_DIR = V5 / 'inline'

MINUS = '\u2212'
NO_SOURCE = '[NO SOURCE]'
MAX_COLS = 7  # no panel wider than 7 columns

# ------------------------------------------------------------------ layout
# new table number -> old appendix table numbers (scripts/269 numbering).
LAYOUT = {
    1: [1, 4],
    2: [2, 3],
    3: [5, 9],
    4: [6, 7, 8],
    5: [10, 11],
    6: [12, 13],
    7: [14, 15],
    8: [16, 17],
    9: [18],
    10: [19],
    11: [20],
    12: [21, 22, 23],   # 22 = 22A, 22B, 22C
    13: [24],
    14: [25],
    15: [26],
    16: [27],
    17: [29],
    18: [30, 31, 32],
    19: [33],
}
DROPPED_OLD = [28]
N_OLD = 33

# set number -> list of new table numbers. Filled in by each set's prompt.
SETS = {}

# new table number -> renderer. Each renderer returns the markdown block
# (**Table N**, italic title, panels, *Note.*) for that table.
RENDERERS = {}


def check_layout():
    used = sorted(o for olds in LAYOUT.values() for o in olds)
    expected = sorted(set(range(1, N_OLD + 1)) - set(DROPPED_OLD))
    if used != expected:
        sys.exit(f'LAYOUT does not cover old tables 1-{N_OLD} exactly once '
                 f'(less {DROPPED_OLD}): {used}')
    if sorted(LAYOUT) != list(range(1, 20)):
        sys.exit('LAYOUT must number new tables 1-19')


_PANEL_RE = re.compile(r'^(\d{2})([A-Z]?)_(.+)\.csv$')


def old_table_files(old):
    """Committed panel CSVs of one old appendix table, in panel order (A, B, ...)."""
    out = []
    for p in sorted(APPENDIX.glob('*.csv')):
        m = _PANEL_RE.match(p.name)
        if m and int(m.group(1)) == old:
            out.append(p)
    if not out:
        sys.exit(f'old Table {old}: no committed CSV in {APPENDIX.relative_to(ROOT)}')
    return out


def source_files(new):
    """All committed panel CSVs feeding new table `new`, in old-table then panel order."""
    return [p for old in LAYOUT[new] for p in old_table_files(old)]


# ------------------------------------------------------------------ inputs
def read_csv(path):
    """Read a committed CSV as strings, so no value is re-typed or re-rounded on load."""
    return pd.read_csv(path, dtype=str, keep_default_na=False, encoding='utf-8')


def load_constants():
    with open(CONSTANTS, encoding='utf-8') as f:
        return json.load(f)


def const(c, dotted):
    """Look up 'a.b.c' in the constants; [NO SOURCE] if absent."""
    cur = c
    for k in dotted.split('.'):
        if not isinstance(cur, dict) or k not in cur:
            return NO_SOURCE
        cur = cur[k]
    return cur


# ------------------------------------------------------------------ formatting
def _num(x):
    if x is None:
        return None
    if isinstance(x, (int, float)):
        return None if (isinstance(x, float) and math.isnan(x)) else float(x)
    s = str(x).strip().replace(MINUS, '-')
    if s == '' or s.lower() in ('nan', 'none', 'na'):
        return None
    try:
        return float(s)
    except ValueError:
        return None


def minus(s):
    """Replace a leading hyphen-minus with a true minus sign."""
    s = str(s)
    return MINUS + s[1:] if s.startswith('-') else s


def fmt_num(x, dp=2, signed=False):
    """Fixed decimals, true minus, optional explicit plus. Missing -> [NO SOURCE]."""
    v = _num(x)
    if v is None:
        return NO_SOURCE
    s = f'{v:+.{dp}f}' if signed else f'{v:.{dp}f}'
    if float(s) == 0:          # no "-0.00"
        s = s.replace('-', '').replace('+', '') if not signed else '+' + s.lstrip('+-')
    return minus(s)


def fmt_int(x):
    v = _num(x)
    if v is None:
        return NO_SOURCE
    if v != int(v):
        sys.exit(f'expected a count, got {x!r}')
    return minus(f'{int(v):,}')


def fmt_p(x, dp=3):
    """APA p-value: no leading zero; below .001 -> '< .001'."""
    v = _num(x)
    if v is None:
        return NO_SOURCE
    if not 0 <= v <= 1:
        sys.exit(f'p-value out of range: {x!r}')
    if v < 0.001:
        return '< .001'
    s = f'{v:.{dp}f}'
    return s[1:] if s.startswith('0') else s


def fmt_ci(lo, hi, dp=3):
    a, b = fmt_num(lo, dp), fmt_num(hi, dp)
    if NO_SOURCE in (a, b):
        return NO_SOURCE
    return f'[{a}, {b}]'


# ------------------------------------------------------------------ markdown
def _cell(s):
    if '*' in str(s):
        sys.exit(f'asterisk in cell {s!r} (no significance stars)')
    return str(s).replace('|', '\\|').replace('\n', ' ')


def md_table(header, rows):
    if len(header) > MAX_COLS:
        sys.exit(f'panel has {len(header)} columns (max {MAX_COLS}); split it')
    for r in rows:
        if len(r) != len(header):
            sys.exit(f'row width {len(r)} != header width {len(header)}: {r}')
    lines = ['| ' + ' | '.join(_cell(h) for h in header) + ' |',
             '|' + '|'.join([':---'] + ['---:'] * (len(header) - 1)) + '|']
    lines += ['| ' + ' | '.join(_cell(c) for c in r) + ' |' for r in rows]
    return '\n'.join(lines)


def panel_letter(i):
    return chr(ord('A') + i)


def render_table(new, title, panels, note):
    """panels: list of (panel title, header, rows). One panel -> no panel label."""
    out = [f'**Table {new}**', '', f'*{title}*', '']
    for i, (ptitle, header, rows) in enumerate(panels):
        if len(panels) > 1:
            out += [f'Panel {panel_letter(i)}: {ptitle}', '']
        out += [md_table(header, rows), '']
    out.append(f'*Note.* {note}')
    return '\n'.join(out) + '\n'


# ------------------------------------------------------------------ main
def write_set(n):
    if n not in SETS:
        sys.exit(f'set {n} has no tables registered yet (SETS is filled in by each set\'s prompt)')
    blocks = []
    for new in SETS[n]:
        if new not in RENDERERS:
            sys.exit(f'Table {new} (set {n}) has no renderer')
        blocks.append(RENDERERS[new]())
    text = '\n'.join(blocks)
    no_src = text.count(NO_SOURCE)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / f'set_{n}.md'
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)
    print(f'wrote {path.relative_to(ROOT)} (tables {SETS[n]}; {no_src} [NO SOURCE] cells)')


def print_layout():
    for new, olds in LAYOUT.items():
        files = ', '.join(p.name for p in source_files(new))
        print(f'Table {new:>2}: old {" + ".join(map(str, olds)):<12} <- {files}')
    print(f'dropped: old {DROPPED_OLD}')


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--set', type=int, dest='set_n')
    g.add_argument('--layout', action='store_true')
    a = ap.parse_args()
    check_layout()
    if a.layout:
        print_layout()
    else:
        write_set(a.set_n)


if __name__ == '__main__':
    main()
