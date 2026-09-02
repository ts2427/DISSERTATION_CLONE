# Essay 2 Query 4 — Parts A, B2, C, E4, H, J, I (computed live)

==========================================================================================
ESSAY 2 QUERY 4 — PARTS A, B2, C, E4, H, J, I
==========================================================================================

## A1 — 47 CFR 64.2011, verbatim (sources: govinfo 2008 CFR annual edition,
CFR-2008-title47-vol3-sec64-2011.xml; current text law.cornell.edu/cfr/text/
47/64.2011 mirroring eCFR; both retrieved 2026-08-30; texts IDENTICAL)

(a) "A telecommunications carrier shall notify law enforcement of a breach
    of its customers' CPNI as provided in this section. The carrier shall
    not notify its customers or disclose the breach publicly, whether
    voluntarily or under state or local law or these rules, until it has
    completed the process of notifying law enforcement pursuant to
    paragraph (b) of this section."
(b) "As soon as practicable, and in no event later than seven (7) business
    days, after reasonable determination of the breach, the
    telecommunications carrier shall electronically notify the United
    States Secret Service (USSS) and the Federal Bureau of Investigation
    (FBI) through a central reporting facility."
(b)(1) "Notwithstanding any state law to the contrary, the carrier shall not
    notify customers or disclose the breach to the public until 7 full
    business days have passed after notification to the USSS and the FBI"
    [except per (b)(2)-(b)(3)].
(b)(2) urgent-need earlier notice only "after consultation with the relevant
    investigating agency."
(b)(3) investigating agency may direct no-disclosure for an initial period
    of up to 30 days, and "Such period may be extended by the agency as
    reasonably necessary in the judgment of the agency."
(c) "After a telecommunications carrier has completed the process of
    notifying law enforcement pursuant to paragraph (b) of this section,
    it shall notify its customers of a breach of those customers' CPNI."
    — NO TIME LIMIT IS SPECIFIED.
(d) two-year recordkeeping.
(e) "A 'breach' has occurred when a person, without authorization or
    exceeding authorization, has INTENTIONALLY gained access to, used, or
    disclosed CPNI." — inadvertent exposure is outside the 2007 rule.
Source credit: [72 FR 31963, June 8, 2007].

EVERY A0 CLAIM CONFIRMED: (1) the 7 business days run to LAW ENFORCEMENT,
not customers; (2) the trigger is the carrier's own "reasonable
determination", not discovery; (3) the rule imposes a MANDATORY MINIMUM
public-disclosure delay (~14 business days, extendable indefinitely under
(b)(3)); (4) customer notification has NO outer deadline; (5) the event PRC
records — public notification — is the event the rule leaves untimed.
FCC 23-111 (89 FR 9968, 2024-02-12): amendments to 64.2011 "delayed
indefinitely" pending OMB approval (verbatim in the repository's Federal
Register summary, COMPREHENSIVE_ARTICLE_SUMMARIES_COMPLETE.txt) — the 2007
text governed the ENTIRE 2006-2024 sample period; no mid-sample amendment.
The draft's mechanism (a deadline forcing disclosure before investigations
complete) requires a ceiling; the rule is a FLOOR. If it predicts anything
about observed notification timing, it predicts LONGER and MORE HOMOGENEOUS
delays for covered carriers.

==========================================================================================
## A2 — NEW PRIMARY TEST: does Form 499 treatment predict disclosure delay? (N=333)
==========================================================================================
  delay (raw days): coef +26.923  SE 39.420  95% CI [-51.525, +105.372]  (G=81, G1=11, CV1 parent-CIK, t(80))
  delay (winsorized p99): coef +11.136  SE 29.907  95% CI [-48.380, +70.652]  (G=81, G1=11, CV1 parent-CIK, t(80))
  log(1+delay): coef -0.124  SE 0.461  95% CI [-1.042, +0.794]  (G=81, G1=11, CV1 parent-CIK, t(80))

  Dispersion: treated SD 254.4, IQR 84, CV 2.54 | control SD 125.0, IQR 76, CV 1.76 | Brown-Forsythe W=2.546 (p=0.1115)
  The floor prediction (treated delays longer AND more homogeneous, compressed against a regulatory floor) requires treated dispersion BELOW control.

  ZERO-DELAY CONTAMINATION: 41/102 treated and 75/231 control delays are EXACTLY zero (34.8% of the sample). Same-day public notification at scale is implausible; these are almost certainly records whose occurrence date defaulted to the notification date in the source. The share-of-treated-below-the-regulatory-floor statistic is therefore measuring MISSING DATA, not non-compliance, and no compliance claim is made from it. Among NON-ZERO delays, 7/61 treated (11.5%) fall below ~20 calendar days — still diagnostic only (the clock measured is occurrence-to-notification, not determination-to-notification).

  A2 EXCLUDING ZERO DELAYS (N=217: 61 treated / 156 control):
    delay (raw days): coef +50.689  SE 59.065  95% CI [-67.028, +168.406]
    log(delay): coef +0.040  SE 0.336  95% CI [-0.631, +0.710]
    medians: treated 63d vs control 50d | dispersion: treated SD 312.3 CV 1.87 vs control SD 139.9 CV 1.33 | Brown-Forsythe W=3.387 (p=0.0671) | KS D=0.1487 (p=0.2546) | log-rank chi2=2.887 (p=0.0893)

  Quantile regressions (delay ~ treatment + controls; treatment coefficient; iid-kernel SEs, descriptive):
    q10: -0.00 (SE 7.27)
    q25: -0.00 (SE 6.51)
    q50: -5.02 (SE 7.25)
    q75: +13.63 (SE 16.51)
    q90: +18.23 (SE 39.65)

  Kaplan-Meier time-to-notification (no censoring — the sample conditions on an observed notification): median treated 22d vs control 24d; log-rank chi2=0.591 (p=0.4420)

  A2 DIRECTION, PLAINLY: see the coefficients above. If treated firms disclose no more slowly (and no more homogeneously) than controls, the rule does not bind on observed public-notification behavior — which is itself the candidate explanation for the volatility null and belongs in the essay as a finding.

