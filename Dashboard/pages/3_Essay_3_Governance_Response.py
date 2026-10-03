"""
Essay 3 - Governance response.

Descriptive, post-2007 cross-sectional comparison of executive departures (Item 5.02 8-K filings,
coded by a rule-based classifier) after breach notification, by FCC Form 499 status.

Every number on this page is read at run time from committed outputs under outputs/essay3_v4/,
outputs/essay3_q4/ and outputs/essay3_appendix/. Nothing is typed in. Essay 3 v4 is the
authoritative vintage; the retired v3 run appears only in one labelled comparison expander.
"""
import sys
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from data import FRAMING, e3_constants, e3_q4_table, e3_table, guard, source  # noqa: E402

st.set_page_config(page_title='Essay 3 - Governance response', layout='wide')

# Conventions (not results): significance level used to label verdicts, and chart colours.
ALPHA = 0.05
BLUE = '#2a78d6'     # estimates / treated
ORANGE = '#eb6834'   # control / comparison marker
GRAY = '#8a8984'     # bounding exercises, reference lines

V4 = 'outputs/essay3_v4'
Q4 = 'outputs/essay3_q4'


def pp(x, nd=2):
    """Proportion -> percentage points string."""
    if pd.isna(x):
        return 'n/a'
    return f'{x * 100:+.{nd}f}'


def pct(x, nd=1):
    if pd.isna(x):
        return 'n/a'
    return f'{x * 100:.{nd}f}%'


def p3(x):
    if pd.isna(x):
        return 'n/a'
    return f'{x:.3f}'


def wlabel(w):
    return f'{int(w)}-day'


def ci_chart(df, label_col, title, height=320, color_col=None, colors=None):
    """Horizontal-free vertical dot + CV3 95% CI chart in percentage points, zero line."""
    fig = go.Figure()
    groups = [(None, df)] if color_col is None else list(df.groupby(color_col, sort=False))
    for key, g in groups:
        c = BLUE if colors is None else colors.get(key, BLUE)
        fig.add_trace(go.Scatter(
            x=g[label_col], y=g['coef'] * 100, mode='markers', name=str(key) if key else 'estimate',
            marker=dict(size=11, color=c),
            error_y=dict(type='data', symmetric=False, thickness=2, width=6, color=c,
                         array=(g['ci_cv3_hi'] - g['coef']) * 100,
                         arrayminus=(g['coef'] - g['ci_cv3_lo']) * 100),
            customdata=g[['ci_cv3_lo', 'ci_cv3_hi', 'p_cv3', 'p_wcr']].values,
            hovertemplate=('%{x}<br>coef %{y:+.2f} pp<br>CV3 95% CI [%{customdata[0]:.4f}, '
                           '%{customdata[1]:.4f}] (proportion)<br>CV3 p %{customdata[2]:.3f}'
                           '<br>WCR p %{customdata[3]:.3f}<extra></extra>')))
    fig.add_hline(y=0, line=dict(color=GRAY, width=1, dash='dash'))
    fig.update_layout(title=title, height=height, margin=dict(l=10, r=10, t=50, b=10),
                      yaxis_title='Coefficient (percentage points)', showlegend=color_col is not None)
    return fig


# ====================================================================== header
st.title('Essay 3 - Governance response to breach notification')
st.info(FRAMING)
st.markdown(
    '**What the essay asks.** Among breached public firms, is FCC Form 499 status related to the '
    'probability that an executive departure is disclosed (Item 5.02 of Form 8-K, coded by a '
    'rule-based classifier) within fixed windows after the breach is publicly notified? The model '
    'is a linear probability model, so each coefficient is a difference in the probability of a '
    'departure between Form 499 events and other events, shown here **in percentage points '
    '(coefficient x 100)**.\n\n'
    '**Inference.** The governing inference is **CV3** (cluster jackknife on parent CIK) together '
    'with the **restricted wild cluster bootstrap (WCR)**. HC3 is shown only for comparison and is '
    '**disqualified**: it ignores the clustering of events within parent firms.')


