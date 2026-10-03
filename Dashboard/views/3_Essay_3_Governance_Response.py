"""
Essay 3 - Governance response.

Descriptive, post-2007 cross-sectional comparison of executive departures (Item 5.02 8-K filings,
coded by a rule-based classifier) after breach notification, by FCC Form 499 status.

Every number on this page is read at run time from committed outputs under outputs/essay3_v4/,
outputs/essay3_q4/ and outputs/essay3_appendix/. Nothing is typed in. Essay 3 v4 is the
authoritative vintage; the retired v3 run appears only in one labelled comparison tab.
"""
import sys
import textwrap
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import ui  # noqa: E402
from data import e3_constants, e3_q4_table, e3_table, guard, source  # noqa: E402
from ui import COLORS, CONTROL, TREATED  # noqa: E402

# Convention (not a result): significance level used to label verdicts.
ALPHA = 0.05

V4 = 'outputs/essay3_v4'
Q4 = 'outputs/essay3_q4'

NAVY = COLORS['navy']
MUTED = COLORS['muted']
HC3_LABEL = 'HC3 p (disqualified)'


# ---------------------------------------------------------------- small helpers
def _ok(v):
    return v is not None and not pd.isna(v)


def to_pp(v):
    """Proportion -> percentage points (float), missing stays missing."""
    return v * 100 if _ok(v) else None


def pp_s(v, d=2):
    """Percentage-point string with sign, from a value already in pp."""
    return ui.fmt_num(v, d, signed=True)


def pp_of(v, d=2):
    """Percentage-point string with sign, from a proportion."""
    return ui.fmt_num(to_pp(v), d, signed=True)


def pp_unsigned(v):
    return ui.fmt_num(v, 2)


def ci_pp(lo, hi):
    """CI string in pp from proportion endpoints."""
    return ui.fmt_ci(to_pp(lo), to_pp(hi)) if _ok(lo) and _ok(hi) else '—'


def rate(v):
    return ui.fmt_pct(v, 1, scale=100)


def ratio3(v):
    return ui.fmt_num(v, 3)


def yes_no(v):
    if not _ok(v):
        return '—'
    s = str(v).strip().lower()
    if s in ('true', '1', '1.0', 'y', 'yes'):
        return 'Yes'
    if s in ('false', '0', '0.0', 'n', 'no'):
        return 'No'
    return str(v)


def wlabel(w):
    return f'{int(w)}-day'


def wrap(s, width=34):
    return '<br>'.join(textwrap.wrap(str(s), width)) or str(s)


def group_label(g):
    return {'treated': 'Form 499', 'control': 'Control'}.get(str(g), str(g))


def ci_chart(df, label_col, title, height=380, band=True):
    """Dot + CV3 95% CI per window in percentage points, zero line, optional +/- MDE80 bands."""
    fig = go.Figure()
    x = list(df[label_col])
    if band and 'mde80_cv3' in df.columns:
        for i, m in enumerate(df['mde80_cv3'] * 100):
            fig.add_shape(type='rect', xref='x', yref='y', x0=i - 0.32, x1=i + 0.32, y0=-m, y1=m,
                          fillcolor=COLORS['band'], line=dict(width=0), layer='below')
        fig.add_trace(go.Scatter(x=[None], y=[None], mode='markers', name='± MDE80 (80% power)',
                                 marker=dict(size=14, symbol='square', color='rgba(0, 32, 91, 0.12)')))
    fig.add_trace(go.Scatter(
        x=x, y=df['coef'] * 100, mode='markers', name='Coefficient, CV3 95% CI',
        marker=dict(size=14, color=NAVY),
        error_y=dict(type='data', symmetric=False, thickness=2.5, width=8, color=NAVY,
                     array=(df['ci_cv3_hi'] - df['coef']) * 100,
                     arrayminus=(df['coef'] - df['ci_cv3_lo']) * 100),
        customdata=df[['ci_cv3_lo', 'ci_cv3_hi', 'p_cv3', 'p_wcr']].values * [100, 100, 1, 1],
        hovertemplate=('%{x}<br>coefficient %{y:+.2f} pp<br>CV3 95% CI [%{customdata[0]:.2f}, '
                       '%{customdata[1]:.2f}] pp<br>CV3 p %{customdata[2]:.3f}'
                       '<br>bootstrap (WCR) p %{customdata[3]:.3f}<extra></extra>')))
    fig.add_hline(y=0, line=dict(color=MUTED, width=1, dash='dash'))
    fig.update_layout(title=title, height=height, yaxis_title='Coefficient (percentage points)',
                      xaxis=dict(type='category'), showlegend=True,
                      legend=dict(orientation='h', y=-0.15, x=0))
    return fig


