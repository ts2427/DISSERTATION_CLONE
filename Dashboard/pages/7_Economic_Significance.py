"""
Economic Significance Analysis Page

Shows the real-world dollar impact of dissertation findings
"""

import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
from PIL import Image

st.set_page_config(page_title="Economic Significance", page_icon="💰", layout="wide")

st.markdown("""
# 💰 Economic Significance Analysis

## Real-World Impact of Disclosure Regulation

*Translating statistical findings into economic costs and implications*
""")

# Load data
@st.cache_data(ttl=3600)
def load_economic_data():
    try:
        # Try multiple possible paths in order of likelihood
        possible_paths = [
            '/mount/src/dissertation_clone/outputs/economic_significance/economic_impact_summary.csv',
            'outputs/economic_significance/economic_impact_summary.csv',
            '../outputs/economic_significance/economic_impact_summary.csv',
            '../../outputs/economic_significance/economic_impact_summary.csv',
        ]

        for path in possible_paths:
            try:
                impact_df = pd.read_csv(path)
                return impact_df
            except:
                continue

        # If still not found, try with Path - go up to Dashboard parent (which is repo root)
        base_dir = Path(__file__).parent.parent.parent
        data_path = base_dir / 'outputs' / 'economic_significance' / 'economic_impact_summary.csv'
        impact_df = pd.read_csv(str(data_path))
        return impact_df
    except Exception as e:
        st.error(f"Error loading economic impact data: {str(e)}")
        return None

@st.cache_data(ttl=3600)
def load_report():
    try:
        # Try multiple possible paths in order of likelihood
        possible_paths = [
            '/mount/src/dissertation_clone/outputs/economic_significance/economic_significance_report.txt',
            'outputs/economic_significance/economic_significance_report.txt',
            '../outputs/economic_significance/economic_significance_report.txt',
            '../../outputs/economic_significance/economic_significance_report.txt',
        ]

        for path in possible_paths:
            try:
                with open(path, 'r') as f:
                    return f.read()
            except:
                continue

        # If still not found, try with Path - go up to Dashboard parent (which is repo root)
        base_dir = Path(__file__).parent.parent.parent
        report_path = base_dir / 'outputs' / 'economic_significance' / 'economic_significance_report.txt'
        with open(str(report_path), 'r') as f:
            return f.read()
    except Exception as e:
        st.error(f"Error loading economic report: {str(e)}")
        return None

impact_df = load_economic_data()
report_text = load_report()

# ============================================================================
# SECTION 1: ECONOMIC IMPACT SUMMARY TABLE
# ============================================================================

st.markdown("---")
st.markdown("## 📊 Economic Impact Summary (Per Breach)")

if impact_df is not None:
    st.dataframe(impact_df, use_container_width=True)
else:
    st.warning("Economic impact data not found. Run script 96_economic_significance.py first.")

# ============================================================================
# SECTION 2: KEY FINDINGS
# ============================================================================

st.markdown("---")
st.markdown("## 🎯 Key Findings")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="FCC Regulatory Cost (Median Firm)",
        value="-$0.9M",
        delta="per breach",
        delta_color="inverse"
    )

with col2:
    st.metric(
        label="Cost of Capital Impact",
        value="+0.0137%",
        delta="from FCC regulation",
        delta_color="off"
    )

with col3:
    st.metric(
        label="Governance Disruption Cost",
        value="$1.0M",
        delta="per breach",
        delta_color="off"
    )

# ============================================================================
# SECTION 3: VISUALIZATIONS
# ============================================================================

st.markdown("---")
st.markdown("## 📈 Visualizations")

@st.cache_data(ttl=3600)
def load_image(filename):
    """Load image from economic_significance directory with multiple path attempts"""
    possible_paths = [
        f'/mount/src/dissertation_clone/outputs/economic_significance/{filename}',
        f'outputs/economic_significance/{filename}',
        f'../outputs/economic_significance/{filename}',
        f'../../outputs/economic_significance/{filename}',
    ]

    for path in possible_paths:
        try:
            img = Image.open(path)
            return img
        except:
            continue

    # Try with Path object - go up to repo root
    try:
        base_dir = Path(__file__).parent.parent.parent
        img_path = base_dir / 'outputs' / 'economic_significance' / filename
        img = Image.open(str(img_path))
        return img
    except:
        return None

tab1, tab2, tab3 = st.tabs(["FCC Cost by Size", "Impact Breakdown", "Governance Costs"])

