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
from data import (FRAMING, e2_ledger_md, e2_table, guard, read_csv, read_text,  # noqa: E402
                  source, supp_table)

st.set_page_config(page_title='Essay 2 - Information environment', layout='wide')

E2 = 'outputs/tables/essay2_v2'
T1 = f'{E2}/t1_final_sample.csv'
LADDER = 'outputs/defense_supplement/e2_delay_ladder.csv'
Q7 = 'outputs/ESSAY2_QUERY7_REPORT.md'
PART_S = 'outputs/ESSAY2_QUERY5_PART_S.md'
CONTRAST_MD = 'outputs/ESSAY2_ANNOUNCEMENT_CONTRAST.md'
LEDGER_MD = 'outputs/ESSAY2_SAMPLE_ATTRITION_LEDGER.md'

C_TREAT = '#2a6fdb'
C_CTRL = '#9aa5b1'
C_GOV = '#1b7f5a'
C_CMP = '#b0b7c0'
C_BAD = '#c0504d'


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


def rung_role(name: str) -> str:
    n = name.lower()
    if 'hc3' in n:
        return 'comparison only - disqualified (ignores within-parent correlation)'
    if 'cv3' in n or 'jackknife' in n:
        return 'GOVERNING (cluster jackknife on parent CIK)'
    if 'webb' in n:
        return 'robustness (wild bootstrap, alternative weights)'
    if 'wcr' in n or ('restricted' in n and 'unrestricted' not in n):
        return 'GOVERNING (restricted wild cluster bootstrap)'
    if 'wcu' in n or 'unrestricted' in n:
        return 'comparison - over-rejects with few treated clusters'
    if 'cv1' in n or 'cluster' in n:
        return 'comparison - downward-biased SE with few treated clusters'
    return 'comparison'


def is_governing(name: str) -> bool:
    return rung_role(name).startswith('GOVERNING')


def fmt(x, d=3):
    return '-' if pd.isna(x) else f'{x:+.{d}f}'


def fp(x):
    return '-' if pd.isna(x) else f'{x:.3f}'


def ladder_chart(df, coef_col, name_col, title, xlab):
    """Point estimate with CI per rung; zero line; governing rungs coloured."""
    d = df.dropna(subset=['ci_lo', 'ci_hi']).copy()
    fig = go.Figure()
    for _, r in d.iterrows():
        gov = is_governing(r[name_col])
        fig.add_trace(go.Scatter(
            x=[r[coef_col]], y=[r[name_col]], mode='markers',
            marker=dict(size=11, color=C_GOV if gov else C_CMP),
            error_x=dict(type='data', symmetric=False,
                         array=[r['ci_hi'] - r[coef_col]],
                         arrayminus=[r[coef_col] - r['ci_lo']],
                         color=C_GOV if gov else C_CMP, thickness=2),
            showlegend=False,
            hovertemplate=(f"{r[name_col]}<br>coef {r[coef_col]:+.3f}<br>"
                           f"95% CI [{r['ci_lo']:+.3f}, {r['ci_hi']:+.3f}]<br>"
                           f"p {fp(r['p'])}<extra></extra>")))
    fig.add_vline(x=0, line_dash='dash', line_color='#555')
    fig.update_layout(title=title, xaxis_title=xlab, height=110 + 55 * len(d),
                      margin=dict(l=10, r=10, t=50, b=40),
                      yaxis=dict(autorange='reversed'))
    return fig


# ====================================================================== header
st.title('Essay 2 - The information environment around breach notifications')
st.info(FRAMING)
st.markdown(
    'The essay asks two descriptive questions about publicly traded firms that notified a data breach '
    'after the CPNI breach rule (47 CFR 64.2011) took effect: **(a)** is FCC Form 499 registration '
    'status associated with how long a firm takes to notify the public, and **(b)** is it associated '
    'with a persistent change in the firm\'s return volatility after notification? '
    'The rule sets a notification clock for law enforcement and an embargo on public disclosure until '
    'that clock runs - a *floor* on how soon a registered carrier may go public, not a ceiling on how '
    'late it may do so. Both primary answers are nulls; a pre-specified secondary result on the '
    'announcement window is reported with its full history below.')

# ====================================================================== sample
st.header('Sample')


