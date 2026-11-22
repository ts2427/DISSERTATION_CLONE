"""
Essay 2 - the information environment around breach notifications.

Every number on this page is read at run time from committed pipeline outputs (Dashboard/data.py
loaders). Text describes results qualitatively and interpolates the loaded values; nothing is typed in.
No event-level returns are listed: the final-sample file is used only for aggregate counts and the
disclosure-delay distribution (a non-licensed variable).
"""
import re
import sys
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import ui  # noqa: E402
from data import (e2_ledger_md, e2_table, guard, read_csv, read_json, read_text,  # noqa: E402
                  source, supp_table)
from ui import COLORS, CONTROL, TREATED, fmt_ci, fmt_int, fmt_num, fmt_p  # noqa: E402

E2 = 'outputs/tables/essay2_v2'
T1 = f'{E2}/t1_final_sample.csv'
LADDER = 'outputs/defense_supplement/e2_delay_ladder.csv'
Q7 = 'outputs/ESSAY2_QUERY7_REPORT.md'
PART_S = 'outputs/ESSAY2_QUERY5_PART_S.md'
CONTRAST_MD = 'outputs/ESSAY2_ANNOUNCEMENT_CONTRAST.md'
V5 = 'outputs/essay2_v5'
V5_FAM = f'{V5}/v5_t09_announcement.csv'            # family of four + BH (scripts/265)
V5_LAD = f'{V5}/v5_t09b_announcement_ladder.csv'    # eight-rung ladder (scripts/265)
SUPERSEDED = 'earlier specification (superseded)'


def v5_announcement():
    """The v5 announcement test (scripts/265): the family of four and the registrant row."""
    fam = read_csv(V5_FAM)
    fam = fam[~fam['test'].astype(str).str.startswith('BRIDGE')].reset_index(drop=True)
    reg = fam[fam['test'].str.startswith('Form 499')].iloc[0]
    return fam, reg
LEDGER_MD = 'outputs/ESSAY2_SAMPLE_ATTRITION_LEDGER.md'


def fix_text(s):
    """Repair UTF-8 text that was double-encoded through cp1252 (e.g. dashes in some notes)."""
    if not isinstance(s, str):
        return s
    out = []
    for line in s.split('\n'):
        try:
            out.append(line.encode('cp1252').decode('utf-8'))
        except (UnicodeEncodeError, UnicodeDecodeError):
            out.append(line)
    return '\n'.join(out)


# ---------------------------------------------------------------- inference-rung vocabulary
def rung_kind(name: str) -> str:
    """'governing' | 'comparison' | 'robustness' | 'hc3' for a rung label from the outputs."""
    n = str(name).lower()
    if 'hc3' in n:
        return 'hc3'
    if 'cv3' in n or 'jackknife' in n:
        return 'governing'
    if 'webb' in n:
        return 'robustness'
    if 'wcr' in n or ('restricted' in n and 'unrestricted' not in n):
        return 'governing'
    return 'comparison'


def rung_name(name: str) -> str:
    """Plain-words name for a rung label from the outputs."""
    n = str(name).lower()
    if 'hc3' in n:
        return 'HC3 (comparison only)'
    if 'cv3' in n or 'jackknife' in n:
        return 'CV3 cluster jackknife (governing)'
    if 'webb' in n:
        return 'Wild cluster bootstrap, Webb weights (robustness)'
    if 'wcu' in n or 'unrestricted' in n:
        return 'Wild cluster bootstrap, unrestricted (comparison)'
    if 'wcr' in n or 'restricted' in n:
        return 'Wild cluster bootstrap, restricted (governing)'
    if 'cv1' in n or 'cluster' in n:
        return 'CV1 clustered on parent CIK (comparison)'
    return str(name)


ROLE = {
    'governing': 'Governing',
    'comparison': 'Comparison',
    'robustness': 'Robustness',
    'hc3': 'Comparison only',
}
KIND_COLOR = {
    'governing': COLORS['navy'],
    'comparison': COLORS['comparison'],
    'robustness': COLORS['comparison'],
    'hc3': COLORS['disqualified'],
}
KIND_LEGEND = {
    'governing': 'Governing rung',
    'comparison': 'Comparison rung',
    'robustness': 'Comparison rung',
    'hc3': 'HC3 (comparison only)',
}


def coef3(v):
    return fmt_num(v, 3, signed=True)


def coef4(v):
    return fmt_num(v, 4, signed=True)


def num3(v):
    return fmt_num(v, 3)


def add_ci(df, lo='ci_lo', hi='ci_hi', d=3, col='ci'):
    df = df.copy()
    df[col] = [fmt_ci(a, b, d) for a, b in zip(df[lo], df[hi])]
    return df


def legend_top():
    return dict(orientation='h', yanchor='bottom', y=1.02, xanchor='left', x=0)


