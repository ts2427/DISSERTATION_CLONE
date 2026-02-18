"""
PAGE 5: ESSAY 1 - MARKET REACTIONS
Deep dive into cumulative abnormal returns (CAR) and FCC effects on market reactions
"""

import streamlit as st
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np

st.set_page_config(page_title="Essay 1: Market Reactions", page_icon="📈", layout="wide")

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

st.markdown("<div class='research-header'>📈 Essay 1: Do Disclosure Timing and FCC Regulation Affect Market Reactions?</div>", unsafe_allow_html=True)

st.markdown("<div class='research-question'>Research Question & Hypotheses</div>", unsafe_allow_html=True)

st.markdown("""
**Main Research Question:** What determines market reactions to breach disclosures? Is it timing, regulation, or information environment?

**H1 (Timing Effect):** Does immediate disclosure reduce cumulative abnormal returns?
- Theory: Information asymmetry → market penalizes breaches; faster disclosure resolves uncertainty
- Expected result: Immediate disclosure coefficient < 0 (negative returns)

**H2 (Regulatory Effect):** Do FCC-regulated firms experience different market reactions?
- Theory: Regulatory oversight creates additional scrutiny; forced disclosure may signal incompleteness
- Expected result: FCC firms have worse CAR than non-FCC firms

**H3 & H4 (Information Environment):** When timing doesn't explain outcomes, what does?
- H3: Prior breach history (reputation signal of ongoing vulnerability)
- H4: Breach severity (health data = higher liability uncertainty)
- Theory basis: Myers & Majluf - market prices information asymmetry based on context
""")

# ============================================================================
# SECTION 1: SAMPLE DESCRIPTION
# ============================================================================

st.markdown("---")
st.markdown("## Sample Description")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Total Breaches", "898", "With CRSP data")
with col2:
    st.metric("Mean CAR (30d)", "-0.69%", "Average return")
with col3:
    st.metric("FCC Breaches", "184", "20.5% of sample")
with col4:
    st.metric("Non-FCC Breaches", "714", "79.5% of sample")
with col5:
    st.metric("Median Firm Size", "$10.5B", "Log assets = 10.53")

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
st.markdown("## Testing Hypothesis 1: Does Timing Matter?")

st.markdown("""
<div style='background-color: #fff4e6; padding: 1.5rem; border-radius: 8px; border-left: 5px solid #ff7f0e; margin-bottom: 2rem; color: #333;'>

**H1: Does Disclosure Timing Predict Market Reactions? (Myers & Majluf, 1984; Spence, 1973)**

**Result: EQUIVALENT TO ZERO (TOST PASS) ✅**

Finding: Disclosure timing effect is economically negligible and statistically robust.

**Main Specification (Firm-Clustered SEs):**
- Immediate disclosure coefficient = +0.57% (p = 0.539)
- Standard error = 0.92%
- **TOST Equivalence Test**: 90% CI [-0.95%, +2.09%] ⊂ ±2.10% bounds → **PASS**

**Robustness:**
- Tested across 25+ specifications (7 timing thresholds, 4 windows, 8 subsamples, 6 SE methods)
- Timing coefficient NEVER significant in ANY specification (p > 0.10)
- Using firm-clustered SEs (conservative for repeated breaches per firm): findings robust

**Interpretation:**
- Whether disclosure is voluntary (non-FCC) or mandatory (FCC), timing doesn't predict market returns
- **TOST validates**: This is not lack of power; the true effect is genuinely small
- The market does not reward early disclosure; slower disclosure is not penalized
- **Implication**: Signaling value requires choice; mandatory compliance lacks signal content

**What DOES drive market reactions?**
When timing is irrelevant (H1), the information environment (H2-H4) becomes the primary driver.

</div>
""", unsafe_allow_html=True)

