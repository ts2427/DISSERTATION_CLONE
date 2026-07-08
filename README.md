# Data Breach Disclosure Timing and Market Reactions

**Author:** Timothy D. Spivey  
**Institution:** University of South Alabama  
**Year:** 2026

---

## Executive Summary

This dissertation analyzes how data breach disclosure timing and regulatory requirements affect stock market reactions, information asymmetry, and governance response using a natural experiment design.

**Core Finding:** Markets penalize *who you are* (regulatory status, breach history) and *what was breached* (data sensitivity), not *when you disclose*. Disclosure timing requirements create information asymmetry costs without corresponding governance benefits.

**Sample:** 1,054 breaches from 2006-2025 | 926 with market data | FCC natural experiment (regulation effective Sept 28, 2007)

---

## Quick Start

### 1. Setup (5 minutes)

```bash
# Clone and navigate
git clone https://github.com/ts2427/DISSERTATION_CLONE.git
cd DISSERTATION_CLONE

# Create environment
python -m venv venv
source venv/bin/activate  # macOS/Linux
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Download data (see Data Setup section below)
```

### 2. Data Setup (Required)

Data files are NOT in GitHub (size constraints). Download from Google Drive:

**[Shared Data Folder](https://drive.google.com/drive/folders/1aeEnpS-agQeaQCpgyD9UqQJDuJD1oij-?usp=sharing)**

Copy the `Data/` folder to your repo root. Verify with:

```bash
python -c "import pandas as pd; df = pd.read_csv('Data/processed/FINAL_DISSERTATION_DATASET_ENRICHED.csv'); print(f'Loaded: {len(df)} breaches')"
```

### 3. Run Analysis

```bash
# Complete pipeline (OLS + robustness, ~40 minutes)
python run_all.py

# Or individual essays
python Notebooks/01_descriptive_statistics.py
python Notebooks/02_essay2_volatility_analysis.py
python Notebooks/03_essay3_governance_response.py
```

---

## Key Findings

| Essay | Outcome | Result | Mechanism |
|-------|---------|--------|-----------|
| **1** | Market Returns (CAR) | Timing: +0.65% (NS) | Markets price firm characteristics, not disclosure speed |
| **1** | Market Returns (CAR) | FCC Regulation: -2.20%** | Regulatory burden signal |
| **2** | Information Asymmetry (Volatility) | FCC Effect: +1.79%* | Timing requirements force incomplete disclosure → uncertainty |
| **3** | Executive Turnover | FCC Effect: +3.71pp (NS) | No significant governance response to regulatory timing |

**The Paradox:** FCC regulation increases market uncertainty (H5) without triggering governance response (H6).

---

## Causal Identification

FCC Rule 37.3 (Sept 28, 2007) requires data breach notification within 30 days—a natural experiment.

**Validation Tests:**
- ✅ **Temporal:** Effects emerge post-2007 only
- ✅ **Balance:** FCC and non-FCC firms comparable pre-2007
- ✅ **Heterogeneity:** Effects vary by firm size (consistent pattern)
- ✅ **Robustness:** Stable across specifications, clustering, and industry controls

---

## Project Structure

```
dissertation-analysis/
├── run_all.py                 # Main pipeline
├── Data/                      # Download from Google Drive (not in Git)
│   ├── raw/                   # Original breaches
│   ├── processed/             # Enriched dataset (1,054 × 83 cols)
│   └── wrds/                  # CRSP/Compustat stock & financial data
├── Notebooks/                 # Analysis notebooks
├── scripts/                   # Data processing & regression scripts
├── Dashboard/                 # Streamlit interactive dashboard
└── outputs/                   # Generated tables, figures, diagnostics
```

---

## Key Outputs

**After running the pipeline:**

### Main Results Tables
- `outputs/tables/TABLE1_COMBINED.txt` — Descriptive statistics
- `outputs/tables/essay2/TABLE2_baseline_disclosure.txt` — Market returns models (5 specs)
- `outputs/tables/essay2/TABLE3_fcc_regulation.txt` — FCC regulation effect
- `outputs/tables/essay3/TABLE2_executive_turnover.txt` — Governance response models (3 specs)

### Causal Identification Tests
- `outputs/tables/essay2/TABLE_B8_post_2007_interaction.txt` — Pre-2007 vs post-2007
- `outputs/tables/essay2/TABLE_FCC_Industry_FE_Comparison.txt` — Industry FE robustness
- `outputs/tables/essay2/TABLE_FCC_Size_Sensitivity.txt` — Firm size heterogeneity

### Robustness & Diagnostics
- `outputs/tables/essay2/TABLE_B9_clustered_vs_hc3_comparison.txt` — Standard errors
- `outputs/tables/essay2/H1_TOST_Equivalence_Test.txt` — Equivalence testing for H1
- `outputs/tables/essay2/DIAGNOSTICS_VIF_summary.txt` — Multicollinearity check

### Heterogeneity Analysis (Essays 1-3)
- `outputs/tables/essay3_governance/CAUSAL_ID_PLACEBO_TESTS.csv` — Placebo tests
- `outputs/tables/essay3_governance/CAUSAL_ID_DOSE_RESPONSE.csv` — Dose-response analysis
- `outputs/tables/essay3_governance/CAUSAL_ID_COVARIATE_BALANCE.csv` — Covariate balance

---

## Methodologies

**Essays 1-3 use:**
- Event study framework (MacKinlay 1997)
- Logistic regression (binary outcomes: turnover)
- OLS with firm-clustered standard errors
- TOST equivalence testing (H1 null hypothesis)
- Robustness: Industry FE, size stratification, alternative windows, bootstrap SEs

**Causal Identification:**
- Natural experiment (FCC Rule 37.3, Sept 28 2007)
- Temporal validation (pre-post 2007 comparison)
- Covariate balance testing
- Parallel trends visualization
- Multiple robustness specifications

---

## Variables

**Dependent Variables:**
- `car_30d` — 30-day cumulative abnormal return (Essay 1)
- `volatility_change` — Change in return volatility post-breach (Essay 2)
- `executive_change_30d` — Binary: CEO departure within 30 days (Essay 3)

**Key Independent Variables:**
- `immediate_disclosure` — Binary: ≤7 days to disclosure
- `fcc_reportable` — Binary: FCC-regulated firm
- `prior_breaches_total` — Firm's all-time breach count
- `health_breach` — Binary: HIPAA-covered data

**Controls:**
- `firm_size_log` — log(market cap at breach)
- `leverage` — debt/assets ratio
- `roa` — net income/total assets

For full variable dictionary: `Data/processed/DATA_DICTIONARY_ENRICHED.csv`

---

## Interactive Dashboard

Explore results interactively:

```bash
streamlit run Dashboard/app.py
```

Navigate through:
1. Research story & questions
2. Natural experiment validation
3. Sample composition
4. Essay 1-3 findings & heterogeneity
5. Cross-essay synthesis
6. Raw data explorer

---

## Sample Composition

| Group | N | % |
|-------|---|---|
| **Total Breaches** | 1,054 | 100% |
| With CRSP price data | 926 | 87.9% |
| With volatility data | 916 | 86.9% |
| With turnover data | 896 | 85.0% |
| **FCC-Regulated** | 200 | 19.0% |
| **Non-FCC** | 854 | 81.0% |
| With prior breaches | 442 | 41.9% |
| Health data breaches | 117 | 11.1% |
| Financial data breaches | 257 | 24.4% |

---

## Citation

```
Spivey, T. D. (2026). Data breach disclosure timing and market reactions. 
Dissertation, University of South Alabama.
```

---

## Questions?

**Contact:** Timothy Spivey  
**Email:** ts2427@jagmail.southalabama.edu

For data access issues or technical questions about the code, see `STREAMLIT_DEPLOYMENT.md` for cloud setup or troubleshooting.

---

## License

This research project is provided as-is for academic use.
