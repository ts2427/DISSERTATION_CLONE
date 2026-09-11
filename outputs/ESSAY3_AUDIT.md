# Essay 3 Audit (Query 5 Part E, computed live)

==========================================================================================
ESSAY 3 AUDIT — computed 2026-08-30 (scripts/168)
==========================================================================================

## E1 — Data vintage
CURRENT CANONICAL: H6 IS in constants_v3.json / CONSTANTS_BLOCK_V3.md
(committed, v3 chain, scripts/158): N_essay3 = 338; AME 30/90/180d =
+7.37/+9.97/+4.77pp, p = 0.174/0.156/0.494, MDE80 = 15.2/19.7/19.5pp, base
rates 17.2%/43.2%/69.8%.
COMMITTED LEGACY OUTPUTS ARE A DIFFERENT VINTAGE (or a different essay):
- outputs/essay3/tables/regression_full_output.txt (tracked, Jan 22 2026)
  contains OLS regressions of VOLATILITY_CHANGE (N=534) — Essay-2-style
  information-asymmetry content from when Essay 3 was a different topic.
  It is not Essay 3's current H6 analysis at all.
- outputs/tables/essay3_governance/*.csv (tracked) carry the 7/28 audit
  chain (e.g. ols_lpm_h6_results.csv: 30d FCC +0.0091pp p=.828 — the
  pre-rebuild N=646-era LPM), not v3.
- outputs/essay3_figures, outputs/essay3_revised: pre-audit era.
VERDICT: the v3 numbers exist and are committed via constants_v3; every
OTHER committed Essay 3 artifact is stale vintage or off-topic.

## E2 — Does the prose match the code? (ESSAY3_METHODS_SECTION_CORRECTED
.docx.txt and ESSAY3_RESULTS_AND_APPENDIX.md vs scripts/154-158)

| # | Prose claim | Code reality (v3) | Verdict |
|---|---|---|---|
| 1 | DV = CEO turnover from BoardEx succession records cross-referenced with SEC filings | ANY 8-K listing Item 5.02 (any director/officer departure, election, OR compensation event) within (breach, +Nd], from live EDGAR submissions (scripts/156). NO BoardEx data exists anywhere in the repository | **PROSE DESCRIBES A DV THAT WAS NEVER COMPUTED** |
| 2 | Windows measured "following public disclosure"; t=0 = breach discovery date | Windows anchored on BREACH date (bdt < filing <= bdt+Nd), not disclosure | MISMATCH (anchor) |
| 3 | Treatment = fcc_reportable from SIC 4810 x FCC dockets | fcc_form499 from the Form 499 registry snapshot, date-valid (scripts/154) | STALE — SIC-era prose |
| 4 | Rule: "effective September 28, 2007", "notification to customers and the FCC ... typically within 7 business days" | 47 CFR 64.2011, effective Dec 8 2007; 7-business-day clock runs to USSS/FBI; public disclosure EMBARGOED; no customer deadline | **WRONG DATE + WRONG RULE CHARACTERIZATION** |
| 5 | Sample chain 1,054 -> 784 -> 769 -> 718 -> 651 (PRC 2005-2017) | v3: 1,054 records -> 758 -> 524 -> 489 events -> N_essay3 = 338 (2006-2024) | STALE — pre-rebuild chain |
| 6 | Turnover rates 37.9/58.2/59.1%% (N=651); formal tables say 46.4/66.9/67.5%% (N=896) | v3 base rates 17.2/43.2/69.8%% (N=338). The 46%%-class rates are the retired ANY-8-K era (scripts/46 pre-7/24 bug); the essay's own files disagree with each other (651 vs 896 vs 926) | **THREE INCONSISTENT VINTAGES INSIDE THE ESSAY'S OWN MATERIALS** |
| 7 | Firm size = log MARKET CAP from CRSP at announcement | firm_size_log = ln(TOTAL ASSETS), Compustat prior FY (scripts/156) | MISMATCH (variable construction) |
| 8 | Inference: robust SEs clustered at INDUSTRY level | scripts/158: plain MLE logit (no clustering), AME | MISMATCH (inference) |
| 9 | Mediation with bootstrap (1,000 iter), indirect effects | Not in the v3 chain (old scripts 91/91m, retired base) | NOT IMPLEMENTED in canonical code |
| 10 | Kamiya-style inclusion: external malicious action only, excluding negligence | No breach-type restriction anywhere in the v3 chain | PROSE CLAIMS A SCREEN THE CODE NEVER RAN |
| 11 | "Primary Causal Identification (SCM n=41 FCC firms): -4.03%%, p=.003" | SCM deleted as broken (provenance corrected 7/28); n=41/-4.03%% figures are known-stale SIC-era | **RETIRED RESULT STILL HEADLINING THE METHODS FILE** |
| 12 | TOST vs +/-10pp bound, "PASSES equivalence" all windows | The +/-10pp equivalence claim was retired 7/28 (it FAILS under the methods-stated 95%% convention on its own stored inputs — old-vs-new exhibit); v3 MDEs are 15-20pp, H6 status null-unbounded/inconclusive | **RETIRED CLAIM; v3 says INCONCLUSIVE, not equivalent** |
| 13 | "immediate disclosure" significant NEGATIVE predictor (-0.650, p=.002) | Pre-rebuild 651-era estimate; not a v3 result; v3 stores no such coefficient. Also predates the 8/17 delay fixes | UNVERIFIED/STALE — must be re-estimated before any use |

## E3 — Internal reconciliation of the prose-reported coefficients
  30d FCC: z=coef/se=+0.531 -> implied p=0.5951 vs reported 0.595 -> RECONCILES
  90d FCC: z=coef/se=+0.024 -> implied p=0.9805 vs reported 0.982 -> RECONCILES
  180d FCC: z=coef/se=-0.298 -> implied p=0.7660 vs reported 0.768 -> RECONCILES
  30d immediate: z=coef/se=-3.066 -> implied p=0.0022 vs reported 0.002 -> RECONCILES
  Constant-ratio test (reported-implied-z / computed-z): [np.float64(1.0), np.float64(0.925), np.float64(0.991), np.float64(1.008)] — all ~1.0; NO 0.8806-style pathology. The Essay 3 prose numbers are internally coherent; the problem is VINTAGE and DV mislabeling, not table assembly.

## E5 — N chain (v3, closes by construction)
  489 events -> 354 CRSP -> 338 covariate-complete (Essay 3 sample; treated 104 / 35 orgs / 11 parent CIKs). Matches N_essay3=338: True. The prose chains (651, 896, 926) trace to retired vintages and do not close against any committed artifact.

## E6 — Variable provenance
Canonical sources identified for every v3 variable (scripts/154-156).
UNIDENTIFIABLE-SOURCE variables appearing in prose only: BoardEx CEO
succession records (no such data in repo); "governance weakness score" and
"weak governance indicator" (old scripts 102/106-era constructs, source
columns absent from CANONICAL_V3); SCM donor weights (deleted).

## E7 — Purge-list content in Essay 3 local files
  ESSAY3_COMPLETION_STATUS.txt: ['651']
  ESSAY3_FORMAL_TABLES.txt: ['651', '896', '926', 'causal identification']
  ESSAY3_H6_APPENDIX.md: ['651']
  ESSAY3_H6_APPENDIX_COMPLETE.md: ['651']
  ESSAY3_INTRODUCTION_FINAL.txt: ['September 28']
  ESSAY3_LITERATURE_REVIEW.docx.txt: ['651', 'exogenous']
  ESSAY3_METHODS_SECTION.docx.txt: ['natural experiment']
  ESSAY3_METHODS_SECTION_CORRECTED.docx.txt: ['651', 'September 28', 'exogenous']
  ESSAY3_RESULTS_AND_APPENDIX.md: ['37\\.3', '651', 'September 28']
  ESSAY3_VISUALIZATION_GUIDE.txt: ['896', '926']
  ESSAY3_COMPLETION_STATUS.txt: ['651']
  ESSAY3_FORMAL_TABLES.txt: ['651', '896', '926', 'causal identification']
  ESSAY3_H6_APPENDIX.md: ['651']
  ESSAY3_H6_APPENDIX_COMPLETE.md: ['651']
  ESSAY3_INTRODUCTION_FINAL.txt: ['September 28']
  ESSAY3_LITERATURE_REVIEW.docx.txt: ['651', 'exogenous']
  ESSAY3_METHODS_SECTION.docx.txt: ['natural experiment']
  ESSAY3_METHODS_SECTION_CORRECTED.docx.txt: ['651', 'September 28', 'exogenous']
  ESSAY3_RESULTS_AND_APPENDIX.md: ['37\\.3', '651', 'September 28']
  ESSAY3_VISUALIZATION_GUIDE.txt: ['896', '926']
  (Every hit above is pre-rebuild content: wrong rule/date, retired sample sizes, or causal-identification language that the zero-treated-pre-rule design cannot support.)

## E8 — Scope estimate
The empirical core is ALREADY REGENERATED on v3 (H6 logits + AME + MDE in
scripts/158, committed constants). What Essay 3 needs is what Essay 2 just
got:
  1. An Essay-3 ground-truth script (163-equivalent): sample ledger,
     descriptives, logit + LPM, parent-CIK-clustered inference ladder,
     TOST at a defensible bound, reconciliation assertions, exhibit CSVs.
     Machinery is directly reusable from scripts 163-166.  ~1-2 sessions.
  2. Decisions Tim must make: (a) DV honesty — rename/redefine the outcome
     as "any Item 5.02 governance-disclosure event" (what the code
     computes) or fund a real CEO-turnover coding (the 5.02 calibration
     package from 8/5 was built for exactly this); (b) mediation — retire
     or rebuild on v3 with the fixed delay variable; (c) SCM — drop
     (already deleted) and purge from prose.
  3. Prose rewrite: methods section is unusable as-is (items 1-13 above);
     results section numbers all replaced by v3 values.  Writing time, not
     computation.
COMPATIBLE WITH A DECEMBER DEFENSE: yes on the empirics — the v3 numbers
exist today; the binding constraint is prose rewriting and the DV-naming
decision, not computation.
