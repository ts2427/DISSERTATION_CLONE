# Essay 2 Appendix Tables â€” Form 499 rerun (ground truth)

**Generated live by scripts/163_essay2_rerun_form499.py on CANONICAL_V3.
Nothing here is carried forward from the old draft.**

## Plain-language report

**1. Main effect.** Treatment (Form 499) on volatility change (daily-pp,
log-return SD, [-25,-5] vs [+5,+25] trading days around notification):
coef +0.1486, SE 0.1321, t +1.125,
df 322, p 0.2613, N 331. Verdict: **null â€” underpowered/inconclusive**
(TOST p = 0.5491 against the Essay 1 bound converted to
daily units; MDE80 = 0.3698 daily pp =
5.87pp annualized â€” the design cannot
detect, at 80% power, effect sizes of the magnitude the prior literature
discusses). DV-convention note: the breach-anchored annualized DV the old
CODE used gives +3.52 (p=0.054 HC3, p=0.133
firm-clustered) on this sample, but it is DISQUALIFIED on construct
validity â€” 56.7% of its measured post-window days precede public
notification (median observation: 74%) â€” see Phase E. The draft-spec
measure is the valid one, and it is null.

**2. Firm-size step-down.** Q1 (smallest): -0.989 (p=0.003, 1 treated parent CIKs, <5 â€” do not interpret bare); Q2: +0.300 (p=0.361, 4 treated parent CIKs, <5 â€” do not interpret bare); Q3: +0.702 (p=0.031, 3 treated parent CIKs, <5 â€” do not interpret bare); Q4 (largest): +0.348 (p=0.063, 5 treated parent CIKs). (Old draft's +7.31 Q1 figure is not
reproduced; treated parent-CIK counts are now printed beside every quartile.)

**3. Final N = 331** (102 treated / 35 orgs /
11 parent CIKs), vs Essay 1 v3 regression N = 338.
The old draft's N = 891 is not reproducible from the canonical chain â€” it
predates deduplication (1,054 records -> 489 events) and entity resolution.
Full chain in ESSAY2_SAMPLE_ATTRITION_LEDGER.md; the volatility-window
requirement and the delay-regressor requirement are separate lines.

**4. Old vs new.** No old-draft coefficient was confirmed; none reproduced
(see leak check). NOT REGENERABLE AT ALL: the five moderators (CVSS, media,
governance, information-environment, reputation), the N = 891 sample, the
records-based prior-breach count (mean 3.65, range 0-68), and the old
draft's t/p columns (which were internally inconsistent â€” every t was
0.8806 x coef/SE, and its headline p = .047 was the single reconciled cell;
the printed t = 1.769 implies p = .077).

**5. Pipeline findings** are listed at the end of this file.

---
==========================================================================================
ESSAY 2 RERUN â€” GROUND TRUTH (Form 499 treatment, CANONICAL_V3)
==========================================================================================
ASSERT PASS â€” treatment column is fcc_form499 (Form 499), not SIC

Computing Essay 2 volatility DV (log-return SD, trading days [-25,-5]/[+5,+25], notification-anchored)...
ASSERT PASS â€” prior_breaches_total equals recomputed prior-event count
ASSERT PASS â€” universe is 1,054 notification records [1054]
ASSERT PASS â€” entity resolution retains 758 records
ASSERT PASS â€” dedup yields 524 firm-day events
ASSERT PASS â€” Gate 2 yields 489 events
ASSERT PASS â€” record chain closes: 1054 - 296 = 758
ASSERT PASS â€” event chain closes: 524 -> 489 removes 35
ASSERT PASS â€” CRSP daily extract ends at the 2024-12-31 WRDS boundary [max trading date in extract = 2024-12-31]
ASSERT PASS â€” every notification beyond the boundary is calendar-2025 (none later) [years: [2025]]
ASSERT PASS â€” boundary line reorders attrition only: window step would drop every 2025-notified event anyway
ASSERT PASS â€” ledger closes: no CRSP match [489 -> 366 (-123)]
ASSERT PASS â€” ledger closes: no notification date [366 -> 366 (-0)]
ASSERT PASS â€” ledger closes: beyond WRDS extract boundary [366 -> 360 (-6)]
ASSERT PASS â€” ledger closes: windows not computable [360 -> 349 (-11)]
ASSERT PASS â€” ledger closes: missing covariates [349 -> 334 (-15)]
ASSERT PASS â€” ledger closes: missing delay [334 -> 333 (-1)]
ASSERT PASS â€” ledger closes: malformed ATT-artifact records [333 -> 331 (-2)]
ASSERT PASS â€” final N is nowhere near the old draft N=891 (dedup+CRSP applied) [N=331]
ASSERT PASS â€” window-loss decomposition closes [8+0+3+0 == 11]
ASSERT PASS â€” CRSP-match failures = canonical minus matched [123 == 489 - 366]
ASSERT PASS â€” treated CRSP-match failures reconcile
ASSERT PASS â€” org-type composition sums to CRSP-fail total
ASSERT PASS â€” by-year canonical column sums to canonical N/treated
ASSERT PASS â€” by-year final column sums to final N/treated
ASSERT PASS â€” Essay 1 regression sample reproduces from the script-158 recipe and matches constants_v3 [338/104 vs constants 338/104]

