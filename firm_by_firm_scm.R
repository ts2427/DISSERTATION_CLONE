# FIRM-BY-FIRM SYNTHETIC CONTROL METHOD
# ============================================================================
# Individual SCM for each FCC firm with aggregation
#
# This script:
# 1. Identifies all unique FCC firms in the data
# 2. For each FCC firm, constructs synthetic control from non-FCC peers
# 3. Estimates individual treatment effects
# 4. Saves results for Python aggregation
#
# INPUT: Your main dissertation data (breach-level)
# OUTPUT: Firm-level treatment effects, weights, gaps

library(Synth)
library(dplyr)
library(tidyr)
library(data.table)

# ============================================================================
# CONFIGURATION - EDIT THIS FOR YOUR DATA
# ============================================================================

# Data file
DATA_FILE <- "Data/raw/your_breach_data.csv"  # Change to your actual data file

# Output directory
OUTPUT_DIR <- "outputs/scm_firm_by_firm"
dir.create(OUTPUT_DIR, showWarnings = FALSE, recursive = TRUE)

# FCC firm list (update if needed)
FCC_SICS <- c(4813, 4899, 4841)  # Telecom SICs

# Pre- and post-treatment years
PRE_YEAR <- 2007
POST_START <- 2007
POST_END <- 2024

# Matching variables (pre-treatment characteristics to balance)
MATCH_VARS <- c(
  "log_assets",
  "leverage",
  "roa",
  "log_records_affected"
)

# ============================================================================
# DATA PREPARATION
# ============================================================================

cat("\n[1/4] Loading and preparing data...\n")

# Load data
df <- fread(DATA_FILE)

# Ensure key variables exist
required_vars <- c("firm_id", "firm_name", "year", "sic_code",
                   "car_30d", "volatility_change", "executive_change_30d",
                   MATCH_VARS)

missing_vars <- setdiff(required_vars, names(df))
if (length(missing_vars) > 0) {
  stop("Missing required variables: ", paste(missing_vars, collapse = ", "))
}

# Create FCC indicator
df <- df %>%
  mutate(
    is_fcc = sic_code %in% FCC_SICS,
    period = ifelse(year < PRE_YEAR, "pre", "post")
  ) %>%
  as.data.table()

# Get FCC and non-FCC firms
fcc_firms <- unique(df[is_fcc == TRUE, .(firm_id, firm_name)])
non_fcc_firms <- unique(df[is_fcc == FALSE, .(firm_id, firm_name)])

cat(sprintf("Found %d FCC firms and %d non-FCC firms\n",
            nrow(fcc_firms), nrow(non_fcc_firms)))

# ============================================================================
# FUNCTION: Prepare data for single firm's SCM
# ============================================================================

prepare_scm_data <- function(treatment_firm_id, data, pre_year, post_start, post_end) {
  """
  Prepare breach-level data into firm-year panel for SCM.

  For synthetic control method, we need:
  - Time periods (years)
  - Outcome variable (mean CAR, volatility, or governance by year)
  - Predictor variables (pre-treatment characteristics)
  """

  # Filter data for treatment firm and years of interest
  all_years <- pre_year:post_end

  # Aggregate to firm-year level
  firm_year_data <- data[year %in% all_years, .(
    # Outcomes (mean within firm-year)
    car_mean = mean(car_30d, na.rm = TRUE),
    volatility_mean = mean(volatility_change, na.rm = TRUE),
    governance_mean = mean(as.numeric(executive_change_30d), na.rm = TRUE),

    # Predictors (use most recent pre-treatment values)
    log_assets = mean(log_assets, na.rm = TRUE),
    leverage = mean(leverage, na.rm = TRUE),
    roa = mean(roa, na.rm = TRUE),
    log_records = mean(log_records_affected, na.rm = TRUE),

    # Count for weighting
    n_breaches = .N
  ), by = .(firm_id, year)]

  return(firm_year_data)
}

# ============================================================================
# FUNCTION: Run SCM for single firm
# ============================================================================

