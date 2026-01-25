# Streamlit Cloud Deployment Guide

## Overview
Your dashboard is now configured to work **both locally and on Streamlit Cloud** with automatic fallback logic:
- **Locally**: Uses fast local CSV files (after running `run_all.py`)
- **Streamlit Cloud**: Automatically downloads from Google Drive on first load

## Deployment Steps

### 1. Verify Google Drive Setup
Your data is already in Google Drive:
- **Folder**: https://drive.google.com/drive/folders/1aeEnpS-agQeaQCpgyD9UqQJDuJD1oij-?usp=sharing
- **Main file ID**: `1v0nKdwjihWGdbJLwTttFL0UkE2Jo2OIc` (already configured in utils.py)

### 2. Create Streamlit Cloud Account
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign up with GitHub account (use your ts2427 account)
3. Click "New app" button

### 3. Deploy Dashboard
1. **Repository**: `ts2427/DISSERTATION_CLONE`
2. **Branch**: `main`
3. **Main file path**: `Dashboard/app.py`
4. **Python version**: Keep default (3.12)

Once deployed, Streamlit will:
- Install dependencies from `requirements.txt` (includes gdown)
- Launch your dashboard
- On first access, it will download data from Google Drive

### 4. Test the Deployment
Once deployed, you'll get a URL like:
```
https://dissertation-clone-XXXXX.streamlit.app
```

Share this URL with committee members. They can access it without:
- Installing Python
- Running any scripts
- Having any local data files
- Waiting for analysis pipeline

### How It Works (Technical)

**Load Strategy (in `Dashboard/utils.py`):**
```
1. Does local file exist? → Load it (fast, ~1 second)
2. Local file missing? → Download from Google Drive (slow, ~30 seconds first time)
3. Download cached by Streamlit → Subsequent loads instant
```

This is why first cloud load takes ~30 seconds, but all subsequent loads are instant.

### Troubleshooting

**Issue**: "Permission denied" error from Google Drive
- **Solution**: The file is public and should work. Check that file ID is correct: `1v0nKdwjihWGdbJLwTttFL0UkE2Jo2OIc`

**Issue**: Dashboard shows "Data not found"
- **Solution**: Check logs in Streamlit Cloud dashboard (click three dots → Logs) for detailed error message

**Issue**: Slow first load
- **Expected**: First load downloads from Google Drive (~30 seconds). Subsequent loads use Streamlit's cache.

## Sharing with Committee

Send committee members this URL (replace with your actual URL):
```
https://dissertation-clone-XXXXX.streamlit.app
```

They can:
- Click through all pages
- View all tables and figures
- Download data for their own analysis (Raw Data Explorer page)
- No setup required

## Local Testing (Before Deployment)

To test as if you're in the cloud (without local files):
1. Temporarily rename or move `Data/processed/FINAL_DISSERTATION_DATASET_ENRICHED.csv`
2. Run dashboard: `cd Dashboard && streamlit run app.py`
3. Dashboard will download from Google Drive
4. Restore the file afterward

## Files Modified

- ✅ `Dashboard/utils.py` - Added Google Drive fallback logic
- ✅ `Dashboard/app.py` - Now uses centralized load_main_dataset()
- ✅ `Dashboard/pages/*.py` - All 5 data-loading pages now use utils
- ✅ `requirements.txt` - Added gdown>=4.7.1
- ✅ `pyproject.toml` - Added gdown>=4.7.1

## Next Steps

1. Go to https://share.streamlit.io
2. Follow "Deploy Dashboard" steps above
3. Test the URL
4. Share with committee
5. Celebrate! 🎉
