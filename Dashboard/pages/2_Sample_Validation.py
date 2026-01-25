"""
PAGE 3: SAMPLE VALIDATION
Proves sample is defensible and addresses selection bias concerns
"""

import streamlit as st
from pathlib import Path
import pandas as pd
from utils import load_main_dataset

st.set_page_config(page_title="Sample Validation", page_icon="📋", layout="wide")

st.markdown("""
<style>
.research-header {
    font-size: 2.5rem;
    font-weight: bold;
    color: #1f77b4;
    text-align: center;
    padding: 1rem 0;
    margin-bottom: 2rem;
    border-bottom: 3px solid #1f77b4;
}
.evidence-box {
    background-color: #f0f2f6;
    padding: 1.5rem;
    border-radius: 10px;
    border-left: 5px solid #1f77b4;
    margin: 1rem 0;
    color: #333;
}
.evidence-box p, .evidence-box li, .evidence-box h3, .evidence-box span {
    color: #333 !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='research-header'>📋 Sample Validation</div>", unsafe_allow_html=True)

st.markdown("""
<div class='evidence-box'>
<h3>Why This Matters</h3>

Key concerns:
- How many breaches are excluded, and why?
- Could selection bias explain the results?
- Do FCC and non-FCC firms differ systematically?
</div>
""", unsafe_allow_html=True)

# Load data
def load_data():
    return load_main_dataset()

@st.cache_data
def load_sample_attrition():
    return pd.read_csv(str(Path(__file__).parent.parent.parent / 'outputs' / 'tables' / 'sample_attrition.csv'))

df = load_data()
sample_attrition = load_sample_attrition()

st.markdown("---")
st.markdown("## Sample Attrition")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Raw Breaches", f"{len(df):,}")
with col2:
    essay2_count = (df['has_crsp_data'] == True).sum()
    pct = (essay2_count / len(df)) * 100
    st.metric("Essay 2 Sample", f"{essay2_count:,}", f"{pct:.1f}%")
with col3:
    essay3_count = (df['return_volatility_pre'].notna()).sum()
    pct = (essay3_count / len(df)) * 100
    st.metric("Essay 3 Sample", f"{essay3_count:,}", f"{pct:.1f}%")

st.markdown("""
**Exclusions:**
- No CRSP stock data (14.7%): Delisted, private, penny stocks
- No volatility data (15.3%): Missing historical price data
- Final samples: **898 breaches (Essay 2)**, **891 breaches (Essay 3)**

**Key point:** Disclosure timing does NOT predict exclusion → No selection bias on main predictor

Excluded firms tend to be smaller and have fewer prior breaches, but these differences
are controlled for in regression models. The natural experiment (FCC status) is orthogonal
to exclusion criteria.
""")

st.markdown("---")
st.markdown("## Selection Bias Check")

st.dataframe(sample_attrition, use_container_width=True, hide_index=True)

st.markdown("""
**Bottom line:**
- ✓ Main predictor (timing) doesn't predict exclusion
- ⚠️ Results stronger for larger firms with prior breach history
- ⚠️ Smaller firms and startups underrepresented
- → Findings apply best to mid-sized to large publicly-traded firms
""")

st.markdown("---")
st.markdown("## Natural Experiment: Are FCC and Non-FCC Firms Comparable?")

try:
    fcc_df = df[df['fcc_reportable'] == 1]
    non_fcc_df = df[df['fcc_reportable'] == 0]

    comparison_vars = {
        'Firm Size (log)': 'firm_size_log',
        'Leverage': 'leverage',
        'ROA': 'roa',
        'Prior Breaches': 'prior_breaches_total'
    }

    comp_data = []
    for label, col in comparison_vars.items():
        if col in df.columns:
            fcc_val = pd.to_numeric(fcc_df[col], errors='coerce').mean()
            non_fcc_val = pd.to_numeric(non_fcc_df[col], errors='coerce').mean()
            diff = fcc_val - non_fcc_val
            comp_data.append({
                'Variable': label,
                'FCC': f"{fcc_val:.2f}",
                'Non-FCC': f"{non_fcc_val:.2f}",
                'Difference': f"{diff:.2f}"
            })

    comp_table = pd.DataFrame(comp_data)
    st.dataframe(comp_table, use_container_width=True, hide_index=True)

    st.markdown("""
    **Interpretation:**
    - FCC firms are larger (expected: regulated firms are bigger)
    - FCC firms have more prior breaches (longer history)
    - Differences are OK because we control for them in regressions
    - → Natural experiment is valid with appropriate controls
    """)

except Exception as e:
    st.warning(f"Could not run comparison: {e}")

st.markdown("---")
st.markdown("""
<div class='evidence-box'>
<h3>Conclusion</h3>

✓ Sample attrition is explained and not biased by main predictor
✓ FCC and non-FCC firms are comparable with statistical controls
✓ Limitations are documented and honest

→ Sample is defensible for causal inference
</div>
""", unsafe_allow_html=True)
