# =====================================================================================
# R replication of the dissertation's headline estimates
# "Data Breach Disclosure Timing and Market Reactions" - Timothy D. Spivey
#
# Run from inside this folder:   Rscript replicate.R
#
# R version used : R 4.5.0 (2025-04-11 ucrt), Windows x64
# Packages       : base R for every estimate; sandwich 3.1.1 and lmtest 0.9.40 for the HC3 rows
# Run time       : about 5 seconds on a laptop (almost all of it the wild cluster bootstrap)
#
# The full pipeline is in Python. This script re-implements ONLY the headline models and the
# inference methods they use, formula for formula, so each number can be read off the code:
#   HC3   heteroskedasticity-robust (sandwich::vcovHC, type "HC3")
#   CV1   cluster-robust on parent CIK, correction G/(G-1) * (n-1)/(n-k)
#   CV3   leave-one-cluster-out jackknife, (G-1)/G * sum of squared deviations from the mean
#         of the delete-one estimates; t with G-1 df
#   WCR   restricted wild cluster bootstrap: null imposed, Rademacher weights drawn per parent
#         CIK, CV1 t-statistic recomputed each draw
#   TOST  two one-sided tests against +/- 2.10 pp (Essay 1)
#   MDE80 minimum detectable effect at 80% power
# Each function names the Python file and lines it mirrors (repository tag defense-final).
#
# The bootstrap uses R's random numbers, not numpy's, so bootstrap p-values agree with the
# Python ones only within Monte Carlo error. Everything else is deterministic.
# =====================================================================================

suppressPackageStartupMessages({
  library(sandwich)
  library(lmtest)
})

t_start <- Sys.time()
SEED <- 499            # fixed before any result was seen; same integer the Python scripts use
set.seed(SEED)
TREAT <- "fcc_form499"
EQ    <- 2.10          # TOST bound, percentage points      (scripts/158:78)

results <- data.frame(essay = character(), model = character(), term = character(),
                      statistic = character(), r_value = numeric(), stringsAsFactors = FALSE)
add <- function(essay, model, term, ...) {
  v <- list(...)
  results <<- rbind(results, data.frame(essay = essay, model = model, term = term,
                                        statistic = names(v), r_value = as.numeric(unlist(v)),
                                        stringsAsFactors = FALSE))
}

# -------------------------------------------------------------------------------------
# Building blocks
# -------------------------------------------------------------------------------------

# Design matrix with a constant first, regressors in the order given.
design <- function(d, xvars) {
  X <- cbind(const = 1, as.matrix(d[, xvars, drop = FALSE]))
  storage.mode(X) <- "double"
  X
}

# OLS by the normal equations.                       (scripts/165:72-76; scripts/227:100-103)
ols <- function(X, y) {
  XtXi <- solve(crossprod(X))
  b <- drop(XtXi %*% crossprod(X, y))
  list(b = b, XtXi = XtXi, u = drop(y - X %*% b))
}

# CV1: cluster-robust variance on parent CIK.
#   meat = sum_g (X_g' u_g)(X_g' u_g)',  V = adj * (X'X)^-1 meat (X'X)^-1,
#   adj  = G/(G-1) * (n-1)/(n-k)                     (scripts/165:79-86; scripts/227:104-109)
# This is also what statsmodels cov_type='cluster' computes (scripts/158:286, 164:127, 175:179).
cv1 <- function(X, u, cl, XtXi) {
  n <- nrow(X); k <- ncol(X); G <- length(unique(cl))
  S <- rowsum(X * u, cl)                 # G x k matrix of cluster scores
  adj <- (G / (G - 1)) * ((n - 1) / (n - k))
  list(V = adj * XtXi %*% crossprod(S) %*% XtXi, adj = adj, G = G)
}

