"""PART D: trace every number in the essay drafts to the output that produces it.

Usage:
    python scripts/248_essay_to_output_match.py [--drafts DIR] [--out FILE]

Reads .docx drafts (default docs/drafts/), extracts every number from body text, tables
and captions, and classifies each against the pipeline outputs:

    MATCH          equals a pipeline output at the precision written
    MISMATCH       a source exists for the quantity and the value differs
    NO PROVENANCE  no pipeline output carries this value
    STALE          matches a RETIRED or TOMBSTONED source, which is named

It also runs the D3 purge-list scan and the D4 contradicted-claim scan, including the two
added checks: Essay 2 sentences citing an H5_* value from constants_v3.json rather than
scripts/165, and any sentence stating the direction of T6_treated_timing_coef.

Nothing is edited. The drafts are read only.

TWO LIMITATIONS, STATED RATHER THAN HIDDEN
------------------------------------------
1. Matching is on the numeric value alone, so a MATCH is evidence that the value exists
   somewhere in the pipeline, not proof that it is the value that sentence should carry.
   Common numbers collide: validated against the pipeline-generated Essay 3 appendix, this
   returned 4 STALE purely from value collisions with the tombstoned set. Treat the output
   as triage that tells a reader where to look, not as a verdict.
2. This script cannot emit MISMATCH. Distinguishing "the draft says 338 where the output
   says 340" from "the draft says 338 about something else entirely" needs to know which
   quantity the sentence is about, which bare number extraction cannot establish. Values
   that do not appear anywhere are therefore reported as NO PROVENANCE, and MISMATCH has to
   be read out of the NO PROVENANCE rows by a human who knows the quantity. The known
   mismatches to look for first are the rebaseline's: 338 -> 340, 104 -> 106 treated
   events, 35 -> 36 parent entities, 11 -> 12 parent CIKs, 354 -> 356, 109 -> 111, 116 ->
   118, and car30d_regression_mean -0.1581 -> -0.2052.
"""
import argparse
import json
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree

# ----------------------------------------------------------------- live sources
LIVE = {
    'constants_v3.json': Path('outputs/rebuild/constants_v3.json'),
    'constants_essay3_v4.json': Path('outputs/essay3_v4/constants_essay3_v4.json'),
}
LIVE_CSV_DIRS = [Path('outputs/tables/essay2_v2'), Path('outputs/rebuild/appendix_v3'),
                 Path('outputs/essay3_q4')]
LIVE_MD = [Path('outputs/ESSAY1_SAMPLE_ATTRITION_LEDGER_V3.md'),
           Path('outputs/ESSAY2_SAMPLE_ATTRITION_LEDGER.md')]

# ----------------------------------------------------------------- retired sources
STALE = {
    'Essay 3 Query 2 (RETIRED 2026-09-29)': Path('outputs/essay3_q2/constants_essay3_q2.json'),
}
STALE_CSV_DIRS = [Path('outputs/tables/essay2_appendix')]   # tombstoned 2026-09-29

# ----------------------------------------------------------------- D3 purge list
PURGE = [
    ('Rule 37.3', re.compile(r'Rule\s*37\.3', re.I)),
    ('September 28, 2007', re.compile(r'September\s*28,?\s*2007', re.I)),
    ('June 8, 2007 without the publication qualifier',
     re.compile(r'June\s*8,?\s*2007(?!\s*\(publication)', re.I)),
    ('1,054 breaches', re.compile(r'1,?054\s+breaches', re.I)),
    ('14.52', re.compile(r'\b14\.52\b')),
    ('16.71', re.compile(r'\b16\.71\b')),
    ('15.05', re.compile(r'\b15\.05\b')),
    ('BoardEx', re.compile(r'BoardEx', re.I)),
    ('64.2011 as a customer/public disclosure deadline',
     re.compile(r'64\.2011[^.]{0,120}(customer|public|consumer)[^.]{0,40}(deadline|disclos)', re.I)),
    ('claim the rule changed disclosure timing',
     re.compile(r'rule[^.]{0,60}(changed|accelerat|reduc|shorten)[^.]{0,40}(disclosure|timing|delay)', re.I)),
    ('Item 5.02 incidence described as turnover',
     re.compile(r'(Item\s*5\.02|5\.02)[^.]{0,80}turnover', re.I)),
    ('natural-experiment language', re.compile(r'natural\s+experiment', re.I)),
    ('causal-identification language',
     re.compile(r'causal\s+identif|identif\w*\s+strategy|exogenous\s+shock', re.I)),
]

