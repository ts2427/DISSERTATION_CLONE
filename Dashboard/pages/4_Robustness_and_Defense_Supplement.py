"""
Robustness and defense supplement.

Charts and tables from outputs/defense_supplement/: the Essay 2 delay inference ladder, the
Essay 3 randomization inference, the Essay 1 notification-anchored CARs, and the deck exhibits
(long-format file). Every number is read from those committed files at run time.
"""
import sys
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from data import FRAMING, guard, source, supp_constants, supp_table  # noqa: E402

st.set_page_config(page_title='Robustness and defense supplement', layout='wide')

BLUE = '#2a78d6'
ORANGE = '#eb6834'
AQUA = '#1baf7a'
GRAY = '#8a8984'
SUPP = 'outputs/defense_supplement'

st.title('Robustness and Defense Supplement')
st.info(FRAMING)
st.markdown('Analyses prepared for the defense, beyond the essays\' main tables. None of them changes '
            'a primary verdict; each tests whether a null survives a different inference procedure, '
            'anchor date, or unit of measurement.')


# ------------------------------------------------------------------ inference ladder (words only)
with st.expander('The inference ladder: HC3, CV1, CV3, wild cluster bootstrap', expanded=False):
    st.markdown(
        '- **HC3** corrects for heteroskedasticity but treats every event as independent. Events from '
        'the same parent company are correlated, so HC3 standard errors are too small and its p-values '
        'too low. It is disqualified as the governing procedure for Essays 2 and 3 and is shown only as '
        'a lower bound on uncertainty.\n'
        '- **CV1** clusters on the parent CIK. With few treated clusters of very unequal size it is '
        'still biased downward.\n'
        '- **CV3** (cluster jackknife) re-estimates leaving out one parent at a time. It is conservative '
        'with few treated clusters and is the **governing** procedure for Essays 2 and 3.\n'
        '- **WCR** (restricted wild cluster bootstrap) imposes the null and resamples whole clusters; '
        'it corroborates CV3. The unrestricted variant (WCU) fails in the opposite direction '
        '(over-rejects) and is a robustness row only; Webb six-point weights are a second check.\n\n'
        'Essay 1 reports HC3 with parent-CIK clustered p-values alongside. Reading a ladder: if a '
        'result is null at the least conservative rung, it is null at every rung above it.'
    )

st.divider()

# ------------------------------------------------------------------ E2 delay ladder
st.header('Essay 2 · Disclosure delay across the inference ladder')


def e2_delay():
    df = supp_table('e2_delay_ladder')
    outcomes = list(dict.fromkeys(df['outcome']))
    first = df.iloc[0]
    st.markdown(f"Does Form 499 status predict a longer gap between breach and public notification? "
                f"Three codings of the delay outcome, each estimated once and re-inferred at every rung. "
                f"N = {int(first['N'])} events ({int(first['n_treated_events'])} treated events, "
                f"{int(first['G1'])} treated parent CIKs of {int(first['G'])} clusters).")
    cols = st.columns(len(outcomes))
    for col, oc in zip(cols, outcomes):
        sub = df[df['outcome'] == oc].reset_index(drop=True)
        fig = go.Figure()
        has_ci = sub['ci_lo'].notna()
        fig.add_trace(go.Scatter(
            x=sub.loc[has_ci, 'coef'], y=sub.loc[has_ci, 'rung'], mode='markers',
            marker=dict(color=BLUE, size=9),
            error_x=dict(type='data', symmetric=False,
                         array=sub.loc[has_ci, 'ci_hi'] - sub.loc[has_ci, 'coef'],
                         arrayminus=sub.loc[has_ci, 'coef'] - sub.loc[has_ci, 'ci_lo'],
                         thickness=2, width=0, color=BLUE),
            customdata=sub.loc[has_ci, ['ci_lo', 'ci_hi', 'p']].values,
            hovertemplate='%{y}<br>coef %{x:.3f}<br>95% CI [%{customdata[0]:.3f}, %{customdata[1]:.3f}]'
                          '<br>p %{customdata[2]:.3f}<extra></extra>', showlegend=False))
        fig.add_vline(x=0, line_color=GRAY, line_width=1)
        fig.update_layout(title=oc, height=300, margin=dict(l=10, r=10, t=40, b=10),
                          yaxis=dict(categoryorder='array', categoryarray=list(sub['rung'])[::-1]),
                          xaxis_title='coefficient')
        col.plotly_chart(fig, width='stretch')
    st.caption('Rungs without an interval (unrestricted and Webb bootstraps) report a p-value only.')
    show = df[['outcome', 'rung', 'coef', 'se', 'ci_lo', 'ci_hi', 'p', 'B', 'mde80_cv3',
               'mean_outcome', 'mde80_share_of_mean', 'note']]
    st.dataframe(show, hide_index=True, width='stretch')
    source(f'{SUPP}/e2_delay_ladder.csv')


