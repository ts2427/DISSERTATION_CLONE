# REBUILD V4 — Stage 5 ledger

- run (UTC): 2026-09-19T00:39:19+00:00
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
| CRSP data (has_crsp_data) | computed | 356 | 393 | 111.0 | 111 | 245.0 | 282 |
| Compustat covariates (size, leverage, ROA) = Query 2 scope | not_computable_until_stage6 | 341 |  | 107.0 |  | 234.0 |  |
| Outcome-data requirement (>=1 8-K in [t0-730d, t0+180d], outcome CIK) | not_computable_until_stage6 | 340 |  | 107.0 |  | 233.0 |  |
| Prior 12-month market-adjusted return available (>=150 daily returns) | not_computable_until_stage6 | 338 |  | 107.0 |  | 231.0 |  |

## Symmetry

| measure | value | treated | control | total |
|---|---|---|---|---|
| link_source | (unlinked) | 7 | 89 | 96 |
| link_source | cusip_header | 7 | 28 | 35 |
| link_source | cusip_ncusip | 104 | 254 | 358 |
| crsp_retention | v3 linked | 111 | 250 | 361 |
| crsp_retention | v4 linked | 111 | 282 | 393 |
| crsp_retention | delta v4-v3 | 0 | 32 | 32 |

## Attribution of the CRSP-step gain

The pulled `crsp.dsf` reaches 2024-12-31, which does NOT extend past the 2024-12-31 extract v3 used. The **added by the longer extract** line is therefore empty by construction, and every gain below is attributable to relinking.

| cause | treated | control | total |
|---|---|---|---|
| recovered by relinking | 0 | 56 | 56 |
| added by the longer extract | 0 | 0 | 0 |
| gained but window past the extract, not covered | 0 | 1 | 1 |
| overlap (counted under relinking only) | 0 | 0 | 0 |
| GAINED: linked in v4, not in v3 | 0 | 57 | 57 |
| LOST: linked in v3, not in v4 | 0 | 25 | 25 |
| NET change (gained - lost) | 0 | 32 | 32 |

## Events linked in v3 but not in v4

| category | control |
|---|---|
| a_no_usable_returns_in_v3 | 5 |
| c_v4_gap | 20 |

