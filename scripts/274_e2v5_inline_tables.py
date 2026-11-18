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
    2: [3, 4, 5],
    3: [6, 7, 8],
    4: [9, 10, 11],
    5: [12],
    6: [13],
    7: [14, 15],
    8: [16],
    9: [17, 18, 19],
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
    if v > 0.999:
        return '> .999'
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
    return dict(new=new, title=title, note=note, md='\n'.join(out) + '\n',
                panels=[(pt, h, r, (k[0] if k else None)) for pt, h, r, *k in panels])


# ------------------------------------------------------------------ note numbers
# Every number written into a note goes through a Notes object, which records the text
# shown, its committed source and the source value. write_set dumps the registry to
# outputs/essay2_check/note_numbers_setN.json (git-excluded) for the note checks.
NOTE_REG = {}
CHECK_DIR = ROOT / 'outputs' / 'essay2_check'


class Notes:
    def __init__(self, table):
        self.t = table
        NOTE_REG[table] = []

    def reg(self, shown, source, value):
        NOTE_REG[self.t].append(dict(shown=str(shown), source=source,
                                     value=value if isinstance(value, (int, float, str, bool)) else str(value)))
        return str(shown)

    def i(self, value, source):
        return self.reg(fmt_int(value), source, float(value))

    def f(self, value, dp, source, signed=False):
        return self.reg(fmt_num(value, dp, signed), source, float(value))

    def p(self, value, source):
        return self.reg(fmt_p(value), source, float(value))

    def r(self, value, dp, source):
        """A bounded share / correlation written without a leading zero."""
        sh = fmt_num(value, dp)
        sh = sh[1:] if sh.startswith('0.') else (MINUS + sh[2:] if sh.startswith(MINUS + '0.') else sh)
        return self.reg(sh, source, float(value))

    def pct(self, value, dp, source):
        return self.reg(f'{fmt_num(100 * float(value), dp)}', source + ' (x 100)', 100 * float(value))

    def c(self, key, kind='f', dp=2):
        v = V(key)
        src = f'constants values.{key}'
        if kind == 'i':
            return self.i(v, src)
        if kind == 'p':
            return self.p(v, src)
        if kind == 'r':
            return self.r(v, dp, src)
        if kind == 'pct':
            return self.pct(v, dp, src)
        return self.f(v, dp, src)

    def d(self, shown, source):
        """A design constant (window bound, cap rule, code set) with the file that defines it."""
        return self.reg(shown, 'design: ' + source, shown)


def claim(ok, what):
    """A statement a note makes about the data; the render stops if the data do not bear it out."""
    if not ok:
        sys.exit(f'note claim fails: {what}')


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
        reg_ = ('—' if str(r.treated).strip() == '' else
                f'{fmt_int(r.treated)} ({fmt_int(r.t_orgs)}, {fmt_int(r.t_parents)})')
        rows_a.append([ATTRITION_LABELS[r.step], blank_dash(r.removed, fmt_int), fmt_int(r.N),
                       reg_, blank_dash(r.control, fmt_int)])
    hdr_a = ['Step', 'Removed', 'Remaining', 'Registrant events (organizations, parent filer entities)',
             'Other events']

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
    nb = Notes(1)
    ev = pd.read_csv(PANEL_CSV, dtype={'final_cik': str})
    both = ev[ev.final_cik.isin(s['both_parents']) & (ev.fcc_form499 == 0)]
    other_names = sorted(both.org_name.unique())
    claim(other_names == ['NBC Sports Group', 'Verizon Media'], f'other-side names {other_names}')
    n_nbc, n_vzm = (both.org_name == 'NBC Sports Group').sum(), (both.org_name == 'Verizon Media').sum()
    att_ = appendix_csv('01_sample_attrition.csv')
    first, g2 = att_.iloc[0], att_[att_.step == 'Gate 2 adjacency verdicts'].iloc[0]
    can0 = att_[att_.step == 'Canonical events (post-Gate 2)'].iloc[0]
    claim(int(float(g2.N)) == int(float(can0.N)), 'records after Gate 2 = canonical events')
    note = (f'Each row of Panel A is one step in building the analytical sample. The first four rows count '
            f'Privacy Rights Clearinghouse (PRC) notification records; from the row "canonical events after '
            f'Gate 2" onward the rows count canonical events, so the unit changes at that row, where the '
            f'{nb.i(g2.N, "01, Gate 2 adjacency verdicts / N")} records retained become '
            f'{nb.i(can0.N, "01, Canonical events (post-Gate 2) / N")} canonical events. A notification record '
            f'is one entry in the PRC data, and one breach can produce several records, so the starting '
            f'{nb.i(first.N, "01, PRC universe / N")} records are not {nb.i(first.N, "01, PRC universe / N")} '
            f'breaches. Gate 1 is the entity-resolution screen: it keeps a record only when the reporting '
            f'organization resolves to a public filer entity. Gate 2 is the adjacency review: it examines records '
            f'at the same parent filer entity whose dates lie close together and rules whether they describe the '
            f'same breach, so that each breach enters once. Removed is the count dropped at a step and Remaining '
            f'the count left. Registrant counts are reported at the event level only, because registration is '
            f'assigned to events; the registrant column gives registrant events with, in parentheses, the '
            f'organizations and parent filer entities they belong to, and an em dash (—) marks a count the ledger does not track at that step. '
            f'Panel B reports the final sample of {nb.i(n, "01, final row / N")} events '
            f'({nb.i(nt, "01, final row / treated")} Form 499 registrant events and '
            f'{nb.i(nc, "01, final row / control")} other events) at three levels. A Form 499 registrant event is '
            f'an event at a firm registered on Federal Communications Commission (FCC) Form 499. The parent filer '
            f'entity is the Securities and Exchange Commission (SEC) filer that owns the breached organization; '
            f'it is the clustering unit for inference (G = {nb.i(g, "constants values.ann_G (= distinct final_cik in v5_event_panel.csv)")}). '
            f'The registrant and other parent counts sum to {nb.i(gt + gc, "v5_event_panel.csv, distinct final_cik by group, summed")} '
            f'rather than {nb.i(g, "constants values.ann_G")} because '
            f'{nb.i(len(s["both_parents"]), "v5_event_panel.csv, final_cik in both groups")} parent filer '
            f'entities, Comcast and Verizon, have events in both groups: the '
            f'{nb.i(n_nbc, "v5_event_panel.csv, NBC Sports Group events")} NBC Sports Group events (Comcast) and '
            f'the {nb.i(n_vzm, "v5_event_panel.csv, Verizon Media events")} Verizon Media event (Verizon) are '
            f'other events, adjudicated as not registrant operations, while the carrier subsidiaries’ events '
            f'are registrant events. Panel C counts events by the year of the agency reporting date. "One group '
            f'only" marks the {nb.c("years_single_kind", "i")} years whose events are all registrant events or '
            f'all other events; together they hold {nb.c("years_single_kind_events", "i")} events, '
            f'{nb.c("years_single_kind_treated", "i")} of them registrant events. Under year fixed effects each '
            f'event is compared only with events reported in the same year, so a year with only one group offers '
            f'no comparison and contributes nothing to the registrant estimate. Reporting dates run from '
            f'{nb.reg(s["date_min"], "v5_event_panel.csv, min reported_date", s["date_min"])} to '
            f'{nb.reg(s["date_max"], "v5_event_panel.csv, max reported_date", s["date_max"])}. CRSP is the '
            f'Center for Research in Security Prices; Compustat is the S&P Global accounting database.')
    claim(len(one_group) == V('years_single_kind'), 'one-group years match the constants')
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

    nb = Notes(2)
    dfx = diff
    ctrl_sig = [v for v in CONTROL_VARS if float(dfx.loc[v, 'p']) < .05]
    claim(ctrl_sig == [v for v in CONTROL_VARS if v != 'delay_w'], 'every control but the gap differs at .05')
    claim(float(dfx.loc['dv', 'p']) >= .05 and float(dfx.loc['pre_sd', 'p']) < .05
          and float(dfx.loc['post_sd', 'p']) < .05, 'change not different; both levels different')
    offd = [(abs(float(cor.loc[a, b])), a, b) for i_, a in enumerate(CORR_ORDER) for b in CORR_ORDER[:i_]]
    top = max(offd)
    claim({top[1], top[2]} == {'fcc_form499', 'firm_size_log'}, 'registration-size is the largest correlation')
    hc_c, hc_t = V('desc_control_health_breach_n'), V('desc_treated_health_breach_n')
    cap = cell[('full', 'delay_w')]['max']
    nN = {g: nb.i(cell[(g, 'dv')].N, f'02A, {g} / dv / N') for g in ('full', 'treated', 'control')}
    note = (f'Each row compares the {nN["treated"]} Form 499 registrant events with the {nN["control"]} other '
            f'events in the analytical sample of {nN["full"]} events. '
            f'The dependent variable is the change in abnormal return volatility: the standard deviation (SD) of '
            f'daily abnormal returns, RET − vwretd (the stock’s return minus the CRSP value-weighted '
            f'market return), in percentage points, over trading days '
            f'{nb.d("[+1, +20]", "constants primary_outcome")} after the agency reporting date minus the same SD '
            f'over trading days {nb.d("[−60, −11]", "constants primary_outcome")} before it; the '
            f'pre-window and post-window rows report the two levels. M is the group mean and SD the group '
            f'standard deviation. Difference is the registrant mean minus the other-firm mean, with its standard '
            f'error (SE) in parentheses; a positive difference means the registrant events have the higher '
            f'value. The Welch t-test tests whether the two group means are equal. It does not assume that the '
            f'two groups have equal variances, which matters here because the groups differ in size and in '
            f'spread, and it uses the Welch–Satterthwaite degrees of freedom (df) shown in parentheses. A '
            f'p-value below .05 indicates that the means differ. The two groups do not differ on the change '
            f'(p = {nb.p(dfx.loc["dv", "p"], "02B, dv / p")}) but differ on the pre-window and post-window levels '
            f'(p = {nb.p(dfx.loc["pre_sd", "p"], "02B, pre_sd / p")} and '
            f'{nb.p(dfx.loc["post_sd", "p"], "02B, post_sd / p")}) and on every control except the disclosure '
            f'gap (p = {nb.p(dfx.loc["delay_w", "p"], "02B, delay_w / p")}). Log total assets is the natural log '
            f'of Compustat total assets. Leverage is total liabilities divided by total assets. Return on assets '
            f'is net income divided by total assets. The health-breach flag equals 1 when the breach record lists '
            f'medical or health information as affected; it applies to '
            f'{nb.c("desc_full_health_breach_n", "i")} events, all of them other '
            f'events ({nb.i(hc_t, "constants values.desc_treated_health_breach_n")} registrant events). Prior '
            f'breach events counts earlier sample events at the same parent filer entity. The disclosure gap is '
            f'the number of days from the breach date to the agency reporting date; gaps of '
            f'{nb.d("−30", "scripts/156 (delay floor rule)")} to {nb.d("−1", "scripts/156")} days, '
            f'where the reporting date precedes the breach date by a field-level error, are set to 0, and values '
            f'are capped at the in-sample {nb.d("99th", "scripts/163 (P99 winsorization rule)")} percentile (P99), '
            f'{nb.f(cap, 2, "02A, full / delay_w / max (the P99 cap)")} days. Panel C reports Pearson '
            f'correlations among the model variables over all {nN["full"]} events, lower triangle only; the column '
            f'numbers refer to the numbered rows. The largest correlation in absolute value is between '
            f'registration and log total assets, '
            f'{nb.r(cor.loc["fcc_form499", "firm_size_log"], 2, "03, fcc_form499 x firm_size_log")}. Percentiles, '
            f'minima and maxima are in the committed appendix CSV. RET is the CRSP daily stock return and vwretd '
            f'the CRSP value-weighted market return; CRSP is the Center for Research in Security Prices.')
    return render_table(2, 'Descriptive Statistics by Registration',
                        [('Dependent variable', hdr_ab, group_rows(DV_VARS)),
                         ('Controls', hdr_ab, group_rows(CONTROL_VARS)),
                         ('Correlations of model variables', hdr_c, rows_c, CORRELATION)], note)


RENDERERS.update({1: table_1, 2: table_2})


# ------------------------------------------------------------------ Set 2 shared
RECORD_SPEC = ('Record-level panels use the earlier specification: raw-return volatility on '
               'notification records, size measured by market value.')
QLAB = {'main': 'All', 'Q1': 'Q1 (smallest)', 'Q2': 'Q2', 'Q3': 'Q3', 'Q4': 'Q4 (largest)'}


def V(key):
    """A value from constants_essay2.json; exits if absent (a missing key is a source error)."""
    v = const(load_constants(), f'values.{key}')
    if v == NO_SOURCE:
        sys.exit(f'constants key values.{key} missing')
    return v


def demojibake(s):
    """Undo UTF-8 read as cp1252 in names (e.g. 'Oâ€™Connor' -> 'O’Connor'); text only."""
    try:
        return s.encode('cp1252').decode('utf-8')
    except (UnicodeEncodeError, UnicodeDecodeError):
        return s


def est_se(coef, se, dp=3):
    if str(se).strip() == '':
        return fmt_num(coef, dp)
    return f'{fmt_num(coef, dp)} ({fmt_num(se, dp)})'


def apa_share(x, dp=2):
    """A proportion bounded by 1: no leading zero (R², shares)."""
    s = fmt_num(x, dp)
    return s[1:] if s.startswith('0.') else s


def pct(num, den, dp=1):
    return f'{fmt_num(100 * num / den, dp)}%'