==========================================================================================
PHASE B â€” DESCRIPTIVES BY TREATMENT STATUS
==========================================================================================
ASSERT PASS â€” group SDs computed independently and NOT identical (e2_vol_change) [1.0884 vs 1.1012]
ASSERT PASS â€” pooled mean reconciles to subgroup means (e2_vol_change)
ASSERT PASS â€” group SDs computed independently and NOT identical (e2_pre_sd) [1.1625 vs 1.0541]
ASSERT PASS â€” pooled mean reconciles to subgroup means (e2_pre_sd)
ASSERT PASS â€” group SDs computed independently and NOT identical (e2_post_sd) [1.0427 vs 1.0222]
ASSERT PASS â€” pooled mean reconciles to subgroup means (e2_post_sd)
ASSERT PASS â€” group SDs computed independently and NOT identical (disclosure_delay_days) [254.4334 vs 125.5262]
ASSERT PASS â€” pooled mean reconciles to subgroup means (disclosure_delay_days)
ASSERT PASS â€” group SDs computed independently and NOT identical (delay_w) [161.0944 vs 120.5801]
ASSERT PASS â€” pooled mean reconciles to subgroup means (delay_w)
ASSERT PASS â€” group SDs computed independently and NOT identical (firm_size_log) [1.2359 vs 1.3676]
ASSERT PASS â€” pooled mean reconciles to subgroup means (firm_size_log)
ASSERT PASS â€” group SDs computed independently and NOT identical (leverage) [0.1648 vs 0.2176]
ASSERT PASS â€” pooled mean reconciles to subgroup means (leverage)
ASSERT PASS â€” group SDs computed independently and NOT identical (roa) [0.0474 vs 0.1238]
ASSERT PASS â€” pooled mean reconciles to subgroup means (roa)
ASSERT PASS â€” group SDs computed independently and NOT identical (health_breach) [0.0000 vs 0.2480]
ASSERT PASS â€” pooled mean reconciles to subgroup means (health_breach)
ASSERT PASS â€” group SDs computed independently and NOT identical (prior_events) [9.1366 vs 21.1154]
ASSERT PASS â€” pooled mean reconciles to subgroup means (prior_events)
ASSERT PASS â€” post-window mean - pre-window mean == mean volatility change (treated)
ASSERT PASS â€” post-window mean - pre-window mean == mean volatility change (control)
ASSERT PASS â€” post-window mean - pre-window mean == mean volatility change (pooled)
             variable  mean_treated  sd_treated  mean_control  sd_control  mean_pooled  sd_pooled  n_treated  n_control
        e2_vol_change        0.0060      1.0884       -0.0402      1.1012      -0.0260     1.0958        102        229
            e2_pre_sd        1.7080      1.1625        1.6878      1.0541       1.6940     1.0869        102        229
           e2_post_sd        1.7139      1.0427        1.6476      1.0222       1.6680     1.0274        102        229
disclosure_delay_days      100.0490    254.4334       71.0961    125.5262      80.0181   175.7243        102        229
              delay_w       83.3745    161.0944       70.3424    120.5801      74.3583   134.2555        102        229
        firm_size_log       11.6238      1.2359        9.6211      1.3676      10.2382     1.6178        102        229
             leverage        0.7230      0.1648        0.6412      0.2176       0.6664     0.2061        102        229
                  roa        0.0239      0.0474        0.0771      0.1238       0.0607     0.1090        102        229
        health_breach        0.0000      0.0000        0.0655      0.2480       0.0453     0.2083        102        229
         prior_events       10.2157      9.1366       13.9039     21.1154      12.7674    18.3441        102        229

(The old Table A2 reported identical treated/control SDs on three variables â€” 14.2/14.2, 16.3/16.3, 1.84/1.84 â€” impossible for unequal groups; the independent SDs above replace it.)