def ladder_chart(df, coef_col, name_col, xlab):
    """Point estimate with CI per rung; zero line; governing rungs navy, HC3 lightest."""
    d = df.dropna(subset=['ci_lo', 'ci_hi']).copy()
    fig = go.Figure()
    shown = set()
    for _, r in d.iterrows():
        kind = rung_kind(r[name_col])
        col = KIND_COLOR[kind]
        leg = KIND_LEGEND[kind]
        label = rung_name(r[name_col])
        p_txt = fmt_p(r['p']) if 'p' in r else '—'
        fig.add_trace(go.Scatter(
            x=[r[coef_col]], y=[label], mode='markers', name=leg, legendgroup=leg,
            showlegend=leg not in shown,
            marker=dict(size=15, color=col, line=dict(color='white', width=1)),
            error_x=dict(type='data', symmetric=False,
                         array=[r['ci_hi'] - r[coef_col]],
                         arrayminus=[r[coef_col] - r['ci_lo']],
                         color=col, thickness=3, width=6),
            hovertemplate=(f"{label}<br>coefficient {coef3(r[coef_col])}<br>"
                           f"95% CI {fmt_ci(r['ci_lo'], r['ci_hi'], 3)}<br>"
                           f"p {p_txt}<extra></extra>")))
        shown.add(leg)
    fig.add_vline(x=0, line_dash='dash', line_color=COLORS['muted'])
    fig.update_layout(xaxis_title=xlab, height=150 + 60 * len(d), legend=legend_top(),
                      margin=dict(l=10, r=20, t=50, b=50),
                      yaxis=dict(autorange='reversed'))
    return fig


def ladder_table(d, name_col, download=None):
    show = add_ci(d)
    show['rung_label'] = show[name_col].map(rung_name)
    show['role'] = show[name_col].map(lambda s: ROLE[rung_kind(s)])
    cols = {'rung_label': 'Inference rung', 'role': 'Role', 'coef': 'Coefficient', 'se': 'SE',
            'ci': '95% CI', 'p': 'p-value'}
    if 'df' in show.columns:
        cols['df'] = 'df'
    if 'B' in show.columns:
        cols['B'] = 'Bootstrap draws (B)'
    ui.table(show, columns=cols,
             formats={'Coefficient': coef3, 'SE': num3, 'p-value': fmt_p, 'df': fmt_int,
                      'Bootstrap draws (B)': fmt_int},
             download=download)


def parse_bh():
    txt = read_text(Q7)
    sec = txt.split('Multiplicity position', 1)[-1] if 'Multiplicity position' in txt else ''
    return re.findall(r'^\s+(.+?): p=([0-9.eE+-]+) vs threshold ([0-9.]+) -> (\w+)', sec, re.M)


# ====================================================================== header
ui.page_header('Essay 2 — Information environment around breach notifications',
               'Is FCC Form 499 registration associated with how long a firm takes to notify the '
               'public of a breach, or with a lasting change in its return volatility afterwards?')
ui.framing_note()


def sec_findings():
    lad = supp_table('e2_delay_ladder')
    raw = lad[lad['outcome'] == lad['outcome'].iloc[0]]
    d_cv3 = raw[raw['rung'].str.contains('CV3')].iloc[0]
    vlad = e2_table('t26_inference_ladder')
    v_cv3 = vlad[vlad['procedure'].str.contains('CV3')].iloc[0]
    dr = e2_table('t28_design_resolution').iloc[0]
    fam5, reg5 = v5_announcement()
    bh_txt = ('survives Benjamini–Hochberg' if str(reg5['bh_reject_05']) == 'True'
              else 'does not survive Benjamini–Hochberg')
    n_fam = len(fam5)
    coding = 'raw-day coding' if 'raw' in str(d_cv3['outcome']) else f'coding: {d_cv3["outcome"]}'

    def verdict(p):
        return 'null' if p >= 0.05 else 'rejects at 5%'

    ui.key_findings([
        f'**Primary 1 — disclosure delay ({verdict(d_cv3["p"])}).** Form 499 events notify '
        f'{fmt_num(d_cv3["coef"], 1, signed=True)} days later on average ({coding}), '
        f'CV3 p = {fmt_p(d_cv3["p"])}; the design detects only effects of about '
        f'{fmt_num(d_cv3["mde80_cv3"], 0)} days or more with 80% power.',
        f'**Primary 2 — post-notification volatility ({verdict(v_cv3["p"])}).** Form 499 coefficient '
        f'{coef3(v_cv3["coef"])} daily pp, CV3 p = {fmt_p(v_cv3["p"])}; MDE at 80% power '
        f'{num3(dr["mde_daily"])} daily pp ({fmt_num(dr["mde_annualized"], 2)} pp annualized)'
        + (' — an underpowered null, not evidence of equivalence.' if not bool(dr['negligible'])
           else '.'),
        f'**Secondary (exploratory, added after the primary nulls) — announcement-window '
        f'elevation.** Form 499 coefficient {coef3(reg5["coef"])} daily pp, CV3 p = '
        f'{fmt_p(reg5["p"])}; {bh_txt} within its {n_fam}-test exploratory family.',
    ])


guard(sec_findings)

st.markdown(
    'The essay asks two descriptive questions about publicly traded firms that notified a data breach '
    'after the CPNI breach rule (47 CFR 64.2011) took effect: **(a)** is FCC Form 499 registration '
    'status associated with how long a firm takes to notify the public, and **(b)** is it associated '
    'with a persistent change in the firm\'s return volatility after notification? '
    'The rule sets a notification clock for law enforcement and an embargo on public disclosure until '
    'that clock runs — a *floor* on how soon a registered carrier may go public, not a ceiling on how '
    'late it may do so. Both primary answers are nulls; an exploratory secondary result on the '
    'announcement window is reported with its full history below.')

