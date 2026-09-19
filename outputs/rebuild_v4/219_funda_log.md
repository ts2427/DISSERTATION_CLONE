# REBUILD V4 - Stage 6 Compustat fundamentals (scripts/219)

gvkeys to pull: 140
first 3 gvkey literals sent: '001300', '001410', '001440'
sentinel gvkeys: AT&T 009899; Sprint 010984; T-Mobile 017874
  chunk 1: gvkeys 140, rows 5378
comp.funda: 5378 rows; gvkeys reached 140/140 = 100.0%
sentinels reached funda: AT&T, Sprint, T-Mobile
written Data\wrds_v4\comp_funda.csv

## Coverage (gvkey arm)
- firm_size_log: 438 of 489 (v3 inherited 346)
- leverage: 436 of 489 (v3 inherited 346)
- roa: 438 of 489 (v3 inherited 346)
- op_margin: 438 of 489 (v3 inherited 346)

## Ticker vs gvkey agreement (ticker arm is diagnostic only)
     variable  both_present  identical  differ  gvkey_only  ticker_only  max_abs_diff
firm_size_log           330        330       0         108            0           0.0
     leverage           330        330       0         106            0           0.0
          roa           330        330       0         108            0           0.0
    op_margin           330        330       0         108            0           0.0

## Covariate deltas, v3-inherited vs v4-refreshed
change         changed  gained  identical
variable                                 
firm_size_log        1      92        345
leverage             1      90        345
op_margin            1      92        345
roa                  1      92        345

By treated/control (non-identical only):
change   changed  gained
treated                 
0              0     358
1              4       8

written 219_covariates_v4.csv, 219_covariate_deltas.csv, 219_ticker_gvkey_agreement.csv
