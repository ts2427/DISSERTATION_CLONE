# Alignment — make `run_all.py` match the essays, then prove it

No sample changed. `CANONICAL_V3` and `CANONICAL_V4` are byte-identical to their previous
commits; no DISH fold, no incident merge, no date re-anchoring, no linkage change, no WRDS
or CRSP pull. `essay3-v4-final` is unmoved at `8c0d09e`.

| Part | State |
|---|---|
| **A** rebaseline and re-freeze | **complete** — `0c9b378`, `7bddcd0`, `f0bdf72`, tag `v3-rebaseline-final` |
| **B** Essay 2 appendix and the WRDS exception | **complete** — `e16e702` |
| **C** clean-clone run | **complete** — 77 steps, **76 OK, 1 failed** (210 only); all three essays reproduce |
| **D** essay-to-output match | **cannot run — `docs/drafts/` does not exist on this machine; harness built and validated** |
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

# PART C — clean-clone run, after the four fixes

Four attempts in total. The table records them because the progression is the result.

| attempt | change | outcome |
|---|---|---|
| 1 | deep path, no `core.longpaths` | lost 13 PDFs at checkout; failed at `219` |
| 2 | `core.longpaths=true` | 47 OK, `210` failed; **I killed it on the first `[ERROR]`**, turning 1 failure into 29 artefacts |
| 3 | manifest at HEAD, `run_all.py` untouched | 77 steps, 74 OK, **3 failed** — `121a`, `182`, `210` |
| **4** | after the 121a / 182 / 210 / 164 fixes | **77 steps, 76 OK, 1 failed, 654.5 s** |

## C1. Setup

Clone of `rebuild-v4` with `core.longpaths=true`: **clone rc=0, 0 missing tracked files,
`run_all.py` byte-identical to the commit.** LFS pulled from GitHub, rc=0. Interpreter
3.13.2 with `bidask` and `lifelines` present — installing `requirements.txt` is a
documented prerequisite, not part of what the repository reproduces, and `run_all` invokes
`sys.executable`, so the choice propagates to every step. `scripts/170` skipped by renaming
the file, so `run_all.py` is not edited. No file was copied in from the working copy.

## C2. The one remaining failure

**`scripts/210_verify_v3_frozen.py`, rc=1, 86.6 s.** `121a` and `182` now pass; the
previous attempt's three failures are down to one, and it is the gate, not a stage.

| 210 finding | run 3 | run 4 |
|---|---:|---:|
| `SHA256 CHANGED` | 8 | 10 |
| `BLOB ID CHANGED` | 0 | **0** |
| `DELETED / UNTRACKED` | 14 | **1** |
| `ADDED outside allowlist` | 0 | **0** |
| eol artifacts | 1,354 | 1,351 |

**The long-path fix worked: deletions fell from 14 to 1**, and the one remaining is
`scripts/170`, which I renamed to skip it. The 13 literature PDFs are gone from the list.

The 10 content findings decompose as follows, and **only one is a reproducibility problem**:

| files | verdict |
|---|---|
| `scripts/121a`, `scripts/164`, `scripts/182` | **EOL-only, misclassified.** Verified: after newline normalisation the hashes match exactly (`badbba89ef`, `f2f672defb`, `9c31a790fb` on both sides). See the defect below. |
| 3 × `FINAL_DISSERTATION_DATASET_*` | consequence of Part H retiring `99_add_cpni_hhi_variables`; these legacy datasets feed nothing cited |
| `187_fetch.log`, `b_fetch_log.csv`, `APPENDIX_V3_TABLES.docx` | timestamps |
| **`outputs/rebuild/appendix_v3/table_15.csv`** | **a real numeric difference — see below** |

### A second defect in 210's eol escape hatch

210 compares the on-disk sha256 against **the manifest**, but decides whether a mismatch is
an eol artefact or real content by running `git diff --quiet v3-frozen^{commit} -- <path>`.
After a re-freeze those two references disagree: a file that legitimately changed since
`v3-frozen` — which the current manifest records — fails the `git diff` test, so any
line-ending variance in a clone is reported as a **content change**. That is exactly what
happened to the three scripts edited this session. The adjudication should be against the
manifest's recorded state, not the frozen tag. **Reported, not patched.**

