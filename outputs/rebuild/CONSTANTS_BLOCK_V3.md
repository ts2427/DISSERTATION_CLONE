# CONSTANTS BLOCK v3 — Rebuilt base (8/4/2026)

Every value below regenerates from run_all (scripts 150-158) off the 1,054-record universe; assertion baseline in constants_v3.json.

- **events_total**: 489
- **events_crsp**: 356
- **N_regression**: 340
- **treated_total**: 118
- **treated_crsp**: 111
- **treated_regression**: 106
- **treated_orgs_regression**: 36
- **treated_parent_ciks_regression**: 12
- **H2_FCC_coef**: -0.8051
- **H2_FCC_p**: 0.5659
- **H2_FCC_ci**: [np.float64(-3.5541), np.float64(1.9438)]
- **H2_FCC_mde80**: 3.9272
- **H2_FCC_tost_p**: 0.1783
- **H2_FCC_status**: NULL-INCONCLUSIVE
- **H1_timing_coef**: 1.15
- **H1_timing_p**: 0.2526
- **H1_timing_ci**: [np.float64(-0.82), np.float64(3.12)]
- **H1_timing_mde80**: 2.8143
- **H1_timing_tost_p**: 0.1726
- **H1_timing_status**: NULL-INCONCLUSIVE
- **H3_prior_coef**: 0.0332
- **H3_prior_p**: 0.6063
- **H3_prior_ci**: [np.float64(-0.0931), np.float64(0.1594)]
- **H3_prior_mde80**: 0.1804
- **H3_prior_tost_p**: 0.0
- **H3_prior_status**: BOUNDED NULL
- **H4_health_coef**: -1.0247
- **H4_health_p**: 0.6944
- **H4_health_ci**: [np.float64(-6.137), np.float64(4.0875)]
- **H4_health_mde80**: 7.3034
- **H4_health_tost_p**: 0.3402
- **H4_health_status**: NULL-INCONCLUSIVE
- **ROA_coef**: 7.353
- **ROA_p**: 0.175
- **AMEND_opmargin_coef**: 8.2816
- **AMEND_opmargin_p**: 0.058
- **AMEND_both_roa_p**: 0.4776
- **AMEND_both_opmargin_p**: 0.087
- **AMEND_nulls_unchanged**: True
- **first_stage_pp**: 15.26
- **prior_breach_obs_share**: 0.7584
- **prior_breach_firm_share**: 0.5455
- **immediate_share_full**: 0.3285
- **immediate_share_crsp**: 0.3662
- **immediate_share_regression**: 0.3647
- **health_events_crsp**: 15
- **T2_treated_N**: 118
- **T2_treated_median_gap**: 15.0
- **T2_treated_mean_gap**: 22.44
- **T2_treated_share_8k_90d**: 0.9915
- **T2_untreated_N**: 219
- **T2_untreated_median_gap**: 26.0
- **T2_untreated_mean_gap**: 30.16
- **T2_untreated_share_8k_90d**: 0.9178
- **car30d_regression_mean**: -0.281
- **car30d_regression_median**: 0.1423
- **T3_filer_median**: -0.437
- **T3_nonfiler_median**: 0.4118
- **T3_immediate_median**: 1.0849
- **T3_delayed_median**: -0.461
- **T3_health_median**: 0.4276
- **T3_nonhealth_median**: 0.14
- **T3_any_prior_median**: 0.4212
- **T3_no_prior_median**: -0.6034
- **T6_treated_timing_coef**: -0.2202
- **T6_treated_timing_se**: 1.8879
- **T6_treated_timing_p**: 0.9071
- **T6_treated_N**: 106
- **T6_untreated_timing_coef**: 1.9307
- **T6_untreated_timing_se**: 1.1916
- **T6_untreated_timing_p**: 0.1052
- **T6_untreated_N**: 234
- **T6_interaction_coef**: -2.3776
- **T6_interaction_se**: 2.1868
- **T6_interaction_p**: 0.2769
- **volume_fcc_coef**: 0.1064
- **volume_fcc_p**: 0.0446
- **RF_top_feature**: roa
- **T16_ann_excluded_no_reported**: 1
- **T16_breach_N**: 356
- **T16_breach_excluded_history**: 0
- **T16_ann_N**: 355
- **T16_ann_excluded_history**: 0
- **T16_breach_m30_m21_mean**: -0.143
- **T16_breach_m30_m21_p**: 0.5999
- **T16_breach_m30_m21_diff_p**: 0.6208
- **T16_breach_m20_m11_mean**: 0.7709
- **T16_breach_m20_m11_p**: 0.0167
- **T16_breach_m20_m11_diff_p**: 0.3258
- **T16_breach_m10_m1_mean**: 0.0414
- **T16_breach_m10_m1_p**: 0.8941
- **T16_breach_m10_m1_diff_p**: 0.0506
- **T16_ann_m30_m21_mean**: -0.0183
- **T16_ann_m30_m21_p**: 0.9456
- **T16_ann_m30_m21_diff_p**: 0.8173
- **T16_ann_m20_m11_mean**: 0.303
- **T16_ann_m20_m11_p**: 0.2658
- **T16_ann_m20_m11_diff_p**: 0.058
- **T16_ann_m10_m1_mean**: -0.3361
- **T16_ann_m10_m1_p**: 0.2555
- **T16_ann_m10_m1_diff_p**: 0.0301

==========================================================================================
REBUILD STAGE 8: FULL REGENERATION
==========================================================================================

Samples: 489 events | CRSP 356 | regression 340 (106 treated, 12 parent CIKs)

Essay 1 (H1-H4, HC3):
  H2_FCC: -0.8051pp p=0.5659 | TOST(±2.10) p=0.1783 | MDE 3.93 | NULL-INCONCLUSIVE
  H1_timing: +1.1500pp p=0.2526 | TOST(±2.10) p=0.1726 | MDE 2.81 | NULL-INCONCLUSIVE
  H3_prior: +0.0332pp p=0.6063 | TOST(±2.10) p=0.0000 | MDE 0.18 | BOUNDED NULL
  H4_health: -1.0247pp p=0.6944 | TOST(±2.10) p=0.3402 | MDE 7.30 | NULL-INCONCLUSIVE
  ROA: +7.3530 p=0.1750

ROA amendment: op_margin +8.2816 p=0.0580 (N=340); both-spec roa p=0.4776 / op_margin p=0.0870; hypothesis nulls unchanged: True

First stage (descriptive): treated immediate-disclosure share exceeds untreated by +15.26pp

Appendix v3 tables...
  Table 2 disclosure verification: treated N=118 (median gap 15.0d, share 99%); untreated N=219 (median 26.0d, share 92%)
  Table 6 timing-by-regime: treated -0.2202 p=0.9071 (N=106); untreated +1.9307 p=0.1052 (N=234); interaction -2.3776 p=0.2769
  Table 16 leakage: breach panel N=356 (excl 0 history); ann panel N=355 (excl 1 no-reported + 0 history)
  16 tables (citation order, captioned) -> outputs/rebuild/appendix_v3/

Baseline constants_v3.json WRITTEN (future runs assert against it)