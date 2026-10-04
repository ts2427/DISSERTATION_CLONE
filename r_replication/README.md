# R replication of the headline estimates

For Dr. Affuso. This folder reproduces, in R, the headline estimates of the dissertation *Data Breach Disclosure Timing and Market Reactions* (Timothy D. Spivey), and checks them against the Python results frozen at the repository tag `defense-final` (`902a8ea`).

**The full pipeline is in Python.** Data construction, every robustness table and the appendix are in the main repository. These files reproduce the headline estimates only: one baseline model for Essay 1, four models for Essay 2 and four for Essay 3.

## What is here

| File | What it is |
|---|---|
| `replicate.R` | The R script. Every inference method is written out in base R, so each number can be read off the code |
| `essay1_car.csv` | Essay 1 regression sample, N = 340 |
| `essay2_volatility.csv` | Essay 2 sample, N = 333 (volatility change and disclosure delay) |
| `essay2_announcement.csv` | Essay 2 announcement-window sample, N = 331 |
| `essay3_departures.csv` | Essay 3 sample, N = 405 |
| `DATA_DICTIONARY.md` | Every column: definition, units, and the Python script that builds it |
| `r_results.csv` | Output of `replicate.R`: essay, model, term, statistic, R value |
| `VERIFICATION.md` | Every R value beside the committed Python value |
| `export_data.py`, `verify_against_python.py` | How the CSVs were exported and how the comparison was made (these two need the full repository; the R script does not) |

The data files hold derived variables only: event-level outcomes, the treatment indicator, the parent-CIK cluster id and the controls. They contain no raw CRSP or Compustat fields.

## How to run

```
cd r_replication
Rscript replicate.R
```

- **R version:** 4.5.0 (any recent R should work).
- **Packages:** `sandwich` and `lmtest`, used only for the HC3 rows (`install.packages(c("sandwich", "lmtest"))`). Everything else is base R.
- **Run time:** about 5 seconds.
- **Output:** a summary printed to the console, and `r_results.csv`.

## What it estimates

- **Essay 1:** OLS of the 30-day CAR on the four hypothesis variables and three controls. Reports HC3 standard errors and p-values, 95% and 90% CIs, the TOST p-value against ±2.10 percentage points, MDE80 = 2.8 × SE, and the parent-CIK clustered p-value.
- **Essay 2:** the Form 499 coefficient on the volatility change, on disclosure delay (raw and winsorized), and on the announcement-window elevation. Each has CV1, the CV3 jackknife (t with G − 1 df) and the restricted wild cluster bootstrap (Rademacher), plus the CV3 MDE80.
- **Essay 3:** the linear probability model of executive departure at 30, 90 and 180 days, and the placebo. Each has HC3, CV1, CV3 and the wild cluster bootstrap, plus the CV3 confidence interval and MDE80.

Each R function names the Python file and lines it mirrors.

## Does it match?

See `VERIFICATION.md`.

- **Analytic values:** every coefficient, standard error, analytic p-value, confidence interval, TOST p-value and MDE matches the committed Python value to four decimal places.
- **Bootstrap p-values:** they agree within Monte Carlo error. They cannot match exactly, because R and Python draw different random numbers. The script uses the same number of draws as Python (99,999; 49,999 for the announcement model) and a fixed seed (499).
