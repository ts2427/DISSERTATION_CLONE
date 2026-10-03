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
from plotly.subplots import make_subplots

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import ui  # noqa: E402
from data import e1_constants, e1_ledger_md, e1_table, guard, source  # noqa: E402
from ui import COLORS, CONTROL, TREATED, fmt_ci, fmt_int, fmt_num, fmt_p, fmt_pct  # noqa: E402

CONST_PATH = 'outputs/rebuild/constants_v3.json'
LEDGER_PATH = 'outputs/ESSAY1_SAMPLE_ATTRITION_LEDGER_V3.md'


def tpath(i: int) -> str:
    return f'outputs/rebuild/appendix_v3/table_{i}.csv'


# Hypothesis keys in constants_v3.json, in essay order, with plain-language labels.
HYP = [
    ('H1_timing', 'Immediate disclosure', 'H1'),
    ('H2_FCC', 'FCC Form 499 filer', 'H2'),
    ('H3_prior', 'Prior breaches (past year)', 'H3'),
    ('H4_health', 'Health-data breach', 'H4'),
]
HYP_LABEL = {k: f'{lab} ({h})' for k, lab, h in HYP}
# Which table 8 column carries each hypothesis (table 8 reports timing and FCC only).
T8_COL = {'H1_timing': 'Timing p', 'H2_FCC': 'FCC p'}

# Plain names for regression variables in the appendix tables.
VAR = {
    'const': 'Intercept',
    'fcc_form499': 'FCC Form 499 filer',
    'immediate_disclosure': 'Immediate disclosure',
    'prior_breaches_1yr': 'Prior breaches (past year)',
    'health_breach': 'Health-data breach',
    'firm_size_log': 'Firm size (log assets)',
    'leverage': 'Leverage',
    'roa': 'Return on assets',
}


def var_name(v) -> str:
    s = str(v)
    for k, lab in VAR.items():
        s = re.sub(rf'\b{k}\b', lab, s)
    return s.replace(' x ', ' × ').replace('=1', ' = 1').replace('=0', ' = 0')


def p3(x):
    return fmt_num(x, 3)


def p3s(x):
    return fmt_num(x, 3, signed=True)


def tost_bound() -> float:
    """The equivalence bound (pp), parsed from table 5's TOST column header."""
    df, _ = e1_table(5)
    for c in df.columns:
        m = re.search(r'TOST_p_([0-9.]+)', c)
        if m:
            return float(m.group(1))
    raise ValueError('table_5.csv has no TOST_p_<bound> column')


def small_caption(cap: str):
    if cap:
        st.caption(cap)


def hypothesis_frame() -> pd.DataFrame:
    c = e1_constants()
    t8, _ = e1_table(8)
    t8 = t8.set_index('Method')
    clust_row = next((m for m in t8.index if 'cluster' in m.lower()), None)
    rows = []
    for key, _lab, _h in HYP:
        lo, hi = c[f'{key}_ci']
        clust = (t8.loc[clust_row, T8_COL[key]]
                 if clust_row is not None and key in T8_COL else None)
        rows.append({
            'key': key, 'Hypothesis': HYP_LABEL[key],
            'coef': c[f'{key}_coef'], 'ci_lo': lo, 'ci_hi': hi,
            'p_hc3': c[f'{key}_p'], 'p_clust': clust,
            'tost_p': c[f'{key}_tost_p'], 'mde80': c[f'{key}_mde80'],
            'status': c[f'{key}_status'],
        })
    df = pd.DataFrame(rows)
    df['p_clust'] = pd.to_numeric(df['p_clust'], errors='coerce')
    df['95% CI'] = [fmt_ci(a, b, 3) for a, b in zip(df['ci_lo'], df['ci_hi'])]
    return df


# ------------------------------------------------------------------ header
ui.page_header('Essay 1 — Market reaction to breach events',
               'Is the 30-day abnormal stock return after a data breach associated with disclosure '
               'timing, Form 499 status, breach history, or health data?')