def sec_sample():
    d = read_csv(T1)[['final_cik', 'fcc_form499']]
    n = len(d)
    tr = d[d['fcc_form499'] == 1]
    g = d['final_cik'].nunique()
    g1 = tr['final_cik'].nunique()
    c = st.columns(4)
    c[0].metric('Events (N)', f'{n:,}')
    c[1].metric('Form 499 events', f'{len(tr):,}', help=f'{n - len(tr):,} control events')
    c[2].metric('Treated parent CIKs (G1)', f'{g1}')
    c[3].metric('Clusters (parent CIKs, G)', f'{g}')
    t16 = e2_table('t16_delay_on_treatment')
    if not ((t16['n'] == n).all() and (t16['G'] == g).all() and (t16['G1'] == g1).all()):
        st.warning('The regression tables report a different N/G/G1 than the final-sample file - '
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
st.header('Primary result 1 - Disclosure delay')


def sec_delay():
    lad = supp_table('e2_delay_ladder')
    outcomes = list(dict.fromkeys(lad['outcome']))
    first = lad.iloc[0]
    st.markdown(
        f'Disclosure delay (days from breach to public notification) regressed on Form 499 status, '
        f'N = {int(first["N"])}, {int(first["n_treated_events"])} '
        f'treated events, G = {int(first["G"])}, G1 = {int(first["G1"])}. Three codings of the outcome; '
        'every rung of the inference ladder is shown. Green = governing rungs.')
    tabs = st.tabs(outcomes)
    for tab, oc in zip(tabs, outcomes):
        with tab:
            d = lad[lad['outcome'] == oc].copy()
            gov = d[d['rung'].str.contains('CV3')].iloc[0]
            wcr = d[d['rung'].str.contains('WCR restricted')].iloc[0]
            c = st.columns(4)
            c[0].metric('Form 499 coefficient', fmt(gov['coef'], 2))
            c[1].metric('CV3 p (governing)', fp(gov['p']))
            c[2].metric('WCR p (governing)', fp(wcr['p']))
            c[3].metric('MDE at 80% power (CV3)', f'{gov["mde80_cv3"]:.2f}',
                        help=f'{gov["mde80_share_of_mean"]:.0%} of the outcome mean '
                             f'({gov["mean_outcome"]:.2f}); units as the outcome')
            unit = 'days' if 'log' not in oc else 'log(1+days)'
            st.plotly_chart(ladder_chart(d, 'coef', 'rung', f'{oc}: coefficient by inference rung',
                                         f'Form 499 coefficient ({unit}), 95% CI'),
                            width='stretch')
            show = d[['rung', 'coef', 'se', 'ci_lo', 'ci_hi', 'p', 'df', 'B', 'note']].copy()
            show.insert(1, 'role', show['rung'].map(rung_role))
            st.dataframe(show, hide_index=True, width='stretch')
            st.caption(
                f'The smallest effect this design could detect with 80% power on the governing rung is '
                f'{gov["mde80_cv3"]:.2f} ({unit}) - {gov["mde80_share_of_mean"]:.0%} of the sample mean. '
                'The null is therefore uninformative about effects smaller than that; it is reported as '
                'an underpowered null, not as evidence of no association.')
    source(LADDER)

    with st.expander('Cross-check: CV1 (parent-clustered) delay regressions from the essay table'):
        t16 = e2_table('t16_delay_on_treatment')
        st.dataframe(t16, hide_index=True, width='stretch')
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
    for grp, val, col in [('treated', 1, C_TREAT), ('control', 0, C_CTRL)]:
        x = d.loc[d['fcc_form499'] == val, 'disclosure_delay_days'].clip(upper=cap)
        fig.add_trace(go.Histogram(x=x, name=f'{grp} (Form 499 = {val})', marker_color=col,
                                   opacity=0.65, histnorm='percent', nbinsx=30))
    fig.update_layout(barmode='overlay', xaxis_title=f'Disclosure delay, days (top-coded at the '
                      f'larger group p95, {cap:.0f} days, for display)',
                      yaxis_title='% of group', height=380, margin=dict(l=10, r=10, t=30, b=40))
    st.plotly_chart(fig, width='stretch')
    tq = q.set_index('group')
    st.dataframe(q, hide_index=True, width='stretch')
    st.caption(
        f'Medians are close (treated {tq.loc["treated", "p50"]:.0f} vs control '
        f'{tq.loc["control", "p50"]:.0f} days) and both groups have a mass of same-day notifications '
        f'({tq.loc["treated", "zeros"]:.0f} of {tq.loc["treated", "n"]:.0f} treated, '
        f'{tq.loc["control", "zeros"]:.0f} of {tq.loc["control", "n"]:.0f} control). The treated mean is '
        'pulled up by a long right tail, which is why the winsorized and log codings are reported.')
    source(f'{E2}/t17_delay_distribution.csv', T1 + ' (delay variable only)')


guard(sec_delay)

# ====================================================================== primary 2: volatility
st.header('Primary result 2 - Post-notification volatility change')


def sec_vol():
    lad = e2_table('t26_inference_ladder')
    coef = lad['coef'].iloc[0]
    gov = lad[lad['procedure'].str.contains('CV3')].iloc[0]
    wcr = lad[lad['procedure'].str.startswith('WCR wild')].iloc[0]
    hc3 = lad[lad['procedure'].str.contains('HC3')].iloc[0]
    c = st.columns(4)
    c[0].metric('Form 499 coefficient (daily pp)', fmt(coef))
    c[1].metric('CV3 p (governing)', fp(gov['p']))
    c[2].metric('WCR p (governing)', fp(wcr['p']))
    c[3].metric('HC3 p (disqualified)', fp(hc3['p']))
    st.markdown(
        f'Change in daily return volatility (post-window minus pre-window SD, percentage points) '
        f'regressed on Form 499 status. The estimate is positive ({coef:+.3f}) but every calibrated '
        f'rung includes zero: CV3 95% CI [{gov["ci_lo"]:+.3f}, {gov["ci_hi"]:+.3f}]. Even the '
        f'disqualified HC3 rung does not reject (p = {hc3["p"]:.3f}).')
    st.plotly_chart(ladder_chart(lad, 'coef', 'procedure', 'Volatility change: coefficient by rung',
                                 'Form 499 coefficient (daily pp), 95% CI'), width='stretch')
    show = lad.copy()
    show.insert(2, 'role', show['procedure'].map(rung_role))
    show['bias'] = show['bias'].map(fix_text)
    st.dataframe(show, hide_index=True, width='stretch')
    source(f'{E2}/t26_inference_ladder.csv')

    st.subheader('What the design can and cannot rule out')
    dr = e2_table('t28_design_resolution').iloc[0]
    c = st.columns(4)
    c[0].metric('MDE, daily pp', f'{dr["mde_daily"]:.3f}')
    c[1].metric('MDE, annualized pp', f'{dr["mde_annualized"]:.2f}')
    c[2].metric('SESOI, daily pp', f'{dr["sesoi_daily"]:.3f}')
    c[3].metric('Negligible?', 'yes' if bool(dr['negligible']) else 'no')
    fig = go.Figure()
    s = dr['sesoi_daily']
    fig.add_shape(type='rect', x0=-s, x1=s, y0=-0.5, y1=0.5, fillcolor='rgba(27,127,90,0.15)',
                  line_width=0)
    fig.add_trace(go.Scatter(
        x=[(dr['ci90_lo'] + dr['ci90_hi']) / 2], y=['90% CI'], mode='markers',
        marker=dict(size=1, color=C_TREAT), showlegend=False,
        error_x=dict(type='data', symmetric=False,
                     array=[dr['ci90_hi'] - (dr['ci90_lo'] + dr['ci90_hi']) / 2],
                     arrayminus=[(dr['ci90_lo'] + dr['ci90_hi']) / 2 - dr['ci90_lo']],
                     color=C_TREAT, thickness=4, width=12)))
    fig.add_vline(x=0, line_dash='dash', line_color='#555')
    fig.update_layout(height=200, xaxis_title='daily pp (shaded band = +/- SESOI)',
                      margin=dict(l=10, r=10, t=20, b=40))
    st.plotly_chart(fig, width='stretch')
    st.caption(
        f'The 90% CI [{dr["ci90_lo"]:+.3f}, {dr["ci90_hi"]:+.3f}] is not contained in the band of '
        f'effects judged too small to matter (+/- {s:.3f}), so the null cannot be read as equivalence: '
        f'it is a directional, underpowered null. The design detects with 80% power only effects of '
        f'{dr["mde_daily"]:.3f} daily pp ({dr["mde_annualized"]:.2f} pp annualized) or larger.'
        if not bool(dr['negligible']) else
        f'The 90% CI [{dr["ci90_lo"]:+.3f}, {dr["ci90_hi"]:+.3f}] lies inside +/- {s:.3f}.')
    st.dataframe(e2_table('t28_design_resolution'), hide_index=True, width='stretch')
    source(f'{E2}/t28_design_resolution.csv')

    with st.expander('Descriptive statistics by Form 499 status'):
        st.dataframe(e2_table('t2_descriptives_by_treatment'), hide_index=True,
                     width='stretch')
        st.caption('Treated events come from markedly larger firms (firm_size_log), the main reason the '
                   'size-conditioned and size-quartile checks below exist.')
        source(f'{E2}/t2_descriptives_by_treatment.csv')


guard(sec_vol)

# ====================================================================== secondary
st.header('Secondary result - Announcement-window elevation')


def sec_announce():
    t50 = e2_table('t50_announcement_contrast')
    t53 = e2_table('t53_test_ledger')
    n_full = len(read_csv(T1))
    l3 = t50[t50['level'] == 'L3'].iloc[0]
    l1 = t50[t50['level'] == 'L1'].copy()
    fam_mask = t53['family'].str.contains('announcement window', case=False, na=False)
    fam_label = t53.loc[fam_mask, 'family'].iloc[0]
    n_fam = int(fam_mask.sum())
    n_l3 = int(l3['n'])

    st.info(
        f'**History - read before the number.** This test is not one of the essay\'s original '
        f'hypotheses. It was added by the rescoping directive after the primary tests had returned '
        f'nulls, and was pre-specified as one of a {n_fam}-test family (ledger label '
        f'"{fam_label}") before it was estimated. It is reported as a secondary result. It is estimated '
        f'on N = {n_l3}, not {n_full}: {n_full - n_l3} IPO-recent control events lack the history '
        'needed to estimate the abnormal-volatility beta.')

    c = st.columns(4)
    c[0].metric('Form 499 on elevation (daily pp)', fmt(l3['coef'], 4))
    c[1].metric('CV3 p (governing)', fp(l3['p_cv3']))
    c[2].metric('WCR p (governing)', fp(l3['p_wcr']))
    c[3].metric('N', f'{n_l3}')
    rungs = pd.DataFrame([
        {'rung': 'CV1 parent CIK', 'role': rung_role('CV1'), 'se': l3['se'], 'p': l3['p_cv1']},
        {'rung': 'CV3 jackknife', 'role': rung_role('CV3'), 'se': l3['se_cv3'], 'p': l3['p_cv3']},
        {'rung': f'WCR restricted wild cluster bootstrap (B = {int(l3["B_wcr"]):,})',
         'role': rung_role('WCR restricted'), 'se': None, 'p': l3['p_wcr']},
    ])
    rungs.insert(1, 'coef', l3['coef'])
    st.dataframe(rungs, hide_index=True, width='stretch')
    st.markdown(
        f'Announcement-window elevation is abnormal volatility in the notification window relative to a '
        f'pre-event baseline. Form 499 events show more elevation than control events by '
        f'{l3["coef"]:+.3f} daily pp, and the difference holds on the governing rungs '
        f'(CV3 p = {l3["p_cv3"]:.4f}; WCR p = {l3["p_wcr"]:.4f}). Read with the level-1 rows below: '
        'breach notifications as a whole carry little announcement-window information compared with '
        'the same firms\' earnings announcements, so the differential describes controls\' '
        'notifications as slightly volatility-damping and treated notifications as roughly neutral.')
    source(f'{E2}/t50_announcement_contrast.csv')

    st.subheader('Level 1 - breach notifications vs the same firms\' earnings announcements')
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=l1['row'], y=l1['coef'],
        marker_color=[C_TREAT if 'earn' in r and 'contrast' not in r else
                      (C_BAD if 'contrast' in r else C_CTRL) for r in l1['row']],
        error_y=dict(type='data', array=1.96 * l1['se']),
        hovertemplate='%{x}<br>%{y:+.3f}<extra></extra>'))
    fig.add_hline(y=0, line_color='#555')
    fig.update_layout(yaxis_title='daily pp (bars = +/- 1.96 SE)', height=360,
                      margin=dict(l=10, r=10, t=20, b=40))
    st.plotly_chart(fig, width='stretch')
    st.dataframe(l1[['row', 'coef', 'se', 'n']], hide_index=True, width='stretch')
    e = l1[l1['row'] == 'earnings elevation'].iloc[0]
    b = l1[l1['row'] == 'breach elevation'].iloc[0]
    st.caption(
        f'The same instrument that registers earnings announcements ({e["coef"]:+.3f}, '
        f'N = {int(e["n"]):,}) registers essentially nothing at breach notifications '
        f'({b["coef"]:+.3f}, N = {int(b["n"])}). This is the design-validation result: the persistent-'
        'window null is not an artifact of an insensitive measure.')
    source(f'{E2}/t50_announcement_contrast.csv')

    st.subheader('Multiplicity - Benjamini-Hochberg within the pre-specified family')
    txt = read_text(Q7)
    sec = txt.split('Multiplicity position', 1)[-1] if 'Multiplicity position' in txt else ''
    rows = re.findall(r'^\s+(.+?): p=([0-9.eE+-]+) vs threshold ([0-9.]+) -> (\w+)', sec, re.M)
    if rows:
        bh = pd.DataFrame(rows, columns=['test', 'p', 'BH threshold (FDR 5%)', 'decision'])
        st.dataframe(bh, hide_index=True, width='stretch')
        tr = [r for r in rows if 'treatment' in r[0]]
        if tr:
            st.caption(f'The Form 499 test ({tr[0][0]}) is evaluated at its CV3 p-value and '
                       f'{"survives" if tr[0][3] == "reject" else "does not survive"} BH within its '
                       f'{len(rows)}-test family.')
    else:
        st.warning(f'Could not parse the BH lines from {Q7}.')
    fam = t53.loc[fam_mask, ['script', 'family', 'test']]
    st.dataframe(fam, hide_index=True, width='stretch')
    st.caption(
        f'Program-wide context: the test ledger enumerates {len(t53)} tests across '
        f'{t53["family"].nunique()} families. This is the only Form 499 coefficient in the essay that '
        'survives calibrated inference; it is one rejection among many tests and is reported as such.')
    source(Q7, f'{E2}/t53_test_ledger.csv')
    with st.expander('Full announcement-contrast report'):
        st.text(fix_text(read_text(CONTRAST_MD)))
        source(CONTRAST_MD)


