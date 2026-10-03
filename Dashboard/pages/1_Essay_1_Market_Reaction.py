"""
Essay 1 - market reaction to data-breach events (30-day market-adjusted CAR).

Every number on this page is read at run time from committed Essay 1 outputs:
    outputs/rebuild/constants_v3.json
    outputs/rebuild/appendix_v3/table_1.csv ... table_16.csv
    outputs/ESSAY1_SAMPLE_ATTRITION_LEDGER_V3.md
Nothing here reads raw licensed data or row-level event files.
"""
import re
import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from data import FRAMING, e1_constants, e1_ledger_md, e1_table, guard, source  # noqa: E402

st.set_page_config(page_title='Essay 1 - Market reaction', layout='wide')

CONST_PATH = 'outputs/rebuild/constants_v3.json'
LEDGER_PATH = 'outputs/ESSAY1_SAMPLE_ATTRITION_LEDGER_V3.md'


def tpath(i: int) -> str:
    return f'outputs/rebuild/appendix_v3/table_{i}.csv'


# Hypothesis keys in constants_v3.json, in essay order, with plain-language labels.
HYP = [
    ('H1_timing', 'H1 - immediate disclosure'),
    ('H2_FCC', 'H2 - FCC Form 499 filer'),
    ('H3_prior', 'H3 - prior breaches (1 yr)'),
    ('H4_health', 'H4 - health-data breach'),
]
# Which table 8 column carries each hypothesis (table 8 reports timing and FCC only).
T8_COL = {'H1_timing': 'Timing p', 'H2_FCC': 'FCC p'}


def tost_bound() -> float:
    """The equivalence bound (pp), parsed from table 5's TOST column header."""
    df, _ = e1_table(5)
    for c in df.columns:
        m = re.search(r'TOST_p_([0-9.]+)', c)
        if m:
            return float(m.group(1))
    raise ValueError('table_5.csv has no TOST_p_<bound> column')


def show_table(i: int, title: str | None = None, expand: bool = False):
    df, cap = e1_table(i)
    with st.expander(title or f'Table {i}', expanded=expand):
        if cap:
            st.caption(cap)
        st.dataframe(df, hide_index=True, width='stretch')
        source(tpath(i))
    return df


# ------------------------------------------------------------------ header
st.title('Essay 1 - Market reaction to breach events')
st.info(FRAMING)


def intro():
    c = e1_constants()
    st.markdown(
        '**What this essay asks.** Among publicly traded firms that experienced a data breach, '
        'is the 30-day market-adjusted cumulative abnormal return (CAR) associated with four '
        'event and firm characteristics?\n\n'
        '- **H1** - whether the breach was disclosed immediately (timing)\n'
        '- **H2** - whether the firm is an FCC Form 499 filer (regulatory status)\n'
        '- **H3** - the firm\'s count of prior breaches in the preceding year\n'
        '- **H4** - whether the breach involved health data\n\n'
        f'The outcome is the 30-day CAR in percentage points, estimated by OLS on the regression '
        f'sample (N = {c["N_regression"]}). Inference is **HC3 heteroskedasticity-robust**, which is '
        'what the essay reports; parent-CIK clustered p-values are shown alongside for comparison. '
        'The design is descriptive and cross-sectional.'
    )
    source(CONST_PATH)


guard(intro)

# ------------------------------------------------------------------ sample
st.header('Sample')


def sample():
    c = e1_constants()
    cols = st.columns(4)
    cols[0].metric('Events after Gate 2 (all)', c['events_total'])
    cols[1].metric('Events with CRSP data', c['events_crsp'])
    cols[2].metric('Regression sample (N)', c['N_regression'])
    cols[3].metric('Control events in regression', c['N_regression'] - c['treated_regression'])
    st.markdown('**Treated (Form 499 filer) counts in the regression sample, at three levels**')
    cols = st.columns(3)
    cols[0].metric('Treated events', c['treated_regression'])
    cols[1].metric('Treated organisations', c['treated_orgs_regression'])
    cols[2].metric('Treated parent CIKs', c['treated_parent_ciks_regression'])
    st.caption(
        f'Treated events across stages: {c["treated_total"]} after Gate 2, {c["treated_crsp"]} with '
        f'CRSP data, {c["treated_regression"]} in the regression sample. One parent CIK can cover '
        'several organisations, so the organisation and parent-CIK counts differ.'
    )
    source(CONST_PATH)
    with st.expander('Sample attrition ledger (computed live by scripts/247)'):
        st.markdown(e1_ledger_md())
        source(LEDGER_PATH)


guard(sample)

# ------------------------------------------------------------------ hypotheses
st.header('Hypothesis results')


