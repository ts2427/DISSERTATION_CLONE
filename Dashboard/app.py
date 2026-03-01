"""
Data Breach Disclosure Timing and Market Reactions
Interactive Committee-Focused Dashboard

Central Research Question:
"Is there any benefit to disclosing a data breach immediately,
or should it be delayed?"

Framework: Information Asymmetry Theory
Natural Experiment: FCC Regulation (2007)

This dashboard tells the complete story: Problem → Theory → Evidence → Implications
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import json
from utils import load_main_dataset

# ===============================
# PAGE CONFIGURATION
# ===============================
st.set_page_config(
    page_title="Data Breach Analytics - Committee View",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===============================
# CUSTOM STYLING
# ===============================
st.markdown("""
<style>
/* Research story color scheme */
.research-header {
    font-size: 2.8rem;
    font-weight: bold;
    color: #1f77b4;
    text-align: center;
    padding: 1rem 0;
    margin-bottom: 2rem;
    border-bottom: 3px solid #1f77b4;
}

.research-question {
    font-size: 1.6rem;
    color: #d62728;
    font-weight: bold;
    margin: 1.5rem 0 1rem 0;
    padding: 1rem;
    background-color: #ffe6e6;
    border-left: 5px solid #d62728;
    border-radius: 5px;
}

.research-question p, .research-question li {
    color: #333;
}

.key-finding {
    font-size: 1.2rem;
    color: #2ca02c;
    font-weight: bold;
    margin: 1rem 0;
    padding: 1rem;
    background-color: #e6ffe6;
    border-left: 5px solid #2ca02c;
    border-radius: 5px;
}

.evidence-box {
    background-color: #f0f2f6;
    padding: 1.5rem;
    border-radius: 10px;
    border-left: 5px solid #1f77b4;
    margin: 1rem 0;
    color: #333;
}

.evidence-box p, .evidence-box li, .evidence-box span {
    color: #333 !important;
}

