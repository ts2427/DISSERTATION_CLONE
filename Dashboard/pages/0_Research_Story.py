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
### "Is There Any Benefit to Disclosing a Data Breach Immediately?"

This is a **practical question** every breached company faces:
- **Immediate disclosure**: Signals transparency, reduces uncertainty, but may reveal weakness
- **Delayed disclosure**: Allows investigation and remedy planning, but signals possible cover-up

This creates a **strategic dilemma** at the intersection of:
- Corporate strategy (optimal disclosure timing)
- Information asymmetry theory (market uncertainty)
- Regulatory requirements (FCC rule: 7-day mandatory disclosure)
""")

# ============================================================================
# SECTION 2: THEORETICAL FRAMEWORK
# ============================================================================

st.markdown("---")
st.markdown("<div class='theory-box'>", unsafe_allow_html=True)
st.markdown("""
## Theoretical Foundation: Information Asymmetry Theory

**Myers & Majluf (1984) Framework:**

When managers possess **private information** (breach severity, scope, potential liability)
that markets lack, **disclosure timing becomes a signal** about information quality.

### The Signaling Mechanism

```
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│  BREACH OCCURS                                               │
│  ↓                                                            │
│  Manager knows: Severity, scope, impact, future liability    │
│  Market knows: Only that breach happened                     │
│  ↓                                                            │
│  DISCLOSURE TIMING DECISION                                  │
│  ├─ Immediate (≤7 days): "We're handling this quickly"      │
│  └─ Delayed (>30 days): "We're investigating thoroughly"    │
│  ↓                                                            │
│  MARKET INTERPRETS                                           │
│  ├─ Credibility signal: "Immediate = transparent"           │
│  ├─ Adverse selection: "Delayed = bad news coming"          │
│  └─ Regulatory signal: "FCC-required = sector risk"         │
│  ↓                                                            │
│  MARKET REACTION                                             │
│  ├─ Cumulative Abnormal Returns (CAR) = stock price impact  │
│  └─ Volatility change = uncertainty reduction               │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

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
    <h3 style='color: #1f77b4;'>Essay 1: Theory & Setup</h3>
    <p><b>Develops theoretical framework</b> predicting when immediate vs. delayed disclosure is optimal.</p>
    <p>Tests moderating factors to identify boundary conditions.</p>
    <hr>
    <p><b>Key Question:</b> When does timing matter?</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style='background-color: #fff4e6; color: #333; padding: 1.5rem; border-radius: 8px; border-left: 5px solid #ff7f0e; height: 100%; color: #333;'>
    <h3 style='color: #ff7f0e;'>Essay 2: Market Reactions</h3>
    <p><b>Event study</b> examining stock price reactions to breach disclosure.</p>
    <p>Uses Cumulative Abnormal Returns (CAR) as outcome measure.</p>
    <hr>
    <p><b>Key Finding:</b> Market penalties vary dramatically by context</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div style='background-color: #e6ffe6; color: #333; padding: 1.5rem; border-radius: 8px; border-left: 5px solid #2ca02c; height: 100%; color: #333;'>
    <h3 style='color: #2ca02c;'>Essay 3: Mechanism</h3>
    <p><b>Volatility analysis</b> revealing mechanism linking timing to reactions.</p>
    <p>Tests information asymmetry theory using volatility change as proxy.</p>
    <hr>
    <p><b>Key Finding:</b> Pre-breach volatility dominates explanation</p>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# SECTION 4: KEY THEORETICAL MODERATORS
# ============================================================================

st.markdown("---")
st.markdown("<div class='research-question'>Key Factors That Determine Optimal Disclosure Timing</div>", unsafe_allow_html=True)

# Create moderator table
moderators_data = {
    'Factor': [
        'FCC Regulation',
        'Prior Breaches',
        'Health Data',
        'Executive Turnover',
        'Regulatory Action'
    ],
    'Mechanism': [
        'Mandatory 7-day disclosure rule (2007)',
        'Repeat offender learning effect',
        'HIPAA compliance costs',
        'Accountability/governance signal',
        'Legal closure/settlement'
    ],
    'Predicted Effect': [
        'Expectations penalty → MORE negative CAR',
        'Repeat offender penalty → LESS negative CAR',
        'Higher compliance costs → MORE negative CAR',
        'Governance failure signal → MORE negative CAR',
        'Legal certainty → LESS negative CAR'
    ],
    'Theoretical Explanation': [
        'Market expects compliance; no credibility premium; sector risk penalty',
        'Learning: firm has experience managing breaches',
        'Health data involves higher liability costs',
        'Executive change signals accountability for failure',
        'Enforcement resolves uncertainty; market can price in costs'
    ]
}

moderators_df = pd.DataFrame(moderators_data)
st.dataframe(moderators_df, use_container_width=True, hide_index=True)

# ============================================================================
# SECTION 5: HYPOTHESES
# ============================================================================

st.markdown("---")
st.markdown("## Hypotheses to Test in Essays 2 & 3")

st.markdown("""
### Essay 2 Hypotheses (Market Reactions):

**H1 (Main Effect):**
- Immediate disclosure: Should reduce CAR (credibility signal beats adverse selection)
- Delayed disclosure: Should worsen CAR (adverse selection signal)

**H2 (FCC Moderation) - THE KEY HYPOTHESIS:**
- Non-FCC immediate: Positive effect (credibility premium)
- FCC immediate: Negative effect (expectations penalty dominates)
- **Why?** Mandatory disclosure removes credibility premium but adds sector risk

**H3-H6 (Additional Moderators):**
- Prior breaches: Repeat offenders get smaller penalty (learning effect)
- Health data: Additional penalty due to HIPAA liability
- Executive turnover: Additional penalty (signals failure)
- Regulatory enforcement: Actually reduces penalty (legal closure)

### Essay 3 Hypotheses (Information Asymmetry):

**H1 (Volatility Mechanism):**
- Immediate disclosure reduces post-breach volatility (resolves uncertainty)
- Delayed disclosure maintains higher volatility (prolonged uncertainty)
- **BUT:** If H2 holds, volatility reduction doesn't translate to better CAR for FCC

**H2 (Pre-breach Volatility):**
- Pre-existing volatility dominates post-breach volatility
- This is a control variable but critical for understanding heterogeneity
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
2. **Then "Sample Validation"** to see if our sample is defensible
3. **Then "Data Landscape"** to see what we're analyzing
4. **Then "Essay 2" and "Essay 3"** to see the actual evidence
5. **Finally "Key Findings"** to see the FCC Paradox explained
""")
