"""
Robustness and defense supplement.

Charts and tables from outputs/defense_supplement/: the Essay 2 delay inference ladder, the
Essay 3 randomization inference, the Essay 1 notification-anchored CARs, and the deck exhibits
(long-format file). Every number is read from those committed files at run time.
"""
import re
import sys
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import ui  # noqa: E402
from data import guard, source, supp_constants, supp_table  # noqa: E402
from ui import COLORS, CONTROL, TREATED, fmt_ci, fmt_int, fmt_num, fmt_p, fmt_pct  # noqa: E402

SUPP = 'outputs/defense_supplement'
GOVERN = COLORS['navy']
COMPARE = COLORS['comparison']
MUTED = COLORS['muted']

# ------------------------------------------------------------------ human labels
HYP = {'H1_timing': 'H1 · Immediate disclosure', 'H2_FCC': 'H2 · Form 499 registrant',
       'H3_prior': 'H3 · Prior breaches (1 yr)', 'H4_health': 'H4 · Health breach'}
POOL = {'C1 all parents': 'All parents', 'C3 size-matched parents': 'Size-matched parents'}
WINDOW_LABEL = {'30': '30-day', '90': '90-day', '180': '180-day'}


def ri_window(w) -> str:
    w = str(w)
    return 'Placebo' if w.lower().startswith('placebo') else WINDOW_LABEL.get(w, f'{w}-day')


def pool(v) -> str:
    return POOL.get(str(v), re.sub(r'^C\d+\s+', '', str(v)).capitalize())


def hyp(h) -> str:
    return HYP.get(str(h), str(h))


def group_label(g) -> str:
    g = str(g)
    if g.startswith('treated'):
        return 'Treated (Form 499)'
    if g.startswith('control'):
        return 'Control'
    return 'All events' if g == 'all' else g


def anchor_label(a) -> str:
    return 'Breach date (baseline)' if str(a).startswith('breach') else 'Notification date'


TERM = {'H1_timing': 'H1 · Immediate disclosure', 'H2_FCC': 'H2 · Form 499 registrant',
        'H3_prior': 'H3 · Prior breaches (1 yr)', 'H4_health': 'H4 · Health breach',
        'w30': '30-day window', 'w90': '90-day window', 'w180': '180-day window'}

KEY_LABEL = {
    # E1_caar summaries
    'caar30_minus_caarm1': 'CAAR(+30) − CAAR(−1)', 'car_0_1': 'CAR (0,+1)', 'car_0_5': 'CAR (0,+5)',
    # E2 scaling
    'coef_pct_of_pre_sd': 'Coefficient, % of pooled pre-window volatility',
    'cv3_ci_lo_pct': 'CV3 95% CI lower, % of pooled pre-window volatility',
    'cv3_ci_hi_pct': 'CV3 95% CI upper, % of pooled pre-window volatility',
    'mde_pct_of_pre_sd': 'MDE (80% power), % of pooled pre-window volatility',
    'sesoi_pct_of_pre_sd': 'Smallest effect of interest, % of pooled pre-window volatility',
    'coef_pct_of_control_pre_sd': 'Coefficient, % of control pre-window volatility',
    'coef': 'Coefficient', 'cv3_p': 'CV3 p-value', 'mde80': 'MDE (80% power)',
    'pre_sd_pooled': 'Pooled pre-window daily volatility',
    # E1 dollar
    'tost_bound_pos_at_median_mcap': 'TOST upper bound at median market cap',
    'tost_bound_neg_at_median_mcap': 'TOST lower bound at median market cap',
    'tost_bound_at_treated_median_mcap': 'TOST bound at treated median market cap',
    # E3 MDE (per-window stat)
    'mde80_pp': 'MDE (80% power, CV3), pp', 'extra_departures': 'Extra departures detectable',
    'implied_treated_rate_pct': 'Implied treated departure rate (%)',
    'control_rate_pct': 'Control departure rate (%)', 'implied_rate_ratio': 'Implied rate ratio (×)',
    'departures_at_control_rate': 'Departures expected at control rate',
    'committed_treated_departures': 'Observed treated departures',
    # T-Mobile worked example
    'event_date_day0': 'Day 0 (event date)', 'reported_date': 'Public notification date',
    'car_30d': 'CAR (0,+30)', 'mcap_date': 'Market-cap date', 'mcap_prc': 'Share price',
    'mcap_shrout_thousands': 'Shares outstanding (thousands)', 'mcap': 'Market cap',
    'dollar_car_30d': 'Dollar CAR (0,+30)',
    # CRSP duplicate diagnostic
    'n_duplicate_rows': 'Duplicate top-up rows', 'n_events_affected': 'Events affected',
}
STAT = {'n_covered': 'events covered', 'n_missing': 'events missing', 'median': 'median',
        'mean': 'mean', 'coef': 'coefficient', 'ci95_lo': '95% CI lower', 'ci95_hi': '95% CI upper',
        'ci90_lo': '90% CI lower', 'ci90_hi': '90% CI upper', 'se_hc3': 'SE (HC3)',
        'se_cv3': 'SE (CV3)'}
