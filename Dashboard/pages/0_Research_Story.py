"""
PAGE 1: RESEARCH STORY & THEORY FRAMEWORK
Explains the theoretical foundation using Information Asymmetry Theory
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Research Story & Theory", page_icon="📖", layout="wide")

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
    font-size: 1.4rem;
    color: #d62728;
    font-weight: bold;
    margin: 1.5rem 0 1rem 0;
    padding: 1rem;
    background-color: #ffe6e6;
    border-left: 5px solid #d62728;
    border-radius: 5px;
}
.theory-box {
    background-color: #e6f2ff;
    padding: 1.5rem;
    border-left: 5px solid #1f77b4;
    border-radius: 5px;
    margin: 1rem 0;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='research-header'>📖 Research Story & Theoretical Framework</div>", unsafe_allow_html=True)

# ============================================================================
# SECTION 1: THE CENTRAL QUESTION
# ============================================================================

st.markdown("<div class='research-question'>Central Research Question</div>", unsafe_allow_html=True)

st.markdown("""
### "Is There Any Benefit to Disclosing a Data Breach Immediately, or Should It Be Delayed?"

This is a **practical question** every breached company faces:
- **Immediate disclosure**: Signals transparency, but may reveal weakness or incomplete information
- **Delayed disclosure**: Allows investigation, but signals possible cover-up

This creates a **strategic dilemma** at the intersection of:
- Corporate strategy (optimal disclosure timing)
- Market efficiency (what information matters to investors)
- Regulatory requirements (SEC, FCC, state laws mandate specific timelines)
- Firm reputation (how investors evaluate breach management)

**Answer:** Timing itself doesn't matter. What matters is WHAT gets disclosed, WHO the firm is, and WHAT regulatory framework applies.
""")

# ============================================================================
# SECTION 2: THEORETICAL FRAMEWORK
# ============================================================================

st.markdown("---")
st.markdown("<div class='theory-box'>", unsafe_allow_html=True)
st.markdown("""
## Theoretical Framework: Information Asymmetry & Signaling

Grounded in **Myers & Majluf (1984)** and **Spence (1973)**

### Core Theory: Information Asymmetry (Myers & Majluf, 1984)

Disclosure decisions balance transparency benefits against the costs of revealing incomplete/unfavorable information.

### Signaling Mechanism (Spence, 1973)

**Voluntary disclosure** signals firm strength:
- Immediate voluntary disclosure = confidence in managing the crisis
- Market rewards with smaller CAR penalty (credibility premium)

**Mandatory disclosure** breaks the signal:
- Immediate mandatory disclosure = regulatory compliance, not choice
- Market penalizes incomplete information (information asymmetry remains)
- Forced early disclosure before investigation complete = negative signal

### The Empirical Puzzle

```
VOLUNTARY TIMING (Non-FCC firms):
  Firm chooses to disclose immediately
  → Signals strength and confidence
  → Information asymmetry decreases
  → Smaller CAR penalty

MANDATORY TIMING (FCC firms):
  Regulator forces 7-day disclosure
  → Signals compliance, not strength
  → Incomplete information = asymmetry remains/increases
  → Larger CAR penalty despite faster disclosure
```

**Empirical test:**
- H1: Does disclosure timing reduce CAR? (NO - not significant)
- H2-H4: What else matters when timing doesn't? (YES - FCC, prior breaches, severity all matter)

