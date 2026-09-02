# Essay 2 Query 5 — Part S + H3/H4/H6/P/B3 (computed live)

==========================================================================================
ESSAY 2 QUERY 5 — PART S SPECIFICATION REPAIRS (N=331)
==========================================================================================

## S1 — Abnormal-volatility DV (market-model residual), year FE, two-way cluster (parent x event-month)
  S1 PRIMARY: abnormal vol, mkt-vol control, year FE, two-way: coef +0.0840 SE 0.1916 95% CI [-0.2974, +0.4653] N=329
  market-volatility-change control coefficient: +0.1887 (SE 0.0709) — reported per Billings-Jennings-Lev precedent
  S1 excl. 2008-09 & 2020: coef +0.0549 SE 0.1948 95% CI [-0.3331, +0.4428] N=303
  raw-vol robustness row (Dai et al., Financial Review): coef +0.0027 SE 0.1903 95% CI [-0.3762, +0.3815] N=329
  Query-2 headline (raw log-ret DV, CV1 firm) for continuity: coef +0.1486 SE 0.2021 95% CI [-0.2535, +0.5507] N=331

## S2 — Distant-baseline leakage test (MAIN TABLE rows)
  S2 baseline [-120,-60]: coef +0.0622 SE 0.2015 95% CI [-0.3388, +0.4632] N=329
  S2 baseline [-250,-50]: coef +0.0778 SE 0.2106 95% CI [-0.3414, +0.4971] N=326
  Stability: distant-baseline coefficients (+0.062, +0.078) vs adjacent (+0.084) — STABLE (within 2 SE). The "leakage biases toward zero, so the nulls are conservative" sentence is now LICENSED as a finding.

## S3 — ANCOVA identity, errors-in-variables, split-sample IV
  ANCOVA identity (footnote text): adding sigma_pre to both sides of D = a + g*sigma_pre + XB + e yields identical estimates on X; the specification ABSORBS regression to the mean. The pre-volatility coefficient is arithmetic, not economics — never interpreted.
  DV distribution: skewness +0.61, kurtosis 8.4
  S3 split-sample IV (pre-vol instrumented by [-120,-60]): coef -0.0815 SE 0.1827 95% CI [-0.4451, +0.2822] N=329
  first-stage F on the instrument: 110.6 (t^2). NOTE: second-stage SEs are the plug-in two-step ones (generated-regressor caveat stated); the point is covariate stability, shown below.
  S3 no pre-vol control (covariate movement visible): coef -0.0977 SE 0.1578 95% CI [-0.4118, +0.2164] N=329

## S4 — Log variance ratio ln(sd_post^2/sd_pre^2)
  S4 log variance ratio (Ohlson-Penman): coef +0.0240 SE 0.1967 95% CI [-0.3675, +0.4156] N=329
  If sign/inference differ from the level DV, the level results are driven by high-volatility firms and the log specification leads.

## S5 — Lineage (text): with the announcement window excluded this design measures a PERSISTENT shift in firm-specific uncertainty (Ohlson & Penman variance-change ancestry), not announcement information content; the Beaver (1968)/Patell (1976) U statistic tests the announcement window itself and is therefore not the right test for the question asked. All "market reaction to the announcement" language attached to this DV is purged.

