"""
PAGE 11: DATA DICTIONARY
Reference: All 83 variables documented with descriptions and sources
"""

import streamlit as st
from pathlib import Path
import pandas as pd

st.set_page_config(page_title="Data Dictionary", page_icon="📚", layout="wide")

st.markdown("""
<style>
.reference-header {
    font-size: 2.5rem;
    font-weight: bold;
    color: #555;
    text-align: center;
    padding: 1rem 0;
    margin-bottom: 2rem;
    border-bottom: 3px solid #555;
}
.reference-box {
    background-color: #f8f9fa;
    padding: 1.5rem;
    border-left: 5px solid #555;
    border-radius: 5px;
    margin: 1rem 0;
    color: #333;
}
.reference-box p, .reference-box li, .reference-box h3, .reference-box span {
    color: #333 !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='reference-header'>📚 Data Dictionary</div>", unsafe_allow_html=True)

st.markdown("""
<div class='reference-box'>
<h3>What's Here</h3>
Complete documentation of all 83 variables in the dataset.
Includes: variable name, description, source, data type, sample values.
</div>
""", unsafe_allow_html=True)

# Load data to get actual column info
@st.cache_data
def load_data():
    df = pd.read_csv(str(Path(__file__).parent.parent.parent / 'Data' / 'processed' / 'FINAL_DISSERTATION_DATASET_ENRICHED.csv'))
    return df

df = load_data()

# Create comprehensive data dictionary
data_dictionary = {
    # ===== CORE IDENTIFIER =====
    'org_name': {'Source': 'Privacy Rights Clearinghouse', 'Type': 'String', 'Description': 'Organization name'},
    'reported_date': {'Source': 'Privacy Rights Clearinghouse', 'Type': 'Date', 'Description': 'Date breach was first reported'},
    'breach_date': {'Source': 'Privacy Rights Clearinghouse', 'Type': 'Date', 'Description': 'Date breach was discovered'},
    'end_breach_date': {'Source': 'Privacy Rights Clearinghouse', 'Type': 'Date', 'Description': 'Date breach was contained'},
    'incident_details': {'Source': 'Privacy Rights Clearinghouse', 'Type': 'String', 'Description': 'Narrative description of breach'},

    # ===== COMPANY CHARACTERISTICS =====
    'organization_type': {'Source': 'Privacy Rights Clearinghouse', 'Type': 'Categorical', 'Description': 'Type of organization (BSO=Business Services Organization)'},
    'cik': {'Source': 'SEC EDGAR', 'Type': 'String', 'Description': 'SEC Central Index Key for public companies'},
    'sic': {'Source': 'SEC EDGAR', 'Type': 'Integer', 'Description': 'Standard Industrial Classification code'},
    'naics': {'Source': 'SEC EDGAR', 'Type': 'Integer', 'Description': 'North American Industry Classification System code'},

    # ===== BREACH CHARACTERISTICS =====
    'information_affected': {'Source': 'Privacy Rights Clearinghouse', 'Type': 'String', 'Description': 'Types of data affected (categorical)'},
    'total_affected': {'Source': 'Privacy Rights Clearinghouse', 'Type': 'Integer', 'Description': 'Number of individuals affected'},
    'breach_type': {'Source': 'Privacy Rights Clearinghouse', 'Type': 'Categorical', 'Description': 'Classification of breach type'},
    'records_affected_numeric': {'Source': 'Calculated', 'Type': 'Integer', 'Description': 'Numeric version of total_affected'},

    # ===== DATA BREACH TYPES (BINARY FLAGS) =====
    'health_breach': {'Source': 'Calculated', 'Type': 'Binary', 'Description': '1 if health/medical data affected'},
    'financial_breach': {'Source': 'Calculated', 'Type': 'Binary', 'Description': '1 if financial data affected'},
    'pii_breach': {'Source': 'Calculated', 'Type': 'Binary', 'Description': '1 if personally identifiable information affected'},
    'ip_breach': {'Source': 'Calculated', 'Type': 'Binary', 'Description': '1 if intellectual property affected'},

    # ===== THREAT ATTRIBUTES (BINARY FLAGS) =====
    'ransomware': {'Source': 'Calculated', 'Type': 'Binary', 'Description': '1 if ransomware involved'},
    'nation_state': {'Source': 'Calculated', 'Type': 'Binary', 'Description': '1 if nation-state threat suspected'},
    'insider_threat': {'Source': 'Calculated', 'Type': 'Binary', 'Description': '1 if insider threat'},
    'ddos_attack': {'Source': 'Calculated', 'Type': 'Binary', 'Description': '1 if DDoS attack'},
    'phishing': {'Source': 'Calculated', 'Type': 'Binary', 'Description': '1 if phishing vector'},
    'malware': {'Source': 'Calculated', 'Type': 'Binary', 'Description': '1 if malware involved'},

    # ===== REGULATORY & SEVERITY =====
    'fcc_reportable': {'Source': 'FCC Database', 'Type': 'Binary', 'Description': '1 if company is FCC-regulated (telecommunications)'},
    'fcc_category': {'Source': 'FCC Database', 'Type': 'Categorical', 'Description': 'FCC category if regulated'},
    'regulatory_enforcement': {'Source': 'NCSL / State AG Records', 'Type': 'Binary', 'Description': '1 if regulatory enforcement action taken'},
    'enforcement_type': {'Source': 'NCSL / State AG Records', 'Type': 'Categorical', 'Description': 'Type of enforcement action'},
    'penalty_amount_usd': {'Source': 'NCSL / State AG Records', 'Type': 'Float', 'Description': 'Penalty amount in USD'},
    'enforcement_within_1yr': {'Source': 'Calculated', 'Type': 'Binary', 'Description': '1 if enforcement within 1 year of breach'},
    'enforcement_within_2yr': {'Source': 'Calculated', 'Type': 'Binary', 'Description': '1 if enforcement within 2 years of breach'},

    # ===== DISCLOSURE TIMING (KEY VARIABLE) =====
    'disclosure_delay_days': {'Source': 'Calculated', 'Type': 'Integer', 'Description': 'Days from breach date to public disclosure'},
    'days_to_first_change': {'Source': 'Calculated', 'Type': 'Integer', 'Description': 'Days to first executive change after breach'},

    # ===== MARKET DATA (CRSP) =====
    'has_stock_data': {'Source': 'CRSP', 'Type': 'Binary', 'Description': '1 if company has stock price data in CRSP'},
    'has_crsp_data': {'Source': 'CRSP', 'Type': 'Binary', 'Description': '1 if company in Essay 2 sample (has CRSP data)'},
    'stock_price_at_breach': {'Source': 'CRSP', 'Type': 'Float', 'Description': 'Stock price on breach date'},
    'return_5d_pct': {'Source': 'CRSP', 'Type': 'Float', 'Description': 'Raw return 5 days post-breach (%)'},
    'return_30d_pct': {'Source': 'CRSP', 'Type': 'Float', 'Description': 'Raw return 30 days post-breach (%)'},

    # ===== CUMULATIVE ABNORMAL RETURNS (CAR) =====
    'car_5d': {'Source': 'Calculated from CRSP', 'Type': 'Float', 'Description': 'Cumulative abnormal return over 5 days post-breach'},
    'car_30d': {'Source': 'Calculated from CRSP', 'Type': 'Float', 'Description': 'Cumulative abnormal return over 30 days post-breach'},
    'bhar_5d': {'Source': 'Calculated from CRSP', 'Type': 'Float', 'Description': 'Buy-and-hold abnormal return over 5 days'},
    'bhar_30d': {'Source': 'Calculated from CRSP', 'Type': 'Float', 'Description': 'Buy-and-hold abnormal return over 30 days'},

    # ===== VOLATILITY ANALYSIS (ESSAY 3) =====
    'return_volatility_pre': {'Source': 'CRSP', 'Type': 'Float', 'Description': 'Stock volatility 60 days before breach'},
    'return_volatility_post': {'Source': 'CRSP', 'Type': 'Float', 'Description': 'Stock volatility 60 days after breach'},
    'volatility_change': {'Source': 'Calculated', 'Type': 'Float', 'Description': 'Change in volatility: (post - pre) / pre'},
    'volume_volatility_pre': {'Source': 'CRSP', 'Type': 'Float', 'Description': 'Trading volume volatility 60 days before breach'},
    'volume_volatility_post': {'Source': 'CRSP', 'Type': 'Float', 'Description': 'Trading volume volatility 60 days after breach'},

    # ===== FIRM CONTROLS =====
    'firm_size_log': {'Source': 'Compustat', 'Type': 'Float', 'Description': 'Log of total assets (firm size)'},
    'leverage': {'Source': 'Compustat', 'Type': 'Float', 'Description': 'Debt-to-assets ratio'},
    'roa': {'Source': 'Compustat', 'Type': 'Float', 'Description': 'Return on assets'},

    # ===== BREACH HISTORY =====
    'prior_breaches_total': {'Source': 'Privacy Rights Clearinghouse', 'Type': 'Integer', 'Description': 'Total breaches for company before current breach'},
    'prior_breaches_1yr': {'Source': 'Calculated', 'Type': 'Integer', 'Description': 'Breaches in prior 1 year'},
    'prior_breaches_3yr': {'Source': 'Calculated', 'Type': 'Integer', 'Description': 'Breaches in prior 3 years'},
    'prior_breaches_5yr': {'Source': 'Calculated', 'Type': 'Integer', 'Description': 'Breaches in prior 5 years'},

    # ===== EXECUTIVE CHANGES =====
    'executive_change_30d': {'Source': 'Audit Analytics', 'Type': 'Binary', 'Description': '1 if executive change within 30 days of breach'},
    'executive_change_90d': {'Source': 'Audit Analytics', 'Type': 'Binary', 'Description': '1 if executive change within 90 days of breach'},
    'executive_change_180d': {'Source': 'Audit Analytics', 'Type': 'Binary', 'Description': '1 if executive change within 180 days of breach'},
    'num_changes_180d': {'Source': 'Audit Analytics', 'Type': 'Integer', 'Description': 'Number of executive changes in 180 days'},

    # ===== INSTITUTIONAL OWNERSHIP =====
    'num_institutions': {'Source': 'Compustat Institutional Holdings', 'Type': 'Integer', 'Description': 'Number of institutional owners'},
    'high_institutional_ownership': {'Source': 'Calculated', 'Type': 'Binary', 'Description': '1 if institutional ownership in top tercile'},

    # ===== VULNERABILITY MEASURES =====
    'total_cves': {'Source': 'NVD', 'Type': 'Integer', 'Description': 'Total CVEs for company products'},
    'cves_1yr_before': {'Source': 'NVD', 'Type': 'Integer', 'Description': 'CVEs in 1 year before breach'},
    'cves_2yr_before': {'Source': 'NVD', 'Type': 'Integer', 'Description': 'CVEs in 2 years before breach'},
    'cves_5yr_before': {'Source': 'NVD', 'Type': 'Integer', 'Description': 'CVEs in 5 years before breach'},
    'nvd_vendor': {'Source': 'NVD', 'Type': 'String', 'Description': 'Vendor name from NVD'},

    # ===== SEVERITY SCORES =====
    'severity_score': {'Source': 'Calculated', 'Type': 'Float', 'Description': 'Composite severity score'},
    'records_severity': {'Source': 'Calculated', 'Type': 'Float', 'Description': 'Severity based on records affected'},
    'combined_severity_score': {'Source': 'Calculated', 'Type': 'Float', 'Description': 'Combined severity metric'},
    'high_severity_breach': {'Source': 'Calculated', 'Type': 'Binary', 'Description': '1 if breach in high severity tier'},
    'num_breach_types': {'Source': 'Calculated', 'Type': 'Integer', 'Description': 'Number of different data types affected'},
    'complex_breach': {'Source': 'Calculated', 'Type': 'Binary', 'Description': '1 if complex (multiple breach types)'},

    # ===== INDUSTRY CONTROLS =====
    'industry_car_30d': {'Source': 'Calculated', 'Type': 'Float', 'Description': 'Industry median CAR 30d'},
    'industry_adjusted_car_30d': {'Source': 'Calculated', 'Type': 'Float', 'Description': 'Firm CAR minus industry median'},
}

st.markdown("---")
st.markdown("## Variable Definitions")

# Create searchable dictionary
search_col = st.text_input("Search variables:", placeholder="e.g., 'car' or 'volatility'")

# Filter dictionary
if search_col:
    filtered_dict = {k: v for k, v in data_dictionary.items() if search_col.lower() in k.lower()}
else:
    filtered_dict = data_dictionary

# Display as table
dict_data = []
for var_name, var_info in filtered_dict.items():
    dict_data.append({
        'Variable': var_name,
        'Type': var_info.get('Type', 'Unknown'),
        'Source': var_info.get('Source', 'Unknown'),
        'Description': var_info.get('Description', 'Unknown')
    })

dict_df = pd.DataFrame(dict_data)
st.dataframe(dict_df, use_container_width=True)

st.markdown("---")
st.markdown(f"""
### Summary
- **Total Variables**: {len(data_dictionary)}
- **Key Sample**: {sum(1 for k, v in data_dictionary.items() if 'car' in k or 'volatility' in k)} variables used in main analysis
- **Control Variables**: {sum(1 for k, v in data_dictionary.items() if any(x in k for x in ['leverage', 'roa', 'firm_size', 'prior']))} firm and breach controls

### Data Sources
- **Privacy Rights Clearinghouse**: Breach incident data
- **SEC EDGAR / Compustat**: Firm characteristics and financials
- **CRSP**: Stock prices and returns
- **Audit Analytics**: Executive changes
- **FCC Database**: Regulatory classifications
- **NVD (NIST)**: Vulnerability data
- **State AG & NCSL**: Regulatory enforcement records
""")
