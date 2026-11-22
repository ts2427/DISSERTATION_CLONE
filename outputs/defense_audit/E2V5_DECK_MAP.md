# Essay 2 v5 deck map (Stage 1, read-only)

Every v5 value is read from `outputs/essay2_v5/constants_essay2.json` and the committed v5 tables at **16f9611** (verified unchanged at HEAD). Full table: `E2V5_DECK_MAP.csv`.

| status | n |
|---|---:|
| REPLACE | 28 |
| SAME | 16 |
| REWORD | 9 |
| NO-SOURCE | 4 |
| DROP | 1 |

## chain (4)

| current text | v5 | source | status | note |
|---|---|---|---|---|
| Essay 2 · Does regulated status change how long firms take to disclose, and how volatile returns are around disclosure? | unchanged wording fits v5 (delay; abnormal-return volatility around notification) | outputs/essay2_v5/constants_essay2.json primary_*; delay_* | SAME |  |

## data (6)

| current text | v5 | source | status | note |
|---|---|---|---|---|
| Essay 2: 333 events (104 treated) | 333 events (104 treated events) | outputs/essay2_v5/constants_essay2.json sample_N, sample_treated | SAME |  |
| Treated events come from 12 to 13 parent CIKs | Essay 2: 12 treated parent CIKs | outputs/essay2_v5/constants_essay2.json sample_G1 | SAME |  |

## e2q (16)

| current text | v5 | source | status | note |
|---|---|---|---|---|
| H5a · Disclosure delay | no v5 committed hypothesis label | — — | NO-SOURCE | no v5 essay draft or spine is committed; labels H5a/H5b appear nowhere in the repo (B2) |
| H5b · ... change in return volatility from [−25, −5] to [+5, +25] trading days around notification | The change in the standard deviation of daily market-adjusted abnormal returns (return minus CRSP value-weighted return) from trading days [−60, −11] to [+1, +20] around the agency reporting date does not differ between Form 499 filers and other firms. | scripts/263_e2v5_lib.py lines 48, 131, 152-163 | REWORD | outcome definition changed (benchmark, windows, coverage rule) |
| Pre-specified secondary test: Volatility elevation in the announcement window [−4, +4] | Volatility elevation [−4, +4] minus [−25, −5], now on market-adjusted abnormal returns (no market-model beta) | scripts/265_e2v5_results.py docstring A; lines 70-90 | REWORD | windows unchanged; benchmark changed from market model to market-adjusted |
| NOTES: the primary one skips the announcement days, the pre-specified one measures them | The primary post window starts at day +1, so it overlaps days +1 to +4 of the announcement window; the pre-specified test measures [−4, +4]. | scripts/263_e2v5_lib.py line 48 | REWORD | v5 primary no longer skips the announcement days |

## e2model (17)

| current text | v5 | source | status | note |
|---|---|---|---|---|
| 333 events; 104 treated (36 organizations, 12 parent CIKs); 229 control; 82 parent-CIK clusters | 333 events; 104 treated events (36 organizations, 12 parent CIKs); 229 control; 82 parent-CIK clusters | outputs/essay2_v5/constants_essay2.json; outputs/ESSAY2_SAMPLE_ATTRITION_LEDGER.md:31 sample_*; ledger line 31 (36 orgs) | SAME |  |
| ΔVol = σpost − σpre | σ = SD of daily market-adjusted abnormal returns; post [+1,+20], pre [−60,−11] | scripts/263_e2v5_lib.py lines 152-196 | REWORD | same form; σ now of abnormal returns |
| CV3 jackknife and the wild cluster bootstrap govern. HC3 is disqualified | unchanged | scripts/263_e2v5_lib.py ladder() 235-276 | SAME |  |

## e2results (18)

