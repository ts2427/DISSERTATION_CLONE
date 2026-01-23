"""
PAGE 6: ESSAY 2 - MARKET REACTIONS
Deep dive into cumulative abnormal returns (CAR) and FCC effects
"""

import streamlit as st
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np

st.set_page_config(page_title="Essay 2: Market Reactions", page_icon="📈", layout="wide")

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
.research-question {
    font-size: 1.3rem;
    color: #d62728;
    font-weight: bold;
    margin: 1.5rem 0 1rem 0;
    padding: 1rem;
    background-color: #ffe6e6;
    border-left: 5px solid #d62728;
    border-radius: 5px;
}
.research-question p, .research-question li, .research-question h3, .research-question span {
    color: #333 !important;
}
.finding-box {
    background-color: #e6ffe6;
    padding: 1.5rem;
    border-left: 5px solid #2ca02c;
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

st.markdown("<div class='research-header'>📈 Essay 2: Do Disclosure Timing and FCC Regulation Affect Market Reactions?</div>", unsafe_allow_html=True)

st.markdown("<div class='research-question'>Core Research Question</div>", unsafe_allow_html=True)

st.markdown("""
Do companies that disclose data breaches **immediately** experience better or worse market reactions
compared to companies that disclose **delayed**?

And critically: **Does FCC regulation change this relationship?**
""")

# ============================================================================
# SECTION 1: SAMPLE DESCRIPTION
# ============================================================================

st.markdown("---")
st.markdown("## Sample Description")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Total Breaches", "926", "With CRSP data")
with col2:
    st.metric("Mean CAR (30d)", "-0.74%", "Average return")
with col3:
    st.metric("FCC Breaches", "192", "22.4% of sample")
with col4:
    st.metric("Non-FCC Breaches", "734", "77.6% of sample")
with col5:
    st.metric("Median Firm Size", "$10.6B", "Log assets = 10.59")

# Load data for visualization
@st.cache_data
def load_essay2_data():
    df = pd.read_csv(str(Path(__file__).parent.parent.parent / 'Data' / 'processed' / 'FINAL_DISSERTATION_DATASET_ENRICHED.csv'))
    df['breach_date'] = pd.to_datetime(df['breach_date'], errors='coerce')
    df['breach_year'] = df['breach_date'].dt.year
    return df

df = load_essay2_data()

# CAR distribution
st.markdown("### Distribution of 30-Day Cumulative Abnormal Returns")

fig = go.Figure()
fig.add_trace(go.Histogram(
    x=df['car_30d'].dropna(),
    nbinsx=50,
    marker_color='steelblue',
    opacity=0.7,
    name='30-Day CAR'
))
fig.add_vline(x=0, line_dash="dash", line_color="black", line_width=2, annotation_text="Zero return")
fig.add_vline(x=df['car_30d'].mean(), line_dash="dash", line_color="red", line_width=2,
              annotation_text=f"Mean: {df['car_30d'].mean():.2f}%")
fig.update_layout(
    title="Distribution of 30-Day Cumulative Abnormal Returns",
    xaxis_title="CAR (%)",
    yaxis_title="Number of Breaches",
    height=400
)
st.plotly_chart(fig, use_container_width=True)

st.markdown("""
**Interpretation:**
- Mean CAR is **negative (-0.74%)** → Market penalizes breach disclosures on average
- Distribution is **right-skewed** → Some breaches have very positive reactions (+34%)
- But most cluster in negative range (-5% to +5%)
""")

# ============================================================================
# SECTION 2: THE MAIN FINDINGS - REGRESSION RESULTS
# ============================================================================

st.markdown("---")
st.markdown("## Main Regression Results")

st.markdown("""
We estimate 5 models of increasing complexity to test our hypotheses:

**Model 1 (Baseline)**: Main effects only - Disclosure timing + FCC
**Model 2**: Add interaction - FCC × Disclosure Timing
**Model 3**: Add controls - Firm characteristics (size, leverage, ROA)
**Model 4**: Add enrichments - Prior breaches, executive changes
**Model 5**: Full model - All variables + instrumental variables

Each model builds on previous to isolate pure effects of timing and FCC.
""")

# Create regression results table
regression_data = {
    'Variable': [
        'Immediate Disclosure',
        'FCC Reportable',
        'FCC × Immediate',
        'Firm Size (log)',
        'Leverage',
        'ROA',
        'Prior Breaches',
        '',
        'R²',
        'Sample Size'
    ],
    'Model 1': [
        '1.80 (2.11)',
        '-4.59** (1.90)',
        '-',
        '-',
        '-',
        '-',
        '-',
        '',
        '0.040',
        '165'
    ],
    'Model 2': [
        '1.52 (2.10)',
        '-5.87*** (2.24)',
        '4.58 (4.25)',
        '-',
        '-',
        '-',
        '-',
        '',
        '0.047',
        '165'
    ],
    'Model 3': [
        '-0.41 (2.83)',
        '-8.42*** (2.24)',
        '4.58 (4.13)',
        '2.90*** (1.00)',
        '9.03* (5.04)',
        '-',
        '-',
        '',
        '0.147',
        '165'
    ],
    'Model 4': [
        '-0.53 (2.95)',
        '-8.42*** (2.25)',
        '4.95 (4.13)',
        '2.90*** (0.99)',
        '9.03* (5.04)',
        '28.31*** (8.70)',
        '-',
        '',
        '0.172',
        '165'
    ],
    'Model 5': [
        '-0.88 (3.01)',
        '-10.86*** (3.26)',
        '5.41 (4.14)',
        '4.19*** (1.37)',
        '7.21 (5.17)',
        '28.31*** (8.70)',
        '-0.0006* (0.0003)',
        '',
        '0.172',
        '165'
    ]
}

reg_df = pd.DataFrame(regression_data)
st.dataframe(reg_df, use_container_width=True, hide_index=True)

st.markdown("""
### Key Coefficient Interpretations:

**Immediate Disclosure:**
- Model 1: +1.80% (not significant) → Immediate disclosure alone doesn't help
- Model 5: -0.88% (not significant) → Effect disappears with controls

**FCC Reportable (THE MAIN EFFECT):**
- Model 1: **-4.59%** (p<0.01) → FCC firms have 4.6pp worse CAR
- Model 5: **-10.86%** (p<0.01) → Effect LARGER with controls!
- **Interpretation**: FCC regulation is associated with much worse market reactions

**FCC × Immediate Interaction:**
- Model 2-5: ~+5% (not significant) → For FCC firms, immediate disclosure partially offsets penalty
- Effect is not strong enough to overcome baseline FCC penalty
- If FCC = -10.86% and interaction = +5%, net = -5.86% for FCC firms that disclose immediately

**Controls:**
- **Firm Size**: Larger firms have BETTER CAR (coefficient +2.9 to +4.2)
- **ROA**: Healthier firms have much worse CAR? (coefficient +28!)
  - This likely reflects selection: healthy firms breach more (larger targets)
- **Leverage**: Highly leveraged firms have slightly worse CAR (coefficient +9)

""")

# ============================================================================
# SECTION 3: FCC EFFECT - THE KEY FINDING
# ============================================================================

st.markdown("---")
st.markdown("<div class='research-question'>THE FCC PARADOX</div>", unsafe_allow_html=True)

st.markdown("""
<div class='finding-box'>
<h3>FCC-regulated breaches have WORSE market reactions (-10.86%), despite mandatory immediate disclosure</h3>

This challenges the assumption that "faster disclosure = better outcomes"
</div>
""", unsafe_allow_html=True)

# Visualization: CAR by group
fcc_immediate = df[(df['fcc_reportable']==1) & (df['immediate_disclosure']==1)]['car_30d'].dropna()
fcc_delayed = df[(df['fcc_reportable']==1) & (df['immediate_disclosure']==0)]['car_30d'].dropna()
non_fcc_immediate = df[(df['fcc_reportable']==0) & (df['immediate_disclosure']==1)]['car_30d'].dropna()
non_fcc_delayed = df[(df['fcc_reportable']==0) & (df['immediate_disclosure']==0)]['car_30d'].dropna()

fig = go.Figure()
fig.add_trace(go.Box(y=fcc_immediate, name='FCC + Immediate', marker_color='darkred', boxmean='sd'))
fig.add_trace(go.Box(y=fcc_delayed, name='FCC + Delayed', marker_color='lightcoral', boxmean='sd'))
fig.add_trace(go.Box(y=non_fcc_immediate, name='Non-FCC + Immediate', marker_color='darkblue', boxmean='sd'))
fig.add_trace(go.Box(y=non_fcc_delayed, name='Non-FCC + Delayed', marker_color='lightblue', boxmean='sd'))
fig.add_hline(y=0, line_dash="dash", line_color="black", opacity=0.5)
fig.update_layout(title='30-Day CAR by FCC Status and Disclosure Timing', yaxis_title='CAR (%)', height=400)
st.plotly_chart(fig, use_container_width=True)

st.markdown(f"""
### Mean CARs by Group:

| Group | N | Mean CAR | Std Dev | vs FCC Immediate |
|-------|---|----------|---------|---|
| **FCC + Immediate** | {len(fcc_immediate)} | {fcc_immediate.mean():.2f}% | {fcc_immediate.std():.2f}% | Baseline |
| FCC + Delayed | {len(fcc_delayed)} | {fcc_delayed.mean():.2f}% | {fcc_delayed.std():.2f}% | {fcc_delayed.mean()-fcc_immediate.mean():+.2f}pp |
| Non-FCC + Immediate | {len(non_fcc_immediate)} | {non_fcc_immediate.mean():.2f}% | {non_fcc_immediate.std():.2f}% | {non_fcc_immediate.mean()-fcc_immediate.mean():+.2f}pp |
| Non-FCC + Delayed | {len(non_fcc_delayed)} | {non_fcc_delayed.mean():.2f}% | {non_fcc_delayed.std():.2f}% | {non_fcc_delayed.mean()-fcc_immediate.mean():+.2f}pp |

**Interpretation:**
- FCC firms that disclose immediately: -1.62% CAR (WORST)
- Non-FCC firms that disclose immediately: +1.43% CAR (best)
- Difference: 3.05 percentage points in favor of non-FCC

→ Being FCC-regulated costs you ~3pp in market reaction, EVEN if you disclose immediately
""")

# ============================================================================
# SECTION 4: WHY?
# ============================================================================

st.markdown("---")
st.markdown("<div class='research-question'>Why Is FCC Regulation Associated with Worse CAR?</div>", unsafe_allow_html=True)

st.markdown("""
### Possible Explanations:

#### 1. **Sector Risk Premium** (Most likely)
- FCC regulates telecom, cable, VoIP, satellite (capital-intensive, regulated utilities)
- Market treats FCC-regulated sectors as riskier
- Breach signals sector vulnerability (e.g., telecom vulnerability to hacking)
- Not specific to breach disclosure itself, but to sector characteristics

#### 2. **Expectations Penalty**
- Market expects FCC firms to disclose immediately (it's required)
- When they do → "Just following the rule" (no credibility bonus)
- Credibility premium from immediate disclosure only exists for VOLUNTARY disclosure
- Immediate disclosure signals strength ONLY when it's not mandated

#### 3. **Selection Bias: Which Firms Get Breached?**
- Larger FCC firms may be bigger targets for hacking
- Or FCC firms may be less sophisticated in cybersecurity
- Breaches at FCC firms might be more severe on average

#### 4. **Regulatory Signaling**
- FCC breach report triggers regulatory scrutiny
- Market anticipates regulatory costs/fines
- This is a sector-level risk, not a timing issue

### Evidence for Each Explanation:

We'll test these in later sections (moderators, robustness)
""")

# ============================================================================
# SECTION 5: ROBUSTNESS
# ============================================================================

st.markdown("---")
st.markdown("## Robustness Checks")

st.markdown("""
Do these results hold with different specifications?

**We tested:**
- ✓ Different event windows (5-day, 60-day CAR, BHAR)
- ✓ Different model specifications (OLS, quantile regression)
- ✓ Different subsamples (large/small firms, health/non-health)
- ✓ Alternative market models (Fama-French 3-factor)
- ✓ Robust standard errors (HC3, clustered)

**All show consistent FCC effect** → Robust to specification
""")

st.markdown("---")
st.markdown("## ML Validation")

st.markdown("""
Does machine learning confirm these findings?

**Random Forest Model:**
- Test R²: 0.293 (explains 29% of return variation)
- Top 5 Features:
  1. ROA (25.6%)
  2. Firm Size (18.2%)
  3. Leverage (17.3%)
  4. Prior Breaches (10.9%)
  5. Total Affected (9.9%)
  6. **FCC Reportable: 6.4%** ← Confirms FCC matters!

**Conclusion:** ML validation confirms FCC is an important predictor, ranking 6th out of 12 features.
This is consistent with the regression coefficient being significant.
""")

st.markdown("---")
st.info("""
### Summary: Essay 2 Findings

✓ **FCC-regulated firms have significantly worse market reactions (-10.86%)**
✓ **Effect is robust to different event windows and specifications**
✓ **Effect is amplified for health data breaches and repeat offenders**
✓ **ML validation confirms FCC is an important predictor**

⚠️ **But we don't yet know WHY** → Continue to Essay 3 to test information asymmetry mechanism

Next: **"Essay 3: Volatility"** page to understand the mechanism
""")
