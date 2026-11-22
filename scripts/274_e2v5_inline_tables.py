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

    def w(self, word, value, source):
        """A number written as a word; its value must equal the source value."""
        if WORDNUM[word.lower()] != int(value):
            sys.exit(f'Table {self.t} note: "{word}" but the source ({source}) gives {value}')
        return self.reg(word, source, int(value))

    def final(self):
        """The note exactly as written, after every number in it is checked against the registry."""
        text = NOTE_TEXT[self.t]
        mt = _mask(text)
        taken, errs = [], []
        for e in NOTE_REG[self.t]:
            i = _free_at(mt, e['shown'], taken)
            if i is None:
                errs.append(f'registered {e["shown"]!r} ({e["source"]} = {e["value"]}) does not occur in the note')
            else:
                taken.append((i, i + len(e['shown'])))
        cov = lambda a, b: any(x <= a and b <= y for x, y in taken)
        for m in list(_NUM_TOKEN.finditer(mt)) + list(_SCAN_WORDS.finditer(mt)):
            if not cov(*m.span()):
                errs.append(f'no registered source for {m.group()!r} in "...{text[max(0, m.start() - 50):m.end() + 30]}..."')
        if errs:
            sys.exit(f'Table {self.t} note check failed:\n  ' + '\n  '.join(errs))
        return text


def claim(ok, what):
    """A statement a note makes about the data; the render stops if the data do not bear it out."""
    if not ok:
        sys.exit(f'note claim fails: {what}')


# ------------------------------------------------------------------ note text (Tim, 2026-11-18)
# Each note is used exactly as written. Notes.final() checks it against the registry: every
# registered number (formatted from its committed source) must occur in the text, and every
# number in the text must be covered by a registration. The render stops otherwise.
WORDNUM = {'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6, 'seven': 7, 'eight': 8,
           'nine': 9, 'ten': 10, 'eleven': 11, 'twelve': 12, 'twenty-eight': 28}
_SCAN_WORDS = re.compile(r'\b(two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|twenty-eight)\b', re.I)
_NUM_TOKEN = re.compile(r'(?<![\w.])[\u2212+]?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?(?:st|nd|rd|th)?(?!\w)'
                        r'|(?<![\w.])\.\d+')
# names and terms whose digits or number words are not statistics
_MASKS = [r'Form 499', r'\b(?:M[1-4]|H1|Q[1-4]|G1|CV[13]|HC[13]|MDE80|FF3)\b', r'Table \d+', r'Gate [12]',
          r'R\u00b2', r'two-digit', r'three-factor',
          r'(?<=et al\. \()(?:19|20)\d{2}', r'(?<=et al\., )(?:19|20)\d{2}',
          r'(?<=[a-z] & [A-Z])[a-z]+, (?:19|20)\d{2}']


def _mask(text):
    out = list(text)
    for pat in _MASKS:
        for m in re.finditer(pat, text):
            for k in range(m.start(), m.end()):
                if out[k].isdigit():
                    out[k] = 'x'
            if pat in ('two-digit', 'three-factor'):
                for k in range(m.start(), m.start() + m.group().index('-')):
                    out[k] = 'x'
    return ''.join(out)


def _free_at(text, shown, taken):
    i = text.find(shown)
    while i != -1:
        j = i + len(shown)
        left = text[i - 1] if i > 0 else ' '
        right = text[j] if j < len(text) else ' '
        nxt = text[j + 1] if j + 1 < len(text) else ' '
        ok = (not left.isalnum() and left != '.' and not (shown[0].isdigit() and left in '\u2212+')
              and not right.isalnum() and not (right in '.,' and nxt.isdigit()))
        if ok and not any(a < j and i < b for a, b in taken):
            return i
        i = text.find(shown, i + 1)
    return None