==========================================================================================
## A3 — Delay distribution, treated vs control
==========================================================================================
  group   n  zeros  min  p10  p25  p50   p75   p90    p95    max  mean    sd
treated 102     41  0.0  0.0  0.0 22.0 84.25 214.0 342.75 1917.0 100.0 254.4
control 231     75  0.0  0.0  0.0 24.0 76.00 199.0 311.50  961.0  71.0 125.0
  KS test of distributional equality: D=0.0980 (p=0.4683). Exact zeros: treated 41, control 75.

==========================================================================================
## A4 — Locations describing 64.2011 as a DISCLOSURE deadline (deletions, not edits)
==========================================================================================
  scripts\105_complexity_index_heterogeneity.py:12: Mechanism: FCC mandates 7-day disclosure -> complex breach requires
  scripts\106_information_environment_composite.py:12: Mechanism: FCC mandates 7-day disclosure -> for firms with weak information environments,
  scripts\80_essay1_car_regressions.py:503: f.write("Notes: FCC-regulated firms subject to mandatory 7-day disclosure.\n")
  scripts\99_cvss_complexity_heterogeneity.py:11: Mechanism: FCC mandates 7-day disclosure -> complex breach (high CVSS) requires
  scripts\99_cvss_complexity_heterogeneity_BROKEN_June22.py:11: Mechanism: FCC mandates 7-day disclosure -> complex breach (high CVSS) requires
  scripts\99_cvss_complexity_heterogeneity_essay2.py:11: Mechanism: FCC mandates 7-day disclosure -> complex breach (high CVSS) requires
  scripts\create_regression_tables_word.py:384: - fcc_reportable: Telecom breach subject to FCC 7-day mandatory disclosure rule
  scripts\h1_comprehensive_power_analysis.py:385: only {immediate_7d/len(analysis_df)*100:.1f}% disclose within 7 days).
  scripts\update_existing_proposal.py:190: "Only 17.6% of firms disclose within 7 days. This non-compliance puzzle is explained by "
  scripts\update_proposal_documents.py:621: FCC 7-Day Rule Impacts:
  scripts\update_proposal_documents.py:660: Current Rule: 7-day disclosure mandate (effective 2007)
  outputs\DEAD_DATE_PURGE_INVENTORY.md:12: "FCC 7-Day Rule (47 CFR 64.2011, effective September 28, 2007)" → corrected to
  outputs\ESSAY2_QUERY4_PARTS_ACJ.md:95: scripts\105_complexity_index_heterogeneity.py:12: Mechanism: FCC mandates 7-day disclosure -> complex breach requires
  outputs\ESSAY2_QUERY4_PARTS_ACJ.md:96: scripts\106_information_environment_composite.py:12: Mechanism: FCC mandates 7-day disclosure -> for firms with weak inf
  outputs\ESSAY2_QUERY4_PARTS_ACJ.md:97: scripts\80_essay1_car_regressions.py:503: f.write("Notes: FCC-regulated firms subject to mandatory 7-day disclosure.\n")
  outputs\ESSAY2_QUERY4_PARTS_ACJ.md:98: scripts\99_cvss_complexity_heterogeneity.py:11: Mechanism: FCC mandates 7-day disclosure -> complex breach (high CVSS) r
  outputs\ESSAY2_QUERY4_PARTS_ACJ.md:99: scripts\99_cvss_complexity_heterogeneity_BROKEN_June22.py:11: Mechanism: FCC mandates 7-day disclosure -> complex breach
  outputs\ESSAY2_QUERY4_PARTS_ACJ.md:100: scripts\99_cvss_complexity_heterogeneity_essay2.py:11: Mechanism: FCC mandates 7-day disclosure -> complex breach (high 
  outputs\ESSAY2_QUERY4_PARTS_ACJ.md:101: scripts\create_regression_tables_word.py:384: - fcc_reportable: Telecom breach subject to FCC 7-day mandatory disclosure
  outputs\ESSAY2_QUERY4_PARTS_ACJ.md:102: scripts\h1_comprehensive_power_analysis.py:385: only {immediate_7d/len(analysis_df)*100:.1f}% disclose within 7 days).
  outputs\ESSAY2_QUERY4_PARTS_ACJ.md:103: scripts\update_existing_proposal.py:190: "Only 17.6% of firms disclose within 7 days. This non-compliance puzzle is expl
  outputs\ESSAY2_QUERY4_PARTS_ACJ.md:104: scripts\update_proposal_documents.py:621: FCC 7-Day Rule Impacts:
  outputs\ESSAY2_QUERY4_PARTS_ACJ.md:105: scripts\update_proposal_documents.py:660: Current Rule: 7-day disclosure mandate (effective 2007)
  outputs\ESSAY2_QUERY4_PARTS_ACJ.md:106: outputs\DEAD_DATE_PURGE_INVENTORY.md:12: "FCC 7-Day Rule (47 CFR 64.2011, effective September 28, 2007)" → corrected to
  outputs\ESSAY2_QUERY4_PARTS_ACJ.md:107: outputs\ESSAY2_QUERY4_PARTS_ACJ.md:95: scripts\105_complexity_index_heterogeneity.py:12: Mechanism: FCC mandates 7-day d
  outputs\ESSAY2_QUERY4_PARTS_ACJ.md:108: outputs\ESSAY2_QUERY4_PARTS_ACJ.md:96: scripts\106_information_environment_composite.py:12: Mechanism: FCC mandates 7-da
  outputs\ESSAY2_QUERY4_PARTS_ACJ.md:109: outputs\ESSAY2_QUERY4_PARTS_ACJ.md:97: scripts\80_essay1_car_regressions.py:503: f.write("Notes: FCC-regulated firms sub
  outputs\ESSAY2_QUERY4_PARTS_ACJ.md:110: outputs\ESSAY2_QUERY4_PARTS_ACJ.md:98: scripts\99_cvss_complexity_heterogeneity.py:11: Mechanism: FCC mandates 7-day dis
  outputs\ESSAY2_QUERY4_PARTS_ACJ.md:111: outputs\ESSAY2_QUERY4_PARTS_ACJ.md:99: scripts\99_cvss_complexity_heterogeneity_BROKEN_June22.py:11: Mechanism: FCC mand
  outputs\ESSAY2_QUERY4_PARTS_ACJ.md:112: outputs\ESSAY2_QUERY4_PARTS_ACJ.md:100: scripts\99_cvss_complexity_heterogeneity_essay2.py:11: Mechanism: FCC mandates 7
  outputs\ESSAY2_QUERY4_PARTS_ACJ.md:113: outputs\ESSAY2_QUERY4_PARTS_ACJ.md:101: scripts\build_essay1_appendix_final.py:479: table.rows[2].cells[0].text = 'Post-
  outputs\ESSAY2_QUERY4_PARTS_ACJ.md:114: outputs\ESSAY2_QUERY4_PARTS_ACJ.md:102: scripts\build_essay1_appendix_final.py:691: doc.add_paragraph('Conclusion: The F
  outputs\ESSAY2_QUERY4_PARTS_ACJ.md:115: outputs\ESSAY2_QUERY4_PARTS_ACJ.md:103: scripts\create_conceptual_models.py:130: ax.text(8, 8.8, 'FCC Rule 37.3 (2007): 
  outputs\ESSAY2_QUERY4_PARTS_ACJ.md:116: outputs\ESSAY2_QUERY4_PARTS_ACJ.md:104: scripts\create_regression_tables_word.py:384: - fcc_reportable: Telecom breach s
  outputs\ESSAY2_QUERY4_PARTS_ACJ.md:117: outputs\ESSAY2_QUERY4_PARTS_ACJ.md:105: scripts\h1_comprehensive_power_analysis.py:385: only {immediate_7d/len(analysis_
  outputs\ESSAY2_QUERY4_PARTS_ACJ.md:118: outputs\ESSAY2_QUERY4_PARTS_ACJ.md:106: scripts\update_existing_proposal.py:190: "Only 17.6% of firms disclose within 7 
  outputs\ESSAY2_QUERY4_PARTS_ACJ.md:119: outputs\ESSAY2_QUERY4_PARTS_ACJ.md:107: scripts\update_proposal_documents.py:621: FCC 7-Day Rule Impacts:
  outputs\ESSAY2_QUERY4_PARTS_ACJ.md:120: outputs\ESSAY2_QUERY4_PARTS_ACJ.md:108: scripts\update_proposal_documents.py:660: Current Rule: 7-day disclosure mandate
  outputs\ESSAY2_QUERY4_PARTS_ACJ.md:121: outputs\ESSAY2_QUERY4_PARTS_ACJ.md:109: outputs\DEAD_DATE_PURGE_INVENTORY.md:12: "FCC 7-Day Rule (47 CFR 64.2011, effect
  outputs\ESSAY2_QUERY4_PARTS_ACJ.md:133: outputs\ESSAY2_QUERY4_PARTS_ACJ.md:121: outputs\ESSAY2_QUERY4_PARTS_ACJ.md:106: scripts\update_existing_proposal.py:190:
  outputs\ESSAY2_QUERY4_PARTS_ACJ.md:134: outputs\ESSAY2_QUERY4_PARTS_ACJ.md:122: outputs\ESSAY2_QUERY4_PARTS_ACJ.md:107: scripts\update_proposal_documents.py:621
  outputs\ESSAY2_QUERY4_PARTS_ACJ.md:135: outputs\ESSAY2_QUERY4_PARTS_ACJ.md:123: outputs\ESSAY2_QUERY4_PARTS_ACJ.md:108: scripts\update_proposal_documents.py:660
  outputs\ESSAY2_QUERY4_PARTS_ACJ.md:136: outputs\ESSAY2_QUERY4_PARTS_ACJ.md:124: outputs\ESSAY2_QUERY4_PARTS_ACJ.md:109: outputs\DEAD_DATE_PURGE_INVENTORY.md:12:
  outputs\ESSAY2_QUERY4_PARTS_ACJ.md:152: outputs\ESSAY2_QUERY4_PARTS_ACJ.md:171: outputs\ESSAY2_QUERY4_PARTS_ACJ.md:174: Dashboard\app.py:225: - Interpretation: 
  outputs\ESSAY2_QUERY4_PARTS_ACJ.md:153: outputs\ESSAY2_QUERY4_PARTS_ACJ.md:173: outputs\ESSAY2_QUERY4_PARTS_ACJ.md:176: Dashboard\app.py:409: before the 2007 FC
  outputs\ESSAY2_QUERY4_PARTS_ACJ.md:154: outputs\ESSAY2_QUERY4_PARTS_ACJ.md:174: outputs\ESSAY2_QUERY4_PARTS_ACJ.md:177: Dashboard\app.py:422: Pre-2007 (before F
  outputs\ESSAY2_QUERY4_PARTS_ACJ.md:156: outputs\ESSAY2_QUERY4_PARTS_ACJ.md:176: outputs\ESSAY2_QUERY4_PARTS_ACJ.md:179: Dashboard\pages\0_Research_Story.py:103:
  outputs\ESSAY2_QUERY4_PARTS_ACJ.md:157: outputs\ESSAY2_QUERY4_PARTS_ACJ.md:178: outputs\ESSAY2_QUERY4_PARTS_ACJ.md:181: Dashboard\pages\1_Natural_Experiment.py:
  outputs\ESSAY2_QUERY4_PARTS_ACJ.md:160: outputs\ESSAY2_QUERY4_PARTS_ACJ.md:181: outputs\ESSAY2_QUERY4_PARTS_ACJ.md:184: Dashboard\pages\5_Essay2_InformationAsym
  outputs\ESSAY2_QUERY4_PARTS_ACJ.md:161: outputs\ESSAY2_QUERY4_PARTS_ACJ.md:182: outputs\ESSAY2_QUERY4_PARTS_ACJ.md:185: Dashboard\pages\5_Essay2_InformationAsym
  outputs\ESSAY2_QUERY4_PARTS_ACJ.md:162: outputs\ESSAY2_QUERY4_PARTS_ACJ.md:183: outputs\ESSAY2_QUERY4_PARTS_ACJ.md:186: Dashboard\pages\6_Essay3_GovernanceRespo
  outputs\ESSAY2_QUERY4_PARTS_ACJ.md:163: outputs\ESSAY2_QUERY4_PARTS_ACJ.md:184: outputs\ESSAY2_QUERY4_PARTS_ACJ.md:187: Dashboard\pages\8_Key_Findings.py:287: F
  outputs\ESSAY2_QUERY4_PARTS_ACJ.md:164: outputs\ESSAY2_QUERY4_PARTS_ACJ.md:185: outputs\ESSAY2_QUERY4_PARTS_ACJ.md:188: Dashboard\pages\8_Key_Findings.py:359: -
  outputs\ESSAY2_QUERY4_PARTS_ACJ.md:167: outputs\ESSAY2_QUERY4_PARTS_ACJ.md:188: outputs\ESSAY2_QUERY4_PARTS_ACJ.md:191: (96 locations; every one describes a cus
  outputs\ESSAY2_QUERY4_PARTS_ACJ.md:168: outputs\ESSAY2_QUERY4_PARTS_ACJ.md:189: Dashboard\app.py:225: - Interpretation: Forced 7-day disclosure INCREASES rather
  outputs\ESSAY2_QUERY4_PARTS_ACJ.md:170: outputs\ESSAY2_QUERY4_PARTS_ACJ.md:191: Dashboard\app.py:409: before the 2007 FCC 7-Day Rule implementation. This figure
  outputs\ESSAY2_QUERY4_PARTS_ACJ.md:171: outputs\ESSAY2_QUERY4_PARTS_ACJ.md:192: Dashboard\app.py:422: Pre-2007 (before FCC 7-Day Rule): FCC and non-FCC firms sh
  outputs\ESSAY2_QUERY4_PARTS_ACJ.md:172: outputs\ESSAY2_QUERY4_PARTS_ACJ.md:193: Dashboard\app.py:427: the regulation takes effect, not before. This is the core 
  outputs\ESSAY2_QUERY4_PARTS_ACJ.md:173: outputs\ESSAY2_QUERY4_PARTS_ACJ.md:194: Dashboard\pages\0_Research_Story.py:103: Regulator forces 7-day disclosure
  outputs\ESSAY2_QUERY4_PARTS_ACJ.md:175: outputs\ESSAY2_QUERY4_PARTS_ACJ.md:196: Dashboard\pages\1_Natural_Experiment.py:66: 'Regulation passed\n(Mandatory 7-day
  outputs\ESSAY2_QUERY4_PARTS_ACJ.md:176: outputs\ESSAY2_QUERY4_PARTS_ACJ.md:197: Dashboard\pages\1_Natural_Experiment.py:111: <li><b>Requirement:</b> Disclose wi
  outputs\ESSAY2_QUERY4_PARTS_ACJ.md:177: outputs\ESSAY2_QUERY4_PARTS_ACJ.md:198: Dashboard\pages\3_Data_Landscape.py:89: - After 2007: FCC firms forced to disclo
  outputs\ESSAY2_QUERY4_PARTS_ACJ.md:178: outputs\ESSAY2_QUERY4_PARTS_ACJ.md:199: Dashboard\pages\5_Essay2_InformationAsymmetry.py:327: - Forced 7-day disclosure 
  outputs\ESSAY2_QUERY4_PARTS_ACJ.md:179: outputs\ESSAY2_QUERY4_PARTS_ACJ.md:200: Dashboard\pages\5_Essay2_InformationAsymmetry.py:473: **The FCC 7-Day Rule was e
  outputs\ESSAY2_QUERY4_PARTS_ACJ.md:180: outputs\ESSAY2_QUERY4_PARTS_ACJ.md:201: Dashboard\pages\6_Essay3_GovernanceResponse.py:272: **The FCC 7-Day Rule was ena
  outputs\ESSAY2_QUERY4_PARTS_ACJ.md:181: outputs\ESSAY2_QUERY4_PARTS_ACJ.md:202: Dashboard\pages\8_Key_Findings.py:287: FCC PATH (Forced 7-day disclosure):
  outputs\ESSAY2_QUERY4_PARTS_ACJ.md:182: outputs\ESSAY2_QUERY4_PARTS_ACJ.md:203: Dashboard\pages\8_Key_Findings.py:359: - Market EXPECTS 7-day disclosure (it's r
  outputs\ESSAY2_QUERY4_PARTS_ACJ.md:183: outputs\ESSAY2_QUERY4_PARTS_ACJ.md:204: Dashboard\pages\9_Conclusion.py:144: - After 2007: FCC firms forced to disclose 
  outputs\ESSAY2_QUERY4_PARTS_ACJ.md:184: outputs\ESSAY2_QUERY4_PARTS_ACJ.md:205: README.md:82: FCC Rule 37.3 (Sept 28, 2007) requires data breach notification wi
  outputs\ESSAY2_QUERY4_PARTS_ACJ.md:185: outputs\ESSAY2_QUERY4_PARTS_ACJ.md:206: (111 locations; every one describes a customer-disclosure deadline or ceiling th
  outputs\ESSAY2_QUERY4_PARTS_ACJ.md:187: Dashboard\app.py:225: - Interpretation: Forced 7-day disclosure INCREASES rather than decreases asymmetry
  outputs\ESSAY2_QUERY4_PARTS_ACJ.md:188: Dashboard\app.py:391: <b>Essay 2:</b> FCC firms experience HIGHER volatility (+1.83%**) even with forced 7-day disclosur
  outputs\ESSAY2_QUERY4_PARTS_ACJ.md:189: Dashboard\app.py:409: before the 2007 FCC 7-Day Rule implementation. This figure provides visual proof of that assumptio
  outputs\ESSAY2_QUERY4_PARTS_ACJ.md:190: Dashboard\app.py:422: Pre-2007 (before FCC 7-Day Rule): FCC and non-FCC firms show similar CAR patterns (no significant 
  outputs\ESSAY2_QUERY4_PARTS_ACJ.md:191: Dashboard\app.py:427: the regulation takes effect, not before. This is the core evidence that FCC 7-Day Rule causally af
  outputs\ESSAY2_QUERY4_PARTS_ACJ.md:192: Dashboard\pages\0_Research_Story.py:103: Regulator forces 7-day disclosure
  outputs\ESSAY2_QUERY4_PARTS_ACJ.md:193: Dashboard\pages\0_Research_Story.py:283: FCC-regulated firms (telecom, cable, VoIP, satellite) → FORCED to disclose with
  outputs\ESSAY2_QUERY4_PARTS_ACJ.md:194: Dashboard\pages\1_Natural_Experiment.py:66: 'Regulation passed\n(Mandatory 7-day rule)',
  outputs\ESSAY2_QUERY4_PARTS_ACJ.md:195: Dashboard\pages\1_Natural_Experiment.py:111: <li><b>Requirement:</b> Disclose within 7 days (FCC 7-Day Rule)</li>
  outputs\ESSAY2_QUERY4_PARTS_ACJ.md:196: Dashboard\pages\3_Data_Landscape.py:89: - After 2007: FCC firms forced to disclose within 7 days
  outputs\ESSAY2_QUERY4_PARTS_ACJ.md:197: Dashboard\pages\5_Essay2_InformationAsymmetry.py:327: - Forced 7-day disclosure → Incomplete information → Market uncert
  outputs\ESSAY2_QUERY4_PARTS_ACJ.md:200: Dashboard\pages\8_Key_Findings.py:287: FCC PATH (Forced 7-day disclosure):
  outputs\ESSAY2_QUERY4_PARTS_ACJ.md:201: Dashboard\pages\8_Key_Findings.py:359: - Market EXPECTS 7-day disclosure (it's required)
  outputs\ESSAY2_QUERY4_PARTS_ACJ.md:202: Dashboard\pages\9_Conclusion.py:144: - After 2007: FCC firms forced to disclose within 7 days; non-FCC still free
  outputs\ESSAY2_QUERY4_PARTS_ACJ.md:203: (108 locations; every one describes a customer-disclosure deadline or ceiling the rule does not contain — these are dele
  outputs\ESSAY2_QUERY5_REPORT.md:43: Deadline-language locations: the t24 scan (executed below). Hypothesis logic: **none of H1–H4 requires the deadline read
  Dashboard\app.py:225: - Interpretation: Forced 7-day disclosure INCREASES rather than decreases asymmetry
  Dashboard\app.py:391: <b>Essay 2:</b> FCC firms experience HIGHER volatility (+1.83%**) even with forced 7-day disclosure. Information asymmet
  Dashboard\app.py:409: before the 2007 FCC 7-Day Rule implementation. This figure provides visual proof of that assumption.
  Dashboard\app.py:422: Pre-2007 (before FCC 7-Day Rule): FCC and non-FCC firms show similar CAR patterns (no significant difference, p=0.88)
  Dashboard\app.py:427: the regulation takes effect, not before. This is the core evidence that FCC 7-Day Rule causally affects market outcomes.
  Dashboard\pages\0_Research_Story.py:103: Regulator forces 7-day disclosure
  Dashboard\pages\0_Research_Story.py:283: FCC-regulated firms (telecom, cable, VoIP, satellite) → FORCED to disclose within 7 days
  Dashboard\pages\1_Natural_Experiment.py:66: 'Regulation passed\n(Mandatory 7-day rule)',
  Dashboard\pages\1_Natural_Experiment.py:111: <li><b>Requirement:</b> Disclose within 7 days (FCC 7-Day Rule)</li>
  Dashboard\pages\3_Data_Landscape.py:89: - After 2007: FCC firms forced to disclose within 7 days
  Dashboard\pages\5_Essay2_InformationAsymmetry.py:327: - Forced 7-day disclosure → Incomplete information → Market uncertainty INCREASES
  Dashboard\pages\5_Essay2_InformationAsymmetry.py:473: **47 CFR 64.2011 became effective December 8, 2007; it sets a 7-business-day law-enforcement notification clock and emba
  Dashboard\pages\6_Essay3_GovernanceResponse.py:272: **47 CFR 64.2011 became effective December 8, 2007; it sets a 7-business-day law-enforcement notification clock and emba
  Dashboard\pages\8_Key_Findings.py:287: FCC PATH (Forced 7-day disclosure):
  Dashboard\pages\8_Key_Findings.py:359: - Market EXPECTS 7-day disclosure (it's required)
  Dashboard\pages\9_Conclusion.py:144: - After 2007: FCC firms forced to disclose within 7 days; non-FCC still free
  (102 locations; every one describes a customer-disclosure deadline or ceiling the rule does not contain — these are deletions.)

==========================================================================================
## B2 — Is duplication non-random in firm size? (489-event universe)
==========================================================================================
  records-per-event ~ ln(assets): coef +0.0827 SE 0.0481 95% CI [-0.0119, +0.1772] N=350
  records-per-event ~ ln(mktcap): coef -0.0635 SE 0.0553 95% CI [-0.1723, +0.0453] N=332
  records-per-event by size quartile:
            mean  median  max  count
size_q                              
Q1      1.325843     1.0    4     89
Q2      1.425287     1.0    9     87
Q3      2.139535     1.0   31     86
Q4      1.443182     1.0    8     88
  Cencora illustration: 3 events, n_source_records = [31, 25, 1] — one 2024-02-21 event carries 31 notification records. Number-of-states-of-operation is NOT constructible from committed data (stated).
  (If the size gradient in records-per-event is positive, record-level analysis mechanically overweights large firms and the old size gradient is a record-vs-event artifact.)

==========================================================================================
## B2b — Size composition of the misclassified sets (the mechanism the four-panel decomposition implies: treatment reclassification, not deduplication)
==========================================================================================
  SIC-treated, NOT registered (the manufactured group): n=6 (3 orgs) | ln(assets) mean 12.26 median 12.25 | pre-vol 16.2 | vol-change -1.70
  SIC-treated AND registered (concordant treated): n=98 (32 orgs) | ln(assets) mean 11.72 median 12.17 | pre-vol 30.7 | vol-change -3.78
  registered, NOT SIC-treated (missed by SIC): n=7 (4 orgs) | ln(assets) mean 10.04 median 9.36 | pre-vol 35.9 | vol-change -3.52
  neither (concordant control): n=228 (91 orgs) | ln(assets) mean 9.59 median 9.01 | pre-vol 28.6 | vol-change -2.95

  Welch tests: SIC-treated-but-unregistered vs concordant treated — ln(assets) t=+3.32 (p=0.0039); pre-breach volatility t=-5.37 (p=0.0000). Volatility change, SIC-only vs all others: t=+0.87 (p=0.4044).
  On CORRECTED data the discordant cell is nearly empty (6 events / 3 orgs — post-resolution SIC and Form 499 almost coincide), so the mechanism must be tested where the artifact was produced: the OLD record-level data.
  OLD DATA — SIC-treated, NOT registered (manufactured): n=17 (11 orgs) | ln(assets) 10.17 | pre-vol 38.3 | vol-change +5.06
  OLD DATA — SIC-treated AND registered (concordant): n=167 (38 orgs) | ln(assets) 11.16 | pre-vol 24.3 | vol-change -0.39
  OLD DATA — control (neither): n=700 (319 orgs) | ln(assets) 10.39 | pre-vol 28.4 | vol-change -1.95

  Welch, OLD data (join-gap REPAIRED group): size manufactured-vs-concordant t=-2.39 (p=0.0280) — on the repaired group the manufactured records ARE smaller than concordant carriers (the pre-repair null, t=-0.54/p=.59, was a statement about the 14 misjoined Comcast records). Volatility change, manufactured-vs-control: t=+3.14 (p=0.0057; pre-repair t=+4.43/p=.0001 on the contaminated 31-record group — reported as the join-gap sensitivity).
  Manufactured share of SIC-treated records by size quartile (N=891 spec sample): Q1: 9/34 (26%); Q2: 0/17 (0%); Q3: 1/23 (4%); Q4: 7/109 (6%)
  Manufactured orgs: ['ATT-SecurityBreach', 'ATT-SecurityBreach2', 'Aero Charter, Inc.', 'Charter Next Generation, Inc.', 'DISH Network Corporation', 'DISH Network L.L.C.', 'DISH Network, LLC', 'Impact Mobile Home Communities', 'Johnson Matthey, Inc.', 'Suddenlink Communications', 'WillScot Mobile Mini Holdings Corp.']

  MECHANISM VERDICT (revised 9/2, join-gap-repaired group): the SIC-treated-but-unregistered records are smaller than concordant carriers (p=0.028 old data repaired; the earlier "not smaller" was a statement about the misjoined Comcast records) and their measured volatility CHANGES are elevated — mean +5.06 against -0.39 for correctly-classified carriers and -1.95 for controls (t=+3.14, p=0.0057) — with the share of the "treated" cell peaking in Q1 (26% of Q1 SIC-treated records vs 0% in Q2). The Q1 records are NOT name-adjacency non-carriers (those sit in Q3/Q4 with unremarkable outcomes): they are DISH and Suddenlink — genuine communications firms OUTSIDE the Form 499 contribution base — a REGULATORY-STATUS distinction SIC cannot see. And the Q1 collapse (+7.65 -> +0.13, panel ii) is a SWAP, not a removal: 9 records averaging +7.56 leave (DISH/Suddenlink), 10 records averaging -8.62 enter (GoDaddy, Twilio — Form 499 filers SIC coded as software). SIC errs in both directions and both errors land in the small-firm cell; the published spike is the net of a positive-outcome exclusion failure and a negative-outcome inclusion failure — not a records-per-event size gradient (B2), and not driven by the name-adjacency admissions (data-quality paragraph, incl. the two ATT-SecurityBreach permno-collision records).

==========================================================================================
## C1 — Vintage-matched treatment
==========================================================================================
  1. Pull used: committed snapshot Data/edgar/form499_registry.xml (7/31/2026 vintage; Registration_Current_as_of 2026-04-01), 20,669 filer records.
  2. Registration histories ARE in the data as pulled: every record carries start_date; 11767 records (57%) are TERMINATED records retained with end_date and end_reason — the database is not a live-filers-only snapshot, so the premise that deregistered filers vanish does not hold for this pull (named evidence: HBO's dead 1997-2003 record and Sprint's 1997-2024 record both appear and both drove stage-4 rulings).
  3. Stage 4 (scripts/154) ASSIGNED TREATMENT AS OF THE BREACH DATE from these windows: coverage_valid treats an ended record as covering only through its end_date (this rule made HBO 2017 untreated and was the documented divergence from the retired 121b logic). Wayback reconstruction is therefore not required; the residual risk is a filer HARD-DELETED from the current database, for which no in-sample evidence exists (stated as a limitation, direction: would misclassify a deregistered-then-deleted carrier as control, attenuating any true effect).
  4. Independent re-verification (family-keyword match to registry, date-window containment of each breach date):
 parent_cik  family_records  treated_events  date_covered
      18926              95               5             5
      20520              61               4             4
     101830              39               9             9
     732712             202              10            10
     732717             114              24            24
    1091667              85               8             8
    1166691              31               9             9
    1283699              22              26            26
    1447669               2               2             2
    1609711               2               3             3
    1632127              13               2             2
  => 102/102 treated observations have a date-valid family filer record at the breach date (0 not covered by this keyword check). Control->treated flips: stage 2/4 ran name resolution with abstain against the full registry; an exact-normalized-name rescan of the 231 control orgs is part of the J funnel below.
  5. Headline re-estimation: unnecessary if 102/102 survive; otherwise rerun flagged.

==========================================================================================
## C2 — Over-inclusion audit (Principal_Communications_Type)
==========================================================================================
  18926: types ['CAP/LEC', 'Cellular/PCS/SMR', 'Incumbent Local Exchange Carrier', 'Interexchange Carrier (IXC)', 'Operator Service Provider (OSP)', 'Toll Reseller'] | non-covered: none
  20520: types ['CAP/LEC', 'Incumbent Local Exchange Carrier', 'Interexchange Carrier (IXC)', 'Local Reseller', 'Toll Reseller'] | non-covered: none
  101830: types ['Cellular/PCS/SMR', 'Incumbent Local Exchange Carrier', 'Interexchange Carrier (IXC)', 'Local Reseller', 'Private Service Provider', 'Toll Reseller'] | non-covered: ['Private Service Provider']
  732712: types ['CAP/LEC', 'Cellular/PCS/SMR', 'Incumbent Local Exchange Carrier', 'Interexchange Carrier (IXC)', 'Private Service Provider', 'Toll Reseller'] | non-covered: ['Private Service Provider']
  732717: types ['CAP/LEC', 'Cellular/PCS/SMR', 'Incumbent Local Exchange Carrier', 'Interconnected VoIP', 'Interexchange Carrier (IXC)', 'Toll Reseller'] | non-covered: none
  1091667: types ['CAP/LEC', 'Cellular/PCS/SMR', 'Interconnected VoIP', 'Paging & Messaging', 'Private Service Provider', 'SMR (dispatch)'] | non-covered: ['Private Service Provider']
  1166691: types ['CAP/LEC', 'Cellular/PCS/SMR', 'Interconnected VoIP', 'Other Toll', 'Private Service Provider', 'Toll Reseller'] | non-covered: ['Private Service Provider']
  1283699: types ['Cellular/PCS/SMR', 'Interconnected VoIP', 'Prepaid Card', 'Private Service Provider', 'Toll Reseller'] | non-covered: ['Private Service Provider']
  1447669: types ['', 'Interconnected VoIP'] | non-covered: none
  1609711: types ['Interconnected VoIP', 'Other Toll'] | non-covered: none
  1632127: types ['CAP/LEC', 'Incumbent Local Exchange Carrier', 'Interconnected VoIP', 'Private Service Provider'] | non-covered: ['Private Service Provider']
  HONEST READING: the registry carries NO "Non-Interconnected VoIP" and no TRS label anywhere in Principal_Communications_Type — which means the over-inclusion risk CANNOT BE ASSESSED FROM THIS SOURCE, not that it is absent. What can be said: every treated family also matches on telecommunications-carrier or Interconnected-VoIP records (categories 64.2011 via 64.2003 covers), so no treated parent rests SOLELY on a category this snapshot can identify as non-covered, and the exclusion re-estimation is a no-op by construction. The residual over-inclusion risk (a family whose relevant filer is in fact a non-interconnected-VoIP or TRS-only filer mislabeled here) is a stated limitation. Separately: coverage runs to CPNI held as a carrier, so non-CPNI breaches at covered carriers are regulated only insofar as CPNI is involved — a scope limit of the treatment proxy itself, stated.

==========================================================================================
## E4 — Events by notification year (final sample)
==========================================================================================
      control  treated
year                  
2007        6        0
2008        6        5
2009        0        3
2010        4        0
2011        2        0
2012        6        1
2013       13        1
2014        6       12
2015       13        7
2016       37        0
2017       32       12
2018       13        4
2019       14        9
2020        6        6
2021       10        9
2022       15        6
2023       34       12
2024       14       15
  Zero treated observations precede the December 8, 2007 effective date — visible above, not asserted. DiD and synthetic control are unavailable: no pre-treatment period exists for treated units, so no donor pool can be weighted to a treated pre-period trajectory (Abadie, Diamond & Hainmueller 2010; Abadie 2021 JEL).

==========================================================================================
## H1 — Repeated events within firm
==========================================================================================
  treated: 11 parents, events/parent mean 9.3, median 8, max 26
  control: 73 parents, events/parent mean 3.2, median 1, max 76
  first event per parent: coef -0.0016 SE 0.3615 95% CI [-0.7222, +0.7191] N=81 (11 treated)
  most recent event per parent: coef +0.1174 SE 0.3183 95% CI [-0.5172, +0.7520] N=81 (11 treated)
  parent fixed effects: coef +0.4508 SE 0.2055 95% CI [+0.0460, +0.8556] — identified off only 3 parents whose treatment status varies across their own events (AT&T-family and Comcast coverage-window cases); interpret accordingly.

## H3 — Sample period
  The WRDS extract ends 2024-12-31; the final sample's latest notification year is 2024. SAMPLE PERIOD IS 2006-2024 everywhere. 9 events in the 489-event universe carry 2025 notification dates; the five with matched securities (Nucor, Intuit, Workday, HPE, Zscaler) drop at the volatility-window step because the extract ends — stated in the attrition ledger.

==========================================================================================
## J — Census: is 11 treated parents the population ceiling?
==========================================================================================
  Funnel (2006-2024 window; exact-normalized-name matching with abstain — a LOWER BOUND on public mapping, since filings are at operating-entity level with no CIK/ticker field and full parent attribution is a hand-construction task, stated):
    Form 499 filer records with coverage in window:      16,815
    Distinct legal entities (normalized):                16,433
    Distinct named holding companies:                    2,584
    Name-matched to an SEC registrant (CIK, exact):      81
    ...of the 11 verified treated parents so surfaced:   6
    ...appearing in the 489-event breach universe:       10
  READING (DECIDED 8/30, per Tim): the census claim is RESTATED AT THE INTERSECTION. The automated exact-name census undercounts by construction — filings are operating-entity-level (Verizon New York Inc., not Verizon Communications), and only 6 of the 11 hand-verified treated parents surface via exact matching; this undercount is stated as a limitation (direction: understates the public regulated population). The hand census (~2,584 holding names) is NOT undertaken. The defensible census is the observable intersection: within firms that BOTH filed Form 499 AND publicly disclosed a breach captured by PRC with CRSP coverage, the pipeline exhausted the set at 13 parents (11 surviving to the final sample). The POPULATION argument is carried by E3 instead, which is stronger and does not depend on the census: a 3pp-annualized effect is unreachable at ANY treated count given the control-side variance floor — a variance-structure result, not a sample-size result.

==========================================================================================
## I — Literature-claim corrections (text to carry into the essay)
==========================================================================================

I1 (4.2pp REMOVED). Replacement sentence, verbatim:
  "Obaydin, Xu, and Zurbruegg (2024) find that the staggered adoption of
  state data breach notification laws raises stock price crash risk by at
  least 5% of a standard deviation across NCSKEW, DUVOL, and COUNT, with a
  corresponding 5.2%-of-a-standard-deviation increase in residual short
  interest consistent with managerial bad-news hoarding."
  (DUVOL is a down-to-up volatility log-ratio, not a volatility level —
  the likely origin of the 4.2pp error. Nothing in the paper is in pp.)

I2 (novelty NARROWED). Within breach notification, deadline variation is
  unexploited — but Ashraf & Sunder (2023, TAR 98(4)) footnote 25 already
  tested an explicit-deadline incremental effect and "find no statistically
  significant incremental effect (untabulated)", inviting future research.
  Cite as motivation; never claim nobody has looked. Across disclosure
  settings the claim is false: engage Doyle & Magilke (2013 JAR), Lambert
  et al. (2017 AOS), Impink et al. (2012 RAST — a deadline-change null),
  Lerman & Livnat (2010 RAST), Tartaroglu & Imhof (2017 RQFA).

I3 (unbundling SOFTENED). 64.2011 is itself a bundle (new federal mandate +
  LE-first sequencing + 7-business-day LE clock + 7-business-day public
  embargo + recordkeeping). Defensible claim: unusual in imposing a hard,
  short, federally specified LAW-ENFORCEMENT clock with a mandatory
  public-disclosure embargo on a defined industry; earliest US instrument
  to do so. Degree, not kind.

I4 (state-law bundling, QUALIFIED). Report as "no deadline-only amendment
  was identified in the amendments surveyed" (Ashraf & Sunder 2023; Perkins
  Coie annual updates; NY GBL 899-aa Dec-2024 near-miss also changed delay
  exceptions and data-maintainer scope; both near-misses postdate the
  sample).

I5 (SEC 2023 rule). Future-research framing holds; note the DOJ
  delay-determination mechanism as observable disclosure-lag variation and
  the May-2024 Gerding statement (Item 8.01 venue break) as design points;
  the low-hanging event study is being picked (Block 2025 working paper).

==========================================================================================
Hypothesis tests in this script: 26 — A2-delay: 11; A2-delay-nz: 5; B2b: 5; H1: 3; B2: 2
(Multiplicity framework applied across Query-4 parts in the umbrella report: Benjamini-Hochberg within each pre-specified family; the specification grid is descriptive and contributes no tests.)
