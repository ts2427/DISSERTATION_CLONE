# Reproducing Essay 2 — and the one declared exception

Everything in the Essay 2 chain reruns offline from committed bytes, with **one
exception**, declared here in the same form as the WRDS and SEC stages in
`REPRODUCE_ESSAY3_V4.md`.

## Declared exceptions

| Stage | Needs | Committed output it leaves behind |
|---|---|---|
| `121a` Form 499 entity matching (**staged with `--assemble-only`**) | the FCC Form 499 endpoint for a live refresh; **nothing** to run offline | `outputs/form499_matched_records.csv`, `outputs/form499_unmatched_with_candidates.csv`, from the committed snapshot |
| `167` Essay 2 microstructure pull (**not staged**) | WRDS subscription (CRSP-licensed quote data) | the quote extract itself is gitignored; its derived table `outputs/tables/essay2_v2/t35_microstructure.csv` **is** committed |
| `170` Essay 2 scope and bounds (**staged; fails loudly**) | the quote extract `167` pulls | `outputs/tables/essay2_v2/t43_intent_scope.csv` and `t44_equivalence_bounds.csv` |
| `173`, `179` one-time licensed WRDS pulls | WRDS subscription | `Data/wrds/q6_*.csv`, `Data/wrds/crsp_daily_topup_dish.csv` — committed; **do not re-run** |

Everything else reruns offline from those bytes.

## `scripts/121a_form499_entity_matching.py` — the Form 499 registry

**The live fetch.** Without `--assemble-only`, `121a` queries
`https://apps.fcc.gov/cgb/form499/499results.cfm?xml=TRUE` with a declared academic
User-Agent. From a clean clone that returns **HTTP 403**, which is why this was the one
undeclared network dependency in the Essay 2 chain and why the clean-clone run of
2026-10-01 failed on it.

**The snapshot, and how it was obtained.** `Data/edgar/form499_registry.xml`, 63.8 MB,
Git-LFS tracked, committed **2026-08-04** in `77b362d` ("Canonical V3: rebuild chain,
vintage snapshots, and portability closure"). It is the response body of exactly that
query, and it carries the FCC's own stamp in its root element:

```xml
<Filer499QueryResults ... Updated="2026-07-21" RecordCount="20669" >
```

So the registry vintage is **2026-07-21** — the FCC's last update before the snapshot was
taken — and it contains **20,669 `<Filer>` records**. Treatment is assigned from this
snapshot, not from a live query, which is what makes the Form 499 membership stable across
reruns.

**Offline mode.** `python scripts/121a_form499_entity_matching.py --assemble-only` parses
the snapshot instead of querying, and prints the stamp it read so the vintage is in the log.
`run_all.py` stages the step with that flag. **Verified: the assembled outputs are
byte-identical to the committed `outputs/form499_matched_records.csv` and
`outputs/form499_unmatched_with_candidates.csv`.**

Without the flag the step still attempts the live fetch, and on a non-200 it now names the
flag and the snapshot path in the error rather than failing silently.

## `scripts/170_essay2_scope_and_bounds.py` — the exception in full

**What it needs.** `scripts/170:79` reads
`Data/wrds/crsp_quotes_topup.csv`:

```python
qd = pd.read_csv('Data/wrds/crsp_quotes_topup.csv', low_memory=False)
```

That file is a **CRSP-licensed intraday quote extract** pulled by `scripts/167`. It is
gitignored and is not in the repository, so a clean clone does not have it.

**Why it cannot run without a WRDS login.** CRSP's licence does not permit redistributing
the quote data, so the file cannot be committed the way
`Data/wrds/crsp_daily_returns.csv` is. `scripts/167`, which would pull it, is deliberately
**not staged in `run_all.py`** for the same reason. `170` **is** staged, and it **fails
loudly** rather than degrading: it raises on the missing file instead of substituting a
proxy or silently skipping the microstructure channel.

**What it computes.** Two things, which is why it is staged despite the dependency:

1. **The intent-scope restriction (H1).** 47 C.F.R. § 64.2011(e) reaches only intentional
   access until the indefinitely delayed 2024 amendment. PRC breach vectors are mapped to
   intent — HACK, INSD and CARD in scope; DISC out; PHYS, PORT and STAT ambiguous and
   reported both ways. Treated events failing the scope test are **dropped, not recoded to
   control**, because they are covered-entity events outside the rule's event-level scope.
   A stated limitation sits in the script's own docstring: the canonical data carry only
   the legacy vector codes, so within PHYS/PORT/STAT theft cannot be separated from loss.
2. **Part A, the equivalence bounds.**

**Where its committed output lives.** `170` writes two tables, both committed:
`outputs/tables/essay2_v2/t43_intent_scope.csv` (`170:198`) and
`t44_equivalence_bounds.csv` (`170:268`).

The microstructure table `t35_microstructure.csv` is written by **`167`, not `170`** — 12
columns, 11 of which match the tombstoned `channel_microstructure.csv`, which makes it the
live counterpart for that appendix table. `167` is the unstaged pull; its derived table is
committed even though the quote extract it came from cannot be.

**What to do on a clean clone.** Skip `170` as declared. Nothing downstream of it feeds
`constants_v3.json`, the Essay 1 ledger, or the Essay 3 v4 chain; its outputs are cited by
the Essay 2 appendix only. Any other failing step is a real failure and must not be
skipped.

## The appendix situation, in one line

The Essay 2 appendix Tim cites (`outputs/ESSAY2_APPENDIX.md`, 28 tables) draws on
`outputs/tables/essay2_appendix/` — 41 CSVs with **no committed generator**, tombstoned
2026-09-29 (`outputs/tables/essay2_appendix/TOMBSTONE.md`). The live chain writes 61 files
to `outputs/tables/essay2_v2/` instead, and the two sets share no filenames. See
`outputs/ALIGNMENT_REPORT.md` Part B for the table-by-table mapping.