guard(e2_delay)

st.divider()

# ------------------------------------------------------------------ E3 randomization inference
st.header('Essay 3 · Randomization inference')


def e3_ri():
    df = supp_table('e3_randomization_inference')
    r0 = df.iloc[0]
    st.markdown(
        f"Treatment is reassigned at random across parent companies {int(r0['B']):,} times; each draw is "
        f"re-estimated and the observed statistic is ranked against the draws. Two pools of eligible "
        f"parents: all parents, and a size-matched subset. Both the raw coefficient and the CV3 "
        f"t-statistic are ranked. N = {int(r0['N'])} ({int(r0['treated_events_obs'])} treated events; "
        f"{int(r0['G1'])} treated of {int(r0['G'])} parent clusters).")
    show = df[['outcome', 'window', 'variant', 'n_eligible_parents', 'coef_obs', 'cv3_t_obs',
               'ri_p_coef', 'ri_p_t', 'draw_coef_sd']]
    st.dataframe(show, hide_index=True, width='stretch')

    left, right = st.columns(2)
    with left:
        fig = go.Figure()
        for var, color in zip(df['variant'].unique(), [BLUE, ORANGE]):
            s = df[df['variant'] == var]
            fig.add_bar(x=s['window'].astype(str), y=s['ri_p_t'], name=f'{var}: RI p (CV3 t)',
                        marker_color=color,
                        hovertemplate='%{x}<br>RI p on CV3 t %{y:.3f}<extra></extra>')
        fig.update_layout(barmode='group', height=340, yaxis=dict(range=[0, 1], title='RI p-value'),
                          xaxis_title='window', legend=dict(orientation='h', y=1.12),
                          margin=dict(l=10, r=10, t=40, b=10), bargap=0.35, bargroupgap=0.08)
        st.plotly_chart(fig, width='stretch')
        st.caption('Randomization p-value on the CV3 t-statistic, by window and pool.')
    with right:
        # Distribution of treated events per random draw (one per pool; identical across windows).
        dist = df.drop_duplicates('variant')
        fig = go.Figure()
        for (_, r), color in zip(dist.iterrows(), [BLUE, ORANGE]):
            fig.add_trace(go.Box(
                name=r['variant'], q1=[r['te_p25']], median=[r['te_median']], q3=[r['te_p75']],
                lowerfence=[r['te_p5']], upperfence=[r['te_p95']], mean=[r['te_mean']],
                marker_color=color, orientation='v', boxpoints=False, showlegend=False))
            fig.add_trace(go.Scatter(
                x=[r['variant']], y=[r['te_min']], mode='markers', marker=dict(color=GRAY, size=6),
                showlegend=False, hovertemplate='min %{y}<extra></extra>'))
            fig.add_trace(go.Scatter(
                x=[r['variant']], y=[r['te_max']], mode='markers', marker=dict(color=GRAY, size=6),
                showlegend=False, hovertemplate='max %{y}<extra></extra>'))
        fig.add_hline(y=float(df['treated_events_obs'].iloc[0]), line_dash='dash', line_color=AQUA,
                      annotation_text='observed treated events', annotation_position='top left')
        fig.update_layout(height=340, yaxis_title='treated events per draw',
                          margin=dict(l=10, r=10, t=40, b=10))
        st.plotly_chart(fig, width='stretch')
        st.caption('Box: 25th-75th percentile and median; whiskers 5th-95th; dots min and max; '
                   'dashed line the observed count.')
        for _, r in dist.iterrows():
            st.markdown(f"- **{r['variant']}**: {r['share_draws_te_ge_obs']:.1%} of draws assign at least "
                        f"as many treated events as observed ({int(r['treated_events_obs'])}).")
    st.markdown('Treated events concentrate in a few large parents, so a random draw rarely '
                'reproduces the observed treated-event count; ranking the CV3 t-statistic, not only the '
                'coefficient, accounts for that.')
    source(f'{SUPP}/e3_randomization_inference.csv')


