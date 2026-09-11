# Essay 3 — Handoff Document

Written September 11, 2026. Purpose: let any new chat pick up Essay 3 without reconstructing this session.

**Read these three files first, in order:**
1. `claude_ESSAY3_POST_RERUN_STATE.md` — the settled empirical state, with provenance.
2. `claude_ESSAY3_PRE_RERUN_AUDIT.md` — the tiered punch list against the circulated draft.
3. This file — decisions, verification results, and what happens next.

Repository pointer file: `outputs/essay3_q2/ESSAY3_STARTING_POINT.md` (commit `ebe5c0f`).

---

## PART 1 — Where Essay 3 stands

**Finished.** The data work is complete and reproducible. A clean clone from GitHub at `c5f761d` runs scripts 195–204 end to end and reproduces every committed output. `run_all` and script 158 were not run and must not be.

**Not started.** No prose. The circulated draft (*Compliance Without Accountability*) predates the rebuild and cannot be edited into shape section by section; most of it rests on claims that no longer exist.

**The essay in one paragraph.** A post-2007 cross-sectional study of whether FCC-regulated carriers show more executive-officer departure after a breach becomes public. Outcome: Item 5.02(b) executive departure measured from the public notification date, one departure per person per parent CIK, dated to its earliest disclosing filing. Treatment: Form 499 two-clause rule. Sample: 338 events, 107 treated, 12 treated parent CIKs, G = 81, G\* = 23.6. The hypothesis is not supported at 30, 90, or 180 days on any inference rung. The pre-disclosure placebo shows no gap. All 27 sensitivities are null. At 90 and 180 days the MDE exceeds the control base rate.

---

## PART 2 — Decisions made in this session

| # | Decision | Status |
|---|---|---|
| D1 | Outcome is Item 5.02(b) executive-officer departure; CEO-only secondary; directors descriptive | Locked, built |
| D2 | Primary anchor is the public notification date; breach date is a sensitivity | Locked, built |
| D3 | `immediate_disclosure` removed from the model; no mediation analysis | Locked |
| D4 | No TOST, no equivalence claim | Locked |
| D5 | Validation by an independent blind rater (Claude), not by Tim | Done, disclosed in the report |
| D6 | Restatement ruling: one departure per person per parent CIK, dated to first disclosure | Locked, built |
| D7 | Pay-agreement-only departures count; vacancy mentions count for directors only; pre-announced includes effective dates | Locked, built |
| D8 | Stopping rule: no classifier revisions after round 2 | Locked |
| D9 | v2 is final: `scripts/195_essay3_q2_classifier_v2.py`, commit `6f7be7a`, blob `ec3236471df71279531e0593304eb7b478b210b9` | Frozen |
| D10 | Essay 3 runs on today's CANONICAL_V3 (338); global rebaseline deferred | Locked |
| D11 | HC3 disqualified everywhere; CV3 and wild cluster bootstrap govern | Locked |
| D12 | The six corner-case recall rows are bounding exercises, not estimates; they stay in the BH family | Locked |
| D13 | Dissertation is a T-Mobile case study; the explicit framing lives only in the front and back matter; no essay calls itself a "part" and no essay cross-references another | Confirmed (decided earlier in Essays 1 and 2, reaffirmed here) |
| D14 | Theory stays Mitchell, Agle, and Wood (1997) stakeholder salience; the hypothesis moves from the deadline to regulatory status | Decided, not yet written |
| D15 | Title is open. "Compliance Without Accountability" is consistent with the findings but promises more than the design delivers | Open, decide at the spine stage |

---

## PART 3 — Verification done in this session

Everything below was checked against primary sources during this session. Findings that change the essay are marked **NEW**.

### Rule characterization — confirmed, current as of today
Verified against eCFR (title 47 current as of 9/03/2026), Cornell LII, and FCC 22-102:
- § 64.2011(b): seven business days run to the Secret Service and FBI after the carrier's reasonable determination.
- § 64.2011(a) and (b)(1): the carrier **shall not** notify customers or disclose publicly until seven full business days have passed after law-enforcement notification, notwithstanding any state law to the contrary.
- Law enforcement may direct non-disclosure for an initial 30 days, extendable.
- § 64.2011(c) requires customer notification after the law-enforcement process, with **no outer deadline**.
- § 64.2011(e): a breach requires that access, use, or disclosure be **intentional**.
- The 2024 amendments (FCC 23-111, 89 FR 9968, published 2024-02-12) are effective March 13, 2024 **except** the amendments to § 64.2011 and § 64.5111, which are **delayed indefinitely** pending OMB approval. eCFR still displays the 2007 text. The Sixth Circuit upheld the 2024 order in August 2025; the § 64.2011 amendments remain not in effect.

**Conclusion: the project instructions are accurate.** The 2007 text governs the entire sample period (2006-12-01 to 2024-12-20).

