# Essay 1: table revisions for chair feedback (October 2026)

State as of commit **1634b2f** (scripts 260/261 and every file in `outputs/essay1_chair/`, regenerated from scratch at that commit; row-count gate PASS; freeze gate PASS). This header line was added in the commit that follows it; a file cannot carry its own commit's hash.

Draft reviewed: `Dissertation Essay 1 - Timing Without Consequence - Compliance and Market Reactions under Mandatory Breach Disclosure 10062026.docx` (Downloads; the version carrying the chair's 32 comments and her Panel A–F layout of Table 16).

Numbers of record: `outputs/rebuild/constants_v3.json` and `outputs/rebuild/appendix_v3/table_{1..16}.csv` at **dd8b564**, identical to tag **defense-final** for every one of those files (asserted by `scripts/261`). Sample: 489 events, 356 CRSP, **340 regression, 106 treated, 36 organizations, 12 parent CIKs**.

New files: `scripts/260_essay1_chair_tables.py` and `scripts/261_essay1_vintage_diff.py`. Outputs go to `outputs/essay1_chair/`. Neither script re-estimates anything on the frozen sample. 260 recomputes per-event inputs only to reproduce committed values, and it asserts the reproduction before any new test runs.

---

## 0. Provenance

The draft's figures (N = 338; H1 0.9641 / .3298; H2 −0.2663 / .8404; H3 0.0238 / .7092; H4 −1.0553 / .687; MDE80 2.7702 / 3.703 / 0.1786 / 7.3343; TOST .1259 / .0833 / <.0001 / .3451) are `constants_v3.json` and `appendix_v3/table_4.csv`, `table_5.csv` at **67e7c60** (2026-08-30). That vintage is from **before the DISH top-up** (338 / 104 / 11). `outputs/PENDING_REBASELINE.md` documents it, and the current `constants_v3.json` does **not** match it. The draft's Table 2 (116 treated) and Table 16 (+1.65 / .030, +1.69 / .015) also come from 67e7c60.

---

## 1. Table 2: group tests (new)

Source: `outputs/essay1_chair/t2_group_tests.csv` (per-event gaps in `t2_event_gaps.csv`). The gaps were recomputed with script 158's method and reproduce `constants_v3.json` T2_* exactly before any test runs.

| Test | Treated N | Control N | Treated | Control | Difference | Statistic | p |
|---|---|---|---|---|---|---|---|
| Welch two-sample t-test, mean days to first 8-K | 117 | 201 | 22.44 | 30.16 | −7.72 | t = −3.238 (df 256.8) | .001 |
| Mann-Whitney U (Wilcoxon rank-sum), distribution of days | 117 | 201 | median 15.0 | median 26.0 | −11.0 | U = 9,153.5 | .001 |
| Two-proportion z-test, share with an 8-K within 90 days | 118 | 219 | .9915 | .9178 | +.0737 | z = 2.799 | .005 |
| Fisher's exact test, same share (small-count check) | 118 | 219 | 117 of 118 | 201 of 219 | | | .005 |

Exact p-values: .0014, .0010, .0051, .0049. The Ns in the day tests (117, 201) are the events that have an 8-K within 90 days. The share tests use every event (118, 219). Fisher's exact test is included because only one treated event lacks a filing, which is too few for the z-test's normal approximation to be fully reliable. The two tests agree.

**Draft note for Table 2:**
> For every Form 499 filer event and every non-filer event at a parent company with three or more breaches in the sample, the table reports the number of calendar days from the breach date to the first Form 8-K the firm filed within 90 days after it, read from SEC EDGAR. Day statistics use only events with such a filing (117 treated, 201 control); the share column uses all events. The mean is compared with a Welch two-sample t-test (which does not assume equal variances), the distribution with a Mann-Whitney rank-sum test (which compares medians and the full distribution without assuming normality), and the share with a two-proportion z-test, with Fisher's exact test as a check because only one treated event lacks a filing. An 8-K filed near a breach need not mention the breach, so these tests measure how quickly and how consistently firms file with the SEC after a breach, not when they disclosed the breach. The control group is not a random sample of non-filers. The table does not show that the rule changed when breaches were disclosed.

---

## 2. Table 16: Panels A–F

Source: `outputs/essay1_chair/t16_panels.csv` (per-event CARs in `t16_event_cars.csv`). All 24 rows reproduce `outputs/rebuild/appendix_v3/table_16.csv` cell for cell. The full six-panel table is in `ESSAY1_CHAIR_TABLES.md`, Table 16.

**Checking the requested figures: neither reproduces on the frozen sample.** Both come from 67e7c60.

| Contrast, window [−10,−1] | Draft (67e7c60) | Frozen (dd8b564) |
|---|---|---|
| Panel C, breach-anchored, treated − untreated | +1.65 pp, p = .030 | **+1.48 pp, Welch p = .051** |
| Panel F, announcement-anchored, treated − untreated | +1.69 pp, p = .015 | **+1.53 pp, Welch p = .030** |

Facts by panel, for writing the panel-by-panel conclusion she asked for (mean CAR in pp, one-sample t-test p; difference row = Welch p):

| Panel | Anchor, window | All | Filers | Non-filers | Filers − non-filers |
|---|---|---|---|---|---|
| A | Breach, [−30,−21] | −0.14 (.600) | −0.37 (.532) | −0.04 (.887) | −0.33 (.621) |
| B | Breach, [−20,−11] | +0.77* (.017) | +0.29 (.638) | +0.99** (.009) | −0.70 (.326) |
| C | Breach, [−10,−1] | +0.04 (.894) | +1.06 (.120) | −0.42 (.199) | +1.48 (.051) |
| D | Disclosure, [−30,−21] | −0.02 (.946) | +0.09 (.884) | −0.07 (.816) | +0.15 (.817) |
| E | Disclosure, [−20,−11] | +0.30 (.266) | −0.47 (.339) | +0.65* (.046) | −1.12 (.058) |
| F | Disclosure, [−10,−1] | −0.34 (.256) | +0.72 (.250) | −0.81* (.012) | +1.53* (.030) |

Ns: breach-anchored 356 (111 filers / 245 non-filers); disclosure-anchored 355 (110 / 245).

**Draft leakage definition (one sentence):**
> A leakage window is a period of trading days before the recorded event date, used to test whether stock prices had already moved before that date, which would indicate that information reached the market earlier than the recorded date.

**Draft note for Table 16:**
> Each panel reports the cumulative market-adjusted abnormal return (the firm's daily return minus the CRSP value-weighted market return, in percent, summed over the window) for one pre-event window. In Panels A–C, day 0 is the trading day nearest the breach date. In Panels D–F, day 0 is the trading day nearest the date the breach was reported; one event without a valid reported date is excluded. For the All, Filer and Non-filer rows, t and p test whether the mean equals zero. The difference row tests whether the two group means differ (Welch two-sample t-test). Because the median disclosure delay is 24 days, a firm's public disclosure can fall inside a breach-anchored pre-event window, so movement there is not necessarily anticipation. \* p < .05, \*\* p < .01, \*\*\* p < .001; p-values in parentheses.

---

## 3. Variable definitions

### What the code actually computes (verified)

`scripts/260` Part D recomputes each control from the raw Compustat extract for all 340 regression events and compares it with the dataset column. Every row matches exactly (`covariate_formula_check.csv`, `260_run.log`).

| Variable | Methods says | Table 1 note says | **Code computes** (`scripts/156_rebuild_s6_assembly.py:80-85`) |
|---|---|---|---|
| Firm size | natural log of total assets | "log transformed size" | **ln(AT)**, the natural log of total assets in $ millions. Methods is correct. |
| Leverage | total debt / total assets | debt-to-equity ratio | **LT / AT = total liabilities / total assets.** Both descriptions are wrong. The extract has no debt fields (no DLTT or DLC), so a debt ratio cannot be computed from it. A liabilities-to-equity ratio would have a median of about 2.0; the leverage column's median is 0.669. |
| ROA | operating income / total assets | (none) | **NI / AT = net income / total assets.** Methods is wrong. |
| Timing | fiscal year prior to the breach | (none) | The **latest fiscal year ending before the breach date**, if it ended within 550 days. Lag median 184 days, range 1–364 days. |

### Variable Definitions table (paste-ready; also `outputs/essay1_chair/variable_definitions.csv`)

| Variable | Definition | Unit | Source | Timing |
|---|---|---|---|---|
| 30-day CAR | Sum of daily abnormal returns over trading days 0 to +30; the abnormal return is the firm's daily return minus the CRSP value-weighted market return; day 0 is the trading day nearest the breach date | Percent | CRSP daily stock file and market index | Trading days 0 to +30 from the breach date |
| 5-day CAR | Same, over trading days 0 to +5 | Percent | CRSP | Trading days 0 to +5 |
| Pre-event (leakage) CAR | Sum of daily abnormal returns over [−30,−21], [−20,−11] or [−10,−1] before day 0; day 0 = breach date (Panels A–C) or reported date (Panels D–F) | Percent | CRSP | Before day 0 |
| Abnormal trading turnover | Mean of log(daily volume ÷ shares outstanding) over trading days −5 to +25, minus its mean over days −240 to −60 | Log points | CRSP | Event window vs. pre-event baseline |
| Form 499 filer | 1 if the breached organization was a registered FCC Form 499 telecommunications filer whose registration covered the breach date (subject to the FCC seven-day rule); 0 otherwise | 0/1 | FCC Form 499 filer registry; 22 documented adjudication rules | At the breach date |
| Disclosed within 7 days | 1 if the breach was publicly reported no more than 7 calendar days after the breach date; missing if the delay is missing | 0/1 | Privacy Rights Clearinghouse (PRC) | Breach date to reported date |
| Disclosure delay | Calendar days from the breach date to the reported date (reported dates up to 30 days before the breach date set to 0; more than 30 days before, set to missing as a source error) | Days | PRC | Breach date to reported date |
| Prior breaches (past 12 months) | Number of other verified breach events at the same parent company in the 365 days before this breach | Count | PRC, after collapsing filings to events | 12 months before the breach |
| Any prior breach | 1 if prior breaches (past 12 months) > 0 | 0/1 | PRC | 12 months before the breach |
| Health data breach | 1 if the source record lists medical or health information as compromised, or the organization type is medical | 0/1 | PRC record text | At the breach |
| Firm size | Natural log of total assets (Compustat AT, $ millions) | Log $ millions | Compustat annual | Latest fiscal year ending before the breach |
| Leverage | Total liabilities (LT) ÷ total assets (AT) | Ratio | Compustat annual | Latest fiscal year ending before the breach |
| Return on assets | Net income (NI) ÷ total assets (AT) | Ratio | Compustat annual | Latest fiscal year ending before the breach |
| Operating margin (amendment only) | (Sales − cost of goods sold − SG&A) ÷ sales | Ratio | Compustat annual | Latest fiscal year ending before the breach |
| Records affected | Largest number of affected individuals reported across the event's source filings | Count | PRC | As reported |
| Days to first 8-K | Calendar days from the breach date to the first Form 8-K filed in the 90 days after it | Days | SEC EDGAR | Breach date to +90 days |
| 8-K within 90 days | 1 if any Form 8-K was filed in the 90 days after the breach date | 0/1 | SEC EDGAR | Breach date to +90 days |
| Fama-French factors | Market excess return (Mkt−RF), size (SMB) and value (HML) factors for the breach month | Percent | Kenneth French data library | Month of the breach |
| Year fixed effects | One indicator for each calendar year of the breach | 0/1 | PRC breach date | Year of the breach |

Note: the code's CAR window is days 0 through +30 (31 trading days, day 0 included). The draft says "the following thirty trading days".

### Label replacements (applied in `ESSAY1_CHAIR_TABLES.md`)

| Code name in draft tables | Plain label |
|---|---|
| fcc_form499 / H2_FCC | Form 499 filer |
| immediate_disclosure / H1_timing | Disclosed within 7 days |
| prior_breaches_1yr / H3_prior / "Prior_breaches 1 year" | Prior breaches (past 12 months) |
| health_breach / H4_health | Health data breach |
| firm_size_log | Firm size (log total assets) |
| leverage | Leverage (total liabilities / total assets) |
| roa | Return on assets (net income / total assets) |
| car_30d / car_5d | 30-day CAR (%) / 5-day CAR (%) |
| disclosure_delay_days | Disclosure delay (days) |
| Treated only (fcc_form499=1) / Untreated only (fcc_form499=0) | Form 499 filers only / Non-filers only |
| Pooled with interaction | All events, with interaction |
| immediate_disclosure x fcc_form499 | **Disclosed within 7 days × Form 499 filer** |
| Firm-clustered | Clustered by parent company (CIK) |
| NULL-INCONCLUSIVE / BOUNDED NULL | Inconclusive (cannot rule out a 2.10 pp effect) / Bounded null (effect shown to be small) |
| TOST_p_2.10 | TOST p (bound ±2.10 pp) |

---

## 4. Table notes (drafts for your review)

**Star legend, for every table that reports p-values:**
> \* p < .05, \*\* p < .01, \*\*\* p < .001. p-values in parentheses.

The draft's legend lists "\*\*" twice; the third entry should be "\*\*\*". Several draft cells carry stars that do not match their p-values (see §7c).

**Table 1.**
> Summary statistics for the CRSP-matched sample (N = 356 events). N varies by row because Compustat data are available for 341 events and a valid disclosure delay for 355. CARs are cumulative market-adjusted abnormal returns in percent. Firm size is the natural log of total assets; leverage is total liabilities divided by total assets; return on assets is net income divided by total assets, all from the latest fiscal year ending before the breach. Disclosure delay is calendar days from the breach date to the reported date.

**Table 3.**
> Mean and median 30-day CAR by group on the regression sample (N = 340). Each difference row reports the difference in group means and a Welch two-sample t-test, which compares the means without assuming the groups have equal variances. Medians are reported for description and are not tested.

**Table 4.**
> Ordinary least squares regression of the 30-day CAR (percent) on the four hypothesis variables and three controls, regression sample (N = 340). Standard errors are HC3 heteroskedasticity-robust (see Table 8). Variables are defined in the Variable Definitions table.

**Table 5.**
> Each row summarizes one hypothesis test from the Table 4 regression (N = 340). A conventional p-value tests whether an effect is different from zero. A high p-value alone cannot tell "there is no effect" apart from "the sample is too small to detect one." Two additional statistics separate those cases. **TOST p** (two one-sided tests) tests whether the effect is smaller than ±2.10 percentage points, a bound fixed from prior breach event studies before estimation; it runs one test that the effect is above −2.10 and one that it is below +2.10, and reports the larger p-value. A TOST p below .05 means the data show the effect lies within ±2.10 pp. **MDE80** (minimum detectable effect at 80 percent power) is the smallest true effect the regression would detect at the 5 percent level four times out of five, computed as 2.8 × the standard error. The **Status** column combines the two. *Bounded null*: the TOST rejects, so any effect is shown to be smaller than 2.10 pp. *Inconclusive*: neither the zero test nor the TOST rejects, so the data cannot distinguish a small effect from none. That is why the column is needed in addition to the p-value. The 95 percent confidence interval gives the range of effects consistent with the data.

**Table 6.**
> The Table 4 regression estimated separately for Form 499 filers (N = 106) and non-filers (N = 234), and on all events (N = 340) with the interaction term Disclosed within 7 days × Form 499 filer, which equals 1 only for filer events disclosed within 7 days. In the pooled model, the "Disclosed within 7 days" coefficient is the timing effect for non-filers, and the interaction is how much the timing effect differs for filers. The Form 499 filer indicator is omitted from the separate-group models because it does not vary within them. HC3 standard errors.

**Table 7.**
> The Table 4 regression re-estimated on restricted samples, each with its own N. Size deciles are by log total assets. HC3 standard errors.

**Table 8.**
> p-values for three coefficients from the Table 4 regression (N = 340) under four standard-error methods. A standard error measures how precisely a coefficient is estimated; each method makes different assumptions about the regression errors. **Classical OLS** assumes every event's unexplained return has the same variance and that events are independent. **HC1** allows the variance to differ across events (heteroskedasticity) and applies a small-sample correction. **HC3**, the primary method, also allows unequal variances and gives extra weight to influential observations; it is the more conservative choice at this sample size. **Clustered by parent company (CIK)** allows the errors of events at the same parent company to be correlated, as repeat breaches at one carrier can be; there are 83 parent-company clusters, 12 of which contain Form 499 filer events. With so few treated clusters, conventional clustered standard errors can understate uncertainty; small-cluster corrections for H1–H4 are reported in `outputs/defense_supplement/e1_cluster_ladder.csv`.

**Tables 9 and 10.**
> The Table 4 regression estimated separately within quartiles of firm size (log total assets), Q1 smallest. The Form 499 filer event count is shown because filer events concentrate in the larger quartiles; Q1 holds 2, so its estimate is illustrative only. Controls that do not vary within a quartile are dropped. HC3 standard errors.

**Table 11.**
> Form 499 filer coefficient from the Table 4 regression, with and without calendar-year fixed effects (one indicator per breach year), N = 340. The fixed effects absorb anything common to all breaches in a given year. HC3 standard errors.

**Table 12.**
> Table 4 regression with the number of records affected (largest count across the event's filings) added as a control, N = 340. HC3 standard errors.

**Table 13.**
> Table 4 regression with the Fama-French market, size and value factor values for the breach month added as controls, N = 340. HC3 standard errors.

**Table 14.**
> Table 4 regression with abnormal trading turnover replacing the 30-day CAR as the outcome. Abnormal turnover is the mean of log(daily volume ÷ shares outstanding) over trading days −5 to +25 minus its mean over days −240 to −60. N = 321; 19 regression-sample events lack enough trading history. HC3 standard errors.

**Table 15.**
> Random-forest importance of the seven Table 4 variables for predicting the 30-day CAR (500 trees, fixed seed, N = 340). Importance is the share of the forest's total reduction in prediction error attributable to each variable; the shares sum to 1. The forest was fit on the full sample without a holdout, so the ranking describes the fitted model rather than out-of-sample prediction, and carries no causal interpretation.

---

## 5. Every new number and its source file

| Number | Source |
|---|---|
| Welch t = −3.238, df 256.8, p = .0014; means 22.44 vs 30.16, diff −7.72; Ns 117 / 201 | `outputs/essay1_chair/t2_group_tests.csv` |
| Mann-Whitney U = 9,153.5, p = .0010; medians 15.0 vs 26.0 | `outputs/essay1_chair/t2_group_tests.csv` |
| Two-proportion z = 2.799, p = .0051; .9915 vs .9178, diff +.0737; Ns 118 / 219 | `outputs/essay1_chair/t2_group_tests.csv` |
| Fisher's exact p = .0049; 117 of 118 vs 201 of 219 | `outputs/essay1_chair/t2_group_tests.csv` |
| Table 16 panels A–F (all cells) | `outputs/essay1_chair/t16_panels.csv` = `outputs/rebuild/appendix_v3/table_16.csv` |
| Leverage = LT/AT, ROA = NI/AT, size = ln(AT): exact match on 340 events | `outputs/essay1_chair/covariate_formula_check.csv`, `260_run.log` |
| Fiscal-year lag median 184 d, range 1–364 d; LT/CEQ median 2.00 vs leverage median 0.669 | `outputs/essay1_chair/260_run.log` |
| 83 clusters, 12 containing treated events | `appendix_v3/table_8.csv` caption; `defense_supplement/e1_cluster_ladder.csv` (G, G1) |
| 95% CIs in relabelled Table 5 | `outputs/rebuild/constants_v3.json` (H*_ci) |
| Every other table cell | `outputs/rebuild/appendix_v3/table_{n}.csv` (dd8b564) |
| Every old → new value in §6 | `outputs/essay1_chair/vintage_diff_67e7c60_dd8b564.csv` |

---

## 6. Find-list for the Word draft (67e7c60 → dd8b564)

All values are from `outputs/essay1_chair/vintage_diff_67e7c60_dd8b564.csv`, which compares `constants_v3.json` (C) and `appendix_v3/table_n.csv` (Tn) at the two commits; the key is given. "Derived" means simple arithmetic on two committed values.

### Methods: sample description

| Draft text | Old | New | Source |
|---|---|---|---|
| "354 events matched to CRSP securities" | 354 | **356** | C `events_crsp` |
| "338 carry both the Compustat fundamentals …" | 338 | **340** | C `N_regression` |
| "129 of the 353 events with a valid delay, 36.5 percent" | 129 / 353 / 36.5% | **130 / 355 / 36.6%** | C `immediate_share_crsp` .3654 → .3662; T1 `disclosure_delay_days` N; 130 derived |
| "116 treated events" | 116 | **118** | C `treated_total` |
| "109 (30.8 percent) matched to CRSP" | 109 / 30.8% | **111 / 31.2%** | C `treated_crsp`; % = 111/356, derived |
| "104 survive into the regression sample" | 104 | **106** | C `treated_regression` |
| "35 organizations resolving to 11 parent filer entities" | 35 / 11 | **36 / 12** | C `treated_orgs_regression`, `treated_parent_ciks_regression` |
| "concentrated in eleven parent filer entities" (identification paragraph) | eleven | **twelve** | C `treated_parent_ciks_regression` |
| "15 health data breaches, 4.2 percent" | 15 / 4.2% | 15 / 4.2% (no change) | C `health_events_crsp`; 15/356 |
| "Of the 96 events treated by rule, 58 … 38 …; a further 26 … untreated by rule … satellite television …; 122 of the 489" | 96 / 38 / 26 | **⚠ no committed source found.** See §7, item 7. | `CANONICAL_V3.csv` `treatment_evidence`, DISH rows (CIK 1001082) |

### Results

| Draft text | Old | New | Source |
|---|---|---|---|
| Opening: MDEs "2.77, 3.70, and 7.33" | 2.77 / 3.70 / 7.33 | **2.81 / 3.93 / 7.30** | C `H1_timing_mde80`, `H2_FCC_mde80`, `H4_health_mde80` |
| Opening: H3 bound "0.18" | 0.18 | 0.18 (no change) | C `H3_prior_mde80` .1786 → .1804 |
| "338 firms matched to CRSP having complete firm-level data" | 338 | **340** | C `N_regression` |
| "104 treated events … 35 organizations … 11 parent" | 104 / 35 / 11 | **106 / 36 / 12** | C |
| CRSP mean / median 30-day CAR "−0.26 / +0.09" | −0.262 / +0.087 | **−0.378 / −0.031** | T1 `car_30d` |
| Regression mean / median "−0.16 / +0.19" | −0.1581 / +0.1911 | **−0.281 / +0.142** | C `car30d_regression_mean`, `_median` |
| Delay median 24 / mean 91 | 24 / 90.8 | 24 / 90.6 (rounded text unchanged) | T1 `disclosure_delay_days` |
| Table 2 text "all 116 treated events" | 116 | **118** | C `T2_treated_N` |
| Table 2 shares "99 percent … 92 percent" | .9914 / .9178 | .9915 / .9178 (rounded text unchanged) | C `T2_*_share_8k_90d` |
| Table 3: Form 499 "−0.55 vs +0.01, Welch p .578" | −0.545 / +0.014 / gap −0.559 / p .578 | **−0.933 / +0.014 / gap −0.947 / p .373** | T3 |
| Table 3: Timing "+0.39 vs −0.47, p .363" | +0.387 / −0.470 / gap 0.858 / p .3629 | **+0.365 / −0.652 / gap 1.017 / p .287** | T3 |
| Table 3: Health "−1.54 vs −0.09, gap 1.45, p .540" | −1.541 / −0.094 / 1.447 / .54 | **−1.541 / −0.223 / 1.318 / .577** | T3 |
| Table 3: Prior "+0.28 vs −0.81, gap 1.09, p .273" | +0.278 / −0.814 / 1.092 / .2725 | **+0.265 / −1.100 / 1.365 / .186** | T3 |
| Table 3 Ns | 104/234, 123/215, 15/323, 203/135 | **106/234, 124/216, 15/325, 204/136** | T3 |
| H1: "0.96, SE 0.99, p .330" | 0.9641 / 0.9894 / .3298 | **1.150 / 1.005 / .253** | T4; C `H1_timing_*` |
| H1: "CI −0.98 to +2.90" | −0.975 / 2.903 | **−0.82 / +3.12** | C `H1_timing_ci` |
| H1: "TOST p .126" | .1259 | **.173** | C `H1_timing_tost_p` |
| H1: "MDE 2.77"; "roughly 2.8 points" | 2.77 | **2.81** | C `H1_timing_mde80` |
| Table 6: filers "−0.78, p .665" | −0.7835 / .6648 (SE 1.8085) | **−0.220 / .907 (SE 1.888)** | C `T6_treated_*` |
| Table 6: non-filers "+1.93, p .105" | 1.9307 / .1052 | no change | T6 |
| Table 6: interaction "−3.02, p .152" | −3.0166 / .1516 (SE 2.1039) | **−2.378 / .277 (SE 2.187)** | C `T6_interaction_*` |
| Table 6: pooled timing main effect | 1.9807 / .097 | **1.962 / .100** | T6 |
| Table 6: pooled Form 499 main effect | 0.9518 / .5487 | **0.157 / .929** | T6 |
| Table 6 Ns "104 … 338" | 104 / 338 | **106 / 340** | C `T6_treated_N` |
| Table 7: excl. largest decile "1.17 (p .277)" | 1.17 / .277; FCC −0.375 / .80; ROA 8.57 / .13; N 305 | **1.382 / .207; FCC −0.998 / .525; ROA 8.18 / .147; N 307** | T7 |
| Table 7: excl. smallest decile "0.53 (p .611)" | 0.527 / .611; FCC −0.471 / .736; ROA 4.92 / .379; N 316 | **0.733 / .487; FCC −1.050 / .478; ROA 4.70 / .401; N 318** | T7 |
| Table 7: non-health "0.74 (p .447)" | 0.743 / .447; FCC −0.212 / .874; ROA 8.07 / .156; N 323 | **0.933 / .349; FCC −0.761 / .593; ROA 7.78 / .169; N 325** | T7 |
| Table 8: "from .255 under firm-level clustering to .330 under HC3" | .2547 … .3298 | **.185 … .253** | T8 |
| Table 8 all cells (timing / FCC / ROA) | OLS .3138/.8277/.1076; HC1 .3235/.8384/.1491; HC3 .3298/.8404/.1596; clustered .2547/.8227/.1866 | **OLS .2423/.5204/.1334; HC1 .2466/.5616/.1642; HC3 .2526/.5659/.175; clustered .1849/.5335/.199** | T8 |
| Table 8 note "82 clusters … 11 treated parent-CIK clusters" | 82 / 11 | **83 / 12** | T8 caption; `e1_cluster_ladder.csv` G, G1 |
| Table 9: "−1.07 to +3.17 … p from .356 to .773" | Q3 3.169 / .356, treated 29, N 83 | **Q3 3.829 / .274, treated 31, N 85 → range −1.07 to +3.83, p .274 to .773** | T9 |
| H2: "−0.27, SE 1.32, p .840" | −0.2663 / 1.3225 / .8404 | **−0.805 / 1.403 / .566** | T4; C `H2_FCC_*` |
| H2: "CI −2.86 to +2.33" | −2.858 / 2.326 | **−3.55 / +1.94** | C `H2_FCC_ci` |
| H2: "TOST p .083"; "MDE 3.70" | .0833 / 3.70 | **.178 / 3.93** | C |
| H2: "104 events from 35 organizations … 11 parent" | 104 / 35 / 11 | **106 / 36 / 12** | C |
| Table 10: "coefficients from +0.80 to +3.94" | Q3 0.804 / .808, treated 29, N 83 | **Q3 −1.298 / .720, treated 31, N 85 → range −1.30 to +3.94** ⚠ claim (§7, item 3) | T10 |
| Table 11: year FE "−1.00 (p .440)" | −0.9976 / .4396 | **−1.723 / .237** | T11 |
| Table 12: "−0.27 (p .839) … breach size p .953" | −0.2695 / .8386 / .9534 | **−0.807 / .565 / .978** | T12 |
| Table 13: FF3 "p .736"; ROA | .7358; ROA .1151 | **.477; ROA .132** | T13 |
| H3: "+0.02, SE 0.06, p .709" | 0.0238 / 0.0638 / .7092 | **0.033 / 0.064 / .606** | T4; C |
| H3: "CI −0.10 to +0.15" | −0.1012 / 0.1488 | **−0.09 / +0.16** | C `H3_prior_ci` |
| H3: "TOST p below .0001"; "MDE 0.18" | 0.0 / .1786 | <.001 (stored as 0.0) / 0.18 | C |
| H4: "−1.06, SE 2.62, p .687" | −1.0553 / 2.6194 / .687 | **−1.025 / 2.608 / .694** | T4; C |
| H4: "CI −6.19 to +4.08" | −6.189 / 4.079 | **−6.14 / +4.09** | C `H4_health_ci` |
| H4: "TOST p .345"; "MDE 7.33" | .3451 / 7.33 | **.340 / 7.30** | C |
| Controls: size "+0.03 (p .931)" | 0.0313 / .9307 | **+0.099 / .787** | T4 |
| Controls: leverage "−0.10 (p .961)" | −0.1029 / .9614 | **+0.133 / .950** (sign flips) | T4 |
| Controls: ROA "+7.65 (p .160)" | 7.6509 / .1596 | **+7.353 / .175** | T4; C `ROA_*` |
| Constant | −1.1918 / 4.31 / .7822 | **−2.084 / 4.377 / .634** | T4 |
| Op-margin amendment "p = .085" | 7.50 / .0851 | **8.28 / .058** | C `AMEND_opmargin_*` |
| Table 14: "Form 499 .117, timing .902, prior .060, health .559 … ROA .018" | .1167 / .9016 / .0598 / .5586 / ROA .0181 | **.045 / .793 / .042 / .544 / ROA .016** ⚠ claim (§7, item 2) | T14; C `volume_fcc_p` |
| Table 14 coefficients | Form 499 0.0779; timing 0.0045; prior −0.0055; health 0.0547; size −0.0197; leverage −0.1624; ROA 0.432 | **0.1064; 0.0098; −0.0060; 0.0566; −0.0232; −0.1731; 0.4486** | T14 |
| Table 14 N | 319 | **321** (19 excluded, unchanged) | T14 |
| Table 15: "ROA .331, size .243, leverage .205, prior .148, timing .044, Form 499 .017, health .013" | as quoted | **.341, .236, .202, .142, .049, .020, .011**; order unchanged; firm-characteristic share still about three quarters (.779) | T15 |
| Table 16 full-sample text "−0.07 (p .785) … +0.80 (p .013) … +0.09 (p .778)" | as quoted, N 354 | **−0.14 (p .600) … +0.77 (p .017) … +0.04 (p .894), N 356** | T16; C `T16_breach_*` |
| Table 16 [−10,−1] breach: filers "+1.23", non-filers "−0.42", "difference 1.65, p .030"; own-drift p ".073 … .199" | 1.231 / −0.421 / 1.653 / .0301; .0732 / .1989 | **1.063 / −0.421 / 1.484 / .051; .120 / .199** ⚠ claim (§7, item 1) | T16 |
| Table 16 [−10,−1] announcement: "1.69 points at p .015" | 1.694 / .015 | **1.526 / .030** | T16 |
| Table 16 announcement N | 353 (108 treated) | **355 (110 treated)** | C `T16_ann_N` |
| Table 16 notes "1 of 354 CRSP-sample events" | 354 | **356** | T16 caption |
| SIC paragraph: "Of the 116 Form 499-treated events, 25 … 91 … 26 … 65 … sixty" | 116 / 25 / 91 / 26 / 65 / 60 | **116 → 118; the rest: ⚠ no committed source found** (§7, item 8) | — |

### Table notes in the draft

| Note | Old | New |
|---|---|---|
| Table 1 "N = 354 … 339 … 353" | 354 / 339 / 353 | **356 / 341 / 355** |
| Table 1 cells | see T1 | 30-day CAR −0.378 / 8.776 / −0.031; 5-day CAR −0.457 / 4.295 / −0.218; size 10.266 / 1.607 / 10.287; leverage 0.665 / 0.204 / 0.669; ROA unchanged; delay 90.555 / 204.178 / 24 |
| Table 2 "treated N = 116"; row 116 / 22.46 / .9914 | 116 / 22.46 / .9914 | **118 / 22.44 / .9915** |
| Tables 3, 4, 5, 6, 8, 11, 12, 13, 15 "N = 338" | 338 | **340** |
| Table 6 note "N = 104" | 104 | **106** |
| Table 14 note "N = 319" | 319 | **321** |

### Conclusion

| Draft text | Old | New | Source |
|---|---|---|---|
| "Disclosure speed and regulatory status are bounded above at 2.8 and 3.7 percentage points" (twice) | 2.8 / 3.7 | **2.8 / 3.9** | C mde80 |
| "The minimum effect this analysis could detect is 2.77 points" | 2.77 | **2.81** ⚠ claim (§7c) | C |
| "The interval runs from −0.10 to +0.15" | −0.10 / +0.15 | **−0.09 / +0.16** | C `H3_prior_ci` |
| "Breach type is bounded at 7.3 points" | 7.33 | 7.30 (rounded text unchanged) | C |
| "104 treated events come from 35 organizations resolving to 11 parent filer entities … bounded at 3.7" | 104 / 35 / 11 / 3.7 | **106 / 36 / 12 / 3.9** | C |
| "identifying 26 of the 91 treated events it can classify and missing 65, sixty …" | as quoted | ⚠ no committed source (§7, item 8) | — |

---

## 7. Claims that change (not just numbers)

**(a) Changes caused by the vintage**

1. **Table 16, breach-anchored contrast is no longer significant.** In the old draft: "a difference of 1.65 points with a p of .030 … Anchoring the same windows on the disclosure date … produces a difference of 1.69 points at p = .015, so the pattern does not depend on which date defines the event." Frozen values: breach-anchored +1.48, **p = .051**; announcement-anchored +1.53, p = .030. Only the announcement-anchored contrast is below .05, so "does not depend on which date defines the event" no longer holds. Also in the newer draft: "What is specific here is the divergence: the drift appears at regulated carriers and runs the other direction at everyone else." Neither group's own drift is distinguishable from zero in Panel C (filers +1.06, p = .120; non-filers −0.42, p = .199). In Panel F, non-filers alone drift down significantly (−0.81, p = .012) and filers do not (+0.72, p = .250).
2. **Table 14 turnover: two hypothesis variables now fall below .05 under HC3.** The draft says "leaves every hypothesis variable null … Return on assets is the only variable associated with abnormal turnover" and "Our conclusion holds. The only variable [that] is statistically significant is the ROA." Frozen values: **Form 499 filer +0.106, p = .045; prior breaches −0.006, p = .042**; ROA p = .016. These are HC3-only p-values on a sample with 12 treated parent clusters. The Essay 1 rule (`scripts/158:91`) is that HC3 alone cannot carry a significance verdict, and no clustered or small-cluster check exists for the turnover regression. The sentence cannot stand as written. Whether to report these as HC3-only results or to run a cluster check is a decision for Tim; I did not run one.
3. **Table 10: the size-quartile range now includes a negative.** The draft says "coefficients from +0.80 to +3.94, none significant". Frozen values: Q3 = −1.30 (p = .720), so the range is −1.30 to +3.94. Still none significant, but the implied "all positive" pattern is gone.
4. **H2 bound.** "Regulatory status … bounded above at 3.7" becomes **3.9** (Results opening, Conclusion twice, Boundaries).
5. **CRSP-sample median 30-day CAR changes sign.** "−0.26 percent against a median of +0.09" becomes −0.38 against **−0.03**. The mean is still below the median, so the left-tail reading survives, but the median is no longer positive. (The regression-sample median stays positive at +0.14.)
6. **Operating-margin amendment** p moves .085 → **.058**. Still not below .05, but "returns a similar estimate at p = .085" needs the new value.
7. **Methods treatment-rule tallies.** The two DISH events (CIK 1001082; 2023-02-22, 2023-05-17) were "Adjudicated untreated (7/28): satellite TV not a telecom service" at 67e7c60. At dd8b564 they are "Clause (b) date-conditional (9/4)": treated. The draft's example of an untreated-by-rule case, "satellite television operations that fall outside the rule's scope", describes a classification that no longer exists; no satellite-TV untreated row remains in `CANONICAL_V3.csv`. **Unsourced:** no committed file produces 96 / 58 / 38 / 26 / 122 (see §8).
8. **SIC paragraph** (Results and Conclusion): "Of the 116 Form 499-treated events, 25 have no industry code … 26 … 65 … sixty in 4812". The treated count is now 118. **Unsourced:** no committed file produces 25 / 91 / 26 / 65 / 60 on either vintage (see §8).

**(b) Unaffected by the vintage but affected by the definitions check**

9. Methods: "Leverage … total debt divided by total assets" should be **total liabilities ÷ total assets**. "Return on assets, measured as operating income divided by total assets" should be **net income ÷ total assets**. Table 1 note: "Leverage is debt to equity ratio" is wrong (see §3).

**(c) Errors in the newer draft that exist on either vintage** (listed because they misstate the result)

10. Table 2 text: "the results show that control firms have significant less median and average days of filing" reverses the direction. Control firms take *more* days (median 26 vs 15; mean 30.2 vs 22.4), and the new tests put that at p = .001.
11. H1 text: "market reacted with a penalty that is not statistically significant for fast disclosure". The coefficient is **positive** (+1.15), so it is a small, non-significant premium, not a penalty.
12. H1 text: "returns a p-value of .126, meaning there is no equivalence." A TOST p above .05 means equivalence is **not established**, not that there is no equivalence.
13. H1 text and Conclusion: "effects larger than roughly 2.8 points are ruled out" and "An effect that size would have shown up here." The MDE is not what the data rule out; the confidence interval is. The H1 interval's upper end is **+3.12**, so a 3-point effect (the Amir et al. figure) is not ruled out. An MDE of 2.81 means a true 2.81-point effect would be detected 80 percent of the time, not always. The chair flagged this sentence as confusing.
14. H4 text: "TOST … p-value of 0.345 indicating that breaches involving health data does not have higher negative impact." A TOST p of .34 means the test is **inconclusive**; it cannot show the absence of an effect.
15. Stars in the chair's tables do not match the legend: Table 6 pooled timing "1.9807\*(0.097)"; Table 14 "−0.0055\*(0.0598)" and "0.432\*\*(0.0181)"; Table 16 "2.493\*\*(0.013)" and "2.636\*\*\*(0.009)". The legend also lists "\*\*" for both .01 and .001. The relabelled tables in `ESSAY1_CHAIR_TABLES.md` apply * < .05, ** < .01, *** < .001 mechanically.
16. Table 3 text: "Collectively, the results present opposite to what reputation theory predicts." Only the prior-breach comparison runs opposite: events at firms with a prior breach average +0.27 against −1.10 for firms without one. The chair asked that the opposite pattern be stated.
17. Conclusion: "Regulated carriers file faster, more consistently, and without exception." One of 118 treated events has no 8-K within 90 days, and an 8-K need not mention the breach. "Roughly half the time" overstates the gap: median 15 vs 26 days is 58 percent, and the means are 22 vs 30 days.
18. Methods: "the following thirty trading days". The code sums days 0 through +30.

---

## 8. Lookups in committed outputs (2026-10-15 scope correction; nothing new run)

**Table 14 turnover, p-values beyond HC3.** None exist. The only committed turnover regression is `outputs/rebuild/appendix_v3/table_14.csv` (HC3). `outputs/defense_supplement/e1_cluster_ladder.csv` (script 255) covers only the H1–H4 coefficients of the 30-day CAR regression (rungs: HC3, CV1 parent CIK, CV3 jackknife, wild cluster bootstrap). No committed file reports clustered or small-cluster p-values for turnover.

**Treatment-by-rule counts (96 / 58 / 38 / 26 / 122): unsourced.** No committed report, log or table carries them. `outputs/rebuild/STAGE4_TREATMENT_REPORT.md` exists locally but is not tracked (`.gitignore`; it prints the registry file date) and does not contain them either. Not computed here.

**SIC-proxy counts (25 / 91 / 26 / 65 / 60): unsourced.** No committed file carries them. `docs/DATA_QUALITY_DOCUMENTATION.md:81` mentions "25 SIC-flagged firms (marked SIC 4812 but not matched)". That is a count of firms from the pre-rebuild classification (script 122), not the 25 treated events without an industry code, and it is not a source for the draft sentence. Not computed here.

**H1–H4 95% confidence intervals: committed.** They are in `outputs/rebuild/constants_v3.json` (keys `H1_timing_ci`, `H2_FCC_ci`, `H3_prior_ci`, `H4_health_ci`, HC3, dd8b564) and again in the HC3 rows of `outputs/defense_supplement/e1_cluster_ladder.csv` (`ci95_lo`, `ci95_hi`):

| Hypothesis | Coef | HC3 SE | 95% CI | Source |
|---|---|---|---|---|
| H1 Disclosed within 7 days | 1.1500 | 1.0051 | [−0.82, 3.12] | constants_v3.json `H1_timing_ci`; e1_cluster_ladder.csv |
| H2 Form 499 filer | −0.8051 | 1.4026 | [−3.5541, 1.9438] | constants_v3.json `H2_FCC_ci`; e1_cluster_ladder.csv |
| H3 Prior breaches (12 months) | 0.0332 | 0.0644 | [−0.0931, 0.1594] | constants_v3.json `H3_prior_ci`; e1_cluster_ladder.csv |
| H4 Health data breach | −1.0247 | 2.6083 | [−6.137, 4.0875] | constants_v3.json `H4_health_ci`; e1_cluster_ladder.csv |

`appendix_v3/table_4.csv` and `table_5.csv` themselves carry only coefficient, SE and p (Table 5 adds TOST p and MDE80), not the interval.
