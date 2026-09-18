# REBUILD V4 — Point-in-time CRSP relink, built in parallel to v3

Branch `rebuild-v4`. Nothing is committed to `main` and nothing is merged without
Tim's explicit instruction.

## Why

The stage-5 matcher (`scripts/155_rebuild_s5_outcomes.py:124–141`) maps CIK → ticker
from *current* SEC ticker files. Firms since acquired, taken private, or reorganized
fail at `155:125` and drop out. The manual ticker dictionary (`155:58–71`) repaired 24
of 111 treated matches and 11 of 245 control matches, and `permno_match` records
neither. CRSP retention is 111/118 treated against 245/371 control. v4 replaces the
matcher with one point-in-time procedure applied identically to both groups.

## Prime directive: v3 does not change

1. **No existing file is edited, moved, renamed, or deleted.** The only exception is
   appending new rules to `.gitattributes`. This covers `CANONICAL_V3`,
   `constants_v3.json`, every Essay 1, 2, and 3 script and output, `run_all.py`, and
   script 155.
2. **New work lives only in new paths:** scripts numbered 210+, `Data/wrds_v4/`,
   `Data/processed/rebuild_v4/`, `outputs/rebuild_v4/`, `outputs/essay3_v4/`,
   `Data/edgar/ex21_cache_v4/`. To reuse existing logic, copy it into a new script.
   Never import-and-patch.
3. **Branch `rebuild-v4` only.** All commits go there. Stage files by explicit path;
   never `git add -A` or `git add outputs/`, because `.gitignore:162` un-ignores
   `outputs/essay3_q2/**` and would sweep in the untracked worksheets.
4. **Leave the uncommitted `Data/enrichment/regulatory_enforcement.csv` change
   untouched and unstaged.**
5. **Do not run `run_all.py` or script 158.**
6. **Every stage ends with the freeze check (script 210) passing.** If it fails, stop
   and report. Do not repair.
7. **Stop at every STOP.** Report and wait.

---

## Stage 0 — Safety net

- Record `git status` and HEAD.
- Create the annotated tag `v3-frozen` at HEAD and push the tag.
- Create branch `rebuild-v4` from `v3-frozen`.
- Write `scripts/210_verify_v3_frozen.py`. It writes
  `outputs/rebuild_v4/V3_FREEZE_MANIFEST.csv` with the path, size, and sha256 of every
  tracked file under `Data/`, `outputs/` (excluding `outputs/rebuild_v4/` and
  `outputs/essay3_v4/`), `scripts/`, and `docs/`, plus `run_all.py` and
  `.gitattributes`. On later runs it re-hashes and diffs against the manifest. The only
  permitted difference is appended lines in `.gitattributes`. Exit nonzero on any other
  difference.
- **LFS capacity.** A prior commit (`5f5c950`, "quota exceeded") broke LFS. Before any
  large file is added, report the total size of the LFS objects the new pulls will add,
  and ask Tim to confirm available GitHub LFS storage and bandwidth. Do not push LFS
  objects until Tim confirms.
- Append `.gitattributes` rules covering `Data/wrds_v4/**` **before** any file is added
  there. Verify with NUL-delimited `git check-attr -z` on a test path.

**STOP.** Report the tag, branch, manifest file count, and LFS estimate.

---

## Stage 1 — WRDS pull (script 211; Tim runs it locally)

Write `scripts/211_wrds_pull_v4.py` using the `wrds` Python package. Credentials come
from Tim's local WRDS config or a prompt. Never write a password to disk, a log, or the
repo.

**CIK list:** every `final_cik` in `CANONICAL_V3` (489 events), plus every nominated
parent CIK in `outputs/essay3_q2/crsp_drop_nominations.csv`.

**AMENDED 2026-09-18 — the CUSIP route.** The CCM route is unavailable on this
subscription. Run 1 failed with `InsufficientPrivilege: permission denied for schema
crsp_a_ccm`, and `scripts/216` confirmed no gvkey→permno link table is reachable
anywhere (`wrdssec` blocked too; the `wrdsapps.*link` tables are bond/short/FactSet/TAQ/
patent bridges, not CCM). The `ccmxpf_lnkhist` and `wrdssec` pulls are **dropped** and
`comp.security` added. Chain: **CIK → gvkey → CUSIP(8) → permno**.

**Pulls,** each written to `Data/wrds_v4/`:

1. `comp.company` filtered by CIK — `SELECT *`, so **`priusa` survives if present**
   (Stage 2 uses it to pick the primary US issue). CIK is zero-padded to 10 characters,
   confirmed against run 1 at 148/185 = 80%.