# ====================================================================== sample
ui.section('Sample')


def sec_sample():
    d = read_csv(T1)[['final_cik', 'fcc_form499']]
    n = len(d)
    tr = d[d['fcc_form499'] == 1]
    g = d['final_cik'].nunique()
    g1 = tr['final_cik'].nunique()
    c = st.columns(4)
    c[0].metric('Events (N)', fmt_int(n))
    c[1].metric('Form 499 events', fmt_int(len(tr)), help=f'{n - len(tr):,} control events')
    c[2].metric('Treated parent CIKs (G1)', fmt_int(g1))
    c[3].metric('Clusters (parent CIKs, G)', fmt_int(g))
    t16 = e2_table('t16_delay_on_treatment')
    if not ((t16['n'] == n).all() and (t16['G'] == g).all() and (t16['G1'] == g1).all()):
        st.warning('The regression tables report a different N/G/G1 than the final-sample file — '
                   'check the pipeline outputs.')
    st.caption(f'With G1 = {g1} treated clusters, conventional clustered SEs are unreliable; the '
               'governing inference rung throughout is CV3 (cluster jackknife on parent CIK) with the '
               'restricted wild cluster bootstrap. HC3 is shown only for comparison.')
    source(T1 + ' (aggregate counts only)', f'{E2}/t16_delay_on_treatment.csv')
    with st.expander('Sample attrition ledger'):
        st.markdown(fix_text(e2_ledger_md()))
        source(LEDGER_MD)


guard(sec_sample)

# ====================================================================== primary 1: delay
ui.section('Primary result 1 — Disclosure delay')


def sec_delay():
    lad = supp_table('e2_delay_ladder')
    outcomes = list(dict.fromkeys(lad['outcome']))
    first = lad.iloc[0]
    st.markdown(
        f'Disclosure delay (days from breach to public notification) regressed on Form 499 status, '
        f'N = {fmt_int(first["N"])}, {fmt_int(first["n_treated_events"])} treated events, '
        f'G = {fmt_int(first["G"])}, G1 = {fmt_int(first["G1"])}. Three codings of the outcome; every '
        'rung of the inference ladder is shown. Navy = governing rungs.')
    tabs = st.tabs([oc[0].upper() + oc[1:] for oc in outcomes])
    for tab, oc in zip(tabs, outcomes):
        with tab:
            d = lad[lad['outcome'] == oc].copy()
            gov = d[d['rung'].str.contains('CV3')].iloc[0]
            wcr = d[d['rung'].str.contains('WCR restricted')].iloc[0]
            unit = 'days' if 'log' not in oc else 'log(1+days)'
            c = st.columns(4)
            c[0].metric('Form 499 coefficient', fmt_num(gov['coef'], 2, signed=True), help=unit)
            c[1].metric('CV3 p (governing)', fmt_p(gov['p']))
            c[2].metric('Bootstrap p (governing)', fmt_p(wcr['p']))
            c[3].metric('MDE, 80% power', fmt_num(gov['mde80_cv3'], 2),
                        help=f'{gov["mde80_share_of_mean"]:.0%} of the outcome mean '
                             f'({fmt_num(gov["mean_outcome"], 2)}); units as the outcome')
            ui.chart(ladder_chart(d, 'coef', 'rung', f'Form 499 coefficient ({unit}), 95% CI'))
            slug = re.sub(r'[^a-z0-9]+', '_', oc.lower()).strip('_')
            ladder_table(d, 'rung', download=f'essay2_delay_ladder_{slug}.csv')
            notes = [fix_text(x) for x in d['note'].dropna().unique()]
            if notes:
                st.caption('Restricted bootstrap: ' + '; '.join(notes) + '.')
            st.caption(
                f'The smallest effect this design could detect with 80% power on the governing rung is '
                f'{fmt_num(gov["mde80_cv3"], 2)} ({unit}) — {gov["mde80_share_of_mean"]:.0%} of the '
                'sample mean. The null is therefore uninformative about effects smaller than that; it is '
                'reported as an underpowered null, not as evidence of no association.')
    source(LADDER)

    with st.expander('Cross-check: CV1 (parent-clustered) delay regressions from the essay table'):
        t16 = e2_table('t16_delay_on_treatment')
        ui.table(add_ci(t16),
                 columns={'dv': 'Outcome', 'coef': 'Coefficient', 'se': 'SE', 'ci': '95% CI',
                          'p': 'p-value', 'df': 'df', 'n': 'N', 'G': 'Clusters (G)',
                          'G1': 'Treated clusters (G1)'},
                 formats={'Coefficient': coef3, 'SE': num3, 'p-value': fmt_p, 'df': fmt_int})
        st.caption('CV1 is a comparison rung (downward-biased SEs with few treated clusters). The '
                   'coefficients must match the ladder above.')
        mism = []
        for _, r in t16.iterrows():
            m = lad[(lad['outcome'] == r['dv']) & lad['rung'].str.startswith('CV1')]
            if len(m) and abs(m.iloc[0]['coef'] - r['coef']) > 0.01:
                mism.append(r['dv'])
        if mism:
            st.warning('Ladder and t16 coefficients disagree for: ' + ', '.join(mism))
        source(f'{E2}/t16_delay_on_treatment.csv')

    st.subheader('Delay distribution by group')
    d = read_csv(T1)[['fcc_form499', 'disclosure_delay_days']].dropna()
    q = e2_table('t17_delay_distribution')
    cap = float(q['p95'].max())
    fig = go.Figure()
    for grp, val, col in [('Form 499 (treated)', 1, TREATED), ('Control', 0, CONTROL)]:
        x = d.loc[d['fcc_form499'] == val, 'disclosure_delay_days'].clip(upper=cap)
        fig.add_trace(go.Histogram(x=x, name=grp, marker_color=col, opacity=0.7,
                                   histnorm='percent', nbinsx=30))
    fig.update_layout(barmode='overlay', legend=legend_top(),
                      xaxis_title=f'Disclosure delay, days (top-coded at the larger group p95, '
                                  f'{cap:.0f} days, for display)',
                      yaxis_title='% of group', height=400, margin=dict(l=10, r=20, t=50, b=50))
    ui.chart(fig)
    tq = q.set_index('group')
    qd = q.copy()
    qd['group'] = qd['group'].map(lambda s: 'Form 499 (treated)' if s == 'treated'
                                  else 'Control' if s == 'control' else s)
    f0 = lambda v: fmt_num(v, 0)  # noqa: E731
    f1 = lambda v: fmt_num(v, 1)  # noqa: E731
    ui.table(qd, columns={'group': 'Group', 'n': 'Events', 'zeros': 'Same-day', 'p25': 'p25',
                          'p50': 'Median', 'p75': 'p75', 'p90': 'p90', 'p95': 'p95', 'max': 'Max',
                          'mean': 'Mean', 'sd': 'SD'},
             formats={'Events': fmt_int, 'Same-day': fmt_int, 'p25': f0, 'Median': f0, 'p75': f0,
                      'p90': f0, 'p95': f0, 'Max': f0, 'Mean': f1, 'SD': f1})
    st.caption(
        f'Medians are close (treated {tq.loc["treated", "p50"]:.0f} vs control '
        f'{tq.loc["control", "p50"]:.0f} days) and both groups have a mass of same-day notifications '
        f'({tq.loc["treated", "zeros"]:.0f} of {tq.loc["treated", "n"]:.0f} treated, '
        f'{tq.loc["control", "zeros"]:.0f} of {tq.loc["control", "n"]:.0f} control). The treated mean is '
        'pulled up by a long right tail, which is why the winsorized and log codings are reported. '
        'All values in days.')
    source(f'{E2}/t17_delay_distribution.csv', T1 + ' (delay variable only)')


