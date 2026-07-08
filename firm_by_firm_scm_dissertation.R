# FIRM-BY-FIRM SYNTHETIC CONTROL METHOD - DISSERTATION ADAPTATION
# ========================================================================
# Adapted for dissertation data structure
#
# INPUT: data_scm_ready.csv (prepared from FINAL_DISSERTATION_DATASET_ENRICHED.csv)
# OUTPUT: Firm-level treatment effects in outputs/scm_firm_by_firm/

library(Synth)
library(dplyr)
library(tidyr)
library(data.table)

# ============================================================================
# CONFIGURATION - DISSERTATION-SPECIFIC
# ============================================================================

# Data file
DATA_FILE <- "data_scm_ready.csv"

# Output directory
OUTPUT_DIR <- "outputs/scm_firm_by_firm"
dir.create(OUTPUT_DIR, showWarnings = FALSE, recursive = TRUE)

# FCC identification (using sic code)
FCC_SICS <- c(4813, 4899, 4841)

# Time periods
PRE_YEAR <- 2007
POST_START <- 2007
POST_END <- 2024

cat("\n" %+% strrep("=", 70) %+% "\n")
cat("FIRM-BY-FIRM SYNTHETIC CONTROL METHOD\n")
cat("Dissertation Data Analysis\n")
cat(strrep("=", 70) %+% "\n")

# ============================================================================
# LOAD AND PREPARE DATA
# ============================================================================

cat("\n[1/4] Loading and preparing data...\n")

df <- fread(DATA_FILE)

# Create FCC indicator
df <- df %>%
  mutate(
    is_fcc = sic %in% FCC_SICS,
    year = breach_year,
    firm_id = cik,
    firm_name = org_name,
    records_affected = total_affected,
    log_records = log(total_affected + 1)
  ) %>%
  as.data.table()

# Get FCC and non-FCC firms
fcc_firms <- unique(df[is_fcc == TRUE, .(firm_id, firm_name)])
non_fcc_firms <- unique(df[is_fcc == FALSE, .(firm_id, firm_name)])

cat(sprintf("Found %d FCC firms and %d non-FCC firms\n",
            nrow(fcc_firms), nrow(non_fcc_firms)))

# Check if we have enough firms
if (nrow(fcc_firms) < 10) {
  cat("WARNING: Less than 10 unique FCC firms. SCM may not work well.\n")
}

# ============================================================================
# PREPARE FIRM-YEAR PANEL FOR SCM
# ============================================================================

cat("\n[2/4] Preparing firm-year panel data...\n")

# Aggregate to firm-year level
all_years <- PRE_YEAR:POST_END

firm_year_data <- df[year %in% all_years, .(
  # Outcomes (mean within firm-year)
  car_mean = mean(car_30d, na.rm = TRUE),
  volatility_mean = mean(volatility_change, na.rm = TRUE),
  governance_mean = mean(as.numeric(executive_change_30d), na.rm = TRUE),

  # Predictors (pre-treatment characteristics)
  log_assets = mean(firm_size_log, na.rm = TRUE),
  leverage = mean(leverage, na.rm = TRUE),
  roa = mean(roa, na.rm = TRUE),
  log_records = mean(log_records, na.rm = TRUE),

  # Counts
  n_breaches = .N
), by = .(firm_id, firm_name, year)]

cat(sprintf("Created firm-year panel: %d rows\n", nrow(firm_year_data)))

# ============================================================================
# RUN SCM FOR EACH FCC FIRM
# ============================================================================

cat("\n[3/4] Running SCM for each FCC firm...\n")

# Storage for results
scm_results <- list()
summary_results <- data.table()

# Get unique FCC firms
fcc_firm_list <- unique(firm_year_data[firm_name %in% fcc_firms$firm_name, .(firm_id, firm_name)])