ui.framing_note()


def findings():
    c = e1_constants()
    df = hypothesis_frame()
    min_p = df['p_hc3'].min()
    min_lab = df.loc[df['p_hc3'].idxmin(), 'Hypothesis']
    clust_min = df['p_clust'].min()
    status_lab = df['status'].map(lambda s: ui.STATUS_STYLE.get(str(s).upper(), (str(s),))[0])
    groups = df.groupby(status_lab, sort=False)['Hypothesis'].apply(list)
    status_txt = '; '.join(f'{", ".join(h.split(" (")[0] for h in hs)}: {s.lower()}'
                           for s, hs in groups.items())
    any_sig = (min_p < 0.05) or (pd.notna(clust_min) and clust_min < 0.05)
    lead = ('At least one hypothesis p-value is below .05' if any_sig
            else 'None of the four hypotheses is significant at .05')
    h2 = df.set_index('key').loc['H2_FCC']
    items = [
        f'{lead} ({status_txt}). Smallest HC3 p = {fmt_p(min_p)} '
        f'({min_lab.split(" (")[0].lower()})'
        + (f'; smallest parent-CIK clustered p = {fmt_p(clust_min)}.' if pd.notna(clust_min)
           else '.'),
        f'Form 499 filers (H2): coefficient {fmt_num(h2["coef"], 2, signed=True)} pp of 30-day CAR, '
        f'95% CI {fmt_ci(h2["ci_lo"], h2["ci_hi"], 2)}, HC3 p {fmt_p(h2["p_hc3"])}; '
        f'the minimum detectable effect at 80% power is {fmt_num(h2["mde80"], 2)} pp.',
        f'Regression sample: {fmt_int(c["N_regression"])} events, of which '
        f'{fmt_int(c["treated_regression"])} are Form 499 filer events from '
        f'{fmt_int(c["treated_orgs_regression"])} organisations and '
        f'{fmt_int(c["treated_parent_ciks_regression"])} parent CIKs.',
    ]
    ui.key_findings(items)
    source(CONST_PATH, tpath(8))


guard(findings)


def intro():
    c = e1_constants()
    st.markdown(
        'Among publicly traded firms that experienced a data breach, is the 30-day '
        'market-adjusted cumulative abnormal return (CAR) associated with four event and firm '
        'characteristics?\n\n'
        '- **H1 — Immediate disclosure:** whether the breach was disclosed immediately\n'
        '- **H2 — FCC Form 499 filer:** the firm\'s regulatory status\n'
        '- **H3 — Prior breaches:** the firm\'s count of breaches in the preceding year\n'
        '- **H4 — Health-data breach:** whether the breach involved health data\n\n'
        f'The outcome is the 30-day CAR in percentage points, estimated by OLS on the regression '
        f'sample (N = {fmt_int(c["N_regression"])}). Inference is **HC3 heteroskedasticity-robust**, '
        'as reported in the essay; parent-CIK clustered p-values are shown alongside for comparison.'
    )
    source(CONST_PATH)


ui.section('What this essay asks')
guard(intro)

# ------------------------------------------------------------------ sample
ui.section('Sample')


def sample():
    c = e1_constants()
    cols = st.columns(4)
    cols[0].metric('Events after Gate 2', fmt_int(c['events_total']))
    cols[1].metric('With CRSP returns', fmt_int(c['events_crsp']))
    cols[2].metric('Regression sample (N)', fmt_int(c['N_regression']))
    cols[3].metric('Control events', fmt_int(c['N_regression'] - c['treated_regression']))
    st.markdown('**Form 499 filer (treated) counts in the regression sample**')
    cols = st.columns(4)
    cols[0].metric('Treated events', fmt_int(c['treated_regression']))
    cols[1].metric('Treated organisations', fmt_int(c['treated_orgs_regression']))
    cols[2].metric('Treated parent CIKs', fmt_int(c['treated_parent_ciks_regression']))
    st.caption(
        f'Treated events across stages: {fmt_int(c["treated_total"])} after Gate 2, '
        f'{fmt_int(c["treated_crsp"])} with CRSP data, {fmt_int(c["treated_regression"])} in the '
        'regression sample. One parent CIK can cover several organisations, so the organisation '
        'and parent-CIK counts differ.'
    )
    source(CONST_PATH)
    with st.expander('Sample attrition ledger (computed live by scripts/247)'):
        st.markdown(e1_ledger_md())
        source(LEDGER_PATH)


