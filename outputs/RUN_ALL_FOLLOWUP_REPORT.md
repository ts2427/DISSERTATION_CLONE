# Run-All Follow-Up — STAGE 1 (read-only)

**Nothing executed from `run_all.py`. Script 158 not executed. No script, table, constants
file or prose edited.** Untracked until you say to commit (`.gitignore:79` is `*.md`).

Two corrections to my own earlier work are flagged where they arise: one to the prior
audit's framing of the pre-rebuild dataset (Part B), and one to my first attempt at the
clean-clone pointer count in this query (Part D).

---

# PART A — Which Essay 3 build is authoritative

## A1. What v4 is

**37 scripts, `210`–`246`.** Opened `14085e6` (2026-09-18, *"REBUILD V4 Stage 0: freeze v3,
open rebuild-v4, add the freeze check"*), last touched `39ef0ba` (2026-09-25). The
authorising directive is committed in-repo at `docs/claude/REBUILD_V4_QUERY.md`, whose
stated reason (`:7-14`, verbatim):

> *"The stage-5 matcher (`scripts/155_rebuild_s5_outcomes.py:124–141`) maps CIK → ticker
> from *current* SEC ticker files. Firms since acquired, taken private, or reorganized fail
> at `155:125` and drop out. The manual ticker dictionary (`155:58–71`) repaired 24 of 111
> treated matches and 11 of 245 control matches, and `permno_match` records neither. CRSP
> retention is 111/118 treated against 245/371 control. v4 replaces the matcher with one
> point-in-time procedure applied identically to both groups."*

Its prime directive (`:17-23`): *"v3 does not change … No existing file is edited, moved,
renamed, or deleted."* `scripts/210` enforces this as a gate over a 2,647-file manifest.

### What v4 changes relative to Query 2 — and what it does not

| Dimension | Query 2 | v4 | Changed? |
|---|---|---|---|
| **Classifier method** | `scripts/195` | `scripts/220` | **NO** |
| **Outcome definition** | executive departure, one per person, earliest disclosing filing | same | **NO** |
| **Event anchor** | notification date, `(t0, t0+w]` | same | **NO** |
| **Estimator** | LPM, OLS | same | **NO** |
| **Inference rungs** | HC3 / CV1 / CV3 / WCR, B = 99,999 | same | **NO** |
| **CRSP linkage** | CIK → current ticker → permno (`155`) | CIK → gvkey → CUSIP → permno, point-in-time, with an identity gate | **YES** |
| **Filing entity** | `final_cik` | `outcome_cik`, resolved by rule (`234`) | **YES** |
| **Covariates** | v3's, from `156` | rebuilt from `comp.funda` (`219`), 550-day rule preserved verbatim | **YES** |
| **Sample** | 338 events | 405 events | **YES** |

**The classifier is not merely "the same version" — its functions are byte-identical.**
The two files differ in size (43,766 vs 46,588 bytes), but an AST comparison of every
method shows:

```
function         in 195     in 220     identical?
classify         yes        yes        IDENTICAL
person_key       yes        yes        IDENTICAL
pre_announced    yes        yes        IDENTICAL
section_502      yes        yes        IDENTICAL
strip_caption    yes        yes        IDENTICAL
to_text          yes        yes        IDENTICAL
```

Every byte of difference is docstring and I/O path. `220`'s own header says so:
*"Copied from `scripts/195_essay3_q2_classifier_v2.py`. Only the data sources move; the
method does not."* Both constants files record the same classifier identity:
`scripts/195 v2 (6f7be7a, blob ec32364)`.

The estimator is identical line for line — `202:63` and `227:88` are the same
`ladder(d, ycol, xcols, B=99_999, B_ci=9_999, full=True, fe=None)`, with the same CV3
jackknife at `202:92` / `227:117` and the same HC3 fit at `202:93` / `227:118`.

**So v4 changes the sample, not the method.** That is the single fact that matters for
authority.

## A2. Which build each document describes

| Document | Cites | Verbatim |
|---|---|---|
| `docs/claude/ESSAY3_POST_RERUN_STATE.md` | **q2** | `:24` *"`constants_v3.json` untouched; Essay 3's own constants are in `outputs/essay3_q2/constants_essay3_q2.json`"* |
| `outputs/ESSAY3_QUERY2_REPORT.md` | **q2** (and `constants_v3.json` for Essay 1) | `:65` *"outputs/rebuild/constants_v3.json (Essay 1: 489 / 354 / 338)"* |
| `docs/claude/ESSAY3_V4_STATE.md` | **v4** | `:19` *"Every estimation constant — `outputs/essay3_v4/constants_essay3_v4.json`"* |
| `docs/claude/POST_DEFENSE.md` | **v4** | `:1-3` *"Essay 3 v4 — post-freeze change rule. Tagged `essay3-v4-final`."* |
| `outputs/ESSAY3_QUERY3_REPORT.md` | **v4** | `:34` *"Authoritative constants: `outputs/essay3_v4/constants_essay3_v4.json`"* |

**The conflict is explicit and adjudicated in the repository.**
`docs/claude/ESSAY3_V4_STATE.md:10-11`, verbatim:

> *"Where this document and `ESSAY3_POST_RERUN_STATE.md` (v3) conflict, this one governs
> for v4. Section 7 lists what is superseded."*

Its §7 is a line-by-line supersession table retiring the q2 sample ladder, primary table,
G/G\*, LOCO table, placebo figures and sensitivity table. `POST_DEFENSE.md` then froze the
v4 chain at tag `essay3-v4-final` and logged three exceptions against it — a freeze rule
would not exist for a build that had been abandoned.

## A3. Side-by-side, all keys

**94 keys in each file. Same key set exactly: 0 q2-only, 0 v4-only. 85 differ, 9 identical.**

The 9 identical:

```
F1_30_B_wcr   99999      F1_30_window   30     classifier  scripts/195 v2 (6f7be7a, blob ec32364)
F1_90_B_wcr   99999      F1_90_window   90     n_tests     31
F1_180_B_wcr  99999      F1_180_window 180
F4_B_wcr      99999
```

Every identical key is a **design constant** — bootstrap draws, window lengths, classifier
identity, test count. Every substantive key differs. Full 94-row table available from the
comparison script on request; the headline set follows.

## A4. Headline comparison (verbatim from each file; not recomputed)

| Quantity | q2 | v4 | Differs |
|---|---|---|---|
| Analysis sample N (events) | 338 | **405** | yes |
| Treated events | 107 | **109** | yes |
| Control events | 231 | **296** | yes |
| Parent CIKs (G) | 81 | **119** | yes |
| Treated parent CIKs (G₁) | 12 | **13** | yes |
| G\* | 23.6 | **24.5** | yes |
| Cluster-size CV | 2.267 | **2.328** | yes |
| Pre-rule treated / control (events) | 0 / 6 | **0 / 7** | yes |
| Tests in the ledger | 31 | 31 | no |
| Classifier | `195 v2 (6f7be7a)` | same | no |
| **30d** coef / CV3 p / WCR p | +0.0168 / .6118 / .4924 | **+0.0040 / .9061 / .8889** | yes |
| 30d MDE80 / control rate | 0.0934 / 0.0433 | **0.0944 / 0.0439** | yes |
| **90d** coef / CV3 p / WCR p | −0.0169 / .8701 / .8154 | **−0.0410 / .6053 / .5136** | yes |
| 90d MDE80 / control rate | 0.2918 / 0.1602 | **0.2234 / 0.1453** | yes |
| **180d** coef / CV3 p / WCR p | +0.0434 / .7052 / .6474 | **+0.0233 / .8159 / .7901** | yes |
| 180d MDE80 / control rate | 0.3245 / 0.2511 | **0.2815 / 0.2466** | yes |
| Placebo coef / CV3 p / WCR p | −0.0658 / .5281 / .4060 | **−0.0862 / .3116 / .2308** | yes |
| Sensitivities: rows / null / min CV3 p | 27 / 27 / .1532 | **27 / 27 / .1132** | min p differs |

Treated parent *entities* (organizations): q2 11, v4 12 — the difference is the Sprint →
T-Mobile family collapse, which v4 applies via `scripts/224:361`.

## A5. Does any verdict differ? **No. Not one.**

Every window, every rung, both builds:

```
q2    30d coef +0.0168 | HC3 NOT(.4703) CV1 NOT(.3950) CV3 NOT(.6118) WCR NOT(.4924)
q2    90d coef -0.0169 | HC3 NOT(.7212) CV1 NOT(.7698) CV3 NOT(.8701) WCR NOT(.8154)
q2   180d coef +0.0434 | HC3 NOT(.5158) CV1 NOT(.6070) CV3 NOT(.7052) WCR NOT(.6474)
v4    30d coef +0.0040 | HC3 NOT(.8764) CV1 NOT(.8730) CV3 NOT(.9061) WCR NOT(.8889)
v4    90d coef -0.0410 | HC3 NOT(.3445) CV1 NOT(.4128) CV3 NOT(.6053) WCR NOT(.5136)
v4   180d coef +0.0233 | HC3 NOT(.7034) CV1 NOT(.7668) CV3 NOT(.8159) WCR NOT(.7901)
```

**24 of 24 rung-window cells fail to reject at .05 in both builds.** Placebo: not rejected
in both. Sensitivities: **27 of 27 null in both**.

**The T-Mobile deletion agrees in direction at every window and differs in magnitude:**

| | 30d | 90d | 180d |
|---|---|---|---|
| q2 without T-Mobile | −0.0022 | −0.0492 | −0.0196 |
| v4 without T-Mobile | −0.0164 | −0.0687 | −0.0349 |

Both builds turn negative at all three windows when T-Mobile is deleted. **Sign-flip
counts do differ:** q2 is 1 / 2 / 1 and v4 is 3 / 1 / 1. The 30-day count rises (v4 adds
Sirius XM and Sprint) and the 90-day count falls (v4 drops one). No verdict turns on it —
a sign flip on a null coefficient is a stability statement, not a result.

## A6. Can v4 run from a clean clone?

**Yes for the offline chain, verified twice in this session** (Query 4 Part H and again in
Part D below): 19 of 19 offline steps `rc=0`, all 94 constants reproducing byte-identically.

Not reproducible, and declared as such in `docs/claude/REPRODUCE_ESSAY3_V4.md`:

| Stage | Why | Status |
|---|---|---|
| `211`, `219` WRDS pulls | subscription | outputs committed under `Data/wrds_v4/` (LFS, **objects present**) |
| `213`, `231` EDGAR fetches | network + declared User-Agent | caches committed under `Data/edgar/` |

**No v4 input is an LFS pointer, untracked, or gitignored.** All `Data/wrds_v4/**` objects
show `*` (present) in `git lfs ls-files`. Two known non-content differences remain:
`CANONICAL_V4.csv` and `b_scope_events.csv` are not byte-reproducible on Windows (CR inside
quoted JSON fields), and `scripts/210` reports FAIL in a clone purely on EOL artefacts with
`SHA256 CHANGED: 0`.

## A7. One sentence

**The Essay 3 Results section's number set matches v4, not q2** — the appendix Tables 1–11
carry N = 405, 109 treated events, 13 treated parent CIKs, G = 119 and β = +0.0040 /
−0.0410 / +0.0233, all of which are v4 values and none of which appear in
`constants_essay3_q2.json` — and **yes, v4 has a documented reason to supersede q2**: the
committed directive `docs/claude/REBUILD_V4_QUERY.md:7-14` identifies a named defect in
`scripts/155:124-141` that dropped control firms asymmetrically (CRSP retention 111/118
treated against 245/371 control), `ESSAY3_V4_STATE.md:10-11` states v4 governs where the
two conflict, and `POST_DEFENSE.md` froze v4 at tag `essay3-v4-final`.

**This contradicts the standing record cited in the query.** Your note says the standing
record names q2 as authoritative, and `ESSAY3_POST_RERUN_STATE.md` does. But that document
is dated 2026-09-11 and `ESSAY3_V4_STATE.md`, dated 2026-09-19, supersedes it in writing.
**This is yours to settle, not mine** — I am reporting that the repository resolves it for
v4 and that no verdict changes either way.

---

# PART B — Dataset lineage

## B1. The 49 live steps reading `FINAL_DISSERTATION_DATASET*`

All 49 read `FINAL_DISSERTATION_DATASET_DEDUPLICATED_ENRICHED.csv` (779 rows, 99 columns)
or a sibling. Classified by what they feed:

- **18 feed something** — a constants key, an appendix table, a ledger or a figure
- **31 feed nothing downstream** — no constants file, no appendix path, no ledger, no `.png`

The 31 that feed nothing: `46`, `99_add_cpni_hhi_variables`, `98_sox404_heterogeneity`,
`70`, `h1_timing_fcc_interaction`, `82`, `90`, `86`, `scm_mahalanobis_distance`, `00`,
`99_firm_fixed_effects_analysis`, `100`, `101`, `103`, `104`, `106`,
`92_heterogeneity_analysis`, `93`, `95`, `robustness_1`–`robustness_5`,
`power_analysis_h3_h4`, `overlap_audit_fcc_clustering`, `corrected_longrun_car_clustering`,
`calendar_month_clustering_60_90`, `sample_composition_diagnostic`, `ff3_simple_merge`,
`factor_model_carhart_ff5`, `extended_bhar_60d_90d`, `defense_prep_all_tasks`.

## B2. `constants_v3.json` lineage — **a correction to my prior audit**

My audit report implied the pre-rebuild dataset might feed `constants_v3.json`. It does
not. `scripts/158_rebuild_s8_regenerate.py` is the sole writer, and its only inputs are:

```
read_csv -> Data/processed/rebuild/CANONICAL_V3.csv
read_csv -> Data/wrds/crsp_daily_returns.csv
read_csv -> Data/wrds/market_indices.csv
read_csv -> Data/F-F_Research_Data_Factors_daily.csv
```

`grep FINAL_DISSERTATION_DATASET scripts/158` returns **nothing**.

| Source | Keys |
|---|---|
| `CANONICAL_V3` (plus the CRSP/FF extracts joined to it) | **121** |
| `FINAL_DISSERTATION_DATASET*` | **0** |
| Both | **0** |

**No key in `constants_v3.json` traces to the pre-rebuild dataset.** The two vintages
coexist in the pipeline but do not mix inside the constants file. The 49 legacy-reading
steps write elsewhere — to `outputs/tables/*`, robustness tables, and diagnostics.

## B3. Do the two datasets differ? **Yes, substantially.** *(NEW — computed in this query, no script)*

```
FINAL_DISSERTATION_DATASET_DEDUPLICATED_ENRICHED.csv : 779 rows, 99 cols
CANONICAL_V3.csv                                     : 489 rows, 47 cols

treatment column, legacy : fcc_reportable   -> 139 treated records
treatment column, v3     : fcc_form499      -> 118 treated events

event keys (org_name|breach_date): legacy 779, v3 489
  in both       487
  legacy only   292
  v3 only         2
```

They are **not** row-for-row identical and the treatment variable is a **different column
with a different definition** — `fcc_reportable` (SIC-era) versus `fcc_form499` (registry
adjudication). 292 legacy rows have no v3 counterpart; 2 v3 events are absent from the
legacy file. Any value computed from the legacy file is on a different sample **and** a
different treatment definition from every value in `constants_v3.json`.

Because B2 shows no constants key touches the legacy file, this difference does not
contaminate the constants — but it does mean every output of those 49 steps is on the
superseded sample.

## B4. By essay

- **Essay 1.** Its authoritative appendix is `outputs/rebuild/appendix_v3/` (16 tables),
  written by `158` from `CANONICAL_V3`. **Zero cited values trace to the legacy dataset.**
  The legacy-era appendix, `outputs/ESSAY1_APPENDIX_TABLES_FORM499.md`, carries a
  **TOMBSTONE** header (quoted in C1) and must not be cited.
- **Essay 2.** Its chain (`163`–`182`) reads **both**: `163`, `164`, `166` read the legacy
  file *and* `CANONICAL_V3`; `169`, `180`, `174` read `CANONICAL_V3` only. The 41 committed
  appendix CSVs cannot be attributed to either, because no generator exists (C2).

---

# PART C — Essay 1 and Essay 2 appendix provenance

## C1. Essay 1

| File | Tracked | Last commit | Status |
|---|---|---|---|
| `outputs/rebuild/appendix_v3/` (16 CSVs) | yes | via `158` | **current; live writer** |
| `outputs/ESSAY1_APPENDIX_TABLES_FORM499.md` | yes | `950cb85` 2026-09-11 | **TOMBSTONE** |
| `outputs/ESSAY1_APPENDIX_TABLES.docx` | **untracked** | — | legacy |
| `outputs/Essay1_Appendix_Final.docx` | **untracked** | — | legacy |

The tombstone, verbatim (`outputs/ESSAY1_APPENDIX_TABLES_FORM499.md:1-6`):

> *"TOMBSTONE — RETIRED 2026-09-11. DO NOT CITE. This file is the 7/28 audit-era Essay 1
> appendix (pre-rebuild chain: 779 / 672 / 648, treated 127 / 118 / 115). Every number in
> it is SUPERSEDED."*

**`appendix_v2/` is empty (0 files) and nothing Essay 1 cites depended on it.** Its
builders `141` and `142` are deleted and their steps commented out. The only script still
naming that directory is `161_old_vs_new_exhibit.py`, which is not live. The word-build
step `160_appendix_v3_to_word.py` exists but is **not live in `run_all.py`**, so the 16
CSVs regenerate and the Word rendering does not.

## C2. Essay 2 — the 41 CSVs have no generator, and never did

All 41 were last committed in just two commits: **36 at `b11e884`** (2026-09-08) and
**5 at `6e0fbb9`**. `b11e884`'s body names `178` as a *"docx+markdown appendix builder"* —
a renderer, not an emitter. A search of the last 120 commits for any file named
`emit_appendix*` returns **nothing**: the emitter was never committed. No live script writes
into `outputs/tables/essay2_appendix/`; the only script naming the path is `178`, which
reads it.

`run_all.py:87-88` states this itself: *"have NO committed generator. scripts/178 only
renders them into ESSAY2_APPENDIX.docx (itself gitignored). They are committed artifacts
only."*

**No regeneration attempt was made** (it would require reconstructing the emitter, which is
Stage 2 work at best and a new script at worst).

## C3. Appendix cells by regenerability

| Essay | Appendix | Cells/files | Regenerable by a live step | By a non-live script | No generator |
|---|---|---|---|---|---|
| 1 | `appendix_v3/` 16 CSVs | 16 files | **16** (`158`) | 0 | 0 |
| 1 | `appendix_v2/` | **0 files** | — | — | — (directory empty) |
| 2 | `essay2_appendix/` 41 CSVs | **41 files** | 0 | 0 | **41** |
| 3 | `essay3_v4/` + `essay3_appendix/` | 58 files | 0 | **58** (`220`–`246`) | 0 |

---

# PART D — Clean-clone reproducibility

## D1. **87 files** arrive as LFS pointers

Fresh clone of `https://github.com/ts2427/DISSERTATION_CLONE.git` at `1cfcaac`, clean
checkout, 0 dirty files. Files under 1 KB beginning `version https://git-lfs`: **87**.

**A correction to my own first attempt in this query.** My initial scan reported **0**,
because I piped `find` into `while read` and the path `Data/JSON Files/` contains a space,
so every one of those 19 paths was silently split and lost. Re-run with a proper walk, the
count is 87 — exactly the recorded figure. The shell idiom failed silently and would have
produced a confidently wrong "zero pointers" finding.

By directory:

| Prefix | Files |
|---|---|
| `Data/JSON Files/` | 19 |
| `outputs/tables/` | 13 |
| `outputs/audit/` | 9 |
| `outputs/robustness/` | 9 |
| `outputs/essay2/` | 8 |
| `Data/enrichment/` | 6 |
| `outputs/essay2_final/` | 6 |
| `Data/audit_analytics/` | 4 |
| `outputs/essay3_revised/` | 4 |
| `outputs/ml_models/` | 4 |
| `Data/fcc/` | 2 |
| `outputs/essay2_expanded/` | 2 |
| `outputs/essay3/` | 1 |

## D2. **All 87 objects ARE on GitHub's LFS service.** The data is not lost.

This is the most important finding in Part D, and it is better news than the record implies.

```
git lfs ls-files            : 113 paths known to LFS; 27 present (*), 86 pointer-only (-)
the 87 on-disk pointers     : all 87 known to LFS
git lfs fetch --all         : "231 objects found, done."
after fetch, objects in store: 230
of the 87 pointers, object IS in the local store : 87
of the 87 pointers, object NOT in the store      :  0
```

**Cause, proven not inferred:** `git check-attr filter` over all 87 returns
`{'unspecified': 87}`. The objects download; git never runs the smudge because no
`.gitattributes` rule covers the path, so checkout leaves the pointer text on disk and
reports no error. `git lfs checkout` after a full fetch still leaves 87 pointers, because
checkout also consults the filter attribute.

**Rules that should exist and do not.** `.gitattributes` has `filter=lfs` rules for
`Data/wrds/*`, `Data/edgar/cik-lookup-data.txt`, `Data/edgar/form499_registry.xml`,
`Data/processed/DATA_DICTIONARY_ENRICHED.csv` and `Data/wrds_v4/**` — and **nothing** for
`Data/JSON Files/`, `Data/enrichment/`, `Data/audit_analytics/`, `Data/fcc/` or any
`outputs/` path. The only `outputs/` rules present are the two `-text` CRLF rules at
`:42-43`.

## D3. Reconciling 87 against 19 against 87

| Count | What it is |
|---|---|
| **87** | clean clone — every file whose object was never smudged |
| **19** | my working copy — only `Data/JSON Files/*.json` |
| **87** | the recorded figure — **correct** |

The working copy shows 19 because the other 68 were **written as real content by earlier
pipeline runs** on this machine: they are outputs (`outputs/tables/*`, `outputs/audit/*`,
`outputs/essay2/*`) that a script regenerated locally after the clone, overwriting the
pointer. The 19 NVD files are pure *inputs* that nothing regenerates, so the pointer
survives. The discrepancy is therefore not an inconsistency — it measures which pointers
happen to be downstream of a script that has been run here.

Note `Data/enrichment/regulatory_enforcement.csv` is in both lists: it shows as a pointer
in the clone and as real content in the working copy. That is the same file whose "1,055
insertions" I investigated in the prior query — the working copy holds the real object and
git reports a diff against the pointer blob forever.

## D4. Which steps read a pointer? **Only 5 of 87.**

| Pointer | Live step |
|---|---|
| `Data/enrichment/breach_severity_classification.csv` | `53_merge_CONFIRMED_enrichments` |
| `Data/enrichment/media_coverage.csv` | `53_merge_CONFIRMED_enrichments` |
| `Data/enrichment/prior_breach_history.csv` | `53_merge_CONFIRMED_enrichments` |
| `Data/enrichment/regulatory_enforcement.csv` | `53_merge_CONFIRMED_enrichments` |
| `Data/audit_analytics/restatements.csv` | `104_restatement_summary` |

**No v4 script reads any of the 87.** **82 of the 87 are read by nothing** in either
chain — they are legacy *outputs*, not inputs, so their degradation costs nothing except a
misleading diff.

The five that matter all feed `53`, which builds
`FINAL_DISSERTATION_DATASET_DEDUPLICATED_ENRICHED.csv` — the pre-rebuild dataset no
constants key depends on (B2). So in a clean clone, `53` would silently merge four
3-line pointer files as enrichment tables, and the damage would land in the legacy dataset
only.

---

# PART E — Assertion gaps

## E1. The assertion-free live steps, what they produce, and proposed assertions

| Step | Writes | Depends on it |
|---|---|---|
| `155_rebuild_s5_outcomes` | `stage5_outcomes.csv` | `156` → `CANONICAL_V3` → all 121 constants |
| `156_rebuild_s6_assembly` | `CANONICAL_V3.csv`, lineage header | **all 121 constants; every Essay 1/2/3 chain** |
| `157_rebuild_s7_verification` | `stage7_disclosure_date_verification.csv`, `stage7_crsp_attrition_balance.csv` | report only |
| `195_essay3_q2_classifier_v2` | `c2_filing_codes`, `c2_person_rows`, `c2_sections`, `c2_departure_events` | `199` → `202` → 94 q2 constants |
| `163_essay2_rerun_form499` | `t2_descriptives_by_treatment`, `t3_nested_models`, `t4_se_specifications`, `t7_delay_winsor` | Essay 2 appendix |
| `165_essay2_inference_ladder` | `t25_cluster_diagnostics`, `t26_inference_ladder`, `t27_required_parents` | Essay 2 appendix |

**Proposed assertion lines (NOT added).** Expected values taken from the committed ledgers,
so each is a fact the repository already asserts elsewhere:

```python
# scripts/156, after ev is assembled — the step the whole pipeline rests on
assert len(ev) == 489, f'CANONICAL_V3 must hold 489 events, got {len(ev)}'
assert int(ev['fcc_form499'].sum()) == 118, f'treated events must be 118, got {int(ev["fcc_form499"].sum())}'
assert ev['final_cik'].nunique() == 119, f'parent CIKs must be 119, got {ev["final_cik"].nunique()}'
assert int(ev['has_crsp_data'].sum()) == 354, f'CRSP-linked must be 354, got {int(ev["has_crsp_data"].sum())}'

# scripts/155, after the outcome merge
assert len(out) == 489, f'stage5 must carry 489 events, got {len(out)}'

# scripts/195, after the filing codes are written
assert len(F) == 1078, f'B1 scope is 1,078 filings, got {len(F)}'
assert F['accession'].nunique() == len(F), 'accession must be unique per filing row'

# scripts/163, after the analytical sample is cut
assert len(analytic) == 333, f'Essay 2 analytical N must be 333, got {len(analytic)}'
assert int(analytic[TREAT].sum()) == 104, f'treated events must be 104, got {int(analytic[TREAT].sum())}'

# scripts/165, against its own ladder
assert len(ladder) == 4, f'the ladder has four rungs, got {len(ladder)}'
```

`156` is the one that matters most: it is where the covariates, the disclosure-timing
recodes and the Item 5.02 outcome are assembled, it feeds every constant in the project,
and a dropped input would move a number rather than trip anything.

## E2. Ledger closure

| Ledger | Closes? |
|---|---|
| Essay 3 v4 (`outputs/essay3_v4/e_ledger.csv`) | **yes** — N monotone non-increasing at every step; treated + control = N at every populated step (asserted by `scripts/245`) |
| Essay 3 q2 (`outputs/essay3_q2/e_ledger.csv`) | **yes** — monotone |
| Essay 2 (`outputs/tables/essay2_appendix/sample_attrition.csv`) | **yes** — carries an explicit `removed` column; **0 steps fail** `prev − removed == next` |
| Essay 1 | **no such ledger exists** |

Essay 1's `appendix_v3/table_1.csv` is a **descriptives** table (`Variable, N, Mean, SD,
Median`), not an attrition ledger — its `N` column is per-variable and is not monotone, as
expected. Essay 1 has no committed step-by-step attrition ledger; the chain counts live
only in `constants_v3.json` keys and in prose. **That is a gap: Essay 1 is the only essay
whose sample construction cannot be checked arithmetically from a committed artefact.**

---

# Stage 1 close

**1. Essay 3's authoritative build, and do verdicts differ?** The repository resolves it
for **v4** — the committed directive names the defect v4 repairs (`REBUILD_V4_QUERY.md:7-14`),
`ESSAY3_V4_STATE.md:10-11` states v4 governs where it conflicts with the q2 record,
`POST_DEFENSE.md` froze v4 at a tag, and the Results section's numbers are v4's — while the
older `ESSAY3_POST_RERUN_STATE.md` still names q2, so **the conflict is real and yours to
settle**; and **no verdict differs**, with all 24 rung-window cells null in both builds, the
placebo null in both, 27 of 27 sensitivities null in both, and the T-Mobile deletion
negative at all three windows in both (only the sign-flip counts move, 1/2/1 against
3/1/1).

**2. `constants_v3.json` keys from the pre-rebuild dataset, and does that dataset differ?**
**Zero of 121** — `scripts/158` reads only `CANONICAL_V3` plus the CRSP and Fama-French
extracts, which corrects the framing in my own prior audit; and the pre-rebuild dataset
**does** differ materially from `CANONICAL_V3` (779 vs 489 rows, 292 legacy-only keys, 2
v3-only, and a different treatment column entirely — `fcc_reportable` at 139 treated
records versus `fcc_form499` at 118 treated events), so the 31 legacy-reading steps that
feed nothing are computing on a superseded sample.

**3. Appendix cells with no generator, by essay.** Essay 1: **0** — all 16 `appendix_v3`
tables regenerate from `158`, and the tombstoned legacy appendix is not cited; Essay 2:
**all 41 CSVs**, whose emitter was never committed to git at all; Essay 3: **0**, though all
58 files depend on scripts `210`–`246` that `run_all.py` does not call.

**4. LFS pointers in a clean clone, and how many are on the service?** **87 arrive as
pointers and all 87 objects are present on GitHub's LFS service** — `git lfs fetch --all`
retrieves every one, so nothing is lost; the cause is a missing `.gitattributes` rule
(`git check-attr filter` returns `unspecified` for all 87), and **only 5 of the 87 are read
by any live step**, all five feeding `scripts/53` and the pre-rebuild dataset.

**STOP — Stage 2 not begun.**

---

# PART N — read-only, run before Stage 2 (added after Tim's rulings)

**Nothing executed from `run_all.py`. Script 158 not executed. Nothing edited.**

## N1. Matcher impact on Essays 1 and 2 *(NEW — but not newly computed)*

**The work already exists and is committed.** `scripts/212_pit_linker_v4.py` takes
`--canonical` with **`CANONICAL_V3` as its default** (`212:752-753`), and the first pass of
the v4 chain runs exactly that, writing `outputs/rebuild_v4/212_links.csv` (489 rows, one
per v3 event). The v4 point-in-time linkage applied to the `CANONICAL_V3` events is
therefore a committed artefact. I did not re-run it, and I edited nothing in `155`, `156`
or `158`.

### Retention: `scripts/155` against the v4 linkage

| Group | Events | `155` linked (`has_crsp_data`) | v4 linked (`permno` present) |
|---|---|---|---|
| **Treated** | 118 | 111 / 118 = **94.1%** | 111 / 118 = **94.1%** |
| **Control** | 371 | 245 / 371 = **66.0%** | 267 / 371 = **72.0%** |
| All | 489 | 356 / 489 = 72.8% | 378 / 489 = **77.3%** |

**Treated retention does not change at all — 111 either way.** The entire effect is on the
control side: **42 control events gained, 20 control lost, net +22**. Zero treated events
gained, zero lost.

Parent CIKs: treated **13 to 13** (unchanged); control **78 to 89** (+11).

The 20 control events the v4 linkage **loses** — every one a foreign issuer, an ADR, or a
post-reorganisation entity, the cases where a point-in-time gvkey-to-CUSIP-to-permno path
with an identity gate refuses a link a current-ticker lookup accepted:

```
Aon Corporation (315293); Aon Corporation PLC and Aon PLC (1808065)
Honeywell International x3 (773840)
Paramount and Paramount Global (813828)
Carnival Corporation x2 (815097)
Essex Property Trust (920522); Nokia Inc. (924613)
The Walt Disney Company (926480); Google, Inc. (1288776)
Yahoo! Voices, Yahoo! Inc., Yahoo, Yahoo Inc. x4 (1011006)
Seagate Technology LLC (1137789); CyrusOne (1553023)
```

This is a real cost of the v4 procedure, not only a gain, and it lands entirely on
controls.

### Essay 1 and Essay 2 analysis-sample Ns — the boundary I did not cross

At the **link step**, which is the only thing the linkage changes:

```
155 linked : 356 events (treated 111 / control 245)
v4 linked  : 378 events (treated 111 / control 267)
```

**Downstream of the link I did not compute, and the reason is the instruction itself.**
Essay 1's sample requires `car_30d`; Essay 2's requires the two 21-day volatility windows.
Both are derived *from the permno*, so 42 gained and 20 lost events change which return
series are read, and re-deriving them is a market-model estimation. What can be said
without estimating: **at most 378 events could enter either essay under the v4 linkage
against 356 today, with the treated count fixed at 111.**

One incidental finding while establishing the current baseline: recomputing Essay 1's
regression sample on today's `CANONICAL_V3` gives **N = 340, treated 106 events**, against
`constants_v3.json`'s committed `N_regression = 338`. That is the **pending rebaseline
drift** already recorded, not a new discrepancy — and a further reason to hold the
rebaseline until Part N is ruled on.

## N2. Essay 2's use of the legacy dataset — all three reads are forensic

| Script | Line | File read |
|---|---|---|
| `163_essay2_rerun_form499` | **1010** | `FINAL_DISSERTATION_DATASET_ENRICHED.csv` |
| `164_essay2_rule_delay_classification` | **429** | `FINAL_DISSERTATION_DATASET_ENRICHED.csv` |
| `166_essay2_spec_grid` | **298** | `FINAL_DISSERTATION_DATASET_ENRICHED.csv` |
| `165_essay2_inference_ladder` | — | **does not read it at all** (0 occurrences) |

Each read is labelled in the code as a replication of the retired draft, not a result.
Verbatim:

`163:1007-1009`

```
# ---- FORENSIC provenance closure (NOT a candidate result) ----
log('\nFORENSIC - old-draft provenance closure (nothing here is a result; '
    'pre-dedup data, SIC-based fcc_reportable treatment, both retired):')
```

`164:426-428` — *"so the mechanism must be tested where the artifact was produced: the OLD
record-level data."*

`166:296-298` — *"Named prior specification: the draft's own published quartile
specification (the direct object of replication)"*

Columns taken from it, `163:1012-1016`: `has_crsp_data`, `fcc_reportable`,
`volatility_change`, `return_volatility_pre`, `firm_size_log`, `leverage`, `roa`,
`disclosure_delay_days`, `prior_breaches_total`, `health_breach`. `164` and `166` take only
the key triple (`org_name`, `breach_date`, `reported_date`) and join it to
`stage2_signed.csv` / `CANONICAL_V3` to locate the old records in the current chain.

**Does any of it define the sample, treatment, outcome or a cited covariate? No.**

- **Sample** — no. `163`'s canonical sample comes from `CANONICAL_V3`; the legacy read
  builds a separate frame whose stated purpose is to *"reproduce the old draft's 891
  exactly"*.
- **Treatment** — no. The legacy read uses `fcc_reportable`, the SIC-era flag, and the code
  says so: *"SIC-based fcc_reportable treatment, both retired"*. The canonical treatment is
  `fcc_form499` from `CANONICAL_V3`.
- **Outcome** — no. The legacy `volatility_change` is used only inside the forensic OLS.
- **Cited covariate** — no. The seven canonical controls come from `CANONICAL_V3`.

**This answers N2 and unblocks I2 for `163` and `165`:** no assertion need guard the legacy
frame, because nothing cited depends on it. The assertion should pin the *canonical* sample
(N = 333, treated 104 events).

## N3. The legacy-reading steps that feed something — 11, not 18

My prior audit said 18. Re-classified with the commented-step fix, it is **11**. The 18
counted every script naming a feed-target string anywhere in the file, comments included;
11 both read the legacy dataset and name a feed target.

| Script | Feeds | Does an essay cite that output? |
|---|---|---|
| `163_essay2_rerun_form499` | appendix table, ledger, constants key | **partly** — writes `outputs/tables/essay2_v2/`; the cited appendix is `essay2_appendix/` |
| `164_essay2_rule_delay_classification` | appendix table, ledger | same — `essay2_v2/` |
| `80_essay1_car_regressions` | appendix table, figure | **no** — Essay 1's cited appendix is `appendix_v3/`, written by `158` |
| `60_train_ml_model` | figure | no |
| `61_ml_validation` | figure | no |
| `96_economic_significance` | figure | no (its turnover figures are `nan` by the retirement) |
| `97_heterogeneous_mechanisms` | figure | no (Essay 3 block gated off) |
| `robustness_2_timing_thresholds` | figure | no |
| `robustness_3_sample_restrictions` | figure | no |
| `robustness_4_standard_errors` | figure | no |
| `robustness_5_fixed_effects` | figure | no |

**A finding that matters for Part L.** `163` and `164` write to
`outputs/tables/essay2_v2/` (61 files). The appendix Essay 2 actually cites is
`outputs/tables/essay2_appendix/` (41 files) — and the two directories share **zero
filenames**. The 41 cited CSVs are not stale copies of the 61 generated ones; they are a
different set entirely, with no generator. That is what the Part L tombstone must say.

`ESSAY2_APPENDIX.md:3` confirms which is cited: *"All tables from
`outputs/tables/essay2_appendix/*.csv`"*.

## Part N close

**1. Retention under the v4 linkage.** Treated retention is **unchanged at 111 of 118
events (94.1%)** for both essays, since both draw on the same link step, while control
retention rises from **245 to 267 of 371 (66.0% to 72.0%)** — net +22 from 42 gained and 20
lost, control parent CIKs 78 to 89, treated parent CIKs unchanged at 13; the downstream
analysis Ns are not reported because they require re-deriving CAR and the volatility
windows on the new permnos, which is estimation.

**2. Essay 2 and the pre-rebuild dataset.** **No** — the sample, the treatment
(`fcc_form499`, not the legacy `fcc_reportable`), the outcome and all seven cited
covariates come from `CANONICAL_V3`; the three legacy reads at `163:1010`, `164:429` and
`166:298` are each labelled in the code as a forensic replication of the retired draft, and
`165` does not read the legacy file at all.

**3. Essay 3 in `run_all.py`.** Not yet — Part N was run first as instructed, so
`run_all.py` is unchanged and still calls only the Query 2 chain. F1 begins on your word.

---

# STAGE 2 — executed 2026-09-29

Twelve commits, one per part. Neither `run_all.py` nor `scripts/158` was executed. The one
script Tim allowed, `scripts/247`, was run.

| Part | Commit | What |
|---|---|---|
| F1 | `881123b` | Query 2 retired; the 24-step v4 chain staged; 160 staged after 158 |
| G1 | `69027d5` | the 13 Essay 3 H6 keys removed from `scripts/158` |
| G2 | `7cea236` | the HC3 status label may no longer read SIGNIFICANT |
| H | `7914d97` | **28** steps retired (not 31 — see below) |
| J1 | `f5c6bca` | duplicate `98_sox404_heterogeneity` declaration removed |
| J2 | `438814f` | retired strings moved out of live script text |
| J3 | `bf57474` | six dead commented-out tuples deleted |
| I3 | `a381a0b` | the LFS filter attribute restored for all 87 pointer files |
| I1 | `dc5607f` | an executable LFS guard, before any step runs |
| F1 follow-up | `a91c5be` | the module docstring contradicted the code |
| I2 | `fd1a563` | sample-size tripwires in five steps |
| L | `9ab0ce4` | TOMBSTONE on `outputs/tables/essay2_appendix/` |
| K | `e048b97` | `scripts/247`, the Essay 1 attrition ledger |
| — | `7475aef` | the new Stage 2 documents allowlisted in the freeze gate |

## Three corrections to my own earlier work

**1. Part H is 28, not 31.** The ruling's criterion is "reads `FINAL_DISSERTATION_DATASET*`
and feeds nothing downstream". Re-tested mechanically, four entries on my Part A list fail
it. `180_essay2_elevation_calibration` and `181_essay2_spec_curve_permutation` contain **no
reference to the legacy dataset at all** — they read the *canonical* Essay 2 sample
(`t42_final_sample_with_repairs.csv`, `t1_final_sample.csv` with `assert N == 333`), and
180's docstring names its output as the source for **Table 21 Panel C**. Retiring them
would have removed live Essay 2 work. They stay live. `power_analysis_h3_h4` and
`extract_merge_fama_french` are retired but on different, stated reasons.

Criterion 2 was then re-tested for all 28 against the 77 surviving steps and 87 cited
documents: no output of any of the 28 is read or cited by anything that survives.

**2. Two of the four numbers proposed for the 156 assertion were wrong.** The distinct
parent CIK count in `CANONICAL_V3` is **162**, not 119 (14 is the *treated* parent count,
which is what the assertion now pins), and the CRSP-linked count is **356**, not 354. All
12 pinned values were recomputed from the committed outputs before being written in.

**3. `scripts/195` was not edited.** I2 named it, but it is the frozen classifier
(commit `6f7be7a`, blob `ec32364`), its identity is recorded in two handoff documents and
its EOL is pinned in `.gitattributes` so its logged sha reproduces. Editing it would
invalidate the blind validation and require a fresh round. Its assertion — 1,078 filings,
accession unique — went to `scripts/199`, the non-frozen consumer of the same table.

## Part M — whitespace-path check: nothing to fix

92 distinct files scanned (the 77 live steps plus every v4 script, 210–249) for
`find … | while read`, `xargs` without `-0`, `shell=True`, `os.system`/`os.popen`,
`shlex.split`, and `.split()` on a path-bearing variable.

**No whitespace-splitting construct exists in any live step or v4 script.** Nothing was
changed, because there is nothing to change.

448 tracked paths contain a space — 286 under `Data/Articles_Notes`, 142 under
`Data/Articles`, 20 under `Data/JSON Files`. The bug this part was written to catch was
mine, in an ad-hoc shell command during Stage 1, not in the pipeline.

## Part G3 — what the rebaseline would change (REPORT ONLY)

**No rebaseline performed. `scripts/158` was not run.** Every NEW value below is recomputed
from today's `CANONICAL_V3` using 158's own frame definitions, lifted verbatim.

Of the 15 constants that are direct counts or shares, **11 move**:

| Constant | Committed | Recomputed | |
|---|---:|---:|---|
| `events_total` | 489 | 489 | same |
| `events_crsp` | 354 | **356** | moves |
| `N_regression` | 338 | **340** | moves |
| `treated_total` | 116 | **118** | moves |
| `treated_crsp` | 109 | **111** | moves |
| `treated_regression` | 104 | **106** | moves |
| `treated_orgs_regression` | 35 | **36** | moves |
| `treated_parent_ciks_regression` | 11 | **12** | moves |
| `immediate_share_crsp` | 0.3654 | **0.3662** | moves |
| `immediate_share_regression` | 0.3639 | **0.3647** | moves |
| `immediate_share_full` | 0.3285 | 0.3285 | same |
| `prior_breach_obs_share` | 0.7599 | **0.7584** | moves |
| `health_events_crsp` | 15 | 15 | same |
| `car30d_regression_mean` | −0.1581 | **−0.2052** | moves |
| `car30d_regression_median` | 0.1911 | 0.1911 | same |

**The one to look at twice is `car30d_regression_mean`: −0.1581 to −0.2052**, a 30% change
in the mean 30-day CAR of the regression sample, from two added events. That is what a
small sample does, and it is an argument for stating the rebaseline rather than absorbing
it quietly.

**13 keys disappear** (G1): `N_essay3` = 338, and the twelve `H6_{30,90,180}d_*` values,
including the ones a reader would take as Essay 3's headline — `H6_30d_ame_pp` = 7.37
(p = .1741), `H6_90d_ame_pp` = 9.97 (p = .156), `H6_180d_ame_pp` = 4.77 (p = .4941).

**86 further keys come out of a fitted model** and would move with the sample. They are not
recomputed here: reproducing them means re-running the estimation, which is the held
rebaseline itself.

**`scripts/158` will abort, not drift.** Line 569 asserts every existing key against the
baseline and raises `ASSERTION FAILURE vs baseline` on the first mismatch. With 11
constants moving it cannot complete until the rebaseline is authorised. That is the
designed behaviour, and it is also why Essay 1 cannot currently be regenerated from a
clean clone.

## The v3 freeze gate now FAILs, and this needs Tim's decision

`scripts/210` reports **0 additions outside the allowlist** after the four new Stage 2
documents were listed. It still reports **FAIL on 13 changed files**:

`run_all.py`, `outputs/RETIREMENT_LEDGER.md`, `scripts/155`, `scripts/156`, `scripts/158`,
`scripts/163`, `scripts/165`, `scripts/199`, and `robustness_1`–`robustness_5`.

Every one is an authorised Stage 2 edit — F1, G1, G2, I2, J1, J2, J3, K — and each was
traced to its commit. But six of them are v3-chain scripts, and the prime directive is
*v3 does not change*. The rulings that authorised the edits and the freeze that forbids
them are in genuine tension, and the manifest is the record of which won.

**I did not re-create the manifest.** `210 --create` would record the new state as the
baseline and erase the evidence that these files moved. That is Tim's call, not mine.
Until it is made, 210 will FAIL on every run, including as the last step of the v4 chain
in `run_all.py`.

## STAGE 2 CLOSE — the four sentences

**1. Which Essay 3 build is in `run_all.py`, and does it assert against its own outputs?**
The v4 chain, 24 steps in `REPRODUCE_ESSAY3_V4.md` order, staged as the authoritative
Essay 3 category with the Query 2 chain relabelled RETIRED beside it, and **yes** — it
asserts at six points: 224 on its own ledger closing, 227 on every ladder value against
`constants_essay3_v4.json`, 229 on its recomputed HC3/CV1/CV3 equalling `f1_ladder.csv` at
all three windows, 242 on t and p reproducing that file within its stored precision, 243
on the control coefficients and logit AMEs, and 244 and 245 on 24 and 36 checks
respectively.

**2. Does `constants_v3.json` still hold any Essay 3 value or any path to a significance
verdict on a disqualified rung?** Not in the code: `scripts/158` no longer writes an Essay
3 key, and both `'SIGNIFICANT'` branches now read `'HC3-ONLY, NOT A VERDICT (disqualified
rung)'` — but the **file on disk still carries all 13 H6 keys**, because 158 has not been
run and must not be, so they persist until the rebaseline and should be treated as
withdrawn in the meantime.

**3. Of the 20 events the v4 linker drops, how many were correct links that v4 refused?**
**Thirteen** — Honeywell ×3, Google, Disney, Paramount ×2, Carnival ×2, Essex, Nokia,
Seagate and CyrusOne — against 7 wrong links correctly refused (Aon ×3, where permno 61735
is "AON PLC NEW", and Yahoo ×4, where permno 83435 has no CRSP name interval covering the
event date); and the mechanism matters more than the count: **not one of the 20 is an
identity-gate rejection** — `212_identity_review.csv` has 8 rows and none of these CIKs
appear — because 6 have no gvkey at all and 14 have a gvkey but no CUSIP in the committed
`comp.security` extract, so the 13 correct links were lost to **data coverage, not to the
rule**.

**4. From a fresh clone, can each essay be regenerated by `run_all.py`?**

- **Essay 1 — no.** `scripts/158` asserts every constant against `constants_v3.json` and
  11 of them have moved, so it aborts with `ASSERTION FAILURE vs baseline` before writing
  anything. `scripts/247` now states the same drift as a ledger and exits nonzero rather
  than leaving it implicit. **The blocker is the held rebaseline**, and it clears the
  moment 158 is authorised to run.
- **Essay 2 — partly.** The canonical tables (`outputs/tables/essay2_v2/`, 61 files from
  163 and 164) regenerate, and 163 and 165 now assert N = 333 / 104 treated / 82 clusters
  on write and on read. Two blockers remain: `scripts/170` reads
  `Data/wrds/crsp_quotes_topup.csv`, which is CRSP-licensed and gitignored, so it **fails
  loudly without a WRDS login** (167, the script that would pull it, is deliberately not
  staged); and the 41 CSVs in `outputs/tables/essay2_appendix/` have **no committed
  generator at all** and are now tombstoned — they cannot be regenerated by anything, at
  any time, which is why they are no longer citable.
- **Essay 3 — yes.** The v4 chain runs from committed inputs. The four steps that reach
  outside (211 and 216 for WRDS, 213 and 231 for SEC) are deliberately unstaged and their
  outputs are committed and treated as inputs. The one thing that could still break it
  silently was the LFS placeholder problem, and that is now closed twice over: I3 restored
  the attribute for all 87 files, and I1 aborts the run before step 1 if a required input
  is missing or is still pointer text.