# Tab 1: FCC Cost
with tab1:
    st.markdown("### FCC Regulatory Cost by Firm Size")
    try:
        img = load_image('FCC_Cost_by_Firm_Size.png')
        if img:
            st.image(img, use_column_width=True)
            st.markdown("""
            **Interpretation:**
            - Smaller firms experience larger absolute costs ($0.2M to $0.9M)
            - Large firms experience larger costs in absolute terms ($4.1M to $10.4M)
            - Effect scales with firm size: regulatory burden increases with market capitalization
            - Regulatory compliance creates measurable shareholder value destruction
            """)
        else:
            st.warning("Visualization not found. Run script 96_economic_significance.py first.")
    except Exception as e:
        st.warning(f"Error loading image: {str(e)}")

# Tab 2: Breakdown
with tab2:
    st.markdown("### Total Economic Impact Breakdown")
    try:
        img = load_image('Economic_Impact_Breakdown.png')
        if img:
            st.image(img, use_column_width=True)
            st.markdown("""
            **Three Economic Mechanisms:**
            1. **Market Valuation** (Blue): Direct shareholder value loss from FCC regulation
            2. **Cost of Capital** (Orange): Annual cost increase from information asymmetry
            3. **Governance Disruption** (Green): Executive turnover and organizational costs

            Effects compound across all three channels, creating substantial total economic burden.
            """)
        else:
            st.warning("Visualization not found. Run script 96_economic_significance.py first.")
    except Exception as e:
        st.warning(f"Error loading image: {str(e)}")

# Tab 3: Governance
with tab3:
    st.markdown("### Executive Turnover Cost Components")
    try:
        img = load_image('Governance_Cost_Components.png')
        if img:
            st.image(img, use_column_width=True)
            st.markdown("""
            **Turnover Cost Breakdown:**
            - **Direct Costs** ($2-5M): Severance packages, recruitment, legal fees
            - **Indirect Costs** ($10-20M): Disruption, lost relationships, learning curve
            - **Total Impact** ($12-25M): Full economic burden per executive departure

            Timing-driven changes in executive turnover (5.3 percentage point increase)
            translate to $1M per breach in expected governance costs.
            """)
        else:
            st.warning("Visualization not found. Run script 96_economic_significance.py first.")
    except Exception as e:
        st.warning(f"Error loading image: {str(e)}")

# ============================================================================
# SECTION 4: DETAILED ANALYSIS
# ============================================================================

st.markdown("---")
st.markdown("## 📋 Detailed Economic Analysis")

if report_text:
    with st.expander("Full Economic Significance Report", expanded=False):
        st.text(report_text)
else:
    st.warning("Full report not available. Run script 96_economic_significance.py first.")

# ============================================================================
# SECTION 5: IMPLICATIONS
# ============================================================================

st.markdown("---")
st.markdown("## 💡 Implications for Policy & Practice")

st.markdown("""
### For Regulators
- **Cost-Benefit Analysis:** FCC regulation imposes $0.76B in aggregate shareholder losses
- **Effectiveness Question:** Are regulatory objectives (faster disclosure, governance changes) worth the $4M-$10.4M cost per firm?
- **Size Effects:** Smaller firms bear disproportionate burden (larger % of market cap)

### For Firms
- **Disclosure Strategy:** Information asymmetry costs ($1.4-1.8M annually) suggest value in faster voluntary disclosure
- **Governance Response:** Timing-driven executive changes have $1M+ per breach cost; may warrant better crisis communications
- **Hedging Opportunities:** Cost of capital increases create opportunity for better investor relations post-breach

### For Investors
- **Risk Pricing:** Market prices in FCC regulatory burden (-2.20% CAR) and governance uncertainty
- **Timing Signal:** Market indifferent to disclosure timing (no market reward for speed)
- **Information Risk:** Volatility increases suggest information environment deterioration worth 1-2 basis points in cost of capital

### For Researchers
- **Economic Magnitude:** Statistical significance without economic significance is insufficient
- **Mechanism Validation:** Three independent mechanisms (valuation, learning, governance) generate different economic impacts
- **Next Steps:** Quantify whether outcomes improve (regulatory effectiveness) or just costs shift (regulatory burden transfer)
""")

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #888; font-size: 12px;">
Generated: February 27, 2026 | Data: 1,054 breaches | Script: 96_economic_significance.py
</div>
""", unsafe_allow_html=True)
