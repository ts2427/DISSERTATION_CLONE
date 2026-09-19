"""
REBUILD V4 — STAGE 5: THE v4 LEDGER (offline; writes only to v4 paths)
=====================================================================================
Audits CANONICAL_V4 and reports, step by step, how v4 differs from v3 — by treated and
control — with the gains attributed to their causes rather than pooled.

    python scripts/215_ledger_v4.py

READS   Data/processed/rebuild_v4/CANONICAL_V4.csv   (written by 214)
        outputs/rebuild_v4/212_links.csv             (written by 212)
        outputs/essay3_q2/e_ledger.csv               (the v3 ledger, read-only)
        Data/wrds_v4/crsp_dsf*.csv                   (date column only)
WRITES  outputs/rebuild_v4/v4_ledger.csv
        outputs/rebuild_v4/v4_symmetry.csv
        outputs/rebuild_v4/215_ledger.md

CANONICAL_V4 is produced by 214, not here. Stage 5 audits it; two scripts writing the
same path is how they drift apart.

NO TIMESTAMPS IN DATA ARTIFACTS. Both CSVs are checked with
218_v4_common.assert_no_timestamp before they are written, so a run timestamp cannot
reach them by accident. The .md may carry one, in a declared header line only.

JOINING BY ROW INDEX, NOT BY KEY
--------------------------------
212 ran against CANONICAL_V3 and 214 then changed three keys (Sprint's breach_date,
International Paper's and Lennar's final_cik). Joining the links to CANONICAL_V4 on
(final_cik, breach_date) would therefore drop exactly the corrected rows — the ones most
in need of auditing. All three files are 489 rows in the same order, which is asserted
here, so the join is positional.

WHAT STAGE 5 CANNOT COMPUTE
---------------------------
The ledger's last three steps — Compustat covariates, the outcome-data requirement, and
the prior 12-month return — depend on data the Essay 3 pipeline builds. The matching
columns in CANONICAL_V4 hold v3-derived values, so reporting them as v4 numbers would be
false. They are marked `not_computable_until_stage6` and carry the v3 figure for
reference only.
"""
import importlib.util
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

CANON_V4 = Path("Data/processed/rebuild_v4/CANONICAL_V4.csv")
LINKS = Path("outputs/rebuild_v4/212_links.csv")
E_LEDGER = Path("outputs/essay3_q2/e_ledger.csv")
DSF = (Path("Data/wrds_v4/crsp_dsf.csv"),)
DSF_GLOB = "crsp_dsf_topup_*.csv"

OUT_LEDGER = Path("outputs/rebuild_v4/v4_ledger.csv")
OUT_SYMMETRY = Path("outputs/rebuild_v4/v4_symmetry.csv")
OUT_MD = Path("outputs/rebuild_v4/215_ledger.md")
V4_PREFIXES = ("Data/processed/rebuild_v4/", "outputs/rebuild_v4/")

V3_EXTRACT_END = pd.Timestamp("2024-12-31")   # the CRSP extract v3 was built on
OUTCOME_HORIZON_DAYS = 180                    # longest Essay 3 outcome window

LOG = []


def log(m=""):
    print(m, flush=True)
    LOG.append(str(m))


def load_common():
    p = Path("scripts/218_v4_common.py")
    if not p.exists():
        sys.exit(f"missing input: {p}")
    spec = importlib.util.spec_from_file_location("v4common", str(p))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def assert_v4(*paths):
    for p in paths:
        if not Path(p).as_posix().startswith(V4_PREFIXES):
            sys.exit(f"refusing to write outside a v4 path: {p}")


def md_table(df):
    cols = [str(c) for c in df.columns]
    out = ["| " + " | ".join(cols) + " |", "|" + "|".join("---" for _ in cols) + "|"]
    for _, r in df.iterrows():
        out.append("| " + " | ".join("" if pd.isna(v) else str(v)[:70] for v in r) + " |")
    return "\n".join(out)


def crsp_max_date(paths):
    """Latest date in the pulled daily stock file(s)."""
    best = None
    for p in paths:
        try:
            d = pd.read_csv(p, usecols=["date"], low_memory=False)
        except Exception:
            continue
        m = pd.to_datetime(d["date"], errors="coerce").max()
        if pd.notna(m) and (best is None or m > best):
            best = m
    return best


def group_of(ev):
    return ev["fcc_form499"].map({1: "treated", 0: "control"})