guard(sec_delay)

# ====================================================================== primary 2: volatility
ui.section('Primary result 2 — Post-notification volatility change')

DESC_LABELS = {
    'e2_vol_change': 'Volatility change (post − pre SD, daily pp)',
    'e2_pre_sd': 'Pre-window return SD (daily pp)',
    'e2_post_sd': 'Post-window return SD (daily pp)',
    'disclosure_delay_days': 'Disclosure delay (days)',
    'delay_w': 'Disclosure delay, winsorized p99 (days)',
    'firm_size_log': 'Firm size (log assets)',
    'leverage': 'Leverage',
    'roa': 'Return on assets',
    'health_breach': 'Health-data breach (share)',
    'prior_events': 'Prior breach events',
}


def sec_vol():
    lad = e2_table('t26_inference_ladder')
    lad['bias'] = lad['bias'].map(fix_text)
    coef = lad['coef'].iloc[0]
    gov = lad[lad['procedure'].str.contains('CV3')].iloc[0]
    wcr = lad[lad['procedure'].str.startswith('WCR wild')].iloc[0]
    hc3 = lad[lad['procedure'].str.contains('HC3')].iloc[0]
    c = st.columns(4)
    c[0].metric('Coefficient (daily pp)', coef3(coef))
    c[1].metric('CV3 p (governing)', fmt_p(gov['p']))
    c[2].metric('Bootstrap p (governing)', fmt_p(wcr['p']))
    c[3].metric('HC3 p (comparison only)', fmt_p(hc3['p']))
    st.markdown(
        f'Change in daily return volatility (post-window minus pre-window SD, percentage points) '
        f'regressed on Form 499 status. The estimate is positive ({coef3(coef)}) but every calibrated '
        f'rung includes zero: CV3 95% CI {fmt_ci(gov["ci_lo"], gov["ci_hi"], 3)}. Even the '
        f'disqualified HC3 rung does not reject (p = {fmt_p(hc3["p"])}).')
    ui.chart(ladder_chart(lad, 'coef', 'procedure', 'Form 499 coefficient (daily pp), 95% CI'))
    ladder_table(lad, 'procedure', download='essay2_volatility_ladder.csv')
    st.markdown('**Known behaviour of each rung** (from the output table)\n' + '\n'.join(
        f'- *{rung_name(r["procedure"])}* — {r["bias"]}' for _, r in lad.iterrows()
        if isinstance(r['bias'], str)))
    source(f'{E2}/t26_inference_ladder.csv')

    st.subheader('What the design can and cannot rule out')
    dr = e2_table('t28_design_resolution').iloc[0]
    c = st.columns(4)
    c[0].metric('MDE, daily pp', num3(dr['mde_daily']))
    c[1].metric('MDE, annualized pp', fmt_num(dr['mde_annualized'], 2))
    c[2].metric('SESOI, daily pp', num3(dr['sesoi_daily']))
    c[3].metric('Negligible?', 'Yes' if bool(dr['negligible']) else 'No')
    s = dr['sesoi_daily']
    fig = go.Figure()
    fig.add_shape(type='rect', x0=-s, x1=s, y0=-0.5, y1=0.5, fillcolor=COLORS['band'],
                  line=dict(color=COLORS['navy'], width=1, dash='dot'))
    fig.add_trace(go.Scatter(
        x=[coef], y=['90% CI'], mode='markers', name='Estimate with 90% CI',
        marker=dict(size=15, color=COLORS['navy']),
        error_x=dict(type='data', symmetric=False, array=[dr['ci90_hi'] - coef],
                     arrayminus=[coef - dr['ci90_lo']], color=COLORS['navy'], thickness=4, width=10),
        hovertemplate=(f'estimate {coef3(coef)}<br>90% CI '
                       f'{fmt_ci(dr["ci90_lo"], dr["ci90_hi"], 3)}<extra></extra>')))
    fig.add_trace(go.Scatter(x=[None], y=[None], mode='markers', name=f'± SESOI ({num3(s)})',
                             marker=dict(size=14, symbol='square', color=COLORS['band'],
                                         line=dict(color=COLORS['navy'], width=1))))
    fig.add_vline(x=0, line_dash='dash', line_color=COLORS['muted'])
    fig.update_layout(height=230, xaxis_title='Form 499 coefficient, daily pp',
                      legend=legend_top(), margin=dict(l=10, r=20, t=50, b=50))
    ui.chart(fig)
    st.caption(
        f'The 90% CI {fmt_ci(dr["ci90_lo"], dr["ci90_hi"], 3)} is not contained in the band of effects '
        f'judged too small to matter (± {num3(s)}), so the null cannot be read as equivalence: it is a '
        f'directional, underpowered null. The design detects with 80% power only effects of '
        f'{num3(dr["mde_daily"])} daily pp ({fmt_num(dr["mde_annualized"], 2)} pp annualized) or larger.'
        if not bool(dr['negligible']) else
        f'The 90% CI {fmt_ci(dr["ci90_lo"], dr["ci90_hi"], 3)} lies inside ± {num3(s)}.')
    t28 = add_ci(e2_table('t28_design_resolution'), 'ci90_lo', 'ci90_hi')
    t28['negligible'] = t28['negligible'].map(lambda b: 'Yes' if bool(b) else 'No')
    ui.table(t28, columns={'mde_daily': 'MDE (80% power), daily pp',
                           'mde_annualized': 'MDE (80% power), annualized pp',
                           'sesoi_daily': 'SESOI, daily pp', 'ci': '90% CI',
                           'negligible': 'Negligible?',
                           'tost_car_converted_p': 'TOST p (CAR-converted)',
                           'bloom_factor': 'Bloom factor'},
             formats={'MDE (80% power), daily pp': num3, 'SESOI, daily pp': num3,
                      'TOST p (CAR-converted)': fmt_p, 'Bloom factor': num3})
    source(f'{E2}/t28_design_resolution.csv')

    with st.expander('Descriptive statistics by Form 499 status'):
        t2 = e2_table('t2_descriptives_by_treatment')
        t2['variable'] = t2['variable'].map(lambda v: DESC_LABELS.get(v, v))
        ui.table(t2, columns={'variable': 'Variable', 'mean_treated': 'Mean (Form 499)',
                              'sd_treated': 'SD (Form 499)', 'mean_control': 'Mean (control)',
                              'sd_control': 'SD (control)', 'n_treated': 'N (Form 499)',
                              'n_control': 'N (control)'},
                 formats={c: num3 for c in ('Mean (Form 499)', 'SD (Form 499)', 'Mean (control)',
                                            'SD (control)')} | {'N (Form 499)': fmt_int,
                                                                'N (control)': fmt_int})
        st.caption('Treated events come from markedly larger firms (firm size, log assets), the main '
                   'reason the size-conditioned and size-quartile checks below exist.')
        source(f'{E2}/t2_descriptives_by_treatment.csv')