# ====================================================================== sample
def sample():
    st.header('Sample')
    c = e3_constants()
    cols = st.columns(5)
    cols[0].metric('Events (N)', f"{c['N']:,}")
    cols[1].metric('Form 499 (treated) events', f"{c['treated']:,}")
    cols[2].metric('Other (control) events', f"{c['control']:,}")
    cols[3].metric('Parent CIKs (G)', f"{c['parent_ciks']:,}")
    cols[4].metric('Treated parent CIKs (G1)', f"{c['treated_parent_ciks']:,}")
    st.caption(f"Effective number of clusters G* = {c['F1_30_G_star']}; coefficient of variation of "
               f"cluster size = {c['F1_30_cluster_size_cv']}. Outcome classifier: {c['classifier']}.")
    source(f'{V4}/constants_essay3_v4.json')

    led = e3_table('e_ledger')
    left, right = st.columns([3, 2])
    with left:
        fig = go.Figure(go.Funnel(y=led['step'], x=led['N'], textinfo='value',
                                  marker=dict(color=BLUE)))
        fig.update_layout(title='From notification records to the analysis sample', height=460,
                          margin=dict(l=10, r=10, t=50, b=10))
        st.plotly_chart(fig, width='stretch')
    with right:
        show = led[['step', 'N', 'treated', 'control', 'treated_parent_ciks']].copy()
        for k in ['treated', 'control', 'treated_parent_ciks']:
            show[k] = show[k].map(lambda v: '' if pd.isna(v) else f'{int(v):,}')
        st.dataframe(show, hide_index=True, width='stretch', height=420)
    with st.expander('Ledger notes (why events leave at each step)'):
        st.dataframe(led[['step', 'N', 'note']], hide_index=True, width='stretch')
    st.caption('Rows above the canonical-event step are record-level, where treatment is undefined.')
    source(f'{V4}/e_ledger.csv')


guard(sample)


# ====================================================================== main result
def main_result():
    st.header('Main result: executive departure after notification')
    lad = e3_table('f1_ladder').copy()
    lad['label'] = lad['window'].map(wlabel)
    n_sig = int((lad['p_cv3'] < ALPHA).sum() + (lad['p_wcr'] < ALPHA).sum())
    verdict = ('No window rejects at the conventional level under either CV3 or WCR.' if n_sig == 0
               else 'At least one window rejects under CV3 or WCR - see the table.')
    st.markdown(f'**{verdict}**')

    st.plotly_chart(ci_chart(lad, 'label', 'Form 499 coefficient by window, CV3 95% CI '
                             '(percentage points)'), width='stretch')

    tab = pd.DataFrame({
        'Window': lad['label'],
        'Coef (pp)': lad['coef'].map(pp),
        'CV3 SE (pp)': lad['se_cv3'].map(lambda v: f'{v * 100:.2f}'),
        'CV3 95% CI (pp)': [f'[{pp(a)}, {pp(b)}]' for a, b in zip(lad['ci_cv3_lo'], lad['ci_cv3_hi'])],
        'CV3 p': lad['p_cv3'].map(p3),
        'WCR p': lad['p_wcr'].map(p3),
        'WCR 95% CI (pp)': [f'[{pp(a)}, {pp(b)}]' for a, b in zip(lad['ci_wcr_lo'], lad['ci_wcr_hi'])],
        'MDE80 (pp, CV3)': lad['mde80_cv3'].map(lambda v: f'{v * 100:.2f}'),
        'Treated departure rate': lad['treated_mean'].map(pct),
        'Control departure rate': lad['control_mean'].map(pct),
        'MDE80 / control rate': (lad['mde80_cv3'] / lad['control_mean']).map(lambda v: f'{v:.2f}x'),
        'HC3 p (disqualified; comparison only)': lad['p_hc3'].map(p3),
    })
    st.dataframe(tab, hide_index=True, width='stretch')
    st.caption(f"N = {int(lad['n'].iloc[0]):,}; G = {int(lad['G'].iloc[0])} parent CIKs; "
               f"G1 = {int(lad['G1'].iloc[0])} treated clusters; WCR draws B = {int(lad['B_wcr'].iloc[0]):,}.")

    lines = []
    for _, r in lad.iterrows():
        ratio = r['mde80_cv3'] / r['control_mean']
        lines.append(f"- **{r['label']}**: the minimum effect detectable with 80% power is "
                     f"{r['mde80_cv3'] * 100:.2f} pp against a control departure rate of "
                     f"{pct(r['control_mean'])}, i.e. {ratio:.2f} times the base rate"
                     + (' - larger than the base rate itself.' if ratio > 1 else '.'))
    st.markdown('**What MDE80 implies.** The design can only detect differences on the scale of the '
                'base rate, so a null here rules out very large differences only:\n' + '\n'.join(lines))
    source(f'{V4}/f1_ladder.csv')

    with st.expander('Departure counts and rates by window and group (Essay 3 Table 6)'):
        t6 = e3_q4_table('table06')
        keep = ['window', 'group', 'n', 'any_502', 'any_502_rate', 'exec_departure', 'exec_rate',
                'ceo_departure', 'ceo_rate', 'director_only', 'director_rate']
        t6 = t6[[k for k in keep if k in t6.columns]].copy()
        for k in [k for k in t6.columns if k.endswith('_rate')]:
            t6[k] = t6[k].map(pct)
        st.dataframe(t6, hide_index=True, width='stretch')
        source(f'{Q4}/table06.csv')