| current text | v5 | source | status | note |
|---|---|---|---|---|
| Volatility change: +0.21 | +0.14 | outputs/essay2_v5/constants_essay2.json primary_coef | REPLACE | daily pp |
| Volatility change: CV3 p .386 | .481 | outputs/essay2_v5/constants_essay2.json primary_p_cv3 | REPLACE |  |
| Volatility change: wild bootstrap p .333 | .426 | outputs/essay2_v5/constants_essay2.json primary_p_wcr | REPLACE |  |
| Volatility change: MDE80 0.69 (40% of baseline) | 0.55 daily pp (37% of mean pre-window SD 1.47); 8.69 annualized | outputs/essay2_v5/constants_essay2.json; outputs/essay2_v5/v5_event_panel.csv dr_mde80_daily; mean(prim_pre_sd) | REPLACE | share is DERIVED: MDE / mean pre-window SD |
| Disclosure delay: +25.5 | +29.2 days | outputs/essay2_v5/constants_essay2.json delay_raw_coef | REPLACE | only the control changed (v5 pre-window SD); scripts/271 |
| Disclosure delay: CV3 p .608 | .585 | outputs/essay2_v5/constants_essay2.json delay_raw_p_cv3 | REPLACE |  |
| Disclosure delay: wild bootstrap p .574 | .551 | outputs/essay2_v5/constants_essay2.json delay_raw_p_wcr | REPLACE |  |
| Disclosure delay: MDE80 141 days (176% of mean) | 151 days (190% of mean delay 79.8) | outputs/essay2_v5/constants_essay2.json; outputs/tables/essay2_v2/t1_final_sample.csv delay_raw_mde80; mean(disclosure_delay_days) | REPLACE | share is DERIVED |
| Delay, winsorized: +10.0 | +13.3 days | outputs/essay2_v5/constants_essay2.json delay_winsor_coef | REPLACE |  |
| Delay, winsorized: CV3 p .800 | .755 | outputs/essay2_v5/constants_essay2.json delay_winsor_p_cv3 | REPLACE |  |
| Delay, winsorized: wild bootstrap p .765 | .715 | outputs/essay2_v5/constants_essay2.json delay_winsor_p_wcr | REPLACE |  |
| Delay, winsorized: MDE80 112 days | 121 days | outputs/essay2_v5/constants_essay2.json delay_winsor_mde80 | REPLACE |  |
| H5a and H5b are not rejected | both nulls not rejected (labels have no committed source) | outputs/essay2_v5/constants_essay2.json primary_p_cv3; delay_raw_p_cv3 | NO-SOURCE | verdict SAME; label NO-SOURCE |
| The volatility coefficient is about 12% of mean pre-window volatility | about 9% of mean pre-window SD (0.1367 / 1.4717) | outputs/essay2_v5/constants_essay2.json; outputs/essay2_v5/v5_event_panel.csv primary_coef; mean(prim_pre_sd) | REPLACE | DERIVED |
| Both designs can rule out only large effects | holds (MDE80 0.55 daily pp vs SESOI 0.19; ratio 2.87) | outputs/essay2_v5/constants_essay2.json dr_mde80_daily, dr_sesoi_daily, dr_mde_over_sesoi | SAME |  |
| The earlier size gradient came from SIC-based misclassification and disappears under registry-verified treatment | Registry-verified treatment weakens the SIC-era gradient: smallest quartile +7.56 (p .009) becomes +5.15 (p .069); largest quartile -3.79 (p .015) stays; spread 11.57 -> 8.94. Counting events instead of records reverses the pattern. | outputs/essay2_v5/constants_essay2.json fp_i_industry_codes_records_*, fp_ii_form499_repaired_* | REWORD | "disappears" overstates it: attenuated, not removed (appendix Table 5) |

## e2announce (19)

