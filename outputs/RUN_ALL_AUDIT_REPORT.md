# Run-All Audit: Does `run_all.py` Regenerate Every Number the Defense Will Show?

**Static audit. `run_all.py` was NOT executed. Script 158 was NOT executed.** Nothing was
edited. Every count below comes from reading `run_all.py`, the scripts it names, and the
committed artefacts. Tracking status: this file is untracked until you say to commit
(`.gitignore:79` is `*.md`, so it needs `git add -f`).

**One methodological note that changes several counts.** `run_all.py` declares steps as
`('scripts/NNN_x.py', 'label')` tuples, and fourteen of them are **commented out** rather
than deleted. A naive grep counts those as live. Every "called / not called" verdict below
distinguishes a live tuple from a commented one, and I state which.

- **95** step tuples in the file
- **81** live
- **14** commented out (retired in place)
- **0** live steps whose script file is missing

---

# PART C — What should no longer be called

## C1. The good news first: the legacy Essay 3 chain is genuinely out

All twelve scripts the `RETIREMENT_LEDGER.md` says were removed are **commented out, not
live**:

| Script | Live? | In `RETIREMENT_LEDGER.md`? |
|---|---|---|
| `91_essay3_governance_regressions` | no (never a tuple) | yes |
| `91b_essay3_reduced_form_mediation` | no | yes |
| `91c_essay3_mediation_bootstrap` | no | yes |
| `91e_essay3_h6_tost_equivalence` | no | yes |
| `91f_essay3_h6_firm_size_heterogeneity` | no | yes |
| `91g_extract_reduced_form_controls` | no | yes |
| `91h_essay3_cox_hazards` | no | yes |
| `91j_essay3_ols_lpm_and_negbin` | no | yes |
| `91k_essay3_robustness_checks` | no | yes |
| `91m_essay3_h6_form499_corrected` | **commented out, L450** | yes |
| `91_essay3_mediation_analysis` | **commented out, L540** | yes |
| `102_extended_governance_windows` | **commented out, L528** | yes |

`91m` is **out of `critical_keys`**, with the reason recorded inline at `run_all.py:783`:
`] # 91m removed from critical_keys 2026-09-11 (Essay 3 Query 2 Part H)`. The TOST label
is withdrawn in a comment at `run_all.py:480`: *"The TOST description 'confirms FCC effect
is economically negligible' is withdrawn."* Neither string reaches a live label.

`96`'s hardcoded turnover constant is **neutralised, not merely commented**
(`scripts/96_economic_significance.py:168`):

```python
turnover_prob_increase = float('nan')  # RETIRED: was 0.053 (no computed source)
```

`97`'s Essay 3 block is gated off at `scripts/97_heterogeneous_mechanisms.py:292`
(`RETIRED_ESSAY3 = True`, with the loop running over an empty list at `:298`).

## C2. Six commented-out steps name scripts that **no longer exist on disk**

Not a live failure — `run_all.py:600` skips a missing script — but five of the six are
**not in the retirement ledger**, so the record does not explain where they went:

| Script | In ledger? |
|---|---|
| `scripts/141_essay1_appendix_tables_form499.py` | yes |
| `scripts/142_sample_attrition_ledger.py` | **NO** |
| `scripts/83_fcc_causal_identification.py` | **NO** |
| `scripts/create_parallel_trends_figure.py` | **NO** |
| `scripts/create_balance_test_table.py` | **NO** |
| `scripts/94_falsification_tests.py` | **NO** |

`scripts/141` and `142` are gone **and** `outputs/tables/appendix_v2/` is **empty (0
files)**, so the 7/28-vintage outputs are no longer present to be mis-cited. The only
script still naming that directory is `161_old_vs_new_exhibit.py`, which is **not live**.

## C3. Purge-list strings still reachable by a LIVE step

