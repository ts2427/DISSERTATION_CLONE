# FCC Treatment Classification — Premise Verification (STEP 0)

**Date:** July 28, 2026  
**Data file:** FINAL_DISSERTATION_DATASET_DEDUPLICATED_ENRICHED.csv (N=779, n=653 regression sample)  
**Current classification:** SIC codes [4813, 4841, 4899]

---

## STEP 0a: SIC Code Definitions (Authoritative Source)

**Finding:** SIC definitions from U.S. Census Bureau and OSHA records confirm the structure but reveal a classification error.

| SIC Code | Title | Scope |
|----------|-------|-------|
| **4812** | Radiotelephone Communications | Cellular, wireless, paging services |
| **4813** | Telephone Communications (except radiotelephone) | Wireline local and long-distance carriers |
| **4841** | Cable and Other Pay Television Services | Cable TV systems — **NOT telecommunications carriers** |
| **4899** | Communications Services, NEC | Satellite, specialized carriers, other comms |

**Status of working hypothesis:**
- ✓ 4812 = Radiotelephone (wireless) — **CONFIRMED**
- ✓ 4813 = Wireline telephone — **CONFIRMED**  
- ✗ 4841 = Cable TV — **NOT a telecommunications carrier per SIC definition**

---

## STEP 0b: SIC Code Frequency in Dataset

**Finding:** Current classification includes SIC 4841, which the FCC rule does not cover. Dataset contains zero 4812 observations (wireless carriers).

### Full 48xx Breakdown (N=188, 24.1% of 779 observations)

| SIC | Description | Observations | Distinct Firms |
|-----|-------------|--------------|-----------------|
| 4813 | Wireline telephone | 106 | 5 |
| 4841 | Cable TV | 33 | 6 |
| 4832 | Radio broadcasting | 20 | 3 |
| 4833 | Television broadcasting | 29 | 9 |

### Current Classification Status

| SIC | Included in fcc_reportable | Data Present | Observations |
|-----|---------------------------|--------------|--------------|
| 4813 | **Yes** ✓ | Yes | 106 |
| 4841 | **Yes** ✗ | Yes (33) | 33 |
| 4899 | **Yes** | No | 0 |
| 4812 | No | No (0 observations) | — |

**Critical findings:**
- **SIC 4812 (Wireless/CMRS):** Zero observations. No wireless carriers with this SIC in the dataset.
- **SIC 4841 (Cable TV):** Present with 33 observations (6 firms) but should NOT be classified as FCC-covered.
- **SIC 4899:** Included in classification but zero observations in data.

**Implication:** The current treatment variable may include non-covered entities (4841) and miss any wireless carriers miscoded under different SICs.

---

## STEP 0c: Rule Scope at Breach Date (rule effective December 8, 2007)

**Finding:** Current classification does not align with 47 CFR § 64.2011 as written and in force in 2007.

### Entities Covered by FCC Rule in 2007

1. **Wireline local exchange carriers (LECs)** — SIC 4813
2. **Wireless/cellular carriers (CMRS)** — SIC 4812
3. **Interexchange carriers (IXCs)** — SIC 4813
4. **Other common carriers** — SIC 4899 (satellite, specialized carriers)

### Entities NOT Covered in 2007

- **Cable television systems** (SIC 4841) — even if providing VoIP, **NOT covered** under original 2007 rule
- **Broadcast stations** (SIC 4832, 4833) — NOT covered
- **Information services** — NOT covered

### 2024 Amendments

The FCC amended 47 CFR § 64.2011 in 2024 to broaden scope to "communications services" beyond traditional common carriers. This expansion post-dates the dataset (all breaches pre-2024) and should NOT be applied retroactively.

**Conclusion:** Cable TV systems (SIC 4841) were not covered by the FCC rule when the breaches in this dataset occurred.

---

## STEP 0 VERDICT: PREMISE FAILURE

### Critical Findings

| Claim | Status | Evidence |
|-------|--------|----------|
| **0a: 4812 is wireless** | ✓ CONFIRMED | SIC definition verified |
| **0b: 4812 in data** | ✗ **FALSE** | 0/779 observations; all wireless coded differently |
| **0b: 4841 should be included** | ✗ **FALSE** | 33 obs present but rule does not cover cable TV |
| **0c: Current classification matches 2007 rule** | ✗ **FALSE** | Includes 4841 (not covered); may exclude 4812 carriers miscoded |

### Impact Assessment

The current classification **contradicts the 47 CFR § 64.2011 scope as of September 2007:**

1. **SIC 4841 (Cable TV):** Included but NOT covered by the rule. This introduces **33 false-positive treated observations** (6 firms).
2. **SIC 4812 (Wireless/CMRS):** Should be covered but not present in dataset with that code. Wireless carriers likely coded under 4813 or other codes (parent/subsidiary issue).
3. **SIC 4899:** Included but not present in data (0 observations).

### Recommendation

**STOP. Do not proceed to STEP 1 until resolving:**

1. **Parent/subsidiary audit (STEP 2a):** Identify whether wireless carriers in the dataset are held as subsidiaries under different parent SIC codes.
2. **Business description verification:** Flag firms with telecommunications business descriptions who fall outside the 48xx range.
3. **SIC 4841 handling:** Decide whether to (a) exclude cable TV firms as non-covered entities, or (b) flag for manual review if they provided telecommunications common carrier services.

The reclassification task as framed assumes the current [4813, 4841, 4899] specification is close to correct. The premise verification shows it contradicts the statutory rule scope.

---

**Next action:** Pause here and consult before proceeding to STEP 1. The classification requires more investigation than SIC-code logic alone.
