"""
REBUILD V4 - STAGE 6: FETCH COMPLETENESS CHECK
=============================================================================
A missing Item 5.02 document is not a visible error.  It reads downstream as
"this firm had no executive departure", which is a real outcome value, so a
silent shortfall biases the dependent variable toward zero.  Nothing else in the
chain would catch it.

This script compares, for every in-scope event with a resolved outcome_cik:

    EXPECTED  the Item 5.02-tagged 8-K accessions the submissions INDEX lists
              inside that event's own [win_lo, win_hi]
    ON DISK   the documents actually present under
              Data/edgar/item5_02_text/{outcome_cik}/{accession}_*

and reports every shortfall by CIK.  It also separates the two reasons an
outcome CIK can hold zero documents:

    genuine        its index lists zero 5.02 filings in-window - the firm
                   really did not file one, and a zero outcome is correct
    fetch failure  its index lists some, but none are on disk

Offline.  Inputs (missing ABORTS):
    outputs/rebuild_v4/230_outcome_cik_gap.csv
    Data/edgar/submissions_cache_v4/ and Data/edgar/rebuild_submissions_cache/
    Data/edgar/item5_02_text/
Outputs:
    outputs/rebuild_v4/235_completeness.csv        one row per event x accession
    outputs/rebuild_v4/235_completeness_by_cik.csv one row per outcome CIK
    outputs/rebuild_v4/235_completeness.md
"""
import sys
from pathlib import Path

import pandas as pd

GAP = Path("outputs/rebuild_v4/230_outcome_cik_gap.csv")
TXT = Path("Data/edgar/item5_02_text")
OUT = Path("outputs/rebuild_v4")

L = []


def log(msg=""):
    print(msg, flush=True)
    L.append(str(msg))


def flush():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "235_completeness.md").write_text(chr(10).join(L) + chr(10), encoding="utf-8")


def abort(msg):
    log("")
    log("ABORT: " + str(msg))
    flush()
    sys.exit("ABORT: " + str(msg))


def require(p):
    if not Path(p).exists():
        abort("missing input: " + str(p) + " (no graceful fallback)")
    return Path(p)


def on_disk_accessions(cik):
    """Accessions present under item5_02_text/{cik}/, keyed by the filename prefix
    231 and 187 both write: '{accession}_{primaryDocument}'."""
    d = TXT / str(int(cik))
    if not d.exists():
        return set()
    out = set()
    for f in d.iterdir():
        if f.is_file() and "_" in f.name:
            out.add(f.name.split("_", 1)[0])
    return out


def build(gap, load_pages, item502):
    rows = []
    disk_cache, page_cache = {}, {}
    for _, r in gap.iterrows():
        if int(r.get("in_scope", 0) or 0) != 1 or pd.isna(r.get("outcome_cik")):
            continue
        cik = int(r["outcome_cik"])
        if cik not in page_cache:
            page_cache[cik] = load_pages(cik)
        if cik not in disk_cache:
            disk_cache[cik] = on_disk_accessions(cik)
        pages = page_cache[cik]
        lo, hi = pd.Timestamp(r["win_lo"]), pd.Timestamp(r["win_hi"])
        expected = item502(pages, lo, hi) if pages else []
        have = disk_cache[cik]
        for f in expected:
            rows.append(dict(outcome_cik=cik, final_cik=r["final_cik"],
                             org_name=r.get("org_name", ""),
                             breach_date=r["breach_date"],
                             treated=int(r.get("treated", 0) or 0),
                             accession=f["accession"], filing_date=f["filing_date"],
                             primary_doc=f["primary_doc"],
                             on_disk=int(f["accession"] in have),
                             win_lo=r["win_lo"], win_hi=r["win_hi"],
                             submissions_cached=int(pages is not None)))
        if not expected:
            rows.append(dict(outcome_cik=cik, final_cik=r["final_cik"],
                             org_name=r.get("org_name", ""),
                             breach_date=r["breach_date"],
                             treated=int(r.get("treated", 0) or 0),
                             accession="", filing_date="", primary_doc="",
                             on_disk=0, win_lo=r["win_lo"], win_hi=r["win_hi"],
                             submissions_cached=int(pages is not None)))
    return pd.DataFrame(rows)


