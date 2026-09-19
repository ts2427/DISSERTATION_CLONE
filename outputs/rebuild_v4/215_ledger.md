# REBUILD V4 — Stage 5 ledger

- run (UTC): 2026-09-19T00:24:34+00:00
- CANONICAL_V4: 489 rows | 212 links: 489 rows (positional join asserted)
- CRSP daily extract reaches 2024-12-31; v3 was built on 2024-12-31

## Ledger, v3 against v4

| step | status | N_v3 | N_v4 | treated_v3 | treated_v4 | control_v3 | control_v4 |
|---|---|---|---|---|---|---|---|
| PRC notification records (master_breach_dataset.xlsx) | upstream_of_v4 | 1054 | 1054 |  |  |  |  |
| Gate 1: signed parent CIK | upstream_of_v4 | 758 | 758 |  |  |  |  |
| Stage 3: CIK+date firm-day events | upstream_of_v4 | 524 | 524 |  |  |  |  |
| Gate 2 adjacency collapse | upstream_of_v4 | 491 | 491 |  |  |  |  |
| Stage 4/5 canonical events (CANONICAL_V3) | computed | 489 | 489 | 118.0 | 118 | 371.0 | 371 |
| CRSP data (has_crsp_data) | computed | 356 | 378 | 111.0 | 111 | 245.0 | 267 |
| Compustat covariates (size, leverage, ROA) = Query 2 scope | not_computable_until_stage6 | 341 |  | 107.0 |  | 234.0 |  |
| Outcome-data requirement (>=1 8-K in [t0-730d, t0+180d], outcome CIK) | not_computable_until_stage6 | 340 |  | 107.0 |  | 233.0 |  |
| Prior 12-month market-adjusted return available (>=150 daily returns) | not_computable_until_stage6 | 338 |  | 107.0 |  | 231.0 |  |

## Symmetry

| measure | value | treated | control | total |
|---|---|---|---|---|
| link_source | (unlinked) | 7 | 104 | 111 |
| link_source | cusip_header | 7 | 25 | 32 |
| link_source | cusip_ncusip | 104 | 242 | 346 |
| crsp_retention | v3 linked | 111 | 250 | 361 |
| crsp_retention | v4 linked | 111 | 267 | 378 |
| crsp_retention | delta v4-v3 | 0 | 17 | 17 |

## Attribution of the CRSP-step gain

The pulled `crsp.dsf` reaches 2024-12-31, which does NOT extend past the 2024-12-31 extract v3 used. The **added by the longer extract** line is therefore empty by construction, and every gain below is attributable to relinking.

| cause | treated | control | total |
|---|---|---|---|
| recovered by relinking | 0 | 42 | 42 |
| added by the longer extract | 0 | 0 | 0 |
| gained but window past the extract, not covered | 0 | 0 | 0 |
| overlap (counted under relinking only) | 0 | 0 | 0 |
| GAINED: linked in v4, not in v3 | 0 | 42 | 42 |
| LOST: linked in v3, not in v4 | 0 | 25 | 25 |
| NET change (gained - lost) | 0 | 17 | 17 |