| current text | v5 | source | status | note |
|---|---|---|---|---|
| +0.47 daily pp | +0.43 daily pp | outputs/essay2_v5/constants_essay2.json ann_coef | REPLACE | market-adjusted basis |
| CV3 p = .021 | .027 | outputs/essay2_v5/constants_essay2.json ann_p_cv3 | REPLACE |  |
| wild bootstrap p = .006 | .009 | outputs/essay2_v5/constants_essay2.json ann_p_wcr | REPLACE |  |
| CV1 p = .004 | .008 | outputs/essay2_v5/v5_t09b_announcement_ladder.csv rung CV1 parent filer entity | REPLACE |  |
| N = 331 (G = 81, 12 treated parent CIKs) | N = 333 (G = 82, 12 treated parent CIKs) | outputs/essay2_v5/constants_essay2.json ann_N, ann_G, ann_G1 | REPLACE | no events drop on the v5 basis |
| Pre-specified on 8/31, before estimation, and added after earlier nulls were known | v5 code labels the test "exploratory" (v5_t09 row "Form 499 on breach elevation (exploratory)"; relabelled 2026-11-22); the 8/31 date has no v5 source | outputs/essay2_v5/v5_t09_announcement.csv row 4 label | NO-SOURCE | 8/31 appears only in scripts/175 docstring (115a72f); see B11 |
| Survives Benjamini-Hochberg adjustment within its four-test family | survives: BH-adjusted p 0.036 (family of 4, all p read live in scripts/265) | outputs/essay2_v5/constants_essay2.json ann_bh_adj_p, ann_bh_reject | SAME |  |
| The primary windows skip days [−4, +4]: the effect appears at announcement and is gone by the post window | The primary post window starts at +1. The elevation does not carry into the 20-day post window (primary +0.14, CV3 p .481) or into [+1,+5] (+0.20, CV3 p .320). | outputs/essay2_v5/constants_essay2.json primary_*, dyn_1_5_* | REWORD | v5 primary windows no longer skip [−4,+4] |
| NOTES: Two control events drop from 333 (Uber, Zscaler) for lack of pre-event return history | no event drops: the v5 elevation is market-adjusted and needs no estimation window (N = 333) | outputs/essay2_v5/constants_essay2.json ann_N | DROP |  |

## e2measure (20)

| current text | v5 | source | status | note |
|---|---|---|---|---|
| 117 of 333 events show zero delay | 117 of 333 (42 treated, 75 control events) | outputs/essay2_v5/constants_essay2.json delay_zero_events/_treated/_control | SAME |  |
| 112 of those are same-date records | no v5 output | — — | NO-SOURCE | only in TIMING_MEASUREMENT_REPORT.md (defense era, no committed generator) |
| Two records carry the breach date in the notification field (Sprint 2019, Roku 2023) | unchanged (frozen sample) | docs/claude/KNOWN_LIMITATIONS.md lines 189-190 | SAME | documentation, not a v5 output |
| the volatility measures, anchored on notification, do not depend on breach dates | holds for v5 (anchor = reporting date) | scripts/264_e2v5_primary.py outcome(date_col="rdt") | SAME |  |

## e2take (21)

| current text | v5 | source | status | note |
|---|---|---|---|---|
| Regulated status does not change when firms disclose; ... more volatility at the announcement, gone within a week | holds on v5: delay CV3 p .585; announcement +0.43 (CV3 p .027); [+1,+5] +0.20 (p .320) | outputs/essay2_v5/constants_essay2.json delay_raw_p_cv3, ann_*, dyn_1_5_* | SAME |  |
| Correct treatment classification removes the effects that SIC codes produced | Correct treatment classification weakens the SIC-era gradient (smallest-quartile effect loses significance; spread narrows), and counting events reverses it | outputs/essay2_v5/constants_essay2.json fp_i_*, fp_ii_*, fp_iii_*, fp_iv_* | REWORD | see e2results row |

## story (29)

| current text | v5 | source | status | note |
|---|---|---|---|---|
| No difference in delay. More volatility at announcement, gone within a week. | holds on v5 (see e2take) | outputs/essay2_v5/constants_essay2.json delay_raw_p_cv3, ann_*, dyn_1_5_* | SAME |  |

## measure (30)

| current text | v5 | source | status | note |
|---|---|---|---|---|
| Registry-verified Form 499 treatment removes the SIC-era effects | weakens (see e2results REWORD) | outputs/essay2_v5/constants_essay2.json fp_i_*, fp_ii_* | REWORD |  |
| Every number in this defense regenerates from a clean clone ... at the defense-final tag | false for Essay 2 v5: v5 is not at defense-final and scripts 262-272 are not run_all.py steps | run_all.py no 262-273 entries | REWORD | C1 |

## limits (31)

| current text | v5 | source | status | note |
|---|---|---|---|---|
| 12 to 13 treated parent CIKs | Essay 2: 12 | outputs/essay2_v5/constants_essay2.json sample_G1 | SAME |  |

