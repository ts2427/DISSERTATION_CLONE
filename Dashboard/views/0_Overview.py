"""
Overview page of the dissertation dashboard.

Shows the setting, the data chain from notification records to each essay's analysis sample,
and one headline card per essay. Every number on this page is read at run time from a
committed pipeline output (named in a caption under each element); none is typed here.

Run from the repository root:
    streamlit run Dashboard/app.py
"""
import re
import sys
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from streamlit.errors import StreamlitAPIException

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import ui  # noqa: E402
from data import (FRAMING, e1_constants, e1_ledger_md, e2_ledger_md, e2_table,  # noqa: E402
                  e3_constants, guard, source, supp_table)
from ui import COLORS, CONTROL, TREATED, fmt_ci, fmt_int, fmt_num, fmt_p  # noqa: E402

ALPHA = 0.05


# ------------------------------------------------------------------ helpers
def md_tables(text: str) -> list:
    """Every pipe table in a markdown document, as (heading, DataFrame of strings)."""
    out, heading, block = [], '', []

    def flush():
        if len(block) >= 2:
            rows = [[c.strip() for c in ln.strip().strip('|').split('|')] for ln in block]
            hdr, body = rows[0], [r for r in rows[1:] if not set(''.join(r)) <= set('-: ')]
            body = [r + [''] * (len(hdr) - len(r)) for r in body]
            out.append((heading, pd.DataFrame([r[:len(hdr)] for r in body], columns=hdr)))
        block.clear()

    for ln in text.splitlines():
        if ln.strip().startswith('|'):
            block.append(ln)
            continue
        flush()
        if ln.startswith('#'):
            heading = ln.lstrip('#').strip()
    flush()
    return out


def num(s) -> int:
    """'**1,054**' -> 1054."""
    return int(re.sub(r'[^\d-]', '', str(s)))


def find_table(tables, col_must: str, heading_has: str = ''):
    for h, df in tables:
        if col_must in df.columns and heading_has.lower() in h.lower():
            return df
    raise KeyError(f'no table with column {col_must!r} under a heading containing {heading_has!r}')


def row_starting(df: pd.DataFrame, col: str, prefix: str) -> pd.Series:
    hit = df[df[col].astype(str).str.strip().str.startswith(prefix)]
    if hit.empty:
        raise KeyError(f'no row whose {col!r} starts with {prefix!r}')
    return hit.iloc[0]


def verdict(label: str, null: bool):
    """Status line for a card, derived from the loaded p-values / committed status."""
    st.badge(label, color='orange' if null else 'blue',
             icon=':material/remove:' if null else ':material/check:')


def card_title(kicker: str, title: str):
    st.markdown(f'<div style="color:{COLORS["muted"]};font-size:0.78rem;letter-spacing:0.08em;'
                f'text-transform:uppercase;font-weight:600">{kicker}</div>'
                f'<div style="font-size:1.25rem;font-weight:600;margin-bottom:0.3rem">{title}</div>',
                unsafe_allow_html=True)


def essay_link(page: str, label: str):
    """Link to an essay page (works under the st.navigation router; quiet when run standalone)."""
    try:
        st.page_link(page, label=label, icon=':material/arrow_forward:')
    except (StreamlitAPIException, KeyError):
        st.caption(f'{label}: see the essay page in the sidebar.')


# ------------------------------------------------------------------ header
ui.page_header('Data Breach Disclosure Timing and Market Reactions',
               'Timothy D. Spivey · University of South Alabama · Doctoral dissertation in three essays')

with st.container(border=True):
    st.markdown(f':material/info: **How the evidence should be read.** {FRAMING}')

st.markdown(
    '**The setting.** The FCC rule at **47 CFR 64.2011** governs breaches of customer proprietary '
    'network information at telecommunications carriers. It sets two things: a clock for '
    'notifying *law enforcement* (through the federal reporting facility), and an *embargo* that '
    'bars the carrier from telling customers or the public until a waiting period after that '
    'law-enforcement report has run (law enforcement can extend it). That makes the rule a '
    '**floor on public notice, not a ceiling**: it says when a carrier may first speak, not how '
    'quickly it must. It sets no time limit at all on customer notification. Carriers are '
    'identified by FCC Form 499 registration, so "treated" throughout means a breach at a Form 499 '
    'registrant, compared against breaches at other public firms in the same post-2007 period.'
)

# ------------------------------------------------------------------ result cards
ui.section('Headline results',
           'Each essay\'s primary hypothesis is **null**. Each card gives the headline estimate and the '
           'governing p-value; the essay pages carry the full tables.')

col1, col2, col3 = st.columns(3, border=True)


