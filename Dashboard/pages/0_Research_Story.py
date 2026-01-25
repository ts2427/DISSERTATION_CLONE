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

**Answer:** Timing itself doesn't matter. What matters is WHAT you disclose, WHO you are, and WHAT regulatory framework you operate under.
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
- H1a: Does voluntary timing reduce CAR?
- H1b: Does mandatory timing fail to reduce CAR (despite being faster)?
- H2-H4: What else matters when timing doesn't?

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
    <h3 style='color: #1f77b4;'>Essay 1: Theory</h3>
    <p><b>Develops competing theories:</b></p>
    <p>🕐 Timing Hypothesis: Speed matters</p>
    <p>📋 Severity-Dominance: Content matters</p>
    <hr>
    <p><b>Question:</b> Which theory fits the data?</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style='background-color: #fff4e6; color: #333; padding: 1.5rem; border-radius: 8px; border-left: 5px solid #ff7f0e; height: 100%; color: #333;'>
    <h3 style='color: #ff7f0e;'>Essay 2: Market Reactions</h3>
    <p><b>Tests Information Asymmetry:</b></p>
    <p>❌ H1a: Voluntary timing signals strength (NOT SUPPORTED)</p>
    <p>✅ H1b: Mandatory timing lacks signal value (NOT SIGNIFICANT)</p>
    <hr>
    <p><b>Finding:</b> Timing irrelevant; information environment (regulation, reputation, severity) drives CAR</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div style='background-color: #e6ffe6; color: #333; padding: 1.5rem; border-radius: 8px; border-left: 5px solid #2ca02c; height: 100%; color: #333;'>
    <h3 style='color: #2ca02c;'>Essay 3: Volatility</h3>
    <p><b>Tests 3 hypotheses:</b></p>
    <p>✅ H5: Pre-volatility dominates (R²=0.39)</p>
    <p>❌ H6: Timing reduces volatility (NOT SUPPORTED)</p>
    <hr>
    <p><b>Finding:</b> Firm traits matter more than timing</p>
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
        '+0.45% to +1.00% (NOT SIG, p>0.30)',
        '-0.08%** per breach (STRONGEST)',
        '-2.65%***',
        '-2.19%*'
    ],
    'Information Asymmetry Signal': [
        'Mandatory compliance ≠ signal of strength',
        'Firm vulnerability / history signals risk',
        'Liability complexity / uncertainty premium',
        'Regulatory environment / sector risk'
    ],
    'Implication': [
        'Timing lacks signaling value when mandatory',
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
### Essay 2 Hypotheses: Information Asymmetry Framework (Myers & Majluf, 1984)

**H1a: Voluntary Disclosure Signals Strength** (Spence Signaling)
- When firms voluntarily disclose immediately → signals confidence managing crisis
- Information asymmetry decreases
- **Prediction**: For voluntary disclosures, timing coefficient < 0 (p < 0.05)

**H1b: Mandatory Disclosure Lacks Signaling Value**
- When regulation forces immediate disclosure → compliance doesn't equal confidence
- Information asymmetry may persist (incomplete information on compressed timeline)
- **Prediction**: For mandatory disclosures, timing coefficient = 0 (not significant)

**Secondary Factors (What Matters When Timing Doesn't):**

**H2: Regulatory Context Affects Information Environment**
- FCC-regulated firms operate in higher-scrutiny environment
- Market prices in regulatory risk independently of timing
- **Prediction**: FCC coefficient ≠ 0 (captures information environment effect)

**H3: Prior Breach Reputation Signals Vulnerability**
- Firms with prior breach history signal higher ongoing risk
- Market adjusts information asymmetry interpretation based on history
- **Prediction**: Prior breaches coefficient ≠ 0

**H4: Breach Severity Affects Information Asymmetry**
- Health data breaches carry higher uncertainty about damages/liability
- Greater information asymmetry around complexity and cost
- **Prediction**: Health breach severity coefficient ≠ 0

### Essay 3 Hypotheses: Testing Information Processing Mechanism

**H5: Pre-Existing Uncertainty Dominates** (Information Processing Capacity)
- Firm's pre-breach volatility reflects information processing baseline
- Post-breach volatility anchors to this pre-existing level
- **Prediction**: Pre-breach volatility coefficient > 0, large effect (R² ~0.40)

**H6: Mandatory Timing Doesn't Resolve Information Asymmetry**
- Immediate mandatory disclosure doesn't reduce post-breach volatility
- Market remains uncertain because disclosure is forced (incomplete information signal)
- **Prediction**: For mandatory disclosure, timing coefficient = 0 (not significant)

**H7: Information Complexity Increases Uncertainty** (Tushman & Nadler, 1978)
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
- Credibility premium disappears (you HAVE to disclose, so it's not a signal)
- Sector risk penalty remains (you're FCC-regulated = higher risk sector)
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
3. **Then "Data Landscape"** to see what we're analyzing
4. **Then "Essay 2" and "Essay 3"** to see the actual evidence
5. **Finally "Key Findings"** to see the FCC Paradox explained
""")
