# MANUAL DATA PIPELINE RUNSHEET - 1,054 ROWS

**Goal:** Process data from 1,054 raw breaches → 1,054 enriched dataset (with analysis sample flags)

**DO NOT DELETE ANY FILES BETWEEN STEPS - Keep intermediate outputs**

---

## STEP 0: VERIFY STARTING DATA
```bash
cd C:\Users\mcobp\OneDrive\Desktop\DISSERTATION_CLONE
python -c "import pandas as pd; df=pd.read_excel('Data/DataBreaches.xlsx'); print(f'✓ Raw data: {len(df)} rows')"
```
**Expected:** `1054 rows`

---

## STEP 1: COMPANY-TO-VENDOR MATCHING
**Script:** `scripts/03_company_matching.py`
**Input:** Data/DataBreaches.xlsx (1,054 rows)
**Output:** Data/processed/company_vendor_matching.xlsx
**Command:**
```bash
python scripts/03_company_matching.py
```
**Verify Output:**
```bash
python -c "import pandas as pd; df=pd.read_excel('Data/processed/company_vendor_matching.xlsx'); print(f'✓ Vendor matching: {len(df)} rows')"
```
**Expected:** `~400+ rows` (unique company-vendor pairs)

---

## STEP 2: CREATE MASTER DATASET WITH CVE DATA
**Script:** `scripts/06_create_master_dataset.py`
**Input:** Data/DataBreaches.xlsx (1,054 rows) + vendor matches from Step 1
**Output:** `Data/processed/master_breach_dataset.xlsx`
**Command:**
```bash
python scripts/06_create_master_dataset.py
```
**Verify Output:**
```bash
python -c "import pandas as pd; df=pd.read_excel('Data/processed/master_breach_dataset.xlsx'); print(f'✓ Master dataset: {len(df)} rows, {len(df.columns)} cols')"
```
**Expected:** `1054 rows, 18 columns`
**CHECK:** Verify the output includes columns like: org_name, breach_date, total_cves, cves_1yr_before, etc.

---

## STEP 3: COPY TO FINAL ANALYSIS DATASET
(Skip yfinance - use WRDS data instead)

**Script:** Manual copy
**Command:**
```bash
copy Data/processed/master_breach_dataset.xlsx Data/processed/final_analysis_dataset.xlsx
```
**Verify:**
```bash
python -c "import pandas as pd; df=pd.read_excel('Data/processed/final_analysis_dataset.xlsx'); print(f'✓ Final analysis: {len(df)} rows')"
```
**Expected:** `1054 rows`

---

## STEP 4: FINAL COMPREHENSIVE MERGE (WITH WRDS DATA)
**Script:** `scripts/20_final_comprehensive_merge.py`
**Inputs:**
- Data/processed/final_analysis_dataset.xlsx (1,054 rows)
- Data/wrds/crsp_daily_returns.csv (already downloaded)
- Data/wrds/compustat_fundamentals.csv (already downloaded)
- Data/wrds/compustat_annual.csv (already downloaded)
- Data/wrds/market_indices.csv (already downloaded)

**Output:** `Data/processed/FINAL_DISSERTATION_DATASET.xlsx`
**Command:**
```bash
python scripts/20_final_comprehensive_merge.py
```
**Verify Output:**
```bash
python -c "import pandas as pd; df=pd.read_excel('Data/processed/FINAL_DISSERTATION_DATASET.xlsx'); print(f'✓ Comprehensive merge: {len(df)} rows'); print(f'  - CAR columns: {\"car_5d\" in df.columns}'); print(f'  - CRSP data: {df[\"has_crsp_data\"].sum()} rows marked True'); print(f'  - Complete data: {df[\"has_complete_data\"].sum()} rows marked True')"
```
**Expected:**
- `1054 rows` total (NO FILTERING)
- `car_5d`, `car_30d`, `bhar_5d`, `bhar_30d` columns present
- `has_crsp_data` should be TRUE for ~926 rows
- `has_complete_data` should be TRUE for ~736 rows

