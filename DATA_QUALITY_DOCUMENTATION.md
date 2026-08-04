# Data Quality and Entity Matching Documentation

## Overview

This dissertation analyzes market and governance responses to data breaches among publicly-traded firms (2005–2023). Four systematic data-construction errors required detection and correction before hypothesis testing:

1. **CIK-to-CRSP fuzzy-match duplicates** (firm-level duplication)
2. **Form 499 name-token collisions** (brand-vs-subsidiary mismatch)
3. **SIC code as regulatory proxy** (industry classification ≠ regulatory status)
4. **Silent outcome-extraction failure** (Item 5.02 detection never fired; stale any-8-K measure substituted silently)

This section documents each failure mode, its detection, the correction applied, and impact on inference.

---

## Failure Mode 1: CIK-to-CRSP Mapping Duplicates

### Problem
The initial entity-linking algorithm used string-similarity scoring (fuzzy matching) to link PRC breach records to CRSP stock returns by firm name. Fuzzy matching produces fuzzy results: a high-similarity match is probable, not certain.

### Detection and Scope
- **CIK audit conducted July 28, 2026** against SEC Master Index
- Matched 41 FCC-regulated carriers (direct lookup) and 13 T-Mobile subsidiary breaches
- Identified 110+ corrupted mappings where fuzzy scoring created false-positive duplicate links
- Example: A merger or subsidiary spin-off created multiple valid CRSP records for the same CIK; fuzzy-match algorithm assigned one breach event to multiple ticker-years

### Sample Impact
| Metric | Before Dedup | After Dedup | Change |
|--------|--------------|-------------|--------|
| Total observations | 784 | 779 | -5 |
| CRSP-matched | 677 | 672 | -5 |
| H1-H4 regression N | 652 | 648 | -4 |

The four-observation drop in the final regression sample reflects both the deduplication (5 obs) and recovery of 1 observation with complete controls.

### Correction Method
1. Parse SEC Master Index CIK-to-ticker mapping
2. For each firm in the sample, verify CIK matches CRSP identifier
3. Recompute abnormal returns (CAR) using authoritative ticker mapping
4. Validate through hand-matching of 10 largest carriers (Comcast, AT&T, Verizon, Sprint, Charter, Frontier, Altice, T-Mobile, Cricket, Twilio)

### Result
Removed spurious duplicates. Firms now appear once with correct CRSP returns. This correction is necessary but does not change the causal interpretation of the treatment effect—it only removes noise from the outcome variable.

---

## Failure Mode 2: Form 499 Name-Token Identifier Collisions

### Problem
The FCC Form 499 filer registry contains 20,669 records of carriers required to file with the FCC under 47 CFR Part 32 (accounting reporting). The PRC dataset records consumer-visible breach disclosures. These datasets use different naming conventions:

- **PRC names** (consumer-visible brands): "Comcast", "Charter", "T-Mobile", "Verizon"
- **Form 499 names** (filing entities, legal structures): "Comcast Telephony Communications of Maryland, Inc.", "Charter Communications Operating, LLC", "TMUS Fiber LLC"

A direct string match between these two naming systems produces high false-negative rates.

### Detection and Scope
- **Exact-string matching attempt** (names normalized: uppercase, punctuation removal, suffix stripping)
  - Match rate: 107 of 779 observations (13.7%)
  - False negatives: Major carriers (Comcast, Charter, Frontier, Altice, AT&T Services) incorrectly marked untreated
  - False positives: NBCSports marked treated (media subsidiary, not telecom)

### Unit Mismatch Root Cause
A consumer brand (e.g., "Comcast") and its subsidiary filing entity (e.g., "Comcast Telephony Communications of Maryland, Inc.") are not variants of the same string—they are different legal entities. A brand-name breach affects the parent company and its regulatory status, but the actual Form 499 filer is the subsidiary.

### Correction Method: Two-Clause Classification Rule

**Rule:** A breach is treated (subject to FCC 7-Day Rule) if:
1. **(Clause A)** The breached entity is itself a Form 499 filer at the breach date, **OR**
2. **(Clause B)** The breached entity is a consumer brand of a Form 499 filer **AND** the breach involves telecommunications/subscriber operations

**Clause B rationale:** A breach of Comcast's customer database (telecom subscribers) falls under the FCC rule because the breach implicates the parent's obligation to notify. A breach of Comcast's media subsidiary (e.g., NBCSports) does not, because it does not involve telecom customer data.

### Application and Verification

**Step 1: Entity Matching** (scripts 121A–121B)
- Exact string match (normalized): 107/779 matches
- Identified 672 non-matching firms with Form 499 candidates listed