guard(main_result)


# ====================================================================== placebo + BH
def placebo_bh():
    st.header('Placebo and multiple-testing adjustment')
    pl = e3_table('f4_placebo').iloc[0]
    st.markdown('**Placebo: executive departures before notification.** The same model with a '
                'pre-notification departure outcome; a non-null here would point to firm differences '
                'unrelated to the breach.')
    cols = st.columns(5)
    cols[0].metric('Placebo coef (pp)', pp(pl['coef']))
    cols[1].metric('CV3 95% CI (pp)', f"[{pp(pl['ci_cv3_lo'])}, {pp(pl['ci_cv3_hi'])}]")
    cols[2].metric('CV3 p', p3(pl['p_cv3']))
    cols[3].metric('WCR p', p3(pl['p_wcr']))
    cols[4].metric('MDE80 (pp)', f"{pl['mde80_cv3'] * 100:.2f}")
    st.caption(f"Treated rate {pct(pl['treated_mean'])} vs control rate {pct(pl['control_mean'])}. "
               f"HC3 p (disqualified; comparison only) = {p3(pl['p_hc3'])}.")
    source(f'{V4}/f4_placebo.csv')

    st.subheader('Benjamini-Hochberg adjustment within each test family')
    it = e3_table('i_tests')
    fam = it.groupby('family', sort=False).agg(tests=('test', 'size'), min_cv3_p=('p', 'min'),
                                               min_wcr_p=('p_wcr', 'min'), min_bh_p=('p_bh', 'min'))
    fam['any BH-adjusted p below the conventional level'] = fam['min_bh_p'] < ALPHA
    fam = fam.reset_index()
    for k in ['min_cv3_p', 'min_wcr_p', 'min_bh_p']:
        fam[k] = fam[k].map(p3)
    st.dataframe(fam, hide_index=True, width='stretch')
    st.caption('p is the CV3 p-value; p_bh is the BH-adjusted CV3 p-value within the family.')
    with st.expander(f'All {len(it)} tests'):
        st.dataframe(it, hide_index=True, width='stretch')
    source(f'{V4}/i_tests.csv')


guard(placebo_bh)


