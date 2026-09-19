# REBUILD V4 - outcome-CIK gap (scripts/230)

Item 5.02 cache on disk: 121 CIK directories, 1534 documents

## Scope
events in CANONICAL_V4        : 489
linked in v4                  : 414
in outcome scope (linked+cov) : 412  (treated 109, control 303)

## Item 5.02 coverage, scope events, by treated/control
cached   not_cached  cached
treated                    
0                 1     302
1                 0     109

## Outcome CIKs needing a fetch
scope events with no cached documents: 1  (treated 0, control 1)
distinct outcome CIKs to fetch       : 1

 outcome_cik outcome_rule                 org_name breach_date  treated  resolve_contested     win_lo     win_hi outcome_unresolved
    860731.0    final_cik Tyler Technologies, Inc.  2020-09-21        0                  0 2018-09-22 2021-07-17                NaN

written outputs\rebuild_v4\230_outcome_cik_gap.csv