### **NEW — the breach-type finding that reframes the lit review**
Banker and Feng (2019), *Journal of Information Systems* 33(3), 309–329:
- Breaches caused by **system deficiency** raise CIO turnover likelihood by 72 percent.
- **No such association for breaches caused by criminal fraud or human error.**
- CEOs are more likely to turn over after system-deficiency and human-error breaches. **No CFO effect.**

Essay 3's sample applies the Kamiya et al. (2021) inclusion rule: external malicious action. Section 64.2011(e) likewise covers intentional access only. So the sample is concentrated in exactly the breach category where the closest prior study finds **no turnover response**.

This is a theoretical prediction of Essay 3's null, available before the fact and from an independent sample. It belongs in the hypothesis development, not in the discussion as an excuse. It also supplies the honest framing: the essay tests whether regulatory status changes a board response that prior work already finds absent for criminally caused breaches.

### **NEW — the null has company**
Liu and Babar (2026), systematic review of 203 empirical cybersecurity studies, *Australian Journal of Management*: post-breach executive turnover findings are mixed.
- Increased turnover: Banker and Feng (2019), Lending et al. (2018), Say and Vasudeva (2020).
- No evidence of increased turnover: **Tosun (2021) for CEOs**, Li et al. (2021b) for CIOs, Hilary et al. (2016) for top-five executives.

Tosun is already in the project files (`Tosun.pdf`). A CEO-turnover null in a published paper is a direct precedent and should be cited in the hypothesis section, not buried in limitations.

### Citation errors confirmed (Tier 3 of the audit)
- **Xu, Guo, Haislip, and Pinsker (2019)** is *Earnings Management in Firms with Data Security Breaches*. It is **not** about CEO turnover. The draft's citation for elevated post-breach CEO turnover is wrong. Remove or replace with Banker and Feng (2019).
- **Gentry, Harrison, Quigley, and Boivie (2021)**, *SMJ* 42(5), 968–991: an open-source CEO turnover and dismissal database for **S&P 1500 firms, 2000–2018**, with eight departure classifications, narrative descriptions, and source links. The Zenodo release also includes 8-K filings from 270 days before and after each departure. Coverage ends in 2018, and Essay 3's sample runs to 2024, so it cannot validate this sample. It **is** the right citation for the measurement point that independent coders disagree about why CEOs leave.
- **Banker and Feng's 72 percent** is verified, but it applies to **CIO** turnover after **system-deficiency** breaches only. Any use of "72%" must carry both qualifiers.

### Still to verify before the lit review is finished
Not yet checked in this session: Donaldson and Preston (1995) miscitation (audit says it is a theory paper with nothing on breaches), Hirschman (1970) attributed jointly to Freeman (1994), Lending et al. (2018) described two ways, Say and Vasudeva (2020), Agarwal et al. (2024), Ashraf et al. (2022) "90 percent faster," Kamiya et al. (2021) dollar figures, Hermalin and Weisbach (2003) paraphrase, MacKinlay (1997) used as the framework for a logit, Smith and Tonidandel (2003), Roman (2014) on Target. Also confirm **17 C.F.R. § 229.106** (Regulation S-K Item 106) versus **Form 8-K Item 1.05** (the four-business-day incident disclosure), and **45 C.F.R. § 164.404** ("without unreasonable delay and in no case later than 60 calendar days").

---

## PART 4 — What to ask Python next

Nothing is required before the lit review. These are the outstanding items, in order.

**Tonight, if not already sent:**
> Force-add the settled-state document as `docs/claude/ESSAY3_POST_RERUN_STATE.md`, commit and push. Do not restore the LFS rule for the 87 files yet.

**When the methods section starts:**
> Print, for the methods and appendix tables: the Part E attrition ledger with treated and control at every step; the F1 ladder with all four rungs; cluster diagnostics (G, G1, G\*, cluster-size CV); the F2 baseline distribution; the validation tables for both rounds and the stratified audit, with Clopper–Pearson intervals; and the test ledger with BH values. Every figure from its committed file, with file and line.

**When the T-Mobile case section starts:**
> Print `tmobile_timeline.csv` in full, `g6_case_table.csv` with the verbatim excerpts, the three proxy pay-adjustment passages verbatim with proxy year, the 10-Q and 10-K charge and settlement sentences verbatim, and the Item 1C passages verbatim for each 10-K year.

**Deferred to Essays 1 and 2 (do not start now):**
1. Restore the `.gitattributes` LFS rule for the 87 files. **All 87 objects are confirmed present on GitHub's LFS service**, so this is a missing rule, not a quota or re-upload problem. Restore `Data/` paths first, then `outputs/` paths after the rebaseline, so 1.82 GB of soon-to-be-regenerated outputs is not pinned into every clone.
2. Retire or relabel script 158's Essay 2 volatility block, which prints "SIGNIFICANT" (p = .029) for a specification Essay 2 disqualified.
3. Rebaseline `constants_v3.json` after the DISH top-up. The diff is computed and reviewed: 94 of 121 constants change, **no Essay 1 verdict changes**, ROA is not significant in either version (p .160 → .153).
4. Revise Essay 2's DISH wording to "excluded before July 1, 2020, treated after."
5. Remove script 46 from `run_all`; clean up the 47 legacy Essay 1 and 2 scripts that depend on script 53. Script 53 itself cannot be retired.
6. Run the Essay 1 consistency pass against v3, including whether its prose claims ROA is a significant predictor of CARs.