# ====================================================================== header
def header():
    ui.page_header('Essay 3 — Governance response to breach notification',
                   'Is FCC Form 499 status related to whether a breached firm discloses an executive '
                   'departure (Form 8-K Item 5.02) in the 30, 90 and 180 days after the breach is '
                   'publicly notified?')
    ui.framing_note()

    lad = e3_table('f1_ladder')
    pl = e3_table('f4_placebo').iloc[0]
    n_sig = int((lad['p_cv3'] < ALPHA).sum() + (lad['p_wcr'] < ALPHA).sum())
    coefs = '; '.join(f"{wlabel(r['window'])} {pp_of(r['coef'])} pp (CV3 p {ui.fmt_p(r['p_cv3'])})"
                      for _, r in lad.iterrows())
    verdict = ('no window rejects under CV3 or the wild cluster bootstrap' if n_sig == 0
               else 'at least one window rejects under CV3 or the wild cluster bootstrap')
    pl_verdict = 'also null' if pl['p_cv3'] >= ALPHA and pl['p_wcr'] >= ALPHA else 'not null'
    mdes = '; '.join(f"{wlabel(r['window'])} {ui.fmt_num(r['mde80_cv3'] * 100, 1)} pp vs "
                     f"{rate(r['control_mean'])}" for _, r in lad.iterrows())
    ui.key_findings([
        f'**Executive departures after notification** — Form 499 coefficient: {coefs}; {verdict}.',
        f"**Placebo** (departures before notification): {pp_of(pl['coef'])} pp, "
        f"CV3 p {ui.fmt_p(pl['p_cv3'])} — {pl_verdict}.",
        f'**Power caveat** — the minimum detectable effect at 80% power (MDE80) is on the scale of '
        f'the control departure rate ({mdes}), so these nulls rule out only very large differences.',
    ])
    source(f'{V4}/f1_ladder.csv', f'{V4}/f4_placebo.csv')

    with st.expander('What the essay asks and how it is tested'):
        st.markdown(
            'Among breached public firms, is FCC Form 499 status related to the probability that an '
            'executive departure is reported (Item 5.02 of Form 8-K, coded by a rule-based classifier) '
            'in fixed windows after the breach is publicly notified? The model is a linear probability '
            'model, so each coefficient is a difference in the probability of a departure between '
            'Form 499 events and other events, shown **in percentage points (coefficient × 100)**.\n\n'
            'The governing inference is **CV3** (cluster jackknife on parent CIK) together with the '
            '**restricted wild cluster bootstrap (WCR)**. HC3 is shown only for comparison and is '
            '**disqualified**: it ignores the clustering of events within parent firms.')


guard(header)


# ====================================================================== sample
def sample():
    ui.section('Sample', 'From the breach-notification records to the analysis sample of events.')
    c = e3_constants()
    cols = st.columns(5)
    cols[0].metric('Events (N)', ui.fmt_int(c['N']))
    cols[1].metric('Form 499 events', ui.fmt_int(c['treated']))
    cols[2].metric('Control events', ui.fmt_int(c['control']))
    cols[3].metric('Parents (G)', ui.fmt_int(c['parent_ciks']))
    cols[4].metric('Form 499 parents', ui.fmt_int(c['treated_parent_ciks']))
    st.caption(f"Effective number of clusters G* = {c['F1_30_G_star']}; coefficient of variation of "
               f"cluster size = {c['F1_30_cluster_size_cv']}. Outcome classifier: {c['classifier']}.")
    source(f'{V4}/constants_essay3_v4.json')

    led = e3_table('e_ledger')
    labels = [wrap(s, 46) for s in led['step']]
    fig = go.Figure(go.Funnel(y=labels, x=led['N'], textinfo='value', textfont=dict(size=14),
                              marker=dict(color=NAVY), connector=dict(fillcolor=COLORS['grid']),
                              hovertemplate='%{y}<br>N = %{x:,}<extra></extra>'))
    fig.update_layout(title='From notification records to the analysis sample', yaxis=dict(automargin=True))
    ui.chart(fig, height=40 + 62 * len(led))
    st.caption('Rows above the canonical-event step are record-level, where treatment is undefined.')
    with st.expander('Ledger notes (why events leave at each step)'):
        lines = []
        for _, r in led.iterrows():
            extra = ''
            if _ok(r.get('treated')):
                extra = (f" — {ui.fmt_int(r['treated'])} Form 499 / {ui.fmt_int(r['control'])} control; "
                         f"{ui.fmt_int(r['treated_parent_ciks'])} Form 499 parent CIKs")
            note = f": {r['note']}" if _ok(r['note']) else ''
            lines.append(f"- **{r['step']}** (N = {ui.fmt_int(r['N'])}){extra}{note}")
        st.markdown('\n'.join(lines))
    source(f'{V4}/e_ledger.csv')


