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

sys.path.insert(0, str(Path(__file__).resolve().parent))
from data import (FRAMING, e1_constants, e1_ledger_md, e2_ledger_md, e2_table,  # noqa: E402
                  e3_constants, guard, read_csv, source, supp_table)

st.set_page_config(page_title='Breach disclosure dissertation', layout='wide')

BLUE = '#2a78d6'
ORANGE = '#eb6834'
GRAY = '#8a8984'


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


# ------------------------------------------------------------------ header
st.title('Data Breach Disclosure Timing and Market Reactions')
st.markdown('**Timothy D. Spivey** · University of South Alabama · Doctoral dissertation, three essays')
st.info(FRAMING)

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

st.divider()

# ------------------------------------------------------------------ data chain
st.header('The data chain')
st.markdown(
    'The unit changes along the way. The source is a set of public breach **notification records**; '
    'entity resolution (Gate 1) keeps records that resolve to an SEC registrant, de-duplication on '
    'parent CIK and breach date turns records into **firm-day events**, and the rolling-campaign rule '
    '(Gate 2) folds chained refilings into one **canonical event**. Each essay then builds its own '
    'analysis sample from the canonical events. The three essay samples overlap heavily but are '
    '**not nested**: each applies its own data requirements (returns around the breach date, returns '
    'around the public notification date, or executive-departure filings).'
)


def chain_section():
    t1 = md_tables(e1_ledger_md())
    t2 = md_tables(e2_ledger_md())
    chain = find_table(t1, 'Step', 'chain')
    g1 = row_starting(chain, 'Step', 'Gate 1')
    s3 = row_starting(chain, 'Step', 'Stage 3')
    g2 = row_starting(chain, 'Step', 'Gate 2')

    stages = ['Notification records', 'After Gate 1 (entity resolution)',
              'Firm-day events (CIK + breach date)', 'Canonical events (after Gate 2)']
    values = [num(g1['In']), num(g1['Out']), num(s3['Out']), num(g2['Out'])]

    ev2 = find_table(t2, 'Treated parent CIKs', 'event-level')
    canon = row_starting(ev2, 'Level', 'Canonical events')
    final2 = ev2.iloc[-1]

    tr1 = find_table(t1, 'Treated parent CIKs', 'treated counts')
    reg1 = row_starting(tr1, 'Stage', 'Essay 1 regression')
    c1 = e1_constants()
    c3 = e3_constants()

    left, right = st.columns([3, 2])
    with left:
        fig = go.Figure(go.Funnel(
            y=stages, x=values, textinfo='value+percent initial',
            marker=dict(color=[GRAY, GRAY, GRAY, BLUE]),
            hovertemplate='%{y}<br>%{x:,}<br>%{percentInitial:.1%} of records<extra></extra>'))
        fig.update_layout(height=360, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, width='stretch')
        st.caption(f"Canonical events: **{num(canon['Treated'])} treated events** "
                   f"at **{num(canon['Treated parent CIKs'])} treated parent CIKs** "
                   f"({num(canon['Treated orgs'])} treated organisations); "
                   f"{num(canon['Control'])} control events.")
        source('outputs/ESSAY1_SAMPLE_ATTRITION_LEDGER_V3.md (chain table)',
               'outputs/ESSAY2_SAMPLE_ATTRITION_LEDGER.md (event-level table)')

    with right:
        samples = pd.DataFrame([
            dict(Sample='Essay 1 regression (breach-anchored CARs)',
                 N=int(c1['N_regression']), treated=int(c1['treated_regression']),
                 parents=int(c1['treated_parent_ciks_regression'])),
            dict(Sample='Essay 2 analytic (notification-anchored volatility)',
                 N=num(final2['N']), treated=num(final2['Treated']),
                 parents=num(final2['Treated parent CIKs'])),
            dict(Sample='Essay 3 v4 analysis (executive departures)',
                 N=int(c3['N']), treated=int(c3['treated']),
                 parents=int(c3['treated_parent_ciks'])),
        ])
        samples['control'] = samples['N'] - samples['treated']
        fig = go.Figure()
        fig.add_bar(y=samples['Sample'], x=samples['treated'], name='Treated events',
                    orientation='h', marker_color=BLUE,
                    customdata=samples['parents'],
                    hovertemplate='%{x} treated events<br>%{customdata} treated parent CIKs<extra></extra>')
        fig.add_bar(y=samples['Sample'], x=samples['control'], name='Control events',
                    orientation='h', marker_color=GRAY,
                    hovertemplate='%{x} control events<extra></extra>')
        fig.update_layout(barmode='stack', height=360, margin=dict(l=10, r=10, t=30, b=10),
                          legend=dict(orientation='h', y=1.08), bargap=0.45,
                          yaxis=dict(autorange='reversed'), xaxis_title='events')
        st.plotly_chart(fig, width='stretch')
        show = samples.rename(columns={'N': 'N (events)', 'treated': 'Treated events',
                                       'parents': 'Treated parent CIKs',
                                       'control': 'Control events'})
        st.dataframe(show, hide_index=True, width='stretch')
        st.caption(f"Essay 1 treated events sit in {num(reg1['Treated organisations'])} treated "
                   'organisations. Inference clusters on the parent CIK, so the parent-CIK count '
                   '(not the event count) is the effective number of treated units.')
        source('outputs/rebuild/constants_v3.json', 'outputs/ESSAY2_SAMPLE_ATTRITION_LEDGER.md',
               'outputs/essay3_v4/constants_essay3_v4.json')