==========================================================================================
PHASE C â€” MAIN EFFECT, NESTED MODELS, SE SPECIFICATIONS
==========================================================================================
ASSERT PASS â€” t == coef/se (M1 timing + pre-vol :: delay_w) [t=0.094188 coef/se=0.094188]
ASSERT PASS â€” p follows from t and df (M1 timing + pre-vol :: delay_w) [p=0.925017 implied=0.925017 df=328]
ASSERT PASS â€” t == coef/se (M1 timing + pre-vol :: e2_pre_sd) [t=-8.894806 coef/se=-8.894806]
ASSERT PASS â€” p follows from t and df (M1 timing + pre-vol :: e2_pre_sd) [p=0.000000 implied=0.000000 df=328]

M1 timing + pre-vol: N=331 df_resid=328 R2=0.3102
ASSERT PASS â€” t == coef/se (M2 + financial controls :: delay_w) [t=0.053508 coef/se=0.053508]
ASSERT PASS â€” p follows from t and df (M2 + financial controls :: delay_w) [p=0.957360 implied=0.957360 df=325]
ASSERT PASS â€” t == coef/se (M2 + financial controls :: e2_pre_sd) [t=-9.598777 coef/se=-9.598777]
ASSERT PASS â€” p follows from t and df (M2 + financial controls :: e2_pre_sd) [p=0.000000 implied=0.000000 df=325]
ASSERT PASS â€” t == coef/se (M2 + financial controls :: firm_size_log) [t=-1.063728 coef/se=-1.063728]
ASSERT PASS â€” p follows from t and df (M2 + financial controls :: firm_size_log) [p=0.288242 implied=0.288242 df=325]
ASSERT PASS â€” t == coef/se (M2 + financial controls :: leverage) [t=-1.042893 coef/se=-1.042893]
ASSERT PASS â€” p follows from t and df (M2 + financial controls :: leverage) [p=0.297773 implied=0.297773 df=325]
ASSERT PASS â€” t == coef/se (M2 + financial controls :: roa) [t=-1.392148 coef/se=-1.392148]
ASSERT PASS â€” p follows from t and df (M2 + financial controls :: roa) [p=0.164829 implied=0.164829 df=325]

M2 + financial controls: N=331 df_resid=325 R2=0.3163
ASSERT PASS â€” t == coef/se (M3 + treatment :: delay_w) [t=0.059785 coef/se=0.059785]
ASSERT PASS â€” p follows from t and df (M3 + treatment :: delay_w) [p=0.952363 implied=0.952363 df=324]
ASSERT PASS â€” t == coef/se (M3 + treatment :: e2_pre_sd) [t=-9.685207 coef/se=-9.685207]
ASSERT PASS â€” p follows from t and df (M3 + treatment :: e2_pre_sd) [p=0.000000 implied=0.000000 df=324]
ASSERT PASS â€” t == coef/se (M3 + treatment :: firm_size_log) [t=-1.706517 coef/se=-1.706517]
ASSERT PASS â€” p follows from t and df (M3 + treatment :: firm_size_log) [p=0.088870 implied=0.088870 df=324]
ASSERT PASS â€” t == coef/se (M3 + treatment :: leverage) [t=-1.243192 coef/se=-1.243192]
ASSERT PASS â€” p follows from t and df (M3 + treatment :: leverage) [p=0.214696 implied=0.214696 df=324]
ASSERT PASS â€” t == coef/se (M3 + treatment :: roa) [t=-1.317030 coef/se=-1.317030]
ASSERT PASS â€” p follows from t and df (M3 + treatment :: roa) [p=0.188759 implied=0.188759 df=324]
ASSERT PASS â€” t == coef/se (M3 + treatment :: fcc_form499) [t=1.157153 coef/se=1.157153]
ASSERT PASS â€” p follows from t and df (M3 + treatment :: fcc_form499) [p=0.248062 implied=0.248062 df=324]

M3 + treatment: N=331 df_resid=324 R2=0.3187
  M3 + treatment :: fcc_form499: coef +0.1451  SE 0.1254  t +1.157  df 324  p 0.2481  N 331