# ------------------------------------------------------------------ Table 3
def table_3():
    fp = appendix_csv('05A_four_panel_decomposition.csv')
    cell = {(r.panel, r.cell): r for _, r in fp.iterrows()}
    order = ['main', 'Q1', 'Q2', 'Q3', 'Q4']

    def record_panel(pan):
        rows = []
        for c in order:
            r = cell[(pan, c)]
            rows.append([QLAB[c], est_se(r.coef, r.se), fmt_p(r.p), fmt_int(r.cellN),
                         fmt_int(r.treatedN), fmt_int(r.t_parents)])
        if sum(int(float(cell[(pan, c)].cellN)) for c in order[1:]) != int(float(cell[(pan, 'main')].cellN)):
            sys.exit(f'Table 3: quartile records do not sum to the total in {pan}')
        rows.append(['Q1 − Q4 spread', fmt_num(cell[(pan, 'Q1_minus_Q4_spread')].coef, 3), '', '', '', ''])
        return rows

    hdr_ab = ['Cell', 'Estimate (SE)', 'p', 'Records', 'Treated records', 'Treated parent filer entities']

    rows_c = []
    for c in order:
        a, b = cell[('iii_dedup_sic', c)], cell[('iv_dedup_form499', c)]
        if a.cellN != b.cellN:
            sys.exit(f'Table 3 Panel C: event counts differ between definitions in {c}')
        cl = {'main': 'All', 'Q1': 'Q1, smallest', 'Q4': 'Q4, largest'}.get(c, c)
        rows_c.append([f'{cl} ({fmt_int(a.cellN)} events)',
                       est_se(a.coef, a.se), fmt_p(a.p), f'{fmt_int(a.treatedN)} ({fmt_int(a.t_parents)})',
                       est_se(b.coef, b.se), fmt_p(b.p), f'{fmt_int(b.treatedN)} ({fmt_int(b.t_parents)})'])
    rows_c.append(['Q1 − Q4 spread', fmt_num(cell[('iii_dedup_sic', 'Q1_minus_Q4_spread')].coef, 3), '', '',
                   fmt_num(cell[('iv_dedup_form499', 'Q1_minus_Q4_spread')].coef, 3), '', ''])
    hdr_c = ['Cell', 'Industry codes: estimate (SE)', 'p', 'Treated events (parents)',
             'Form 499: estimate (SE)', 'p', 'Treated events (parents)']

    rp = appendix_csv('05B_records_per_event.csv')
    summ = {r['item']: r['value'] for _, r in rp[rp.panel == 'summary'].iterrows()}
    dist = rp[rp.panel == 'distribution']
    if sum(int(float(v)) for v in dist.value) != int(float(summ['events'])):
        sys.exit('Table 3 Panel D: distribution does not sum to events')
    if sum(int(re.search(r'_(\d+)_records', i).group(1)) * int(float(v))
           for i, v in zip(dist['item'], dist.value)) != int(float(summ['records'])):
        sys.exit('Table 3 Panel D: distribution does not sum to records')
    big = rp[rp.panel == 'largest'].copy()
    big['cik'] = big['item'].str.extract(r'^c(\d+) ')[0]
    big['date'] = big['item'].str.extract(r'(\d{4}-\d{2}-\d{2})$')[0]
    top = big.iloc[0]
    pair = big[(big.cik == top.cik) & big.date.str.startswith('2024')]
    if len(pair) != 2:
        sys.exit('Table 3 Panel D: expected two 2024 events for the largest parent')
    rows_d = [['Records', fmt_int(summ['records'])],
              ['Events', fmt_int(summ['events'])],
              ['Mean records per event', fmt_num(summ['mean_records_per_event'], 2)],
              ['Median records per event', fmt_int(summ['median_records_per_event'])],
              ['Events with more than one record', fmt_int(summ['events_with_more_than_one_record'])],
              ['Records in those events', fmt_int(summ['records_in_multi_record_events'])]]
    for _, r in pair.iterrows():
        rows_d.append([f'Records in the {r.date} event of parent CIK {r.cik}', fmt_int(r.value)])
    rows_d.append([f'Records in both 2024 events of parent CIK {top.cik}',
                   fmt_int(sum(int(float(v)) for v in pair.value))])
    hdr_d = ['Measure', 'Value']

    gg = appendix_csv('09_gradient_grid.csv')
    alab = {'breach': 'Breach date', 'notification': 'Notification date', 'TOTAL': 'Both anchors'}
    rows_e = [[alab[r.anchor], fmt_int(r.n_specs), fmt_int(r.q1_gt_q4), fmt_int(r.monotone_stepdown)]
              for _, r in gg.iterrows()]
    hdr_e = ['Anchor date', 'Specifications', 'Q1 estimate above Q4', 'Monotone decline Q1 to Q4']

    m = cell[('i_industry_codes_records', 'main')]
    g_tot = int(gg[gg.anchor == 'TOTAL'].n_specs.iloc[0])
    g_per = sorted({int(x) for x in gg[gg.anchor != 'TOTAL'].n_specs})
    if len(g_per) != 1:
        sys.exit('Table 3 Panel E: anchors have different specification counts')
    nb = Notes(3)
    I_, II_, III_, IV_ = 'i_industry_codes_records', 'ii_form499_repaired', 'iii_dedup_sic', 'iv_dedup_form499'
    q1p = cell[(IV_, 'Q1')]
    note = (f'Each cell reports the coefficient on treatment from a separate ordinary least squares (OLS) '
            f'regression of the change in raw-return volatility on treatment and the earlier specification’s '
            f'controls (pre-period volatility, size, leverage, return on assets, disclosure gap, prior breaches '
            f'and the health-breach flag), estimated within the sample the row names; the standard error (SE) '
            f'is in parentheses. {RECORD_SPEC} Panels A and B use '
            f'{nb.i(m.cellN, f"05A, {I_} / main / cellN")} notification records, quartiles of log market value and '
            f'HC3 heteroskedasticity-consistent standard errors, which do not account for clustering. Panel A '
            f'treats a record when its Standard Industrial Classification (SIC) code is '
            f'{nb.d("4813, 4841 or 4899", "scripts/269 section B (industry-code set)")}; Panel B treats it when '
            f'its parent filer entity is registered on Federal Communications Commission (FCC) Form 499. Panels A '
            f'and B estimate on the same records, so their estimates share observations and no test of their '
            f'difference is reported. Panel C repeats the comparison on '
            f'{nb.i(cell[(IV_, "main")].cellN, f"05A, {IV_} / main / cellN")} canonical events (records '
            f'collapsed to events), with the earlier breach-date-anchored raw-return outcome and quartiles of log '
            f'total assets from the canonical event file; Treated events (parents) gives the treated events and, '
            f'in parentheses, the treated parent filer entities. The Q1 − Q4 spread is the Q1 estimate minus '
            f'the Q4 estimate. A p-value below .05 marks a coefficient different from zero under HC3, but '
            f'treatment varies across few parent filer entities (the Panel C Q1 cell has '
            f'{nb.i(q1p.treatedN, f"05A, {IV_} / Q1 / treatedN")} treated events at '
            f'{nb.i(q1p.t_parents, f"05A, {IV_} / Q1 / t_parents")} parent), so the event-level standard errors '
            f'are too small for this design to support a rejection. Panel D shows how the records concentrate in '
            f'events: {nb.i(summ["events_with_more_than_one_record"], "05B, summary / events_with_more_than_one_record")} '
            f'of the {nb.i(summ["events"], "05B, summary / events")} events have more than one record and '
            f'together supply {nb.i(summ["records_in_multi_record_events"], "05B, summary / records_in_multi_record_events")} '
            f'records, and the two 2024 events of parent CIK '
            f'{nb.reg(top.cik, "05B, largest / first row parent CIK", top.cik)} supply '
            f'{nb.i(sum(int(float(v_)) for v_ in pair.value), "05B, largest / two 2024 rows of that CIK, summed")}. '
            f'Panel E counts specifications only: across '
            f'{nb.i(g_tot, "09, TOTAL / n_specs")} window specifications on the corrected data '
            f'({nb.i(g_per[0], "09, breach and notification / n_specs")} per anchor date, the breach date and the '
            f'notification date), it reports how many put the Q1 estimate above Q4 '
            f'({nb.i(gg[gg.anchor == "TOTAL"].q1_gt_q4.iloc[0], "09, TOTAL / q1_gt_q4")}) and how many decline '
            f'monotonically from Q1 to Q4 ({nb.i(gg[gg.anchor == "TOTAL"].monotone_stepdown.iloc[0], "09, TOTAL / monotone_stepdown")}); '
            f'the full grid is in the committed CSV outputs/tables/essay2_v2/t31_gradient_grid.csv. Q1 to Q4 are '
            f'size quartiles, Q1 smallest; HC3 is the heteroskedasticity-consistent covariance estimator, type 3; '
            f'CIK is the SEC (Securities and Exchange Commission) Central Index Key.')
    return render_table(3, 'How the Size Gradient Is Produced',
                        [('Industry-code treatment on records', hdr_ab,
                          record_panel('i_industry_codes_records')),
                         ('Form 499 treatment on the same records', hdr_ab, record_panel('ii_form499_repaired')),
                         ('Events instead of records, both definitions', hdr_c, rows_c),
                         ('Concentration of records in events', hdr_d, rows_d),
                         (f'Gradient on corrected data, {g_tot} specifications', hdr_e, rows_e)], note)


# ------------------------------------------------------------------ Table 4
def table_4():
    gc = appendix_csv('08A_misclassified_group_comparisons.csv').set_index('group')
    mr = appendix_csv('07_misclassified_records.csv')

    def grow(label, g):
        r = gc.loc[g]
        return [label, fmt_int(r.N), fmt_int(r.orgs), f'{fmt_num(r.mean_ln_mktcap, 2)} ({fmt_num(r.sd_ln_mktcap, 2)})',
                f'{fmt_num(r.mean_vol_change, 2)} ({fmt_num(r.sd_vol_change, 2)})']

    part = ['missed_by_industry_codes', 'misclassified_repaired', 'concordant_registrants', 'control']
    n_all = sum(int(gc.loc[g].N) for g in part)
    if n_all != int(float(cell_main_records())):
        sys.exit(f'Table 4: groups sum to {n_all}, not the record total')
    n_dis = int(gc.loc['missed_by_industry_codes'].N) + int(gc.loc['misclassified_repaired'].N)
    if n_dis != V('disagree_records'):
        sys.exit('Table 4: disagreement records do not match constants')
    rows_a = [grow('Disagree: Form 499 registrant, no industry code (missed by the codes)', part[0]),
              grow('Disagree: industry code, not a registrant (damaged source entries)', part[1])]
    for _, r in mr.iterrows():
        rows_a.append([f' {r.organization} (SIC {r.source_sic}, breach {r.breach_date}, Q{r.prior_spec_quartile_mktcap})',
                       '1', '1', fmt_num(r.ln_mktcap_as_found, 2), fmt_num(r.volatility_change, 2)])
    rows_a += [grow('Agree: industry code and registrant', part[2]),
               grow('Agree: neither definition treats', part[3]),
               ['All records', fmt_int(n_all), '', '', '']]
    hdr_a = ['Group', 'Records', 'Organizations', 'Log market value M (SD)', 'Change M (SD)']

    comp = appendix_csv('06A_q1_transition_components.csv').set_index('component')
    recs = appendix_csv('06B_q1_transition_records.csv')
    clab = {'stayed': 'Treated under both definitions', 'dropped': 'Treated by codes only (dropped)',
            'added': 'Treated by Form 499 only (added)', 'never_treated': 'Treated by neither'}

    def crow(k):
        r = comp.loc[k]
        ms_ = '—' if str(r['mean']).strip() == '' else (
            f'{fmt_num(r["mean"], 2)} ({fmt_num(r.sd, 2)})' if str(r.sd).strip() else fmt_num(r['mean'], 2))
        return [clab[k], fmt_int(r.N_records), fmt_int(r.N_events), ms_]

    rows_b = [crow(k) for k in ['stayed', 'dropped', 'added']]
    added = recs[recs.direction == 'added']
    if len(added) != int(comp.loc['added'].N_records) or len(added) != V('q1_added_records'):
        sys.exit('Table 4 Panel B: added records disagree')
    for pc, g in sorted(added.groupby('parent_cik'), key=lambda kv: (-len(kv[1]), kv[0])):
        name = min(g.organization, key=lambda x: (len(x), x))
        vc = g.volatility_change.astype(float)
        rows_b.append([f' of which {name} (parent CIK {pc})', fmt_int(len(g)), '',
                       f'{fmt_num(vc.mean(), 2)} ({fmt_num(vc.std(), 2)})'])
    rows_b.append(crow('never_treated'))
    q1n = sum(int(comp.loc[k].N_records) for k in comp.index)
    hdr_b = ['Q1 component', 'Records', 'Events', 'Change M (SD)']

    mi = gc.loc['missed_by_industry_codes']
    mc = pd.read_csv(MISSED_CSV)
    if int(mc.records.sum()) != int(mi.N) or mc.organization.nunique() != int(mi.orgs):
        sys.exit(f'{MISSED_CSV.name} disagrees with 08A (records / organizations)')
    n_q1, n_q4 = V('q1_added_records'), V('missed_q4_records')
    rows_c = [['All missed registrants', fmt_int(mi.N), fmt_int(mi.orgs),
               f'{fmt_num(mi.mean_vol_change, 2)} ({fmt_num(mi.sd_vol_change, 2)})',
               f'Q1 {n_q1}; Q2\u2013Q3 {int(mi.N) - n_q1 - n_q4}; Q4 {n_q4}']]
    hdr_c = ['Group', 'Records', 'Organizations', 'Change M (SD)', 'Quartile placement (records)']

    nb = Notes(4)
    claim(set(mr.parent_cik) == {'unresolved'}, 'damaged entries resolve to no parent')
    added_by = {pc: len(g) for pc, g in added.groupby('parent_cik')}
    note = (f'Each row of Panel A is a group of the {nb.i(n_all, "08A, N summed over the four groups")} '
            f'notification records, defined by the two treatment definitions: the industry-code definition '
            f'(Standard Industrial Classification, SIC, code {nb.d("4813, 4841 or 4899", "scripts/269 section B")} '
            f'on the record) and the Form 499 definition (parent filer entity registered on Federal '
            f'Communications Commission Form 499). The two definitions disagree on '
            f'{nb.c("disagree_records", "i")} records. Missed by the codes are Form 499 registrants whose record '
            f'carries none of the three codes ({nb.i(mi.N, "08A, missed_by_industry_codes / N")} records at '
            f'{nb.i(mi.orgs, "08A, missed_by_industry_codes / orgs")} organizations). Damaged source entries are '
            f'the {nb.i(gc.loc["misclassified_repaired"].N, "08A, misclassified_repaired / N")} records coded '
            f'{nb.reg(str(mr.source_sic.iloc[0]), "07, source_sic", str(mr.source_sic.iloc[0]))} whose organization '
            f'field holds an AT&T breach label rather than a firm name, so they resolve to no parent filer entity '
            f'and no registration. Industry code and registrant are records both definitions treat. Neither '
            f'definition treats are records outside both, the comparison group under either definition. M is the '
            f'mean and SD the standard deviation; log market value is the earlier dataset’s size variable; '
            f'change is the change in raw-return volatility under the earlier specification. Panel B splits the '
            f'{nb.i(q1n, "06A, N_records summed")} records in the smallest size quartile (Q1) by how the two '
            f'definitions treat them. The added records are treated under Form 499 only: '
            f'{nb.i(added_by[1609711] if 1609711 in added_by else added_by["1609711"], "06B, added rows, parent_cik 1609711")} '
            f'from GoDaddy, a domain registrar, and '
            f'{nb.i(added_by[1447669] if 1447669 in added_by else added_by["1447669"], "06B, added rows, parent_cik 1447669")} '
            f'from Twilio, a communications platform; their mean change, '
            f'{nb.f(comp.loc["added"]["mean"], 2, "06A, added / mean")}, compares with '
            f'{nb.f(comp.loc["never_treated"]["mean"], 2, "06A, never_treated / mean")} for records neither '
            f'definition treats. Panel C summarizes the {nb.i(mi.N, "08A, missed_by_industry_codes / N")} missed '
            f'records: {nb.c("q1_added_records", "i")} fall in Q1, {nb.c("missed_q4_records", "i")} in Q4 and the '
            f'remaining {nb.i(int(mi.N) - n_q1 - n_q4, "08A N minus constants q1_added_records and missed_q4_records")} '
            f'in Q2 or Q3. The firm names and record SIC codes of the '
            f'{nb.i(mi.N, "08A, missed_by_industry_codes / N")} records are in the committed CSV '
            f'{MISSED_CSV.relative_to(ROOT).as_posix()}. {RECORD_SPEC} Q1 to Q4 are quartiles of log market '
            f'value, Q1 smallest; CIK is the SEC Central Index Key.')
    return render_table(4, 'Where the Two Treatment Definitions Disagree',
                        [(f'The {fmt_int(n_dis)} disagreement records against the {fmt_int(n_all - n_dis)} '
                          f'agreements', hdr_a, rows_a),
                         ('Records added to the smallest quartile', hdr_b, rows_b),
                         ('Registrants the industry codes miss', hdr_c, rows_c)], note)


def cell_main_records():
    fp = appendix_csv('05A_four_panel_decomposition.csv')
    return fp[(fp.panel == 'i_industry_codes_records') & (fp.cell == 'main')].cellN.iloc[0]


# ------------------------------------------------------------------ Table 5
def table_5():
    ic = appendix_csv('10A_identifier_collisions.csv')
    rows_a = []
    for _, r in ic.iterrows():
        orgs = [demojibake(o) for o in r.organizations_absorbed.split('; ')]
        ex = '; '.join(orgs[:2]) + ('; …' if len(orgs) > 2 else '')
        rows_a.append([r.legacy_cik, r.ticker_for_cik, fmt_int(len(orgs)), ex, fmt_int(r.n_records),
                       fmt_int(r.canonical_events_with_these_names),
                       'Yes' if r.legacy_cik_is_canonical_parent == 'True' else 'No'])
    if len(rows_a) != V('collision_sinks'):
        sys.exit('Table 5 Panel A: collision count disagrees with constants')
    hdr_a = ['Legacy CIK', 'Ticker on the CIK', 'Organizations absorbed', 'Examples', 'Records',
             'Canonical events with these names', 'CIK is a canonical parent']

    rt = appendix_csv('10B_recycled_tickers.csv')
    if len(rt) != V('recycled_ticker_events'):
        sys.exit('Table 5 Panel B: recycled-ticker count disagrees with constants')
    rows_b = [[r.organization, r.event_date, r.ticker, f'{r.assigned_security} ({r.assigned_permno})',
               r.ticker_end_for_assigned, r.later_owner_in_mapping] for _, r in rt.iterrows()]
    hdr_b = ['Organization', 'Breach date', 'Ticker', 'Security the old rule assigned (PERMNO)',
             'Assigned security’s ticker ended', 'Later owner of the ticker (PERMNO)']

    sv = appendix_csv('10C_size_variable_reconciliation.csv').set_index('candidate')
    slab = {'ln_market_cap': 'Log market value (CRSP price × shares outstanding)',
            'ln_total_assets': 'Log total assets (earlier dataset)'}
    rows_c = [[slab[k], fmt_int(r.N), fmt_num(r.slope, 2), fmt_num(r.intercept, 2), apa_share(r.R2),
               apa_share(r.share_within_010), apa_share(r.share_within_025)] for k, r in sv.iterrows()]
    hdr_c = ['Candidate measure', 'Records', 'Slope', 'Intercept', 'R²', 'Share within 0.10',
             'Share within 0.25']

    att = appendix_csv('01_sample_attrition.csv').set_index('step')
    ms = appendix_csv('11_missingness_precase.csv').set_index('variable')
    base = att.loc['Notification on/before 2024-12-31']
    nb, tb, cb = int(float(base.N)), int(float(base.treated)), int(float(base.control))
    if nb != V('miss_base'):
        sys.exit('Table 5 Panel D: base disagrees with constants')
    steps = [('Volatility windows computable', 'e2_vol_change (volatility windows)',
              'Fewer trading days than the volatility windows need'),
             ('Compustat covariates complete', 'firm_size_log', 'No Compustat match (size, leverage, return on assets)'),
             ('Disclosure delay valid', 'disclosure_delay_days', 'Invalid disclosure date'),
             ('Malformed-record exclusion (FINAL)', 'ATT_artifact_records (excluded at final step)',
              'Damaged source records')]
    rows_d, prev, lost = [], (nb, tb, cb), [0, 0, 0]
    for step, mv, lab in steps:
        r = att.loc[step]
        cur = (int(float(r.N)), int(float(r.treated)), int(float(r.control)))
        d = tuple(p - c for p, c in zip(prev, cur))
        if d[0] != int(ms.loc[mv].missing) or d[0] != d[1] + d[2]:
            sys.exit(f'Table 5 Panel D: ledger and missingness disagree at {step}')
        rows_d.append([lab, fmt_int(d[0]), pct(d[0], nb), fmt_int(d[1]), fmt_int(d[2])])
        lost = [a + b for a, b in zip(lost, d)]
        prev = cur
    rows_d.append(['All losses', fmt_int(lost[0]), pct(lost[0], nb), fmt_int(lost[1]), fmt_int(lost[2])])
    rows_d.append(['Retained', fmt_int(prev[0]), pct(prev[0], nb), f'{fmt_int(prev[1])} ({pct(prev[1], tb)})',
                   f'{fmt_int(prev[2])} ({pct(prev[2], cb)})'])
    hdr_d = ['Reason', 'Events', f'Share of {fmt_int(nb)}', 'Registrant events', 'Other events']

    nn = Notes(5)
    big = ic.assign(norg=[len(x.split('; ')) for x in ic.organizations_absorbed]).sort_values('norg').iloc[-1]
    meta = rt[rt.ticker == 'META'].iloc[0]
    dash = rt[rt.ticker == 'DASH'].iloc[0]
    note = (f'Panel A lists the {nn.c("collision_sinks", "i")} legacy identifiers in the earlier matching chain '
            f'at which an identifier collision occurred: one Securities and Exchange Commission (SEC) Central '
            f'Index Key (CIK) absorbed the names of unrelated organizations, so their breach records took on that '
            f'firm’s stock data. Organizations absorbed counts the distinct organization names on the CIK, '
            f'Records counts their breach records, and Canonical events with these names counts events in the '
            f'current chain that carry one of those names; the largest collision, CIK '
            f'{nn.reg(big.legacy_cik, "10A, legacy_cik with most organizations", big.legacy_cik)}, absorbed '
            f'{nn.c("collision_max_orgs", "i")} organizations and {nn.i(big.n_records, "10A, n_records of that CIK")} '
            f'records. Panel B lists the {nn.c("recycled_ticker_events", "i")} events at which ticker reuse would '
            f'have matched the breached firm to an earlier, unrelated holder of the same ticker symbol: the old '
            f'fallback rule took the last security to carry the ticker before the breach date, here a security '
            f'whose ticker had ended years before (in '
            f'{nn.reg(str(meta.ticker_end_for_assigned)[:4], "10B, META / ticker_end_for_assigned (year)", str(meta.ticker_end_for_assigned))} '
            f'for META and {nn.reg(str(dash.ticker_end_for_assigned)[:4], "10B, DASH / ticker_end_for_assigned (year)", str(dash.ticker_end_for_assigned))} '
            f'for DASH). The current chain blocks that rule, and none of the {nn.i(len(rt), "10B, rows")} events has a CRSP match. '
            f'PERMNO is the CRSP permanent security identifier. Panel C regresses the earlier dataset’s size '
            f'variable on two candidate measures. Against log market value the slope is '
            f'{nn.c("sizerec_mktcap_slope", "f", 2)} and the R² {nn.c("sizerec_mktcap_r2", "r", 2)}, so the '
            f'variable measures market value; against log total assets the slope is '
            f'{nn.c("sizerec_assets_slope", "f", 2)} and the R² {nn.c("sizerec_assets_r2", "r", 2)}. Share '
            f'within gives the share of records whose absolute gap to the candidate is at most '
            f'{nn.d("0.10", "scripts/269 (size reconciliation thresholds)")} or '
            f'{nn.d("0.25", "scripts/269")}. Panel D starts from the {nn.c("miss_base", "i")} events matched to '
            f'CRSP and reported by {nn.d("December 31, 2024", "01, step Notification on/before 2024-12-31")} ({nn.i(tb, "01, Notification on/before 2024-12-31 / treated")} '
            f'registrant and {nn.i(cb, "01, Notification on/before 2024-12-31 / control")} other events). Fewer '
            f'trading days means the stock lacks the trading days the volatility windows require. No Compustat '
            f'match means no annual accounting record supplies size, leverage and return on assets. Invalid '
            f'disclosure date means the reporting date precedes the breach date by more than '
            f'{nn.d("30", "scripts/156 (delay_invalid rule)")} days, so the disclosure gap is set to missing. '
            f'Damaged source records are the {nn.c("miss_att", "i")} records whose organization field holds an '
            f'AT&T breach label rather than a firm name. Retained shares are within each group: '
            f'{nn.i(prev[1], "01, final row / treated")} of {nn.i(tb, "01, 355 row / treated")} registrant events '
            f'({nn.f(100 * prev[1] / tb, 1, "01, 104 / 111 x 100")} percent) and '
            f'{nn.i(prev[2], "01, final row / control")} of {nn.i(cb, "01, 355 row / control")} other events '
            f'({nn.f(100 * prev[2] / cb, 1, "01, 229 / 244 x 100")} percent). {RECORD_SPEC} CRSP is the Center '
            f'for Research in Security Prices; R² is the share of variance explained.')
    return render_table(5, 'Data Quality in the Matching Chain',
                        [('Identifier collisions in the earlier chain', hdr_a, rows_a),
                         ('Reused-ticker matches', hdr_b, rows_b),
                         ('The size-measure defect', hdr_c, rows_c),
                         ('Losses after the CRSP match', hdr_d, rows_d)], note)


