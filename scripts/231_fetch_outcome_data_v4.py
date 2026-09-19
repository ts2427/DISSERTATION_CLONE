"""
REBUILD V4 - STAGE 6: SEC FETCH FOR OUTCOME DATA (run locally by Tim)
=============================================================================
Two modes, run in this order:

    set SEC_EDGAR_USER_AGENT=Your Name your.email@university.edu
    python scripts/231_fetch_outcome_data_v4.py --submissions
    python scripts/231_fetch_outcome_data_v4.py --documents

--submissions
    Fetches the submissions JSON for every CIK in 234_submissions_needed.txt -
    the candidates scripts/234 could not count offline, which is why 67 events
    have no outcome_cik.  Stored in the SAME page-list shape as v3's committed
    cache, so 234 reads both without special-casing.

    It then re-runs 234 -> 233 -> 230 OFFLINE and reports: how many of the
    in-scope events still lack an outcome_cik, split treated/control; the 233
    verdicts (Disney must reach 'agree', or the reason it did not); and the
    refreshed needs_fetch list.

--documents
    Fetches the Item 5.02 filing text for every needs_fetch == 1 row of
    230_outcome_cik_gap.csv, each row using ITS OWN win_lo/win_hi, into the
    existing Data/edgar/item5_02_text/{cik}/{accession}_{primaryDocument}
    layout (scripts/187's convention, so the two vintages interleave).

    It then draws the fresh OUT-OF-SAMPLE validation sample from the NEW
    documents only.  The seed is fixed in this file, below, before any
    classification exists for these documents.  This script NEVER classifies and
    never reads classifier output - that separation is the whole point of the
    firewall, and per Tim's ruling the v3-era draws and the v2 classifier are
    frozen, with no retuning permitted under any result.

NETWORK BEHAVIOUR is scripts/213's, reused rather than reimplemented: declared
User-Agent from SEC_EDGAR_USER_AGENT, MIN_INTERVAL 0.20s (5 req/s), retry with
exponential backoff on 429/503 and on the transient read errors that killed
runs 2 and 3, Retry-After honoured, and ONLY a 200 whose body is not an error
page is ever cached.  Any cached throttle page already on disk is quarantined
before the run starts.

FAILS LOUDLY
------------
Missing input ABORTS.  A missing or malformed User-Agent ABORTS.  Any exception
writes the PARTIAL log with an ABORTED section naming the phase that was
running and what had completed, then exits nonzero (cf. 211/213).

OUTPUTS
-------
    Data/edgar/submissions_cache_v4/{cik}.json     (--submissions)
    Data/edgar/item5_02_text/{cik}/{acc}_{doc}     (--documents)
    outputs/rebuild_v4/231_fetch_rows.csv          one row per item attempted
    outputs/rebuild_v4/231_validation_new_ids.csv  (--documents) the fresh draw
    outputs/rebuild_v4/231_fetch_log.md
"""
import argparse
import json
import random
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

# The validation seed is FIXED HERE, before any classification of the new
# documents is run or inspected. Changing it after seeing any result would
# destroy the firewall the v3 rounds established.
NEW_VALIDATION_SEED = 20260919
NEW_VALIDATION_MAX = 30

NEEDED = Path("outputs/rebuild_v4/234_submissions_needed.txt")
GAP = Path("outputs/rebuild_v4/230_outcome_cik_gap.csv")
SUBS_V4 = Path("Data/edgar/submissions_cache_v4")
SUBS_V3 = Path("Data/edgar/rebuild_submissions_cache")
TXT = Path("Data/edgar/item5_02_text")
OUT = Path("outputs/rebuild_v4")
ROWS = []
PHASE = {"name": "startup", "detail": ""}

M213 = None


def load_213():
    global M213
    if M213 is None:
        import importlib.util
        p = Path("scripts/213_stage3_verify.py")
        if not p.exists():
            abort("missing input: " + str(p))
        spec = importlib.util.spec_from_file_location("m213_for_231", str(p))
        M213 = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(M213)
    return M213


L = []


def log(msg=""):
    print(msg, flush=True)
    L.append(str(msg))


