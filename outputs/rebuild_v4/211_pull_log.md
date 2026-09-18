# REBUILD V4 — Stage 1 WRDS pull log (CUSIP route)

- CIK filter list: 185 CIKs (162 from CANONICAL_V3, +23 nominated parents not already present)
- route: CIK -> gvkey -> CUSIP(8) -> permno   (CCM is blocked; see scripts/216)
- pull started (UTC): 2026-09-18T19:11:37+00:00
- daily data from: 2005-01-01

- WRDS username: tispivey   (no password is stored, printed, or logged)

## 1. comp.company (filtered by CIK)  ->  gvkey
  CIK literal form that matched: zero-padded 10-char
  priusa column present: True
  CIK -> gvkey: 148 / 185 = 80.0%
  sentinels reached a gvkey: Sprint=1, AT&T=1, T-Mobile=1
  gvkeys reached: 148
  wrote Data\wrds_v4\comp_company.csv  rows=148  0.1 MB  sha256=792b590fda8f0d5526fab5a84105a4e7c0a87b76097113e2d7e60a6fbe36776e

## 2. comp.security (filtered by gvkey)  ->  CUSIP
  security rows: 308   raw cusip lengths: [9] -> trimmed to 8
  trim sample: [['438516205', '43851620'], ['438516130', '43851613'], ['43856Q107', '43856Q10']]
  gvkey -> CUSIP: 148 / 148 = 100.0%
  sentinels reached a CUSIP: Sprint=6, AT&T=4, T-Mobile=3
  distinct 8-char CUSIPs reached: 307
  wrote Data\wrds_v4\comp_security.csv  rows=308  0.0 MB  sha256=9935171501ef2a68d6f7c6d9debeed780a40664dfb951e517788125a70f56a51

## 3. crsp.stocknames (filtered by 8-char CUSIP, ncusip OR cusip)  ->  permno
  name rows: 613   matched via ncusip: 165, via header cusip: 165
  CUSIP -> permno: 165 / 307 = 53.7%
  sentinels reached a permno: Sprint=2, AT&T=1, T-Mobile=1
  permnos reached: 165
  wrote Data\wrds_v4\crsp_stocknames.csv  rows=613  0.0 MB  sha256=e9cb84bb0d5fdc5ef269650d143783435e8de6f98e067c9e1f4459abcafd815e

## 4. crsp.dsf (filtered by permno; the dominant payload)
  daily rows: 591,717   range: 2005-01-03 .. 2024-12-31
  permno -> daily returns: 150 / 165 = 90.9%
  wrote Data\wrds_v4\crsp_dsf.csv  rows=591,717  36.5 MB  sha256=b66d255b3f665a02a47827412b961c389e71b88121111d2f0f8eee794a95fea1

## 5. crsp.dsi (market index, date range only)
  index rows: 5,033   range: 2005-01-03 .. 2024-12-31
  wrote Data\wrds_v4\crsp_dsi.csv  rows=5,033  0.2 MB  sha256=71555c4aee3db70cbfe5e38ae25ea726acffbfd904c9977677d5b4f0a3562e6e

## CRSP coverage end date
- max(crsp.dsf.date) = 2024-12-31
- v3 committed extract ended 2024-12-31
- does not extend past v3; the past-extract exclusions stand

## Files written

| file | rows | MB | sha256 |
|---|---:|---:|---|
| `Data\wrds_v4\comp_company.csv` | 148 | 0.1 | `792b590fda8f0d5526fab5a84105a4e7c0a87b76097113e2d7e60a6fbe36776e` |
| `Data\wrds_v4\comp_security.csv` | 308 | 0.0 | `9935171501ef2a68d6f7c6d9debeed780a40664dfb951e517788125a70f56a51` |
| `Data\wrds_v4\crsp_stocknames.csv` | 613 | 0.0 | `e9cb84bb0d5fdc5ef269650d143783435e8de6f98e067c9e1f4459abcafd815e` |
| `Data\wrds_v4\crsp_dsf.csv` | 591,717 | 36.5 | `b66d255b3f665a02a47827412b961c389e71b88121111d2f0f8eee794a95fea1` |
| `Data\wrds_v4\crsp_dsi.csv` | 5,033 | 0.2 | `71555c4aee3db70cbfe5e38ae25ea726acffbfd904c9977677d5b4f0a3562e6e` |

- total written: 36.8 MB

## Hit rates (distinct keys reached, never row counts)

| step | reached | requested | rate |
|---|---:|---:|---:|
| CIK -> gvkey | 148 | 185 | 80.0% |
| gvkey -> CUSIP | 148 | 148 | 100.0% |
| CUSIP -> permno | 165 | 307 | 53.7% |
| permno -> daily returns | 150 | 165 | 90.9% |

- pull finished (UTC): 2026-09-18T19:12:05+00:00

## Determinism note (appended at commit)

`comp_company.csv` from this run reproduces the file written by the aborted run 1
**byte for byte**:

```
run 1 (aborted): 792b590fda8f0d5526fab5a84105a4e7c0a87b76097113e2d7e60a6fbe36776e
run 2 (this)   : 792b590fda8f0d5526fab5a84105a4e7c0a87b76097113e2d7e60a6fbe36776e
```

Two separate WRDS sessions, the same 185-CIK filter, the same 148 gvkeys, identical
bytes. That is evidence the CIK -> gvkey step is deterministic and that the zero-padded
10-character CIK form is stable, not an artifact of one session.

Run 1's partial output is retained untracked at
`Data/wrds_v4/_aborted_run_1/comp_company.csv` and is excluded from this commit.