RENDERERS.update({3: table_3, 4: table_4, 5: table_5})


# ------------------------------------------------------------------ Set 3 shared
CONV_LABEL = {
    'published_regulated_dummy_4812_4813': ('Published regulated-carrier dummy', '4812, 4813'),
    'prior_spec_4813_4841_4899': ('Earlier specification of this essay', '4813, 4841, 4899'),
    'tuned_4812_4813_4841_4899': ('Tuned to the registry', '4812, 4813, 4841, 4899'),
    'full_range_4800_4899': ('Full communications range', '4800–4899'),
}


def parent_names():
    """Parent filer entity names: the organization column of 17 (one row per canonical treated parent)."""
    sv = appendix_csv('17_sich_vs_curated_sic.csv')
    return {str(r.parent_cik): r.organization for _, r in sv.iterrows()}


# ------------------------------------------------------------------ Table 6
def table_6():
    reg = appendix_csv('12_form499_registry_matches.csv')
    names = parent_names()
    rows_a, tot_rec, tot_ev = [], 0, 0
    order = (reg.groupby('parent_cik').size().sort_values(ascending=False, kind='stable').index)
    for pc in order:
        g = reg[reg.parent_cik == pc]
        ev = {int(x) for x in g.events_in_sample}
        span = set(g.event_span)
        if len(ev) != 1 or len(span) != 1:
            sys.exit(f'Table 6: events per parent not constant for {pc}')
        a_, b_ = next(iter(span)).split('..')
        n_ebs = int((g.end_before_start == 'True').sum())
        rows_a.append([names.get(pc, pc), pc, fmt_int(len(g)), fmt_int(g.FRN.nunique()), fmt_int(n_ebs),
                       fmt_int(next(iter(ev))), f'{a_} to {b_}'])
        tot_rec += len(g)
        tot_ev += next(iter(ev))
    if tot_rec != V('registry_family_records') or tot_ev != V('primary_treated'):
        sys.exit('Table 6 Panel A: totals disagree with the constants')
    rows_a.append(['All treated parent filer entities', '', fmt_int(tot_rec), '', '', fmt_int(tot_ev), ''])
    hdr_a = ['Parent filer entity', 'CIK', 'Registry records matched', 'Distinct FRNs',
             'End date before start date', 'Registrant events', 'Breach dates']

    adj = appendix_csv('13_treatment_adjudications.csv')
    st = adj[adj.kind == 'stage4_pattern']
    ep = adj[adj.kind == 'equity_parent']
    if len(st) != V('adjudication_rules') or len(ep) != V('equity_parent_maps'):
        sys.exit('Table 6: adjudication counts disagree with the constants')
    ruling = {'FORCE TREATED': 'Treated', 'FORCE EXCLUDED': 'Excluded'}
    rows_b = [[r.pattern.replace('^', '').replace(' ?', ' ').replace('|', '; '), ruling[r.direction],
               r.basis.replace('—', '—')] for _, r in st.iterrows()]
    hdr_b = ['Organization name pattern', 'Ruling', 'Basis']
    rows_c = [[r.pattern.split(' -> ')[0], r.pattern.split(' -> ')[1], r.basis] for _, r in ep.iterrows()]
    hdr_c = ['Registrant CIK', 'Parent CIK assigned', 'Basis']

    nb = Notes(6)
    dish = st[st.pattern.str.startswith('DISH')]
    claim(len(dish) == 2 and set(dish.direction) == {'FORCE TREATED', 'FORCE EXCLUDED'}, 'DISH has two rules')
    ebs = int((reg.end_before_start == 'True').sum())
    note = (f'Panel A has one row per treated parent filer entity in the analytical sample '
            f'({nb.i(len(order), "12, distinct parent_cik")} parents, {nb.c("primary_treated", "i")} registrant '
            f'events). The Federal Communications Commission (FCC) Form 499 registry holds '
            f'{nb.c("registry_records", "i")} filer records; Registry records matched counts the records whose '
            f'legal name, doing-business-as name or holding company contains one of the parent’s family '
            f'keywords ({nb.c("registry_family_records", "i")} records in all). A name match counts toward '
            f'treatment only when the matched registration is open on the breach date: its start date falls on or '
            f'before the breach date and its end date, if any, falls after it. Distinct FRNs counts the FCC '
            f'Registration Numbers among the matched records. End date before start date counts matched records '
            f'whose registry end date precedes their start date, a data error in the registry '
            f'({nb.i(ebs, "12, end_before_start == True")} records in all). Registrant events counts the parent’s '
            f'events in the analytical sample, and Breach dates gives the first and last breach date among them. '
            f'Panel B lists the adjudication rules. An adjudication rule is a recorded ruling for an organization '
            f'name pattern that exact name matching against the registry would treat wrongly; it either forces '
            f'treatment, under clause (a), a registration of the organization itself open on the breach date, or '
            f'clause (b), the organization is the parent brand of a registered filer whose subscriber operations '
            f'were breached, or it forces exclusion when neither clause holds. There are '
            f'{nb.c("adjudication_rules", "i")} rules covering {nb.c("adjudication_names", "i")} organization '
            f'names; DISH Network has two rules, so it is excluded before '
            f'{nb.d("July 1, 2020", "13, DISH rules (2020-07-01 divestiture date)")}, when it had no covered '
            f'wireless operation, and treated on and after that date. Panel C lists the '
            f'{nb.c("equity_parent_maps", "i")} equity re-parenting rules, which assign a registrant with no '
            f'traded equity to the parent filer entity that owns it. CIK is the Securities and Exchange Commission '
            f'(SEC) Central Index Key; FRN is the FCC Registration Number; Form 499 registrant means an event at a '
            f'firm registered on FCC Form 499.')
    return render_table(6, 'The Form 499 Registry: Treated Parent Filer Entities and Adjudication Rules',
                        [('Registry records matched to each treated parent filer entity', hdr_a, rows_a),
                         ('Adjudication rules', hdr_b, rows_b),
                         ('Equity re-parenting rules', hdr_c, rows_c)], note)


# ------------------------------------------------------------------ Table 7
def table_7():
    cv = appendix_csv('14_sic_conventions_vs_form499.csv')
    er = appendix_csv('15_sic_convention_errors.csv')
    rows_a = []
    for _, r in cv.iterrows():
        lab, codes = CONV_LABEL[r.convention]
        rows_a.append([f'{lab} (SIC {codes})', fmt_num(r.agree_pct, 1), fmt_int(r.FP), fmt_int(r.FN),
                       fmt_int(r.parents_identified), fmt_int(r.parents_wrongly_included), r.characteristic_failure])
    hdr_a = ['Convention (codes)', 'Event agreement, %', 'False positives', 'False negatives',
             'Treated parents identified', 'Other parents included', 'Characteristic failure']
    elab = {'FALSE_POSITIVE': 'False positive', 'FALSE_NEGATIVE': 'False negative'}
    rows_b = [[CONV_LABEL[r.convention][0], elab[r.error_type], r.organization, r.parent_cik, r.sich,
               fmt_int(r.events)] for _, r in er.iterrows()]
    hdr_b = ['Convention', 'Error', 'Organization', 'Parent CIK', 'SIC', 'Events']

    nb = Notes(7)
    nt = int(cv.N_testable.iloc[0])
    claim(nt == V('sic_testable'), 'testable events match the constants')
    best = cv.sort_values('agree_pct').iloc[-1]
    claim(best.convention.startswith('tuned'), 'the tuned set has the highest agreement')
    pub = cv[cv.convention.str.startswith('published')].iloc[0]
    note = (f'Each row of Panel A applies one industry-code convention to the '
            f'{nb.i(nt, "14, N_testable (= constants sic_testable)")} canonical events with a Compustat '
            f'historical Standard Industrial Classification (SIC) code and compares the result with Federal '
            f'Communications Commission (FCC) Form 499 registration. The conventions are the published regulated-'
            f'carrier dummy (SIC 4812 and 4813), the earlier specification of this essay (4813, 4841 and 4899), a '
            f'set tuned to the registry (4812, 4813, 4841 and 4899) and the full communications range (4800 to '
            f'4899); literature source for each convention: [NO SOURCE]. The tuned set was chosen after looking '
            f'at the registry, so its agreement is an upper bound, not a test. Event agreement is the percentage '
            f'of the {nb.i(nt, "14, N_testable")} events on which the convention and registration agree. A false '
            f'positive is an event the convention codes as a carrier although its parent filer entity is not a '
            f'registrant; a false negative is a registrant event the convention does not code. Treated parents '
            f'identified counts, of the {nb.c("sic_treated_parents_testable", "i")} registrant parent filer '
            f'entities in the comparison, those with at least one event the convention codes as a carrier; Other '
            f'parents included counts non-registrant parents the convention codes as carriers. The tuned set '
            f'agrees most often ({nb.f(best.agree_pct, 1, "14, tuned / agree_pct")} percent) and the published '
            f'dummy identifies the fewest registrant parents ({nb.i(pub.parents_identified, "14, published / parents_identified")}). '
            f'Panel B lists the misclassified organizations under the published dummy and the tuned set, with the '
            f'SIC code that produced the error and the number of events. CIK is the Securities and Exchange '
            f'Commission Central Index Key.')
    for code in ('4812', '4813', '4841', '4899', '4800'):
        nb.d(code, 'scripts/269 CONV (convention code sets)')
    return render_table(7, 'Industry-Code Conventions Against Form 499 Registration',
                        [('Agreement with Form 499 registration', hdr_a, rows_a),
                         ('Misclassified organizations', hdr_b, rows_b)], note)


# ------------------------------------------------------------------ Table 8
def table_8():
    ot = appendix_csv('16_treated_outside_comparison.csv')
    sv = appendix_csv('17_sich_vs_curated_sic.csv')
    rlab = {'no matched ticker': 'No matched ticker',
            'ticker but no Compustat row in 550-day window': 'Ticker, but no Compustat record in the prior 550 days'}
    rows_a = [[r.organization, r.parent_cik, r.reported_date, rlab[r.reason]] for _, r in ot.iterrows()]
    hdr_a = ['Organization', 'Parent CIK', 'Reporting date', 'Reason']
    rows_b = [[r.organization, r.parent_cik, r.tickers, r.sich or '—', r.curated_sic or '—',
               'Registrant' if r.form499 == 'treated' else 'Not a registrant',
               'Yes' if r.sources_disagree == 'True' else 'No'] for _, r in sv.iterrows()]
    hdr_b = ['Organization', 'Parent CIK', 'Tickers', 'Compustat SIC', 'Breach-record SIC', 'Form 499',
             'Sources disagree']

    nb = Notes(8)
    claim(len(ot) == V('outside_treated') and ot.parent_cik.nunique() == V('outside_parents'), 'outside counts')
    claim(V('sic_treated_total') - V('sic_treated_testable') == V('outside_treated'), '118 - 107 = 11')
    n_noticker = int((ot.reason == 'no matched ticker').sum())
    note = (f'Panel A lists the {nb.c("outside_treated", "i")} registrant events, at '
            f'{nb.c("outside_parents", "i")} parent filer entities, that fall outside the industry-code comparison '
            f'in Table 7. The comparison starts from the {nb.c("sic_treated_total", "i")} verified registrant events '
            f'among the canonical events and keeps the {nb.c("sic_treated_testable", "i")} with a Compustat '
            f'historical Standard Industrial Classification (SIC) code. An event goes uncoded when its firm has no '
            f'matched stock ticker ({nb.i(n_noticker, "16, reason == no matched ticker")} events) or when the '
            f'ticker has no Compustat annual record in the {nb.d("550", "scripts/163 sich rule (550-day window)")} '
            f'days before the breach date ({nb.i(len(ot) - n_noticker, "16, other reason")} events); '
            f'{nb.c("outside_tmobile", "i")} of the {nb.c("outside_treated", "i")} are T-Mobile events. Panel B '
            f'compares, for each treated parent filer entity and for Roku, the Compustat historical SIC code with '
            f'the SIC codes attached to the breach records in the source data. The two sources disagree for '
            f'{nb.c("sich_sources_disagree_treated", "i")} of the {nb.c("sich_treated_parents", "i")} treated '
            f'parents. Compustat SIC is the code on the firm’s most recent annual record within '
            f'{nb.d("550", "scripts/163 sich rule")} days before the breach date; Breach-record SIC is every code '
            f'found on the parent’s breach records; an em dash (—) marks a missing code. CIK is the '
            f'Securities and Exchange Commission Central Index Key.')
    return render_table(8, 'Industry-Code Coverage and Source',
                        [('Registrant events outside the industry-code comparison', hdr_a, rows_a),
                         ('Compustat SIC against the breach records’ SIC', hdr_b, rows_b)], note)


RENDERERS.update({6: table_6, 7: table_7, 8: table_8})


# ------------------------------------------------------------------ Set 4 shared
MODEL_VARS = [('fcc_form499', 'Form 499 registrant'), ('pre_sd', 'Pre-window abnormal return volatility'),
              ('delay_w', 'Disclosure gap (days)'), ('firm_size_log', 'Log total assets'),
              ('leverage', 'Leverage'), ('roa', 'Return on assets'), ('health_breach', 'Health-breach flag'),
              ('prior_events', 'Prior breach events'), ('const', 'Intercept')]
SQRT252 = 252 ** 0.5


def cv3_text(nb):
    """The standing CV3 definition, numbers registered."""
    return (f'CV3 is the cluster jackknife standard error, clustered by parent filer entity (G = '
            f'{nb.c("primary_G", "i")} parents, {nb.c("primary_G1", "i")} with registrant events); it '
            f're-estimates the model leaving out one parent at a time, and its p-values use the t distribution '
            f'with G − 1 = {nb.i(V("primary_G") - 1, "constants primary_G - 1")} degrees of freedom (df)')


