# NLP Validation & Unit Testing Guide

This document describes the validation framework and unit tests added to the dissertation project.

## Overview

The validation and testing framework provides:
- **NLP Classifier Validation**: Quantifies accuracy of breach classification
- **Unit Tests**: 93 comprehensive tests ensuring code quality
- **Test Fixtures**: Reusable test data via pytest fixtures
- **Automated Reporting**: HTML and markdown validation reports

**Key Guarantee**: All additions are non-invasive. Existing analysis code, data, and results remain unchanged.

## Quick Start

### Run All Unit Tests

```bash
uv run pytest tests/ -v
```

Expected output: **93 tests passed**

### Run Specific Test Category

```bash
uv run pytest tests/unit/test_nlp_classifier.py -v    # NLP classifier tests (54 tests)
uv run pytest tests/unit/test_data_validation.py -v   # Data validation tests (39 tests)
```

### Run Tests by Marker

```bash
uv run pytest tests/ -m unit -v          # Only unit tests
uv run pytest tests/ -m validation -v    # Only validation tests
```

## Directory Structure

```
validation/
├── nlp_validation/
│   ├── __init__.py
│   ├── nlp_classifier.py         # Core BreachClassifier class
│   ├── manual_coding_template.xlsx
│   └── sample_breaches_for_coding.csv  # Output from script 00
└── scripts/
    ├── 00_sample_breaches_for_validation.py
    ├── 01_run_nlp_validation.py
    └── 02_generate_validation_report.py

tests/
├── conftest.py                   # Pytest fixtures
├── unit/
│   ├── test_nlp_classifier.py    # 54 tests
│   └── test_data_validation.py   # 39 tests
└── integration/
    └── (planned for future)

validation_results/              # Output directory
├── validation_metrics.json
├── validation_summary.csv
├── VALIDATION_REPORT.md
└── validation_report.html
```

## Validation Workflow

### Step 1: Sample Breaches for Manual Coding

```bash
python validation/scripts/00_sample_breaches_for_validation.py
```

**Output**: `validation/nlp_validation/sample_breaches_for_coding.csv`

This script:
- Samples 150 representative breaches from the dataset
- Stratifies by severity quartiles (ensures balanced representation)
- Creates a CSV with empty columns for manual coding

**Columns to manually code** (0=No, 1=Yes):
- `pii_breach`: Personally identifiable information
- `health_breach`: Protected health information (HIPAA)
- `financial_breach`: Financial account/payment data
- `ip_breach`: Intellectual property or trade secrets
- `ransomware`: Ransom/encryption attack
- `nation_state`: Nation-state or advanced persistent threat
- `insider_threat`: Employee or insider involvement
- `ddos_attack`: Denial of service attack
- `phishing`: Phishing or social engineering
- `malware`: Malware, virus, trojan, etc.

### Step 2: Run NLP Validation

After manually coding the breaches (save as `manual_codes_2026_01_22.csv`):

```bash
python validation/scripts/01_run_nlp_validation.py --manual-codes manual_codes_2026_01_22.csv
```

**Outputs**:
- `validation_results/validation_metrics.json`: Raw metrics (JSON)
- `validation_results/validation_summary.csv`: Per-category summary (CSV)

**Metrics calculated**:
- Per-category: Precision, Recall, F1-score, sample counts
- Overall: Weighted precision, recall, F1, accuracy

### Step 3: Generate Report

```bash
python validation/scripts/02_generate_validation_report.py
```

**Outputs**:
- `validation_results/VALIDATION_REPORT.md`: Markdown report
- `validation_results/validation_report.html`: Interactive HTML report

## Unit Tests

### Test Files

#### test_nlp_classifier.py (54 tests)

Tests the `BreachClassifier` class:

**TestBreachClassifierInit** (4 tests)
- Initialization and data structure validation

**TestClassifyBreachText** (13 tests)
- Keyword matching for each breach type
- Case insensitivity
- Null/empty value handling
- Multiple breach types in single text

**TestCalculateRecordsSeverity** (9 tests)
- Severity scoring based on record counts
- Boundary value testing (1000, 10000, 100000, 1000000 records)

