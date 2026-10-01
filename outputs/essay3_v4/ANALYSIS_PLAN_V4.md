# Essay 3 Query 2 — v4 analysis plan

Pre-specified. Committed **before** `scripts/227_essay3_v4_estimation.py` is run on the
v4 sample, so git history fixes the order. **No specification change is permitted after
this commit.** Everything below is read off the frozen code (`scripts/227`, copied from
v3's `scripts/202` with data sources moved and no method changed), not chosen now.

## Sample

`outputs/essay3_v4/e_analysis_sample.csv`, `in_analysis_sample == 1`.

| step | N | treated | control |
|---|---:|---:|---:|
| CANONICAL_V4 | 489 | 118 | 371 |
| CRSP linked (v4) | 414 | 111 | 303 |
| Compustat covariates (size, leverage, ROA) | 412 | 109 | 303 |
| **Fully observed outcome window (censoring rule)** | **412** | **109** | **303** |
| Outcome-data requirement (≥1 8-K in window, outcome CIK) | 412 | 109 | 303 |
| Prior 12-month market-adjusted return (≥150 daily returns) | **405** | **109** | **296** |

**Censoring rule (pre-specified):** restrict to events whose 180-day outcome window is
fully observed — the outcome CIK was still filing at the window end. On this data it
removes **0** events. The margin is reported rather than the bare zero: minimum slack
**26 days** (NextGen Healthcare, 2023-03-29), median **2,718 days**.

The 2 treated events lost at the Compustat step are **T-Mobile, CIK 1283699,
2013-11-01 and 2013-11-26**. Cause: the first `comp.funda` fiscal year under gvkey
`017874` is 2013-12-31, after both breach dates, so nothing falls in the 550-day
prior-fiscal-year window. This is a data fact, not a rule change.

## Primary specification (F1) — unchanged from v3

Linear probability model, one row per event, outcome `exec_departure_{30,90,180}_rd`:

```
exec_departure_{w}_rd ~ fcc_form499 + prior_breaches_1yr + health_breach
                      + firm_size_log + leverage + roa
                      + baseline_exec_rate_py_rd + prior12m_mktadj_ret_rd
```

Anchor: `reported_date`. Treatment: `fcc_form499`. Windows: 30, 90, 180 days.

## Inference ladder — CV3 and WCR govern; HC3 is disqualified

Clustering on **parent CIK**. Reported: HC3; CV1; **CV3** (cluster jackknife) with
t(G−1); **restricted wild cluster bootstrap** (Rademacher, B = 99,999 for p, CI by
inversion at B = 9,999). Diagnostics: G, G1, G\* (Carter–Schnepel–Steigerwald on
treatment partial leverage), cluster-size CV. Logit AME (cluster-robust) as
corroboration only.

**HC3 is DISQUALIFIED**: it ignores within-parent clustering and is anticonservative
here. It is printed for completeness and must never be read as significance. The
inferential frame is **CV3 and WCR**.

**MDE80** = (t₍.975₎ + t₍.80₎) at df = G−1, times the CV3 SE. Reported against the
control base rate.

## Sensitivities (F3) — 9 rows per window × 3 windows = 27

Per window, with CV3 inference and WCR p at B = 9,999:

1. year FE (reported year)
2. two-digit SIC FE (cell composition reported in `f3_sic2_cells.csv`)
3. breach_date anchor
4. excluding pre-announced departures
5. excluding the F2 baseline control
6. restatement-dated outcome
7. recall-corrected, audit point estimates
8. recall-corrected, treated recall at CI low / control at CI high — **bounding
   exercise, not an estimate**
9. recall-corrected, treated recall at CI high / control at CI low — **bounding
   exercise, not an estimate**

**Recall input — a declared adaptation.** v4 has no recall audit of its own (that would
require a fresh hand-coded audit sheet). The recall-correction rows therefore use v3's
measured recall, `outputs/essay3_q2/d3_audit_recall_by_stratum.csv`, row
`exec departure (A)` / `PRIMARY (verified)`: treated 0.8421 [0.604, 0.966], control
0.7500 [0.476, 0.927]. The justification is that `scripts/220` is byte-identical to v3's
`scripts/195`, so measured recall is a property of the frozen classifier. The limitation
is that it was measured on v3-era documents and is assumed to transfer. This is recorded
here, before estimation, so it cannot be presented later as anything but an assumption.

**Plus, reported but NOT counted as tests:** leave-one-parent-CIK-out (range, sign
flips, and the T-Mobile and Sprint deletions named explicitly).

## Additional analyses

- **F4 placebo:** the primary specification with exec departure in (t0 − 180d, t0].
- **F2:** baseline departure-rate distribution, treated vs control.
- **F5 CEO-only:** counts by group; LPM (CV3) estimated **only** where both groups have
  ≥ 10 events. If that gate fails the specification is not estimated, and its absence is
  the result — not a reason to relax the gate.
- **F6 director-only:** counts.
- **v3-overlap sensitivity (new in v4):** the full v4 primary specification re-estimated
  on the v4 sample with the control group restricted to events also linked in v3, all
  treated kept. Reported side by side with the full v4 result. This exists because every
  v4 linkage gain fell on the control side, so the gain and the estimate must be
  separable.

## Multiplicity — Benjamini–Hochberg within family, on CV3 p-values

| family | tests |
|---|---:|
| primary H6 | 3 (one per window) |
| placebo | 1 |
| sensitivities | 27 (9 × 3 windows; includes the 2 bounding rows per window) |
| CEO-only | 0–3, conditional on the ≥10-per-group gate |
| **total** | **31–34** |

Not counted, and declared descriptive: logit AMEs (3), the F2 distribution, F5/F6
counts, leave-one-out.

## Verdict rules, fixed now

- The primary verdict at each window is read from **CV3 and WCR**, never HC3.
- A result is called **NULL** where the CV3 interval contains zero; direction and MDE80
  are reported alongside so an underpowered null is not read as an absence of effect.
- The two recall corner rows bound how far misclassification could move the estimate.
  They are not estimates and are labelled as such in `f3_sensitivities.csv`.
- No result in this round may retune the classifier, the reference codes, or the v3-era
  draws. All are frozen.
