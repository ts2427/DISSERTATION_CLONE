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
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

CANON_V4 = Path("Data/processed/rebuild_v4/CANONICAL_V4.csv")
# The SECOND linker pass, run against CANONICAL_V4 after Stage 3 verification and Stage 4
# corrections re-parented the events. The first pass (212_links.csv, keyed to
# CANONICAL_V3) produced the Stage 3 worklist and is kept as evidence, not used here.
LINKS = Path("outputs/rebuild_v4/v4_212_links.csv")
STOCKNAMES = ("crsp_stocknames.csv", "crsp_stocknames_topup_*.csv")
OUT_LOST = Path("outputs/rebuild_v4/215_lost_events.csv")
OUT_S3B = Path("outputs/rebuild_v4/stage3b_candidates.csv")
TICKERS_JSON = Path("Data/edgar/company_tickers.json")

# The two causes a top-up could in principle fix. A share-code exclusion cannot be fixed
# by pulling more data, and a 2025 event with no usable returns has nothing to pull.
TOPUPABLE = ("absent from the CUSIP-filtered pull", "no Compustat gvkey")

# Deferred pending Tim's ruling: Honeywell and Yahoo are self-CIK cases whose chain breaks
# for reasons a successor nomination cannot fix (see the 215 report), and Carnival is a
# Stage 4 CIK-correction candidate rather than a Stage 3b one. They stay OUT of the
# worklist until ruled on, rather than being sent to 213 to fail.
STAGE3B_DEFERRED = {773840: "Honeywell - chain break, pending ruling",
                    1011006: "Yahoo - CIK resolves to the successor entity, pending ruling",
                    815097: "Carnival - Stage 4 CIK-correction candidate, pending ruling"}

# Tim's ruling names the TICKER; the CIK still comes from SEC's own company_tickers.json,
# so no identifier originates in anybody's memory. 213 still decides on the filing.
STAGE3B_TICKER = {1288776: "GOOGL", 813828: "PSKY"}

# Exclusions that are DOCUMENTED rather than unexplained: each has been traced to a
# specific, named cause, and none is a candidate for a further top-up. They are printed
# in the Stage 5 report so the ledger's residual losses are accounted for by name.
# Link choices worth recording because a reader would otherwise have to re-derive them.
DOCUMENTED_IDENTIFICATIONS = [
    ("Paramount (CIK 2041610, 2 events, 2023)",
     "v4 links permno 75104 on the Class A CUSIP 92556H10 - the only share class on the "
     "successor's comp.security record - selected by the exact 8-char ncusip match, "
     "which runs before any fallback. v3 used permno 76226 (92556H20, the other class). "
     "Both are Paramount Global; the difference is which class the identifier resolves "
     "to, not which company."),
]

DOCUMENTED_EXCLUSIONS = [
    ("Yahoo (CIK 1011006, 4 events, 2012-2016)",
     "comp.company maps this CIK to gvkey 62634 ALTABA INC - the post-2017 rump, a "
     "registered closed-end fund (shrcd 14), whose only security runs 2017-06-19 "
     "onward. Its CRSP permco differs from the pre-2017 Yahoo! Inc. permno 83435, so "
     "neither the issuer nor the permco fallback reaches the security that existed at "
     "any of the four breach dates."),
    ("Nokia (CIK 924613, 2013-07-22)",
     "the security CRSP carries is an ADR (shrcd 31), a claim on a foreign share rather "
     "than the share itself. ADRs are excluded by rule, not by accident."),
    ("Audacy / Entercom (2019)",
     "the only match is a header-CUSIP hit against the former name ENTERCOM, which the "
     "identity gate rejects. That is by rule indistinguishable from the "
     "MetroPCS/T-Mobile case the gate exists to catch: CRSP back-fills the header CUSIP "
     "and keeps one permno across the rename. v3 did not link it either, so no "
     "comparison is lost."),
]
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


def m212_for_lookup():
    """213's SEC name-index lookup, loaded without issuing any request."""
    p = Path("scripts/213_stage3_verify.py")
    if not p.exists():
        return None
    spec = importlib.util.spec_from_file_location("m213_for_215", str(p))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    m.fetch = lambda url: None          # Stage 5 never reaches the network
    return m


def load_212():
    """212's name rules, so 'same firm?' is decided identically in both scripts."""
    p = Path("scripts/212_pit_linker_v4.py")
    if not p.exists():
        sys.exit(f"missing input: {p}")
    spec = importlib.util.spec_from_file_location("m212_for_215", str(p))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


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