**TestClassifyBreach** (9 tests)
- Full breach row classification
- Severity score calculation
- Complex breach flag

**TestClassifyDataFrame** (7 tests)
- Batch classification of entire dataframes
- Consistency between individual and batch classification

**TestValidateKeywords** (6 tests)
- Keyword dictionary validation

**TestEdgeCases** (5 tests)
- Very long text, special characters, unicode
- Negative/very large record counts

#### test_data_validation.py (39 tests)

Tests data quality and integrity:

**TestDataFrameStructure** (3 tests)
- Column presence and data types

**TestMissingValues** (4 tests)
- Null/NaN handling

**TestNumericFields** (4 tests)
- Numeric field validation and boundaries

**TestCategoricalFields** (3 tests)
- Categorical value validation

**TestDateFields** (3 tests)
- Date format and chronological order

**TestTextFields** (4 tests)
- Text field length and content validation

**TestDataConsistency** (3 tests)
- Row consistency and data integrity

**TestBoundaryValues** (5 tests)
- Boundary condition testing for severity scoring

**TestDataIntegrity** (4 tests)
- No corruption, independence of fixtures

**TestDataFiltering** (3 tests)
- Filtering operations preserve structure

**TestDataAggregation** (3 tests)
- Aggregation operations

### Pytest Fixtures (conftest.py)

Available fixtures for use in tests:

```python
@pytest.fixture
def classifier():
    """BreachClassifier instance"""

@pytest.fixture
def sample_breach_row():
    """Sample breach as pandas Series"""

@pytest.fixture
def sample_health_breach_row():
    """Health breach example"""

@pytest.fixture
def sample_financial_breach_row():
    """Financial breach example"""

@pytest.fixture
def sample_dataframe():
    """DataFrame with 5 diverse breach examples"""

@pytest.fixture
def empty_dataframe():
    """Empty dataframe for edge case testing"""

@pytest.fixture
def null_values_dataframe():
    """DataFrame with missing values"""

@pytest.fixture
def sample_metrics_dict():
    """Sample validation metrics dictionary"""

@pytest.fixture
def output_dir(tmp_path):
    """Temporary directory for test outputs"""
```

### Example Test Usage

Run tests with different verbosity levels:

```bash
# Verbose output with test names
uv run pytest tests/ -v

# Very verbose with assertion details
uv run pytest tests/ -vv

# Quiet output (only pass/fail counts)
uv run pytest tests/ -q

# Show print statements during tests
uv run pytest tests/ -s

# Stop on first failure
uv run pytest tests/ -x

# Run last failed tests only
uv run pytest tests/ --lf

# Run failed tests first
uv run pytest tests/ --ff
```

## Architecture

### BreachClassifier Class

Located in `validation/nlp_validation/nlp_classifier.py`

**Methods**:

```python
class BreachClassifier:
    # Text classification
    def classify_breach_text(text) -> Dict[str, int]
        """Classify text for breach keywords. Returns {breach_type: 0/1}"""

    # Severity calculation
    def _calculate_records_severity(records_affected) -> int
        """Calculate severity score (0-5) based on record count"""

    # Single breach classification
    def classify_breach(row, text_columns=None) -> Dict
        """Full classification of single breach row"""

    # Batch classification
    def classify_dataframe(df, text_columns=None) -> DataFrame
        """Classify entire dataframe"""

    # Validation
    @staticmethod
    def validate_keywords(keywords_dict) -> bool
        """Validate keyword dictionary structure"""
```

**Keywords Dictionary**:
- 10 breach categories with keyword lists each
- Keywords match substrings (case-insensitive)
- Can be customized for different datasets

**Sensitivity Weights**:
- Used to calculate severity_score
- health_breach has highest weight (4)
- ddos_attack has lowest weight (1)

### Validation Workflow

```
Raw Data
   ↓
[00] Sample 150 breaches (stratified)
   ↓
Manual Coding (0=No, 1=Yes for each breach type)
   ↓
[01] Compare NLP output vs manual codes
   ↓
Calculate metrics (precision, recall, F1)
   ↓
[02] Generate HTML/markdown reports
   ↓
Review classifier accuracy & adjust keywords if needed
```

