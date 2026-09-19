# REBUILD V4 — Stage 4 corrections

- run (UTC): 2026-09-19T00:22:40+00:00
- input: `Data/processed/rebuild/CANONICAL_V3.csv` (489 rows, read-only)
- Stage 4 issues no SEC request; the EDGAR cache is read, never written.

## Corrections applied

- Sprint: recomputation reproduces the stored prior_breaches_1yr exactly (12 rows) under the original dates, so the rule matches v3's.
- International Paper: CIK 1283246 -> 51434 on 1 row(s).
- Lennar: CIK 58696 -> 920760 on 1 row(s).

| kind | cik | org_name | breach_date | old_value | new_value | applied |
|---|---|---|---|---|---|---|
| breach_date | 101830 | Sprint Nextel | 2012-08-01 | 2012-08-01 | 2009-01-01 | YES |
| prior_breaches_1yr | 101830 | Sprint | 2009-02-01 | 0 | 1 | YES |
| reported_date_excluded | 1125259 | Carnival Corporation & PLC | 2019-04-01 | 2020-03 | (missing) | YES |
| final_cik | 1283246 | International Paper Company | 2023-05-30 | 1283246 | 51434 | YES |
| final_cik | 58696 | Lennar Corporation | 2023-07-20 | 58696 | 920760 | YES |

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

Rows differing from CANONICAL_V3 on final_cik or breach_date: 3