def main():
    import importlib.util
    gap = pd.read_csv(require(GAP), low_memory=False)
    spec = importlib.util.spec_from_file_location(
        "m231", "scripts/231_fetch_outcome_data_v4.py")
    m231 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m231)

    log("# REBUILD V4 - Item 5.02 fetch completeness (scripts/235)")
    log("")
    df = build(gap, m231.load_pages, m231.item502_filings)
    OUT.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT / "235_completeness.csv", index=False)

    exp = df[df["accession"] != ""]
    log("## Expected vs on disk")
    log("in-scope events with a resolved outcome_cik : "
        + str(df[["final_cik", "breach_date"]].drop_duplicates().shape[0]))
    log("distinct outcome CIKs                       : "
        + str(df["outcome_cik"].nunique()))
    log("event x accession pairs expected            : " + str(len(exp)))
    log("distinct accessions expected                : "
        + str(exp[["outcome_cik", "accession"]].drop_duplicates().shape[0]))
    log("of those, on disk                           : "
        + str(exp[exp["on_disk"] == 1][["outcome_cik", "accession"]]
              .drop_duplicates().shape[0]))

    # ---- shortfall by CIK ----
    by = (exp.drop_duplicates(["outcome_cik", "accession"])
          .groupby("outcome_cik")
          .agg(expected=("accession", "size"), on_disk=("on_disk", "sum")))
    by["missing"] = by["expected"] - by["on_disk"]
    names = (exp.drop_duplicates("outcome_cik").set_index("outcome_cik")["org_name"])
    by["org_name"] = by.index.map(names)
    by["submissions_cached"] = by.index.map(
        exp.drop_duplicates("outcome_cik").set_index("outcome_cik")["submissions_cached"])
    by = by.reset_index()
    by.to_csv(OUT / "235_completeness_by_cik.csv", index=False)

    short = by[by["missing"] > 0]
    log("")
    log("## Shortfall by CIK (a shortfall is a silent 'no departure')")
    if len(short):
        log(short[["outcome_cik", "org_name", "expected", "on_disk",
                   "missing"]].sort_values("missing", ascending=False).to_string(index=False))
        miss = exp[(exp["on_disk"] == 0)].drop_duplicates(["outcome_cik", "accession"])
        log("")
        log("Missing accessions:")
        log(miss[["outcome_cik", "org_name", "accession", "filing_date",
                  "primary_doc"]].to_string(index=False))
    else:
        log("NONE - every expected Item 5.02 filing is on disk.")

    # ---- zero-document outcome CIKs ----
    zero = []
    for cik, g in df.groupby("outcome_cik"):
        have = on_disk_accessions(cik)
        if have:
            continue
        n_exp = g[g["accession"] != ""][["accession"]].drop_duplicates().shape[0]
        zero.append(dict(outcome_cik=int(cik),
                         org_name=g["org_name"].iloc[0],
                         events=g[["final_cik", "breach_date"]].drop_duplicates().shape[0],
                         treated=int(g["treated"].max()),
                         index_lists_502_in_window=n_exp,
                         submissions_cached=int(g["submissions_cached"].max()),
                         verdict=("genuine - index lists zero 5.02 in-window"
                                  if n_exp == 0 else
                                  "FETCH FAILURE - index lists "
                                  + str(n_exp) + " in-window")))
    Z = pd.DataFrame(zero)
    log("")
    log("## Outcome CIKs holding zero documents")
    if len(Z):
        log(Z.sort_values(["index_lists_502_in_window", "outcome_cik"],
                          ascending=[False, True]).to_string(index=False))
        bad = Z[Z["index_lists_502_in_window"] > 0]
        log("")
        log("fetch failures: " + str(len(bad)) + "; genuine zeros: "
            + str(len(Z) - len(bad)))
    else:
        log("NONE - every outcome CIK holds at least one document.")

    log("")
    log("written 235_completeness.csv, 235_completeness_by_cik.csv")
    flush()


if __name__ == "__main__":
    main()
