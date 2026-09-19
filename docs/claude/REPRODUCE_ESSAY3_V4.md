# Reproducing the v4 rebuild from a clean clone

What a fresh clone of `rebuild-v4` can regenerate, what it cannot, and how the diff is
compared. Written so that a failed clean-clone check means a real difference rather than
a timestamp.

---

## What is rerun, and what is an input

**Rerun from a clean clone:** scripts **212** (point-in-time linker), **214** (record
corrections), **215** (CANONICAL_V4 and the ledger), and the Essay 3 scripts **220–229**.
Every file these emit is regenerated and diffed against the committed copy.

**NOT rerun — committed outputs are treated as inputs:**

| script | why it is not rerun | what evidences it |
|---|---|---|
| **211** (WRDS pull) | needs a licensed WRDS session; the data cannot be redistributed or re-pulled by a reader | `outputs/rebuild_v4/211_pull_log.md`, the per-file sha256 table in it, and the committed `Data/wrds_v4/*.csv` LFS objects |
| **213** (SEC verification) | needs live SEC EDGAR access under a declared User-Agent, and re-running it would re-issue hundreds of requests for documents already held | `outputs/rebuild_v4/213_run_log.md`, `213_verification_log.csv`, and the complete fetched-document cache committed under `Data/edgar/ex21_cache_v4/` |

This is the point of committing the Exhibit 21 cache: every document 213 relied on is in
the repository, so its verdicts can be audited line by line without a single network
request, even though the script itself is not rerun.

`211`'s determinism is evidenced where it can be. `crsp_dsi` is the one pulled table that
is not filtered by CIK, so the same query must return the same bytes; the top-up run
reproduced the first pull's sha256 exactly
(`71555c4aee3db70cbfe5e38ae25ea726acffbfd904c9977677d5b4f0a3562e6e`). The other four
tables are CIK-filtered and differ by construction.

---

## Timestamps and the diff

Defined once in `scripts/218_v4_common.py`; this document and that module must agree.

**Data artifacts — `.csv`, `.json`, the ledger — carry NO run timestamp.** They are
compared byte for byte with no exemptions. `assert_no_timestamp()` enforces this at write
time, so a timestamp cannot reach a data file by accident.

**Narrative `.md` run logs may carry a run timestamp, but only in a declared header
line.** The clean-clone diff ignores exactly the lines matching
`VOLATILE_LINE_PATTERNS` and nothing else:

```
^- run \(UTC\):
^- generated \d{4}-\d{2}-\d{2}T
^- finished \(UTC\):
^- pull (started|finished) \(UTC\):
^# generated \d{4}-\d{2}-\d{2}T
```

Every pattern is anchored at the start of the line and matches a header line only. A
difference anywhere else in a narrative log is a real difference and fails the check.
Widening this list forgives more, so it warrants the same scrutiny as changing a result.

---

## Commands

```bash
git clone <repo> && cd DISSERTATION_CLONE
git checkout rebuild-v4
git lfs pull                      # Data/wrds_v4/** are LFS objects

python scripts/212_pit_linker_v4.py
python scripts/214_corrections_v4.py
python scripts/215_ledger_v4.py
# Stage 6 only, once approved:
# python scripts/220_*.py ... through 229

python scripts/217_v4_offline_tests.py   # must pass
python scripts/210_verify_v3_frozen.py   # must pass: v3 unchanged
```

Then diff each regenerated file against the committed copy, byte for byte for data
artifacts and after `strip_volatile()` for narrative logs.

---

## What a failure means

- **A data artifact differs at all** — a genuine change in inputs, code, or environment.
  Investigate before accepting; nothing in these files is allowed to vary between runs.
- **A narrative log differs outside the volatile headers** — likewise a real change.
- **`210` fails** — the v3 baseline moved. This is the prime directive; stop and find out
  why before anything else.