**Step 2: Manual Two-Clause Classification** (script 122)
- Applied two-clause rule to 25 SIC-flagged firms (marked SIC 4812 but not matched)
- Verified major carriers:

| Firm | Breaches | Classification | Primary Source (FRN) | Rationale |
|------|----------|-----------------|---------------------|-----------|
| Comcast | 10 | Treat (1b) | Comcast Telephony Communications of Maryland (0003766052) | Parent brand; subsidiary files Form 499; breach involves subscriber operations |
| Charter | 8 | Treat (1b) | Charter Communications Operating, LLC (0002526580) | Parent brand; operating subsidiary is Form 499 filer |
| Frontier | 6 | Treat (1b) | Frontier regional subsidiaries (0001583244, 0001583228) | Multiple regional Form 499 filers; breach involves telecommunications |
| Altice USA | 3 | Treat (1b) | CSC Wireless NY, LLC (0027517648) | Parent brand; Altice Wireless files Form 499 |
| AT&T Services | 9 | Treat (1b) | AT&T Inc. and subsidiaries (parent is filer) | Parent brand; multiple AT&T subsidiaries file Form 499 |
| NBC Sports | 3 | Control | Not Form 499 filer | Media/entertainment operation; breach does not involve telecom subscriber operations |
| ATT-Breach-Notification | 4 | Control | Artificial entity | System-generated marker, not actual business entity |

**Step 3: Primary-Source Verification**
- Looked up Form 499 registry directly for all 25 SIC-flagged firms
- Confirmed major carriers via FRN (Filer Reference Number) lookup
- Documented end_reason_desc categories to handle carrier deregistrations (Nextel → Sprint, Alltel → Verizon, etc.)

### Sample Impact

| Metric | Exact Match Only | After Two-Clause | Change |
|--------|------------------|------------------|--------|
| Treated observations | 79 | 112 | +36 (+45.6%) |
| Treated firms | 23 | 35 | +12 |
| H2 regression N | 648 | 648 | — |

**Result of correction on H2 (FCC Regulation effect on CAR):**

| Specification | Coefficient | Std. Error | p-value | Interpretation |
|---------------|-------------|-----------|---------|-----------------|
| SIC-based (original) | −2.21% | 0.88% | 0.017 | Significant |
| Exact-match Form 499 | −0.69% | 0.85% | 0.405 | Null |
| Two-clause Form 499 | −0.47% | 0.76% | 0.540 | Null |

The progressive movement toward null is consistent with improved classification: the SIC-based effect was partially driven by inclusion of non-filers (false positives) in the treated group.

---

## Failure Mode 3: SIC Code as Regulatory Proxy

### Problem
The Standard Industrial Classification (SIC) system classifies firms by industry. SIC code 4812 is "Radiotelephone Communications," intended to identify wireless carriers. However:

1. **Coverage gaps:** Not all FCC-regulated carriers have SIC 4812 (e.g., some subsidiaries, international affiliates)
2. **False positives:** Some SIC 4812 firms are not FCC Form 499 filers (e.g., foreign carriers operating in the US through partnerships)
3. **Conceptual confusion:** A firm's industry classification (SIC) and its regulatory filing requirement (FCC Form 499) are independent

### Original Implementation
The original Essay 1 analysis classified treatment as:
```
treated if SIC ∈ {4812, 4813, 4899}
```

This captured firms in the telecom industry but conflated "operates in telecom" with "subject to FCC 7-Day Rule."

### Detection and Impact

**Affected hypotheses:** H1–H4 (market valuation effects)

**Original results (SIC-based treatment, n=128):**
- H1 (Timing): +0.19%, p=.788 (null)
- H2 (Regulation): −2.21%, p=.017 (**significant**)
- H3 (Prior breaches): +0.03%, p=.578 (null)
- H4 (Health): −0.99%, p=.403 (null)

**Corrected results (Form 499-based treatment, n=112):**
- H1 (Timing): +0.61%, p=.480 (null)
- H2 (Regulation): −0.47%, p=.540 (null)
- H3 (Prior breaches): +0.03%, p=.644 (null)
- H4 (Health): −0.39%, p=.809 (null)

The loss of statistical significance in H2 is consistent with removal of false positives from the treated group.

### Correction Method: Form 499 Registry

**Source:** FCC Form 499 filer database (47 CFR Part 32)
- Contains 20,669 carrier records (1989–present)
- Each record: legal_name, dba, trade_name, FRN, start_date, end_date, end_reason_desc
- Provides authoritative regulatory status at any point in time

