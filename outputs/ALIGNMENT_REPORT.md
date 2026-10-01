# Alignment — make `run_all.py` match the essays, then prove it

No sample changed. `CANONICAL_V3` and `CANONICAL_V4` are byte-identical to their previous
commits; no DISH fold, no incident merge, no date re-anchoring, no linkage change, no WRDS
or CRSP pull. `essay3-v4-final` is unmoved at `8c0d09e`.

| Part | State |
|---|---|
| **A** rebaseline and re-freeze | **complete** — `0c9b378`, `7bddcd0`, `f0bdf72`, tag `v3-rebaseline-final` |
| **B** Essay 2 appendix and the WRDS exception | **complete** — `e16e702` |
| **C** clean-clone run | **complete** — 77 steps, 74 OK, 3 failed; Essay 1 and Essay 3 reproduce byte-identically, Essay 2 does not |
| **D** essay-to-output match | **cannot run — `docs/drafts/` does not exist; harness built and validated** |
| **E** known-limitations ledger | **complete** — `ff2b88f` |

---

# PART A — rebaseline, then re-freeze

## A1. G1 and G2 confirmed in place

**G1, `scripts/158:139-148`** — the Essay 3 block is gone and the removal is legible:

```
# ---------------- Essay 3: REMOVED 2026-09-29 ----------------
# The 13 H6 keys this block used to write into constants_v3.json are GONE:
#   N_essay3, H6_{30,90,180}d_{base_rate,ame_pp,p,mde80_pp}
...
# Essay 3 values live ONLY in outputs/essay3_v4/constants_essay3_v4.json, written by
# scripts/227. Nothing in this script may write an Essay 3 result again.
```

A grep for `N_essay3` or `H6_` in `scripts/158` returns **only line 141, inside that
comment**.

**G2, two sites.** `scripts/158:91-94` (the Essay 1 hypothesis loop) and `158:128-134`
(the H5 block), both ending:

```python
                           'HC3-ONLY, NOT A VERDICT (disqualified rung; see scripts/165)'))
```

## A2. `scripts/158` run alone — exit 0, 22.3 s

`run_all.py` was not run. All of 158's inputs are committed and local, so no network was
needed. There is no rebaseline flag: `158:565-574` asserts against `constants_v3.json` when
it exists and writes a fresh baseline when it does not, so the old file was moved aside
(copies kept; the committed version untouched in git).

**A side effect worth recording.** On the assert-and-merge path `158:571` writes
`{**old, **C}`, which *preserves* keys absent from `C`. The 13 Essay 3 H6 keys would have
survived a merge indefinitely. **G1 only takes effect through a fresh baseline** — which is
what this rebaseline did.

## A3. What changed

**121 keys → 108: 13 removed, 0 added, 81 changed, 27 unchanged.**

**Removed (G1):** `N_essay3` = 338, and the twelve `H6_{30,90,180}d_*` keys — including the
figures a reader would have taken as Essay 3's headline: `H6_30d_ame_pp` 7.37,
`H6_90d_ame_pp` 9.97, `H6_180d_ame_pp` 4.77.

**Sample keys**, every one moving by exactly the two DISH events already traced:

| key | before | after |
|---|---:|---:|
| `N_regression` | 338 | **340** |
| `treated_regression` (events) | 104 | **106** |
| `treated_orgs_regression` (parent entities) | 35 | **36** |
| `treated_parent_ciks_regression` | 11 | **12** |
| `treated_total` (events) | 116 | **118** |
| `events_crsp` | 354 | **356** |
| `treated_crsp` (events) | 109 | **111** |
| `N_essay2` | 337 | **339** |

**Verdict table:**

