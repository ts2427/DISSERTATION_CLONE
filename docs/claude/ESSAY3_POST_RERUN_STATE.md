# Essay 3 — Settled State

Built from `outputs/ESSAY3_QUERY2_REPORT.md` (Stage 1 and Stage 2), commit chain through `c5f761d`. Every number here carries a provenance pointer into that report or its named output file. Nothing in this document comes from the circulated draft, from `constants_v3.json`, or from memory.

Date: September 11, 2026.

**Status of this document.** This is the settled empirical state. It fixes what Essay 3 finds, and what it can and cannot claim, before any prose is written. Where the circulated draft conflicts with a line here, the line here governs.

---

## 0. What Essay 3 is now

A post-2007 cross-sectional study of whether FCC-regulated carriers show more executive-officer departure after a data breach becomes public than other breached firms do.

- **Outcome:** departure of an executive officer reported under Item 5.02(b), measured from the public notification date. One departure per person within a parent CIK, dated to its earliest disclosing filing.
- **Treatment:** the FCC Form 499 two-clause rule with documented adjudications.
- **Answer:** the hypothesis is not supported at 30, 90, or 180 days, on every rung of the inference ladder.
- **Not in the essay:** no first stage, no mediation, no equivalence test, no Cox model, no causal or natural-experiment framing.

---

## 1. Sample

Source: Part E ledger, `e_ledger.csv`. Chain: today's `CANONICAL_V3`. `constants_v3.json` untouched; Essay 3's own constants are in `outputs/essay3_q2/constants_essay3_q2.json`.

| Step | N | Treated | Control | Treated parent CIKs |
|---|---|---|---|---|
| PRC notification records | 1,054 | — | — | — |
| Gate 1 signed parent CIK (records) | 758 | — | — | — |
| Stage 3 firm-day events | 524 | — | — | — |
| Gate 2 adjacency collapse | 491 | — | — | — |
| CANONICAL_V3 events | 489 | 118 | 371 | 14 |
| CRSP data | 356 | 111 | 245 | 13 |
| Compustat covariates (Query 2 scope) | 341 | 107 | 234 | 12 |
| Outcome-data requirement | 340 | 107 | 233 | 12 |
| **Prior 12-month return available — ANALYSIS SAMPLE** | **338** | **107** | **231** | **12** |

The ledger closes arithmetically at every step.

**Facts to carry into prose:**
- The 1,054 are notification records, not breaches. Records-to-events deduplication is a finding of the dissertation.
- Parent entities and parent CIKs are the same count here; the pipeline has no separate entity key. Folding Sprint into T-Mobile as one corporate family gives 11 treated families.
- **Attrition explanations:** the outcome-data requirement removes one event (Nokia, a foreign private issuer that files no Form 8-K). The prior-return requirement removes two controls, both recent IPOs (Uber, Zscaler).
- **Pre-rule events:** 6 at the analysis-sample level, all control, under the December 8, 2007 effective date. No treated pre-rule events, so DiD is not identified.
- **Two CIK re-pointings**, both controls: Disney 926480 → 1001039, Aon 1808065 → 315293. Both were structural zeros in Query 1 because the registration CIK files no 8-Ks.

---

## 2. Primary result (F1)

Source: `f1_ladder.csv`, `202_estimation.log:3-8`. LPM, notification anchor, clustered on parent CIK (G = 81, 12 treated).

| Window | Coef | CV3 SE | CV3 p | CV3 95% CI | WCR p | MDE80 | Treated mean | Control mean |
|---|---|---|---|---|---|---|---|---|
| 30d | +0.0168 | 0.0329 | .6118 | [−0.0487, +0.0823] | .4924 | 0.0934 | .037 | .043 |
| 90d | −0.0169 | 0.1029 | .8701 | [−0.2217, +0.1879] | .8154 | 0.2918 | .112 | .160 |
| 180d | +0.0434 | 0.1144 | .7052 | [−0.1842, +0.2711] | .6474 | 0.3245 | .318 | .251 |

Logit AMEs corroborate: +0.0238 (p .4362), −0.0225 (p .6944), +0.0392 (p .6475).

Benjamini–Hochberg within the primary family: all three at .8701.

**Settled language:** "The hypothesis is not supported." Never "confirms the null," never "demonstrably negligible," never any equivalence claim.

---

## 3. What the design can and cannot detect

This is the most important constraint in the essay, and it must appear in the results, not only the limitations.

- 30d: MDE 9.3 pp against a control mean of 4.3%.
- 90d: MDE 29.2 pp against a control mean of 16.0%.
- 180d: MDE 32.5 pp against a control mean of 25.1%.