guard(sec_announce)

# ====================================================================== robustness
st.header('Robustness')
st.caption('Each check re-estimates the volatility result. Unless the table says otherwise, the p-values '
           'in these tables are from conventional SEs, not the governing CV3 rung.')


def rob_s1():
    with st.expander('S1 - persistent window with abnormal volatility, market-volatility control, year FE'):
        t = e2_table('t37_s1_s2_main')
        t['spec'] = t['spec'].map(fix_text)
        st.plotly_chart(ladder_chart(t.rename(columns={'spec': 'name'}).assign(p=float('nan')),
                                     'coef', 'name', 'Volatility coefficient across specifications',
                                     'Form 499 coefficient (daily pp), 95% CI'),
                        width='stretch')
        st.dataframe(t, hide_index=True, width='stretch')
        n_cross = int(((t['ci_lo'] < 0) & (t['ci_hi'] > 0)).sum())
        st.caption(f'{n_cross} of {len(t)} specifications have a 95% CI that includes zero.')
        source(f'{E2}/t37_s1_s2_main.csv')


def rob_placebo():
    with st.expander('Placebo reassignment of treatment across parent CIKs'):
        t = e2_table('t41_placebo').rename(columns={'Unnamed: 0': 'statistic'})
        st.dataframe(t, hide_index=True, width='stretch')
        line = next((l.strip() for l in read_text(PART_S).splitlines()
                     if 'PLACEBO-TREATMENT' in l), None)
        sd = t.loc[t['statistic'] == 'std', 'placebo_t'].iloc[0]
        st.caption(
            f'Distribution of CV1 t-statistics when treatment is randomly reassigned at the parent level. '
            f'Under well-calibrated SEs the spread would be about 1; it is {sd:.2f}, so CV1 SEs are too '
            'small - this is a diagnostic of the inference procedure (and the reason CV3 governs), not a '
            'p-value for the treatment effect.')
        if line:
            st.markdown(f'> {fix_text(line)}')
        source(f'{E2}/t41_placebo.csv', PART_S)