guard(sample)

# ------------------------------------------------------------------ hypotheses
ui.section('Hypothesis results',
           'Baseline OLS of the 30-day CAR on the four hypothesis variables and three accounting '
           'controls, with HC3 standard errors.')


def hypotheses():
    bound = tost_bound()
    df = hypothesis_frame()

    cols = st.columns(len(df))
    for col, (_, r) in zip(cols, df.iterrows()):
        with col:
            with st.container(border=True):
                st.markdown(f'**{r["Hypothesis"]}**')
                ui.status_badge(r['status'])
                st.caption(f'HC3 p {fmt_p(r["p_hc3"])} · TOST p {fmt_p(r["tost_p"])}')

    # Coefficient plot: point + 95% CI, zero line, TOST equivalence band (labelled in legend).
    fig = go.Figure()
    fig.add_vrect(x0=-bound, x1=bound, fillcolor=COLORS['band'], line_width=0, layer='below')
    fig.add_trace(go.Scatter(
        x=[None], y=[None], mode='markers', name=f'Equivalence band (±{bound:.2f} pp)',
        marker=dict(symbol='square', size=14, color='rgba(0, 32, 91, 0.18)'), hoverinfo='skip'))
    fig.add_vline(x=0, line_color=COLORS['muted'], line_dash='dash', line_width=1)
    fig.add_trace(go.Scatter(
        x=df['coef'], y=df['Hypothesis'], mode='markers',
        marker=dict(size=11, color=COLORS['navy']),
        error_x=dict(type='data', symmetric=False,
                     array=df['ci_hi'] - df['coef'], arrayminus=df['coef'] - df['ci_lo'],
                     thickness=2.5, width=8, color=COLORS['navy']),
        customdata=df[['ci_lo', 'ci_hi', 'p_hc3', 'status']].values,
        hovertemplate=('%{y}<br>coefficient %{x:.3f} pp<br>95% CI [%{customdata[0]:.3f}, '
                       '%{customdata[1]:.3f}]<br>HC3 p %{customdata[2]:.3f}<br>'
                       '%{customdata[3]}<extra></extra>'),
        name='Coefficient with 95% CI (HC3)'))
    fig.update_layout(
        title='Hypothesis coefficients on the 30-day CAR',
        xaxis_title='Coefficient (percentage points of 30-day CAR)',
        yaxis=dict(type='category', categoryorder='array', categoryarray=list(df['Hypothesis']),
                   autorange='reversed', title=None),
        legend=dict(orientation='h', yanchor='bottom', y=1.0, xanchor='right', x=1.0),
        height=400, margin=dict(l=10, r=10, t=80, b=40))
    ui.chart(fig)
    st.caption('H3 is per additional prior breach in the preceding year, so its scale differs '
               'from the three binary indicators.')
    source(CONST_PATH, tpath(5), tpath(8))

    st.subheader('Summary: status, equivalence test, power')
    ui.table(df, columns={
        'Hypothesis': 'Hypothesis', 'coef': 'Coefficient (pp)', '95% CI': '95% CI',
        'p_hc3': 'HC3 p', 'p_clust': 'Parent-CIK clustered p',
        'tost_p': f'TOST p (±{bound:.2f} pp)', 'mde80': 'MDE (80% power)', 'status': 'Status',
    }, formats={
        'Coefficient (pp)': p3s, 'HC3 p': fmt_p, 'Parent-CIK clustered p': fmt_p,
        f'TOST p (±{bound:.2f} pp)': fmt_p, 'MDE (80% power)': p3,
        'Status': lambda s: ui.STATUS_STYLE.get(str(s).upper(), (str(s),))[0],
    }, download='essay1_hypotheses.csv')
    st.caption('Parent-CIK clustered p-values come from table 8, which reports the timing and '
               'Form 499 terms only; H3 and H4 have no clustered value there.')
    source(CONST_PATH, tpath(8))

    t4, cap4 = e1_table(4)
    st.subheader('Table 4 — full baseline regression (HC3)')
    small_caption(cap4)
    t4 = t4.assign(Variable=t4['Variable'].map(var_name))
    ui.table(t4, columns={'Variable': 'Variable', 'Coef': 'Coefficient (pp)',
                          'SE': 'Std. error (HC3)', 'p': 'HC3 p'},
             formats={'Coefficient (pp)': p3s, 'Std. error (HC3)': p3, 'HC3 p': fmt_p},
             download='essay1_table4_baseline.csv')
    source(tpath(4))

    t5, cap5 = e1_table(5)
    with st.expander('Table 5 — hypothesis tests as reported in the appendix'):
        small_caption(cap5)
        tcol = next(c for c in t5.columns if c.startswith('TOST_p_'))
        t5 = t5.assign(Hypothesis=t5['Hypothesis'].map(lambda k: HYP_LABEL.get(k, k)))
        ui.table(t5, columns={'Hypothesis': 'Hypothesis', 'Coef': 'Coefficient (pp)',
                              'p': 'HC3 p', tcol: f'TOST p (±{bound:.2f} pp)',
                              'MDE80': 'MDE (80% power)', 'Status': 'Status'},
                 formats={'Coefficient (pp)': p3s, 'HC3 p': fmt_p,
                          f'TOST p (±{bound:.2f} pp)': fmt_p, 'MDE (80% power)': p3,
                          'Status': lambda s: ui.STATUS_STYLE.get(str(s).upper(), (str(s),))[0]})
        source(tpath(5))