---

## PART 5 — Writing plan

Order: **literature review → methods → results → introduction → conclusion.** Same order Essay 1 used; the introduction is written last because it must summarize settled findings.

### Literature review (start here; no pipeline runs needed)
1. **Delete the first paragraph's result announcement** ("The result is compliance without accountability").
2. **Recharacterize the rule** everywhere. Remove every sentence saying it forces fast public disclosure or that firms had no choice about when to disclose. The verified text is in Part 3 above.
3. **Rebuild the mechanism.** The old chain (deadline → urgency → salience → board response) is dead: Essays 2 and 3 both show the rule does not move observed timing. The new chain rests on regulatory status under Mitchell, Agle, and Wood:
   - For an unregulated firm the FCC holds legitimacy at most: a discretionary stakeholder.
   - For a Form 499 registrant it also holds coercive power (enforcement authority, consent decrees, an ongoing licensing relationship): a dominant stakeholder.
   - The rule supplies little public **urgency**: the seven-day clock runs to law enforcement and public notification is embargoed afterward. A dominant stakeholder is not a definitive one, which predicts a smaller effect ex ante.
   - Cite Mitchell, Agle, and Wood for the attribute framework and salience typology only. Never for empirical claims about post-breach outcomes; that is the error the draft made with Donaldson and Preston.
4. **Add the breach-type argument** from Banker and Feng (2019) and the mixed-findings literature including Tosun (2021). See Part 3.
5. **Move the measurement literature into the review** (Gentry et al. 2021; Parrino 1997), since measurement is now a contribution rather than a methods detail.
6. **Fix the citations** listed in Part 3 and the audit's Tier 3.
7. **Restructure the source-by-source paragraphs** (Kamiya, Gordon, Diamond–Verrecchia).
8. **State one testable prediction, in the null**, and give it a hypothesis section. The draft never names H6 and predicts three different things in three places.

### Methods
Sample from the Part E ledger. Treatment from Form 499. Outcome and classifier from section 7 of the settled state, written as a contribution. Inference ladder with CV3 primary. The MDE discussion goes here and is repeated in results. Add the Essay 2 R50 limitation in Essay 3's own words: treatment marks firms the rule can reach, not events the rule did reach, because § 64.2011 covers CPNI only and the August 2021 T-Mobile breach exposed Social Security and driver's license numbers, which are almost certainly not CPNI.

### Results
F1 ladder, placebo, sensitivities, leave-one-out, CEO and director counts. Two sentences that must both appear: the null is robust, and the point estimates are not. Name FIS as the 90-day variance driver with the 65.6% figure. State the MDE against the control base rate at each window.

### T-Mobile case section (after results)
Fuller than Essays 1 and 2 received, because the material is richer here. Weight in the treated set, the four departures with flags, Legere and Carter's pre-breach disclosure, the Deutsche Telekom control record, the three proxy pay adjustments, the $400 million charge and $150 million committed spending, Item 1C security leadership, and the disclosure-channel counts. Quote filings exactly; interpretation goes in the discussion.

### Introduction and conclusion
Last. No cross-references to Essays 1 and 2.

---

## PART 6 — Standing rules for any chat working on this essay

- No number enters prose without provenance in a pasted pipeline output or a named committed file. Not from memory, not from the circulated draft, not from the project instructions.
- Sum every subgroup table's Ns; verify attrition closes arithmetically.
- When a sentence resists revision, it is usually built on a claim that no longer exists. Delete rather than bend.
- Exact find-and-replace edits, one at a time, with confirmation. Tim holds the authoritative draft.
- "Confirms" only for significant results. "The hypothesis is not supported" for nulls.
- No natural-experiment, quasi-experimental, or causal language.
- No cross-references between essays.
- Watch for silent pipeline degradation, not just crashes. Two Essay 3 failures emitted wrong numbers without erroring.
- Anticipate Lambert (pipeline and classifier), Affuso (clustering, G\*, economic significance), Zeng (microstructure), Johnson (framing and governance).

## PART 7 — The purge list, Essay 3 specifics

Never write: Rule 37.3; September 28, 2007; June 8, 2007 as an effective date; "1,054 breaches"; any characterization of § 64.2011 as a customer- or public-disclosure deadline; 14.52 pp, 16.71 pp, or 15.05 pp as a first stage; N = 651 or 648; 140 or 115 treated; SIC 4810 treatment; BoardEx cross-validation; any Item 5.02 incidence rate called turnover; the "health" flag on Ray and Ewens; any equivalence or TOST claim; any HC3 p-value presented as significant.