# ====================================================================== sensitivities
def sensitivities():
    st.header('Sensitivities')
    s = e3_table('f3_sensitivities').copy()
    s['kind'] = s['row_type'].map(lambda v: 'bounding exercise (not an estimate)'
                                  if 'BOUNDING' in str(v).upper() else 'estimate')
    windows = sorted(s['window'].unique())
    fig = make_subplots(rows=1, cols=len(windows), shared_yaxes=True,
                        subplot_titles=[wlabel(w) for w in windows])
    order = list(dict.fromkeys(s['sensitivity']))
    colors = {'estimate': BLUE, 'bounding exercise (not an estimate)': GRAY}
    for i, w in enumerate(windows, start=1):
        g = s[s['window'] == w]
        for kind, gk in g.groupby('kind', sort=False):
            fig.add_trace(go.Scatter(
                y=gk['sensitivity'], x=gk['coef'] * 100, mode='markers', name=kind,
                legendgroup=kind, showlegend=(i == 1), marker=dict(size=9, color=colors[kind]),
                error_x=dict(type='data', symmetric=False, thickness=2, width=4, color=colors[kind],
                             array=(gk['ci_cv3_hi'] - gk['coef']) * 100,
                             arrayminus=(gk['coef'] - gk['ci_cv3_lo']) * 100),
                customdata=gk[['p_cv3', 'p_wcr']].values,
                hovertemplate=('%{y}<br>coef %{x:+.2f} pp<br>CV3 p %{customdata[0]:.3f}'
                               '<br>WCR p %{customdata[1]:.3f}<extra></extra>')), row=1, col=i)
        fig.add_vline(x=0, line=dict(color=GRAY, width=1, dash='dash'), row=1, col=i)
        fig.update_xaxes(title_text='pp', row=1, col=i)
    fig.update_yaxes(categoryorder='array', categoryarray=order[::-1], automargin=True)
    fig.update_layout(height=470, margin=dict(l=10, r=10, t=60, b=10),
                      title='Sensitivity coefficients with CV3 95% CIs (percentage points)',
                      legend=dict(orientation='h', y=-0.15))
    st.plotly_chart(fig, width='stretch')

    n_bound = int((s['kind'] != 'estimate').sum())
    hc3_states = s['hc3_status'].dropna().unique()
    it = e3_table('i_tests')
    min_bh = it.loc[it['family'] == 'sensitivities', 'p_bh'].min()
    st.markdown(
        f'- Gray rows ({n_bound}) are **bounding exercises**: the outcome is recall-corrected at the '
        'ends of the classifier recall confidence intervals. They show how far measurement error could '
        'move the estimate; they are not estimates.\n'
        '- HC3 status on every sensitivity row: ' + '; '.join(f'*{h}*' for h in hc3_states) + '\n'
        f"- Smallest BH-adjusted p in the sensitivity family: "
        f"{p3(min_bh)}.")
    with st.expander('Sensitivity table'):
        t = s[['window', 'sensitivity', 'row_type', 'coef', 'ci_cv3_lo', 'ci_cv3_hi', 'p_cv3', 'p_wcr',
               'mde80_cv3', 'p_hc3', 'hc3_status']].copy()
        for k in ['coef', 'ci_cv3_lo', 'ci_cv3_hi']:
            t[k] = t[k].map(pp)
        t['mde80_cv3'] = t['mde80_cv3'].map(lambda v: f'{v * 100:.2f}')
        t = t.rename(columns={'coef': 'coef (pp)', 'ci_cv3_lo': 'CV3 lo (pp)', 'ci_cv3_hi': 'CV3 hi (pp)',
                              'mde80_cv3': 'MDE80 (pp)', 'p_hc3': 'p_hc3 (DISQUALIFIED)'})
        st.dataframe(t, hide_index=True, width='stretch')
    source(f'{V4}/f3_sensitivities.csv')

    st.subheader('Leave-one-cluster-out (parent CIK)')
    lo = e3_table('f3_loco').copy()
    diag = e3_table('f1_cluster_diagnostics')
    fig = go.Figure()
    for _, r in lo.iterrows():
        d = diag[diag['window'] == r['window']]
        fig.add_trace(go.Box(x=[wlabel(r['window'])] * len(d), y=d['coef_without'] * 100,
                             boxpoints='all', jitter=0.4, pointpos=0, marker=dict(size=5, color=BLUE),
                             line=dict(color='rgba(0,0,0,0)'), fillcolor='rgba(0,0,0,0)',
                             name='one parent CIK dropped', showlegend=bool(_ == lo.index[0]),
                             customdata=d[['deleted_parent_cik', 'cluster_size']].values,
                             hovertemplate=('without CIK %{customdata[0]} (%{customdata[1]} events)'
                                            '<br>coef %{y:+.2f} pp<extra></extra>')))
    fig.add_trace(go.Scatter(x=lo['window'].map(wlabel), y=lo['full_coef'] * 100, mode='markers',
                             name='full sample', marker=dict(size=14, color='black', symbol='line-ew-open',
                                                             line=dict(width=3))))
    fig.add_trace(go.Scatter(x=lo['window'].map(wlabel), y=lo['without_TMobile'] * 100, mode='markers',
                             name='without T-Mobile', marker=dict(size=11, color=ORANGE, symbol='diamond')))
    fig.add_hline(y=0, line=dict(color=GRAY, width=1, dash='dash'))
    fig.update_layout(height=380, margin=dict(l=10, r=10, t=40, b=10),
                      yaxis_title='Coefficient (percentage points)',
                      title='Coefficient after dropping each parent CIK in turn')
    st.plotly_chart(fig, width='stretch')

    t = pd.DataFrame({
        'Window': lo['window'].map(wlabel),
        'Full coef (pp)': lo['full_coef'].map(pp),
        'LOCO min (pp)': lo['loco_min'].map(pp),
        'LOCO max (pp)': lo['loco_max'].map(pp),
        'Sign flips': [f'{int(a)} of {int(b)}' for a, b in zip(lo['sign_flips'], lo['of_G'])],
        'Without T-Mobile (pp)': lo['without_TMobile'].map(pp),
        'Without Sprint (pp)': lo['without_Sprint'].map(pp),
        'Largest-move CIK': lo['largest_move_cik'].astype(int),
    })
    st.dataframe(t, hide_index=True, width='stretch')
    source(f'{V4}/f3_loco.csv', f'{V4}/f1_cluster_diagnostics.csv')

    with st.expander('Which clusters carry the CV3 variance (Essay 3 Table 10, top-ten variance shares)'):
        t10 = e3_q4_table('table10')
        t10 = t10[t10['panel'] == 'top-ten variance shares'][
            ['window', 'name', 'final_cik', 'treated_cluster', 'n_events', 'coef_without', 'share', 'sign_flip']].copy()
        t10['final_cik'] = t10['final_cik'].astype('Int64')
        t10['coef_without'] = t10['coef_without'].map(pp)
        t10['share'] = t10['share'].map(pct)
        t10 = t10.rename(columns={'coef_without': 'coef without (pp)', 'share': 'share of CV3 variance'})
        st.dataframe(t10, hide_index=True, width='stretch')
        source(f'{Q4}/table10.csv')


