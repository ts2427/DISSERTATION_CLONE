"""
REBUILD V4 - TARGETED RE-ESTIMATION OF THE SIC-FE SENSITIVITY ONLY
=============================================================================
    python scripts/241_sic_fe_reestimate_v4.py

Freeze exception 2026-09-24, reason 1, logged in docs/claude/POST_DEFENSE.md BEFORE
the code change. scripts/224 now builds sic2 from Compustat's header SIC for the
resolved parent instead of the PRC extract's inherited sic.

SCOPE. Three rows only - 'two-digit SIC FE' at 30, 90 and 180 days - plus the
Benjamini-Hochberg adjustment over the 27-row sensitivities family, which has to be
redone because BH is computed within family and three of its p-values move.

NOT re-estimated, and asserted byte-identical afterwards: f1_ladder.csv,
f4_placebo.csv, f1_cluster_diagnostics.csv, f3_loco.csv, f5_ceo.csv,
constants_essay3_v4.json. None of them reads sic2.

THE ESTIMATOR IS NOT REIMPLEMENTED. ladder(), pub(), the seeded rng and the
constants are lifted out of scripts/227 by parsing its source, so these rows run the
identical code path with the identical arguments (B=9_999, full=False, fe='sic2').

ONE THING THIS CANNOT REPRODUCE, stated plainly: scripts/227 draws every bootstrap
from ONE seeded generator in sequence, so the draws a row receives depend on
everything estimated before it. Re-running three rows in isolation starts that
generator fresh, so their WCR p-values are from a different position in the stream
than a full 227 re-run would give. The CV3 p-values, which govern, are deterministic
and unaffected. WCR differences of a few thousandths are bootstrap noise, not a
change in result.

Offline. Inputs: outputs/essay3_v4/{e_analysis_sample,f3_sensitivities,i_tests}.csv
Outputs (rewritten in place): f3_sensitivities.csv, i_tests.csv, f3_sic2_cells.csv
         plus outputs/essay3_v4/241_sic_fe_reestimate.md
"""
import ast
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats
from statsmodels.stats.multitest import multipletests

OUT = Path("outputs/essay3_v4")
SRC227 = Path("scripts/227_essay3_v4_estimation.py")
LABEL = "two-digit SIC FE"
FROZEN = ("f1_ladder.csv", "f4_placebo.csv", "f1_cluster_diagnostics.csv",
          "f3_loco.csv", "f5_ceo.csv", "constants_essay3_v4.json")

L = []


def log(m=""):
    print(m, flush=True)
    L.append(str(m))