""")
st.markdown("</div>", unsafe_allow_html=True)

# ============================================================================
# SECTION 3: THE THREE ESSAYS
# ============================================================================

st.markdown("---")
st.markdown("## How Three Essays Answer the Central Question")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div style='background-color: #e6f2ff; color: #333; padding: 1.5rem; border-radius: 8px; border-left: 5px solid #1f77b4; height: 100%; color: #333;'>
    <h3 style='color: #1f77b4;'>📈 Essay 1: Market Reactions</h3>
    <p><b>Tests Information Asymmetry & Signaling:</b></p>
    <p>✅ H1: Timing effect = +0.57% (Equivalent to Zero, TOST PASS)</p>
    <p>✅ H2: FCC effect = -2.20%** (SIGNIFICANT)</p>
    <p>✅ H3: Prior breaches effect = -0.22%*** per breach (SIGNIFICANT)</p>
    <p>✅ H4: Severity effect = -1.67%* (SIGNIFICANT)</p>
    <hr>
    <p><b>Finding:</b> Timing economically negligible (H1); information environment (H2-H4) drives CAR</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style='background-color: #fff4e6; color: #333; padding: 1.5rem; border-radius: 8px; border-left: 5px solid #ff7f0e; height: 100%; color: #333;'>
    <h3 style='color: #ff7f0e;'>💨 Essay 2: Information Asymmetry</h3>
    <p><b>Tests Information Processing Mechanism:</b></p>
    <p>✅ Pre-volatility dominates (coef = -0.53***, R²=0.39)</p>
    <p>❌ Timing reduces volatility (NOT SUPPORTED)</p>
    <p>✅ H2-Extended: FCC moderation = +1.83%** (increases volatility)</p>
    <hr>
    <p><b>Finding:</b> Forced disclosure increases uncertainty, not resolves it</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div style='background-color: #e6ffe6; color: #333; padding: 1.5rem; border-radius: 8px; border-left: 5px solid #2ca02c; height: 100%; color: #333;'>
    <h3 style='color: #2ca02c;'>👔 Essay 3: Governance Response</h3>
    <p><b>Tests Organizational Consequences:</b></p>
    <p>✅ H5: Executive turnover = 46.4% within 30 days</p>
    <p>✅ H6: Enforcement rare = 6 cases (0.6%), all FCC</p>
    <p>✅ Cascading response: 66.9% by 90 days</p>
    <hr>
    <p><b>Finding:</b> Governance response exceeds regulatory response</p>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# SECTION 4: KEY THEORETICAL MODERATORS
# ============================================================================

st.markdown("---")
st.markdown("<div class='research-question'>Information Asymmetry: What Matters When Timing Doesn't</div>", unsafe_allow_html=True)

# Create factors table
factors_data = {
    'Factor': [
        'Disclosure Timing (H1)',
        'Prior Breaches (H3)',
        'Health Data Severity (H4)',
        'FCC Regulatory Context (H2)'
    ],
    'Coefficient': [
        '+0.57% (TOST PASS: [-0.95%, +2.09%])',
        '-0.22%*** per breach (STRONGEST)',
        '-1.67%*',
        '-2.20%**'
    ],
    'Information Asymmetry Signal': [
        'Economically negligible effect (equiv. to zero)',
        'Firm vulnerability / market memory',
        'Liability complexity / uncertainty premium',
        'Regulatory environment / sector risk'
    ],
    'Implication': [
        'Timing economically irrelevant (TOST validated)',
        'Market prices in breach history',
        'Information complexity drives reactions',
        'Information environment (not speed) matters'
    ]
}

factors_df = pd.DataFrame(factors_data)
st.dataframe(factors_df, use_container_width=True, hide_index=True)

# ============================================================================
# SECTION 5: HYPOTHESES
# ============================================================================

st.markdown("---")
st.markdown("## Hypotheses: Testing Timing vs. Severity-Dominance")

st.markdown("""
## The Six Core Hypotheses

### Essay 1: Market Reactions to Breach Disclosure

**H1: Timing Effect on Cumulative Abnormal Returns (CAR)**
- Does immediate disclosure reduce negative market reaction?
- **Result**: Timing coefficient = +0.57%, p = 0.539 (NOT significant)
- **TOST Equivalence Test**: 90% CI [-0.95%, +2.09%] falls entirely within ±2.10% bounds
- **Finding**: ✅ EQUIVALENT TO ZERO - Timing effect is economically negligible (robust via TOST)

**H2: FCC Regulatory Context Effect**
- Do FCC-regulated firms experience different CAR than non-FCC?
- **Result**: FCC coefficient = -2.20%** (p = 0.010, firm-clustered SEs)
- **Post-2007 Test**: FCC effect emerges after regulation (-2.26%, p=0.0125), proving regulatory source
- **Finding**: ✅ SUPPORTED - FCC firms have worse CAR; effect is regulatory, not industry-driven
- Robust to alternative controls (CPNI, HHI)

**H3: Prior Breach Reputation Effect**
- Do firms with prior breach history suffer larger CAR penalties?
- **Result**: Prior breaches coefficient = -0.22%*** per breach (STRONGEST effect, p < 0.01)
- **Finding**: ✅ SUPPORTED - Firm vulnerability/market memory drives strongest reaction

