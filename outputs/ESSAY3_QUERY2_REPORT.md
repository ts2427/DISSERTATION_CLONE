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
| Essay 1: `outputs/ESSAY1_APPENDIX_TABLES_FORM499.md` (committed 2026-09-11 with a TOMBSTONE header, do not cite; its generator, scripts/141, was retired from run_all 2026-08-30 and no longer exists — the current appendix is `outputs/rebuild/appendix_v3/` from scripts/158) | **7/28 audit** (1,054 → 784 → 779 → 672 → 648) | 648 | 115 | 11 | 35 |
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
    - outputs/rebuild/appendix_v3/               (Essay 1 appendix)
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

**Stage 1 ends here.** Stage 2 starts after the sheet is coded: D3 agreement and kappa, then E–I.

---

# STAGE 2 — PART D3: VALIDATION (round 1 done; classifier revised; round 2 sheet drawn — STOP)

## Provenance of the reference codes (recorded on Tim's instruction)

**Tim did not hand-code the validation sheet.** The reference codes are **Claude's**, produced in a separate session:
- coded **blind to the classifier output**;
- coded from the sheet's Item 5.02 text only, under the sheet README rules;
- followed by a verification pass on uncertain rows using SEC filings, company releases and (sheet 57) trade press. The verification log is reproduced in `outputs/essay3_q2/VALIDATION_REFERENCE_CODES_R1_README.txt`.

Tim reviewed and adopted them as the reference standard. Earlier wording in this project that called them "your codes" or "Tim's codes" is corrected here.

The coder's interpretive rules where the README is silent (pre-announced dates; leaving a covered title; restatements tagged `restates_prior_disclosure`; EVP/SVP departures; "unclear") are in the same README file.

**Sheet 31** (T-Mobile, 2013-05-02) is scored at its **verified** CEO code (Y) as **primary** and its blind code ("unclear", dropped) as **secondary**. It is a random-draw filing, not one of the seven T-Mobile calibration filings, so it stays in the primary statistics. The seven are sheets 33, 37, 39, 51, 53, 74 and 75, per the sheet's own source column.

## Round 1 — frozen classifier v1 (scripts/188, freeze commit `d39bc6d`, blob `af2c97c`) vs reference codes

NEW, scripts/194; `d3_agreement.csv`, `d3_disagreements.csv`. Variant A = reference codes as given, with restated departures = Y (coder rule 3).

| Field | κ, all 80 | Agreement | Precision / recall | κ, excluding the 7 T-Mobile calibration filings |
|---|---|---|---|---|
| Executive departure | **.803** | .913 | .958 / .793 | **.876** |
| CEO departure (sheet 31 verified Y, primary) | .707 | .963 | .800 / .667 | .785 |
| CEO departure (sheet 31 blind, secondary) | .787 | .975 | | .882 |
| Director-only departure | .858 | .963 | 1.000 / .786 | .819 |
| Pre-announced | .698 | .888 | 1.000 / .600 | .719 |

Variant B (restated departures recoded N), all 80: executive departure κ .729, CEO κ .475, director-only κ .804, pre-announced κ .519.

Person agreement: on the 23 filings both call an executive departure, 19 share at least one departing surname.

**Round-1 disagreements (17 filings) and their causes:**

*v1 bugs:*
- the "retiring" stem was never matched (sheet 37);
- "forfeited upon his departure" from a prior employer counted as a departure (sheet 52);
- "continue in his role as CEO" was not treated as keeping the title (sheet 71);
- phrasings not recognised:
  - "no longer be an executive officer" (66);
  - "decline to stand for re-election" (62);
  - "does not wish to seek re-election" (76);
  - "will be leaving" (2);
  - "has left his position as" (32);
  - "Mr. X's employment … will … terminate" (39).

*Definitional differences:*
- restated departures (53);
- pay-agreement-only departures (39);
- vacancy mentions (14);
- pre-announced with an effective date before the reference date (7, 21, 27, 63, 71, 76).

Sheet 31's CEO call depends on outside verification, not the text.

## Revision: classifier v2 (scripts/195), committed alone as `6f7be7a` (blob `ec32364`) before the round-2 draw