guard(sample)


# ====================================================================== main result
def main_result():
    ui.section('Main result: executive departure after notification',
               'Form 499 coefficient by window with its CV3 95% confidence interval. The shaded band '
               'is ± the minimum effect detectable with 80% power (MDE80).')
    lad = e3_table('f1_ladder').copy()
    lad['label'] = lad['window'].map(wlabel)
    n_sig = int((lad['p_cv3'] < ALPHA).sum() + (lad['p_wcr'] < ALPHA).sum())
    verdict = ('No window rejects at the conventional level under either CV3 or the bootstrap (WCR).'
               if n_sig == 0 else 'At least one window rejects under CV3 or WCR — see the table.')
    st.markdown(f'**{verdict}**')

    ui.chart(ci_chart(lad, 'label', 'Form 499 coefficient by window (percentage points)'))

    tab = pd.DataFrame({
        'Window': lad['label'],
        'Coefficient (pp)': lad['coef'] * 100,
        'CV3 SE (pp)': lad['se_cv3'] * 100,
        'CV3 95% CI (pp)': [ci_pp(a, b) for a, b in zip(lad['ci_cv3_lo'], lad['ci_cv3_hi'])],
        'CV3 p': lad['p_cv3'],
        'Bootstrap p (WCR)': lad['p_wcr'],
        'MDE80 (pp)': lad['mde80_cv3'] * 100,
    })
    ui.table(tab, formats={'Coefficient (pp)': pp_s, 'CV3 SE (pp)': pp_unsigned, 'CV3 p': ui.fmt_p,
                           'Bootstrap p (WCR)': ui.fmt_p, 'MDE80 (pp)': pp_unsigned},
             download='essay3_main_results.csv')
    rates = pd.DataFrame({
        'Window': lad['label'],
        'Form 499 departure rate': lad['treated_mean'],
        'Control departure rate': lad['control_mean'],
        'MDE80 / control rate': lad['mde80_cv3'] / lad['control_mean'],
        HC3_LABEL: lad['p_hc3'],
    })
    ui.table(rates, formats={'Form 499 departure rate': rate, 'Control departure rate': rate,
                             'MDE80 / control rate': lambda v: ui.fmt_num(v, 2) + '×', HC3_LABEL: ui.fmt_p},
             download='essay3_departure_rates.csv')
    wcr_ci = '; '.join(f"{r['label']} {ci_pp(r['ci_wcr_lo'], r['ci_wcr_hi'])}" for _, r in lad.iterrows())
    st.caption(f"N = {ui.fmt_int(lad['n'].iloc[0])}; G = {ui.fmt_int(lad['G'].iloc[0])} parent CIKs; "
               f"G1 = {ui.fmt_int(lad['G1'].iloc[0])} Form 499 clusters; bootstrap draws B = "
               f"{ui.fmt_int(lad['B_wcr'].iloc[0])}. Bootstrap (WCR) 95% CIs (pp): {wcr_ci}.")

    lines = []
    for _, r in lad.iterrows():
        ratio = r['mde80_cv3'] / r['control_mean']
        lines.append(f"- **{r['label']}**: MDE80 {ui.fmt_num(r['mde80_cv3'] * 100, 2)} pp against a "
                     f"control departure rate of {rate(r['control_mean'])} — {ratio:.2f}× the base rate"
                     + (', larger than the base rate itself.' if ratio > 1 else '.'))
    st.markdown('**What MDE80 implies.** The design can only detect differences on the scale of the '
                'base rate, so a null here rules out very large differences only:\n' + '\n'.join(lines))
    source(f'{V4}/f1_ladder.csv')

    with st.expander('Departure counts and rates by window and group (Essay 3 Table 6)'):
        t6 = e3_q4_table('table06').copy()
        t6['window'] = t6['window'].map(wlabel)
        t6['group'] = t6['group'].map(group_label)
        cols = {'window': 'Window', 'group': 'Group', 'n': 'Events',
                'any_502': 'Any Item 5.02 filing', 'any_502_rate': 'Item 5.02 rate',
                'exec_departure': 'Executive departures', 'exec_rate': 'Executive departure rate',
                'ceo_departure': 'CEO departures', 'ceo_rate': 'CEO departure rate',
                'director_only': 'Director-only departures', 'director_rate': 'Director-only rate'}
        fm = {v: rate for k, v in cols.items() if k.endswith('_rate')}
        fm.update({v: ui.fmt_int for k, v in cols.items()
                   if k in ('n', 'any_502', 'exec_departure', 'ceo_departure', 'director_only')})
        ui.table(t6, columns=cols, formats=fm)
        source(f'{Q4}/table06.csv')


