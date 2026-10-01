# Essay 3 — settled state, v4

Branch `rebuild-v4`. **Not merged into `main`.**

**This document transcribes no figures.** Every number lives in a named artefact and is
cited by pointer. That is deliberate: a transcribed number goes stale silently, and the
v3 state doc it replaces is now partly wrong for exactly that reason. If a figure is
wanted, read it from the file named here.

Where this document and `ESSAY3_POST_RERUN_STATE.md` (v3) conflict, this one governs for
v4. Section 7 lists what is superseded.

---

## 1. Where the numbers live

| What | File |
|---|---|
| Every estimation constant | `outputs/essay3_v4/constants_essay3_v4.json` |
| Sample ledger, every step with a **computed** note | `outputs/essay3_v4/e_ledger.csv` |
| Primary verdicts + placebo, v3 beside v4 | `outputs/essay3_v4/239_verdict_table.csv` |
| Full inference ladder | `outputs/essay3_v4/f1_ladder.csv` |
| 27 sensitivities, with `row_type` and `hc3_status` | `outputs/essay3_v4/f3_sensitivities.csv` |
| Test ledger, BH within family | `outputs/essay3_v4/i_tests.csv` |
| LOCO by window | `outputs/essay3_v4/f3_loco.csv`, `229_se_diagnostics.log` |
| Cluster variance shares | `outputs/essay3_v4/f1_cv3_variance_shares.csv` |
| v3-overlap sensitivity | `outputs/essay3_v4/239_v3_overlap_sensitivity.csv` |
| Censoring, with margins | `outputs/essay3_v4/232_censoring.csv` |
| All 94 constants, v3 vs v4 | `outputs/essay3_v4/239_v3_vs_v4_constants.csv` |
| T-Mobile case timeline | `outputs/essay3_v4/228_case.log` |

## 2. What is frozen, and provable

| Artefact | Frozen how |
|---|---|
| v3 | `scripts/210`, run **after staging**. Tag `v3-frozen`. |
| Classifier | `scripts/220` byte-identical to v3's `scripts/195`. No result may retune it. |
| Analysis plan | `outputs/essay3_v4/ANALYSIS_PLAN_V4.md`, sha256 `c9dbe88910669c7720a937b0119d906a312f08bd26349bc174ccf04e16f8afe0`, committed at `6f033bc` **before** `227` ran. No specification change permitted after it. |
| Reference codes | Committed before the classifier ever ran on those documents. sha256 of blind and verified files in `outputs/rebuild_v4/231_validation_draws.md`. |

The plan's pre-specified test counts held exactly, and CEO-only was **not** estimated
because its pre-specified ≥10-per-group gate failed — see `i_tests.csv` and `f5_ceo.csv`.

## 3. Validation of the new documents

- Blind codes: `outputs/essay3_v4/VALIDATION_REFERENCE_CODES_V4.psv` (+ `_README.txt`)
- Verified codes (primary): `..._V4_VERIFIED.psv`; change log `VALIDATION_VERIFICATION_LOG_V4.csv`
- Accuracy beside v3-era: `outputs/essay3_v4/238_new_document_agreement.csv`
- Bounds over rows that could not be settled: `238_new_document_bounds.csv`
- Narrative: `238_scoring.md`

**Two limits to carry into prose.** No code changed at verification; the flag set moved,
and four rows remain unsettled, so field accuracy is reported as bounds rather than a
point. And `pre_announced` is **mechanical** on the full pool — the draw spans the whole
fetch window, so most drawn filings sit in the baseline window years before the
reference date. The substantive figure is restricted to the outcome window and rests on
very few documents; read it from `238_new_document_agreement.csv`, and do not quote the
full-pool number as a measure of anything.

### Validation-draw history

`outputs/rebuild_v4/231_validation_draws.md` records all three draws with sha256s. Two
were superseded **before any coding or classification**, so the firewall held:

1. pool of 445 — the fetch was later found short by 5 documents (`scripts/235`)
2. pool of 5 — `scripts/231` had defined the pool as "documents THIS run fetched", so a
   re-run that had little outstanding produced a pool of 5 though v4 had added ~450
3. **operative**: `outputs/rebuild_v4/237_validation_new_ids.csv`, pool defined against
   `git ls-tree -r v3-frozen` intersected with `b_scope_filings.csv` — a property of the
   repository, not of fetch history

## 4. The three declared adaptations

Each is an input-reading choice, declared where it occurs and before it mattered.

1. **Recall input is v3's.** `227`'s recall-correction sensitivities read
   `outputs/essay3_q2/d3_audit_recall_by_stratum.csv`. v4 has no audit of its own; the
   classifier is byte-identical, so measured recall is a property of the classifier.
   **Assumes** recall measured on v3-era documents transfers. Declared in
   `ANALYSIS_PLAN_V4.md` before `227` ran.
2. **T-Mobile case files are v3's.** `228` falls back to six artefacts from `scripts/191`
   that were never copied into the 220s; they describe one firm's governance and do not
   vary with the event set. It prints which ones on each use.