def hypotheses():
    c = e1_constants()
    bound = tost_bound()
    t8, t8cap = e1_table(8)
    t8 = t8.set_index('Method')
    clust_row = next((m for m in t8.index if 'cluster' in m.lower()), None)

    rows = []
    for key, label in HYP:
        lo, hi = c[f'{key}_ci']
        clust = (t8.loc[clust_row, T8_COL[key]]
                 if clust_row is not None and key in T8_COL else None)
        rows.append({
            'Hypothesis': label, 'key': key,
            'Coef (pp)': c[f'{key}_coef'], 'CI low': lo, 'CI high': hi,
            'HC3 p': c[f'{key}_p'],
            'Parent-CIK clustered p': clust,
            'TOST p': c[f'{key}_tost_p'], 'MDE80': c[f'{key}_mde80'],
            'Status': c[f'{key}_status'],
        })
    df = pd.DataFrame(rows)
    df['Parent-CIK clustered p'] = pd.to_numeric(df['Parent-CIK clustered p'], errors='coerce')

    min_p = df['HC3 p'].min()
    clust_min = pd.to_numeric(df['Parent-CIK clustered p'], errors='coerce').min()
    any_sig = (min_p < 0.05) or (pd.notna(clust_min) and clust_min < 0.05)
    if any_sig:
        st.warning('At least one hypothesis p-value is below .05 in the committed outputs.')
    else:
        st.success(
            f'All four hypotheses are nulls. No hypothesis p-value is below .05 '
            f'(smallest HC3 p = {min_p:.3f}'
            + (f'; smallest parent-CIK clustered p = {clust_min:.3f}' if pd.notna(clust_min) else '')
            + ').'
        )

    stat_cols = st.columns(len(df))
    for col, (_, r) in zip(stat_cols, df.iterrows()):
        col.metric(r['Hypothesis'], r['Status'], help=f"HC3 p = {r['HC3 p']:.3f}")

    # Coefficient plot: point + 95% CI, zero line, TOST equivalence band.
    fig = go.Figure()
    fig.add_vrect(x0=-bound, x1=bound, fillcolor='rgba(120,160,200,0.18)', line_width=0,
                  annotation_text=f'TOST equivalence band (+/-{bound:.2f} pp)',
                  annotation_position='top left')
    fig.add_vline(x=0, line_color='grey', line_dash='dash')
    fig.add_trace(go.Scatter(
        x=df['Coef (pp)'], y=df['Hypothesis'], mode='markers',
        marker=dict(size=11, color='#1f4e79'),
        error_x=dict(type='data', symmetric=False,
                     array=df['CI high'] - df['Coef (pp)'],
                     arrayminus=df['Coef (pp)'] - df['CI low'],
                     thickness=2, width=6),
        customdata=df[['CI low', 'CI high', 'HC3 p', 'Status']].values,
        hovertemplate=('%{y}<br>coef %{x:.3f} pp<br>95% CI [%{customdata[0]:.3f}, '
                       '%{customdata[1]:.3f}]<br>HC3 p %{customdata[2]:.3f}<br>'
                       '%{customdata[3]}<extra></extra>'),
        name='Coefficient (95% CI, HC3)'))
    fig.update_layout(
        title='Hypothesis coefficients on the 30-day CAR (pp), 95% HC3 confidence intervals',
        xaxis_title='Coefficient (percentage points of 30-day CAR)',
        yaxis=dict(autorange='reversed'), height=380, showlegend=False,
        margin=dict(l=10, r=10, t=60, b=40))
    st.plotly_chart(fig, width='stretch')
    st.caption('H3 is per additional prior breach in the preceding year, so its scale differs '
               'from the three binary indicators.')
    source(CONST_PATH, tpath(5), tpath(8))

    st.subheader('Summary: status, equivalence test, power')
    st.dataframe(df.drop(columns='key'), hide_index=True, width='stretch',
                 column_config={
                     'Coef (pp)': st.column_config.NumberColumn(format='%.4f'),
                     'CI low': st.column_config.NumberColumn(format='%.4f'),
                     'CI high': st.column_config.NumberColumn(format='%.4f'),
                     'HC3 p': st.column_config.NumberColumn(format='%.4f'),
                     'Parent-CIK clustered p': st.column_config.NumberColumn(format='%.4f'),
                     'TOST p': st.column_config.NumberColumn(format='%.4f'),
                     'MDE80': st.column_config.NumberColumn(format='%.4f'),
                 })
    st.caption('Parent-CIK clustered p-values come from table 8, which reports the timing and '
               'FCC terms only; H3 and H4 have no clustered value there.')
    source(CONST_PATH, tpath(8))

    t5, cap5 = e1_table(5)
    st.markdown('**Table 5 - hypothesis tests as reported in the appendix**')
    if cap5:
        st.caption(cap5)
    st.dataframe(t5, hide_index=True, width='stretch')
    source(tpath(5))

    show_table(4, 'Table 4 - full baseline regression (HC3)')


guard(hypotheses)

# ------------------------------------------------------------------ descriptives
st.header('Descriptives')


