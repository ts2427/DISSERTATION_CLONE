"""
REBUILD V4 - STAGE 6: OUT-OF-SAMPLE VALIDATION DRAW (offline)
=============================================================================
    python scripts/237_validation_draw_v4.py

THE POOL IS DEFINED BY WHAT v4 ADDED, NEVER BY FETCH HISTORY
------------------------------------------------------------
This draw used to live inside scripts/231 --documents, where the pool was "the
documents THIS run fetched".  That is wrong twice over: a resumed or re-run
fetch changes the pool, and a fetch that finds everything already on disk
produces an empty one.  The second re-run drew from 5 documents because only 5
were outstanding, though v4 had added ~450.

The pool is therefore defined against the frozen v3 tree:

    pool = { files under Data/edgar/item5_02_text/ }
           MINUS { the same paths in git ls-tree -r v3-frozen }
           INTERSECTED WITH { documents named in b_scope_filings.csv }

Nothing in that depends on when, or in how many batches, the documents arrived.
The v3-frozen difference says which documents are v4's; b_scope_filings says
which are in scope for the analysis.

SEED
----
Fixed at 20260919, the same value the superseded draws used, and fixed here
before any classification of these documents is run or inspected.  Size is
min(30, pool).  This script never classifies and never reads classifier output.

Offline.  Inputs (missing ABORTS):
    git ls-tree -r v3-frozen           (the frozen v3 document set)
    Data/edgar/item5_02_text/
    outputs/essay3_v4/b_scope_filings.csv
Outputs:
    outputs/rebuild_v4/237_validation_new_ids.csv
    outputs/rebuild_v4/237_validation_draw.md
"""
import random
import subprocess
import sys
from pathlib import Path

import pandas as pd

SEED = 20260919
MAX_DRAW = 30
FROZEN_REF = "v3-frozen"
TXT = Path("Data/edgar/item5_02_text")
SCOPE = Path("outputs/essay3_v4/b_scope_filings.csv")
OUT = Path("outputs/rebuild_v4")

L = []


def log(msg=""):
    print(msg, flush=True)
    L.append(str(msg))


def flush():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "237_validation_draw.md").write_text(chr(10).join(L) + chr(10),
                                                encoding="utf-8")


def abort(msg):
    log("")
    log("ABORT: " + str(msg))
    flush()
    sys.exit("ABORT: " + str(msg))


def norm(p):
    """Repo-relative POSIX path, so git output and local paths compare."""
    return str(p).replace("\\", "/").lstrip("./")


def frozen_paths(ref=FROZEN_REF, prefix="Data/edgar/item5_02_text/"):
    r = subprocess.run(["git", "ls-tree", "-r", "--name-only", ref],
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace")
    if r.returncode != 0:
        abort("cannot read " + ref + " - " + (r.stderr or "").strip())
    out = {ln.strip() for ln in (r.stdout or "").splitlines()
           if ln.strip().startswith(prefix)}
    if not out:
        abort(ref + " lists no files under " + prefix
              + " - refusing to treat every document as v4's")
    return out


def on_disk_paths(root=TXT):
    if not Path(root).exists():
        abort("missing input: " + str(root))
    return {norm(p) for p in Path(root).rglob("*") if p.is_file()}


def scope_paths(path=SCOPE):
    if not Path(path).exists():
        abort("missing input: " + str(path) + " - run scripts/235 first")
    df = pd.read_csv(path, low_memory=False)
    if "local_file" not in df.columns:
        abort(str(path) + " has no local_file column")
    return df, {norm(x) for x in df["local_file"].dropna()}


def build_pool(disk, frozen, scope):
    """Pure. -> sorted list of repo-relative paths v4 added AND that are in scope."""
    return sorted((disk - frozen) & scope)


def draw(pool, seed=SEED, cap=MAX_DRAW):
    k = min(cap, len(pool))
    if k == 0:
        return []
    return sorted(random.Random(seed).sample(sorted(pool), k))


def main():
    log("# REBUILD V4 - out-of-sample validation draw (scripts/237)")
    log("")
    frozen = frozen_paths()
    disk = on_disk_paths()
    df, scope = scope_paths()

    added = disk - frozen
    pool = build_pool(disk, frozen, scope)
    log("documents under item5_02_text        : " + str(len(disk)))
    log("of those, frozen in " + FROZEN_REF + " (v3's)   : " + str(len(disk & frozen)))
    log("added by v4                          : " + str(len(added)))
    log("documents named in b_scope_filings   : " + str(len(scope)))
    log("POOL (v4-added AND in scope)         : " + str(len(pool)))
    out_of_scope = len(added) - len(pool)
    if out_of_scope:
        log("  (" + str(out_of_scope) + " v4-added document(s) are not in scope "
            "and are excluded from the pool)")
    missing = scope - disk
    if missing:
        abort(str(len(missing)) + " scope document(s) are not on disk; the pool would "
              "be short. Re-run scripts/231 --documents, then scripts/235. "
              "First: " + sorted(missing)[0])

    chosen = draw(pool)
    log("")
    log("seed                                 : " + str(SEED) + " (fixed in this file)")
    log("drawn                                : " + str(len(chosen))
        + " = min(" + str(MAX_DRAW) + ", pool)")

    key = df.copy()
    key["_p"] = [norm(x) for x in key["local_file"]]
    key = key.drop_duplicates("_p").set_index("_p")
    rows = []
    for p in chosen:
        r = key.loc[p] if p in key.index else None
        rows.append(dict(local_file=p,
                         cik=(None if r is None else r.get("cik")),
                         accession=(None if r is None else r.get("accession")),
                         filing_date=(None if r is None else r.get("filing_date")),
                         primary_doc=(None if r is None else r.get("primary_doc"))))
    OUT.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(OUT / "237_validation_new_ids.csv", index=False)
    log("")
    log("written " + str(OUT / "237_validation_new_ids.csv"))
    log("")
    log("This draw is blind: no classification of these documents has been run or")
    log("inspected. The v3-era draws and the v2 classifier stay frozen, and no")
    log("result may retune them.")
    flush()


if __name__ == "__main__":
    main()