def write_log(aborted=None):
    OUT.mkdir(parents=True, exist_ok=True)
    if ROWS:
        pd.DataFrame(ROWS).to_csv(OUT / "231_fetch_rows.csv", index=False)
    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    head = ["# REBUILD V4 - Stage 6 SEC fetch run log", "",
            "- finished (UTC): " + stamp,
            "- phase reached: **" + PHASE["name"] + "**"
            + ((" - " + PHASE["detail"]) if PHASE["detail"] else ""),
            "- items attempted: " + str(len(ROWS)), ""]
    tail = []
    if aborted:
        tail = ["## ABORTED", "", "**" + str(aborted) + "**", "",
                "- the phase above is the one that was running",
                "- 231_fetch_rows.csv is PARTIAL; items after the last row were never "
                "attempted",
                "- nothing downstream should treat this run as complete"]
    else:
        tail = ["## COMPLETE", "", "The requested phase finished."]
    (OUT / "231_fetch_log.md").write_text(
        chr(10).join(head + L + [""] + tail) + chr(10), encoding="utf-8")


def abort(msg):
    write_log(aborted=msg)
    sys.exit("ABORT: " + str(msg))


def require(p):
    if not Path(p).exists():
        abort("missing input: " + str(p) + " (no graceful fallback)")
    return Path(p)