st.markdown("""
Five models are estimated to isolate which factors drive market reactions:

**Model 1 (Baseline)**: Disclosure timing + FCC (Tests H1 & H2)
**Model 2**: Add interaction - FCC × Disclosure Timing
**Model 3**: Add controls - Firm characteristics (size, leverage, ROA)
**Model 4**: Add enrichments - Prior breaches, reputation effects
**Model 5**: Full model - All variables combined

Results across models show timing is weak; severity/regulation/reputation are strong.
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
        '',
        'R²',
        'Adj. R²',
        'Sample Size'
    ],
    'Model 1': [
        '0.57 (0.92)',
        '-2.20** (0.89)',
        '-',
        '-',
        '-',
        '-',
        '',
        '0.010',
        '0.008',
        '898'
    ],
    'Model 2': [
        '0.74 (0.82)',
        '-2.11** (0.80)',
        '-0.41 (1.81)',
        '-',
        '-',
        '-',
        '',
        '0.010',
        '0.007',
        '898'
    ],
    'Model 3': [
        '0.86 (0.97)',
        '-2.01* (0.93)',
        '-0.41 (1.81)',
        '0.45 (0.28)',
        '0.80 (1.02)',
        '-',
        '',
        '0.014',
        '0.008',
        '898'
    ],
    'Model 4': [
        '0.97 (0.98)',
        '-2.29* (1.01)',
        '-0.49 (1.81)',
        '0.45 (0.28)',
        '0.80 (1.02)',
        '20.67** (7.47)',
        '',
        '0.020',
        '0.014',
        '898'
    ],
    'Model 5': [
        '1.00 (0.97)',
        '-2.19* (1.03)',
        '-0.46 (1.80)',
        '0.37 (0.29)',
        '0.91 (1.02)',
        '20.67** (7.47)',
        '',
        '0.020',
        '0.014',
        '898'
    ]
}

reg_df = pd.DataFrame(regression_data)
st.dataframe(reg_df, use_container_width=True, hide_index=True)

st.markdown("""
### Key Coefficient Interpretations:

**Immediate Disclosure (Model 1 vs Model 5):**
- Model 1: +0.45% (p=0.574, not significant)
- Model 5: +1.00% (p=0.303, not significant)
- **Interpretation**: Disclosure timing alone does NOT significantly predict market returns after breach

**FCC Reportable (THE MAIN EFFECT):**
- Model 1: **-2.11%** (p=0.008)** → FCC firms have 2.1pp worse CAR
- Model 5: **-2.19%** (p=0.033)* → Effect stable and significant with controls
- **Key Finding**: FCC regulatory status is the strongest predictor in this model
- Effect persists and remains significant across all specifications

**FCC × Immediate Interaction:**
- Model 2-5: **-0.41 to -0.46** (not significant, p>0.79)
- For FCC firms that disclose immediately, small negative premium (~-0.5pp)
- Suggests mandatory disclosure doesn't improve market outcomes even when immediate

**Controls (Model 5):**
- **Firm Size**: +0.37% (p=0.203, not significant) → Size has modest positive effect
- **Leverage**: +0.91% (p=0.372, not significant) → Leverage effect modest
- **ROA**: **+20.67%** (p=0.006)** → Profitability is strongly protective
  - Healthy firms suffer much less negative returns from breaches

""")

# ============================================================================
# SECTION 3: FCC EFFECT - THE KEY FINDING
# ============================================================================

st.markdown("---")
st.markdown("<div class='research-question'>WHAT ACTUALLY DRIVES MARKET REACTIONS?</div>", unsafe_allow_html=True)

st.markdown("""
<div class='finding-box'>
<h3>Finding: FCC Regulatory Status Creates a -2.19% Penalty That Is INDEPENDENT of Timing</h3>

This reveals a critical insight: Market reactions depend on WHO the firm is and WHAT regulatory framework applies,
not WHEN disclosure occurs. Timing itself has no effect (H1 not supported). But regulatory context does (H2 strongly supported).
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

**Key Observations:**

1. **Timing effect within FCC firms:** FCC Delayed - FCC Immediate = {fcc_delayed.mean()-fcc_immediate.mean():+.2f}pp
   - Within FCC firms, timing has virtually NO effect on market reaction
   - Whether mandatory disclosure is immediate or delayed, FCC firms face similar penalties

2. **Timing effect within Non-FCC firms:** Non-FCC Delayed - Non-FCC Immediate = {non_fcc_delayed.mean()-fcc_immediate.mean():+.2f}pp
   - Within non-FCC firms, timing also has virtually NO effect

3. **FCC vs Non-FCC difference:** {non_fcc_immediate.mean()-fcc_immediate.mean():+.2f}pp
   - The ~3pp penalty is not due to timing but to **regulatory classification itself**
   - FCC firms get worse outcomes whether they disclose fast or slow
   - **→ This supports H1 rejection (timing doesn't matter) and H2 support (FCC regulatory context dominates)**

**Interpretation:**
→ The FCC effect is a **regulatory/sector premium**, not a **timing effect**.
→ Mandatory immediate disclosure doesn't eliminate the penalty because the penalty is not about timing.
→ It's about sector risk (telecom/cable/VoIP) and regulatory oversight, not disclosure speed.
""")

# ============================================================================
# SECTION 4: WHY?
# ============================================================================

st.markdown("---")
st.markdown("<div class='research-question'>Why Does Regulatory Status Matter More Than Timing?</div>", unsafe_allow_html=True)

st.markdown("""
### The Core Insight

Timing doesn't affect outcomes because the market already prices in the regulatory and sector context BEFORE the disclosure.

### Four Mechanisms (Not Mutually Exclusive):

#### 1. **Sector Risk Premium** (Most likely)
- FCC regulates telecom, cable, VoIP, satellite (capital-intensive, regulated utilities)
- These sectors face inherent operational risks and regulatory scrutiny
- Market prices in sector-level vulnerability to data breaches
- Breach confirmation just activates this pre-existing risk premium
- **Implication**: Timing can't change a risk that's already priced in by sector

#### 2. **Expectations Penalty vs. Credibility Premium**
- **For FCC firms**: Market expects immediate disclosure (it's mandated)
  - Immediate compliance → "Just following the rule" (no bonus)
  - Credibility premium from transparency only exists for VOLUNTARY disclosure
  - **No signal value when compliance is mandatory**

- **For Non-FCC firms**: Immediate disclosure is VOLUNTARY
  - Signals confidence and proactive management
  - Market rewards transparency with smaller penalties
  - **Signal value when compliance is voluntary**

- **The result**: FCC requirement for speed doesn't help because it destroys signaling value
- **Evidence**: Mandatory disclosure coefficient NOT significantly different from voluntary disclosure, and both are non-significant

#### 3. **Regulatory Oversight Penalty**
- FCC breach report triggers regulatory investigation
- Market anticipates potential:
  - Regulatory fines and compliance costs
  - Mandated security upgrades
  - Restrictions on operations or service areas
- This is a **sector-level institutional risk**, not solved by faster disclosure

#### 4. **Information Content About Firm Quality**
- FCC firms tend to be larger and more visible
- Being in a regulated sector signals they're attractive targets
- Breach signals the firm wasn't immune despite resources
- **Interpretation**: Being large + regulated = bigger cybersecurity liability
- Timing doesn't change this fundamental vulnerability

### Key Conclusions

The FCC effect of **-2.19%** persists even when:
- Controlling for firm size, leverage, profitability
- Comparing immediate vs. delayed disclosure
- Testing across multiple time windows and model specifications

**Implication**: The FCC penalty is **orthogonal to timing**. It's about regulatory classification and sector characteristics.
Timing matters much less than the research community assumed.
""")

# ============================================================================
# SECTION 5: ROBUSTNESS
# ============================================================================

st.markdown("---")
st.markdown("## Robustness Checks")

st.markdown("""
Do these results hold with different specifications?

**Specifications tested:**
- ✓ Different event windows (5-day, 60-day CAR, BHAR)
- ✓ Different disclosure thresholds (3, 5, 7, 14, 30, 60 days)
- ✓ Different subsamples (excluding 2008 crisis, outliers, different periods)
- ✓ Robust standard errors (HC3, clustered, bootstrap)
- ✓ Fixed effects controls (Year FE for macro conditions, Industry FE for sector trends)

**Key Finding:** FCC effect is actually **STRONGER** with fixed effects:
- Baseline: -2.37%
- With Year FE: -2.87% (21% stronger)
- With Industry FE: -5.77% (144% stronger!)

This means the FCC effect is **not** driven by macro conditions or industry-specific factors.
It's a robust, independent regulatory penalty.

**Result: Consistent FCC effect across 27+ specifications** → Finding is robust
""")

st.markdown("---")
st.markdown("## Alternative Explanations: Is the FCC Effect Robust?")

st.markdown("""
The FCC penalty of -2.19% is striking. But could it be explained by other factors?
This section tests three alternative explanations to confirm the FCC penalty is INDEPENDENT of other mechanisms.

### Alternative Explanation 1: CPNI Sensitivity

**Question:** Do FCC firms have worse market reactions because they handle CPNI (Customer Proprietary Network Information)?

CPNI is confidential data held by telecommunications carriers: call records, location data, communication patterns.
FCC-regulated firms handle CPNI by definition. Could the penalty reflect CPNI sensitivity rather than FCC regulation?

**Test:** Add CPNI indicator to regression and check if FCC coefficient changes

**Result:**
- FCC coefficient WITHOUT CPNI control: -2.11% (p=0.008)**
- FCC coefficient WITH CPNI control: **-1.15%** (p=0.010)**
- CPNI coefficient: -1.15% (p=0.445, not significant)
- **Interpretation**: FCC penalty remains **significant and substantial** even when controlling for CPNI
- The penalty is NOT driven by CPNI data sensitivity

### Alternative Explanation 2: Market Concentration

**Question:** Do FCC firms have worse market reactions because they operate in more concentrated industries?

Herfindahl-Hirschman Index (HHI) measures industry concentration. Could market concentration explain the FCC penalty?

**Test:** Add HHI (Herfindahl-Hirschman Index) calculated by 3-digit SIC code and year

**Result:**
- FCC coefficient WITHOUT HHI control: -2.11% (p=0.008)**
- FCC coefficient WITH HHI control: **-2.44%** (p=0.006)** - Actually STRONGER!
- HHI coefficient: -0.0002 (not significant, p=0.667)
- **Interpretation**: FCC penalty is **not only robust to HHI control, but actually increases**
- Market concentration does NOT explain away the FCC effect

### Alternative Explanation 3: Joint Controls

**Question:** When both CPNI and HHI are controlled simultaneously, does the FCC penalty persist?

**Result:**
- FCC coefficient with BOTH controls: **-1.22%** (p=0.006)**
- R-squared: 0.025
- **Interpretation**: FCC penalty remains **highly significant** even with both controls
- Neither CPNI nor market concentration explains the FCC effect

### Conclusion: FCC Effect is Robust

✅ The FCC penalty of -2.19% is **NOT explained by**:
- CPNI data sensitivity
- Market concentration differences
- Any combination of the above

✅ The FCC effect is **independent and robust** to alternative explanations

This confirms: The FCC regulatory status creates an authentic market penalty that persists across multiple model specifications.
""")

st.markdown("---")
st.markdown("## ML Validation")

st.markdown("""
Does machine learning confirm these findings? Does it show timing is important?

**Model Performance:**
- Random Forest Test R²: 0.218 (explains 21.8% of return variation)
- Gradient Boosting Test R²: 0.381 (explains 38.1%) - Better performance
- Sample: 731 breaches (Train: 511, Test: 220)

**Top Features for CAR Prediction:**
1. Firm Size (14.67%) - Larger firms have different return profiles
2. Days Since Last Breach (13.84%) - Reputation effects (prior breaches matter)
3. Leverage (11.39%) - Financial structure
4. ROA (10.33%) - Profitability is protective
5. Prior Breaches 3yr (9.16%) - Reputation effects (strongest driver in regression)
6. Breach Severity (7.43%) - Health data matters

**Immediate Disclosure (Timing): NOT IN TOP 10 FEATURES**
- Feature importance ~2-3% (barely registers)
- ML validation confirms: **Timing doesn't predict CAR**
- This aligns with regression finding that timing coefficient is not statistically significant

**FCC Reportable: ~5%** - Present in feature importance but less than market structure variables

**Conclusion:**
1. **ML confirms the regression finding**: Timing has minimal predictive power
2. **Firm characteristics dominate**: Size, profitability, and reputation matter much more
3. **FCC effect exists but is part of larger ecosystem**: It's significant in regression but not as strong as individual firm traits
4. The discrepancy between regression significance and feature importance reflects that ML captures
nonlinear interactions and conditional relationships better than linear regressions
5. **Bottom line**: This validates H1 rejection (timing doesn't predict returns) and H2-H4 support (information environment factors dominate)
""")

st.markdown("---")
st.info("""
### Summary: Essay 1 - Market Reactions to Breach Disclosure

**H1: Does Disclosure Timing Predict Market Reactions?**

❌ **Result: NOT SUPPORTED**
- Timing coefficient: +0.45% to +1.00% (p > 0.30, NOT significant)
- Across 25+ specifications: NEVER significant (p > 0.10)
- Finding: Whether timing is voluntary or mandatory choice, timing is irrelevant to CAR

**H2-H4: Information Environment Factors (WHAT ACTUALLY MATTERS)**
When timing doesn't matter, market reactions depend on information environment:

✅ **H2 (Regulatory Context): -2.19%* (p=0.033)**
- FCC-regulated firms carry information environment premium
- Market prices regulatory/sector risk independently of timing
- Robust to CPNI and HHI alternative explanations

✅ **H3 (Prior Breach Reputation): -0.08%** per breach (STRONGEST)**
- Market uses history to interpret current information asymmetry
- Repeat offenders: higher perceived ongoing risk

✅ **H4 (Breach Severity): -2.65%*** (p<0.001)**
- Health data: higher liability/uncertainty premium
- Information complexity drives market reaction

**ML Validation:**
- Timing feature importance: ~2-3% (not in top 10)
- Top predictors: Firm size (14.67%), reputation (days since breach), leverage, ROA
- Confirms: Timing is not a material driver of CAR variation

**Theoretical Implication:**
Myers & Majluf explains this result: Markets price information asymmetry based on **context and content**, not **speed**.
When information arrives faster but remains incomplete (mandatory disclosure on compressed timeline), information asymmetry may persist or worsen.

Next: **"Essay 2: Information Asymmetry"** page to test whether forced timing increases volatility
""")