MC_GROUP = {'all': 'all events', 'treated': 'treated', 'control': 'control'}


def key_label(key: str) -> str:
    """Readable name for a deck_exhibits key."""
    k = str(key)
    if k in KEY_LABEL:
        return KEY_LABEL[k]
    m = re.match(r'^(treated|control)_(.+)$', k)
    if m and m.group(2) in KEY_LABEL:
        return f'{group_label(m.group(1))}: {KEY_LABEL[m.group(2)]}'
    m = re.match(r'^(treated|control)_day([+-]\d+)_(caar|aar)$', k)
    if m:
        return f'{group_label(m.group(1))}: {m.group(3).upper()}, day {int(m.group(2)):+d}'
    m = re.match(r'^ar_day(\d+)_(\d{4}-\d{2}-\d{2})$', k)
    if m:
        return f'Abnormal return, day {int(m.group(1))} ({m.group(2)})'
    m = re.match(r'^cum_day(\d+)$', k)
    if m:
        return f'Cumulative AR, day {int(m.group(1))}'
    m = re.match(r'^w(\d+)_(.+)$', k)
    if m and m.group(2) in KEY_LABEL:
        return f'{m.group(1)}-day: {KEY_LABEL[m.group(2)]}'
    m = re.match(r'^(\d+)_(\d{4}-\d{2}-\d{2})_car_30d_(prefix|committed)$', k)
    if m:
        ver = 'pre-fix' if m.group(3) == 'prefix' else 'fixed'
        return f'PERMNO {m.group(1)} · {m.group(2)}: {ver} 30-day CAR'
    m = re.match(r'^(.+?)_(coef|se_hc3|se_cv3|ci90_lo|ci90_hi)$', k)
    if m and m.group(1) in TERM:
        return f'{TERM[m.group(1)]}: {STAT[m.group(2)]}'
    m = re.match(r'^mcap_(all|treated|control)_(.+)$', k)
    if m:
        return f'Market cap, {MC_GROUP[m.group(1)]}: {STAT.get(m.group(2), m.group(2))}'
    m = re.match(r'^(H\d)_(coef|ci\d\d_lo|ci\d\d_hi)_at_median_mcap$', k)
    if m:
        return f'{m.group(1)} {STAT[m.group(2)]} at median market cap'
    return k.replace('_', ' ').capitalize()


def full_height(df) -> int:
    """Table height that shows every row without an inner scrollbar."""
    return 35 * (len(df) + 1) + 3


def unit_label(u) -> str:
    return '—' if pd.isna(u) else str(u)


# ------------------------------------------------------------------ header
ui.page_header('Robustness & Defense Supplement',
               'Analyses prepared for the defense, beyond the essays\' main tables')
ui.framing_note()
st.markdown('None of these analyses changes a primary verdict; each tests whether a null survives a '
            'different inference procedure, anchor date, or unit of measurement.')


