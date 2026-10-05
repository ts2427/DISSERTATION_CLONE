"""
ESSAY 3 APPENDIX SUPPLEMENT - Tables 12-15 and a provenance note to Table 5
==========================================================================
scripts/245 writes Appendix Tables 1-11 (outputs/essay3_appendix/ESSAY3_APPENDIX_TABLES.md).
This script ADDS tables after them and does not touch 245 or anything it writes. Every value
is read from a committed output; nothing is estimated here.

  Table 12  Randomization inference (parent-CIK reassignment)     defense_supplement/e3_randomization_inference.csv
  Table 13  Chief-executive departures: counts only                essay3_v4/f5_ceo.csv
  Table 14  Director-only departures: descriptive counts           essay3_v4/f6_director.csv
  Table 15  T-Mobile: the four in-window executive departures and
            the placebo-window succession filing                   essay3_v4/g6_case_table.csv,
                                                                   essay3_q4/tmobile_502_text.md
  Note to Table 5  which classifier the recall audit scored        scripts/195, 220, 201; constants

Table 15 quotes the filings verbatim and reports no classifier context flags: the classifier's
"health" flag on the Ray and Ewens filings is a known false positive, so the stated context is
given in the filing's own words only.

The Table 5 note is not typed in: this script checks that the recall audit (scripts/201) scored
scripts/195, that the 15 classifier functions in scripts/220 (the v4 chain) are identical to
195's by AST, and that the v4 constants name the same classifier - and stops if any check fails.

Outputs: outputs/essay3_appendix/ESSAY3_APPENDIX_SUPPLEMENT.md and supp_table12..15_*.csv
"""

import ast
import json
import re
import subprocess
import sys
from pathlib import Path

import pandas as pd

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
V4 = Path('outputs/essay3_v4')
APP = Path('outputs/essay3_appendix')
C = json.loads((V4 / 'constants_essay3_v4.json').read_text())
N, NT, NC, G, G1 = C['N'], C['treated'], C['control'], C['parent_ciks'], C['treated_parent_ciks']
assert (N, NT, NC, G, G1) == (405, 109, 296, 119, 13), f'Essay 3 sample {(N, NT, NC, G, G1)}'


def p3(x):
    """p-value, no leading zero."""
    return '< .001' if float(x) < 0.001 else f'{float(x):.3f}'.lstrip('0')


def pp(x, d=1):
    return f'{100 * float(x):+.{d}f}'.replace('-', '−')


def md_table(df):
    out = ['| ' + ' | '.join(df.columns) + ' |', '|' + '---|' * len(df.columns)]
    out += ['| ' + ' | '.join(str(v) for v in r) + ' |' for r in df.itertuples(index=False)]
    return out


L = ['# Essay 3 — Appendix Tables, Supplement (Tables 12–15)', '',
     'Written by `scripts/256_essay3_appendix_supplement.py` from committed outputs. These tables follow '
     'Appendix Tables 1–11 (`ESSAY3_APPENDIX_TABLES.md`, written by `scripts/245`), which are unchanged. '
     f'Analysis sample throughout: N = {N} events ({NT} treated events at {G1} treated parent CIKs; '
     f'{NC} control events; {G} parent-CIK clusters).', '']

# ------------------------------------------------------------------ Note to Table 5
def funcs(p):
    return {n.name: ast.dump(n) for n in ast.walk(ast.parse(Path(p).read_text(encoding='utf-8')))
            if isinstance(n, ast.FunctionDef)}


f195, f220 = funcs('scripts/195_essay3_q2_classifier_v2.py'), funcs('scripts/220_essay3_v4_classifier_v2.py')
assert set(f195) == set(f220) and all(f195[k] == f220[k] for k in f195), \
    'STOP: scripts/220 classifier functions differ from scripts/195 - the recall audit may not apply to v4'
src201 = Path('scripts/201_essay3_q2_recall_audit_scoring.py').read_text(encoding='utf-8')
assert "scripts/195_essay3_q2_classifier_v2.py" in src201, 'STOP: scripts/201 does not load scripts/195'
blob195 = subprocess.run(['git', 'hash-object', 'scripts/195_essay3_q2_classifier_v2.py'],
                         capture_output=True, text=True).stdout.strip()[:7]