**General-rule fixes** (Tim's list plus the phrasings above):
- the "retiring" stem;
- prior-employer departures ignored;
- "continue in his role as" treated as keeping the title;
- "no longer be an executive officer";
- "decline to stand / does not wish to seek re-election";
- "will be leaving";
- "has left his position";
- "<Name>'s employment … will terminate".

**One narrow implied-departure rule:** "successor to / in succession to <Name>" with a covered title. It is tagged, and **it fires on 0 of the 1,078 filings**, so it has no false positives to drop in round 2 and captures nothing.

**Rulings implemented:**

(1) **One departure per person within parent CIK, dated to its earliest disclosing filing.** Restatements create no new events; the restatement-dated, filing-level outcomes are kept as the `rs_*` sensitivity.
- Result: **768 departure mentions → 513 departure events** (300 exec, 213 director).
- **63 events merge more than one filing, folding 70 filings** into an earlier disclosure.
- 38 mentions carry no person name and cannot merge.

(2) Pay-agreement-only departures count.

(3) Vacancy mentions count for director departures only.

(4) Pre-announced uses every date in a departure sentence, including effective dates.

**Merge spot-check** (25 random multi-filing events, seed 7, in `195_classifier.log`):
- Name matching is correct in the cases checked, e.g. Legere, Carter, Collis, Stephenson, Stephens and Rencher.
- **One false merge was found and fixed before the commit:** "Duke Energy" and "Progress Energy" had been read as persons keyed "energy". Corporate words can no longer be merge keys, and 0 such keys remain.
- **T-Mobile, for the case:** under ruling (1), both Legere's CEO departure and Carter's CFO departure date to the November 2019 filing 0001193125-19-294093:
  - Legere: "will cease to serve as CEO of T-Mobile effective as of April 30, 2020";
  - Carter: the "Carter Amendment" states his "employment with T-Mobile will automatically terminate upon the expiration of the employment term".

  For the 2019-11-26 event, that filing precedes t0 on both anchors.

**In-sample check** (v2 on the round-1 80 — these filings informed the fixes, so this is NOT a validation):
- executive departure κ 1.000 (variant A) and .912 (variant B);
- CEO κ .902; director-only κ .955; pre-announced κ .902.

Remaining in-sample disagreements:
- sheet 31, the CEO call that rests on outside verification;
- sheet 53, where the classifier doesn't code Legere's board resignation as director-only because he is also coded as a restated CEO departure.

## Round 2 — fresh blind sheet (scripts/196): drawn, STOP

- **The sheet:** `outputs/essay3_q2/VALIDATION_SHEET_R2.xlsx`, 30 filings in the same format and README as round 1. Order randomised with seed 4343.
- **The draw:** seed 20260912, from a pool of 596. The pool is the B1-scope filings excluding the round-1 80, the 40 development filings and the 35 T-Mobile documents read in Query 1.
- **The v2 answers** are only in `validation_classifier_HIDDEN_R2.csv`, which includes the "new only" variants and the restated, vacancy and implied flags.

**Stop here until round 2 is coded blind.** After round 2, the plan is:
1. report both rounds;
2. run v2 on all 1,078 filings and report how many outcome flags change at 30/90/180 days, treated vs control;
3. then Parts E–I.

---

## Round 2 — classifier v2 vs round-2 reference codes (NEW, scripts/197; `197_r2.log`, `d3_r2_agreement.csv`)

**Commit order.** The history proves each step came before the next:
1. `6f7be7a`: classifier v2 alone.
2. `edbf670`: the round-2 sheet, with v2's answers in `validation_classifier_HIDDEN_R2.csv`. The answers were already committed here, so no separate commit was needed.
3. `5ec8f9e`: the round-2 reference codes, in their own commit.

**The reference codes** are Claude's, coded blind to v2's answers, from the sheet text first, under the round-1 rules plus Tim's four rulings. A verification pass on uncertain rows followed. **Tim did not hand-code.**
- **File of record:** `VALIDATION_SHEET_R2_CLAUDE_RATER.xlsx` (sha256 `96fa041e…`), copied unchanged from Downloads. It matches the pasted text with 0 cell differences.
- **Sheet 9's pre-announced code:** verified Y is primary; blind "unclear" is secondary.

**Round 2 contains 5 executive departures and 0 CEO departures** (reference codes). **CEO-departure validation therefore rests on round 1, which informed v2's fixes.**

Exact 95% CIs are Clopper–Pearson. Variant A compares the reference codes as given with v2's any-mention codes. Variant B compares restated reference departures, recoded N, with v2's new-only codes.

| Field | n | Agreement | κ | Reference positives | v2 positives | TP / FP / FN | Precision [95% CI] | Recall [95% CI] |
|---|---|---|---|---|---|---|---|---|
| Executive departure (A) | 29¹ | .931 | .713 | 5 | 3 | 3 / 0 / 2 | 1.00 [.29, 1.00] | .60 [.15, .95] |
| Executive departure (B) | 29¹ | .897 | .514 | 4 | 3 | 2 / 1 / 2 | .67 [.09, .99] | .50 [.07, .93] |
| CEO departure (A and B) | 30 | 1.000 | n/a | 0 | 0 | 0 / 0 / 0 | n/a | n/a |
| Director-only departure | 30 | 1.000 | 1.000 | 9 | 9 | 9 / 0 / 0 | 1.00 [.66, 1.00] | 1.00 [.66, 1.00] |
| Pre-announced, **primary** (sheet 9 = Y) | 30 | .867 | .718 | 12 | 8 | 8 / 0 / 4 | 1.00 [.63, 1.00] | .67 [.35, .90] |
| Pre-announced, secondary (sheet 9 = unclear) | 30 | .900 | .792 | 11 | 8 | 8 / 0 / 3 | 1.00 [.63, 1.00] | .73 [.39, .94] |

¹ Sheet 29 has reference executive = "unclear" and is dropped from that field.

**Round-2 disagreements.** Causes were diagnosed on the text; all are in `ADJUDICATION.xlsx`, tab round2_v2.
- **Sheet 16 (Sprint, Crull, Chief Strategy Officer).** Missed. The text reads "it was determined that Kevin Crull … **would be leaving** the Company effective December 31, 2018". v2 knows "will be leaving" but not "would be leaving". The reference coder also flagged his executive-officer status for adjudication.
- **Sheet 22 (Charter, Ellen, Senior EVP).** Missed. The text has no departure verb: Ellen "has agreed to remain employed by the Company as Senior Executive Vice President through November 30, 2023 and then as Executive Advisor". This is a pay-agreement role change. The reference coder counts it under ruling 2; v2's rules do not reach it.
- **Sheet 9 (Charter, Rutledge).** v2 says pre-announced "unclear", which matches the blind reference code. The verified primary code is Y.
- **Sheet 24 (AT&T, directors resigning at a transaction close).** Pre-announced: the reference says Y; v2 says N.

**Sheet 29** (Sysco, interim Chief Accounting Officer Stone, succeeded by Johnson; reference executive = "unclear") is the recall test of the implied-departure rule, which fires on 0 of the 1,078 filings. **v2's call: executive N, CEO N, director-only N, implied-succession flag 0, action "appointment".** The implied-departure rule, as specified ("successor to / in succession to <Name>"), does not capture "will succeed Mr. Stone", so the implied departure goes unrecorded.

**Both rounds together:**

| Round | Classifier | Reference codes | Executive κ | Executive recall | CEO κ | Director-only κ | Pre-announced κ |
|---|---|---|---|---|---|---|---|
| 1 (80 filings) | v1, frozen `d39bc6d` | Claude, blind, R1 | .803 (.876 without the T-Mobile 7) | .79 | .707 (primary; .787 with sheet 31 blind) | .858 | .698 |
| 1, in-sample (NOT a validation) | v2 | same | 1.000 | 1.00 | .902 | .955 | .902 |
| 2 (30 filings) | v2, `6f7be7a` | Claude, blind, R2 | .713 | .60 (3/5) | no positives | 1.000 | .718 |

## ADJUDICATION.xlsx (NEW, scripts/197)

No earlier ADJUDICATION.xlsx existed in the repository or on disk. This one was created for this step, with these tabs:
- **round1_v1:** the 17 round-1 disagreements between v1 and the reference codes;
- **round2_v2:** the 5 round-2 disputes, including sheet 29;
- **flagged_by_reference:** the 2 rows the reference coder marked "candidate for adjudication" (round 1, sheet 57 Schwartz; round 2, sheet 16 Crull).

Every row has blank adjudicated_* columns, with the classifier's and the reference coder's codes side by side.

## Outcome-flag changes, classifier v1 → v2 (all 1,078 filings; `e_flag_changes_v1_v2.csv`)

v2 was re-run on all 1,078 filings; it reproduced its committed outputs byte for byte. Below: the Query 1 Essay 3 sample (340; 106 treated events, 234 control at this level), executive departure, **notification anchor**. Each cell reads "v1 rate → v2 rate (flips 0→1 / 1→0)".

| Window | v2 primary, one departure per person: treated | v2 primary: control | v2 restatement-dated (rs): treated | rs: control |
|---|---|---|---|---|
| 30 | .047 → .038 (0 / 1) | .038 → .043 (1 / 0) | .047 → .066 (2 / 0) | .038 → .043 (1 / 0) |
| 90 | .132 → .113 (1 / 3) | .137 → .158 (5 / 0) | .132 → .142 (1 / 0) | .137 → .158 (5 / 0) |
| 180 | .349 → .321 (1 / 4) | .252 → .248 (5 / 6) | .349 → .358 (1 / 0) | .252 → .274 (5 / 0) |

**On the breach anchor**, at 180 days: primary treated .245 → .226 (1 / 3) and control .239 → .235 (6 / 7); rs treated .245 → .255 (1 / 0) and control .239 → .265 (6 / 0).

**CEO departure, notification anchor, 180 days:** primary treated .075 → .075 (2 / 2), control .094 → .094 (0 / 0); rs treated .075 → .094 (2 / 0).

**Director-only departure, notification anchor, 180 days:** primary treated .208 → .198 (0 / 1), control .162 → .180 (6 / 2).

The any-5.02 flags are identical under v1 and v2 at every window and anchor. Every row, including the 341-event scope and the 30/90-day CEO and director cells, is in `e_flag_changes_v1_v2.csv`.

## The November 2019 T-Mobile filing naming Carter (0001193125-19-294093; filed 2019-11-18; items 5.02, 7.01, 9.01)

Verbatim from the Item 5.02 section:
- "In addition, (i) on November 15, 2019, T-Mobile adopted a third amendment to the amended and restated employment agreement, dated as of December 20, 2017, with J. Braxton Carter, the Company's Executive Vice President and Chief Financial Officer (the "Carter Amendment") …"
- "The Carter Amendment amends Mr. Carter's employment agreement to (i) extend the term of Mr. Carter's employment thereunder through July 1, 2020 (the "Expiration Date") and (ii) clarify that Mr. Carter's employment with T-Mobile will automatically terminate upon the expiration of the employment term. The Carter Amendment provides that, during the remainder of his employment term, Mr. Carter shall continue to (i) serve as Executive Vice President and Chief Financial Officer of the Company, (ii) receive the same base salary as currently in effect (i.e., $950,000 per year) and (iii) be eligible to participate in employee benefit plans maintained by the Company … Except as otherwise determined by T-Mobile, Mr. Carter will not be eligible to receive STI awards or grants of LTI awards after December 31, 2019."
- The same filing: "John Legere, the current CEO, will cease to serve as CEO of T-Mobile effective as of April 30, 2020, upon the conclusion of his current employment agreement …"

Under ruling (1), both departures date to this filing, which precedes the 2019-11-26 event's breach date and its reported date (2020-03-02).

## FINAL CLASSIFIER AND STOPPING RULE (Tim, 2026-09-11)

**v2 is the final classifier:** `scripts/195_essay3_q2_classifier_v2.py`, commit `6f7be7a`, git blob `ec3236471df71279531e0593304eb7b478b210b9`. See `outputs/essay3_q2/FINAL_CLASSIFIER.txt`.

**Stopping rule: no further revisions after round 2.** Every fix made after seeing a round needs another blind round. Without a stopping point, validation never ends and the classifier ends up tuned to the reference set.

**Remaining misses are documented as recall limitations, by name:**
- round 2, sheet 16 (Sprint, Crull): "would be leaving" (a tense variant);
- round 2, sheet 22 (Charter, Ellen): a job change to "Executive Advisor" set in an employment agreement, with no departure verb;
- round 2, sheet 29 (Sysco, Stone): an interim-title implied departure.

**Direction of error.** Against the reference codes (restated departures counted, variant A), v2 made **no false-positive executive-departure calls in either round**: round 2 precision is 1.00 (3/3); round 1 is 1.00 (29/29, in-sample). Its executive-departure errors are false negatives only. Stated exactly:
- Under variant B (restatements recoded N), round-2 precision is .67. v2's new-only code counts Rutledge's departure, which the reference treats as a restatement.
- The frozen v1's round-1 precision was .958; its ServiceNow false positive was fixed in v2.

If misses fall equally on treated and control events, they shrink the estimated treated–control difference toward zero and cannot manufacture one. **That is an assumption, tested below by recall by treatment status.** Adjudication (`ADJUDICATION.xlsx`) runs in parallel and does not block estimation.

**STOP (validation).**

## Differential-recall check (NEW, scripts/198; `d3_misses_by_treatment.csv`, `d3_recall_by_treatment.csv`)

**Every classifier miss across both rounds, by treatment status.** A miss means reference = Y, classifier = N, under variant A. Treatment is that of the event the filing was drawn for.

| Round / classifier | Field | Sheet | Company | Treated |
|---|---|---|---|---|
| 1 / v1 | exec | 2 | Frontier Communications | yes |
| 1 / v1 | exec | 32 | Fidelity National Information Services | no |
| 1 / v1 | exec | 37 | T-Mobile | yes |
| 1 / v1 | exec | 39 | T-Mobile | yes |
| 1 / v1 | exec | 53 | T-Mobile | yes |
| 1 / v1 | exec | 66 | Microsoft | no |
| 1 / v1 | CEO | 31 | T-Mobile | yes |
| 1 / v1 | CEO | 53 | T-Mobile | yes |
| 1 / v1 | director-only | 14 | PACCAR | no |
| 1 / v1 | director-only | 62 | Fidelity National Information Services | no |
| 1 / v1 | director-only | 76 | Hewlett Packard Enterprise | no |
| 1 / v2, **in-sample** | CEO | 31 | T-Mobile | yes |
| 1 / v2, **in-sample** | director-only | 53 | T-Mobile | yes |
| **2 / v2** | **exec** | **16** | **Sprint** | **yes** |
| **2 / v2** | **exec** | **22** | **Charter** | **yes** |

**Executive-departure recall by group:**

| Round / classifier | Treated recall [Clopper–Pearson 95% CI] | Control recall [95% CI] |
|---|---|---|
| 1 / v1 | 8/12 = .67 [.35, .90] | 15/17 = .88 [.64, .99] |
| 1 / v2 (in-sample) | 12/12 = 1.00 [.74, 1.00] | 17/17 = 1.00 [.81, 1.00] |
| **2 / v2 (out-of-sample)** | **1/3 = .33 [.01, .91]** | **2/2 = 1.00 [.16, 1.00]** |

**The condition fired.** Every miss of the final classifier v2, in either round (two in-sample, two out-of-sample), is in a treated (carrier) filing, and v1 showed the same lean.

The counts are small and every interval overlaps. But if carrier filings word departures differently, the misses **bias the treated–control difference downward**; they do not merely shrink it toward zero. That can mask a positive effect or create a spurious negative one.

**Decision (Tim, 2026-09-11):** keep v2 frozen, so the stopping rule is intact. Measure recall by treatment status on a blind audit stratified by treatment, then estimate with a misclassification sensitivity.

## Recall audit sheet (NEW, scripts/200): drawn — STOP until coded blind

- **The sheet:** `outputs/essay3_q2/VALIDATION_SHEET_AUDIT.xlsx`, 80 filings in the same format and README as rounds 1–2. It has **no treatment column**, and the order is randomised (seed 4444).
- **The draw:** 40 treated (seed 20260913) and 40 control (seed 20260914), from the B1-scope filings not already coded or read. That pool holds 185 eligible treated and 381 control filings. The stratum is the treatment of the event the filing was drawn for.
- **v2's answers and each filing's stratum** are only in `validation_classifier_HIDDEN_AUDIT.csv`.
- The audit **measures and does not revise.** v2 stays frozen (`6f7be7a`).

---

# STAGE 2 — PART E: SAMPLE (NEW, scripts/199; `e_ledger.csv`, `e1_cik_resolution.csv`, `e_analysis_sample.csv`)

Essay 3 runs on today's CANONICAL_V3; `constants_v3.json` is untouched. The outcome comes from final classifier v2.

**Helper validation.** Script 199 rebuilds outcomes for re-pointed CIKs. As a check, it rebuilt all 26 T-Mobile events' outcomes and matched v2's committed values on every one of the 56 outcome columns. A mismatch would have stopped the run.

### E1. Outcome-data requirement and the four Query 1 structural zeros

| Event | Action | Outcome CIK | Reason |
|---|---|---|---|
| Nokia (924613), 2013-07-22, control | **EXCLUDED** | — | Foreign private issuer (20-F/6-K); files no Form 8-K, so no Item 5.02 departures can exist. |
| Walt Disney (926480), 2008-07-29, control | **FIXED** | 1001039 | CIK 926480 holds only 13 no-action letters (2001–2006); Disney's 2008 8-Ks are under CIK 1001039. 6 of its Item 5.02 filings were classified with v2. |
| Aon (1808065), 2020-12-29 and 2022-02-25, control | **FIXED** | 315293 | CIK 1808065 is used for registrations only; Aon's 8-Ks are under CIK 315293. 15 of its Item 5.02 filings were classified with v2. |

After the fixes, the requirement (at least one 8-K of any kind in `[t0 − 730d, t0 + 180d]`, t0 = reported_date) removes **1 event**: Nokia, a control.

### E2. Ledger

Record-level steps carry no treatment. Parent entities are the same as parent CIKs, since the pipeline has no separate key. "Families" is a labeled alternative that folds Sprint (101830) into T-Mobile (1283699).

| Step | N | Treated | Control | Treated parent CIKs | Treated families | Pre-rule (treated / control) |
|---|---|---|---|---|---|---|
| PRC notification records | 1,054 | — | — | — | — | — |
| Gate 1 signed parent CIK (records) | 758 | — | — | — | — | — |
| Stage 3 firm-day events | 524 | — | — | — | — | — |
| Gate 2 adjacency collapse | 491 | — | — | — | — | — |
| CANONICAL_V3 events | 489 | 118 | 371 | 14 | 13 | 0 / 7 |
| CRSP data | 356 | 111 | 245 | 13 | 12 | 0 / 6 |
| Compustat covariates = Query 2 scope | **341** | 107 | 234 | 12 | 11 | 0 / 6 |
| Outcome-data requirement | 340 | 107 | 233 | 12 | 11 | 0 / 6 |
| **Prior 12-month market-adjusted return available (≥150 daily returns) = ANALYSIS SAMPLE** | **338** | **107** | **231** | **12** | **11** | **0 / 6** |

Why the scope is 341 against Query 1's 340: Query 1 required `immediate_disclosure`, which decision L3 removed. The +1 is **Sprint Nextel, 2012-08-01**, whose `immediate_disclosure` is missing. It is a wrong-field delay record; its reported_date is 2009-03-30.

The prior-return requirement removes 2 controls, both recent IPOs: Uber (reported 2019-10-28; 117 daily returns) and Zscaler (2018-10-10; 143).

### E3. Anchor diagnostic

The share of analysis-sample events whose breach-anchored 180-day window ends before reported_date, meaning every departure in that window predates public disclosure:
- **treated: 13/107 = .121**
- **control: 28/231 = .121**

The prior 12-month market-adjusted return (reported_date anchor; 339 of the 341 scope events have one) has mean +0.030, SD 0.272, median +0.047.

**Estimation (F1 onward) waits for the recall audit, per Tim's decision.**

Committed in this step: `5ec8f9e` (round-2 reference codes).

Commits that followed:
- `6bd21a8`: scripts/197, `d3_r2_*`, `ADJUDICATION.xlsx`, `e_flag_changes_v1_v2.csv`, the stopping rule.
- `762a4b9`: Part E, the recall check, the audit sheet and its hidden answers.
- `8e18c4e`: the audit reference codes, in their own commit.

---

# STAGE 2 — RECALL AUDIT, ESTIMATION (F), T-MOBILE CASE (G6), PIPELINE (H), TESTS (I)

Order of the work:
1. The differential-recall condition fired.
2. Tim chose "Audit recall, then estimate".
3. The audit reference codes were committed alone as `8e18c4e`, after `762a4b9`.
4. Scoring and estimation followed, in the committed order: F1, F4, E (above), F2–F3, F5–F6, G6 and the timeline, H, I.

Every number below is an emitted value, quoted from the log file and line named. All computations are NEW.
- **Sample level.** The analysis sample is N = 338 events: 107 treated and 231 control, with G = 81 parent CIKs, 12 of them treated.
- **Terms.** "Organizations" means parent CIKs.
- **Classifier.** Every outcome comes from the FINAL classifier v2 (`6f7be7a`): one departure per person within a parent CIK, dated to its earliest disclosing filing.

## Recall audit (NEW, scripts/201; `201_audit.log`; tab `audit_v2` in `ADJUDICATION.xlsx`)

**Provenance.** The reference codes are Claude's, from a separate session. They were coded blind to v2's answers (hidden file committed in `762a4b9`) and to the strata, and a blind verification pass followed. **Tim did not hand-code.**

**Integrity.** File of record: `VALIDATION_SHEET_AUDIT_CLAUDE_RATER.xlsx`, sha256 `ee58191e…`. It matches the pasted text with "0 cell differences" (201_audit.log:5).

**Scoring.**
- The verified (main) columns are PRIMARY and the `blind_*` columns are SECONDARY.
- 'unclear' rows are left out of the primary statistics. Executive departure has 3 (sheets 17, 24, 55); CEO departure has 1 (sheet 75) (201_audit.log:6–7).
- A sensitivity scores 'unclear' as Y.

**By treatment stratum**: executive departure under variant A (a restatement counts as Y), and CEO departure (201_audit.log:29–44). All intervals are Clopper–Pearson.

| Field | Scoring | Stratum | n | ref Y | v2 Y | TP | FP | FN | Precision [95% CI] | Recall [95% CI] |
|---|---|---|---|---|---|---|---|---|---|---|
| Exec departure | PRIMARY | treated | 38 | 19 | 16 | 16 | 0 | 3 | 1.000 [.794, 1.000] | **.842 [.604, .966]** |
| Exec departure | PRIMARY | control | 39 | 16 | 13 | 12 | 1 | 4 | .923 [.640, .998] | **.750 [.476, .927]** |
| Exec departure | SECONDARY (blind) | treated | 38 | 19 | 16 | 16 | 0 | 3 | 1.000 | .842 [.604, .966] |
| Exec departure | SECONDARY (blind) | control | 37 | 14 | 13 | 12 | 1 | 2 | .923 | .857 [.572, .982] |
| Exec departure | unclear → Y | treated | 40 | 21 | 16 | 16 | 0 | 5 | 1.000 | .762 [.528, .918] |
| Exec departure | unclear → Y | control | 40 | 17 | 13 | 12 | 1 | 5 | .923 | .706 [.440, .897] |
| CEO departure | PRIMARY | treated | 39 | 4 | 4 | 2 | 2 | 2 | .500 [.068, .932] | .500 [.068, .932] |
| CEO departure | PRIMARY | control | 40 | 3 | 3 | 2 | 1 | 1 | .667 [.094, .992] | .667 [.094, .992] |
| CEO departure | unclear → Y | treated | 40 | 5 | 4 | 2 | 2 | 3 | .500 | .400 [.053, .853] |

Overall, PRIMARY (201_audit.log:13, 18):
- Executive departure: κ .7874, precision .9655, recall .8000 [.631, .916].
- CEO departure: κ .5298, precision and recall both .5714.

Under the committed plan, **recall does not run lower for treated events**. Treated recall .842 is at or above control .750, and the two intervals overlap almost entirely. The round-2 lean toward carriers is not confirmed.

The CEO field is weak in both strata. Segment and subsidiary CEOs cause false positives: sheets 48, 57 and 71. Titles moving to Executive Chairman cause misses: sheet 13. This is why F5 reports counts only.

**Sheet 3 (Carnival 2022-04-27, control) is a structural, exhibit-only miss** (201_audit.log:122).
- The whole Item 5.02 text (340 characters) says the transitions are "described in greater detail in the attached press release included as Exhibit 99.1."
- The departure (Donald leaving as President and CEO) appears only in the exhibit, and v2 reads only the Item 5.02 text.

**Exhibit-only candidates** are counted by a heuristic: a short Item 5.02 text that points to an exhibit or press release and has no departure language. The counts are unverified (201_audit.log:123–124):
- audit sample: treated 2/40, control 4/40 (sheets 3, 19, 30, 31, 50, 80);
- all 1,078 filings: **control 89/694 (12.8%), treated 22/384 (5.7%).**

Controls lean on exhibits more often. So if the exhibit channel is systematic, v2 under-counts control departures more than treated ones. That would push the treated–control gap upward, not toward zero.

**Sheet 75 (T-Mobile 2018-04-30, 0001104659-18-028086)** (201_audit.log:127–140).
- **v2's call:** exec departure Y, CEO departure N. Its person rows are:
  - John J. Legere (President; "Mr. Sievert will succeed Mr. Legere as President upon ratification by the T-Mobile board of directors");
  - Michael Sievert (COO). This row is a person-level false positive: the sentence describes severance terms, not a departure.
- **Reference:** exec Y, CEO 'unclear'.
- **Deduplication:** it gives the 2018-04-30 filing its **own** Legere event (the President title; exec group, is_ceo 0). That event is separate from the Legere CEO-departure event first dated **2019-11-18 (0001193125-19-294093)**, because the two are 567 days apart, beyond the 540-day merge window.
- **Neither v2 nor the deduplication treats the 2018 filing as the first disclosure of Legere's CEO departure.** That first disclosure is 2019-11-18.

## F1 — PRIMARY: executive departure, LPM, notification anchor (NEW, scripts/202; `202_estimation.log:3–8`; `f1_ladder.csv`)

**Specification.** The outcome is an executive-officer 5.02(b) departure in (t0, t0 + w], with t0 = reported_date. The regressor of interest is treatment. Controls are:
- the prior 12-month market-adjusted return;
- the F2 baseline departure rate;
- the committed covariates.

**Inference.** Clustering is by parent CIK (G = 81; 12 treated). The inference ladder is ported from Essay 2 script 165.

| Window | Coef | HC3 p | CV1 p | CV3 SE | CV3 p | CV3 95% CI | WCR p | WCR 95% CI | MDE80 | Mean T / C |
|---|---|---|---|---|---|---|---|---|---|---|
| 30d | **+0.0168** | .4703 | .3950 | 0.0329 | **.6118** | [−0.0487, +0.0823] | **.4924** | [−0.0336, +0.0621] | **0.0934** | .037 / .043 |
| 90d | **−0.0169** | .7212 | .7698 | 0.1029 | **.8701** | [−0.2217, +0.1879] | **.8154** | [−0.1517, +0.1270] | **0.2918** | .112 / .160 |
| 180d | **+0.0434** | .5158 | .6070 | 0.1144 | **.7052** | [−0.1842, +0.2711] | **.6474** | [−0.1563, +0.2352] | **0.3245** | .318 / .251 |

**Cluster diagnostics.** The Carter–Schnepel–Steigerwald G* on the treatment partial leverage is 23.6, and the cluster-size CV is 2.267.

**Wild bootstrap.** WCR is the restricted wild cluster bootstrap: Rademacher weights, B = 99,999 for p; the CI is by inversion with B = 9,999.

**Logit AMEs (corroboration):** 30d +0.0238 (p .4362); 90d −0.0225 (p .6944); 180d +0.0392 (p .6475) (202_estimation.log:8).

**Reading.** No window rejects on any rung. The 30d MDE (9.3pp) is more than twice the control mean (4.3%). At 90d and 180d the MDEs (29.2pp and 32.5pp) exceed the control means (16.0% and 25.1%). The design can rule out only very large effects.

## F4 — PRE-DISCLOSURE PLACEBO (NEW; `202_estimation.log:13`; `f4_placebo.csv`)

The placebo outcome is an executive departure in (t0 − 180d, t0], under the primary specification.
- coef **−0.0658**; HC3 p .2539;
- CV3 p **.5281**, CI [−0.2724, +0.1408];
- WCR p **.4060**, CI [−0.2188, +0.0962];
- means: treated .224, control .203.

## E — outcome-data requirement, ledger, anchor diagnostic

See Part E above (ledger N = 338). The anchor diagnostic is .121 in both groups.

## F2 — baseline executive-departure rate, [t0 − 730d, t0 − 181d], per year (NEW; `202_estimation.log:18–20`; `f2_baseline.csv`)

| Group | n | Mean/yr | SD | Median | p75 | Max | Share zero | Mean count |
|---|---|---|---|---|---|---|---|---|
| treated | 107 | 0.9861 | 0.8855 | 0.6636 | 1.3273 | 3.9818 | .2523 | 1.486 |
| control | 231 | 0.9366 | 1.0054 | 0.6636 | 1.3273 | 3.9818 | .3463 | 1.411 |

## F3 — sensitivities (NEW; `202_estimation.log:25–59`; `f3_sensitivities.csv`, `f3_sic2_cells.csv`, `f3_loco.csv`)

**27 sensitivities:** nine specifications, each at three windows. All are null. The smallest CV3 p is **.1532**, at 180d, recall-corrected with treated recall at its CI low (.604) and control recall at its CI high (.927): coef +0.2225, WCR p .1230 (202_estimation.log:53).

| Sensitivity | 30d coef (CV3 p) | 90d coef (CV3 p) | 180d coef (CV3 p) |
|---|---|---|---|
| Year FE (reported year) | +0.0219 (.5092) | −0.0002 (.9984) | +0.0636 (.4832) |
| Two-digit SIC FE | +0.0404 (.3907) | +0.0868 (.6038) | +0.1494 (.5508) |
| breach_date anchor (N = 337) | −0.0057 (.8962) | −0.0635 (.4627) | −0.0334 (.7885) |
| Excluding pre-announced departures | +0.0334 (.1990) | +0.0273 (.7575) | +0.0932 (.4110) |
| Excluding the F2 baseline control | +0.0167 (.5735) | −0.0181 (.8554) | +0.0445 (.6706) |
| Restatement-dated outcome (ruling-1 sensitivity) | +0.0491 (.4163) | +0.0155 (.8982) | +0.0161 (.9261) |
| Recall-corrected, audit point estimates (r_T .842, r_C .750) | +0.0177 (.6817) | −0.0387 (.7755) | +0.0135 (.9264) |
| Recall-corrected, r_T at CI low / r_C at CI high | +0.0366 (.3779) | +0.0457 (.7105) | +0.2225 (.1532) |
| Recall-corrected, r_T at CI high / r_C at CI low | +0.0009 (.9884) | −0.1535 (.4572) | −0.2333 (.2444) |

**SIC FE caveat.** Only two SIC2 cells hold treated events: SIC 48 (102 treated / 24 control) and SIC 73 (5 / 114) (202_estimation.log:26). Under SIC FE, treatment is identified almost entirely from SIC 48's 24 controls.

**Leave-one-parent-CIK-out** (202_estimation.log:57–59):
- 30d: range [−0.0022, +0.0388]; sign flips 1/81.
- 90d: range [−0.0492, +0.0675]; sign flips 2/81.
- 180d: range [−0.0196, +0.0942]; sign flips 1/81.
- **Dropping T-Mobile (1283699) flips the sign at 30d (−0.0022) and 180d (−0.0196), and is the largest move at 180d.** Dropping Sprint gives +0.0109, −0.0167 and +0.0386.

**Full leave-one-cluster-out range** (NEW, scripts/204; `204_se_diagnostics.log`, `f1_cv3_variance_shares.csv`, `f3_loco.csv`):

| Window | Full coef | Leave-one-out range | Sign flips | Cluster(s) whose deletion flips the sign |
|---|---|---|---|---|
| 30d | +0.0168 | [−0.0022, +0.0388] | 1/81 | T-Mobile, 1283699 (treated, 26 events): −0.0022 |
| 90d | −0.0169 | [−0.0492, +0.0675] | 2/81 | FIS, 1136893 (control, 12 events): +0.0675; AT&T, 732717 (treated, 26 events): +0.0025 |
| 180d | +0.0434 | [−0.0196, +0.0942] | 1/81 | T-Mobile, 1283699: −0.0196 |

**At 90 days, one control cluster drives the CV3 variance.** Fidelity National Information Services (FIS, CIK 1136893, 12 events) accounts for 65.6% of the CV3 jackknife variance. Deleting it moves the coefficient from −0.0169 to +0.0675.

This is most of why the CV3 SE triples between 30d and 90d (0.0329 → 0.1029), and the MDE80 with it (0.0934 → 0.2918). The outcome variance also rises, from .0398 to .1243. T-Mobile's share of the 90d CV3 variance is 10.1%, and deleting T-Mobile raises the 90d CV3 SE to 0.1189 rather than lowering it.

**Labels in `f3_sensitivities.csv`:**
- A `row_type` column marks the two corner-case recall-corrected rows at each window (treated recall at one CI end, control at the other) as **BOUNDING EXERCISES, not estimates**.
- An `hc3_status` column marks HC3 as **DISQUALIFIED** in every row. For example, the 180d treated-low/control-high bound has HC3 p .018, but its valid CV3 p is .1532.
- The six bounding rows remain in the 27-test sensitivity family used for BH, so `n_tests` (31) and the assertion baseline are unchanged.

## F5 — CEO-only departures; F6 — director-only departures (counts; NEW; `202_estimation.log:64–71`)

| Window | CEO treated | CEO control | Director-only treated | Director-only control |
|---|---|---|---|---|
| 30d | 0 | 1 | 8 | 3 |
| 90d | 4 | 7 | 18 | 15 |
| 180d | 8 | 22 | 21 | 43 |

- **F5 (secondary outcome) was not estimated:** "fewer than 10 CEO departures in at least one group; counts only". The audit's CEO precision and recall of .571 add a second reason.
- **F6 is descriptive only** (decision L1). Denominators are 107 treated and 231 control events.

## G6 — T-Mobile executive departures within 180 days of NOTIFICATION (NEW, scripts/203; `203_case.log`; `g6_case_table.csv`, `g6_restatement_dated.csv`)

**Scope.** 34 T-Mobile breach events for parent CIK 1283699. Of these, 26 are in the analysis sample and 8 are pre-rule or outside it; none of the 8 has a departure in its window. *(Corrected after commit 3b5be1e, which said 25 and 9. The count of 26 matches the T-Mobile cluster size in `f1_cluster_diagnostics.csv`.)* Departures are v2 exec departure events in (rd, rd + 180], each dated to its first disclosing filing. Flags come from that filing.

| Departure (first filing) | Title | T-Mobile events whose window contains it | Pre-announced | v2 flags | Retirement / transaction flag? |
|---|---|---|---|---|---|
| Gary A. King, 2016-02-19 (0001193125-16-470124) | EVP and CIO | 3 (2015-09-14, 2015-10-01, 2015-11-04) | N | termination, severance_release | **no** |
| David A. Miller, 2021-09-16 (0001193125-21-275230) | EVP, General Counsel and Secretary | 6 (2021-02-20 → 2021-08-26) | N | retirement | **yes** (retirement) |
| Neville Ray, 2023-02-13 (0001193125-23-035719) | President, Technology | 1 (2022-11-25) | N | retirement, health, severance_release | **yes** (retirement) |
| Peter Ewens, 2023-09-08 (0001193125-23-231377) | EVP, Corporate Strategy & Development | 3 (2023-02-01, 2023-02-24, 2023-04-28) | N | retirement, health, severance_release | **yes** (retirement) |

- **Counts:**
  - Event–departure pairs: 13; distinct departures: 4. Pairs flagged pre-announced 0, retirement 10, transaction 0. Pairs carrying any of the three: **10 of 13** (203_case.log:66).
  - **Distinct departures carrying any of the three: 3 of 4** (203_case.log:67). All three are retirement flags; none is pre-announced and none transaction.
- **The "health" flag** appears to come from benefit-continuation language ("health and dental benefit coverage"), not an illness. It is not among the three flags the query asks about.
- **Affiliation** (per `g3_director_roster`): none of the four is a Deutsche Telekom or SoftBank designee. The parsed rosters list directors only, so this column tells us nothing about officers.
- **Verbatim, from the first filings:**
  - King: "On February 16, 2016, T-Mobile US, Inc. (the "Company") and Gary A. King, Executive Vice President and Chief Information Officer, agreed that Mr. King will terminate his employment with the Company effect[ive …]". This filing has no EX-99 (203_case.log).
  - Miller: "On September 10, 2021, David A. Miller, Executive Vice President, General Counsel and Secretary of T-Mobile US, Inc. (the "Company") notified the Company that he will retire from the Company effective April 1, 2022."
  - Ray: "The Company and Mr. Ray have agreed that Mr. Ray's retirement date will be on or about October 1, 2023."

### Legere and Carter — the 2019-11-18 filing (0001193125-19-294093; items 5.02, 7.01, 9.01)

**Legere**, verbatim:
> "…announced that G. Michael Sievert, age 50, has been appointed as Chief Executive Officer ("CEO") of T-Mobile, effective as of May 1, 2020. John Legere, the current CEO, will cease to serve as CEO of T-Mobile effective as of April 30, 2020, upon the conclusion of his current employment agreement with T-Mobile. Mr. Legere will continue to serve as CEO of T-Mobile and as a member of the Board through such date, and will continue to serve as a member of the Board thereafter."

**Carter**, verbatim:
> "…on November 15, 2019, T-Mobile adopted a third amendment to the amended and restated employment agreement, dated as of December 20, 2017, with J. Braxton Carter, the Company's Executive Vice President and Chief Financial Officer (the "Carter Amendment") … The Carter Amendment amends Mr. Carter's employment agreement to (i) extend the term of Mr. Carter's employment thereunder through July 1, 2020 (the "Expiration Date") and (ii) clarify that Mr. Carter's employment with T-Mobile will automatically terminate upon the expiration of the employment term."

**v2 dates both departures to this filing, 2019-11-18.**
- Legere: exec event, is_ceo 1. Later filings 0001193125-20-093622 (2020-04-01) and 0001193125-20-119230 (2020-04-24) restate it.
- Carter: exec event. Later filing 0001140361-20-014081 (2020-06-17) restates it.
- Timing against the 2019-11-26 event (203_case.log:107–108):
  - The Sievert employment agreement (2019-11-15) is −108 days from reported_date (2020-03-02) and −11 days from breach_date.
  - The 8-K (2019-11-18) is −105 days from reported_date and −8 days from breach_date.
- **Legere and Carter are therefore NOT in G6 under the primary rules.** Both were announced before the breach occurred and before notification. They fall in the F4 placebo window, (t0 − 180d, t0], for the 2019-11-26 event and also for the 2020-04-02 and 2020-04-15 events.
- **Under the restatement-dated sensitivity** (`g6_restatement_dated.csv`; 11 additions, 203_case.log:68):
  - Legere enters at +30d (2020-04-01) for the 2019-11-26 event.
  - Carter enters at +107d (2020-06-17), and also for the April 2020 events.
- **The 2020-04-01 EX-99.1** (`d886127dex991.htm`) calls it the "long-planned Chief Executive Officer transition from John Legere to Mike Sievert", completed "ahead of schedule" with the merger's close (203_case.log:97).

### T-Mobile timeline (`tmobile_timeline.csv`; 173 dated rows, 203_case.log:113)

| Row type | Rows |
|---|---|
| Breach occurrence (PRC) | 34 |
| Public notification (PRC reported_date) | 34 |
| 10-Q charge/settlement/recovery | 25 |
| Director departure (v2, first disclosure) | 16 |
| Proxy: first committee cyber/privacy mention | 15 |
| Proxy: controlled-company status | 14 |
| Exec departure (v2, first disclosure) | 11 |
| 10-K charge/settlement/recovery | 10 |
| Proxy CD&A: pay metric adjusted for the August 2021 cyberattack | 5 |
| Incident 8-K (7.01/8.01) | 5 |
| 10-K Item 1C: named security role and oversight | 3 |
| Exec CEO departure (v2, first disclosure) | 1 |

## H — pipeline hygiene (NEW edits; `outputs/RETIREMENT_LEDGER.md`)

**Removed from `run_all.py` (commented out with reasons):**
- 91m, and its `critical_keys` entry;
- 91, 91b, 91c, 91e, 91f, 91g, 91h, 91j, 91k;
- 102;
- 91_mediation.

**Other run_all.py changes:**
- The legacy Essay 3 outputs are commented out of `verify_outputs`, and the Query 2 outputs are added.
- The docstring and banners mark 16.71pp, 14.52pp and the 7/28 H6 figures as RETIRED.
- New category "ESSAY 3 — QUERY 2 CHAIN", in order 187 → 195 → 199 → 202 → 190 → 191 → 203.
  - 202 asserts against `constants_essay3_q2.json` (202:312).
  - 199 asserts that its helper reproduces v2 (199:189).
  - 187 asserts the fixed draws (187:175).
  - 195 is frozen and not edited.

**Hardcoded values retired:**
- Script 96: `turnover_prob_increase = 0.053` is now NaN, so the turnover costs print nan.
- Script 97: Table E and Figure 3 (the hardcoded quartile values) are gated off.
- Script 161: line 68.
- The 14.52 strings in the four legacy appendix builders.

**Script 46 stays in run_all** (parking lot).

**Not run:** run_all and script 158. The edited scripts pass `py_compile`.

## I — test ledger and Benjamini–Hochberg (NEW; `202_estimation.log:76–82`; `i_tests.csv`)

The new Essay 3 code runs **31 hypothesis tests**:
- 3 primary (F1);
- 1 placebo (F4);
- 27 sensitivities (F3).

Not counted, as descriptive or corroborating: the logit AMEs, F2, F5/F6 counts, and leave-one-out.

BH adjustment is within each family, on CV3 p:

| Family | Test | CV3 p | WCR p | BH p |
|---|---|---|---|---|
| primary H6 | F1 30d | .6118 | .4924 | .8701 |
| primary H6 | F1 90d | .8701 | .8154 | .8701 |
| primary H6 | F1 180d | .7052 | .6474 | .8701 |
| placebo | F4 | .5281 | .4060 | .5281 |
| sensitivity (27) | min raw .1532 | — | — | min BH .9984 |

**No test rejects, raw or adjusted.** The Essay 3 constants are in `outputs/essay3_q2/constants_essay3_q2.json`; `constants_v3.json` is untouched.

---

## Answers

1. **At each window, is executive departure higher for treated events, under the CV3 and wild-bootstrap rungs, and what is the MDE?** No window shows it.
   - 30d: +0.0168, CV3 p .6118, WCR p .4924, MDE80 0.0934.
   - 90d: −0.0169, CV3 p .8701, WCR p .8154, MDE80 0.2918.
   - 180d: +0.0434, CV3 p .7052, WCR p .6474, MDE80 0.3245.
   - These are 338 events: 107 treated across 12 parent CIKs, 81 parent-CIK clusters in all.

2. **Does the pre-disclosure placebo show the same treated–control gap?** No. The placebo coefficient is −0.0658 (CV3 p .5281, WCR p .4060; means .224 vs .203). It is no gap and of opposite sign to the 30d and 180d estimates, so it neither supports nor undermines a disclosure effect that F1 did not find.

3. **How many T-Mobile executive departures within 180 days of notification carry a pre-announced, retirement, or transaction flag, out of how many total?**
   - **3 of 4** distinct departures (Miller, Ray, Ewens: all retirement flags, none pre-announced or transaction). **10 of 13** event–departure pairs.
   - Legere and Carter are outside the count because the 2019-11-18 filing disclosed both before the 2019-11-26 breach and its 2020-03-02 notification.