def card_e1():
    c = e1_constants()
    na = supp_table('e1_notification_anchored')
    base = na[na['anchor'].astype(str).str.startswith('breach') & (na['hypothesis'] == 'H2_FCC')]
    with col1:
        card_title('Essay 1', 'Market reaction')
        status = str(c['H2_FCC_status'])
        verdict(ui.STATUS_STYLE.get(status.upper(), (status.capitalize(), ''))[0],
                'NULL' in status.upper())
        st.metric('H2 · 30-day CAR, Form 499 vs others', f"{fmt_num(c['H2_FCC_coef'], 2, signed=True)} pp")
        lo, hi = c['H2_FCC_ci']
        st.markdown(f"95% CI {fmt_ci(lo, hi)} pp  \nHC3 p = **{fmt_p(c['H2_FCC_p'])}**"
                    + (f" · parent-CIK clustered p = {fmt_p(base['p_cv1_parentcik'].iloc[0])}"
                       if not base.empty else ''))
        st.caption(f"N = {fmt_int(c['N_regression'])} events · {fmt_int(c['treated_regression'])} treated "
                   f"events · {fmt_int(c['treated_parent_ciks_regression'])} treated parent CIKs")
        essay_link('views/1_Essay_1_Market_Reaction.py', 'Essay 1 details')
        source('outputs/rebuild/constants_v3.json', 'outputs/defense_supplement/e1_notification_anchored.csv')


def card_e2():
    lad = e2_table('t26_inference_ladder')
    r = row_starting(lad, 'procedure', 'CV3')
    dl = supp_table('e2_delay_ladder')
    d = dl[(dl['outcome'] == 'delay (raw days)') & dl['rung'].astype(str).str.startswith('CV3')].iloc[0]
    with col2:
        card_title('Essay 2', 'Information environment')
        verdict('Null (CV3)' if float(r['p']) >= ALPHA else 'Significant (CV3)', float(r['p']) >= ALPHA)
        st.metric('Post-notification volatility, Form 499 vs others',
                  f"{fmt_num(r['coef'], 3, signed=True)} daily pp")
        st.markdown(f"CV3 95% CI {fmt_ci(r['ci_lo'], r['ci_hi'], 3)} daily pp  \n"
                    f"CV3 p = **{fmt_p(r['p'])}**")
        st.caption(f"Disclosure delay: {fmt_num(d['coef'], 1, signed=True)} days, CV3 p = {fmt_p(d['p'])} "
                   f"· N = {fmt_int(d['N'])} events · {fmt_int(d['n_treated_events'])} treated events · "
                   f"{fmt_int(d['G1'])} treated parent CIKs. The announcement-window elevation is a "
                   'pre-specified secondary result on the Essay 2 page.')
        essay_link('views/2_Essay_2_Information_Environment.py', 'Essay 2 details')
        source('outputs/tables/essay2_v2/t26_inference_ladder.csv',
               'outputs/defense_supplement/e2_delay_ladder.csv')


def card_e3():
    c = e3_constants()
    windows = (30, 90, 180)
    ps = [float(c[f'F1_{w}_p_cv3']) for w in windows]
    n_sig = sum(p < ALPHA for p in ps)
    with col3:
        card_title('Essay 3', 'Governance response')
        verdict('Null at every window (CV3)' if n_sig == 0 else f'Significant at {n_sig} window(s)',
                n_sig == 0)
        st.metric('Executive departure · windows with CV3 p < 0.05',
                  f'{n_sig} of {len(windows)}')
        st.markdown('  \n'.join(
            f"{w}-day: **{fmt_num(100 * c[f'F1_{w}_coef'], 1, signed=True)} pp** (CV3 p {fmt_p(p)})"
            for w, p in zip(windows, ps)))
        st.caption(f"N = {fmt_int(c['N'])} events · {fmt_int(c['treated'])} treated events · "
                   f"{fmt_int(c['treated_parent_ciks'])} treated parent CIKs of "
                   f"{fmt_int(c['parent_ciks'])} clusters")
        essay_link('views/3_Essay_3_Governance_Response.py', 'Essay 3 details')
        source('outputs/essay3_v4/constants_essay3_v4.json')


guard(card_e1)
guard(card_e2)
guard(card_e3)

# ------------------------------------------------------------------ data chain
ui.section(
    'The data chain',
    'The unit changes along the way. The source is a set of public breach **notification records**; '
    'entity resolution (Gate 1) keeps records that resolve to an SEC registrant, de-duplication on '
    'parent CIK and breach date turns records into **firm-day events**, and the rolling-campaign rule '
    '(Gate 2) folds chained refilings into one **canonical event**. Each essay then builds its own '
    'analysis sample from the canonical events. The three essay samples overlap heavily but are '
    '**not nested**: each applies its own data requirements (returns around the breach date, returns '
    'around the public notification date, or executive-departure filings).')


