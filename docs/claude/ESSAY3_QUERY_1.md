# Essay 3 — Query 1: What Exists, and Where the Rebuild Starts

This is a discovery query. Its purpose is to establish what the repository currently contains for Essay 3, answer two gating questions, and pull the T-Mobile record. It is not a fix query.

Companion: `claude/ESSAY3_PRE_RERUN_AUDIT.md` (tiered audit of the circulated draft). Section numbers below reference it.

---

## PART 0 — Standing rules for this query

- **Report what you find, not what you expect.** The circulated draft is known to be wrong. Do not use it as a reference for what the code "should" produce.
- **Print verbatim.** For any value already emitted by a script, print it from the named output file with file path and line number. Do not recompute it. State "not recomputed" next to each such value.
- **Where this query asks for a new computation, label it NEW** and name the script that produced it.
- **Do not edit any existing script, table, or prose.** New scripts go in `scripts/` with the next free number and a `essay3_q1_` prefix.
- **Do not fix anything you find broken.** Record it. Fixes come in Query 2.
- Output: `outputs/ESSAY3_QUERY1_REPORT.md`. State at the top whether it is committed or gitignored (`.gitignore` line 79 excludes `outputs/*.md`). Commit it anyway with `git add -f`.
- Every sentence citing a treated N names its sample level.

---

## PART A — Inventory

### A1. Which code produces Essay 3?
List every script that reads, constructs, or estimates anything for Essay 3 (H6), including: script 46 (Item 5.02 extraction and cache), script 91e (TOST), the v3 rebuild Stage 6, and anything numbered 150–177 that touches turnover. For each: path, tracked or untracked, inputs read, outputs written, last commit date.

### A2. Which chain generated the current Essay 3 results?
Pre-v3 (the 651-observation chain), v3, the 7/28 audit chain, or something else? Is H6 in `constants_v3.json` / `CONSTANTS_BLOCK_V3.md`? If yes, print the H6 block verbatim.

### A3. Does `run_all.py` regenerate Essay 3 from a fresh clone?
Name every Essay 3 input that is not committed (EDGAR caches, registry snapshot, WRDS extracts). This is the failure Lambert already hit.

### A4. What do the current v3 Essay 3 outputs say?
Print verbatim, with file and line: sample N, treated N, turnover base rates at 30/90/180 days, the H6 coefficients and p-values at each window, the first-stage estimate, the Cox estimate, and any MDE or equivalence output. Do not interpret.

---

## PART B — The outcome variable (gating, audit §2.1)

Essay 3 will measure executive turnover. Item 5.02 incidence is not an acceptable substitute. This part determines whether the repository can support that.

### B1. Confirm what the old variable counted
Read the code that produced the 651-observation turnover variable. Did it count any 8-K in the window, any Item 5.02, or something else? Quote the relevant lines.

### B2. What does the script 46 cache retain?
For each cached filing: does it store (a) only item flags, (b) the Item 5.02 section text, or (c) the full filing document? Print the schema and three raw example entries.

### B3. Can departures be separated from everything else?
Item 5.02 has sub-items: (a) director resignation or refusal to stand for reelection due to disagreement, (b) departure of the principal executive officer, president, principal financial officer, principal accounting officer, principal operating officer, or a named executive officer, and director departures, (c) appointment of those officers, (d) election of directors, (e) compensatory arrangements, (f) supplemental compensation.

If the cache retains text (B2 = b or c):
- Build a NEW classifier flagging 5.02(b) departures, and separately flagging departures of the **principal executive officer (CEO)**. Rules-based first (sub-item headers plus departure verbs such as resign, retire, terminate, step down, depart), no ML.
- Report counts by sub-item across the Essay 3 sample.
- Report NEW base rates at 30/90/180 days for: any 5.02 filing; any 5.02(b) departure; CEO departure only.
- **Hand-validation:** draw 40 events at random (seed stated). For each, print the filing URL, the classifier's call, and the relevant text excerpt, so the calls can be checked by hand. Report the classifier's agreement with the text as read.

If the cache retains flags only (B2 = a):
- State that plainly.
- Scope the re-pull: number of 8-K filings in the Essay 3 event windows, the EDGAR endpoints required, rate-limit time estimate, and storage.
- Do not start the re-pull.

### B4. BoardEx
`grep -ri boardex` across the repository. Is BoardEx data present anywhere? Did any script ever read it? The circulated draft claims BoardEx cross-validation.

### B5. Event anchor
Which date is t = 0 in the turnover code: breach occurrence, discovery, reasonable determination, or public notification? Quote the line. Where does the date come from in PRC or elsewhere?