**Classification algorithm:**
For each breach record:
1. Attempt exact-match to Form 499 registry (normalized names)
2. If match found and start_date ≤ breach_date ≤ end_date (or end_date = NULL): treat = 1
3. If no exact match but firm is parent of Form 499 filer and breach involves telecom operations: treat = 1
4. Otherwise: treat = 0

**Why this is superior:**
- Regulatory status is defined by the FCC's own registry, not a proxy
- Start/end dates provide precise coverage windows
- Verification via FRN lookup is reproducible and auditable

### Remaining Limitations

**Limitation 1: Parent-brand classification**
The two-clause rule requires judgment about whether a breach "involves telecommunications operations." For major carriers (Comcast, Charter, Frontier, etc.), this is clear. For edge cases (Twilio, which offers APIs for telecom but is not itself a carrier), the classification is defensible but imperfect.

**Limitation 2: Pre-period identification**
The Form 499 registry provides start_date for each filer, enabling a staggered-adoption design. However, this dataset's pre-period is short:
- Only 1 firm (GoDaddy) has breaches spanning pre-filer and post-filer periods
- Only 4 total breaches occur pre-2007 (vs 775 post-2007)
- Staggered adoption cannot be identified with sufficient power

**Limitation 3: Deregistration timing**
The end_reason_desc field captures why a carrier stopped filing (bankruptcy, acquisition, merger, etc.). We verified 5-of-6 known-defunct carriers (Nextel, Embarq, Alltel, MCI, Sprint) appear with end_dates, confirming retrospective coverage. However, 8.1% of end_date records carry a sentinel value (1997-01-01), likely an administrative placeholder for "unknown end date." We exclude these from analysis.

---

## Failure Mode 4: Silent Outcome-Extraction Failure (Item 5.02)

### Problem
The executive-turnover outcome for Essay 3 requires identifying 8-K filings containing Item 5.02 (departure/appointment of directors and officers) within event windows of each breach. The original extraction script parsed filing dates from a `/Archives/YYYY/MM/DD/` URL pattern that does not exist in EDGAR URLs. The date regex never matched, so no filing was ever counted — for any firm — and the script exited with success, writing an all-zero outcome file. A separate merge-key mismatch (the pipeline expected `breach_id`; the extraction was keyed on cik + breach date) caused the merge step to fail silently as well, so downstream scripts fell back to a stale outcome column measuring *any* 8-K filing, inflating base rates to 55–59%.

### Detection
The all-zero extraction was caught by base-rate inspection (0.0% executive change at every window across 779 breaches is impossible). The stale fallback was caught by the saturation signature: 90-day and 180-day base rates nearly identical (58.0% vs 59.0%).

### Correction
Rewrote the extraction against the SEC EDGAR submissions JSON API, which reports each filing's item codes as structured metadata ("5.02,9.01") — exact matching, no HTML scraping. Validated against a known-positive canary before deployment: Equifax (CIK 33185), breach 2017-09-07, shows a first Item 5.02 filing 19 days post-breach, matching the CEO's actual September 26 departure. Corrected base rates: 20.1% (30d), 44.1% (90d), 68.2% (180d) — a plausible monotonic time structure. The merge was fixed to key on (cik, breach_date) and to *replace* stale same-named columns; both the extraction and the merge now fail loudly on an all-zero input rather than exiting with success.

### Verification-audit catch: Cricket Wireless (7/28/2026)
A final membership audit — comparing the synthetic-control treated pool against the Form 499 classification — surfaced a defect the verification process itself existed to prevent: the verification document recorded Cricket Wireless as a CONFIRMED direct Form 499 filer (Cricket Communications, Inc., FRN 0004321139, "already in treated group"), while the dataset carried it as untreated. The exact matcher had missed the "LLC" name variant, and the manual-corrections rule for Cricket had been commented out. A verification document that says "treated" while the data says otherwise is worse than either error alone; the rule is now active in the corrections script and both observations are treated. The same audit caught Aero Charter, Inc. — an aviation company — inside the SIC-era treated pool via a "Charter" name-token collision (an additional Failure Mode 2 instance), and produced explicit adjudications for Boost Mobile (treated, clause b: prepaid wireless brand of Form 499 filer Sprint Spectrum LLC, FRN 0006693022) and DISH Network (untreated: satellite television is not a telecommunications service under §64.2011, and no covered carrier operation is documented at the breach dates).

### Downstream resolution: the Schoenfeld "violation" was an artifact
Under the broken event coding, the Cox proportional-hazards robustness check for H6 recorded a proportional-hazards violation (Schoenfeld p = .020 for the FCC term) — a caveat carried in Essay 3's documentation for months. With the corrected event definition (event = Item 5.02 within 180 days; duration = days to first Item 5.02 filing) and the corrected treatment variable, the violation disappears (Schoenfeld p = .479). The "violation" was measurement error, not a property of the data — a concrete example of how outcome mismeasurement propagates into specification diagnostics, not just point estimates.

