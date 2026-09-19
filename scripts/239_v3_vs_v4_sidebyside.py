"""
REBUILD V4 - STAGE 6: v3-OVERLAP SENSITIVITY AND THE v3 vs v4 SIDE-BY-SIDE
=============================================================================
    python scripts/239_v3_vs_v4_sidebyside.py

TWO JOBS
--------
1. THE v3-OVERLAP SENSITIVITY, pre-specified in ANALYSIS_PLAN_V4.md. The v4
   primary specification re-estimated on the v4 sample with the control group
   restricted to events that were ALSO linked in v3; every treated event is kept.

   It exists because every v4 linkage gain fell on the control side. Without it,
   a change in the estimate cannot be separated from the change in who is in the
   control group.

2. THE SIDE-BY-SIDE of every constant and verdict, v3 against v4.

THE ESTIMATOR IS NOT REIMPLEMENTED. ladder() and pub() are lifted out of
scripts/227 by parsing its source and executing those definitions here, so the
overlap sensitivity runs the identical code path as the primary. 227 has no
__main__ guard, so importing it would re-run the whole estimation.

Offline.  Inputs (missing ABORTS):
    outputs/essay3_v4/e_analysis_sample.csv, f1_ladder.csv, f4_placebo.csv,
    f3_loco.csv, i_tests.csv, f5_ceo.csv
    outputs/rebuild_v4/v4_212_links.csv        (v3_linked)
    outputs/essay3_q2/constants_essay3_q2.json (v3 constants, read-only)
Outputs:
    outputs/essay3_v4/239_v3_overlap_sensitivity.csv
    outputs/essay3_v4/239_v3_vs_v4_constants.csv
    outputs/essay3_v4/239_sidebyside.md
"""
import ast
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats

OUT = Path("outputs/essay3_v4")
V3DIR = Path("outputs/essay3_q2")
LINKS = Path("outputs/rebuild_v4/v4_212_links.csv")
SRC227 = Path("scripts/227_essay3_v4_estimation.py")

L = []


def log(msg=""):
    print(msg, flush=True)
    L.append(str(msg))


def flush():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "239_sidebyside.md").write_text(chr(10).join(L) + chr(10), encoding="utf-8")


def abort(msg):
    log("")
    log("ABORT: " + str(msg))
    flush()
    sys.exit("ABORT: " + str(msg))


def require(p):
    if not Path(p).exists():
        abort("missing input: " + str(p))
    return Path(p)


def borrow_from_227():
    """Lift ladder() / pub() and their constants out of scripts/227, unchanged."""
    src = require(SRC227).read_text(encoding="utf-8")
    tree = ast.parse(src)
    want_fn = {"ladder"}
    # pub is a lambda ASSIGNMENT in 227, not a def, so it is lifted with the constants.
    # rng is 227's seeded generator (default_rng(3)); the bootstrap needs it.
    want_const = {"TREAT", "BASE", "CTRL", "pub", "rng"}
    pieces = []
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name in want_fn:
            pieces.append(ast.get_source_segment(src, node))
        elif isinstance(node, ast.Assign):
            names = {t.id for t in node.targets if isinstance(t, ast.Name)}
            if names & want_const:
                pieces.append(ast.get_source_segment(src, node))
    ns = {"np": np, "pd": pd, "sm": sm, "stats": stats}
    exec(chr(10).join(pieces), ns)
    missing = (want_fn | want_const) - set(ns)
    if missing:
        abort("could not lift from scripts/227: " + ", ".join(sorted(missing)))
    return ns