def flush():
    (OUT / "241_sic_fe_reestimate.md").write_text(chr(10).join(L) + chr(10),
                                                  encoding="utf-8")


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
    src = require(SRC227).read_text(encoding="utf-8")
    tree = ast.parse(src)
    want_fn = {"ladder"}
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
    ladder, pub, TREAT, CTRL = ns["ladder"], ns["pub"], ns["TREAT"], ns["CTRL"]

    d0 = pd.read_csv(require(OUT / "e_analysis_sample.csv"), low_memory=False)
    d0 = d0[d0["in_analysis_sample"] == 1].copy()
    S3 = pd.read_csv(require(OUT / "f3_sensitivities.csv"))
    IT = pd.read_csv(require(OUT / "i_tests.csv"))

    log("# SIC-FE sensitivity, re-estimated on the Compustat header SIC")
    log("")
    log("Freeze exception 2026-09-24, reason 1 (docs/claude/POST_DEFENSE.md).")
    log("")
    log("## sic2 composition (new)")
    cells = (d0.groupby("sic2")[TREAT].agg(["size", "sum"])
             .rename(columns={"size": "events", "sum": "treated"}))
    cells["control"] = cells["events"] - cells["treated"]
    cells.to_csv(OUT / "f3_sic2_cells.csv")
    log("cells: %d; cells containing treated events: %d"
        % (len(cells), int((cells["treated"] > 0).sum())))
    log(cells.sort_values("events", ascending=False).to_string())
    log("")
    log("cells with treated events: " + "; ".join(
        "SIC %s: %d treated / %d control" % (i, r["treated"], r["control"])
        for i, r in cells[cells["treated"] > 0].iterrows()))

    old = S3[S3["sensitivity"] == LABEL].copy()
    if len(old) != 3:
        abort("expected 3 '%s' rows in f3_sensitivities.csv, found %d"
              % (LABEL, len(old)))

    new_rows = {}
    for w in (30, 90, 180):
        y = "exec_departure_%d_rd" % w
        r = ladder(d0, y, [TREAT] + CTRL["rd"], B=9_999, full=False, fe="sic2")
        new_rows[w] = dict(window=w, sensitivity=LABEL, **pub(r))

    log("")
    log("## Old vs new, the three SIC-FE rows")
    cmp_rows = []
    for w in (30, 90, 180):
        o = old[old["window"] == w].iloc[0]
        n = new_rows[w]
        cmp_rows.append(dict(window=w, which="old (inherited sic)", n=o["n"],
                             coef=round(o["coef"], 4), p_cv3=round(o["p_cv3"], 4),
                             p_wcr=round(o["p_wcr"], 4)))
        cmp_rows.append(dict(window=w, which="new (Compustat sic)", n=n["n"],
                             coef=round(n["coef"], 4), p_cv3=round(n["p_cv3"], 4),
                             p_wcr=round(n["p_wcr"], 4)))
    CMP = pd.DataFrame(cmp_rows)

    # splice the new rows in, preserving row order and every other row untouched
    for w in (30, 90, 180):
        mask = (S3["sensitivity"] == LABEL) & (S3["window"] == w)
        for k, v in new_rows[w].items():
            if k in S3.columns:
                S3.loc[mask, k] = v
    S3.to_csv(OUT / "f3_sensitivities.csv", index=False)

    # BH within the sensitivities family, over all 27 rows
    key = "F3 " + LABEL + " %dd"
    for w in (30, 90, 180):
        m = IT["test"] == (key % w)
        if not m.any():
            abort("test ledger has no row for " + (key % w))
        IT.loc[m, "p"] = new_rows[w]["p_cv3"]
        IT.loc[m, "p_wcr"] = new_rows[w]["p_wcr"]
    old_bh = IT.loc[IT["family"] == "sensitivities", "p_bh"].copy()
    for fam, g in IT.groupby("family"):
        IT.loc[g.index, "p_bh"] = np.round(
            multipletests(g["p"], method="fdr_bh")[1], 4)
    IT.to_csv(OUT / "i_tests.csv", index=False)

    bh = IT[IT["test"].isin([key % w for w in (30, 90, 180)])]
    CMP = CMP.merge(
        bh[["test", "p_bh"]].assign(
            window=[int(t.split()[-1].rstrip("d")) for t in bh["test"]])[["window", "p_bh"]],
        on="window", how="left")
    CMP.loc[CMP["which"].str.startswith("old"), "p_bh"] = np.nan
    log(CMP.to_string(index=False))
    log("")
    log("BH over the sensitivities family (27 rows) recomputed; family min BH p: %.4f"
        % IT.loc[IT["family"] == "sensitivities", "p_bh"].min())
    log("sensitivities-family BH p unchanged elsewhere: %s"
        % ("yes" if np.allclose(
            old_bh.drop(bh.index, errors="ignore").astype(float),
            IT.loc[IT["family"] == "sensitivities", "p_bh"].drop(bh.index,
                                                                errors="ignore").astype(float),
            atol=1e-4) else "NO - inspect"))

    log("")
    log("written f3_sensitivities.csv (3 rows), i_tests.csv (BH), f3_sic2_cells.csv")
    flush()


if __name__ == "__main__":
    main()