# Loop over FCC firms
for (i in 1:nrow(fcc_firm_list)) {
  treatment_id <- fcc_firm_list[i, firm_id]
  treatment_name <- fcc_firm_list[i, firm_name]

  if (i %% 10 == 0 || i == 1) {
    cat(sprintf("  [%d/%d] Processing: %s\n", i, nrow(fcc_firm_list), treatment_name))
  }

  tryCatch({
    # Get years available for this firm
    firm_data <- firm_year_data[firm_id == treatment_id]
    available_years <- firm_data$year

    if (length(available_years) < 3) {
      # Skip if insufficient data
      next
    }

    # Identify control firms (all non-FCC firms)
    control_data <- firm_year_data[!firm_name %in% fcc_firms$firm_name]
    control_ids <- unique(control_data[year < PRE_YEAR, firm_id])

    if (length(control_ids) < 5) {
      # Skip if insufficient controls
      next
    }

    # Prepare data: wide format (firms as rows, years as columns)
    all_units <- c(treatment_id, control_ids)
    wide_data <- firm_year_data[
      firm_id %in% all_units & year %in% all_years,
      .(firm_id, year, car_mean)
    ] %>%
      dcast(firm_id ~ year, value.var = "car_mean")

    # Convert to matrix
    unit_names <- wide_data$firm_id
    panel_matrix <- as.matrix(wide_data[, -1])
    rownames(panel_matrix) <- unit_names
    colnames(panel_matrix) <- as.character(as.numeric(colnames(panel_matrix)))

    # Prepare predictors (pre-treatment characteristics)
    pred_data <- firm_year_data[
      firm_id %in% all_units & year == (PRE_YEAR - 1),
      .(firm_id, log_assets, leverage, roa, log_records)
    ]

    if (nrow(pred_data) < length(all_units) / 2) {
      # Skip if insufficient predictor data
      next
    }

    pred_matrix <- as.matrix(pred_data[, -1])
    rownames(pred_matrix) <- pred_data$firm_id

    # Years for pre/post split
    year_nums <- as.numeric(colnames(panel_matrix))
    pre_years <- which(year_nums < PRE_YEAR)
    post_years <- which(year_nums >= PRE_YEAR)

    if (length(pre_years) < 2 || length(post_years) < 1) {
      # Skip if insufficient pre/post data
      next
    }

    # Run Synth
    tryCatch({
      synth_obj <- synth(
        data.prep.obj = dataprep(
          foo = panel_matrix,
          predictors = rownames(pred_matrix),
          predictors.op = "mean",
          dependent = "car_mean",
          unit.variable = 1,
          time.variable = 2,
          special.predictors = list(
            list("car_mean", pre_years, "mean")
          ),
          treatment.identifier = which(rownames(panel_matrix) == treatment_id),
          controls.identifier = which(rownames(panel_matrix) %in% control_ids),
          time.predictors.prior = pre_years,
          time.treat = min(year_nums[post_years])
        ),
        Margin.ipop = 0.005,
        Sigf.ipop = 7,
        bound.ipop = 6,
        gen.feature = FALSE
      )

      # Extract results
      Y_treated <- synth_obj$Y1
      Y_synthetic <- synth_obj$Y0 %*% synth_obj$solution.w
      gaps <- Y_treated - Y_synthetic

      # Store results
      summary_results <- rbind(summary_results, data.table(
        firm_id = treatment_id,
        firm_name = treatment_name,
        n_controls = length(control_ids),
        mean_gap = mean(gaps[post_years], na.rm = TRUE),
        mean_gap_pre = mean(gaps[pre_years], na.rm = TRUE),
        mean_gap_post = mean(gaps[post_years], na.rm = TRUE),
        rmse_pre = sqrt(mean((gaps[pre_years])^2, na.rm = TRUE)),
        outcome = "car_30d"
      ))

    }, error = function(e) {
      # Synth failed for this firm, skip
      NULL
    })

  }, error = function(e) {
    # General error, skip this firm
    NULL
  })
}

cat(sprintf("\nSuccessfully estimated SCM for %d FCC firms\n", nrow(summary_results)))

# ============================================================================
# SAVE RESULTS
# ============================================================================

cat("\n[4/4] Saving results...\n")

# Save summary
fwrite(summary_results,
       file = file.path(OUTPUT_DIR, "scm_firm_summary_results.csv"))

print(summary_results[, .(
  N_firms = .N,
  mean_effect = mean(mean_gap, na.rm = TRUE),
  median_effect = median(mean_gap, na.rm = TRUE),
  sd_effect = sd(mean_gap, na.rm = TRUE),
  min_effect = min(mean_gap, na.rm = TRUE),
  max_effect = max(mean_gap, na.rm = TRUE)
)])

cat("\n" %+% strrep("=", 70) %+% "\n")
cat("FIRM-BY-FIRM SCM COMPLETE\n")
cat(sprintf("Results saved to: %s\n", OUTPUT_DIR))
cat(strrep("=", 70) %+% "\n\n")

cat("Next: Run Python aggregation\n")
cat("  python scripts/firm_by_firm_scm_analysis.py\n\n")