guard(e3_ri)

st.divider()

# ------------------------------------------------------------------ E1 notification anchored
st.header('Essay 1 · Notification-anchored CARs')


def e1_notif():
    df = supp_table('e1_notification_anchored')
    d2 = df[df['section'] == 'D2'].copy()
    d3 = df[df['section'] == 'D3'].copy()
    st.markdown('Essay 1 anchors its event window on the breach date. Here the same four hypotheses are '
                're-estimated with the window anchored on the public **notification** date, over three '
                'windows; the breach-anchored 30-day row is the committed baseline, for reference. '
                'TOST is the two one-sided equivalence test; MDE80 the minimum detectable effect at '
                '80% power.')
    d2['spec'] = d2['anchor'].astype(str).str.split(' ').str[0] + ' ' + d2['window'].astype(str)
    hyps = list(dict.fromkeys(d2['hypothesis']))
    fig = make_subplots(rows=1, cols=len(hyps), subplot_titles=hyps, shared_yaxes=True)
    specs = list(dict.fromkeys(d2['spec']))
    for i, h in enumerate(hyps, start=1):
        s = d2[d2['hypothesis'] == h]
        fig.add_trace(go.Scatter(
            x=s['coef'], y=s['spec'], mode='markers', marker=dict(color=BLUE, size=8),
            error_x=dict(type='data', symmetric=False, array=s['ci95_hi'] - s['coef'],
                         arrayminus=s['coef'] - s['ci95_lo'], thickness=1.5, width=0, color=GRAY),
            customdata=s[['ci95_lo', 'ci95_hi', 'ci90_lo', 'ci90_hi', 'p_hc3', 'p_cv1_parentcik']].values,
            hovertemplate='%{y}<br>coef %{x:.3f} pp<br>95% CI [%{customdata[0]:.2f}, %{customdata[1]:.2f}]'
                          '<br>90% CI [%{customdata[2]:.2f}, %{customdata[3]:.2f}]'
                          '<br>HC3 p %{customdata[4]:.3f} · CV1 p %{customdata[5]:.3f}<extra></extra>',
            showlegend=False), row=1, col=i)
        fig.add_trace(go.Scatter(
            x=s['coef'], y=s['spec'], mode='markers', marker=dict(color=BLUE, size=8),
            error_x=dict(type='data', symmetric=False, array=s['ci90_hi'] - s['coef'],
                         arrayminus=s['coef'] - s['ci90_lo'], thickness=4, width=0, color=BLUE),
            hoverinfo='skip', showlegend=False), row=1, col=i)
        fig.add_vline(x=0, line_color=GRAY, line_width=1, row=1, col=i)
    fig.update_yaxes(categoryorder='array', categoryarray=specs[::-1])
    fig.update_layout(height=340, margin=dict(l=10, r=10, t=40, b=10))
    st.plotly_chart(fig, width='stretch')
    st.caption('Coefficients in pp of CAR. Thick bar: 90% CI; thin bar: 95% CI (HC3).')
    st.dataframe(d2[['anchor', 'window', 'hypothesis', 'coef', 'se_hc3', 'p_hc3', 'ci95_lo', 'ci95_hi',
                     'ci90_lo', 'ci90_hi', 'tost_p_2_10', 'mde80', 'p_cv1_parentcik', 'n_clusters',
                     'N', 'n_treated', 'n_treated_parent_ciks']],
                 hide_index=True, width='stretch')
    st.subheader('Descriptive notification-anchored CARs by group (pp)')
    st.dataframe(d3[['window', 'variable', 'group', 'mean', 'median', 'n']],
                 hide_index=True, width='stretch')
    source(f'{SUPP}/e1_notification_anchored.csv')


