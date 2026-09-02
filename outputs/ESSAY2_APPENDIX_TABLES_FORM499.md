# Essay 2 Appendix Tables — Form 499 rerun (ground truth)

**Generated live by scripts/163_essay2_rerun_form499.py on CANONICAL_V3.
Nothing here is carried forward from the old draft.**

## Plain-language report

**1. Main effect.** Treatment (Form 499) on volatility change (daily-pp,
log-return SD, [-25,-5] vs [+5,+25] trading days around notification):
coef +0.1575, SE 0.1304, t +1.208,
df 324, p 0.2281, N 333. Verdict: **null — underpowered/inconclusive**
(TOST p = 0.5766 against the Essay 1 bound converted to
daily units; MDE80 = 0.3652 daily pp =
5.80pp annualized — the design cannot
detect, at 80% power, effect sizes of the magnitude the prior literature
discusses). DV-convention note: the breach-anchored annualized DV the old
CODE used gives +3.62 (p=0.044 HC3, p=0.112
firm-clustered) on this sample, but it is DISQUALIFIED on construct
validity — 56.7% of its measured post-window days precede public
notification (median observation: 74%) — see Phase E. The draft-spec
measure is the valid one, and it is null.

**2. Firm-size step-down.** Q1 (smallest): -1.000 (p=0.002, 1 treated parent CIKs, <5 — do not interpret bare); Q2: +0.322 (p=0.322, 4 treated parent CIKs, <5 — do not interpret bare); Q3: +0.703 (p=0.027, 4 treated parent CIKs, <5 — do not interpret bare); Q4 (largest): +0.301 (p=0.103, 5 treated parent CIKs). (Old draft's +7.31 Q1 figure is not
reproduced; treated parent-CIK counts are now printed beside every quartile.)

**3. Final N = 333** (102 treated / 35 orgs /
11 parent CIKs), vs Essay 1 v3 regression N = 338.
The old draft's N = 891 is not reproducible from the canonical chain — it
predates deduplication (1,054 records -> 489 events) and entity resolution.
Full chain in ESSAY2_SAMPLE_ATTRITION_LEDGER.md; the volatility-window
requirement and the delay-regressor requirement are separate lines.

**4. Old vs new.** No old-draft coefficient was confirmed; none reproduced
(see leak check). NOT REGENERABLE AT ALL: the five moderators (CVSS, media,
governance, information-environment, reputation), the N = 891 sample, the
records-based prior-breach count (mean 3.65, range 0-68), and the old
draft's t/p columns (which were internally inconsistent — every t was
0.8806 x coef/SE, and its headline p = .047 was the single reconciled cell;
the printed t = 1.769 implies p = .077).

**5. Pipeline findings** are listed at the end of this file.

---
==========================================================================================
ESSAY 2 RERUN — GROUND TRUTH (Form 499 treatment, CANONICAL_V3)
==========================================================================================
ASSERT PASS — treatment column is fcc_form499 (Form 499), not SIC

Computing Essay 2 volatility DV (log-return SD, trading days [-25,-5]/[+5,+25], notification-anchored)...
ASSERT PASS — prior_breaches_total equals recomputed prior-event count
ASSERT PASS — universe is 1,054 notification records [1054]
ASSERT PASS — entity resolution retains 758 records
ASSERT PASS — dedup yields 524 firm-day events
ASSERT PASS — Gate 2 yields 489 events
ASSERT PASS — record chain closes: 1054 - 296 = 758
ASSERT PASS — event chain closes: 524 -> 489 removes 35
ASSERT PASS — CRSP daily extract ends at the 2024-12-31 WRDS boundary [max trading date in extract = 2024-12-31]
ASSERT PASS — every notification beyond the boundary is calendar-2025 (none later) [years: [2025]]
ASSERT PASS — boundary line reorders attrition only: window step would drop every 2025-notified event anyway
ASSERT PASS — ledger closes: no CRSP match [489 -> 366 (-123)]
ASSERT PASS — ledger closes: no notification date [366 -> 366 (-0)]
ASSERT PASS — ledger closes: beyond WRDS extract boundary [366 -> 360 (-6)]
ASSERT PASS — ledger closes: windows not computable [360 -> 349 (-11)]
ASSERT PASS — ledger closes: missing covariates [349 -> 334 (-15)]
ASSERT PASS — ledger closes: missing delay [334 -> 333 (-1)]
ASSERT PASS — final N is nowhere near the old draft N=891 (dedup+CRSP applied) [N=333]
ASSERT PASS — window-loss decomposition closes [8+0+3+0 == 11]
ASSERT PASS — CRSP-match failures = canonical minus matched [123 == 489 - 366]
ASSERT PASS — treated CRSP-match failures reconcile
ASSERT PASS — org-type composition sums to CRSP-fail total
ASSERT PASS — by-year canonical column sums to canonical N/treated
ASSERT PASS — by-year final column sums to final N/treated
ASSERT PASS — Essay 1 regression sample reproduces from the script-158 recipe and matches constants_v3 [338/104 vs constants 338/104]