2. `comp.security` filtered by the gvkeys step 1 reaches: gvkey, cusip, tic, exchg, plus
   a derived `cusip8`.
3. `crsp.stocknames` filtered by the **8-character** CUSIPs step 2 reaches, matched on
   **both `ncusip` (historical) and `cusip` (header)**: permno, namedt, nameenddt,
   ncusip, cusip, ticker, comnam, shrcd, exchcd.
4. `crsp.dsf` for the permnos step 3 reaches, from 2005-01-01 to the latest available
   date: permno, date, ret, retx, prc, vol, shrout.
5. `crsp.dsi` over the same range: date, vwretd, ewretd.

**Two traps the pull must be built around:**

- **CUSIP length.** Compustat stores 9 characters including the check digit; CRSP stores
  8. Matching 9 against 8 returns nothing and looks exactly like "these securities are
  not in CRSP." Trim to `cusip[:8]`, uppercase, and log the trim with a sample.
- **One company, several securities.** A gvkey can carry several issues. Hit rates are
  measured as **distinct keys reached, never row counts**, or a one-to-many join reads
  as over 100%.

**Sentinels run the whole chain.** 1283699 T-Mobile, 732717 AT&T, 101830 Sprint must each
reach a gvkey **and** a CUSIP **and** a permno; the abort names the step that broke.
Checking only the gvkey step would let the CUSIP-length failure through silently, since
`comp.company` would still look healthy.

Write `outputs/rebuild_v4/211_pull_log.md` with the pull timestamp, the WRDS username
(not the password), row counts, the hit rate at every step, the sentinel trace, date
ranges, and the sha256 of each file.

**Record the new CRSP end date.** If it extends past 2024-12-31, events previously lost
to "past-extract" may enter; the Stage 5 ledger must show this.

**STOP.** Tim runs 211 and returns the log.

---

## Stage 2 — Point-in-time linker (script 212)

**AMENDED 2026-09-18 — the CUSIP route,** since no CCM link table is reachable.

**Rule, applied identically to treated and control:**

1. `final_cik` → gvkey via `comp.company.cik` (zero-padded 10-char).
2. gvkey → **all US common issues** — `comp.security` where `tpci='0'` and
   `excntry='USA'`. **AMENDED 2026-09-18: `priusa` is not point-in-time** and must not
   gate the search. Sprint is the proof: `priusa=10` → `85207U10` → permno 14040, which
   exists only from 2013-07-12, so every pre-2013 Sprint event would fail while
   `iid=01` → `85206110` → permno **39087** (`SPRINT NEXTEL CORP`, 2005-08-15 →
   2013-07-10) sat unexamined. Both are permnos v3 used.
3. issue → `cusip[:8]`, uppercased.
4. `cusip8` → permno in `crsp.stocknames`, in this order:
   a. **`ncusip` match** (historical CUSIP) where `namedt ≤ breach_date ≤ nameenddt`,
      across **any** US common issue of the gvkey;
   b. failing that on every US common issue, **header `cusip` match** with a names row
      valid on breach_date — and only then does the identity gate apply.
   **Tie-break**, where more than one permno is valid: (i) prefer the issue named by
   `comp.company.priusa`; (ii) prefer `shrcd` 11 over 10; (iii) prefer the later
   `namedt`. The report states which rule fired and how often. Observed: the tie arises
   on 15 events across four dual-class firms (Brown-Forman, Gray Television, Comcast,
   Google) and rule (i) resolves all of them.
5. Require `shrcd ∈ {10, 11}` on breach_date.
6. **Identity gate (added 2026-09-18, mandatory).** Date validity and `shrcd` are not
   sufficient. CRSP keeps **one permno across a reverse merger** and back-fills the
   header `cusip` with the surviving firm's identifier, changing only `comnam` and
   `ncusip`. **permno 91937** is continuous from `METROPCS COMMUNICATIONS INC`
   (2007-04-19 → 2013-04-30) into `T MOBILE U S INC`, with header cusip `87259010`
   throughout. All six T-Mobile events before 2013-04-29 match that row on the header,
   with `shrcd` 11 and valid dates, and would link to MetroPCS. So:
   - `cusip_ncusip` links are accepted on date validity and `shrcd` alone.
   - `cusip_header` links are accepted **only if** the CRSP `comnam` on the row valid
     at breach_date matches the PRC org string **or** the resolved EDGAR name.
     Otherwise the event is **excluded**, reason `"registrant at breach_date is a
     different firm (header-cusip back-fill)"`. The rule decides; there is no manual
     review queue. Every exclusion is written to
     `outputs/rebuild_v4/212_identity_review.csv` with both names, both CUSIPs and the
     names-row dates.
   - **Normalisation** (deterministic, both sides): uppercase; every character outside
     A–Z0–9 becomes a space; split on whitespace; drop legal-suffix and filler tokens
     (INC, CORP, CO, COMPANY, LLC, LP, LTD, PLC, HOLDINGS, GROUP, THE, NEW, CLASS,
     TRUST, PARTNERS, ENTERPRISES, …).
   - **Token match:** let A and B be the normalised tokens of length ≥ 4 from each
     name. If both are non-empty, match iff they intersect. If either is empty, match
     iff the full normalised token sequences are equal.
   - The T-Mobile pre-2013-04-29 regression must PASS **via this gate**, not via the
     date rule.
