#!/bin/bash
# QUICK_RESULTS_EXTRACT.sh
# Extract critical results from pipeline logs and output files

echo "========================================================================"
echo "DISSERTATION PIPELINE - QUICK RESULTS EXTRACT"
echo "========================================================================"

# Find latest log
LATEST_LOG=$(ls -t outputs/logs/analysis_log_*.txt 2>/dev/null | head -1)
echo "Latest log: $LATEST_LOG"
echo ""

# Check if pipeline completed
if grep -q "PIPELINE SUMMARY" "$LATEST_LOG" 2>/dev/null; then
    echo "[OK] Pipeline COMPLETED"
else
    echo "[RUNNING] Pipeline still in progress"
fi

echo ""
echo "========================================================================"
echo "H1-H4 BOUNDED NULL RESULTS"
echo "========================================================================"

if [ -f "outputs/h1_h4_form499_corrected_summary.csv" ]; then
    echo "File: outputs/h1_h4_form499_corrected_summary.csv"
    echo ""
    cat outputs/h1_h4_form499_corrected_summary.csv | column -t -s,
else
    echo "File not yet available"
fi

echo ""
echo "========================================================================"
echo "H5 VOLATILITY RESULTS"
echo "========================================================================"

if [ -f "outputs/h5_form499_corrected_regression_results.txt" ]; then
    echo "Main effect:"
    grep -A 3 "FCC coefficient:" outputs/h5_form499_corrected_regression_results.txt | head -4
    echo ""
    echo "Firm-size heterogeneity:"
    grep "Q[1-4]:" outputs/h5_form499_corrected_regression_results.txt
else
    echo "File not yet available"
fi

echo ""
echo "========================================================================"
echo "H6 EXECUTIVE TURNOVER RESULTS"
echo "========================================================================"

if [ -f "outputs/h6_form499_corrected_ame_by_window.csv" ]; then
    echo "File: outputs/h6_form499_corrected_ame_by_window.csv"
    echo ""
    cat outputs/h6_form499_corrected_ame_by_window.csv | column -t -s,
else
    echo "File not yet available"
fi

echo ""
echo "========================================================================"
echo "FORM 499 CLASSIFICATION (Reproducibility)"
echo "========================================================================"

if [ -f "Data/processed/FINAL_DISSERTATION_DATASET_FORM499_CORRECTED.csv" ]; then
    echo "Dataset exists: Data/processed/FINAL_DISSERTATION_DATASET_FORM499_CORRECTED.csv"
    N_TOTAL=$(wc -l < "Data/processed/FINAL_DISSERTATION_DATASET_FORM499_CORRECTED.csv")
    echo "Total rows: $((N_TOTAL - 1)) (excluding header)"

    # Count treated
    N_TREATED=$(tail -n +2 "Data/processed/FINAL_DISSERTATION_DATASET_FORM499_CORRECTED.csv" | \
                awk -F, '$NF == 1' | wc -l 2>/dev/null || echo "N/A")
    echo "Treated (fcc_form499=1): $N_TREATED"
else
    echo "Dataset not found"
fi

echo ""
echo "========================================================================"
echo "SUMMARY STATUS"
echo "========================================================================"
echo ""
echo "Critical files generated:"
echo "  H1-H4: outputs/h1_h4_form499_corrected_summary.csv"
echo "  H5:    outputs/h5_form499_corrected_regression_results.txt"
echo "  H6:    outputs/h6_form499_corrected_ame_by_window.csv"
echo "  Data:  Data/processed/FINAL_DISSERTATION_DATASET_FORM499_CORRECTED.csv"
echo ""
echo "See RESULTS_ANALYSIS_GUIDE.md for detailed interpretation guide"
echo ""