def read_stocknames():
    """CRSP names, first pull plus every top-up, as one set."""
    paths = [Path("Data/wrds_v4") / STOCKNAMES[0]] + sorted(
        Path("Data/wrds_v4").glob(STOCKNAMES[1]))
    frames = [pd.read_csv(p, low_memory=False) for p in paths if p.exists()]
    if not frames:
        return pd.DataFrame(columns=["permno", "comnam", "namedt", "nameenddt"])
    nam = pd.concat(frames, ignore_index=True)
    nam["namedt"] = pd.to_datetime(nam["namedt"], errors="coerce")
    nam["nameenddt"] = pd.to_datetime(nam["nameenddt"], errors="coerce")
    return nam


def comnam_at(nam, permno, when):
    """CRSP's name for this permno on this date. -> (comnam, note)."""
    if pd.isna(permno):
        return "", "no v3 permno"
    pn = int(permno)
    if pn not in set(nam["permno"].dropna().astype(int)):
        return "", "permno absent from the CUSIP-filtered pull"
    s = nam[(nam["permno"] == pn) & (nam["namedt"] <= when) & (when <= nam["nameenddt"])]
    if not len(s):
        return "", "no CRSP name row valid at breach_date"
    return str(s["comnam"].iloc[0]), ""


def lost_subcause(note, resolvable):
    n = str(note)
    if n.startswith("shrcd"):
        return f"excluded by share code: {n}"
    if n == "no gvkey":
        return "the CIK has no Compustat gvkey, so the chain cannot start"
    if not resolvable:
        return "v3 permno absent from the CUSIP-filtered pull"
    return n


def categorise_lost(ev4, links, nam, names_match):
    """Every event linked in v3 but not in v4, with its cause.

    (a) is not a loss: v3 recorded a permno but its own pipeline found no usable returns,
        so nothing was actually available to lose.
    (b) is a correction: v3 pointed at a different firm than the breached organisation.
    (c) is a real loss, and its sub-cause matters - a share-code exclusion is a policy
        choice, while a permno missing from the pull is a coverage gap in our own data.
    """
    lost = links["v3_permno"].notna().values & ~links["permno"].notna().values
    grp = group_of(ev4).fillna("(unknown)")
    rows = []
    for i in ev4.index[lost]:
        bd = pd.to_datetime(ev4.at[i, "breach_date"], errors="coerce")
        v3p = links.at[i, "v3_permno"]
        cn, cn_note = comnam_at(nam, v3p, bd)
        note = str(links.at[i, "note"])
        usable = bool(ev4.at[i, "has_crsp_data"]) if "has_crsp_data" in ev4.columns else True
        org = str(ev4.at[i, "org_name"])
        if not usable:
            cat, sub = "a_no_usable_returns_in_v3", "v3 flagged has_crsp_data False"
        elif cn and not names_match(cn, org):
            cat, sub = "b_v3_linked_a_different_firm", f"v3 CRSP name {cn!r} vs org {org!r}"
        else:
            cat, sub = "c_v4_gap", lost_subcause(note, bool(cn) or not cn_note)
        rows.append({"category": cat, "sub_cause": sub,
                     "org_name": org,
                     "orig_cik": ev4.at[i, "orig_cik"] if "orig_cik" in ev4.columns else "",
                     "final_cik": ev4.at[i, "final_cik"],
                     "breach_date": str(ev4.at[i, "breach_date"])[:10],
                     "group": grp.at[i],
                     "v3_permno": v3p,
                     "v3_comnam_at_breach": cn or f"({cn_note})",
                     "v4_reason": note})
    return pd.DataFrame(rows)


def ticker_cik_map():
    """ticker -> CIK from the LOCAL company_tickers.json."""
    if not TICKERS_JSON.exists():
        return {}
    j = json.loads(TICKERS_JSON.read_text(encoding="utf-8", errors="replace"))
    out = {}
    for v in (j.values() if isinstance(j, dict) else j):
        t = str(v.get("ticker", "")).strip().upper()
        if t:
            out.setdefault(t, (int(v["cik_str"]), str(v.get("title", ""))))
    return out


def ticker_title_map(norm):
    """normalised company title -> {CIKs}, from the LOCAL company_tickers.json.

    A second, independent nomination source. company_tickers.json lists only CURRENTLY
    registered filers, so a firm whose historical name is ambiguous in the full SEC name
    index can still resolve here - and a unique hit is by construction a live registrant,
    which is what a successor looks like. Stage 5 issues no request; the file is local.
    """
    if not TICKERS_JSON.exists():
        return {}
    j = json.loads(TICKERS_JSON.read_text(encoding="utf-8", errors="replace"))
    out = {}
    for v in (j.values() if isinstance(j, dict) else j):
        title = str(v.get("title", "")).strip()
        if not title:
            continue
        out.setdefault(tuple(norm(title)), set()).add(int(v["cik_str"]))
    return out


