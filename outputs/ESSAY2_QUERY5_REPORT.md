# Essay 2 — Query 5 umbrella report (2026-08-30)

Artifacts (all live-computed by committed code): `ESSAY3_AUDIT.md` (scripts/168), `ESSAY2_QUERY5_PART_S.md` (169), `ESSAY2_QUERY5_PART_HA.md` (170), figures `fig_C3_spec_curve.png` / `fig_C4_power_curve.png` (171), consolidated runner `scripts/172_essay2_run_all.py`, `ESSAY2_MECHANICAL_RULES.md`, CSVs t37–t45.

## Part E — Essay 3 audit (schedule verdict: HOLDS, with conditions)

The v3 empirical core exists and is committed (H6 in constants_v3: AME +7.4/+10.0/+4.8pp, p=.17/.16/.49, MDE 15–20pp, N=338 ✓ recomputed). Everything else fails the audit: the methods prose describes **a DV that was never computed** (BoardEx CEO turnover vs. the code's any-8-K-Item-5.02 flag, breach-anchored not disclosure-anchored), SIC-based treatment, September 28 2007 + a 7-day customer/FCC notification claim, a Kamiya-style screen never run, the deleted SCM as "primary causal identification," the retired ±10pp equivalence PASSES, and **three mutually inconsistent sample vintages inside its own materials** (651 / 896 / 926; the committed `outputs/essay3/` folder even contains Essay-2-style volatility regressions). The one clean finding: the prose numbers reconcile internally (every reported p follows from coef/SE; constant-ratio ≈ 1.0 — no 0.8806 pathology). Correction scope: ~1–2 sessions of computation (163-style ground-truth script; machinery reusable) + Tim's three decisions (DV naming/honesty, mediation retire-or-rebuild, SCM purge) + prose rewrite. **Compatible with a December defense on the empirics.**

## Part S — Specification repairs (the null survives all of them, and gets cleaner)

- **S1** Abnormal-volatility DV (market-model residual, beta on [−250,−46]), market-volatility-change control, event-year FE, two-way cluster (parent × event-month): **+0.086, 95% CI [−0.284, +0.455]** — null. The market-volatility control **loads** (+0.19, SE 0.07): the raw DV was regime-contaminated, the repair was needed, and the internal inconsistency with the month-FE microstructure spec is resolved. Crisis-exclusion (drop 2008-09, 2020): +0.061 — stable, disclosed. Raw-DV robustness row retained (Dai et al. citation).
- **S2** Distant baselines [−120,−60]: +0.065; [−250,−50]: +0.077 vs adjacent +0.086 — **STABLE (within 2 SE), in the main table. The leakage objection closes; the "leakage biases toward zero, so the nulls are conservative" sentence is now licensed as a finding, not an assertion.**
- **S3** ANCOVA identity footnoted (pre-vol coefficient never interpreted); split-sample IV (instrument = [−120,−60] volatility; first-stage t²≈F large) leaves the treatment coefficient in place; DV skewness/kurtosis reported.
- **S4** Log variance ratio: +0.018, CI [−0.37, +0.41] — same story; level results are not outlier-driven.
- **S5** Lineage purged: Ohlson–Penman variance-change design; the Beaver/Patell U tests the announcement window and is stated as not the right test.

## Part H1 — Intent-scope restriction (attenuation is not hiding an effect)

Treated vectors: HACK 58, INSD 21, PHYS 12, PORT 5, combos 4, DISC 2 (legacy codes only — the 36-subtype schema is absent; theft vs loss inseparable, checked and stated). STRICT scope (HACK/INSD/CARD): 83 treated / 31 orgs / **11 parents**, coef +0.143 (CI [−0.30, +0.59], MDE80 0.63); LENIENT (+PHYS/PORT/STAT): 100 treated, +0.145. All three channels null on both restricted sets. ITT-vs-effective framing with Aigner/Bound/Mahajan in place; CPNI hand-coding stated as not attempted (no field approximation offered).

## Part A — Equivalence bounds (the honest answer changed)

Half-tick SESOI at the sample median price ($75.52): one tick = 1.32bp, SESOI = **0.66bp**. THE ONE-SENTENCE ANSWER: **under the stronger derivation, CPQS does NOT bound and neither does volatility — every outcome is INCONCLUSIVE at its derived SESOI.** CPQS misses narrowly: its equivalence CI (smallest concludable bound, Hartman–Hidalgo) is **1.03bp — it would bound at one full tick but not at the half-tick** (MDE/SESOI 1.43). Volatility: equivalence CI 0.485 daily pp vs quarter-SD 0.274 and Wellek 0.395 (MDE/SESOI 2.04). EDGE is far too noisy for spread-granularity bounds (MDE/SESOI 125 — stated). log-OCAM at ±10%: inconclusive (MDE/SESOI 2.74). A3 statement corrected everywhere (two one-sided tests; intersection–union; never "because the test is one-sided").

## Parts H4/H6/P/B3/H3

- **H4** Treated events cluster in calendar time (χ²(17)=57.9) — year FE/two-way clustering is the structural fix; Kolari–Pynnönen distinguished (pooled-CAR tests, not cross-sectional regressions). Same-firm window-overlap rate is **49.2%** (event trains at T-Mobile/AT&T); rule: both kept; drop-overlaps sensitivity −0.091 (null, N=167).
- **H6** The valid positive control (earnings announcements through the identical pipeline) is **specified and blocked on a one-line RDQ pull** — the substitute I first ran (breach announcement window) tests the breach effect itself and is reported as descriptive only: breach notifications produce **no announcement-window volatility elevation** (−0.091 daily pp, p=.071), consistent with the CAR nulls. **Placebo-treatment diagnostic (10,000 parent-level reassignments): rejection rate 12.1% at α=.05 — the analytic CV1 SEs are too small, which is itself a finding**: it says the calibrated rungs of the ladder are CV3/WCR (p≈.48–.50), exactly as MNW predict for this configuration. Framed as an SE diagnostic, not a p-value (exchangeability false; Eggers–Tunón–Dafoe).
- **P** Provenance: product name/version/download date are NOT recorded in the repo — must be supplied. The 2019 frame break shows **no fall** in treated share (20.9% → 27.0%, p=.12): the H5 selection mechanism leaves no visible mark in treated representation (reported as-is). PRC's own dedup and completeness caveats quoted; Edwards et al. cited with the open reporting-rate question.
- **B3** Dropped-vs-retained: size balanced (std diff −0.03); dropped events have higher pre-vol (−0.40) — attrition is mildly volatility-selective, stated.
- **H3** Balance table with both denominators stated, variance ratios, G₁=11 on the face, no p-values: size std-diff **1.51** (Imbens-2015 denominator) — overlap is poor and said so; no matching (reasoned paragraph with citations); common-support re-estimate (+0.078, N=326) reported as a **change of estimand**.

## Part C exhibits

t45 misclassified-organization exhibit is the persuasion centerpiece: **Aero Charter (air charter), WillScot Mobile Mini (modular offices), and Impact Mobile Home Communities all carry SIC 4833 — television broadcasting** — legacy name-pattern coding assigned communications codes to whatever contained "Charter" or "Mobile"; the two "ATT-SecurityBreach" rows are malformed records treated as firms; Johnson Matthey (2834) and Suddenlink (6500) show the old flag wasn't even consistent with its own SIC column. Spec-curve and power-curve figures rendered (fig_C3, fig_C4); four-panel, ladder, year table, DV correlations already exist as CSVs; sample-vs-population comparison remains open (flagged).

## Part D — SEC 2023 discussion corrections (text, applied to the record)

DOJ delay-mechanism claim DELETED (two issuers, three determinations — no usable variation). "Tractable setting" softened to "a larger population with its own identification problems" (≈29 Item 1.05 filings strict / 9–12 material / ~74 pooled — no better than 11; Gerding-statement regime break mid-window; retrieve the Debevoise primary before citing any count). The 4.5-business-day median timing figure noted for the timing essay.

## Part F — Essay 1 consistency

Deadline-language locations: the t24 scan (executed below). Hypothesis logic: **none of H1–H4 requires the deadline reading for measurement**; H1/H2's hypothesis-development prose leans on "compliance with the 7-day disclosure requirement" and must be rewritten to the floor/embargo mechanism — prose fix, not respecification. **The bigger consistency issue found: Essay 1's car_30d is breach-anchored** — the same construct-validity analysis that disqualified Essay 2's old DV applies (a majority of the CAR window's days precede public notification for the median event). A notification-anchored CAR sensitivity is ~1 session of work reusing the 163 machinery, and should be run before the defense. H1-scope (entity-vs-event) and H5-selection (severity truncation) apply to Essay 1 equally: limitations text plus optional re-runs (~half session each). Retired: `outputs/ESSAY1_APPENDIX_TABLES.md`, scripts 141/142 + appendix_v2 CSVs + `sample_attrition_ledger.csv` (run_all entries commented with dated notes).