def findings():
    dl = supp_table('e2_delay_ladder')
    d = dl[(dl['outcome'] == 'delay (raw days)') & dl['rung'].astype(str).str.startswith('CV3')].iloc[0]
    ri = supp_table('e3_randomization_inference')
    real = ri[~ri['window'].astype(str).str.lower().str.startswith('placebo')]
    na = supp_table('e1_notification_anchored')
    h2 = na[(na['section'] == 'D2') & (na['anchor'] == 'notification') & (na['hypothesis'] == 'H2_FCC')]
    h2 = h2.iloc[-1]
    ui.key_findings([
        f"**Disclosure delay (Essay 2):** Form 499 events differ by "
        f"{fmt_num(d['coef'], 1, signed=True)} days, CV3 p = **{fmt_p(d['p'])}**; every coding is "
        f"null at every rung of the ladder (smallest p {fmt_p(dl['p'].min())}).",
        f"**Randomization inference (Essay 3):** RI p-values on the CV3 t-statistic range from "
        f"**{fmt_p(real['ri_p_t'].min())} to {fmt_p(real['ri_p_t'].max())}** across the three windows "
        f"and both parent pools.",
        f"**Notification-anchored CARs (Essay 1):** re-anchored on the public notification date, H2 "
        f"over {h2['window']} is {fmt_num(h2['coef'], 2, signed=True)} pp, HC3 p = {fmt_p(h2['p_hc3'])}, "
        f"parent-CIK clustered p = {fmt_p(h2['p_cv1_parentcik'])}.",
    ])


guard(findings)

# ------------------------------------------------------------------ inference ladder (words only)
with st.expander('The inference ladder: HC3, CV1, CV3, wild cluster bootstrap', expanded=False,
                 icon=':material/stairs:'):
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

# ------------------------------------------------------------------ E2 delay ladder
ui.section('Essay 2 · Disclosure delay across the inference ladder')

RUNG = {'HC3': 'HC3', 'CV1 parent CIK': 'CV1 (parent CIK)', 'CV3 jackknife': 'CV3 jackknife',
        'WCR restricted Rademacher': 'WCR (Rademacher)', 'WCU unrestricted Rademacher': 'WCU (unrestricted)',
        'WCR Webb six-point': 'WCR (Webb six-point)'}


def e2_delay():
    df = supp_table('e2_delay_ladder').copy()
    df['Rung'] = df['rung'].map(lambda r: RUNG.get(r, r))
    df['Outcome'] = df['outcome'].map(lambda o: str(o)[:1].upper() + str(o)[1:])
    outcomes = list(dict.fromkeys(df['outcome']))
    first = df.iloc[0]
    st.markdown(f"Does Form 499 status predict a longer gap between breach and public notification? "
                f"Three codings of the delay outcome, each estimated once and re-inferred at every rung. "
                f"N = {fmt_int(first['N'])} events ({fmt_int(first['n_treated_events'])} treated events, "
                f"{fmt_int(first['G1'])} treated parent CIKs of {fmt_int(first['G'])} clusters). "
                f"**Navy = governing rung (CV3)**; grey = comparison rungs.")
    cols = st.columns(len(outcomes))
    for col, oc in zip(cols, outcomes):
        sub = df[(df['outcome'] == oc) & df['ci_lo'].notna()].reset_index(drop=True)
        gov = sub['rung'].astype(str).str.startswith('CV3')
        fig = go.Figure()
        for mask, color, name in ((~gov, COMPARE, 'comparison'), (gov, GOVERN, 'governing')):
            s = sub[mask]
            fig.add_trace(go.Scatter(
                x=s['coef'], y=s['Rung'], mode='markers', marker=dict(color=color, size=10),
                error_x=dict(type='data', symmetric=False, array=s['ci_hi'] - s['coef'],
                             arrayminus=s['coef'] - s['ci_lo'], thickness=2.5, width=0, color=color),
                customdata=s[['ci_lo', 'ci_hi', 'p']].values, name=name, showlegend=False,
                hovertemplate='%{y}<br>coef %{x:.3f}<br>95% CI [%{customdata[0]:.3f}, '
                              '%{customdata[1]:.3f}]<br>p %{customdata[2]:.3f}<extra></extra>'))
        fig.add_vline(x=0, line_color=MUTED, line_width=1)
        fig.update_layout(title=dict(text=oc.capitalize(), x=0, font=dict(size=15)),
                          yaxis=dict(categoryorder='array', categoryarray=list(sub['Rung'])[::-1]),
                          xaxis_title='coefficient (days or log days)', margin=dict(l=10, r=10, t=40, b=10))
        with col:
            ui.chart(fig, height=280)
    st.caption('Bootstrap rungs without an interval (unrestricted and Webb) report a p-value only and '
               'appear in the table.')
    show = df.assign(CI=[fmt_ci(lo, hi) for lo, hi in zip(df['ci_lo'], df['ci_hi'])])
    ui.table(show, columns={'Outcome': 'Outcome', 'Rung': 'Rung', 'coef': 'Coefficient', 'se': 'SE',
                            'CI': '95% CI', 'p': 'p-value', 'mde80_cv3': 'MDE80 (CV3)',
                            'mean_outcome': 'Outcome mean'},
             formats={'p-value': fmt_p}, download='e2_delay_ladder.csv',
             height=full_height(show))
    source(f'{SUPP}/e2_delay_ladder.csv')