At 90 and 180 days the minimum detectable effect exceeds the entire control base rate. The design can rule out only very large effects.

**Why the MDE triples between 30 and 90 days** (scripts/204, `f1_cv3_variance_shares.csv`):
- Outcome variance rises with the base rate, .0398 → .1243, roughly doubling the HC3 SE.
- One control cluster, Fidelity National Information Services (CIK 1136893, 12 events), accounts for **65.6%** of the 90-day CV3 jackknife variance.
- T-Mobile's share of that variance is 10.1%. Deleting T-Mobile *raises* the 90-day CV3 SE to 0.1189.

Cluster diagnostics: G = 81, treated clusters 12, effective clusters G\* = 23.6, cluster-size CV 2.267.

---

## 4. No point estimate is stable to a single cluster deletion

Source: `f3_loco.csv`, `204_se_diagnostics.log`.

| Window | Full coef | Leave-one-out range | Sign flips | Flipping cluster |
|---|---|---|---|---|
| 30d | +0.0168 | [−0.0022, +0.0388] | 1/81 | T-Mobile (treated, 26 events) → −0.0022 |
| 90d | −0.0169 | [−0.0492, +0.0675] | 2/81 | FIS (control, 12) → +0.0675; AT&T (treated, 26) → +0.0025 |
| 180d | +0.0434 | [−0.0196, +0.0942] | 1/81 | T-Mobile → −0.0196 |

**Settled language:** the null is robust; the point estimates are not. Both sentences belong in the results. A single cluster deletion moves the sign in either direction at every window. With 12 treated clusters and G\* = 23.6, no point estimate should be interpreted directionally.

---

## 5. Placebo

Source: `f4_placebo.csv`, `202_estimation.log:13`. Outcome measured in (t0 − 180d, t0], before public notification.

Coef −0.0658; CV3 p .5281, CI [−0.2724, +0.1408]; WCR p .4060. Means: treated .224, control .203.

**Settled reading:** no pre-disclosure gap. Treated and control firms are not on different executive-departure trajectories going into notification. The placebo neither supports nor undermines an effect that F1 did not find.

---

## 6. Sensitivities

Source: `f3_sensitivities.csv`, `202_estimation.log:25-59`. Nine specifications × three windows = 27. **All null.** Smallest CV3 p is .1532.

| Sensitivity | 30d (CV3 p) | 90d (CV3 p) | 180d (CV3 p) |
|---|---|---|---|
| Year FE | +0.0219 (.5092) | −0.0002 (.9984) | +0.0636 (.4832) |
| Two-digit SIC FE | +0.0404 (.3907) | +0.0868 (.6038) | +0.1494 (.5508) |
| breach_date anchor (N = 337) | −0.0057 (.8962) | −0.0635 (.4627) | −0.0334 (.7885) |
| Excluding pre-announced departures | +0.0334 (.1990) | +0.0273 (.7575) | +0.0932 (.4110) |
| Excluding the F2 baseline control | +0.0167 (.5735) | −0.0181 (.8554) | +0.0445 (.6706) |
| Restatement-dated outcome | +0.0491 (.4163) | +0.0155 (.8982) | +0.0161 (.9261) |
| Recall-corrected, audit point estimates | +0.0177 (.6817) | −0.0387 (.7755) | +0.0135 (.9264) |
| Recall bound, r_T low / r_C high | +0.0366 (.3779) | +0.0457 (.7105) | +0.2225 (.1532) |
| Recall bound, r_T high / r_C low | +0.0009 (.9884) | −0.1535 (.4572) | −0.2333 (.2444) |

**Two hard rules:**
1. The last two rows are **bounding exercises, not estimates** (`row_type` column). They take treated and control recall from opposite ends of their confidence intervals.
2. **HC3 is disqualified in every row** (`hc3_status` column). The 180-day bounding row shows HC3 p = .018; its valid CV3 p is .1532. That number must never appear as significant in any table or sentence.

**SIC FE caveat:** only two SIC2 cells contain treated events, SIC 48 (102 treated / 24 control) and SIC 73 (5 / 114). Under SIC FE, treatment is identified almost entirely off SIC 48's 24 controls. Report the specification, note the caveat, do not lean on it.

---

## 7. Measurement: the classifier and its validation

This is a contribution section, not a methods footnote.

**What the old measure was.** The circulated draft's outcome counted any 8-K in the window (`46_executive_changes.py:65`). The v3 outcome counted any Item 5.02 filing, which reaches appointments, elections, and compensation arrangements as well as departures.

