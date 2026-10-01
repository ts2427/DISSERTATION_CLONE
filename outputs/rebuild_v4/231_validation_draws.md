# REBUILD V4 — validation draws on the new Item 5.02 documents

One draw governs. This file records every draw made, so a superseded one cannot
be mistaken later for the operative sample.

## SUPERSEDED — `231_validation_new_ids_SUPERSEDED_incomplete_pool.csv`

- drawn from a pool of **445** new documents, seed **20260919**, size 30
- superseded because `scripts/235` then found the pool **incomplete**: Seagate
  (CIK 1137789) was short 5 of 21 expected Item 5.02 filings. The cause was in
  `scripts/230`/`231`, not the fetch — `needs_fetch` was CIK-level ("holds no
  documents at all"), and Seagate already held 16 documents from v3, so 231
  never requested it and the 5 filings inside v4's wider windows were never
  asked for.
- **No coding and no classification had occurred against this draw.** Nothing
  was seen, so redrawing on the completed pool is blind and the firewall the v3
  rounds established is intact.
- retained only as a record. It must not be used for scoring.

## SUPERSEDED — `231_validation_new_ids_SUPERSEDED_fetch_run_pool.csv`

- drawn after the corrected re-run, from a pool of **5** documents, seed 20260919
- superseded because `scripts/231` defined the pool as "the documents THIS run
  fetched" rather than "the documents v4 added". The re-run had only 5 filings
  outstanding (Seagate), so the pool was 5 though v4 had added 450. A pool that
  moves with fetch history is not a sampling frame: the same end state reached by
  one fetch or by three would give different draws.
- **No coding and no classification had occurred against this draw.**
- retained only as a record. It must not be used for scoring.

## OPERATIVE — `237_validation_new_ids.csv`

- drawn by `scripts/237_validation_draw_v4.py`, offline, after `scripts/235`
  reported a zero shortfall (1517/1517)
- pool = files under `Data/edgar/item5_02_text/` that are NOT in
  `git ls-tree -r v3-frozen`, intersected with the documents named in
  `b_scope_filings.csv`. Nothing in that definition depends on when, or in how
  many batches, the documents arrived.
- measured pool: 1576 on disk - 1126 frozen in v3 = **450** added by v4, all 450
  of them in scope
- same fixed seed (20260919), size min(30, pool) = 30
- this is the only draw used for new-document accuracy

## Reference codes for the operative draw

- `outputs/essay3_v4/VALIDATION_REFERENCE_CODES_V4.psv`
- sha256 `1b6dda546c4f37f0c52a9492a91ba2a78a00d7bd95c5843109e464c11892804b`
- coded BLIND by Claude (Claude Opus 5, this session), disclosed as the v3 rounds
  disclosed their LLM coder; provenance and the rules applied are in
  `VALIDATION_REFERENCE_CODES_V4_README.txt`
- committed BEFORE the first run of the frozen classifier (scripts/220) on these
  documents, so git history fixes the order rather than an assertion about it.
  No 220 output existed on disk for any of these documents when the codes were written.
- sheet_id to cik/accession mapping: `outputs/essay3_v4/validation_ids_v4.csv`

## Verification pass (still blind to scripts/220)

- `outputs/essay3_v4/VALIDATION_REFERENCE_CODES_V4_VERIFIED.psv` — sha256 `c269548f8d78b6ca3870f374ec5ece40bc53ff47cb9030b6e859ec5a2fb35263`
- change log: `outputs/essay3_v4/VALIDATION_VERIFICATION_LOG_V4.csv`
- the blind file `VALIDATION_REFERENCE_CODES_V4.psv` is UNCHANGED and keeps its own
  sha256 above; the verified file is a separate artefact
- run before any execution of scripts/220 on these documents
- six rows checked (5, 8, 12, 13, 21, 28) against reachable non-SEC sources; SEC is
  blocked from this environment
- **no code changed.** The flag set moved: 12 and 13 resolved, 5 and 8 newly flagged
  because executive-officer status of the registrant could not be confirmed, following
  the round-1 sheet 57 precedent
- flagged before: 12, 13, 21, 28 -> flagged after: 5, 8, 21, 28

PRIMARY for scoring = the verified codes. SECONDARY = the raw blind codes. For each
still-flagged row, accuracy is reported twice, with the row coded Y and coded N, as
bounds.

## Pre-specified analysis plan

- `outputs/essay3_v4/ANALYSIS_PLAN_V4.md` — sha256 `c9dbe88910669c7720a937b0119d906a312f08bd26349bc174ccf04e16f8afe0`
- committed BEFORE scripts/227 was run on the v4 sample. No specification change is
  permitted after that commit.