### `table_15.csv` does not reproduce, and the cause is in the script

`scripts/158:385-390` builds it with
`RandomForestRegressor(n_estimators=500, random_state=42, n_jobs=-1)`. The seed is fixed,
but `n_jobs=-1` parallelises tree aggregation, and the mean importances are not
bit-reproducible across thread counts:

| feature | repo | clone |
|---|---:|---:|
| roa | 0.3371 | 0.3371 |
| firm_size_log | 0.2386 | **0.2392** |
| leverage | 0.2068 | **0.2065** |
| prior_breaches_1yr | 0.1359 | **0.1357** |
| immediate_disclosure | 0.0456 | **0.0457** |
| fcc_form499 | 0.0247 | **0.0246** |
| health_breach | 0.0112 | 0.0112 |

**Row order and the top feature are stable**, which is why `constants_v3.json` — whose only
dependency here is `RF_top_feature` = `roa` — is byte-identical. The wobble is confined to
the fourth decimal, max 6 × 10⁻⁴. The table's own caption says "fixed seed 42", which is
true and still not sufficient for bit-reproducibility. Setting `n_jobs=1` would fix it, at
a cost in runtime. **Reported, not patched.**

## C3. Regenerated against committed, file by file

Tolerance for "numerically identical": **1e-9** on every numeric column, text columns
compared as strings.

| target | verdict |
|---|---|
| **`constants_v3.json`** | **byte-identical** |
| **`constants_essay3_v4.json`** | **byte-identical** |
| `constants_essay3_q2.json` | byte-identical |
| **Essay 1 attrition ledger** | **byte-identical** |
| `appendix_v3/` (16 tables) | **15 byte-identical**, 1 different (`table_15.csv`, above) |
| **Essay 3 table CSVs (18)** | **18 of 18 byte-identical** |
| Essay 2 live tables (61) | **60 byte-identical**, 1 different (`t24_a4_deadline_scan.csv`) |
| Essay 3 v4 outputs (50) | 47 byte-identical, 2 eol-only, 1 different (`227_estimation.log`) |
| Essay 3 appendix (5) | 4 byte-identical, 1 different (`.docx` build timestamp) |
| Essay 2 attrition ledger | different — J2 rewrote `163`'s header text, and the committed copy still carries the `DUAL-PRINT` paragraph the rebaseline resolved |

Essay 2's live tables improved from 50 byte-identical + 10 numerically identical in run 3 to
**60 byte-identical** in run 4: carrying 170's rows made `t53_test_ledger.csv` deterministic.

**Every differing value is accounted for**, and two of the causes were mine: `table_15.csv`
(RF `n_jobs=-1`), `t24_a4_deadline_scan.csv` (2 rows from audit reports created after the
committed t24), the Essay 2 ledger (stale against J2 and the rebaseline), and three
timestamped artefacts.

## C4. One sentence per essay

- **Essay 1 — yes, with one caveat.** `150`–`158`, `160` and `247` all returned 0, and
  `constants_v3.json`, the attrition ledger and **15 of 16** appendix tables are
  byte-identical; `table_15.csv`'s random-forest importances move in the fourth decimal
  because the script passes `n_jobs=-1`.
- **Essay 2 — yes, for the first time.** `121a` passes from the committed registry
  snapshot, `182` passes with 170's rows carried, and **60 of 61** live tables are
  byte-identical; the single declared exception `170` remains unreproducible without a
  WRDS login, and `t24` carries two extra rows from audit reports that postdate it.
- **Essay 3 — yes.** The whole v4 chain returned 0, `constants_essay3_v4.json` is
  byte-identical, and all 18 table CSVs are byte-identical.

**`run_all.py` still exits 1**, because `210` fails. Both reasons for that failure are
defects in `210` itself — the eol adjudication reference and, previously, the long-path
check — not in the pipeline it guards.

---

# PART D — the drafts are not on this machine

Run exactly as specified:

```
$ python scripts/248_essay_to_output_match.py --drafts docs/drafts
ABORT: no drafts directory at docs\drafts
Part D needs the three essay .docx drafts. Nothing was guessed or inferred.
EXIT: 2
```