# CV3: leave-one-cluster-out jackknife.
#   b_(g) = OLS without cluster g;  V3 = (G-1)/G * sum_g (b_(g) - bbar)(b_(g) - bbar)',
#   bbar = mean of the delete-one estimates          (scripts/165:89-95; scripts/227:110-115)
cv3 <- function(X, y, cl) {
  ids <- unique(cl); G <- length(ids)
  Bdel <- t(vapply(ids, function(g) {
    keep <- cl != g
    drop(solve(crossprod(X[keep, , drop = FALSE]), crossprod(X[keep, , drop = FALSE], y[keep])))
  }, numeric(ncol(X))))
  dev <- sweep(Bdel, 2, colMeans(Bdel))
  list(V = (G - 1) / G * crossprod(dev), Bdel = Bdel)
}

# WCR: restricted wild cluster bootstrap p-value for H0: beta_t = 0.
#   1. impose the null: regress y on the other regressors, keep fitted values and residuals u;
#   2. each draw b: one Rademacher weight v_g per parent CIK, y* = fit + v_g * u;
#   3. re-estimate, recompute the CV1 t-statistic, compare |t*| with |t_obs| (t_obs uses CV1);
#   4. p = (#{|t*| >= |t_obs|} + 1) / (B + 1).
# The algebra below avoids refitting: X'y* = X'fit + S v, with S the cluster scores of u.
#                                        (scripts/165:147-176; scripts/227:128-147; 175:183-218)
wcr_p <- function(X, y, cl, ti, B, chunk = 20000) {
  n <- nrow(X); k <- ncol(X)
  f <- ols(X, y)
  c1 <- cv1(X, f$u, cl, f$XtXi)
  t_obs <- f$b[ti] / sqrt(c1$V[ti, ti])
  ids <- sort(unique(cl)); G <- length(ids)
  Xr <- X[, -ti, drop = FALSE]
  fit <- drop(Xr %*% solve(crossprod(Xr), crossprod(Xr, y)))   # restricted fit (beta_t = 0)
  u <- y - fit
  S   <- t(rowsum(X * u, cl))             # k x G cluster scores of the restricted residuals
  a   <- f$XtXi[ti, ]                     # row of (X'X)^-1 for the treatment coefficient
  aq  <- drop(a %*% t(rowsum(X * fit, cl)))              # a' X_g' fit_g,      length G
  a_s <- drop(a %*% S)                                   # a' X_g' u_g,        length G
  P   <- t(vapply(ids, function(g) drop(a %*% crossprod(X[cl == g, , drop = FALSE])),
                  numeric(k)))                           # a' X_g' X_g,        G x k
  Xtfit <- drop(crossprod(X, fit))
  exceed <- 0
  done <- 0
  while (done < B) {
    b <- min(chunk, B - done)
    V  <- matrix(sample(c(-1, 1), G * b, replace = TRUE), nrow = G)   # Rademacher, G x b
    Bs <- f$XtXi %*% (Xtfit + S %*% V)                                # k x b bootstrap betas
    W  <- aq + a_s * V - P %*% Bs                                     # G x b projected scores
    t_star <- Bs[ti, ] / sqrt(c1$adj * colSums(W^2))
    exceed <- exceed + sum(abs(t_star) >= abs(t_obs))
    done <- done + b
  }
  (exceed + 1) / (B + 1)
}