# ------------------------------------------------------------------ Table 9
def table_9():
    nm = appendix_csv('18_nested_models.csv')
    models = ['M1', 'M2', 'M3', 'M4']
    cell = {(r.model, r.variable): r for _, r in nm.iterrows()}
    rows = []
    for v, lab in MODEL_VARS:
        dp = 5 if v == 'delay_w' else 3
        rows.append([lab] + [f'{fmt_num(cell[(m, v)].coef, dp)}\n({fmt_num(cell[(m, v)].se_cv3, dp)})'
                             if (m, v) in cell else '' for m in models])
        rows.append([' p'] + [fmt_p(cell[(m, v)].p_cv3) if (m, v) in cell else '' for m in models])
    first = {m: nm[nm.model == m].iloc[0] for m in models}
    rows.append(['N'] + [fmt_int(first[m].N) for m in models])
    rows.append(['R²'] + [apa_share(first[m].r2, 3) for m in models])
    rows.append(['Adjusted R²'] + [apa_share(first[m].adj_r2, 3) for m in models])
    hdr = ['Variable', 'M1', 'M2', 'M3', 'M4']
    nb = Notes(9)
    claim(fmt_num(first['M4'].r2, 6) == fmt_num(V('primary_r2_M4'), 6), 'M4 R2 matches constants')
    claim(abs(float(cell[('M4', 'fcc_form499')].coef) - V('primary_coef')) < 1e-9, 'M4 coefficient = primary')
    note = (f'Each column is one ordinary least squares (OLS) regression of the change in abnormal return '
            f'volatility on the analytical sample (N = {nb.c("primary_N", "i")} events, '
            f'{nb.c("primary_treated", "i")} of them Form 499 registrant events). The dependent variable is the '
            f'change in abnormal return volatility: the standard deviation (SD) of daily abnormal returns, '
            f'RET − vwretd, in percentage points, over trading days {nb.d("[+1, +20]", "constants primary_outcome")} '
            f'after the agency reporting date minus the same SD over {nb.d("[−60, −11]", "constants primary_outcome")}. '
            f'M1 regresses it on the pre-window volatility level and the disclosure gap; M2 adds log total assets, '
            f'leverage and return on assets; M3 adds the Form 499 registrant indicator, the test of the first '
            f'hypothesis (H1); M4 adds the health-breach flag and prior breach events and is the primary model. '
            f'Each cell shows the coefficient with its CV3 standard error in parentheses below it and, on the next '
            f'row, its p-value. {cv3_text(nb)}. With the pre-window level on the right-hand side, each model is an '
            f'analysis of covariance: the registrant coefficient compares post-window volatility between groups '
            f'holding the pre-window level fixed. Because the dependent variable is a change that contains the '
            f'pre-window level, R² is not the share of post-disclosure volatility the model explains. In M4 the registrant coefficient is '
            f'{nb.f(cell[("M4", "fcc_form499")].coef, 3, "18, M4 / fcc_form499 / coef")} '
            f'(p = {nb.p(cell[("M4", "fcc_form499")].p_cv3, "18, M4 / fcc_form499 / p_cv3")}), and adding the '
            f'registrant indicator raises R² from {nb.r(V("r2_M4_without_treatment"), 3, "constants values.r2_M4_without_treatment")} '
            f'to {nb.r(V("r2_M4_with_treatment"), 3, "constants values.r2_M4_with_treatment")}. Disclosure-gap '
            f'coefficients are per day and shown to five decimals. RET is the daily stock return and vwretd the '
            f'value-weighted market return, both from the Center for Research in Security Prices (CRSP).')
    return render_table(9, 'Hierarchical Model for H1', [('', hdr, rows)], note)


# ------------------------------------------------------------------ Table 10
def table_10():
    ld = appendix_csv('19_inference_ladder.csv')
    lab = {'OLS (classical)': 'OLS, classical', 'HC1': 'HC1', 'HC3': 'HC3',
           'CV1 parent filer entity': 'CV1, parent filer entity', 'CV3 cluster jackknife (PRIMARY)': 'CV3, parent filer entity (primary)'}
    rows = []
    for _, r in ld.iterrows():
        name = lab.get(r.rung)
        if name is None:
            name = (r.rung.replace('WCR restricted Rademacher', 'Wild cluster, restricted, Rademacher weights')
                    .replace('WCU unrestricted Rademacher', 'Wild cluster, unrestricted, Rademacher weights')
                    .replace('WCR Webb six-point', 'Wild cluster, restricted, Webb weights'))
        ci = fmt_ci(r.ci_lo, r.ci_hi) if str(r.ci_lo).strip() else '—'
        rows.append([name, fmt_num(r.se, 3) if str(r.se).strip() else '—',
                     fmt_int(float(r.df)) if str(r.df).strip() else '—', fmt_p(r.p), ci])
    hdr = ['Procedure', 'SE', 'df', 'p', '95% CI']
    rows_b = [['CV1, two-digit SIC industry', fmt_num(V('sic2_cluster_se_cv1'), 3), fmt_p(V('sic2_cluster_p_cv1'))],
              ['CV3, two-digit SIC industry', fmt_num(V('sic2_cluster_se_cv3'), 3), fmt_p(V('sic2_cluster_p_cv3'))]]
    hdr_b = ['Procedure', 'SE', 'p']
    nb = Notes(10)
    r0 = ld.iloc[0]
    claim(len(set(ld.coef)) == 1, 'one coefficient across the ladder')
    claim(all(float(x) >= .05 for x in ld.p), 'no procedure rejects')
    hc1, cv3 = V('primary_se_hc1'), V('primary_se_cv3')
    note = (f'Each row of Panel A reports a different standard error (SE) and test for the same coefficient, the '
            f'Form 499 registrant coefficient of the primary model M4 '
            f'({nb.f(r0.coef, 3, "19, coef")}; N = {nb.i(r0.N, "19, N")} events, '
            f'{nb.i(r0.n_treated, "19, n_treated")} registrant events). OLS is the classical SE, which assumes '
            f'independent errors of equal variance. HC1 and HC3 allow the error variance to differ across events '
            f'but treat events as independent; HC3 inflates each residual by its leverage. CV1 clusters by parent '
            f'filer entity with the usual small-sample correction. {cv3_text(nb)}; it is the primary procedure. '
            f'The three wild cluster bootstrap rows resample parent-level residuals: the restricted version '
            f'imposes the null hypothesis of a zero coefficient when it builds the bootstrap samples and the '
            f'unrestricted version does not; Rademacher weights flip each parent’s residuals with '
            f'probability one half, and Webb weights draw from six points, which suits few clusters. The '
            f'Rademacher rows use {nb.d("99,999", "19, rung labels (B)")} draws and the Webb row '
            f'{nb.d("9,999", "19, rung labels (B)")}, with seed {nb.d("499", "scripts/263 SEED")}. Procedures '
            f'that ignore clustering understate the SE when treatment varies across few parents, because events '
            f'at the same parent share shocks: the HC1 SE ({nb.f(hc1, 3, "constants primary_se_hc1")}) is '
            f'{nb.f(100 * (1 - hc1 / cv3), 0, "constants 1 - primary_se_hc1 / primary_se_cv3 (x 100)")} percent '
            f'smaller than the CV3 SE ({nb.f(cv3, 3, "constants primary_se_cv3")}). G is the number of parent '
            f'filer entities ({nb.c("primary_G", "i")}), G1 the number with registrant events '
            f'({nb.c("primary_G1", "i")}), and G* the effective number of clusters (Carter et al., 2017), '
            f'{nb.c("primary_G_star", "f", 1)}, which adjusts G for unequal cluster sizes and the concentration of '
            f'treatment; the coefficient of variation of cluster size is {nb.c("cluster_size_cv_ddof0", "f", 2)}. '
            f'No procedure gives p below .05. A 95 percent confidence interval (CI) is shown where the procedure '
            f'produces one; an em dash (—) marks none. Panel B clusters instead by two-digit Standard '
            f'Industrial Classification (SIC) industry, with {nb.c("sic2_clusters", "i")} clusters.')
    return render_table(10, 'Inference for the Registrant Coefficient',
                        [('Inference ladder, clustering by parent filer entity', hdr, rows),
                         ('Clustering by industry', hdr_b, rows_b)], note)


# ------------------------------------------------------------------ Table 11
def table_11():
    dr = appendix_csv('20_design_resolution.csv').iloc[0]
    mult = V('dr_mde80_daily') / V('primary_se_cv3')
    rows_a = [['Smallest effect size of interest (SESOI)', fmt_num(dr.sesoi_daily, 3), fmt_num(dr.sesoi_ann, 2)],
              ['Equivalence bound from the announcement-return literature', fmt_num(V('sesoi_car_daily'), 3),
               fmt_num(V('sesoi_car_ann'), 2)],
              ['Minimum detectable effect, CV3 (MDE80)', fmt_num(dr.mde80_daily, 3), fmt_num(dr.mde80_ann, 2)],
              ['Minimum detectable effect, HC3', fmt_num(V('mde80_hc3_daily'), 3), fmt_num(V('mde80_hc3_ann'), 2)],
              ['MDE80 floor as treated parents grow without limit', fmt_num(dr.floor_daily, 3), fmt_num(dr.floor_ann, 2)]]
    hdr_a = ['Quantity', 'Daily, pp', 'Annualized, pp']
    rows_b = [['Registrant coefficient (CV3)', fmt_num(V('primary_coef'), 3)],
              ['90% confidence interval', fmt_ci(dr.ci90_lo, dr.ci90_hi)],
              ['90% interval inside ±SESOI', 'Yes' if dr.ci90_inside_sesoi == 'True' else 'No'],
              ['TOST p, lower test (effect below −SESOI)', fmt_p(dr.tost_p_lower)],
              ['TOST p, upper test (effect above +SESOI)', fmt_p(dr.tost_p_upper)],
              ['TOST p against the literature bound', fmt_p(V('tost_car_p'))],
              ['MDE80 as a multiple of SESOI', fmt_num(dr.mde_over_sesoi, 2)],
              ['Treated parents needed for MDE80 of 5 pp annualized', fmt_int(dr.required_parents_5pp_ann)],
              ['Share of events that are registrant events', fmt_num(dr.share_treated, 3)]]
    hdr_b = ['Quantity', 'Value']
    nb = Notes(11)
    claim(dr.ci90_inside_sesoi == 'False', '90% CI not inside SESOI')
    claim(float(dr.tost_p_lower) < .05 <= float(dr.tost_p_upper), 'lower bound ruled out, upper not')
    claim(abs(V('sesoi_car_daily') * SQRT252 - V('sesoi_car_ann')) < 1e-9, 'CAR bound conversion')
    note = (f'The table asks whether the primary estimate (M4, N = {nb.c("primary_N", "i")}, G = '
            f'{nb.c("primary_G", "i")} parent filer entities, {nb.c("primary_G1", "i")} with registrant events) '
            f'is precise enough to rule out effects that matter. Daily values are in percentage points (pp) of '
            f'daily abnormal return volatility; annualized values multiply them by √{nb.d("252", "scripts/263 (trading days per year)")}. '
            f'The smallest effect size of interest (SESOI) is {nb.d("0.25", "scripts/263 design_resolution sesoi_mult")} '
            f'times the standard deviation of the dependent variable among other events '
            f'({nb.f(dr.sd_control, 3, "20, sd_control")}), or {nb.f(dr.sesoi_daily, 3, "20, sesoi_daily")} pp '
            f'daily and {nb.f(dr.sesoi_ann, 2, "20, sesoi_ann")} pp annualized; it rests on the outcome’s own '
            f'spread because no commensurable effect size exists in the literature for volatility. TOST (two one-'
            f'sided tests) asks whether the effect is small enough to treat as practically zero: it runs one test '
            f'that the effect is above −SESOI and one that it is below +SESOI, using the CV3 standard error and '
            f'the t distribution with {nb.i(V("primary_G") - 1, "constants primary_G - 1")} degrees of freedom '
            f'(df), and the TOST p is the larger of the two. The lower test rejects '
            f'(p = {nb.p(dr.tost_p_lower, "20, tost_p_lower")}), so effects below −SESOI are ruled out; the '
            f'upper test does not (p = {nb.p(dr.tost_p_upper, "20, tost_p_upper")}), so a positive effect as large '
            f'as SESOI cannot be excluded and the TOST p is {nb.p(dr.tost_p_upper, "20, tost_p_upper")}. The '
            f'literature bound is the Essay 1 equivalence bound of ±{nb.f(V("sesoi_car_ann"), 2, "constants sesoi_car_ann")} '
            f'pp, whose size matches the two-day breach penalty reported by Cavusoglu et al. (2004), divided by '
            f'√252 to a daily {nb.f(V("sesoi_car_daily"), 3, "constants sesoi_car_daily")} pp; its TOST p is '
            f'{nb.p(V("tost_car_p"), "constants tost_car_p")}. The 90 percent confidence interval, '
            f'[{nb.f(dr.ci90_lo, 3, "20, ci90_lo")}, {nb.f(dr.ci90_hi, 3, "20, ci90_hi")}], is '
            f'the interval that matches TOST at the 5 percent level, because each one-sided test uses 5 percent; it '
            f'is not inside ±SESOI. MDE80 is the minimum detectable effect, the smallest true effect the '
            f'regression would detect four times in five at the 5 percent level, computed as '
            f'(t.975 + t.80, df {nb.i(V("primary_G") - 1, "constants primary_G - 1")}) × SE_CV3 = '
            f'{nb.f(mult, 2, "constants dr_mde80_daily / primary_se_cv3")} × SE_CV3; it is '
            f'{nb.f(dr.mde_over_sesoi, 2, "20, mde_over_sesoi")} times SESOI. The HC3 row shows the MDE80 that '
            f'heteroskedasticity-consistent (HC3) standard errors would imply, '
            f'{nb.c("mde80_hc3_pct_below_cv3", "f", 0)} percent below the CV3 value. Reaching an MDE80 of '
            f'{nb.d("5", "scripts/263 design_resolution target_ann")} pp annualized would take '
            f'{nb.i(dr.required_parents_5pp_ann, "20, required_parents_5pp_ann")} treated parents, holding the other '
            f'parents and the variance structure fixed; as treated parents grow without limit the MDE80 falls only '
            f'to a floor of {nb.f(dr.floor_daily, 3, "20, floor_daily")} pp daily '
            f'({nb.f(dr.floor_ann, 2, "20, floor_ann")} pp annualized), set by the other parents. CV3 is the cluster '
            f'jackknife standard error by parent filer entity.')
    return render_table(11, 'Design Resolution: Equivalence and Power',
                        [('Thresholds', hdr_a, rows_a), ('Tests and design', hdr_b, rows_b)], note)


RENDERERS.update({9: table_9, 10: table_10, 11: table_11})


def win(w):
    """'[+1,+20]' -> '[+1, +20]' with true minus signs."""
    return minus_all(str(w).replace(',', ', ').replace(',  ', ', '))


def minus_all(t):
    return re.sub(r'(?<![\w])-(?=\d)', MINUS, t)


def est(r, se_col='se_cv3'):
    return f'{fmt_num(r.coef, 3)} ({fmt_num(r[se_col], 3)})'