| hypothesis | vintage | coef (pp) | HC3 p | TOST p | MDE80 | status |
|---|---|---:|---:|---:|---:|---|
| H1_timing | before / after | 0.9641 / 1.4143 | 0.3298 / 0.1712 | 0.1259 / 0.2538 | 2.77 / 2.89 | NULL-INCONCLUSIVE both |
| H2_FCC | before / after | −0.2663 / −0.4994 | 0.8404 / 0.7326 | 0.0833 / 0.1371 | 3.70 / 4.09 | NULL-INCONCLUSIVE both |
| H3_prior | before / after | 0.0238 / 0.0258 | 0.7092 / 0.6916 | 0.0000 / 0.0000 | 0.18 / 0.18 | BOUNDED NULL both |
| H4_health | before / after | −1.0553 / −0.9405 | 0.6870 / 0.7176 | 0.3451 / 0.3280 | 7.33 / 7.28 | NULL-INCONCLUSIVE both |
| **H5** | **before** | **3.2897** | **0.0630** | **0.7491** | **4.95** | **NULL-INCONCLUSIVE** |
| **H5** | **after** | **3.9442** | **0.0292** | **0.8456** | **5.07** | **HC3-ONLY, NOT A VERDICT** |

**One status changed — H5.** Its HC3 p crossed .05 while its TOST p moved further from
rejection. Tim's ruling: proceed, because this is a status-label change on a disqualified
rung on the Essay 1 frame, not a change in Essay 2's verdict of record, which comes from
`scripts/165` and is unchanged. Essay 1's four verdicts are unchanged.

**The thing to keep in view.** The third branch used to read `'SIGNIFICANT'`. Before Stage
2's G2 this rebaseline **would have written `H5_status = "SIGNIFICANT"`** into the constants
file of record, from the disqualified rung. This is the first time that branch has been
reached. The constants file now shows HC3 p = .029 for a treated-group volatility effect
while the frame of record reports a null — two different estimands on two different samples
(158's H5 is HC3 on the Essay 1 frame, `N_essay2` 339; Essay 2's canonical is N = 333, 104
treated events, 82 clusters, 12 treated parent entities), but a reader taking `H5_p` from
the JSON gets .029.

Also moved: `car30d_regression_mean` −0.1581 → **−0.2052** (the DISH tail effect; the median
and 5% trimmed mean do not move), `first_stage_pp` 15.05 → 15.26, `T6_interaction_coef`
−3.0166 → −1.6411 (p .1516 → .4754), and `T6_treated_timing_coef` −0.7835 → **+0.5562**, a
**sign change**. All 16 `appendix_v3` tables regenerated (94 insertions, 94 deletions).

## A4. Committed, and the ledger check now passes

`0c9b378` carries the new `constants_v3.json`, `CONSTANTS_BLOCK_V3.md` and the 16 tables.

`scripts/247` previously exited 1 with *"PENDING REBASELINE: constants_v3.json is stale
against CANONICAL_V3"* (340 vs 338, 106 vs 104 treated events). It now reports:

```
| Regression sample N | 340 | 340 | yes |
| Treated events      | 106 | 106 | yes |
The ledger and the committed constants agree.
Assertions passed: 10.
```

**Exit 0.** Committed as `7bddcd0`.

## A5. Full re-freeze — and two defects in `scripts/210`

`210 --create` rewrote the manifest over the same scope (the `v3-frozen` tree, 2,648 files,
447.6 MB) with hashes refreshed to the rebaselined bytes. **32 recorded hashes moved**: the
16 appendix tables, `constants_v3.json`, the 13 Stage 2 files, and the two append-only
prefixes.

The 13 pinned exceptions in `docs/claude/V3_FREEZE_EXCEPTIONS.md` are **retired** with a
dated note. Their rows are preserved verbatim with a leading `RETIRED` cell so `210` no
longer parses them; `load_exceptions()` returns 0. The authorising commits stay recorded as
provenance. This does not weaken the gate — the new manifest pins the current bytes of all
2,648 files, so any later change fails as before; what is gone is the hash-pinned
permission for 13 specific files to differ from an older manifest.

**Two defects found by actually running the re-freeze, both fixed:**

