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
- **H2_FCC_coef**: -0.4994
- **H2_FCC_p**: 0.7326
- **H2_FCC_ci**: [np.float64(-3.3642), np.float64(2.3653)]
- **H2_FCC_mde80**: 4.0926
- **H2_FCC_tost_p**: 0.1371
- **H2_FCC_status**: NULL-INCONCLUSIVE
- **H1_timing_coef**: 1.4143
- **H1_timing_p**: 0.1712
- **H1_timing_ci**: [np.float64(-0.6117), np.float64(3.4402)]
- **H1_timing_mde80**: 2.8942
- **H1_timing_tost_p**: 0.2538
- **H1_timing_status**: NULL-INCONCLUSIVE
- **H3_prior_coef**: 0.0258
- **H3_prior_p**: 0.6916
- **H3_prior_ci**: [np.float64(-0.1015), np.float64(0.153)]
- **H3_prior_mde80**: 0.1818
- **H3_prior_tost_p**: 0.0
- **H3_prior_status**: BOUNDED NULL
- **H4_health_coef**: -0.9405
- **H4_health_p**: 0.7176
- **H4_health_ci**: [np.float64(-6.0366), np.float64(4.1556)]
- **H4_health_mde80**: 7.2803
- **H4_health_tost_p**: 0.328
- **H4_health_status**: NULL-INCONCLUSIVE
- **ROA_coef**: 7.7592
- **ROA_p**: 0.1533
- **AMEND_opmargin_coef**: 7.8076
- **AMEND_opmargin_p**: 0.0773
- **AMEND_both_roa_p**: 0.4001
- **AMEND_both_opmargin_p**: 0.1265
- **AMEND_nulls_unchanged**: True
- **N_essay2**: 339
- **H5_coef**: 3.9442
- **H5_p**: 0.0292
- **H5_tost_p**: 0.8456
- **H5_mde80**: 5.0651
- **H5_status**: HC3-ONLY, NOT A VERDICT (disqualified rung; see scripts/165)
- **H5_R2**: 0.529
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
- **car30d_regression_mean**: -0.2052
- **car30d_regression_median**: 0.1911
- **T3_filer_median**: -0.2416
- **T3_nonfiler_median**: 0.4118
- **T3_immediate_median**: 1.4152
- **T3_delayed_median**: -0.461
- **T3_health_median**: 0.4276
- **T3_nonhealth_median**: 0.1446
- **T3_any_prior_median**: 0.567
- **T3_no_prior_median**: -0.6034
- **T6_treated_timing_coef**: 0.5562
- **T6_treated_timing_se**: 2.0246
- **T6_treated_timing_p**: 0.7835
- **T6_treated_N**: 106
- **T6_untreated_timing_coef**: 1.9307
- **T6_untreated_timing_se**: 1.1916
- **T6_untreated_timing_p**: 0.1052
- **T6_untreated_N**: 234
- **T6_interaction_coef**: -1.6411
- **T6_interaction_se**: 2.2995
- **T6_interaction_p**: 0.4754
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
- **T16_ann_m30_m21_mean**: -0.0403
- **T16_ann_m30_m21_p**: 0.8808
- **T16_ann_m30_m21_diff_p**: 0.902
- **T16_ann_m20_m11_mean**: 0.3213
- **T16_ann_m20_m11_p**: 0.2389
- **T16_ann_m20_m11_diff_p**: 0.0739
- **T16_ann_m10_m1_mean**: -0.3581
- **T16_ann_m10_m1_p**: 0.2273
- **T16_ann_m10_m1_diff_p**: 0.0401

==========================================================================================
REBUILD STAGE 8: FULL REGENERATION
==========================================================================================

Samples: 489 events | CRSP 356 | regression 340 (106 treated, 12 parent CIKs)

Essay 1 (H1-H4, HC3):
  H2_FCC: -0.4994pp p=0.7326 | TOST(±2.10) p=0.1371 | MDE 4.09 | NULL-INCONCLUSIVE
  H1_timing: +1.4143pp p=0.1712 | TOST(±2.10) p=0.2538 | MDE 2.89 | NULL-INCONCLUSIVE
  H3_prior: +0.0258pp p=0.6916 | TOST(±2.10) p=0.0000 | MDE 0.18 | BOUNDED NULL
  H4_health: -0.9405pp p=0.7176 | TOST(±2.10) p=0.3280 | MDE 7.28 | NULL-INCONCLUSIVE
  ROA: +7.7592 p=0.1533

ROA amendment: op_margin +7.8076 p=0.0773 (N=340); both-spec roa p=0.4001 / op_margin p=0.1265; hypothesis nulls unchanged: True

Essay 2 (H5, N=339, treated 106): FCC +3.9442 p=0.0292 | TOST p=0.8456 | MDE 5.07 | R2=0.529 | HC3-ONLY, NOT A VERDICT (disqualified rung; see scripts/165)

First stage (descriptive): treated immediate-disclosure share exceeds untreated by +15.26pp

Appendix v3 tables...
  Table 2 disclosure verification: treated N=118 (median gap 15.0d, share 99%); untreated N=219 (median 26.0d, share 92%)
  Table 6 timing-by-regime: treated +0.5562 p=0.7835 (N=106); untreated +1.9307 p=0.1052 (N=234); interaction -1.6411 p=0.4754
  Table 16 leakage: breach panel N=356 (excl 0 history); ann panel N=355 (excl 1 no-reported + 0 history)
  16 tables (citation order, captioned) -> outputs/rebuild/appendix_v3/

Assertion check vs existing baseline: PASS