ASSERT PASS â€” t == coef/se (M4 + breach controls (HEADLINE) :: delay_w) [t=0.029195 coef/se=0.029195]
ASSERT PASS â€” p follows from t and df (M4 + breach controls (HEADLINE) :: delay_w) [p=0.976727 implied=0.976727 df=322]
ASSERT PASS â€” t == coef/se (M4 + breach controls (HEADLINE) :: e2_pre_sd) [t=-9.546091 coef/se=-9.546091]
ASSERT PASS â€” p follows from t and df (M4 + breach controls (HEADLINE) :: e2_pre_sd) [p=0.000000 implied=0.000000 df=322]
ASSERT PASS â€” t == coef/se (M4 + breach controls (HEADLINE) :: firm_size_log) [t=-1.697376 coef/se=-1.697376]
ASSERT PASS â€” p follows from t and df (M4 + breach controls (HEADLINE) :: firm_size_log) [p=0.090592 implied=0.090592 df=322]
ASSERT PASS â€” t == coef/se (M4 + breach controls (HEADLINE) :: leverage) [t=-1.395527 coef/se=-1.395527]
ASSERT PASS â€” p follows from t and df (M4 + breach controls (HEADLINE) :: leverage) [p=0.163819 implied=0.163819 df=322]
ASSERT PASS â€” t == coef/se (M4 + breach controls (HEADLINE) :: roa) [t=-1.213794 coef/se=-1.213794]
ASSERT PASS â€” p follows from t and df (M4 + breach controls (HEADLINE) :: roa) [p=0.225716 implied=0.225716 df=322]
ASSERT PASS â€” t == coef/se (M4 + breach controls (HEADLINE) :: fcc_form499) [t=1.125209 coef/se=1.125209]
ASSERT PASS â€” p follows from t and df (M4 + breach controls (HEADLINE) :: fcc_form499) [p=0.261339 implied=0.261339 df=322]
ASSERT PASS â€” t == coef/se (M4 + breach controls (HEADLINE) :: health_breach) [t=0.028391 coef/se=0.028391]
ASSERT PASS â€” p follows from t and df (M4 + breach controls (HEADLINE) :: health_breach) [p=0.977368 implied=0.977368 df=322]
ASSERT PASS â€” t == coef/se (M4 + breach controls (HEADLINE) :: prior_events) [t=-0.115930 coef/se=-0.115930]
ASSERT PASS â€” p follows from t and df (M4 + breach controls (HEADLINE) :: prior_events) [p=0.907780 implied=0.907780 df=322]

M4 + breach controls (HEADLINE): N=331 df_resid=322 R2=0.3188
  M4 + breach controls (HEADLINE) :: fcc_form499: coef +0.1486  SE 0.1321  t +1.125  df 322  p 0.2613  N 331
ASSERT PASS â€” t == coef/se (MAIN EFFECT (M4, HC3)) [t=1.125209 coef/se=1.125209]
ASSERT PASS â€” p follows from t and df (MAIN EFFECT (M4, HC3)) [p=0.261339 implied=0.261339 df=322]

HEADLINE: MAIN EFFECT (M4, HC3): coef +0.1486  SE 0.1321  t +1.125  df 322  p 0.2613  N 331
ASSERT PASS â€” t == coef/se (MAIN EFFECT (untrimmed delay)) [t=1.130323 coef/se=1.130323]
ASSERT PASS â€” p follows from t and df (MAIN EFFECT (untrimmed delay)) [p=0.259181 implied=0.259181 df=322]
ASSERT PASS â€” t == coef/se (delay (winsorized p99)) [t=0.029195 coef/se=0.029195]
ASSERT PASS â€” p follows from t and df (delay (winsorized p99)) [p=0.976727 implied=0.976727 df=322]
ASSERT PASS â€” t == coef/se (delay (untrimmed)) [t=-0.254773 coef/se=-0.254773]
ASSERT PASS â€” p follows from t and df (delay (untrimmed)) [p=0.799061 implied=0.799061 df=322]

Winsorization rule: delay capped at in-sample p99 = 788 days (documented). Clock note: 47 CFR 64.2011(b) starts its seven-BUSINESS-day law-enforcement clock at "reasonable determination" of the breach, not discovery, and customer notice waits a further seven business days; days_to_disclosure here is reported_date minus breach OCCURRENCE date, which measures neither statutory clock â€” it proxies total public-notification lag, and the theory should be read against that. With vs without winsorization:
  MAIN EFFECT (M4, HC3): coef +0.1486  SE 0.1321  t +1.125  df 322  p 0.2613  N 331
  MAIN EFFECT (untrimmed delay): coef +0.1499  SE 0.1326  t +1.130  df 322  p 0.2592  N 331
  delay (winsorized p99): coef +0.0000  SE 0.0003  t +0.029  df 322  p 0.9767  N 331
  delay (untrimmed): coef -0.0000  SE 0.0002  t -0.255  df 322  p 0.7991  N 331

