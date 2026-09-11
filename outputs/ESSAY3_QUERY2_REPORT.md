# Essay 3 — Query 2 Report, STAGE 1 (outcome build, blind validation sheet, T-Mobile collection)

Produced 2026-09-11. **Stage 1 only. Stage 1 stops here: nothing is estimated on the new outcome.**

## Status

- **Commits (on Tim's instruction of 2026-09-11, before he began coding; not pushed):**
  1. **Freeze commit `d39bc6d`** (2026-09-11 13:58): `scripts/188_essay3_q2_classifier.py` alone, at git blob `af2c97c280629edc5c06dd8d4a2b7874378fb9d0`. That commit comes before any comparison with Tim's codes; see `git log -- scripts/188_essay3_q2_classifier.py`.
  2. **Query 2 files commit**, force-added where gitignored:
     - this report and `outputs/PENDING_REBASELINE.md`;
     - scripts 186, 187, 189–193;
     - `outputs/essay3_q2/`;
     - `Data/edgar/item5_02_text/` and `Data/edgar/tmobile_filings/`;
     - `docs/claude/`.
  - Before that instruction Tim had said "dont commit anything until i explicitly say, store them in this project", so these files stayed uncommitted until 2026-09-11.
- **Companions:** `docs/claude/ESSAY3_QUERY_1.md` and `docs/claude/ESSAY3_QUERY_2.md` were written from the query texts. Per Tim they sit under `docs/`, not a new root `claude/`, which keeps the root clean. **`ESSAY3_PRE_RERUN_AUDIT.md` was not supplied** and is not in the repository.
- **New scripts (all uncommitted):**

| Script | Part |
|---|---|
| 186_essay3_q2_chain_reconciliation | A |
| 187_essay3_q2_fetch_502_text | B |
| 188_essay3_q2_classifier | C, frozen |
| 189_essay3_q2_validation_sheet | D1 |
| 190_essay3_q2_tmobile_sprint_case | G1, G2, G5 |
| 191_essay3_q2_tmobile_proxy_periodic | G3, G4; written by a forked agent |
| 192_essay3_q2_ceo_exhibits | B1 exhibits |

- All outputs are in `outputs/essay3_q2/`. NEW means computed by these scripts; "not recomputed" means printed from a named file.

---

## PART A — Chain and treatment reconciliation (NEW, scripts/186; `186_chain.log`)

### A1. Which chain each essay's authoritative output uses

| Essay / artifact | Chain | Regression N | Treated events | Treated parent CIKs | Treated `org_name` strings (label only) |
|---|---|---|---|---|---|
| Essay 1: `outputs/ESSAY1_APPENDIX_TABLES_FORM499.md` (untracked; its generator, scripts/141, was retired from run_all 2026-08-30) | **7/28 audit** (1,054 → 784 → 779 → 672 → 648) | 648 | 115 | 11 | 35 |
| Essay 1: `constants_v3.json` (committed; the v3 artifact the tombstone names as authoritative) | **v3** (1,054 → 758 → 524 → 489) | 338 | 104 | 11 | 35 |
| Essay 2: `outputs/ESSAY2_SAMPLE_ATTRITION_LEDGER.md` (committed b11e884, after the DISH top-up) | v3 | 333 | 104 | 12 | 36 |
| Essay 3: `constants_v3.json` (committed, before the top-up) | v3 | 338 | 104 (`CONSTANTS_BLOCK_V3.md:144`) | not stored | not stored |
| Essay 1 regression, today's CANONICAL_V3 (NEW) | v3 | 340 | 106 | 12 | 36 |
| Essay 3 regression (Query 1 definition), today's CANONICAL_V3 (NEW) | v3 | 340 | 106 | 12 | 36 |

**"Parent entities" versus parent CIKs.** The pipeline has no parent-entity key separate from the parent CIK, so the two counts are the same (12 at the 340 level). One labeled alternative: folding Sprint (CIK 101830) into T-Mobile (1283699) as one corporate family gives 11 treated families at the 340 level.

**Which chain Essay 1's authoritative appendix uses.** The project instructions carry 1,054 → 784 → 779 → 672 → 648 with 115 treated. That is the 7/28 chain, and it lives only in the untracked `ESSAY1_APPENDIX_TABLES_FORM499.md`. The repository marks that chain retired and names the v3 constants as authoritative. First lines, verbatim (not recomputed):

- `outputs/ESSAY1_APPENDIX_TABLES_FORM499.md:1-8`:
  ```
  # ESSAY 1 APPENDIX TABLES — FORM 499 CORRECTED (regenerated from final pipeline dataset)
  Sample: 779 incidents. Treatment: fcc_form499.
  - Full sample: 127 treated of 779
  - CRSP sample: 118 treated of 672 (37 organizations, 12 parent filer CIKs)
  - Regression sample: 115 treated of 648 (35 organizations, 11 parent filer CIKs)
  ```
- `outputs/SAMPLE_ATTRITION_LEDGER.md:1-16` (tracked, 6e0fbb9):
  ```
  TOMBSTONE — RETIRED 2026-09-02. DO NOT CITE.
  ... The pre-rebuild chain it described (1,054 -> 784 -> 779 -> 672 -> 648; ...) was replaced
  on 8/17-8/30/2026 by the canonical v3 rebuild: 1,054 records -> 758 (Gate 1 entity verification) -> 524 (CIK+date
  dedup) -> 489 canonical events ...
  Current authoritative artifacts:
    - outputs/rebuild/constants_v3.json          (Essay 1: 489 / 354 / 338)
    - outputs/tables/appendix_v3/                (Essay 1 appendix)
    - outputs/ESSAY2_SAMPLE_ATTRITION_LEDGER.md  (Essay 2: 489 / 366 / 333)
  ```
- `outputs/ESSAY2_SAMPLE_ATTRITION_LEDGER.md:13-16, 22, 29`:
  ```
  | PRC universe | 1,054 | ... | Entity resolution + Gate 1 | 758 | 296 | ... | CIK+date deduplication | 524 | 234 | ... | Gate 2 adjacency verdicts | 489 | 35 |
  | Canonical events (post-Gate 2) | events | 489 | 118 | 39 | 14 | 371 | 7 | 0 | CANONICAL_V3 |
  | Malformed-record exclusion (FINAL) | events | 333 | 104 | 36 | 12 | 229 | 6 | 0 | ...
  ```
- `outputs/ESSAY2_APPENDIX_TABLES_FORM499.md:26-27`: "**3. Final N = 333** (104 treated / 36 orgs / 12 parent CIKs), vs Essay 1 v3 regression N = 338."

Both Essay 2 files named in the query are in `outputs/`, not at the root.

### A2. DISH (CIK 1001082)

The adjudication records, verbatim (not recomputed):
- **7/28 chain**, `scripts/122_manual_form499_corrections.py:81`: `(r'DISH Network', 0, 'Excluded: satellite TV not a telecom service under 64.2011; no covered operation documented at breach dates')`
- **v3 chain**, `scripts/154_rebuild_s4_treatment.py:129-130`:
  - `(r'DISH Network', 1, 'Clause (b) date-conditional (9/4): DISH is a facilities-based CMRS carrier from the 2020-07-01 Boost divestiture — DISH Wireless L.L.C. FRN 0027852722 (dba Boost Mobile) and DISH Wireless Puerto Rico L.L.C. FRN 0029666096 are open family registrations at the breach date; standard coverage rule applies', ('on_or_after', '2020-07-01'))`
  - `(r'DISH Network', 0, 'Adjudicated untreated (7/28, retained for pre-divestiture events only): ...')`

DISH's two canonical events (2023-02-22 and 2023-05-17) are both after 2020-07-01, so both are **treated in v3**.

| Essay / artifact | DISH status |
|---|---|
| 7/28 chain (Essay 1 appendix, N = 648) | untreated, by script 122 |
| Essay 1 v3 constants (338) | treated in the universe, but **absent** from the sample: no CRSP data at the time |
| Essay 2 (333, committed) | **treated, included**: 2 events |
| Essay 3 constants (338) | absent |
| Essay 1 and Essay 3 on today's CANONICAL_V3 (340) | **treated, included**: 2 events |

The project instructions' "excluded" is the 7/28 adjudication, superseded on 9/4. On today's data DISH is treated in all three v3 essays. Only the committed Essay 1 and Essay 3 constants predate its inclusion.

### A3. Effect of the DISH top-up on committed constants (NEW; no rebaselining)

Script 158 was re-run in a throwaway sandbox on today's CANONICAL_V3. **94 of the 121 committed keys change.** The committed `constants_v3.json` and `appendix_v3` were not touched. All 94 are in `a3_constants_diff.csv`; the ones bearing on the hypotheses:

| Key | Committed | Today | Change |
|---|---|---|---|
| N_regression / treated_regression / treated parent CIKs | 338 / 104 / 11 | 340 / 106 / 12 | +2 / +2 / +1 |
| treated_total / treated_crsp | 116 / 109 | 118 / 111 | +2 / +2 |
| H2_FCC coef (p; TOST p) | −0.2663 (.8404; .0833) | −0.4994 (.7326; .1371) | −0.2331 |
| H1_timing coef (p) | +0.9641 (.3298) | +1.4143 (.1712) | +0.4502 |
| H3_prior coef (p) | +0.0238 (.7092) | +0.0258 (.6916) | +0.0020 |
| H4_health coef (p) | −1.0553 (.687) | −0.9405 (.7176) | +0.1148 |
| **H5 coef (p; status)**, 158's own Essay 2 spec | +3.2897 (.063; NULL-INCONCLUSIVE) | **+3.9442 (.0292; SIGNIFICANT)** | +0.6545 |
| H6 AME 30/90/180d (pp) | 7.37 / 9.97 / 4.77 | 6.85 / 9.88 / 5.46 | −0.52 / −0.09 / +0.69 |
| H6 p 30/90/180d | .1741 / .156 / .4941 | .2028 / .1566 / .4294 | |
| first_stage_pp | 15.05 | 15.26 | +0.21 |
| volume_fcc coef (p) | 0.0779 (.1167) | 0.1064 (.0446) | |
| T6 interaction coef (p) | −3.0166 (.1516) | −1.6411 (.4754) | |
| T16 breach [−10,−1] difference p / announcement [−10,−1] difference p | .0301 / .015 | .0506 / .0401 | |

**About H5.** The H5 row is script 158's breach-anchored, annualized volatility specification. Essay 2's authoritative script-163 chain disqualifies that specification on construct validity (`ESSAY2_APPENDIX_TABLES_FORM499.md:16-21`). Essay 2's own committed artifacts were already regenerated on the topped-up file (b11e884) and do not change.

### A4. Consumers of script 46 and script 53 outputs (NEW; `a4_consumers.csv`)

- **`Data/enrichment/executive_changes*.csv`** is read by the script-46 variants (46×3, 47×2), both script-53 variants, `40_MASTER_enrichment.py`, `run_enrichments.py` and `91_essay3_governance_regressions.py`.
- **`…DEDUPLICATED_ENRICHED.csv`** is read by **47 scripts active in run_all**, including Essay 1 and Essay 2 reference scripts:
  - 70, 80, 82, 90, `h1_timing_fcc_interaction`, 00, 99_firm_FE, 60, 61, 92_heterogeneity, 93, 95;
  - robustness_1–5;
  - the factor-model, long-run CAR and SCM scripts;
  - 98 and 99_cpni, which feed 121c → 122 → `FORM499_CORRECTED.csv`, the input of the 7/28 Essay 1/2 scripts 86c and 90b.
- **Non-Essay-3 scripts that use the `executive_change` columns themselves:**
  - 00 (validation print)
  - 60 and 61 (ML features)
  - 70 (Table 1 labels)
  - 92_heterogeneity
  - 95
- **The v3 chain (150–185) reads neither file.** A4 flagged only scripts/186, because its own docstring names them.

**What this means for Part H:**
- The legacy Essay 3 estimation scripts can come out of run_all.
- **Script 53 cannot be retired**; non-Essay-3 legacy scripts depend on its output.
- Script 46 can come out of run_all without breaking anything, because script 53 reads the committed `executive_changes.csv` file, not the script. The Essay 1/2 legacy scripts above would then carry the frozen 7/28 Item 5.02 flags. Tim decides.

---

## PART B — Filing text (NEW, scripts/187 and 192)

### B1. Scope

**Scope events: 341** (107 treated events, 83 parent CIKs). This is the Query 1 Essay 3 sample (340) without the `immediate_disclosure` requirement, which decision L3 removes; the extra event lacks only that variable.

| Set | Window | Filings | Event–filing pairs |
|---|---|---|---|
| B1 as written | `[min(bd, rd) − 365d, rd + 180d]` | **738** across 79 CIKs | |
| Extension (see deviation) | pre-window to `min(bd, rd) − 730d` (F2 baseline); post-window to `max(bd, rd) + 180d` (breach anchor) | +340 | |
| **Total** | | **1,078** | 2,693 |

**Deviation, flagged.** Two gaps in B1's window required the extension:
- F2's baseline window `[t0 − 730d, t0 − 181d]` is longer than B1's 365-day pre-window.
- The breach-anchored window `(bd, bd + 180d]` runs past `rd + 180d` whenever `bd > rd` (recoded and wrong-field delays). Before the extension, one scope event's breach-anchored any-5.02 disagreed with v3; after it, zero disagree.

The validation and development draws come from the B1 set only, and the rerun asserted they reproduce exactly.

### B2. Storage and counts

- **Location:** `Data/edgar/item5_02_text/{cik}/{accession}_{primaryDocument}`, 36.9 MB. The path is **not gitignored and not LFS**; it is **uncommitted** per Tim.

| Set | Fetched | Reused | Failed |
|---|---|---|---|
| B1 set (738) | 666 | 72 (49 calibration, 23 T-Mobile) | 0 |
| Extension (340) | 335 | 5 | 0 after one retry of 0000101830-12-000091 |

All 50 calibration documents are inside the extended scope. One of them, 0000101830-12-000110, is outside the B1 set.

**EX-99 exhibits** (`b_exhibits_log.csv`) cover the 73 filings the frozen classifier codes as CEO departures, plus the two named in G6:
- EX-99 documents on disk: 37;
- filings whose index lists no EX-99: 42, including the King filing (0001193125-16-470124);
- index lookup failed: 1 (0001645590-23-000079, not T-Mobile).

The Legere-to-Sievert filing's EX-99 (`d886127dex991.htm`) is on disk.

---

## PART C — Classifier (NEW, scripts/188; deterministic rules, no ML)

### C1–C2. Rules

The parser:
- isolates the Item 5.02 section, from the header to the next item *header* (an item number followed by a capitalised caption) or SIGNATURE, so inline "described in Item 8.01" references no longer truncate it;
- strips the caption (including an "ITEM 5.01"-mislabeled variant);
- records printed sub-item labels.

The coder works sentence by sentence:
- **Departure verbs** count unless the sentence is:
  - conditional contract language (hard markers such as if/may/shall/would/good reason block it unless the sentence states an explicit effective date; soft markers such as upon/following block it unless a firm current-departure marker is present);
  - biography;
  - a reference to an earlier departure.
- **Role class** is the title nearest the verb, with "resign as/from <title>" binding first. Otherwise it is the title the text gave the person earlier ("Name, the Company's <title>"). Titles the person keeps ("while remaining CEO") are excluded.
- **Other elements recorded:** a person sub-row for each departure, appointment and election, plus the filing date (the outcome date), the notice date, the effective date, context flags, and pre-announcement relative to each event's t0.

Results on the 1,078 filings:
- The Item 5.02 section was found in 1,077.
- Sub-item labels are printed in 278 filings: (e) 109, (b) 100, (d) 76, (c) 40, (a) 11.
- 1,537 person sub-rows:

| Role class | Departure | Appointment | Election |
|---|---|---|---|
| CEO | 105 | 67 | — |
| CFO | 97 | 88 | — |
| COO | 18 | 45 | — |
| PAO | 36 | 61 | — |
| president | 47 | 40 | — |
| other exec | 161 | 92 | — |
| director | 255 | — | 425 |

Filing-level codes:

| Filings | Exec departure | CEO departure | Director departure | Appointment | Election |
|---|---|---|---|---|---|
| All 1,078 | 294 | 74 | 173 | 230 | 298 |
| B1 set, 738 | 206 | 52 | 122 | 160 | 195 |

Flags among the 294 exec-departure filings:

| Flag | Filings |
|---|---|
| retirement | 126 |
| severance/release | 35 |
| termination | 34 |
| health | 18 |
| "no disagreement" | 17 |
| transaction | 13 |
| "previously announced" phrase | 33 |

### C3–C4. Outcomes and crosswalk (`c_outcomes_events.csv`, `c_crosswalk.csv`; rates, not estimates)

Query 1 Essay 3 sample, N = 340 (106 treated events at this level). Treated / control shares:

| Anchor | Window | v3 any-5.02 | any_502 | exec_departure | ceo_departure | director_departure | any-5.02 events that are not exec departures |
|---|---|---|---|---|---|---|---|
| reported_date (primary) | 30 | .236 / .141 | .255 / .120 | .047 / .039 | .009 / .004 | .104 / .009 | 41 of 55 |
| | 90 | .547 / .380 | .547 / .397 | .132 / .137 | .047 / .030 | .179 / .056 | 105 of 151 |
| | 180 | .764 / .671 | .764 / .641 | .349 / .252 | .075 / .094 | .208 / .162 | 135 of 231 |
| breach_date | 30 | .236 / .141 | .236 / .141 | .057 / .068 | .000 / .026 | .066 / .017 | 36 of 58 |
| | 90 | .547 / .380 | .547 / .380 | .132 / .128 | .019 / .034 | .189 / .081 | 103 of 147 |
| | 180 | .764 / .671 | .764 / .671 | .245 / .239 | .047 / .077 | .236 / .167 | 156 of 238 |

**Reproduction check:** on the breach anchor, `any_502` equals v3's stored `executive_change_{w}d` for every event, with **0 mismatches** at all windows. That holds on the 340-event sample and on the 341-event scope.

Supporting variables, reported_date anchor, 341-event scope:
- **F2 baseline count**, `[t0 − 730d, t0 − 181d]`: mean 1.34, median 1, max 5.
- **Placebo exec departure**, `(t0 − 180d, t0]`: 24 % of events.
- **Days to first exec departure:** median 95.5 days, over 96 events.

### C5. Freeze

`outputs/essay3_q2/CLASSIFIER_FREEZE.txt`:
- **sha256** `ee0cc05dc1826c4b5e394ca5562374d5c7053e1644127aa7696f07590003fedc`
- **git blob hash** `af2c97c280629edc5c06dd8d4a2b7874378fb9d0`
- **Frozen** 2026-09-11 13:26.
- **Not committed** (Tim). The blob hash is the id the file will carry when committed. The final run printed the same sha256.

**How the classifier was developed:**
- **Development sets:** a random draw of 40 (seed 1117) plus the 28 non-calibration T-Mobile documents read in Query 1. Only these were printed during development.
- **Firewall:** the validation 30 (seed 20260911) were fixed before any development, and their codes, like the calibration 50's, were never printed.
- **Rounds:** four, logged in `188_dev_round{1..4}.txt`. The rule changes corrected:
  - elections missed because of middle initials;
  - "named executive officers" read as an appointment;
  - a mislabeled "Item 5.01" caption;
  - retirement-plan and contract language counted as departures;
  - references to earlier departures ("previously held by", "vacancy resulting from") counted again;
  - titles the person keeps;
  - dated retirement letters.
- **Known remaining behaviour, observed on development filings only:**
  - Stepping down from one title while staying an executive (e.g., a General Counsel who remains SVP) codes as an exec departure.
  - Election filings that restate a prior director departure ("As previously disclosed, X … resign") code a director departure, with the pre-announced phrase flag.
  - Person names in *election* rows are sometimes company names; departures are unaffected.

---

## PART G — T-Mobile data collection (G1–G5; print, do not interpret)

### G1. T-Mobile's weight in the treated set (NEW, scripts/190; `g1_weights.csv`)

| Level | Treated events | T-Mobile (CIK 1283699) | Share | Sprint (CIK 101830) | T-Mobile + Sprint | Share |
|---|---|---|---|---|---|---|
| 489-event universe | 118 | 34 | .288 | 12 | 46 | .390 |
| CRSP | 111 | 28 | .252 | 12 | 40 | .360 |
| Query 2 scope (341) | 107 | 26 | .243 | 12 | 38 | .355 |
| Query 1 Essay 3 regression (340) | 106 | 26 | .245 | 11 | 37 | .349 |

26 of 106 is confirmed at the Query 1 level; the Stage 2 sample is confirmed in Stage 2. The two post-merger Sprint-named events (2020-04-02, 2020-04-15) sit on CIK 1283699 and are counted under T-Mobile.

### G2. How each T-Mobile breach reached the public (NEW; `g2_disclosure_channel.csv`, `g2_8k_passages.csv`)

- **PRC source type**, from `stage2_signed` `incident_details` and rule-classified: state AG for 20 events, other for 14.
- **Incident 8-Ks.** For each event, the 8-Ks in `[rd − 30d, rd + 30d]` that list 7.01, 8.01 or 1.05 were fetched with their EX-99s. Only 5 events have one that describes a security incident:

| Event (breach / reported) | PRC source | Earliest incident 8-K | Days, 8-K − reported_date |
|---|---|---|---|
| 2021-03-01 / 2021-08-16 | state AG | 0001193125-21-248002 (7.01) | 0 |
| 2021-08-13 / 2021-08-16 | state AG | 0001193125-21-248002 | 0 |
| 2021-08-17 / 2021-08-19 | state AG | 0001193125-21-248002 | −3 |
| 2021-08-26 / 2021-08-26 | other | 0001193125-21-248002 | −10 |
| 2022-11-25 / 2023-01-19 | state AG | 0001193125-23-010949 (8.01) | 0 |

**Incident passages, verbatim:**
- **2021-08-16 (248002):** "We have determined that unauthorized access to some T-Mobile data occurred, however we have not yet determined that there is any personal customer data involved."
- **2021-08-18 (249635, EX-99.1):** "Late last week we were informed of claims made in an online forum that a bad actor had compromised T-Mobile systems."
- **2021-08-20 (251974):** "We previously reported information from approximately 7.8 million current T-Mobile postpaid customer accounts that included first and last names, date of birth, SSN, and driver's license/ID information was compromised."
- **2021-08-27 (258261):** "On August 17 th we confirmed that T-Mobile's systems were subject to a criminal cyberattack that compromised data of millions of our customers, former customers, and prospective customers."
- **2023-01-19 (010949):** "On January 5, 2023, T-Mobile US, Inc. … identified that a bad actor was obtaining data through a single Application Programming Interface ("API") without authorization."

The other 29 events have **no incident 8-K** within ±30 days; the six MetroPCS-era events sit on MetroPCS's filings.

**Methodological note.** A first keyword list matched "compromise on quality", "attacked this pain point" and "breaches of certain representations". It was replaced before any result was used, and the earliest-8-K ordering was fixed in the same way.

### G3. Who controls the board (NEW, scripts/191; forked agent; `g3_*.csv`)

**Scope.** 14 DEF 14A filings, 2013–2026, all fetched. Raw 201.2 MB, stored gzip in `Data/edgar/tmobile_filings/` (11.8 MB, uncommitted). The DEFA14A, DEFR14A, DEFC14A and DEFM14A filings are listed but not parsed.

**Controlled company.** Every proxy states it. Deutsche Telekom's stated position, verbatim percentages:

| Proxy | Deutsche Telekom | SoftBank |
|---|---|---|
| 2013 | ~74 % (fully diluted) | |
| 2014 | 66.7 % | |
| 2015 | 65.95 % | |
| 2016–2017 | 65 % | |
| 2018 | 63 % | |
| 2019 | 63.0 % | |
| 2020 | 43.6 % held | 24.7 % held; the SoftBank proxy agreement directs its vote |
| 2021 | 43.2 % held, 52.1 % voting control | 8.5 % held |
| 2022 | 46.6 % held, 51.9 % voting control | 4.9 % held |
| 2023 | 54.0 % voting control | |
| 2024 | 57.9 % voting control | |
| 2025 | 58.9 % voting control | |
| 2026 | 54.5 % voting control | |

**Director roster.** Only the 2021 and 2022 proxies print a nominee table with independence and designation.
- 2022 (parsed reliably): 13 nominees, 5 independent, 9 designated by Deutsche Telekom, 3 by the Nominating and Governance Committee, plus Sievert (N/A).
- 2021: 14 rows, flagged unreliable (the table has one more row than there are biography blocks).
- Other years: `g3_director_roster.csv` holds the verbatim independence and designation sentences, with nothing inferred.

**Committees.** First proxy in which each cyber or privacy term appears:
- **2018:** a *management* "Enterprise Risk and Compliance Committee and an Information Security and Privacy Council".
- **2021:** the Audit Committee receives Chief Audit Executive risk assessments "including risks relating to cybersecurity and privacy".
- **2022:** the Nominating and Corporate Governance Committee is named for cybersecurity, privacy and information security.
- **2026:** renamed the "Nominating, Corporate Governance and Compliance Committee", with "The Chief Information Officer, Chief Security Officer and Chief Privacy Officer provide periodic reports…".

**CD&A.**
- 85 sentences match the terms. 19 also mention pay, but most of those are generic market-*data* language.
- **Statements that an incident affected pay**, verbatim from the full proxy text:
  - **2023 proxy:** "Actual performance of Free Cash Flow excludes the impacts of the cyberattack that the Company publicly disclosed in August 2021 … Actual performance of Free Cash Flow under our 2022 STIP equals Free Cash Flow for the full year 2022 of $7,656 million as reported in our Annual Report on Form 10-K, plus the impact of the August 2021 cyberattack of $40 million."
  - **2024 proxy:** "…Adjusted Free Cash Flow for the full year 2023 of $13,586 million … (a) minus $290 million, reflecting the net impact of settlement payment timing relating to the cyberattack that the Company publicly disclosed in August 2021…"
  - **2026 proxy:** "…further adjusted to reflect (a) the difference between the assumed incremental payments for the cyberattack in August 2021 under the 2025 Plan and the actual result…"

### G4. What T-Mobile told investors (NEW, scripts/191; `g4_*.csv`)

**Scope.** 14 10-K and 41 10-Q filings from 2013 onward, all fetched. They contain 392 unique incident sentences, 335 of them cyber-related.

**Charges, settlements, reserves and committed spending** tied to the August 2021 cyberattack, verbatim amounts:
- **$400 million:** "In connection with the proposed class action settlement and the separate settlements, we recorded a total pre-tax charge of approximately $ 400 million in the second quarter of 2022." It is first stated in the 10-Q of 2022-07-29 and again at 2023-07-27.
- **$150 million:** "committed aggregate incremental spend of $150 million for data security and related technology in 2022 and 2023 under the proposed settlement agreement". It appears in the 10-Qs of 2022-07-29 and 2022-10-27 and the 10-K of 2023-02-14.
- **Insurance reimbursements:** $50 million (2022), $100 million (FY2022), $50 million (2023) and $105 million (FY2024).
- **Legal-related expenses, net of tax:** $300 million (Q2 2022), $286 million (9M 2022) and $293 million (FY2022).
- **Legal-related recoveries, net:** $32 million (2023).

**Item 1C** (10-Ks filed from 2024):
- **2024-02-02 and 2025-01-31:**
  - "our Chief Security Officer ("CSO") presents on our cybersecurity practices to the Nominating and Corporate Governance Committee … and to our full Board of Directors on a periodic basis"
  - "As the Company's CSO, Jeff Simon has extensive experience in risk management and information security, including serving as the Chief Information Security Officer at Fidelity National Information Services, Inc."
  - "Our CSO and Chief Compliance Officer, among other executives, provide periodic reports to the NCG Committee"
  - "The NCG Committee oversees risks associated with data privacy and information security, which encompasses cybersecurity."
- **2026-02-11:**
  - "Mark Clancy, our Senior Vice President, Cybersecurity , under the direction of the Chief Information Officer, is responsible for overseeing the cybersecurity organization"
  - "As the Company's Chief Information Officer, Jeff Simon has extensive experience…"
  - "The NCGC Committee oversees risks associated with data privacy and information security"

The full sentence lists are in `g4_item1c.csv` and the forked agent's summary.

### G5. Sprint's Item 5.02 record (NEW, scripts/190; `g5_sprint_502.csv`)

The table covers Sprint (CIK 101830) events in the scope, with filings in `(breach_date, breach_date + 180d]` as in Query 1 E2. **Rows for filings on the blind validation sheet are masked until Tim has coded it.**

| Event (breach / reported) | 5.02 filings in 180d (days from breach): classifier code |
|---|---|
| 2009-02-01 / 2009-06-12 | 2009-03-03 (+30): exec departure, Christopher J. Gregoire (PAO); 2009-03-27 (+54): other |
| 2012-08-01 / 2009-03-30 | 2012-08-08 (+7): other; 2012-10-04 (+64): other; 2012-11-20 (+111): **[masked]** |
| 2015-08-17 / 2020-04-09 | 2015-10-15 (+59): **[masked]**; 2015-11-12 (+87): compensation only |
| 2017-05-01, 2017-05-07 / 2017-09-20 | none |
| 2018-03-02 / 2018-03-30 | 2018-05-02 (+61): appointment; 2018-05-30 (+89): director departure, Stephen R. Kappes ("Security Director" board role); 2018-07-02 (+122): **[masked]** |
| 2019-03-14, 2019-05-09 | 2019-05-22: appointment |
| 2019-06-02, 2019-06-08, 2019-06-22, 2019-08-13 | none |

Two Sprint events carry reported dates that precede their breach dates by years: the 2012-08-01 event (reported 2009-03-30) and the 2015-08-17 event (reported 2020-04-09, i.e. after its breach date). These are source dates, printed as they stand.

---

## PART D — Blind validation sheet (D1 confirmed; STOP)

**The sheet** is `outputs/essay3_q2/VALIDATION_SHEET.xlsx`:
- **80 rows:** the 50 calibration documents plus the 30-filing validation draw (seed 20260911). The row order is randomised (seed 4242).
- **Columns:** sheet_id, company, filing_date, URL, the reference date for "pre-announced" (the event's reported_date) and the event breach_date. Then the Item 5.02 text with the caption stripped: none truncated, none empty.
- **Blank columns for Tim:** EXEC officer departure (Y/N), CEO departure (Y/N), DIRECTOR-ONLY departure (Y/N), person and role, pre-announced (Y/N/unclear), notes. All blank cells were verified empty.
- **A README tab** states the coding rules.

**The classifier's answers** are **only** in `outputs/essay3_q2/validation_classifier_HIDDEN.csv`, keyed by sheet_id. Neither this report nor any log printed them.

**Contamination to disclose.** 7 of the 50 calibration documents are T-Mobile filings whose hand codes were published in the Query 1 report (E2). Their text was also read before the freeze, in Query 1. D3 should report agreement both with and without those 7.

**Stage 1 ends here.** Stage 2 starts only after Tim codes the sheet: D3 agreement and kappa, then E–I.