m = re.search(r'scripts/195 v2 \((\w+), blob (\w+)\)', C['classifier'])
assert m, f'unexpected classifier string in constants: {C["classifier"]}'
assert blob195 == m.group(2), f'STOP: scripts/195 blob {blob195} != v4 constants {m.group(2)}'
L += ['## Note to Table 5 (Classifier Validation)', '',
      f'The recall audit in Table 5 (source: `outputs/essay3_q2/d3_audit_recall_by_stratum.csv`, written by '
      f'`scripts/201`) scored classifier v2, `scripts/195` at commit `{m.group(1)}` (blob `{blob195}`). That is '
      f'the classifier the v4 chain uses: the v4 constants name it, and the {len(f195)} classifier functions in '
      f'`scripts/220` are identical to those in `scripts/195`. The audit file sits in the earlier build\'s folder '
      f'because the audit was drawn and scored once, before the v4 relink; the relink changed the sample, not '
      f'the classifier.', '']

# ------------------------------------------------------------------ Table 12: randomization inference
ri = pd.read_csv('outputs/defense_supplement/e3_randomization_inference.csv')
assert set(ri['N']) == {N} and set(ri['G']) == {G} and set(ri['G1']) == {G1}, 'RI file is not the v4 sample'
assert set(ri['treated_events_obs']) == {NT}
WIN = {'exec_departure_30_rd': '30 days', 'exec_departure_90_rd': '90 days',
       'exec_departure_180_rd': '180 days', 'placebo_exec_departure_rd': 'Placebo (180 days before)'}
VAR = {'C1 all parents': 'All parent CIKs', 'C3 size-matched parents': 'Size-matched parent CIKs'}
assert set(ri['outcome']) == set(WIN) and set(ri['variant']) == set(VAR)
t12 = pd.DataFrame({
    'Outcome window': ri['outcome'].map(WIN), 'Reassignment pool': ri['variant'].map(VAR),
    'Eligible parent CIKs': ri['n_eligible_parents'].astype(int),
    'Coefficient (pp)': ri['coef_obs'].map(pp), 'CV3 t': ri['cv3_t_obs'].map(lambda v: f'{v:+.2f}'.replace('-', '−')),
    'RI p (coefficient)': ri['ri_p_coef'].map(p3), 'RI p (CV3 t)': ri['ri_p_t'].map(p3)})
d = ri.drop_duplicates('variant')
t12b = pd.DataFrame({
    'Reassignment pool': d['variant'].map(VAR), 'Minimum': d['te_min'].astype(int),
    '5th pct.': d['te_p5'].round().astype(int), '25th pct.': d['te_p25'].round().astype(int),
    'Median': d['te_median'].round().astype(int), '75th pct.': d['te_p75'].round().astype(int),
    '95th pct.': d['te_p95'].round().astype(int), 'Maximum': d['te_max'].astype(int),
    'Mean': d['te_mean'].map(lambda v: f'{v:.1f}'),
    f'Share of draws with ≥ {NT} treated events': d['share_draws_te_ge_obs'].map(lambda v: f'{100 * v:.1f}%')})
B, seed = int(ri['B'].iloc[0]), int(ri['seed'].iloc[0])
tot = int(ri['treated_events_obs_parents_total'].iloc[0])
L += ['**Table 12**', '', '*Randomization Inference: Reassigning Treatment Across Parent CIKs*', '',
      '**Panel A: Randomization p-values**', ''] + md_table(t12) + ['',
      '**Panel B: Treated events per draw**', ''] + md_table(t12b) + ['',
      f'*Note.* Each draw selects {G1} of the eligible parent CIKs at random, treats all of their events, and '
      f're-estimates the specification of Table 7; {B:,} draws, seed {seed}. The randomization p-value is the '
      f'share of draws whose statistic is at least as large in absolute value as the observed one, computed for '
      f'the coefficient and for the CV3 t-statistic. The size-matched pool keeps parent CIKs whose event count '
      f'lies within the range of the observed treated parents. The observed design has {NT} treated events; the '
      f'{G1} treated parent CIKs hold {tot} events in total because some have untreated events, and each draw '
      f'treats every event of a selected parent. Treated events are concentrated in a few large parents, so '
      f'few draws reach the observed treated-event count (Panel B); the CV3 t-statistic accounts for that, the '
      f'raw coefficient does not. Coefficients are percentage points. '
      f'Source: `outputs/defense_supplement/e3_randomization_inference.csv` (`scripts/250`).', '']
