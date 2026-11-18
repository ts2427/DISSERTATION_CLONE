"""ESSAY 2 v5 — inline Results tables (19-table layout).

Renders Essay 2's tables for the Results section in the Essay 1 inline (APA 7)
format. Rendering only: every cell is read from a committed CSV under
outputs/essay2_v5/ or from outputs/essay2_v5/constants_essay2.json; nothing is
estimated here and no number is typed by hand. A cell with no committed source
is printed as [NO SOURCE].

    python scripts/274_e2v5_inline_tables.py --set N
    python scripts/274_e2v5_inline_tables.py --layout     # print the old->new map
    python scripts/274_e2v5_inline_tables.py --constants  # constants_parts/274.json (merge: scripts/270)

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
MAX_COLS = 7  # no panel wider than 7 columns (correlation matrices excepted)
CORRELATION = 'correlation'

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
SETS = {
    1: [1, 2],
}

# new table number -> renderer. Each renderer returns the markdown block
# (**Table N**, italic title, panels, *Note.*) for that table. Registered
# below the renderers' definitions.
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


def md_table(header, rows, wide_ok=False):
    """wide_ok: the correlation-matrix exception to the 7-column limit (rules, 2026-11-18)."""
    if len(header) > MAX_COLS and not wide_ok:
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
    """panels: list of (panel title, header, rows[, CORRELATION]). One panel -> no panel label.

    A fourth element CORRELATION marks a correlation matrix, the one panel type allowed
    past the 7-column limit.
    """
    out = [f'**Table {new}**', '', f'*{title}*', '']
    for i, (ptitle, header, rows, *kind) in enumerate(panels):
        if len(panels) > 1:
            out += [f'Panel {panel_letter(i)}: {ptitle}', '']
        out += [md_table(header, rows, wide_ok=kind == [CORRELATION]), '']
    out.append(f'*Note.* {note}')
    return '\n'.join(out) + '\n'


# ------------------------------------------------------------------ shared labels
GROUP_TREATED = 'Form 499 registrant'
GROUP_CONTROL = 'Other firm'
DV_WORDS = ('abnormal return volatility = SD of daily (RET − vwretd) in percentage points; '
            'change = post-window [+1, +20] minus pre-window [−60, −11], in trading days '
            'around the agency reporting date')

VAR_LABELS = {
    'dv': 'Change in abnormal return volatility',
    'pre_sd': 'Pre-window abnormal return volatility, [−60, −11]',
    'post_sd': 'Post-window abnormal return volatility, [+1, +20]',
    'fcc_form499': 'Form 499 registrant',
    'delay_w': 'Disclosure gap (days)',
    'firm_size_log': 'Log total assets',
    'leverage': 'Leverage',
    'roa': 'Return on assets',
    'health_breach': 'Health-breach flag',
    'prior_events': 'Prior breach events',
}

PANEL_CSV = V5 / 'v5_event_panel.csv'


def appendix_csv(name):
    p = APPENDIX / name
    if not p.exists():
        sys.exit(f'missing committed source {p.relative_to(ROOT)}')
    return read_csv(p)


def blank_dash(x, fmt):
    """Ledger cells the source leaves empty are not tracked at that level: an em dash."""
    return '—' if str(x).strip() == '' else fmt(x)


def sample_counts():
    """Final-sample counts by level, from the committed event panel and attrition ledger.

    Events and treated organizations / parents come from the ledger's final row;
    organization and parent totals and the other-firm counts are distinct counts
    in v5_event_panel.csv (org_name, final_cik), cross-checked against the ledger.
    """
    att = appendix_csv('01_sample_attrition.csv')
    fin = att.iloc[-1]
    ev = pd.read_csv(PANEL_CSV, dtype={'final_cik': str, 'org_name': str})
    t, c = ev[ev.fcc_form499 == 1], ev[ev.fcc_form499 == 0]
    out = {
        'events': (len(ev), len(t), len(c)),
        'orgs': (ev.org_name.nunique(), t.org_name.nunique(), c.org_name.nunique()),
        'parents': (ev.final_cik.nunique(), t.final_cik.nunique(), c.final_cik.nunique()),
        'both_parents': sorted(set(t.final_cik) & set(c.final_cik)),
        # each mixed parent named by its shortest registrant organization name
        'both_parent_names': sorted(min(t[t.final_cik == k].org_name, key=lambda x: (len(x), x))
                                    for k in set(t.final_cik) & set(c.final_cik)),
        'both_orgs': sorted(set(t.org_name) & set(c.org_name)),
        'date_min': ev.reported_date.min()[:10], 'date_max': ev.reported_date.max()[:10],
    }
    ledger = (int(float(fin.N)), int(float(fin.treated)), int(float(fin.control)))
    if out['events'] != ledger:
        sys.exit(f'event panel {out["events"]} != attrition ledger {ledger}')
    if out['orgs'][1] != int(float(fin.t_orgs)) or out['parents'][1] != int(float(fin.t_parents)):
        sys.exit('treated organizations / parents disagree between event panel and ledger')
    g = const(load_constants(), 'values.ann_G')
    if out['parents'][0] != g:
        sys.exit(f'parent filer entities {out["parents"][0]} != constants values.ann_G {g}')
    if out['both_orgs']:
        sys.exit(f'organizations in both groups: {out["both_orgs"]}')
    return out


# ------------------------------------------------------------------ Table 1
ATTRITION_LABELS = {
    'PRC universe': 'Records: Privacy Rights Clearinghouse notification records (start)',
    'Entity resolution + Gate 1': 'Records: not resolved to a public filer entity (entity resolution, Gate 1)',
    'CIK+date deduplication': 'Records: duplicate records for the same filer and date removed',
    'Gate 2 adjacency verdicts': 'Records: removed at the Gate 2 adjacency review',
    'Canonical events (post-Gate 2)': 'Events: canonical events after Gate 2',
    'CRSP security matched': 'Events: no matched CRSP security',
    'Public notification date present': 'Events: no public notification date',
    'Notification on/before 2024-12-31': 'Events: notified after December 31, 2024',
    'Volatility windows computable': 'Events: volatility windows not computable',
    'Compustat covariates complete': 'Events: Compustat controls incomplete',
    'Disclosure delay valid': 'Events: disclosure gap not valid',
    'Malformed-record exclusion (FINAL)': 'Events: malformed records excluded (final sample)',
}


def table_1():
    att = appendix_csv('01_sample_attrition.csv')
    rows_a = []
    for _, r in att.iterrows():
        if r.step not in ATTRITION_LABELS:
            sys.exit(f'Table 1: no plain-language label for attrition step {r.step!r}')
        rows_a.append([ATTRITION_LABELS[r.step], blank_dash(r.removed, fmt_int), fmt_int(r.N),
                       blank_dash(r.treated, fmt_int), blank_dash(r.t_orgs, fmt_int),
                       blank_dash(r.t_parents, fmt_int), blank_dash(r.control, fmt_int)])
    hdr_a = ['Step', 'Removed', 'Remaining', 'Registrant events', 'Registrant organizations',
             'Registrant parent filer entities', 'Other events']

    s = sample_counts()
    rows_b = [['Events'] + [fmt_int(x) for x in s['events']],
              ['Organizations'] + [fmt_int(x) for x in s['orgs']],
              ['Parent filer entities'] + [fmt_int(x) for x in s['parents']]]
    hdr_b = ['Level', 'Total', GROUP_TREATED, GROUP_CONTROL]

    yr = appendix_csv('04_events_by_year.csv')
    rows_c, one_group = [], []
    for _, r in yr.iterrows():
        t, c = int(r.treated), int(r.control)
        if int(r.total) != t + c:
            sys.exit(f'Table 1 Panel C: {r.year} total != registrant + other')
        flag = 'Registrants only' if c == 0 else ('Other firms only' if t == 0 else '')
        if flag:
            one_group.append(r.year)
        rows_c.append([r.year, fmt_int(r.total), fmt_int(r.treated), fmt_int(r.control), flag])
    tot = [sum(int(x) for x in yr[k]) for k in ('total', 'treated', 'control')]
    if tot[0] != s['events'][0]:
        sys.exit(f'Table 1 Panel C: years sum to {tot[0]}, not {s["events"][0]}')
    rows_c.append(['Total'] + [fmt_int(x) for x in tot] + [''])
    hdr_c = ['Year', 'Total', 'Registrant events', 'Other events', 'One group only']

    n, nt, nc = s['events']
    g, gt, gc = s['parents']
    note = (f'The starting units are Privacy Rights Clearinghouse (PRC) notification records, '
            f'not breaches; a breach can generate several records, and the record-level steps '
            f'reduce records to events. Final sample: {fmt_int(n)} events ({fmt_int(nt)} '
            f'{GROUP_TREATED} events, {fmt_int(nc)} other), {fmt_int(s["orgs"][0])} '
            f'organizations, and {fmt_int(g)} parent filer entities (G = {fmt_int(g)}; '
            f'{fmt_int(gt)} with registrant events). Of these, {len(s["both_parents"])} '
            f'parent filer entities ({" and ".join(s["both_parent_names"])}) have both registrant and other '
            f'events, so the registrant and other parent counts in Panel B sum to '
            f'{fmt_int(gt + gc)}, not {fmt_int(g)}. Reporting dates run from '
            f'{s["date_min"]} to {s["date_max"]}. An em dash (—) marks a count the ledger '
            f'does not track at that step. In Panel C, "one group only" marks years whose events '
            f'are all registrant or all other events. Form 499 registrant = event at a firm '
            f'registered with the Federal Communications Commission on FCC Form 499. '
            f'Gate 1 = entity-resolution screen; Gate 2 = adjacency review of near-duplicate '
            f'events. CRSP = Center for Research in Security Prices.')
    return render_table(1, 'Sample Construction',
                        [('Attrition from notification records to analytical events', hdr_a, rows_a),
                         ('Final sample by level', hdr_b, rows_b),
                         ('Events by reporting year', hdr_c, rows_c)], note)


# ------------------------------------------------------------------ Table 2
DV_VARS = ['dv', 'pre_sd', 'post_sd']
CONTROL_VARS = ['firm_size_log', 'leverage', 'roa', 'health_breach', 'prior_events', 'delay_w']
CORR_ORDER = ['dv', 'fcc_form499', 'pre_sd', 'delay_w', 'firm_size_log', 'leverage', 'roa',
              'health_breach', 'prior_events']


def table_2():
    d = appendix_csv('02A_descriptives_v5.csv')
    diff = appendix_csv('02B_descriptives_v5_differences.csv').set_index('variable')
    cell = {(r.group, r.variable): r for _, r in d.iterrows()}

    def ms(g, v):
        r = cell[(g, v)]
        return f'{fmt_num(r["mean"], 2)} ({fmt_num(r.sd, 2)})'

    def group_rows(vars_):
        rows = []
        for v in vars_:
            x = diff.loc[v]
            rows.append([VAR_LABELS[v], ms('treated', v), ms('control', v),
                         f'{fmt_num(x["diff"], 2)} ({fmt_num(x.se, 2)})',
                         f'{fmt_num(x.t, 2)} ({fmt_num(x.welch_df, 2)})', fmt_p(x.p)])
        return rows

    n = {g: fmt_int(cell[(g, 'dv')].N) for g in ('full', 'treated', 'control')}
    for g in n:
        if {fmt_int(cell[(g, v)].N) for v in DV_VARS + CONTROL_VARS} != {n[g]}:
            sys.exit(f'Table 2: N varies across variables in group {g}')
    hdr_ab = ['Variable', f'{GROUP_TREATED} M (SD)', f'{GROUP_CONTROL} M (SD)',
              'Difference (SE)', 'Welch t (df)', 'p']

    cor = appendix_csv('03_correlations_v5.csv').set_index('variable')
    if list(cor.index) != CORR_ORDER or list(cor.columns) != CORR_ORDER:
        sys.exit('Table 2: correlation matrix order changed')
    hdr_c = ['Variable'] + [f'({j + 1})' for j in range(len(CORR_ORDER))]
    rows_c = [[f'({i + 1}) {VAR_LABELS[v]}'] +
              [fmt_num(cor.loc[v, CORR_ORDER[j]], 2) if j <= i else '' for j in range(len(CORR_ORDER))]
              for i, v in enumerate(CORR_ORDER)]

    note = (f'Sample: {n["full"]} events ({n["treated"]} {GROUP_TREATED} events, '
            f'{n["control"]} other-firm events). Dependent variable: {DV_WORDS}; the pre- and '
            f'post-window rows give the two levels. Difference = {GROUP_TREATED} mean '
            f'minus other-firm mean; Welch t and p are from the unequal-variance two-sample '
            f't test, with Welch–Satterthwaite df. Correlations are Pearson, lower triangle, '
            f'over all {n["full"]} events; column numbers refer to the numbered rows. Percentiles, '
            f'minima and maxima are in the committed appendix CSV. Log total assets = natural log of Compustat total '
            f'assets; leverage = total liabilities / total assets; return on assets = net income '
            f'/ total assets; health-breach flag = 1 when the record lists medical or health '
            f'information as affected or the organization is a medical organization; prior '
            f'breach events = earlier sample events at the same parent filer entity; disclosure '
            f'gap = days from the breach date to the reporting date (negative gaps set to 0), '
            f'top-coded at the 99th percentile. M = mean; SD = standard '
            f'deviation; SE = standard error; df = degrees of freedom; Form 499 registrant = '
            f'event at a firm registered with the Federal Communications Commission on FCC '
            f'Form 499.')
    return render_table(2, 'Descriptive Statistics by Registration',
                        [('Dependent variable', hdr_ab, group_rows(DV_VARS)),
                         ('Controls', hdr_ab, group_rows(CONTROL_VARS)),
                         ('Correlations of model variables', hdr_c, rows_c, CORRELATION)], note)


RENDERERS.update({1: table_1, 2: table_2})


# ------------------------------------------------------------------ constants
T1 = ROOT / 'outputs' / 'tables' / 'essay2_v2' / 't1_final_sample.csv'
PART = V5 / 'constants_parts' / '274.json'


def emit_constants():
    """Counts the prose cites that had no direct committed source; writes constants_parts/274.json.

    Health-breach counts by group come from the committed analytical sample (t1, the file
    scripts/269 reads for the 02A descriptives) and are cross-checked against 02A mean x N.
    Merge into constants_essay2.json with scripts/270.
    """
    fin = pd.read_csv(T1, low_memory=False)
    if len(fin) != 333:
        sys.exit(f't1 has {len(fin)} rows, not 333')
    d = appendix_csv('02A_descriptives_v5.csv')
    out = {}
    for grp, m in [('full', fin.fcc_form499 >= 0), ('treated', fin.fcc_form499 == 1),
                   ('control', fin.fcc_form499 == 0)]:
        h = fin.loc[m, 'health_breach'].astype(float)
        if h.isna().any() or not h.isin([0, 1]).all():
            sys.exit(f'health_breach not 0/1 in group {grp}')
        k = int(h.sum())
        r = d[(d.group == grp) & (d.variable == 'health_breach')].iloc[0]
        if abs(float(r['mean']) * int(r.N) - k) > 1e-9 or int(r.N) != len(h):
            sys.exit(f'health-breach count {k} disagrees with 02A for group {grp}')
        out[f'desc_{grp}_health_breach_n'] = k
    with open(PART, 'w', encoding='utf-8', newline='\n') as f:
        f.write(json.dumps(out, indent=1, sort_keys=True) + '\n')
    print(f'wrote {PART.relative_to(ROOT)}: {out}')


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
    g.add_argument('--constants', action='store_true',
                   help='write constants_parts/274.json (then merge with scripts/270)')
    a = ap.parse_args()
    check_layout()
    if a.constants:
        emit_constants()
    elif a.layout:
        print_layout()
    else:
        write_set(a.set_n)


if __name__ == '__main__':
    main()