guard(sec_vol)

# ====================================================================== secondary
ui.section('Secondary result — Announcement-window elevation')


def sec_announce():
    fam, reg = v5_announcement()
    lad = read_csv(V5_LAD)
    old = e2_table('t50_announcement_contrast').query("level == 'L3'").iloc[0]
    v = read_json('outputs/essay2_v5/constants_essay2.json')['values']
    n_full = len(read_csv(T1))
    cv3 = lad[lad['rung'].str.startswith('CV3')].iloc[0]
    wcr = lad[lad['rung'].str.startswith('WCR restricted')].iloc[0]

    st.info(
        f'**History — read before the number.** This test is not one of the essay\'s original '
        f'hypotheses. It was added by the rescoping directive after the primary tests had returned '
        f'nulls. It is exploratory: one of a {len(fam)}-test exploratory family, and the test and its '
        f'first result appear together in commit 115a72f. It is reported as a secondary result, '
        f'estimated on all N = {fmt_int(cv3["N"])} of {fmt_int(n_full)} events (market-adjusted '
        f'returns need no estimation window).', icon=':material/history:')

    c = st.columns(4)
    c[0].metric('Coefficient (daily pp)', coef4(cv3['coef']))
    c[1].metric('CV3 p (governing)', fmt_p(cv3['p']))
    c[2].metric('Bootstrap p (governing)', fmt_p(wcr['p']))
    c[3].metric('N', fmt_int(cv3['N']))
    rungs = lad.assign(label=lad['rung'].map(rung_name),
                       role=lad['rung'].map(lambda r_: ROLE[rung_kind(r_)]))
    ui.table(rungs, columns={'label': 'Inference rung', 'role': 'Role', 'coef': 'Coefficient',
                             'se': 'SE', 'p': 'p-value', 'ci_lo': '95% CI low', 'ci_hi': '95% CI high'},
             formats={'Coefficient': coef4, 'SE': num3, 'p-value': fmt_p, '95% CI low': num3,
                      '95% CI high': num3},
             download='essay2_v5_announcement_ladder.csv')
    st.markdown(
        f'Announcement-window elevation is the SD of market-adjusted returns over trading days '
        f'[−4, +4] around the agency reporting date minus the SD over [−25, −5]. Form 499 events show '
        f'more elevation than other events by {coef3(cv3["coef"])} daily pp after controls '
        f'(CV3 p = {fmt_p(cv3["p"])}; restricted bootstrap p = {fmt_p(wcr["p"])}). The mean elevation is '
        f'{coef3(v["ann_treated_elev"])} for registrant events and {coef3(v["ann_control_elev"])} for '
        'other events, so the differential describes other firms\' notifications as slightly '
        'volatility-damping and registrants\' as roughly neutral.')
    st.caption(
        f'{SUPERSEDED[0].upper() + SUPERSEDED[1:]}: market-model residuals, N = {fmt_int(old["n"])}, '
        f'coefficient {coef3(old["coef"])}, CV3 p = {fmt_p(old["p_cv3"])} (scripts/175, t50). '
        'Replaced by the v5 estimate above.')
    source(V5_LAD, f'{E2}/t50_announcement_contrast.csv')

    st.subheader('Breach notifications vs the same firms\' earnings announcements')
    lab = {'earnings elevation (mean)': 'Earnings elevation', 'breach elevation (mean)': 'Breach elevation',
           'breach minus earnings (contrast)': 'Contrast (breach − earnings)'}
    l1 = fam[fam['test'].isin(list(lab))].copy()
    l1['label'] = l1['test'].map(lab)

    def bar_color(r_):
        if 'contrast' in r_:
            return COLORS['red']
        return TREATED if 'earn' in r_ else CONTROL

    fig = go.Figure(go.Bar(
        x=l1['label'], y=l1['coef'], marker_color=[bar_color(r_) for r_ in l1['test']],
        error_y=dict(type='data', array=1.96 * l1['se'], color=COLORS['text'], thickness=1.5),
        hovertemplate='%{x}<br>%{y:+.3f}<extra></extra>'))
    fig.add_hline(y=0, line_color=COLORS['muted'])
    fig.update_layout(yaxis_title='daily pp (bars = ± 1.96 SE)', height=380, showlegend=False,
                      margin=dict(l=10, r=20, t=30, b=50))
    ui.chart(fig)
    ui.table(l1, columns={'label': 'Quantity', 'coef': 'Coefficient', 'se': 'SE', 'N': 'N'},
             formats={'Coefficient': coef3, 'SE': num3, 'N': fmt_int})
    e = l1[l1['test'].str.startswith('earnings')].iloc[0]
    b = l1[l1['test'].str.startswith('breach elevation')].iloc[0]
    st.caption(
        f'The same instrument that registers earnings announcements ({coef3(e["coef"])}, '
        f'N = {fmt_int(e["N"])}) registers essentially nothing at breach notifications '
        f'({coef3(b["coef"])}, N = {fmt_int(b["N"])}). This is the design-validation result: the '
        'persistent-window null is not an artifact of an insensitive measure.')
    source(V5_FAM)

    st.subheader('Multiplicity — Benjamini–Hochberg within the exploratory family')
    bh = fam.assign(test=fam['test'].map(lambda t_: t_[0].upper() + t_[1:]),
                    decision=fam['bh_reject_05'].map(lambda x: 'Reject' if str(x) == 'True' else 'Fail to reject'))
    ui.table(bh, columns={'test': 'Test', 'p': 'p-value', 'bh_adj_p': 'BH-adjusted p', 'inference': 'SE',
                          'decision': 'Decision (FDR 5%)'},
             formats={'p-value': fmt_p, 'BH-adjusted p': fmt_p})
    st.caption(
        f'The Form 499 test is evaluated at its CV3 p-value and '
        f'{"survives" if str(reg["bh_reject_05"]) == "True" else "does not survive"} BH within its '
        f'{len(fam)}-test exploratory family (BH-adjusted p = {fmt_p(reg["bh_adj_p"])}). Program-wide, '
        f'the v5 analysis enumerates {fmt_int(v["program_tests_total"])} tests. This is the only Form 499 '
        'coefficient in the essay that survives calibrated inference; it is one rejection among many '
        'tests and is reported as such.')
    source(V5_FAM, 'outputs/essay2_v5/constants_essay2.json')
    with st.expander(f'Full announcement-contrast report — {SUPERSEDED}'):
        st.caption('Defense-era report (scripts/175): its numbers are the superseded market-model '
                   'specification, and its "pre-specified" wording predates the exploratory label.')
        st.text(fix_text(read_text(CONTRAST_MD)))
        source(CONTRAST_MD)