NOTE_TEXT = {
    1: 'Panel A traces the sample from Privacy Rights Clearinghouse (PRC) notification records to analytical events. The first four rows count records and the remaining rows count canonical events; one breach can produce several records, so the starting 1,054 records are not 1,054 breaches. Gate 1 keeps a record only when the reporting organization resolves to a public filer entity. Gate 2 reviews records at the same parent filer entity with nearby dates and rules whether they describe one breach, so that each breach enters once. The registrant column gives Form 499 registrant events, with their organizations and parent filer entities in parentheses; an em dash (—) marks a count not tracked at that step. Panel B reports the final sample at three levels. The registrant and other parent counts sum to 84 rather than 82 because Comcast and Verizon each have events in both groups: the NBC Sports Group and Verizon Media events are other events. Panel C counts events by reporting year. The 5 years marked "one group only" hold 52 events, 3 of them registrant events, and contribute nothing to the estimate under year fixed effects. A Form 499 registrant event is an event at a firm registered on Federal Communications Commission (FCC) Form 499. The parent filer entity is the Securities and Exchange Commission (SEC) filer that owns the breached organization and is the clustering unit (G = 82). CRSP = Center for Research in Security Prices.',
    2: 'Each row compares the 104 Form 499 registrant events with the 229 other events in the analytical sample (N = 333). The dependent variable is the change in abnormal return volatility: the standard deviation (SD) of daily abnormal returns (the stock return minus the CRSP value-weighted market return), in percentage points, over trading days [+1, +20] after the agency reporting date minus the same SD over [−60, −11]; the pre-window and post-window rows report the two levels. M is the group mean. Difference is the registrant mean minus the other-firm mean, with its standard error (SE) in parentheses. The Welch t-test tests whether the two means are equal without assuming equal variances and uses Welch–Satterthwaite degrees of freedom (df), shown in parentheses; a p-value below .05 indicates that the means differ. The groups do not differ on the change (p = .700) but differ on both levels (p = .009 and .008) and on every control except the disclosure gap (p = .490). Log total assets is the natural log of Compustat total assets; leverage is total liabilities divided by total assets; return on assets is net income divided by total assets. The health-breach flag equals 1 when the breach record lists medical or health information as affected (15 events, all other events). Prior breach events counts earlier sample events at the same parent filer entity. The disclosure gap is the number of days from the breach date to the agency reporting date, with gaps of −30 to −1 days set to 0 and values capped at the 99th percentile (784.96 days). Panel C reports Pearson correlations; the largest in absolute value is between registration and log total assets (.57). CRSP = Center for Research in Security Prices.',
    3: 'Panels A and B reproduce the earlier specification: raw-return volatility on 891 notification records, size quartiles of log market value, and HC3 heteroskedasticity-consistent standard errors (SE), which do not account for clustering. Each cell is the treatment coefficient from a separate ordinary least squares (OLS) regression within the quartile named, with its SE in parentheses. Panel A treats a record when its Standard Industrial Classification (SIC) code is 4813, 4841, or 4899; Panel B treats it when its parent filer entity is registered on Federal Communications Commission (FCC) Form 499. The two panels use the same records, so their estimates share observations and no test of their difference is reported. Panel C repeats the comparison on 339 canonical events, with size quartiles of log total assets; treated parent filer entities are in parentheses. The Q1 − Q4 spread is the smallest-quartile estimate minus the largest. Treatment varies across few parent filer entities (the Panel C Q1 cell holds 2 treated events at 1 parent), so these SEs are too small to support a rejection. Panel D shows how records concentrate in events: 115 of the 618 events have more than one record and supply 388 records, and two 2024 events at one parent filer entity supply 56. Panel E counts, among 48 window specifications on the corrected data (24 per anchor date), those that place the Q1 estimate above Q4 (0) and those that decline steadily from Q1 to Q4 (0). Q1 is the smallest quartile.',
    4: 'Panel A divides the 891 notification records by the two treatment definitions: an industry code of 4813, 4841, or 4899 on the record, and registration of the parent filer entity on Federal Communications Commission (FCC) Form 499. The definitions disagree on 30 records. Twenty-eight are Form 499 registrant records that carry none of the three codes, at 16 organizations. The other 2 are damaged source entries coded 4813 whose organization field holds an AT&T breach label rather than a firm name, so they resolve to no parent filer entity. Records neither definition treats form the comparison group under both. Change is the change in raw-return volatility under the earlier specification, and size is log market value. Panel B splits the 229 records in the smallest size quartile (Q1). The 10 records treated under Form 499 only come from GoDaddy, a domain registrar (8), and Twilio, a communications platform (2); their mean change, −8.62, compares with −2.20 for records neither definition treats. Panel C places the 28 missed records by quartile: 10 in Q1, 13 in Q4, and 5 in Q2 or Q3. M = mean; SD = standard deviation.',
    5: "Panel A lists the 6 identifiers in the earlier matching chain that absorbed the names of unrelated organizations, so those organizations' breach records took on another firm's stock data. Organizations absorbed counts distinct organization names, records counts their breach records, and canonical events counts current events carrying one of those names; the largest collision absorbed 25 organizations and 46 records. Panel B lists the 7 events at which ticker reuse would have matched the breached firm to an earlier, unrelated holder of the same symbol whose ticker had ended years before (in 2002 for META and 1992 for DASH). The current chain blocks that match, and none of the 7 events has a stock match. Panel C regresses the earlier dataset's size variable on two candidate measures: against log market value the slope is 0.99 and R² is .86, and against log total assets the slope is 0.46 and R² is .44, so the variable measures market value. Share within is the share of records within 0.10 or 0.25 of each candidate. Panel D starts from the 355 events matched to stock data and reported by December 31, 2024 (111 registrant and 244 other events) and counts the events lost at each requirement. Retention is 93.7 percent of registrant events (104 of 111) and 93.9 percent of other events (229 of 244). PERMNO = CRSP permanent security identifier; CRSP = Center for Research in Security Prices; R² = share of variance explained.",
    6: "Panel A has one row per treated parent filer entity (12 parents, 104 registrant events). The Federal Communications Commission (FCC) Form 499 registry holds 20,669 filer records. Registry records matched counts the records whose legal name, doing-business-as name, or holding company contains one of the parent's name keywords (671 in all). A match counts toward treatment only when the matched registration is open on the breach date. Distinct FRNs counts FCC Registration Numbers among the matched records, and end date before start date counts records carrying that registry error (2 in all). Breach dates gives the first and last breach date among the parent's events. Panel B lists the 23 adjudication rules, covering 22 organization names. Each rule records a ruling for a name pattern that exact matching would treat wrongly. A rule forces treatment under clause (a), a registration of the organization itself open on the breach date, or clause (b), the organization is the parent brand of a registered filer whose subscriber operations were breached, and forces exclusion when neither clause holds. DISH Network has two rules: it is excluded before July 1, 2020, and treated after. Panel C lists the 3 rules that assign a registrant with no traded equity to the parent filer entity that owns it. CIK = Securities and Exchange Commission Central Index Key.",
    7: "Each row of Panel A applies one industry-code convention to the 346 canonical events with a Compustat historical Standard Industrial Classification (SIC) code and compares the result with Federal Communications Commission (FCC) Form 499 registration. The conventions are the regulated-carrier codes from published practice (4812 and 4813; Barclay & Smith, 1995), the communications codes of this essay's earlier specification (4813, 4841, and 4899), the full communications range (4800 to 4899), and a set chosen after examining the registry (4812, 4813, 4841, and 4899), whose agreement is therefore an upper bound rather than a test. Event agreement is the percentage of events on which convention and registration agree. A false positive is an event the convention codes as a carrier although its parent filer entity is not a registrant; a false negative is a registrant event the convention does not code. Treated parents identified counts, of the 12 registrant parent filer entities, those with at least one event the convention codes as a carrier. The tuned set agrees most often (96.0 percent), and the published convention identifies the fewest registrant parents (6). Panel B lists the misclassified organizations with the SIC code that produced each error.",
    8: "Panel A lists the 11 registrant events, at 3 parent filer entities, that fall outside the comparison in Table 7. Of the 118 verified registrant events, 107 carry a Compustat historical Standard Industrial Classification (SIC) code. An event goes uncoded when its firm has no matched stock ticker (7 events) or no Compustat annual record in the 550 days before the breach date (4 events); 8 of the 11 are T-Mobile events. Panel B compares, for each treated parent filer entity and for Roku, the Compustat code on the most recent annual record within 550 days before the breach date with every code on the parent's breach records. The two sources disagree for 11 of the 14 treated parents. An em dash (—) marks a missing code.",
    9: 'Each column is an ordinary least squares (OLS) regression on the analytical sample (N = 333 events, 104 Form 499 registrant events). The dependent variable is the change in abnormal return volatility, defined in Table 2. M1 includes the pre-window volatility level and the disclosure gap; M2 adds log total assets, leverage, and return on assets; M3 adds the Form 499 registrant indicator, the test of H1; M4 adds the health-breach flag and prior breach events and is the primary model. Each cell shows the coefficient, its CV3 standard error in parentheses, and its p-value below. CV3 is the cluster jackknife standard error, clustered by parent filer entity (G = 82, 12 with registrant events); it re-estimates the model leaving out one parent at a time, and its p-values use the t distribution with 81 degrees of freedom. With the pre-window level as a regressor, each model is an analysis of covariance: the registrant coefficient compares post-window volatility across groups at the same pre-window level. Because the dependent variable contains the pre-window level, R² is not the share of post-disclosure volatility explained. In M4 the registrant coefficient is 0.137 (p = .481), and adding the indicator in M3 raises R² from .159 to .163. Disclosure-gap coefficients are per day.',
    10: "Each row of Panel A reports a different standard error (SE) and test for the Form 499 registrant coefficient of the primary model M4 (0.137; N = 333). OLS assumes independent errors with equal variance. HC1 and HC3 allow the variance to differ across events but treat events as independent; HC3 inflates each residual by its leverage. CV1 clusters by parent filer entity with the usual small-sample correction. CV3, the primary procedure, is the cluster jackknife, which re-estimates the model leaving out one parent filer entity at a time; its p-values use the t distribution with 81 degrees of freedom. The three wild cluster bootstrap rows reweight parent-level residuals to simulate the distribution of the test statistic: the restricted version imposes a zero coefficient and the unrestricted version does not. Rademacher weights flip each parent's residuals with probability one half (99,999 draws); Webb weights draw from six points, which suits few clusters (9,999 draws); the seed is 499. Procedures that ignore clustering understate the SE when treatment varies across few parents: the HC1 SE (0.112) is 42 percent smaller than the CV3 SE (0.193). No procedure gives a p-value below .05. G is the number of parent filer entities (82), G1 the number with registrant events (12), and G* the effective number of clusters, 23.4, which adjusts G for unequal cluster sizes and the concentration of treatment (Carter et al., 2017); the coefficient of variation of cluster size is 2.25. An em dash (—) marks a procedure that produces no confidence interval. Panel B clusters by two-digit Standard Industrial Classification (SIC) industry (25 clusters).",
    11: "The table asks whether the primary estimate (M4; N = 333, G = 82) is precise enough to rule out effects that matter. Values are in percentage points (pp) of daily abnormal return volatility; annualized values multiply by √252. The smallest effect size of interest (SESOI) is 0.25 times the standard deviation of the dependent variable among other events (0.763), or 0.191 pp daily (3.03 pp annualized); no comparable volatility effect is reported in the literature, so the bound rests on the outcome's own spread. TOST (two one-sided tests) tests whether the effect is small enough to treat as practically zero: it runs one test that the effect is above −SESOI and one that it is below +SESOI, using the CV3 standard error and the t distribution with 81 degrees of freedom, and reports the larger p-value. The lower test rejects (p = .047), so effects below −SESOI are ruled out; the upper test does not (p = .390), so a positive effect as large as SESOI cannot be excluded. The 90 percent confidence interval, [−0.185, 0.458], corresponds to TOST at the 5 percent level and does not lie inside ±SESOI. The literature bound is ±2.10 pp, the two-day breach penalty reported by Cavusoglu et al. (2004), divided by √252 to 0.132 pp daily; its TOST p is .509. MDE80 is the minimum detectable effect, the smallest true effect the regression would detect approximately four times in five at the 5 percent level, computed as 2.84 times the CV3 standard error; it is 2.87 times SESOI. The HC3 row shows the MDE80 that heteroskedasticity-consistent standard errors would imply, 41 percent lower. An MDE80 of 5 pp annualized would require 55 treated parent filer entities, and as treated parents increase without limit the MDE80 falls only to 0.207 pp daily (3.29 pp annualized).",
    12: "Each row re-estimates the primary model M4 with one change and reports the Form 499 registrant coefficient, its CV3 standard error (SE) in parentheses, its p-value, and its 95 percent confidence interval; N = 333 and G = 82 unless the N column shows otherwise. CV3 is the cluster jackknife SE by parent filer entity. Panel A ends the post-window at day +5, +10, or +20 against the pre-window [−60, −11]; the three windows form one family, and the BH-adjusted p applies the Benjamini–Hochberg false-discovery-rate adjustment within it. The wild cluster p comes from the restricted wild cluster bootstrap with Rademacher weights. Every window must have returns on at least 80 percent of its trading days. Panel B replaces the market adjustment with abnormal returns from the market model and the Fama–French three-factor (FF3) model, both estimated over trading days [−250, −30]; 6 events (1 registrant event) lack 80 percent coverage in that window, leaving 327 events. Panel C counts contaminated estimation windows, those containing another event at the same parent filer entity, dated by that event's notification date and by its breach date; the focal event itself is excluded. The shares across all events are .43 by notification date and .59 by breach date. Panel D lists coverage drops by benchmark and pre-window; the primary windows drop no event. Panel E moves step by step from the earlier outcome, raw log-return volatility over [−25, −5] and [+5, +25], to the primary one: the same outcome with the 80 percent rule, then market-adjusted simple returns on the same windows, then the current windows. Its first rows start the pre-window at day −45. No row gives a p-value below .05.",
    13: 'Announcement elevation is the standard deviation (SD) of daily market-adjusted returns over the nine trading days [−4, +4] centered on the agency reporting date minus the SD over the three weeks before, [−25, −5]; each window needs returns on 8 of 9 and 17 of 21 days. Unless a row shows otherwise, each estimate is the Form 499 registrant coefficient from a regression of elevation on registration, baseline-window volatility, and the M4 controls (N = 333, G = 82). Panel A is the pre-specified family of 4 tests: mean elevation on earnings-announcement dates, mean elevation on breach reporting dates, their contrast, and the registrant coefficient; the BH-adjusted p applies the Benjamini–Hochberg adjustment within that family. The two earnings tests are calibration checks expected to reject. The registrant coefficient is 0.433 (CV3 p = .027, BH-adjusted p = .036). Panel B repeats the test under each procedure in Table 10; every procedure gives p below .05. Panel C adds controls in steps; the baseline-window SD closes .42 of the distance from the unadjusted to the full-model coefficient, and log total assets brings the total to .81. Panel D is the placebo test: in each of 200 draws (seed 499), every security receives a random quiet date at least 120 trading days from any breach notification and 30 from any earnings date, and no draw matches the actual coefficient (0 of 200). Relative to their own quiet days, registrant events show elevation 0.008 higher on breach dates and other events 0.140 lower, so the difference comes from other events. Panel E reports the earnings-announcement benchmark, with SEs clustered by security. Panel F removes one treated parent filer entity at a time; the CV3 p stays below .05 in 11 of 12 removals but not when T-Mobile is removed (p = .076). Panel G adds the four sensitivities (breach severity, flexible size, both, and a common-support sample), each with CV3 p below .05.',
    14: "Delay is the number of days from the breach date to the agency reporting date, with delays of −30 to −1 days, which arise from field-level errors, set to 0. Each row of Panel A regresses a delay outcome on the Form 499 registrant indicator and controls (N = 333, G = 82), with CV3 standard errors by parent filer entity. In all, 117 events have a zero delay (42 registrant, 75 other), because the source records the breach and its report on the same day or a small negative delay was set to 0. Uncapped rows use the delay as recorded; capped rows cap it at the 99th percentile (784.96 days), the disclosure gap of Table 2. The unadjusted difference in mean uncapped delay is 27.8 days; the capped difference in Table 2 is 12.13 days. Log rows use log(1 + delay) in Panel A and log(delay) on nonzero delays in Panel B, which drops the zero delays (216 events, 62 registrant). MDE80 is the minimum detectable effect at 80 percent power, in the units of the outcome. Panel C reports quantile regressions of the uncapped delay; at the 10th and 25th percentiles both groups' delays are 0, so those estimates are 0 by construction and carry no information. Panel D describes the uncapped delay by group. Panel E tests whether the groups' delays differ in spread or shape: the Brown–Forsythe test compares spread around each group's median, the Kolmogorov–Smirnov test compares whole distributions, and the log-rank test compares time to report. No test in the table gives a p-value below .05. CV1 and the wild cluster bootstrap are defined in Table 10.",
    15: 'Each row regresses the change in one trading-cost measure, its mean over trading days [+1, +20] after the agency reporting date minus its mean over [−60, −11], on the Form 499 registrant indicator, the M4 controls, and calendar-month fixed effects (N = 333, G = 82), with CV3 standard errors by parent filer entity. CPQS is the closing percent quoted spread, the ask minus the bid divided by the quote midpoint, from valid uncrossed closing quotes, with values above 0.5 set to missing (Chung & Zhang, 2014); it is a fraction and is shown to five decimals. EDGE is the efficient bid–ask spread estimator from open, high, low, and close prices (Ardia et al., 2024). OCAM is the open-to-close Amihud illiquidity measure, the absolute open-to-close return divided by dollar volume (Barardehi et al., 2021); its window means are winsorized at the 1st and 99th percentiles and logged. OCAM is biased toward zero in large stocks, where dollar volume is high. Each window needs trading on at least 80 percent of its days. The three measures form one family, and the BH-adjusted p applies the Benjamini–Hochberg adjustment within it; no measure gives p below .05 before or after adjustment. The last column is the Pearson correlation between the change in each measure and the change in abnormal return volatility; none exceeds .11 in absolute value, so trading costs and volatility move largely independently around the reporting date.',
    16: "Each row of Panel A re-estimates the primary model M4 within one quartile of log total assets (333 events in all), with CV3 standard errors clustered by parent filer entity; G is the number of parent filer entities in the cell, and p-values use the t distribution with that cell's G − 1 degrees of freedom. Registrant events concentrate at the top: Q4 holds 59 of 104, and Q1 rests on 2 registrant events at 1 parent filer entity, so its estimate compares one firm with the rest of the cell; Q1 omits the health-breach flag, which does not vary there. The four cells form one family, and the BH-adjusted p applies the Benjamini–Hochberg adjustment within it; the smallest BH-adjusted CV3 p is .535. Panel B asks whether any cell shows the effect to be negligible. A cell does so only if its 90 percent confidence interval lies inside ±0.191, the smallest effect size of interest (SESOI) from Table 11; no cell's interval does. MDE80, the minimum detectable effect at 80 percent power, runs from 0.821 to 2.632, or 4.30 to 13.80 times SESOI. Panel C shows p-values from procedures that understate clustering, to document over-rejection when few treated parents sit in a cell: HC1 and HC3 give p below .05 in 3 of the four cells, and CV3 in none. Q1 is the smallest quartile.",
    17: 'Each specification re-estimates the registrant coefficient of the primary model M4 (N = 333, G = 82) under one combination of five decisions: the pre-window, the post-window, the return benchmark, simple or log returns, and whether the outcome is winsorized at the 1st and 99th percentiles, for 3 × 4 × 3 × 2 × 2 = 144 specifications. Panel A summarizes the estimates for each option, pooling the specifications that use it, and counts those with p below .05 under CV3, the cluster jackknife standard error by parent filer entity, and under CV1, the cluster-robust standard error with the usual small-sample correction. All 144 estimates are positive, none is significant under either procedure, and the median estimate is 0.194. Panel B tests the whole curve by permutation (Simonsohn et al., 2020): in each of 1,000 draws, registration is reassigned at random to 12 of the 82 parent filer entities, and all 144 specifications are re-estimated. Each permutation p is the share of draws at least as extreme as the observed curve, for the median estimate, the count of estimates sharing the dominant sign, and the count significant in that direction under CV1; none is below .05. A curve of a single sign is common under the null here because every specification uses the same events, so the estimates move together: .283 of the null draws produce one.',
    18: "Each row re-estimates the registrant coefficient of the primary model M4 (N = 333, G = 82) with one change, with CV3 standard errors by parent filer entity. Panel A drops one parent filer entity at a time (82 re-estimates) and reports the smallest and largest estimates: dropping Sprint Corp (9 events) lowers the estimate to 0.029, removing 78.9 percent of it, and dropping Intuit Inc. (76 events) raises it to 0.213. Panel B drops the 18 events whose Cook's distance, a measure of how much all fitted values move when one observation is deleted, exceeds 4/N, and separately the 6 events reported before the rule took effect on December 8, 2007, none of them registrant events. Panel C adds fixed effects for reporting year, two-digit Standard Industrial Classification (SIC) industry, or both. A mixed stratum is a year, industry, or year-by-industry cell holding both registrant and other events; with fixed effects the coefficient is identified only within mixed strata, so events in single-group strata carry no weight (Aronow & Samii, 2016). Effective events counts the events in mixed strata, with registrant events in parentheses: year fixed effects leave 281, and both sets leave 109 events in 12 mixed cells. Industries with a single event drop as singletons (7 events). Panel D uses the revised reporting dates the source later published for 12 events and then corrects Sprint's breach date, which adds 1 event. No row gives a p-value below .05.",
    19: 'Each row is one family of tests in the analysis program, which holds 45 tests. A family is a set of tests addressing one question. Within each family of more than one test, p-values are adjusted by the Benjamini–Hochberg (BH) false-discovery-rate procedure; single checks and joint tests use their own reference distributions. The last column counts tests with p below .05, using the CV3 cluster jackknife standard error where the test has one. Five tests give p below .05. Three are in the announcement-window family, and two of them are calibration checks expected to reject on earnings dates (the earnings elevation and the breach-minus-earnings contrast). The other two are composition checks, which compare the size and pre-breach volatility of events that industry codes treat but Form 499 does not with registrant events the codes also treat (p = .003 and p < .001); neither tests registration. One test of registration rejects: the registrant coefficient on announcement elevation (p = .027, BH-adjusted p = .036). If every null hypothesis were true, about 45 × .05 = 2.25 tests would give p below .05 by chance.',
}


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
    n, nt, nc = s['events']
    g, gt, gc = s['parents']
    nb = Notes(1)
    ev = pd.read_csv(PANEL_CSV, dtype={'final_cik': str})
    both = ev[ev.final_cik.isin(s['both_parents']) & (ev.fcc_form499 == 0)]
    claim(sorted(both.org_name.unique()) == ['NBC Sports Group', 'Verizon Media'], 'other-side events are NBC Sports Group and Verizon Media')
    pn = parent_names()
    claim(sorted(pn[str(c)] for c in s['both_parents']) == ['Comcast Cable Communications LLC', 'Verizon'], 'both-group parents are Comcast and Verizon')
    first = att.iloc[0]
    n_rec = sum(1 for st_ in att.step if ATTRITION_LABELS[st_].startswith('Records:'))
    claim(all(ATTRITION_LABELS[st_].startswith('Records:') for st_ in att.step[:n_rec]), 'record rows come first')
    nb.w('four', n_rec, 'Panel A rows that count records')
    nb.i(first.N, '01, PRC universe / N')
    nb.i(first.N, '01, PRC universe / N')
    nb.w('three', len(rows_b), 'Panel B rows (levels)')
    nb.i(gt + gc, 'v5_event_panel.csv, distinct final_cik by group, summed')
    nb.i(g, 'constants values.ann_G')
    nb.c('years_single_kind', 'i')
    nb.c('years_single_kind_events', 'i')
    nb.c('years_single_kind_treated', 'i')
    nb.i(g, 'constants values.ann_G (= distinct final_cik in v5_event_panel.csv)')
    claim(len(one_group) == V('years_single_kind'), 'one-group years match the constants')
    note = nb.final()

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
    claim(V('desc_treated_health_breach_n') == 0 and V('desc_control_health_breach_n') == V('desc_full_health_breach_n'),
          'all health breaches are other events')
    cap = cell[('full', 'delay_w')]['max']
    nb.i(cell[('treated', 'dv')].N, '02A, treated / dv / N')
    nb.i(cell[('control', 'dv')].N, '02A, control / dv / N')
    nb.i(cell[('full', 'dv')].N, '02A, full / dv / N')
    nb.d('[+1, +20]', 'constants primary_outcome')
    nb.d('[\u221260, \u221211]', 'constants primary_outcome')
    nb.w('two', 2, 'design: the pre-window and post-window levels')
    nb.w('two', 2, 'design: the two groups compared')
    nb.d('.05', 'design: significance level')
    nb.p(dfx.loc['dv', 'p'], '02B, dv / p')
    nb.p(dfx.loc['pre_sd', 'p'], '02B, pre_sd / p')
    nb.p(dfx.loc['post_sd', 'p'], '02B, post_sd / p')
    nb.p(dfx.loc['delay_w', 'p'], '02B, delay_w / p')
    nb.d('1', 'design: indicator value')
    nb.c('desc_control_health_breach_n', 'i')
    nb.d('\u221230', 'scripts/156 (delay floor rule)')
    nb.d('\u22121', 'scripts/156')
    nb.d('0', 'scripts/156 (recoded value)')
    nb.d('99th', 'scripts/163 (P99 winsorization rule)')
    nb.f(cap, 2, '02A, full / delay_w / max (the P99 cap)')
    nb.r(cor.loc['fcc_form499', 'firm_size_log'], 2, '03, fcc_form499 x firm_size_log')
    note = nb.final()

    return render_table(2, 'Descriptive Statistics by Registration',
                        [('Dependent variable', hdr_ab, group_rows(DV_VARS)),
                         ('Controls', hdr_ab, group_rows(CONTROL_VARS)),
                         ('Correlations of model variables', hdr_c, rows_c, CORRELATION)], note)