guard(hypotheses)

# ------------------------------------------------------------------ descriptives
ui.section('Descriptives')


def descriptives():
    t3, cap3 = e1_table(3)
    st.subheader('30-day CAR by subgroup (table 3, regression sample)')
    small_caption(cap3)
    groups = t3[t3['Group'] != 'Difference'].copy()
    for col in ('Mean CAR', 'Median CAR'):
        groups[col] = pd.to_numeric(groups[col], errors='coerce')
    comps = list(dict.fromkeys(groups['Comparison']))
    fig = make_subplots(rows=1, cols=len(comps), subplot_titles=comps, shared_yaxes=True,
                        horizontal_spacing=0.04)
    for j, comp in enumerate(comps, start=1):
        g = groups[groups['Comparison'] == comp]
        colors = [TREATED if k == 0 else CONTROL for k in range(len(g))]
        fig.add_trace(go.Bar(
            x=g['Group'], y=g['Mean CAR'], marker_color=colors, name='Mean CAR',
            showlegend=(j == 1), customdata=g[['N']].values,
            hovertemplate='%{x}<br>mean CAR %{y:.3f} pp<br>N %{customdata[0]}<extra></extra>'),
            row=1, col=j)
        fig.add_trace(go.Scatter(
            x=g['Group'], y=g['Median CAR'], mode='markers', name='Median CAR',
            marker=dict(symbol='diamond', size=11, color=COLORS['red'],
                        line=dict(color='white', width=1)),
            showlegend=(j == 1),
            hovertemplate='%{x}<br>median CAR %{y:.3f} pp<extra></extra>'), row=1, col=j)
    fig.add_hline(y=0, line_color=COLORS['muted'], line_width=1)
    fig.update_yaxes(title_text='30-day CAR (pp)', row=1, col=1)
    fig.update_layout(height=400, bargap=0.35,
                      legend=dict(orientation='h', yanchor='bottom', y=1.08, xanchor='right', x=1),
                      margin=dict(l=10, r=10, t=80, b=40))
    ui.chart(fig)
    st.caption('Bars: group mean (dark = Form 499 filer, immediate, health, or any-prior group; '
               'grey = its comparison group). Diamonds: group median.')
    diffs = t3[t3['Group'] == 'Difference']
    st.markdown('**Differences in group means (Welch tests)**')
    ui.table(diffs, columns={'Comparison': 'Comparison', 'Mean CAR': 'Difference in means (pp)',
                             'Welch diff': 'Welch t', 'Welch p': 'Welch p'},
             formats={'Difference in means (pp)': p3s, 'Welch t': p3, 'Welch p': fmt_p})
    with st.expander('Table 3 — full table'):
        ui.table(t3, columns={'Comparison': 'Comparison', 'Group': 'Group',
                              'Mean CAR': 'Mean CAR (pp)', 'Median CAR': 'Median CAR (pp)',
                              'N': 'N', 'Welch diff': 'Welch t', 'Welch p': 'Welch p'},
                 formats={'Mean CAR (pp)': p3s, 'Median CAR (pp)': p3s, 'N': fmt_int,
                          'Welch t': p3, 'Welch p': fmt_p})
    source(tpath(3))

    t1, cap1 = e1_table(1)
    st.subheader('Summary statistics (table 1)')
    small_caption(cap1)
    names = {'car_30d': '30-day CAR (pp)', 'car_5d': '5-day CAR (pp)',
             'disclosure_delay_days': 'Disclosure delay (days)'}
    t1 = t1.assign(Variable=t1['Variable'].map(lambda v: names.get(v, var_name(v))))
    ui.table(t1, columns={'Variable': 'Variable', 'N': 'N', 'Mean': 'Mean', 'SD': 'SD',
                          'Median': 'Median'},
             formats={'N': fmt_int, 'Mean': p3, 'SD': p3, 'Median': p3})
    source(tpath(1))

    t2, cap2 = e1_table(2)
    st.subheader('Disclosure-date verification (table 2)')
    small_caption(cap2)
    ui.table(t2, columns={'Group': 'Group', 'N': 'N',
                          'Median gap (days)': 'Median gap (days)',
                          'Mean gap (days)': 'Mean gap (days)',
                          'Share with 8-K in 90d': '8-K within 90 days'},
             formats={'N': fmt_int, 'Median gap (days)': lambda v: fmt_num(v, 1),
                      'Mean gap (days)': lambda v: fmt_num(v, 1),
                      '8-K within 90 days': lambda v: fmt_pct(v, 1, scale=100)})
    source(tpath(2))


