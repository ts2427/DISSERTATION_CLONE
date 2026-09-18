# REBUILD V4 — scripts/213 invalid runs

A record of Stage 3 verification runs whose output must not be used. The cache is kept in
every case: the fetched documents are evidence, and re-fetching them would cost SEC
requests for no gain. Only the verdicts are void.

---

## Run 1 — INVALID

- run: first execution of `scripts/213_stage3_verify.py` (committed at `9fa0d42`)
- output: `outputs/rebuild_v4/213_verification_log.csv` — **void, do not use**
- cache: `Data/edgar/ex21_cache_v4/` — **kept**, 64 documents, 8.8 MB
- verdicts produced: 10 VERIFIED, 21 UNVERIFIED

### How it was caught

Two canaries were named in advance as rows that *must* come back UNVERIFIED, on the
grounds that both are name collisions rather than real relationships. Both came back
VERIFIED:

| row | candidate | shared token | accession | line matched |
|---|---|---|---|---|
| Brown, Lisle/Cummings, Inc. (cik 14745) | BROWN FORMAN CORP | `BROWN` | 0000014693-26-000048 | `Brown-Forman Corporation` |
| Communications & Power Industries LLC (cik 1000564) | AMERICAN ELECTRIC POWER CO | `POWER` | 0000004904-26-000055 | `AMERICAN ELECTRIC POWER COMPANY, INC.` |

A verification standard that accepts a surname and an industry word as proof of corporate
succession is not a verification standard. The canaries did their job.

### Causes — four distinct defects, not one

**1. The match standard accepted a single shared token.**
`match_line` used Stage 2's `name_overlap`, which matches on ONE shared token of length
>= 4. That rule exists to decide whether a CRSP name and a PRC org string denote the same
firm, where one distinctive token is good evidence. It is the wrong rule for asking
whether a specific subsidiary appears in a list of hundreds of subsidiaries, where one
token is nearly guaranteed by chance. Cricket Wireless "verified" against
`New Cingular Wireless` on `WIRELESS` alone.

**2. `breach_date` was blank on 21 of 31 worklist rows.**
Stage 2 emitted `a_subsidiary` and `b_successor_cik` rows one per CIK with no date, so the
18-month 10-K window was evaluated against `NaT` and never selected a filing: all 13
`a_subsidiary` rows failed with *"no 10-K within 548 days of NaT"*. The Exhibit 21 route
was therefore never exercised at all for the largest category on the worklist.

**3. Exhibit selection matched the wrong exhibit.**
`EX21_RE = r"ex.?-?\s?21"` let the `.?` wildcard consume the "1" in "ex**1**21", so
`dex121.htm` (Exhibit 12.1, ratio of earnings to fixed charges) matched as an Exhibit 21.
News Corp's 2009 10-K (accession 0001193125-09-172310) contains `dex121.htm`, `dex21.htm`
and `dex321.htm`; all three matched and the first in directory order was taken. Fox
Entertainment Group was recorded UNVERIFIED — *"Exhibit 21 does not list 'Fox
Entertainment Group'"* — on the strength of a document that is not an Exhibit 21 and
contains no subsidiary list. That verdict was a false negative produced by reading the
wrong file.

**4. The successor search had no succession requirement and no date anchor.**
Any 8-K naming the other firm counted. Filings were scanned most-recent-first, so seven of
the eight `b_successor_cik` verifications rest on **2026** 8-Ks that have nothing to do
with a succession — one matched the string `Uber 8-K`, another matched
`len-20260916 LENNAR CORP /NEW/ ...` inside an XBRL header line. Only Aon
(8-K12B, 2020-04-01) is plausibly a genuine succession filing, and it was not verified on
that basis; it was verified because the token `AON` appeared.

### All 10 VERIFIED rows from run 1, with the evidence that produced them

| candidate_type | cik | org | candidate | form / filed | shared | matching line |
|---|---|---|---|---|---|---|
| b_successor_cik | 14745 | Brown, Lisle/Cummings, Inc. | BROWN FORMAN CORP | 8-K 2026-09-02 | BROWN | `Brown-Forman Corporation` |
| b_successor_cik | 58696 | Lennar Corporation | LENNAR CORP | 8-K 2026-09-16 | LENNAR | `len-20260916 LENNAR CORP /NEW/ 0000920760 false ...` |
| b_successor_cik | 826083 | Dell Inc. | DELL TECHNOLOGIES INC | 8-K 2026-09-15 | DELL | `Dell Technologies Inc.` |
| b_successor_cik | 912752 | Sinclair Broadcast Group, Inc. | SINCLAIR INC | 8-K 2026-08-28 | SINCLAIR | `Sinclair, Inc.` |
| b_successor_cik | 1000564 | Communications & Power Industries LLC | AMERICAN ELECTRIC POWER CO | 8-K 2026-07-30 | POWER | `AMERICAN ELECTRIC POWER COMPANY, INC.` |
| b_successor_cik | 1283246 | International Paper Company | INTL PAPER CO | 8-K 2026-07-30 | INTERNATIONAL\|PAPER | `International Paper Company` |
| b_successor_cik | 1431473 | Uber | UBER TECHNOLOGIES INC | 8-K 2026-09-15 | UBER | `Uber 8-K` |
| b_successor_cik | 1808065 | Aon Corporation PLC | AON PLC | 8-K12B 2020-04-01 | AON | `Aon plc` |
| ncusip_name_mismatch | 732717 | Cricket Wireless LLC | — | 10-K 2018-02-20 | WIRELESS | `New Cingular Wireless` |
| ncusip_name_mismatch | 732717 | Cricket Wireless LLC | — | 10-K 2018-02-20 | WIRELESS | `New Cingular Wireless` |

Note that `International Paper Company` -> `International Paper Company` is very likely a
correct identification. It is void anyway: it was produced by a rule that cannot
distinguish it from the Brown-Forman match, so it carries no more evidentiary weight than
the others and must be re-derived under the corrected rule.

### Fixes applied before any re-run

1. Stage 2 emits one worklist row per EVENT, with a `breach_date` on every row.
2. Exhibit 21 match: a line must contain EVERY significant token of the subsidiary name,
   or its space-stripped concatenation must equal the candidate's.
3. Successor match: a SINGLE passage must both name the other firm to the same standard
   AND carry succession language (successor, predecessor, holding company reorganization,
   Rule 12g-3, merger).
4. Parent nomination: name knowledge may NOMINATE a parent CIK, with the basis recorded;
   only the filing verifies.
5. `EX21_RE` tightened to `ex[-_ ]?21`, which matches `dex21.htm` and not `dex121.htm`.

Regression tests for every one of these are in `scripts/217_v4_offline_tests.py`,
including both canaries as explicit negative cases.

### Not re-run here

Run 2 requires SEC network access and therefore Tim's `SEC_EDGAR_USER_AGENT`. The Fox
Exhibit 21 (`dex21.htm`) was never fetched by run 1 and is not in the cache, so the
question *"does News Corp's 2009 Exhibit 21 list Fox Entertainment Group?"* remains
unanswered. It costs one request under the corrected exhibit selection.