SE specifications for the M4 treatment coefficient (the old draft scaled every t by 0.8806 â€” coef and t/p came from different runs; here each row is one fit):
ASSERT PASS â€” t == coef/se (classical OLS) [t=1.063931 coef/se=1.063931]
ASSERT PASS â€” p follows from t and df (classical OLS) [p=0.288157 implied=0.288157 df=322]
ASSERT PASS â€” t == coef/se (HC1) [t=1.140170 coef/se=1.140170]
ASSERT PASS â€” p follows from t and df (HC1) [p=0.255063 implied=0.255063 df=322]
ASSERT PASS â€” t == coef/se (HC3) [t=1.125209 coef/se=1.125209]
ASSERT PASS â€” p follows from t and df (HC3) [p=0.261339 implied=0.261339 df=322]
ASSERT PASS â€” t == coef/se (firm-clustered) [t=0.735367 coef/se=0.735367]
ASSERT PASS â€” p follows from t and df (firm-clustered) [p=0.464267 implied=0.464267 df=80]
ASSERT PASS â€” t == coef/se (industry-clustered (N=331)) [t=0.968203 coef/se=0.968203]
ASSERT PASS â€” p follows from t and df (industry-clustered (N=331)) [p=0.342600 implied=0.342600 df=24]
  classical OLS: coef +0.1486  SE 0.1397  t +1.064  df 322  p 0.2882  N 331
  HC1: coef +0.1486  SE 0.1303  t +1.140  df 322  p 0.2551  N 331
  HC3: coef +0.1486  SE 0.1321  t +1.125  df 322  p 0.2613  N 331
  firm-clustered: coef +0.1486  SE 0.2021  t +0.735  df 80  p 0.4643  N 331  clusters=81
  industry-clustered (N=331): coef +0.1486  SE 0.1535  t +0.968  df 24  p 0.3426  N 331  clusters=25
  Cluster counts: firm 81 (meets the ~40-50 convention), industry 25 2-digit-SIC clusters (BELOW the conventional ~40-50 threshold for asymptotic cluster-robust inference â€” treat industry-clustered p with caution).

==========================================================================================
PHASE D â€” FIRM-SIZE HETEROGENEITY (quartiles of log total assets)
==========================================================================================
ASSERT PASS â€” t == coef/se (quartile Q1 (smallest)) [t=-3.031280 coef/se=-3.031280]
ASSERT PASS â€” p follows from t and df (quartile Q1 (smallest)) [p=0.003342 implied=0.003342 df=75]
  quartile Q1 (smallest): coef -0.9894  SE 0.3264  t -3.031  df 75  p 0.0033  N 83  treated 2 obs / 1 orgs / 1 parent CIKs  MDE80 0.91pp  FEWER THAN 5 TREATED PARENT CIKs (1) â€” do not interpret bare
ASSERT PASS â€” t == coef/se (quartile Q2) [t=0.919806 coef/se=0.919806]
ASSERT PASS â€” p follows from t and df (quartile Q2) [p=0.360623 implied=0.360623 df=75]
  quartile Q2: coef +0.3000  SE 0.3262  t +0.920  df 75  p 0.3606  N 84  treated 14 obs / 8 orgs / 4 parent CIKs  MDE80 0.91pp  FEWER THAN 5 TREATED PARENT CIKs (4) â€” do not interpret bare
ASSERT PASS â€” t == coef/se (quartile Q3) [t=2.201971 coef/se=2.201971]
ASSERT PASS â€” p follows from t and df (quartile Q3) [p=0.030871 implied=0.030871 df=72]
  quartile Q3: coef +0.7022  SE 0.3189  t +2.202  df 72  p 0.0309  N 81  treated 27 obs / 12 orgs / 3 parent CIKs  MDE80 0.89pp  FEWER THAN 5 TREATED PARENT CIKs (3) â€” do not interpret bare
ASSERT PASS â€” t == coef/se (quartile Q4 (largest)) [t=1.889872 coef/se=1.889872]
ASSERT PASS â€” p follows from t and df (quartile Q4 (largest)) [p=0.062692 implied=0.062692 df=74]
  quartile Q4 (largest): coef +0.3485  SE 0.1844  t +1.890  df 74  p 0.0627  N 83  treated 59 obs / 19 orgs / 5 parent CIKs  MDE80 0.52pp  
ASSERT PASS â€” quartile Ns sum to full sample N [331 == 331]

Prior-breach count reconstruction (records vs events â€” substantive finding, not a silent fix):
                                                                                 measure   n  mean    sd  p50  p90  max
                                   NEW: prior deduplicated events (canonical, regressor) 331 12.77 18.34  4.0 42.0   75
