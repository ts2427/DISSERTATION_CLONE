"""
REBUILD V4 - STAGE 6: OUTCOME-CIK GAP LIST
=============================================================================
Lists the v4 outcome CIKs whose Item 5.02 filing text v3 never fetched, so the
231 fetch knows exactly what to add.  Offline; reads the on-disk v3 cache.

    python scripts/230_outcome_gap_v4.py

SCOPE, reproduced from scripts/187
----------------------------------
An event is in outcome scope when it is LINKED and its size, leverage and roa
are all present.  Two substitutions against v3:

  has_crsp_data == 1   ->  v4_linked == 1 from outputs/rebuild_v4/v4_212_links.csv.
                           CANONICAL_V4's own has_crsp_data / permno columns are
                           INHERITED FROM v3 and are NOT v4's link result - reading
                           them here would silently score the v3 sample.
  size/leverage/roa    ->  the REFRESHED values from scripts/219, not the
                           v3-inherited columns.  219 must run first.

FETCH WINDOW, reproduced from scripts/187 (win_lo_ext / win_hi_ext)
-------------------------------------------------------------------
    lo = min(breach_date, reported_date_eff) - 730 days
    hi = max(breach_date, reported_date_eff) + 180 days
    reported_date_eff = reported_date, falling back to breach_date when missing

730 days because the F2 baseline departure rate needs [t0-730d, t0-181d]; the
post-window runs off the LATER anchor because breach_date can exceed
reported_date under v3's recoded / wrong-field delays.  This covers the longest
lookback of every filing-based variable (baseline rate, placebo window, the
30/90/180d outcome windows).  The outcome-data requirement itself is computed
from submissions METADATA, not fetched text, so it needs no document.

OUTCOME CIK
-----------
The outcome CIK is v4's final_cik (post re-parenting).  Where scripts/233 marks
the event contested between v3's RESOLVE dict and v4's re-parenting, the row
carries resolve_contested = 1 and BOTH candidate CIKs; 231 fetches for both so
no ruling is foreclosed by what has been downloaded.

FAILS LOUDLY
------------
Any missing input ABORTS - no graceful fallback.

OUTPUTS
-------
    outputs/rebuild_v4/230_outcome_cik_gap.csv    one row per scope event
    outputs/rebuild_v4/230_outcome_gap.md
"""
import sys
from datetime import timedelta
from pathlib import Path

import pandas as pd

CANON = Path("Data/processed/rebuild_v4/CANONICAL_V4.csv")
LINKS = Path("outputs/rebuild_v4/v4_212_links.csv")
COVAR = Path("outputs/rebuild_v4/219_covariates_v4.csv")
RECON = Path("outputs/rebuild_v4/resolve_reconciliation.csv")
TXT = Path("Data/edgar/item5_02_text")
OUT = Path("outputs/rebuild_v4")

SCOPE_COVARS = ["firm_size_log", "leverage", "roa"]   # scripts/187, verbatim
PRE_DAYS = 730
POST_DAYS = 180

L = []


def log(msg=""):
    print(msg)
    L.append(str(msg))


def abort(msg):
    log("")
    log("ABORT: " + str(msg))
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "230_outcome_gap.md").write_text(chr(10).join(L) + chr(10), encoding="utf-8")
    sys.exit("ABORT: " + str(msg))


def require(path):
    if not path.exists():
        abort("missing input: " + str(path) + " (no graceful fallback)")
    return path


def cached_ciks(root):
    """CIK directories already holding fetched Item 5.02 documents."""
    if not root.exists():
        return {}
    out = {}
    for d in root.iterdir():
        if d.is_dir() and d.name.isdigit():
            out[int(d.name)] = len([f for f in d.iterdir() if f.is_file()])
    return out


