"""
PAGE 10: RAW DATA EXPLORER
Transparency tool - Search, filter, and explore the actual dataset
Not the main story, but proves the data is real and accessible
"""

import streamlit as st
from pathlib import Path
import pandas as pd
from utils import load_main_dataset

st.set_page_config(page_title="Raw Data Explorer", page_icon="🔍", layout="wide")

st.markdown("""
<style>
.explorer-header {
    font-size: 2.5rem;
    font-weight: bold;
    color: #555;
    text-align: center;
    padding: 1rem 0;
    margin-bottom: 2rem;
    border-bottom: 3px solid #555;
}
.transparency-box {
    background-color: #f8f9fa;
    padding: 1.5rem;
    border-left: 5px solid #555;
    border-radius: 5px;
    margin: 1rem 0;
    color: #333;
}
.transparency-box p, .transparency-box li, .transparency-box h3, .transparency-box span {
    color: #333 !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='explorer-header'>🔍 Raw Data Explorer</div>", unsafe_allow_html=True)

st.markdown("""
<div class='transparency-box'>
<h3>Why This Matters</h3>
This dashboard is built on real data. Here you can search, filter, and download the complete dataset.
Transparency: Every number in this dashboard comes directly from the data shown here.
</div>
""", unsafe_allow_html=True)

# Load data
df = load_main_dataset()

st.markdown("---")
st.markdown("## Search & Filter the Data")

# Create three columns for filters
col1, col2, col3 = st.columns(3)

with col1:
    search_term = st.text_input("Search by company name:", placeholder="e.g., 'Apple'")

with col2:
    min_year = st.number_input("Minimum year:", min_value=int(df['breach_date'].dt.year.min()),
                               max_value=int(df['breach_date'].dt.year.max()),
                               value=int(df['breach_date'].dt.year.min()))

with col3:
    max_year = st.number_input("Maximum year:", min_value=int(df['breach_date'].dt.year.min()),
                               max_value=int(df['breach_date'].dt.year.max()),
                               value=int(df['breach_date'].dt.year.max()))

# Apply filters
filtered_df = df.copy()

if search_term:
    filtered_df = filtered_df[filtered_df['org_name'].str.contains(search_term, case=False, na=False)]

filtered_df['year'] = filtered_df['breach_date'].dt.year
filtered_df = filtered_df[(filtered_df['year'] >= min_year) & (filtered_df['year'] <= max_year)]

# Show results
st.markdown(f"### Found {len(filtered_df):,} breaches")

# Key display columns
display_cols = ['org_name', 'breach_date', 'fcc_reportable', 'total_affected', 'car_5d', 'car_30d', 'volatility_change']
display_cols = [col for col in display_cols if col in filtered_df.columns]

st.dataframe(filtered_df[display_cols], use_container_width=True, height=400)

# Download option
st.markdown("---")
st.markdown("## Download Data")

csv = filtered_df.to_csv(index=False)
st.download_button(
    label="📥 Download filtered data as CSV",
    data=csv,
    file_name=f"breach_data_{min_year}_{max_year}.csv",
    mime="text/csv"
)

st.markdown("---")
st.markdown("""
**Note:** The download includes all {0} columns from the full dataset.
Each row is a data breach. FCC-reportable breaches (1 = yes, 0 = no) are highlighted in the analysis.
""")