t12.to_csv(APP / 'supp_table12_randomization_inference.csv', index=False, lineterminator='\n')

# ------------------------------------------------------------------ Table 13: CEO departures (counts only)
ceo = pd.read_csv(V4 / 'f5_ceo.csv')
assert not ceo['estimated'].any(), 'f5_ceo reports an estimated window; Table 13 is counts-only'
assert set(ceo['treated_n']) == {NT} and set(ceo['control_n']) == {NC}
t13 = pd.DataFrame({
    'Window': ceo['window'].map(lambda w: f'{int(w)} days'),
    f'Treated events with a CEO departure (of {NT})': ceo['treated_events'].astype(int),
    f'Control events with a CEO departure (of {NC})': ceo['control_events'].astype(int),
    'Treated rate': (100 * ceo['treated_events'] / ceo['treated_n']).map(lambda v: f'{v:.1f}%'),
    'Control rate': (100 * ceo['control_events'] / ceo['control_n']).map(lambda v: f'{v:.1f}%')})
L += ['**Table 13**', '', '*Chief Executive Departures by Window: Counts Only*', ''] + md_table(t13) + ['',
      f'*Note.* Not estimated. The estimation script fits a chief-executive model only when each group has at '
      f'least ten chief-executive departures in the window, and no window meets that (committed reason: '
      f'"{ceo["reason"].iloc[0]}"). The '
      f'chief-executive field also validates poorly (Table 5), which is a second reason to report counts '
      f'rather than estimates. Rates are counts divided by group size. Source: `outputs/essay3_v4/f5_ceo.csv` '
      f'(`scripts/227`).', '']
t13.to_csv(APP / 'supp_table13_ceo_departure_counts.csv', index=False, lineterminator='\n')

# ------------------------------------------------------------------ Table 14: director-only departures
dr = pd.read_csv(V4 / 'f6_director.csv')
t14 = pd.DataFrame({
    'Window': dr['window'].map(lambda w: f'{int(w)} days'),
    f'Treated events with a director-only departure (of {NT})': dr['treated_events'].astype(int),
    f'Control events with a director-only departure (of {NC})': dr['control_events'].astype(int),
    'Treated rate': (100 * dr['treated_events'] / NT).map(lambda v: f'{v:.1f}%'),
    'Control rate': (100 * dr['control_events'] / NC).map(lambda v: f'{v:.1f}%')})
L += ['**Table 14**', '', '*Director-Only Departures by Window: Descriptive Counts*', ''] + md_table(t14) + ['',
      '*Note.* Descriptive only; no model is fitted and no test is reported. A director-only departure is an '
      'Item 5.02 departure of a board member who is not also an executive officer; it is outside the outcome '
      'of H6. Rates are counts divided by group size. Source: `outputs/essay3_v4/f6_director.csv` '
      '(`scripts/227`).', '']
t14.to_csv(APP / 'supp_table14_director_departure_counts.csv', index=False, lineterminator='\n')

# ------------------------------------------------------------------ Table 15: T-Mobile exhibit
case = pd.read_csv(V4 / 'g6_case_table.csv')
dep = case[(case['departure'] != 'none') & (case['in_analysis_sample'] == 1)]
txt = Path('outputs/essay3_q4/tmobile_502_text.md').read_text(encoding='utf-8')


def filing(accession):
    """Filing date and the verbatim Item 5.02 block for one accession, from tmobile_502_text.md."""
    sec = txt.split(f'## {accession}', 1)[1].split('\n## ', 1)[0]
    date = re.search(r'\*\*Filing date:\*\* (\d{4}-\d\d-\d\d)', sec).group(1)
    block = sec.split('### Item 5.02 section, verbatim', 1)[1].split('```', 2)[1].strip('\n').split('\n')
    return date, block