def build_gap(canon, links, cov, recon, cache):
    canon = canon.copy()
    canon["breach_date"] = canon["breach_date"].astype(str).str[:10]
    key = ["final_cik", "breach_date"]

    lk = links.copy()
    lk["breach_date"] = lk["breach_date"].astype(str).str[:10]
    if "v4_linked" not in lk.columns:
        abort(str(LINKS) + " has no v4_linked column")
    linked = (lk.drop_duplicates(key).set_index(key)["v4_linked"]
              .apply(lambda v: int(v) if pd.notna(v) else 0))

    cv = cov.copy()
    cv["breach_date"] = cv["breach_date"].astype(str).str[:10]
    cv = cv.drop_duplicates(key).set_index(key)

    contested = {}
    if recon is not None and len(recon):
        rc = recon[recon["verdict"] == "disagree"]
        for _, r in rc.iterrows():
            if pd.isna(r.get("breach_date")) or str(r.get("breach_date")) == "":
                continue
            contested[(r["v4_final_cik"], str(r["breach_date"])[:10])] = r.get(
                "resolve_target_cik", "")

    rows = []
    for _, e in canon.iterrows():
        k = (e["final_cik"], e["breach_date"])
        bdt = pd.to_datetime(e["breach_date"])
        rdt = pd.to_datetime(e.get("reported_date"), errors="coerce")
        rdt_eff = bdt if pd.isna(rdt) else rdt
        lo = min(bdt, rdt_eff) - timedelta(days=PRE_DAYS)
        hi = max(bdt, rdt_eff) + timedelta(days=POST_DAYS)

        is_linked = int(linked.get(k, 0) or 0)
        crow = cv.loc[k] if k in cv.index else None
        have_cov = bool(crow is not None
                        and all(pd.notna(crow.get(c)) for c in SCOPE_COVARS))
        in_scope = int(is_linked == 1 and have_cov)

        oc = int(e["final_cik"])
        alt = contested.get(k, "")
        n_cached = cache.get(oc, 0)
        rows.append(dict(
            final_cik=e["final_cik"], breach_date=e["breach_date"],
            org_name=e.get("org_name", ""),
            treated=int(e.get("fcc_form499", 0) or 0),
            outcome_cik=oc,
            resolve_contested=int(alt != "" and pd.notna(alt)),
            resolve_alt_cik=alt,
            v4_linked=is_linked, covariates_present=int(have_cov), in_scope=in_scope,
            cached=int(n_cached > 0), n_cached_docs=n_cached,
            needs_fetch=int(in_scope == 1 and n_cached == 0),
            rd_missing=int(pd.isna(rdt)),
            win_lo=lo.date().isoformat(), win_hi=hi.date().isoformat()))
    return pd.DataFrame(rows)


def main():
    canon = pd.read_csv(require(CANON), low_memory=False)
    links = pd.read_csv(require(LINKS), low_memory=False)
    cov = pd.read_csv(require(COVAR), low_memory=False)
    recon = pd.read_csv(RECON, low_memory=False) if RECON.exists() else None
    if recon is None:
        log("NOTE: " + str(RECON) + " absent - contested outcome CIKs not flagged. "
            "Run scripts/233 first if that matters.")

    cache = cached_ciks(TXT)
    log("# REBUILD V4 - outcome-CIK gap (scripts/230)")
    log("")
    log("Item 5.02 cache on disk: " + str(len(cache)) + " CIK directories, "
        + str(sum(cache.values())) + " documents")

    gap = build_gap(canon, links, cov, recon, cache)
    OUT.mkdir(parents=True, exist_ok=True)
    gap.to_csv(OUT / "230_outcome_cik_gap.csv", index=False)

    sc = gap[gap["in_scope"] == 1]
    log("")
    log("## Scope")
    log("events in CANONICAL_V4        : " + str(len(gap)))
    log("linked in v4                  : " + str(int((gap["v4_linked"] == 1).sum())))
    log("in outcome scope (linked+cov) : " + str(len(sc))
        + "  (treated " + str(int(sc["treated"].sum()))
        + ", control " + str(int((sc["treated"] == 0).sum())) + ")")
    log("")
    log("## Item 5.02 coverage, scope events, by treated/control")
    tab = (sc.groupby(["treated", "cached"]).size().unstack(fill_value=0)
           .rename(columns={0: "not_cached", 1: "cached"}))
    log(tab.to_string())

    need = sc[sc["needs_fetch"] == 1]
    newc = sorted(set(need["outcome_cik"]))
    log("")
    log("## Outcome CIKs needing a fetch")
    log("scope events with no cached documents: " + str(len(need))
        + "  (treated " + str(int(need["treated"].sum()))
        + ", control " + str(int((need["treated"] == 0).sum())) + ")")
    log("distinct outcome CIKs to fetch       : " + str(len(newc)))
    if len(need):
        log("")
        cols = ["outcome_cik", "org_name", "breach_date", "treated",
                "resolve_contested", "win_lo", "win_hi"]
        log(need[cols].sort_values(["outcome_cik", "breach_date"]).to_string(index=False))

    cont = gap[gap["resolve_contested"] == 1]
    if len(cont):
        log("")
        log("## Contested outcome CIKs (scripts/233 disagreements)")
        log(cont[["final_cik", "resolve_alt_cik", "org_name", "breach_date",
                  "in_scope", "cached"]].to_string(index=False))
        log("231 fetches BOTH candidates so no ruling is foreclosed.")

    log("")
    log("written " + str(OUT / "230_outcome_cik_gap.csv"))
    (OUT / "230_outcome_gap.md").write_text(chr(10).join(L) + chr(10), encoding="utf-8")


if __name__ == "__main__":
    main()