3. **The filing-to-event join uses `outcome_cik`, not `final_cik`.** v4 separates the
   equity link from the filing entity. Joining on `final_cik` would find no filings for
   the events where they differ and score them as silent zeros.

## 5. Two v4 structures a reader must know

**`outcome_cik` ≠ `final_cik`.** `final_cik` is the equity link; `outcome_cik` is the
entity whose Form 8-Ks are read. They diverge where an event was re-parented across a
succession that postdates the breach — Disney's 2008 event links a company created in
2019. The rule and its evidence are in `scripts/234` and
`outputs/rebuild_v4/234_candidate_evidence.csv`; the affected events are named in
`e_ledger.csv`. `scripts/233` reconciles the rule against v3's hard-coded `RESOLVE` dict
and `224` aborts unless every row agrees.

**`CANONICAL_V4` carries v3's inherited columns.** `has_crsp_data`, `permno` and the four
covariates in that file are v3's, not v4's — Nokia is the tell. Every Essay 3 v4 script
loads through `scripts/236_essay3_v4_loader.py`, which drops them and re-attaches v4's
own; `scripts/217` asserts that none of 220–229 or 232 opens the file directly.

**The two treated events lost at the Compustat step** are T-Mobile's 2013 events. This is
not a coverage gap to fix: no fiscal year ending before the breach describes the
post-merger registrant (MetroPCS's pre-May-2013 financials would describe a different,
smaller firm). The note is computed into `e_ledger.csv`, not asserted here.

## 6. Reproduction

Procedure, traps and the verified result: `docs/claude/REPRODUCE_ESSAY3_V4.md`.

In short: clone from GitHub into a fresh directory, **full** `git lfs pull`, and fetch
the `v3-frozen` tag if the clone is shallow. A worktree is not a clean-clone test — it
shares `.git` and the LFS store and cannot catch a missing object or ref. `220` and `227`
are slow and are covered by their own assertions instead (`227` asserts against the
constants it first wrote; `229` independently recomputes the SEs).

## 7. What this supersedes in `ESSAY3_POST_RERUN_STATE.md` (v3)

That document remains correct **as the v3 record**. These statements in it do not
describe v4:

| v3 statement | Status in v4 |
|---|---|
| §1 sample ladder (489 → CRSP → covariates → outcome → analysis sample) and every count in it | **Superseded.** Read `e_ledger.csv`. The CRSP step changed because the link was rebuilt without CCM. |
| §1 "Attrition: the outcome-data requirement removes one event (Nokia)" | **Superseded.** In v4 that requirement removes none; `outcome_cik` is resolved by rule beforehand. |
| §1 "Two CIK re-pointings, both controls: Disney, Aon" | **Superseded.** v4 resolves the filing entity by rule for every event; the divergent set is larger and is listed in `e_ledger.csv`. |
| §2 primary table (coefficients, SEs, p, MDE, G = 81, 12 treated clusters) | **Superseded.** Read `f1_ladder.csv` / `constants_essay3_v4.json`. **The verdict does not change** — see `239_verdict_table.csv`. |
| §3 MDE figures and "G\* = 23.6, cluster-size CV 2.267" | **Superseded.** Read `f1_ladder.csv`. |
| §3 "FIS accounts for 65.6% of the 90-day CV3 jackknife variance"; "T-Mobile's share 10.1%" | **Superseded.** Read `f1_cv3_variance_shares.csv`. |
| §4 LOCO table, including which cluster flips at which window | **Superseded.** v3's table is not v4's. Read `f3_loco.csv` and the per-window lines in `229_se_diagnostics.log`, which now carry a window prefix on every line. |
| §5 placebo figures | **Superseded.** Read `f4_placebo.csv`. Still null. |
| §6 sensitivity table and "smallest CV3 p is .1532" | **Superseded.** Read `f3_sensitivities.csv` and `i_tests.csv`. Still all null. |
| §6 SIC FE caveat cell counts | **Superseded.** Read `f3_sic2_cells.csv`. |
| §7 round-2 validation row (κ, recall, "0 CEO positives") | **Not superseded, but not the v4 figure.** v4's new-document round is `238_new_document_agreement.csv`; both are reported side by side. |
| §7 "CEO-only is not estimable" | **Holds in v4**, by the same pre-specified gate. Counts in `f5_ceo.csv`. |
| §8 "clean clone at `c5f761d` ran 195–204" | **Superseded for v4.** See `REPRODUCE_ESSAY3_V4.md`; a third silent failure (CRLF renormalisation of generated CSVs) was found and fixed here. |
| §9 T-Mobile weight and case-study facts | **Carry over**, but recompute the weight against the v4 sample before quoting it. |
| §10 "31 tests" | **Holds**, and was pre-specified. Confirm from `i_tests.csv`. |
| §11 claims the circulated draft no longer supports | **Carries over unchanged.** Nothing in v4 revives any of them. |

**The headline is unchanged.** The hypothesis is not supported at 30, 90 or 180 days, on
CV3 and WCR, in v3 and in v4, and the v3-overlap sensitivity shows the control-side
linkage gain is not what produces that. Settled language stays as v3 fixed it: "the
hypothesis is not supported" — never "confirms the null", never an equivalence claim.
