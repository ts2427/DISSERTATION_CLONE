# NLP Validation & Unit Tests Implementation Plan

**Question:** Can NLP validation and unit tests be added without losing existing work?

**Answer:** ✅ **YES - Completely Safe**

Both can be added as **supplementary, non-invasive additions** that read but never modify your existing analysis. Your current work remains 100% intact.

---

## Quick Summary

### What You're Adding

1. **NLP Validation Framework** (4-5 hours work)
   - Sample 150 breaches for manual coding
   - Compare classifier output vs manual codes
   - Generate precision/recall metrics
   - Produces: Validation report + metrics (doesn't change analysis)

2. **Unit Tests** (6-8 hours work)
   - Test core functions (NLP, enrichment, statistics)
   - 70+ tests covering edge cases
   - Run with: `pytest tests/`
   - Produces: Test results (doesn't change analysis)

### Total Implementation: 14-19 hours (can be done in phases)

### Key Guarantee: Zero Risk to Existing Work
- ✅ Script 45 (NLP) unchanged
- ✅ Script 53 (merge) unchanged
- ✅ Analysis notebooks unchanged
- ✅ Results unchanged
- ✅ Outputs unchanged

---

## Part 1: NLP Validation Framework

### What Problem Does It Solve?

Currently:
- NLP classifier uses keyword matching (simple, working)
- No validation against manually coded breaches
- Unknown accuracy/precision/recall
- Hard to justify to committee

With validation:
- Manually code 150 breaches (gold standard)
- Compare classifier vs manual codes
- Report precision/recall/F1 per category
- Document limitations and accuracy

### Architecture (Non-Invasive)

```
EXISTING PIPELINE (unchanged):
script 45 → breach_severity_classification.csv → script 53 → analysis
                                  ↓
                        (used by your analysis)

NEW VALIDATION LAYER (parallel, read-only):
breach_severity_classification.csv ← Read (not modify)
                                  ↓
                    validation/scripts/01_run_nlp_validation.py
                                  ↓
                    Compare vs manual codes (user provides)
                                  ↓
                    Output: precision/recall report
                            (doesn't affect analysis)
```

### Workflow (Step-by-Step)

#### Step 1: Extract Classifier Logic (45 min)

Move core classification from script 45 into reusable module:

```
NEW FILE: validation/nlp_validation/nlp_classifier.py

This module:
- Contains all keyword dicts and weights
- Provides classify_breach_text() function
- Same logic as script 45 (no changes to script 45)
- Can be imported by tests and validation
```

**Key point:** Script 45 is unchanged. We just extract its logic to a shareable module.

#### Step 2: Sample 150 Breaches (1 hr)

Create `validation/scripts/00_sample_breaches_for_validation.py`:

```
Input: FINAL_DISSERTATION_DATASET_ENRICHED.csv (1,054 breaches)
Process:
  - Stratified sampling (ensure all breach types represented)
  - Balanced difficulty (samples from all severity levels)
  - Random selection (unbiased)
Output: sample_breaches_for_coding.csv (150 breaches)
```

#### Step 3: Manual Coding Phase (Variable - You decide)

**What you do:**
1. Open `sample_breaches_for_coding.csv` in Excel
2. For each breach, manually code 10 categories (0/1):
   - pii_breach: Does this involve PII? 1=yes, 0=no
   - health_breach: HIPAA/medical data? 1=yes, 0=no
   - financial_breach: Financial data? 1=yes, 0=no
   - (7 more categories)
3. Save as `manual_codes_2026_01_22.csv`

**Time estimate:**
- 150 breaches × 2-3 min each = 5-7.5 hours
- Or split with 2-3 people (faster)
- Include confidence scores (1-5) if desired

**Best practice:**
- Use 2 independent coders to calculate inter-rater reliability (Cohen's Kappa)
- Discuss disagreements to reach consensus

#### Step 4: Run Validation Analysis (1 hr)

Create `validation/scripts/01_run_nlp_validation.py`:

```python
# Pseudo-code
nlp_classifications = read_csv('Data/enrichment/breach_severity_classification.csv')
manual_codes = read_csv('manual_codes_2026_01_22.csv')

# Compare each category
for category in ['pii_breach', 'health_breach', ...]:
    y_true = manual_codes[category]           # Gold standard
    y_pred = nlp_classifications[category]    # Your classifier

    # Calculate metrics
    precision = TP / (TP + FP)
    recall = TP / (TP + FN)
    f1_score = 2 * (precision * recall) / (precision + recall)

    # Output
    print(f"{category}: Prec={precision:.2f} Recall={recall:.2f} F1={f1:.2f}")
```

**Output:**
```
=====================================
VALIDATION REPORT
Sample: 150 breaches (14.2% of dataset)
=====================================

Overall Metrics:
  - Weighted F1: 0.847
  - Accuracy: 0.873

Per-Category Performance:
  pii_breach:        Precision=0.92  Recall=0.88  F1=0.90  ✓
  health_breach:     Precision=0.95  Recall=0.91  F1=0.93  ✓
  financial_breach:  Precision=0.81  Recall=0.75  F1=0.78  ⚠️
  ransomware:        Precision=0.88  Recall=0.84  F1=0.86  ✓
  (... more categories)

RECOMMENDATIONS:
- financial_breach needs more keywords (low recall)
- Overall performance is good (F1 > 0.84)
```

#### Step 5: Report & Visualization (1.5 hrs)

Create `validation/scripts/02_generate_validation_report.py` and `03_visualize_confusion_matrices.py`:

**Output:**
- `validation_results/validation_report_2026_01_22.html` (HTML report)
- `validation_results/confusion_matrices/` (heatmaps for each category)
- `validation_results/validation_metrics.json` (machine-readable metrics)

### Key Files to Create

```
NEW DIRECTORY STRUCTURE:

validation/
├── README_VALIDATION.md                    # User guide
├── nlp_validation/
│   ├── __init__.py
│   ├── nlp_classifier.py                   # Extracted from script 45
│   ├── manual_coding_template.xlsx         # For manual coders
│   └── sample_breaches_for_coding.csv      # Output from step 2
└── scripts/
    ├── 00_sample_breaches_for_validation.py
    ├── 01_run_nlp_validation.py
    ├── 02_generate_validation_report.py
    └── 03_visualize_confusion_matrices.py

validation_results/
├── validation_report_2026_01_22.html
├── validation_metrics.json
└── confusion_matrices/
    ├── pii_breach_confusion.png
    ├── health_breach_confusion.png
    └── ... (8 more)
```

### Does This Change Your Analysis?

**NO.**

```
❌ DOES NOT change:
- Script 45 (NLP classifier)
- Enrichment files in Data/enrichment/
- Analysis notebooks
- Results in outputs/
- Statistical conclusions

✅ DOES provide:
- Validation report (purely informational)
- Confidence intervals on classifications
- Evidence of classifier accuracy
- Documentation of limitations
```

---

## Part 2: Unit Tests

### What Problem Does It Solve?

Currently:
- Hard to know if code changes break anything
- No automated verification of edge cases
- Difficult to refactor with confidence
- Difficult for committee to verify correctness

With tests:
- Automated verification of core functions
- Catch regressions when code changes
- Document expected behavior
- Build confidence in code

### Test Architecture (Non-Invasive)

```
tests/
├── unit/                           # Test individual functions
│   ├── test_nlp_classifier.py     (12 tests)
│   ├── test_data_validation.py    (8 tests)
│   ├── test_enrichment_functions.py (15 tests)
│   ├── test_statistical_calculations.py (10 tests)
│   └── test_data_quality.py       (8 tests)
│
├── integration/                    # Test workflows
│   ├── test_nlp_pipeline.py       (5 tests)
│   ├── test_enrichment_merge.py   (5 tests)
│   └── test_analysis_workflow.py  (4 tests)
│
└── fixtures/                       # Test data
    ├── test_breaches_sample.csv
    ├── conftest.py                # Shared fixtures
    └── README_TESTING.md          # User guide

Total: ~70 tests
Time to run: 2-3 minutes
Time to write: 6-8 hours
```

### What to Test

#### Category A: NLP Classifier Functions

```python
# Test: classify_breach_text()
Test case 1: None/NaN input → returns dict of zeros
Test case 2: "Social security number" → detects pii_breach
Test case 3: "HIPAA violation" → detects health_breach
Test case 4: "Ransomware encrypted files" → detects ransomware
Test case 5: Mixed case ("HIPAA" vs "hipaa") → same result
Test case 6: Multiple breach types → detects all
Test case 7: Empty string → returns zeros
```

#### Category B: Enrichment Functions

```python
# Test: calculate_prior_breaches()
Test case 1: First breach by org → prior_breaches_total = 0
Test case 2: Company with 3 prior breaches → correct count
Test case 3: Prior breaches in 1yr window → correct
Test case 4: Prior breaches in 3yr window → correct
Test case 5: days_since_last_breach calculated → correct
```

#### Category C: Statistical Functions

```python
# Test: calculate_volatility_change()
Test case 1: volatility increased → volatility_change > 0
Test case 2: volatility decreased → volatility_change < 0
Test case 3: No change → volatility_change = 0
Test case 4: Large values don't overflow → handles correctly
```

#### Category D: Data Validation

```python
# Test: validate_dataset()
Test case 1: Required columns present → pass
Test case 2: Duplicate breach_ids → fail
Test case 3: Dates out of range → catch
Test case 4: Numeric column non-numeric → catch
Test case 5: Negative metrics → catch
```

#### Category E: Merge Logic

```python
# Test: merge_enrichments()
Test case 1: Correct merge (1:1) → row count preserved
Test case 2: No duplicate columns → pass
Test case 3: NaN values handled → correctly
Test case 4: Invalid merge (1:many) → error caught
```

### Example: NLP Classifier Tests

```python
# File: tests/unit/test_nlp_classifier.py

import pytest
from validation.nlp_validation.nlp_classifier import BreachClassifier

class TestBreachClassifier:

    @pytest.fixture
    def classifier(self):
        return BreachClassifier()

    def test_null_input_returns_zeros(self, classifier):
        """None input should return dict of zeros"""
        result = classifier.classify_breach_text(None)
        assert all(v == 0 for v in result.values())

    def test_pii_keyword_detected(self, classifier):
        """Should detect PII keywords"""
        text = "Social security number exposed"
        result = classifier.classify_breach_text(text)
        assert result['pii_breach'] == 1

    def test_health_keyword_detected(self, classifier):
        """Should detect health/HIPAA keywords"""
        text = "HIPAA medical records breach"
        result = classifier.classify_breach_text(text)
        assert result['health_breach'] == 1

    def test_case_insensitive(self, classifier):
        """Should handle mixed case"""
        lower = classifier.classify_breach_text("hipaa")
        upper = classifier.classify_breach_text("HIPAA")
        assert lower == upper

    def test_multiple_types_detected(self, classifier):
        """Should detect multiple breach types"""
        text = "Ransomware encrypted HIPAA medical records"
        result = classifier.classify_breach_text(text)
        assert result['ransomware'] == 1
        assert result['health_breach'] == 1
```

### How to Run Tests

```bash
# Install test dependencies (already in pyproject.toml)
uv sync --all-extras

# Run all tests
pytest tests/

# Run specific category
pytest tests/unit/
pytest tests/integration/

# Run with verbose output
pytest tests/ -v

# Run single test
pytest tests/unit/test_nlp_classifier.py::TestBreachClassifier::test_pii_keyword_detected

# Run with coverage report
pytest tests/ --cov=validation

# Stop on first failure
pytest tests/ -x

# Show print statements
pytest tests/ -s
```

### Test Configuration

**File: `pytest.ini`**

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_functions = test_*
addopts = -v --tb=short

markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow tests (>1 sec)
```

### Does This Change Your Analysis?

**NO.**

```
❌ DOES NOT change:
- Any analysis code
- Results
- Outputs
- Methods

✅ DOES provide:
- Confidence that functions work correctly
- Regression detection if code changes
- Documentation of expected behavior
- Professional development practice
```

---

## Implementation Timeline

### Phase 1: Setup (2-3 hours)
- Extract NLP classifier to module: 45 min
- Create directory structure: 15 min
- Write pytest fixtures: 30 min
- Create test data: 30 min

### Phase 2: NLP Validation (4-5 hours)
- Sampling script: 1 hr
- Validation analysis script: 1.5 hrs
- Report generation: 1 hr
- Visualization: 1 hr

### Phase 3: Unit Tests (6-8 hours)
- NLP classifier tests: 1.5 hrs
- Data validation tests: 1 hr
- Enrichment tests: 1.5 hrs
- Statistical tests: 1 hr
- Integration tests: 1.5 hrs

### Phase 4: Documentation (1-2 hours)
- README files: 1 hr
- Examples: 1 hr

**Total: 13-18 hours (can be done in phases)**

---

## Can They Be Done in Phases?

**YES - Absolutely**

### Option 1: Validation First (Recommended)
```
Week 1-2: NLP Validation (4-5 hrs work)
  ✓ Higher priority (answers committee question about accuracy)
  ✓ Required for dissertation methodology
  ✓ Provides immediate value

Week 3+: Unit Tests (6-8 hrs work)
  ✓ Nice-to-have (but good practice)
  ✓ Useful for maintenance
  ✓ Can be done incrementally
```

### Option 2: Minimal Version
```
NLP Validation (simplified): 2-3 hours
- Sample 50-100 breaches instead of 150
- Manual coding only (skip inter-rater reliability)
- Basic metrics only (skip visualizations)

Unit Tests (core only): 2-3 hours
- Just test NLP classifier
- Skip enrichment/statistical tests
```

### Option 3: No Tests (Validation Only)
```
If time-constrained:
- Do NLP validation (4-5 hrs) ✓ Critical
- Skip unit tests (nice-to-have)
- Both are safe to skip analysis
```

---

## Critical Safety Guarantees

### Your Analysis is 100% Safe Because:

1. **Tests are read-only**
   - Never modify data
   - Never change outputs
   - Never alter results

2. **Validation is supplementary**
   - Compares against existing outputs
   - Doesn't change analysis pipeline
   - Produces separate report

3. **Extraction of NLP logic**
   - Script 45 can remain unchanged
   - Or update to import from module (safer)
   - Either way, no behavior change

4. **No modification of:**
   - Analysis notebooks
   - Data processing scripts
   - Results or outputs
   - Any part of dissertation

### How to Verify Nothing Changed

```bash
# Before starting
git status                      # Note current state
git log --oneline -n 10         # Note commits

# After adding tests/validation
# - NO changes to notebooks/
# - NO changes to scripts/ (except extraction)
# - NO changes to data/
# - ONLY new files in tests/ and validation/

git diff HEAD~1 HEAD            # Should show only additions
git status                      # Should only show new files
```

---

## When to Do This

### Critical Path (Must have for dissertation):
1. ✅ Fix Git LFS config (.gitattributes) - 5 min
2. ✅ Create cloud data folder - 30 min
3. ✅ Finalize README - Already done

### High Priority (Strengthens dissertation):
4. ⏳ NLP Validation (4-5 hrs) - Recommended before final submission
5. ⏳ Unit Tests (6-8 hrs) - Nice-to-have

### Medium Priority (Nice-to-have):
6. ⏳ CI/CD integration - Optional
7. ⏳ Coverage reports - Optional

---

## Getting Started (If You Decide to Proceed)

### Step 1: Decide Scope
- [ ] Full validation + tests (13-18 hrs total)
- [ ] Validation only (4-5 hrs)
- [ ] Skip for now, focus on dissertation writing

### Step 2: If Proceeding - Create Structure
```bash
# Create directories
mkdir -p validation/nlp_validation validation/scripts
mkdir -p tests/unit tests/integration tests/fixtures
mkdir -p validation_results/confusion_matrices
```

### Step 3: Extract NLP Classifier
```bash
# Create: validation/nlp_validation/nlp_classifier.py
# Copy keyword dicts and classify_breach_text() function from scripts/45_breach_severity_nlp.py
# Add type hints and docstrings
```

### Step 4: Create Sampling Script
```bash
# Create: validation/scripts/00_sample_breaches_for_validation.py
# Stratified sample of 150 breaches
# Output: sample_breaches_for_coding.csv
```

### Step 5: Run Validation
```bash
python validation/scripts/01_run_nlp_validation.py \
    --manual-codes manual_codes_2026_01_22.csv \
    --output validation_results/report.html
```

---

## FAQ

**Q: Will tests slow down my analysis?**
A: No. Tests run separately (`pytest tests/`). Analysis pipeline (`python run_all.py`) is unaffected.

**Q: What if a test fails?**
A: Tests are informational. If a test fails, it means the tested function doesn't behave as expected. You'd fix the function or adjust the test. Never affects analysis itself.

**Q: Do I have to do manual coding?**
A: If you want NLP validation, yes. But it's optional work, not required. You could skip validation and just do unit tests.

**Q: Can I do partial implementation?**
A: Yes. Validation and tests are independent. You could do validation only, tests only, or both.

**Q: Will this impact my results?**
A: Not at all. Tests don't run during analysis. Validation just compares existing outputs. Analysis results are completely untouched.

**Q: How do I explain this to my committee?**
A: "I added automated validation of the NLP classifier against manually coded breaches, achieving an F1-score of X across all categories. I also wrote unit tests to verify code correctness."

---

## Summary: Is It Safe?

### 🟢 YES - Completely Safe

- ✅ Existing code untouched (or optionally improved via refactoring)
- ✅ Existing results unchanged
- ✅ Tests/validation don't affect analysis pipeline
- ✅ Can skip if time constraints critical
- ✅ Can be added in phases
- ✅ Can be reverted easily if needed

### Bottom Line

These are **supplementary professional development additions** to a working research pipeline. They strengthen your dissertation but don't change anything about your analysis. Think of them as "defensive" work - verifying that what you've already done is correct.

---

**Questions? See:**
- FEEDBACK_REVIEW.md - Overall feedback status
- README.md - Project overview
- UV_SETUP_GUIDE.md - Environment setup
- This document - NLP/testing details

