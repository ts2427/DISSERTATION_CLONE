# PENDING REBASELINE — constants_v3.json vs today's CANONICAL_V3 (NOT APPLIED)

Generated 2026-09-11 by scripts/193_essay3_q2_pending_rebaseline.py from outputs/essay3_q2/a3_constants_diff.csv (scripts/186: script 158 re-run in a throwaway sandbox). **Nothing here has been applied. constants_v3.json is unmodified. Do not run run_all or script 158 until the rebaseline is decided: 158 asserts against constants_v3.json and will fail on today's file.**

## Vintage gap (logged 2026-09-11)

- **Essay 3** (Query 2 Stage 2, pending): runs on **today's CANONICAL_V3** — Essay 3 regression sample 340 (106 treated events, 12 treated parent CIKs), DISH (CIK 1001082) treated from 2020-07-01 (scripts/154:129, 9/4 adjudication; CRSP top-up scripts/179). Results go to a separate Essay 3 constants file, not constants_v3.json.
- **Essay 1 and the v3 Essay 2/3 blocks in constants_v3.json**: the **pre-top-up** file — Essay 1 regression 338 (104 treated, 11 treated parent CIKs), N_essay2 337, N_essay3 338; DISH's two 2023 events absent (no CRSP data at that vintage).
- **Essay 2 authoritative artifacts** (scripts/163 chain, outputs/ESSAY2_SAMPLE_ATTRITION_LEDGER.md, commit b11e884) are already on the topped-up file (333; 104 treated, 12 parent CIKs) and are not affected by this ledger.
- Scope of the gap: **94 of 121** committed constants change; the treated counts move by exactly DISH's two events at every level.

## Essay 1 H1–H4 and ROA: committed vs today (verdict-change flags)

| Test | Coef committed | Coef today | p committed | p today | Status committed | Status today | TOST p committed | TOST p today | Flag |
|---|---|---|---|---|---|---|---|---|---|
| H1 timing (immediate disclosure) | 0.9641 | 1.4143 | 0.3298 | 0.1712 | NULL-INCONCLUSIVE | NULL-INCONCLUSIVE | 0.1259 | 0.2538 | no verdict change |
| H2 Form 499 treatment | -0.2663 | -0.4994 | 0.8404 | 0.7326 | NULL-INCONCLUSIVE | NULL-INCONCLUSIVE | 0.0833 | 0.1371 | no verdict change |
| H3 prior breaches | 0.0238 | 0.0258 | 0.7092 | 0.6916 | BOUNDED NULL | BOUNDED NULL | 0.0 | 0.0 | no verdict change |
| H4 health breach | -1.0553 | -0.9405 | 0.687 | 0.7176 | NULL-INCONCLUSIVE | NULL-INCONCLUSIVE | 0.3451 | 0.328 | no verdict change |
| ROA (control) | 7.6509 | 7.7592 | 0.1596 | 0.1533 | — | — |  |  | no verdict change (not significant at .05 or .10 in either vintage: 0.1596 -> 0.1533) |

Verdict-change rule: a flag is raised if the status label changes, the p-value crosses .05 or .10, the coefficient changes sign, or the TOST (±2.10pp) p-value crosses .05.

## Also flagged: script 158's Essay 2 volatility block

