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

---

# REBUILD V4 — Stage 1 TOP-UP pull, CUSIP route (20260919T000910Z)

- top-up source: `outputs/rebuild_v4/213_extra_ciks.txt`
- CIK filter list: 1 CIKs (top-up only; the first pull is untouched)
- output suffix: `_topup_20260919T000910Z`
- route: CIK -> gvkey -> CUSIP(8) -> permno   (CCM is blocked; see scripts/216)
- pull started (UTC): 2026-09-19T00:09:10+00:00
- daily data from: 2005-01-01

- WRDS username: tispivey   (no password is stored, printed, or logged)

## 1. comp.company (filtered by CIK)  ->  gvkey
  CIK literal form that matched: zero-padded 10-char
  priusa column present: True
  CIK -> gvkey: 1 / 1 = 100.0%
  gvkeys reached: 1
  wrote Data\wrds_v4\comp_company_topup_20260919T000910Z.csv  rows=1  0.0 MB  sha256=026a47047fb06298bb50872fda5750dceb23ed8c35579696e7354d7ca043a1f6

## 2. comp.security (filtered by gvkey)  ->  CUSIP
  security rows: 1   raw cusip lengths: [9] -> trimmed to 8
  trim sample: [['00507V109', '00507V10']]
  gvkey -> CUSIP: 1 / 1 = 100.0%
  distinct 8-char CUSIPs reached: 1
  wrote Data\wrds_v4\comp_security_topup_20260919T000910Z.csv  rows=1  0.0 MB  sha256=20e95ad914e011c0587d70d6e08d42d64f5a401be096a6243a371016eb1eaaa8

## 3. crsp.stocknames (filtered by 8-char CUSIP, ncusip OR cusip)  ->  permno
  name rows: 2   matched via ncusip: 1, via header cusip: 1
  CUSIP -> permno: 1 / 1 = 100.0%
  permnos reached: 1
  wrote Data\wrds_v4\crsp_stocknames_topup_20260919T000910Z.csv  rows=2  0.0 MB  sha256=584f5ed5bd0ec407d577ebd8a1232bc64fc79d342dc6aab035e5156491ead735

## 4. crsp.dsf (filtered by permno; the dominant payload)
  daily rows: 4,727   range: 2005-01-03 .. 2023-10-12
  permno -> daily returns: 1 / 1 = 100.0%
  wrote Data\wrds_v4\crsp_dsf_topup_20260919T000910Z.csv  rows=4,727  0.3 MB  sha256=2a51324fe4b4d830630ba1e707d307082b00ea90b5906dfbed607d20af29b3fb

## 5. crsp.dsi (market index, date range only)
  index rows: 5,033   range: 2005-01-03 .. 2024-12-31
  wrote Data\wrds_v4\crsp_dsi_topup_20260919T000910Z.csv  rows=5,033  0.2 MB  sha256=71555c4aee3db70cbfe5e38ae25ea726acffbfd904c9977677d5b4f0a3562e6e

## CRSP coverage end date
- max(crsp.dsf.date) = 2023-10-12
- v3 committed extract ended 2024-12-31
- does not extend past v3; the past-extract exclusions stand

## Files written

| file | rows | MB | sha256 |
|---|---:|---:|---|
| `Data\wrds_v4\comp_company_topup_20260919T000910Z.csv` | 1 | 0.0 | `026a47047fb06298bb50872fda5750dceb23ed8c35579696e7354d7ca043a1f6` |
| `Data\wrds_v4\comp_security_topup_20260919T000910Z.csv` | 1 | 0.0 | `20e95ad914e011c0587d70d6e08d42d64f5a401be096a6243a371016eb1eaaa8` |
| `Data\wrds_v4\crsp_stocknames_topup_20260919T000910Z.csv` | 2 | 0.0 | `584f5ed5bd0ec407d577ebd8a1232bc64fc79d342dc6aab035e5156491ead735` |
| `Data\wrds_v4\crsp_dsf_topup_20260919T000910Z.csv` | 4,727 | 0.3 | `2a51324fe4b4d830630ba1e707d307082b00ea90b5906dfbed607d20af29b3fb` |
| `Data\wrds_v4\crsp_dsi_topup_20260919T000910Z.csv` | 5,033 | 0.2 | `71555c4aee3db70cbfe5e38ae25ea726acffbfd904c9977677d5b4f0a3562e6e` |