OLD-STYLE regenerated: prior notification RECORDS (sum n_source_records of prior events) 331 17.21 23.91  5.0 53.0   94
        OLD DRAFT (quoted, NOT regenerable: computed on pre-dedup records, N=891 sample) 891  3.65   NaN  NaN  NaN   68
NOTE: the canonical count is per PARENT CIK (post entity-resolution), so large carrier families accumulate more prior events than the old org-name-string count even after dedup â€” the two differences (dedup, parent aggregation) move in opposite directions.

==========================================================================================
PHASE E â€” MODERATORS AND ROBUSTNESS
==========================================================================================
                         moderator          status n                                                                                                                                                                                                                                 reason
          Breach complexity (CVSS) NOT REGENERABLE 0 NVD/CVSS columns and scripts (99, 105) retired at Rebuild Stage 0; no CVE linkage exists in CANONICAL_V3. The old claim that this ran on the full N=891 while being defined only for CVE-linked breaches was internally contradictory.
                    Media coverage NOT REGENERABLE 0                                                                                                       Constructed on the pre-audit dataset (script 101); source columns absent from CANONICAL_V3; no committed pipeline produces them.
Governance quality (SOX 404 proxy) NOT REGENERABLE 0                                                                                                                                                                                Old-draft construct; no source data in canonical chain.
 Information-environment composite NOT REGENERABLE 0                                                  Script 106 construct on pre-audit base. The old draft reported p=.275 in prose vs p=.0589 in the table for this interaction â€” neither value survives; retired, not carried forward.
               Reputation weakness NOT REGENERABLE 0                                                                                        Old-draft construct (its table row also printed R2=.0156 against ~.39 for every other row â€” a different-model artifact); no canonical source.
ASSERT PASS â€” t == coef/se (year FE) [t=0.726614 coef/se=0.726614]
ASSERT PASS â€” p follows from t and df (year FE) [p=0.468020 implied=0.468020 df=305]
  year FE: coef +0.1053  SE 0.1450  t +0.727  df 305  p 0.4680  N 331  R2=0.4377
ASSERT PASS â€” t == coef/se (industry FE (2-digit SIC)) [t=2.057508 coef/se=2.057508]
ASSERT PASS â€” p follows from t and df (industry FE (2-digit SIC)) [p=0.040507 implied=0.040507 df=298]
  industry FE (2-digit SIC): coef +0.3649  SE 0.1773  t +2.058  df 298  p 0.0405  N 331  R2=0.3776
ASSERT PASS â€” t == coef/se (year + industry FE) [t=0.751466 coef/se=0.751466]
ASSERT PASS â€” p follows from t and df (year + industry FE) [p=0.453001 implied=0.453001 df=281]
  year + industry FE: coef +0.1379  SE 0.1835  t +0.751  df 281  p 0.4530  N 331  R2=0.508
  Identification check: the combined year+industry FE treatment coefficient is IDENTIFIED (SE finite at 0.184) â€” an improvement over the old draft, whose combined specification collapsed because SIC-based treatment was a function of three SIC codes. BUT the identification is THIN: only 2 of 25 2-digit-SIC cells contain both treated and control events, so the within-industry comparison rests on those 2 cells. The industry-FE-only estimate (p=0.0405) leans on the same thin variation and on 25 clusters (below the ~40-50 convention) â€” do not headline it.

VIF (M4 design):
     variable  VIF
      delay_w 1.05
    e2_pre_sd 1.17
firm_size_log 1.67
     leverage 1.11
          roa 1.49
  fcc_form499 1.64
health_breach 1.09
 prior_events 1.41