guard(e2_delay)

# ------------------------------------------------------------------ E3 randomization inference
ui.section('Essay 3 · Randomization inference')


def e3_ri():
    df = supp_table('e3_randomization_inference').copy()
    df['Window'] = df['window'].map(ri_window)
    df['Pool'] = df['variant'].map(pool)
    r0 = df.iloc[0]
    st.markdown(
        f"Treatment is reassigned at random across parent companies {fmt_int(r0['B'])} times; each draw is "
        f"re-estimated and the observed statistic is ranked against the draws. Two pools of eligible "
        f"parents: all parents, and a size-matched subset. Both the raw coefficient and the CV3 "
        f"t-statistic are ranked. N = {fmt_int(r0['N'])} events ({fmt_int(r0['treated_events_obs'])} "
        f"treated events; {fmt_int(r0['G1'])} treated of {fmt_int(r0['G'])} parent clusters).")
    order = list(dict.fromkeys(df['Window']))
    left, right = st.columns(2, gap='large')
    with left:
        st.markdown('**Randomization p-value on the CV3 t-statistic**')
        fig = go.Figure()
        for pl, color in zip(df['Pool'].unique(), [TREATED, CONTROL]):
            s = df[df['Pool'] == pl]
            fig.add_bar(x=s['Window'], y=s['ri_p_t'], name=pl, marker_color=color,
                        text=[fmt_p(v) for v in s['ri_p_t']], textposition='outside',
                        hovertemplate='%{x}<br>RI p on CV3 t %{y:.3f}<extra>' + pl + '</extra>')
        fig.add_hline(y=0.05, line_dash='dot', line_color=COLORS['red'])
        fig.update_layout(barmode='group', yaxis=dict(range=[0, 1.08], title='RI p-value'),
                          xaxis=dict(type='category', categoryorder='array', categoryarray=order,
                                     title=None),
                          legend=dict(orientation='h', y=1.12, x=0), bargap=0.3, bargroupgap=0.08,
                          margin=dict(l=10, r=10, t=40, b=10))
        ui.chart(fig, height=340)
        st.caption('Dotted line: p = 0.05. Placebo = departures in the 180 days before notification.')
    with right:
        st.markdown('**Treated events assigned per random draw**')
        dist = df.drop_duplicates('Pool')
        fig = go.Figure()
        for (_, r), color in zip(dist.iterrows(), [TREATED, CONTROL]):
            fig.add_trace(go.Box(
                x=[r['Pool']], q1=[r['te_p25']], median=[r['te_median']], q3=[r['te_p75']],
                lowerfence=[r['te_p5']], upperfence=[r['te_p95']], mean=[r['te_mean']],
                name=r['Pool'], marker_color=color, boxpoints=False, showlegend=False))
            fig.add_trace(go.Scatter(
                x=[r['Pool'], r['Pool']], y=[r['te_min'], r['te_max']], mode='markers',
                marker=dict(color=MUTED, size=6), showlegend=False,
                hovertemplate='%{y} treated events (min / max)<extra></extra>'))
        fig.add_hline(y=float(df['treated_events_obs'].iloc[0]), line_dash='dash',
                      line_color=COLORS['red'], annotation_text='observed treated events',
                      annotation_position='top left')
        fig.update_layout(yaxis_title='treated events per draw',
                          xaxis=dict(type='category', categoryorder='array',
                                     categoryarray=list(dist['Pool']), title=None),
                          margin=dict(l=10, r=10, t=40, b=10))
        ui.chart(fig, height=340)
        st.caption('Box: 25th–75th percentile and median; whiskers 5th–95th; dots min and max; '
                   'dashed line the observed count.')
        st.markdown('\n'.join(
            f"- **{r['Pool']}**: {fmt_pct(r['share_draws_te_ge_obs'], 1, scale=100)} of draws assign at "
            f"least as many treated events as observed ({fmt_int(r['treated_events_obs'])})."
            for _, r in dist.iterrows()))
    show = df.assign(coef_pp=100 * df['coef_obs'])
    ui.table(show, columns={'Window': 'Window', 'Pool': 'Parent pool',
                            'n_eligible_parents': 'Eligible parents', 'coef_pp': 'Coefficient (pp)',
                            'cv3_t_obs': 'CV3 t', 'ri_p_coef': 'RI p (coefficient)',
                            'ri_p_t': 'RI p (CV3 t)'},
             formats={'RI p (coefficient)': fmt_p, 'RI p (CV3 t)': fmt_p},
             download='e3_randomization_inference.csv', height=full_height(show))
    st.markdown('Treated events concentrate in a few large parents, so a random draw rarely '
                'reproduces the observed treated-event count; ranking the CV3 t-statistic, not only the '
                'coefficient, accounts for that.')
    source(f'{SUPP}/e3_randomization_inference.csv')


