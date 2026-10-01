# Alignment — make `run_all.py` match the essays, then prove it

No sample changed. `CANONICAL_V3` and `CANONICAL_V4` are byte-identical to their previous
commits; no DISH fold, no incident merge, no date re-anchoring, no linkage change, no WRDS
or CRSP pull. `essay3-v4-final` is unmoved at `8c0d09e`.

| Part | State |
|---|---|
| **A** rebaseline and re-freeze | **complete** — `0c9b378`, `7bddcd0`, `f0bdf72`, tag `v3-rebaseline-final` |
| **B** Essay 2 appendix and the WRDS exception | **complete** — `e16e702` |
| **C** clean-clone run | **running** — launched, 0 errors through the Essay 1 and Query 2 chains; see C below |
| **D** essay-to-output match | **cannot start — `docs/drafts/` does not exist** |
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

# PART C — clean-clone run (in progress)

## C1. Setup, and what it already proved

Cloned `rebuild-v4` at **`e16e702`** into a temporary directory. The clone was taken from
the local repository rather than GitHub, because the rebaseline commits are not pushed yet;
LFS objects were pulled from GitHub (**113 objects, 1.87 GiB**). **No file was copied in
from the working copy.**

Two findings from the setup alone:

- **The checkout initially failed on 13 files** — all literature PDFs under `Data/Articles/`
  — with `Filename too long`. This is Windows `MAX_PATH` against a deep temporary directory,
  not a repository defect; `git config core.longpaths true` then completed the checkout with
  **0 missing tracked files**. Worth knowing that a clone into a deep path needs that flag.
- **The I1 guard passes in the clean clone, with zero placeholders anywhere.** All 7
  required inputs present and real; the "Git LFS placeholders elsewhere" section printed
  nothing, where the working repo still has 19. That is direct evidence that **I3 fixed the
  clean-clone LFS problem** — `git lfs pull` now materialises every tracked object because
  the filter attribute exists for all of them.

`scripts/170` was commented out **in the clone only**, as declared in B3. Nothing else was
skipped. Live steps in the clone: 77.

## C2. Step results so far

**0 errors.** The run has passed the v3 chain (150–158), `160`, and `247` — the Essay 1
ledger, which exits 0 against the rebaselined constants — and is now inside the Essay 3
Query 2 chain at `202`, the wild cluster bootstrap with B = 99,999.

The remaining steps include several declared hour-scale ones: `163` (full DV rebuild),
`166` (193-specification grid), `181` (permutation null across that grid), `182`
(re-executes six Essay 2 scripts via `runpy`), then the v4 chain's `220` (~1,500 filings)
and `227` (B = 99,999). **The declared timeouts alone sum to over seven hours**, so the run
is still going as this report is written.

**C2's stop condition has not triggered: no step has returned nonzero, and nothing has been
patched.** The full step-by-step return codes and runtimes, C3's file-by-file comparison and
C4's per-essay verdict will be appended when the run finishes.

---

# PART D — cannot start

**`docs/drafts/` does not exist.** Checked again at the time of writing: the directory is
absent, and **no `.docx` anywhere in the repository has been created or modified in the last
24 hours**. The newest three are `outputs/essay3_appendix/ESSAY3_APPENDIX_TABLES.docx`
(2026-09-29, generated by `scripts/245`), `outputs/ESSAY2_APPENDIX.docx` (2026-09-07) and
`outputs/rebuild/INTEXT_TABLES_3_14.docx` (2026-08-30).

The only directory named `drafts` is `./drafts/` at the repository root, holding six **Essay
3 methods fragments** in Markdown dated 2026-09-19 — `e3_sample.md`, `e3_treatment.md`,
`e3_outcome.md`, `e3_controls.md`, `e3_design.md`, `e3_estimation.md`. Those are not the
three essay drafts D1 asks for, and they are not new.

**Nothing in Part D has been attempted.** No number has been extracted, classified,
estimated or guessed, and the added D4 checks — Essay 2 sentences citing an `H5_*` value
from `constants_v3.json` instead of `scripts/165`, and any sentence stating the direction of
`T6_treated_timing_coef` — are both unrun. Both are pointed checks given Part A: `H5_p` is
now .0292 in the JSON against a null in the frame of record, and
`T6_treated_timing_coef` **changed sign** at the rebaseline, from −0.7835 to +0.5562, so any
sentence asserting its direction is now suspect whichever direction it asserts.

Place the three `.docx` files at `docs/drafts/` and Part D runs as specified.

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
(.7491 → .8456); Essay 1's four verdicts are unchanged, and **210 now reports PASS** against
the new manifest with 0 exceptions declared, 0 sha changes, 0 blob changes and 0
unallowlisted additions, after two defects in `210` itself had to be fixed to make
`--create` usable at all.

**2. Does each essay regenerate from a clean clone?** Not yet answerable — the run is still
going, with **0 errors** through the v3 chain, `160`, `247` and into the Query 2 chain, and
several hour-scale steps still ahead.

**3. Per essay, how many numbers are MATCH, MISMATCH, NO PROVENANCE, STALE?** Not
answerable — `docs/drafts/` does not exist and no `.docx` has appeared, so there is no essay
text to trace.

**4. How many purge-list hits and contradicted claims per essay?** Not answerable, for the
same reason.