def rob_se():
    with st.expander('Standard-error specifications'):
        t = e2_table('t4_se_specifications')
        t.insert(1, 'role', t['label'].map(
            lambda s: 'disqualified - ignores within-parent correlation'
            if s in ('classical OLS', 'HC1', 'HC3') else rung_role(s)))
        st.dataframe(t, hide_index=True, width='stretch')
        st.caption('None of these rejects at the 5% level. Heteroskedasticity-only SEs are shown for '
                   'comparison; they understate uncertainty when events cluster within parents.')
        source(f'{E2}/t4_se_specifications.csv')


def rob_fe():
    with st.expander('Fixed effects'):
        t = e2_table('t8_fixed_effects')
        t['inference'] = 'HC3 (disqualified rung)'
        t['reading'] = t['p'].map(lambda p: 'HC3-only significance - not established on the governing '
                                  'CV3 rung' if p < 0.05 else 'not significant')
        st.dataframe(t, hide_index=True, width='stretch')
        st.caption('Fixed-effect variants are estimated with HC3 SEs. A row significant only on HC3 is '
                   'not a finding; with year and industry FE together the coefficient is not significant.')
        source(f'{E2}/t8_fixed_effects.csv')


def rob_size():
    with st.expander('Size quartiles'):
        t = e2_table('t5_size_quartiles')
        t['note'] = t['note'].map(fix_text)
        t['inference'] = 'HC3 (disqualified rung)'
        t['reading'] = t['p'].map(lambda p: 'HC3-only - NOT significant on the governing CV3 rung '
                                  '(no cluster-robust quartile estimate)' if p < 0.05 else
                                  'not significant')
        fig = go.Figure(go.Bar(
            x=t['label'], y=t['coef'], error_y=dict(type='data', array=1.96 * t['se']),
            marker_color=[C_CMP if p < 0.05 else C_CTRL for p in t['p']]))
        fig.add_hline(y=0, line_color='#555')
        fig.update_layout(yaxis_title='Form 499 coefficient (daily pp), +/- 1.96 HC3 SE', height=340,
                          margin=dict(l=10, r=10, t=20, b=40))
        st.plotly_chart(fig, width='stretch')
        st.dataframe(t, hide_index=True, width='stretch')
        few = t['treated_parent_ciks'] < 5
        st.caption(
            f'{int(few.sum())} of {len(t)} quartiles have fewer than five treated parent CIKs and cannot be '
            'interpreted on their own. Quartile p-values are HC3 only; signs flip across quartiles, and no '
            'quartile result is a finding on the governing rung.')
        source(f'{E2}/t5_size_quartiles.csv')