## Part G — Hygiene executed

README lines 15/82/153 corrected (Rule 37.3/Sept-28/30-day claims deleted, v3-correct text in place); both dashboard banners fixed; `create_parallel_trends_figure.py` **deleted**; `create_defense_qa_guide.py` **stubbed** (raises on import); scripts 83/94, build_essay1_*, create_balance_test_table, create_conceptual_models retired (git history preserves); `Data/wrds/crsp_quotes_topup.csv` added to .gitignore with the pull recipe. **Licensing flag for Tim's decision: the committed CRSP/Compustat extracts (crsp_daily_returns.csv 44MB etc.) are WRDS-licensed and generally may not be redistributed — a repo shared with a committee is redistribution; either confirm the repo stays private-and-permitted or replace the extracts with the pull recipe (do not want to delete committed data unilaterally).** Consolidated runner `scripts/172_essay2_run_all.py`; mechanical rules documented in `ESSAY2_MECHANICAL_RULES.md`.

## Literature actions

Obaydin 4.2pp already deleted (Query 4). To cite and position: Viancourt (2026, ICS) — distinguished on classification/event-construction; Amani–Magnan–Moldovan (2025) review — position against it; Ashraf–Sunder fn.25 as motivation. Bangalore (2026 SSRN) noted with its quality flags — its filing-count discrepancy is a live illustration of the classification-unreliability thesis. DPRG 27(1):37 requires library retrieval (not accessible from here). FCC CPNI setting confirmed unoccupied — novelty claim safe.

## Test count and multiplicity

New hypothesis tests this query: **25** — Part S main family 7, H4 2, H6 1 (descriptive announcement check), P 1, H3 1 (common support), H1 family 9, A family 4 (TOST). Benjamini–Hochberg at FDR 5% within families: **one rejection — the H4 calendar-clustering χ² (p<.0001)**, a design diagnostic that motivates the year-FE repair, not a treatment finding. Cumulative across Queries 4–5: 56 tests; treatment-effect rejections: **zero, anywhere, under any calibrated procedure.** The placebo diagnostic (12.1% rejection rate) is reported as an SE-calibration finding, not a test.

Standing-rule check: nothing changed the headline — every repair, restriction, and re-basing left the null in place, and S2's stability licenses the leakage-conservative sentence. The two flags raised mid-work (invalid positive-control substitute; CV1 anti-conservatism) are reported above, unsoftened.
