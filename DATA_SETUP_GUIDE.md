# Data Setup Guide for DISSERTATION_CLONE

## Problem
When cloning the repository to a new environment, the `Data/` folder is empty because:
- Data files are NOT stored in Git (too large)
- Git LFS is configured, but data is source from cloud or original location
- Only `.gitkeep` placeholder files are in the repository

## Solution

### Option 1: Copy from Existing Installation (Fastest)
If you already have a working installation with data, copy the entire `Data/` folder:

```bash
# Windows (Command Prompt)
xcopy "C:\path\to\original\DISSERTATION_CLONE\Data" "C:\path\to\new\DISSERTATION_CLONE\Data" /E /I

# Windows (PowerShell)
Copy-Item -Path "C:\path\to\original\DISSERTATION_CLONE\Data" -Destination "C:\path\to\new\DISSERTATION_CLONE\Data" -Recurse

# macOS/Linux
cp -r /path/to/original/DISSERTATION_CLONE/Data /path/to/new/DISSERTATION_CLONE/
```

### Option 2: Download from Cloud Folder
If you don't have a local copy, download from the shared cloud folder (see README.md section "Data Setup"):
1. Request access to OneDrive/Google Drive folder from instructor
2. Download the entire `Data/` folder (~1.8 GB)
3. Copy to your repository root

### Option 3: Regenerate Data from Source (Advanced)
Requires WRDS access and knowledge of data pipeline:
```bash
# This would require running all scripts 00-53 in sequence
# Only recommended if modifying original data sources
# See scripts/ directory for details
```

## Directory Structure After Setup

Your project should look like:

```
DISSERTATION_CLONE/
├── Data/
│   ├── raw/
│   │   └── DataBreaches.xlsx
│   ├── processed/
│   │   ├── FINAL_DISSERTATION_DATASET_ENRICHED.csv  (2.0 MB)
│   │   ├── FINAL_DISSERTATION_DATASET_ENRICHED.xlsx
│   │   └── DATA_DICTIONARY_ENRICHED.csv
│   ├── wrds/
│   │   ├── crsp_daily_returns.csv
│   │   ├── compustat_fundamentals.csv
│   │   ├── compustat_annual.csv
│   │   ├── market_indices.csv
│   │   └── ticker_permno_mapping.csv
│   ├── enrichment/
│   │   ├── prior_breach_history.csv
│   │   ├── breach_severity_classification.csv
│   │   ├── executive_changes.csv
│   │   └── regulatory_enforcement.csv
│   ├── fcc/
│   │   └── fcc_data_template.csv
│   └── audit_analytics/
├── Notebooks/
├── scripts/
├── Dashboard/
├── outputs/
├── run_all.py
├── pyproject.toml
└── README.md
```

## Verification After Setup

After copying data, verify it's complete:

```bash
# Check main dataset exists and has content
python -c "import pandas as pd; df = pd.read_csv('Data/processed/FINAL_DISSERTATION_DATASET_ENRICHED.csv'); print(f'✓ Dataset loaded: {len(df)} rows, {len(df.columns)} columns')"

# Check WRDS data
python -c "import pandas as pd; df = pd.read_csv('Data/wrds/crsp_daily_returns.csv'); print(f'✓ CRSP returns: {len(df)} observations')"

# Check enrichment files
python -c "
import os
enrichment_files = os.listdir('Data/enrichment')
print(f'✓ Enrichment files: {len(enrichment_files)} CSVs')
for f in enrichment_files:
    print(f'  - {f}')
"
```

## Expected File Sizes

| File | Size | Purpose |
|------|------|---------|
| FINAL_DISSERTATION_DATASET_ENRICHED.csv | ~2.0 MB | Main analysis dataset |
| FINAL_DISSERTATION_DATASET_ENRICHED.xlsx | ~3.5 MB | Excel version |
| crsp_daily_returns.csv | ~450 MB | Stock price data (4M+ observations) |
| compustat_fundamentals.csv | ~80 MB | Quarterly financial data |
| compustat_annual.csv | ~20 MB | Annual financial data |
| market_indices.csv | ~2 MB | S&P 500, market index returns |

**Total size: ~1.8 GB**

## Common Issues

### "FINAL_DISSERTATION_DATASET_ENRICHED.csv not found"
**Solution:**
1. Verify Data/processed/ folder exists
2. Check file name spelling (case-sensitive on Linux)
3. Verify file isn't corrupted: `file Data/processed/FINAL_DISSERTATION_DATASET_ENRICHED.csv`

### Data file appears empty or corrupted
**Solution:**
1. Delete and re-copy the Data/ folder
2. Verify original location has complete data
3. Check available disk space (need ~2 GB free)

### "git lfs pull" doesn't download files
**Solution:**
1. Git LFS is configured but files not pushed
2. Use Option 1 (copy from existing) instead
3. Or Option 2 (download from cloud)

## For Committee Members

If reviewing/reproducing the dissertation:
1. Clone the repository: `git clone https://github.com/ts2427/DISSERTATION_CLONE.git`
2. Follow Option 2 above to download data from provided cloud link
3. Then run: `python run_all.py` or `uv run run_all.py`

## Future Improvements

To avoid this issue in the next version:
1. **Option A:** Store data in cloud folder (current approach)
2. **Option B:** Use proper Git LFS setup (commit data files, track with LFS)
3. **Option C:** Provide data download script (auto-downloads from cloud)
4. **Option D:** Provide Docker image (includes data in container)

---

**Last Updated:** January 23, 2026
**Repository:** https://github.com/ts2427/DISSERTATION_CLONE