def rob_clusters():
    with st.expander('Cluster diagnostics (leave-one-parent-out)'):
        t = e2_table('t25_cluster_diagnostics')
        lad = e2_table('t26_inference_ladder')
        full = lad['coef'].iloc[0]
        fig = go.Figure(go.Scatter(
            x=t['size'], y=t['jackknife_coef'], mode='markers',
            marker=dict(size=6 + 40 * t['partial_leverage_share'], color=C_TREAT, opacity=0.6),
            hovertemplate='events %{x}<br>coef without this parent %{y:+.3f}<extra></extra>'))
        fig.add_hline(y=full, line_dash='dot', line_color=C_GOV,
                      annotation_text=f'full-sample {full:+.3f}')
        fig.add_hline(y=0, line_color='#555')
        fig.update_layout(xaxis_title='events in the parent cluster',
                          yaxis_title='coefficient with this parent deleted', height=380,
                          margin=dict(l=10, r=10, t=20, b=40))
        st.plotly_chart(fig, width='stretch')
        st.caption(
            f'{len(t)} parent clusters; leave-one-out coefficients range from '
            f'{t["jackknife_coef"].min():+.3f} to {t["jackknife_coef"].max():+.3f}, '
            f'{int((t["jackknife_coef"] < 0).sum())} with a negative sign. The largest cluster holds '
            f'{int(t["size"].max())} events. Point size = partial-leverage share.')
        st.dataframe(t, hide_index=True, width='stretch')
        source(f'{E2}/t25_cluster_diagnostics.csv', f'{E2}/t26_inference_ladder.csv')


for fn in (rob_s1, rob_placebo, rob_se, rob_fe, rob_size, rob_clusters):
    guard(fn)
