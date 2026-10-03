"""
Dissertation dashboard - entry point and navigation.

    streamlit run Dashboard/app.py        (from the repository root)

Each page reads its numbers from the committed pipeline outputs (Dashboard/data.py) and shares
one look (Dashboard/ui.py). Theme: .streamlit/config.toml.
"""
import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent))

st.set_page_config(page_title='Breach disclosure dissertation', page_icon=':material/query_stats:',
                   layout='wide', initial_sidebar_state='expanded')

PAGES = {
    'Dissertation': [
        st.Page('views/0_Overview.py', title='Overview', icon=':material/home:', default=True),
    ],
    'Essays': [
        st.Page('views/1_Essay_1_Market_Reaction.py', title='Essay 1 · Market reaction',
                icon=':material/trending_down:'),
        st.Page('views/2_Essay_2_Information_Environment.py', title='Essay 2 · Information',
                icon=':material/insights:'),
        st.Page('views/3_Essay_3_Governance_Response.py', title='Essay 3 · Governance',
                icon=':material/groups:'),
    ],
    'Evidence base': [
        st.Page('views/4_Robustness_and_Defense_Supplement.py', title='Robustness & supplement',
                icon=':material/fact_check:'),
        st.Page('views/5_Limitations_and_Audit_Trail.py', title='Limitations & audit',
                icon=':material/policy:'),
    ],
}

with st.sidebar:
    st.markdown('**Data Breach Disclosure Timing and Market Reactions**  \n'
                '<span style="color:#5B6475;font-size:0.85rem">Timothy D. Spivey · '
                'University of South Alabama</span>', unsafe_allow_html=True)

st.navigation(PAGES).run()

with st.sidebar:
    st.caption('Results as of tag `defense-final`. Every number is read from a committed output.')