### Non-Invasive Design

The validation framework is completely separate from analysis:

```
analysis/
├── notebooks/         <- Original analysis (unchanged)
├── scripts/           <- Original scripts (unchanged)
└── outputs/          <- Original results (unchanged)

validation/           <- NEW: Validation layer
├── nlp_validation/   <- NLP classifier module
└── scripts/          <- Validation scripts (read-only to analysis output)

tests/                <- NEW: Unit tests
├── unit/
└── integration/

validation_results/   <- NEW: Validation output
```

**Key Properties**:
- Validation scripts READ from analysis outputs
- Validation scripts NEVER MODIFY analysis data/results
- Unit tests import BreachClassifier but don't change it
- Tests run independently with `pytest`, not part of analysis pipeline

## Metrics Explained

### Precision
**Definition**: Of predicted positives, how many were correct?
**Formula**: TP / (TP + FP)
**Range**: 0-1 (higher is better)
**Use**: When false positives are costly

### Recall
**Definition**: Of actual positives, how many did we find?
**Formula**: TP / (TP + FN)
**Range**: 0-1 (higher is better)
**Use**: When false negatives are costly

### F1-Score
**Definition**: Harmonic mean of precision and recall
**Formula**: 2 * (precision * recall) / (precision + recall)
**Range**: 0-1 (higher is better)
**Use**: When you want balance between precision and recall

### Accuracy
**Definition**: Overall correctness across all samples
**Formula**: (TP + TN) / (TP + TN + FP + FN)
**Range**: 0-1 (higher is better)
**Use**: When classes are balanced

### Confusion Matrix
Shows all combinations of actual vs predicted:

```
                Predicted Positive    Predicted Negative
Actual Positive      TP                     FN
Actual Negative      FP                     TN
```

Where:
- TP = True Positive (correct detection)
- TN = True Negative (correct non-detection)
- FP = False Positive (false alarm)
- FN = False Negative (missed case)

## Performance Interpretation

| F1-Score | Interpretation |
|----------|---|
| > 0.85 | Excellent - high precision and recall |
| 0.75-0.85 | Good - acceptable for production |
| 0.65-0.75 | Acceptable - may need refinement |
| < 0.65 | Poor - needs significant improvement |

## Extending the Framework

### Add Custom Keywords

Modify `BREACH_KEYWORDS` in `nlp_classifier.py`:

```python
BREACH_KEYWORDS = {
    'your_category': ['keyword1', 'keyword2', 'phrase'],
    # ... other categories
}
```

### Add New Tests

Create new test files in `tests/unit/`:

```python
import pytest
from validation.nlp_validation import BreachClassifier

@pytest.mark.unit
class TestNewFeature:
    def test_something(self, classifier):
        result = classifier.classify_breach_text("test text")
        assert result['pii_breach'] == 1
```

### Integration Tests

Create integration tests in `tests/integration/`:

```python
@pytest.mark.integration
def test_full_pipeline():
    # Test entire workflow
    pass
```

## Troubleshooting

### pytest not found
```bash
uv pip install pytest
```

### ModuleNotFoundError: validation
Ensure you're running from project root directory

### Validation metrics not found
Run `01_run_nlp_validation.py` first before generating report

### Tests failing
Check that fixtures are properly imported in conftest.py

## Performance Notes

- 93 unit tests: ~1.5 seconds
- Sample script: ~5 seconds
- Validation script: ~10 seconds (depends on file sizes)
- Report generation: ~2 seconds

## Further Reading

- Pytest documentation: https://docs.pytest.org/
- Scikit-learn metrics: https://scikit-learn.org/stable/modules/metrics.html
- Pandas documentation: https://pandas.pydata.org/

## Summary

The validation and testing framework provides:

✅ **Comprehensive Unit Tests** (93 tests, 100% pass rate)
✅ **NLP Validation Workflow** (stratified sampling, metric calculation)
✅ **Automated Reporting** (HTML and markdown reports)
✅ **Non-Invasive Architecture** (zero impact on existing work)
✅ **Reusable Components** (BreachClassifier can be imported and used anywhere)

All components work together to ensure data quality, code reliability, and classifier accuracy.
