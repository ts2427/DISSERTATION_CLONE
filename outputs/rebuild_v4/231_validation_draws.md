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

## OPERATIVE — `231_validation_new_ids.csv`

- drawn after `scripts/231 --documents` was re-run on the corrected scope and
  `scripts/235` reported a zero shortfall
- same fixed seed (20260919) and the same size rule, min(30, new documents),
  over the completed pool
- this is the only draw used for new-document accuracy
