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
