"""
Limitations and audit trail.

Renders the committed documentation of what the dissertation discloses rather than corrects
(docs/claude/KNOWN_LIMITATIONS.md), what was retired and why (outputs/RETIREMENT_LEDGER.md),
how the frozen baseline is guarded (scripts/210 and its manifest), and where superseded files
moved (archive/ARCHIVE_MAP.csv). Every count is read from those files at run time.
"""
import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import ui  # noqa: E402
from data import guard, read_csv, read_text, source  # noqa: E402
from ui import fmt_int  # noqa: E402

ui.page_header('Limitations & Audit Trail',
               'What the dissertation discloses rather than corrects, what was retired, and how the '
               'baseline is guarded')
ui.framing_note()


def split_sections(text: str, marker: str):
    """Split markdown on lines starting with `marker` (e.g. '## '), ignoring fenced code.
    Returns (preamble, [(heading, body), ...])."""
    pre, sections, cur_head, cur, fenced = [], [], None, [], False
    for ln in text.splitlines():
        if ln.lstrip().startswith('```'):
            fenced = not fenced
        if not fenced and ln.startswith(marker):
            if cur_head is None:
                pre = cur
            else:
                sections.append((cur_head, '\n'.join(cur).strip()))
            cur_head, cur = ln[len(marker):].strip(), []
            continue
        cur.append(ln)
    if cur_head is None:
        return '\n'.join(cur).strip(), []
    sections.append((cur_head, '\n'.join(cur).strip()))
    return '\n'.join(pre).strip(), sections


# ------------------------------------------------------------------ at a glance
def glance():
    _, lim = split_sections(read_text('docs/claude/KNOWN_LIMITATIONS.md'), '## ')
    _, ret = split_sections(read_text('outputs/RETIREMENT_LEDGER.md'), '# ')
    n_man = len(read_csv('outputs/rebuild_v4/V3_FREEZE_MANIFEST.csv'))
    n_arc = len(read_csv('archive/ARCHIVE_MAP.csv'))
    c = st.columns(4)
    c[0].metric('Disclosed limitations', fmt_int(len(lim)), border=True)
    c[1].metric('Retirement-ledger entries', fmt_int(len(ret)), border=True)
    c[2].metric('Files in the freeze manifest', fmt_int(n_man), border=True)
    c[3].metric('Files moved to archive/', fmt_int(n_arc), border=True)


guard(glance)

# ------------------------------------------------------------------ known limitations
ui.section('Known limitations: disclosed, not corrected')


def limitations():
    p = 'docs/claude/KNOWN_LIMITATIONS.md'
    pre, secs = split_sections(read_text(p), '## ')
    # The preamble opens with the document's own '# ' title; the page header replaces it.
    st.markdown('\n'.join(ln for ln in pre.splitlines() if not ln.startswith('# ')))
    st.caption(f'{len(secs)} sections. Open each to read it in full.')
    for head, body in secs:
        with st.expander(head):
            st.markdown(body)
    source(p)


guard(limitations)

# ------------------------------------------------------------------ retirement ledger
ui.section('Retirement ledger',
           'What was removed from the live pipeline or superseded, when, and why. Nothing listed is '
           'deleted: every retired script and output stays in git history.')


def retirement():
    p = 'outputs/RETIREMENT_LEDGER.md'
    _, entries = split_sections(read_text(p), '# ')
    st.caption(f'{len(entries)} dated entries, oldest first.')
    for head, body in entries:
        with st.expander(head):
            st.markdown(body)
    source(p)


guard(retirement)

# ------------------------------------------------------------------ freeze gate
ui.section('The freeze gate')


def freeze():
    man = 'outputs/rebuild_v4/V3_FREEZE_MANIFEST.csv'
    st.markdown(
        'The v3 baseline (the annotated tag `v3-frozen`) is guarded by '
        '`scripts/210_verify_v3_frozen.py`. Its manifest records, for every tracked file under '
        '`Data/`, `outputs/`, `scripts/` and `docs/` (plus `run_all.py`, `.gitattributes` and '
        '`.gitignore`), two identities: the SHA-256 of the bytes on disk and the git blob id at the '
        'baseline commit. On every run the gate:\n'
        '- **fails** if a baseline file\'s blob id changed, or if its on-disk hash changed and git '
        'also reports a real content difference;\n'
        '- **passes, and logs,** an on-disk hash change that git reports as no difference (a '
        'line-ending or LFS representation artifact);\n'
        '- **fails** if a baseline file is gone, or if a newly tracked file appears outside the '
        'narrow allowlist for v4 work;\n'
        '- treats `.gitattributes` and `.gitignore` as **append-only**: the baseline bytes must '
        'remain an exact prefix of the current file;\n'
        '- admits only the individually **authorised exceptions** in '
        '`docs/claude/V3_FREEZE_EXCEPTIONS.md`, each pinned on both the old and the new hash, so a '
        'further change to an excepted file fails, and a rewritten manifest makes every exception '
        'stop matching (the gate fails closed). Exceptions are printed in full on every run.\n\n'
        'The manifest itself is never rewritten to make a change pass.'
    )
    st.caption(f'{fmt_int(len(read_csv(man)))} files recorded in the freeze manifest.')
    source(man, 'scripts/210_verify_v3_frozen.py')
    with st.expander('Authorised freeze exceptions (V3_FREEZE_EXCEPTIONS.md)', icon=':material/rule:'):
        st.markdown(read_text('docs/claude/V3_FREEZE_EXCEPTIONS.md'))
        source('docs/claude/V3_FREEZE_EXCEPTIONS.md')
    with st.expander('After the defense (POST_DEFENSE.md)', icon=':material/event:'):
        st.markdown(read_text('docs/claude/POST_DEFENSE.md'))
        source('docs/claude/POST_DEFENSE.md')


guard(freeze)

# ------------------------------------------------------------------ archive map
ui.section('Where did a file go? (archive map)')


def archive():
    p = 'archive/ARCHIVE_MAP.csv'
    df = read_csv(p)
    old, new = df.columns[0], df.columns[1]
    st.markdown(f'The repository cleanup moved **{fmt_int(len(df))}** superseded files into `archive/`. '
                'Search an old path (or any part of it) to find its archive location.')
    q = st.text_input('Search old paths', placeholder='e.g. scripts/ or Dashboard/',
                      icon=':material/search:').strip()
    hits = df[df[old].astype(str).str.contains(q, case=False, regex=False)] if q else df
    if q and hits.empty:
        st.info(f'No archived file path contains "{q}".', icon=':material/search_off:')
    else:
        st.caption(f'{fmt_int(len(hits))} of {fmt_int(len(df))} files'
                   + (f' match "{q}".' if q else '.'))
        ui.table(hits, columns={old: 'Old path', new: 'Archive location'}, height=360,
                 download='archive_map.csv')
    source(p)


guard(archive)

# ------------------------------------------------------------------ pointers
ui.section('Reproducing the pipeline',
           '`README.md` (repository root) describes the layout, setup and full run. '
           '`REVIEWER_GUIDE.md` is the one-page guide for a committee member reviewing the code and data '
           'pipeline, including what the `defense-final` tag and `main` each represent.')


def reviewer():
    with st.expander('REVIEWER_GUIDE.md', icon=':material/menu_book:'):
        st.markdown(read_text('REVIEWER_GUIDE.md'))
        source('REVIEWER_GUIDE.md')


guard(reviewer)
