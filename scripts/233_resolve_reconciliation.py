"""
REBUILD V4 - STAGE 6 PREREQUISITE: RESOLVE vs v4 RE-PARENTING RECONCILIATION
=============================================================================
scripts/199 carries a hardcoded RESOLVE dict of outcome-CIK corrections, applied
because v3 had no way to re-parent an event.  v4's Stage 3/4 re-parents events
upstream and records the result in CANONICAL_V4 as final_cik / orig_cik /
link_basis.  Applying both would correct the same event twice.

This script compares them and writes one row per RESOLVE entry x affected event:

  agree     v4's final_cik equals the CIK RESOLVE would have fixed the event to
            (v4 reached the same answer upstream, so 224 must NOT re-apply
            RESOLVE); or RESOLVE excludes the event and v4 does not link it
  disagree  v4 re-parented the event somewhere else, or RESOLVE says EXCLUDE
            while v4 links the event (or the reverse)

Per Tim's ruling, 224 ABORTS on any disagreement.  Each disagreement is ruled on
by hand and the ruling recorded in outputs/rebuild_v4/resolve_rulings.csv, which
224 reads.  This script never decides anything; it only reports.

RUN ORDER NOTE: numeric order and run order diverge here.  233 is a PREREQUISITE
of 224 and must run before it.  It is numbered 233 only because 220-229 are taken
by the Essay 3 copies.

Offline.  Inputs (missing ABORTS, no graceful fallback):
    Data/processed/rebuild_v4/CANONICAL_V4.csv
    outputs/rebuild_v4/v4_212_links.csv
    scripts/199_essay3_q2_sample_e.py            (RESOLVE parsed from source)
Output:
    outputs/rebuild_v4/resolve_reconciliation.csv
"""
import ast
import sys
from pathlib import Path

import pandas as pd

CANON = Path("Data/processed/rebuild_v4/CANONICAL_V4.csv")
LINKS = Path("outputs/rebuild_v4/v4_212_links.csv")
SRC199 = Path("scripts/199_essay3_q2_sample_e.py")
OUT = Path("outputs/rebuild_v4/resolve_reconciliation.csv")

COLS = ["resolve_cik", "resolve_action", "resolve_target_cik", "org_name",
        "breach_date", "treated", "v4_final_cik", "v4_orig_cik", "v4_link_basis",
        "v4_linked", "v4_permno", "verdict", "detail", "resolve_reason"]


def abort(msg):
    sys.exit("ABORT: " + str(msg))


def parse_resolve(path):
    """Read RESOLVE out of scripts/199 by parsing the source - never by importing it
    (199 hits the network at import time)."""
    path = Path(path)
    if not path.exists():
        abort("missing input: " + str(path))
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
                getattr(t, "id", None) == "RESOLVE" for t in node.targets):
            return ast.literal_eval(node.value)
    abort("no RESOLVE assignment found in " + str(path))