## be2 (B5)

| current text | v5 | source | status | note |
|---|---|---|---|---|
| HC3 (disqualified): volatility change p | .231 | outputs/essay2_v5/constants_essay2.json primary_p_hc3 | REPLACE |  |
| CV1 parent CIK, t(81): volatility change p | .398 | outputs/essay2_v5/constants_essay2.json primary_p_cv1 | REPLACE |  |
| CV3 jackknife, t(81): volatility change p | .481 | outputs/essay2_v5/constants_essay2.json primary_p_cv3 | REPLACE |  |
| Wild cluster bootstrap (B = 99,999): volatility change p | .426 | outputs/essay2_v5/constants_essay2.json primary_p_wcr | REPLACE |  |
| HC3 (disqualified): delay (raw) p | .397 | outputs/essay2_v5/v5_t17_delay.csv delay (raw days) / v5 control, rung HC3 | REPLACE |  |
| CV1 parent CIK, t(81): delay (raw) p | .487 | outputs/essay2_v5/v5_t17_delay.csv delay (raw days) / v5 control, rung CV1 parent filer entity | REPLACE |  |
| CV3 jackknife, t(81): delay (raw) p | .585 | outputs/essay2_v5/v5_t17_delay.csv delay (raw days) / v5 control, rung CV3 cluster jackknife (PRIMARY) | REPLACE |  |
| Wild cluster bootstrap (B = 99,999): delay (raw) p | .551 | outputs/essay2_v5/constants_essay2.json delay_raw_p_wcr | REPLACE |  |
| Volatility change +0.21 daily pp, CV3 95% CI [−0.27, 0.70] | +0.14 daily pp, CV3 95% CI [-0.25, 0.52] | outputs/essay2_v5/constants_essay2.json primary_coef, primary_ci95_* | REPLACE |  |
| Delay +25.5 days, CV3 95% CI [−73.1, 124.1] | +29.2 days, CV3 95% CI [-76.9, 135.4] | outputs/essay2_v5/constants_essay2.json; outputs/essay2_v5/v5_t17_delay.csv delay_raw_coef; CV3 row ci_lo/ci_hi | REPLACE |  |
| N = 333; G = 82; 12 treated parent CIKs | N = 333; G = 82; 12 treated parent CIKs | outputs/essay2_v5/constants_essay2.json primary_N, primary_G, primary_G1 | SAME |  |
| B = 99,999 | B = 99,999 | outputs/essay2_v5/v5_t03_ladder.csv rung WCR restricted Rademacher (B=99,999) | SAME |  |

## blimits (B8)

| current text | v5 | source | status | note |
|---|---|---|---|---|
| One firm split across clusters (Aon): Essay 2: 82 → 81 if merged | unchanged (same frozen 333-event sample) | docs/claude/KNOWN_LIMITATIONS.md lines 199-218 | SAME | documentation, not a v5 output |

# Part B: facts

All values are from `outputs/essay2_v5/constants_essay2.json` at 16f9611 unless stated otherwise.

**B1 Sample**
- **Volatility model:** N 333, 104 treated events, 229 control, 36 treated organizations, 12 treated parent CIKs (the same as parent filer entities, `final_cik`), G 82, G* 23.4 (`primary_G_star`).
- **Announcement model:** N 333, 104 treated events, G 82, 12 treated parent CIKs (`ann_N`, `ann_G`, `ann_G1`).
  - **No events drop.** The v5 elevation is market-adjusted and needs no estimation window. The defense-era 331 had excluded Uber and Zscaler for lacking market-model beta history.
  - **G\* for the announcement model:** NO-SOURCE (not emitted).
- **Attrition ledger:** unchanged. v5 uses the frozen 333 (scripts/263:60-67 asserts it), and appendix Table 1 (scripts/269) reproduces `outputs/ESSAY2_SAMPLE_ATTRITION_LEDGER.md` exactly.

**B2 Hypotheses: NO-SOURCE**
- No v5 essay draft or spine is committed; the only hits from `git ls-files` are appendix CSVs.
- The labels H5a and H5b appear nowhere in the repo.
- The v5 code names the outcomes, not the hypotheses.