guard(descriptives)

# ------------------------------------------------------------------ robustness
ui.section('Robustness',
           'Each table re-estimates or extends the baseline specification. Captions are the '
           'appendix captions, read from the committed CSVs.')


def robustness():
    tabs = st.tabs(['By regime', 'Restricted samples', 'SE methods', 'Quartiles', 'Controls',
                    'Turnover', 'Leakage', 'Random forest'])

    with tabs[0]:
        t6, cap6 = e1_table(6)
        st.markdown('**Table 6 — timing effect by regulatory regime**')
        small_caption(cap6)
        t6 = t6.assign(Specification=t6['Specification'].map(var_name),
                       Term=t6['Term'].map(var_name))
        ui.table(t6, columns={'Specification': 'Specification', 'Term': 'Term',
                              'Coef': 'Coefficient (pp)', 'SE': 'Std. error (HC3)', 'p': 'HC3 p',
                              'N': 'N'},
                 formats={'Coefficient (pp)': p3s, 'Std. error (HC3)': p3, 'HC3 p': fmt_p,
                          'N': fmt_int})
        source(tpath(6))

    with tabs[1]:
        t7, cap7 = e1_table(7)
        st.markdown('**Table 7 — restricted samples**')
        small_caption(cap7)
        ui.table(t7, columns={'Restriction': 'Sample', 'Timing coef': 'Timing coef. (pp)',
                              'Timing p': 'Timing p', 'FCC coef': 'Form 499 coef. (pp)',
                              'FCC p': 'Form 499 p', 'ROA coef': 'ROA coef.', 'ROA p': 'ROA p',
                              'N': 'N'},
                 formats={'Timing coef. (pp)': p3s, 'Timing p': fmt_p,
                          'Form 499 coef. (pp)': p3s, 'Form 499 p': fmt_p, 'ROA coef.': p3s,
                          'ROA p': fmt_p, 'N': fmt_int})
        source(tpath(7))

    with tabs[2]:
        t8, cap8 = e1_table(8)
        st.markdown('**Table 8 — standard-error methods**')
        small_caption(cap8)
        t8 = t8.assign(Method=t8['Method'].map(
            lambda m: 'Parent-CIK clustered' if 'cluster' in str(m).lower() else m))
        ui.table(t8, columns={'Method': 'Standard errors', 'Timing p': 'Timing p',
                              'FCC p': 'Form 499 p', 'ROA p': 'ROA p'},
                 formats={'Timing p': fmt_p, 'Form 499 p': fmt_p, 'ROA p': fmt_p})
        source(tpath(8))

    with tabs[3]:
        qcols = {'Quartile': 'Size quartile', 'Coef': 'Coefficient (pp)', 'p': 'HC3 p',
                 'N': 'N', 'Treated N': 'Treated N'}
        qfmt = {'Coefficient (pp)': p3s, 'HC3 p': fmt_p, 'N': fmt_int, 'Treated N': fmt_int}
        a, b = st.columns(2)
        for col, i, title in ((a, 9, 'Table 9 — immediate-disclosure coefficient'),
                              (b, 10, 'Table 10 — Form 499 coefficient')):
            with col:
                t, cap = e1_table(i)
                st.markdown(f'**{title} by firm-size quartile**')
                small_caption(cap)
                ui.table(t, columns=qcols, formats=qfmt)
                source(tpath(i))

    with tabs[4]:
        t11, cap11 = e1_table(11)
        st.markdown('**Table 11 — adding calendar-year fixed effects**')
        small_caption(cap11)
        ui.table(t11, columns={'Spec': 'Specification', 'FCC coef': 'Form 499 coef. (pp)',
                               'p': 'Form 499 p'},
                 formats={'Form 499 coef. (pp)': p3s, 'Form 499 p': fmt_p})
        source(tpath(11))

        t12, cap12 = e1_table(12)
        st.markdown('**Table 12 — adding breach severity**')
        small_caption(cap12)
        ui.table(t12, columns={'Added control': 'Added control',
                               'FCC coef': 'Form 499 coef. (pp)', 'FCC p': 'Form 499 p',
                               'Control p': 'Control p', 'N': 'N', 'Note': 'Note'},
                 formats={'Form 499 coef. (pp)': p3s, 'Form 499 p': fmt_p,
                          'Control p': fmt_p, 'N': fmt_int})
        source(tpath(12))

        t13, cap13 = e1_table(13)
        st.markdown('**Table 13 — adding Fama-French factors**')
        small_caption(cap13)
        ui.table(t13, columns={'Model': 'Model', 'FCC p': 'Form 499 p', 'ROA p': 'ROA p'},
                 formats={'Form 499 p': fmt_p, 'ROA p': fmt_p})
        source(tpath(13))

    with tabs[5]:
        t14, cap14 = e1_table(14)
        st.markdown('**Table 14 — abnormal share turnover**')
        small_caption(cap14)
        coef_col = next(c for c in t14.columns if c.startswith('Coef'))
        body = t14[pd.to_numeric(t14[coef_col], errors='coerce').notna()].copy()
        notes = t14.loc[pd.to_numeric(t14[coef_col], errors='coerce').isna(), 'Variable']
        body['Variable'] = body['Variable'].map(var_name)
        ui.table(body, columns={'Variable': 'Variable', coef_col: 'Coefficient (log turnover)',
                                'SE': 'Std. error (HC3)', 'p': 'HC3 p'},
                 formats={'Coefficient (log turnover)': lambda v: fmt_num(v, 4, signed=True),
                          'Std. error (HC3)': lambda v: fmt_num(v, 4), 'HC3 p': fmt_p})
        for n in notes:
            st.caption(str(n))
        source(tpath(14))

    with tabs[6]:
        leakage()

    with tabs[7]:
        t15, cap15 = e1_table(15)
        st.markdown('**Table 15 — random-forest feature importances (descriptive only)**')
        small_caption(cap15)
        st.markdown('Feature importances describe which covariates the forest uses to fit the '
                    'CAR. They carry no causal meaning and are not a hypothesis test.')
        t15 = t15.assign(Feature=t15['Feature'].map(var_name),
                         Importance=pd.to_numeric(t15['Importance'], errors='coerce'))
        t15 = t15.sort_values('Importance')
        fig = go.Figure(go.Bar(x=t15['Importance'], y=t15['Feature'], orientation='h',
                               marker_color=COLORS['navy'],
                               hovertemplate='%{y}<br>importance %{x:.3f}<extra></extra>'))
        fig.update_layout(xaxis_title='Importance (share of total)', yaxis_title=None,
                          height=340, margin=dict(l=10, r=10, t=20, b=40))
        ui.chart(fig)
        source(tpath(15))