guard(main_result)


# ====================================================================== placebo + BH
def placebo_bh():
    ui.section('Placebo and multiple-testing adjustment',
               'The same model with a pre-notification departure outcome; a non-null here would point '
               'to firm differences unrelated to the breach.')
    pl = e3_table('f4_placebo').iloc[0]
    cols = st.columns(4)
    cols[0].metric('Coefficient (pp)', pp_of(pl['coef']))
    cols[1].metric('CV3 p', ui.fmt_p(pl['p_cv3']))
    cols[2].metric('Bootstrap p (WCR)', ui.fmt_p(pl['p_wcr']))
    cols[3].metric('MDE80 (pp)', ui.fmt_num(pl['mde80_cv3'] * 100, 2))
    st.caption(f"CV3 95% CI (pp): {ci_pp(pl['ci_cv3_lo'], pl['ci_cv3_hi'])}. Form 499 departure rate {rate(pl['treated_mean'])} vs control {rate(pl['control_mean'])}. "
               f"{HC3_LABEL}; comparison only = {ui.fmt_p(pl['p_hc3'])}.")
    source(f'{V4}/f4_placebo.csv')

    st.subheader('Benjamini–Hochberg adjustment within each test family')
    it = e3_table('i_tests')
    fam = it.groupby('family', sort=False).agg(tests=('test', 'size'), min_p=('p', 'min'),
                                               min_wcr=('p_wcr', 'min'), min_bh=('p_bh', 'min'))
    fam['any_bh'] = (fam['min_bh'] < ALPHA).map({True: 'Yes', False: 'No'})
    fam = fam.reset_index()
    ui.table(fam, columns={'family': 'Test family', 'tests': 'Tests', 'min_p': 'Min CV3 p',
                           'min_wcr': 'Min bootstrap p', 'min_bh': 'Min BH-adjusted p',
                           'any_bh': f'BH p < {ALPHA}?'},
             formats={'Tests': ui.fmt_int, 'Min CV3 p': ui.fmt_p,
                      'Min bootstrap p': ui.fmt_p, 'Min BH-adjusted p': ui.fmt_p})
    st.caption('Bootstrap p = restricted wild cluster bootstrap (WCR). BH-adjusted p is the Benjamini–Hochberg adjusted CV3 p-value within the family.')
    with st.expander(f'All {len(it)} tests'):
        ui.table(it, columns={'family': 'Test family', 'test': 'Test', 'p': 'CV3 p',
                              'p_wcr': 'Bootstrap p (WCR)', 'p_bh': 'BH-adjusted p'},
                 formats={'CV3 p': ui.fmt_p, 'Bootstrap p (WCR)': ui.fmt_p, 'BH-adjusted p': ui.fmt_p},
                 download='essay3_all_tests.csv')
    source(f'{V4}/i_tests.csv')


guard(placebo_bh)


