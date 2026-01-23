# Dissertation Dataset Audit Report

This directory contains comprehensive audit results for the dissertation dataset:
`Data/processed/FINAL_DISSERTATION_DATASET_ENRICHED.csv`

## Quick Start

**New to the audit?** Start here:
1. Read `AUDIT_QUICK_REFERENCE.txt` (in project root) - 2 min overview
2. Read `AUDIT_SUMMARY.md` (in project root) - 10 min detailed analysis

**Want specific metrics?** Use the CSV files below.

---

## CSV Files Overview

### Master File
- **audit_comprehensive.csv** - All metrics in one file (simple lookup)

### Section-Specific Files
- **audit_dataset_size.csv** - Overall dataset dimensions and date range
- **audit_essay2_sample.csv** - CRSP stock data availability (CAR metrics)
- **audit_essay3_sample.csv** - Volatility data availability
- **audit_fcc_analysis.csv** - FCC regulatory analysis and disclosure timing
- **audit_market_reactions_car.csv** - Cumulative abnormal returns by group
- **audit_volatility_analysis.csv** - Volatility change analysis
- **audit_sample_characteristics.csv** - Firm characteristics and financial metrics
- **audit_data_quality.csv** - Missing data and data integrity assessment

---

## Key Findings at a Glance

| Metric | Value |
|--------|-------|
| **Total Breaches** | 1,054 |
| **Unique Organizations** | 452 |
| **Date Range** | 2006-2025 |
| **Essay 2 Sample Size** | 926 (87.86%) |
| **Essay 3 Sample Size** | 916 (86.91%) |

### FCC Regulatory Impact
- **FCC Breaches**: 200 (18.98%)
- **5-Day CAR Effect**: -1.27% (FCC worse)
- **30-Day CAR Effect**: -2.48% (FCC worse)
- **Volatility Effect**: +1.55% (FCC higher uncertainty)
- **Disclosure Speed**: 35.6 days faster for FCC post-2007

### Data Quality
- Missing values: 2 columns (100%), 3 columns (>50%)
- Corrupt data: NONE detected
- Overall status: **CLEAN**

---

## How to Use These Files

### For Dashboard/Report Creation
```excel
Open audit_comprehensive.csv in Excel
Filter by Section column to extract specific topic
All values pre-formatted for charts/tables
```

### For Statistical Analysis
```python
import pandas as pd
df = pd.read_csv('audit_comprehensive.csv')
# Filter by section and metric as needed
fcc_data = df[df['Section'] == 'fcc_analysis']
```

### For Methodology Documentation
- Reference specific metrics from CSV files when describing sample
- Example: "Essay 2 analysis uses 926 observations (87.86% of total)"
- Use data quality section for missing data disclosure

---

## Understanding the Key Metrics

### Essay 2 (Market Reactions)
- **Has CRSP Data**: Observations with stock price data for return calculations
- **CAR 5-Day**: Cumulative abnormal returns, 5-day event window
- **CAR 30-Day**: Cumulative abnormal returns, 30-day event window

### Essay 3 (Information Asymmetry)
- **Volatility Pre**: Standard deviation of returns before breach
- **Volatility Post**: Standard deviation of returns after breach
- **Volatility Change**: Post minus Pre (negative = decreased volatility)

### FCC Analysis
- **FCC Reportable**: Breaches subject to FCC Rule 37.3 (telecom)
- **Disclosure Delay**: Days from breach date to public disclosure
- **Pre/Post 2007**: Before vs after FCC rule effective date

### Sample Characteristics
- **Prior Breaches**: Companies with history of >1 breach
- **Firm Size**: Log of total assets (proxy for company scale)
- **Leverage**: Debt-to-assets ratio
- **ROA**: Return on assets (profitability measure)

---

## Critical Caveats

1. **FCC vs Non-FCC Comparison**: FCC firms are 2.22x LARGER (confounding variable)
   - Control for size in all regression models
   - Consider propensity score matching

2. **Financial Data Availability**: Only 55.8% have firm characteristics
   - Analyze with/without financial subset for sensitivity
   - Document missing data approach in methodology

3. **Survivor Bias**: Sample contains public companies and their subsidiaries only
   - Results may not generalize to private firms

4. **Regulatory Context**: 99.5% of sample post-2007 FCC Rule 37.3
   - Very limited pre-2007 comparison group (n=4)

---

## Related Files

- `AUDIT_SUMMARY.md` (project root) - Detailed narrative report with context
- `AUDIT_QUICK_REFERENCE.txt` (project root) - Quick lookup guide

---

## Questions?

Refer to the section-specific CSV file that matches your question:
- "How much data do I have?" → audit_dataset_size.csv
- "Can I use CAR in my analysis?" → audit_essay2_sample.csv
- "What's the volatility situation?" → audit_essay3_sample.csv
- "FCC impact on returns?" → audit_market_reactions_car.csv
- "Missing data issues?" → audit_data_quality.csv

---

**Report Generated**: January 23, 2026
**Data Source**: Data/processed/FINAL_DISSERTATION_DATASET_ENRICHED.csv
**Total Observations**: 1,054 breaches across 452 organizations