1. **`create()` could never produce a passing manifest.** It refreshed `sha256` from disk
   but copied `blob_id` straight from the baseline tag's tree, while `verify()` compares
   `blob_id` against `git ls-files -s` today. After a `--create`, all 30 files whose git
   blob had moved since `v3-frozen` still failed the blob test, so the gate returned
   `BLOB ID CHANGED: 30` and `FAIL`. `--create` was effectively unusable. It now records the
   current blob from the same source `verify()` reads. The manifest's **scope** still comes
   from the baseline tree, deliberately: a re-freeze re-records the frozen set's bytes, it
   does not widen the set.
2. **`CONSTANTS_BLOCK_V3.md` tripped the gate.** Written by `158` beside
   `constants_v3.json`, it had never been committed (`outputs/*.md` is gitignored). Newly
   tracked at the rebaseline, it appeared as an unallowlisted addition. It and the two query
   reports are added to `V4_DOCS`.

**Verified after the fixes:**

```
AUTHORISED EXCEPTIONS (docs\claude\V3_FREEZE_EXCEPTIONS.md) : 0 of 0 declared
SHA256 CHANGED (real content)  : 0
BLOB ID CHANGED (git object)   : 0
DELETED / UNTRACKED            : 0
ADDED outside v4 allowlist     : 0
RESULT: PASS - v3 baseline intact          exit 0
```

**Negative-tested 3 of 3:** perturbing `scripts/156`, `constants_v3.json` or `scripts/152`
each returns `FAIL` rc=1, and `PASS` returns once restored. Each probe was restored in a
`finally` block.

Committed `f0bdf72` and tagged **`v3-rebaseline-final`**.

---

# PART B — Essay 2 appendix and the WRDS exception

**The draft path was not supplied and `docs/drafts/` does not exist**, so the citation
source used here is `outputs/ESSAY2_APPENDIX.md` — the committed Essay 2 appendix, whose own
header reads *"All tables from outputs/tables/essay2_appendix/*.csv via the committed Essay
2 chain."* That is the document that actually cites the tables. **28 `TABLE` headings.**

## B1. Live versus tombstoned

**Every table the appendix cites comes from the tombstoned set.** The appendix header names
`outputs/tables/essay2_appendix/` as its source, and that directory holds **41 CSVs with no
committed generator** (`TOMBSTONE.md`, 2026-09-29). The live chain writes **61 files** to
`outputs/tables/essay2_v2/` via `163`, `164`, `165`, `166`, `169`, `174`, `180`, `181`,
`182` — and **the two sets share zero filenames**.

So the answer to B1 is uniform and blunt: of the 28 cited tables, **28 are sourced from the
tombstoned set and 0 from a live step**. That is the gap Tim is repointing.

## B2. The live output carrying the same quantities

Matched on two signals — a distinctive filename token **and** column overlap — because
column overlap alone over-matches small tables (a 3-column file shares `group, n, mean`
with almost anything).

**CONFIRMED (11):** both signals agree.

| tombstoned | live counterpart | shared columns |
|---|---|---:|
| `channel_elevation_calibration.csv` | `t51_elevation_calibration.csv` (180) | 4 of 4 |
| `channel_microstructure.csv` | `t35_microstructure.csv` (**167**) | 11 of 12 |
| `delay_distribution_by_group.csv` | `t17_delay_distribution.csv` | 8 of 9 |
| `disclosure_delay.csv` | `t16_delay_on_treatment.csv` | 4 of 10 |
| `events_by_year.csv` | `t18_events_by_year.csv` | 3 of 4 |
| `fixed_effects.csv` | `t8_fixed_effects.csv` | 3 of 14 |
| `inference_ladder.csv` | `t26_inference_ladder.csv` (165) | 6 of 7 |
| `misclassified_group_comparisons.csv` | `t19b_misclassified_composition.csv` | 3 of 7 |
| `nested_models.csv` | `t3_nested_models.csv` | 3 of 13 |
| `program_test_enumeration.csv` | `t53_test_ledger.csv` (182) | 3 of 3 |
| `specification_curve_permutation.csv` | `t52_spec_curve_permutation.csv` (181) | 8 of 8 |

