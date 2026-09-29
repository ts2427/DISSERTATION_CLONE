# Retirement Ledger — Essay 3 (Query 2, Part H; 2026-09-11)

The scripts below are removed from `run_all.py`, and the hardcoded values are marked retired. Nothing is deleted: every script and output stays on disk and in git history.

- **Retiring commit:** the Essay 3 Query 2 Stage 2 commit, which follows `8e18c4e`. Record its hash here once it exists: `git log --oneline -- outputs/RETIREMENT_LEDGER.md`.
- **Replacement:** the Query 2 chain, scripts 187 → 195 (frozen v2 classifier, `6f7be7a`) → 199 → 202 → 190/191 → 203. Results are in `outputs/ESSAY3_QUERY2_REPORT.md` and the assertion baseline is `outputs/essay3_q2/constants_essay3_q2.json`.

**Why these went.** The legacy Essay 3 chain has two problems:
- **Outcome.** It uses any Item 5.02 filing as the outcome, but Item 5.02 also covers appointments, elections and pay.
- **Treatment and sample.** It uses the SIC-era or 7/28-era treatment and the N = 646/651 samples. Both predate the v3 rebuild.

Query 1 (`outputs/ESSAY3_QUERY1_REPORT.md`) found that the essay prose describes a dependent variable that was never computed.

## Scripts removed from run_all.py

"Last commit" is the last commit touching the script. "Last committed output" is the last commit touching that output file.

| Script | Reason | Last commit | Main output(s) | Last committed output |
|---|---|---|---|---|
| 91m_essay3_h6_form499_corrected | 7/28-chain H6 on the any-5.02 outcome. Its MDE/TOST framing was retired (decision L4). | aa2ed2d (2026-07-28) | `outputs/h6_form499_corrected_regression_results.txt`, `h6_form499_corrected_ame_by_window.csv`, `h6_form499_corrected_power_analysis.csv` | none (untracked on disk) |
| 91_essay3_governance_regressions | SIC-era logit by window; includes the immediate_disclosure mediator (decision L3) | d3ef2fe (2026-06-30) | TABLE2_turnover_summary.csv, TABLE4_ownership_results.txt, with_mediator_model_coefficients.csv | — |
| 91b_essay3_reduced_form_mediation | Reduced form plus mediator first stage; source of the 14.52pp first stage | d3ef2fe (2026-06-30) | `essay3_governance/reduced_form_h6_results.csv`, `mediator_first_stage_results.csv` | aa2ed2d / afa618a |
| 91c_essay3_mediation_bootstrap | Mediation (decision L3: none) | d3ef2fe (2026-06-30) | `essay3_governance/mediation_bootstrap_indirect_effects.csv` | aa2ed2d |
| 91e_essay3_h6_tost_equivalence | TOST (decision L4: none). The run_all label "confirms FCC effect is economically negligible" is withdrawn. | 5abe766 (2026-07-22) | `essay3_governance/h6_tost_equivalence_results.csv`, `H6_TOST_Equivalence_Test.txt` | aa2ed2d |
| 91f_essay3_h6_firm_size_heterogeneity | Quartile heterogeneity on the legacy outcome | 5abe766 (2026-07-22) | `essay3_governance/h6_firm_size_heterogeneity_full.csv` | aa2ed2d |
| 91g_extract_reduced_form_controls | Controls table from the legacy reduced form | 5abe766 (2026-07-22) | `essay3_governance/h6_reduced_form_all_coefficients.csv` | aa2ed2d |
| 91h_essay3_cox_hazards | Cox HR 1.43 (post hoc; outcome includes appointments and pay). Robustness only; now retired with its chain. | aa2ed2d (2026-07-28) | `cox_model_all_turnover.csv`, `H6_Cox_Model_Results.txt` | aa2ed2d |
| 91j_essay3_ols_lpm_and_negbin | LPM and negative binomial on the legacy outcome | 5abe766 (2026-07-22) | `essay3_governance/ols_lpm_h6_results.csv`, `negative_binomial_h6_results.csv` | aa2ed2d |
| 91k_essay3_robustness_checks | Threshold and restricted-sample checks on the legacy outcome | 5abe766 (2026-07-22) | `essay3_governance/robustness_check{1,2,3}_*.csv` | 5abe766 |
| 102_extended_governance_windows | Entirely Essay 3: 30/90/180-day windows on the any-5.02 outcome with the SIC treatment | faae3ee (2026-06-30) | `outputs/tables/TABLE_EXTENDED_GOVERNANCE_WINDOWS_RESULTS.csv` | aa2ed2d |
| 91_essay3_mediation_analysis | Volatility → turnover mediation (decision L3) | d3ef2fe (2026-06-30) | TABLE_Mediation_Effects_Essay3.txt, Mediation_Summary_Essay3.txt | — |