# ====================================================================== robustness (tabs)
def sensitivities_tab():
    s = e3_table('f3_sensitivities').copy()
    s['kind'] = s['row_type'].map(lambda v: 'Bounding exercise (not an estimate)'
                                  if 'BOUNDING' in str(v).upper() else 'Estimate')
    windows = sorted(s['window'].unique())
    fig = make_subplots(rows=1, cols=len(windows), shared_yaxes=True, horizontal_spacing=0.03,
                        subplot_titles=[wlabel(w) for w in windows])
    order = [wrap(x, 44) for x in dict.fromkeys(s['sensitivity'])]
    colors = {'Estimate': NAVY, 'Bounding exercise (not an estimate)': COLORS['comparison']}
    for i, w in enumerate(windows, start=1):
        g = s[s['window'] == w]
        for kind, gk in g.groupby('kind', sort=False):
            fig.add_trace(go.Scatter(
                y=[wrap(x, 44) for x in gk['sensitivity']], x=gk['coef'] * 100, mode='markers', name=kind,
                legendgroup=kind, showlegend=(i == 1), marker=dict(size=11, color=colors[kind]),
                error_x=dict(type='data', symmetric=False, thickness=2, width=5, color=colors[kind],
                             array=(gk['ci_cv3_hi'] - gk['coef']) * 100,
                             arrayminus=(gk['coef'] - gk['ci_cv3_lo']) * 100),
                customdata=gk[['p_cv3', 'p_wcr']].values,
                hovertemplate=('%{y}<br>coefficient %{x:+.2f} pp<br>CV3 p %{customdata[0]:.3f}'
                               '<br>bootstrap (WCR) p %{customdata[1]:.3f}<extra></extra>')), row=1, col=i)
        fig.add_vline(x=0, line=dict(color=MUTED, width=1, dash='dash'), row=1, col=i)
        fig.update_xaxes(title_text='pp', row=1, col=i)
    fig.update_yaxes(type='category', categoryorder='array', categoryarray=order[::-1], automargin=True)
    fig.update_layout(title='Sensitivity coefficients with CV3 95% CIs (percentage points)',
                      legend=dict(orientation='h', y=-0.12, x=0), margin=dict(t=70))
    ui.chart(fig, height=620)

    n_bound = int((s['kind'] != 'Estimate').sum())
    hc3_states = s['hc3_status'].dropna().unique()
    it = e3_table('i_tests')
    min_bh = it.loc[it['family'] == 'sensitivities', 'p_bh'].min()
    st.markdown(
        f'- Light rows ({n_bound}) are **bounding exercises**: the outcome is recall-corrected at the '
        'ends of the classifier recall confidence intervals. They show how far measurement error could '
        'move the estimate; they are not estimates.\n'
        '- HC3 status on every sensitivity row: ' + '; '.join(f'*{h}*' for h in hc3_states) + '\n'
        f'- Smallest BH-adjusted p in the sensitivity family: {ui.fmt_p(min_bh)}.')

    t = pd.DataFrame({
        'Window': s['window'].map(wlabel),
        'Sensitivity': s['sensitivity'],
        'Type': s['kind'].map(lambda k: 'Estimate' if k == 'Estimate' else 'Bounding'),
        'Coefficient (pp)': s['coef'] * 100,
        'CV3 95% CI (pp)': [ci_pp(a, b) for a, b in zip(s['ci_cv3_lo'], s['ci_cv3_hi'])],
        'CV3 p': s['p_cv3'],
        'Bootstrap p (WCR)': s['p_wcr'],
        'MDE80 (pp)': s['mde80_cv3'] * 100,
        HC3_LABEL: s['p_hc3'],
    })
    ui.table(t, formats={'Coefficient (pp)': pp_s, 'CV3 p': ui.fmt_p, 'Bootstrap p (WCR)': ui.fmt_p,
                         'MDE80 (pp)': pp_unsigned, HC3_LABEL: ui.fmt_p},
             download='essay3_sensitivities.csv')
    source(f'{V4}/f3_sensitivities.csv', f'{V4}/i_tests.csv')


