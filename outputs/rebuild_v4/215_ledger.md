# REBUILD V4 — Stage 5 ledger

- run (UTC): 2026-09-19T14:08:37+00:00
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
| CRSP data (has_crsp_data) | computed | 356 | 414 | 111.0 | 111 | 245.0 | 303 |
| Compustat covariates (size, leverage, ROA) = Query 2 scope | not_computable_until_stage6 | 341 |  | 107.0 |  | 234.0 |  |
| Outcome-data requirement (>=1 8-K in [t0-730d, t0+180d], outcome CIK) | not_computable_until_stage6 | 340 |  | 107.0 |  | 233.0 |  |
| Prior 12-month market-adjusted return available (>=150 daily returns) | not_computable_until_stage6 | 338 |  | 107.0 |  | 231.0 |  |

## Symmetry

| measure | value | treated | control | total |
|---|---|---|---|---|
| link_source | (unlinked) | 7 | 68 | 75 |
| link_source | cusip_header | 7 | 32 | 39 |
| link_source | cusip_issuer | 0 | 7 | 7 |
| link_source | cusip_ncusip | 104 | 264 | 368 |
| crsp_retention | v3 linked | 111 | 250 | 361 |
| crsp_retention | v4 linked | 111 | 303 | 414 |
| crsp_retention | delta v4-v3 | 0 | 53 | 53 |

## Attribution of the CRSP-step gain

The pulled `crsp.dsf` reaches 2024-12-31, which does NOT extend past the 2024-12-31 extract v3 used. The **added by the longer extract** line is therefore empty by construction, and every gain below is attributable to relinking.

| cause | treated | control | total |
|---|---|---|---|
| recovered by relinking | 0 | 62 | 62 |
| added by the longer extract | 0 | 0 | 0 |
| gained but window past the extract, not covered | 0 | 1 | 1 |
| overlap (counted under relinking only) | 0 | 0 | 0 |
| GAINED: linked in v4, not in v3 | 0 | 63 | 63 |
| LOST: linked in v3, not in v4 | 0 | 10 | 10 |
| NET change (gained - lost) | 0 | 53 | 53 |

## Documented exclusions

Residual losses that are accounted for by name. None is a candidate for a further top-up.

- **Yahoo (CIK 1011006, 4 events, 2012-2016)** — comp.company maps this CIK to gvkey 62634 ALTABA INC - the post-2017 rump, a registered closed-end fund (shrcd 14), whose only security runs 2017-06-19 onward. Its CRSP permco differs from the pre-2017 Yahoo! Inc. permno 83435, so neither the issuer nor the permco fallback reaches the security that existed at any of the four breach dates.
- **Nokia (CIK 924613, 2013-07-22)** — the security CRSP carries is an ADR (shrcd 31), a claim on a foreign share rather than the share itself. ADRs are excluded by rule, not by accident.
- **Audacy / Entercom (2019)** — the only match is a header-CUSIP hit against the former name ENTERCOM, which the identity gate rejects. That is by rule indistinguishable from the MetroPCS/T-Mobile case the gate exists to catch: CRSP back-fills the header CUSIP and keeps one permno across the rename. v3 did not link it either, so no comparison is lost.

## Documented identifications

- **Paramount (CIK 2041610, 2 events, 2023)** — v4 links permno 75104 on the Class A CUSIP 92556H10 - the only share class on the successor's comp.security record - selected by the exact 8-char ncusip match, which runs before any fallback. v3 used permno 76226 (92556H20, the other class). Both are Paramount Global; the difference is which class the identifier resolves to, not which company.

## Events linked in v3 but not in v4

| category | control |
|---|---|
| a_no_usable_returns_in_v3 | 5 |
| c_v4_gap | 5 |

| category | org_name | orig_cik | final_cik | breach_date | group | v3_permno | v3_comnam_at_breach | v4_reason |
|---|---|---|---|---|---|---|---|---|
| a_no_usable_returns_in_v3 | Nucor Corporation | 73309 | 73309 | 2025-05-03 | control | 34817.0 | (no CRSP name row valid at breach_date) | no names row valid on breach_date |
| a_no_usable_returns_in_v3 | Intuit Inc. | 896878 | 896878 | 2025-01-21 | control | 78975.0 | (no CRSP name row valid at breach_date) | no names row valid on breach_date |
| c_v4_gap | Nokia Inc. | 924613 | 924613 | 2013-07-22 | control | 87128.0 | NOKIA CORP | shrcd not in [10, 11, 12, 18, 72] ([31]) |
| c_v4_gap | Yahoo! Voices | 1011006 | 1011006 | 2012-07-11 | control | 83435.0 | (permno absent from the CUSIP-filtered pull) | no names row valid on breach_date |
| c_v4_gap | Yahoo! Inc. | 1011006 | 1011006 | 2013-08-01 | control | 83435.0 | (permno absent from the CUSIP-filtered pull) | no names row valid on breach_date |
| c_v4_gap | Yahoo | 1011006 | 1011006 | 2014-12-01 | control | 83435.0 | (permno absent from the CUSIP-filtered pull) | no names row valid on breach_date |
| c_v4_gap | Yahoo Inc. | 1011006 | 1011006 | 2016-08-13 | control | 83435.0 | (permno absent from the CUSIP-filtered pull) | no names row valid on breach_date |
| a_no_usable_returns_in_v3 | Workday Inc. | 1327811 | 1327811 | 2025-08-06 | control | 13628.0 | (no CRSP name row valid at breach_date) | no names row valid on breach_date |
| a_no_usable_returns_in_v3 | Hewlett Packard Enterprise Company | 1645590 | 1645590 | 2025-02-05 | control | 15707.0 | (no CRSP name row valid at breach_date) | no names row valid on breach_date |
| a_no_usable_returns_in_v3 | Zscaler Inc. | 1713683 | 1713683 | 2025-08-08 | control | 17341.0 | (no CRSP name row valid at breach_date) | no names row valid on breach_date |

Sub-causes within each category:

| category | sub_cause | events |
|---|---|---|
| a_no_usable_returns_in_v3 | v3 flagged has_crsp_data False | 5 |
| c_v4_gap | excluded by share code: shrcd not in [10, 11, 12, 18, 72] ([31]) | 1 |
| c_v4_gap | v3 permno absent from the CUSIP-filtered pull | 4 |

## Stage 3b worklist

No event's loss is fixable by a top-up.