guard(sensitivities)


# ====================================================================== logit AME
def logit():
    st.header('Logit average marginal effects (corroboration only)')
    ame = e3_table('f1_logit_ame').copy()
    t7 = e3_q4_table('table07')
    conv = t7[t7['panel'] == 'logit AME'][['window', 'converged', 'iterations', 'warnings_verbatim']]
    ame = ame.merge(conv, on='window', how='left')
    bad = ame[ame['converged'].astype(str).str.lower() == 'false']
    if len(bad):
        st.info('Non-convergence: the logit did **not converge** for the '
                   + ', '.join(wlabel(w) for w in bad['window'])
                   + ' window (' + '; '.join(bad['warnings_verbatim'].dropna().astype(str).unique())
                   + '). Its AME is reported for corroboration only and carries no inferential weight.')
    st.markdown('The logit is a functional-form check on the linear probability model, not the governing '
                'estimate. Inference for Essay 3 remains CV3 / WCR on the linear probability model.')
    t = pd.DataFrame({
        'Window': ame['window'].map(wlabel),
        'AME (pp)': ame['ame'].map(pp),
        'Cluster SE (pp)': ame['se_cluster'].map(lambda v: f'{v * 100:.2f}'),
        '95% CI (pp)': [f'[{pp(a)}, {pp(b)}]' for a, b in zip(ame['ci_lo'], ame['ci_hi'])],
        'p': ame['p'].map(p3),
        'Converged': ame['converged'],
        'Iterations': ame['iterations'],
    })
    st.dataframe(t, hide_index=True, width='stretch')
    source(f'{V4}/f1_logit_ame.csv', f'{Q4}/table07.csv')