==========================================================================================
PHASE B — DESCRIPTIVES BY TREATMENT STATUS
==========================================================================================
ASSERT PASS — group SDs computed independently and NOT identical (e2_vol_change) [1.0884 vs 1.0968]
ASSERT PASS — pooled mean reconciles to subgroup means (e2_vol_change)
ASSERT PASS — group SDs computed independently and NOT identical (e2_pre_sd) [1.1625 vs 1.0528]
ASSERT PASS — pooled mean reconciles to subgroup means (e2_pre_sd)
ASSERT PASS — group SDs computed independently and NOT identical (e2_post_sd) [1.0427 vs 1.0205]
ASSERT PASS — pooled mean reconciles to subgroup means (e2_post_sd)
ASSERT PASS — group SDs computed independently and NOT identical (disclosure_delay_days) [254.4334 vs 124.9830]
ASSERT PASS — pooled mean reconciles to subgroup means (disclosure_delay_days)
ASSERT PASS — group SDs computed independently and NOT identical (delay_w) [160.6476 vs 119.9689]
ASSERT PASS — pooled mean reconciles to subgroup means (delay_w)
ASSERT PASS — group SDs computed independently and NOT identical (firm_size_log) [1.2359 vs 1.3882]
ASSERT PASS — pooled mean reconciles to subgroup means (firm_size_log)
ASSERT PASS — group SDs computed independently and NOT identical (leverage) [0.1648 vs 0.2167]
ASSERT PASS — pooled mean reconciles to subgroup means (leverage)
ASSERT PASS — group SDs computed independently and NOT identical (roa) [0.0474 vs 0.1233]
ASSERT PASS — pooled mean reconciles to subgroup means (roa)
ASSERT PASS — group SDs computed independently and NOT identical (health_breach) [0.0000 vs 0.2469]
ASSERT PASS — pooled mean reconciles to subgroup means (health_breach)
ASSERT PASS — group SDs computed independently and NOT identical (prior_events) [9.1366 vs 21.0262]
ASSERT PASS — pooled mean reconciles to subgroup means (prior_events)
ASSERT PASS — post-window mean - pre-window mean == mean volatility change (treated)
ASSERT PASS — post-window mean - pre-window mean == mean volatility change (control)
ASSERT PASS — post-window mean - pre-window mean == mean volatility change (pooled)
             variable  mean_treated  sd_treated  mean_control  sd_control  mean_pooled  sd_pooled  n_treated  n_control
        e2_vol_change        0.0060      1.0884       -0.0397      1.0968      -0.0257     1.0928        102        231
            e2_pre_sd        1.7080      1.1625        1.6803      1.0528       1.6888     1.0859        102        231
           e2_post_sd        1.7139      1.0427        1.6406      1.0205       1.6631     1.0264        102        231
disclosure_delay_days      100.0490    254.4334       71.0087    124.9830      79.9039   175.2005        102        231
              delay_w       83.2733    160.6476       70.2466    119.9689      74.2368   133.6339        102        231
        firm_size_log       11.6238      1.2359        9.6463      1.3882      10.2520     1.6227        102        231
             leverage        0.7230      0.1648        0.6414      0.2167       0.6664     0.2055        102        231
                  roa        0.0239      0.0474        0.0770      0.1233       0.0608     0.1087        102        231
        health_breach        0.0000      0.0000        0.0649      0.2469       0.0450     0.2077        102        231
         prior_events       10.2157      9.1366       13.8745     21.0262      12.7538    18.2900        102        231

(The old Table A2 reported identical treated/control SDs on three variables — 14.2/14.2, 16.3/16.3, 1.84/1.84 — impossible for unequal groups; the independent SDs above replace it.)

==========================================================================================
PHASE C — MAIN EFFECT, NESTED MODELS, SE SPECIFICATIONS
==========================================================================================
ASSERT PASS — t == coef/se (M1 timing + pre-vol :: delay_w) [t=0.109198 coef/se=0.109198]
ASSERT PASS — p follows from t and df (M1 timing + pre-vol :: delay_w) [p=0.913112 implied=0.913112 df=330]
ASSERT PASS — t == coef/se (M1 timing + pre-vol :: e2_pre_sd) [t=-8.872952 coef/se=-8.872952]
ASSERT PASS — p follows from t and df (M1 timing + pre-vol :: e2_pre_sd) [p=0.000000 implied=0.000000 df=330]