These edits were also made in `run_all.py`:
- The 91m entry is removed from `critical_keys`.
- The legacy Essay 3 files are commented out of `verify_outputs` `critical_files`, and the Query 2 outputs are added.
- The docstring and the final banner now mark 16.71pp, 14.52pp and the 7/28 H6 figures as RETIRED.
- The Query 2 chain is added as its own category.
- `LONG_RUNNING_SCRIPTS` has entries for 187, 191 and 202.

**Script 46 stays in run_all.** Script 53 merges its committed output for the legacy Essay 1/2 scripts. Removing 46 is in Tim's parking lot, pending a check that `executive_changes.csv` is committed and that 53 runs without 46.

> **SUPERSEDED 2026-09-29 (Part H).** Both conditions were checked and both hold, so script 46 is retired. See the Part H entry below.

## Hardcoded values retired in scripts that stay

| Script | Location | Value | Action |
|---|---|---|---|
| 96_economic_significance | Section 3 (`turnover_prob_increase`), report text part C | 0.053 (+5.3pp) | Set to NaN; every turnover-cost figure now prints nan. The text is marked retired. |
| 97_heterogeneous_mechanisms | Section 5 (Table E) | LPM of executive_change_30d by size quartile | Gated off with `RETIRED_ESSAY3 = True` (the loop runs over an empty list) |
| 97_heterogeneous_mechanisms | Figure 3 | `fcc_turnover = [19.23, -20.08, -29.96, 11.72]`, `timing_turnover = [-22.53, -20.58, -20.27, 5.79]` | Gated off. The existing `Essay3_Heterogeneous_Turnover.png` on disk is a legacy artifact. |
| 161_old_vs_new_exhibit | line 68 | '+16.71pp descriptive' | Marked "[RETIRED 2026-09-11: no computed source; ESSAY3_QUERY1_REPORT C1]" |
| build_essay3_appendix_all_tables | lines 130, 162 | +14.52pp | Marked retired |
| create_essay3_appendix_word | line 253 | +14.52pp | Marked retired |
| create_essay3_appendix_docx | lines 197, 211 | 14.52 | Marked retired |
| create_essay3_appendix_sequential | lines 183, 193 | 14.52 | Marked retired |

**Not run.** Per the standing rules, neither `run_all.py` nor script 158 was run. Every edited script was checked with `py_compile`.

---

# Addendum — 2026-09-11 (repo hygiene, after the README rewrite)

## Script archived

| Script | Moved to | Reason |
|---|---|---|
| `scripts/update_readme.py` | `scripts/root_dev_archive/update_readme.py` | A one-off that rewrote `README.md` in place through a hardcoded absolute path (`C:\Users\mcobp\DISSERTATION_CLONE\README.md`), string-replacing audit-era H1 values (`0.57%` → `0.649%`, `p=0.539` → `p=0.443`). Those values match neither the old README nor the current one, and the README now carries no numbers at all. It was never in `run_all.py`, and nothing references it. Moved with `git mv`, so its history is preserved. |

