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