**B3 Definitions**
- **Volatility:** abnormal return = r − vwretd on the same calendar day (263:131). The SD uses ddof = 1 and is multiplied by 100, giving daily percentage points (263:163). Annualized values (× √252) are used only for MDE and SESOI.
- **Windows:** [−60,−11] and [+1,+20] (263:48), on the CRSP market calendar. Day 0 is the nearest market trading day to the reporting date, and the stock must trade within ±7 calendar days (263:109-122).
- **Coverage:** each window needs at least ceil(0.8 × length) non-missing abnormal returns (263:152-163). 0 of 333 events drop (v5_t01:2).
- **Announcement:** the SD of market-adjusted abnormal returns over [−4,+4] minus the SD over [−25,−5]. Controls are the baseline SD plus the six standard controls; inference is CV3 (scripts/265 docstring A; lines 70-90).
- **Delay:** calendar days from breach to reporting date (156:110-131; 163:505-507; 271).
  - Below −30 days is set to missing; −30 to −1 is set to 0.
  - Winsorized at P99 = 784.96.
  - Log version: log1p.
- **Spreads (268):**
  - CPQS = (ask − bid)/mid.
  - EDGE comes from `bidask.edge` on OHLC prices.
  - OCAM = \|C − O\|/O ÷ dollar volume, winsorized 1/99, then logged.
  - Each spread is post minus pre over the same windows. The model uses the M4 controls plus reporting-month fixed effects, with CV3.

**B4 Estimates** (HC3 is the disqualified rung)

| outcome | coef (units) | HC3 p | CV1 p | CV3 p | WCR p | CV3 95% CI | MDE80 | share |
|---|---|---|---|---|---|---|---|---|
| volatility change | +0.1367 daily pp | .231 | .398 | .481 | .426 | [−0.248, 0.521] | 0.548 daily pp (8.69 annualized) | MDE = 37% of mean pre-window SD 1.47 (DERIVED); coef = 9% |
| announcement elevation | +0.4327 daily pp | .0023 | .0081 | .0271 | .0093 | [0.050, 0.815] | NO-SOURCE | NO-SOURCE |
| delay, raw | +29.2 days | .397 | .487 | .585 | .551 | [−76.9, 135.4] | 151 days | 190% of mean delay 79.8 (DERIVED) |
| delay, winsorized | +13.3 days | .587 | .679 | .755 | .715 | [−71.3, 97.9] | 121 days | 163% of mean winsorized delay 74.1 (DERIVED) |
| delay, log | −0.107 log points | .769 | .831 | .873 | .845 | [−1.435, 1.222] | 1.89 log points | — |
| CPQS change | +0.00001 | NO-SOURCE | .715 | .779 | NO-SOURCE | in v5_t16 | NO-SOURCE | — |
| EDGE change | +0.0035 | NO-SOURCE | .310 | .485 | NO-SOURCE | in v5_t16 | NO-SOURCE | — |
| log-OCAM change | +0.037 | NO-SOURCE | .696 | .794 | NO-SOURCE | in v5_t16 | NO-SOURCE | — |

Sources:
- Volatility: `primary_*`, `dr_*`, v5_t03.
- Announcement: v5_t09b (all eight rungs).
- Delay: v5_t17, v5-control rows.
- Spreads: v5_t16 and `spread_*`. Spreads ran with CV1 and CV3 only (scripts/268 calls `ladder(full=False)`), so no HC3, WCR or MDE is emitted.

**B5 Equivalence**
- **Bounds:** ±SESOI = ±0.25 × the control group's SD of the outcome = ±0.1907 daily pp (3.03 annualized). Key `dr_sesoi_daily`, defined at 263:348,352.
- **TOST:** lower p .0470, upper p .3902 (`dr_tost_p_lower` / `dr_tost_p_upper`, 263:368-369). Both confirmed.
- **When the bound was set:**
  - The rule (a quarter of the control SD) was first committed in scripts/165, **115a72f, 2026-09-02**.
  - The v5 implementation and the first v5 estimates were committed together, **21cfbbb, 2026-11-07**.
  - So the rule predates v5 by two months, but its value is computed from v5 data in the same run.