## Stale pointers corrected

The line `outputs/tables/appendix_v3/` names a directory that has never existed. The Essay 1 appendix tables are in **`outputs/rebuild/appendix_v3/`**, written by `scripts/158` (Word build `scripts/160`).

- Corrected in 18 committed files: `outputs/SAMPLE_ATTRITION_LEDGER.md`, `outputs/ESSAY1_APPENDIX_TABLES_FORM499.md` and `outputs/ESSAY3_QUERY2_REPORT.md`, plus the 15 audit-era files that carry the same boilerplate tombstone block.
- `scripts/141_essay1_appendix_tables_form499.py` no longer exists. The two documents that still described it as live — `docs/DATA_QUALITY_DOCUMENTATION.md` and `outputs/STALE_RESULTS_MANIFEST.txt` — now say so and name the current generator.

None of these files is read by code: every reference is either the generator that writes it, a filename inside another script's printed output, or a line of banner text. None is a Git LFS pointer. The edits change documentation only.

---

# Addendum — 2026-09-29 (Run-All Follow-Up, Stage 2)

Tim's ruling of 2026-09-29: **v4 is authoritative for Essay 3.** Each part below is its own
commit. Nothing is deleted: every retired script and every output stays on disk and in git
history. Neither `run_all.py` nor `scripts/158` was executed.

## Part F1 — Essay 3 Query 2 retired; the v4 chain staged as authoritative

**Retired: the Essay 3 Query 2 chain** (scripts 187 → 195 → 199 → 202 → 190/191 → 203).

| | |
|---|---|
| **Reason** | Superseded. v4 changes the *sample*, not the method: the classifier functions are byte-identical by AST and the estimator is identical line for line, but v4 relinks CRSP point-in-time, which moves the sample from N = 338 / 107 treated / 12 parent CIKs to **N = 405 / 109 treated / 13 parent CIKs** (G = 119, G\* = 24.5). Two builds of the same hypothesis cannot both be citable. |
| **Ruling** | Tim, 2026-09-29: "v4 is authoritative for Essay 3. Record q2 as retired in `outputs/RETIREMENT_LEDGER.md`; keep its outputs." |
| **Last committed output** | `outputs/essay3_q2/` — kept, not deleted. It is the **v3 side of the `scripts/239` side-by-side**, which is why the category stays staged in `run_all.py` rather than being commented out. |
| **Not authoritative** | `outputs/essay3_q2/constants_essay3_q2.json`. The authoritative constants file is `outputs/essay3_v4/constants_essay3_v4.json`, written and asserted by `scripts/227`. |
| **Still names q2** | `docs/claude/ESSAY3_POST_RERUN_STATE.md` predates this ruling and still describes the q2 build as current. It is Tim's document; it is not edited here. |

**Added: the `ESSAY 3 — v4 CHAIN` category**, 24 live steps in `REPRODUCE_ESSAY3_V4.md` order —
212, 214, 215, 219, 234, 233, 230, 235, 237, 220, 238, 232, 224, 227, 229, 228, 239, 242,
243, 244, 246, 245, 217, 210.

The order is not numeric, deliberately, and two of the departures are load-bearing:

- **232 before 224** — 224's ledger reads the censoring result.
- **233 before 224** — 224 aborts unless every reconciliation row says `agree`.
- **210 last** — the freeze gate cannot see newly added files until they are staged.

**Does the chain assert against its own outputs?** Yes, at six points: `224` asserts its own
ledger closes; `227` asserts every ladder value against `constants_essay3_v4.json`; `229`
re-derives HC3, CV1 and CV3 and asserts equality with `f1_ladder.csv` at all three windows;
`242` asserts t and p reproduce `f1_ladder.csv` within its stored precision; `243` asserts
the control coefficients and the logit AMEs against `f1_ladder.csv` and `f1_logit_ame.csv`;
`244` carries 24 assertions and `245` thirty-six.