| category | org_name | orig_cik | final_cik | breach_date | group | v3_permno | v3_comnam_at_breach | v4_reason |
|---|---|---|---|---|---|---|---|---|
| a_no_usable_returns_in_v3 | Nucor Corporation | 73309 | 73309 | 2025-05-03 | control | 34817.0 | (no CRSP name row valid at breach_date) | no names row valid on breach_date |
| c_v4_gap | Aon Corporation | 315293 | 315293 | 2020-12-17 | control | 61735.0 | AON PLC NEW | shrcd not in {10,11} ([12]) |
| c_v4_gap | Honeywell International Inc. | 773840 | 773840 | 2021-02-16 | control | 10145.0 | (permno absent from the CUSIP-filtered pull) | no names row valid on breach_date |
| c_v4_gap | Honeywell International, Inc. | 773840 | 773840 | 2023-05-27 | control | 10145.0 | (permno absent from the CUSIP-filtered pull) | no names row valid on breach_date |
| c_v4_gap | Honeywell International Inc. | 773840 | 773840 | 2023-06-03 | control | 10145.0 | (permno absent from the CUSIP-filtered pull) | no names row valid on breach_date |
| c_v4_gap | Paramount | 813828 | 813828 | 2023-01-01 | control | 76226.0 | (permno absent from the CUSIP-filtered pull) | no gvkey |
| c_v4_gap | Paramount Global | 813828 | 813828 | 2023-08-10 | control | 76226.0 | (permno absent from the CUSIP-filtered pull) | no gvkey |
| c_v4_gap | Carnival Corporation | 815097 | 815097 | 2020-12-25 | control | 75154.0 | (permno absent from the CUSIP-filtered pull) | no names row valid on breach_date |
| c_v4_gap | Carnival Corporation | 815097 | 815097 | 2021-03-19 | control | 75154.0 | (permno absent from the CUSIP-filtered pull) | no names row valid on breach_date |
| a_no_usable_returns_in_v3 | Intuit Inc. | 896878 | 896878 | 2025-01-21 | control | 78975.0 | (no CRSP name row valid at breach_date) | no names row valid on breach_date |
| c_v4_gap | Essex Property Trust, Inc. | 920522 | 920522 | 2013-08-13 | control | 80681.0 | ESSEX PROPERTY TRUST INC | shrcd not in {10,11} ([18]) |
| c_v4_gap | Nokia Inc. | 924613 | 924613 | 2013-07-22 | control | 87128.0 | NOKIA CORP | no names row valid on breach_date |
| c_v4_gap | The Walt Disney Company | 926480 | 926480 | 2008-07-29 | control | 26403.0 | (permno absent from the CUSIP-filtered pull) | no gvkey |
| c_v4_gap | Yahoo! Voices | 1011006 | 1011006 | 2012-07-11 | control | 83435.0 | (permno absent from the CUSIP-filtered pull) | no names row valid on breach_date |
| c_v4_gap | Yahoo! Inc. | 1011006 | 1011006 | 2013-08-01 | control | 83435.0 | (permno absent from the CUSIP-filtered pull) | no names row valid on breach_date |
| c_v4_gap | Yahoo | 1011006 | 1011006 | 2014-12-01 | control | 83435.0 | (permno absent from the CUSIP-filtered pull) | no names row valid on breach_date |
| c_v4_gap | Yahoo Inc. | 1011006 | 1011006 | 2016-08-13 | control | 83435.0 | (permno absent from the CUSIP-filtered pull) | no names row valid on breach_date |
| c_v4_gap | Seagate Technology LLC | 1137789 | 1137789 | 2017-07-08 | control | 89641.0 | SEAGATE TECHNOLOGY PLC | shrcd not in {10,11} ([12]) |
| c_v4_gap | Google, Inc. | 1288776 | 1288776 | 2008-06-27 | control | 90319.0 | GOOGLE INC | no gvkey |
| a_no_usable_returns_in_v3 | Workday Inc. | 1327811 | 1327811 | 2025-08-06 | control | 13628.0 | (no CRSP name row valid at breach_date) | no names row valid on breach_date |
| c_v4_gap | CyrusOne, Inc. | 1553023 | 1553023 | 2017-10-18 | control | 13752.0 | CYRUSONE INC | shrcd not in {10,11} ([18]) |
| a_no_usable_returns_in_v3 | Hewlett Packard Enterprise Company | 1645590 | 1645590 | 2025-02-05 | control | 15707.0 | (no CRSP name row valid at breach_date) | no names row valid on breach_date |
| a_no_usable_returns_in_v3 | Zscaler Inc. | 1713683 | 1713683 | 2025-08-08 | control | 17341.0 | (no CRSP name row valid at breach_date) | no names row valid on breach_date |
| c_v4_gap | Aon Corporation PLC | 1808065 | 315293 | 2020-12-29 | control | 61735.0 | AON PLC NEW | shrcd not in {10,11} ([12]) |
| c_v4_gap | Aon PLC | 1808065 | 315293 | 2022-02-25 | control | 61735.0 | AON PLC NEW | shrcd not in {10,11} ([12]) |

Sub-causes within each category:

| category | sub_cause | events |
|---|---|---|
| a_no_usable_returns_in_v3 | v3 flagged has_crsp_data False | 5 |
| c_v4_gap | excluded by share code: shrcd not in {10,11} ([12]) | 4 |
| c_v4_gap | excluded by share code: shrcd not in {10,11} ([18]) | 2 |
| c_v4_gap | no names row valid on breach_date | 1 |
| c_v4_gap | the CIK has no Compustat gvkey, so the chain cannot start | 4 |
| c_v4_gap | v3 permno absent from the CUSIP-filtered pull | 9 |

