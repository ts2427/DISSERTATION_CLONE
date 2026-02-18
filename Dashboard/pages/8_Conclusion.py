"""
PAGE 9: CONCLUSION - THREE-ESSAY SYNTHESIS
Wraps up the complete dissertation: Market reactions → Information asymmetry → Governance response
What we found, why it matters, what it means for policy and practice
"""

import streamlit as st
import pandas as pd

st.set_page_config(page_title="Conclusion: Three-Essay Synthesis", page_icon="🎯", layout="wide")

st.markdown("""
<style>
.conclusion-header {
    font-size: 2.5rem;
    font-weight: bold;
    color: #d62728;
    text-align: center;
    padding: 1rem 0;
    margin-bottom: 2rem;
    border-bottom: 3px solid #d62728;
}
.finding-summary {
    background-color: #e6f2ff;
    padding: 1.5rem;
    border-left: 5px solid #1f77b4;
    border-radius: 5px;
    margin: 1rem 0;
    color: #333;
}
.finding-summary p, .finding-summary li, .finding-summary h3, .finding-summary span, .finding-summary h2, .finding-summary b {
    color: inherit;
}
.implication-box {
    background-color: #fff4e6;
    padding: 1.5rem;
    border-left: 5px solid #ff7f0e;
    border-radius: 5px;
    margin: 1rem 0;
    color: #333;
}
.implication-box p, .implication-box li, .implication-box h3, .implication-box span {
    color: #333 !important;
}
.research-contribution {
    background-color: #e6ffe6;
    padding: 1.5rem;
    border-left: 5px solid #2ca02c;
    border-radius: 5px;
    margin: 1rem 0;
    color: #333;
}
.research-contribution p, .research-contribution li, .research-contribution h3, .research-contribution span {
    color: #333 !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='conclusion-header'>⏰ Conclusion: Timing is Irrelevant; Severity, Reputation, and Regulation Matter</div>", unsafe_allow_html=True)

# ============================================================================
# SECTION 1: EXECUTIVE SUMMARY
# ============================================================================

st.markdown("---")
st.markdown("## Executive Summary")

st.markdown("""
<div class='finding-summary'>
<h3 style='color: inherit;'>Testing Information Asymmetry Theory (Myers & Majluf, 1984; Spence, 1973)</h3>

<b>The Central Finding Across Three Essays:</b>

<b>Essay 1 (Market Reactions):</b> <b style='color: #d62728;'>Timing is irrelevant to market reactions</b>
- Result: Timing coefficient = +0.57% (p = 0.539); markets care about firm characteristics, not disclosure speed
- Robustness: Tested across 25+ specifications; timing never significant (p > 0.10 in ANY spec)
- All other timing thresholds (3, 5, 7, 14, 30, 60 days) also NOT significant

<b>What DOES predict market reactions (H2-H4):</b>
- <b>H3 (Reputation):</b> Prior breach history → -0.22%*** per breach (STRONGEST effect, firm-clustered SEs)
- <b>H4 (Severity):</b> Health data → -1.67%* (p = 0.066, firm-clustered SEs)
- <b>H2 (Regulation):</b> FCC status → -2.20%** (p = 0.010, post-2007 test validates regulatory effect)

<b>Essay 2 (Information Asymmetry):</b> <b style='color: #d62728;'>Forced disclosure INCREASES volatility, not decreases it</b>
- Pre-breach volatility dominates (coefficient = -0.53***, explains 38.6% of variance)
- H2-Extended (FCC moderation on volatility): +1.83%** (p < 0.05) - FCC firms have HIGHER post-disclosure volatility
- Interpretation: Forced early disclosure of incomplete information worsens information asymmetry

<b>Essay 3 (Governance Response):</b> <b style='color: #d62728;'>46.4% of breaches trigger executive turnover within 30 days</b>
- H5: Executive turnover = 416/896 breaches with 30-day leadership changes
- H6: Regulatory enforcement rare = 6 cases (0.6%), all FCC
- Pattern: Governance response (50x more common than enforcement) dominates

<b>Theory Interpretation:</b> Myers & Majluf correctly predicts that markets price **information asymmetry** (what is known, who the firm is, what regulatory context applies), not **information speed** (how fast facts arrive).

<b>Why This Matters:</b> Regulators and policymakers assume "faster disclosure = better transparency = better outcomes."
This study shows: (1) Faster timing has no benefit when forced by regulation, (2) Information quality matters more than speed, (3) Forced early disclosure may worsen outcomes by creating incomplete/uncertain information signal.
</div>
""", unsafe_allow_html=True)

# ============================================================================
# SECTION 2: RESEARCH APPROACH
# ============================================================================

st.markdown("---")
st.markdown("## Research Approach and Methodology")

st.markdown("""
### The Research Journey

**Phase 1: Motivation (Why this question?)**
- Prior literature: "Faster disclosure = better outcomes" (assumed)
- Reality: Many companies disclose strategically, not immediately
- Gap: What if forced speed damages information quality?

**Phase 2: Natural Experiment (How to test causality?)**
- 2007 FCC regulation creates exogenous variation
- Before 2007: FCC and non-FCC firms chose disclosure timing freely
- After 2007: FCC firms forced to disclose within 7 days; non-FCC still free
- Result: Pseudo-randomized treatment assignment (natural experiment)

**Phase 3: Sample Validation (Is the sample defensible?)**
- 1,054 total breaches → 926 with stock market data (Essay 2)
- Attrition is explained: need CRSP stock prices
- Excluded breaches: mostly smaller, private firms
- Key test: Disclosure timing doesn't predict exclusion (not selection bias on main predictor)
- Conclusion: Results apply to publicly-traded firms, not universally

**Phase 4: Essay 1 Analysis (What are the market effects?)**
- Dependent variable: Cumulative Abnormal Returns (CAR) at 30-day window
- Method: OLS with firm controls, firm-clustered standard errors (main specification)
- Main findings:
  - H1 (Timing coefficient): +0.57% (p=0.539) - timing is irrelevant; markets reward firm characteristics, not speed
  - H2 (FCC coefficient): -2.20%** (p=0.010) - regulatory effect validated via post-2007 test, robust to CPNI and HHI
  - H3 (Prior breaches): -0.22%*** per breach (STRONGEST effect, p<0.001)
  - H4 (Health breach): -1.67%* (p=0.066)
  - ROA coefficient: +20.53%** (p=0.006) - profitability protective
- Robustness: Held across 25+ specifications (7 timing thresholds, 4 windows, 8 subsamples, 6 SE methods)

**Phase 5: Essay 2 Analysis (What's the mechanism?)**
- Mechanism hypothesis: Information asymmetry (measured by post-disclosure volatility)
- Why volatility?: High volatility = market uncertainty; low volatility = resolved uncertainty
- Main findings:
  - Pre-breach volatility: -0.53*** coefficient (explains 38.6% of post-breach volatility alone)
  - Immediate disclosure: 1.30 (NOT significant, p > 0.10) - faster disclosure doesn't reduce uncertainty
  - H2-Extended (FCC moderation): +1.83%** (p < 0.05) - FCC firms have HIGHER volatility despite mandatory immediate disclosure
  - R-squared: 0.3933 (Model 3)
- Interpretation: Forced early disclosure INCREASES uncertainty; firm-level traits dominate

**Phase 6: Essay 3 Analysis (What's the organizational response?)**
- Dependent variables: Executive turnover (binary, multiple time windows), enforcement (binary)
- Main findings:
  - H5: 30-day turnover = 46.4% (416/896 breaches)
  - 90-day turnover = 66.9% (599/896 breaches)
  - 180-day turnover = 67.5% (605/896 breaches)
  - H6: Enforcement = 6 cases (0.6%), all FCC firms
  - Executive turnover is ~50x more common than regulatory enforcement
- Interpretation: Governance response (board/investor pressure) exceeds regulatory response

**Phase 7: Synthesis (What's the big picture?)**
- Central insight: Timing has NO effect on market reactions or volatility; severity/reputation/regulation DO
- All three essays show timing irrelevance in different contexts (returns, uncertainty, governance)
- FCC effect persists across all three essays (stronger market reaction, higher volatility, not different turnover)
- Market correctly interprets that firm quality, breach content, and regulatory context matter more than disclosure speed
- Result: Timing regulations don't improve outcomes; forced early disclosure may worsen them (information quality ≠ information speed)

**Phase 7: Validation (Do the findings hold up?)**
- Robustness checks: Different windows, specifications, subsamples → All consistent
- ML validation: Random Forest models confirm FCC matters for both CAR and volatility
- Alternative explanations: Ruled out (sector risk, breach severity, firm characteristics)
- Conclusion: Finding is robust and not easily explained by confounds
""")

# ============================================================================
# SECTION 3: CONTRIBUTIONS TO LITERATURE
# ============================================================================

st.markdown("---")
st.markdown("## Contributions to Research")

st.markdown("""
<div class='research-contribution'>
<h3 style='color: inherit;'>What This Adds to the Literature</h3>

**1. Information Asymmetry in Regulatory Context**
- Extends Myers & Majluf (1984) to disclosure regulation
- Shows that forced disclosure can backfire when information is incomplete
- Contributes to understanding when regulations help vs. hurt

**2. Disclosure Timing as Strategic Choice**
- Challenges assumption that "faster is always better"
- Shows credibility comes from exceeding expectations, not meeting mandates
- Contributes to behavioral economics of disclosure

**3. Empirical Evidence on FCC Regulation (2007)**
- First systematic study of whether FCC 7-day rule achieves intended effects
- Documents unintended consequence: worse market reactions
- Contributes to regulatory impact assessment literature

**4. Event Study Methodology During Crises**
- Demonstrates importance of controlling for confounds in crisis periods (2008 financial crisis happened post-2007)
- Shows why time-aware cross-validation matters for ML validation
- Contributes to methodological guidance for financial event studies

**5. Natural Experiment Design**
- Shows how regulatory changes create credible causal identification
- Demonstrates parallel trends testing and pre-treatment balance
- Contributes to program evaluation methods in corporate finance
</div>
""", unsafe_allow_html=True)

# ============================================================================
# SECTION 4: POLICY IMPLICATIONS
# ============================================================================

st.markdown("---")
st.markdown("## What This Means for Policy")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### For Regulators (FCC, SEC, State Attorneys General)

    **Key Insight:**
    Disclosure timing can be mandated, but information completeness cannot.

    **Current Approach:**
    - Focus on speed: 7-day, 30-day, 60-day rules
    - Implicit assumption: Faster = more transparency = better

    **Evidence Shows:**
    - Forced speed can reduce information quality
    - Market penalizes companies that disclose before investigation complete
    - Result: Regulation doesn't achieve intended effect

    **Key Policy Insight:**
    Stock market discipline does not operate through disclosure timing. This explains why voluntary rapid disclosure remains rare despite regulatory pressure—it provides no market benefit over delayed complete disclosure.

    **Recommendation (Bounded):**
    Rather than mandating faster disclosure, focus on:
    - **Governance mechanisms** (board oversight, breach investigation quality)
    - **Data type protections** (heightened scrutiny for health/financial data)
    - **Firm capacity** (encourage cybersecurity investment and incident response capabilities)

    Speed alone doesn't reduce information asymmetry; information quality does. Current timing mandates may be well-intentioned but don't achieve stated regulatory goals (based on stock market evidence).

    **Note:** These findings apply to stock market reactions. Other regulatory goals (consumer protection, government oversight) may justify timing rules even if stock market doesn't reward them.
    """)

with col2:
    st.markdown("""
    ### For Companies (Disclosure Strategy)

    **Key Insight:**
    Credibility premium comes from beating expectations, not meeting mandates.

    **Current Practice (Many Firms):**
    - Wait until required to disclose
    - Disclose minimum required details
    - Hope market reacts mildly

    **Evidence Shows:**
    - Voluntary early disclosure helps (Non-FCC +1.43% CAR)
    - Forced disclosure hurts (FCC -1.62% CAR)
    - Market distinguishes voluntary vs. mandatory

    **Recommended Changes:**
    1. **Strategic Disclosure Timing**
       - If breach is contained and severity clear: disclose early (beat expectations)
       - If breach is ongoing or severity uncertain: wait for complete investigation
       - Don't disclose just because you must; disclose because you're ready

    2. **Information Completeness**
       - When you do disclose, provide COMPLETE information
       - Preliminary disclosures with investigation updates = worse than waiting
       - One good disclosure > multiple partial updates

    3. **Communications Strategy**
       - Frame disclosure as confidence (clear investigation outcomes)
       - Frame delay as thoroughness (proper investigation completed)
       - Market rewards "disclosure done right" more than "disclosure done fast"

    4. **Investor Relations**
       - Brief investors before public disclosure if allowed
       - Explain investigation timeline upfront
       - Signal that delays are about completeness, not cover-up
    """)

# ============================================================================
# SECTION 5: BUSINESS IMPLICATIONS
# ============================================================================

st.markdown("---")
st.markdown("## What This Means for Business")

st.markdown("""
<div class='implication-box'>
<h3 style='color: inherit;'>Implications for Corporate Strategy</h3>

**1. Cyber Security Investment**
- Data breach disclosure is now material event (affects stock price)
- Prevention is far cheaper than managing breach response
- FCC-regulated firms especially vulnerable to market reaction
- Strong cyber security = crisis prevention = value protection

**2. Crisis Communications**
- Traditional PR wisdom: "Get ahead of story, communicate early"
- Finding: "Get ahead of story, but only when you have complete information"
- New wisdom: "Be first with complete information, not first with incomplete"
- Implications: Invest in rapid investigation capability, not just rapid communication

**3. Insurance and Risk Management**
- Cyber liability insurance premiums may increase post-breach
- Insurance carriers understand market reaction
- Companies with worse CAR may face higher future premiums
- Prevention ROI: 1 breach avoided = major premium savings + stock price protection

**4. Regulatory Compliance**
- Compliance with 7-day rule is necessary but not sufficient
- FCC firms should prepare internal processes for rapid investigation
- Goal: Provide complete (not just fast) disclosure
- Invest in investigation infrastructure, not just disclosure infrastructure

**5. Industry Effects**
- FCC-regulated sectors (telecom, cable): Need to be especially careful
- These sectors already have regulatory scrutiny; breach disclosure = regulatory risk trigger
- Non-FCC sectors (retail, tech): Have more flexibility; can use disclosure strategically
- Cross-industry M&A: Consider post-acquisition breach disclosure strategy
</div>
""", unsafe_allow_html=True)

# ============================================================================
# SECTION 6: LIMITATIONS
# ============================================================================

st.markdown("---")
st.markdown("## Limitations & Future Research")

st.markdown("""
### Limitations of This Study

**1. Sample Selection**
- Results apply to publicly-traded firms with stock market data
- May not generalize to: Private companies, startups, small businesses
- Selection bias toward larger, older firms with longer CRSP histories

**2. Causal Identification**
- Natural experiment assumes no confounding
- FCC firms (telecom) differ in systematic ways from non-FCC firms
- Parallel trends assumption tested but can't be fully proven
- Unobserved confounds (e.g., hacking vulnerability by sector) possible

**3. Measurement**
- CAR is stock market reaction; may not equal true economic impact
- Volatility is proxy for uncertainty; may reflect other factors
- CRSP data only covers US public markets

**4. Generalization**
- FCC 2007 regulation is one policy moment
- Results may not generalize to other disclosure regulations
- Market has evolved since 2007 (better cyber awareness)

**5. Mechanism**
- Volatility increases observed; causality not directly tested
- Could be alternative mechanisms (regulatory risk, industry effects, etc.)
- Future work should directly test information asymmetry mechanisms

### Promising Avenues for Future Research

1. **Heterogeneous Effects**
   - How do results vary by firm size, industry, breach severity?
   - Do health data breaches follow same pattern?
   - Do repeat offenders face worse penalties?

2. **Alternative Disclosure Mechanisms**
   - Do social media disclosures help or hurt?
   - Does CEO letter to shareholders change market reaction?
   - Do competing disclosures (news vs. company) matter?

3. **International Comparisons**
   - Do European GDPR rules have similar effects?
   - Do other countries' disclosure mandates help or hurt?
   - Cross-country natural experiments (GDPR staggered implementation)

4. **Timing Elasticity**
   - What's the optimal disclosure delay?
   - Is 7 days too short? 30 days too long?
   - Does optimal timing vary by breach type?

5. **Downstream Effects**
   - Do worse market reactions hurt hiring, sales, partnerships?
   - Do firms with worse breach CAR face higher cost of capital?
   - Long-term effects on firm value and growth?

6. **Policy Simulation**
   - What if 7-day rule was changed to 30 days?
   - What if information quality was mandated instead of timing?
   - Counterfactual policy analysis using empirical results
""")

# ============================================================================
# SECTION 7: FINAL THOUGHTS
# ============================================================================

st.markdown("---")
st.markdown("## Final Thoughts: The Bigger Picture")

st.markdown("""
### What This Dissertation Is Really About

This is not a paper about FCC regulations or data breaches, though it studies both.

**It's about the tension between:**
- **Transparency (disclosure)** vs. **Accuracy (completeness)**
- **Speed** vs. **Quality**
- **Compliance (following the rule)** vs. **Effectiveness (achieving the goal)**

In many policy domains, we assume:
> "More information, faster = better"

But information economics teaches us:
> "Incomplete information can be worse than no information"

The market correctly interprets forced disclosure of incomplete information as a negative signal.
This is rational. Firms disclose early only if forced; otherwise they'd wait for complete information.

**The implication:** Regulators should be careful about mandating speed without mandating quality.

### What Makes a Good Regulation?

**Good regulations:**
1. Clearly define what is forbidden
2. Provide safe harbors for uncertain cases
3. Allow for supplemental disclosures
4. Focus on outcomes (information quality) not inputs (disclosure speed)
5. Are informed by evidence about actual effects

**Bad regulations:**
1. Mandate inputs (speed) without ensuring outcomes (quality)
2. Assume faster is always better
3. Don't account for information costs
4. Create perverse incentives

This dissertation provides evidence that the FCC 7-day rule may be an example of well-intentioned regulation
with unintended negative consequences.

### The Broader Takeaway

Regulation of disclosure requirements across multiple domains (privacy, AI, content moderation, cybersecurity)
should consider this lesson:

**Mandate the outcomes you want (clear information), not the process that supposedly gets you there (fast disclosure).
Let organizations figure out how to meet the outcome requirement efficiently.**

If regulators required "complete breach assessment within 30 days" instead of "preliminary disclosure within 7 days",
the market might reward companies with better returns, and actual consumer protection would improve.

---

### Implications

This research shows that forced disclosure can harm companies (reducing their value and ability to invest in security)
when timing mandates sacrifice information quality. Understanding unintended consequences of regulation is essential
for designing disclosure policy that actually protects consumers rather than policy that sounds good but backfires in practice.
""")

st.markdown("---")
st.markdown("""
<div style='text-align: center; padding: 2rem; background-color: #f0f0f0; color: #333; border-radius: 8px;'>
<h2>Thank you for reading</h2>

This Streamlit dashboard was designed to tell a research story clearly and completely,
so that a PhD committee can understand the findings, evaluate the evidence, and judge the contribution.

If you have questions about methodology, data, or interpretations,
please see the <b>"Raw Data Explorer"</b> and <b>"Data Dictionary"</b> pages for verification.

---

<b>Prepared by:</b> Timothy D. Spivey<br>
<b>Date:</b> January 2026<br>
<b>Data:</b> 1,054 data breaches (2004-2025), 926 with stock market analysis
</div>
""", unsafe_allow_html=True)