**Not staged, deliberately:** 211 and 216 (WRDS pulls, subscription), 213 and 231 (SEC
fetches, network plus a declared User-Agent), 221–223 and 225–226 (one-off blind validation
and audit draws), 236 and 218 (imported, not run), 241 (superseded by 227). Their outputs
are committed and are treated as inputs.

**Also added:** `scripts/160_appendix_v3_to_word.py` as a live step **immediately after
158**. It renders the 16 Essay 1 appendix tables that 158 writes, and it was never staged,
so the Word appendix was only ever built by hand.

## Part G1 — the 13 Essay 3 H6 keys are removed from `constants_v3.json`

**Retired: every Essay 3 value written by `scripts/158_rebuild_s8_regenerate.py`.**

| | |
|---|---|
| **Keys removed** | `N_essay3`, and for each window in {30, 90, 180}: `H6_{w}d_base_rate`, `H6_{w}d_ame_pp`, `H6_{w}d_p`, `H6_{w}d_mde80_pp`. Thirteen keys. |
| **Reason** | They were the **legacy any-Item-5.02 outcome** on the 338-event sample — the outcome the Query 2 retirement retired and that `ESSAY3_QUERY1_REPORT.md` found the essay prose never computed. They sat in the same JSON file as the live Essay 1 and Essay 2 constants, under `H6_` key names, with nothing marking them superseded. A reader taking "H6" from `constants_v3.json` got the retired figure. |
| **Removed from** | `scripts/158_rebuild_s8_regenerate.py`, a 21-line block. Replaced by a comment block naming the removed keys and the reason, so the absence is legible rather than silent. |
| **Where Essay 3 values live now** | `outputs/essay3_v4/constants_essay3_v4.json` only, written and asserted by `scripts/227`. Nothing in 158 may write an Essay 3 result again. |
| **Effect on the file** | `constants_v3.json` on disk still carries the 13 keys until 158 is next run. **158 was not run** — the standing rule holds. The keys disappear at the next 158 run, which is the same run as the pending Essay 1 rebaseline. |

## Part G2 — the HC3 status label may no longer read SIGNIFICANT

`scripts/158` set two status strings by comparing an **HC3** p-value to .05 and writing
`'SIGNIFICANT'`. HC3 is a **disqualified rung** on this project's inference ladder
(`run_all.py:77-78`; the placebo rejects at 12.1% under CV1, and HC3 is more
anticonservative still). A file consumed as the constants of record must not contain a
significance verdict from a rung that has been ruled out.

Both branches — the Essay 1 hypothesis loop and the H5 block — now read
`'HC3-ONLY, NOT A VERDICT (disqualified rung; see scripts/165)'`. The `BOUNDED NULL` and
`NULL-INCONCLUSIVE` branches are untouched: neither claims significance. A real verdict
needs CV3 or the wild cluster bootstrap, which 158 does not compute; Essay 2's inferential
frame is `scripts/165`.

## Part H — 28 steps retired from `run_all.py`

**The ruling.** Tim, 2026-09-29: "Retire the 31 live steps that read
`FINAL_DISSERTATION_DATASET*` and feed nothing downstream."

**The count is 28, not 31, and the correction is mine.** Re-testing the ruling's own
criterion mechanically against the list I had produced in Part A found **four** entries that
do not satisfy it:

| Script | What the re-test found | Outcome |
|---|---|---|
| `180_essay2_elevation_calibration` | Contains **no reference to `FINAL_DISSERTATION_DATASET`**. It reads `outputs/tables/essay2_v2/t42_final_sample_with_repairs.csv` — the **canonical** Essay 2 sample — and its own docstring names its output as the source for **Table 21 Panel C**. | **NOT retired.** It fails the criterion on both halves. |
| `181_essay2_spec_curve_permutation` | Same: no legacy reference. Reads `t1_final_sample.csv` and asserts `N == 333`, the canonical Essay 2 sample. | **NOT retired.** |
| `power_analysis_h3_h4` | Reads no data at all. It hardcodes **`n = 653`** (line 19), a pre-rebuild sample size, and computes an MDE from it. | Retired, on a **different reason**: a hardcoded pre-rebuild constant, feeding nothing, with an untracked output. |
| `extract_merge_fama_french` | Reads the raw Ken French files, not the legacy dataset. Writes `Data/wrds/fama_french_factors.csv`, which stays committed. | Retired, on a **different reason**: all nine scripts that read that file are themselves retired here, so no live step consumes it. |

**Criterion 2 was then re-tested for all 28** against (a) the 77 steps still live after this
part, (b) 87 cited documents — the essay appendices, the reports, the constants files and
`docs/` — matching on output filename. **No output of any of the 28 is read by a surviving
step or named in a cited document.**

### The 28

"Last commit" is the last commit touching the script. Their shared input is the pre-rebuild
`FINAL_DISSERTATION_DATASET*`, which is why they go.

| Script | Last commit | Result file(s) under `outputs/` | Last committed output |
|---|---|---|---|
| 99_add_cpni_hhi_variables | d3ef2fe (2026-06-30) | none - console and log output only | - |
| 70_summary_statistics | 163fc84 (2026-09-15) | none - console and log output only | - |
| h1_timing_fcc_interaction | b53541a (2026-07-24) | `outputs/H1_timing_fcc_interaction_results.csv` | b53541a (2026-07-24) |
| 82_clustered_vs_hc3_comparison | d3ef2fe (2026-06-30) | `outputs/tables/essay2/TABLE_B9_clustered_vs_hc3_comparison.txt` | afa618a (2026-07-23) |
| 90_essay2_volatility_regressions | aa2ed2d (2026-07-28) | none - console and log output only | - |
| 86_essay3_fcc_causal_identification | d3ef2fe (2026-06-30) | none - console and log output only | - |
| scm_mahalanobis_distance | afa618a (2026-07-23) | `outputs/scm_mahalanobis_results.csv`, `outputs/scm_mahalanobis_firm_level.csv`, `outputs/scm_mahalanobis_summary.csv` | afa618a (2026-07-23) |
| 00_data_validation_checks | d3ef2fe (2026-06-30) | none - console and log output only | - |
| 99_firm_fixed_effects_analysis | faae3ee (2026-06-30) | `outputs/tables/FE_H1_H4_RESULTS.txt` | - |
| 100_ransomware_heterogeneity | faae3ee (2026-06-30) | `outputs/tables/TABLE_RANSOMWARE_HETEROGENEITY_RESULTS.csv` | afa618a (2026-07-23) |
| 101_media_coverage_heterogeneity | faae3ee (2026-06-30) | `outputs/tables/TABLE_MEDIA_COVERAGE_HETEROGENEITY_RESULTS.csv` | afa618a (2026-07-23) |
| 103_breach_type_diversity | faae3ee (2026-06-30) | `outputs/tables/TABLE_DIVERSITY_HETEROGENEITY_RESULTS.csv` | afa618a (2026-07-23) |
| 104_restatement_summary | faae3ee (2026-06-30) | none - console and log output only | - |
| 106_information_environment_composite | d3ef2fe (2026-06-30) | `outputs/tables/TABLE_INFO_ENVIRONMENT_COMPOSITE_RESULTS.csv` | afa618a (2026-07-23) |
| 92_heterogeneity_analysis | d3ef2fe (2026-06-30) | none - console and log output only | - |
| 93_market_model_sensitivity | d3ef2fe (2026-06-30) | none - console and log output only | - |
| 95_low_r2_sensitivity | d3ef2fe (2026-06-30) | none - console and log output only | - |
| robustness_1_alternative_windows | d3ef2fe (2026-06-30) | none - console and log output only | - |
| power_analysis_h3_h4 | afa618a (2026-07-23) | `outputs/tables/essay1_null_sensitivity_analysis.txt` | - |
| overlap_audit_fcc_clustering | 7951379 (2026-07-24) | `outputs/overlap_audit_summary.csv` | aa2ed2d (2026-07-28) |
| corrected_longrun_car_clustering | 7951379 (2026-07-24) | `outputs/corrected_longrun_analysis_results.csv` | aa2ed2d (2026-07-28) |
| calendar_month_clustering_60_90 | 7951379 (2026-07-24) | `outputs/calendar_month_clustering_results.csv` | aa2ed2d (2026-07-28) |
| extract_merge_fama_french | 03c8ae6 (2026-07-24) | none - console and log output only | - |
| sample_composition_diagnostic | 03c8ae6 (2026-07-24) | none - console and log output only | - |
| ff3_simple_merge | 03c8ae6 (2026-07-24) | none - console and log output only | - |
| factor_model_carhart_ff5 | 03c8ae6 (2026-07-24) | `outputs/factor_model_robustness_results.csv` | aa2ed2d (2026-07-28) |
| extended_bhar_60d_90d | aa2ed2d (2026-07-28) | `outputs/extended_bhar_60d_90d_results.csv` | aa2ed2d (2026-07-28) |
| 46_executive_changes_item5_02_with_cache | aa2ed2d (2026-07-28) | none - console and log output only | - |