Separating detectors from contamination matters here: most hits are in the *checks*
(`217`'s test fixtures, `240`'s lint rules, `168`'s audit patterns), which must contain the
banned strings to test for them. Excluding those, **seven hits in six live scripts**:

| String | Live script | Lines |
|---|---|---|
| `Rule 37.3` | `scripts/163_essay2_rerun_form499.py` | 232, 861, 1044, 1089 |
| `September 28, 2007` | `scripts/163_essay2_rerun_form499.py` | 232, 1044 |
| `1,054 breaches` | `scripts/robustness_1_alternative_windows.py` | 7 |
| `1,054 breaches` | `scripts/robustness_2_timing_thresholds.py` | 7 |
| `1,054 breaches` | `scripts/robustness_3_sample_restrictions.py` | 10 |
| `1,054 breaches` | `scripts/robustness_4_standard_errors.py` | 12 |
| `1,054 breaches` | `scripts/robustness_5_fixed_effects.py` | 9 |

**All seven are in docstrings or log lines, not in emitted values**, and `163`'s four are
*disclaimers* — `163:232` reads `lg2('there is no September 28, 2007 date and no "Rule
37.3").')`. The five `robustness_*` hits are docstring provenance lines describing the
input file as "1,054 breaches", which is the phrasing the purge list forbids because those
are notification records, not breaches. Low severity, but they are in live scripts and
they do print to logs.

`BoardEx`: **0 hits in any live script.** Only in `91i`/`91k` (not called) and in the
three detectors.

`14.52` / `16.71` / `15.05`: **0 hits in any live script.** `14.52` survives in
`create_essay3_appendix_docx.py:197,211` and `create_essay3_appendix_sequential.py:183,193`
— both **not called**, both already marked retired in the ledger.

## C4. `158`'s Essay 2 volatility block can still print "SIGNIFICANT" from a disqualified specification

Quoted verbatim, `scripts/158_rebuild_s8_regenerate.py:113-125`:

```python
# ---------------- Essay 2: H5 ----------------
reg2 = crsp.dropna(subset=['volatility_change', 'return_volatility_pre'] + CONTROLS).copy()
X2 = sm.add_constant(reg2[CONTROLS + ['return_volatility_pre']].astype(float))
m2 = sm.OLS(reg2['volatility_change'], X2).fit(cov_type='HC3')
b, se, p = m2.params[TREAT], m2.bse[TREAT], m2.pvalues[TREAT]
dof2 = int(m2.df_resid)
tost2 = max(1 - stats.t.cdf((b + EQ) / se, dof2), stats.t.cdf((b - EQ) / se, dof2))
C['N_essay2'] = len(reg2)
C['H5_coef'] = round(b, 4)
C['H5_p'] = round(p, 4)
C['H5_tost_p'] = round(tost2, 4)
C['H5_mde80'] = round(2.8 * se, 4)
C['H5_status'] = 'BOUNDED NULL' if tost2 < .05 else ('NULL-INCONCLUSIVE' if p > .05 else 'SIGNIFICANT')
```

`cov_type='HC3'` — and `run_all.py:77-78` states in its own docstring that *"HC3 is
reported for comparison only and is DISQUALIFIED as a significance test."* The `'SIGNIFICANT'`
branch at `:125` is therefore reachable from a specification the project has disqualified,
and the same pattern appears at `:91` for the Essay 1 hypothesis labels. No CV3 or
bootstrap rung appears anywhere in `158`.

This is the most consequential Part C finding: it is not a retired script still being
called, it is a **live script that can emit a significance verdict on a disqualified
standard error**, and its output is the assertion baseline the whole v3 chain compares
against.

## C5. `create_defense_qa_guide.py` and `create_parallel_trends_figure.py`

- `create_defense_qa_guide.py` — **on disk, not called.** Contains `September 28, 2007` at
  line 5, in a sentence describing the error.
- `create_parallel_trends_figure.py` — **commented out at L495 and the file is deleted.**
  Not in the retirement ledger.

---

# PART B — Orphans and hardcodes

## B1. `constants_v3.json` — 121 keys

Nine scripts name the file. Only **four are live**: `158` (the writer), `163`, `199`, `202`.
The other five name it to *read or assert against* it, and are **not called**:
`161`, `168`, `183`, `186`, `193`.

- **Sole writer: `scripts/158_rebuild_s8_regenerate.py`**, which **is** live (L385).
- **77 of 121** keys are assigned by a literal `C['key']` in that writer.
- **44 of 121** are built dynamically in f-string loops (`C[f'H6_{w}d_ame_pp']`,
  `C[f'{lab}_status']`), so they are still written by `158` but cannot be traced to a
  literal assignment by grep. **None is orphaned; none is hardcoded.**

**Every key in `constants_v3.json` traces to `158`, which `run_all.py` calls.** The file is
reproducible in principle — but see Part E: `158` is frozen pending the rebaseline
(`outputs/PENDING_REBASELINE.md`), so the committed file and a fresh run are known to
disagree.

## B2. `constants_essay3_q2.json` — 94 keys

- Two scripts name it: `202` (the writer, **live**, L394) and `239` (**not live**).
- **All 94 keys are built dynamically** — `C.update({f'F1_{w}_{k}': v ...})` — so zero
  literal assignments. All 94 are written by `202`. **None orphaned, none hardcoded.**

## B3. The finding that matters more than either count

**`constants_essay3_v4.json` — the file Query 3 established as authoritative for Essay 3 —
has NO writer in `run_all.py` at all.**

| Constants file | Keys | Writer | Writer live in `run_all.py`? |
|---|---|---|---|
| `constants_v3.json` | 121 | `158` | yes |
| `constants_essay3_q2.json` | 94 | `202` | yes |
| **`constants_essay3_v4.json`** | **94** | **`227`** | **NO** |

`F1_30_coef` is `0.0168` in the Query 2 file and **`0.004`** in the v4 file. `run_all.py`
regenerates the first and cannot regenerate the second. Every Essay 3 number in the
current Results section and the rendered appendix comes from the v4 build.

## B4. Appendix tables, ledgers and figures

| Directory | Files | Writers | Live writers |
|---|---|---|---|
| `outputs/rebuild/appendix_v3/` (Essay 1, 16 tables) | 16 | 1 | **1** |
| `outputs/tables/appendix_v2/` (Essay 1, 7/28 vintage) | **0** | 1 | 0 |
| `outputs/tables/essay2_appendix/` (Essay 2, 41 CSVs) | 41 | 1 | **0** |
| `outputs/essay3_q2/` (Essay 3 Query 2) | 124 | 30 | 8 |
| `outputs/essay3_v4/` (Essay 3 v4, **authoritative**) | 53 | 22 | **0** |
| `outputs/essay3_appendix/` (rendered appendix) | 5 | 3 | **0** |

Three whole directories of committed artefacts have **no live writer**:

- **`outputs/tables/essay2_appendix/` — 41 CSVs, no generator at all.** `run_all.py:87-88`
  admits this in its own docstring: *"have NO committed generator. scripts/178 only renders
  them."* These are committed artefacts, not reproducible output.
- **`outputs/essay3_v4/` — 53 files.** The v4 chain (210–246) is entirely absent from
  `run_all.py`.
- **`outputs/essay3_appendix/` — the rendered appendix.** `245` and `246` are not called.

## B5. T-Mobile exhibits

| File | Writer | Live? |
|---|---|---|
| `outputs/essay3_q2/tmobile_timeline.csv` | `203` | **yes** |
| `outputs/essay3_v4/228_case.log` | `228` | no |
| `outputs/essay3_q3/tmobile_case.csv` | `242` | no |
| `outputs/essay3_q4/table11.csv` | `244` | no |
| `outputs/essay3_q4/tmobile_502_text.md` | `245` | no |

Only the Query 2 timeline regenerates. The four exhibits the appendix actually uses do not.

---

# PART E — Reproducibility and silent degradation

## E1. Inputs absent or degraded in a clean clone

**19 tracked files are LFS pointers on disk right now**, in this working tree, not merely
in a fresh clone — all of them `Data/JSON Files/nvdcve-2.0-YYYY.json` (2007–2025), at
136–137 bytes each. They lack the `filter=lfs` attribute, so git reports no difference and
the smudge never runs.

Consumers: `scripts/99_cvss_complexity_heterogeneity.py` (**live**, L524 — but commented
out), plus `01`, `02`, `03`, `06` (not live). So the NVD degradation currently reaches no
live step, because `99_cvss` is commented out. The CVE columns in the master dataset were
built when the files were real.

Other non-reproducible inputs, all declared in `run_all.py:82-96`:

| Input | Status | Consuming step |
|---|---|---|
| `Data/wrds/crsp_quotes_topup.csv` | **gitignored** (`.gitignore:153`), present locally only | `167` (not staged), `170` (**live**, fails loudly) |
| `Data/wrds/q6_*.csv`, `crsp_daily_topup_dish.csv` | committed; one-time licensed pulls | `173`, `179` — must NOT be re-run |
| `Data/edgar/*` caches, `Data/wrds_v4/*` | committed (LFS, real) | v4 chain — **not in run_all** |

## E2. Does `run_all.py` fail loudly on an LFS pointer? **No.**

`grep -n "git-lfs" run_all.py` returns exactly two hits, both in the **docstring**
(`run_all.py:83-86`), which describes the hazard in prose:

> *"a clean clone writes small placeholder files with NO error … A placeholder begins
> `version https://git-lfs.github.com/spec/v1`."*

There is **no executable check**. `grep -rln "version https://git-lfs" scripts/*.py`
returns **nothing** — no script guards either. A pointer file is read by pandas as a
3-line CSV or fails on a JSON parse, and the failure mode depends entirely on the
consumer.

**Proposed guard (NOT added):** in `run_all.py`, before the category loop, walk every path
the steps declare as input and abort if the first 40 bytes of any file match
`version https://git-lfs`. It belongs in `run_all.py` rather than in each script, because
the property being checked — "the clone is complete" — is a property of the run, not of any
one step. A per-file allowlist would be needed for the deliberately-gitignored WRDS
extracts so the guard does not fire on a known-absent licensed input.

## E3. Attrition assertions: five live steps have none

| Live step | `assert` statements |
|---|---|
| `150_rebuild_s2_entity_resolution` | 2 |
| `151_rebuild_gate1_apply` | 2 |
| `152_rebuild_s3_dedup` | 1 |
| `153_rebuild_gate2_apply` | 2 |
| `154_rebuild_s4_treatment` | 2 |
| **`155_rebuild_s5_outcomes`** | **0** |
| **`156_rebuild_s6_assembly`** | **0** |
| **`157_rebuild_s7_verification`** | **0** |
| `158_rebuild_s8_regenerate` | 1 (the constants baseline) |
| `187_essay3_q2_fetch_502_text` | 1 (the draw is fixed) |
| **`195_essay3_q2_classifier_v2`** | **0** |
| `199_essay3_q2_sample_e` | 2 |
| `202_essay3_q2_estimation` | 1 (the constants baseline) |
| `204_essay3_q2_se_diagnostics` | 2 |
| **`163_essay2_rerun_form499`** | **0** |
| **`165_essay2_inference_ladder`** | **0** |

`156` is the one that matters most: it is where the covariates, the disclosure-timing
recodes and the Item 5.02 outcome are assembled, and a dropped input would move a number
rather than trip an assertion. `163` is Essay 2's ground truth and has none either.

## E4. `.gitignore` rules that can hide a needed input

Four rules are broad enough to hide an input, and the precedent (31 Essay 3 filing texts
hidden by `*.txt`) is exactly this failure:

| Line | Rule | Risk |
|---|---|---|
| 22 | `Data/processed/*.xlsx` | would hide `master_breach_dataset.xlsx`, the PRC extract the whole chain reads. Currently tracked, so force-added at some point — but a fresh copy would be silently dropped. |
| 26 | `Data/JSON\ Files/*.json` | the NVD files. Tracked, and simultaneously ignored. |
| 79 | `*.md` | every report and ledger needs `git add -f` |
| 84 | `*.txt` | the precedent rule; `!Data/edgar/item5_02_text/**` at line 87 is the fix for Essay 3 only |
| 153 | `Data/wrds/crsp_quotes_topup.csv` | deliberate (CRSP licence), but makes `170` unreproducible |

---

# PART A — What `run_all.py` calls

## A1. The 81 live steps, in order

Grouped as `run_all.py` groups them. Essay attribution is by the sample the script reads:
**L** = pre-rebuild `FINAL_DISSERTATION_DATASET*`, **V3** = `CANONICAL_V3`.

| # | Line | Script | Essay | Sample |
|---|---|---|---|---|
| 1 | 362 | `46_executive_changes_item5_02_with_cache` | shared (feeds 53) | L |
| 2 | 368 | `53_merge_CONFIRMED_enrichments` | shared | L |
| 3 | 369 | `99_add_cpni_hhi_variables` | 1 | L |
| 4 | 370 | `98_sox404_heterogeneity` | 1 | L |
| 5–14 | 376–385 | `150`,`151`,`152`,`153`,`154`,`159`,`155`,`156`,`157`,`158` | shared rebuild | V3 |
| 15–22 | 391–398 | `187`,`195`,`199`,`202`,`190`,`191`,`203`,`204` | 3 (Query 2) | V3 |
| 23–36 | 409–422 | `163`,`164`,`165`,`166`,`169`,`170`,`171`,`175`,`176`,`177`,`180`,`181`,`174`,`182` | 2 | mixed L/V3 |
| 37–40 | 438–441 | `121a`,`121b`,`121c`,`122` | shared (Form 499) | L |
| 41–42 | 447–448 | `86c`,`90b` | 1, 2 | L |
| 43–44 | 459–460 | `143`,`144` | 1 | L |
| 45–56 | 466–477 | `70`,`80`,`h1_timing_fcc_interaction`,`82`,`90`,`86` | 1, 2 | L |
| 57 | 487 | `scm_mahalanobis_distance` | 1 | L |
| 58–81 | 502–575 | `00`,`99_firm_fixed_effects`,`60`,`61`,`96`,`97`,`98`,`100`,`101`,`103`,`104`,`106`, `91_essay3_mediation`(#), `92`,`93`,`95`, `robustness_1..5`, `power_analysis_h3_h4`, `overlap_audit`, `corrected_longrun_car`, `calendar_month`, `extract_merge_fama_french`, `sample_composition`, `ff3_simple_merge`, `factor_model_carhart_ff5`, `extended_bhar_60d_90d`, `defense_prep_all_tasks` | 1 / shared | L |

**49 of the 81 live steps read the pre-rebuild `FINAL_DISSERTATION_DATASET*`; 15 read
`CANONICAL_V3`.** That is the central structural fact: the majority of the pipeline still
runs on the sample the v3 rebuild replaced.

## A2. Steps that feed no constants file, ledger, appendix or figure

**32 of 81 live steps** name no constants file, no ledger, no appendix path and no figure
output. They are candidates for removal, listed in full:

`46`, `99_add_cpni_hhi_variables`, `98_sox404_heterogeneity` (twice — declared at both L370
and L521), `180`, `181`, `70`, `h1_timing_fcc_interaction`, `82`, `90`, `86`,
`scm_mahalanobis_distance`, `00`, `99_firm_fixed_effects_analysis`, `100`, `101`, `103`,
`104`, `106`, `92_heterogeneity_analysis`, `93`, `95`, `robustness_1`, `power_analysis_h3_h4`,
`overlap_audit_fcc_clustering`, `corrected_longrun_car_clustering`,
`calendar_month_clustering_60_90`, `extract_merge_fama_french`,
`sample_composition_diagnostic`, `ff3_simple_merge`, `factor_model_carhart_ff5`,
`extended_bhar_60d_90d`.

`98_sox404_heterogeneity` is declared **twice** (L370 and L521) and runs twice per pipeline.

---

# PART D — Essay 3 chain

## D1. The Query 2 chain is called in order, with assertions

`run_all.py:391-398`, in its own category *"ESSAY 3 — QUERY 2 CHAIN (executive departure;
CURRENT, 2026-09-11; results in a separate constants file)"*:

```
187 -> 195 -> 199 -> 202 -> 190 -> 191 -> 203 -> 204
```

Chain order is correct. The assertion lines, verbatim:

```
187:175   assert prior == ids, f'{fn}: rerun draw differs from the fixed draw — STOP'
199:189   assert not bad, 'helper does not reproduce scripts/195 — STOP'
199:337   assert len(A2) == LED.iloc[-1]['N']
202:322   assert not mism, f'ASSERTION FAILURE vs Essay 3 baseline: {list(mism.items())[:5]}'
204:81    assert round(full[s], 4) == round(c[s], 4), f'{w}d {s}: recomputed {full[s]:.4f} != committed {c[s]:.4f}'
204:82    assert round(full['coef'], 4) == round(c['coef'], 4)
```

`199:337` is the ledger-closure assertion, and `204:81-82` independently recompute the SEs
and compare to the committed values. **`195` has no assertion** (E3).

## D2. `run_all.py` DOES write Essay 3 values into `constants_v3.json` — 13 of them

This is the check that fails. `scripts/158_rebuild_s8_regenerate.py:132-144`:

```python
C['N_essay3'] = len(reg3)
...
    C[f'H6_{w}d_base_rate'] = round(yv.mean(), 4)
    C[f'H6_{w}d_ame_pp'] = round(row['dy/dx'] * 100, 2)
    C[f'H6_{w}d_p'] = round(row['Pr(>|z|)'], 4)
    C[f'H6_{w}d_mde80_pp'] = round(2.8 * row['Std. Err.'] * 100, 2)
```

Present in the committed `outputs/rebuild/constants_v3.json`:

```
H6_30d_ame_pp   7.37    H6_30d_p   0.1741   H6_30d_base_rate  0.1716   H6_30d_mde80_pp  15.19
H6_90d_ame_pp   9.97    H6_90d_p   0.1560   H6_90d_base_rate  0.4320   H6_90d_mde80_pp  19.67
H6_180d_ame_pp  4.77    H6_180d_p  0.4941   H6_180d_base_rate 0.6982   H6_180d_mde80_pp 19.51
N_essay3        338
```

These are the **legacy any-Item-5.02 outcome** on the 338-event sample — the outcome the
retirement ledger retired and Query 1 found the prose never computed. They sit in the same
file as the Essay 1 and 2 constants, under H6 key names, with no marker distinguishing them
from a current result. A reader taking "H6" from `constants_v3.json` gets the retired
figure, not the v4 result.

---

# PART F — Defense exhibits

## F1. No such script exists.

The three candidates:

| Script | Called? | Reads the constants files? |
|---|---|---|
| `defense_prep_all_tasks.py` | **live** (L575) | **no** — reads `FINAL_DISSERTATION_DATASET_DEDUPLICATED_ENRICHED.csv` (`:23`) |
| `create_defense_qa_guide.py` | not called | no |
| `rerun_defense_prep_on_648.py` | not called | no (the name carries the retired 648 chain) |

`grep -c "constants_v3.json|constants_essay3" scripts/defense_prep_all_tasks.py` returns
**0**. The one live defense script computes from the pre-rebuild dataset, so the exhibits
it produces are on the superseded sample.

**Proposed `scripts/NNN_defense_exhibits.py` (NOT written).** Shape, in one paragraph so
you can judge it before I build anything: read **only** `constants_v3.json`,
`constants_essay3_v4.json`, `e_ledger.csv` and the committed appendix CSVs — no dataset, no
model, no estimation; emit `outputs/defense/` with one CSV per slide and a
`provenance.csv` mapping every cell to its source key; assert that every value it prints is
present in a constants file rather than computed, so the script cannot become a second
estimation path. It should take the **v4** Essay 3 constants, not the `H6_*` keys in
`constants_v3.json`, and it should refuse to run if the two disagree on a shared key.

---

# Close

**1. Orphaned or hardcoded constants.** **Zero of 215** — every key in `constants_v3.json`
(121) and `constants_essay3_q2.json` (94) is written by a script `run_all.py` calls (`158`
and `202` respectively), with 121 assigned literally and 94 built in f-string loops. But
the count flatters the situation: the authoritative Essay 3 constants file,
`constants_essay3_v4.json` (94 keys), has **no writer in `run_all.py` at all**, so the
honest figure is **94 of 309 Essay-relevant constants unreachable** by the pipeline.

**2. Retired things still reached.** **Zero retired scripts are live** — all twelve legacy
Essay 3 scripts are commented out, `91m` is out of `critical_keys`, and the "economically
negligible" label is withdrawn. But `run_all.py` still reaches **seven purge-list strings in
six live scripts** (`Rule 37.3` and `September 28, 2007` in `163`, all as disclaimers;
`1,054 breaches` in the five `robustness_*` docstrings), **13 retired Essay 3 H6 values that
`158` writes into `constants_v3.json`**, and one live code path — `158:125` — that can label
a result `SIGNIFICANT` on an HC3 standard error the project's own docstring calls
disqualified.

**3. Can each essay be regenerated from a clean clone today?**
**Essay 1 — no.** `158` is frozen pending the rebaseline, so its constants assertion is
known to fail (354→356, 338→340, 116→118); `outputs/tables/appendix_v2/` is empty and its
builders `141`/`142` are deleted.
**Essay 2 — no.** The 41-CSV appendix has no generator at all, and `170` cannot run without
the gitignored CRSP quotes extract.
**Essay 3 — no, and for the sharpest reason.** The Query 2 chain in `run_all.py` does
regenerate `constants_essay3_q2.json`, but that is **not the authoritative build**: the v4
chain (210–246) that produces every current Essay 3 number, table and appendix figure is
absent from `run_all.py` entirely.
