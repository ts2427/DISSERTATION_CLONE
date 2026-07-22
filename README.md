# Data Breach Disclosure Timing and Market Reactions

**Author:** Timothy D. Spivey  
**Institution:** University of South Alabama  
**Year:** 2026

---

## Executive Summary

This dissertation analyzes how data breach disclosure timing and regulatory requirements affect stock market reactions, information asymmetry, and governance response using a natural experiment design.

**Core Finding:** Markets penalize *who you are* (regulatory status), not *when you disclose*. FCC regulation imposes both information asymmetry costs (volatility) and governance disruption (executive turnover), with heterogeneous effects by firm size.

**Sample:** 784 breaches (Cencora-deduplicated, 2006-2025) | 677 with CRSP market data | 141 FCC-regulated firms | Natural experiment: FCC Rule 37.3 (Sept 28, 2007)

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

| Essay | Hypothesis | Result | Interpretation |
|-------|-----------|--------|-----------------|
| **1** | H1: Timing Effect | +0.8394% (p=0.3504, NS) | Disclosure speed does NOT matter for stock returns |
| **1** | H2: FCC Regulation | -2.1179% (p=0.0494**) | FCC firms suffer 2.1% abnormal return penalty |
| **2** | H5: Volatility (FCC) | +1.793% (p=0.0487*) | Small firms: +7.31% (p=0.003); Large firms: -3.39% (p=0.015) |
| **3** | H6: Executive Turnover | Odds ratio 0.518 (p=0.007***) | Immediate disclosure REDUCES 30-day turnover risk by 48% |

**Integration:** Markets penalize FCC regulation directly (-2.1% returns) AND indirectly (through volatility shock). Governance responds via executive displacement, not mediated by volatility.

Sample: N=653 regression observations | HC3 robust standard errors (primary)

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

### 📊 CANONICAL RESULTS (START HERE)
- **`outputs/CANONICAL_RESULTS_SUMMARY_20260722.txt`** — Complete Essay 1-3 verified results, heterogeneity analysis, defense positioning

### Main Results Tables
- `outputs/tables/TABLE1_COMBINED.txt` — Descriptive statistics (n=784)
- `outputs/tables/essay2/TABLE2_baseline_disclosure.txt` — H1: Disclosure timing effect (HC3 robust SEs)
- `outputs/tables/essay2/TABLE3_fcc_regulation.txt` — H2: FCC regulation effect (HC3 robust SEs)
- `outputs/tables/essay2/TABLE_B9_clustered_vs_hc3_comparison.txt` — **PRIMARY: All H1-H4 full specification with HC3 vs clustered comparison**
- `outputs/tables/essay3_governance/TABLE2_turnover_summary.csv` — H6: Executive turnover (30/90/180-day windows)

### Causal Identification & Robustness
- `outputs/tables/essay2/TABLE_FCC_Industry_FE_Comparison.txt` — Industry FE robustness
- `outputs/tables/essay2/TABLE_FCC_Size_Sensitivity.txt` — Firm size heterogeneity
- `outputs/tables/essay2/H1_TOST_Equivalence_Test.txt` — Equivalence testing confirms H1 null
- `outputs/tables/essay2/DIAGNOSTICS_VIF_summary.txt` — Multicollinearity verification

### Heterogeneity Analysis
- `outputs/tables/essay3/TABLE2_volatility_changes.txt` — H5: Volatility by firm size quartiles
- `outputs/tables/essay3_governance/mediation_bootstrap_indirect_effects.csv` — Mediation analysis (volatility does NOT mediate timing→turnover)

---

## Methodologies

**Essays 1-3 use:**
- Event study framework (MacKinlay 1997) for abnormal returns
- OLS regression with HC3 heteroskedasticity-consistent robust standard errors (primary)
- Alternative: Firm-level clustered SEs (for robustness comparison in TABLE B9)
- Logistic regression for binary outcomes (executive turnover)
- TOST equivalence testing (H1: demonstrates timing effect is null AND economically negligible)
- Full specification testing: All four hypothesis predictors included simultaneously to isolate each effect

**Robustness Checks:**
- Industry fixed effects (12 SIC groups)
- Firm size stratification (quartiles)
- Alternative event windows (5-day, 30-day, 60-day CAR)
- Bootstrap mediation analysis (does volatility mediate timing→turnover? No)
- Placebo tests (pre-FCC era)

**Causal Identification:**
- Natural experiment: FCC Rule 37.3 (Sept 28, 2007) mandates 30-day breach notification
- Temporal validation: Pre-2007 effects zero (parallel trends confirmed)
- FCC classification: SIC-code based (4813=Telephone, 4841=Cable, 4899=VoIP) — NOT name-string matching
- Covariate balance: FCC and non-FCC firms comparable pre-2007

---

## Variables

**Dependent Variables:**
- `car_30d` — 30-day cumulative abnormal return (Essay 1)
- `volatility_change` — Change in return volatility post-breach (Essay 2)
- `executive_change_30d` — Binary: CEO departure within 30 days (Essay 3)

**Key Independent Variables:**
- `immediate_disclosure` — Binary: ≤7 days to disclosure (24.5% of sample)
- `fcc_reportable` — Binary: FCC-regulated telecom/cable firm (SIC 4813/4841/4899, 18% of sample)
- `prior_breaches_1yr` — Count: Firm's breaches in prior year
- `health_breach` — Binary: HIPAA-covered (PHI) data (6.1% of sample)

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
| **Total Breaches (Cencora-deduplicated)** | 784 | 100% |
| With CRSP price data | 677 | 86.4% |
| Regression sample (complete data) | 653 | 83.3% |
| **FCC-Regulated** (SIC 4813/4841/4899) | 141 | 18.0% |
| **Non-FCC** | 643 | 82.0% |
| Immediate Disclosure (≤7 days) | 192 | 24.5% |
| Delayed Disclosure (>30 days) | 470 | 60.0% |
| With prior breaches | 331 | 42.2% |
| Health data breaches | 48 | 6.1% |
| Financial data breaches | 202 | 25.8% |

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
