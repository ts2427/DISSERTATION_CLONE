# REBUILD V4 - outcome-window censoring (scripts/232)

Reports only. No censoring rule is applied and no event is dropped.

in-scope events: 412  (treated 109, control 303)
events with a usable filing history: 412

## Censored events - anchor 'rd'
(window end is past the outcome CIK's last filing of any form)
 window  censored  treated  control  treated_pct  control_pct  median_days_uncovered
     30         0        0        0          0.0          0.0                      0
     90         0        0        0          0.0          0.0                      0
    180         0        0        0          0.0          0.0                      0
entire window uncovered (last filing on or before t0): 0  (treated 0, control 0)

## Censored events - anchor 'bd'
(window end is past the outcome CIK's last filing of any form)
 window  censored  treated  control  treated_pct  control_pct  median_days_uncovered
     30         0        0        0          0.0          0.0                      0
     90         0        0        0          0.0          0.0                      0
    180         0        0        0          0.0          0.0                      0
entire window uncovered (last filing on or before t0): 0  (treated 0, control 0)

## Margin, not just the count (rd anchor, 180d window)
days between the window end and the outcome CIK's last filing:
count     412.0
mean     2689.0
std      1636.0
min        26.0
25%      1129.0
50%      2718.0
75%      3608.0
max      6961.0

tightest 5 events:
                          org_name breach_date  outcome_cik      t0_rd last_filing  days_of_slack
          NextGen Healthcare, Inc.  2023-03-29       708818 2023-04-28  2023-11-20             26
       Activision Publishing, Inc.  2022-12-02       718877 2023-02-20  2024-06-11            297
 iHeartMedia + Entertainment, Inc.  2024-12-24      1400891 2025-04-11  2026-08-13            309
Hewlett Packard Enterprise Company  2023-12-12      1645590 2025-02-05  2026-07-28            358
                        Intuit Inc  2024-03-05       896878 2024-12-20  2026-07-31            408

Every event clears its window, so the zero above is a real result and not an
empty computation. Breaches are old relative to the filing histories, and the
firms that stopped filing did so after their event windows closed.

## Reading these counts
A censored event contributes a zero that may mean 'not observable'.
If the treated and control percentages differ materially at a given
window, censoring is DIFFERENTIAL and a rule that drops censored events
changes the treated/control composition. Every v4 linkage gain fell on
the control side, so the two can compound.

written outputs\essay3_v4\232_censoring.csv
