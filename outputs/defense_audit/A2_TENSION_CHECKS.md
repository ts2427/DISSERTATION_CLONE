# Defense audit: A2 tension checks

The deck text is not in the repo yet; the claims checked are the ones quoted in the audit brief.

## Checks 1, 2, 5, 6

**A2-1. "65 of 66 steps succeed"**
- **At `defense-final` (902a8ea):** run_all.py has **66** live step tuples. That is 65 distinct scripts, because 212 runs twice as PASS 1 and PASS 2 (run_all.py:674, 684).
- **Declared skip:** script 170 is the one declared skip (REVIEWER_GUIDE.md:26, 32-34: "66 steps", "the one declared skip: step 170"). So "65 of 66" is **MATCH for `defense-final`**.
- **On current `main` (e25cf88):** there are **70** live tuples. 255, 256, 257 and 258 were added after `defense-final` (c298475 10/04, cf1feeb 10/05, 38af08b 10/06). None of the v5 scripts is a live step.

**A2-2. "All 99 analytic values match"**
- **Current r_replication/VERIFICATION.md (c298475, 2026-10-04):**
  - **143 of 143** analytic values (line 9);
  - 8 of 8 Essay 1 90% CIs (line 10);
  - **12 of 12 bootstrap p-values** (restricted wild cluster), within a Monte Carlo tolerance of 3·√(p(1−p)/B) (line 11).
- **"99 of 99" is the earlier version** (1566d02, the same day). So the deck's 99 is **STALE**: the current figure is 143.
- **Stochastic values:** 12 bootstrap p-values, all 12 compared. The randomization-inference values (scripts/250) are **not** in the R replication (0 compared; no randomization-inference rows in VERIFICATION.md or README.md).

**A2-5. "T-Mobile alone carries 26 of Essay 3's 109 treated events"**
- **MATCH.** Counted from outputs/essay3_v4/e_analysis_sample.csv with `in_analysis_sample == 1`, after asserting N = 405, 109 treated, G = 119 and 13 treated parent CIKs. CIK 1283699 carries 26 treated events (26 events in all).
- **Next largest:** AT&T 24, Sprint 12, Verizon 10, Comcast 9.

**A2-6. "Pre-specified on 8/31, before estimation, and added after earlier nulls were known"**
- **Source of the 8/31 date:** the scripts/175 docstring, line 4 ("Tim's 8/31 rescoping decision"), and 175:53-56. Repeated in ESSAY2_QUERY7_REPORT.md:35 and ESSAY2_ANNOUNCEMENT_CONTRAST.md:19.
- **First commit:** 115a72f, 2026-09-02. There is no separate dated document.
- **The rescope question itself** is raised in ESSAY2_QUERY6_REPORT.md:50 ("DECISION IS TIM'S: rescope the claim"), also first committed in 115a72f.
- **"Before estimation" cannot be verified from git.** The announcement-window elevation was already computed in scripts/169 (169:290-291; t53:37 lists it as "announcement-window elevation (descriptive)"). 169 and 175 were committed together in 115a72f.

## Checks 3, 4, 7, 8

**A2-3 (e1timing vs blimits): the two "116" figures are the same set.** RECOMPUTED on the Essay 1 sample (CANONICAL_V3, has_crsp_data == 1, dropna on the 8 variables per 247:97-104; asserted 340 / 106 treated):
- breach_date == reported_date for **116** events (41 treated).
- **93** of them are Massachusetts (31 treated). Massachusetts is identified as "Massachusetts" in the first 200 characters of incident_details, because the dataset has no state column.
- "The 124" = events with immediate_disclosure == 1 (delay ≤ 7 days). **All 116 same-date events are inside the 124** (116 + 8 other events with delay 1–7 days); 0 same-date events fall outside it. The 116 is not "across all 340" in any other sense: it is the same-date subset of the 340, and every one of those is also inside the 124.
- Committed source: `outputs/TIMING_MEASUREMENT_REPORT.md:24, 39, 145-151` (116; 93 with 31 treated; 124 = 45 treated / 79 control). That report's numbers were produced by **scratchpad scripts (tm_*.py) that were never committed**. The report itself is committed (`dd8b564`).

**A2-4 (measure, "143 of 150 Massachusetts records"): record level.** Source: `outputs/TIMING_MEASUREMENT_REPORT.md:42-44` ("Across the full 1,054-record PRC file, breach_date == reported_date holds for 143 of 150 Massachusetts records (95%) against 38 of 904"). It counts PRC records, not events. The generator is a scratchpad script, never committed. RECOMPUTED with the simple first-200-character parse: 143 same-date of **149** Massachusetts records (38 of 905 elsewhere). The denominator differs by 1 because of the parser; the 143 matches.

**A2-7 (e1robust, "no small-cluster correction is available for this regression", turnover): TRUE as stated for turnover.** `outputs/defense_supplement/e1_cluster_ladder.csv` (scripts/255) covers **only the baseline H1–H4 CAR regression**: HC3 (normal), CV1 (normal and t(G−1)), CV3 jackknife and WCR (Rademacher, B = 99,999, seed 499) for each of H1_timing, H2_FCC, H3_prior and H4_health (e.g. `e1_cluster_ladder.csv:2-3` for H2_FCC). **Turnover** (`158:363`, HC3 only; `appendix_v3/table_14.csv`) has no CV1-t, CV3 or WCR output anywhere. 255 contains no "turnover" or "abto". Caveat: "available" means no committed output exists; the 255 machinery could produce one.

**A2-8 (bbound literature figures): NO-SOURCE in the committed repo.** No tracked file holds any of the five figures with those authors. Untracked local drafts sit in the repo root, are not in git, and date from March 2026, before the rebuild. What they contain:
- `Essay 1 (6) (1) (1)_COMPLETE_FINAL.docx` paragraph 46: "Cavusoglu et al. (2004) found -2.1% CAR across 66 events". **No "two-day" is stated.**
- Paragraph 25: Gordon et al. (2024): "-2.91% CAR … 8-K … other methods only dropped initially to -0.35%, but kept sliding to -1.04%". **No −0.63% three-day figure.**
- `Essay 1 DRAFT.docx` paragraph 28: "Cavusoglu, Mishra, and Chatterjee (2004) found average abnormal returns of -1.0% to -1.5%". **This contradicts −2.1%.**
- Kamiya 2021 −1.09%, Martins 2025 −4.08% and Campbell 2003 −5.46% are not found in any draft. Only Campbell, Lo & MacKinlay (1997) appears, and only as a reference.

Tim should check all five against the PDFs.
