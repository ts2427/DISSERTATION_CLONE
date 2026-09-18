# REBUILD V4 — Stage 1 aborted runs

A record of every `scripts/211_wrds_pull_v4.py` run that did not complete. Partial
outputs are quarantined, never deleted and never committed, so a later run cannot mistake
them for a finished pull.

---

## Run 1 — 2026-10, aborted at step 2 (no CCM subscription)

**Outcome: FAILED. No usable pull. Nothing downstream may read run 1.**

### What succeeded

| Step | Result |
|---|---|
| 1. `comp.company` (filtered by CIK) | OK — CIK literal form **zero-padded 10-char** |
| CIK hit rate | **148 / 185 = 80.0%** (above the 50% floor) |
| Sentinels | OK — T-Mobile (1283699), AT&T (732717), Sprint (101830) each returned a gvkey |

The zero-padded form was correct on the first attempt, so the padded→unpadded retry never
fired. That answers one of the two open Stage 1 questions: **Compustat stores `cik`
zero-padded to 10 characters**, and Stage 2's join must use that form.

### What failed

Step 2, `crsp.ccmxpf_lnkhist`:

```
psycopg2 InsufficientPrivilege: permission denied for schema crsp_a_ccm
```

The subscription does not reach the CRSP/Compustat Merged link tables by that path. This
is an entitlement boundary, not a query error — no retry or reformulation of the same
query will succeed.

### The defect this exposed in scripts/211

The exception propagated as an uncaught traceback. `abort()` was only reachable from
*anticipated* conditions — an empty frame, a low hit rate, a sentinel miss — so the
failure bypassed `abort()` and `flush_log()` entirely and **`211_pull_log.md` was never
written**. The only evidence of the run was a half-written data file.

Fixed in the same commit as this record: `safe_run_pull()` now wraps `run_pull()` so any
exception becomes an `abort()`, and the connection attempt is wrapped too. The log is
written on every exit path. A `scrub()` pass redacts password-shaped text from driver
messages before they reach the log, since a connection-level exception can carry the
connection string.

### Quarantined output

`Data/wrds_v4/comp_company.csv` was written before the crash and has been moved to:

| Field | Value |
|---|---|
| Path | `Data/wrds_v4/_aborted_run_1/comp_company.csv` |
| sha256 | `792b590fda8f0d5526fab5a84105a4e7c0a87b76097113e2d7e60a6fbe36776e` |
| Size | 64,702 bytes |
| Rows | 148 |
| Distinct CIK | 148 |

**Untracked and not committed**, deliberately. It is a partial artifact of a failed run
and must not enter history. Note it sits under `Data/wrds_v4/**`, which `.gitattributes`
marks `filter=lfs`, so staging it would push it to LFS — keep staging explicit-path.

It is retained rather than deleted because it is the evidence for the 80% hit rate and the
zero-padded CIK finding above. Stage 2 must not read it; a completed run will rewrite
`Data/wrds_v4/comp_company.csv` at the canonical path, and the no-clobber guard in
`write()` will refuse if a stale file is ever left there.

### What happens next

`scripts/216_wrds_access_probe.py` establishes what the subscription actually reaches
before the Stage 2 rule is chosen. Two routes are live:

- **CCM route (as originally specified)** — if any link table is reachable under some
  other schema or name, use gvkey → permno with linktype/linkprim and date validity.
- **CUSIP route (fallback)** — `comp.security.cusip` → a CRSP names file
  (`stocknames` / `msenames` / `dsenames`) with date validity.

The Stage 2 linker rule is **unchanged** pending that probe.