- H5 (158's breach-anchored annualized volatility spec): N 337 -> 339, coef 3.2897 -> 3.9442, p 0.063 -> 0.0292, status **NULL-INCONCLUSIVE -> SIGNIFICANT**. Essay 2's authoritative chain disqualifies this specification on construct validity (outputs/ESSAY2_APPENDIX_TABLES_FORM499.md:16-21). Retire or relabel this block before script 158 runs again.

## All 94 changed constants

| Key | Committed | Today | Delta |
|---|---|---|---|
| events_crsp | 354 | 356 | 2.0 |
| N_regression | 338 | 340 | 2.0 |
| treated_total | 116 | 118 | 2.0 |
| treated_crsp | 109 | 111 | 2.0 |
| treated_regression | 104 | 106 | 2.0 |
| treated_orgs_regression | 35 | 36 | 1.0 |
| treated_parent_ciks_regression | 11 | 12 | 1.0 |
| H2_FCC_coef | -0.2663 | -0.4994 | -0.2331 |
| H2_FCC_p | 0.8404 | 0.7326 | -0.1078 |
| H2_FCC_ci | [-2.8583, 2.3258] | [-3.3642, 2.3653] |  |
| H2_FCC_mde80 | 3.703 | 4.0926 | 0.3896 |
| H2_FCC_tost_p | 0.0833 | 0.1371 | 0.0538 |
| H1_timing_coef | 0.9641 | 1.4143 | 0.4502 |
| H1_timing_p | 0.3298 | 0.1712 | -0.1586 |
| H1_timing_ci | [-0.975, 2.9032] | [-0.6117, 3.4402] |  |
| H1_timing_mde80 | 2.7702 | 2.8942 | 0.124 |
| H1_timing_tost_p | 0.1259 | 0.2538 | 0.1279 |
| H3_prior_coef | 0.0238 | 0.0258 | 0.002 |
| H3_prior_p | 0.7092 | 0.6916 | -0.0176 |
| H3_prior_ci | [-0.1012, 0.1488] | [-0.1015, 0.153] |  |
| H3_prior_mde80 | 0.1786 | 0.1818 | 0.0032 |
| H4_health_coef | -1.0553 | -0.9405 | 0.1148 |
| H4_health_p | 0.687 | 0.7176 | 0.0306 |
| H4_health_ci | [-6.1892, 4.0787] | [-6.0366, 4.1556] |  |
| H4_health_mde80 | 7.3343 | 7.2803 | -0.054 |
| H4_health_tost_p | 0.3451 | 0.328 | -0.0171 |
| ROA_coef | 7.6509 | 7.7592 | 0.1083 |
| ROA_p | 0.1596 | 0.1533 | -0.0063 |
| AMEND_opmargin_coef | 7.5 | 7.8076 | 0.3076 |
| AMEND_opmargin_p | 0.0851 | 0.0773 | -0.0078 |
| AMEND_both_roa_p | 0.3868 | 0.4001 | 0.0133 |
| AMEND_both_opmargin_p | 0.134 | 0.1265 | -0.0075 |
| N_essay2 | 337 | 339 | 2.0 |
| H5_coef | 3.2897 | 3.9442 | 0.6545 |
| H5_p | 0.063 | 0.0292 | -0.0338 |
| H5_tost_p | 0.7491 | 0.8456 | 0.0965 |
| H5_mde80 | 4.9536 | 5.0651 | 0.1115 |
| H5_status | NULL-INCONCLUSIVE | SIGNIFICANT |  |
| H5_R2 | 0.551 | 0.529 | -0.022 |
| N_essay3 | 338 | 340 | 2.0 |
| H6_30d_base_rate | 0.1716 | 0.1706 | -0.001 |
| H6_30d_ame_pp | 7.37 | 6.85 | -0.52 |
| H6_30d_p | 0.1741 | 0.2028 | 0.0287 |
| H6_30d_mde80_pp | 15.19 | 15.07 | -0.12 |
| H6_90d_base_rate | 0.432 | 0.4324 | 0.0004 |
| H6_90d_ame_pp | 9.97 | 9.88 | -0.09 |
| H6_90d_p | 0.156 | 0.1566 | 0.0006 |
| H6_90d_mde80_pp | 19.67 | 19.53 | -0.14 |
| H6_180d_base_rate | 0.6982 | 0.7 | 0.0018 |
| H6_180d_ame_pp | 4.77 | 5.46 | 0.69 |
| H6_180d_p | 0.4941 | 0.4294 | -0.0647 |
| H6_180d_mde80_pp | 19.51 | 19.33 | -0.18 |
| first_stage_pp | 15.05 | 15.26 | 0.21 |
| prior_breach_obs_share | 0.7599 | 0.7584 | -0.0015 |
| prior_breach_firm_share | 0.5402 | 0.5455 | 0.0053 |
| immediate_share_crsp | 0.3654 | 0.3662 | 0.0008 |
| immediate_share_regression | 0.3639 | 0.3647 | 0.0008 |
| volume_fcc_coef | 0.0779 | 0.1064 | 0.0285 |
| volume_fcc_p | 0.1167 | 0.0446 | -0.0721 |
| T16_breach_N | 354 | 356 | 2.0 |
| T16_ann_N | 353 | 355 | 2.0 |
| T16_breach_m30_m21_mean | -0.0733 | -0.143 | -0.0697 |
| T16_breach_m30_m21_p | 0.7854 | 0.5999 | -0.1855 |
| T16_breach_m30_m21_diff_p | 0.8738 | 0.6208 | -0.253 |
| T16_breach_m20_m11_mean | 0.8012 | 0.7709 | -0.0303 |
| T16_breach_m20_m11_p | 0.0131 | 0.0167 | 0.0036 |
| T16_breach_m20_m11_diff_p | 0.3943 | 0.3258 | -0.0685 |
| T16_breach_m10_m1_mean | 0.0876 | 0.0414 | -0.0462 |
| T16_breach_m10_m1_p | 0.7781 | 0.8941 | 0.116 |
| T16_breach_m10_m1_diff_p | 0.0301 | 0.0506 | 0.0205 |
| T16_ann_m30_m21_mean | 0.0436 | -0.0403 | -0.0839 |
| T16_ann_m30_m21_p | 0.8686 | 0.8808 | 0.0122 |
| T16_ann_m30_m21_diff_p | 0.5794 | 0.902 | 0.3226 |
| T16_ann_m20_m11_mean | 0.3571 | 0.3213 | -0.0358 |
| T16_ann_m20_m11_p | 0.1911 | 0.2389 | 0.0478 |
| T16_ann_m20_m11_diff_p | 0.108 | 0.0739 | -0.0341 |
| T16_ann_m10_m1_mean | -0.2905 | -0.3581 | -0.0676 |
| T16_ann_m10_m1_p | 0.3223 | 0.2273 | -0.095 |
| T16_ann_m10_m1_diff_p | 0.015 | 0.0401 | 0.0251 |
| car30d_regression_mean | -0.1581 | -0.2052 | -0.0471 |
| T3_immediate_median | 1.3985 | 1.4152 | 0.0167 |
| T3_delayed_median | -0.4593 | -0.461 | -0.0017 |
| T3_any_prior_median | 0.4465 | 0.567 | 0.1205 |
| T3_no_prior_median | -0.5372 | -0.6034 | -0.0662 |
| T6_treated_timing_coef | -0.7835 | 0.5562 | 1.3397 |
| T6_treated_timing_se | 1.8085 | 2.0246 | 0.2161 |
| T6_treated_timing_p | 0.6648 | 0.7835 | 0.1187 |
| T6_treated_N | 104 | 106 | 2.0 |
| T6_interaction_coef | -3.0166 | -1.6411 | 1.3755 |
| T6_interaction_se | 2.1039 | 2.2995 | 0.1956 |
| T6_interaction_p | 0.1516 | 0.4754 | 0.3238 |
| T2_treated_N | 116 | 118 | 2.0 |
| T2_treated_mean_gap | 22.46 | 22.44 | -0.02 |
| T2_treated_share_8k_90d | 0.9914 | 0.9915 | 0.0001 |

Unchanged keys (27): events_total, H2_FCC_status, H1_timing_status, H3_prior_tost_p, H3_prior_status, H4_health_status, AMEND_nulls_unchanged, immediate_share_full, health_events_crsp, RF_top_feature, T16_ann_excluded_no_reported, T16_breach_excluded_history, T16_ann_excluded_history, car30d_regression_median, T3_filer_median, T3_nonfiler_median, T3_health_median, T3_nonhealth_median, T6_untreated_timing_coef, T6_untreated_timing_se, T6_untreated_timing_p, T6_untreated_N, T2_treated_median_gap, T2_untreated_N, T2_untreated_median_gap, T2_untreated_mean_gap, T2_untreated_share_8k_90d.