guard(sec_announce)

# ====================================================================== robustness
ui.section('Robustness',
           'Each check re-estimates the volatility result. Unless the table says otherwise, the '
           'p-values in these tables are from conventional SEs, not the governing CV3 rung.')


def rob_s1():
    t = e2_table('t37_s1_s2_main')
    t['spec'] = t['spec'].map(fix_text)
    fig = go.Figure()
    for _, r in t.iterrows():
        fig.add_trace(go.Scatter(
            x=[r['coef']], y=[r['spec']], mode='markers', showlegend=False,
            marker=dict(size=14, color=COLORS['navy']),
            error_x=dict(type='data', symmetric=False, array=[r['ci_hi'] - r['coef']],
                         arrayminus=[r['coef'] - r['ci_lo']], color=COLORS['navy'], thickness=3,
                         width=6),
            hovertemplate=(f"{r['spec']}<br>coefficient {coef3(r['coef'])}<br>95% CI "
                           f"{fmt_ci(r['ci_lo'], r['ci_hi'], 3)}<extra></extra>")))
    fig.add_vline(x=0, line_dash='dash', line_color=COLORS['muted'])
    fig.update_layout(xaxis_title='Form 499 coefficient (daily pp), 95% CI', height=150 + 55 * len(t),
                      yaxis=dict(autorange='reversed'), margin=dict(l=10, r=20, t=30, b=50))
    ui.chart(fig)
    ui.table(add_ci(t), columns={'spec': 'Specification', 'coef': 'Coefficient', 'se': 'SE',
                                 'ci': '95% CI', 'n': 'N', 'n_treated': 'Treated events'},
             formats={'Coefficient': coef3, 'SE': num3, 'N': fmt_int, 'Treated events': fmt_int})
    n_cross = int(((t['ci_lo'] < 0) & (t['ci_hi'] > 0)).sum())
    st.caption(f'{n_cross} of {len(t)} specifications have a 95% CI that includes zero.')
    source(f'{E2}/t37_s1_s2_main.csv')