M1 timing + pre-vol: N=333 df_resid=330 R2=0.3093
ASSERT PASS — t == coef/se (M2 + financial controls :: delay_w) [t=0.075110 coef/se=0.075110]
ASSERT PASS — p follows from t and df (M2 + financial controls :: delay_w) [p=0.940173 implied=0.940173 df=327]
ASSERT PASS — t == coef/se (M2 + financial controls :: e2_pre_sd) [t=-9.585930 coef/se=-9.585930]
ASSERT PASS — p follows from t and df (M2 + financial controls :: e2_pre_sd) [p=0.000000 implied=0.000000 df=327]
ASSERT PASS — t == coef/se (M2 + financial controls :: firm_size_log) [t=-1.158759 coef/se=-1.158759]
ASSERT PASS — p follows from t and df (M2 + financial controls :: firm_size_log) [p=0.247400 implied=0.247400 df=327]
ASSERT PASS — t == coef/se (M2 + financial controls :: leverage) [t=-1.033785 coef/se=-1.033785]
ASSERT PASS — p follows from t and df (M2 + financial controls :: leverage) [p=0.302001 implied=0.302001 df=327]
ASSERT PASS — t == coef/se (M2 + financial controls :: roa) [t=-1.405937 coef/se=-1.405937]
ASSERT PASS — p follows from t and df (M2 + financial controls :: roa) [p=0.160692 implied=0.160692 df=327]

M2 + financial controls: N=333 df_resid=327 R2=0.3157
ASSERT PASS — t == coef/se (M3 + treatment :: delay_w) [t=0.076449 coef/se=0.076449]
ASSERT PASS — p follows from t and df (M3 + treatment :: delay_w) [p=0.939109 implied=0.939109 df=326]
ASSERT PASS — t == coef/se (M3 + treatment :: e2_pre_sd) [t=-9.682511 coef/se=-9.682511]
ASSERT PASS — p follows from t and df (M3 + treatment :: e2_pre_sd) [p=0.000000 implied=0.000000 df=326]
ASSERT PASS — t == coef/se (M3 + treatment :: firm_size_log) [t=-1.844791 coef/se=-1.844791]
ASSERT PASS — p follows from t and df (M3 + treatment :: firm_size_log) [p=0.065975 implied=0.065975 df=326]
ASSERT PASS — t == coef/se (M3 + treatment :: leverage) [t=-1.248971 coef/se=-1.248971]
ASSERT PASS — p follows from t and df (M3 + treatment :: leverage) [p=0.212572 implied=0.212572 df=326]
ASSERT PASS — t == coef/se (M3 + treatment :: roa) [t=-1.323583 coef/se=-1.323583]
ASSERT PASS — p follows from t and df (M3 + treatment :: roa) [p=0.186569 implied=0.186569 df=326]
ASSERT PASS — t == coef/se (M3 + treatment :: fcc_form499) [t=1.238091 coef/se=1.238091]
ASSERT PASS — p follows from t and df (M3 + treatment :: fcc_form499) [p=0.216573 implied=0.216573 df=326]

M3 + treatment: N=333 df_resid=326 R2=0.3185
  M3 + treatment :: fcc_form499: coef +0.1535  SE 0.1240  t +1.238  df 326  p 0.2166  N 333