RENDERERS.update({1: table_1, 2: table_2})


# ------------------------------------------------------------------ Set 2 shared
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
    claim(float(pair.value.iloc[0]) > float(pair.value.iloc[1]), 'the first 2024 event is the larger')
    for k_, (_, r) in enumerate(pair.iterrows()):
        rows_d.append(['Records in the larger 2024 event at one parent filer entity' if k_ == 0
                       else 'Records in the second 2024 event at that parent', fmt_int(r.value)])
    rows_d.append(['Records in both 2024 events of that parent',
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
    I_, IV_ = 'i_industry_codes_records', 'iv_dedup_form499'
    q1p = cell[(IV_, 'Q1')]
    claim(all(d_.startswith('2024') for d_ in pair.date), 'both largest-parent events are in 2024')
    nb.i(m.cellN, f'05A, {I_} / main / cellN')
    nb.d('4813, 4841, or 4899', 'scripts/269 section B (industry-code set)')
    nb.w('two', 2, 'design: Panels A and B')
    nb.i(cell[(IV_, 'main')].cellN, f'05A, {IV_} / main / cellN')
    nb.i(q1p.treatedN, f'05A, {IV_} / Q1 / treatedN')
    nb.i(q1p.t_parents, f'05A, {IV_} / Q1 / t_parents')
    nb.i(summ['events_with_more_than_one_record'], '05B, summary / events_with_more_than_one_record')
    nb.i(summ['events'], '05B, summary / events')
    nb.i(summ['records_in_multi_record_events'], '05B, summary / records_in_multi_record_events')
    nb.w('two', len(pair), '05B, largest / 2024 rows of the top parent (count)')
    nb.reg('2024', '05B, largest / year of those rows', '; '.join(pair.date))
    nb.i(sum(int(float(v_)) for v_ in pair.value), '05B, largest / two 2024 rows of that parent, summed')
    nb.i(g_tot, '09, TOTAL / n_specs')
    nb.i(g_per[0], '09, breach and notification / n_specs')
    nb.i(gg[gg.anchor == 'TOTAL'].q1_gt_q4.iloc[0], '09, TOTAL / q1_gt_q4')
    nb.i(gg[gg.anchor == 'TOTAL'].monotone_stepdown.iloc[0], '09, TOTAL / monotone_stepdown')
    note = nb.final()

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
        rows_b.append([f' of which {name}', fmt_int(len(g)), '',
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
    added_by = {str(pc): g for pc, g in added.groupby('parent_cik')}
    claim(all(o.startswith('GoDaddy') for o in added_by['1609711'].organization)
          and all(o.startswith('Twilio') for o in added_by['1447669'].organization), 'added records are GoDaddy and Twilio')
    nb.i(n_all, '08A, N summed over the four groups')
    nb.w('two', 2, 'design: the two treatment definitions')
    nb.d('4813, 4841, or 4899', 'scripts/269 section B')
    nb.c('disagree_records', 'i')
    nb.w('Twenty-eight', mi.N, '08A, missed_by_industry_codes / N')
    nb.w('three', 3, 'design: the three industry codes')
    nb.i(mi.orgs, '08A, missed_by_industry_codes / orgs')
    nb.i(gc.loc['misclassified_repaired'].N, '08A, misclassified_repaired / N')
    nb.reg(str(mr.source_sic.iloc[0]), '07, source_sic', ', '.join(sorted(set(str(x) for x in mr.source_sic))))
    claim(set(str(x) for x in mr.source_sic) == {'4813'}, 'both damaged entries are coded 4813')
    nb.i(q1n, '06A, N_records summed')
    nb.i(comp.loc['added'].N_records, '06A, added / N_records')
    nb.i(len(added_by['1609711']), '06B, added rows, parent_cik 1609711 (GoDaddy)')
    nb.i(len(added_by['1447669']), '06B, added rows, parent_cik 1447669 (Twilio)')
    nb.f(comp.loc['added']['mean'], 2, '06A, added / mean')
    nb.f(comp.loc['never_treated']['mean'], 2, '06A, never_treated / mean')
    nb.i(mi.N, '08A, missed_by_industry_codes / N')
    nb.c('q1_added_records', 'i')
    nb.c('missed_q4_records', 'i')
    nb.i(int(mi.N) - n_q1 - n_q4, '08A N minus constants q1_added_records and missed_q4_records')
    note = nb.final()

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
        rows_a.append([r.ticker_for_cik, fmt_int(len(orgs)), ex, fmt_int(r.n_records),
                       fmt_int(r.canonical_events_with_these_names),
                       'Yes' if r.legacy_cik_is_canonical_parent == 'True' else 'No'])
    if len(rows_a) != V('collision_sinks'):
        sys.exit('Table 5 Panel A: collision count disagrees with constants')
    hdr_a = ['Ticker on the identifier', 'Organizations absorbed', 'Examples', 'Records',
             'Canonical events with these names', 'Identifier is a current parent filer entity']

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
    rows_c = [[slab[k], fmt_num(r.slope, 2), fmt_num(r.intercept, 2), apa_share(r.R2),
               apa_share(r.share_within_010), apa_share(r.share_within_025)] for k, r in sv.iterrows()]
    hdr_c = ['Candidate measure', 'Slope', 'Intercept', 'R²', 'Share within 0.10',
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
    claim(all(str(x) == '0' for x in rt.has_crsp_data), 'none of the reused-ticker events has stock data')
    nn.c('collision_sinks', 'i')
    nn.c('collision_max_orgs', 'i')
    nn.i(big.n_records, '10A, n_records of the largest collision')
    nn.c('recycled_ticker_events', 'i')
    nn.reg(str(meta.ticker_end_for_assigned)[:4], '10B, META / ticker_end_for_assigned (year)', str(meta.ticker_end_for_assigned))
    nn.reg(str(dash.ticker_end_for_assigned)[:4], '10B, DASH / ticker_end_for_assigned (year)', str(dash.ticker_end_for_assigned))
    nn.i(len(rt), '10B, rows (has_crsp_data = 0 in all)')
    nn.w('two', len(sv), '10C, rows (candidate measures)')
    nn.c('sizerec_mktcap_slope', 'f', 2)
    nn.c('sizerec_mktcap_r2', 'r', 2)
    nn.c('sizerec_assets_slope', 'f', 2)
    nn.c('sizerec_assets_r2', 'r', 2)
    nn.d('0.10', 'scripts/269 (size reconciliation thresholds)')
    nn.d('0.25', 'scripts/269')
    nn.c('miss_base', 'i')
    nn.d('December 31, 2024', '01, step Notification on/before 2024-12-31')
    nn.i(tb, '01, Notification on/before 2024-12-31 / treated')
    nn.i(cb, '01, Notification on/before 2024-12-31 / control')
    nn.f(100 * prev[1] / tb, 1, '01, 104 / 111 x 100')
    nn.i(prev[1], '01, final row / treated')
    nn.i(tb, '01, 355 row / treated')
    nn.f(100 * prev[2] / cb, 1, '01, 229 / 244 x 100')
    nn.i(prev[2], '01, final row / control')
    nn.i(cb, '01, 355 row / control')
    note = nn.final()

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


# Plain-language basis for each adjudication rule (Tim, 2026-11-18), keyed by the committed pattern
# in committed order. The committed rule text stays in 13_treatment_adjudications.csv. Each FRN and
# filer ID quoted here is checked against the committed basis and the registry (12) in table_6().
BASIS_PLAIN = [
    ('Cricket', 'Clause (a): Cricket Communications holds its own registration (FRN 0004321139); the LLC name variant defeats exact matching.'),
    ('T-Mobile', 'Clause (a): the open registration "T-Mobile USA, Inc.- CONSOLIDATED" (filer 822060, active since 1997); the suffix defeats exact matching.'),
    ('Boost Mobile', 'Clause (b): prepaid wireless brand of Sprint Spectrum LLC (FRN 0006693022); subscriber data were breached.'),
    ('^Sprint', 'Clause (a): Sprint Spectrum LLC, doing business as Sprint (filer 811754), registered through 2024 and covering every Sprint breach date; name variants defeat exact matching.'),
    ('Verizon Media', 'Content division (Yahoo and AOL), not telecommunications subscriber operations.'),
    ('^Verizon', 'Clause (a): Verizon carrier filers (for example, Verizon New York, FRN 0003469442, through 2021, and consolidated successors after); consolidated names defeat exact matching.'),
    ('^Comcast|Comcast Cable', 'Clause (b): parent brand of the Comcast telephony filers.'),
    ('Charter Communication', 'Clause (b): parent brand of Charter Communications Operating LLC.'),
    ('Frontier Communications', 'Clause (b): parent of regional Form 499 filers.'),
    ('Altice USA', 'Clause (b): parent of the Altice Wireless filer.'),
    ('AT&T Services', 'Clause (b): part of the AT&T Inc. filing family.'),
    ('CenturyLink', 'Clause (b): CenturyLink and Lumen carrier family (regional local exchange carriers).'),
    ('DISH Network (on/after 2020-07-01)', 'Clause (b): a facilities-based wireless carrier after acquiring Boost Mobile on July 1, 2020; DISH Wireless L.L.C. (FRN 0027852722) and DISH Wireless Puerto Rico L.L.C. (FRN 0029666096) are open registrations on the breach dates.'),
    ('DISH Network', 'Satellite television is not a telecommunications service under \u00a7 64.2011, and DISH had no covered wireless operation before July 1, 2020.'),
    ('NBC Sports', 'No registry match; not a carrier.'),
    ('ATT-Breach Notification|ATT-SecurityBreach', 'Damaged source entries carrying a breach label in place of a firm name; stock data attach to AT&T, but treatment is excluded.'),
    ('NBCUniversal', 'Clause (a): NBCUniversal, LLC is itself a registered filer (FRN {nbcu_frn}).'),
    ('Mediacom', 'Clause (b): cable telephony operator and parent brand of the active filer MCC Telephony LLC.'),
    ('Cisco Systems', 'The holding link to Tropo LLC postdates the breaches: Cisco acquired Tropo in 2015, and the breaches occurred in 2012.'),
    ('Citrix', 'Enterprise-software incidents, not telecommunications subscriber operations; the 2018 event follows the divestiture of Citrix Online.'),
    ('^Google|Alphabet', 'Consumer web-service incidents with no Google Fiber subscriber data; clause (b) fails.'),
    ('^Time ?Warner', 'The 2006 breach did not involve telecommunications subscriber operations; the holding link to the HBO filer fails clause (b).'),
    ('Home Box Office', 'The HBO filer was terminated on December 31, 2012, before the 2017 breaches, so clause (a) fails on the breach date.'),
]


def plain_basis(st, reg):
    """Tim's plain-language basis, row by row; stops if a quoted identifier disagrees with the committed facts."""
    if [p for p, _ in BASIS_PLAIN] != list(st.pattern):
        sys.exit('Table 6 Panel B: plain-language basis rows do not match the committed rules in order')
    nb = reg[reg.legal_name == 'NBCUniversal, LLC'].FRN.unique()
    if len(nb) != 1:
        sys.exit('Table 6 Panel B: NBCUniversal, LLC FRN not unique in the registry')
    nbcu = str(nb[0])
    out = []
    for (pat, txt), (_, r) in zip(BASIS_PLAIN, st.iterrows()):
        txt = txt.format(nbcu_frn=nbcu)
        committed = r.basis
        for frn in re.findall(r'FRN (\d+)', txt):
            if len(frn) != 10 or frn not in set(reg.FRN.astype(str)):
                sys.exit(f'Table 6 Panel B: FRN {frn} ({pat}) is not a ten-digit registry FRN')
            if frn.lstrip('0') not in committed:
                sys.exit(f'Table 6 Panel B: FRN {frn} ({pat}) is not in the committed basis')
        for fid in re.findall(r'filer (\d{6})', txt):
            if f'499ID {fid}' not in committed:
                sys.exit(f'Table 6 Panel B: filer {fid} ({pat}) is not in the committed basis')
        out.append(txt)
    return out, nbcu


# ------------------------------------------------------------------ Table 6
def table_6():
    reg = appendix_csv('12_form499_registry_matches.csv')
    names = filer_names()
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
        rows_a.append([names[pc], pc, fmt_int(len(g)), fmt_int(g.FRN.nunique()), fmt_int(n_ebs),
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
    basis, _ = plain_basis(st, reg)
    lab_b = {'DISH Network (on/after 2020-07-01)': 'DISH Network (on or after July 1, 2020)'}   # Tim, 2026-11-18
    claim(set(lab_b) <= set(st.pattern), 'Table 6 relabel matches a committed pattern')
    rows_b = [[lab_b.get(r.pattern, r.pattern.replace('^', '').replace(' ?', ' ').replace('|', '; ')), ruling[r.direction], b_]
              for (_, r), b_ in zip(st.iterrows(), basis)]
    hdr_b = ['Organization name pattern', 'Ruling', 'Basis']
    rows_c = []
    for _, r in ep.iterrows():
        m_ = re.match(r'^(.+?) registrant has no equity; (?:\d{4} )?parent = (.+?)(?: [A-Z]{2,5})? \(', r.basis)
        if m_ is None:
            sys.exit(f'Table 6 Panel C: cannot read names from {r.basis!r}')
        rows_c.append([m_.group(1), r.pattern.split(' -> ')[0], m_.group(2), r.pattern.split(' -> ')[1]])
    hdr_c = ['Registrant', 'Registrant CIK', 'Parent filer entity assigned', 'Parent CIK']

    nb = Notes(6)
    dish = st[st.pattern.str.startswith('DISH')]
    claim(len(dish) == 2 and set(dish.direction) == {'FORCE TREATED', 'FORCE EXCLUDED'}, 'DISH has two rules')
    ebs = int((reg.end_before_start == 'True').sum())
    nb.i(len(order), '12, distinct parent_cik')
    nb.c('primary_treated', 'i')
    nb.c('registry_records', 'i')
    nb.c('registry_family_records', 'i')
    nb.i(ebs, '12, end_before_start == True')
    nb.c('adjudication_rules', 'i')
    nb.c('adjudication_names', 'i')
    nb.w('two', len(dish), '13, DISH Network rules')
    nb.d('July 1, 2020', '13, DISH rules (2020-07-01 divestiture date)')
    nb.c('equity_parent_maps', 'i')
    note = nb.final()

    return render_table(6, 'The Form 499 Registry: Treated Parent Filer Entities and Adjudication Rules',
                        [('Registry records matched to each treated parent filer entity', hdr_a, rows_a),
                         ('Adjudication rules', hdr_b, rows_b),
                         ('Equity re-parenting rules', hdr_c, rows_c)], note)


# ------------------------------------------------------------------ Table 7
FAILURE_LABEL = {'post-hoc; boundary-blind': 'chosen after examining the registry'}   # Tim, 2026-11-18


def table_7():
    cv = appendix_csv('14_sic_conventions_vs_form499.csv')
    claim(set(FAILURE_LABEL) <= set(cv.characteristic_failure), 'Table 7 relabel matches a committed label')
    er = appendix_csv('15_sic_convention_errors.csv')
    rows_a = []
    for _, r in cv.iterrows():
        lab, codes = CONV_LABEL[r.convention]
        rows_a.append([f'{lab} (SIC {codes})', fmt_num(r.agree_pct, 1), fmt_int(r.FP), fmt_int(r.FN),
                       fmt_int(r.parents_identified), fmt_int(r.parents_wrongly_included),
                       FAILURE_LABEL.get(r.characteristic_failure, r.characteristic_failure)])
    hdr_a = ['Convention (codes)', 'Event agreement, %', 'False positives', 'False negatives',
             'Treated parents identified', 'Other parents included', 'Characteristic failure']
    elab = {'FALSE_POSITIVE': 'False positive', 'FALSE_NEGATIVE': 'False negative'}
    rows_b = [[CONV_LABEL[r.convention][0], elab[r.error_type], r.organization, r.sich,
               fmt_int(r.events)] for _, r in er.iterrows()]
    hdr_b = ['Convention', 'Error', 'Organization', 'SIC', 'Events']

    nb = Notes(7)
    nt = int(cv.N_testable.iloc[0])
    claim(nt == V('sic_testable'), 'testable events match the constants')
    best = cv.sort_values('agree_pct').iloc[-1]
    claim(best.convention.startswith('tuned'), 'the tuned set has the highest agreement')
    pub = cv[cv.convention.str.startswith('published')].iloc[0]
    claim(int(pub.parents_identified) < min(int(x) for x in cv[cv.convention != pub.convention].parents_identified),
          'the published convention identifies the fewest registrant parents')
    nb.i(nt, '14, N_testable (= constants sic_testable)')
    nb.d('4812', 'scripts/269 CONV (published convention)')
    nb.d('4813', 'scripts/269 CONV (published convention)')
    nb.d('4813, 4841, and 4899', 'scripts/269 CONV (earlier specification)')
    nb.d('4800 to 4899', 'scripts/269 CONV (full range)')
    nb.d('4812, 4813, 4841, and 4899', 'scripts/269 CONV (tuned set)')
    nb.c('sic_treated_parents_testable', 'i')
    nb.f(best.agree_pct, 1, '14, tuned / agree_pct')
    nb.i(pub.parents_identified, '14, published / parents_identified')
    note = nb.final()

    return render_table(7, 'Industry-Code Conventions Against Form 499 Registration',
                        [('Agreement with Form 499 registration', hdr_a, rows_a),
                         ('Misclassified organizations', hdr_b, rows_b)], note)


# ------------------------------------------------------------------ Table 8
def table_8():
    ot = appendix_csv('16_treated_outside_comparison.csv')
    sv = appendix_csv('17_sich_vs_curated_sic.csv')
    rlab = {'no matched ticker': 'No matched ticker',
            'ticker but no Compustat row in 550-day window': 'Ticker, but no Compustat record in the prior 550 days'}
    rows_a = [[r.organization, r.reported_date, rlab[r.reason]] for _, r in ot.iterrows()]
    hdr_a = ['Organization', 'Reporting date', 'Reason']
    rows_b = [[r.organization, r.tickers, r.sich or '—', r.curated_sic or '—',
               'Registrant' if r.form499 == 'treated' else 'Not a registrant',
               'Yes' if r.sources_disagree == 'True' else 'No'] for _, r in sv.iterrows()]
    hdr_b = ['Organization', 'Tickers', 'Compustat SIC', 'Breach-record SIC', 'Form 499', 'Sources disagree']

    nb = Notes(8)
    claim(len(ot) == V('outside_treated') and ot.parent_cik.nunique() == V('outside_parents'), 'outside counts')
    claim(V('sic_treated_total') - V('sic_treated_testable') == V('outside_treated'), '118 - 107 = 11')
    n_noticker = int((ot.reason == 'no matched ticker').sum())
    claim(int(ot.organization.str.startswith('T-Mobile').sum()) == V('outside_tmobile'), 'T-Mobile count')
    nb.c('outside_treated', 'i')
    nb.c('outside_parents', 'i')
    nb.c('sic_treated_total', 'i')
    nb.c('sic_treated_testable', 'i')
    nb.i(n_noticker, '16, reason == no matched ticker')
    nb.d('550', 'scripts/163 sich rule (550-day window)')
    nb.i(len(ot) - n_noticker, '16, other reason')
    nb.c('outside_tmobile', 'i')
    nb.c('outside_treated', 'i')
    nb.d('550', 'scripts/163 sich rule')
    nb.w('two', 2, 'design: Compustat and breach-record sources')
    nb.c('sich_sources_disagree_treated', 'i')
    nb.c('sich_treated_parents', 'i')
    note = nb.final()

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
    nb.c('primary_N', 'i')
    nb.c('primary_treated', 'i')
    nb.c('primary_G', 'i')
    nb.c('primary_G1', 'i')
    nb.i(V('primary_G') - 1, 'constants primary_G - 1')
    nb.f(cell[('M4', 'fcc_form499')].coef, 3, '18, M4 / fcc_form499 / coef')
    nb.p(cell[('M4', 'fcc_form499')].p_cv3, '18, M4 / fcc_form499 / p_cv3')
    nb.r(first['M2'].r2, 3, '18, M2 / r2')
    nb.r(first['M3'].r2, 3, '18, M3 / r2')
    note = nb.final()

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
    claim(all(float(x) >= .05 for x in ld.p) and V('sic2_cluster_p_cv1') >= .05 and V('sic2_cluster_p_cv3') >= .05,
          'no procedure rejects')
    hc1, cv3 = V('primary_se_hc1'), V('primary_se_cv3')
    n_wild = int(ld.rung.str.startswith('W').sum())
    nb.f(r0.coef, 3, '19, coef')
    nb.i(r0.N, '19, N')
    nb.i(V('primary_G') - 1, 'constants primary_G - 1')
    nb.w('three', n_wild, '19, wild cluster rows')
    nb.d('99,999', '19, rung labels (B)')
    nb.w('six', 6, 'design: 19, rung label (Webb six-point)')
    nb.d('9,999', '19, rung labels (B)')
    nb.d('499', 'scripts/263 SEED')
    nb.f(hc1, 3, 'constants primary_se_hc1')
    nb.f(100 * (1 - hc1 / cv3), 0, 'constants 1 - primary_se_hc1 / primary_se_cv3 (x 100)')
    nb.f(cv3, 3, 'constants primary_se_cv3')
    nb.d('.05', 'design: significance level')
    nb.c('primary_G', 'i')
    nb.c('primary_G1', 'i')
    nb.c('primary_G_star', 'f', 1)
    nb.c('cluster_size_cv_ddof0', 'f', 2)
    nb.c('sic2_clusters', 'i')
    note = nb.final()

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
    nb.c('primary_N', 'i')
    nb.c('primary_G', 'i')
    nb.d('252', 'scripts/263 (trading days per year)')
    nb.d('0.25', 'scripts/263 design_resolution sesoi_mult')
    nb.f(dr.sd_control, 3, '20, sd_control')
    nb.f(dr.sesoi_daily, 3, '20, sesoi_daily')
    nb.f(dr.sesoi_ann, 2, '20, sesoi_ann')
    nb.w('two', 2, 'design: TOST (two one-sided tests)')
    nb.i(V('primary_G') - 1, 'constants primary_G - 1')
    nb.p(dr.tost_p_lower, '20, tost_p_lower')
    nb.p(dr.tost_p_upper, '20, tost_p_upper')
    nb.d('90', 'design: 90% interval matching TOST at 5%')
    nb.f(dr.ci90_lo, 3, '20, ci90_lo')
    nb.f(dr.ci90_hi, 3, '20, ci90_hi')
    nb.d('5', 'design: significance level (5 percent)')
    nb.f(V('sesoi_car_ann'), 2, 'constants sesoi_car_ann')
    nb.w('two', 2, 'design: literature (two-day announcement window of Cavusoglu et al., 2004; no committed computation)')
    nb.d('252', 'scripts/263 (trading days per year)')
    nb.f(V('sesoi_car_daily'), 3, 'constants sesoi_car_daily')
    nb.p(V('tost_car_p'), 'constants tost_car_p')
    nb.w('four', 4, 'design: 80 percent power (four in five)')
    nb.w('five', 5, 'design: 80 percent power (four in five)')
    nb.d('5', 'design: significance level (5 percent)')
    nb.f(V('dr_mde80_daily') / V('primary_se_cv3'), 2, 'constants dr_mde80_daily / primary_se_cv3')
    nb.f(dr.mde_over_sesoi, 2, '20, mde_over_sesoi')
    nb.c('mde80_hc3_pct_below_cv3', 'f', 0)
    nb.d('5', 'scripts/263 design_resolution target_ann')
    nb.i(dr.required_parents_5pp_ann, '20, required_parents_5pp_ann')
    nb.f(dr.floor_daily, 3, '20, floor_daily')
    nb.f(dr.floor_ann, 2, '20, floor_ann')
    note = nb.final()

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
            alab.append('Raw log returns, [−25, −5] vs. [+5, +25]')
        elif r.startswith('BRIDGE b'):
            alab.append('Raw log returns, [−25, −5] vs. [+5, +25], with the 80% rule')
        elif r.startswith('BRIDGE c'):
            alab.append('Market-adjusted simple returns, [−25, −5] vs. [+5, +25]')
        else:
            alab.append('Market-adjusted simple returns, [−60, −11] vs. [+1, +20] (primary)')
    rows_e = [[lab_, est(r), fmt_p(r.p_cv3), fmt_ci(r.ci3_lo, r.ci3_hi)] for lab_, (_, r) in zip(alab, alt.iterrows())]
    hdr_e = ['Specification', 'Estimate (CV3 SE)', 'p', '95% CI']

    nb = Notes(12)
    claim(all(float(x) >= .05 for x in list(dp_.p_cv3) + list(dp_.bh_adj_p) + list(dp_.p_wcr) + list(bm.p_cv3)
              + list(alt.p_cv3)), 'nothing rejects')
    mm = cv[cv.spec == 'mm'].iloc[0]
    claim(all(int(x) == int(mm.dropped) for x in cv[cv.spec.isin(['mm', 'ff3'])].dropped), 'mm and ff3 drop the same events')
    claim(all(int(x) == 0 for x in cv[cv.spec == 'market-adjusted'].dropped), 'the market-adjusted windows drop none')
    allc = ct[ct.group == 'all']
    nb.d('95', 'design: 95 percent confidence interval')
    nb.c('primary_N', 'i')
    nb.c('primary_G', 'i')
    for w_ in dp_.post_window:
        nb.reg('+' + re.search(r'\+(\d+)\]', str(w_)).group(1), '21, post_window (end)', str(w_))
    nb.d('[\u221260, \u221211]', 'constants primary_outcome')
    nb.w('three', len(dp_), '21, rows (family size)')
    nb.d('80', 'scripts/264 (coverage rule)')
    nb.d('[\u2212250, \u221230]', '22C reasons / scripts/263 EST_WIN')
    nb.i(mm.dropped, '22C, mm rows / dropped')
    nb.i(mm.dropped_treated, '22C, mm rows / dropped_treated')
    nb.d('80', 'scripts/264 (coverage rule)')
    nb.i(mm.surviving, '22C, mm / surviving')
    nb.r(allc[allc.definition == 'est_contaminated_by_notification'].share.iloc[0], 2, '22B, all / notification / share')
    nb.r(allc[allc.definition == 'est_contaminated_by_breach_date'].share.iloc[0], 2, '22B, all / breach date / share')
    nb.d('[\u221225, \u22125]', '23, bridge rows')
    nb.d('[+5, +25]', '23, bridge rows')
    nb.d('80', 'scripts/264 (coverage rule)')
    nb.d('\u221245', '23, ALT rows')
    nb.d('.05', 'design: significance level')
    note = nb.final()

    return render_table(12, 'Robustness of the Main Estimate',
                        [('Post-window length', hdr_a, rows_a), ('Return benchmark', hdr_b, rows_b),
                         ('Estimation-window contamination', hdr_c, rows_c),
                         ('Events dropped by the 80% coverage rule', hdr_d, rows_d),
                         ('Alternative pre-window and steps from the earlier outcome', hdr_e, rows_e)], note)


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
    fam = fam[fam.test.isin(list(tlab))]
    if len(fam) != 4:
        sys.exit('Table 13 Panel A: expected the four pre-specified tests')
    for _, r in fam.iterrows():
        lab_ = tlab[r.test]
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
    fn = filer_names()
    rows_f = [[fn[r.deleted_parent_cik], f'{fmt_int(r.deleted_events)} ({fmt_int(r.deleted_treated_events)})',
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
    claim(float(f4.p) < .05 and float(f4.bh_adj_p) < .05, 'the registrant test rejects after BH')
    claim(len(lad) == 8 and all(float(x) < .05 for x in lad.p), 'every procedure rejects')
    nrej = int((lo.rejects_05_cv3 == 'True').sum())
    claim(len(lo) - nrej == V('ann_lotpo_n_not_rejecting'), 'LOTPO non-rejections match constants')
    notrej = lo[lo.rejects_05_cv3 != 'True'].iloc[0]
    claim(notrej.deleted_parent.startswith('T-Mobile'), 'the non-rejecting removal is T-Mobile')
    claim(all(float(x) < .05 for x in se_.p_cv3), 'every sensitivity rejects under CV3')
    claim(V('ann_treated_minus_quiet') > 0 > V('ann_control_minus_quiet'), 'registrant above, other below quiet days')
    claim(int(float(pl.draws_abs_ge_actual.iloc[1])) == 0, 'no placebo draw matches the elevation coefficient')
    nb.w('nine', 9, 'design: scripts/265 ANN [-4, +4]')
    nb.d('[\u22124, +4]', 'scripts/265 ANN')
    nb.w('three', 3, 'design: scripts/265 BASE (21 trading days)')
    nb.d('[\u221225, \u22125]', 'scripts/265 BASE')
    nb.d('8', 'scripts/265 header (80% rule)')
    nb.d('9', 'scripts/265 header')
    nb.d('17', 'scripts/265 header')
    nb.d('21', 'scripts/265 header')
    nb.c('ann_N', 'i')
    nb.c('ann_G', 'i')
    nb.i(load_constants()['bh_families']['announcement_window'], 'constants bh_families.announcement_window')
    nb.w('two', 2, '24A, earnings calibration rows')
    nb.f(f4.coef, 3, '24A, Form 499 row / coef')
    nb.p(f4.p, '24A, Form 499 row / p')
    nb.p(f4.bh_adj_p, '24A, Form 499 row / bh_adj_p')
    nb.d('.05', 'design: significance level')
    nb.c('ann_share_closed_base', 'r', 2)
    nb.c('ann_share_closed_base_size', 'r', 2)
    nb.i(pl.draws.iloc[0], '24D, draws')
    nb.d('499', 'scripts/263 SEED')
    nb.d('120', 'scripts/265 header (eligibility)')
    nb.d('30', 'scripts/265 header')
    nb.i(pl.draws_abs_ge_actual.iloc[1], '24D, elevation / draws_abs_ge_actual')
    nb.i(pl.draws.iloc[1], '24D, draws')
    nb.c('ann_treated_minus_quiet', 'f', 3)
    nb.f(-V('ann_control_minus_quiet'), 3, 'constants values.ann_control_minus_quiet (magnitude; negative)')
    nb.d('.05', 'design: significance level')
    nb.i(nrej, '24F, rejects_05_cv3 == True')
    nb.i(len(lo), '24F, rows')
    nb.p(notrej.p_cv3, '24F, T-Mobile row / p_cv3')
    nb.w('four', len(se_) - 1, 'v5_t18b, sensitivity rows (excluding the base row)')
    nb.d('.05', 'design: significance level')
    note = nb.final()

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
def table_14():
    dl = appendix_csv('25A_disclosure_delay.csv')
    rows_a = []
    for (o, c), g in dl.groupby(['outcome', 'control'], sort=False):
        if c.startswith('BRIDGE'):
            continue
        cv3 = g[g.rung.str.startswith('CV3')].iloc[0]
        cv1 = g[g.rung.str.startswith('CV1')].iloc[0]
        wcr = g[g.rung.str.startswith('WCR restricted')].iloc[0]
        dp = 3 if o.startswith('log') else 2
        rows_a.append([DELAY_OUT[o], f'{fmt_num(cv3.coef, dp)} ({fmt_num(cv3.se, dp)})', fmt_p(cv3.p),
                       fmt_p(cv1.p), fmt_p(wcr.p), fmt_num(cv3.mde80_cv3, dp)])
    hdr_a = ['Outcome', 'Estimate (CV3 SE)', 'p', 'CV1 p', 'Wild cluster p', 'MDE80']

    nz = appendix_csv('25B_delay_nonzero.csv')
    rows_b = [[DELAY_OUT[r.outcome], f'{fmt_num(r.coef, 3 if "log" in r.outcome else 2)} '
               f'({fmt_num(r.se_cv3, 3 if "log" in r.outcome else 2)})', fmt_p(r.p_cv3), fmt_p(r.p_cv1),
               f'{fmt_int(r.N)} ({fmt_int(r.n_treated)})'] for _, r in nz.iterrows() if not r.control.startswith('BRIDGE')]
    hdr_b = ['Outcome', 'Estimate (CV3 SE)', 'p', 'CV1 p', 'N (registrant)']

    qt = appendix_csv('25C_delay_quantiles.csv')
    rows_c = []
    for q in sorted(set(qt.q), key=float):
        a_ = qt[(qt.q == q) & (qt.control == 'v5 control')].iloc[0]
        rows_c.append([f'{int(round(float(q) * 100))}th percentile', f'{fmt_num(a_.coef, 2)} ({fmt_num(a_.se, 2)})',
                       fmt_p(a_.p)])
    hdr_c = ['Quantile', 'Estimate (SE)', 'p']

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
    claim(all(float(x) >= .05 for x in list(dl.p) + list(nz.p_cv3) + list(nz.p_cv1) + list(qt.p)), 'no delay test rejects')
    claim(all(float(x) >= .05 for x in te.p if str(x).strip()), 'no distribution test rejects')
    for g_ in ('treated', 'control'):
        claim(float(ds.loc[g_, 'p10']) == 0 and float(ds.loc[g_, 'p25']) == 0, f'{g_} 10th and 25th percentiles are zero')
    q_lo = qt[(qt.control == 'v5 control') & qt.q.astype(float).isin([.1, .25])]
    claim(all(abs(float(x)) < 1e-4 for x in q_lo.coef), 'the 10th and 25th percentile estimates are 0')
    cap = appendix_csv('02A_descriptives_v5.csv')
    capv = cap[(cap.group == 'full') & (cap.variable == 'delay_w')]['max'].iloc[0]
    nb.d('\u221230', 'scripts/156')
    nb.d('\u22121', 'scripts/156')
    nb.d('0', 'scripts/156 (recoded value)')
    nb.c('primary_N', 'i')
    nb.c('primary_G', 'i')
    nb.c('delay_zero_events', 'i')
    nb.c('delay_zero_treated', 'i')
    nb.c('delay_zero_control', 'i')
    nb.d('0', 'scripts/156 (recoded value)')
    nb.d('99th', 'scripts/163 (P99 winsorization rule)')
    nb.f(capv, 2, '02A, full / delay_w / max')
    nb.c('delay_raw_unadjusted_diff', 'f', 1)
    nb.f(appendix_csv('02B_descriptives_v5_differences.csv').set_index('variable').loc['delay_w', 'diff'], 2, '02B, delay_w / diff')
    nb.d('log(1 + delay)', 'scripts/164 (log outcome)')
    nb.i(nz.N.iloc[0], '25B, N')
    nb.i(nz.n_treated.iloc[0], '25B, n_treated')
    nb.d('80', 'design: 80 percent power')
    nb.d('10th', '25C, q = 0.1')
    nb.d('25th', '25C, q = 0.25')
    nb.reg('0', '25D, treated and control p10 and p25', 0)
    nb.reg('0', '25C, v5 control q = 0.1 and 0.25 / coef (rounded)', 0)
    nb.d('.05', 'design: significance level')
    note = nb.final()

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
    mx = max(abs(float(x)) for x in sp.corr_with_primary_dv)
    claim(mx <= .11, 'no correlation exceeds .11 in absolute value')
    nb.d('[+1, +20]', 'scripts/268 header')
    nb.d('[\u221260, \u221211]', 'scripts/268 header')
    nb.i(r0.N, '26, N')
    nb.i(r0.G, '26, G')
    nb.d('0.5', 'scripts/268 header')
    nb.w('five', 5, 'design: CPQS shown to five decimals (scripts/274 Table 15)')
    nb.d('1st', 'scripts/268 header (winsorized 1/99)')
    nb.d('99th', 'scripts/268 header')
    nb.d('80', 'scripts/268 header')
    nb.w('three', len(sp), '26, rows (family size)')
    nb.d('.05', 'design: significance level')
    nb.r(mx, 2, '26, max |corr_with_primary_dv|')
    note = nb.final()

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
    claim(all(float(x) >= .05 for x in sq.p_cv3), 'CV3 rejects in no cell')
    q1 = sq.iloc[0]
    sesoi = float(ci.iloc[0].sesoi)
    n_hc1 = sum(1 for q in sq.quartile if float(lad[(lad.quartile == q) & lad.rung.str.startswith('HC1')].p.iloc[0]) < .05)
    n_hc3 = sum(1 for q in sq.quartile if float(lad[(lad.quartile == q) & lad.rung.str.startswith('HC3')].p.iloc[0]) < .05)
    claim(n_hc1 == n_hc3, 'HC1 and HC3 reject in the same number of cells')
    claim(int(sq.iloc[3].treated_events) == max(int(x) for x in sq.treated_events), 'Q4 holds the most registrant events')
    nb.c('primary_N', 'i')
    nb.d('G \u2212 1', 'design: cell degrees of freedom (v5_t18c df = G - 1)')
    nb.i(sq.iloc[3].treated_events, '27A, Q4 / treated_events')
    nb.c('primary_treated', 'i')
    nb.i(q1.treated_events, '27A, Q1 / treated_events')
    nb.i(q1.treated_parents, '27A, Q1 / treated_parents')
    nb.w('four', len(sq), '27A, rows (family size)')
    nb.c('q_min_bh_p_cv3', 'p')
    nb.d('90', 'design: 90 percent interval (equivalence at 5 percent)')
    nb.f(sesoi, 3, 'v5_t18c, sesoi (= constants dr_sesoi_daily)')
    nb.d('80', 'design: 80 percent power')
    nb.c('q_mde_min', 'f', 3)
    nb.c('q_mde_max', 'f', 3)
    nb.c('q_mde_min_x_sesoi', 'f', 2)
    nb.c('q_mde_max_x_sesoi', 'f', 2)
    nb.d('.05', 'design: significance level')
    nb.i(n_hc1, '27B, HC1 and HC3 rows with p < .05 (count)')
    nb.w('four', len(sq), '27A, rows')
    note = nb.final()
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
    claim((sc.p_cv3 < .05).sum() == V('spec_cv3_sig') == 0 and (sc.p_cv1 < .05).sum() == V('spec_sig_cv1_any') == 0
          and (sc.coef > 0).sum() == V('spec_positive') == len(sc), 'none significant, all positive')
    claim(set(sc.winsor) == {'raw', 'w1_99'}, 'the fifth decision winsorizes the outcome at 1/99 (scripts/266 lines 65-67)')
    claim(all(float(x) >= .05 for x in pm.perm_p), 'no permutation p below .05')
    nb.c('primary_N', 'i')
    nb.c('primary_G', 'i')
    nb.w('five', len(NODE), '29A, decisions')
    nb.d('1st', 'scripts/266 WINS (w1_99)')
    nb.d('99th', 'scripts/266 WINS (w1_99)')
    for x, k in zip(sizes, NODE):
        nb.i(x, f'29A, distinct {k}')
    nb.c('spec_n', 'i')
    nb.d('.05', 'design: significance level')
    nb.c('spec_positive', 'i')
    nb.c('spec_median', 'f', 3)
    nb.c('spec_perm_draws', 'i')
    nb.c('primary_G1', 'i')
    nb.c('primary_G', 'i')
    nb.c('spec_n', 'i')
    nb.d('.05', 'design: significance level')
    nb.r(V('perm_unanimous_share'), 3, 'constants perm_unanimous_share')
    note = nb.final()

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
    fn = filer_names()   # treated parents carry their filer name (Tim, 2026-11-18)
    lp['parent'] = [fn.get(str(c), p_) for c, p_ in zip(lp.final_cik, lp.parent)]
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
    claim(len(lp) == V('primary_G'), 'one re-estimate per parent')
    claim(V('prerule_treated') == 0, 'no pre-rule event is a registrant event')
    nb.c('primary_N', 'i')
    nb.c('primary_G', 'i')
    nb.i(len(lp), '30A, rows (re-estimates)')
    nb.reg(mn.parent, '30A, smallest coef_without / final_cik -> parent_filer_names.csv', mn.parent)
    nb.i(mn.events, '30A, that row / events')
    nb.f(lo_.coef, 3, '30B, LOPO minimum / coef')
    nb.c('sprint_share_removed', 'pct', 1)
    nb.reg(mx.parent, '30A, largest coef_without / parent', mx.parent)
    nb.i(mx.events, '30A, that row / events')
    nb.f(hi_.coef, 3, '30B, LOPO maximum / coef')
    nb.c('cook_removed', 'i')
    nb.d('4/N', '30B, Cook row (D > 4/N)')
    nb.c('prerule_events', 'i')
    nb.d('December 8, 2007', '30B / scripts/269 (2007-12-08)')
    nb.i(yr.effective_obs, '31, year FE / effective_obs')
    nb.i(fe.iloc[2].effective_obs, '31, year + industry / effective_obs')
    nb.i(fe.iloc[2].mixed_strata, '31, year + industry / mixed_strata')
    nb.i(fe.iloc[1].singletons_dropped, '31, industry / singletons_dropped')
    nb.i(v4.iloc[1].events_changed, '32, revised-dates row / events_changed')
    nb.i(v4.iloc[2].events_changed, '32, Sprint row / events_changed')
    nb.d('.05', 'design: significance level')
    note = nb.final()

    return render_table(18, 'Sensitivity of the Main Estimate',
                        [('Leaving out one parent filer entity', hdr_a, rows_a), ('Influential and pre-rule events', hdr_b, rows_b),
                         ('Fixed effects and effective samples', hdr_c, rows_c), ('Revised dates', hdr_d, rows_d)], note)


# ------------------------------------------------------------------ Table 19
FAMILY_LAB = {
    'A2-delay': 'Disclosure delay', 'A2-delay-nz': 'Disclosure delay, nonzero', 'B2': 'Records per event and firm size',
    'B2b': 'Industry-code-only group comparisons', 'poscontrol': 'Positive control (earnings decline)',
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


QUERY4 = ROOT / 'outputs' / 'ESSAY2_QUERY4_PARTS_ACJ.md'   # committed log of scripts/164
QUERY6 = ROOT / 'outputs' / 'ESSAY2_QUERY6_REPORT.md'      # committed log of scripts/174


def _find(text, pat, what):
    m = re.search(pat, text)
    if m is None:
        sys.exit(f'kept-test result not found ({what}): {pat}')
    return m


def kept_results():
    """Committed p-values (or 95% CIs) of the 23 tests kept from the earlier ledger, by family.

    Each entry: (family, test, p or None, ci or None, source). A test counts as p < .05 when its p is
    below .05 or, where only a CI is committed, when the CI excludes 0.
    """
    a = appendix_csv
    q4 = QUERY4.read_text(encoding='utf-8')
    q6 = QUERY6.read_text(encoding='utf-8')
    out = []
    dl = a('25A_disclosure_delay.csv')
    for o in ['delay (raw days)', 'delay (winsorized p99)', 'log(1+delay)']:
        r = dl[(dl.outcome == o) & (dl.control.str.startswith('v5')) & dl.rung.str.startswith('CV3')].iloc[0]
        out.append(('A2-delay', f'OLS {o}', float(r.p), None, '25A, current controls, CV3'))
    te = a('25E_delay_distribution_tests.csv').set_index('test')
    out.append(('A2-delay', 'Brown-Forsythe, all delays', float(te.loc['Brown-Forsythe, all delays', 'p']), None, '25E'))
    qt = a('25C_delay_quantiles.csv')
    for _, r in qt[qt.control == 'v5 control'].iterrows():
        out.append(('A2-delay', f'quantile q={r.q}', float(r.p), None, '25C, current controls'))
    m = _find(q4, r'Kaplan-Meier time-to-notification.*?log-rank chi2=[\d.]+ \(p=([\d.]+)\)', 'log-rank, all delays')
    out.append(('A2-delay', 'log-rank, all delays', float(m.group(1)), None, QUERY4.name + ' (Kaplan-Meier line)'))
    m = _find(q4, r'KS test of distributional equality: D=[\d.]+ \(p=([\d.]+)\)', 'KS, all delays')
    out.append(('A2-delay', 'KS, all delays', float(m.group(1)), None, QUERY4.name))
    nz = a('25B_delay_nonzero.csv')
    for _, r in nz[nz.control.str.startswith('v5')].iterrows():
        out.append(('A2-delay-nz', f'OLS nonzero {r.outcome}', float(r.p_cv3), None, '25B, current controls, CV3'))
    for t in ['Brown-Forsythe, non-zero', 'KS, non-zero', 'log-rank, non-zero']:
        out.append(('A2-delay-nz', t, float(te.loc[t, 'p']), None, '25E'))
    for lab_, pat in [('records-per-event ~ log assets', r'records-per-event ~ ln\(assets\):.*?95% CI \[([-+\d.]+), ([-+\d.]+)\]'),
                      ('records-per-event ~ log mktcap', r'records-per-event ~ ln\(mktcap\):.*?95% CI \[([-+\d.]+), ([-+\d.]+)\]')]:
        m = _find(q4, pat, lab_)
        out.append(('B2', lab_, None, (float(m.group(1)), float(m.group(2))), QUERY4.name + ' (B2)'))
    m = _find(q4, r'ln\(assets\) t=[-+\d.]+ \(p=([\d.]+)\); pre-breach volatility t=[-+\d.]+ \(p=([\d.]+)\)', 'B2b Welch')
    out.append(('B2b', 'size: industry-code-only vs concordant registrants', float(m.group(1)), None, QUERY4.name + ' (B2b Welch)'))
    out.append(('B2b', 'pre-vol: industry-code-only vs concordant registrants', float(m.group(2)), None, QUERY4.name + ' (B2b Welch)'))
    m = _find(q4, r'size manufactured-vs-concordant t=[-+\d.]+ \(p=([\d.]+)\)', 'B2b old size')
    out.append(('B2b', 'earlier data: size', float(m.group(1)), None, QUERY4.name + ' (B2b, earlier data)'))
    m = _find(q4, r'Volatility change, manufactured-vs-control: t=[-+\d.]+ \(p=([\d.]+)', 'B2b old vol-change')
    out.append(('B2b', 'earlier data: volatility change', float(m.group(1)), None, QUERY4.name + ' (B2b, earlier data)'))
    m = _find(q6, r'Year-FE constant.*?95% CI \[([-+\d.]+), ([-+\d.]+)\]', 'earnings decline')
    out.append(('poscontrol', 'earnings decline', None, (float(m.group(1)), float(m.group(2))), QUERY6.name))
    return out


def _sig(e):
    _, _, p_, ci_, _ = e
    return (p_ < .05) if p_ is not None else (ci_[0] > 0 or ci_[1] < 0)


def table_19():
    en = appendix_csv('33A_program_test_enumeration.csv')
    live = en[~en.v5_status.str.startswith('RETIRED')]
    bh = load_constants()['bh_families']
    rej = _v5_rejections()
    kr = kept_results()
    kept_n = {f: sum(1 for e in kr if e[0] == f) for f in {e[0] for e in kr}}
    rows_a = []
    for fam_, g in live.groupby('family', sort=False):
        kept = g.v5_status.iloc[0].startswith('KEPT')
        if kept and kept_n.get(fam_) != len(g):
            sys.exit(f'Table 19: {fam_} has {len(g)} kept tests but {kept_n.get(fam_)} committed results')
        if kept:
            rej[fam_] = sum(1 for e in kr if e[0] == fam_ and _sig(e))
        bhs = bh.get(BH_KEY.get(fam_, ''), None)
        rows_a.append([FAMILY_LAB[fam_], fmt_int(len(g)), fmt_int(bhs) if bhs else '—', fmt_int(rej[fam_])])
    rows_a.append(['All tests', fmt_int(len(live)), '', fmt_int(sum(rej.values()))])
    hdr_a = ['Family', 'Tests', 'BH family size', 'p < .05']

    nb = Notes(19)
    claim(len(live) == V('program_tests_total'), 'live tests = 45')
    new_fams = [f for f in rej if f not in kept_n]
    n_new = sum(rej[f] for f in new_fams)
    n_kept = sum(rej[f] for f in kept_n)
    claim(n_new == V('program_rejections_cv3'), 'new-test rejections match constants')
    claim(rej['announcement family'] == n_new, 'every new rejection is in the announcement-window family')
    kept_sig = [e for e in kr if _sig(e)]
    claim([e[0] for e in kept_sig] == ['B2b', 'B2b'], 'the kept rejections are the two B2b composition checks')
    claim(len(kr) == V('program_tests_kept_from_t53'), 'kept results cover the 23 kept tests')
    fa = appendix_csv('24A_announcement_family.csv').iloc[3]
    nb.c('program_tests_total', 'i')
    nb.d('.05', 'design: significance level')
    nb.w('Five', n_new + n_kept, 'new rejections (constants program_rejections_cv3) + kept rejections (committed logs)')
    nb.d('.05', 'design: significance level')
    nb.w('Three', rej['announcement family'], '24A, announcement family rows with p < .05')
    nb.w('two', V('program_rejections_cv3') - V('program_rejections_cv3_excl_calibration'),
         'constants program_rejections_cv3 - program_rejections_cv3_excl_calibration')
    nb.w('two', n_kept, 'kept tests with p < .05 (ESSAY2_QUERY4_PARTS_ACJ.md, B2b Welch line)')
    nb.p(kept_sig[0][2], kept_sig[0][4] + ': ' + kept_sig[0][1])
    nb.p(kept_sig[1][2], kept_sig[1][4] + ': ' + kept_sig[1][1])
    nb.w('One', V('program_rejections_cv3_excl_calibration'), 'constants program_rejections_cv3_excl_calibration')
    nb.p(fa.p, '24A, Form 499 row / p')
    nb.p(fa.bh_adj_p, '24A, Form 499 row / bh_adj_p')
    nb.c('program_tests_total', 'i')
    nb.d('.05', 'design: significance level')
    nb.f(V('program_tests_total') * .05, 2, 'constants program_tests_total x .05')
    nb.d('.05', 'design: significance level')
    note = nb.final()

    return render_table(19, 'Test Program Summary', [('Test families', hdr_a, rows_a)], note)


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


FILER_CSV = V5 / 'parent_filer_names.csv'


def _name_key(s):
    s = re.sub(r'/[A-Z]{2}/', '', str(s).upper())
    s = s.replace('CORPORATION', 'CORP')
    return re.sub(r'[^A-Z0-9&]', '', s)


def emit_parent_filer_names():
    """Filer name for each treated parent CIK (Tables 6 Panel A and 13 Panel F).

    Reads committed Data/: the registrant name (conml) that Compustat's company file
    (Data/wrds_v4/comp_company.csv, scripts/211) records for the CIK. Gated: one name per CIK,
    every CIK covered, and the name must agree with the SEC company_tickers.json title wherever
    the SEC file still lists the CIK (it omits delisted filers).
    """
    import json
    ciks = sorted({str(c) for c in appendix_csv('12_form499_registry_matches.csv').parent_cik}
                  | {str(c) for c in appendix_csv('24F_announcement_lotpo.csv').deleted_parent_cik}, key=int)
    cc = pd.read_csv(ROOT / 'Data/wrds_v4/comp_company.csv', dtype=str, keep_default_na=False)
    cc['c'] = cc.cik.str.lstrip('0')
    sec = {}
    for v in json.load(open(ROOT / 'Data/edgar/company_tickers.json', encoding='utf-8')).values():
        sec.setdefault(str(v['cik_str']), set()).add(v['title'])
    rows = []
    for c in ciks:
        nm = set(cc.loc[cc.c == c, 'conml'])
        if len(nm) != 1:
            sys.exit(f'parent filer names: CIK {c} has {len(nm)} Compustat names')
        nm = nm.pop()
        st = sec.get(c, set())
        if any(_name_key(t) != _name_key(nm) for t in st):
            sys.exit(f'parent filer names: CIK {c} {nm!r} disagrees with SEC {st}')
        rows.append(dict(cik=c, filer_name=nm, sec_tickers_title='; '.join(sorted(st))))
    pd.DataFrame(rows).to_csv(FILER_CSV, index=False, lineterminator='\n', encoding='utf-8')
    print(f'wrote {FILER_CSV.relative_to(ROOT)}: {len(rows)} CIKs '
          f'({sum(1 for r in rows if r["sec_tickers_title"])} confirmed in the SEC ticker file)')


FORMER_NAME = {'18926': ('Lumen Technologies Inc', 'CenturyLink')}   # Tim, 2026-11-18


def filer_names():
    if not FILER_CSV.exists():
        sys.exit(f'missing committed source {FILER_CSV.relative_to(ROOT)} (run --parent-names)')
    out = {r.cik: r.filer_name for _, r in read_csv(FILER_CSV).iterrows()}
    for c, (cur, old) in FORMER_NAME.items():
        claim(out.get(c) == cur, f'CIK {c} filer name is {cur}')
        out[c] = f'{cur} (formerly {old})'
    return out


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
    g.add_argument('--parent-names', action='store_true',
                   help=f'write {FILER_CSV.name} (reads committed Data/wrds_v4 and Data/edgar)')
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
    elif a.parent_names:
        emit_parent_filer_names()
    elif a.constants:
        emit_constants()
    elif a.layout:
        print_layout()
    else:
        write_set(a.set_n, docx_too=a.docx)


if __name__ == '__main__':
    main()