guard(e1_notif)

st.divider()

# ------------------------------------------------------------------ deck exhibits
st.header('Deck exhibits')
st.markdown('The figures used in the defense slides, from a single long-format file '
            '(`exhibit, key, value, unit, sample, n, formula, source`). Each exhibit lists the '
            'formula and upstream source that produced it.')


def exhibit(d: pd.DataFrame, name: str) -> pd.DataFrame:
    s = d[d['exhibit'] == name].copy()
    if s.empty:
        raise KeyError(f'exhibit {name!r} not found in deck_exhibits.csv')
    return s


def provenance(s: pd.DataFrame):
    with st.expander('Formula and upstream source'):
        st.dataframe(s[['key', 'formula', 'source', 'sample', 'n']].drop_duplicates(['formula', 'source']),
                     hide_index=True, width='stretch')


def kv_table(s: pd.DataFrame):
    st.dataframe(s[['key', 'value', 'unit', 'n']], hide_index=True, width='stretch')


def deck():
    d = supp_table('deck_exhibits')
    tabs = st.tabs(['CAAR by group', 'T-Mobile worked example', 'Dollar translation', '90% CIs',
                    'Essay 2 scaling', 'Essay 3 MDE as departures', 'CRSP duplicate fix'])

    # --- CAAR
    with tabs[0]:
        s = exhibit(d, 'E1_caar')
        m = s['key'].str.extract(r'^(?P<group>[a-z]+)_day(?P<day>[+-]\d+)_(?P<stat>caar|aar)$')
        series = pd.concat([s, m], axis=1).dropna(subset=['day'])
        series['day'] = series['day'].astype(int)
        series['value'] = pd.to_numeric(series['value'])
        fig = go.Figure()
        for grp, color in zip(series['group'].unique(), [BLUE, ORANGE]):
            g = series[(series['group'] == grp) & (series['stat'] == 'caar')].sort_values('day')
            n = int(g['n'].iloc[0])
            fig.add_trace(go.Scatter(x=g['day'], y=g['value'], mode='lines', name=f'{grp} (n={n})',
                                     line=dict(color=color, width=2),
                                     hovertemplate=f'{grp}<br>day %{{x}}<br>CAAR %{{y:.3f}} pp<extra></extra>'))
        fig.add_vline(x=0, line_color=GRAY, line_dash='dot')
        fig.add_hline(y=0, line_color=GRAY, line_width=1)
        fig.update_layout(height=380, xaxis_title='trading day relative to breach date',
                          yaxis_title='CAAR (pp)', hovermode='x unified',
                          legend=dict(orientation='h', y=1.08), margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig, width='stretch')
        st.caption(f"{s['sample'].iloc[0]}. Cumulative average abnormal return, market-adjusted.")
        summ = s[m['day'].isna()]
        st.markdown('Summary windows:')
        kv_table(summ)
        provenance(s)

    # --- T-Mobile
    with tabs[1]:
        s = exhibit(d, 'E1_tmobile')
        m = s['key'].str.extract(r'^ar_day(?P<day>\d+)_(?P<date>\d{4}-\d{2}-\d{2})$')
        ar = pd.concat([s, m], axis=1).dropna(subset=['day'])
        ar['day'] = ar['day'].astype(int)
        ar['value'] = pd.to_numeric(ar['value'])
        cm = s['key'].str.extract(r'^cum_day(?P<day>\d+)$')
        cum = pd.concat([s, cm], axis=1).dropna(subset=['day'])
        cum['day'] = cum['day'].astype(int)
        cum['value'] = pd.to_numeric(cum['value'])
        kv = dict(zip(s['key'], s['value']))
        units = dict(zip(s['key'], s['unit']))
        st.markdown(f"**{s['sample'].iloc[0]}**: day 0 = {kv['event_date_day0']}, publicly reported "
                    f"{kv['reported_date']}. Daily abnormal returns (bars) and their running sum (line), "
                    f"both in pp of return.")
        fig = go.Figure()
        fig.add_bar(x=ar['day'], y=ar['value'], name='daily AR', marker_color=GRAY,
                    customdata=ar['date'], hovertemplate='day %{x} (%{customdata})<br>AR %{y:.3f} pp<extra></extra>')
        fig.add_trace(go.Scatter(x=cum['day'], y=cum['value'], name='cumulative AR', mode='lines',
                                 line=dict(color=BLUE, width=2),
                                 hovertemplate='day %{x}<br>cumulative %{y:.3f} pp<extra></extra>'))
        fig.add_hline(y=0, line_color=GRAY, line_width=1)
        fig.update_layout(height=380, xaxis_title='trading day from day 0', yaxis_title='pp',
                          legend=dict(orientation='h', y=1.08), margin=dict(l=10, r=10, t=30, b=10),
                          bargap=0.3)
        st.plotly_chart(fig, width='stretch')
        c1, c2, c3, c4 = st.columns(4)
        c1.metric('CAR (0,+1)', f"{float(kv['car_0_1']):+.2f} {units['car_0_1']}")
        c2.metric('CAR (0,+5)', f"{float(kv['car_0_5']):+.2f} {units['car_0_5']}")
        c3.metric('CAR (0,+30)', f"{float(kv['car_30d']):+.2f} {units['car_30d']}")
        c4.metric('Dollar CAR (0,+30)', f"{float(kv['dollar_car_30d']):+.2f} {units['dollar_car_30d']}",
                  help=f"Market cap {float(kv['mcap']):.1f} {units['mcap']} on {kv['mcap_date']}")
        provenance(s)

    # --- dollar
    with tabs[2]:
        s = exhibit(d, 'E1_dollar')
        st.markdown('Essay 1 coefficients converted to dollars at the median market capitalization of the '
                    'regression sample, together with the equivalence (TOST) bound in the same units. '
                    'Market-capitalization coverage by group is listed first.')
        kv_table(s)
        provenance(s)

    # --- 90% CIs
    with tabs[3]:
        for name, label in (('E1_ci90_essay1', 'Essay 1 (HC3)'), ('E1_ci90_essay3', 'Essay 3 (CV3)')):
            s = exhibit(d, name)
            st.markdown(f"**{label}** · {s['sample'].iloc[0]} · unit: {s['unit'].iloc[0]}")
            m = s['key'].str.extract(r'^(?P<term>.+?)_(?P<stat>coef|se_hc3|se_cv3|ci90_lo|ci90_hi)$')
            wide = (pd.concat([s[['value']], m], axis=1)
                    .pivot(index='term', columns='stat', values='value')
                    .reindex(list(dict.fromkeys(m['term']))))
            wide = wide.apply(pd.to_numeric)
            fig = go.Figure(go.Scatter(
                x=wide['coef'], y=wide.index, mode='markers', marker=dict(color=BLUE, size=9),
                error_x=dict(type='data', symmetric=False, array=wide['ci90_hi'] - wide['coef'],
                             arrayminus=wide['coef'] - wide['ci90_lo'], thickness=2, width=0, color=BLUE),
                hovertemplate='%{y}<br>coef %{x:.3f}<extra></extra>'))
            fig.add_vline(x=0, line_color=GRAY, line_width=1)
            fig.update_layout(height=220 + 30 * len(wide), margin=dict(l=10, r=10, t=10, b=10),
                              yaxis=dict(autorange='reversed'), xaxis_title=s['unit'].iloc[0])
            st.plotly_chart(fig, width='stretch')
            st.dataframe(wide.reset_index(), hide_index=True, width='stretch')
            provenance(s)

    # --- E2 scaling
    with tabs[4]:
        s = exhibit(d, 'E2_vol_scaling')
        st.markdown(f"The Essay 2 volatility coefficient restated as a share of typical pre-notification "
                    f"daily volatility, so its size can be judged against the CV3 interval, the minimum "
                    f"detectable effect, and the smallest effect of interest. {s['sample'].iloc[0]}.")
        kv_table(s)
        provenance(s)

    # --- E3 MDE
    with tabs[5]:
        s = exhibit(d, 'E3_mde_departures')
        m = s['key'].str.extract(r'^w(?P<window>\d+)_(?P<stat>.+)$')
        wide = (pd.concat([s[['value']], m], axis=1)
                .pivot(index='stat', columns='window', values='value'))
        wide = wide[sorted(wide.columns, key=int)]
        wide.columns = [f'{c}-day window' for c in wide.columns]
        st.markdown(f"The Essay 3 minimum detectable effect (80% power, CV3) restated as a count of "
                    f"executive departures among the treated events: how many extra departures the design "
                    f"could have detected, against the departures actually observed. {s['sample'].iloc[0]}.")
        st.dataframe(wide.reset_index(), hide_index=True, width='stretch')
        provenance(s)

    # --- dup diagnostic
    with tabs[6]:
        s = exhibit(d, 'E1_dup_diagnostic')
        kv = dict(zip(s['key'], s['value']))
        st.markdown(
            '**The 2026-10-02 CRSP de-duplication fix.** The CRSP top-up extracts were concatenated '
            'onto the main daily-returns file, and some top-up rows repeated a security-date already '
            'present. The pre-fix 30-day CAR summed a fixed count of rows, so a duplicated date entered '
            'the window twice and pushed out a real trading day. The fix drops the repeated rows before '
            'windows are built; the events below are the only ones whose CAR changed. The fix and its '
            're-run are recorded in the Retirement Ledger.')
        c1, c2 = st.columns(2)
        c1.metric('Duplicate top-up rows', f"{int(float(kv['n_duplicate_rows'])):,}")
        c2.metric('Events affected', f"{int(float(kv['n_events_affected']))}")
        m = s['key'].str.extract(r'^(?P<event>\d+_\d{4}-\d{2}-\d{2})_car_30d_(?P<ver>prefix|committed)$')
        ev = pd.concat([s[['value']], m], axis=1).dropna(subset=['event'])
        ev['value'] = pd.to_numeric(ev['value'])
        wide = ev.pivot(index='event', columns='ver', values='value').reset_index()
        wide = wide.rename(columns={'event': 'event (permno_date)', 'prefix': 'pre-fix CAR 30d (pp)',
                                    'committed': 'fixed CAR 30d (pp)'})
        fig = go.Figure()
        fig.add_bar(x=wide.iloc[:, 0], y=wide['pre-fix CAR 30d (pp)'], name='pre-fix', marker_color=GRAY)
        fig.add_bar(x=wide.iloc[:, 0], y=wide['fixed CAR 30d (pp)'], name='fixed (committed)',
                    marker_color=BLUE)
        fig.add_hline(y=0, line_color=GRAY, line_width=1)
        fig.update_layout(barmode='group', height=340, yaxis_title='30-day CAR (pp)',
                          legend=dict(orientation='h', y=1.1), margin=dict(l=10, r=10, t=30, b=10),
                          bargap=0.35, bargroupgap=0.08)
        st.plotly_chart(fig, width='stretch')
        st.dataframe(wide, hide_index=True, width='stretch')
        provenance(s)

    source(f'{SUPP}/deck_exhibits.csv')


guard(deck)

st.divider()


def consts():
    with st.expander('All defense-supplement constants (constants_defense_supplement.json)'):
        st.json(supp_constants())
        source(f'{SUPP}/constants_defense_supplement.json')


guard(consts)