# The cluster ladder for one coefficient: CV1, CV3 (t with G-1 df), WCR, CV3 CI and MDE80.
#   MDE80 = (t_.975 + t_.80, df = G-1) * SE_CV3      (scripts/165:268-269; scripts/227:122)
ladder <- function(d, yvar, xvars, B, hc3 = FALSE) {
  X <- design(d, xvars); y <- as.numeric(d[[yvar]]); cl <- d$parent_cik
  ti <- match(TREAT, colnames(X))
  f <- ols(X, y); n <- nrow(X); k <- ncol(X)
  c1 <- cv1(X, f$u, cl, f$XtXi); G <- c1$G
  se1 <- sqrt(c1$V[ti, ti])
  se3 <- sqrt(cv3(X, y, cl)$V[ti, ti])
  b <- unname(f$b[ti]); tq <- qt(0.975, G - 1)
  out <- list(coef = b, n = n, G = G,
              se_cv1 = se1, p_cv1 = 2 * (1 - pt(abs(b / se1), G - 1)),
              se_cv3 = se3, p_cv3 = 2 * (1 - pt(abs(b / se3), G - 1)),
              ci_cv3_lo = b - tq * se3, ci_cv3_hi = b + tq * se3,
              mde80_cv3 = (qt(0.975, G - 1) + qt(0.80, G - 1)) * se3,
              p_wcr = wcr_p(X, y, cl, ti, B))
  if (hc3) {   # HC3 with t(n-k), as statsmodels use_t=True           (scripts/227:116-119)
    m <- lm(y ~ X - 1)
    se_h <- sqrt(diag(vcovHC(m, type = "HC3")))[ti]
    out$se_hc3 <- unname(se_h)
    out$p_hc3 <- unname(2 * (1 - pt(abs(b / se_h), n - k)))
  }
  out
}

show <- function(label, r) {
  cat(sprintf("  %-34s coef %+9.4f | CV1 p %.4f | CV3 SE %.4f p %.4f | WCR p %.4f | MDE80 %.4f\n",
              label, r$coef, r$p_cv1, r$se_cv3, r$p_cv3, r$p_wcr, r$mde80_cv3))
}

# =====================================================================================
# ESSAY 1 - 30-day CAR on four hypothesis variables and three controls (N = 340)
#   OLS with HC3; p-values and CIs use the normal distribution, as statsmodels does by
#   default for cov_type='HC3'.                                        (scripts/158:72-92)
# =====================================================================================
cat("\nESSAY 1 - market reaction (30-day CAR, percentage points)\n")
e1 <- read.csv("essay1_car.csv")
H1 <- c(fcc_form499 = "H2_FCC", immediate_disclosure = "H1_timing",
        prior_breaches_1yr = "H3_prior", health_breach = "H4_health")
m1 <- lm(car_30d ~ fcc_form499 + immediate_disclosure + prior_breaches_1yr + health_breach +
           firm_size_log + leverage + roa, data = e1)
V_hc3 <- vcovHC(m1, type = "HC3")
ct <- coeftest(m1, vcov. = V_hc3, df = Inf)            # df = Inf -> normal p-values
dof <- nrow(e1) - 7 - 1                                # TOST df: n - regressors - 1 (158:77)
# parent-CIK clustered p-values, normal reference        (scripts/158:286, table 8)
X1 <- model.matrix(m1); c1e <- cv1(X1, residuals(m1), e1$parent_cik, solve(crossprod(X1)))
cat(sprintf("  N = %d, treated events = %d, parent-CIK clusters = %d\n",
            nrow(e1), sum(e1$fcc_form499), c1e$G))
for (v in names(H1)) {
  b <- unname(coef(m1)[v]); se <- sqrt(V_hc3[v, v]); p <- ct[v, 4]
  tost <- max(1 - pt((b + EQ) / se, dof), pt((b - EQ) / se, dof))      # scripts/158:83
  se_cl <- sqrt(c1e$V[v, v]); p_cl <- 2 * (1 - pnorm(abs(b / se_cl)))
  add("Essay 1", "30-day CAR, baseline OLS", H1[[v]],
      coef = b, se_hc3 = se, p_hc3 = p,
      ci95_lo = b - qnorm(0.975) * se, ci95_hi = b + qnorm(0.975) * se,
      ci90_lo = b - qnorm(0.95) * se,  ci90_hi = b + qnorm(0.95) * se,
      tost_p = tost, mde80 = 2.8 * se, p_cluster = p_cl)               # MDE: scripts/158:89
  cat(sprintf("  %-10s coef %+8.4f | HC3 SE %.4f p %.4f | 95%% CI [%+.4f, %+.4f] | TOST p %.4f | MDE80 %.4f | clustered p %.4f\n",
              H1[[v]], b, se, p, b - qnorm(0.975) * se, b + qnorm(0.975) * se, tost, 2.8 * se, p_cl))
}

