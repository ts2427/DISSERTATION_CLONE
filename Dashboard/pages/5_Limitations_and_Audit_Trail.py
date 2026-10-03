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
from data import FRAMING, guard, read_csv, read_text, source  # noqa: E402

st.set_page_config(page_title='Limitations and audit trail', layout='wide')

st.title('Limitations and Audit Trail')
st.info(FRAMING)


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


# ------------------------------------------------------------------ known limitations
st.header('Known limitations: disclosed, not corrected')


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

st.divider()

# ------------------------------------------------------------------ retirement ledger
st.header('Retirement ledger')
st.markdown('What was removed from the live pipeline or superseded, when, and why. Nothing listed is '
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

st.divider()

# ------------------------------------------------------------------ freeze gate
st.header('The freeze gate')


def freeze():
    man = 'outputs/rebuild_v4/V3_FREEZE_MANIFEST.csv'
    n = len(read_csv(man))
    st.markdown(
        'The v3 baseline (the annotated tag `v3-frozen`) is guarded by `scripts/210_verify_v3_frozen.py`. '
        'Its manifest records, for every tracked file under `Data/`, `outputs/`, `scripts/` and `docs/` '
        '(plus `run_all.py`, `.gitattributes` and `.gitignore`), two identities: the SHA-256 of the bytes '
        'on disk and the git blob id at the baseline commit. On every run the gate:\n'
        '- **fails** if a baseline file\'s blob id changed, or if its on-disk hash changed and git also '
        'reports a real content difference;\n'
        '- **passes, and logs,** an on-disk hash change that git reports as no difference (a line-ending '
        'or LFS representation artifact);\n'
        '- **fails** if a baseline file is gone, or if a newly tracked file appears outside the narrow '
        'allowlist for v4 work;\n'
        '- treats `.gitattributes` and `.gitignore` as **append-only**: the baseline bytes must remain an '
        'exact prefix of the current file;\n'
        '- admits only the individually **authorised exceptions** in `docs/claude/V3_FREEZE_EXCEPTIONS.md`, '
        'each pinned on both the old and the new hash, so a further change to an excepted file fails, and '
        'a rewritten manifest makes every exception stop matching (the gate fails closed). Exceptions are '
        'printed in full on every run.\n\n'
        'The manifest itself is never rewritten to make a change pass.'
    )
    st.metric('Files recorded in the freeze manifest', f'{n:,}')
    source(man, 'scripts/210_verify_v3_frozen.py')
    with st.expander('Authorised freeze exceptions (V3_FREEZE_EXCEPTIONS.md)'):
        st.markdown(read_text('docs/claude/V3_FREEZE_EXCEPTIONS.md'))
        source('docs/claude/V3_FREEZE_EXCEPTIONS.md')
    with st.expander('After the defense (POST_DEFENSE.md)'):
        st.markdown(read_text('docs/claude/POST_DEFENSE.md'))
        source('docs/claude/POST_DEFENSE.md')


guard(freeze)

st.divider()

# ------------------------------------------------------------------ archive map
st.header('Where did a file go? (archive map)')


def archive():
    p = 'archive/ARCHIVE_MAP.csv'
    df = read_csv(p)
    st.markdown(f'The repository cleanup moved **{len(df):,}** superseded files into `archive/`. '
                'Search an old path (or any part of it) to find its archive location.')
    q = st.text_input('Old path contains', placeholder='e.g. scripts/ or Dashboard/')
    hits = df[df.iloc[:, 0].astype(str).str.contains(q, case=False, regex=False)] if q else df
    st.caption(f'{len(hits):,} matching rows.')
    st.dataframe(hits, hide_index=True, width='stretch', height=360)
    source(p)


guard(archive)

st.divider()

# ------------------------------------------------------------------ pointers
st.header('Reproducing the pipeline')
st.markdown('`README.md` (repository root) describes the layout, setup and full run. '
            '`REVIEWER_GUIDE.md` is the one-page guide for a committee member reviewing the code and data '
            'pipeline, including what the `defense-final` tag and `main` each represent.')


def reviewer():
    with st.expander('REVIEWER_GUIDE.md'):
        st.markdown(read_text('REVIEWER_GUIDE.md'))
        source('REVIEWER_GUIDE.md')


guard(reviewer)