def loco_tab():
    lo = e3_table('f3_loco').copy()
    diag = e3_table('f1_cluster_diagnostics')
    fig = go.Figure()
    for k, (_, r) in enumerate(lo.iterrows()):
        d = diag[diag['window'] == r['window']]
        fig.add_trace(go.Box(x=[wlabel(r['window'])] * len(d), y=d['coef_without'] * 100,
                             boxpoints='all', jitter=0.45, pointpos=0,
                             marker=dict(size=6, color=CONTROL, opacity=0.75),
                             line=dict(color='rgba(0,0,0,0)'), fillcolor='rgba(0,0,0,0)',
                             name='One parent CIK dropped', showlegend=(k == 0),
                             customdata=d[['deleted_parent_cik', 'cluster_size']].values,
                             hovertemplate=('without CIK %{customdata[0]} (%{customdata[1]} events)'
                                            '<br>coefficient %{y:+.2f} pp<extra></extra>')))
    fig.add_trace(go.Scatter(x=lo['window'].map(wlabel), y=lo['full_coef'] * 100, mode='markers',
                             name='Full sample', marker=dict(size=26, color=NAVY, symbol='line-ew-open',
                                                             line=dict(width=4, color=NAVY))))
    fig.add_trace(go.Scatter(x=lo['window'].map(wlabel), y=lo['without_TMobile'] * 100, mode='markers',
                             name='Without T-Mobile', marker=dict(size=13, color=COLORS['red'],
                                                                  symbol='diamond')))
    fig.add_hline(y=0, line=dict(color=MUTED, width=1, dash='dash'))
    fig.update_layout(yaxis_title='Coefficient (percentage points)', xaxis=dict(type='category'),
                      title='Coefficient after dropping each parent CIK in turn',
                      legend=dict(orientation='h', y=-0.15, x=0))
    ui.chart(fig, height=420)

    t = pd.DataFrame({
        'Window': lo['window'].map(wlabel),
        'Full-sample coefficient (pp)': lo['full_coef'] * 100,
        'LOCO min (pp)': lo['loco_min'] * 100,
        'LOCO max (pp)': lo['loco_max'] * 100,
        'Sign flips': [f'{int(a)} of {int(b)}' for a, b in zip(lo['sign_flips'], lo['of_G'])],
        'Without T-Mobile (pp)': lo['without_TMobile'] * 100,
        'Without Sprint (pp)': lo['without_Sprint'] * 100,
        'Largest-move parent CIK': lo['largest_move_cik'].map(lambda v: str(int(v)) if _ok(v) else None),
    })
    pp_cols = [c for c in t.columns if c.endswith('(pp)')]
    ui.table(t, formats={c: pp_s for c in pp_cols})
    source(f'{V4}/f3_loco.csv', f'{V4}/f1_cluster_diagnostics.csv')

    with st.expander('Which clusters carry the CV3 variance (Essay 3 Table 10, top-ten variance shares)'):
        t10 = e3_q4_table('table10')
        t10 = t10[t10['panel'] == 'top-ten variance shares'].copy()
        t10['window'] = t10['window'].map(wlabel)
        t10['final_cik'] = t10['final_cik'].map(lambda v: str(int(v)) if _ok(v) else None)
        t10['coef_without'] = t10['coef_without'] * 100
        t10['treated_cluster'] = t10['treated_cluster'].map(yes_no)
        t10['sign_flip'] = t10['sign_flip'].map(yes_no)
        ui.table(t10, columns={'window': 'Window', 'name': 'Parent firm', 'final_cik': 'Parent CIK',
                               'treated_cluster': 'Form 499 cluster', 'n_events': 'Events',
                               'coef_without': 'Coefficient without (pp)',
                               'share': 'Share of CV3 variance', 'sign_flip': 'Sign flip'},
                 formats={'Events': ui.fmt_int, 'Coefficient without (pp)': pp_s,
                          'Share of CV3 variance': rate})
        source(f'{Q4}/table10.csv')


def logit_tab():
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
        'Average marginal effect (pp)': ame['ame'] * 100,
        'Cluster SE (pp)': ame['se_cluster'] * 100,
        '95% CI (pp)': [ci_pp(a, b) for a, b in zip(ame['ci_lo'], ame['ci_hi'])],
        'p': ame['p'],
        'Converged': ame['converged'].map(yes_no),
        'Iterations': ame['iterations'],
    })
    ui.table(t, formats={'Average marginal effect (pp)': pp_s, 'Cluster SE (pp)': pp_unsigned,
                         'p': ui.fmt_p, 'Iterations': ui.fmt_int})
    source(f'{V4}/f1_logit_ame.csv', f'{Q4}/table07.csv')


def v3_tab():
    st.markdown('Essay 3 **v4 is authoritative**. The v3 run (outputs/essay3_q2/) is retired; it '
                'appears here only so a reader can see that the verdicts did not change.')
    vt = e3_table('239_verdict_table').copy()
    vt['coef'] = vt['coef'] * 100
    vt['mde80'] = vt['mde80'] * 100
    ui.table(vt, columns={'test': 'Test', 'vintage': 'Run', 'n': 'N', 'coef': 'Coefficient (pp)',
                          'p_cv3': 'CV3 p', 'p_wcr': 'Bootstrap p (WCR)', 'mde80': 'MDE80 (pp)',
                          'verdict': 'Verdict'},
             formats={'N': ui.fmt_int, 'Coefficient (pp)': pp_s, 'CV3 p': ui.fmt_p,
                      'Bootstrap p (WCR)': ui.fmt_p, 'MDE80 (pp)': pp_unsigned})
    source(f'{V4}/239_verdict_table.csv')


def robustness():
    ui.section('Robustness', 'Alternative specifications, influence of single parent firms, a logit '
               'functional-form check, and the retired v3 run for comparison.')
    tabs = st.tabs(['Sensitivities', 'Leave-one-cluster-out', 'Logit AME (corroboration only)',
                    'v3 vs v4 (comparison only)'])
    for tab, fn in zip(tabs, [sensitivities_tab, loco_tab, logit_tab, v3_tab]):
        with tab:
            guard(fn)


guard(robustness)