**PROBABLE (21):** the live chain writes a file with the obvious counterpart name but
reshaped columns — `design_resolution.csv` → `t28_design_resolution.csv`,
`dv_correlations.csv` → `t30_dv_correlations.csv`, `size_quartiles.csv` →
`t5_size_quartiles.csv`, `records_per_event.csv` → `t19_records_per_event.csv`,
`cluster_deletion_prerule.csv` → `t25_cluster_diagnostics.csv`,
`gradient_grid.csv` → `t31_gradient_grid.csv`, `four_panel_decomposition.csv` →
`t32_four_panel.csv`, `delay_quantiles.csv` → `t16b_delay_quantiles.csv`,
`descriptives_by_treatment.csv` → `t2_descriptives_by_treatment.csv`, and twelve more.
These need one look each to confirm the quantity survived the reshape.

**NO LIVE COUNTERPART (8).** Nothing in the live chain writes these, and they are all
identifier- and SIC-convention diagnostics — the provenance tables of the retired SIC-era
work:

`form499_registry_matches.csv`, `identifier_collisions.csv`,
`identifier_collisions_recycled_tickers.csv`, `missingness_precase.csv`,
`q1_transition_components.csv`, `sic_conventions_vs_form499.csv`,
`sich_unavailable_treated.csv`, `sich_vs_curated_sic.csv`.

**These eight are the tables Tim must drop rather than repoint** — there is no live output
carrying their quantities, and no committed code that could produce one.

## B3. Script 170 declared

`docs/claude/REPRODUCE_ESSAY2.md`, in the same form as the WRDS and SEC stages in
`REPRODUCE_ESSAY3_V4.md`. `scripts/170:79` reads `Data/wrds/crsp_quotes_topup.csv` with a
bare `read_csv`, so on a clean clone it **raises** rather than degrading — it does not
substitute a proxy or silently skip the microstructure channel. That file is a
CRSP-licensed quote extract pulled by `scripts/167`, gitignored and uncommittable, and
`167` is deliberately unstaged for the same reason.

**Recorded because I had it wrong first:** `t35_microstructure.csv` is written by **167, not
170**. `170` writes `t43_intent_scope.csv` (`170:198`) and `t44_equivalence_bounds.csv`
(`170:268`).

---

# PART C — clean-clone run

Three attempts. The first two are reported because what went wrong in them is part of the
answer.

| attempt | clone | outcome |
|---|---|---|
| 1 | deep path, no `core.longpaths` | checkout lost 13 literature PDFs; failed at `219` (staged without `--assemble-only`) |
| 2 | `core.longpaths=true` | 47 steps OK, `210` failed; **I killed it on the monitor's first `[ERROR]`**, which turned 1 genuine failure into 29 `STATUS_DLL_INIT_FAILED` artefacts and cost the Essay 2 chain |
| **3** | `core.longpaths=true`, manifest at HEAD, `170` skipped by renaming the script so `run_all.py` stays untouched | **ran to completion: 77 steps, 74 OK, 3 failed, 566.9 s** |

My stop in attempt 2 was too eager: `scripts/210` is a *gate*, not a stage, and its failure
decomposed into causes that were mostly mine. Attempt 3 was allowed to finish so the step
table is complete, with failures read from the log afterwards.

## C1. Setup

Cloned `rebuild-v4` into a temporary directory with `core.longpaths=true`; LFS pulled from
GitHub (113 objects, 1.87 GiB). **clone rc=0, 0 missing tracked files, `run_all.py`
byte-identical to the commit.** No file was copied in from the working copy. `scripts/170`
skipped as declared, by renaming it so `run_all` reports `[SKIP] Script not found`.

**The I1 guard passes in the clean clone with zero LFS placeholders anywhere**, where the
working repository still has 19 — direct evidence that I3 fixed the clean-clone
degradation.

## C2. The three failures