def descriptives():
    t1, cap1 = e1_table(1)
    st.subheader('Table 1 - summary statistics (CRSP-covered sample)')
    if cap1:
        st.caption(cap1)
    st.dataframe(t1, hide_index=True, width='stretch')
    source(tpath(1))

    t3, cap3 = e1_table(3)
    st.subheader('Table 3 - 30-day CAR by subgroup (regression sample)')
    if cap3:
        st.caption(cap3)
    groups = t3[t3['Group'] != 'Difference'].copy()
    groups['Label'] = groups['Comparison'] + ': ' + groups['Group']
    long = groups.melt(id_vars=['Comparison', 'Group', 'Label', 'N'],
                       value_vars=['Mean CAR', 'Median CAR'],
                       var_name='Statistic', value_name='CAR (pp)')
    fig = px.bar(long, x='Group', y='CAR (pp)', color='Statistic', barmode='group',
                 facet_col='Comparison', facet_col_spacing=0.05,
                 hover_data={'N': True}, height=380,
                 color_discrete_sequence=['#1f4e79', '#8fb3d9'])
    fig.for_each_annotation(lambda a: a.update(text=a.text.split('=')[-1]))
    fig.update_xaxes(matches=None, title=None)
    fig.add_hline(y=0, line_color='grey', line_width=1)
    fig.update_layout(margin=dict(l=10, r=10, t=40, b=40))
    st.plotly_chart(fig, width='stretch')
    diffs = t3[t3['Group'] == 'Difference']
    st.markdown('Differences in group means (Welch tests):')
    st.dataframe(diffs[['Comparison', 'Mean CAR', 'Welch diff', 'Welch p']],
                 hide_index=True, width='stretch')
    with st.expander('Table 3 - full table'):
        st.dataframe(t3, hide_index=True, width='stretch')
    source(tpath(3))

    t2, cap2 = e1_table(2)
    st.subheader('Table 2 - disclosure-date verification (8-K filing activity)')
    if cap2:
        st.caption(cap2)
    st.dataframe(t2, hide_index=True, width='stretch')
    source(tpath(2))


guard(descriptives)

# ------------------------------------------------------------------ robustness
st.header('Robustness (Essay 1)')
st.markdown('Each table re-estimates or extends the baseline specification. Captions are the '
            'appendix captions, read from the committed CSVs.')


def robustness():
    show_table(6, 'Table 6 - timing effect by regulatory regime')
    show_table(7, 'Table 7 - restricted samples')
    show_table(8, 'Table 8 - standard-error methods (OLS, HC1, HC3, parent-CIK clustered)')
    show_table(9, 'Table 9 - timing coefficient by firm-size quartile')
    show_table(10, 'Table 10 - Form 499 coefficient by firm-size quartile')
    show_table(11, 'Table 11 - adding calendar-year fixed effects')
    show_table(12, 'Table 12 - adding breach severity')
    show_table(13, 'Table 13 - adding Fama-French factors')
    show_table(14, 'Table 14 - abnormal share turnover')

    t15, cap15 = e1_table(15)
    with st.expander('Table 15 - random-forest feature importances (descriptive only)'):
        if cap15:
            st.caption(cap15)
        st.markdown('Feature importances describe which covariates the forest uses to fit the '
                    'CAR. They carry no causal meaning and are not a hypothesis test.')
        fig = px.bar(t15.sort_values('Importance'), x='Importance', y='Feature',
                     orientation='h', height=320, color_discrete_sequence=['#1f4e79'])
        fig.update_layout(margin=dict(l=10, r=10, t=20, b=30))
        st.plotly_chart(fig, width='stretch')
        st.dataframe(t15, hide_index=True, width='stretch')
        source(tpath(15))


guard(robustness)


def leakage():
    t16, cap16 = e1_table(16)
    st.subheader('Table 16 - pre-event leakage panel')
    if cap16:
        st.caption(cap16)
    g = t16[~t16['Group'].astype(str).str.startswith('Difference')].copy()
    fig = px.bar(g, x='Window', y='Mean CAR (pp)', color='Group', barmode='group',
                 facet_col='Panel', hover_data={'N': True, 'p': ':.4f'}, height=400,
                 color_discrete_sequence=['#7f7f7f', '#1f4e79', '#8fb3d9'],
                 category_orders={'Window': list(dict.fromkeys(g['Window']))})
    fig.for_each_annotation(lambda a: a.update(text=a.text.split('=')[-1]))
    fig.add_hline(y=0, line_color='grey', line_width=1)
    fig.update_layout(margin=dict(l=10, r=10, t=50, b=40))
    st.plotly_chart(fig, width='stretch')
    with st.expander('Table 16 - full panel (including Welch differences)'):
        st.dataframe(t16, hide_index=True, width='stretch')
    source(tpath(16))


guard(leakage)