# ====================================================================== measurement (tabs)
def validation_tab():
    st.markdown('Departures are coded from Item 5.02 text by a rule-based classifier and validated '
                'against hand-coded reference sets. Kappa is chance-corrected agreement; precision is '
                'the share of classifier positives that are true; recall is the share of true '
                'departures the classifier finds.')
    t5 = e3_q4_table('table05')
    agree = t5[t5['panel'] == 'agreement']
    rounds = list(dict.fromkeys(agree['round']))
    default = [r for r in rounds if 'v4' in str(r).lower()] or rounds[-1:]
    pick = st.selectbox('Validation round', rounds, index=rounds.index(default[0]))
    sub = agree[agree['round'] == pick].dropna(axis=1, how='all').copy()
    if 'scoring' not in sub.columns and sub['field'].astype(str).str.contains(' | ', regex=False).all():
        parts = sub['field'].astype(str).str.split(' | ', n=1, regex=False)
        sub['scoring'] = parts.str[0]
        sub['field'] = parts.str[1]
    cols = {'variant': 'Variant', 'sample': 'Sample', 'field': 'Outcome', 'scoring': 'Scoring',
            'n': 'n', 'agreement': 'Agreement', 'kappa': 'Kappa', 'precision': 'Precision',
            'precision_ci95': 'Precision 95% CI', 'recall': 'Recall', 'recall_ci95': 'Recall 95% CI',
            'tp': 'TP', 'fp': 'FP', 'fn': 'FN'}
    order = ['scoring', 'field'] + [k for k in cols if k not in ('scoring', 'field')]
    cols = {k: cols[k] for k in order}
    fm = {k: ratio3 for k in ('Agreement', 'Kappa', 'Precision', 'Recall')}
    fm.update({k: ui.fmt_int for k in ('n', 'TP', 'FP', 'FN')})
    ui.table(sub, columns=cols, formats=fm)
    source(f'{Q4}/table05.csv')


def recall_tab():
    t5 = e3_q4_table('table05')
    strat = t5[t5['panel'] == 'stratified recall'].copy()
    strat['stratum_label'] = strat['stratum'].map(group_label)
    ex = strat[strat['field'].astype(str).str.startswith('exec departure (A)')]
    if len(ex):
        fig = go.Figure()
        for stratum, g in ex.groupby('stratum_label', sort=False):
            fig.add_trace(go.Bar(x=g['scoring'], y=g['recall'], name=str(stratum),
                                 marker_color=TREATED if stratum == 'Form 499' else CONTROL,
                                 text=g['recall'].map(ratio3), textposition='outside',
                                 hovertext=g['recall_ci95'], hovertemplate='%{x}<br>recall %{y:.3f}'
                                 '<br>95% CI %{hovertext}<extra>' + str(stratum) + '</extra>'))
        fig.update_layout(barmode='group', yaxis=dict(title='Recall', range=[0, 1.1]),
                          title='Executive-departure recall, Form 499 vs control strata',
                          legend=dict(orientation='h', y=-0.15, x=0))
        ui.chart(fig, height=380)
    ui.table(strat, columns={'field': 'Outcome', 'scoring': 'Scoring', 'stratum_label': 'Stratum',
                             'n': 'n', 'kappa': 'Kappa', 'precision': 'Precision', 'recall': 'Recall',
                             'recall_ci95': 'Recall 95% CI'},
             formats={'n': ui.fmt_int, 'Kappa': ratio3, 'Precision': ratio3, 'Recall': ratio3})
    st.caption('The Form 499 and control recall estimates and their CI endpoints are what the '
               'recall-corrected sensitivity rows (and their bounding exercises) use.')
    source(f'{Q4}/table05.csv')


def ceo_director_tab():
    ceo = e3_table('f5_ceo')
    d = e3_table('f6_director')
    m = ceo[['window', 'treated_events', 'control_events', 'treated_n', 'control_n', 'reason']].merge(
        d.rename(columns={'treated_events': 'director_treated', 'control_events': 'director_control'}),
        on='window', how='left')
    m['window'] = m['window'].map(wlabel)
    cols = {'window': 'Window', 'treated_n': 'Form 499 events', 'control_n': 'Control events',
            'treated_events': 'CEO departures (Form 499)', 'control_events': 'CEO departures (control)',
            'director_treated': 'Director departures (Form 499)',
            'director_control': 'Director departures (control)'}
    ui.table(m, columns=cols, formats={v: ui.fmt_int for k, v in cols.items() if k != 'window'})
    status = '; '.join(m['reason'].dropna().astype(str).unique())
    st.caption('CEO departures are too rare to estimate; they are reported as counts only. '
               f'CEO model status: {status}.')
    source(f'{V4}/f5_ceo.csv', f'{V4}/f6_director.csv')