# =====================================================================================
# ESSAY 2 - Form 499 coefficient on the volatility change and on disclosure delay (N = 333)
#   Volatility model regressors: scripts/165:58-59.  Delay models: scripts/164:119-127.
# =====================================================================================
cat("\nESSAY 2 - information environment\n")
e2 <- read.csv("essay2_volatility.csv")
B_MAIN <- 99999                                                        # scripts/165:179
X_VOL   <- c("delay_w", "e2_pre_sd", "firm_size_log", "leverage", "roa", TREAT,
             "health_breach", "prior_events")
X_DELAY <- c(TREAT, "e2_pre_sd", "firm_size_log", "leverage", "roa", "health_breach",
             "prior_events")
e2_models <- list(
  list("Volatility change (daily pp)", "e2_vol_change", X_VOL),
  list("Disclosure delay, raw days", "disclosure_delay_days", X_DELAY),
  list("Disclosure delay, winsorized p99", "delay_w", X_DELAY))
for (mm in e2_models) {
  r <- ladder(e2, mm[[2]], mm[[3]], B_MAIN)
  show(mm[[1]], r)
  do.call(add, c(list("Essay 2", mm[[1]], TREAT), r))
}

# Announcement-window elevation (N = 331): elev ~ Form 499 + baseline abnormal volatility +
# controls; CV1, CV3 and WCR with B = 49,999, the number scripts/175 uses.  (175:175-218)
ea <- read.csv("essay2_announcement.csv")
r <- ladder(ea, "elev", c(TREAT, "abn_pre", "delay_w", "firm_size_log", "leverage", "roa",
                          "health_breach", "prior_events"), 49999)
show("Announcement elevation (daily pp)", r)
do.call(add, c(list("Essay 2", "Announcement-window elevation (daily pp)", TREAT), r))

# =====================================================================================
# ESSAY 3 - linear probability model of executive departure (N = 405)
#   y = departure within 30 / 90 / 180 days of notification, and the placebo window;
#   regressors: scripts/227:79-84 and 193, 214.  Coefficients are proportions.
# =====================================================================================
cat("\nESSAY 3 - governance response (linear probability model; proportions)\n")
e3 <- read.csv("essay3_departures.csv")
X_E3 <- c(TREAT, "prior_breaches_1yr", "health_breach", "firm_size_log", "leverage", "roa",
          "baseline_exec_rate_py_rd", "prior12m_mktadj_ret_rd")
e3_models <- c("30-day" = "exec_departure_30_rd", "90-day" = "exec_departure_90_rd",
               "180-day" = "exec_departure_180_rd", "Placebo" = "placebo_exec_departure_rd")
for (w in names(e3_models)) {
  r <- ladder(e3, e3_models[[w]], X_E3, 99999, hc3 = TRUE)             # B: scripts/227:88
  show(paste("Executive departure,", w), r)
  cat(sprintf("  %-34s HC3 SE %.4f p %.4f | CV3 95%% CI [%+.4f, %+.4f]\n", "", r$se_hc3, r$p_hc3,
              r$ci_cv3_lo, r$ci_cv3_hi))
  do.call(add, c(list("Essay 3", paste("Executive departure,", w), TREAT), r))
}

# -------------------------------------------------------------------------------------
write.csv(results, "r_results.csv", row.names = FALSE)
elapsed <- as.numeric(difftime(Sys.time(), t_start, units = "secs"))
cat(sprintf("\nWrote r_results.csv (%d rows). %s. Seed %d. Run time %.1f seconds.\n",
            nrow(results), R.version.string, SEED, elapsed))