def run_offline(script):
    """Re-run one offline script, surfacing its failure rather than swallowing it."""
    import os
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    r = subprocess.run([sys.executable, script], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", env=env)
    if r.returncode != 0:
        log(r.stdout[-2000:] if r.stdout else "")
        log(r.stderr[-2000:] if r.stderr else "")
        abort(script + " failed with exit " + str(r.returncode))
    return r.stdout or ""


# --------------------------------------------------------------- submissions
def submission_pages(cik, m):
    """The page-list shape v3's cache uses: [recent, *older shards]."""
    raw = m.fetch("https://data.sec.gov/submissions/CIK" + format(int(cik), "010d")
                  + ".json")
    if raw is None:
        return None
    d = json.loads(raw.decode("utf-8", "replace"))
    filings = d.get("filings", {}) or {}
    pages = []
    rec = filings.get("recent")
    if rec:
        pages.append(rec)
    for extra in filings.get("files", []) or []:
        nm = extra.get("name", "")
        if not nm:
            continue
        d2 = m.fetch("https://data.sec.gov/submissions/" + nm)
        if d2:
            pages.append(json.loads(d2.decode("utf-8", "replace")))
    return pages


def phase_submissions():
    PHASE["name"] = "submissions"
    m = load_213()
    m.user_agent()
    text = require(NEEDED).read_text(encoding="utf-8")
    ciks = sorted({int(x) for x in text.split() if x.strip().isdigit()})
    if not ciks:
        abort(str(NEEDED) + " lists no CIKs - nothing to fetch")
    log("CIKs to fetch: " + str(len(ciks)))
    SUBS_V4.mkdir(parents=True, exist_ok=True)

    for i, cik in enumerate(ciks, 1):
        PHASE["detail"] = "CIK " + str(cik) + " (" + str(i) + "/" + str(len(ciks)) + ")"
        dest = SUBS_V4 / (str(cik) + ".json")
        if dest.exists():
            ROWS.append(dict(phase="submissions", cik=cik, status="already_on_disk",
                             n_pages=None, path=str(dest)))
            log("  " + str(cik) + ": already on disk")
            continue
        pages = submission_pages(cik, m)
        if not pages:
            ROWS.append(dict(phase="submissions", cik=cik, status="no_submissions",
                             n_pages=0, path=""))
            log("  " + str(cik) + ": NO submissions returned")
            continue
        dest.write_text(json.dumps(pages), encoding="utf-8")
        ROWS.append(dict(phase="submissions", cik=cik, status="fetched",
                         n_pages=len(pages), path=str(dest)))
        log("  " + str(cik) + ": " + str(len(pages)) + " page(s)")

    PHASE["name"] = "re-resolve (offline)"
    PHASE["detail"] = ""
    log("")
    log("## Re-running 234 -> 233 -> 230 offline")
    run_offline("scripts/234_outcome_cik_v4.py")
    out233 = run_offline("scripts/233_resolve_reconciliation.py")
    run_offline("scripts/230_outcome_gap_v4.py")

    PHASE["name"] = "report"
    gap = pd.read_csv(GAP, low_memory=False)
    sc = gap[gap["in_scope"] == 1]
    uns = sc[sc["outcome_cik"].isna()]
    log("")
    log("## Unresolved outcome_cik WITHIN the in-scope events")
    log("in-scope events            : " + str(len(sc))
        + "  (treated " + str(int(sc["treated"].sum()))
        + ", control " + str(int((sc["treated"] == 0).sum())) + ")")
    log("still without an outcome_cik: " + str(len(uns))
        + "  (treated " + str(int(uns["treated"].sum()))
        + ", control " + str(int((uns["treated"] == 0).sum())) + ")")
    if len(uns):
        log("")
        log(uns[["final_cik", "org_name", "breach_date", "treated",
                 "outcome_unresolved"]].to_string(index=False))

    log("")
    log("## scripts/233 verdicts")
    for line in out233.splitlines():
        if line.strip():
            log("    " + line.rstrip())
    recon = pd.read_csv("outputs/rebuild_v4/resolve_reconciliation.csv", low_memory=False)
    dis = recon[recon["v4_final_cik"].astype(str) == "1744489"]
    if len(dis):
        v = str(dis.iloc[0]["verdict"])
        log("")
        log("Disney (926480 -> 1744489): verdict **" + v + "**")
        if v != "agree":
            log("NOT 'agree'. Reason recorded: " + str(dis.iloc[0]["detail"]))
            log("This must be explained before 224 runs - 224 blocks on any "
                "disagree or pending row.")

    need = sc[sc["needs_fetch"] == 1]
    log("")
    log("## Refreshed needs_fetch list")
    log("scope events needing documents: " + str(len(need))
        + "  (treated " + str(int(need["treated"].sum()))
        + ", control " + str(int((need["treated"] == 0).sum())) + ")")
    log("distinct outcome CIKs         : "
        + str(need["outcome_cik"].dropna().nunique()))
    if len(need):
        log("")
        log(need[["outcome_cik", "outcome_rule", "org_name", "breach_date", "treated",
                  "win_lo", "win_hi"]].sort_values(
                      ["outcome_cik", "breach_date"]).to_string(index=False))


# --------------------------------------------------------------- documents
def load_pages(cik):
    for root in (SUBS_V4, SUBS_V3):
        fp = root / (str(int(cik)) + ".json")
        if fp.exists():
            try:
                return json.loads(fp.read_text(encoding="utf-8", errors="replace"))
            except json.JSONDecodeError:
                return None
    return None


def item502_filings(pages, lo, hi):
    """8-K / 8-K/A filings listing Item 5.02, filed inside [lo, hi]."""
    out = []
    for pg in pages or []:
        forms = pg.get("form") or []
        n = len(forms)
        dates = pg.get("filingDate") or []
        items = pg.get("items") or [""] * n
        accs = pg.get("accessionNumber") or []
        docs = pg.get("primaryDocument") or []
        for i, f in enumerate(forms):
            if not str(f).startswith("8-K"):
                continue
            if i >= len(dates) or i >= len(accs):
                continue
            if "5.02" not in str(items[i] if i < len(items) else ""):
                continue
            d = pd.to_datetime(dates[i], errors="coerce")
            if pd.isna(d) or not (lo <= d <= hi):
                continue
            out.append(dict(accession=str(accs[i]), filing_date=str(dates[i]),
                            primary_doc=str(docs[i] if i < len(docs) else "")))
    return out


def phase_documents():
    PHASE["name"] = "documents"
    m = load_213()
    m.user_agent()
    gap = pd.read_csv(require(GAP), low_memory=False)
    need = gap[(gap["in_scope"] == 1) & (gap["needs_fetch"] == 1)].copy()
    need = need[need["outcome_cik"].notna()]
    if not len(need):
        abort("no needs_fetch rows with a resolved outcome_cik - run --submissions "
              "first, or there is nothing to fetch")
    log("scope events to fetch for: " + str(len(need))
        + " (distinct outcome CIKs " + str(need["outcome_cik"].nunique()) + ")")

    pre_existing = set()
    if TXT.exists():
        for d in TXT.iterdir():
            if d.is_dir():
                for f in d.iterdir():
                    if f.is_file():
                        pre_existing.add((d.name, f.name))

    new_docs = []
    for i, (_, r) in enumerate(need.iterrows(), 1):
        cik = int(r["outcome_cik"])
        lo, hi = pd.Timestamp(r["win_lo"]), pd.Timestamp(r["win_hi"])
        PHASE["detail"] = ("CIK " + str(cik) + " " + str(r["breach_date"])
                           + " (" + str(i) + "/" + str(len(need)) + ")")
        pages = load_pages(cik)
        if pages is None:
            ROWS.append(dict(phase="documents", cik=cik,
                             breach_date=r["breach_date"], accession="",
                             status="submissions_not_cached", path=""))
            log("  " + str(cik) + ": submissions not cached - run --submissions first")
            continue
        fl = item502_filings(pages, lo, hi)
        if not fl:
            ROWS.append(dict(phase="documents", cik=cik,
                             breach_date=r["breach_date"], accession="",
                             status="no_502_in_window", path=""))
            continue
        for f in fl:
            if not f["primary_doc"]:
                ROWS.append(dict(phase="documents", cik=cik,
                                 breach_date=r["breach_date"],
                                 accession=f["accession"],
                                 status="no_primary_document", path=""))
                continue
            dest = TXT / str(cik) / (f["accession"] + "_" + f["primary_doc"])
            key = (str(cik), dest.name)
            if dest.exists():
                ROWS.append(dict(phase="documents", cik=cik,
                                 breach_date=r["breach_date"],
                                 accession=f["accession"],
                                 status="already_on_disk", path=str(dest)))
                continue
            url = ("https://www.sec.gov/Archives/edgar/data/" + str(cik) + "/"
                   + f["accession"].replace("-", "") + "/" + f["primary_doc"])
            data = m.fetch(url)
            if data is None:
                ROWS.append(dict(phase="documents", cik=cik,
                                 breach_date=r["breach_date"],
                                 accession=f["accession"], status="absent", path=""))
                continue
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
            ROWS.append(dict(phase="documents", cik=cik,
                             breach_date=r["breach_date"],
                             accession=f["accession"], status="fetched",
                             path=str(dest)))
            if key not in pre_existing:
                new_docs.append(dict(cik=cik, accession=f["accession"],
                                     filing_date=f["filing_date"],
                                     primary_doc=f["primary_doc"],
                                     local_file=str(dest)))

    PHASE["name"] = "validation draw"
    PHASE["detail"] = ""
    draw = draw_validation(new_docs)
    log("")
    log("## Fresh out-of-sample validation draw (new documents only)")
    log("new documents fetched : " + str(len(new_docs)))
    log("seed                  : " + str(NEW_VALIDATION_SEED) + " (fixed in the script)")
    log("drawn                 : " + str(len(draw))
        + " = min(" + str(NEW_VALIDATION_MAX) + ", new documents)")
    if len(draw):
        pd.DataFrame(draw).to_csv(OUT / "231_validation_new_ids.csv", index=False)
        log("written " + str(OUT / "231_validation_new_ids.csv"))
    log("")
    log("The v3-era draws and the v2 classifier are FROZEN. These documents are "
        "reference-coded and disclosed exactly as the v3 rounds were, and no "
        "retuning follows from any result. This script does not classify.")


def draw_validation(new_docs):
    """Deterministic draw from the NEW documents only."""
    pool = sorted({(d["cik"], d["accession"]): d for d in new_docs}.values(),
                  key=lambda d: (int(d["cik"]), str(d["accession"])))
    k = min(NEW_VALIDATION_MAX, len(pool))
    if k == 0:
        return []
    rng = random.Random(NEW_VALIDATION_SEED)
    return sorted(rng.sample(pool, k),
                  key=lambda d: (int(d["cik"]), str(d["accession"])))


def main():
    ap = argparse.ArgumentParser(description="REBUILD V4 Stage 6 SEC fetch")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--submissions", action="store_true")
    g.add_argument("--documents", action="store_true")
    a = ap.parse_args()

    log("# REBUILD V4 - Stage 6 SEC fetch (scripts/231)")
    log("")
    m = load_213()
    bad = m.quarantine_bad_cache()
    if bad:
        log("Quarantined " + str(len(bad)) + " bad cached file(s) before starting:")
        for name, why in bad:
            log("  " + name + " - " + why)
        log("")

    if a.submissions:
        phase_submissions()
    else:
        phase_documents()
    PHASE["name"] = "complete"
    PHASE["detail"] = ""
    write_log()
    log("")
    log("Run log: " + str(OUT / "231_fetch_log.md"))


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except BaseException as e:
        abort("unhandled " + type(e).__name__ + ": " + str(e))