def chain_section():
    t1 = md_tables(e1_ledger_md())
    t2 = md_tables(e2_ledger_md())
    chain = find_table(t1, 'Step', 'chain')
    g1 = row_starting(chain, 'Step', 'Gate 1')
    s3 = row_starting(chain, 'Step', 'Stage 3')
    g2 = row_starting(chain, 'Step', 'Gate 2')

    stages = ['Notification records', 'After entity resolution (Gate 1)',
              'Firm-day events', 'Canonical events (Gate 2)']
    values = [num(g1['In']), num(g1['Out']), num(s3['Out']), num(g2['Out'])]

    ev2 = find_table(t2, 'Treated parent CIKs', 'event-level')
    canon = row_starting(ev2, 'Level', 'Canonical events')
    final2 = ev2.iloc[-1]

    tr1 = find_table(t1, 'Treated parent CIKs', 'treated counts')
    reg1 = row_starting(tr1, 'Stage', 'Essay 1 regression')
    c1 = e1_constants()
    c3 = e3_constants()

    left, right = st.columns([1, 1], gap='large')
    with left:
        st.markdown('**From notification records to canonical events**')
        fig = go.Figure(go.Funnel(
            y=stages, x=values, texttemplate='%{value:,}<br>%{percentInitial:.0%}',
            textfont=dict(color='white', size=14),
            marker=dict(color=[CONTROL, CONTROL, CONTROL, TREATED]),
            connector=dict(fillcolor=COLORS['grid']),
            hovertemplate='%{y}<br>%{x:,}<br>%{percentInitial:.1%} of records<extra></extra>'))
        fig.update_layout(margin=dict(l=10, r=10, t=10, b=10))
        ui.chart(fig, height=340)
        st.caption(f"Canonical events: **{num(canon['Treated'])} treated events** "
                   f"at **{num(canon['Treated parent CIKs'])} treated parent CIKs** "
                   f"({num(canon['Treated orgs'])} treated organisations); "
                   f"{num(canon['Control'])} control events.")
        source('outputs/ESSAY1_SAMPLE_ATTRITION_LEDGER_V3.md (chain table)',
               'outputs/ESSAY2_SAMPLE_ATTRITION_LEDGER.md (event-level table)')

    with right:
        st.markdown('**Each essay\'s analysis sample**')
        samples = pd.DataFrame([
            dict(Sample='Essay 1 regression',
                 N=int(c1['N_regression']), treated=int(c1['treated_regression']),
                 parents=int(c1['treated_parent_ciks_regression'])),
            dict(Sample='Essay 2 analytic',
                 N=num(final2['N']), treated=num(final2['Treated']),
                 parents=num(final2['Treated parent CIKs'])),
            dict(Sample='Essay 3 v4 analysis',
                 N=int(c3['N']), treated=int(c3['treated']),
                 parents=int(c3['treated_parent_ciks'])),
        ])
        samples['control'] = samples['N'] - samples['treated']
        fig = go.Figure()
        fig.add_bar(y=samples['Sample'], x=samples['treated'], name='Treated (Form 499)',
                    orientation='h', marker_color=TREATED, text=samples['treated'],
                    textposition='inside', insidetextanchor='middle', textfont=dict(color='white'),
                    customdata=samples['parents'],
                    hovertemplate='%{x} treated events<br>%{customdata} treated parent CIKs<extra></extra>')
        fig.add_bar(y=samples['Sample'], x=samples['control'], name='Control',
                    orientation='h', marker_color=CONTROL, text=samples['control'],
                    textposition='inside', insidetextanchor='middle', textfont=dict(color='white'),
                    hovertemplate='%{x} control events<extra></extra>')
        fig.update_layout(barmode='stack', legend=dict(orientation='h', y=1.12, x=0, traceorder='normal'),
                          bargap=0.45, yaxis=dict(autorange='reversed', title=None),
                          xaxis=dict(title='events'), margin=dict(l=10, r=10, t=40, b=10))
        ui.chart(fig, height=260)
        ui.table(samples, columns={'Sample': 'Sample', 'N': 'Events',
                                   'treated': 'Treated', 'control': 'Control',
                                   'parents': 'Treated parent CIKs'},
                 download='essay_samples.csv')
        st.caption('Outcome basis: breach-anchored CARs (Essay 1), notification-anchored volatility '
                   '(Essay 2), executive departures (Essay 3). '
                   f"Essay 1 treated events sit in {num(reg1['Treated organisations'])} treated "
                   'organisations. Inference clusters on the parent CIK, so the parent-CIK count '
                   '(not the event count) is the effective number of treated units.')
        source('outputs/rebuild/constants_v3.json', 'outputs/ESSAY2_SAMPLE_ATTRITION_LEDGER.md',
               'outputs/essay3_v4/constants_essay3_v4.json')


guard(chain_section)

# ------------------------------------------------------------------ reading guide
ui.section('How to read this dashboard')
st.markdown(
    '- Every number is **read at run time from a committed pipeline output**; the file is named in '
    'the small "Source:" note under each chart or table. Nothing is typed into the page code, so the '
    'dashboard cannot drift from the essays.\n'
    '- The verified state of every result is the git tag **`defense-final`**.\n'
    '- Treated counts always name their level: events, organisations, or parent CIKs.\n'
    '- Essays 2 and 3 are governed by CV3 (cluster jackknife) with the wild cluster bootstrap as '
    'corroboration; HC3 is shown only as a lower bound on the standard error. Essay 1 reports HC3 '
    'with parent-CIK clustered p-values alongside.\n'
    '- Colours: **navy** marks Form 499 (treated) events and governing estimates; **grey** marks '
    'control events and comparison rows.\n'
    '- No raw licensed data (CRSP or Compustat rows) is loaded; only results and documentation.\n'
    '- Use the sidebar for the three essay pages, the **Robustness & supplement** page, and '
    '**Limitations & audit trail**.'
)