def reconcile(resolve, canon, linked, outcome=None):
    """Pure. resolve: {cik: (action, target, reason)}; canon: CANONICAL_V4 frame;
    linked: {(final_cik, breach_date): row-like with v4_linked / permno};
    outcome: {(final_cik, breach_date): outcome_cik or None} from scripts/234.

    RESOLVE fixes the CIK whose FILINGS are read, so it is reconciled against
    outcome_cik, not final_cik.  An event whose outcome_cik is not yet resolved
    (its submissions are not cached) is 'pending', never agree and never
    disagree - 224 blocks on both pending and disagree.
    """
    outcome = outcome or {}
    rows = []
    for cik, (action, target, reason) in sorted(resolve.items()):
        # v3 matched an event on final_cik == cik. After v4's re-parenting that
        # same event carries orig_cik == cik, so both keys must be checked.
        hit = canon[(canon["orig_cik"] == cik) | (canon["final_cik"] == cik)]
        if not len(hit):
            rows.append(dict(zip(COLS, [
                cik, action, target, "", "", "", "", "", "", "", "", "disagree",
                "RESOLVE names a CIK that no v4 event carries as final_cik or orig_cik",
                reason])))
            continue
        for _, e in hit.iterrows():
            key = (e["final_cik"], str(e["breach_date"])[:10])
            lk = linked.get(key)
            v4_linked = "" if lk is None else int(lk.get("v4_linked", 0) or 0)
            v4_permno = "" if lk is None else lk.get("permno", "")
            basis = e.get("link_basis", "")
            if action == "EXCLUDE":
                if v4_linked == 1:
                    verdict = "disagree"
                    detail = ("RESOLVE excludes this event as having no 8-K filer; "
                              "v4 links it")
                else:
                    verdict = "agree"
                    detail = "RESOLVE excludes it and v4 does not link it"
            else:
                oc = outcome.get(key, "__absent__")
                if oc == "__absent__":
                    verdict = "pending"
                    detail = ("scripts/234 has not been run - no outcome_cik to "
                              "reconcile against")
                elif oc is None or (isinstance(oc, float) and pd.isna(oc)):
                    verdict = "pending"
                    detail = ("outcome_cik unresolved (submissions not cached); "
                              "resolve after the 231 fetch, then re-run 233")
                elif int(oc) == int(target):
                    verdict = "agree"
                    detail = ("v4's outcome_cik rule reaches " + str(target)
                              + " independently - RESOLVE must not be re-applied")
                else:
                    verdict = "disagree"
                    detail = ("RESOLVE fixes the outcome CIK to " + str(target)
                              + "; v4's rule reaches " + str(int(oc)))
            rows.append(dict(zip(COLS, [
                cik, action, target, e.get("org_name", ""),
                str(e["breach_date"])[:10], int(e.get("fcc_form499", 0) or 0),
                e["final_cik"], e["orig_cik"], basis, v4_linked, v4_permno,
                verdict, detail, reason])))
    return pd.DataFrame(rows, columns=COLS)


def main():
    for p in (CANON, LINKS):
        if not p.exists():
            abort("missing input: " + str(p))
    resolve = parse_resolve(SRC199)
    canon = pd.read_csv(CANON, low_memory=False)
    links = pd.read_csv(LINKS, low_memory=False)
    for c in ("final_cik", "orig_cik"):
        if c not in canon.columns:
            abort("CANONICAL_V4 has no " + c + " column")

    linked = {}
    if {"final_cik", "breach_date"} <= set(links.columns):
        for _, r in links.iterrows():
            linked[(r["final_cik"], str(r["breach_date"])[:10])] = r

    outcome = {}
    ocp = Path("outputs/rebuild_v4/234_outcome_cik.csv")
    if ocp.exists():
        oc = pd.read_csv(ocp, low_memory=False)
        for _, r in oc.iterrows():
            outcome[(r["final_cik"], str(r["breach_date"])[:10])] = (
                None if pd.isna(r["outcome_cik"]) else int(r["outcome_cik"]))
    else:
        print("NOTE: " + str(ocp) + " absent - run scripts/234 first; "
              "every FIX row will read as pending.")

    out = reconcile(resolve, canon, linked, outcome)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT, index=False)
    n_dis = int((out["verdict"] == "disagree").sum())
    n_pend = int((out["verdict"] == "pending").sum())
    print("=" * 78)
    print("RESOLVE vs v4 RE-PARENTING - scripts/233")
    print("=" * 78)
    print(out[["resolve_cik", "resolve_action", "resolve_target_cik", "org_name",
               "breach_date", "v4_final_cik", "v4_link_basis", "v4_linked",
               "verdict"]].to_string(index=False))
    print()
    for _, r in out[out["verdict"] == "disagree"].iterrows():
        print("  DISAGREE " + str(r["resolve_cik"]) + " " + str(r["org_name"])
              + " " + str(r["breach_date"]))
        print("           " + str(r["detail"]))
    print()
    print("rows " + str(len(out)) + "; agree "
          + str(len(out) - n_dis - n_pend) + "; disagree " + str(n_dis)
          + "; pending " + str(n_pend))
    for _, r in out[out["verdict"] == "pending"].iterrows():
        print("  PENDING  " + str(r["resolve_cik"]) + " " + str(r["org_name"])
              + " " + str(r["breach_date"]))
        print("           " + str(r["detail"]))
    print("written " + str(OUT))
    print("Each disagreement needs a ruling in outputs/rebuild_v4/resolve_rulings.csv "
          "before 224 can run.")


if __name__ == "__main__":
    main()
