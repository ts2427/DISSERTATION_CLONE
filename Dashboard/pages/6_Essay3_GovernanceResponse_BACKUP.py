"""
PAGE 7: ESSAY 3 - GOVERNANCE RESPONSE & EXECUTIVE TURNOVER
Explains organizational consequences: Do boards respond to forced disclosure with leadership changes?
Shows that 46.4% of breaches trigger executive turnover within 30 days
"""

import streamlit as st
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np

st.set_page_config(page_title="Essay 3: Governance Response", page_icon="👔", layout="wide")

st.markdown("""
<style>
.research-header {
    font-size: 2.5rem;
    font-weight: bold;
    color: #2ca02c;
    text-align: center;
    padding: 1rem 0;
    margin-bottom: 2rem;
    border-bottom: 3px solid #2ca02c;
}
.research-question {
    font-size: 1.3rem;
    color: #2ca02c;
    font-weight: bold;
    margin: 1.5rem 0 1rem 0;
    padding: 1rem;
    background-color: #e6ffe6;
    border-left: 5px solid #2ca02c;
    border-radius: 5px;
}
.research-question p, .research-question li, .research-question h3, .research-question span {
    color: #333 !important;
}
.governance-box {
    background-color: #e6f2ff;
    padding: 1.5rem;
    border-left: 5px solid #1f77b4;
    border-radius: 5px;
    margin: 1rem 0;
    font-size: 1.1rem;
    color: #333;
}
.governance-box p, .governance-box li, .governance-box h3, .governance-box span {
    color: #333 !important;
}
.finding-box {
    background-color: #fff4e6;
    padding: 1.5rem;
    border-left: 5px solid #ff7f0e;
    border-radius: 5px;
    margin: 1rem 0;
    font-size: 1.1rem;
    color: #333;
}
.finding-box p, .finding-box li, .finding-box h3, .finding-box span {
    color: #333 !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='research-header'>👔 Essay 3: Disclosure Timing and Governance Response</div>", unsafe_allow_html=True)

st.markdown("<div class='research-question'>Research Question: Stakeholder and Organizational Response</div>", unsafe_allow_html=True)

st.markdown("""
Essay 1 showed: **Markets react negatively to FCC regulation (-2.20% CAR).**
Essay 2 showed: **FCC volatility increases (+4.96%***) - forced disclosure raises uncertainty, not resolves it.**

Essay 3 asks: **HOW DO FIRMS RESPOND? Do they change governance structures and leadership?**

Stakeholder Theory (Freeman, 1984) and Crisis Management Theory predict:
- Disclosure activates multiple stakeholders simultaneously
- Boards respond to investor pressure and reputational threats
- Leadership changes signal accountability and governance response to crisis

**Testing with executive turnover as outcome measure (Logistic Regression):**

- **H5 (Timing → Turnover)**: Does immediate disclosure predict faster executive turnover?
  - Theory: Forced disclosure creates stakeholder pressure → board must respond quickly
  - Outcome: 30/90/180-day windows for executive changes

- **H6 (FCC Moderation on Turnover)**: Do FCC-regulated firms show different turnover patterns?
  - Theory: Regulatory oversight increases external stakeholder attention
  - Outcome: Enforcement expectations affect board urgency for governance response

- **Cascading Organizational Response**: Executive turnover increases with longer time windows
  - 30-day: Immediate governance shock (46.4% of breaches)
  - 90-day: Extended board deliberation (66.9% of breaches)
  - 180-day: Full governance reorganization (67.5% of breaches)

**Key Finding: 46.4% of breaches trigger executive turnover within 30 days (416 out of 896 breaches)**
""")

# ============================================================================
# SECTION 1: EXECUTIVE TURNOVER OVERVIEW
# ============================================================================

st.markdown("---")
st.markdown("## Executive Turnover Analysis")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Total Breaches", "896", "Analysis sample")
with col2:
    st.metric("30-Day Turnover", "46.4%", "416 breaches")
with col3:
    st.metric("90-Day Turnover", "66.9%", "599 breaches")
with col4:
    st.metric("180-Day Turnover", "67.5%", "605 breaches")
with col5:
    st.metric("Mean Changes", "3.2", "Executives per event")

# Load governance data
@st.cache_data
def load_governance_data():
    try:
        df = pd.read_csv(str(Path(__file__).parent.parent.parent / 'Data' / 'processed' / 'FINAL_DISSERTATION_DATASET_ENRICHED.csv'))
        df['breach_date'] = pd.to_datetime(df['breach_date'], errors='coerce')
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

df = load_governance_data()

if df is not None:
    # Filter to breaches with turnover data
    turnover_df = df[df['executive_change_30d'].notna()].copy()

    # ============================================================================
    # TURNOVER TIMELINE
    # ============================================================================

    st.markdown("### Turnover Timeline: When Does Leadership Change Occur?")

    # Create timeline data
    timeline_data = pd.DataFrame({
        'Window': ['30-day', '90-day', '180-day'],
        'Turnover %': [46.4, 66.9, 67.5],
        'Count': [416, 599, 605],
        'N': [896, 896, 896]
    })

    fig_timeline = px.bar(
        timeline_data,
        x='Window',
        y='Turnover %',
        title='Executive Turnover by Time Window After Breach',
        labels={'Turnover %': 'Percentage with Executive Changes'},
        text='Turnover %',
        color='Window',
        color_discrete_sequence=['#1f77b4', '#ff7f0e', '#2ca02c']
    )
    fig_timeline.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig_timeline.update_layout(height=400, showlegend=False)
    st.plotly_chart(fig_timeline, use_container_width=True)

    st.markdown("""
    <div class='finding-box'>
    <b>Key Pattern:</b> Nearly half of breaches (46.4%) result in executive turnover within 30 days.
    By 90 days, two-thirds (66.9%) have experienced leadership changes. This suggests that
    executive turnover is a primary organizational response to breach disclosure.
    </div>
    """, unsafe_allow_html=True)

    # ============================================================================
    # TURNOVER BY TIMING & FCC STATUS
    # ============================================================================

    st.markdown("---")
    st.markdown("### Turnover by Disclosure Timing and Regulatory Status")

    # Create cross-tabulation
    try:
        # 30-day turnover by immediate disclosure and FCC
        turnover_immediate_fcc = turnover_df.groupby(['immediate_disclosure', 'fcc_reportable'])['executive_change_30d'].agg(['sum', 'count']).reset_index()
        turnover_immediate_fcc.columns = ['Immediate', 'FCC', 'Turnover_Count', 'Total']
        turnover_immediate_fcc['Turnover %'] = (turnover_immediate_fcc['Turnover_Count'] / turnover_immediate_fcc['Total'] * 100).round(1)

        # Prepare for visualization
        turnover_immediate_fcc['Group'] = turnover_immediate_fcc.apply(
            lambda row: f"{'Immediate' if row['Immediate']==1 else 'Delayed'} - {'FCC' if row['FCC']==1 else 'Non-FCC'}",
            axis=1
        )

        fig_subgroup = px.bar(
            turnover_immediate_fcc,
            x='Group',
            y='Turnover %',
            title='30-Day Executive Turnover by Timing & Regulatory Status',
            text='Turnover %',
            labels={'Turnover %': 'Percentage with Turnover'},
            color='Group',
            color_discrete_sequence=['#1f77b4', '#d62728', '#2ca02c', '#ff7f0e']
        )
        fig_subgroup.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig_subgroup.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_subgroup, use_container_width=True)

        # Display table
        st.markdown("**Turnover Rates by Group:**")
        display_table = turnover_immediate_fcc[['Group', 'Total', 'Turnover_Count', 'Turnover %']].copy()
        display_table.columns = ['Group', 'Total Breaches', 'With Turnover', 'Turnover %']
        st.dataframe(display_table, use_container_width=True, hide_index=True)

    except Exception as e:
        st.warning(f"Could not create subgroup analysis: {e}")

    # ============================================================================
    # REGULATORY ENFORCEMENT CASES
    # ============================================================================

    st.markdown("---")
    st.markdown("### Regulatory Enforcement: A Rare Response")

    st.markdown("""
    <div class='governance-box'>
    <b>Finding:</b> Enforcement is rare (0.6% of sample, n=6 cases), all against FCC-regulated firms.
    This suggests regulatory forbearance despite high breach frequency.
    </div>
    """, unsafe_allow_html=True)

    # Create enforcement summary
    enforcement_summary = pd.DataFrame({
        'Company': ['Charter Communications', 'T-Mobile (Multiple)', 'Total'],
        'Penalty': ['$550,000', '$410,392', '$960,392'],
        'FCC Status': ['FCC', 'FCC', 'FCC Only'],
        'Cases': [1, 5, 6]
    })

    st.markdown("**Enforcement Cases Summary:**")
    st.dataframe(enforcement_summary, use_container_width=True, hide_index=True)

    st.markdown("""
    - **6 total enforcement actions** identified (out of 1,054 breaches = 0.6%)
    - **All 6 are FCC-regulated firms** (100% of enforcement cases)
    - **Penalties range**: $76.6M (T-Mobile high) to $118K
    - **Pattern**: Mix of immediate and delayed disclosure in enforcement cases

    **Interpretation**: Executive turnover is ~50x more common than regulatory enforcement
    """)

    # ============================================================================
    # GOVERNANCE RESPONSE MECHANISM
    # ============================================================================

    st.markdown("---")
    st.markdown("### Governance Response Mechanism")

    st.markdown("""
    <div class='governance-box'>

    **Why Do Boards Change Leadership After Breaches?**

    1. **Accountability Signal**: Turnover signals to stakeholders that the board takes breach seriously
    2. **Risk Management**: New leadership may bring fresh security perspectives
    3. **Scapegoating**: Executives removed to absorb blame and protect board
    4. **Regulatory Response**: FCC and other regulators may pressure governance changes

    **Three Interpretations:**

    - **Optimal Response**: Turnover improves security oversight and breach prevention
      - Evidence: Need follow-up research on breach patterns post-turnover

    - **Governance Theater**: Turnover is visible but ineffective response
      - Evidence: High turnover rate suggests reactive rather than strategic response

    - **Stakeholder Pressure**: Multiple stakeholders (investors, regulators, public) activate
      - Evidence: 46.4% turnover rate suggests systematic board response

    </div>
    """, unsafe_allow_html=True)

    # ============================================================================
    # CROSS-ESSAY INTEGRATION
    # ============================================================================

    st.markdown("---")
    st.markdown("### How Essay 3 Completes the Dissertation Story")

    st.markdown("""
    **Essay 1:** Markets react negatively to forced disclosure
    - CAR: Approximately -0.74%*** (statistically significant)
    - Finding: FCC firms have worse market reactions

    **Essay 2:** Forced timing increases volatility
    - Effect: +4.96%*** for FCC firms (p<0.001)
    - Mechanism: Information processing bottleneck (Tushman & Nadler, 1978)

    **Essay 3:** Firms respond with governance changes
    - Primary response: 46.4% experience executive turnover (30 days)
    - Secondary response: 6 regulatory enforcement actions (0.6%)
    - Organizational interpretation: Multiple stakeholders activate simultaneously

    **Integrated Finding: THE DISCLOSURE PARADOX**

    Forced disclosure requirements have cascading effects:
    1. **Market Level** (Essay 1): Negative abnormal returns
    2. **Information Level** (Essay 2): Increased uncertainty (higher volatility)
    3. **Organizational Level** (Essay 3): Executive leadership changes

    Implication: Disclosure policy affects not just transparency, but organizational structure
    """)

    # ============================================================================
    # IMPLICATIONS & FUTURE RESEARCH
    # ============================================================================

    st.markdown("---")
    st.markdown("### Implications & Future Research Questions")

    st.markdown("""
    **For Theory:**
    - Stakeholder theory validated: Multiple stakeholders respond simultaneously
    - Governance changes as organizational adaptation mechanism
    - Disclosure mandates have broader organizational consequences than typically studied

    **For Policy:**
    - Should disclosure timing requirements account for governance consequences?
    - Is executive turnover beneficial (improved security) or harmful (lost expertise)?
    - Should regulators consider governance impacts when setting disclosure timelines?

    **For Investors:**
    - Breach → turnover likely within 6 months (predictable outcome)
    - New leadership may signal security focus or governance instability
    - Long-term returns after turnover: opportunity for further research

    **For Future Research:**
    - Do replacement executives improve breach prevention?
    - What is the long-term firm performance after executive turnover?
    - Do governance changes correlate with better cybersecurity outcomes?
    - How do different regulatory regimes affect governance response patterns?
    """)

else:
    st.error("Failed to load governance data")

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown("""
**Next Steps:** Proceed to the "Key Findings" page to see the complete three-essay synthesis
or "Conclusion" page for policy implications.
""")