ASSERT PASS — t == coef/se (M4 + breach controls (HEADLINE) :: delay_w) [t=0.041093 coef/se=0.041093]
ASSERT PASS — p follows from t and df (M4 + breach controls (HEADLINE) :: delay_w) [p=0.967247 implied=0.967247 df=324]
ASSERT PASS — t == coef/se (M4 + breach controls (HEADLINE) :: e2_pre_sd) [t=-9.543874 coef/se=-9.543874]
ASSERT PASS — p follows from t and df (M4 + breach controls (HEADLINE) :: e2_pre_sd) [p=0.000000 implied=0.000000 df=324]
ASSERT PASS — t == coef/se (M4 + breach controls (HEADLINE) :: firm_size_log) [t=-1.837485 coef/se=-1.837485]
ASSERT PASS — p follows from t and df (M4 + breach controls (HEADLINE) :: firm_size_log) [p=0.067054 implied=0.067054 df=324]
ASSERT PASS — t == coef/se (M4 + breach controls (HEADLINE) :: leverage) [t=-1.407907 coef/se=-1.407907]
ASSERT PASS — p follows from t and df (M4 + breach controls (HEADLINE) :: leverage) [p=0.160117 implied=0.160117 df=324]
ASSERT PASS — t == coef/se (M4 + breach controls (HEADLINE) :: roa) [t=-1.215582 coef/se=-1.215582]
ASSERT PASS — p follows from t and df (M4 + breach controls (HEADLINE) :: roa) [p=0.225029 implied=0.225029 df=324]
ASSERT PASS — t == coef/se (M4 + breach controls (HEADLINE) :: fcc_form499) [t=1.207652 coef/se=1.207652]
ASSERT PASS — p follows from t and df (M4 + breach controls (HEADLINE) :: fcc_form499) [p=0.228062 implied=0.228062 df=324]
ASSERT PASS — t == coef/se (M4 + breach controls (HEADLINE) :: health_breach) [t=0.054035 coef/se=0.054035]
ASSERT PASS — p follows from t and df (M4 + breach controls (HEADLINE) :: health_breach) [p=0.956941 implied=0.956941 df=324]
ASSERT PASS — t == coef/se (M4 + breach controls (HEADLINE) :: prior_events) [t=-0.122210 coef/se=-0.122210]
ASSERT PASS — p follows from t and df (M4 + breach controls (HEADLINE) :: prior_events) [p=0.902809 implied=0.902809 df=324]

M4 + breach controls (HEADLINE): N=333 df_resid=324 R2=0.3185
  M4 + breach controls (HEADLINE) :: fcc_form499: coef +0.1575  SE 0.1304  t +1.208  df 324  p 0.2281  N 333
ASSERT PASS — t == coef/se (MAIN EFFECT (M4, HC3)) [t=1.207652 coef/se=1.207652]
ASSERT PASS — p follows from t and df (MAIN EFFECT (M4, HC3)) [p=0.228062 implied=0.228062 df=324]

HEADLINE: MAIN EFFECT (M4, HC3): coef +0.1575  SE 0.1304  t +1.208  df 324  p 0.2281  N 333
ASSERT PASS — t == coef/se (MAIN EFFECT (untrimmed delay)) [t=1.212855 coef/se=1.212855]
ASSERT PASS — p follows from t and df (MAIN EFFECT (untrimmed delay)) [p=0.226069 implied=0.226069 df=324]
ASSERT PASS — t == coef/se (delay (winsorized p99)) [t=0.041093 coef/se=0.041093]
ASSERT PASS — p follows from t and df (delay (winsorized p99)) [p=0.967247 implied=0.967247 df=324]
ASSERT PASS — t == coef/se (delay (untrimmed)) [t=-0.243646 coef/se=-0.243646]
ASSERT PASS — p follows from t and df (delay (untrimmed)) [p=0.807660 implied=0.807660 df=324]

Winsorization rule: delay capped at in-sample p99 = 785 days (documented). Clock note: 47 CFR 64.2011(b) starts its seven-BUSINESS-day law-enforcement clock at "reasonable determination" of the breach, not discovery, and customer notice waits a further seven business days; days_to_disclosure here is reported_date minus breach OCCURRENCE date, which measures neither statutory clock — it proxies total public-notification lag, and the theory should be read against that. With vs without winsorization:
  MAIN EFFECT (M4, HC3): coef +0.1575  SE 0.1304  t +1.208  df 324  p 0.2281  N 333
  MAIN EFFECT (untrimmed delay): coef +0.1589  SE 0.1310  t +1.213  df 324  p 0.2261  N 333
  delay (winsorized p99): coef +0.0000  SE 0.0003  t +0.041  df 324  p 0.9672  N 333
  delay (untrimmed): coef -0.0000  SE 0.0002  t -0.244  df 324  p 0.8077  N 333