def quote(block, surname):
    """The first paragraph of the Item 5.02 section that names the executive, verbatim.

    One filing's text is hard-wrapped in the source file (short lines that break mid-sentence);
    its lines are rejoined with single spaces until the paragraph's closing punctuation. Long
    single-line paragraphs are taken as they are.
    """
    for i, line in enumerate(block):
        if line.startswith('On ') and surname in ' '.join(block[i:i + 3]):
            text = line.strip()
            j = i + 1
            while len(line) < 200 and not text.endswith(('.', ':')) and j < len(block):
                text += ' ' + block[j].strip()
                j += 1
            return text
    raise AssertionError(f'no paragraph naming {surname}')


rows = []
for name, g in dep.groupby('departure', sort=False):
    acc = g['first_accession'].iloc[0]
    assert g['first_accession'].nunique() == 1 and g['first_disclosure'].nunique() == 1
    date, block = filing(acc)
    assert date == g['first_disclosure'].iloc[0], f'{name}: filing date {date} vs case table'
    days = g['days_from_notification'].astype(int)
    rows.append({'Executive': name, 'Filing date': date, 'Accession number': acc,
                 'Window': 'Outcome (within 180 days after notification)',
                 'T-Mobile events with this departure in window': len(g),
                 'Days from notification': f'{days.min()}–{days.max()}' if days.min() != days.max() else str(days.min()),
                 'Stated context (verbatim, Item 5.02)': '"' + quote(block, name.split()[-1]) + '"'})
assert len(rows) == 4, f'{len(rows)} in-window departures, expected 4'
PL = '0001193125-19-294093'
date, block = filing(PL)
assert date == '2019-11-18'
rows.append({'Executive': 'John Legere (chief executive); J. Braxton Carter', 'Filing date': date,
             'Accession number': PL, 'Window': 'PLACEBO (before notification)',
             'T-Mobile events with this departure in window': '—', 'Days from notification': '—',
             'Stated context (verbatim, Item 5.02)': '"' + quote(block, 'Legere') + '"'})
t15 = pd.DataFrame(rows)
tm_events = int((case['in_analysis_sample'] == 1).sum())
L += ['**Table 15**', '', '*T-Mobile: Executive Departures Disclosed Within the Outcome Windows, and the '
      'Placebo-Window Succession Filing*', ''] + md_table(t15) + ['',
      f'*Note.* T-Mobile US (parent CIK 1283699) contributes {tm_events} events to the analysis sample. Four '
      f'executive departures fall within 180 days after a T-Mobile notification date; one departure can fall in '
      f'the windows of several events, so the events column counts how many T-Mobile events have it in window and the days column gives the range. The '
      f'stated context is the first paragraph of each filing\'s Item 5.02 section that names the executive, '
      f'quoted exactly; no classifier context flag is reported. The 2019 filing announces the chief-executive '
      f'succession and amends the chief financial officer\'s agreement; it precedes the notification date of '
      f'the nearest T-Mobile event and so falls in the placebo window, not an outcome window. No filing links '
      f'a departure to a breach, and none is interpreted here. Sources: `outputs/essay3_v4/g6_case_table.csv` '
      f'(`scripts/228`); `outputs/essay3_q4/tmobile_502_text.md` (verbatim filing text).', '']
t15.to_csv(APP / 'supp_table15_tmobile_departures.csv', index=False, lineterminator='\n')

(APP / 'ESSAY3_APPENDIX_SUPPLEMENT.md').write_text('\n'.join(L), encoding='utf-8', newline='\n')
print(f'wrote {APP / "ESSAY3_APPENDIX_SUPPLEMENT.md"} (Tables 12-15 + note to Table 5) and 4 CSVs')
print(f'  classifier check: scripts/195 blob {blob195} == v4 constants; {len(f195)} functions identical in 220; 201 loads 195')
for r in rows:
    print(f"  {r['Executive'][:28]:28} {r['Filing date']} {r['Accession number']} {r['Window'][:8]}")