def main():
    ns = borrow_from_227()
    ladder, pub = ns["ladder"], ns["pub"]
    TREAT, CTRL = ns["TREAT"], ns["CTRL"]

    d0 = pd.read_csv(require(OUT / "e_analysis_sample.csv"), low_memory=False)
    d0 = d0[d0["in_analysis_sample"] == 1].copy()
    links = pd.read_csv(require(LINKS), low_memory=False)
    if "v3_linked" not in links.columns:
        abort(str(LINKS) + " has no v3_linked column")
    links["breach_date"] = links["breach_date"].astype(str).str[:10]
    d0["breach_date"] = d0["breach_date"].astype(str).str[:10]
    key = ["final_cik", "breach_date"]
    v3l = (links.drop_duplicates(key).set_index(key)["v3_linked"]
           .apply(lambda v: int(v) if pd.notna(v) else 0))
    d0["v3_linked"] = [int(x) if pd.notna(x) else 0
                       for x in d0.set_index(key).index.map(v3l)]

    # every treated event kept; control restricted to events v3 also linked
    keep = (d0[TREAT] == 1) | (d0["v3_linked"] == 1)
    dov = d0[keep].copy()

    log("# REBUILD V4 - v3-overlap sensitivity and the v3 vs v4 side-by-side")
    log("")
    log("## v3-overlap sensitivity")
    log("All treated events kept; control restricted to events also linked in v3.")
    log("")
    log("full v4 sample    : n %d (treated %d, control %d)"
        % (len(d0), int((d0[TREAT] == 1).sum()), int((d0[TREAT] == 0).sum())))
    log("v3-overlap sample : n %d (treated %d, control %d)"
        % (len(dov), int((dov[TREAT] == 1).sum()), int((dov[TREAT] == 0).sum())))
    log("control events dropped: %d"
        % int(((d0[TREAT] == 0) & (d0["v3_linked"] != 1)).sum()))

    F1 = pd.read_csv(require(OUT / "f1_ladder.csv"))
    rows = []
    for w in (30, 90, 180):
        y = "exec_departure_%d_rd" % w
        r = ladder(dov, y, [TREAT] + CTRL["rd"], B=9_999, full=True)
        full = F1[F1["window"] == w].iloc[0]
        rows.append(dict(window=w, sample="v3-overlap", **pub(r)))
        rows.append(dict(window=w, sample="full v4",
                         n=int(full["n"]), coef=full["coef"], se_cv3=full["se_cv3"],
                         p_cv3=full["p_cv3"], ci_cv3_lo=full["ci_cv3_lo"],
                         ci_cv3_hi=full["ci_cv3_hi"], p_wcr=full["p_wcr"],
                         p_hc3=full["p_hc3"]))
    S = pd.DataFrame(rows)
    S.to_csv(OUT / "239_v3_overlap_sensitivity.csv", index=False)
    cols = [c for c in ["window", "sample", "n", "coef", "se_cv3", "p_cv3",
                        "ci_cv3_lo", "ci_cv3_hi", "p_wcr"] if c in S.columns]
    log("")
    log(S[cols].sort_values(["window", "sample"]).to_string(index=False))

    # ---------------- side-by-side of constants and verdicts ----------------
    v3c = {}
    for cand in ("constants_essay3_q2.json", "constants_essay3_v4.json"):
        p = V3DIR / cand
        if p.exists():
            v3c = json.loads(p.read_text(encoding="utf-8"))
            break
    v4p = OUT / "constants_essay3_v4.json"
    v4c = json.loads(require(v4p).read_text(encoding="utf-8"))

    keys = sorted(set(v3c) | set(v4c))
    crows = []
    for k in keys:
        a, b = v3c.get(k, None), v4c.get(k, None)
        same = (a == b)
        crows.append(dict(constant=k, v3=a, v4=b,
                          status=("same" if same else
                                  ("v4 only" if a is None else
                                   ("v3 only" if b is None else "DIFFERS")))))
    C = pd.DataFrame(crows)
    C.to_csv(OUT / "239_v3_vs_v4_constants.csv", index=False)
    log("")
    log("## Constants, v3 vs v4")
    log(C.to_string(index=False))
    diff = C[C["status"] == "DIFFERS"]
    log("")
    log("constants that differ: %d of %d" % (len(diff), len(C)))

    log("")
    log("written 239_v3_overlap_sensitivity.csv, 239_v3_vs_v4_constants.csv")
    flush()


if __name__ == "__main__":
    main()