| step | rc | seconds | cause |
|---|---|---:|---|
| `121a_form499_entity_matching` | 1 | 1.0 | **`ERROR: Status 403` from the FCC Form 499 endpoint.** An undeclared network dependency — this is a real reproducibility gap, in the same class as 219 but not documented anywhere. |
| `182_essay2_test_ledger` | 1 | 22.0 | `runpy.run_path` on `scripts/170`, which is the declared WRDS exception. **Skipping 170 breaks 182**, so the exception is not self-contained. It fails either way on a clean clone: with 170 present it raises on the missing CRSP quote file instead. |
| `210_verify_v3_frozen` | 1 | 85.7 | the freeze gate — decomposed below |

74 steps returned 0, including **the entire Essay 3 v4 chain**: `219` with the new flag
(1.3 s), `220` (22.0 s), `224`, `227` (11.4 s, asserting against its own constants), `229`,
`232` (63.2 s), `239`, `242`–`246`, and `217`'s offline suite.

### Why 210 fails in a clone, and why none of it is the pipeline

| finding | count | cause |
|---|---:|---|
| `SHA256 CHANGED` | 8 | 3 legacy `FINAL_DISSERTATION_DATASET*` files, 2 `stage7_*` CSVs, 2 timestamped logs, 1 `.docx` |
| `BLOB ID CHANGED` | 0 | — |
| `DELETED / UNTRACKED` | 14 | 13 `Data/Articles/*.pdf` **present on disk** but unstattable, plus the 170 I renamed |
| `eol artifacts` | 1,354 | line endings; 210 itself labels these "PERMITTED OFF-PLATFORM ONLY" |
| `ADDED outside allowlist` | 0 | — |