guard(e3_ri)

# ------------------------------------------------------------------ E1 notification anchored
ui.section('Essay 1 · Notification-anchored CARs')


def e1_notif():
    df = supp_table('e1_notification_anchored')
    d2 = df[df['section'] == 'D2'].copy()
    d3 = df[df['section'] == 'D3'].copy()
    st.markdown('Essay 1 anchors its event window on the breach date. Here the same four hypotheses are '
                're-estimated with the window anchored on the public **notification** date, over three '
                'windows; the breach-anchored 30-day row is the committed baseline, for reference. '
                'TOST is the two one-sided equivalence test; MDE80 the minimum detectable effect at '
                '80% power.')
    d2['Anchor'] = d2['anchor'].map(anchor_label)
    d2['Spec'] = d2['anchor'].map(lambda a: 'Breach' if str(a).startswith('breach') else 'Notification') \
        + ' ' + d2['window'].astype(str)
    d2['Hypothesis'] = d2['hypothesis'].map(hyp)
    hyps = list(dict.fromkeys(d2['Hypothesis']))
    specs = list(dict.fromkeys(d2['Spec']))
    fig = make_subplots(rows=1, cols=len(hyps), subplot_titles=hyps, shared_yaxes=True,
                        horizontal_spacing=0.04)
    for i, h in enumerate(hyps, start=1):
        s = d2[d2['Hypothesis'] == h]
        base = s['Spec'].str.startswith('Breach')
        for mask, color in ((base, COMPARE), (~base, GOVERN)):
            t = s[mask]
            fig.add_trace(go.Scatter(
                x=t['coef'], y=t['Spec'], mode='markers', marker=dict(color=color, size=9),
                error_x=dict(type='data', symmetric=False, array=t['ci95_hi'] - t['coef'],
                             arrayminus=t['coef'] - t['ci95_lo'], thickness=1.2, width=0, color=color),
                customdata=t[['ci95_lo', 'ci95_hi', 'ci90_lo', 'ci90_hi', 'p_hc3', 'p_cv1_parentcik']].values,
                hovertemplate='%{y}<br>coef %{x:.3f} pp<br>95% CI [%{customdata[0]:.2f}, %{customdata[1]:.2f}]'
                              '<br>90% CI [%{customdata[2]:.2f}, %{customdata[3]:.2f}]'
                              '<br>HC3 p %{customdata[4]:.3f} · CV1 p %{customdata[5]:.3f}<extra></extra>',
                showlegend=False), row=1, col=i)
            fig.add_trace(go.Scatter(
                x=t['coef'], y=t['Spec'], mode='markers', marker=dict(color=color, size=9),
                error_x=dict(type='data', symmetric=False, array=t['ci90_hi'] - t['coef'],
                             arrayminus=t['coef'] - t['ci90_lo'], thickness=4, width=0, color=color),
                hoverinfo='skip', showlegend=False), row=1, col=i)
        fig.add_vline(x=0, line_color=MUTED, line_width=1, row=1, col=i)
    fig.update_yaxes(categoryorder='array', categoryarray=specs[::-1])
    fig.update_annotations(font_size=13)
    fig.update_layout(margin=dict(l=10, r=10, t=40, b=10))
    ui.chart(fig, height=320)
    st.caption('Coefficients in pp of CAR. Thick bar: 90% CI; thin bar: 95% CI (HC3). Grey = '
               'breach-anchored baseline; navy = notification-anchored.')
    d2['CI95'] = [fmt_ci(lo, hi) for lo, hi in zip(d2['ci95_lo'], d2['ci95_hi'])]
    ui.table(d2, columns={'Anchor': 'Anchor', 'window': 'Window', 'Hypothesis': 'Hypothesis',
                          'coef': 'Coefficient (pp)', 'CI95': '95% CI', 'p_hc3': 'HC3 p',
                          'p_cv1_parentcik': 'Parent-CIK p', 'tost_p_2_10': 'TOST p',
                          'mde80': 'MDE80 (pp)', 'N': 'N', 'n_treated': 'Treated'},
             formats={'HC3 p': fmt_p, 'Parent-CIK p': fmt_p, 'TOST p': fmt_p, 'N': fmt_int,
                      'Treated': fmt_int},
             download='e1_notification_anchored.csv', height=full_height(d2))
    st.markdown('**Descriptive notification-anchored CARs by group (pp)**')
    d3['Group'] = d3['group'].map(group_label)
    ui.table(d3, columns={'window': 'Window', 'Group': 'Group', 'mean': 'Mean CAR (pp)',
                          'median': 'Median CAR (pp)', 'n': 'Events'},
             formats={'Events': fmt_int})
    source(f'{SUPP}/e1_notification_anchored.csv')