guard(logit)


# ====================================================================== measurement
def measurement():
    st.header('Measurement: the departure classifier')
    st.markdown('Departures are coded from Item 5.02 text by a rule-based classifier and validated '
                'against hand-coded reference sets. Kappa is chance-corrected agreement; precision is '
                'the share of classifier positives that are true; recall is the share of true '
                'departures the classifier finds.')
    t5 = e3_q4_table('table05')
    agree = t5[t5['panel'] == 'agreement']
    rounds = list(dict.fromkeys(agree['round']))
    default = [r for r in rounds if 'v4' in str(r).lower()] or rounds[-1:]
    pick = st.selectbox('Validation round', rounds, index=rounds.index(default[0]))
    sub = agree[agree['round'] == pick]
    cols = [k for k in ['variant', 'sample', 'field', 'scoring', 'n', 'agreement', 'kappa', 'precision',
                        'precision_ci95', 'recall', 'recall_ci95', 'tp', 'fp', 'fn'] if k in sub.columns]
    sub = sub[cols].dropna(axis=1, how='all').copy()
    for k in ['agreement', 'kappa', 'precision', 'recall']:
        if k in sub.columns:
            sub[k] = sub[k].map(p3)
    st.dataframe(sub, hide_index=True, width='stretch')

    st.subheader('Recall by treatment stratum (recall audit)')
    strat = t5[t5['panel'] == 'stratified recall'][
        ['field', 'scoring', 'stratum', 'n', 'kappa', 'precision', 'recall', 'recall_ci95']].copy()
    ex = strat[strat['field'].astype(str).str.startswith('exec departure (A)')]
    if len(ex):
        fig = go.Figure()
        for stratum, g in ex.groupby('stratum', sort=False):
            fig.add_trace(go.Bar(x=g['scoring'], y=g['recall'], name=str(stratum),
                                 marker_color=BLUE if stratum == 'treated' else ORANGE,
                                 text=g['recall'].map(p3), textposition='outside',
                                 hovertext=g['recall_ci95'], hovertemplate='%{x}<br>recall %{y:.3f}'
                                 '<br>95% CI %{hovertext}<extra>' + str(stratum) + '</extra>'))
        fig.update_layout(barmode='group', height=330, margin=dict(l=10, r=10, t=40, b=10),
                          yaxis=dict(title='Recall', range=[0, 1.1]),
                          title='Executive-departure recall, treated vs control strata')
        st.plotly_chart(fig, width='stretch')
    st.dataframe(strat, hide_index=True, width='stretch')
    st.caption('The treated and control recall estimates and their CI endpoints are what the '
               'recall-corrected sensitivity rows (and their bounding exercises) use.')
    source(f'{Q4}/table05.csv')

    st.subheader('CEO and director departures')
    ceo = e3_table('f5_ceo')
    d = e3_table('f6_director')
    m = ceo[['window', 'treated_events', 'control_events', 'treated_n', 'control_n', 'reason']].merge(
        d.rename(columns={'treated_events': 'director_treated', 'control_events': 'director_control'}),
        on='window', how='left')
    m['window'] = m['window'].map(wlabel)
    m = m.rename(columns={'treated_events': 'CEO departures (treated)', 'control_events': 'CEO departures (control)',
                          'treated_n': 'treated events', 'control_n': 'control events',
                          'director_treated': 'director departures (treated)',
                          'director_control': 'director departures (control)',
                          'reason': 'CEO model status'})
    st.dataframe(m, hide_index=True, width='stretch')
    st.caption('CEO departures are too rare to estimate; they are reported as counts only.')
    source(f'{V4}/f5_ceo.csv', f'{V4}/f6_director.csv')