SE specifications for the M4 treatment coefficient (the old draft scaled every t by 0.8806 — coef and t/p came from different runs; here each row is one fit):
ASSERT PASS — t == coef/se (classical OLS) [t=1.141716 coef/se=1.141716]
ASSERT PASS — p follows from t and df (classical OLS) [p=0.254415 implied=0.254415 df=324]
ASSERT PASS — t == coef/se (HC1) [t=1.223635 coef/se=1.223635]
ASSERT PASS — p follows from t and df (HC1) [p=0.221979 implied=0.221979 df=324]
ASSERT PASS — t == coef/se (HC3) [t=1.207652 coef/se=1.207652]
ASSERT PASS — p follows from t and df (HC3) [p=0.228062 implied=0.228062 df=324]
ASSERT PASS — t == coef/se (firm-clustered) [t=0.799202 coef/se=0.799202]
ASSERT PASS — p follows from t and df (firm-clustered) [p=0.426540 implied=0.426540 df=80]
ASSERT PASS — t == coef/se (industry-clustered (N=333)) [t=1.003378 coef/se=1.003378]
ASSERT PASS — p follows from t and df (industry-clustered (N=333)) [p=0.325688 implied=0.325688 df=24]
  classical OLS: coef +0.1575  SE 0.1380  t +1.142  df 324  p 0.2544  N 333
  HC1: coef +0.1575  SE 0.1287  t +1.224  df 324  p 0.2220  N 333
  HC3: coef +0.1575  SE 0.1304  t +1.208  df 324  p 0.2281  N 333
  firm-clustered: coef +0.1575  SE 0.1971  t +0.799  df 80  p 0.4265  N 333  clusters=81
  industry-clustered (N=333): coef +0.1575  SE 0.1570  t +1.003  df 24  p 0.3257  N 333  clusters=25
  Cluster counts: firm 81 (meets the ~40-50 convention), industry 25 2-digit-SIC clusters (BELOW the conventional ~40-50 threshold for asymptotic cluster-robust inference — treat industry-clustered p with caution).

==========================================================================================
PHASE D — FIRM-SIZE HETEROGENEITY (quartiles of log total assets)
==========================================================================================
ASSERT PASS — t == coef/se (quartile Q1 (smallest)) [t=-3.163611 coef/se=-3.163611]
ASSERT PASS — p follows from t and df (quartile Q1 (smallest)) [p=0.002221 implied=0.002221 df=78]
  quartile Q1 (smallest): coef -1.0004  SE 0.3162  t -3.164  df 78  p 0.0022  N 86  treated 2 obs / 1 orgs / 1 parent CIKs  MDE80 0.89pp  FEWER THAN 5 TREATED PARENT CIKs (1) — do not interpret bare
ASSERT PASS — t == coef/se (quartile Q2) [t=0.997380 coef/se=0.997380]
ASSERT PASS — p follows from t and df (quartile Q2) [p=0.321920 implied=0.321920 df=72]
  quartile Q2: coef +0.3216  SE 0.3225  t +0.997  df 72  p 0.3219  N 81  treated 14 obs / 8 orgs / 4 parent CIKs  MDE80 0.90pp  FEWER THAN 5 TREATED PARENT CIKs (4) — do not interpret bare
ASSERT PASS — t == coef/se (quartile Q3) [t=2.260975 coef/se=2.260975]
ASSERT PASS — p follows from t and df (quartile Q3) [p=0.026661 implied=0.026661 df=75]
  quartile Q3: coef +0.7033  SE 0.3111  t +2.261  df 75  p 0.0267  N 84  treated 29 obs / 13 orgs / 4 parent CIKs  MDE80 0.87pp  FEWER THAN 5 TREATED PARENT CIKs (4) — do not interpret bare
ASSERT PASS — t == coef/se (quartile Q4 (largest)) [t=1.652029 coef/se=1.652029]
ASSERT PASS — p follows from t and df (quartile Q4 (largest)) [p=0.102824 implied=0.102824 df=73]
  quartile Q4 (largest): coef +0.3008  SE 0.1821  t +1.652  df 73  p 0.1028  N 82  treated 57 obs / 18 orgs / 5 parent CIKs  MDE80 0.51pp  
ASSERT PASS — quartile Ns sum to full sample N [333 == 333]

Prior-breach count reconstruction (records vs events — substantive finding, not a silent fix):
                                                                                 measure   n  mean    sd  p50  p90  max
                                   NEW: prior deduplicated events (canonical, regressor) 333 12.75 18.29  4.0 41.8   75
OLD-STYLE regenerated: prior notification RECORDS (sum n_source_records of prior events) 333 17.18 23.84  6.0 53.0   94
        OLD DRAFT (quoted, NOT regenerable: computed on pre-dedup records, N=891 sample) 891  3.65   NaN  NaN  NaN   68
NOTE: the canonical count is per PARENT CIK (post entity-resolution), so large carrier families accumulate more prior events than the old org-name-string count even after dedup — the two differences (dedup, parent aggregation) move in opposite directions.

==========================================================================================
PHASE E — MODERATORS AND ROBUSTNESS
==========================================================================================
                         moderator          status n                                                                                                                                                                                                                                 reason
          Breach complexity (CVSS) NOT REGENERABLE 0 NVD/CVSS columns and scripts (99, 105) retired at Rebuild Stage 0; no CVE linkage exists in CANONICAL_V3. The old claim that this ran on the full N=891 while being defined only for CVE-linked breaches was internally contradictory.
                    Media coverage NOT REGENERABLE 0                                                                                                       Constructed on the pre-audit dataset (script 101); source columns absent from CANONICAL_V3; no committed pipeline produces them.