guard(e1_notif)

# ------------------------------------------------------------------ deck exhibits
ui.section('Deck exhibits',
           'The figures used in the defense slides, from a single long-format file. Each exhibit '
           'lists the formula and upstream source that produced it.')


def exhibit(d: pd.DataFrame, name: str) -> pd.DataFrame:
    s = d[d['exhibit'] == name].copy()
    if s.empty:
        raise KeyError(f'exhibit {name!r} not found in deck_exhibits.csv')
    return s


def provenance(s: pd.DataFrame):
    with st.expander('Formula and upstream source', icon=':material/functions:'):
        p = s.drop_duplicates(['formula', 'source']).assign(Item=lambda x: x['key'].map(key_label))
        ui.table(p, columns={'Item': 'Item', 'formula': 'Formula', 'source': 'Upstream source',
                             'sample': 'Sample'})


COUNT_UNITS = {'events', 'departures', 'rows'}


def value_text(v, unit) -> str:
    """Counts as integers, everything else to two decimals; dates and text unchanged."""
    try:
        x = float(v)
    except (TypeError, ValueError):
        return '—' if pd.isna(v) else str(v)
    if str(unit) in COUNT_UNITS and x == round(x):
        return fmt_int(x)
    return fmt_num(x, 2)


def kv_table(s: pd.DataFrame, download=None):
    t = s.assign(Item=s['key'].map(key_label), Unit=s['unit'].map(unit_label),
                 Value=[value_text(v, u) for v, u in zip(s['value'], s['unit'])])
    ui.table(t, columns={'Item': 'Item', 'Value': 'Value', 'Unit': 'Unit', 'n': 'n'},
             formats={'n': fmt_int}, download=download)


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
        for grp in series['group'].unique():
            color = TREATED if grp == 'treated' else CONTROL
            g = series[(series['group'] == grp) & (series['stat'] == 'caar')].sort_values('day')
            n = int(g['n'].iloc[0])
            lab = group_label(grp)
            fig.add_trace(go.Scatter(x=g['day'], y=g['value'], mode='lines', name=f'{lab} (n = {n})',
                                     line=dict(color=color, width=2.5),
                                     hovertemplate=f'{lab}<br>day %{{x}}<br>CAAR %{{y:.3f}} pp<extra></extra>'))
        fig.add_vline(x=0, line_color=MUTED, line_dash='dot')
        fig.add_hline(y=0, line_color=MUTED, line_width=1)
        fig.update_layout(xaxis_title='trading day relative to breach date', yaxis_title='CAAR (pp)',
                          hovermode='x unified', legend=dict(orientation='h', y=1.1, x=0),
                          margin=dict(l=10, r=10, t=30, b=10))
        ui.chart(fig, height=380)
        st.caption(f"{s['sample'].iloc[0]}. Cumulative average abnormal return, market-adjusted.")
        st.markdown('**Summary windows**')
        kv_table(s[m['day'].isna()])
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
        c1, c2, c3, c4 = st.columns(4)
        c1.metric('CAR (0,+1)', f"{fmt_num(kv['car_0_1'], 2, signed=True)} {units['car_0_1']}")
        c2.metric('CAR (0,+5)', f"{fmt_num(kv['car_0_5'], 2, signed=True)} {units['car_0_5']}")
        c3.metric('CAR (0,+30)', f"{fmt_num(kv['car_30d'], 2, signed=True)} {units['car_30d']}")
        c4.metric('Dollar CAR (0,+30)',
                  f"{fmt_num(kv['dollar_car_30d'], 2, signed=True)} {units['dollar_car_30d']}",
                  help=f"Market cap {fmt_num(kv['mcap'], 1)} {units['mcap']} on {kv['mcap_date']}")
        fig = go.Figure()
        fig.add_bar(x=ar['day'], y=ar['value'], name='Daily AR', marker_color=CONTROL,
                    customdata=ar['date'],
                    hovertemplate='day %{x} (%{customdata})<br>AR %{y:.3f} pp<extra></extra>')
        fig.add_trace(go.Scatter(x=cum['day'], y=cum['value'], name='Cumulative AR', mode='lines',
                                 line=dict(color=TREATED, width=2.5),
                                 hovertemplate='day %{x}<br>cumulative %{y:.3f} pp<extra></extra>'))
        fig.add_hline(y=0, line_color=MUTED, line_width=1)
        fig.update_layout(xaxis_title='trading day from day 0', yaxis_title='pp',
                          legend=dict(orientation='h', y=1.1, x=0), margin=dict(l=10, r=10, t=30, b=10),
                          bargap=0.3)
        ui.chart(fig, height=380)
        provenance(s)

    # --- dollar
    with tabs[2]:
        s = exhibit(d, 'E1_dollar')
        st.markdown('Essay 1 coefficients converted to dollars at the median market capitalization of the '
                    'regression sample, together with the equivalence (TOST) bound in the same units. '
                    f"Market-capitalization coverage by group is listed first. {s['sample'].iloc[0]}.")
        kv_table(s, download='e1_dollar_translation.csv')
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
            wide.index = [TERM.get(t, t) for t in wide.index]
            fig = go.Figure(go.Scatter(
                x=wide['coef'], y=wide.index, mode='markers', marker=dict(color=GOVERN, size=10),
                error_x=dict(type='data', symmetric=False, array=wide['ci90_hi'] - wide['coef'],
                             arrayminus=wide['coef'] - wide['ci90_lo'], thickness=3, width=0,
                             color=GOVERN),
                hovertemplate='%{y}<br>coef %{x:.3f}<extra></extra>'))
            fig.add_vline(x=0, line_color=MUTED, line_width=1)
            fig.update_layout(yaxis=dict(autorange='reversed'), xaxis_title=s['unit'].iloc[0],
                              margin=dict(l=10, r=10, t=10, b=10))
            ui.chart(fig, height=140 + 40 * len(wide))
            se_col = 'se_hc3' if 'se_hc3' in wide.columns else 'se_cv3'
            t = wide.reset_index().rename(columns={'index': 'term'})
            t['CI90'] = [fmt_ci(lo, hi) for lo, hi in zip(t['ci90_lo'], t['ci90_hi'])]
            ui.table(t, columns={'term': 'Term', 'coef': 'Coefficient',
                                 se_col: 'SE (' + se_col.split('_')[1].upper() + ')', 'CI90': '90% CI'})
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
        wide = wide.reindex([k for k in dict.fromkeys(m['stat']) if k in wide.index])
        wide.columns = [f'{c}-day window' for c in wide.columns]
        wide.index = [KEY_LABEL.get(k, k) for k in wide.index]
        st.markdown(f"The Essay 3 minimum detectable effect (80% power, CV3) restated as a count of "
                    f"executive departures among the treated events: how many extra departures the design "
                    f"could have detected, against the departures actually observed. {s['sample'].iloc[0]}.")
        t = wide.reset_index().rename(columns={'index': 'Quantity'})
        ui.table(t, formats={c: lambda v: fmt_num(v, 1) for c in wide.columns})
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
        c1, c2, _ = st.columns([1, 1, 2])
        c1.metric('Duplicate top-up rows', fmt_int(kv['n_duplicate_rows']))
        c2.metric('Events affected', fmt_int(kv['n_events_affected']))
        m = s['key'].str.extract(r'^(?P<event>\d+_\d{4}-\d{2}-\d{2})_car_30d_(?P<ver>prefix|committed)$')
        ev = pd.concat([s[['value']], m], axis=1).dropna(subset=['event'])
        ev['value'] = pd.to_numeric(ev['value'])
        wide = ev.pivot(index='event', columns='ver', values='value').reset_index()
        wide['label'] = wide['event'].str.replace('_', ' · ', n=1).map(lambda e: f'PERMNO {e}')
        fig = go.Figure()
        fig.add_bar(x=wide['label'], y=wide['prefix'], name='Pre-fix', marker_color=COMPARE)
        fig.add_bar(x=wide['label'], y=wide['committed'], name='Fixed (committed)', marker_color=GOVERN)
        fig.add_hline(y=0, line_color=MUTED, line_width=1)
        fig.update_layout(barmode='group', yaxis_title='30-day CAR (pp)', xaxis=dict(type='category'),
                          legend=dict(orientation='h', y=1.12, x=0), margin=dict(l=10, r=10, t=30, b=10),
                          bargap=0.35, bargroupgap=0.08)
        ui.chart(fig, height=320)
        ui.table(wide, columns={'label': 'Event (PERMNO · date)', 'prefix': 'Pre-fix 30-day CAR (pp)',
                                'committed': 'Fixed 30-day CAR (pp)'})
        provenance(s)

    source(f'{SUPP}/deck_exhibits.csv')


guard(deck)


def consts():
    with st.expander('All defense-supplement constants (constants_defense_supplement.json)',
                     icon=':material/data_object:'):
        st.json(supp_constants(), expanded=1)
        source(f'{SUPP}/constants_defense_supplement.json')


st.divider()
guard(consts)