def leakage():
    t16, cap16 = e1_table(16)
    st.markdown('**Table 16 — pre-event leakage panel**')
    small_caption(cap16)
    g = t16[~t16['Group'].astype(str).str.startswith('Difference')].copy()
    g['Mean CAR (pp)'] = pd.to_numeric(g['Mean CAR (pp)'], errors='coerce')
    g['Group'] = g['Group'].replace({'Treated': 'Form 499 filer', 'Untreated': 'Control'})
    fig = px.bar(g, x='Window', y='Mean CAR (pp)', color='Group', barmode='group',
                 facet_col='Panel', hover_data={'N': True, 'p': ':.3f'}, height=420,
                 color_discrete_map={'All': ui.SEQ[1], 'Form 499 filer': TREATED,
                                     'Control': CONTROL},
                 category_orders={'Window': list(dict.fromkeys(g['Window'])),
                                  'Group': ['All', 'Form 499 filer', 'Control']})
    fig.for_each_annotation(lambda a: a.update(text=a.text.split('=')[-1]))
    fig.update_xaxes(title_text='Pre-event window (trading days)')
    fig.update_yaxes(title_text=None)
    fig.update_yaxes(title_text='Mean CAR (pp)', col=1)
    fig.add_hline(y=0, line_color=COLORS['muted'], line_width=1)
    fig.update_layout(legend=dict(orientation='h', yanchor='bottom', y=1.1, xanchor='right', x=1,
                                  title=None),
                      margin=dict(l=10, r=10, t=80, b=40))
    ui.chart(fig)
    with st.expander('Table 16 — full panel (including Welch differences)'):
        ui.table(t16, columns={'Panel': 'Panel', 'Window': 'Window', 'Group': 'Group', 'N': 'N',
                               'Mean CAR (pp)': 'Mean CAR (pp)', 'Median': 'Median (pp)',
                               'SD': 'SD', 't': 't', 'p': 'p'},
                 formats={'N': fmt_int, 'Mean CAR (pp)': p3s, 'Median (pp)': p3s, 'SD': p3,
                          't': p3, 'p': fmt_p})
    source(tpath(16))


guard(robustness)