# ------------------------------------------------------------------ Table 12
def table_12():
    dp_ = appendix_csv('21_dynamic_path.csv')
    rows_a = [[win(r.post_window), est(r), fmt_p(r.p_cv3), fmt_p(r.bh_adj_p), fmt_p(r.p_wcr), fmt_ci(r.ci3_lo, r.ci3_hi)]
              for _, r in dp_.iterrows()]
    hdr_a = ['Post-window', 'Estimate (CV3 SE)', 'p', 'BH-adjusted p', 'Wild cluster p', '95% CI']

    bm = appendix_csv('22A_benchmarks.csv')
    blab = {'mkt_adj': 'Market-adjusted', 'mm': 'Market model', 'ff3': 'Fama–French three-factor'}
    rows_b = [[blab[r.benchmark], win(r.post_window), est(r), fmt_p(r.p_cv3), fmt_int(r.N),
               fmt_ci(r.ci3_lo, r.ci3_hi)] for _, r in bm.iterrows()]
    hdr_b = ['Benchmark', 'Post-window', 'Estimate (CV3 SE)', 'p', 'N', '95% CI']

    ct = appendix_csv('22B_estimation_contamination.csv')
    glab = {'treated': 'Form 499 registrant events', 'control': 'Other events', 'all': 'All events'}
    rows_c = []
    for g in ['treated', 'control', 'all']:
        a_ = ct[(ct.group == g) & (ct.definition == 'est_contaminated_by_notification')].iloc[0]
        b_ = ct[(ct.group == g) & (ct.definition == 'est_contaminated_by_breach_date')].iloc[0]
        rows_c.append([glab[g], fmt_int(a_.events), fmt_int(a_.contaminated), apa_share(a_.share, 2),
                       fmt_int(b_.contaminated), apa_share(b_.share, 2)])
    hdr_c = ['Group', 'Events', 'Earlier notification in window', 'Share', 'Earlier breach date in window', 'Share']

    cv = appendix_csv('22C_coverage_drops.csv')
    cv['spec'] = cv.window.str.extract(r', ([^,]+)$')[0].str.strip()
    cv['pre'] = cv.window.str.extract(r'pre (\[[^\]]+\])')[0]
    slab = {'market-adjusted': 'Market-adjusted', 'mm': 'Market model', 'ff3': 'Fama–French three-factor'}
    rows_d = []
    for (pre, spec), g in cv[~cv.window.str.startswith('PRIMARY')].groupby(['pre', 'spec'], sort=False):
        cols = ['dropped', 'dropped_treated', 'dropped_control', 'surviving', 'surviving_G']
        if len(g[cols].drop_duplicates()) != 1:
            sys.exit(f'Table 12 Panel D: drops differ across post-windows for {pre} {spec}')
        r = g.iloc[0]
        rows_d.append([f'{slab[spec]}, pre-window {win(pre)}', fmt_int(r.dropped), fmt_int(r.dropped_treated),
                       fmt_int(r.dropped_control), fmt_int(r.surviving), fmt_int(r.surviving_G)])
    hdr_d = ['Benchmark and pre-window (all three post-windows)', 'Dropped', 'Registrant dropped', 'Other dropped',
             'Events kept', 'Parents kept (G)']

    alt = appendix_csv('23_alternatives_bridge.csv')
    alab = []
    for r in alt.row:
        if r.startswith('ALT'):
            w_ = re.search(r'pre (\[[^\]]+\]) / post (\[[^\]]+\])', r)
            alab.append(f'Pre-window {win(w_.group(1))}, post-window {win(w_.group(2))}, market-adjusted')
        elif r.startswith('BRIDGE a'):
            alab.append('Bridge a: raw log returns, [−25, −5] / [+5, +25], committed earlier outcome')
        elif r.startswith('BRIDGE b'):
            alab.append('Bridge b: raw log returns, [−25, −5] / [+5, +25], current calendar and 80% rule')
        elif r.startswith('BRIDGE c'):
            alab.append('Bridge c: market-adjusted simple returns, [−25, −5] / [+5, +25]')
        else:
            alab.append('Bridge d (primary): market-adjusted simple returns, [−60, −11] / [+1, +20]')
    rows_e = [[lab_, est(r), fmt_p(r.p_cv3), fmt_ci(r.ci3_lo, r.ci3_hi)] for lab_, (_, r) in zip(alab, alt.iterrows())]
    hdr_e = ['Specification', 'Estimate (CV3 SE)', 'p', '95% CI']

    nb = Notes(12)
    claim(all(float(x) >= .05 for x in list(dp_.p_cv3) + list(bm.p_cv3) + list(alt.p_cv3)), 'nothing rejects')
    mm = cv[cv.spec == 'mm'].iloc[0]
    from collections import Counter as _C
    dropped_orgs = _C(x.split(':')[0].rsplit(' ', 1)[0] for x in mm.reasons.split('; '))
    claim(sum(dropped_orgs.values()) == int(mm.dropped), 'coverage reasons list every dropped event')
    org_list = '; '.join(f'{o} ({nb.i(k, "22C, mm / reasons, events of " + o)})'
                         for o, k in sorted(dropped_orgs.items(), key=lambda kv: (-kv[1], kv[0])))
    allc = ct[ct.group == 'all']
    note = (f'Each row re-estimates the primary model M4 with one change and reports the Form 499 registrant '
            f'coefficient, its CV3 standard error (SE) in parentheses, its p-value and its 95 percent confidence '
            f'interval (CI); the analytical sample has N = {nb.c("primary_N", "i")} events and G = '
            f'{nb.c("primary_G", "i")} parent filer entities ({nb.c("primary_G1", "i")} with registrant events) '
            f'unless the N column shows otherwise. CV3 is the cluster jackknife standard error, clustered by parent '
            f'filer entity, with p-values from the t distribution with G − 1 degrees of freedom. Panel A varies '
            f'the post-window, the trading days after the agency reporting date over which volatility is measured, '
            f'from {nb.d("[+1, +5]", "21, post_window")} to {nb.d("[+1, +20]", "21, post_window")}, against the '
            f'pre-window {nb.d("[−60, −11]", "constants primary_outcome")}. The three windows form one '
            f'family of {nb.i(len(dp_), "21, rows (family size)")} tests, and the BH-adjusted p applies the '
            f'Benjamini–Hochberg false-discovery-rate adjustment within that family; the wild cluster p comes '
            f'from the restricted wild cluster bootstrap with Rademacher weights. Every window must have at least '
            f'{nb.d("80", "scripts/264 (coverage rule)")} percent of its trading days with returns, the 80 percent '
            f'coverage rule. Panel B replaces the market adjustment (RET − vwretd, the stock return minus the '
            f'value-weighted market return) with abnormal returns from the market model and from the Fama–French '
            f'three-factor (FF3) model, both estimated over trading days {nb.d("[−250, −30]", "22C reasons / scripts/263 EST_WIN")}; '
            f'{nb.i(mm.dropped, "22C, mm rows / dropped")} events '
            f'({nb.i(mm.dropped_treated, "22C, mm rows / dropped_treated")} registrant event) drop because their '
            f'estimation window has less than 80 percent coverage, by organization {org_list}, which leaves '
            f'{nb.i(mm.surviving, "22C, mm / surviving")} events and {nb.i(mm.surviving_G, "22C, mm / surviving_G")} '
            f'parents. Panel C counts contaminated estimation windows: an estimation window is contaminated when '
            f'another event at the same parent filer entity falls inside it, counted once by that event’s '
            f'notification date and once by its breach date. The counts exclude the focal event itself and events '
            f'in its own Gate 2 chain, after the correction of {nb.d("November 13, 2026", "scripts/264 contamination comment (fixed 2026-11-13)")} that stopped an event’s own '
            f'breach date counting against it; across all events the shares are '
            f'{nb.r(allc[allc.definition == "est_contaminated_by_notification"].share.iloc[0], 2, "22B, all / notification / share")} '
            f'by notification date and {nb.r(allc[allc.definition == "est_contaminated_by_breach_date"].share.iloc[0], 2, "22B, all / breach date / share")} '
            f'by breach date. Panel D lists the coverage-rule drops for each benchmark and pre-window; the primary '
            f'market-adjusted windows drop no event. Panel E builds the outcome step by step from the earlier '
            f'construction to the current one: bridge a is the committed earlier outcome, the change in the SD of '
            f'raw log returns between {nb.d("[−25, −5]", "23, bridge rows")} and '
            f'{nb.d("[+5, +25]", "23, bridge rows")}; bridge b recomputes it on the current trading calendar with '
            f'the 80 percent rule; bridge c switches to market-adjusted simple returns on the same windows; bridge d '
            f'moves to the current windows and is the primary estimate. The first rows of Panel E start the '
            f'pre-window at day {nb.d("−45", "23, ALT rows")} instead of {nb.d("−60", "constants primary_outcome")}. '
            f'No row gives p below .05. SD is the standard deviation; RET and vwretd are from the Center for Research '
            f'in Security Prices (CRSP).')
    return render_table(12, 'Robustness of the Main Estimate',
                        [('Post-window length', hdr_a, rows_a), ('Return benchmark', hdr_b, rows_b),
                         ('Estimation-window contamination', hdr_c, rows_c),
                         ('Events dropped by the 80% coverage rule', hdr_d, rows_d),
                         ('Alternative pre-window and the bridge from the earlier outcome', hdr_e, rows_e)], note)


RENDERERS.update({12: table_12})


def ladder_rows(ld):
    lab = {'OLS (classical)': 'OLS, classical', 'HC1': 'HC1', 'HC3': 'HC3',
           'CV1 parent filer entity': 'CV1, parent filer entity',
           'CV3 cluster jackknife (PRIMARY)': 'CV3, parent filer entity (primary)'}
    rows = []
    for _, r in ld.iterrows():
        name = lab.get(r.rung) or (r.rung.replace('WCR restricted Rademacher', 'Wild cluster, restricted, Rademacher weights')
                                   .replace('WCU unrestricted Rademacher', 'Wild cluster, unrestricted, Rademacher weights')
                                   .replace('WCR Webb six-point', 'Wild cluster, restricted, Webb weights'))
        rows.append([name, fmt_num(r.se, 3) if str(r.se).strip() else '—',
                     fmt_int(float(r.df)) if str(r.df).strip() else '—', fmt_p(r.p),
                     fmt_ci(r.ci_lo, r.ci_hi) if str(r.ci_lo).strip() else '—'])
    return ['Procedure', 'SE', 'df', 'p', '95% CI'], rows


# ------------------------------------------------------------------ Table 13
def table_13():
    fam = appendix_csv('24A_announcement_family.csv')
    tlab = {'earnings elevation (mean)': 'Elevation on earnings dates (mean)',
            'breach elevation (mean)': 'Elevation on breach reporting dates (mean)',
            'breach minus earnings (contrast)': 'Breach minus earnings (contrast)',
            'Form 499 on breach elevation (pre-specified)': 'Form 499 registrant on breach elevation (pre-specified)'}
    rows_a = []
    for _, r in fam.iterrows():
        lab_ = tlab.get(r.test, 'Bridge: registrant on elevation, committed market-model definition')
        rows_a.append([lab_, f'{fmt_num(r.coef, 3)} ({fmt_num(r.se, 3)})', fmt_p(r.p),
                       fmt_p(r.bh_adj_p) if str(r.bh_adj_p).strip() else '—', fmt_int(r.N), fmt_int(r.clusters),
                       r.inference.replace('CV1 by security', 'CV1, security').replace('CV1 by parent filer entity', 'CV1, parent')
                       .replace('CV3 by parent filer entity', 'CV3, parent').replace('CV3', 'CV3, parent') if r.inference != 'CV3' else 'CV3, parent'])
    rows_a = [[*r_[:6], r_[6].replace('CV3, parent, parent', 'CV3, parent')] for r_ in rows_a]
    hdr_a = ['Test', 'Estimate (SE)', 'p', 'BH-adjusted p', 'N', 'Clusters', 'SE']

    hdr_b, rows_b = ladder_rows(appendix_csv('24B_announcement_ladder.csv'))

    bu = appendix_csv('24C_announcement_buildup.csv')
    blab = {'unadjusted (Form 499 only)': 'Registrant indicator only',
            '+ baseline SD': '+ baseline-window SD', '+ baseline SD + ln assets': '+ baseline-window SD and log total assets',
            'full (pre-specified)': 'All controls (pre-specified)'}
    rows_c = [[blab[r.step], f'{fmt_num(r.coef, 3)} ({fmt_num(r.se_cv3, 3)})', fmt_p(r.p_cv3), apa_share(r.share_of_movement, 2)]
              for _, r in bu.iterrows()]
    hdr_c = ['Controls', 'Estimate (CV3 SE)', 'p', 'Share of the movement']

    pl = appendix_csv('24D_placebo_dates.csv')
    olab = {'primary DV': 'Change in abnormal return volatility (primary)', 'announcement elevation': 'Announcement elevation'}
    rows_d = [[olab[r.outcome], fmt_num(r.actual, 3), f'{fmt_num(r.placebo_mean, 3)} ({fmt_num(r.placebo_sd, 3)})',
               fmt_int(r.draws_abs_ge_actual), fmt_int(r.draws_cv3_p_lt_05), fmt_int(r.draws)] for _, r in pl.iterrows()]
    hdr_d = ['Outcome', 'Actual estimate', 'Placebo mean (SD)', 'Draws at least as large', 'Draws with p < .05', 'Draws']

    eb = appendix_csv('24E_earnings_benchmark.csv')
    elab = {'primary DV on earnings dates': 'Change in volatility, earnings dates',
            'elevation on earnings dates': 'Elevation, earnings dates',
            'primary DV on breach dates (sample mean)': 'Change in volatility, breach reporting dates (sample mean)'}
    rows_e = [[elab[r.outcome], f'{fmt_num(r["mean"], 3)}' + (f' ({fmt_num(r.se, 3)})' if str(r.se).strip() else ''),
               fmt_p(r.p) if str(r.p).strip() else '—', fmt_int(r.N_announcements), fmt_int(r.securities)]
              for _, r in eb.iterrows()]
    hdr_e = ['Outcome', 'Mean (SE)', 'p', 'Dates', 'Securities']

    lo = appendix_csv('24F_announcement_lotpo.csv')
    rows_f = [[r.deleted_parent, f'{fmt_int(r.deleted_events)} ({fmt_int(r.deleted_treated_events)})',
               f'{fmt_num(r.coef, 3)} ({fmt_num(r.se_cv3, 3)})', fmt_p(r.p_cv3), fmt_int(r.N)] for _, r in lo.iterrows()]
    hdr_f = ['Treated parent removed', 'Events removed (registrant)', 'Estimate (CV3 SE)', 'p', 'N']

    se_ = pd.read_csv(V5 / 'v5_t18b_announcement_sensitivities.csv', dtype=str, keep_default_na=False)
    slab = {'base (scripts/265)': 'Pre-specified model',
            '+ severity (ln records + vector FE)': '+ breach severity (log records and attack-vector fixed effects)',
            '+ flexible size (quartile FE + size^2)': '+ flexible size (size-quartile fixed effects and size squared)',
            '+ severity and flexible size': '+ severity and flexible size',
            'common support (controls in treated size range)': 'Common support (other events within the registrant size range)'}
    rows_g = [[slab[r.spec], f'{fmt_num(r.coef, 3)} ({fmt_num(r.se_cv3, 3)})', fmt_p(r.p_cv3), fmt_p(r.p_cv1), fmt_int(r.N)]
              for _, r in se_.iterrows()]
    hdr_g = ['Specification', 'Estimate (CV3 SE)', 'p', 'CV1 p', 'N']

    nb = Notes(13)
    f4 = fam.iloc[3]
    lad = appendix_csv('24B_announcement_ladder.csv')
    wcu = lad[lad.rung.str.startswith('WCU')].iloc[0]
    claim(float(f4.p) < .05 and float(f4.bh_adj_p) < .05, 'the registrant test rejects after BH')
    claim(float(wcu.p) >= .05 and all(float(x) < .05 for x in lad[~lad.rung.str.startswith('WCU')].p), 'only WCU does not reject')
    nrej = int((lo.rejects_05_cv3 == 'True').sum())
    claim(len(lo) - nrej == V('ann_lotpo_n_not_rejecting'), 'LOTPO non-rejections match constants')
    notrej = lo[lo.rejects_05_cv3 != 'True'].iloc[0]
    claim(all(float(x) < .05 for x in se_.p_cv3), 'every sensitivity rejects under CV3')
    note = (f'Each estimate in Panels A, B, C, F and G is the coefficient on the Form 499 registrant indicator in a '
            f'regression of announcement elevation on registration, the baseline-window volatility and the M4 '
            f'controls, on the analytical sample (N = {nb.c("ann_N", "i")}, G = {nb.c("ann_G", "i")} parent filer '
            f'entities, {nb.c("ann_G1", "i")} with registrant events) unless a row shows otherwise. Announcement '
            f'elevation is the standard deviation (SD) of daily market-adjusted abnormal returns, RET − vwretd, '
            f'over the nine trading days {nb.d("[−4, +4]", "scripts/265 ANN")} centered on the agency reporting '
            f'date (day 0) minus the same SD over the three weeks before, trading days '
            f'{nb.d("[−25, −5]", "scripts/265 BASE")}; each window must have returns on '
            f'{nb.d("8", "scripts/265 header (80% rule)")} of {nb.d("9", "scripts/265 header")} and '
            f'{nb.d("17", "scripts/265 header")} of {nb.d("21", "scripts/265 header")} days. Panel A is the '
            f'pre-specified family of {nb.i(load_constants()["bh_families"]["announcement_window"], "constants bh_families.announcement_window")} '
            f'tests: mean elevation on the sample securities’ earnings-announcement dates, mean elevation on breach '
            f'reporting dates, their contrast, and the registrant coefficient. The BH-adjusted p applies the '
            f'Benjamini–Hochberg false-discovery-rate adjustment within that family. The registrant coefficient '
            f'is {nb.f(f4.coef, 3, "24A, Form 499 row / coef")} (CV3 p = {nb.p(f4.p, "24A, Form 499 row / p")}, '
            f'BH-adjusted p = {nb.p(f4.bh_adj_p, "24A, Form 499 row / bh_adj_p")}), and it clears .05 after the '
            f'adjustment; the bridge row gives the registrant coefficient under the committed market-model definition of elevation. CV3 is the '
            f'cluster jackknife standard error (SE) by parent filer entity, with t distribution p-values on G − 1 '
            f'degrees of freedom; CV1 is the cluster-robust SE with the usual small-sample correction. Panel B repeats '
            f'the registrant test under each inference procedure, defined as in Table 10; every procedure gives p '
            f'below .05 except the unrestricted wild cluster bootstrap (p = {nb.p(wcu.p, "24B, WCU / p")}). Panel C '
            f'adds controls in steps; Share of the movement is how far each step moves the coefficient from the '
            f'registrant-only value toward the full-model value, as a share of the whole distance: the baseline-window '
            f'SD closes {nb.c("ann_share_closed_base", "r", 2)} of it and log total assets brings the total to '
            f'{nb.c("ann_share_closed_base_size", "r", 2)}. Panel D is the placebo test: in each of '
            f'{nb.i(pl.draws.iloc[0], "24D, draws")} draws (seed {nb.d("499", "scripts/263 SEED")}), every '
            f'security in the sample gets a random date that lies at least {nb.d("120", "scripts/265 header (eligibility)")} '
            f'trading days from any of its breach notifications and at least {nb.d("30", "scripts/265 header")} from '
            f'any of its earnings dates, and the regression is re-estimated on those quiet days; the columns count the '
            f'draws whose coefficient is at least as large in absolute value as the actual one and the draws with CV3 '
            f'p below .05. No placebo draw matches the actual elevation coefficient '
            f'({nb.i(pl.draws_abs_ge_actual.iloc[1], "24D, elevation / draws_abs_ge_actual")} of '
            f'{nb.i(pl.draws.iloc[1], "24D, draws")}). Compared with their own quiet days, registrant events show '
            f'elevation {nb.c("ann_treated_minus_quiet", "f", 3)} higher on breach reporting dates and other events '
            f'{nb.c("ann_control_minus_quiet", "f", 3)}, so the registrant difference comes from other events’ '
            f'volatility falling below its quiet-day level. Panel E is the earnings-announcement benchmark: the mean '
            f'of each outcome over the sample securities’ quarterly earnings dates, with SEs clustered by '
            f'security. Panel F removes one treated parent filer entity at a time; the CV3 p-value stays below .05 for '
            f'{nb.i(nrej, "24F, rejects_05_cv3 == True")} of {nb.i(len(lo), "24F, rows")} removals and not when '
            f'{nb.reg(notrej.deleted_parent, "24F, the non-rejecting row", notrej.deleted_parent)} is removed '
            f'(p = {nb.p(notrej.p_cv3, "24F, that row / p_cv3")}). Panel G adds the four sensitivities to the '
            f'pre-specified model: breach severity, flexible size, both, and a common-support sample; each keeps CV3 p '
            f'below .05. RET is the daily stock return and vwretd the value-weighted market return, both from the '
            f'Center for Research in Security Prices (CRSP); OLS is ordinary least squares.')
    return render_table(13, 'Volatility Around the Agency Reporting Date',
                        [('The pre-specified family of four tests', hdr_a, rows_a),
                         ('Inference for the registrant coefficient', hdr_b, rows_b),
                         ('Adding controls in steps', hdr_c, rows_c),
                         ('Placebo dates', hdr_d, rows_d),
                         ('Earnings-announcement benchmark', hdr_e, rows_e),
                         ('Leaving out one treated parent filer entity', hdr_f, rows_f),
                         ('Sensitivities', hdr_g, rows_g)], note)