# ----------------------------------------------------------------- D4 claim checks
CLAIMS = [
    ('immediate_disclosure described as disclosure speed',
     re.compile(r'immediate[_ ]disclosure[^.]{0,120}(speed|prompt|quick|how fast|rapid)', re.I),
     'docs/claude/KNOWN_LIMITATIONS.md entry 2: 8 of Essay 1\'s 124 immediate_disclosure '
     'events reflect a documented gap; 116 of 124 have breach_date == reported_date'),
    ('delay variable described without the same-date issue',
     re.compile(r'(disclosure\s+delay|delay[_ ]w|delay\s+variable)(?![^.]{0,200}same[- ]date)', re.I),
     'KNOWN_LIMITATIONS.md entry 2: delay_w == 0 for 117 of 333, 112 of them same-date '
     'records with no independent breach date'),
    ('car_30d window implied to start at disclosure',
     re.compile(r'(car[_ ]?30|30[- ]day\s+window|event\s+window)[^.]{0,140}'
                r'(announce|disclos|notif|report)', re.I),
     'KNOWN_LIMITATIONS.md entry 3: car_30d anchors on breach_date; 128 of 340 windows '
     '(42 of 106 treated) close BEFORE notification'),
    # the two added checks
     ('Essay 2 citing an H5_* value from constants_v3.json instead of scripts/165',
     re.compile(r'(H5[_ ]|hypothesis\s*5|H5\b)[^.]{0,200}'
                r'(3\.94|3\.29|0?\.0292|0?\.029|0?\.063|0?\.0630|5\.07|4\.95|0?\.8456|0?\.7491)', re.I),
     'ALIGNMENT_REPORT.md Part A3: constants_v3.json H5 is HC3 on the ESSAY 1 frame '
     '(N_essay2 339). Essay 2\'s verdict of record is scripts/165 on N = 333, 104 treated '
     'events, 82 clusters. H5_p is now .0292 against a null in the frame of record.'),
    ('a sentence stating the direction of T6_treated_timing_coef',
     re.compile(r'(treated[^.]{0,60}timing|timing[^.]{0,60}treated)[^.]{0,140}'
                r'(negative|positive|slower|faster|decreas|increas|longer|shorter|'
                r'-0?\.78|0?\.5562|\+0?\.56)', re.I),
     'ALIGNMENT_REPORT.md Part A3: T6_treated_timing_coef CHANGED SIGN at the rebaseline, '
     'from -0.7835 to +0.5562, so any directional claim is suspect either way'),
]

NUM = re.compile(r'(?<![\w.])(-?\d{1,3}(?:,\d{3})+(?:\.\d+)?|-?\d+\.\d+|-?\d+)(?![\w])')
W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'


def docx_blocks(path):
    """(kind, location, text) for every paragraph and table cell, in document order."""
    out = []
    with zipfile.ZipFile(path) as z:
        xml = z.read('word/document.xml')
    root = ElementTree.fromstring(xml)
    body = root.find(W + 'body')
    section, pi, ti = '(front matter)', 0, 0
    for el in body.iter():
        if el.tag == W + 'p':
            txt = ''.join(t.text or '' for t in el.iter(W + 't')).strip()
            if not txt:
                continue
            pi += 1
            style = el.find('.//' + W + 'pStyle')
            if style is not None and 'eading' in (style.get(W + 'val') or ''):
                section = txt[:70]
            out.append(('paragraph', '%s | para %d' % (section, pi), txt))
        elif el.tag == W + 'tbl':
            ti += 1
            for r, row in enumerate(el.findall(W + 'tr'), 1):
                for c, cell in enumerate(row.findall(W + 'tc'), 1):
                    txt = ' '.join(t.text or '' for t in cell.iter(W + 't')).strip()
                    if txt:
                        out.append(('table cell', 'table %d r%dc%d' % (ti, r, c), txt))
    return out