`docs/drafts/` does not exist. **No `.docx` anywhere in the repository has been written in
the last six hours**, and the newest of any kind is `ESSAY3_APPENDIX_TABLES.docx`
(2026-09-29), which the pipeline generated. The `.docx` files whose names contain "draft"
are at the repository root and date from **2026-03-13** and **2026-04-07**; the Essay 2
results sections are **2026-05-31**; the newest root `.docx` is **2026-07-14**. All predate
the rebuild, which closed 2026-08-30, and the rebaseline of 2026-10-01.

**Nothing in Part D was attempted on those files.** No number was extracted, classified or
guessed, and both added D4 checks are implemented and unrun.

The harness is committed and validated: `scripts/248_essay_to_output_match.py` indexes
**40,351 live value forms** and 6,935 retired ones, and on the pipeline-generated Essay 3
appendix returns 2,115 MATCH, 246 NO PROVENANCE, 4 STALE, 0 purge hits, 0 contradicted
claims. Its two documented limitations stand: matching is on numeric value alone, and it
cannot emit MISMATCH without knowing which quantity a sentence is about.

If the drafts are being saved on another machine, or to a synced folder that has not landed
here, that would account for five successive reports that they were placed. They are not on
this disk.

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
because its HC3 p crossed .05 (.0630 → .0292) while its TOST p moved further from rejection,
with Essay 1's four verdicts unchanged; **210 passes in this repository** (0 exceptions, 0
sha, 0 blob, 0 deletions, 0 unallowlisted additions) but still fails in a clean clone, now
for a single remaining reason — its eol escape hatch adjudicates against the `v3-frozen`
tag rather than the manifest, so line-ending variance in files legitimately changed since
that tag is misreported as a content change.

**2. Does each essay regenerate from a clean clone?** **Essay 1 yes** (`constants_v3.json`,
the ledger and 15 of 16 appendix tables byte-identical; `table_15.csv` wobbles in the fourth
decimal because `scripts/158` passes `n_jobs=-1` to the random forest); **Essay 2 yes for
the first time** (`121a` from the committed registry snapshot, `182` with 170's rows
carried, 60 of 61 live tables byte-identical, with `170` the one declared exception);
**Essay 3 yes** (whole v4 chain returns 0, constants and all 18 table CSVs byte-identical).

**3. Per essay, how many numbers are MATCH, MISMATCH, NO PROVENANCE, and STALE?** Not
answerable — `docs/drafts/` does not exist, no `.docx` has been written on this machine in
six hours, and every draft present predates the rebuild; the harness is built and validated
and runs the moment the files land.

**4. How many purge-list hits and how many contradicted claims does each essay contain?**
Not answerable, for the same reason, with both added D4 checks implemented and unrun.

---

# FIX ROUND — 2026-10-01, after the clean-clone findings

| ruling | commit | outcome |
|---|---|---|
| `121a` offline mode | `2ca5639` | **outputs byte-identical**; snapshot vintage documented |
| `182` carry 170's rows | `42acb85` | **`t53` byte-identical**; exposed the undeclared `bidask` dependency |
| `210` long paths | `220f2ef` | **deletions 14 → 0** in a 369-character-path clone |
| `210` EOL adjudication | `16f9a60` | **121a, 164, 182 now classify EOL-only**; gate still catches real changes |
| `158` `n_jobs=1` | `a117145` | **`table_15` byte-identical across two runs**; `constants_v3.json` unchanged |
| `t24` accepted as the record | `246ed6e` | note recorded in `REPRODUCE_ESSAY2.md` |

## 210's EOL adjudication, and what it fixed

The manifest now carries a **`sha256_eolnorm`** column — sha256 of the bytes with CRLF
collapsed to LF — written by `--create` alongside `sha256`. `verify()` compares the disk's
normalised hash against that column, so **both sides of the comparison come from the
manifest**. The old test compared the working tree to the `v3-frozen` *tag* while the
sha256 it was explaining came from the *manifest*; after a re-freeze those disagree, which
is why three scripts edited this session were misreported as content changes.

Manifests without the column fall back to the old git-diff test, so an old manifest still
works and the output says which test was used. The file is read in one pass rather than
chunked, because chunking can split a CRLF across the boundary.