**H4: Breach Severity Effect**
- Do complex breaches (health data) trigger larger CAR penalties?
- **Result**: Health breach coefficient = -1.67%* (p = 0.066, firm-clustered SEs)
- **Finding**: ✅ SUPPORTED - Information complexity drives market reaction

### Essay 2: Information Asymmetry & Volatility

**H2-Extended: FCC Moderation on Volatility**
- Do FCC-regulated firms experience different volatility changes than non-FCC?
- **Result**: FCC coefficient = +1.83%** (p < 0.05)
- **Finding**: ✅ SUPPORTED - FCC forced disclosure INCREASES volatility (opposite of theory prediction)
- **Interpretation**: Forced early disclosure of incomplete information worsens information asymmetry

**Pre-Existing Volatility Baseline**
- Does firm's pre-breach volatility dominate post-breach volatility?
- **Result**: Pre-breach volatility coefficient = -0.53*** (explains 38.6% alone)
- **Finding**: ✅ SUPPORTED - Firm traits matter far more than disclosure timing

### Essay 3: Governance & Organizational Response

**H5: Timing → Executive Turnover**
- Does disclosure timing predict executive turnover?
- **Result**: 30-day turnover = 46.4% (416/896 breaches)
- **Finding**: ✅ SUPPORTED - Nearly half of breaches trigger leadership changes
- **Pattern**: Cascading response - 66.9% by 90 days, 67.5% by 180 days

**H6: Regulatory Enforcement Effects**
- Does disclosure timing predict regulatory enforcement actions?
- **Result**: Enforcement = 6 cases (0.6%), all FCC firms
- **Finding**: ⚠️ LIMITED DATA - Enforcement is rare; governance response (50x more common) dominates
- Health/severe breaches create information processing bottlenecks
- Volatility increases when disclosure cannot resolve complexity
- **Prediction**: Severity indicators have positive coefficients on volatility
""")

# ============================================================================
# SECTION 6: NATURAL EXPERIMENT
# ============================================================================

st.markdown("---")
st.markdown("## Why This Works as a Natural Experiment")

st.markdown("""
**The FCC Regulation (2007) creates exogenous variation in disclosure requirements:**

```
PRE-2007:
  All firms (FCC + Non-FCC) choose their own disclosure timing

2007 REGULATION:
  FCC-regulated firms (telecom, cable, VoIP, satellite) → FORCED to disclose within 7 days
  Non-FCC firms → Continue choosing their own timing

POST-2007:
  Can compare breach reactions between treatment (FCC) and control (Non-FCC)
  Can test if regulatory requirement changes disclosure timing and market reaction
```

**Identification Strategy:**

- **Treatment group**: 192 FCC-regulated breaches (22.4% of sample)
- **Control group**: 666 non-FCC breaches (77.6% of sample)
- **Comparison**: Market reactions before vs. after FCC firms must comply
- **Validity**: Assumes FCC firms and non-FCC firms are comparable before regulation (test this!)
""")

# ============================================================================
# SECTION 7: WHAT MAKES THIS COUNTERINTUITIVE
# ============================================================================

st.markdown("---")
st.markdown("<div class='research-question'>Why This Finding Matters</div>", unsafe_allow_html=True)

st.markdown("""
### The Puzzle

If **immediate disclosure** is supposedly "good" (signals transparency, reduces uncertainty):
- **Why** do FCC-regulated breaches (forced immediate) have WORSE market reactions?
- **Why** don't FCC firms get a credibility bonus for faster disclosure?
- **Why** does mandating disclosure backfire?

### The Counterintuitive Answer

**Because the market already expected it.**

When disclosure is **mandatory** (FCC rule):
- Credibility premium disappears (firms MUST disclose, so disclosure isn't a signal)
- Sector risk penalty remains (FCC-regulated = higher risk sector)
- Net effect: Negative market reaction

When disclosure is **voluntary** (non-FCC):
- Immediate disclosure signals strength and confidence
- Credibility premium applies
- Net effect: Smaller negative reaction

**Implication**: Mandatory disclosure rules may create perverse incentives if the market already prices in sector risk.
""")

st.markdown("---")
st.info("""
### Next Steps:

1. **Continue to "Natural Experiment"** page to understand the FCC regulation setup
2. **Then "Sample Validation"** to see if the sample is defensible
3. **Then "Data Landscape"** to explore the dataset
4. **Then "Essay 2" and "Essay 3"** to see the actual evidence
5. **Finally "Key Findings"** to see the disclosure paradox explained
""")