RENDERERS.update({13: table_13})


# ------------------------------------------------------------------ Table 14
DELAY_OUT = {'delay (raw days)': 'Delay, days (uncapped)', 'delay (winsorized p99)': 'Delay, days (capped at P99)',
             'log(1+delay)': 'Log(1 + delay)', 'log(delay)': 'Log(delay)'}
CTRL_LAB = {'BRIDGE old control': 'Earlier controls', 'v5 control': 'Current controls'}


def _ctrl(c):
    return CTRL_LAB['BRIDGE old control' if c.startswith('BRIDGE') else 'v5 control']


def table_14():
    dl = appendix_csv('25A_disclosure_delay.csv')
    rows_a = []
    for (o, c), g in dl.groupby(['outcome', 'control'], sort=False):
        cv3 = g[g.rung.str.startswith('CV3')].iloc[0]
        cv1 = g[g.rung.str.startswith('CV1')].iloc[0]
        wcr = g[g.rung.str.startswith('WCR restricted')].iloc[0]
        dp = 3 if o.startswith('log') else 2
        rows_a.append([DELAY_OUT[o], _ctrl(c), f'{fmt_num(cv3.coef, dp)} ({fmt_num(cv3.se, dp)})', fmt_p(cv3.p),
                       fmt_p(cv1.p), fmt_p(wcr.p), fmt_num(cv3.mde80_cv3, dp)])
    hdr_a = ['Outcome', 'Controls', 'Estimate (CV3 SE)', 'p', 'CV1 p', 'Wild cluster p', 'MDE80']

    nz = appendix_csv('25B_delay_nonzero.csv')
    rows_b = [[DELAY_OUT[r.outcome], _ctrl(r.control), f'{fmt_num(r.coef, 3 if "log" in r.outcome else 2)} '
               f'({fmt_num(r.se_cv3, 3 if "log" in r.outcome else 2)})', fmt_p(r.p_cv3), fmt_p(r.p_cv1),
               f'{fmt_int(r.N)} ({fmt_int(r.n_treated)})'] for _, r in nz.iterrows()]
    hdr_b = ['Outcome', 'Controls', 'Estimate (CV3 SE)', 'p', 'CV1 p', 'N (registrant)']

    qt = appendix_csv('25C_delay_quantiles.csv')
    rows_c = []
    for q in sorted(set(qt.q), key=float):
        a_ = qt[(qt.q == q) & (qt.control == 'v5 control')].iloc[0]
        b_ = qt[(qt.q == q) & (qt.control != 'v5 control')].iloc[0]
        rows_c.append([f'{int(round(float(q) * 100))}th percentile', f'{fmt_num(a_.coef, 2)} ({fmt_num(a_.se, 2)})',
                       fmt_p(a_.p), f'{fmt_num(b_.coef, 2)} ({fmt_num(b_.se, 2)})', fmt_p(b_.p)])
    hdr_c = ['Quantile', 'Current controls: estimate (SE)', 'p', 'Earlier controls: estimate (SE)', 'p']

    ds = appendix_csv('25D_delay_distribution.csv').set_index('group')
    glab = {'treated': 'Form 499 registrant events', 'control': 'Other events'}
    rows_d = [[glab[g], fmt_int(ds.loc[g, 'n']), fmt_int(ds.loc[g, 'zeros']), fmt_num(ds.loc[g, 'p50'], 0),
               fmt_num(ds.loc[g, 'p90'], 0), fmt_num(ds.loc[g, 'max'], 0),
               f'{fmt_num(ds.loc[g, "mean"], 1)} ({fmt_num(ds.loc[g, "sd"], 1)})'] for g in ['treated', 'control']]
    hdr_d = ['Group', 'Events', 'Zero delays', 'Median', '90th percentile', 'Maximum', 'M (SD)']

    te = appendix_csv('25E_delay_distribution_tests.csv')
    tlab = {'Brown-Forsythe, all delays': 'Brown–Forsythe test of equal spread, all delays',
            'Brown-Forsythe, non-zero': 'Brown–Forsythe test of equal spread, nonzero delays',
            'KS, non-zero': 'Kolmogorov–Smirnov test of equal distributions, nonzero delays',
            'log-rank, non-zero': 'Log-rank test of equal timing, nonzero delays'}
    rows_e = [[tlab[r.test], fmt_num(r.stat, 3), fmt_p(r.p),
               fmt_num(r.sd_treated, 1) if str(r.sd_treated).strip() else '—',
               fmt_num(r.sd_control, 1) if str(r.sd_control).strip() else '—']
              for _, r in te.iterrows() if r.test in tlab]
    hdr_e = ['Test', 'Statistic', 'p', 'SD, registrant', 'SD, other']

    nb = Notes(14)
    zr = te[te.test == 'zero-delay events'].iloc[0]
    claim(int(float(zr.stat)) == V('delay_zero_events') and int(float(zr.sd_treated)) == V('delay_zero_treated')
          and int(float(zr.sd_control)) == V('delay_zero_control'), 'zero-delay counts match constants')
    claim(all(float(x) >= .05 for x in list(dl[dl.rung.str.startswith('CV3')].p) + list(nz.p_cv3)), 'no delay test rejects')
    claim(all(float(x) >= .05 for x in te.p if str(x).strip()), 'no distribution test rejects')
    claim(float(ds.loc['treated', 'p25']) == 0 and float(ds.loc['control', 'p25']) == 0, 'both 25th percentiles are zero')
    cap = appendix_csv('02A_descriptives_v5.csv')
    capv = cap[(cap.group == 'full') & (cap.variable == 'delay_w')]['max'].iloc[0]
    note = (f'Each row of Panel A regresses a delay outcome on the Form 499 registrant indicator and controls in the '
            f'analytical sample (N = {nb.c("primary_N", "i")}, G = {nb.c("primary_G", "i")} parent filer entities, '
            f'{nb.c("primary_G1", "i")} with registrant events). Delay is the number of days from the breach date to '
            f'the agency reporting date. Delays of {nb.d("−30", "scripts/156")} to {nb.d("−1", "scripts/156")} '
            f'days, where the reporting date precedes the breach date by a field-level error, are set to 0. '
            f'In all, {nb.c("delay_zero_events", "i")} events have a zero delay ({nb.c("delay_zero_treated", "i")} registrant, '
            f'{nb.c("delay_zero_control", "i")} other), because the source records the breach and its report on the '
            f'same day or because a small negative delay was set to 0. The uncapped rows use the delay as recorded; '
            f'the capped rows cap it at the in-sample {nb.d("99th", "scripts/163 (P99 winsorization rule)")} percentile (P99), {nb.f(capv, 2, "02A, full / delay_w / max")} '
            f'days, the disclosure gap of Table 2. The unadjusted difference in mean uncapped delay is '
            f'{nb.c("delay_raw_unadjusted_diff", "f", 1)} days, while Table 2 reports the capped gap of '
            f'{nb.f(appendix_csv("02B_descriptives_v5_differences.csv").set_index("variable").loc["delay_w", "diff"], 2, "02B, delay_w / diff")} '
            f'days. The log rows use log(1 + delay) in Panel A and log(delay) on nonzero delays in Panel B. Current '
            f'controls are the M4 controls with the pre-window volatility of the current outcome; earlier controls use '
            f'the pre-window volatility of the earlier raw-return outcome. CV3 is the cluster jackknife standard error '
            f'(SE) by parent filer entity, with p-values from the t distribution with G − 1 degrees of freedom; '
            f'CV1 is the cluster-robust SE with the usual small-sample correction; the wild cluster p comes from the '
            f'restricted wild cluster bootstrap with Rademacher weights. MDE80 is the minimum detectable effect at 80 '
            f'percent power, (t.975 + t.80) × SE_CV3, in the units of the outcome. No row gives p below .05. Panel B '
            f'drops the zero delays ({nb.i(nz.N.iloc[0], "25B, N")} events, {nb.i(nz.n_treated.iloc[0], "25B, n_treated")} '
            f'registrant). Panel C reports quantile regressions of the uncapped delay at five quantiles with SEs in '
            f'parentheses. Below the median the estimates carry no information: more than a quarter of the delays in '
            f'each group are zero, so both groups’ {nb.d("10th", "25C, q = 0.1")} and {nb.d("25th", "25C, q = 0.25")} percentiles are 0 and the estimate there is 0 by '
            f'construction. Panel D describes the uncapped delay by group. Panel E tests whether the two groups’ '
            f'delays differ in spread or shape: the Brown–Forsythe test compares spread using deviations from '
            f'each group’s median, the Kolmogorov–Smirnov test compares whole distributions, and the log-rank '
            f'test compares the time to report as a survival curve; none gives p below .05. SD is the standard '
            f'deviation and M the mean.')
    return render_table(14, 'Disclosure Delay by Registration',
                        [('Delay regressions, all events', hdr_a, rows_a), ('Nonzero delays only', hdr_b, rows_b),
                         ('Quantile regressions of the uncapped delay', hdr_c, rows_c),
                         ('Distribution of the uncapped delay', hdr_d, rows_d),
                         ('Tests of spread and shape', hdr_e, rows_e)], note)


# ------------------------------------------------------------------ Table 15
def table_15():
    sp = appendix_csv('26_spreads.csv')
    mlab = {'CPQS change': 'Closing percent quoted spread (CPQS)', 'EDGE change': 'EDGE spread estimator',
            'log-OCAM change': 'Log open-to-close Amihud illiquidity (OCAM)'}
    rows = [[mlab[r.outcome], f'{fmt_num(r.coef, 5 if "CPQS" in r.outcome else 3)} '
             f'({fmt_num(r.se_cv3, 5 if "CPQS" in r.outcome else 3)})', fmt_p(r.p_cv3), fmt_p(r.bh_adj_p),
             fmt_p(r.p_cv1), fmt_num(r.corr_with_primary_dv, 2)] for _, r in sp.iterrows()]
    hdr = ['Measure (change, post minus pre)', 'Estimate (CV3 SE)', 'p', 'BH-adjusted p', 'CV1 p',
           'Correlation with the volatility change']
    nb = Notes(15)
    claim(all(float(x) >= .05 for x in sp.bh_adj_p) and all(float(x) >= .05 for x in sp.p_cv3), 'no spread test rejects')
    r0 = sp.iloc[0]
    note = (f'Each row regresses the change in one trading-cost measure, its mean over trading days '
            f'{nb.d("[+1, +20]", "scripts/268 header")} after the agency reporting date minus its mean over '
            f'{nb.d("[−60, −11]", "scripts/268 header")}, on the Form 499 registrant indicator, the M4 controls '
            f'and fixed effects for the calendar month of the reporting date, in the analytical sample '
            f'(N = {nb.i(r0.N, "26, N")}, {nb.i(r0.n_treated, "26, n_treated")} registrant events, G = '
            f'{nb.i(r0.G, "26, G")} parent filer entities, {nb.i(r0.G1, "26, G1")} with registrant events). CPQS is the '
            f'closing percent quoted spread, (ask − bid) divided by the quote midpoint, from valid uncrossed '
            f'closing quotes, with values above {nb.d("0.5", "scripts/268 header")} set to missing (Chung & Zhang, '
            f'2014); it is shown to five decimals because it is a fraction. EDGE is the efficient estimator of the '
            f'bid–ask spread from open, high, low and close prices (Ardia et al., 2024). OCAM is the open-to-close '
            f'Amihud illiquidity measure, the absolute open-to-close return divided by dollar volume (Barardehi et al., '
            f'2021); its window means are winsorized at the {nb.d("1st", "scripts/268 header (winsorized 1/99)")} and '
            f'{nb.d("99th", "scripts/268 header")} percentiles within each window and then logged. OCAM is biased '
            f'toward zero in large stocks, where dollar volume is high. Each window needs trading on at least '
            f'{nb.d("80", "scripts/268 header")} percent of its days. CV3 is the cluster jackknife standard error (SE) '
            f'by parent filer entity, with p-values from the t distribution with G − 1 degrees of freedom; CV1 is '
            f'the cluster-robust SE with the usual small-sample correction. The three measures form one family of '
            f'{nb.i(load_constants()["bh_families"]["spreads"], "constants bh_families.spreads")} tests, and the '
            f'BH-adjusted p applies the Benjamini–Hochberg false-discovery-rate adjustment within it; no measure '
            f'gives p below .05 before or after the adjustment. The last column is the Pearson correlation across '
            f'events between the change in the measure and the change in abnormal return volatility; all three are '
            f'small (at most {nb.r(max(abs(float(x)) for x in sp.corr_with_primary_dv), 2, "26, max |corr_with_primary_dv|")} '
            f'in absolute value), so trading costs and volatility move largely independently around the reporting date.')
    return render_table(15, 'Trading-Cost Measures', [('', hdr, rows)], note)


RENDERERS.update({14: table_14, 15: table_15})


# ------------------------------------------------------------------ Table 16
def table_16():
    sq = appendix_csv('27A_size_quartiles.csv')
    lad = appendix_csv('27B_size_quartile_ladder.csv')
    ci = pd.read_csv(V5 / 'v5_t18c_quartile_ci90.csv', dtype=str, keep_default_na=False).set_index('quartile')
    rows_a, rows_b, rows_c = [], [], []
    for _, r in sq.iterrows():
        q = r.quartile
        rows_a.append([q, f'{fmt_int(r.N)} ({fmt_int(r.treated_events)})', fmt_int(r.treated_parents), fmt_int(r.G),
                       f'{fmt_num(r.coef, 3)} ({fmt_num(r.se_cv3, 3)})', fmt_p(r.p_cv3), fmt_p(r.bh_adj_p_cv3)])
        c_ = ci.loc[q]
        rows_b.append([q, fmt_int(float(c_.df)), fmt_ci(c_.ci90_lo, c_.ci90_hi),
                       'Yes' if c_.inside_sesoi == 'True' else 'No', fmt_num(r.mde80_cv3, 3),
                       fmt_num(r.mde_over_full_sesoi, 2)])
        g = lad[lad.quartile == q]
        pick = lambda pre: fmt_p(g[g.rung.str.startswith(pre)].p.iloc[0])
        rows_c.append([q, pick('HC1'), pick('HC3'), fmt_p(r.bh_adj_p_hc3), pick('CV1'), pick('WCR restricted')])
    hdr_a = ['Size quartile', 'Events (registrant)', 'Treated parents', 'G', 'Estimate (CV3 SE)', 'p', 'BH-adjusted p']
    hdr_b = ['Size quartile', 'df', '90% CI', 'Inside ±SESOI', 'MDE80', 'MDE80 / SESOI']
    hdr_c = ['Size quartile', 'HC1 p', 'HC3 p', 'BH-adjusted HC3 p', 'CV1 p', 'Wild cluster p']

    nb = Notes(16)
    claim(all(c_.inside_sesoi == 'False' for _, c_ in ci.iterrows()), 'no cell interval inside SESOI')
    claim(V('q_cells_negligible') == 0, 'constants: no negligible cell')
    claim(all(int(float(ci.loc[q].df)) == int(sq.set_index('quartile').loc[q].G) - 1 for q in ci.index), 'cell df = G - 1')
    claim(sum(int(x) for x in sq.N) == V('primary_N'), 'cells sum to N')
    claim(all(float(x) >= .05 for x in sq.bh_adj_p_cv3), 'no cell rejects under CV3 after BH')
    q1 = sq.iloc[0]
    sesoi = float(ci.iloc[0].sesoi)
    n_hc1 = sum(1 for row in rows_c if row[1] != '' and (row[1] == '< .001' or float('0' + row[1]) < .05))
    note = (f'Each row of Panel A re-estimates the primary model M4 within one quartile of log total assets in the '
            f'analytical sample ({nb.c("primary_N", "i")} events in all), with the CV3 standard error (SE) clustered by '
            f'parent filer entity; G is the number of parent filer entities in the cell, and each cell’s CV3 '
            f'p-values use the t distribution with that cell’s G − 1 degrees of freedom (df). Registrant events '
            f'cluster at the top: Q4 holds {nb.i(sq.iloc[3].treated_events, "27A, Q4 / treated_events")} of '
            f'{nb.c("primary_treated", "i")}, and Q1 rests on {nb.i(q1.treated_events, "27A, Q1 / treated_events")} '
            f'registrant events at {nb.i(q1.treated_parents, "27A, Q1 / treated_parents")} treated parent, so its '
            f'estimate compares one firm with the rest of the cell; Q1 also drops the health-breach flag, which does '
            f'not vary there. The four cells form one family of '
            f'{nb.i(load_constants()["bh_families"]["size_quartiles"], "constants bh_families.size_quartiles")} tests, '
            f'and the BH-adjusted p applies the Benjamini–Hochberg false-discovery-rate adjustment within it; no '
            f'cell gives a BH-adjusted CV3 p below .05 (smallest {nb.c("q_min_bh_p_cv3", "p")}). Panel B asks whether '
            f'any cell can rule out effects that matter. The smallest effect size of interest (SESOI) is '
            f'{nb.f(sesoi, 3, "v5_t18c, sesoi (= constants dr_sesoi_daily)")}, 0.25 times the standard deviation of the '
            f'dependent variable among other events in the full sample. A cell rules out a negligible effect only if '
            f'its 90 percent confidence interval (CI) lies inside ±SESOI, the equivalence test at the 5 percent '
            f'level; no cell’s interval does, so no cell is ruled out as negligible. MDE80, the minimum detectable '
            f'effect at 80 percent power, is (t.975 + t.80, cell df) × SE_CV3; it runs from '
            f'{nb.c("q_mde_min", "f", 3)} to {nb.c("q_mde_max", "f", 3)}, or {nb.c("q_mde_min_x_sesoi", "f", 2)} to '
            f'{nb.c("q_mde_max_x_sesoi", "f", 2)} times SESOI. Panel C shows the p-values from procedures that ignore '
            f'or understate clustering, to document how they over-reject when few treated clusters sit in a cell: HC1 '
            f'and HC3 treat events as independent and give p below .05 in '
            f'{nb.i(n_hc1, "27B, HC1 rows with p < .05 (count)")} of the four cells, while CV3 rejects in none. HC1 and '
            f'HC3 are heteroskedasticity-consistent SEs; CV1 is the cluster-robust SE with the usual small-sample '
            f'correction; the wild cluster p comes from the restricted wild cluster bootstrap with Rademacher weights. '
            f'Q1 to Q4 are the size quartiles, Q1 smallest.')
    nb.d('0.25', 'scripts/263 design_resolution sesoi_mult')
    return render_table(16, 'Estimates by Size Quartile',
                        [('Cell estimates', hdr_a, rows_a), ('Equivalence and power by cell', hdr_b, rows_b),
                         ('Procedures that understate clustering', hdr_c, rows_c)], note)