run_scm_single_firm <- function(treatment_id, firm_year_data, pre_year, outcome_var = "car_mean") {
  """
  Run Synth package for a single treatment firm.

  Returns:
  - Treatment effects (gaps)
  - V weights (predictor importance)
  - W weights (control unit weights)
  - Fit quality metrics
  """

  tryCatch({
    # Get treatment and control firm IDs
    treatment_years <- unique(firm_year_data[firm_id == treatment_id, year])
    treatment_min_year <- min(treatment_years)
    treatment_max_year <- max(treatment_years)

    # Control firms: all non-FCC firms with data in pre-period
    pre_data <- firm_year_data[year < pre_year]
    control_ids <- unique(pre_data[firm_id != treatment_id, firm_id])

    if (length(control_ids) == 0) {
      return(NULL)  # Skip if no controls
    }

    # Prepare data for synth()
    # Format: wide data with rows = units, cols = years
    prep_data <- firm_year_data[
      firm_id %in% c(treatment_id, control_ids),
      .(firm_id, year, outcome = get(outcome_var))
    ]

    # Wide format
    wide_data <- dcast(prep_data, firm_id ~ year, value.var = "outcome")
    unit_names <- wide_data$firm_id
    panel_data <- as.matrix(wide_data[, -1])
    rownames(panel_data) <- unit_names

    # Get predictor data (pre-treatment characteristics)
    predictor_data <- firm_year_data[
      firm_id %in% c(treatment_id, control_ids) & year == (pre_year - 1),
      .(firm_id, log_assets, leverage, roa, log_records)
    ]
    pred_matrix <- as.matrix(predictor_data[, -1])
    rownames(pred_matrix) <- predictor_data$firm_id

    # Prepare years
    pre_years <- which(colnames(panel_data) < pre_year)
    post_years <- which(colnames(panel_data) >= pre_year)

    if (length(pre_years) < 2 || length(post_years) < 1) {
      return(NULL)  # Skip if insufficient data
    }

    # Run synth
    synth_obj <- synth(
      data.prep.obj = dataprep(
        foo = panel_data,
        predictors = rownames(pred_matrix),  # Use all predictors
        predictors.op = "mean",
        dependent = "outcome",
        unit.variable = 1,
        time.variable = 2,
        special.predictors = list(
          list(outcome, pre_years, "mean")
        ),
        treatment.identifier = which(rownames(panel_data) == treatment_id),
        controls.identifier = which(rownames(panel_data) %in% control_ids),
        time.predictors.prior = pre_years,
        time.treat = min(as.numeric(colnames(panel_data)[post_years]))
      ),
      Margin.ipop = 0.005,
      Sigf.ipop = 7,
      bound.ipop = 6,
      gen.feature = FALSE
    )

    # Extract results
    treatment_effect <- synth_obj$solution.v  # V weights
    control_weights <- synth_obj$solution.w   # W weights

    # Compute gaps
    Y_treated <- synth_obj$Y1
    Y_synthetic <- synth_obj$Y0 %*% control_weights
    gaps <- Y_treated - Y_synthetic

    # Return structured results
    results <- list(
      treatment_id = treatment_id,
      outcome_var = outcome_var,
      synth_object = synth_obj,
      v_weights = treatment_effect,
      w_weights = control_weights,
      control_ids = control_ids,
      gaps = gaps,
      years = as.numeric(colnames(panel_data)),
      pre_years = pre_years,
      post_years = post_years,
      mean_gap = mean(gaps[post_years]),
      mean_gap_pre = mean(gaps[pre_years]),
      mean_gap_post = mean(gaps[post_years]),
      rmse_pre = sqrt(mean((gaps[pre_years])^2))
    )

    return(results)

  }, error = function(e) {
    cat(sprintf("ERROR for firm %s: %s\n", treatment_id, e$message))
    return(NULL)
  })
}

# ============================================================================
# MAIN LOOP: Run SCM for each FCC firm
# ============================================================================

