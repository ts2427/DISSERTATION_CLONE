"""
REBUILD V4 - STAGE 6: OUTCOME-WINDOW CENSORING REPORT
=============================================================================
An outcome window that runs past the end of the outcome CIK's filing history is
CENSORED: the firm could not have filed an Item 5.02 in the uncovered part, so a
zero there is "we cannot see" rather than "no departure happened".  Left alone,
those events enter the regression as genuine zeros.

This script only REPORTS.  It chooses no censoring rule and drops no event -
which rule to apply is Tim's call, and the counts have to be on the table before
the choice is made, not after.

Why it matters here in particular: every v4 linkage gain fell on the control
side, so if censoring is also differential by treatment it compounds rather than
cancels.  The split is therefore reported for every window and both anchors.

    t0            reported_date ('rd' anchor) and breach_date ('bd' anchor)
    window end    t0 + 30 / 90 / 180 days
    last filing   the latest filing of ANY form by the outcome CIK, from the
                  submissions cache (not just 8-K: a firm that still files
                  10-Ks is alive and simply did not file a 5.02)
    censored      window end > last filing date
    never covered last filing <= t0, so the entire window is uncovered

Offline.  Inputs (missing ABORTS):
    Data/processed/rebuild_v4/CANONICAL_V4.csv  (through scripts/236's loader)
    Data/edgar/submissions_cache_v4/ and Data/edgar/rebuild_submissions_cache/
Outputs:
    outputs/essay3_v4/232_censoring.csv      one row per event
    outputs/essay3_v4/232_censoring.md
"""
import importlib.util
import sys
from datetime import timedelta
from pathlib import Path

import pandas as pd

OUT = Path("outputs/essay3_v4")
WINDOWS = (30, 90, 180)
ANCHORS = (("rd", "reported_date"), ("bd", "breach_date"))

L = []


def log(msg=""):
    print(msg, flush=True)
    L.append(str(msg))


def flush():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "232_censoring.md").write_text(chr(10).join(L) + chr(10), encoding="utf-8")


def abort(msg):
    log("")
    log("ABORT: " + str(msg))
    flush()
    sys.exit("ABORT: " + str(msg))


def _load(path, name):
    p = Path(path)
    if not p.exists():
        abort("missing input: " + str(p))
    spec = importlib.util.spec_from_file_location(name, str(p))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def last_filing_date(pages):
    """Latest filing of ANY form. -> Timestamp or NaT."""
    best = pd.NaT
    for pg in pages or []:
        for d in (pg.get("filingDate") or []):
            t = pd.to_datetime(d, errors="coerce")
            if pd.notna(t) and (pd.isna(best) or t > best):
                best = t
    return best


def build(ev, load_pages):
    cache = {}
    rows = []
    for _, e in ev.iterrows():
        oc = e.get("outcome_cik")
        if pd.isna(oc):
            rows.append(dict(final_cik=e["final_cik"], breach_date=e["breach_date"],
                             org_name=e.get("org_name", ""),
                             treated=int(e.get("fcc_form499", 0) or 0),
                             outcome_cik=None, last_filing="",
                             status="no_outcome_cik"))
            continue
        oc = int(oc)
        if oc not in cache:
            cache[oc] = last_filing_date(load_pages(oc))
        last = cache[oc]
        rec = dict(final_cik=e["final_cik"], breach_date=e["breach_date"],
                   org_name=e.get("org_name", ""),
                   treated=int(e.get("fcc_form499", 0) or 0),
                   outcome_cik=oc,
                   last_filing="" if pd.isna(last) else last.date().isoformat(),
                   status="ok" if pd.notna(last) else "no_submissions")
        bdt = pd.to_datetime(e["breach_date"], errors="coerce")
        rdt = pd.to_datetime(e.get("reported_date"), errors="coerce")
        for anc, col in ANCHORS:
            t0 = rdt if anc == "rd" else bdt
            if pd.isna(t0):
                t0 = bdt
            rec["t0_" + anc] = "" if pd.isna(t0) else t0.date().isoformat()
            for w in WINDOWS:
                end = t0 + timedelta(days=w) if pd.notna(t0) else pd.NaT
                cen = (pd.notna(end) and pd.notna(last) and end > last)
                rec["censored_%d_%s" % (w, anc)] = int(cen)
                rec["days_uncovered_%d_%s" % (w, anc)] = (
                    int((end - last).days) if cen else 0)
            rec["never_covered_" + anc] = int(
                pd.notna(t0) and pd.notna(last) and last <= t0)
        rows.append(rec)
    return pd.DataFrame(rows)


def main():
    V4 = _load("scripts/236_essay3_v4_loader.py", "v4loader")
    m231 = _load("scripts/231_fetch_outcome_data_v4.py", "m231_for_232")

    ev = V4.load_canonical()
    scope = ev[(ev["has_crsp_data"] == 1)
               & ev["firm_size_log"].notna()
               & ev["leverage"].notna()
               & ev["roa"].notna()].copy()

    log("# REBUILD V4 - outcome-window censoring (scripts/232)")
    log("")
    log("Reports only. No censoring rule is applied and no event is dropped.")
    log("")
    log("in-scope events: " + str(len(scope))
        + "  (treated " + str(int(scope["fcc_form499"].sum()))
        + ", control " + str(int((scope["fcc_form499"] == 0).sum())) + ")")

    df = build(scope, m231.load_pages)
    OUT.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT / "232_censoring.csv", index=False)

    ok = df[df["status"] == "ok"]
    log("events with a usable filing history: " + str(len(ok)))
    bad = df[df["status"] != "ok"]
    if len(bad):
        log("")
        log("## Events with no usable filing history")
        log(bad.groupby(["status", "treated"]).size().unstack(fill_value=0).to_string())

    for anc, _col in ANCHORS:
        log("")
        log("## Censored events - anchor '" + anc + "'")
        log("(window end is past the outcome CIK's last filing of any form)")
        rows = []
        for w in WINDOWS:
            c = ok["censored_%d_%s" % (w, anc)]
            t = ok[(c == 1) & (ok["treated"] == 1)]
            k = ok[(c == 1) & (ok["treated"] == 0)]
            rows.append(dict(window=w, censored=int(c.sum()),
                             treated=len(t), control=len(k),
                             treated_pct=(round(100 * len(t)
                                                / max(1, int((ok["treated"] == 1).sum())), 1)),
                             control_pct=(round(100 * len(k)
                                                / max(1, int((ok["treated"] == 0).sum())), 1)),
                             median_days_uncovered=(
                                 int(ok.loc[c == 1, "days_uncovered_%d_%s" % (w, anc)].median())
                                 if int(c.sum()) else 0)))
        log(pd.DataFrame(rows).to_string(index=False))
        nc = ok["never_covered_" + anc]
        log("entire window uncovered (last filing on or before t0): " + str(int(nc.sum()))
            + "  (treated " + str(int(((nc == 1) & (ok["treated"] == 1)).sum()))
            + ", control " + str(int(((nc == 1) & (ok["treated"] == 0)).sum())) + ")")

    log("")
    log("## Reading these counts")
    log("A censored event contributes a zero that may mean 'not observable'.")
    log("If the treated and control percentages differ materially at a given")
    log("window, censoring is DIFFERENTIAL and a rule that drops censored events")
    log("changes the treated/control composition. Every v4 linkage gain fell on")
    log("the control side, so the two can compound.")
    log("")
    log("written " + str(OUT / "232_censoring.csv"))
    flush()


if __name__ == "__main__":
    main()
