"""
PAGE 4: DATA LANDSCAPE
Shows the landscape of data breaches: timeline, industries
"""

import streamlit as st
from pathlib import Path
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Data Landscape", page_icon="🗺️", layout="wide")

st.markdown("""
<style>
.header {
    font-size: 2.5rem;
    font-weight: bold;
    color: #2ca02c;
    text-align: center;
    padding: 1rem 0;
    margin-bottom: 2rem;
    border-bottom: 3px solid #2ca02c;
}
.context-box {
    background-color: #e6ffe6;
    padding: 1.5rem;
    border-left: 5px solid #2ca02c;
    border-radius: 5px;
    margin: 1rem 0;
    color: #333;
}
.context-box p, .context-box li, .context-box h3, .context-box span {
    color: #333 !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='header'>🗺️ The Data Landscape</div>", unsafe_allow_html=True)

st.markdown("""
<div class='context-box'>
Before we analyze regression results, let's understand the DATA itself.
What breaches are in our dataset? How are they distributed across time and industries?
</div>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv(str(Path(__file__).parent.parent.parent / 'Data' / 'processed' / 'FINAL_DISSERTATION_DATASET_ENRICHED.csv'))
    df['breach_date'] = pd.to_datetime(df['breach_date'], errors='coerce')
    df['breach_year'] = df['breach_date'].dt.year
    df['treatment_group'] = df['fcc_reportable'].apply(lambda x: 'FCC-Regulated' if x == 1 else 'Non-FCC')
    df['period'] = df['breach_year'].apply(lambda x: 'Pre-2007' if x < 2007 else 'Post-2007')
    return df

df = load_data()

# Overall metrics
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Breaches", f"{len(df):,}")
with col2:
    essay2_n = (df['has_crsp_data'] == True).sum()
    st.metric("Essay 2 Sample", f"{essay2_n:,}")
with col3:
    essay3_n = df['return_volatility_pre'].notna().sum()
    st.metric("Essay 3 Sample", f"{essay3_n:,}")
with col4:
    fcc_count = (df['fcc_reportable'] == 1).sum()
    fcc_pct = (fcc_count / len(df)) * 100
    st.metric("FCC Breaches", f"{fcc_pct:.1f}%")

st.markdown("---")
st.markdown("## Breach Timeline: Pre-2007 vs. Post-2007")

timeline_data = df.groupby(['breach_year', 'treatment_group']).size().reset_index(name='count')

fig = px.bar(
    timeline_data,
    x='breach_year',
    y='count',
    color='treatment_group',
    title='Breaches Over Time',
    labels={'breach_year': 'Year', 'count': 'Count'},
    barmode='stack',
    color_discrete_map={'FCC-Regulated': '#d62728', 'Non-FCC': '#1f77b4'}
)
fig.add_vline(x=2007, line_dash="dash", line_color="green", line_width=3,
              annotation_text="FCC Regulation", annotation_position="top right")
fig.update_layout(height=400)
st.plotly_chart(fig, use_container_width=True)

st.markdown("""
**Key Pattern:** FCC regulation in 2007 created natural experiment.
- Before 2007: Both groups choose timing freely
- After 2007: FCC firms forced to disclose within 7 days
""")

st.markdown("---")
st.markdown("## Industry Diversity: Top Industries by SIC Code")

st.markdown("Sample spans diverse industries (not concentrated in one sector):")

try:
    sic_descriptions = {
        7372: "Services - Prepackaged Software",
        6200: "Finance - Security & Commodity Brokers",
        4813: "Communications - Telephone (FCC regulated)",
        3400: "Manufacturing - Fabricated Metals",
        1000: "Mining - Metal Mining",
        5122: "Wholesale - Drugs & Sundries",
        6500: "Finance - Real Estate",
        2834: "Manufacturing - Pharmaceutical Chemicals",
        4841: "Communications - Cable Television (FCC regulated)",
        4833: "Communications - Radio Broadcasting (FCC regulated)",
    }

    sic_counts = df['sic'].value_counts().head(10)

    table_data = []
    for rank, (sic_code, count) in enumerate(sic_counts.items(), 1):
        pct = (count / len(df)) * 100
        description = sic_descriptions.get(sic_code, "Other")
        table_data.append({
            'Rank': rank,
            'SIC Code': sic_code,
            'Industry Description': description,
            'Breaches': count,
            '% of Sample': f"{pct:.1f}%"
        })

    sic_table = pd.DataFrame(table_data)
    st.dataframe(sic_table, use_container_width=True, hide_index=True)

    st.markdown(f"""
    **Diversity:**
    - Top 3 industries: {(sic_counts.head(3).sum() / len(df) * 100):.1f}% of sample
    - Top 10 industries: {(sic_counts.sum() / len(df) * 100):.1f}% of sample
    - Sample includes tech, finance, telecommunications, and manufacturing
    """)

except Exception as e:
    st.warning(f"Could not display industry analysis: {e}")

st.markdown("---")

st.markdown("""
**Summary:**
- ✓ 1,000+ breaches spanning 2004-2025
- ✓ Diverse industries (not one-sided)
- ✓ Clear regulatory event (FCC 2007)
- ✓ Sufficient data for statistical analysis

→ Ready for regression analysis
""")