/* Ensure all text in light boxes is dark */
[style*="background-color: #e6f2ff"] { color: #333; }
[style*="background-color: #ffe6e6"] { color: #333; }
[style*="background-color: #f0f2f6"] { color: #333; }
[style*="background-color: #e6ffe6"] { color: #333; }
[style*="background-color: #fff4e6"] { color: #333; }
[style*="background-color: #e6f2ff"] p { color: #333; }
[style*="background-color: #ffe6e6"] p { color: #333; }
[style*="background-color: #f0f2f6"] p { color: #333; }
[style*="background-color: #e6ffe6"] p { color: #333; }
[style*="background-color: #fff4e6"] p { color: #333; }

.implication-box {
    background-color: #fff4e6;
    padding: 1.5rem;
    border-radius: 10px;
    border-left: 5px solid #ff7f0e;
    margin: 1rem 0;
}

.metric-card {
    background-color: #f8f9fa;
    padding: 1rem;
    border-radius: 8px;
    border: 1px solid #dee2e6;
    margin: 0.5rem 0;
    text-align: center;
}

.tab-container {
    margin: 2rem 0;
}

.stTabs [data-baseweb="tab-list"] { gap: 2rem; }
</style>
""", unsafe_allow_html=True)

# ===============================
# LOAD DATA WITH CACHING
# ===============================
@st.cache_data
def load_ml_results():
    """Load ML validation results"""
    try:
        root_dir = Path(__file__).parent.parent
        ml_path = root_dir / 'outputs' / 'ml_models' / 'ml_model_results.json'
        with open(ml_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return None

@st.cache_data
def load_sample_attrition():
    """Load sample attrition analysis"""
    try:
        root_dir = Path(__file__).parent.parent
        attrition_path = root_dir / 'outputs' / 'tables' / 'sample_attrition.csv'
        return pd.read_csv(attrition_path)
    except FileNotFoundError:
        return None

# Load all data (using smart local + cloud fallback)
df = load_main_dataset()
ml_results = load_ml_results()
sample_attrition = load_sample_attrition()

if df is None:
    st.error("❌ Data not found! Ensure data files are in Data/processed/")
    st.stop()

# ===============================
# EXPORT FUNCTIONALITY
# ===============================
def generate_dissertation_report():
    """Generate downloadable dissertation findings summary report"""

    # Get essay statistics from the dataframe
    essay1_n = 926  # CRSP sample with market reaction data
    essay2_n = df['return_volatility_pre'].notna().sum() if 'return_volatility_pre' in df.columns else 916
    essay3_n = df['executive_change_30d'].notna().sum() if 'executive_change_30d' in df.columns else 896

    # Calculate key statistics
    car_5day_mean = df['car_5d'].mean() if 'car_5d' in df.columns else -0.01
    volatility_post_mean = df['return_volatility_post'].mean() if 'return_volatility_post' in df.columns else 26.46
    exec_change_30d_pct = (df['executive_change_30d'].sum() / essay3_n * 100) if essay3_n > 0 else 46.4
    fcc_car_coef = -2.19  # From TABLE B8

    report = f"""DISSERTATION FINDINGS SUMMARY REPORT
====================================================================================================

Generated: {pd.Timestamp.now().strftime('%B %d, %Y')}
Research Question: Is there any benefit to disclosing a data breach immediately, or should it be delayed?

====================================================================================================
ESSAY 1: MARKET REACTIONS TO DATA BREACHES
====================================================================================================

Research Question:
Do markets react negatively to forced disclosure under FCC regulation?

Key Findings:
- FCC-regulated firms experience WORSE market reactions to disclosures
- Effect is robust across multiple model specifications and robustness checks
- Main coefficient suggests significant negative abnormal returns for regulated firms

Sample Size: {essay1_n} breached firms with CRSP stock market data
Study Period: 2004-2019

Main Results:
- Average 5-day CAR (all firms): {car_5day_mean:.2f}%
- FCC Regulation Effect: {fcc_car_coef:.2f}% (significant at p<0.05)
- Robustness: Effect remains significant controlling for firm size, leverage, prior breaches
- Post-2007 Interaction Test: Effect is FCC-specific (p=0.0125, coef=-2.26%)

Implication:
FCC-mandated immediate disclosure does not reduce information asymmetry but increases market concerns.
Forced timing (7-day requirement) may sacrifice disclosure quality for speed.

====================================================================================================
ESSAY 2: INFORMATION ASYMMETRY AND VOLATILITY RESPONSE
====================================================================================================

Research Question:
Does forced early disclosure increase market volatility (information asymmetry)?

Key Findings:
- FCC firms experience HIGHER post-breach volatility despite forced disclosure
- Volatility increases rather than decreases, suggesting information quality issues
- Early forced disclosure creates uncertainty rather than clarity

Sample Size: {essay2_n} breached firms with complete volatility data
Study Period: 2004-2019

Main Results:
- Average post-breach volatility (all firms): {volatility_post_mean:.2f}%
- FCC Regulation Effect on Volatility: +1.83% (significant at p<0.05)
- Interpretation: Forced 7-day disclosure INCREASES rather than decreases asymmetry
- Mechanism: Speed over substance reduces information quality

Implication:
Regulatory pressure for speed may force incomplete or hastily prepared disclosures, increasing
rather than decreasing information asymmetry. Quality of disclosure matters more than timing.

====================================================================================================
ESSAY 3: GOVERNANCE RESPONSE AND EXECUTIVE TURNOVER
====================================================================================================

Research Question:
Do firms respond to breach disclosure with executive leadership changes?

Key Findings:
- {exec_change_30d_pct:.1f}% of breaches trigger executive turnover within 30 days
- Governance response is the primary firm response (not regulatory enforcement)
- Regulatory enforcement rare (only 0.6% of cases → FCC enforcement)

Sample Size: {essay3_n} breached firms with executive composition data
Study Period: 2004-2019

Main Results:
- Executive turnover (30 days): {exec_change_30d_pct:.1f}% of breaches
- Executive turnover (90 days): 62% of breaches
- Regulatory enforcement cases: 0.6% of breaches
- Governance response >> Regulatory response

Implication:
Firms' primary response to breaches is governance restructuring (board/executive changes),
not regulatory penalties. This suggests boards view breach response as critical to firm credibility.

====================================================================================================
THE DISCLOSURE PARADOX: THREE-ESSAY SYNTHESIS
====================================================================================================

Central Finding:
Faster disclosure ≠ Better market outcomes or reduced information asymmetry

Why This Matters:
1. FOR COMPANIES: Fast disclosure under regulatory pressure may backfire if preparation is rushed
2. FOR REGULATORS: Timing requirements must balance speed with disclosure quality
3. FOR THEORY: Information asymmetry theory requires quality, not just speed
4. FOR MARKETS: Volatility reflects investor uncertainty, not regulatory compliance

====================================================================================================
DATA SOURCE
====================================================================================================

Complete Descriptive Statistics: outputs/tables/TABLE1_COMBINED.txt
- Panel A: Full Sample (N=1,054)
- Panel B: CRSP Sample (N=926, with market reaction data)
- Panel C: By FCC Regulation (N=926)
- Panel D: By Disclosure Timing (N=926)

All continuous variables winsorized at 1% and 99% levels.

====================================================================================================
END OF REPORT
====================================================================================================
"""
    return report

# Add export button in sidebar
with st.sidebar:
    st.markdown("---")
    st.markdown("### 📥 Export Findings")

    # Generate the report
    report_text = generate_dissertation_report()

    # Create download button
    st.download_button(
        label="📥 Download Summary Report",
        data=report_text,
        file_name="Dissertation_Summary_Report.txt",
        mime="text/plain",
        use_container_width=True
    )

    st.caption("📄 Generate a downloadable summary of all dissertation findings.")
    st.markdown("---")

# ===============================
# MAIN WELCOME PAGE
# ===============================
st.markdown("<div class='research-header'>🔒 Data Breach Disclosure Timing and Market Reactions</div>", unsafe_allow_html=True)

st.markdown("""
<div class='evidence-box'>
<h3>Central Research Question</h3>
<p style='font-size: 1.3rem; color: #d62728; font-weight: bold;'>
"Is there any benefit to disclosing a data breach immediately, or should it be delayed?"
</p>
<p style='margin-top: 1rem;'>
This is a <b>practical question</b> every breached company faces with real financial and reputational stakes.<br>
This is a <b>theoretical puzzle</b> that information asymmetry theory helps solve.<br>
This is a <b>policy question</b> that regulators actively debate.
</p>
</div>
""", unsafe_allow_html=True)

# Key statistics
st.markdown("## 📊 The Dataset")
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Total Breaches", f"{len(df):,}")
with col2:
    st.metric("Study Period", f"{int(df['breach_year'].min())}-{int(df['breach_year'].max())}")
with col3:
    essay2_n = df['return_volatility_pre'].notna().sum()
    essay2_pct = (essay2_n / len(df)) * 100
    st.metric("Essay 2 Sample", f"{essay2_n} ({essay2_pct:.1f}%)")
with col4:
    essay3_n = df['executive_change_30d'].notna().sum()
    essay3_pct = (essay3_n / len(df)) * 100
    st.metric("Essay 3 Sample", f"{essay3_n} ({essay3_pct:.1f}%)")
with col5:
    st.metric("Unique Companies", f"{df['org_name'].nunique():,}")

# Navigation guide
st.markdown("---")
st.markdown("""
## 🗺️ How to Use This Dashboard

This dashboard tells a complete three-essay research story. Navigate through pages in order:

1. **📖 Welcome** (you are here) - Research questions and context
2. **🔬 Natural Experiment** - FCC regulation as treatment and identification strategy
3. **📋 Sample Validation** - Proof that sample is defensible
4. **🌍 Data Landscape** - What are we analyzing?
5. **📈 Essay 1: Market Reactions** - Do markets react negatively to forced disclosure?
6. **💨 Essay 2: Information Asymmetry** - Does forced timing increase volatility?
7. **👔 Essay 3: Governance Response** - Do firms respond with executive turnover?
8. **💡 Key Findings** - Three-essay synthesis and the Disclosure Paradox
9. **✅ Conclusion** - Cross-essay implications for business, policy, research
10. **📂 Raw Data Explorer** - Search, filter, explore all data yourself
11. **📚 Data Dictionary** - All variables documented

Each section shows: **Research Question → Evidence → Finding → Implication**

---

### Quick Context

**Why does this research matter?**

- **For Companies**: Understanding market reactions helps with crisis management and disclosure strategy
- **For Regulators**: FCC and other agencies set disclosure timelines; this research shows the market consequences
- **For Theory**: Tests information asymmetry theory in the real-world context of data breaches
- **For Your Committee**: Demonstrates rigorous research combining theory, natural experiments, and ML validation

---

### Preview of Key Findings

This research reveals a **counterintuitive result**:
""", unsafe_allow_html=True)

st.markdown("""
<div class='key-finding'>
✨ THREE KEY FINDINGS - THE DISCLOSURE PARADOX

<b>Essay 1:</b> FCC-regulated firms have WORSE market reactions (-2.19% CAR). FCC penalty is robust to CPNI and market concentration controls (remains significant at -1.15% to -2.44%).

<b>Essay 2:</b> FCC firms experience HIGHER volatility (+1.83%**) even with forced 7-day disclosure. Information asymmetry INCREASES rather than decreases - forced early disclosure sacrifices quality for speed.

<b>Essay 3:</b> 46.4% of breaches trigger executive turnover within 30 days (416/896 breaches). Firms respond organizationally; 6 enforcement cases (0.6%) - governance response exceeds regulatory response.

This challenges the assumption that "faster disclosure = better outcomes". The answer depends critically on regulatory context AND impacts multiple stakeholders (market, management, boards).
</div>
""", unsafe_allow_html=True)

# ===============================
# NATURAL EXPERIMENT VALIDATION
# ===============================
st.markdown("---")
st.markdown("""
## 🔬 Natural Experiment Validation

### Parallel Trends: Evidence of Causal Identification

For a natural experiment design to be credible, FCC-regulated and non-FCC firms must show **parallel trends**
before the 2007 FCC Rule 37.3 implementation. This figure provides visual proof of that assumption.
""")

# Load and display parallel trends figure
try:
    from pathlib import Path
    root_dir = Path(__file__).parent.parent
    figure_path = root_dir / 'outputs' / 'figures' / 'FIGURE_PARALLEL_TRENDS.png'

    if figure_path.exists():
        st.image(str(figure_path), caption="""
        **Figure 1: Parallel Trends in Cumulative Abnormal Returns (CAR)**

        Pre-2007 (before FCC Rule 37.3): FCC and non-FCC firms show similar CAR patterns (no significant difference, p=0.88)

        Post-2007 (after regulation): FCC firms experience worse market reactions (-2.26%, p=0.0125)

        This temporal pattern is consistent with causal interpretation: the treatment effect emerges exactly when
        the regulation takes effect, not before. This is the core evidence that FCC Rule 37.3 causally affects market outcomes.
        """, use_column_width=True)

        st.markdown("""
        ### What This Validates

        ✅ **Temporal Validity**: FCC effect appears post-2007 (when regulation took effect), not pre-2007

        ✅ **Causal Identification**: The timing of effect emergence matches the timing of regulation implementation

        ✅ **Natural Experiment Strength**: This is exactly the pattern expected from a true causal shock

        ✅ **Robustness**: Three additional validation tests support causal interpretation:
        - Industry fixed effects (effect strengthens, not weakens, with industry controls)
        - Size sensitivity (effects vary by firm size in mechanistically consistent ways)
        - Multi-outcome consistency (FCC affects returns, volatility, AND governance)
        """)
    else:
        st.warning("⚠️ Parallel trends figure not found. Run `python scripts/create_parallel_trends_figure.py` to generate.")

except Exception as e:
    st.warning(f"⚠️ Could not load parallel trends figure: {str(e)}")

# Balance Test Reference
st.markdown("""
### Balance Test: Pre-Treatment Covariate Parity

Before 2007, FCC-regulated and non-FCC firms should be balanced on observable characteristics
(firm size, leverage, profitability). This strengthens the parallel trends assumption.

**Table A1 (Balance Test Results):**
- Log(Total Assets): p=0.330 (balanced)
- Leverage (Debt/Assets): p=0.126 (balanced)
- Return on Assets: p=0.474 (balanced)

**Conclusion:** FCC ≈ non-FCC on all observables pre-2007. Parallel trends assumption is plausible.

See `outputs/tables/TABLE_BALANCE_TEST.csv` for detailed results.
""")

# Footer with navigation
st.markdown("---")
st.info("""
👈 **Use the sidebar to navigate** to different analysis pages.

Each page builds on previous insights.
Start with "Natural Experiment" to understand the framework.
Then progress through Essays 1, 2, and 3 evidence.
End with "Conclusion" for the full three-essay synthesis.
""")

st.markdown(f"""
<div style='text-align: center; color: #666; padding: 2rem 0;'>
    <p><b>Committee-Focused Research Dashboard</b> | Dissertation in Progress</p>
    <p>{len(df):,} breaches • {int(df['breach_year'].max()) - int(df['breach_year'].min()) + 1} years ({int(df['breach_year'].min())}-{int(df['breach_year'].max())}) • {len(df.columns)} variables</p>
    <p style='font-size: 0.9rem; margin-top: 1rem;'>
        Built with Streamlit | Data analysis with Pandas, Statsmodels, Scikit-learn | Visualizations with Plotly
    </p>
</div>
""", unsafe_allow_html=True)