guard(measurement)


# ====================================================================== T-Mobile case
def tmobile():
    st.header('The T-Mobile case')
    st.markdown('T-Mobile is the largest treated parent CIK, so the essay reads its record event by '
                'event: breaches, notifications, departures and governance disclosures on one timeline.')
    tl = e3_table('tmobile_timeline').copy()
    tl['date'] = pd.to_datetime(tl['date'], errors='coerce')
    types = list(tl['type'].value_counts().index)
    default = [t for t in types if any(k in t for k in ('breach occurrence', 'notification', 'departure'))]
    pick = st.multiselect('Event types', types, default=default or types)
    v = tl[tl['type'].isin(pick)]
    palette = ['#2a78d6', '#eb6834', '#1baf7a', '#eda100', '#e87ba4', '#008300', '#4a3aa7', '#e34948']
    fig = go.Figure()
    for i, (t, g) in enumerate(v.groupby('type', sort=False)):
        fig.add_trace(go.Scatter(x=g['date'], y=[t] * len(g), mode='markers', name=t,
                                 marker=dict(size=9, color=palette[i % len(palette)] if i < 8 else GRAY,
                                             line=dict(width=1, color='white')),
                                 customdata=g[['description', 'source']].values,
                                 hovertemplate='%{x|%Y-%m-%d}<br>%{customdata[0]}<br>%{customdata[1]}'
                                               '<extra></extra>'))
    fig.update_layout(height=120 + 40 * max(len(pick), 1), showlegend=False,
                      margin=dict(l=10, r=10, t=30, b=10), yaxis=dict(automargin=True))
    st.plotly_chart(fig, width='stretch')
    with st.expander(f'Timeline table ({len(v)} of {len(tl)} rows shown)'):
        out = v.copy()
        out['date'] = out['date'].dt.strftime('%Y-%m-%d')
        st.dataframe(out, hide_index=True, width='stretch')
    source(f'{V4}/tmobile_timeline.csv')

    st.subheader('Treated T-Mobile events and the departures they code')
    case = e3_table('g6_case_table')
    keep = [k for k in ['breach_date', 'reported_date', 'in_analysis_sample', 'departure', 'is_ceo',
                        'first_disclosure', 'days_from_notification', 'pre_announced', 'flags',
                        'controlled_holder_affiliate', 'excerpt', 'first_accession'] if k in case.columns]
    st.dataframe(case[keep], hide_index=True, width='stretch')
    source(f'{V4}/g6_case_table.csv')

    st.subheader('Departures that appear only under the restatement-dated outcome')
    st.dataframe(e3_table('g6_restatement_dated'), hide_index=True, width='stretch')
    st.caption('These filings feed the restatement-dated (rs) sensitivity row, not the primary outcome.')
    source(f'{V4}/g6_restatement_dated.csv')


guard(tmobile)


# ====================================================================== v3 comparison
def v3_comparison():
    with st.expander('Comparison only: the retired v3 run vs authoritative v4'):
        st.markdown('Essay 3 **v4 is authoritative**. The v3 run (outputs/essay3_q2/) is retired; it '
                    'appears here only so a reader can see that the verdicts did not change.')
        vt = e3_table('239_verdict_table').copy()
        for k in ['coef', 'mde80']:
            vt[k] = vt[k].map(pp if k == 'coef' else (lambda x: f'{x * 100:.2f}'))
        vt = vt.rename(columns={'coef': 'coef (pp)', 'mde80': 'MDE80 (pp)'})
        st.dataframe(vt, hide_index=True, width='stretch')
        source(f'{V4}/239_verdict_table.csv')


guard(v3_comparison)