**Script 46 — the ledger's open item is now closed.** The 2026-09-11 entry above reads:
*"Removing 46 is in Tim's parking lot, pending a check that `executive_changes.csv` is
committed and that 53 runs without 46."* Both conditions are met.
`Data/enrichment/executive_changes.csv` is **tracked, real content, 779 rows**, with
`executive_change_180d` summing to **521** — not an LFS pointer and not empty. `scripts/53`
merges that committed file, so it runs whether or not 46 does. Script 46 is retired with
the other 27.

**Nothing was run.** Per the standing rules, neither `run_all.py` nor script 158 was
executed. Every edited file was parsed with `ast.parse`, and `run_all.py` was checked
structurally: 77 live steps, 24 of them v4, the 28 commented out, 180 and 181 still live,
`98_sox404_heterogeneity` declared live exactly once, and 158 < 160, 232 < 224, 233 < 224,
227 < 229, 210 last among the v4 steps.

## Part J1 — a duplicate step declaration removed

`scripts/98_sox404_heterogeneity.py` was declared **twice** in `run_all.py`: once in the
data-preparation category, where `scripts/121c` needs its output, and once again later. It
therefore ran twice on every pipeline invocation, the second run overwriting the first with
identical content.

The **second** declaration is commented out. The first stays, because 121c depends on it.
Nothing is retired: the script itself is unchanged and still live.

## Part J2 — retired strings removed from live script text

The retired rule-effective dates, the retired rule number and the "1,054 breaches" phrasing
appeared in **live** script docstrings and log output. In every case the text was a
*disclaimer* — it reproduced the retired string in order to deny it — but a purge grep
cannot distinguish a denial from a citation, and neither can a reader skimming log output.

Every claim is preserved; only the literals move to the inventory that already holds them,
`outputs/DEAD_DATE_PURGE_INVENTORY.md`.

| File | Sites | Change |
|---|---|---|
| `163_essay2_rerun_form499` | 4 (the ledger header, the DV-convention comment, the codebase-flags log, closing summary item 7) | The literals are replaced by a pointer to the inventory. The codebase-flags log also dropped its list of carrier scripts, which Part H and Part J3 have just made stale. |
| `robustness_1`–`robustness_5` | 1 each | "(1,054 breaches, N variables)" → "(1,054 **PRC notification records**, N variables)". 1,054 is the notification-record count, not a breach count; the two differ by the deduplication the rebuild introduced. |