RENDERERS.update({16: table_16})


# ------------------------------------------------------------------ Table 17
NODE = {
    'pre': ('Pre-window', {'pre60_11': '[−60, −11]', 'pre45_11': '[−45, −11]', 'pre25_5': '[−25, −5]'}),
    'post': ('Post-window', {'post1_5': '[+1, +5]', 'post1_10': '[+1, +10]', 'post1_20': '[+1, +20]', 'post5_25': '[+5, +25]'}),
    'benchmark': ('Return benchmark', {'mkt_adj': 'Market-adjusted', 'mm': 'Market model', 'ff3': 'Fama–French three-factor'}),
    'returns': ('Return type', {'simple': 'Simple', 'log': 'Log'}),
    'winsor': ('Winsorizing', {'raw': 'None', 'w1_99': '1st and 99th percentiles'}),
}


def table_17():
    sc = appendix_csv('29A_specification_curve.csv')
    for c in ['coef', 'p_cv3', 'p_cv1']:
        sc[c] = sc[c].astype(float)

    def row(dec, opt, g):
        return [dec, opt, fmt_int(len(g)), fmt_num(g.coef.median(), 3),
                f'{fmt_num(g.coef.min(), 3)} to {fmt_num(g.coef.max(), 3)}',
                fmt_int((g.p_cv3 < .05).sum()), fmt_int((g.p_cv1 < .05).sum())]
    rows_a = [row('All specifications', '', sc)]
    for k, (dec, opts) in NODE.items():
        for code, lab_ in opts.items():
            rows_a.append(row(dec, lab_, sc[sc[k] == code]))
    hdr_a = ['Decision', 'Option', 'Number', 'Median estimate', 'Range', 'CV3 p < .05', 'CV1 p < .05']
    pm = appendix_csv('29B_specification_curve_permutation.csv')
    plab = {'S1 median estimate': 'Median estimate (two-sided)', 'S2 dominant-sign count': 'Estimates sharing the dominant sign',
            'S3 significant in dominant direction (CV1)': 'Significant in the dominant direction (CV1)'}
    rows_b = [[plab[r.statistic], fmt_num(r.observed, 3) if '.' in str(r.observed) and not float(r.observed).is_integer()
               else fmt_int(float(r.observed)), fmt_num(r.null_mean, 3), fmt_p(r.perm_p), fmt_num(r.percentile, 1)]
              for _, r in pm.iterrows()]
    hdr_b = ['Statistic', 'Observed', 'Mean under the null', 'Permutation p', 'Percentile of the observed value']

    nb = Notes(17)
    sizes = [sc[k].nunique() for k in NODE]
    claim(len(sc) == V('spec_n') and len(sc) == int(np_prod(sizes)), 'grid size = product of options')
    claim((sc.p_cv3 < .05).sum() == V('spec_cv3_sig') == 0 and (sc.coef > 0).sum() == V('spec_positive'), 'none significant, all positive')
    s_ = ' × '.join(nb.i(x, f"29A, distinct {k}") for x, k in zip(sizes, NODE))
    note = (f'Each specification re-estimates the registrant coefficient of the primary model M4 on the analytical '
            f'sample (N = {nb.c("primary_N", "i")}, G = {nb.c("primary_G", "i")} parent filer entities, '
            f'{nb.c("primary_G1", "i")} with registrant events) under one combination of five analysis decisions: the '
            f'pre-window, the post-window, the return benchmark, simple or log returns, and whether daily returns are '
            f'winsorized; {s_} = {nb.c("spec_n", "i")} specifications. Panel A summarizes the estimates for each '
            f'option, pooling the specifications that use it (Number counts them); the last two columns count the specifications whose '
            f'p-value falls below .05 under CV3, the cluster jackknife standard error by parent filer entity, and under '
            f'CV1, the cluster-robust standard error with the usual small-sample correction. All '
            f'{nb.c("spec_positive", "i")} estimates are positive and none is significant under CV3 '
            f'({nb.c("spec_cv3_sig", "i")}) or CV1 ({nb.c("spec_sig_cv1_any", "i")}); the median estimate is '
            f'{nb.c("spec_median", "f", 3)}. Panel B is the permutation test of the whole curve (Simonsohn, Simmons & '
            f'Nelson, 2020): in each of {nb.c("spec_perm_draws", "i")} draws, registration is reassigned at random to '
            f'{nb.c("primary_G1", "i")} of the {nb.c("primary_G", "i")} parent filer entities, all events of a chosen '
            f'parent becoming registrant events, and all {nb.c("spec_n", "i")} specifications are re-estimated. Each '
            f'permutation p is the share of draws at least as extreme as the observed curve: for the median estimate, '
            f'in absolute value; for the count of estimates sharing the dominant sign; and for the count significant '
            f'in the dominant direction, using CV1. None is below '
            f'.05. An all-positive curve is common under the null here because every specification uses the same '
            f'events and parents, so the estimates move together: '
            f'{nb.r(V("perm_unanimous_share"), 3, "constants perm_unanimous_share")} of the null draws produce a curve '
            f'with a single sign.')
    return render_table(17, 'Specification Curve',
                        [('Estimates by decision and option', hdr_a, rows_a), ('Permutation test of the curve', hdr_b, rows_b)], note)


def np_prod(xs):
    out = 1
    for x in xs:
        out *= int(x)
    return out


# ------------------------------------------------------------------ Table 18
def table_18():
    inf = appendix_csv('30B_influence.csv')
    full = inf.iloc[0]
    lo_ = inf[inf.check.str.startswith('leave-one-parent-out minimum')].iloc[0]
    hi_ = inf[inf.check.str.startswith('leave-one-parent-out maximum')].iloc[0]
    sh = inf[inf.check.str.startswith('share of estimate')].iloc[0]
    pre = inf[inf.check.str.startswith('drop 6 pre-rule')].iloc[0]
    cook = inf[inf.check.str.startswith("Cook")].iloc[0]
    lp = appendix_csv('30A_leave_one_parent_out.csv')
    lp['coef_without'] = lp.coef_without.astype(float)
    mn, mx = lp.sort_values('coef_without').iloc[0], lp.sort_values('coef_without').iloc[-1]
    claim(abs(float(mn.coef_without) - float(lo_.coef)) < 1e-12 and abs(float(mx.coef_without) - float(hi_.coef)) < 1e-12, 'LOPO extremes agree')
    rows_a = [['Full sample (primary)', f'{fmt_num(full.coef, 3)} ({fmt_num(full.se_cv3, 3)})', fmt_p(full.p_cv3), fmt_int(float(full.N))],
              [f'Without {mn.parent} ({fmt_int(mn.events)} events), smallest', fmt_num(lo_.coef, 3), '', fmt_int(float(lo_.N))],
              [f'Without {mx.parent} ({fmt_int(mx.events)} events), largest', fmt_num(hi_.coef, 3), '', fmt_int(float(hi_.N))],
              [f'Share of the estimate removed by dropping {mn.parent}', fmt_num(sh.coef, 3), '', '']]
    hdr_a = ['Check', 'Estimate (CV3 SE)', 'p', 'N']
    rows_b = [['Drop events with Cook’s distance above 4/N', f'{fmt_num(cook.coef, 3)} ({fmt_num(cook.se_cv3, 3)})',
               fmt_p(cook.p_cv3), fmt_int(float(cook.N))],
              ['Drop events reported before the rule took effect', f'{fmt_num(pre.coef, 3)} ({fmt_num(pre.se_cv3, 3)})',
               fmt_p(pre.p_cv3), fmt_int(float(pre.N))]]
    hdr_b = hdr_a
    fe = appendix_csv('31_fixed_effects.csv')
    flab = {'year FE': 'Year', 'industry FE (2-digit SIC)': 'Industry (two-digit SIC)', 'year + industry FE': 'Year and industry'}
    rows_c = [[flab[r.spec], f'{fmt_num(r.coef, 3)} ({fmt_num(r.se_cv3, 3)})', fmt_p(r.p_cv3), fmt_int(r.N),
               f'{fmt_int(r.mixed_strata)} of {fmt_int(r.strata)}', f'{fmt_int(r.effective_obs)} ({fmt_int(r.effective_treated)})',
               fmt_int(r.singletons_dropped)] for _, r in fe.iterrows()]
    hdr_c = ['Fixed effects', 'Estimate (CV3 SE)', 'p', 'N', 'Mixed strata', 'Effective events (registrant)', 'Singletons dropped']
    v4 = appendix_csv('32_v4_date_sensitivity.csv')
    vlab = {'v3 dates (PRIMARY)': 'Dates as used (primary)',
            'v4 reporting dates for the re-anchored events': 'Revised source reporting dates',
            "v3 dates + Sprint's corrected breach date (event enters)": 'Sprint’s corrected breach date (event added)'}
    rows_d = [[vlab[r.scenario], f'{fmt_num(r.coef, 3)} ({fmt_num(r.se_cv3, 3)})', fmt_p(r.p_cv3),
               f'{fmt_int(r.N)} ({fmt_int(r.n_treated)})', fmt_int(r.events_changed)] for _, r in v4.iterrows()]
    hdr_d = ['Dates', 'Estimate (CV3 SE)', 'p', 'N (registrant)', 'Events changed']

    nb = Notes(18)
    yr = fe.iloc[0]
    claim(int(yr.N) - int(yr.effective_obs) == V('years_single_kind_events'), 'year FE drops exactly the one-group years')
    claim(all(float(x) >= .05 for x in list(fe.p_cv3) + [cook.p_cv3, pre.p_cv3] + list(v4.p_cv3)), 'no check rejects')
    note = (f'Each row re-estimates the registrant coefficient of the primary model M4 (N = {nb.c("primary_N", "i")}, '
            f'G = {nb.c("primary_G", "i")} parent filer entities, {nb.c("primary_G1", "i")} with registrant events) with '
            f'one change; standard errors are CV3, the cluster jackknife by parent filer entity, with p-values from the '
            f't distribution with G − 1 degrees of freedom. Panel A drops one parent filer entity at a time, '
            f'{nb.c("primary_G", "i")} re-estimates in all, and reports the smallest and largest. Dropping '
            f'{nb.reg(mn.parent, "30A, smallest coef_without / parent", mn.parent)} '
            f'({nb.i(mn.events, "30A, that row / events")} events) lowers the estimate to '
            f'{nb.f(lo_.coef, 3, "30B, LOPO minimum / coef")}, removing {nb.c("sprint_share_removed", "pct", 1)} percent '
            f'of it; dropping {nb.reg(mx.parent, "30A, largest coef_without / parent", mx.parent)} '
            f'({nb.i(mx.events, "30A, that row / events")} events) raises it to '
            f'{nb.f(hi_.coef, 3, "30B, LOPO maximum / coef")}. Panel B drops influential observations: Cook’s distance '
            f'measures how much all fitted values move when an observation is deleted, and the '
            f'{nb.c("cook_removed", "i")} events with a distance above {nb.d("4/N", "30B, Cook row (D > 4/N)")} are '
            f'removed; the second row drops the {nb.c("prerule_events", "i")} events reported before the rule took effect '
            f'on {nb.d("December 8, 2007", "30B / scripts/269 (2007-12-08)")}, none of them registrant events. Panel C '
            f'adds fixed effects for the reporting year, the two-digit Standard Industrial Classification (SIC) industry, '
            f'or both. A stratum is one year, one industry or one year-by-industry cell; a mixed stratum holds both '
            f'registrant and other events. With fixed effects the coefficient is identified only within mixed strata, '
            f'so events in single-group strata carry no weight (Aronow & Samii, 2016); Effective events counts the '
            f'events in mixed strata, with registrant events in parentheses. Under year fixed effects the '
            f'{nb.c("years_single_kind_events", "i")} events in single-group years drop out, leaving '
            f'{nb.i(yr.effective_obs, "31, year FE / effective_obs")}; under both sets only '
            f'{nb.i(fe.iloc[2].effective_obs, "31, year + industry / effective_obs")} events in '
            f'{nb.i(fe.iloc[2].mixed_strata, "31, year + industry / mixed_strata")} mixed cells remain. Industries with a '
            f'single event are dropped as singletons ({nb.i(fe.iloc[1].singletons_dropped, "31, industry / singletons_dropped")} '
            f'events). Panel D re-dates events: the second row uses the revised reporting dates the source later '
            f'published for {nb.i(v4.iloc[1].events_changed, "32, v4 row / events_changed")} events, and the third '
            f'corrects Sprint’s breach date, which adds {nb.i(v4.iloc[2].events_changed, "32, Sprint row / events_changed")} '
            f'event to the sample. No row gives p below .05.')
    return render_table(18, 'Sensitivity of the Main Estimate',
                        [('Leaving out one parent filer entity', hdr_a, rows_a), ('Influential and pre-rule events', hdr_b, rows_b),
                         ('Fixed effects and effective samples', hdr_c, rows_c), ('Revised dates', hdr_d, rows_d)], note)


# ------------------------------------------------------------------ Table 19
FAMILY_LAB = {
    'A2-delay': 'Disclosure delay (A2)', 'A2-delay-nz': 'Disclosure delay, nonzero (A2)', 'B2': 'Records per event and firm size (B2)',
    'B2b': 'Industry-code-only group comparisons (B2b)', 'poscontrol': 'Positive control (earnings decline)',
    'announcement family': 'Announcement window', 'dynamic path': 'Post-window length (dynamic path)',
    'fixed effects': 'Fixed effects', "Cook's exclusion": 'Cook’s distance exclusion', 'pre-rule exclusion': 'Pre-rule exclusion',
    'size quartiles': 'Size quartiles', 'specification-curve permutation (joint)': 'Specification-curve permutation',
    'spreads': 'Trading costs',
}
BH_KEY = {'A2-delay': 'A2-delay (scripts/164, kept)', 'A2-delay-nz': 'A2-delay-nz (scripts/164, kept)',
          'announcement family': 'announcement_window', 'dynamic path': 'dynamic_path', 'size quartiles': 'size_quartiles',
          'spreads': 'spreads'}


def _v5_rejections():
    """Count p < .05 (CV3 where the table has it) among the v5 tests, by family, from the v5 CSVs."""
    a = appendix_csv
    inf = a('30B_influence.csv')
    return {
        'dynamic path': sum(float(x) < .05 for x in a('21_dynamic_path.csv').p_cv3),
        'announcement family': sum(float(x) < .05 for x in a('24A_announcement_family.csv').p.iloc[:4]),
        'size quartiles': sum(float(x) < .05 for x in a('27A_size_quartiles.csv').p_cv3),
        'spreads': sum(float(x) < .05 for x in a('26_spreads.csv').p_cv3),
        'fixed effects': sum(float(x) < .05 for x in a('31_fixed_effects.csv').p_cv3),
        "Cook's exclusion": int(float(inf[inf.check.str.startswith('Cook')].p_cv3.iloc[0]) < .05),
        'pre-rule exclusion': int(float(inf[inf.check.str.startswith('drop 6')].p_cv3.iloc[0]) < .05),
        'specification-curve permutation (joint)': sum(float(x) < .05 for x in a('29B_specification_curve_permutation.csv').perm_p),
    }


def table_19():
    en = appendix_csv('33A_program_test_enumeration.csv')
    live = en[~en.v5_status.str.startswith('RETIRED')]
    bh = load_constants()['bh_families']
    rej = _v5_rejections()
    rows_a = []
    for fam_, g in live.groupby('family', sort=False):
        kept = g.v5_status.iloc[0].startswith('KEPT')
        bhs = bh.get(BH_KEY.get(fam_, ''), None)
        rows_a.append([FAMILY_LAB[fam_], fmt_int(len(g)), 'Kept from the earlier ledger' if kept else 'New in this version',
                       fmt_int(bhs) if bhs else '—', '—' if kept else fmt_int(rej[fam_])])
    rows_a.append(['All tests', fmt_int(len(live)), '', '', fmt_int(sum(rej.values()))])
    hdr_a = ['Family', 'Tests', 'Status', 'BH family size', 'p < .05']
    ret = en[en.v5_status.str.startswith('RETIRED')]
    rlab = {'RETIRED: raw-return volatility outcome, superseded by the v5 outcome': 'Raw-return volatility outcome, replaced by the current outcome',
            'RETIRED: microstructure intent-scope / TOST on the 167 measures, superseded by the v5 spreads family': 'Earlier trading-cost tests, replaced by the trading-cost family',
            'RETIRED: composition checks of the old announcement estimate; not rerun under v5': 'Composition checks of the earlier announcement estimate',
            'RETIRED: announcement family on the market-model basis, superseded by the v5 announcement family': 'Market-model announcement family, replaced by the current family'}
    rows_b = [[rlab[k], fmt_int(n)] for k, n in ret.v5_status.value_counts(sort=False).items()]
    rows_b.append(['All retired tests', fmt_int(len(ret))])
    hdr_b = ['Reason retired', 'Tests']

    nb = Notes(19)
    claim(len(live) == V('program_tests_total'), 'live tests = 45')
    claim(sum(rej.values()) == V('program_rejections_cv3'), 'rejections match constants')
    claim(len(ret) == V('program_tests_retired_from_t53'), 'retired = 39')
    fa = appendix_csv('24A_announcement_family.csv').iloc[3]
    n_bh = sum(1 for k in BH_KEY if k in set(live.family))
    note = (f'Each row of Panel A is one family of tests in the analysis program; the program holds '
            f'{nb.c("program_tests_total", "i")} tests, {nb.c("program_tests_kept_from_t53", "i")} kept from the earlier '
            f'test ledger because their outcomes do not use the volatility measure and '
            f'{nb.c("program_tests_new_v5", "i")} new in this version. A family is a set of tests that address one '
            f'question together. Within each of the {nb.i(n_bh, "33B, families with a BH adjustment (count)")} families '
            f'with a BH family size, p-values are adjusted by the Benjamini–Hochberg false-discovery-rate procedure '
            f'within that family; the other families are single checks or joint tests with their own reference '
            f'distribution. The last column counts tests with p below .05, using the CV3 cluster jackknife standard '
            f'error where the test has one; kept tests were not re-run in this version and show an em dash (—). '
            f'Of the new tests, {nb.c("program_rejections_cv3", "i")} give p below .05, all in the announcement-window family, '
            f'and {nb.i(V("program_rejections_cv3") - V("program_rejections_cv3_excl_calibration"), "constants program_rejections_cv3 - program_rejections_cv3_excl_calibration")} '
            f'of them are calibration tests that check the measure behaves as expected on earnings dates (the earnings '
            f'elevation and the breach-minus-earnings contrast). One substantive test rejects: the registrant coefficient '
            f'on announcement elevation (p = {nb.p(fa.p, "24A, Form 499 row / p")}, BH-adjusted p = '
            f'{nb.p(fa.bh_adj_p, "24A, Form 499 row / bh_adj_p")}). If every null hypothesis were true, about '
            f'{nb.c("program_tests_total", "i")} × .05 = {nb.f(V("program_tests_total") * .05, 2, "constants program_tests_total x .05")} '
            f'tests would give p below .05 by chance. Panel B lists the {nb.c("program_tests_retired_from_t53", "i")} '
            f'tests of the earlier ledger retired in this version, by reason. BH is Benjamini–Hochberg.')
    return render_table(19, 'Test Program Summary',
                        [('Live test families', hdr_a, rows_a), ('Retired tests', hdr_b, rows_b)], note)