- total written: 0.4 MB

## Hit rates (distinct keys reached, never row counts)

| step | reached | requested | rate |
|---|---:|---:|---:|
| CIK -> gvkey | 1 | 1 | 100.0% |
| gvkey -> CUSIP | 1 | 1 | 100.0% |
| CUSIP -> permno | 1 | 1 | 100.0% |
| permno -> daily returns | 1 | 1 | 100.0% |

- pull finished (UTC): 2026-09-19T00:09:33+00:00

### Determinism check against the first pull

`crsp_dsi` is the one table in this pull that is NOT filtered by CIK — it is the market
index over a fixed date range, so the top-up should return exactly what the first pull
returned. It did, byte for byte:

    Data/wrds_v4/crsp_dsi.csv                          sha256 71555c4aee3db70cbfe5e38ae25ea726acffbfd904c9977677d5b4f0a3562e6e
    Data/wrds_v4/crsp_dsi_topup_20260919T000910Z.csv   sha256 71555c4aee3db70cbfe5e38ae25ea726acffbfd904c9977677d5b4f0a3562e6e

Same 5,033 rows, same range 2005-01-03 .. 2024-12-31, identical sha256. WRDS returned a
stable result across two sessions on the one query where that is testable.

The other four files differ from the first pull's, as they must: each is filtered to the
single top-up CIK (718877) rather than the 185 of the first pull.

---

# REBUILD V4 — Stage 1 TOP-UP pull, CUSIP route (20260919T135055Z)

- top-up source: `outputs/rebuild_v4/stage3b_213_extra_ciks.txt`
- issuer/permco pull: True
- CIK filter list: 2 CIKs (top-up only; the first pull is untouched)
- output suffix: `_topup_20260919T135055Z`
- route: CIK -> gvkey -> CUSIP(8) -> permno   (CCM is blocked; see scripts/216)
- pull started (UTC): 2026-09-19T13:50:56+00:00
- daily data from: 2005-01-01

- WRDS username: tispivey   (no password is stored, printed, or logged)

## 1. comp.company (filtered by CIK)  ->  gvkey
  CIK literal form that matched: zero-padded 10-char
  priusa column present: True
  CIK -> gvkey: 2 / 2 = 100.0%
  gvkeys reached: 2
  wrote Data\wrds_v4\comp_company_topup_20260919T135055Z.csv  rows=2  0.0 MB  sha256=710ed40be03f751a6f42d842987051d2483fd7ffe0603952db48ed0fde78e966

## 2. comp.security (filtered by gvkey)  ->  CUSIP
  security rows: 7   raw cusip lengths: [9] -> trimmed to 8
  trim sample: [['254687106', '25468710'], ['25472W105', '25472W10'], ['92556H107', '92556H10']]
  gvkey -> CUSIP: 2 / 2 = 100.0%
  distinct 8-char CUSIPs reached: 7
  wrote Data\wrds_v4\comp_security_topup_20260919T135055Z.csv  rows=7  0.0 MB  sha256=28a8a7739a3b67593811d0e0a0faebb0e9a8284d27b32bd6ab3233dfe089104f

## 3. crsp.stocknames (filtered by 8-char CUSIP, ncusip OR cusip)  ->  permno
  name rows: 20   matched via ncusip: 2, via header cusip: 2
  CUSIP -> permno: 2 / 7 = 28.6%
  permnos reached: 2
  wrote Data\wrds_v4\crsp_stocknames_topup_20260919T135055Z.csv  rows=20  0.0 MB  sha256=8d0b98991639d575b9cb73d45ded02e79f4b0e957e24b33a17ef88cbc79d623e