## H4 — Calendar clustering
  Treated share varies by year: chi2(17)=61.5 (p=0.0000) — treated events DO cluster differently in calendar time; the event-year FE and two-way clustering in S1 are the structural fix (matching the microstructure spec's month FE). Kolari-Pynnonen corrections do not directly bind: they fix pooled tests of mean abnormal returns, not cross-sectional regressions on event-window outcomes (stated choice).
  Window-overlap rule: 162 events fall within 75 calendar days of the same firm's previous event (48.9% overlap rate). Rule: both retained in the main sample (each is a distinct disclosure); sensitivity dropping the later of each overlapping pair:
  H4 drop-overlaps sensitivity: coef -0.0905 SE 0.2150 95% CI [-0.5184, +0.3374] N=167

## H6 — Positive control first, placebo second
  IMPORTANT SCOPE NOTE: the valid positive control specified in the directive — the identical pipeline applied to QUARTERLY EARNINGS announcements, where a volatility spike is among the most robust facts in accounting — requires earnings announcement dates (Compustat RDQ / IBES ANNDATS), which the committed extracts do not carry. It is specified and BLOCKED on a one-line WRDS pull (add rdq to the quotes pull; scripts/167 pattern). The check below is NOT a pipeline validation — applying the pipeline to the breach announcement window tests the breach effect itself, not the instrument.
  Breach announcement-window check (descriptive): abnormal SD over [-4,+4] minus baseline [-25,-5]: -0.0890 daily pp (t=-1.77, p=0.078, N=329) — breach notifications produce NO detectable announcement-window volatility elevation (point estimate slightly negative). This is consistent with the H1/H2 CAR nulls and with the essay's overall story — the market does not visibly reprice at breach notification — but it CANNOT validate the pipeline, and is not claimed to.
  PLACEBO-TREATMENT diagnostic (10,000 parent-level reassignments, 11 treated parents held fixed, CV1 t vs t(80)): rejection rate at alpha=.05 = 12.1%. MATERIALLY ABOVE 5%: the analytic SEs are too small — that is itself the finding. Framed as a diagnostic of the inference procedure, NOT a p-value (exchangeability is false: Form 499 status correlates with size and return variance; Eggers, Tunon & Dafoe 2024). Actual-estimate percentile in the placebo t distribution: 77% (t_actual=0.799, CV1).

## P — PRC provenance diagnostic
  Notification records by year (1,054 universe) and treated share of events (489):
    2007: records  11 | events   7 | treated share 0%
    2008: records  18 | events  15 | treated share 33%
    2009: records  14 | events  13 | treated share 54%
    2010: records   7 | events   5 | treated share 0%
    2011: records  10 | events   3 | treated share 33%
    2012: records  16 | events  11 | treated share 27%
    2013: records  29 | events  23 | treated share 13%
    2014: records  29 | events  20 | treated share 60%
    2015: records  48 | events  28 | treated share 25%
    2016: records  77 | events  49 | treated share 0%
    2017: records  96 | events  60 | treated share 20%
    2018: records  33 | events  24 | treated share 17%
    2019: records  62 | events  36 | treated share 25%
    2020: records  56 | events  26 | treated share 35%
    2021: records  86 | events  27 | treated share 33%
    2022: records  74 | events  26 | treated share 27%
    2023: records 163 | events  66 | treated share 18%
    2024: records 188 | events  40 | treated share 40%
    2025: records  36 | events   9 | treated share 0%
  2019 frame break (media-curated -> statutory filings): treated share 20.9% pre-2019 vs 27.0% 2019+ (Welch t=-1.55, p=0.1209). No fall at the frame change — the H5 mechanism leaves no visible mark in treated representation.
  Provenance statement REQUIRED in Methods (from repo evidence: the universe is master_breach_dataset.xlsx, 1,054 records, 2006-2024 — the product name/version/download date are NOT recorded in the repository and must be supplied by the author; the 2019 methodology break sits inside the sample and is a sampling-frame change; PRC's own duplicate-reporting and completeness caveats quoted verbatim in limitations; Edwards, Hofmeyr & Forrest (2016) cited with the WEIS note that reporting-rate effects remain open.)

## B3 addendum — Dropped vs retained (489 -> 333)
  firm_size_log: retained mean 10.24 (n=331) vs dropped 10.52 (n=19); standardized diff -0.19 (Imbens denominator sqrt((S2t+S2c)/2))
  return_volatility_pre: retained mean 28.87 (n=331) vs dropped 37.30 (n=22); standardized diff -0.31 (Imbens denominator sqrt((S2t+S2c)/2))
  Attrition is size-selective by construction (CRSP+Compustat coverage) — stated; the estimand is the public-firm breach population.

## H3 — Balance (report, do not match; equivalence framing)
     variable  mean_t  mean_c  std_diff_imbens2015  std_diff_imbens_wooldridge  variance_ratio
firm_size_log  11.624   9.621                1.537                       1.086           0.817
     leverage   0.723   0.641                0.424                       0.300           0.573
          roa   0.024   0.077               -0.568                      -0.401           0.146
    e2_pre_sd   1.708   1.688                0.018                       0.013           1.216
      delay_w  83.375  70.342                0.092                       0.065           1.785
 prior_events  10.216  13.904               -0.227                      -0.160           0.187
health_breach   0.000   0.066               -0.374                      -0.264           0.000
  Note: denominators stated — Imbens (2015) sqrt((S2t+S2c)/2) vs Imbens-Wooldridge sqrt(S2t+S2c); they differ by sqrt(2). Thresholds: 0.25 economics convention, 0.10 biostatistics. NO t-tests or p-values (sample-size dependent). Variance ratios per Rubin (2001). TREATED CLUSTER COUNT: G1 = 11 parent CIKs (on the face of the table). Matching is NOT performed: 11 treated parents; wild-bootstrap inference fails under matching (Abadie-Imbens 2008); PSM design sensitivity documented (Shipman-Swanquist-Whited 2017); with limited overlap "there may in fact be no estimation method that leads to robust estimates" (Imbens 2015). Equivalence framing per Hartman-Hidalgo (2018).
  H3 common-support (controls in treated size range; CHANGE OF ESTIMAND, N=325): coef +0.0754 SE 0.1884 95% CI [-0.3000, +0.4507] N=324

==========================================================================================
Tests this script: 12 — S-main: 7; H4: 2; H6: 1; P: 1; H3: 1