guard(chain_section)

st.divider()

# ------------------------------------------------------------------ result cards
st.header('Headline results')
st.markdown('Each essay\'s primary hypothesis is **null**. The cards give the headline estimate and '
            'the governing p-value; the essay pages carry the full tables.')

col1, col2, col3 = st.columns(3)


def card_e1():
    c = e1_constants()
    na = supp_table('e1_notification_anchored')
    base = na[na['anchor'].astype(str).str.startswith('breach') & (na['hypothesis'] == 'H2_FCC')]
    with col1, st.container(border=True):
        st.subheader('Essay 1 · Market reaction')
        st.markdown('**H2: Form 499 registrant vs other firms**, 30-day CAR (pp)')
        st.metric('Coefficient (pp)', f"{c['H2_FCC_coef']:+.2f}")
        lo, hi = c['H2_FCC_ci']
        st.markdown(f"95% CI [{lo:+.2f}, {hi:+.2f}] · HC3 p = {c['H2_FCC_p']:.3f}")
        if not base.empty:
            st.markdown(f"Parent-CIK clustered p = {float(base['p_cv1_parentcik'].iloc[0]):.3f}")
        st.markdown(f"Status: **{c['H2_FCC_status']}** · N = {c['N_regression']} "
                    f"({c['treated_regression']} treated events, "
                    f"{c['treated_parent_ciks_regression']} treated parent CIKs)")
        st.caption('Detail: **Essay 1 - Market Reaction** page.')
        source('outputs/rebuild/constants_v3.json', 'outputs/defense_supplement/e1_notification_anchored.csv')


def card_e2():
    lad = e2_table('t26_inference_ladder')
    r = row_starting(lad, 'procedure', 'CV3')
    dl = supp_table('e2_delay_ladder')
    d = dl[(dl['outcome'] == 'delay (raw days)') & dl['rung'].astype(str).str.startswith('CV3')].iloc[0]
    with col2, st.container(border=True):
        st.subheader('Essay 2 · Information environment')
        st.markdown('**Return volatility after notification**, Form 499 vs others (daily pp)')
        st.metric('Coefficient (daily pp)', f"{r['coef']:+.3f}")
        st.markdown(f"CV3 95% CI [{r['ci_lo']:+.3f}, {r['ci_hi']:+.3f}] · **CV3 p = {r['p']:.3f}**")
        st.markdown(f"**Disclosure delay (raw days):** {d['coef']:+.1f} days, "
                    f"CV3 p = {d['p']:.3f} (N = {int(d['N'])}, {int(d['n_treated_events'])} treated "
                    f"events, {int(d['G1'])} treated parent CIKs)")
        st.markdown('The announcement-window elevation is a pre-specified **secondary** result, '
                    'reported on the Essay 2 page.')
        st.caption('Detail: **Essay 2 - Information Environment** page.')
        source('outputs/tables/essay2_v2/t26_inference_ladder.csv',
               'outputs/defense_supplement/e2_delay_ladder.csv')


def card_e3():
    c = e3_constants()
    with col3, st.container(border=True):
        st.subheader('Essay 3 · Governance response')
        st.markdown('**Executive departure** after the breach, Form 499 vs others (pp)')
        rows = []
        for w in (30, 90, 180):
            rows.append({'Window (days)': w, 'Coefficient (pp)': round(100 * c[f'F1_{w}_coef'], 2),
                         'CV3 p': round(c[f'F1_{w}_p_cv3'], 3),
                         'MDE80 (pp)': round(100 * c[f'F1_{w}_mde80_cv3'], 1)})
        st.dataframe(pd.DataFrame(rows), hide_index=True, width='stretch')
        st.markdown(f"N = {c['N']} ({c['treated']} treated events, "
                    f"{c['treated_parent_ciks']} treated parent CIKs; {c['parent_ciks']} clusters)")
        st.caption('Detail: **Essay 3 - Governance Response** page.')
        source('outputs/essay3_v4/constants_essay3_v4.json')


guard(card_e1)
guard(card_e2)
guard(card_e3)

st.divider()
st.subheader('How to read this dashboard')
st.markdown(
    '- Every number is **read at run time from a committed pipeline output**; the file is named in '
    'the "Source:" caption under each chart or table. Nothing is typed into the page code, so the '
    'dashboard cannot drift from the essays.\n'
    '- The verified state of every result is the git tag **`defense-final`**.\n'
    '- Treated counts always name their level: events, organisations, or parent CIKs.\n'
    '- Essays 2 and 3 are governed by CV3 (cluster jackknife) with the wild cluster bootstrap as '
    'corroboration; HC3 is shown only as a lower bound on the standard error. Essay 1 reports HC3 '
    'with parent-CIK clustered p-values alongside.\n'
    '- No raw licensed data (CRSP or Compustat rows) is loaded; only results and documentation.\n'
    '- Pages: three essay pages, a **Robustness and Defense Supplement**, and **Limitations and '
    'Audit Trail**.'
)