RENDERERS.update({17: table_17, 18: table_18, 19: table_19})


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


# ------------------------------------------------------------------ missed registrants
MISSED_CSV = V5 / 'missed_registrants_by_firm.csv'


def emit_missed_registrants():
    """Firm names and record SIC codes of the records the industry codes miss (Table 4 Panel C).

    The one mode of this script that reads committed Data/ rather than outputs: it rebuilds
    the 891-record earlier-specification frame exactly as scripts/269 section B does (same
    files, merge keys, reparenting map, treatment and SIC rules, complete-case filter and
    quartiles) and gates the result against 08A, 06A and the constants before writing.
    """
    import numpy as np
    oxs = ['return_volatility_pre', 'firm_size_log', 'leverage', 'roa', 'disclosure_delay_days',
           'prior_breaches_total', 'health_breach']
    can = pd.read_csv(ROOT / 'Data/processed/rebuild/CANONICAL_V3.csv', low_memory=False)
    old = pd.read_csv(ROOT / 'Data/processed/FINAL_DISSERTATION_DATASET_ENRICHED.csv', low_memory=False)
    s2 = pd.read_csv(ROOT / 'Data/processed/rebuild/stage2_signed.csv', low_memory=False)
    key = ['org_name', 'breach_date', 'reported_date']
    for df_ in (old, s2):
        for c in ['breach_date', 'reported_date']:
            df_[c] = pd.to_datetime(df_[c], errors='coerce').dt.strftime('%Y-%m-%d')
    old2 = old.merge(s2.drop_duplicates(subset=key)[key + ['final_cik']], on=key, how='left')
    equity_parent = {1040573: 1166691, 1512267: 1166691, 1457937: 1105705}   # scripts/154:185
    old2['final_cik_rep'] = old2['final_cik'].map(
        lambda c: equity_parent.get(int(c), int(c)) if pd.notna(c) else np.nan)
    treated = set(can.loc[can['fcc_form499'] == 1, 'final_cik'].astype(int))
    old2['form499_family'] = old2['final_cik_rep'].isin(treated).astype(float)
    old2['sic_ind'] = pd.to_numeric(old2['sic'], errors='coerce').isin([4813, 4841, 4899]).astype(float)
    oc = old2[old2['has_crsp_data'] == True].dropna(subset=['volatility_change'] + oxs).copy()  # noqa: E712
    oc['q'] = pd.qcut(oc['firm_size_log'], 4, labels=[1, 2, 3, 4]).astype(int)
    m = oc[(oc['sic_ind'] == 0) & (oc['form499_family'] == 1)]
    g8 = appendix_csv('08A_misclassified_group_comparisons.csv').set_index('group').loc['missed_by_industry_codes']
    c = load_constants()['values']
    checks = [(len(oc), 891), (len(m), int(g8.N)), (m['org_name'].nunique(), int(g8.orgs)),
              (int((m['q'] == 1).sum()), c['q1_added_records']), (int((m['q'] == 4).sum()), c['missed_q4_records'])]
    if any(a != b for a, b in checks) or abs(m['volatility_change'].mean() - float(g8.mean_vol_change)) > 1e-9:
        sys.exit(f'missed-registrant rebuild disagrees with the committed outputs: {checks}')
    out = (m.assign(parent_cik=m['final_cik_rep'].astype(int),
                    record_sic=pd.to_numeric(m['sic']).astype(int))
            .groupby(['parent_cik', 'organization' if 'organization' in m else 'org_name', 'record_sic'])
            .agg(records=('q', 'size'),
                 size_quartiles=('q', lambda s: ';'.join(f'Q{x}' for x in sorted(s))))
            .reset_index().rename(columns={'org_name': 'organization'})
            .sort_values(['parent_cik', 'organization'], kind='stable'))
    out.to_csv(MISSED_CSV, index=False, lineterminator='\n', encoding='utf-8')
    print(f'wrote {MISSED_CSV.relative_to(ROOT)}: {len(out)} organizations, {int(out.records.sum())} records')


# ------------------------------------------------------------------ Word output
LAST_SET = 9
FIXED_TIME = (1980, 1, 1, 0, 0, 0)
_NUMERIC_CELL = re.compile(r'^[−\-+<>=.,%()\[\]\d\s;Q–]*$')


def _is_numeric(text):
    t = str(text).strip()
    if re.fullmatch(r'[−\-]?[\d.,]+ to [−\-]?[\d.,]+', t):   # number ranges such as '0.037 to 0.364'
        return True
    return t in ('', '—', NO_SOURCE) or (bool(_NUMERIC_CELL.match(t)) and any(ch.isdigit() for ch in t))


CHAR_IN = 0.075    # average Times New Roman 10 pt character width, inches
HEAD_CHAR_IN = 0.09   # header words: wider letters, must not break mid-word
PAD_IN = 0.16      # left + right cell margins
TABLE_DXA = int(6.5 * 1440)
WRAP_IN = 1.6      # columns wider than this may wrap
MIN_WRAP_IN = 1.0  # narrowest a wrapping column may get


def _column_widths(header, rows, numeric):
    """Column widths (dxa) sized to content, summing to 6.5 in.

    Natural width = widest body cell or longest header word; minimum width = longest single
    word in the column (body or header), so no word breaks mid-word when it can be avoided.
    Columns narrower than WRAP_IN keep their natural width; wider columns (labels, names,
    bases) get their minimum plus a share of what is left in proportion to how much more they
    would need. If even the minimums do not fit, every column scales from its minimum.
    """
    def words(t):
        return [w for w in str(t).replace('/', '/ ').split() if w]
    nat, mn = [], []
    for j, h in enumerate(header):
        body = max([len(line) for r in rows for line in str(r[j]).split('\n')] + [0])
        hw = max([len(w) for w in words(h)] + [0])
        bw = max([len(w) for r in rows for w in words(r[j])] + [0])
        nat.append(max(body * CHAR_IN, hw * HEAD_CHAR_IN) + PAD_IN)
        # numeric cells never wrap (their spaces are non-breaking in Word): minimum = natural
        mn.append(nat[-1] if numeric[j] else max(bw * CHAR_IN, hw * HEAD_CHAR_IN) + PAD_IN)
    total_in = TABLE_DXA / 1440
    if sum(nat) <= total_in:
        w = [n * total_in / sum(nat) for n in nat]
    else:
        wrap = [n > WRAP_IN for n in nat]
        keep = sum(n for n, wr in zip(nat, wrap) if not wr)
        wmins = sum(m for m, wr in zip(mn, wrap) if wr)
        avail = total_in - keep
        if any(wrap) and avail >= wmins:
            need = sum(n - m for n, m, wr in zip(nat, mn, wrap) if wr) or 1.0
            w = [m + (avail - wmins) * (n - m) / need if wr else n for n, m, wr in zip(nat, mn, wrap)]
        elif sum(mn) <= total_in:
            need = sum(n - m for n, m in zip(nat, mn)) or 1.0
            w = [m + (total_in - sum(mn)) * (n - m) / need for n, m in zip(nat, mn)]
        else:
            w = [m * total_in / sum(mn) for m in mn]
    dxa = [int(round(x * 1440)) for x in w]
    dxa[0] += TABLE_DXA - sum(dxa)
    return dxa


def write_docx(path, blocks, section_per_table=False):
    """APA tables (Essay 1 layout) in a .docx; deterministic (fixed core properties and zip times)."""
    import zipfile
    from docx import Document
    from docx.enum.table import WD_TABLE_ALIGNMENT
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    from docx.shared import Inches, Pt
    from datetime import datetime

    doc = Document()
    sec = doc.sections[0]
    sec.left_margin = sec.right_margin = sec.top_margin = sec.bottom_margin = Inches(1)
    st = doc.styles['Normal']
    st.font.name = 'Times New Roman'
    st.font.size = Pt(12)
    st.element.rPr.rFonts.set(qn('w:eastAsia'), 'Times New Roman')
    pf = st.paragraph_format
    pf.space_before = Pt(0)
    pf.space_after = Pt(0)
    pf.line_spacing = 1.0
    from docx.enum.style import WD_STYLE_TYPE
    cs = doc.styles.add_style('Table Cell 10', WD_STYLE_TYPE.PARAGRAPH)
    cs.base_style = st
    cs.font.size = Pt(10)
    cs.paragraph_format.space_before = Pt(0)
    cs.paragraph_format.space_after = Pt(0)
    cs.paragraph_format.line_spacing = 1.0

    def para(text='', size=12, bold=False, italic=False, keep=False, before=0, runs=None):
        p = doc.add_paragraph()
        p.paragraph_format.keep_with_next = keep
        p.paragraph_format.space_before = Pt(before)
        for t, it in (runs or [(text, italic)]):
            r = p.add_run(t)
            r.font.size = Pt(size)
            r.bold = bold
            r.italic = it
        return p

    def border(cell, edges):
        tcpr = cell._tc.get_or_add_tcPr()
        b = tcpr.find(qn('w:tcBorders'))
        if b is None:
            b = OxmlElement('w:tcBorders')
            tcpr.append(b)
        for e in edges:
            el = OxmlElement(f'w:{e}')
            el.set(qn('w:val'), 'single')
            el.set(qn('w:sz'), '6')
            el.set(qn('w:space'), '0')
            el.set(qn('w:color'), '000000')
            b.append(el)

    def table(header, rows):
        t = doc.add_table(rows=1 + len(rows), cols=len(header))
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        t.autofit = True
        tblpr = t._tbl.tblPr
        w = tblpr.find(qn('w:tblW'))
        if w is None:
            w = OxmlElement('w:tblW')
            tblpr.append(w)
        w.set(qn('w:w'), str(int(6.5 * 1440)))
        w.set(qn('w:type'), 'dxa')
        none = OxmlElement('w:tblBorders')
        for e in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'):
            el = OxmlElement(f'w:{e}')
            el.set(qn('w:val'), 'nil')
            none.append(el)
        tblpr.append(none)
        numeric = [all(_is_numeric(r[j]) for r in rows) for j in range(len(header))]
        widths = _column_widths(header, rows, numeric)
        layout = OxmlElement('w:tblLayout')
        layout.set(qn('w:type'), 'fixed')
        tblpr.append(layout)
        grid = t._tbl.tblGrid
        for gc_, wd in zip(grid.findall(qn('w:gridCol')), widths):
            gc_.set(qn('w:w'), str(wd))
        for i, vals in enumerate([header] + rows):
            row = t.rows[i]
            trpr = row._tr.get_or_add_trPr()
            trpr.append(OxmlElement('w:cantSplit'))
            if i == 0:
                trpr.append(OxmlElement('w:tblHeader'))
            for j, v in enumerate(vals):
                cell = row.cells[j]
                tcpr = cell._tc.get_or_add_tcPr()
                tcw = tcpr.find(qn('w:tcW'))
                if tcw is None:
                    tcw = OxmlElement('w:tcW')
                    tcpr.insert(0, tcw)
                tcw.set(qn('w:w'), str(widths[j]))
                tcw.set(qn('w:type'), 'dxa')
                p = cell.paragraphs[0]
                p.style = cs
                p.paragraph_format.keep_with_next = i < len(rows)
                text = str(v)
                if i > 0 and re.fullmatch(r'[A-Z]{1,5}-[A-Z]{1,3}', text):
                    text = text.replace('-', '‑')
                if i > 0 and numeric[j]:
                    # keep "< .001", "0.39 (177.49)", "-0.02 (0.87)" on one line
                    text = text.replace('< ', '<\u00a0').replace(' (', '\u00a0(').replace(' to ', '\u00a0to\u00a0')
                r = p.add_run(text)
                r.font.size = Pt(10)
                if i == 0:
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                elif j == 0 or not numeric[j]:
                    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                else:
                    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                if i == 0:
                    border(cell, ['top', 'bottom'])
                elif i == len(rows):
                    border(cell, ['bottom'])

    from docx.enum.section import WD_SECTION
    for bi, b in enumerate(blocks):
        if section_per_table and bi > 0:
            doc.add_section(WD_SECTION.NEW_PAGE)   # one table per section, each on a new page
        para(f'Table {b["new"]}', bold=True, keep=True,
             before=0 if (bi == 0 or section_per_table) else 24)
        para(b['title'], italic=True, keep=True)
        for pi, (pt, header, rows, _kind) in enumerate(b['panels']):
            if len(b['panels']) > 1:
                para(f'Panel {panel_letter(pi)}: {pt}', size=10, italic=True, keep=True, before=6)
            elif pi == 0:
                para('', size=10, keep=True)
            table(header, rows)
        para(size=10, before=6, runs=[('Note.', True), (' ' + b['note'], False)])

    cp = doc.core_properties
    fixed = datetime(2026, 1, 1)
    cp.author = cp.last_modified_by = 'scripts/274_e2v5_inline_tables.py'
    cp.created = cp.modified = cp.last_printed = fixed
    cp.revision = 1
    cp.title = 'Essay 2 tables'
    tmp = path.with_suffix('.tmp.docx')
    doc.save(tmp)
    with zipfile.ZipFile(tmp) as zin, zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as zout:
        for item in sorted(zin.infolist(), key=lambda z: (z.filename != '[Content_Types].xml', z.filename)):
            zi = zipfile.ZipInfo(item.filename, date_time=FIXED_TIME)
            zi.compress_type = zipfile.ZIP_DEFLATED
            zi.external_attr = 0o644 << 16
            zout.writestr(zi, zin.read(item.filename))
    tmp.unlink()
    print(f'wrote {path.relative_to(ROOT)} ({len(blocks)} tables)')


# ------------------------------------------------------------------ main
def write_set(n, docx_too=False):
    blocks = set_blocks(n)
    text = '\n'.join(b['md'] for b in blocks)
    no_src = text.count(NO_SOURCE)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / f'set_{n}.md'
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)
    print(f'wrote {path.relative_to(ROOT)} (tables {SETS[n]}; {no_src} [NO SOURCE] cells)')
    reg = {str(b['new']): dict(note=b['note'], numbers=NOTE_REG.get(b['new'], [])) for b in blocks}
    CHECK_DIR.mkdir(parents=True, exist_ok=True)
    with open(CHECK_DIR / f'note_numbers_set{n}.json', 'w', encoding='utf-8', newline='\n') as f:
        json.dump(reg, f, indent=1, ensure_ascii=False, sort_keys=True)
    if docx_too:
        write_docx(OUT_DIR / f'Essay2_Tables_Set_{n}.docx', blocks)
        if n == LAST_SET:
            missing = [k for k in range(1, LAST_SET + 1) if k not in SETS]
            if missing:
                sys.exit(f'cannot write Essay2_Tables_All.docx: sets {missing} not registered')
            write_docx(OUT_DIR / 'Essay2_Tables_All.docx',
                       [b for k in range(1, LAST_SET + 1) for b in set_blocks(k)], section_per_table=True)


def set_blocks(n):
    if n not in SETS:
        sys.exit(f'set {n} has no tables registered yet (SETS is filled in by each set\'s prompt)')
    out = []
    for new in SETS[n]:
        if new not in RENDERERS:
            sys.exit(f'Table {new} (set {n}) has no renderer')
        out.append(RENDERERS[new]())
    return out


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
    g.add_argument('--missed-registrants', action='store_true',
                   help=f'write {MISSED_CSV.name} (reads committed Data/, as scripts/269 does)')
    g.add_argument('--constants', action='store_true',
                   help='write constants_parts/274.json (then merge with scripts/270)')
    ap.add_argument('--docx', action='store_true',
                    help='with --set N: also write Essay2_Tables_Set_N.docx (and, for the last set, '
                         'Essay2_Tables_All.docx)')
    a = ap.parse_args()
    if a.docx and a.set_n is None:
        ap.error('--docx needs --set N')
    check_layout()
    if a.missed_registrants:
        emit_missed_registrants()
    elif a.constants:
        emit_constants()
    elif a.layout:
        print_layout()
    else:
        write_set(a.set_n, docx_too=a.docx)


if __name__ == '__main__':
    main()