def symmetry(links):
    """link_source by group, and CRSP retention by group, v3 against v4."""
    L = links.copy()
    L["grp"] = L["grp"].fillna("(unknown)")
    L["link_source"] = L["link_source"].fillna("(unlinked)")
    rows = []
    for src, sub in L.groupby("link_source"):
        rows.append({"measure": "link_source", "value": src,
                     "treated": int((sub["grp"] == "treated").sum()),
                     "control": int((sub["grp"] == "control").sum()),
                     "total": len(sub)})
    v4l = L["permno"].notna()
    v3l = L["v3_permno"].notna()
    for label, mask in (("v3 linked", v3l), ("v4 linked", v4l)):
        rows.append({"measure": "crsp_retention", "value": label,
                     "treated": int((mask & (L["grp"] == "treated")).sum()),
                     "control": int((mask & (L["grp"] == "control")).sum()),
                     "total": int(mask.sum())})
    rows.append({"measure": "crsp_retention", "value": "delta v4-v3",
                 "treated": int((v4l & (L["grp"] == "treated")).sum()
                                - (v3l & (L["grp"] == "treated")).sum()),
                 "control": int((v4l & (L["grp"] == "control")).sum()
                                - (v3l & (L["grp"] == "control")).sum()),
                 "total": int(v4l.sum() - v3l.sum())})
    return pd.DataFrame(rows)


def attribution(ev4, links, crsp_max, horizon=OUTCOME_HORIZON_DAYS):
    """Split the CRSP-step gain into its two distinct causes. -> DataFrame.

    An event is 'recovered by relinking' when v4 found a permno v3 lacked AND its outcome
    window ends on or before the v3 extract. It is 'added by the longer extract' only when
    the new pull actually reaches past that date. Pooling the two would credit the linker
    with recoveries that are really just more data, and vice versa.
    """
    grp = group_of(ev4).fillna("(unknown)").values
    gained = links["permno"].notna().values & ~links["v3_permno"].notna().values
    window_end = (pd.to_datetime(ev4["breach_date"], errors="coerce")
                  + pd.Timedelta(horizon, unit="D"))
    inside_v3 = (window_end <= V3_EXTRACT_END).values
    extends = crsp_max is not None and crsp_max > V3_EXTRACT_END

    lost = (~links["permno"].notna().values) & links["v3_permno"].notna().values

    relink = gained & inside_v3
    needs_more = gained & ~inside_v3
    none = needs_more & False
    # `extends` is a Python bool: `~extends` would be the bitwise inversion of an int
    # (~True == -2, which is truthy), so the branch is written out explicitly.
    longer, unexplained = (needs_more, none) if extends else (none, needs_more)

    def line(label, mask):
        return {"cause": label,
                "treated": int((mask & (grp == "treated")).sum()),
                "control": int((mask & (grp == "control")).sum()),
                "total": int(mask.sum())}

    rows = [line("recovered by relinking", relink),
            line("added by the longer extract", longer),
            line("gained but window past the extract, not covered", unexplained),
            {"cause": "overlap (counted under relinking only)",
             "treated": 0, "control": 0, "total": 0},
            line("GAINED: linked in v4, not in v3", gained),
            line("LOST: linked in v3, not in v4", lost)]
    g, l = rows[-2], rows[-1]
    rows.append({"cause": "NET change (gained - lost)",
                 "treated": g["treated"] - l["treated"],
                 "control": g["control"] - l["control"],
                 "total": g["total"] - l["total"]})
    return pd.DataFrame(rows), extends