def build_stage3b(lost, m213):
    """A Stage 3b worklist for losses a top-up could fix. One row per event.

    v3's permno is NOT carried over. v3 reached it through a CIK->ticker match that this
    rebuild exists to replace, so importing it would reintroduce exactly the thing under
    test. Instead each event gets a NOMINATED successor or parent CIK, to be verified
    against a filing under the same evidence rules as Stage 3 - and where no unique
    candidate exists, the row is emitted with the candidate blank and the reason
    recorded, rather than an invented target.
    """
    c = lost[lost["category"] == "c_v4_gap"]
    c = c[c["sub_cause"].str.contains("|".join(TOPUPABLE), regex=True)]
    if not len(c):
        return pd.DataFrame()
    names = sorted({str(x) for x in c["org_name"]})
    found = m213.lookup_ciks(set(names)) if hasattr(m213, "lookup_ciks") else {}
    titles = ticker_title_map(m213.norm213) if hasattr(m213, "norm213") else {}
    by_ticker = ticker_cik_map()
    rows = []
    for _, r in c.iterrows():
        org, cik = str(r["org_name"]), int(r["orig_cik"])
        if cik in STAGE3B_DEFERRED:
            continue
        cand, basis = found.get(org, (None, "not looked up"))
        tk = STAGE3B_TICKER.get(cik)
        if tk and tk in by_ticker:
            tcik, ttitle = by_ticker[tk]
            if tcik != cik:
                cand = tcik
                basis = (f"ticker {tk} -> CIK {tcik} ({ttitle!r}) via "
                         f"company_tickers.json, per ruling")
        if cand and int(cand) == cik:
            cand, basis = None, (f"the only same-name filer IS the event CIK "
                                 f"({cik}); no successor identified")
        if not cand and titles:
            # Second source: a unique CURRENT registrant with the same normalised title.
            # `titles` is empty when the caller cannot normalise, so this degrades to
            # "no ticker fallback" rather than failing.
            alt = {x for x in titles.get(tuple(m213.norm213(org)), set()) if x != cik}
            if len(alt) == 1:
                cand = alt.pop()
                basis = (f"company_tickers.json: unique current registrant titled "
                         f"{org!r} ({basis})")
            elif len(alt) > 1:
                basis = (f"{basis}; company_tickers.json also ambiguous "
                         f"({len(alt)} current registrants)")
        ctype = ("a_subsidiary" if "no Compustat gvkey" not in str(r["sub_cause"])
                 else "b_successor_cik")
        rows.append({
            "candidate_type": ctype,
            "cik": cik,
            "org": org,
            "breach_date": r["breach_date"],
            "crsp_permno": "",
            "comnam_at_breach": "",
            "candidate": (f"CIK {int(cand)}" if cand else ""),
            "confidence": "unverified" if cand else "no candidate",
            "shared_tokens": "",
            "generic_only": False,
            "reason": (f"Stage 3b: v4 lost this event ({r['sub_cause']}); "
                       f"nomination basis: {basis}")})
    return pd.DataFrame(rows)


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

    m212 = load_212()
    lost = categorise_lost(ev4, links, read_stocknames(), m212.names_match)
    log("## Documented exclusions")
    log("")
    log("Residual losses that are accounted for by name. None is a candidate for a "
        "further top-up.")
    log("")
    for _name, _why in DOCUMENTED_EXCLUSIONS:
        log(f"- **{_name}** — {_why}")
    log("")
    log("## Documented identifications")
    log("")
    for _name, _why in DOCUMENTED_IDENTIFICATIONS:
        log(f"- **{_name}** — {_why}")
    log("")
    log("## Events linked in v3 but not in v4")
    log("")
    if len(lost):
        counts = (lost.groupby(["category", "group"]).size().unstack(fill_value=0)
                  .reset_index())
        log(md_table(counts))
        log("")
        log(md_table(lost[["category", "org_name", "orig_cik", "final_cik", "breach_date",
                           "group", "v3_permno", "v3_comnam_at_breach", "v4_reason"]]))
        log("")
        log("Sub-causes within each category:")
        log("")
        log(md_table(lost.groupby(["category", "sub_cause"]).size()
                     .reset_index(name="events")))
    else:
        log("None.")
    log("")

    OUT_LEDGER.parent.mkdir(parents=True, exist_ok=True)
    s3b = build_stage3b(lost, m212_for_lookup())
    log("## Stage 3b worklist")
    log("")
    if len(s3b):
        log(f"{len(s3b)} event(s) whose loss a top-up could in principle fix, written to "
            f"`{OUT_S3B.as_posix()}`. v3's permno is deliberately NOT carried over: v3 "
            f"reached it through the CIK->ticker match this rebuild replaces.")
        log("")
        log(md_table(s3b[["candidate_type", "cik", "org", "breach_date", "candidate",
                          "confidence"]]))
    else:
        log("No event's loss is fixable by a top-up.")
    log("")

    for path, df in ((OUT_LEDGER, ledger), (OUT_SYMMETRY, sym), (OUT_LOST, lost),
                     (OUT_S3B, s3b)):
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