**IMPORTANT:** This file should have ALL 1,054 rows, just with flags indicating which rows have complete data for analysis

---

## STEP 5: RUN ENRICHMENT PIPELINE
**Script:** `scripts/40_MASTER_enrichment.py`
**Inputs:** Data/processed/FINAL_DISSERTATION_DATASET.xlsx (1,054 rows)
**Outputs:** 6 CSV files in Data/enrichment/ folder:
- prior_breach_history.csv
- industry_adjusted_returns.csv
- institutional_ownership.csv
- breach_severity_classification.csv
- executive_changes.csv
- regulatory_enforcement.csv

**Command:**
```bash
python scripts/40_MASTER_enrichment.py
```
**Each enrichment script will:**
- Read FINAL_DISSERTATION_DATASET.xlsx (1,054 rows)
- Create enrichment metrics
- Save CSV with 1,054 rows (one row per breach)

**Verify Each Output:**
```bash
python -c "
import pandas as pd
import os

enrichment_files = [
    'Data/enrichment/prior_breach_history.csv',
    'Data/enrichment/industry_adjusted_returns.csv',
    'Data/enrichment/institutional_ownership.csv',
    'Data/enrichment/breach_severity_classification.csv',
    'Data/enrichment/executive_changes.csv',
    'Data/enrichment/regulatory_enforcement.csv'
]

for f in enrichment_files:
    if os.path.exists(f):
        df = pd.read_csv(f)
        print(f'{f.split(\"/\")[-1]:40s}: {len(df)} rows')
    else:
        print(f'{f.split(\"/\")[-1]:40s}: MISSING')
"
```
**Expected:** Each file should have `1054 rows`

---

## STEP 6: FINAL MERGE OF ALL ENRICHMENTS
**Script:** `scripts/53_merge_CONFIRMED_enrichments.py`
**Input:**
- Data/processed/FINAL_DISSERTATION_DATASET.xlsx (1,054 rows)
- All 6 enrichment CSVs from Step 5 (each 1,054 rows)

**Output:** `Data/processed/FINAL_DISSERTATION_DATASET_ENRICHED.csv` and `.xlsx`

**Command:**
```bash
python scripts/53_merge_CONFIRMED_enrichments.py
```

**Verify Final Output:**
```bash
python -c "
import pandas as pd

df = pd.read_csv('Data/processed/FINAL_DISSERTATION_DATASET_ENRICHED.csv')
print(f'FINAL ENRICHED DATASET')
print(f'==================')
print(f'Total rows: {len(df)}')
print(f'Total columns: {len(df.columns)}')
print(f'FCC-reportable: {(df[\"fcc_reportable\"]==1).sum()} rows')
print(f'Non-FCC: {(df[\"fcc_reportable\"]==0).sum()} rows')
print(f'Essay 2 sample (has_crsp_data): {df[\"has_crsp_data\"].sum()} rows')
print(f'Essay 3 sample (volatility data): {df[\"return_volatility_pre\"].notna().sum()} rows')
"
```
**Expected Output:**
```
FINAL ENRICHED DATASET
==================
Total rows: 1054
Total columns: 100+
FCC-reportable: 200 rows
Non-FCC: 854 rows
Essay 2 sample (has_crsp_data): 926 rows
Essay 3 sample (volatility data): 916 rows
```

---

## VERIFICATION CHECKLIST

After completing all steps, run this comprehensive check:

```bash
python << 'EOF'
import pandas as pd

print("=" * 80)
print("FINAL DATA PIPELINE VERIFICATION")
print("=" * 80)

# Load final enriched dataset
df = pd.read_csv('Data/processed/FINAL_DISSERTATION_DATASET_ENRICHED.csv')

print(f"\n1. DATASET SIZE")
print(f"   Total rows: {len(df)}")
assert len(df) == 1054, "ERROR: Dataset should have 1054 rows!"
print(f"   ✓ PASS: 1054 rows")

print(f"\n2. FCC CLASSIFICATION")
fcc_count = (df['fcc_reportable'] == 1).sum()
non_fcc_count = (df['fcc_reportable'] == 0).sum()
print(f"   FCC-reportable: {fcc_count}")
print(f"   Non-FCC: {non_fcc_count}")
assert fcc_count == 200, f"ERROR: Expected 200 FCC, got {fcc_count}"
assert non_fcc_count == 854, f"ERROR: Expected 854 non-FCC, got {non_fcc_count}"
print(f"   ✓ PASS: FCC split correct")

print(f"\n3. ESSAY 2 SAMPLE (Event Study)")
essay2_sample = df['has_crsp_data'].sum()
essay2_pct = (essay2_sample / len(df)) * 100
print(f"   Breaches with CRSP data: {essay2_sample} ({essay2_pct:.1f}%)")
assert essay2_sample == 926, f"ERROR: Expected 926 in Essay 2, got {essay2_sample}"
print(f"   ✓ PASS: Essay 2 sample correct (926)")

print(f"\n4. ESSAY 3 SAMPLE (Information Asymmetry)")
essay3_sample = df['return_volatility_pre'].notna().sum()
essay3_pct = (essay3_sample / len(df)) * 100
print(f"   Breaches with volatility data: {essay3_sample} ({essay3_pct:.1f}%)")
assert essay3_sample == 916, f"ERROR: Expected 916 in Essay 3, got {essay3_sample}"
print(f"   ✓ PASS: Essay 3 sample correct (916)")

print(f"\n5. KEY ENRICHMENT VARIABLES")
enrich_vars = [
    'prior_breaches_total',
    'high_severity_breach',
    'executive_change_30d',
    'regulatory_enforcement',
    'health_breach',
    'financial_breach'
]
for var in enrich_vars:
    if var in df.columns:
        non_null = df[var].notna().sum()
        print(f"   {var:30s}: {non_null:4d} non-null")
    else:
        print(f"   {var:30s}: MISSING COLUMN")

print(f"\n" + "=" * 80)
print("✓ ALL CHECKS PASSED - Ready for analysis!")
print("=" * 80)

EOF
```

---

## IF YOU GET 858 ROWS AT ANY POINT

**STOP IMMEDIATELY** and check:

1. **Did you delete/recreate intermediate files?**
   - Keep all intermediate outputs (master_breach_dataset, final_analysis_dataset)

2. **Did you run all scripts in order?**
   - Must run: 03 → 06 → 20 → 40 → 53

3. **Did any script filter rows?**
   - Check the `len(breach_df)` at start vs end of each script

4. **Check file sizes:**
   ```bash
   ls -lh Data/processed/*.xlsx
   python -c "import pandas as pd; df=pd.read_excel('Data/processed/FINAL_DISSERTATION_DATASET.xlsx'); print(f'Rows: {len(df)}')"
   ```

---

## FINAL OUTPUT

When complete, you should have:

**Main Output File:**
- `Data/processed/FINAL_DISSERTATION_DATASET_ENRICHED.csv` (1,054 rows, 100+ columns)
- `Data/processed/FINAL_DISSERTATION_DATASET_ENRICHED.xlsx` (same, Excel format)

**With Analysis Sample Flags:**
- `has_crsp_data`: 926 rows marked TRUE (Essay 2 analytical sample)
- `has_complete_data`: 736 rows marked TRUE (restricted sample)
- `return_volatility_pre`: 916 rows with data (Essay 3 analytical sample)

**Run Pipeline:**
```bash
python run_all.py
```

This should now use 926 rows for Essay 2 and 916 rows for Essay 3!

---

**Date Created:** January 23, 2026
**Status:** Ready for manual execution
**Expected Duration:** 45 minutes - 1 hour