def rob_placebo():
    t = e2_table('t41_placebo').rename(columns={'Unnamed: 0': 'statistic'})
    names = {'count': 'Reassignments', 'mean': 'Mean', 'std': 'Standard deviation', 'min': 'Minimum',
             '25%': '25th percentile', '50%': 'Median', '75%': '75th percentile', 'max': 'Maximum'}
    t['value'] = [fmt_int(v) if s == 'count' else fmt_num(v, 3) for s, v in
                  zip(t['statistic'], t['placebo_t'])]
    t['label'] = t['statistic'].map(lambda s: names.get(s, s))
    sd = t.loc[t['statistic'] == 'std', 'placebo_t'].iloc[0]
    line = next((l.strip() for l in read_text(PART_S).splitlines()
                 if 'PLACEBO-TREATMENT' in l), None)
    c1, c2 = st.columns([1, 2])
    with c1:
        ui.table(t, columns={'label': 'Placebo CV1 t-statistic', 'value': 'Value'})
    with c2:
        st.markdown(
            f'Distribution of CV1 t-statistics when treatment is randomly reassigned at the parent '
            f'level. Under well-calibrated SEs the spread would be about 1; it is {fmt_num(sd, 2)}, so '
            'CV1 SEs are too small — this is a diagnostic of the inference procedure (and the reason '
            'CV3 governs), not a p-value for the treatment effect.')
        if line:
            st.markdown('From the report:')
            st.markdown(f'> {fix_text(line)}')
    source(f'{E2}/t41_placebo.csv', PART_S)


def rob_se():
    t = e2_table('t4_se_specifications')
    t['role'] = t['label'].map(
        lambda s: 'Comparison only'
        if s in ('classical OLS', 'HC1', 'HC3') else ROLE[rung_kind(s)])
    t['label'] = t['label'].map(lambda s: s[0].upper() + s[1:])
    ui.table(t, columns={'label': 'SE specification', 'role': 'Role', 'coef': 'Coefficient',
                         'se': 'SE', 'df': 'df', 'p': 'p-value', 'n': 'N',
                         'clusters': 'Clusters'},
             formats={'Coefficient': coef3, 'SE': num3, 'df': fmt_int,
                      'p-value': fmt_p, 'N': fmt_int, 'Clusters': fmt_int})
    st.caption('None of these rejects at the 5% level. Heteroskedasticity-only SEs (classical, HC1, '
               'HC3) ignore within-parent correlation and are shown for '
               'comparison; they understate uncertainty when events cluster within parents.')
    source(f'{E2}/t4_se_specifications.csv')


