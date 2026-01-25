"""
Shared utilities for dashboard pages
Data loading, caching, calculations, and visualization helpers
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
import json

# ============================================================================
# DATA LOADING (CACHED FOR PERFORMANCE)
# ============================================================================

@st.cache_data
def load_main_dataset():
    """Load the enriched dissertation dataset

    Smart loading strategy:
    1. Check local path first (for post-run_all.py local execution)
    2. Fall back to Google Drive (for Streamlit Cloud or if local file missing)
    """
    from pathlib import Path
    import os

    # Strategy 1: Try local file first (fastest, works after run_all.py)
    try:
        root_dir = Path(__file__).parent.parent
        data_path = root_dir / 'Data' / 'processed' / 'FINAL_DISSERTATION_DATASET_ENRICHED.csv'
        if data_path.exists():
            df = pd.read_csv(data_path)
            df['breach_date'] = pd.to_datetime(df['breach_date'], errors='coerce')
            df['breach_year'] = df['breach_date'].dt.year
            df['period'] = df['breach_year'].apply(lambda x: 'Pre-2007' if x < 2007 else 'Post-2007')
            df['treatment_group'] = df['fcc_reportable'].apply(lambda x: 'FCC-Regulated' if x == 1 else 'Non-FCC')
            return df
    except Exception as e:
        pass  # Will try Google Drive fallback

    # Strategy 2: Fall back to Google Drive (for Streamlit Cloud)
    try:
        import gdown

        # Google Drive file ID
        file_id = "1v0nKdwjihWGdbJLwTttFL0UkE2Jo2OIc"

        # Create temporary file path
        temp_csv = "dissertation_data.csv"

        # Download with progress indication
        with st.spinner("Loading data from cloud storage (first time only)..."):
            gdown.download(
                f'https://drive.google.com/uc?id={file_id}',
                temp_csv,
                quiet=True,
                use_cookies=False
            )

        # Load from temp file
        df = pd.read_csv(temp_csv)
        df['breach_date'] = pd.to_datetime(df['breach_date'], errors='coerce')
        df['breach_year'] = df['breach_date'].dt.year
        df['period'] = df['breach_year'].apply(lambda x: 'Pre-2007' if x < 2007 else 'Post-2007')
        df['treatment_group'] = df['fcc_reportable'].apply(lambda x: 'FCC-Regulated' if x == 1 else 'Non-FCC')

        # Clean up temp file
        if os.path.exists(temp_csv):
            try:
                os.remove(temp_csv)
            except:
                pass  # OK if cleanup fails

        return df

    except Exception as e:
        st.error(f"Failed to load data from both local and cloud sources. Error: {str(e)}")
        return None

@st.cache_data
def load_sample_attrition():
    """Load sample attrition analysis"""
    try:
        return pd.read_csv('outputs/tables/sample_attrition.csv')
    except FileNotFoundError:
        return None

@st.cache_data
def load_ml_results():
    """Load ML validation results"""
    try:
        with open('outputs/ml_models/ml_model_results.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return None

@st.cache_data
def load_feature_importance(essay='essay2'):
    """Load feature importance rankings from ML models"""
    try:
        return pd.read_csv(f'outputs/ml_models/feature_importance_{essay}_rf.csv')
    except FileNotFoundError:
        return None

# ============================================================================
# STATISTICAL CALCULATIONS
# ============================================================================

def calculate_descriptive_stats(series):
    """Calculate key descriptive statistics"""
    return {
        'N': len(series),
        'Mean': series.mean(),
        'Median': series.median(),
        'Std Dev': series.std(),
        'Min': series.min(),
        'Max': series.max(),
        'Q1': series.quantile(0.25),
        'Q3': series.quantile(0.75)
    }

def calculate_group_comparison(df, metric, group_var):
    """Compare metric across groups (for t-tests, etc.)"""
    groups = df[group_var].unique()
    comparison = {}

    for group in groups:
        group_data = df[df[group_var] == group][metric].dropna()
        comparison[str(group)] = calculate_descriptive_stats(group_data)

    return comparison

# ============================================================================
# VISUALIZATION FUNCTIONS
# ============================================================================

def plot_car_distribution(df, color='steelblue', title='Distribution of 30-Day CAR'):
    """Create histogram of CAR distribution with mean line"""
    fig = go.Figure()

    car_data = df['car_30d'].dropna()

    fig.add_trace(go.Histogram(
        x=car_data,
        nbinsx=50,
        marker_color=color,
        opacity=0.7,
        name='CAR'
    ))

    fig.add_vline(x=0, line_dash="dash", line_color="black", line_width=2)
    fig.add_vline(
        x=car_data.mean(),
        line_dash="dash",
        line_color="red",
        line_width=2,
        annotation_text=f"Mean: {car_data.mean():.2f}%"
    )

    fig.update_layout(
        title=title,
        xaxis_title="CAR (%)",
        yaxis_title="Frequency",
        height=400
    )

    return fig

def plot_timeline(df, group_var='breach_year', color_var='treatment_group'):
    """Create timeline of breaches"""
    timeline = df.groupby([group_var, color_var]).size().reset_index(name='count')

    fig = px.bar(
        timeline,
        x=group_var,
        y='count',
        color=color_var,
        title='Breach Timeline',
        labels={group_var: 'Year', 'count': 'Number of Breaches'},
        barmode='stack'
    )

    # Add FCC regulation line
    if group_var == 'breach_year':
        fig.add_vline(
            x=2007,
            line_dash="dash",
            line_color="green",
            line_width=3,
            annotation_text="FCC Regulation"
        )

    fig.update_layout(height=400)
    return fig

def plot_boxplot_comparison(df, metric, group_var, title='Comparison'):
    """Create boxplot comparing metric across groups"""
    fig = px.box(
        df,
        x=group_var,
        y=metric,
        title=title,
        points=False
    )

    fig.add_hline(y=0, line_dash="dash", line_color="black", opacity=0.5)
    fig.update_layout(height=400)
    return fig

def plot_scatter_with_trend(df, x_var, y_var, title='Relationship'):
    """Create scatter plot with trendline"""
    fig = px.scatter(
        df.dropna(subset=[x_var, y_var]),
        x=x_var,
        y=y_var,
        trendline='ols',
        title=title
    )

    fig.update_layout(height=400)
    return fig

# ============================================================================
# DATA FILTERING HELPERS
# ============================================================================

def filter_by_period(df, period='all'):
    """Filter dataset by time period"""
    if period == 'pre_2007':
        return df[df['breach_year'] < 2007]
    elif period == 'post_2007':
        return df[df['breach_year'] >= 2007]
    else:
        return df

def filter_by_treatment(df, treatment='all'):
    """Filter dataset by FCC status"""
    if treatment == 'fcc':
        return df[df['fcc_reportable'] == 1]
    elif treatment == 'non_fcc':
        return df[df['fcc_reportable'] == 0]
    else:
        return df

def filter_by_disclosure(df, timing='all'):
    """Filter dataset by disclosure timing"""
    if timing == 'immediate':
        return df[df['immediate_disclosure'] == 1]
    elif timing == 'delayed':
        return df[df['delayed_disclosure'] == 1]
    else:
        return df

# ============================================================================
# FORMATTING HELPERS
# ============================================================================

def format_pvalue(p):
    """Format p-value with significance stars"""
    if p < 0.001:
        return f"{p:.4f}***"
    elif p < 0.01:
        return f"{p:.4f}**"
    elif p < 0.05:
        return f"{p:.4f}*"
    else:
        return f"{p:.4f}"

def format_percentage(val):
    """Format value as percentage"""
    return f"{val:.2f}%"

def format_currency(val):
    """Format value as currency"""
    if val >= 1e9:
        return f"${val/1e9:.2f}B"
    elif val >= 1e6:
        return f"${val/1e6:.2f}M"
    else:
        return f"${val:.2f}"

# ============================================================================
# RESEARCH NARRATIVE HELPERS
# ============================================================================

def get_effect_interpretation(coefficient, pvalue, unit="percentage points"):
    """Interpret regression coefficient"""
    sig = ""
    if pvalue < 0.001:
        sig = " (p<0.001, highly significant)"
    elif pvalue < 0.01:
        sig = " (p<0.01, very significant)"
    elif pvalue < 0.05:
        sig = " (p<0.05, significant)"
    else:
        sig = " (not significant)"

    direction = "increases" if coefficient > 0 else "decreases"
    return f"{direction.capitalize()} outcome by {abs(coefficient):.2f} {unit}{sig}"

def create_summary_statistics_table(df):
    """Create comprehensive summary statistics table"""
    key_vars = ['car_30d', 'car_5d', 'return_volatility_post', 'firm_size_log', 'leverage', 'roa']
    available_vars = [v for v in key_vars if v in df.columns]

    summary = df[available_vars].describe().round(4)
    return summary