- **Second bound** (the converted announcement-return bound, ±2.10 pp annualized): TOST p .084 / .509 (`tost_car_p_lower` / `tost_car_p_upper`).

**B6 Power framing**
- Treated parents needed to detect 5 pp: **55** (`dr_required_parents_5pp_ann`). The defense era gave 157.
- Formula (263:354-361):
  - σc = SE_CV3 / √(1/G1 + 1/Gc).
  - Find the smallest k with (t.975 + t.80, df = k + Gc − 1) × σc × √(1/k + 1/Gc) ≤ 5/√252.
  - Gc is held fixed at 70.
- Floor: 3.29 annualized (`dr_floor_ann`).

**B7 Benjamini-Hochberg** (announcement family of 4; v5_t09 rows 1-4)

| member | raw p | inference | BH-adjusted p |
|---|---|---|---|
| earnings elevation | <.0001 | CV1 by security | <.0001 |
| breach elevation | .0523 | CV1 by parent | .0523 |
| breach − earnings contrast | <.0001 | CV1 by security | <.0001 |
| Form 499 on elevation | .0271 | CV3 | .0361 (`ann_bh_adj_p`; rejects) |

All four p-values are computed live in scripts/265: `e_m` (line 118), `b_m` (119), the contrast (122) and `r_new` (86). BH runs at line 136. There are no typed constants.

**B8 Sprint influence**
- "Removes 79%" is `sprint_share_removed` = 0.789 = 1 − (M4 volatility-change coefficient with parent CIK 101830, Sprint's 9 events, deleted ÷ the full coefficient) = 1 − 0.0289 / 0.1367 (265:361-365).
- It concerns the primary volatility coefficient, not the announcement test.
- Announcement coefficient and CV3 p without Sprint, and without T-Mobile: NO-SOURCE (no committed v5 output).

**B9 Leave-one-parent-out** (v5_t14b, volatility model)
- **Range:** 0.0289 (dropping Sprint) to 0.2113 (dropping AT&T) across the 12 treated-parent deletions; 0.0289 to 0.2132 across all 82 deletions (the overall maximum is Intuit, a control parent).
- **Sign:** no deletion flips the sign.
- **Verdicts:** per-deletion p-values are not emitted, so any verdict change is NO-SOURCE.
- **Announcement leave-one-parent-out:** NO-SOURCE.

**B10 Contamination** (v5_t06b, corrected in 16f9611)

Share of events whose [−250,−30] estimation window contains **another** canonical event at the same parent:

| definition | treated | control | pooled |
|---|---|---|---|
| by breach date | 58.7% | 58.5% | 58.6% |
| by notification date | 40.4% | 44.1% | 42.9% |

No deck slide carries the old 71% / 76%.

**B11 Status of the announcement test**
- **Committed v5 text:** "exploratory" (relabelled 2026-11-22). It appears in the v5_t09 row label ("Form 499 on breach elevation (exploratory)") and in the scripts/265 docstring ("BH within the exploratory family of four").
- **Not in any committed v5 file:** "secondary" (nor "exploratory" until the 2026-11-22 relabel). The defense-era ruling calling it a "pre-specified SECONDARY result" is not in a committed file, and the essay draft is not committed.

# Part C: reproducibility

**C1: No.**
- run_all.py has no entry for scripts 262-273.
- No live step writes any file in `outputs/essay2_v5/` (all ~95 committed v5 outputs) or in `outputs/defense_audit/`.
- So slide B9 / measure's claim that "every number regenerates from a clean clone … at the defense-final tag" is false for Essay 2 v5.

**C2: uncommitted working-tree changes** (present before this session; untouched)
- `scripts/252_defsup_deck_exhibits.py` (+137): adds an Essay 3 exhibit section — the randomization-inference p on the CV3 t beside the coefficient version, the 2018 placebo flag, and the appendix crosswalk — with assertions against the committed E3 outputs.
- `outputs/defense_supplement/deck_exhibits.csv` (+67 rows): those new E3 exhibit rows (e.g. `w30_all_parents_ri_p_cv3_t` 0.8803).
- `deck_exhibits.json` (+555 lines): the same rows in JSON.
- None of these changes any Essay 2 value.
