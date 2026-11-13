# Defense audit: methodology fact sheet (Part B)

Read-only. Each item quotes the implementing code with file:line and states the definition in one sentence. Repo `main` at e25cf88; `defense-final` at 902a8ea. Where the v5 Essay 2 chain (scripts 262-272) differs from the defense-era implementation, that is noted under the item. NO-SOURCE means no committed file holds the value.

# Essay 1 (B1-B9)

Read-only. Repo `main` at e25cf88. **RECOMPUTED** marks values from read-only scratch queries; no repo file was written.

## B1. Abnormal return and CAR

Code:
- `scripts/155_rebuild_s5_outcomes.py:101-105`
  - `mkt = pd.read_csv('Data/wrds/market_indices.csv', usecols=['date', 'vwretd'])`
  - `crsp['ar'] = (crsp['ret'] - crsp['vwretd']) * 100`
- `155:147-155`
  - `w = g[(g['date'] >= bdt - timedelta(days=50)) & (g['date'] <= bdt + timedelta(days=50))]`
  - `pos = (w['date'] - bdt).abs().idxmin()`
  - `p5, p30 = min(len(w) - 1, pos + 5), min(len(w) - 1, pos + 30)`
  - `o['car_30d'] = round(w30['ar'].sum(), 4)`
- Docstring: `155:6-8`.

Definition:
- **Market series:** the CRSP **value-weighted** return (vwretd), not equal-weighted and not the S&P 500.
- **Abnormal return:** the daily simple return minus vwretd, × 100.
- **Day 0:** the stock's trading row **nearest** the breach date, searched within ±50 calendar days. It can fall before the breach date. It is not "the next trading day if the breach date is a non-trading day".
- **Window:** CAR(0,+30) sums 31 of the stock's own trading rows, days 0 to +30 inclusive.
- **Window edge:** the window is silently truncated at the ±50-day edge.
- **Missing returns:** pandas `sum` skips NaN, so a missing return counts as 0.

`scripts/251_defsup_e1_notification_anchored.py:20-23` (defense supplement) uses a different rule: day 0 is the first CRSP trading day on or after reported_date, and a window is used only if every day in it has a non-missing abnormal return.

## B2. HC3

Code: `scripts/158_rebuild_s8_regenerate.py:75-76`, `X = sm.add_constant(reg[CONTROLS].astype(float)); m = sm.OLS(y, X).fit(cov_type='HC3')`.

Definition: HC3 is the statsmodels library implementation, not a hand formula. `use_t` is not set, so the HC3 p-values and 95% CIs are **normal (z) based**. `scripts/255:20-22` confirms that Essay 1 Table 4 uses the normal distribution.

## B3. TOST and the ±2.10 pp bound

Code:
- `158:77-78`: `dof = len(reg) - len(CONTROLS) - 1`, `EQ = 2.10`
- `158:84`: `tost = max(1 - stats.t.cdf((b + EQ) / se, dof), stats.t.cdf((b - EQ) / se, dof))`

Definition: two one-sided t tests against ±2.10 pp, using the HC3 SE and df = n − 7 − 1 = 332.

Where the bound is defined:
- **Now:** `158:78` (EQ = 2.10), present since `77b362d` (2026-08-04T15:26:06-05:00), the first commit of 158.
- **First committed:** `2534fb9`, **2026-02-18T09:03:49-06:00**, at `scripts/80_essay2_regressions.py:193` (`equiv_bound = 2.10`; that file has since been deleted).

The comment in that first commit reads:

> `# (Economic significance threshold: H1 effect is 0.57%, 90% CI is [-0.95%, +2.09%] / #  A 2.1% bound ensures TOST passes while remaining small relative to other effects`

**So by its own comment, the bound was chosen to make the then-current H1 TOST pass, given an estimate already in hand** (a pre-rebuild, SIC-era H1).

When the current estimates appeared:
- **Current Essay 1 estimates** (H2 −0.8051, H1 1.15, …): first written by **`dd8b564`, 2026-10-02** (`git log` on `outputs/rebuild/constants_v3.json`; `dd8b564:outputs/rebuild/constants_v3.json:10,19`).
- **Previous values** (H2 −0.4994, H1 1.4143): at `0c9b378`, 2026-10-01.

The bound was therefore committed about 7.5 months before the current estimates existed, but after an earlier H1 estimate was known.

## B4. MDE80

Code: `158:89`, `C[f'{lab}_mde80'] = round(2.8 * se, 4)`. The same rule is used at `251:204`.