**How far off that is.** On the notification anchor at 180 days, **135 of the 231 events with any Item 5.02 filing have no executive departure** (`c_crosswalk.csv`). More than half of what the prior measure called turnover was not executive departure.

**The classifier.** Deterministic rules, no ML. Final version v2, `scripts/195_essay3_q2_classifier_v2.py`, commit `6f7be7a`, blob `ec32364`. Frozen before the round-2 draw.

**Deduplication.** 768 departure mentions collapse to 513 departure events (300 executive, 213 director); 63 events span more than one filing, folding 70 filings into an earlier disclosure. One false merge (corporate words read as a person name) was found and fixed before the freeze.

**Validation.** Reference codes are Claude's, coded blind from filing text under written rules, with a logged verification pass. Tim did not hand-code; the report records this.

| Round | Classifier | Executive κ | Executive recall | Notes |
|---|---|---|---|---|
| 1 (80 filings) | v1, frozen `d39bc6d` | .803 (.876 excl. 7 T-Mobile) | .79 | Informed v2's fixes |
| 2 (30 filings) | v2, `6f7be7a` | .713 | .60 (3/5) | Out-of-sample; 0 CEO positives |
| Recall audit (80, stratified) | v2 | .787 | .80 overall | Treated .842 / control .750 |

**Direction of error.** v2 makes no false-positive executive-departure calls in either round. Its errors are misses only.

**Differential recall: checked and not confirmed.** Round 2's misses all landed on carriers, which would have biased the gap downward. The stratified audit with real counts reversed the lean: treated recall .842 [.604, .966] vs control .750 [.476, .927]. The intervals overlap almost entirely.