7. Document the tie-break rule in the script header and the report.

**Output fields:** permno, gvkey, cusip8, `link_source` ∈ {`cusip_ncusip`,
`cusip_header`, `manual_override`}, the names-row validity dates, and the comnam on
breach_date.

**Validation against v3 (new, required).** For every event v3 linked, report whether v4
reaches the same permno. List **every** disagreement with both permnos, the CRSP comnam
on breach_date for each, and the reason. This is the load-bearing check on the route
change: the CUSIP path is not the path v3 used, so agreement on the events v3 got right
is the evidence that v4 is not quietly linking to different securities. Counts by treated
and control.

**Manual overrides.** Write `outputs/rebuild_v4/link_overrides.csv` with columns: cik,
date range, permno, reason, and evidence (a citation). For each entry in the v3
`MANUAL` dict (`155:58–71`), report whether the automated path now reproduces it.
Entries it reproduces are dropped from the override file. Entries it doesn't carry
forward with evidence. The same rule governs both arms.

**Identity check (automated).** For every linked event, compare the CRSP comnam on
breach_date with the org string and the resolved EDGAR name. Write every event whose
names do not plausibly match to `outputs/rebuild_v4/212_identity_review.csv`. This
catches CIK reuse across reverse mergers.

**Regression tests, as assertions in the script:**

- The recycled-ticker cases must not link to prior holders: Facebook → Metatec,
  Motorola → Movie Star, DoorDash → Dash Industries.
- **T-Mobile USA events dated before 2013-04-29 must not link to the MetroPCS permno.**
  CIK 1283699 was MetroPCS's until then, and the old matcher dropped these six events
  correctly. CCM will link them unless the rule prevents it.
- Sprint must link to the permno(s) valid at each event date. v3 used 14040 and 39087
  via the top-up file; report agreement.
- CenturyLink and Lumen must link correctly across the rename; v3 used 60599.
- DISH treatment-date handling is unchanged: excluded before July 1, 2020, treated
  after.

**v3 → v4 comparison** for all 489 events: permno unchanged, newly linked, lost, or
changed. List every lost and changed event with its reason. Give counts by treated and
control.

**STOP.** Report the comparison, the override file, the identity-review list, and the
test results.

---

## Stage 3 — Parent mapping (script 213; Tim runs it locally)

EDGAR blocks the sandbox, so Tim runs this on his machine. The User-Agent comes from an
environment variable Tim sets with his name and email, as SEC fair-access requires.
Keep requests at or below 10 per second.

- **Input (amended 2026-09-18):** `outputs/rebuild_v4/stage3_candidates.csv`, written by
  script 212, is the worklist. Its `candidate_type` column carries three kinds:
  - `gate_exclusion` — a header-CUSIP link the Stage 2 identity gate refused because the
    CRSP `comnam` at breach_date matched neither the org string nor the EDGAR name.
    Verified the same way as any other re-parenting: an **Exhibit 21** naming the
    subsidiary.
  - `a_subsidiary` — a CIK with no Compustat gvkey that a nomination identifies as a
    subsidiary registrant. Verified by **Exhibit 21**.
  - `b_successor_cik` — a listed firm whose Compustat record now sits under a different
    CIK after a holding-company reorganization or merger. The successor is **nominated by
    name and marked `unverified`**. Verified by a **successor filing — an 8-K or a Form
    12g-3 naming the predecessor** — to the same citation standard as Exhibit 21: record
    the accession and the matching line. A name resemblance alone never classifies.
  Plus `crsp_drop_nominations.csv` and any Stage 2 "lost" event whose CIK is a subsidiary.