def index_values():
    """value-string -> list of (source, locator). Built from live and retired outputs."""
    live, stale = {}, {}

    def add(d, val, src, loc):
        for form in {str(val)}:
            d.setdefault(form, []).append((src, loc))
            try:
                f = float(val)
            except (TypeError, ValueError):
                continue
            for p in (0, 1, 2, 3, 4):
                d.setdefault(('%.*f' % (p, f)), []).append((src, loc))
            d.setdefault('%g' % f, []).append((src, loc))

    for name, p in LIVE.items():
        if p.exists():
            for k, v in json.loads(p.read_text(encoding='utf-8')).items():
                if isinstance(v, (int, float)) and not isinstance(v, bool):
                    add(live, v, name, k)
    for name, p in STALE.items():
        if p.exists():
            for k, v in json.loads(p.read_text(encoding='utf-8')).items():
                if isinstance(v, (int, float)) and not isinstance(v, bool):
                    add(stale, v, name, k)

    def scan_csvs(dirs, d, tag):
        for dd in dirs:
            if not dd.exists():
                continue
            for p in sorted(dd.glob('*.csv')):
                try:
                    rows = p.read_text(encoding='utf-8', errors='replace').split('\n')
                except OSError:
                    continue
                hdr = rows[0].split(',') if rows else []
                for ri, row in enumerate(rows[1:], 2):
                    for ci, cell in enumerate(row.split(',')):
                        cell = cell.strip().strip('"')
                        if re.fullmatch(r'-?\d+(\.\d+)?', cell or ''):
                            col = hdr[ci].strip() if ci < len(hdr) else 'col%d' % ci
                            add(d, cell, tag % p.name, 'row %d, %s' % (ri, col))

    scan_csvs(LIVE_CSV_DIRS, live, '%s (live)')
    scan_csvs(STALE_CSV_DIRS, stale, '%s (TOMBSTONED essay2_appendix)')
    for p in LIVE_MD:
        if p.exists():
            for i, ln in enumerate(p.read_text(encoding='utf-8', errors='replace').split('\n'), 1):
                for m in NUM.finditer(ln):
                    add(live, m.group(1).replace(',', ''), p.name + ' (live)', 'line %d' % i)
    return live, stale


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--drafts', default='docs/drafts')
    ap.add_argument('--out', default='outputs/ESSAY_MATCH_REPORT.md')
    a = ap.parse_args()

    d = Path(a.drafts)
    if not d.exists():
        print('ABORT: no drafts directory at %s' % d)
        print('Part D needs the three essay .docx drafts. Nothing was guessed or inferred.')
        return 2
    docs = sorted(d.glob('*.docx'))
    docs = [p for p in docs if not p.name.startswith('~$')]
    if not docs:
        print('ABORT: %s exists but holds no .docx' % d)
        return 2

    live, stale = index_values()
    print('provenance index: %d live value forms, %d retired value forms'
          % (len(live), len(stale)))

    L = ['# Essay-to-output match check', '',
         'Generated by `scripts/248_essay_to_output_match.py`. Drafts read, never edited.',
         '', 'Provenance index: %d live value forms from `constants_v3.json`, '
         '`constants_essay3_v4.json`, the live Essay 2 tables, `appendix_v3/`, the Essay 3 '
         'table CSVs and the two attrition ledgers; %d retired forms from the Query 2 '
         'constants and the tombstoned Essay 2 appendix.' % (len(live), len(stale)), '']
    totals = {}
    for doc in docs:
        blocks = docx_blocks(doc)
        rows, seen = [], set()
        for kind, loc, text in blocks:
            for m in NUM.finditer(text):
                raw = m.group(1)
                key = raw.replace(',', '')
                if (loc, raw) in seen:
                    continue
                seen.add((loc, raw))
                if key in live:
                    src, where = live[key][0]
                    cls = 'MATCH'
                elif key in stale:
                    src, where = stale[key][0]
                    cls = 'STALE'
                else:
                    src, where, cls = '-', '-', 'NO PROVENANCE'
                rows.append((cls, kind, loc, raw, text[:110], src, where))
        order = {'MISMATCH': 0, 'NO PROVENANCE': 1, 'STALE': 2, 'MATCH': 3}
        rows.sort(key=lambda r: (order[r[0]], r[2]))
        tally = {}
        for r in rows:
            tally[r[0]] = tally.get(r[0], 0) + 1
        totals[doc.name] = tally
        L += ['## %s' % doc.name, '',
              '%d numbers extracted. %s' % (len(rows), ', '.join(
                  '%s %d' % (k, v) for k, v in sorted(tally.items()))), '',
              '| class | location | value | source | key/cell | sentence or cell |',
              '|---|---|---|---|---|---|']
        for cls, kind, loc, raw, txt, src, where in rows:
            L.append('| %s | %s | `%s` | %s | %s | %s |'
                     % (cls, loc, raw, src, where, txt.replace('|', '\\|')))
        L.append('')

        L += ['### D3 purge-list hits', '']
        hits = 0
        for label, rx in PURGE:
            for kind, loc, text in blocks:
                if rx.search(text):
                    L.append('- **%s** — %s — %s' % (label, loc, text[:220]))
                    hits += 1
        L.append('' if hits else '- none')
        L.append('')
        L += ['### D4 contradicted claims', '']
        ch = 0
        for label, rx, cite in CLAIMS:
            for kind, loc, text in blocks:
                if rx.search(text):
                    L.append('- **%s** — %s' % (label, loc))
                    L.append('  - claim: %s' % text[:220])
                    L.append('  - contradicted by: %s' % cite)
                    ch += 1
        L.append('' if ch else '- none')
        L.append('')
        totals[doc.name]['purge'] = hits
        totals[doc.name]['claims'] = ch

    Path(a.out).write_text('\n'.join(L) + '\n', encoding='utf-8')
    print('written %s' % a.out)
    for n, t in totals.items():
        print('  %-34s %s' % (n, t))
    return 0


if __name__ == '__main__':
    sys.exit(main())