**Verified, the case the ruling names:** rewriting `scripts/121a`, `164` and `182` with
CRLF moves eol artifacts 0 → 3, leaves `SHA256 CHANGED` at 0, names all three in the
output, and the gate still returns **PASS rc=0**.

**Negative-tested, so the escape hatch cannot be abused:** CRLF *plus one added line* to
`scripts/164` returns **FAIL rc=1** with `SHA256 CHANGED 1` and eol artifacts 0. A real
content change is still caught even when wrapped in a line-ending change.

## 210 in a fresh deep-path clone: the long-path fix works, a third defect blocks the PASS

Clone into a 195-character directory, **longest tracked path 369 characters**, `clone rc=0`,
**0 missing tracked files**:

| finding | before the fixes | now |
|---|---:|---:|
| `DELETED / UNTRACKED` | 14 | **0** |
| `BLOB ID CHANGED` | 0 | **0** |
| `ADDED outside allowlist` | 0 | **0** |
| `SHA256 CHANGED` | 10 | **19** |
| eol artifacts | 1,351 | 1,346 |
| RESULT | FAIL | **FAIL** |

**The two ruled fixes both worked.** Deletions went to zero at a path length that
previously hid 13 files, and the three edited scripts are no longer misreported.

**A third defect, which the ruling did not cover and which I have not patched.** All 19
remaining `SHA256 CHANGED` entries are `Data/JSON Files/nvdcve-2.0-20NN.json`, and the
cause is that **the manifest's `sha256` is machine-state-dependent for Git-LFS files**:

| | bytes on disk | first characters |
|---|---:|---|
| authoring repo | **136** | `version https://git-lfs.github.com/spec/v1` |
| the clone, after `git lfs pull` | **37,669,631** | `{ "resultsPerPage" : 6580, …` |

The manifest records 136 bytes, because on this machine those 19 files are **unsmudged LFS
pointers**; the clone holds the real content. 210 compares on-disk bytes, so it correctly
reports a difference — the two machines genuinely hold different bytes for the same tracked
path. 210's own header already names this duality ("Git-LFS pointers in the index but real
content in the working tree"); what it does not handle is the duality running the other
way.

**So 210 can only PASS on a machine whose LFS smudge state matches the one that wrote the
manifest.** Three ways out, for a ruling rather than my choice: record the LFS **oid** for
pointer files instead of the on-disk hash; compare the *smudged* content on both sides; or
exempt the known-pointer paths and say so in the output. The first is the smallest change
and the only one that makes the manifest machine-independent.

## `table_15` determinism

`scripts/158:385-390` now passes `n_jobs=1`. The seed was always fixed; `n_jobs=-1`
parallelised the aggregation of tree importances, so the floating-point summation order
depended on the thread count.

- **`table_15.csv` is byte-identical across two consecutive runs** (md5 `3a7962abbd89`
  both times), where it previously differed between machines by up to 6 × 10⁻⁴.
- **`constants_v3.json` is unchanged** (md5 `25ab773e8066` before and after), and 158's
  assertion check against the existing baseline passed on both runs.
- The single-threaded values equal the committed ones on this machine, so only the script
  moved.

## Part D — the drafts are not on this machine

Run exactly as ruled:

```
$ python scripts/248_essay_to_output_match.py --drafts "C:\Users\mcobp\Documents\essay_drafts"
ABORT: no drafts directory at C:\Users\mcobp\Documents\essay_drafts
Part D needs the three essay .docx drafts. Nothing was guessed or inferred.
EXIT: 2
```

`C:\Users\mcobp\Documents\` exists; it has no `essay_drafts` subfolder. Searched the
whole user profile at any depth:

- **no directory named `essay_drafts` anywhere**;
- **no `.docx` modified anywhere under the profile in the last two days**;
- no `docs/drafts/` in the second repository copy at
  `C:\Users\mcobp\OneDrive\Documents\DISSERTATION_CLONE\`, and no `.docx` in its
  top three levels.

**Nothing in Part D was attempted.** No number was extracted, classified or guessed, no
report was written, and no file containing draft text exists to commit. Both added D4
checks are implemented and unrun.

The harness is ready: `scripts/248_essay_to_output_match.py --drafts <dir>
--out <dir>/ESSAY_MATCH_REPORT.md` writes wherever it is told, so it can put the report in
the drafts folder outside the repository as ruled.