**Exhibit-only departures.** Some filings keep the departure only in an exhibit the classifier does not read (the audit's Carnival filing is the clear case). By an unverified heuristic, these are more common in control filings: 12.8% vs 5.7%. If systematic, this under-counts control departures and pushes the gap **upward**, not toward zero.

**Documented recall limitations, by name:** "would be leaving" (a tense variant); a role change to Executive Advisor set only in an employment agreement; an interim-title implied departure. Stopping rule: no revisions after round 2, because every post-round fix requires another blind round.

**CEO-only is not estimable.** Audit precision and recall are both .571, and at least one group has fewer than 10 events at every window. Counts only (F5): 30d 0/1, 90d 4/7, 180d 8/22 (treated/control). Director-only is descriptive (F6): 8/3, 18/15, 21/43.

---

## 8. Reproducibility

A clean clone from GitHub at `c5f761d` ran scripts 195–204 end to end; every emitted file matches the committed version. `run_all` and script 158 were not run.

Two silent-degradation failures were found and fixed, and both belong in the methods note on why reproducibility is verified from a clean clone rather than assumed:
1. A `.gitignore` rule excluded 31 filing texts. Script 195 did not crash; it coded 1,047 of 1,078 filings, exited normally, and emitted a different treated 180-day rate.
2. Commit `5f5c950` (March, "quota exceeded") dropped the LFS rule for six input files, so checkout silently delivered 136-byte placeholders.

**Open, not an Essay 3 blocker:** 87 other LFS files across Essays 1 and 2 have the same missing rule and arrive as placeholders in a clean clone. Those essays are currently not reproducible from GitHub.

---

## 9. T-Mobile

**Weight in the treated set** (`g1_weights.csv`): 26 of 106 treated events at the Query 1 level (.245); T-Mobile plus Sprint is 37 of 106 (.349). This is the stated reason the essay leans on T-Mobile: the treated sample does.

**Departures within 180 days of notification** (`g6_case_table.csv`): 4 distinct departures across 13 event–departure pairs.

| Departure (first filing) | Title | Events | Flags |
|---|---|---|---|
| Gary A. King, 2016-02-19 | EVP and Chief Information Officer | 3 | termination, severance/release — **no retirement, transaction, or pre-announced flag** |
| David A. Miller, 2021-09-16 | EVP, General Counsel and Secretary | 6 | retirement |
| Neville Ray, 2023-02-13 | President, Technology | 1 | retirement |
| Peter Ewens, 2023-09-08 | EVP, Corporate Strategy & Development | 3 | retirement |

3 of 4 distinct departures (10 of 13 pairs) carry a flag. King is the only one that does not.

**The "health" flag is a false positive** on Ray and Ewens: it matches benefit-continuation language ("health and dental benefit coverage"), not illness. Do not report it.

**Legere and Carter are outside the window, and this is a finding.** The 2019-11-18 filing (0001193125-19-294093) disclosed both: Legere ceasing to serve as CEO effective April 30, 2020, and Carter's employment terminating at his term's expiration. That is 8 days before the 2019-11-26 breach date and 105 days before its notification. Both therefore fall in the placebo window, not the outcome window. The Sievert employment agreement is dated November 15, 2019. Under the restatement-dated sensitivity they enter at +30d and +107d. The 2020-04-01 exhibit calls it the "long-planned Chief Executive Officer transition."

**Governance context** (Parts G3, G4):
- Deutsche Telekom's stated control runs through every proxy year, from ~74% fully diluted (2013) to 54.5% voting control (2026).
- **Pay:** three proxies adjust the incentive free-cash-flow metric for the August 2021 cyberattack — 2023 (adds back $40 million, "excludes the impacts of the cyberattack"), 2024 (subtracts $290 million for settlement payment timing), 2026 (the gap between assumed and actual attack costs). The 2025 proxy has no such adjustment and gives no reason. **Report what the filings say; interpretation belongs in the discussion.**
- **Money:** a ~$400 million pre-tax charge (Q2 2022) and $150 million of committed incremental security spending for 2022–2023.
- **Security leadership:** Item 1C first appears in the 10-K filed 2024-02-02. The CSO presents to the Nominating and Corporate Governance Committee, which oversees data-privacy and information-security risk. The 2026 10-K places the cybersecurity SVP under the Chief Information Officer. No CISO appears in any Item 5.02 filing, and a CISO change would ordinarily not be reportable — so the absence of security-leadership departures is not evidence that none occurred.
- **Disclosure channel:** only 5 of 34 T-Mobile events have an incident 8-K within ±30 days of notification (the August 2021 events and the January 2023 API incident). 20 events trace to a state AG record.

**Timeline:** `tmobile_timeline.csv`, 173 dated rows.

---

## 10. Test ledger

31 tests: 3 primary, 1 placebo, 27 sensitivities. BH within family. No test rejects, raw or adjusted. Logit AMEs, F2, F5/F6 counts, and leave-one-out are descriptive or corroborating and are not counted.

---

## 11. Claims the circulated draft makes that the evidence no longer supports

Each of these must be removed, not softened.

| Draft claim | Current state |
|---|---|
| The rule moved disclosure timing (14.52 pp first stage) | No first stage. 16.71 pp had no computed source; the Essay 3 first stage does not survive removal of zero-delay records (+2.15 pp, p .55) |
| Mediation: immediate disclosure carries the effect | No mediation. The legacy "indirect effect" was the total effect; a and b have opposite signs |
| The indirect effects confirm it | Table A6's column was mislabeled |
| Adding immediate disclosure does not move the FCC coefficient | It moved at every window and flipped sign at 180 days |
| The null is held to a stricter standard than the design requires | Inverted. The MDE exceeds the equivalence bound, and at 90 and 180 days it exceeds the control base rate |
| TOST-bounded equivalence | No equivalence test (decision L4) |
| Turnover base rates of 37.9% at 30 days | That measure counted any 8-K. Executive departure at 30 days is .037 treated / .043 control |
| BoardEx cross-validation | BoardEx was never in the pipeline |
| Natural experiment, quasi-experimental, causal evidence | Post-2007 cross-sectional. No treated pre-rule events |
| The rule requires disclosure within seven business days | The seven-day clock runs to law enforcement; public notification is embargoed for seven further business days |
| Cox hazard results, negative binomial counts, placebo tests as specified | Not in the v2 chain. Nothing carries over |
| 651 observations, 140 treated, SIC 4810 treatment | 338 events, 107 treated, Form 499 treatment |
| September 28, 2007; four pre-2007 records | December 8, 2007; 6 pre-rule events, all control |

---

## 12. Open items

- **Adjudication.** `ADJUDICATION.xlsx` holds 17 round-1 disputes, 5 round-2 disputes, and 2 rows the reference coder flagged. These affect the reported validation statistics, not the estimates. Tim adjudicates.
- **Two flagged officer-status rows:** Sprint's Schwartz (round 1) and Sprint's Crull (round 2). Both were coded as executive departures without confirmed executive-officer status.
- **87 LFS files** for Essays 1 and 2 (section 8).
- **Title.** "Compliance Without Accountability" is consistent with the findings. Decided at the spine stage.
- **The dissertation's locked closing argument** still claims the rule produces faster disclosure. Essays 2 and 3 both contradict it.