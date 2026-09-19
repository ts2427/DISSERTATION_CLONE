# REBUILD V4 — Stage 4 corrections

- run (UTC): 2026-09-19T13:53:37+00:00
- input: `Data/processed/rebuild/CANONICAL_V3.csv` (489 rows, read-only)
- Stage 4 issues no SEC request; the EDGAR cache is read, never written.

## Corrections applied

- Sprint: recomputation reproduces the stored prior_breaches_1yr exactly (12 rows) under the original dates, so the rule matches v3's.
- International Paper: CIK 1283246 -> 51434 on 1 row(s).
- Lennar: CIK 58696 -> 920760 on 1 row(s).
- Stage 3: read 44 verdict row(s) from 213_verification_log.csv, stage3b_213_verification_log.csv.
- Stage 3: 25 event(s) re-parented, 4 verified without a CIK change (the verified registrant was already the event CIK); 15 UNVERIFIED row(s) left untouched and excluded.

| kind | cik | org_name | breach_date | old_value | new_value | applied |
|---|---|---|---|---|---|---|
| breach_date | 101830 | Sprint Nextel | 2012-08-01 | 2012-08-01 | 2009-01-01 | YES |
| prior_breaches_1yr | 101830 | Sprint | 2009-02-01 | 0 | 1 | YES |
| reported_date_excluded | 1125259 | Carnival Corporation & PLC | 2019-04-01 | 2020-03 | (missing) | YES |
| final_cik | 1283246 | International Paper Company | 2023-05-30 | 1283246 | 51434 | YES |
| final_cik | 58696 | Lennar Corporation | 2023-07-20 | 58696 | 920760 | YES |
| stage3_a_subsidiary | 72945 | Northrop Grumman Systems Corporation | 2016-04-18 | 72945 | 1133421 | YES |
| stage3_a_subsidiary | 108772 | Xerox Corporation | 2023-12-10 | 108772 | 1770450 | YES |
| stage3_a_subsidiary | 353394 | Leidos, Inc. | 2022-09-30 | 353394 | 1336920 | YES |
| stage3_b_successor_cik | 813828 | Paramount | 2023-01-01 | 813828 | 2041610 | YES |
| stage3_b_successor_cik | 813828 | Paramount Global | 2023-08-10 | 813828 | 2041610 | YES |
| stage3_b_successor_cik | 912752 | Sinclair Broadcast Group, Inc. | 2020-05-01 | 912752 | 1971213 | YES |
| stage3_b_successor_cik | 912752 | Sinclair Broadcast Group, Inc. | 2021-06-23 | 912752 | 1971213 | YES |
| stage3_b_successor_cik | 912752 | Sinclair Broadcast Group, Inc. | 2021-12-16 | 912752 | 1971213 | YES |
| stage3_b_successor_cik | 926480 | The Walt Disney Company | 2008-07-29 | 926480 | 1744489 | YES |
| stage3_a_subsidiary | 1137785 | Seagate US LLC | 2016-02-29 | 1137785 | 1137789 | YES |
| stage3_a_subsidiary | 1137785 | Seagate US LLC | 2016-03-14 | 1137785 | 1137789 | YES |
| stage3_a_subsidiary | 1205274 | Herbalife International of America, Inc. | 2022-02-01 | 1205274 | 1180262 | YES |
| stage3_b_successor_cik | 1288776 | Google, Inc. | 2008-06-27 | 1288776 | 1652044 | YES |
| stage3_a_subsidiary | 1387793 | T. Rowe Price Retirement Plan Services, Inc. | 2007-12-24 | 1387793 | 1113169 | YES |
| stage3_a_subsidiary | 1387793 | T. Rowe Price Retirement Plan Services, Inc. | 2023-05-29 | 1387793 | 1113169 | YES |
| stage3_a_subsidiary | 1457738 | iHeartMedia + Entertainment, Inc. | 2024-12-24 | 1457738 | 1400891 | YES |
| stage3_a_subsidiary | 1457738 | iHeartMedia + Entertainment, Inc. | 2025-04-30 | 1457738 | 1400891 | YES |
| stage3_a_subsidiary | 1501362 | J.B. Hunt Transport, Inc. | 2020-08-01 | 1501362 | 728535 | YES |
| stage3_a_subsidiary | 1501362 | J.B. Hunt Transport, Inc. | 2020-08-17 | 1501362 | 728535 | YES |
| stage3_a_subsidiary | 1516658 | Gates Corporation | 2023-02-07 | 1516658 | 1718512 | YES |
| stage3_a_subsidiary | 1516658 | Gates Corporation | 2023-02-11 | 1516658 | 1718512 | YES |
| stage3_b_successor_cik | 1808065 | Aon Corporation PLC | 2020-12-29 | 1808065 | 315293 | YES |
| stage3_b_successor_cik | 1808065 | Aon PLC | 2022-02-25 | 1808065 | 315293 | YES |
| stage3_a_subsidiary | 1870564 | Activision Publishing, Inc. | 2012-08-01 | 1870564 | 718877 | YES |
| stage3_a_subsidiary | 1870564 | Activision Publishing, Inc. | 2022-12-02 | 1870564 | 718877 | YES |

### Sprint — prior_breaches_1yr, every event

| breach_date | prior_breaches_1yr_old | prior_breaches_1yr_new |
|---|---|---|
| 2009-01-01 | 0 | 0 |
| 2009-02-01 | 0 | 1 |
| 2015-08-17 | 0 | 0 |
| 2017-05-01 | 0 | 0 |
| 2017-05-07 | 1 | 1 |
| 2018-03-02 | 2 | 2 |
| 2019-03-14 | 0 | 0 |
| 2019-05-09 | 1 | 1 |
| 2019-06-02 | 2 | 2 |
| 2019-06-08 | 3 | 3 |
| 2019-06-22 | 4 | 4 |
| 2019-08-13 | 5 | 5 |

## Report-only (no change)

- **Dell Inc.** (CIK 826083): EDGAR registrant DELL INC; 533 filings within +/-2 years of the 2013-02-26 breach; no other filer normalises to the same name. The CIK is active and correct - the row is excluded for want of a Compustat gvkey, which is a coverage limit, not a CIK error.
- **Warn Industries, Inc.** (CIK 1984463): Dover Corporation's Exhibit 21 (CIK 29905, accession 0000029905-18-000019, selected by document type EX-21) contains exactly one line matching WARN: 'Warn Automotive, LLC'. 'Warn Industries, Inc.' is not listed. Documented exclusion, not a matcher failure.
- **Uber** (CIK 1431473): Stage 2 nominated UBER TECHNOLOGIES INC (cik 1543151) on the shared token UBER. No Exhibit 21 or succession filing has been produced for the identity, so the row stays excluded and the CIK is left as recorded.

Rows differing from CANONICAL_V3 on final_cik or breach_date: 28