def build_ledger(ev4, links, e_ledger):
    """The v3 ledger's steps, with v4 values where Stage 5 can honestly compute them."""
    grp = group_of(ev4).fillna("(unknown)")
    v4_canon_t = int((grp == "treated").sum())
    v4_canon_c = int((grp == "control").sum())
    v4_link = links["permno"].notna()
    v4_crsp_t = int((v4_link & (grp == "treated").values).sum())
    v4_crsp_c = int((v4_link & (grp == "control").values).sum())

    computed = {
        "Stage 4/5 canonical events (CANONICAL_V3)":
            (len(ev4), v4_canon_t, v4_canon_c, "computed from CANONICAL_V4"),
        "CRSP data (has_crsp_data)":
            (int(v4_link.sum()), v4_crsp_t, v4_crsp_c,
             "BASELINES DIFFER: v3 N is has_crsp_data, v4 N is the point-in-time link. "
             "For the like-for-like permno comparison see v4_symmetry.csv (v3 permno vs "
             "v4 permno); for gained/lost/net see the attribution table. v3 carries more "
             "permnos than has_crsp_data flags, so this row's delta is NOT the net link "
             "change."),
    }
    rows = []
    for _, r in e_ledger.iterrows():
        step = str(r["step"])
        n3 = r["N"]
        t3 = r.get("treated")
        c3 = r.get("control")
        if step in computed:
            n4, t4, c4, note = computed[step]
            status = "computed"
        elif step in ("Compustat covariates (size, leverage, ROA) = Query 2 scope",
                      "Outcome-data requirement (>=1 8-K in [t0-730d, t0+180d], outcome CIK)",
                      "Prior 12-month market-adjusted return available (>=150 daily returns)"):
            n4 = t4 = c4 = pd.NA
            status = "not_computable_until_stage6"
            note = "depends on Essay 3 pipeline inputs; the matching CANONICAL_V4 columns hold v3-derived values"
        else:
            n4, t4, c4 = n3, t3, c3
            status = "upstream_of_v4"
            note = "upstream of every v4 change; carried through unchanged"
        rows.append({
            "step": step, "status": status,
            "N_v3": n3, "N_v4": n4,
            "N_delta": (n4 - n3) if (status == "computed") else pd.NA,
            "treated_v3": t3, "treated_v4": t4,
            "treated_delta": (t4 - t3) if (status == "computed" and pd.notna(t3)) else pd.NA,
            "control_v3": c3, "control_v4": c4,
            "control_delta": (c4 - c3) if (status == "computed" and pd.notna(c3)) else pd.NA,
            "note": note})
    return pd.DataFrame(rows)


def main():
    for p in (CANON_V4, LINKS, E_LEDGER):
        if not p.exists():
            sys.exit(f"missing input: {p}")
    common = load_common()
    assert_v4(OUT_LEDGER, OUT_SYMMETRY, OUT_MD)

    ev4 = pd.read_csv(CANON_V4, low_memory=False)
    links = pd.read_csv(LINKS, low_memory=False)
    e_ledger = pd.read_csv(E_LEDGER)
    if len(ev4) != len(links):
        sys.exit(f"CANONICAL_V4 has {len(ev4)} rows and 212_links has {len(links)}; "
                 "the positional join is only valid when they match.")

    dsf = list(DSF) + sorted(Path("Data/wrds_v4").glob(DSF_GLOB))
    crsp_max = crsp_max_date(dsf)

    ledger = build_ledger(ev4, links, e_ledger)
    sym = symmetry(links)
    attr, extends = attribution(ev4, links, crsp_max)

    log("# REBUILD V4 — Stage 5 ledger")
    log("")
    log(f"- run (UTC): {datetime.now(timezone.utc).isoformat(timespec='seconds')}")
    log(f"- CANONICAL_V4: {len(ev4)} rows | 212 links: {len(links)} rows "
        f"(positional join asserted)")
    log(f"- CRSP daily extract reaches {str(crsp_max)[:10]}; v3 was built on "
        f"{V3_EXTRACT_END.date()}")
    log("")
    log("## Ledger, v3 against v4")
    log("")
    log(md_table(ledger[["step", "status", "N_v3", "N_v4", "treated_v3", "treated_v4",
                         "control_v3", "control_v4"]]))
    log("")
    log("## Symmetry")
    log("")
    log(md_table(sym))
    log("")
    log("## Attribution of the CRSP-step gain")
    log("")
    if not extends:
        log(f"The pulled `crsp.dsf` reaches {str(crsp_max)[:10]}, which does NOT extend "
            f"past the {V3_EXTRACT_END.date()} extract v3 used. The "
            f"**added by the longer extract** line is therefore empty by construction, "
            f"and every gain below is attributable to relinking.")
        log("")
    log(md_table(attr))
    log("")

    OUT_LEDGER.parent.mkdir(parents=True, exist_ok=True)
    for path, df in ((OUT_LEDGER, ledger), (OUT_SYMMETRY, sym)):
        text = df.to_csv(index=False)
        bad = common.assert_no_timestamp(path, text)
        if bad:
            sys.exit(f"{path} is a data artifact and must carry no run timestamp; "
                     f"found: {bad[:3]}")
        path.write_text(text, encoding="utf-8", newline="")
    OUT_MD.write_text("\n".join(LOG) + "\n", encoding="utf-8")
    print(f"\nWROTE {OUT_LEDGER}\nWROTE {OUT_SYMMETRY}\nWROTE {OUT_MD}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