**A portability defect in 210, reported not patched.** It tests presence with
`Path(p).exists()`, and **Python cannot stat paths over 260 characters on Windows even when
`core.longpaths` lets git create them**. Thirteen literature PDFs with long filenames are
therefore reported as deleted, and `verify()` treats deletions as fatal. **The gate cannot
pass in a clone at a deep path regardless of the pipeline.** On the authoring machine the
base path is short, which is why this has never surfaced. The fix is an extended-length
path prefix or `os.stat` on the `\\?\` form.

Two of the eight content differences were mine and are now fixed: the `stage7_*` CSVs were
**stale against the rebaseline** — committed at 335 rows, regenerated at 337 — because A2
ran `158` alone and `157` was never re-run. `scripts/157` has now been run and committed
(`ef551eb`), and the balance table reads Included (CRSP) N=356 treated share 0.3118 against
Excluded N=133 treated share 0.0526.

The three legacy `FINAL_DISSERTATION_DATASET*` differences are a **consequence of Part H**:
`99_add_cpni_hhi_variables` is retired, so `cpni_breach` (139 → 149),
`hhi_industry_year` and `has_high_complexity` (0 → 582) are now produced differently. Those
datasets feed nothing cited — zero of `constants_v3.json`'s keys come from them — so the
difference is real and inconsequential for all three essays.

## C3. Regenerated against committed, file by file

Tolerance for "numerically identical": **1e-9** on every numeric column, with text columns
compared as strings.

| target | verdict |
|---|---|
| **`constants_v3.json`** | **byte-identical** |
| **`constants_essay3_v4.json`** | **byte-identical** |
| `constants_essay3_q2.json` | byte-identical |
| **Essay 1 attrition ledger** | **byte-identical** |
| **`appendix_v3/` (16 tables)** | **16 of 16 byte-identical** |
| **Essay 3 table CSVs (`essay3_q4/`, 18 files)** | **18 of 18 byte-identical** |
| Essay 3 v4 outputs (50 files) | 47 byte-identical, 2 eol-only, 1 different (`227_estimation.log`, timestamped) |
| Essay 2 live tables (61 files) | 50 byte-identical, 10 numerically identical, 1 different (`t24_a4_deadline_scan.csv`) |
| Essay 3 appendix (5 files) | 4 byte-identical, 1 different (`.docx`, embeds a build timestamp) |
| Essay 2 attrition ledger | different — see below |

**Every differing value, accounted for:**

1. `t24_a4_deadline_scan.csv` — a repo-wide grep for deadline language. It now finds a hit
   in **`scripts/248_essay_to_output_match.py`**, the Part D harness I added this session,
   whose purge list contains the literal string "64.2011 as a customer/public disclosure
   deadline". **My own new script pollutes Essay 2's deadline scan.** The harness should be
   excluded from that scan, or its patterns built so they do not match literally.
2. Essay 2 attrition ledger — two differences, both expected consequences of committed
   changes: J2 rewrote `163`'s ledger header, so the regenerated text carries the new
   wording while the committed copy predates J2; and the committed copy still contains the
   `DUAL-PRINT (documented divergence, 9/4)` paragraph reporting 340/106 against 338/104,
   which **the rebaseline resolved**, so `163` no longer prints it. The committed ledger is
   stale, not wrong.
3. `227_estimation.log`, `187_fetch.log`, `b_fetch_log.csv`, `APPENDIX_V3_TABLES.docx`,
   `ESSAY3_APPENDIX_TABLES.docx` — timestamps.

## C4. One sentence per essay

- **Essay 1 — yes.** `150`–`158`, `160` and `247` all returned 0, and `constants_v3.json`,
  all 16 `appendix_v3` tables and the attrition ledger are **byte-identical** to the
  committed copies.
- **Essay 2 — no.** `121a` fails on an **undeclared** FCC endpoint dependency (HTTP 403),
  `182` fails because it `runpy`s the declared WRDS exception `170`, and `170` itself is
  skipped — though the cited core does regenerate: 60 of its 61 live tables are
  byte-identical or numerically identical within 1e-9.
- **Essay 3 — yes.** The whole v4 chain returned 0 including `220`, `224`, `227`, `229`,
  `245` and `217`, `constants_essay3_v4.json` is byte-identical, and all 18 table CSVs are
  byte-identical.

---

# PART D — still cannot run; the drafts are not on this machine

**`docs/drafts/` does not exist.** Searched again, inside and outside the repository:

- No directory named `drafts` anywhere except `./drafts/` at the repository root, which
  holds six **Essay 3 methods fragments** in Markdown dated 2026-09-19.
- The `.docx` files that match "draft" are at the **repository root** and are old:
  `Essay 1 DRAFT.docx` **2026-03-13**, `Draft Draft.docx` **2026-04-07**. The Essay 2
  results sections are 2026-05-31. The newest root `.docx` of any kind is **2026-07-14**.
- **The v3 rebuild closed 2026-08-30 and the rebaseline was 2026-10-01**, so every one of
  those documents predates the data they would be checked against. Running D on them would
  return a table of STALE classifications that establishes nothing.
- The only recent `.docx` anywhere under the user profile is
  `~/Downloads/Essay3_References.docx`, a references file.

**Nothing in Part D was attempted on those files.** No number was extracted, classified or
guessed.

## The harness is written, validated and committed

`scripts/248_essay_to_output_match.py` implements D1–D5 and both added D4 checks. It builds
a provenance index of **40,351 live value forms** — from `constants_v3.json`,
`constants_essay3_v4.json`, the live Essay 2 tables, `appendix_v3/`, the Essay 3 table CSVs
and both attrition ledgers — and **6,935 retired forms** from the Query 2 constants and the
tombstoned Essay 2 appendix. Validated against the pipeline-generated
`ESSAY3_APPENDIX_TABLES.docx`: 2,115 MATCH, 246 NO PROVENANCE, 4 STALE, 0 purge hits, 0
contradicted claims. With no drafts present it aborts rc=2 rather than inventing anything.

Run it with `--drafts <dir>` once the files are placed.

**Two limitations documented in the script**, because they bound what its output can be
trusted for: matching is on numeric value alone, so MATCH means the value exists in the
pipeline rather than that it is right for that sentence (the 4 STALE above are pure value
collisions); and **it cannot emit MISMATCH**, since separating "says 338 where the output
says 340" from "says 338 about something else" requires knowing which quantity a sentence
is about. The rebaseline's known mismatches are listed in the docstring so they can be
found among the NO PROVENANCE rows: 338 → 340, 104 → 106 treated events, 35 → 36 parent
entities, 11 → 12 parent CIKs, 354 → 356, 109 → 111, 116 → 118, and
`car30d_regression_mean` −0.1581 → −0.2052.

**Both added D4 checks are implemented and unrun**, and Part A makes both pointed:
`H5_p` is now **.0292** in `constants_v3.json` against a null in the frame of record, and
**`T6_treated_timing_coef` changed sign** (−0.7835 → +0.5562), so any sentence asserting its
direction is suspect whichever way it points.

---

# PART E — known-limitations ledger

`docs/claude/KNOWN_LIMITATIONS.md`, documentation only, committed `ff2b88f`. It states at
the top that the samples are frozen by decision and that each entry is disclosed rather than
corrected. Six entries, each with counts at every sample level and its source report and
line:

1. **Split incidents** — 79 of 489 events are one incident across separate state filings
   (19 treated, 60 control, 26 parent CIKs), with the DISH 2023 pair worked through and the
   fold explicitly not made.
2. **Same-date records** — counts by sample; the Massachusetts pattern (143 of 150 records,
   95%, against 4% elsewhere); 8 of Essay 1's 124 immediate-disclosure events reflect a
   documented gap; EDGAR recovered 0 of 29.
3. **Anchors** — Essay 1 on `breach_date`, Essay 2 on `reported_date`, undocumented; 128 of
   340 Essay 1 windows (42 of 106 treated events) close before notification; and the mixed
   anchor inside Essay 1, where 116 of 340 events are reporting-date-anchored by accident.
4. **No single notification-date rule** — 31 Gate-2 departures, v4 repairing 14 and v3 none,
   gaps up to 1,109 days, and the v3/v4 DISH disagreement.
5. **CRSP linkage attrition** — 111 of 118 treated events against 245 of 371 control,
   making the control group a survivor sample of the larger listed controls.
6. **The two corrupted notification dates** — Sprint 2019 and Roku 2023, which break Essay 2
   rather than Essay 1.

It closes by naming what *was* fixed — the LFS attributes and guard, the retired H6 keys,
the disqualified HC3 label — so the ledger is not misread as a list of open defects.

---

# Close

**1. Did the rebaseline change any verdict, and does 210 pass against the new manifest?**
One status changed — `H5_status`, from `NULL-INCONCLUSIVE` to `HC3-ONLY, NOT A VERDICT`,
because its HC3 p crossed .05 (.0630 → .0292) while its TOST p moved further from rejection
(.7491 → .8456), with Essay 1's four verdicts unchanged; and **yes, 210 passes** in this
repository — 0 exceptions declared, 0 sha changes, 0 blob changes, 0 deletions, 0
unallowlisted additions — after two defects in `210` had to be fixed to make `--create`
usable at all, though it **cannot** pass in a clone at a deep path because
`Path.exists()` cannot stat 13 long filenames that are present on disk.

**2. Does each essay regenerate from a clean clone?** **Essay 1 yes** (`constants_v3.json`,
all 16 appendix tables and the ledger byte-identical); **Essay 2 no** (`121a` fails on an
undeclared FCC endpoint returning 403, and `182` fails because it executes the declared
WRDS exception `170`, although 60 of its 61 live tables reproduce); **Essay 3 yes** (the
whole v4 chain returns 0 and `constants_essay3_v4.json` plus all 18 table CSVs are
byte-identical).

**3. Per essay, how many numbers are MATCH, MISMATCH, NO PROVENANCE, and STALE?** Not
answerable — `docs/drafts/` does not exist and every `.docx` on this machine predates the
rebuild, so there is no current essay text to trace; the harness is built, validated and
waiting on the files.

**4. How many purge-list hits and how many contradicted claims does each essay contain?**
Not answerable, for the same reason, with both added D4 checks implemented and unrun.