### B6. Forced versus voluntary
Report whether the 5.02 text in the cache is sufficient to support a departure-reason classification (for example, the Parrino 1997 or Gentry et al. 2021 approach). Feasibility only, no coding.

---

## PART C — The first stage and Essay 2 (gating, audit §2.2)

Essay 2's settled state: Form 499 treatment does not predict disclosure delay, in any form. The circulated Essay 3 draft reports 14.52 pp; notes carry a v3 figure of 16.71 pp. The two essays may reach different conclusions about governance. They cannot report different answers to the same question about disclosure timing on the same events.

### C1. Where does 16.71 pp come from?
Find the script and output file. Print it verbatim. If it cannot be found, say so.

### C2. How is `immediate_disclosure` built?
Quote the code. Which two dates, calendar or business days, and how are missing dates handled?

### C3. The zero-delay default
Report the share of Essay 3 events with delay exactly 0, treated and control, at the Essay 3 regression level. Compare with Essay 2's 34.8% figure (print that from its output file).

### C4. Reconcile (NEW)
On the Essay 3 regression sample, Form 499 treatment:
1. First stage as currently coded (≤7-day binary)
2. Same, excluding zero-delay records
3. Continuous delay (raw and log), matching Essay 2's specification

Report all three side by side with Essay 2's corresponding estimates printed from its output files. State in one sentence whether the Essay 3 first stage survives removal of zero-delay records.

---

## PART D — Sample and treatment (audit §1.4, §1.5)

### D1. Essay 3 attrition ledger
From 1,054 records to the Essay 3 regression sample, one line per step, each with its count and a closing check. The succession-data requirement is its own line. Where does Essay 3 depart from the canonical chain (1,054 → 784 → 779 → 672 → 648), and why?

### D2. Treatment
Confirm treatment is the Form 499 two-clause rule, not SIC. Treated N at every sample level, each with organization count and parent CIK count. List the treated organizations with parent CIK.

### D3. Pre-rule observations
Under the December 8, 2007 effective date: count of Essay 3 events before the cutoff, and how many are treated.

---

## PART E — T-Mobile (the case-study thread)

T-Mobile, CIK 0001283699 (formerly MetroPCS Communications Inc.), is the implicit case study in Essay 2. Pull its record for Essay 3.

### E1. Events
Every T-Mobile event in the Essay 3 sample: breach date, notification date, the date used as t = 0, record count collapsed into the event, and whether the event survives to the regression sample. Include events attached to the parent CIK under a predecessor name.

### E2. Governance filings in the windows
For each event, every 8-K Item 5.02 filing within 180 days: filing date, days from t = 0, sub-item, the officer named, and a text excerpt. If none, say none.

### E3. The CEO and security leadership
Does any filing in E2 involve the principal executive officer? Note separately whether the cache contains any officer title related to information security, since CISOs and CIOs are usually not named executive officers and would not appear in Item 5.02. State whether that limits what the case can show.

Print; do not interpret.

---

## PART F — Model structure (audit §0.7–§0.9)

### F1. Industry fixed effects
At what level are industry FE defined? Is `fcc_reportable` collinear with them? If not, why not? Report how many FE cells contain treated firms.

### F2. Clustering
What variable are standard errors clustered on? How many clusters, and how many contain treated events?

### F3. Controls
List every control in the current H6 model as the code estimates it. Is prior breach history computed on records or events?

### F4. TOST
Print the `Z_CRITICAL` value hardcoded in `scripts/91e_essay3_h6_tost_equivalence.py` with line number. Does it match a 90% CI (1.645)? Is 91e in the v3 chain or retired?

---

## PART G — Reconciliation of the current v3 Essay 3 outputs

For every coefficient table the v3 chain emits for Essay 3:
- Assert `t == coef/se` and `p == 2*(1 - cdf(|t|))`. Report any failure and its size. **Test explicitly for a constant ratio between reported t and coef/se.**
- Any reported CI: does it reproduce its p-value?
- Any mediation output: does the reported indirect effect equal a × b in sign and approximate magnitude?

---

## PART H — Test inventory

Every hypothesis test the Essay 3 code currently runs, with file and line. Total count.

---

## Report back

Order: **B, then C, then E, then A, D, F, G, H.**

B decides whether the essay can measure executive turnover with what is on disk, or needs an EDGAR re-pull first. C decides what Essay 3 can say about disclosure timing without contradicting Essay 2. E decides whether T-Mobile carries any turnover evidence at all, which the case-study framing depends on.

Close the report with three sentences:
1. Can executive turnover (5.02(b), and CEO-only) be built from the existing cache: yes, no, or partially?
2. Does the Essay 3 first stage survive removal of zero-delay records?
3. Does T-Mobile have any Item 5.02(b) departure within 180 days of any breach event?