---

## Failure Mode 5: Document–Result Incoherence (Hardcoded Appendix Tables)

### Problem
The Essay 1 appendix table generator (`rebuild_essay1_appendix_tables.py`, 7/24/2026) presented itself as a computation script but hardcoded five of its thirteen tables: the "causal identification" table (industry FE −1.94, falsification +0.23, covariate matching −1.64), factor-model robustness (−2.47/−2.12/−2.14/−2.22), the volume test, random-forest feature importances, and pre-announcement returns were pasted literals its code never computed. It also read the pre-correction dataset with the retired SIC-based treatment flag. Re-running it would have re-emitted superseded numbers under fresh timestamps — stale results indistinguishable from regenerated ones.

### Detection
Caught on 8/2/2026 when the appendix was regenerated for transcription: the table CSVs predated the 7/28 final-membership run, and code inspection showed `causal_results.append({... 'FCC Coefficient': -1.94 ...})`-style literals in place of estimation.

### Correction
Replaced by `scripts/141_essay1_appendix_tables_form499.py` (added to run_all.py, restoring the delete-and-rebuild guarantee for the appendix): all fourteen tables computed live from FINAL_DISSERTATION_DATASET_FORM499_CORRECTED.csv with `fcc_form499`, with thirteen canonical-value assertions (sample counts and all four H1–H4 coefficient/p pairs) that print PASS/FAIL on every run. Materially, the hardcoded SIC-era factor-model marginals (p=.06–.11) become −0.19 to −0.42 with p>.57 on corrected treatment — the near-significance was the misclassification. The general rule this failure mode adds: a document or output that cannot be regenerated by executing code against the canonical dataset is not evidence; every reported table must have a generating script inside the pipeline.

---

## Failure Mode 6: Citation-Layer Propagation (Unverified Secondary-Source Constants)

### Problem
The dissertation's rule-effectiveness anchor — "the FCC breach-notification rule became effective September 28, 2007" — appeared in essay drafts, the proposal, speaker scripts, dashboard pages, variable specifications, and a boilerplate line in 151 article-notes files. It entered from secondary sources (published papers citing the rule) and was never checked against the Federal Register. It is wrong twice over: the rule number cited alongside it ("Rule 37.3") does not exist, and the date has no primary-source referent.

### Detection
Caught 8/2/2026 when a reviewer refused to let the date anchor the Methods sample-period language "on memory." Primary-source chain: the 2007 CPNI Order was published June 8, 2007 (72 FR 31948), whose DATES section explicitly holds §§64.2010–64.2011 ineffective pending OMB approval; FCC compliance guidance (DA-08-1321) states the rules, including §64.2011, became effective December 8, 2007.

### Correction
December 8, 2007 is the sole rule-effective date; June 8, 2007 is publication only. The 151-file boilerplate was batch-corrected; remaining occurrences are inventoried in outputs/DEAD_DATE_PURGE_INVENTORY.md and die with the stale documents that carry them. Identification impact: pre-rule regression observations are 4 (calendar-2007 cutoff) or 10 (December 8 cutoff), 1 treated under either — the DD-unidentified conclusion is invariant, but every pre/post statement must name its cutoff.

### The general rule this failure mode adds
A constant that every secondary source repeats is not thereby verified — replication of a citation is not replication of a fact. This is the citation-layer analogue of the duplicate-notification problem in the PRC data (Failure Mode 1's cousin): the same unverified record, propagated many times, masquerading as corroboration. Load-bearing regulatory facts (rule numbers, effective dates, coverage scope) must be verified against the primary source before they anchor a research design.

---

## Summary: Path Independence

The three corrections documented above are path-independent in the following sense:

1. **CIK deduplication** corrects CRSP return measurement (outcome variable)—necessary regardless of treatment definition
2. **Form 499 classification** corrects regulatory status measurement (treatment variable)—necessary regardless of identification strategy
3. **Removal of SIC proxy bias** produces a cleaner estimate of the true effect of FCC regulation—improves estimation quality under any downstream analysis

Whether the dissertation pursues a **descriptive framing** (report bounded nulls, lead with measurement contribution) or a **state-law staggered-adoption design** (change the research question entirely), these data-quality corrections are foundational and do not depend on that strategic choice.

---

## Document Version
- Date: July 28, 2026
- Prepared for: Committee meeting with Dr. Johnson
- Purpose: Establish data quality baseline before design decisions
- Status: Ready to include in Essay 1 (path-independent) or Methods Appendix (either path)