## 4. crsp.dsf (filtered by permno; the dominant payload)
  daily rows: 10,066   range: 2005-01-03 .. 2024-12-31
  permno -> daily returns: 2 / 2 = 100.0%
  wrote Data\wrds_v4\crsp_dsf_topup_20260919T135055Z.csv  rows=10,066  0.6 MB  sha256=326c79b93d597b8147d048797f437e936c398b4d927e080a7708274570393d77

## 5. crsp.dsi (market index, date range only)
  index rows: 5,033   range: 2005-01-03 .. 2024-12-31
  wrote Data\wrds_v4\crsp_dsi_topup_20260919T135055Z.csv  rows=5,033  0.2 MB  sha256=71555c4aee3db70cbfe5e38ae25ea726acffbfd904c9977677d5b4f0a3562e6e

## CRSP coverage end date
- max(crsp.dsf.date) = 2024-12-31
- v3 committed extract ended 2024-12-31
- does not extend past v3; the past-extract exclusions stand

## ISSUER / PERMCO TOP-UP
  output suffix: `_topup_20260919T135055Z_issuer`
  6-char issuer codes from comp.security (US common): 178
  issuer pass: rows 668  permnos 174  permcos 151
  after permco expansion: rows 673  permnos 176
  wrote Data\wrds_v4\crsp_stocknames_topup_20260919T135055Z_issuer.csv  rows=673  0.1 MB  sha256=6a56453c60941783b5563763ed422e6403dbf3392cb5eefe0563e233c1df5b77
  permnos already pulled: 153   newly reached: 25
  daily rows: 20,199   range: 2005-01-03 .. 2024-12-31
  new permno -> daily returns: 5 / 25 = 20.0%
  wrote Data\wrds_v4\crsp_dsf_topup_20260919T135055Z_issuer.csv  rows=20,199  1.2 MB  sha256=f359f5d0be70e4284f9044fe4e4b585e373bee86d19b3c5ace3fe82ac2a07351

## Files written

| file | rows | MB | sha256 |
|---|---:|---:|---|
| `Data\wrds_v4\comp_company_topup_20260919T135055Z.csv` | 2 | 0.0 | `710ed40be03f751a6f42d842987051d2483fd7ffe0603952db48ed0fde78e966` |
| `Data\wrds_v4\comp_security_topup_20260919T135055Z.csv` | 7 | 0.0 | `28a8a7739a3b67593811d0e0a0faebb0e9a8284d27b32bd6ab3233dfe089104f` |
| `Data\wrds_v4\crsp_stocknames_topup_20260919T135055Z.csv` | 20 | 0.0 | `8d0b98991639d575b9cb73d45ded02e79f4b0e957e24b33a17ef88cbc79d623e` |
| `Data\wrds_v4\crsp_dsf_topup_20260919T135055Z.csv` | 10,066 | 0.6 | `326c79b93d597b8147d048797f437e936c398b4d927e080a7708274570393d77` |
| `Data\wrds_v4\crsp_dsi_topup_20260919T135055Z.csv` | 5,033 | 0.2 | `71555c4aee3db70cbfe5e38ae25ea726acffbfd904c9977677d5b4f0a3562e6e` |
| `Data\wrds_v4\crsp_stocknames_topup_20260919T135055Z_issuer.csv` | 673 | 0.1 | `6a56453c60941783b5563763ed422e6403dbf3392cb5eefe0563e233c1df5b77` |
| `Data\wrds_v4\crsp_dsf_topup_20260919T135055Z_issuer.csv` | 20,199 | 1.2 | `f359f5d0be70e4284f9044fe4e4b585e373bee86d19b3c5ace3fe82ac2a07351` |

- total written: 2.1 MB

## Hit rates (distinct keys reached, never row counts)

| step | reached | requested | rate |
|---|---:|---:|---:|
| CIK -> gvkey | 2 | 2 | 100.0% |
| gvkey -> CUSIP | 2 | 2 | 100.0% |
| CUSIP -> permno | 2 | 7 | 28.6% |
| permno -> daily returns | 2 | 2 | 100.0% |
| new permno -> daily returns | 5 | 25 | 20.0% |

- pull finished (UTC): 2026-09-19T13:51:12+00:00