Governance quality (SOX 404 proxy) NOT REGENERABLE 0                                                                                                                                                                                Old-draft construct; no source data in canonical chain.
 Information-environment composite NOT REGENERABLE 0                                                    Script 106 construct on pre-audit base. The old draft reported p=.275 in prose vs p=.0589 in the table for this interaction — neither value survives; retired, not carried forward.
               Reputation weakness NOT REGENERABLE 0                                                                                          Old-draft construct (its table row also printed R2=.0156 against ~.39 for every other row — a different-model artifact); no canonical source.
ASSERT PASS — t == coef/se (year FE) [t=0.752569 coef/se=0.752569]
ASSERT PASS — p follows from t and df (year FE) [p=0.452286 implied=0.452286 df=307]
  year FE: coef +0.1053  SE 0.1399  t +0.753  df 307  p 0.4523  N 333  R2=0.4379
ASSERT PASS — t == coef/se (industry FE (2-digit SIC)) [t=2.230747 coef/se=2.230747]
ASSERT PASS — p follows from t and df (industry FE (2-digit SIC)) [p=0.026437 implied=0.026437 df=300]
  industry FE (2-digit SIC): coef +0.3739  SE 0.1676  t +2.231  df 300  p 0.0264  N 333  R2=0.3777
ASSERT PASS — t == coef/se (year + industry FE) [t=0.823690 coef/se=0.823690]
ASSERT PASS — p follows from t and df (year + industry FE) [p=0.410809 implied=0.410809 df=283]
  year + industry FE: coef +0.1379  SE 0.1674  t +0.824  df 283  p 0.4108  N 333  R2=0.5082
  Identification check: the combined year+industry FE treatment coefficient is IDENTIFIED (SE finite at 0.167) — an improvement over the old draft, whose combined specification collapsed because SIC-based treatment was a function of three SIC codes. BUT the identification is THIN: only 2 of 25 2-digit-SIC cells contain both treated and control events, so the within-industry comparison rests on those 2 cells. The industry-FE-only estimate (p=0.0264) leans on the same thin variation and on 25 clusters (below the ~40-50 convention) — do not headline it.

VIF (M4 design):
     variable  VIF
      delay_w 1.05
    e2_pre_sd 1.17
firm_size_log 1.65
     leverage 1.11
          roa 1.49
  fcc_form499 1.61
health_breach 1.09
 prior_events 1.41