def rob_fe():
    t = e2_table('t8_fixed_effects')
    t['reading'] = t['p'].map(lambda p: 'HC3 only — not a CV3 finding' if p < 0.05
                              else 'Not significant')
    t['label'] = t['label'].map(lambda s: s[0].upper() + s[1:])
    ui.table(t, columns={'label': 'Fixed effects', 'coef': 'Coefficient', 'se': 'HC3 SE',
                         'p': 'HC3 p-value', 'n': 'N', 'r2': 'R²', 'reading': 'Reading'},
             formats={'Coefficient': coef3, 'HC3 SE': num3, 'HC3 p-value': fmt_p, 'N': fmt_int,
                      'R²': num3})
    st.caption('Fixed-effect variants are estimated with HC3 SEs (the disqualified rung). A row '
               'significant only on HC3 is not a finding; with year and industry FE together the '
               'coefficient is not significant.')
    source(f'{E2}/t8_fixed_effects.csv')


def rob_size():
    t = e2_table('t5_size_quartiles')
    t['reading'] = t['p'].map(lambda p: 'HC3 only — not a CV3 finding' if p < 0.05 else
                              'Not significant')
    t['label'] = t['label'].map(lambda s: s[0].upper() + s[1:])
    fig = go.Figure(go.Bar(
        x=t['label'], y=t['coef'], marker_color=COLORS['comparison'],
        error_y=dict(type='data', array=1.96 * t['se'], color=COLORS['text'], thickness=1.5),
        hovertemplate='%{x}<br>%{y:+.3f}<extra></extra>'))
    fig.add_hline(y=0, line_color=COLORS['muted'])
    fig.update_layout(yaxis_title='Form 499 coefficient (daily pp), ± 1.96 HC3 SE', height=360,
                      showlegend=False, margin=dict(l=10, r=20, t=30, b=50))
    ui.chart(fig)
    ui.table(t, columns={'label': 'Size quartile', 'coef': 'Coefficient', 'se': 'HC3 SE',
                         'p': 'HC3 p-value', 'n_treated': 'Treated events',
                         'treated_parent_ciks': 'Treated parents', 'mde80': 'MDE (80% power)',
                         'reading': 'Reading'},
             formats={'Coefficient': coef3, 'HC3 SE': num3, 'HC3 p-value': fmt_p, 'N': fmt_int,
                      'Treated events': fmt_int, 'Treated parents': fmt_int,
                      'MDE (80% power)': num3})
    few = t['treated_parent_ciks'] < 5
    st.caption(
        f'{int(few.sum())} of {len(t)} quartiles have fewer than five treated parent CIKs and cannot be '
        'interpreted on their own. Quartile p-values are HC3 only; signs flip across quartiles, and no '
        'quartile result is a finding on the governing rung (there is no cluster-robust quartile '
        'estimate).')
    source(f'{E2}/t5_size_quartiles.csv')


def rob_clusters():
    t = e2_table('t25_cluster_diagnostics')
    lad = e2_table('t26_inference_ladder')
    full = lad['coef'].iloc[0]
    fig = go.Figure(go.Scatter(
        x=t['size'], y=t['jackknife_coef'], mode='markers', showlegend=False,
        marker=dict(size=8 + 60 * t['partial_leverage_share'], color=COLORS['navy'], opacity=0.6,
                    line=dict(color='white', width=1)),
        hovertemplate='events %{x}<br>coefficient without this parent %{y:+.3f}<extra></extra>'))
    fig.add_hline(y=full, line_dash='dot', line_color=COLORS['navy'],
                  annotation_text=f'full sample {coef3(full)}', annotation_position='top right')
    fig.add_hline(y=0, line_color=COLORS['muted'])
    fig.update_layout(xaxis_title='Events in the parent cluster',
                      yaxis_title='Coefficient with this parent deleted', height=400,
                      margin=dict(l=10, r=20, t=30, b=50))
    ui.chart(fig)
    st.caption(
        f'{len(t)} parent clusters; leave-one-out coefficients range from '
        f'{coef3(t["jackknife_coef"].min())} to {coef3(t["jackknife_coef"].max())}, '
        f'{int((t["jackknife_coef"] < 0).sum())} with a negative sign. The largest cluster holds '
        f'{int(t["size"].max())} events. Point size = partial-leverage share.')
    tt = t.copy()
    tt['cluster'] = tt['cluster'].astype(str)
    ui.table(tt, columns={'cluster': 'Parent CIK', 'size': 'Events', 'leverage': 'Leverage',
                          'partial_leverage_share': 'Partial-leverage share',
                          'jackknife_coef': 'Coefficient without this parent'},
             formats={'Events': fmt_int, 'Leverage': lambda v: fmt_num(v, 4),
                      'Partial-leverage share': lambda v: fmt_num(v, 4),
                      'Coefficient without this parent': coef3},
             height=320)
    source(f'{E2}/t25_cluster_diagnostics.csv', f'{E2}/t26_inference_ladder.csv')


ROB = [('S1 specifications', rob_s1), ('Placebo reassignment', rob_placebo),
       ('SE specifications', rob_se), ('Fixed effects', rob_fe), ('Size quartiles', rob_size),
       ('Cluster diagnostics', rob_clusters)]
for tab, (_, fn) in zip(st.tabs([n for n, _ in ROB]), ROB):
    with tab:
        guard(fn)
