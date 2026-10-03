"""
Data layer for the dissertation dashboard.

Every number the dashboard shows is READ from a committed output of the pipeline, never typed
into a page. The pages only arrange and chart what these loaders return, so the dashboard
cannot drift from the essays: if an output changes, the page changes with it.

Nothing here reads raw licensed data (CRSP or Compustat rows). Only results, aggregates and
documentation that the pipeline commits under outputs/ and docs/ are loaded.

Paths are resolved from the repository root, so the app works from any working directory:
    streamlit run Dashboard/app.py
"""
import json
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'outputs'

E1_APPX = OUT / 'rebuild' / 'appendix_v3'
E2_DIR = OUT / 'tables' / 'essay2_v2'
E3_DIR = OUT / 'essay3_v4'
E3_APPX = OUT / 'essay3_appendix'
E3_Q4 = OUT / 'essay3_q4'
SUPP = OUT / 'defense_supplement'


class MissingOutput(FileNotFoundError):
    pass


def _need(p: Path) -> Path:
    if not p.exists():
        raise MissingOutput(f'Committed output not found: {p.relative_to(ROOT)}. '
                            'Run the pipeline (python run_all.py) or check out defense-final.')
    return p


def rel(p: Path) -> str:
    """Repository-relative path, for 'Source:' captions."""
    return str(Path(p).resolve().relative_to(ROOT)).replace('\\', '/')


# ------------------------------------------------------------------ generic
@st.cache_data
def read_csv(path: str) -> pd.DataFrame:
    return pd.read_csv(_need(ROOT / path), low_memory=False)


@st.cache_data
def read_json(path: str) -> dict:
    return json.loads(_need(ROOT / path).read_text(encoding='utf-8'))


@st.cache_data
def read_text(path: str) -> str:
    return _need(ROOT / path).read_text(encoding='utf-8')


# ------------------------------------------------------------------ Essay 1
def e1_constants() -> dict:
    """outputs/rebuild/constants_v3.json - the Essay 1 assertion baseline (scripts/158)."""
    return read_json('outputs/rebuild/constants_v3.json')


def e1_table(i: int):
    """Appendix table i (1-16) from scripts/158: returns (table, caption). The committed CSVs
    carry the caption as a final row whose first cell is 'CAPTION'."""
    df = read_csv(f'outputs/rebuild/appendix_v3/table_{i}.csv')
    cap = ''
    if len(df) and str(df.iloc[-1, 0]) == 'CAPTION':
        cap = str(df.iloc[-1, 1])
        df = df.iloc[:-1].reset_index(drop=True)
    return df, cap


def e1_ledger_md() -> str:
    return read_text('outputs/ESSAY1_SAMPLE_ATTRITION_LEDGER_V3.md')


# ------------------------------------------------------------------ Essay 2
def e2_table(name: str) -> pd.DataFrame:
    """outputs/tables/essay2_v2/<name>.csv, e.g. 't26_inference_ladder'."""
    return read_csv(f'outputs/tables/essay2_v2/{name}.csv')


def e2_ledger_md() -> str:
    return read_text('outputs/ESSAY2_SAMPLE_ATTRITION_LEDGER.md')


# ------------------------------------------------------------------ Essay 3
def e3_constants() -> dict:
    """outputs/essay3_v4/constants_essay3_v4.json - the Essay 3 assertion baseline (scripts/227)."""
    return read_json('outputs/essay3_v4/constants_essay3_v4.json')


def e3_table(name: str) -> pd.DataFrame:
    """outputs/essay3_v4/<name>.csv, e.g. 'f1_ladder'."""
    return read_csv(f'outputs/essay3_v4/{name}.csv')


def e3_q4_table(name: str) -> pd.DataFrame:
    """outputs/essay3_q4/<name>.csv, e.g. 'table07'."""
    return read_csv(f'outputs/essay3_q4/{name}.csv')


# ------------------------------------------------------------------ defense supplement
def supp_table(name: str) -> pd.DataFrame:
    """outputs/defense_supplement/<name>.csv."""
    return read_csv(f'outputs/defense_supplement/{name}.csv')


def supp_constants() -> dict:
    return read_json('outputs/defense_supplement/constants_defense_supplement.json')


# ------------------------------------------------------------------ helpers for pages
def source(*paths: str) -> None:
    """Small grey 'Source:' note under a chart or table, naming the committed file(s)."""
    names = ' · '.join(str(p).replace('`', '') for p in paths)
    st.markdown(f'<p style="color:#6B7385;font-size:0.8rem;margin-top:-0.4rem">Source: {names}</p>',
                unsafe_allow_html=True)


def guard(fn):
    """Run a page section; if a committed output is missing, say which one instead of crashing."""
    try:
        return fn()
    except MissingOutput as e:
        st.warning(str(e))
        return None


FRAMING = ('All three essays are **descriptive, post-2007 cross-sectional** studies. There are no treated '
           'events before the 2007 rule took effect, so nothing here is a causal estimate, a natural '
           'experiment, or a difference-in-differences design. Treatment is FCC Form 499 registration '
           'status, never SIC code.')