- **Classification rule:** name knowledge may nominate a parent; only an Exhibit 21
  match classifies. Fetch the nominated parent's 10-K Exhibit 21 filed within 18 months
  of breach_date. Classify as listed-parent only if the subsidiary appears in that
  exhibit. Record the accession and the matching line.
- Cache every fetched exhibit to `Data/edgar/ex21_cache_v4/`, named by accession.
- **A verified parent** gets its event re-parented in v4, then linked by the Stage 2
  rule.
- **An unverified row** keeps its v3 status.
- **Log:** `outputs/rebuild_v4/213_reparent_log.csv`.

Re-parented events have a new outcome CIK for Essay 3. List them for the Stage 6 filing
fetch.

**STOP.** Tim runs 213 and returns the log.

---

## Stage 4 — Known data corrections (script 214)

Each correction is written to `outputs/rebuild_v4/214_corrections.csv` with the old
value, the new value, and a verbatim source quote.

- **Sprint Nextel, CIK 101830, breach_date 2012-08-01.** The source text places the
  incident in December 2008 to January 2009. Correct breach_date from the PRC record's
  own fields. Report its effect on `prior_breaches_1yr` for every Sprint event.
- **The malformed `reported_date` "2020-03".** Use the full date if the PRC record gives
  one. Otherwise set it to missing, and let the downstream requirement exclude the event
  with a logged reason.
- **Uber, CIK 1431473 (org "Uber," breach 2014-05-13).** It has no registration filings.
  Report its EDGAR identity. If it is not Uber Technologies, mark it as a Gate 1
  misresolution in the log. **Report only; do not change Gate 1 logic.**

---

## Stage 5 — CANONICAL_V4 and the v4 ledger (script 215)

- Build `Data/processed/rebuild_v4/CANONICAL_V4.csv` from `CANONICAL_V3` plus the Stage
  2–4 changes. Write it only to the new path.
- Write `outputs/rebuild_v4/v4_ledger.csv` with the same steps as `e_ledger.csv`, adding
  columns for the v3 value and the difference at every step, by treated and control.
- **Symmetry table:** `link_source` counts by treated and control, and CRSP-step
  retention by group, v3 against v4.
- **Attribution of gains (amended).** If `crsp.dsf` extends past 2024-12-31, the ledger
  must not pool the two distinct causes of recovery. Report them as separate lines, each
  by treated and control:
  - **recovered by relinking** — the event has CRSP data in v4 that it lacked in v3
    because the point-in-time linker found a permno the v3 CIK→ticker matcher missed,
    and its window lies inside the v3 extract (on or before 2024-12-31);
  - **added by the longer extract** — the event has CRSP data in v4 only because the
    new pull reaches past 2024-12-31 (the v3 "past-extract" cases: National Presto
    2025-03-01, iHeartMedia 2025-04-30, and the five `fallback-prior` 2025 events).
  An event that needs both is counted under relinking and flagged; the ledger states the
  overlap count explicitly so the two lines never double-count.
- Run script 210. It must pass.

**STOP.** Report the ledger, the symmetry table, and every event that entered or left
relative to v3. **No essay reads v4 until Tim approves this stage.**

---

## Stage 6 — Essay 3 on v4 (after Tim approves Stage 5)

- **Copy** scripts 195–204 to 220–229, pointing their inputs at `CANONICAL_V4` and their
  outputs at `outputs/essay3_v4/`. The originals are not modified.
- Fetch Item 5.02 filing text for any new outcome CIKs, including re-parented events.
  Tim runs the fetch locally if EDGAR blocks the sandbox.
- Emit `outputs/essay3_v4/constants_essay3_v4.json`.
- Produce a side-by-side table of every constant, v3 against v4, and every verdict:
  primary, placebo, sensitivities, BH, and leave-one-out sign flips.
- **Clean-clone test** on `rebuild-v4`: fresh clone, `git lfs pull`, run 220–229, diff
  every emitted file against the committed outputs. Write the exact commands to
  `docs/claude/REPRODUCE_ESSAY3_V4.md`.
- Run script 210. It must pass.

**STOP.**

---

## Out of scope

Essays 1 and 2 keep reading v3, untouched. Moving each to v4 is a separate later query,
one essay at a time. That happens only after the pending items are done: retiring or
relabeling script 158's volatility block, the 87-file LFS rule, the DISH wording, and
the script 143 matcher review.

## Report back after each stage

Report what ran, what was written (paths and sha256), the script 210 result, and
anything that surprised you. Quote numbers only from emitted files, with the file and
line.