cat("\n[2/4] Running SCM for each FCC firm...\n")

# Prepare firm-year panel
firm_year_panel <- prepare_scm_data(
  treatment_firm_id = NULL,
  data = df,
  pre_year = PRE_YEAR,
  post_start = POST_START,
  post_end = POST_END
)

# Results storage
scm_results <- list()
summary_results <- data.table()

# Loop over FCC firms
for (i in 1:nrow(fcc_firms)) {
  treatment_id <- fcc_firms[i, firm_id]
  treatment_name <- fcc_firms[i, firm_name]

  if (i %% 10 == 0) {
    cat(sprintf("  Processing firm %d/%d (%s)...\n", i, nrow(fcc_firms), treatment_name))
  }

  # Run SCM for CAR (primary outcome)
  scm_car <- run_scm_single_firm(
    treatment_id = treatment_id,
    firm_year_data = firm_year_panel,
    pre_year = PRE_YEAR,
    outcome_var = "car_mean"
  )

  if (!is.null(scm_car)) {
    scm_results[[treatment_id]] <- scm_car

    # Store summary
    summary_results <- rbind(summary_results, data.table(
      firm_id = treatment_id,
      firm_name = treatment_name,
      n_controls = length(scm_car$control_ids),
      mean_gap = scm_car$mean_gap,
      mean_gap_pre = scm_car$mean_gap_pre,
      mean_gap_post = scm_car$mean_gap_post,
      rmse_pre = scm_car$rmse_pre,
      outcome = "car_30d"
    ))
  }
}

cat(sprintf("\nSuccessfully estimated SCM for %d FCC firms\n", length(scm_results)))

# ============================================================================
# SAVE RESULTS
# ============================================================================

cat("\n[3/4] Saving results...\n")

# Summary table
fwrite(summary_results,
       file = file.path(OUTPUT_DIR, "scm_firm_summary_results.csv"))

# Individual firm gaps (for aggregation)
all_gaps <- data.table()
for (firm_id in names(scm_results)) {
  result <- scm_results[[firm_id]]
  gaps_df <- data.table(
    firm_id = firm_id,
    year = result$years,
    gap = as.vector(result$gaps),
    treated = as.vector(result$synth_object$Y1),
    synthetic = as.vector(result$synth_object$Y0 %*% result$w_weights),
    is_post_treatment = result$years >= PRE_YEAR
  )
  all_gaps <- rbind(all_gaps, gaps_df)
}

fwrite(all_gaps,
       file = file.path(OUTPUT_DIR, "scm_all_firm_gaps.csv"))

# Summary statistics for aggregation
summary_stats <- summary_results[, .(
  N_firms = .N,
  mean_effect = mean(mean_gap, na.rm = TRUE),
  sd_effect = sd(mean_gap, na.rm = TRUE),
  median_effect = median(mean_gap, na.rm = TRUE),
  min_effect = min(mean_gap, na.rm = TRUE),
  max_effect = max(mean_gap, na.rm = TRUE),
  p25_effect = quantile(mean_gap, 0.25, na.rm = TRUE),
  p75_effect = quantile(mean_gap, 0.75, na.rm = TRUE),
  mean_rmse = mean(rmse_pre, na.rm = TRUE)
)]

fwrite(summary_stats,
       file = file.path(OUTPUT_DIR, "scm_aggregate_statistics.csv"))

cat("\n[4/4] Complete!\n")
cat(sprintf("\nOutput files saved to: %s\n", OUTPUT_DIR))
cat("  - scm_firm_summary_results.csv (individual firm results)\n")
cat("  - scm_all_firm_gaps.csv (gap data for visualization)\n")
cat("  - scm_aggregate_statistics.csv (aggregate statistics)\n")

# Print summary
cat("\n" %+% strrep("=", 70) %+% "\n")
cat("FIRM-BY-FIRM SCM SUMMARY\n")
cat(strrep("=", 70) %+% "\n")
print(summary_stats)