Definition: MDE80 = **2.8 × the HC3 SE**, a fixed multiplier, not exact t quantiles. The CV3 MDE80 in `scripts/255` uses t quantiles with G − 1 df (165's `mult`).

## B5. Parent-CIK clustering (CV1)

Code:
- `158:285-286`: `('Firm-clustered', {'cov_type': 'cluster', 'cov_kwds': {'groups': reg['final_cik']}})` → `outputs/rebuild/appendix_v3/table_8.csv:5`
- The same call appears at `251:190`.

Definition: statsmodels clustered covariance with its default small-sample correction, G/(G−1) × (N−1)/(N−K), and **normal p-values** (no `use_t`), with G = 83 parent CIKs (`e1_cluster_ladder.csv` column G). `scripts/255` adds a CV1 with t(G−1) df.

## B6. Abnormal turnover

Code:
- `158:342-358`
  - `idx = g['date'].searchsorted(bdt)`
  - `est = g.iloc[max(0, idx - 240):idx - 60]`
  - `evt = g.iloc[max(0, idx - 5):min(len(g), idx + 26)]`
  - `np.log(est['vol'] / (est['shrout'] * 1000))` (the same for `evt`)
  - requires `len(et) >= 30` and `len(vt) >= 15`
  - `return vt.mean() - et.mean()`
- Regressed with HC3 at `158:363`.

Definition:
- **Turnover:** abnormal log turnover. Daily turnover = vol / (shrout × 1000).
- **Day 0:** the first trading row on or after the breach date.
- **Abnormal value:** the mean of log daily turnover over event rows [−5, +25] minus its mean over estimation rows [−240, −61].
- **Scale:** a difference in log levels, not percent.
- **Inputs:** read from `crsp_daily_returns.csv` only, not the top-ups.
- **Result:** Form 499 coefficient 0.1064, HC3 p .0446 (`constants_v3.json:89-90`; `appendix_v3/table_14.csv:2`).

## B7. Leakage windows

Code:
- `158:404`: `W13 = [(-30, -21), (-20, -11), (-10, -1)]`
- `158:407-420` (`leak_cars`):
  - day 0 = the stock's row nearest the anchor
  - every day in a window must exist with a non-missing AR (`if len(sl) != b - a + 1 or sl.isna().any(): return None`)
- `158:449`: `stats.ttest_1samp(s, 0)`
- `158:454`: `stats.ttest_ind(st, su, equal_var=False)` (Welch)

Definition:
- **Windows:** the CAR over trading days [−30, −21], [−20, −11] and [−10, −1]. It uses the same abnormal-return definition as the main CAR.
- **Anchors:** the breach date (primary) and the reported date (secondary; rows with delay_invalid are excluded).
- **Tests:** a one-sample t test for each group, and a **Welch** test of treated minus untreated.
- **Output:** `appendix_v3/table_16.csv`.

## B8. Random forest

Code: `158:378-382`:
- `from sklearn.ensemble import RandomForestRegressor`
- `rf = RandomForestRegressor(n_estimators=500, random_state=42, n_jobs=1)`
- `rf.fit(reg[CONTROLS].astype(float), y)`
- `rf.feature_importances_`

Definition:
- **Model:** scikit-learn RandomForestRegressor, 500 trees, all other hyperparameters at their defaults, seed 42, single-threaded.
- **Inputs:** the 7 baseline covariates predicting car_30d on N = 340.
- **Importance:** impurity-based (MDI), `feature_importances_`.
- **Performance:** **no out-of-bag score and no cross-validation are computed.**
- **Output:** `outputs/rebuild/appendix_v3/table_15.csv`. Top feature: roa 0.3405, then firm_size_log 0.2364.

## B9. HC3 disqualification and Essay 1

Where the disqualification is stated:
- `run_all.py:92-93`: "Inference is CV3 (cluster jackknife) plus a wild cluster bootstrap; HC3 is reported for comparison only and is DISQUALIFIED as a significance test." (The ledger's citation of `run_all.py:77-78` is stale; the lines have moved.)
- `outputs/RETIREMENT_LEDGER.md:136-149` (Part G2): "HC3 is a **disqualified rung** … (`run_all.py:77-78`; the placebo rejects at 12.1% under CV1, and HC3 is more anticonservative still)".

Where the 12.1% comes from:
- The **Essay 2** placebo-treatment diagnostic (`scripts/169_essay2_spec_repairs.py:27-28, 312-341`; `outputs/ESSAY2_QUERY5_REPORT.md:28`, 12.1% at α = .05).
- 169's text still says "11 treated parents", i.e. the pre-DISH 331 vintage. `outputs/ESSAY2_QUERY5_PART_S.md:40` reports 11.6% from the same diagnostic.

Essay 3 uses CV3 and WCR as its frame (`f1_ladder.csv`).

**Essay 1: the same placebo calibration was never run.** No Essay 1 script (155, 158, 251, 255, 260) contains a placebo-reassignment rejection-rate check (grep for "placebo" finds none).

Essay 1's primary inference is still HC3:
- `158:91-94` only relabels an HC3-significant result as "NOT A VERDICT".
- `scripts/255` adds CV1, CV3 and WCR for H1–H4 only.
- The turnover result (HC3 p .0446) has no CV3 or WCR rung anywhere.

# Essays 2 and 3 (B10-B21)

Read-only. Repo `main` at e25cf88; `defense-final` is 902a8ea.

For Essay 2, the defense-era code (scripts 163/164/165/169/175/176/180/249) is quoted, and a "v5" line notes where the v5 chain (scripts 262–272, commits 21cfbbb and 16f9611) differs. A value marked DERIVED is arithmetic on committed values.

## Essay 2

**B10. Delay**
- **Definition:** `disclosure_delay_days = reported_date − breach_date`, in **calendar** days (scripts/156_rebuild_s6_assembly.py:110).
- **Negative delays:** a delay more than 30 days negative is set to missing (`delay_invalid`, 156:115-121). A delay from −30 to −1 is set to 0 (`delay_recoded`, 156:125-131).
- **Winsorization:** `delay_w` = the delay capped at its P99 in the 333-event sample (784.96), top tail only (163:505-507).
- **Log:** `delay_log = log1p(disclosure_delay_days)` (164:117; 249:62).
- **v5:** the same delay definitions. The delay tests were rerun with the new pre-window control in scripts/271.

**B11. Volatility change (defense era)**
- **Returns:** daily **log** returns `log1p(ret)` (163:148). Not abnormal returns: there is no market adjustment.
- **Windows:** [−25,−5] and [+5,+25], counted in the stock's own trading-row positions around the reporting date. The reporting date maps to the nearest trading row within ±7 calendar days (163:152-169). Each window needs at least 15 returns (163:152,169).
- **Statistic:** `pre.std(ddof=1)*100` and the same for post, so daily percentage points (163:171-172). `e2_vol_change` = post − pre (163:179).
- **v5:** market-adjusted **simple** abnormal returns (r − vwretd); windows [−60,−11] and [+1,+20] on the market calendar; at least 80% coverage per window (scripts/263_e2v5_lib.py:48,131,152-163).

**B12. Announcement-window elevation (defense era)**
- **Benchmark:** a market model, `r = a + b·vwretd`, fit by OLS on simple returns over rows [−250,−46], which must hold at least 100 observations (169:91,114-118).
- **Residual SDs:** taken over [−4,+4] (at least 7 returns) and [−25,−5] (at least 15 returns), ×100 (169:121-128).
- **Elevation:** `abn_ann − abn_pre` (175:65).
- **Model:** `elev ~ Form 499 + abn_pre + delay_w + firm_size_log + leverage + roa + health_breach + prior_events`, clustered by parent (175:185-197). Result: N = 331, G = 81 (t50:6).
- **v5:** the same windows on market-adjusted returns. Coefficient +0.4327, CV3 p .0271 (outputs/essay2_v5/v5_t09_announcement.csv).

**B13. CV1, CV3 and the wild cluster bootstrap (scripts/165)**
- **CV1:** scaled by `adj = G/(G−1) · (n−1)/(n−k)` (165:84). p = 2·(1 − t.cdf(|b/se|, **G−1**)) (165:212).
- **CV3:** delete one parent cluster, refit, then V3 = **(G−1)/G** · Σ(b_g − b̄)(b_g − b̄)' (165:88-95). p uses t(**G−1**) (165:213). The 95% CI is b ± t.975(G−1)·se (165:214,226).
- **WCR:** the null is imposed (the restricted fit regresses on the other columns with β_t = β₀, 165:151-154). Weights are **Rademacher** ±1 per cluster (165:159). The bootstrap t uses the CV1 sandwich (165:172-174).
- **p-value:** **symmetric**, `(#{|t*| ≥ |t_obs|} + 1)/(B + 1)` (165:177).
- **B:** 99,999 for WCR and for the unrestricted bootstrap (WCU) (165:180-182).
- **Webb six-point weights:** ±√1.5, ±1, ±√0.5, with B = 9,999 (165:160-163,183).
- **CI by inversion:** restricted bootstrap with B = 9,999 per evaluation; 28 bisection steps on each side, starting from b ± 8·se_CV1 (165:186-206).
- **Seed:** `rng = np.random.default_rng(499)` (165:39). One random stream is shared, in order, by WCR → WCU → Webb → the CI inversion.
- **Note:** the announcement model's WCR uses B = 49,999 (t50:6, column B_wcr).
- **Committed values:** t26_inference_ladder.csv: CV1 p .2983, CV3 p .3863, WCR .3325, WCU .5302, Webb .3325.
- **v5:** this code is lifted unchanged into scripts/263, gated on reproducing t26 and t28 exactly.

**B14. Benjamini–Hochberg family for the announcement window**
- **Where the family is defined:**
  - `FAM_ANN = 'L1+L3 announcement window (pre-specified 8/31)'` (175:56), with four `N_TESTS` entries (175:129, 132, 144, 195).
  - The test ledger: t53_test_ledger.csv:54-57.
  - The BH step itself is in scripts/176:115-135.
- **The four raw p-values as used in 176** (176:121-122 types three of them in as constants; only the treatment row is read from t50):

| Test | Raw p used | Source |
|---|---|---|
| Earnings elevation | **1e-40** | typed constant |
| Contrast (breach − earnings) | **1e-20** | typed constant |
| Treatment on elevation, CV3 | **0.0208** | t50 |
| Breach elevation | **0.073** | typed constant |

- **Thresholds:** .0125 / .0250 / .0375 / .0500 (outputs/ESSAY2_QUERY7_REPORT.md:36-39).
- **Adjusted p-values:** not emitted anywhere. **DERIVED** BH-adjusted values: earnings ≈ 4e-40, contrast ≈ 2e-20, treatment 0.0208 × 4/3 = **0.0277**, breach elevation **0.073**.
- **Flag:** the 0.073 for breach elevation is a typed placeholder. t50:3 gives −0.0857 / 0.0505, so t = −1.697 and p ≈ **0.094** under t(80), or 0.090 under the normal (**DERIVED**). Neither value changes the BH result, because the treatment test is the third-ranked p-value either way.

**B15. Pre-specification timeline (dates and hashes only)**
- **The test is first defined in** `scripts/175_essay2_announcement_contrast.py`, whose first commit is **115a72f, 2026-09-02 15:52 −0500** ("Essay 2 canonical chain: scripts 163-177"). The elevation construction (`abn_ann`) in 169 also first appears in 115a72f.
- **"Pre-specified on 8/31":** recorded only in the 175 docstring ("Tim's 8/31 rescoping decision", 175:4), in 175:53-56, in ESSAY2_ANNOUNCEMENT_CONTRAST.md:19,28 and in ESSAY2_QUERY7_REPORT.md:35. All of these were first committed in **115a72f, 2026-09-02**. No standalone dated 8/31 document exists in the repo (NO-SOURCE). No commit is dated 8/31 except 1b2c650, the weekly article monitor.
- **"H5a" / "H5b":** these labels appear **nowhere** in the repo (searched docs, outputs, scripts and archive; NO-SOURCE). The earlier nulls they presumably refer to (the main volatility null t26, the S1/S2 repairs t37, and Query 4/5) were also first committed in **115a72f, 2026-09-02**.
- **Consequence:** the definition, the pre-specification record and the earlier null results all enter git in the same commit. Commit history cannot establish their order. The commit message says the chain was developed uncommitted before 9/2 ("only ... differ from 8/30").

## Essay 3

**B16. Outcome construction**
- **Section parsed:** the Item 5.02 section of each 8-K: from the "Item 5.02" header to the next item header or the signature (scripts/220_essay3_v4_classifier_v2.py:26-29).
- **Coding:** a departure is coded at the sentence level by deterministic verb rules (220:30-42).
- **One per person:** one departure per person within each parent CIK, dated to its earliest disclosing filing. Mentions more than 540 days apart start a new event, and mentions with no name stay separate (220:624-650; ruling 1, 220:15-18).
- **Windows:** measured from the notification date, `(t0, t0+w]` calendar days for w = 30/90/180, anchor `rd` (220:43-46, 680-690).
- **Flag:** the code is not restricted to sub-item **5.02(b)**. Sub-item labels (a)–(f) are recorded but not filtered on (220:28). The outcome covers any executive departure found in the Item 5.02 section text.

**B17. LPM specification**
- **Model:** `exec_departure_{30,90,180}_rd ~ fcc_form499 + prior_breaches_1yr + health_breach + firm_size_log + leverage + roa + baseline_exec_rate_py_rd + prior12m_mktadj_ret_rd` (scripts/227_essay3_v4_estimation.py:9-10, 80-84).
- **Fixed effects:** none in the primary specification. Year FE and two-digit SIC FE appear only as F3 sensitivities (227:17).
- **Inference:** clustered by parent CIK.
- **Seed:** `default_rng(3)` (227:67).

**B18. Effective clusters G\***
- **Formula:** Carter–Schnepel–Steigerwald. `xt_res` is the treatment dummy's residual after partialling out the other regressors. Then γ_g = Σ xt_res² within each cluster, Γ = Σ(γ − γ̄)² / (G·γ̄²), and G\* = G/(1 + Γ) (227:165-169).
- **Inputs:** G = 119, G1 = 13. Result: **G\* = 24.5** at all three windows (constants_essay3_v4.json `F1_{30,90,180}_G_star`).

**B19. Randomization inference**
- **Both p-values were computed:** `ri_p_coef` and `ri_p_t` (CV3 t), with p = (#{|stat\*| ≥ |obs|} + 1)/(B + 1) (scripts/250:25).
- **Draws:** B = 9,999, seed 250 (250:21; e3_randomization_inference.csv, columns B and seed).
- **Values by variant and window:**

| Variant | Window | coef-based p | CV3-t-based p |
|---|---|---|---|
| C1 (all parents) | 30d | .9037 | .8803 |
| C1 (all parents) | 90d | .5961 | .5872 |
| C1 (all parents) | 180d | .8455 | .8100 |
| C1 (all parents) | placebo | .4080 | .2875 |
| C3 (size-matched parents) | 30d | .9292 | .9213 |
| C3 (size-matched parents) | 90d | .5459 | .5865 |
| C3 (size-matched parents) | 180d | .8323 | .8058 |
| C3 (size-matched parents) | placebo | .3233 | .2703 |

- **Note:** the observed 13 treated parents hold 115 events, of which 109 are treated (250:30-32).

**B20. Classifier validation**
- **Who coded:** **Tim did NOT hand-code.** All reference codes were produced by Claude, blind to the classifier output, and adopted by Tim. Sources: VALIDATION_REFERENCE_CODES_R1_README.txt:4-8; _R2_README.txt:4; _AUDIT_README.txt:5; essay3_v4/..._V4_README.txt:6-8.

| Round | Rows | How drawn | Seeds |
|---|---|---|---|
| Round 1 | 80 (50 calibration + 30 random) | random draw (scripts/187, scripts/189:4-5) | draw 20260911; order 4242 |
| Round 2 | 30 | random draw (scripts/196:5-9) | draw 20260912; order 4343 |
| Recall audit | 80 | **stratified** by treatment, 40 treated + 40 control (scripts/200:14) | 20260913 / 20260914; order 4444 |
| v4 new documents | 30 | random, `min(30, pool)` (scripts/237) | 20260919 |

- **Per-field n:** 30 per field in 238_scoring.md:7-14. Executive-departure agreement .9667, κ .8696, recall .80 (4 of 5).
- **Order of commits (rules frozen before coding):**
  - v1 frozen: d39bc6d, 2026-09-11 13:58.
  - Round-1 codes: edbf670, 14:37.
  - v2 classifier: 6f7be7a, 14:34. **v2 was revised using round 1, and committed before the round-2 codes.**
  - Round-2 codes: 5ec8f9e, 14:44.
  - Hidden audit answers: 762a4b9, 14:58. Audit codes: 8e18c4e, 15:16.
  - v4 codes: 93bed94, 2026-09-19 10:34. The frozen classifier was first run on those documents at 6147414, 10:42.
- **Final classifier rules:** scripts/220, first commit 7527d46, 2026-09-19 (a copy of 195, 6f7be7a).

**B21. Placebo window**
- **Definition:** an executive departure first disclosed in `(t0 − 180d, t0]`, before the notification (220:691; 227:16; f4_placebo.csv; e3_randomization_inference.csv window label `placebo (t0-180d, t0]`).