`scripts/163` was verified by parsing both versions and comparing the ASTs with **every
string constant blanked out**: the skeletons are identical, so nothing but string literals
and comments moved.

**Left alone, as ruled:** the purge-detector fixtures in `scripts/168_essay3_audit.py`,
`scripts/217_v4_offline_tests.py` and `scripts/240_methods_toolkit_v4.py`. Those files must
contain the strings — they are what the detectors search for.

**Verified:** across the 77 live steps, excluding those three fixtures, the strings
"Rule 37.3", "September 28, 2007", "September 28 2007", "January 1, 2007",
"1,054 breaches" and "4813/4841/4899" now occur **zero** times.

## Part J3 — six dead commented-out tuples deleted

Six commented-out step tuples named script files that **no longer exist on disk**. A
commented tuple naming a missing file is worse than nothing: it reads as "this step is
temporarily off", when in fact the step cannot be restored without rewriting the script.
They are deleted from `run_all.py`; their history remains in git.

Five of the six had never been recorded as retired anywhere. They are recorded now.

| Script | Reason it went | Last commit touching it | Recorded before? |
|---|---|---|---|
| `142_sample_attrition_ledger` | Superseded by the live ledgers: `outputs/ESSAY2_SAMPLE_ATTRITION_LEDGER.md` (script 163, Phase A) and, for Essay 1, the Part K ledger. Its own note documented the retired rule date and treatment. | 0e75740 (2026-09-08), which deleted it | no — recorded here |
| `83_fcc_causal_identification` | Pre-rebuild FCC identification on the SIC-era treatment. | 0e75740 (2026-09-08), which deleted it | no — recorded here |
| `create_parallel_trends_figure` | Pre-rebuild parallel-trends figure on the retired sample. | 0e75740 (2026-09-08), which deleted it | no — recorded here |
| `create_balance_test_table` | Pre-rebuild balance table on the retired sample. | 0e75740 (2026-09-08), which deleted it | no — recorded here |
| `94_falsification_tests` | Pre-rebuild falsification tests; also a carrier of the retired rule date. | 0e75740 (2026-09-08), which deleted it | no — recorded here |
| `141_essay1_appendix_tables_form499` | Superseded by `scripts/158` (tables) and `scripts/160` (Word). Already recorded in the 2026-09-11 addendum under "Stale pointers corrected". | 0e75740 (2026-09-08), which deleted it | yes |

## Part L — TOMBSTONE on `outputs/tables/essay2_appendix/`

**Not a retirement of a script: a withdrawal of 41 committed artefacts as evidence.**
Nothing is deleted.

| | |
|---|---|
| **What** | The 41 CSV files in `outputs/tables/essay2_appendix/`, plus `manifest.csv`. |
| **Reason** | No committed script writes them. The only script naming the directory is `scripts/178_essay2_appendix_docx.py`, which merely renders them into `ESSAY2_APPENDIX.docx` (itself gitignored). The code that produced the numbers was a scratchpad file, `emit_appendix.py`, never committed. A figure here cannot be traced to its data or specification, cannot be regenerated from a clean clone, and cannot be checked. |
| **Not stale copies** | `163` and `164` write **61** files to `outputs/tables/essay2_v2/`. These two sets share **zero** filenames — verified, not assumed. This directory holds `channel_*`, `cluster_*`, `delay_*` names; the live directory holds `t1_*` through `t52_*`. So these are a **different set of tables**, not an out-of-date copy: a citation to a file here cannot be repaired by pointing at the same name in `essay2_v2/`, because there is no same name. |
| **Cite instead** | `outputs/tables/essay2_v2/` (written by 163 and 164, and since Part I2 asserted at N = 333 / 104 treated / 82 clusters on both write and read), `scripts/165` for the inferential frame, and `outputs/ESSAY2_SAMPLE_ATTRITION_LEDGER.md` for the chain. |
| **Marker on disk** | `outputs/tables/essay2_appendix/TOMBSTONE.md` |