def measurement():
    ui.section('Measurement: the departure classifier',
               'How well the rule-based classifier codes departures, and the rarer CEO and director '
               'outcomes.')
    tabs = st.tabs(['Classifier validation', 'Recall by stratum', 'CEO and director departures'])
    for tab, fn in zip(tabs, [validation_tab, recall_tab, ceo_director_tab]):
        with tab:
            guard(fn)


guard(measurement)


# ====================================================================== T-Mobile case
def tmobile():
    ui.section('The T-Mobile case',
               'T-Mobile is the largest Form 499 parent CIK, so the essay reads its record event by '
               'event: breaches, notifications, departures and governance disclosures on one timeline.')
    tl = e3_table('tmobile_timeline').copy()
    tl['date'] = pd.to_datetime(tl['date'], errors='coerce')
    types = list(tl['type'].value_counts().index)
    default = [t for t in types if any(k in t for k in ('breach occurrence', 'notification', 'departure'))]
    pick = st.multiselect('Event types', types, default=default or types)
    v = tl[tl['type'].isin(pick)]
    palette = ui.SEQ
    fig = go.Figure()
    for i, (t, g) in enumerate(v.groupby('type', sort=False)):
        fig.add_trace(go.Scatter(x=g['date'], y=[wrap(t, 40)] * len(g), mode='markers', name=t,
                                 marker=dict(size=13, color=palette[i % len(palette)], opacity=0.85,
                                             line=dict(width=1, color='white')),
                                 customdata=g[['description', 'source']].values,
                                 hovertemplate='%{x|%Y-%m-%d}<br>%{customdata[0]}<br>%{customdata[1]}'
                                               '<extra></extra>'))
    fig.update_layout(showlegend=False, title='T-Mobile timeline',
                      xaxis=dict(type='date', title='Date', tickformat='%Y'),
                      yaxis=dict(type='category', automargin=True))
    ui.chart(fig, height=140 + 56 * max(len(pick), 1))
    with st.expander(f'Timeline table ({len(v)} of {len(tl)} rows shown)'):
        out = v.copy()
        out['date'] = out['date'].dt.strftime('%Y-%m-%d')
        ui.table(out, columns={'date': 'Date', 'type': 'Event type', 'description': 'Description',
                               'source': 'Source'})
    source(f'{V4}/tmobile_timeline.csv')

    st.subheader('Form 499 T-Mobile events and the departures they code')
    case = e3_table('g6_case_table').copy()
    for k in ('in_analysis_sample', 'is_ceo'):
        if k in case.columns:
            case[k] = case[k].map(yes_no)
    ui.table(case, columns={'breach_date': 'Breach', 'reported_date': 'Notified',
                            'in_analysis_sample': 'In sample', 'departure': 'Departure',
                            'is_ceo': 'CEO', 'first_disclosure': 'First filed',
                            'days_from_notification': 'Days after notice',
                            'pre_announced': 'Pre-announced', 'flags': 'Flags'},
             formats={'Days after notice': ui.fmt_int})
    st.caption('Breach = breach date; Notified = public notification date; First filed = first Item 5.02 '
               'filing naming the departure; Days after notice = days from notification to that filing.')
    with st.expander('Filing excerpts and controlled-holder checks'):
        ex = case[case['excerpt'].notna()].copy() if 'excerpt' in case.columns else case.iloc[0:0]
        if 'excerpt' in ex.columns:
            ex['excerpt'] = ex['excerpt'].astype(str).str.replace('�', '’', regex=False)
        for _, r in ex.drop_duplicates(subset=['departure', 'first_accession']).iterrows():
            st.markdown(f"**{r['departure']}** — first disclosure {r['first_disclosure']} "
                        f"(accession {r['first_accession']}); flags: {r['flags'] if _ok(r['flags']) else '—'}  \n"
                        f"> {r['excerpt']}  \n"
                        f"<span style='color:{MUTED};font-size:0.85rem'>"
                        f"{r['controlled_holder_affiliate'] if _ok(r['controlled_holder_affiliate']) else ''}"
                        '</span>', unsafe_allow_html=True)
    source(f'{V4}/g6_case_table.csv')

    st.subheader('Departures that appear only under the restatement-dated outcome')
    ui.table(e3_table('g6_restatement_dated'),
             columns={'breach_date': 'Breach date', 'reported_date': 'Notification date',
                      'filing_date': 'Filing date', 'days_from_notification': 'Days from notification',
                      'accession': 'Accession', 'persons': 'Persons'},
             formats={'Days from notification': ui.fmt_int})
    st.caption('These filings feed the restatement-dated sensitivity row, not the primary outcome.')
    source(f'{V4}/g6_restatement_dated.csv')


guard(tmobile)