Breusch-Pagan (stated ONCE, used everywhere): chi2(8) = 8.4534, p = 0.3905. (The old draft printed chi2=3.92/p=.049 in prose and 15.5838/p=.0487 in its table — both retired.)
Jarque-Bera residual normality: JB = 2235.1, p = 0.00e+00, skew 2.66, kurtosis 14.53 — heavy-tailed; HC3 primary inference stands, normality rejected as expected for volatility data.
ASSERT PASS — t == coef/se (M4 excl. Cook's D > 4/N (18 obs)) [t=0.872524 coef/se=0.872524]
ASSERT PASS — p follows from t and df (M4 excl. Cook's D > 4/N (18 obs)) [p=0.383607 implied=0.383607 df=306]

Influence: 18 obs with Cook's D > 4/N (0.0120); 18 with |DFFITS| > 0.329.
  M4 excl. Cook's D > 4/N (18 obs): coef +0.0737  SE 0.0845  t +0.873  df 306  p 0.3836  N 315

GARCH(1,1) conditional-volatility DV (Gaussian MLE, Nelder-Mead; estimation window trading days [-250,+25] around the anchor, min 200 obs; DV = mean conditional SD over [+5,+25] minus [-25,-5], daily pp):
ASSERT PASS — t == coef/se (GARCH(1,1) DV (N=330)) [t=0.669893 coef/se=0.669893]
ASSERT PASS — p follows from t and df (GARCH(1,1) DV (N=330)) [p=0.503407 implied=0.503407 df=321]
  GARCH(1,1) DV (N=330): coef +0.0484  SE 0.0722  t +0.670  df 321  p 0.5034  N 330
ASSERT PASS — t == coef/se (canonical DV, HC3 (N=333)) [t=2.025291 coef/se=2.025291]
ASSERT PASS — p follows from t and df (canonical DV, HC3 (N=333)) [p=0.043657 implied=0.043657 df=324]
ASSERT PASS — t == coef/se (canonical DV, firm-clustered) [t=1.607250 coef/se=1.607250]
ASSERT PASS — p follows from t and df (canonical DV, firm-clustered) [p=0.111940 implied=0.111940 df=80]

DV-convention sensitivity (canonical breach-anchored annualized DV, the convention the old CODE actually used, on THIS sample and control set; corr with the draft-spec DV = 0.451):
  canonical DV, HC3 (N=333): coef +3.6239  SE 1.7893  t +2.025  df 324  p 0.0437  N 333
  canonical DV, firm-clustered: coef +3.6239  SE 2.2547  t +1.607  df 80  p 0.1119  N 333  clusters=81
  Under the old code's convention the effect is +3.62 annualized pp (p=0.0437 HC3) but dies under firm clustering (p=0.1119) — the same pattern as the v3 baseline H5 (Essay 2's hypothesis in constants_v3: +3.29, p=.063, estimated under this same breach-anchored convention).

  Breach-to-notification delay (N=333): min 0 | p10 0 | p25 0 | median 23 | p75 79 | p90 201 | max 1917 | mean 79.9 | SD 175.2
  all: window fully pre-notification 45.6% | contains notification 54.4% | mean 56.7% (median 74.2%) of window days precede notification
  treated: window fully pre-notification 47.1% | contains notification 52.9% | mean 53.7% (median 71.0%) of window days precede notification
  control: window fully pre-notification 45.0% | contains notification 55.0% | mean 58.0% (median 77.4%) of window days precede notification
  CONSTRUCT VERDICT: a strict majority of observations does NOT have the window close before notification (45.6% do), but a majority of what the measure contains is pre-notification volatility — 56.7% of all measured post-window days precede public notification, and the median observation has 74% of its "post" window before the market learned anything. The breach-anchored DV is disqualified as a measure of post-DISCLOSURE uncertainty on construct validity: it mostly measures volatility before the event it claims to measure. The treated/control difference in truncation is trivial (47.1% vs 45.0% fully-pre; treated windows contain slightly MORE post-notification days, 46.3% vs 42.0%), so there is no mechanical treatment-correlated measurement bias on top — the disqualification is construct-wide, not treatment-differential.

==========================================================================================
PHASE F — INFERENCE QUALITY
==========================================================================================
  MAIN EFFECT (M4, HC3): TOST(±0.1323 daily pp = ±2.10 annualized) p=0.5766  MDE80=0.3652pp  -> NULL — UNDERPOWERED (inconclusive)
  quartile Q1 (smallest): TOST(±0.1323 daily pp = ±2.10 annualized) p=0.9962  MDE80=0.8855pp  -> SIGNIFICANT [1 treated parent CIKs — do not interpret bare]
  quartile Q2: TOST(±0.1323 daily pp = ±2.10 annualized) p=0.7205  MDE80=0.9029pp  -> NULL — UNDERPOWERED (inconclusive) [4 treated parent CIKs — do not interpret bare]
  quartile Q3: TOST(±0.1323 daily pp = ±2.10 annualized) p=0.9648  MDE80=0.8710pp  -> SIGNIFICANT [4 treated parent CIKs — do not interpret bare]
  quartile Q4 (largest): TOST(±0.1323 daily pp = ±2.10 annualized) p=0.8211  MDE80=0.5099pp  -> NULL — UNDERPOWERED (inconclusive)

  BOUND PROVENANCE: the ±2.10pp bound was pre-specified for Essay 1's CAR outcome ("fixed from literature before rebuilt estimates existed", scripts/158) and was never independently justified as a smallest volatility effect of interest — its use here is a unit conversion only, stated as such.
  LITERATURE-ANCHORED CHECK (conditional): against a candidate SESOI of 4.2pp annualized (0.2646 daily pp), TOST p=0.2062 — still not equivalence-bounded. MDE80 = 0.3652 daily pp = 5.80pp annualized, which EXCEEDS 4.2pp: this design cannot detect, at 80% power, even the effect size used as the literature anchor. CAVEAT: the 4.2pp figure attributed to Obaydin, Xu & Zurbruegg (2024) could not be verified in the repository's article summary — their JBFA 2024 paper reports crash-risk effects (NSKEW/DUVOL/COUNT, >=5% of a SD) and bad-news-hoarding proxies, not a post-breach volatility change in pp. No commensurable volatility-native SESOI has been located in the prior literature on file; until one is, the defensible sentence is the MDE one, not any TOST verdict.

Economic significance: main effect +0.1575 daily pp = +9.5% of mean post-breach volatility (1.6631 daily pp). Incremental R2 from the treatment indicator: +0.0027 (M4 0.3185 vs without-treatment 0.3158). (Old draft: .3922 vs .3896 — about a quarter of one percent.)

==========================================================================================
OLD-DRAFT LEAK CHECK AND CODEBASE FLAGS
==========================================================================================
No regenerated coefficient reproduces any old-draft value (+1.83, +7.31, +3.64, -3.39, -0.54, +1.763, +2.48, +4.074, +1.894, +0.7956) to within 0.005 — no evidence of old-number leakage.

FORENSIC — old-draft provenance closure (nothing here is a result; pre-dedup data, SIC-based fcc_reportable treatment, both retired):
  N=891 (reproduces the old draft's 891 exactly from the PRE-dedup ENRICHED file) | main FCC +1.6121 p=0.0772 (old draft: +1.83 / +1.763)
  Q1: +7.6515 (p=0.0060, N=229) vs old draft +7.31
  Q2: +2.8621 (p=0.0725, N=224) vs old draft +3.64
  Q3: -2.0526 (p=0.3707, N=215) vs old draft -0.54
  Q4: -3.5119 (p=0.0236, N=223) vs old draft -3.39
  The +7.31/+3.64/-0.54/-3.39 step-down REPRODUCES in sign, ordering, and approximate magnitude (+7.65/+2.86/-2.05/-3.51 under the full old control set) — the old quartile numbers are the pre-deduplication + SIC-treatment artifact, not a third-source mystery. Provenance closed. On corrected data the pattern does not exist (Phase D).

Codebase flags (directive): "September 28 2007"/"Rule 37.3" and SIC-code treatment (4813/4841/4899) appear ONLY in retired pre-rebuild scripts (83, 94, 20, build_essay1_*, create_*, scm_*, fix/rebuild_essay1_appendix, boost_mobile_forensics, consolidate_validation_results, and chronology-side scripts 131/137) and in script 142's note deliberately documenting the retirement. NO live v3-chain script (150-158) or this script assigns treatment by SIC or references the wrong date/rule.

==========================================================================================
PIPELINE FINDINGS (item 5 — things not already named in the directive)
==========================================================================================
1. FINAL_DATASET_ORIGINAL_1054.csv contained 784 rows, not 1,054 — misnamed
   (a vintage of the retired dedup set; script 142's docstring had already
   documented this). RENAMED 8/30/2026 to
   FINAL_DATASET_ORIGINAL_1054_MISNAMED_RETIRED.csv; no script reads it; the
   true 1,054-record universe is rebuild/stage2_signed.csv (and
   master_breach_dataset.xlsx).
2. has_crsp_data in CANONICAL_V3 is defined by car_30d computability
   (breach-anchored), not by security match: 12 events carry a
   permno but has_crsp_data = 0. Essay 2's notification-anchored windows are
   computable for some of these, so this rerun keys on permno + its own
   window requirement rather than reusing has_crsp_data — the two essays'
   CRSP samples overlap but are not nested.
3. The canonical prior-breach count is per PARENT CIK (post entity
   resolution), so carrier families accumulate more prior events (mean
   12.8 in this sample) than the old org-string
   count even after deduplication removed the Cencora-style record inflation.
   The regressor's semantics changed twice, in opposite directions.
4. The timing regressor is dead in every specification (|t| < 0.25 with and
   without winsorization): with corrected dates and the 8/17 wrong-field
   fixes, disclosure delay carries no volatility information at all. The old
   draft's timing narrative has no support in the corrected data.
5. Form 499 treatment concentrates in 2 mixed 2-digit-SIC cells;
   industry FE/clustered specifications are technically identified but rest
   on very thin within-industry variation (25 industry clusters,
   below the ~40-50 convention).
6. The old draft's N = 891 REPRODUCES EXACTLY from
   FINAL_DISSERTATION_DATASET_ENRICHED.csv (1,054 rows, PRE-deduplication,
   926 CRSP) under the old spec's dropna — the old Essay 2 ran on duplicate
   notification records and pre-resolution identities.
7. The old Essay 2 CODE never implemented the draft's stated volatility
   windows: scripts 20/90/90b used the breach-anchored annualized
   [-40,-1]/[0,+30] convention; the [-25,-5]/[+5,+25] language exists only
   in create_regression_formulas_document.py, the same file that carries
   "Rule 37.3", SIC-code treatment, and "January 1, 2007" (a THIRD wrong
   rule date). The draft's methods prose described a measure that was never
   computed. See the DV-convention sensitivity in Phase E.

Total reconciliation/consistency assertions passed: 131
