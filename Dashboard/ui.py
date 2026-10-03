"""
Presentation helpers for the dissertation dashboard: one palette, one chart template, one way to
format numbers, tables, status labels, key-findings boxes and source notes. Pages import these so
every page looks the same. Nothing here computes or stores a result; values always come from the
committed outputs via data.py.
"""
import math

import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

# ------------------------------------------------------------------ palette
COLORS = {
    'navy': '#00205B',        # primary; Form 499 (treated); governing rung
    'red': '#BF0D3E',         # accent, used sparingly (alerts, observed values)
    'control': '#8A94A6',     # control group
    'comparison': '#A7B4C8',  # comparison rungs (CV1, unrestricted bootstrap)
    'disqualified': '#C9CED6',  # HC3 shown for comparison only
    'band': 'rgba(0, 32, 91, 0.07)',  # shaded bands (equivalence, SESOI)
    'grid': '#E6E9EF',
    'text': '#1C2430',
    'muted': '#5B6475',
    'green': '#2E7D4F',
    'amber': '#B7791F',
}
TREATED = COLORS['navy']
CONTROL = COLORS['control']
SEQ = [COLORS['navy'], '#4A6FA5', COLORS['red'], '#7A9CC6', COLORS['control'], '#2E7D4F', '#B7791F']

pio.templates['dissertation'] = go.layout.Template(
    layout=dict(
        font=dict(family='Source Sans Pro, Segoe UI, Helvetica, Arial, sans-serif', size=14,
                  color=COLORS['text']),
        title=dict(font=dict(size=16)),
        paper_bgcolor='white', plot_bgcolor='white', colorway=SEQ,
        xaxis=dict(gridcolor=COLORS['grid'], zerolinecolor='#B8C0CC', linecolor='#B8C0CC',
                   ticks='outside', tickcolor='#B8C0CC', automargin=True),
        yaxis=dict(gridcolor=COLORS['grid'], zerolinecolor='#B8C0CC', linecolor='#B8C0CC',
                   automargin=True),
        legend=dict(bgcolor='rgba(255,255,255,0.8)', borderwidth=0, font=dict(size=13)),
        margin=dict(l=10, r=10, t=40, b=10),
        hoverlabel=dict(bgcolor='white', font_size=13),
    ))
pio.templates.default = 'plotly_white+dissertation'


def chart(fig, height=None):
    """Render a plotly figure with the shared template and no plotly logo."""
    fig.update_layout(template='plotly_white+dissertation')
    if height:
        fig.update_layout(height=height)
    st.plotly_chart(fig, width='stretch', config={'displaylogo': False,
                                                  'modeBarButtonsToRemove': ['lasso2d', 'select2d']})


# ------------------------------------------------------------------ number formatting
def _isnum(x):
    try:
        return x is not None and not (isinstance(x, float) and math.isnan(x)) and not pd.isna(x)
    except (TypeError, ValueError):
        return x is not None


def fmt_num(x, d=2, signed=False):
    """Fixed decimals; '—' for missing. signed=True puts '+' on positives."""
    if not _isnum(x):
        return '—'
    try:
        v = float(x)
    except (TypeError, ValueError):
        return str(x)
    s = f'{v:+,.{d}f}' if signed else f'{v:,.{d}f}'
    return s.replace('-', '−')


def fmt_int(x):
    if not _isnum(x):
        return '—'
    try:
        return f'{int(round(float(x))):,}'
    except (TypeError, ValueError):
        return str(x)


def fmt_p(p):
    """p-values: three decimals, '< 0.001' below that, '—' if missing."""
    if not _isnum(p):
        return '—'
    v = float(p)
    return '< 0.001' if v < 0.001 else f'{v:.3f}'


def fmt_pct(x, d=1, scale=1.0):
    """Percent; scale=100 when x is a proportion."""
    if not _isnum(x):
        return '—'
    return f'{float(x) * scale:.{d}f}%'


def fmt_ci(lo, hi, d=2):
    if not (_isnum(lo) and _isnum(hi)):
        return '—'
    return f'[{fmt_num(lo, d)}, {fmt_num(hi, d)}]'


# ------------------------------------------------------------------ tables
def table(df, columns=None, formats=None, download=None, height=None, hide_index=True):
    """Show a tidy table.

    columns  : {source_column: display_name}, in display order. Columns not listed are dropped
               (None = keep all, unrenamed).
    formats  : {display_name: callable} applied cell-wise (e.g. fmt_p). Unformatted numbers get
               fmt_num with two decimals; missing values show as '—'.
    download : file name for a 'Download CSV' button of the underlying (unformatted) rows.
    """
    raw = df.copy()
    if columns:
        keep = [c for c in columns if c in raw.columns]
        raw = raw[keep].rename(columns=columns)
    out = raw.copy()
    formats = formats or {}
    for c in out.columns:
        f = formats.get(c)
        if f is not None:
            out[c] = out[c].map(f)
        elif pd.api.types.is_float_dtype(out[c]):
            out[c] = out[c].map(lambda v: fmt_num(v, 2))
        elif pd.api.types.is_integer_dtype(out[c]):
            out[c] = out[c].map(fmt_int)
        else:
            out[c] = out[c].map(lambda v: '—' if not _isnum(v) else str(v))
    kw = dict(width='stretch', hide_index=hide_index)
    if height:
        kw['height'] = height
    st.dataframe(out, **kw)
    if download:
        st.download_button('Download CSV', raw.to_csv(index=False).encode('utf-8'),
                           file_name=download, mime='text/csv', key=f'dl_{download}',
                           type='tertiary', icon=':material/download:')


# ------------------------------------------------------------------ text blocks
STATUS_STYLE = {
    'NULL-INCONCLUSIVE': ('Null — inconclusive', 'orange'),
    'BOUNDED NULL': ('Bounded null', 'green'),
    'SIGNIFICANT': ('Significant', 'blue'),
}


def status_badge(status):
    """Compact coloured label for a committed status string."""
    s = str(status).strip()
    label, color = STATUS_STYLE.get(s.upper(), (s.capitalize(), 'gray'))
    st.badge(label, color=color)


def page_header(title, subtitle=None):
    st.title(title)
    if subtitle:
        st.markdown(f'<p style="color:{COLORS["muted"]};font-size:1.05rem;margin-top:-0.6rem">'
                    f'{subtitle}</p>', unsafe_allow_html=True)


def framing_note():
    """One-line reminder of the design (the full statement lives on the Overview)."""
    st.caption('Descriptive, post-2007 cross-sectional design — no causal estimates. '
               'Treatment = FCC Form 499 registration status. Every number below is read from a '
               'committed pipeline output; sources are noted under each item.')


def key_findings(items, title='Key findings'):
    """A bordered box with 2-4 bullet points (text built by the page from loaded values)."""
    with st.container(border=True):
        st.markdown(f'**{title}**')
        st.markdown('\n'.join(f'- {i}' for i in items))


def section(title, intro=None):
    st.header(title, divider='gray')
    if intro:
        st.markdown(intro)