Breusch-Pagan (stated ONCE, used everywhere): chi2(8) = 8.2886, p = 0.4058. (The old draft printed chi2=3.92/p=.049 in prose and 15.5838/p=.0487 in its table â€” both retired.)
Jarque-Bera residual normality: JB = 2194.9, p = 0.00e+00, skew 2.65, kurtosis 14.45 â€” heavy-tailed; HC3 primary inference stands, normality rejected as expected for volatility data.
ASSERT PASS â€” t == coef/se (M4 excl. Cook's D > 4/N (18 obs)) [t=0.786717 coef/se=0.786717]
ASSERT PASS â€” p follows from t and df (M4 excl. Cook's D > 4/N (18 obs)) [p=0.432060 implied=0.432060 df=304]

Influence: 18 obs with Cook's D > 4/N (0.0121); 18 with |DFFITS| > 0.330.
  M4 excl. Cook's D > 4/N (18 obs): coef +0.0676  SE 0.0859  t +0.787  df 304  p 0.4321  N 313

GARCH(1,1) conditional-volatility DV (Gaussian MLE, Nelder-Mead; estimation window trading days [-250,+25] around the anchor, min 200 obs; DV = mean conditional SD over [+5,+25] minus [-25,-5], daily pp):
ASSERT PASS â€” t == coef/se (GARCH(1,1) DV (N=328)) [t=0.647875 coef/se=0.647875]
ASSERT PASS â€” p follows from t and df (GARCH(1,1) DV (N=328)) [p=0.517532 implied=0.517532 df=319]
  GARCH(1,1) DV (N=328): coef +0.0476  SE 0.0734  t +0.648  df 319  p 0.5175  N 328
ASSERT PASS â€” t == coef/se (canonical DV, HC3 (N=331)) [t=1.929886 coef/se=1.929886]
ASSERT PASS â€” p follows from t and df (canonical DV, HC3 (N=331)) [p=0.054499 implied=0.054499 df=322]
ASSERT PASS â€” t == coef/se (canonical DV, firm-clustered) [t=1.519415 coef/se=1.519415]
ASSERT PASS â€” p follows from t and df (canonical DV, firm-clustered) [p=0.132600 implied=0.132600 df=80]

DV-convention sensitivity (canonical breach-anchored annualized DV, the convention the old CODE actually used, on THIS sample and control set; corr with the draft-spec DV = 0.451):
  canonical DV, HC3 (N=331): coef +3.5185  SE 1.8232  t +1.930  df 322  p 0.0545  N 331
  canonical DV, firm-clustered: coef +3.5185  SE 2.3157  t +1.519  df 80  p 0.1326  N 331  clusters=81
  Under the old code's convention the effect is +3.52 annualized pp (p=0.0545 HC3) but dies under firm clustering (p=0.1326) â€” the same pattern as the v3 baseline H5 (Essay 2's hypothesis in constants_v3: +3.29, p=.063, estimated under this same breach-anchored convention).

  Breach-to-notification delay (N=331): min 0 | p10 0 | p25 0 | median 23 | p75 79.5 | p90 201 | max 1917 | mean 80.0 | SD 175.7
  all: window fully pre-notification 45.3% | contains notification 54.7% | mean 56.4% (median 74.2%) of window days precede notification
  treated: window fully pre-notification 47.1% | contains notification 52.9% | mean 53.7% (median 71.0%) of window days precede notification
  control: window fully pre-notification 44.5% | contains notification 55.5% | mean 57.6% (median 77.4%) of window days precede notification
  CONSTRUCT VERDICT: a strict majority of observations does NOT have the window close before notification (45.6% do), but a majority of what the measure contains is pre-notification volatility â€” 56.7% of all measured post-window days precede public notification, and the median observation has 74% of its "post" window before the market learned anything. The breach-anchored DV is disqualified as a measure of post-DISCLOSURE uncertainty on construct validity: it mostly measures volatility before the event it claims to measure. The treated/control difference in truncation is trivial (47.1% vs 45.0% fully-pre; treated windows contain slightly MORE post-notification days, 46.3% vs 42.0%), so there is no mechanical treatment-correlated measurement bias on top â€” the disqualification is construct-wide, not treatment-differential.

==========================================================================================
PHASE F â€” INFERENCE QUALITY
==========================================================================================
  MAIN EFFECT (M4, HC3): TOST(Â±0.1323 daily pp = Â±2.10 annualized) p=0.5491  MDE80=0.3698pp  -> NULL â€” UNDERPOWERED (inconclusive)
  quartile Q1 (smallest): TOST(Â±0.1323 daily pp = Â±2.10 annualized) p=0.9948  MDE80=0.9139pp  -> SIGNIFICANT [1 treated parent CIKs â€” do not interpret bare]
  quartile Q2: TOST(Â±0.1323 daily pp = Â±2.10 annualized) p=0.6957  MDE80=0.9134pp  -> NULL â€” UNDERPOWERED (inconclusive) [4 treated parent CIKs â€” do not interpret bare]
  quartile Q3: TOST(Â±0.1323 daily pp = Â±2.10 annualized) p=0.9609  MDE80=0.8929pp  -> SIGNIFICANT [3 treated parent CIKs â€” do not interpret bare]
  quartile Q4 (largest): TOST(Â±0.1323 daily pp = Â±2.10 annualized) p=0.8776  MDE80=0.5163pp  -> NULL â€” UNDERPOWERED (inconclusive)

  BOUND PROVENANCE: the Â±2.10pp bound was pre-specified for Essay 1's CAR outcome ("fixed from literature before rebuilt estimates existed", scripts/158) and was never independently justified as a smallest volatility effect of interest â€” its use here is a unit conversion only, stated as such.
  LITERATURE-ANCHORED CHECK (conditional): against a candidate SESOI of 4.2pp annualized (0.2646 daily pp), TOST p=0.1902 â€” still not equivalence-bounded. MDE80 = 0.3698 daily pp = 5.87pp annualized, which EXCEEDS 4.2pp: this design cannot detect, at 80% power, even the effect size used as the literature anchor. CAVEAT: the 4.2pp figure attributed to Obaydin, Xu & Zurbruegg (2024) could not be verified in the repository's article summary â€” their JBFA 2024 paper reports crash-risk effects (NSKEW/DUVOL/COUNT, >=5% of a SD) and bad-news-hoarding proxies, not a post-breach volatility change in pp. No commensurable volatility-native SESOI has been located in the prior literature on file; until one is, the defensible sentence is the MDE one, not any TOST verdict.

Economic significance: main effect +0.1486 daily pp = +8.9% of mean post-breach volatility (1.6680 daily pp). Incremental R2 from the treatment indicator: +0.0024 (M4 0.3188 vs without-treatment 0.3164). (Old draft: .3922 vs .3896 â€” about a quarter of one percent.)

==========================================================================================
OLD-DRAFT LEAK CHECK AND CODEBASE FLAGS
==========================================================================================
No regenerated coefficient reproduces any old-draft value (+1.83, +7.31, +3.64, -3.39, -0.54, +1.763, +2.48, +4.074, +1.894, +0.7956) to within 0.005 â€” no evidence of old-number leakage.

FORENSIC â€” old-draft provenance closure (nothing here is a result; pre-dedup data, SIC-based fcc_reportable treatment, both retired):
  N=891 (reproduces the old draft's 891 exactly from the PRE-dedup ENRICHED file) | main FCC +1.6121 p=0.0772 (old draft: +1.83 / +1.763)
  Q1: +7.6515 (p=0.0060, N=229) vs old draft +7.31
  Q2: +2.8621 (p=0.0725, N=224) vs old draft +3.64
  Q3: -2.0526 (p=0.3707, N=215) vs old draft -0.54
  Q4: -3.5119 (p=0.0236, N=223) vs old draft -3.39
  The +7.31/+3.64/-0.54/-3.39 step-down REPRODUCES in sign, ordering, and approximate magnitude (+7.65/+2.86/-2.05/-3.51 under the full old control set) â€” the old quartile numbers are the pre-deduplication + SIC-treatment artifact, not a third-source mystery. Provenance closed. On corrected data the pattern does not exist (Phase D).

Codebase flags (directive): "September 28 2007"/"Rule 37.3" and SIC-code treatment (4813/4841/4899) appear ONLY in retired pre-rebuild scripts (83, 94, 20, build_essay1_*, create_*, scm_*, fix/rebuild_essay1_appendix, boost_mobile_forensics, consolidate_validation_results, and chronology-side scripts 131/137) and in script 142's note deliberately documenting the retirement. NO live v3-chain script (150-158) or this script assigns treatment by SIC or references the wrong date/rule.

==========================================================================================
PIPELINE FINDINGS (item 5 â€” things not already named in the directive)
==========================================================================================
1. FINAL_DATASET_ORIGINAL_1054.csv contained 784 rows, not 1,054 â€” misnamed
   (a vintage of the retired dedup set; script 142's docstring had already
   documented this). RENAMED 8/30/2026 to
   FINAL_DATASET_ORIGINAL_1054_MISNAMED_RETIRED.csv; no script reads it; the
   true 1,054-record universe is rebuild/stage2_signed.csv (and
   master_breach_dataset.xlsx).
2. has_crsp_data in CANONICAL_V3 is defined by car_30d computability
   (breach-anchored), not by security match: 12 events carry a
   permno but has_crsp_data = 0. Essay 2's notification-anchored windows are
   computable for some of these, so this rerun keys on permno + its own
   window requirement rather than reusing has_crsp_data â€” the two essays'
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
   926 CRSP) under the old spec's dropna â€” the old Essay 2 ran on duplicate
   notification records and pre-resolution identities.
7. The old Essay 2 CODE never implemented the draft's stated volatility
   windows: scripts 20/90/90b used the breach-anchored annualized
   [-40,-1]/[0,+30] convention; the [-25,-5]/[+5,+25] language exists only
   in create_regression_formulas_document.py, the same file that carries
   "Rule 37.3", SIC-code treatment, and "January 1, 2007" (a THIRD wrong
   rule date). The draft's methods prose described a measure that was never
   computed. See the DV-convention sensitivity in Phase E.

Total reconciliation/consistency assertions passed: 132
