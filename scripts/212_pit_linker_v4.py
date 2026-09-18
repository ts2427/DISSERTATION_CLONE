"""
REBUILD V4 — STAGE 2: POINT-IN-TIME LINKER, CUSIP ROUTE (local files only, no WRDS)
=====================================================================================
Links every CANONICAL_V3 event to a permno valid on its breach_date, identically for
treated and control. No CCM link table is reachable (scripts/216), so:

    final_cik -> gvkey        comp.company.cik, zero-padded 10-char
    gvkey     -> US issues    comp.security where tpci='0' and excntry='USA'
    issue     -> cusip8       comp.security.cusip[:8], uppercased
    cusip8    -> permno       crsp.stocknames, ncusip first, header cusip as fallback,
                              namedt <= breach_date <= nameenddt, shrcd in {10,11}

WHY ALL US COMMON ISSUES, NOT priusa
------------------------------------
`priusa` names the CURRENT primary issue; it is not point-in-time. Sprint is the proof:
priusa=10 -> 85207U10 -> permno 14040, which only exists from 2013-07-12, so every
pre-2013 Sprint event would fail while iid=01 -> 85206110 -> permno 39087
(SPRINT NEXTEL CORP, 2005-08-15..2013-07-10) sat unexamined. Both are permnos v3 used.
So the search covers every US common issue of the gvkey, and priusa is demoted to a
tie-break.

TIE-BREAK, in order:
  1. prefer the issue named by comp.company.priusa
  2. prefer shrcd 11 over 10
  3. prefer the later namedt
Observed: the tie fires on 15 events across 4 dual-class firms (Brown-Forman, Gray
Television, Comcast, Google) and rule 1 resolves every one; rules 2 and 3 are reported
if they ever fire.

IDENTITY GATE (header links only)
---------------------------------
CRSP keeps ONE permno across a reverse merger and back-fills the header `cusip` with
the surviving firm's identifier, changing only `comnam` and `ncusip`. permno 91937 runs
continuously from METROPCS COMMUNICATIONS INC (2007-04-19..2013-04-30) into
T MOBILE U S INC, header cusip 87259010 throughout. All six T-Mobile events before
2013-04-29 match it on the header with shrcd 11 and valid dates. Date validity and
shrcd do NOT catch this.

  cusip_ncusip -> accepted on date validity + shrcd alone.
  cusip_header -> accepted ONLY if the CRSP comnam on the row valid at breach_date
                  matches the PRC org string OR the resolved EDGAR name. Otherwise
                  EXCLUDED, reason: "CRSP name at breach_date does not match the
                  breached organization; parent relationship unverified."
                  The rule decides; there is no manual review queue.

NORMALISATION (deterministic, both sides): uppercase; every character outside A-Z0-9
becomes a space; split; drop legal-suffix and filler tokens (LEGAL_TOKENS).
TOKEN MATCH: let A, B be normalised tokens of length >= 4. If both non-empty, match iff
they intersect. If either is empty, match iff the full normalised sequences are equal.

  "T-Mobile" -> {T, MOBILE}; "METROPCS COMMUNICATIONS INC" -> {METROPCS,
  COMMUNICATIONS}. No overlap -> EXCLUDED, via the gate rather than the date rule.
  "CenturyLink Communications" vs "CENTURYLINK INC" -> {CENTURYLINK} shared -> ACCEPTED,
  correctly, the same firm renamed.

The same names_match is applied to cusip_ncusip links REPORT-ONLY: no ncusip link is
ever excluded on a name mismatch, but every one is listed with its final_evidence,
because a mismatch there means the CUSIP is right and the name is not. A mismatch is
EXPLAINED iff final_evidence carries a Gate 1 or Gate 2 verdict or an EDGAR confirmation
— i.e. the v3 chain already adjudicated the identity. Otherwise the event is written to
stage3_candidates.csv as `ncusip_name_mismatch`: the link stands, but the identity is
unadjudicated and a human should look.

WHAT THE MATCHES REST ON
------------------------
One shared token of length >= 4 accepts a match. That is decisive for CENTURYLINK and
near-worthless for COMMUNICATIONS. So every header accept and every b_successor_cik
nomination logs the token(s) that produced it, and any match resting ONLY on industry
words (GENERIC_TOKENS) is FLAGGED in the report. Flagging changes nothing: the rule is
unchanged and no flagged row is excluded. It exists so the weak matches are visible
before anyone decides whether the rule should tighten.

Reads only Data/wrds_v4/*.csv, CANONICAL_V3, and the COMMITTED nomination copy at
outputs/rebuild_v4/inputs/crsp_drop_nominations.csv. Every input is required: a missing
file aborts, so a clean clone either reproduces this exactly or fails loudly.
Writes only outputs/rebuild_v4/212_*.csv, stage3_candidates.csv, 212_link_report.md.
Touches no v3 path.
"""
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

W = Path("Data/wrds_v4")
OUT = Path("outputs/rebuild_v4")
CANON = Path("Data/processed/rebuild/CANONICAL_V3.csv")
# The committed copy, not outputs/essay3_q2/. The essay3_q2 original stays untracked, so
# a clean clone could not reproduce the no-gvkey classification from it. Missing ABORTS.
NOMS = Path("outputs/rebuild_v4/inputs/crsp_drop_nominations.csv")

TMOBILE_CIK, TMOBILE_CUTOFF = 1283699, pd.Timestamp("2013-04-29")
SPRINT_CIK, SPRINT_CUTOFF = 101830, pd.Timestamp("2013-07-12")
SPRINT_V3_PERMNOS = {14040, 39087}
SHRCD_OK = {10, 11}
GATE_REASON = ("CRSP name at breach_date does not match the breached organization; "
               "parent relationship unverified")

LEGAL_TOKENS = {
    "INC", "INCORPORATED", "CORP", "CORPORATION", "CO", "COS", "COMPANY", "COMPANIES",
    "LLC", "LLP", "LP", "LTD", "LIMITED", "PLC", "SA", "NV", "AG", "AB", "AS",
    "HOLDING", "HOLDINGS", "GROUP", "GRP", "THE", "NEW", "CL", "CLASS", "TRUST",
    "PARTNERS", "PARTNERSHIP", "ENTERPRISES", "INTL",
}
SIGNIFICANT_LEN = 4

# Tokens that are common industry words rather than firm identity. A match resting
# ONLY on these is weak evidence: "X Communications" and "Y Communications" share a
# token without being the same company. Flagged for review, NOT excluded - the rule is
# unchanged until Tim rules on the flagged list.
GENERIC_TOKENS = {
    "COMMUNICATIONS", "COMMUNICATION", "SYSTEMS", "INTERNATIONAL", "AMERICAN",
    "AMERICA", "FINANCIAL", "SERVICES", "SERVICE", "TECHNOLOGIES", "TECHNOLOGY",
    "HEALTH", "HEALTHCARE", "BANK", "BANKS", "NATIONAL", "GLOBAL", "INDUSTRIES",
    "SOLUTIONS", "NETWORKS", "MEDIA", "ENERGY", "GENERAL", "UNITED", "FIRST",
}

# A name mismatch is EXPLAINED iff the v3 chain already adjudicated the identity: any
# Gate 1 or Gate 2 verdict, or an EDGAR confirmation. The previous keyword list
# ("parent", "subsidiary", "merger") was a bad proxy - it recognised Gate2 wording but
# missed Gate1-B/E/G rescues that are equally adjudicated, so it reported 34 unexplained
# mismatches when almost none were.
GATE_RE = re.compile(r"GATE\s*-?\s*[12]\b")

LOG = []


def log(m=""):
    print(m, flush=True)
    LOG.append(str(m))


def md(df, floatfmt=None):
    df = df.reset_index() if df.index.name or isinstance(df.index, pd.MultiIndex) else df
    cols = [str(c) for c in df.columns]
    out = ["| " + " | ".join(cols) + " |", "|" + "|".join("---" for _ in cols) + "|"]
    for _, r in df.iterrows():
        out.append("| " + " | ".join("" if pd.isna(v) else str(v) for v in r) + " |")
    return "\n".join(out)


def join_initial_runs(toks):
    """A T T -> ATT; E M C -> EMC; SIRIUS X M RADIO -> SIRIUS XM RADIO.

    CRSP writes initialisms letter-spaced ("A T & T INC", "E M C CORP MA") while the PRC
    org string does not ("AT&T", "EMC Corporation"). Without this, every such pair
    tokenises to single letters, no token reaches SIGNIFICANT_LEN, and the comparison
    falls through to exact-sequence equality and fails on a firm matching itself.
    """
    out, run = [], []
    for t in toks:
        if len(t) == 1:
            run.append(t)
            continue
        if run:
            out.append("".join(run))
            run = []
        out.append(t)
    if run:
        out.append("".join(run))
    return out


def norm_tokens(name):
    if name is None or (isinstance(name, float) and pd.isna(name)):
        return []
    s = "".join(ch if ch.isalnum() else " " for ch in str(name).upper())
    return join_initial_runs([t for t in s.split() if t and t not in LEGAL_TOKENS])


def name_overlap(a, b):
    """-> (matched, shared_tokens). Same rule as names_match, but shows its working.

    1. significant tokens (len >= 4) on both sides that intersect
    2. else equal space-stripped concatenations ("TimeWarner" vs "TIME WARNER INC NEW",
       "AT&T" -> AT|T vs "A T & T INC" -> ATT; both concatenate to ATT)
    3. else, when either side has no significant token, exact sequence equality
    """
    ta, tb = norm_tokens(a), norm_tokens(b)
    sa = {t for t in ta if len(t) >= SIGNIFICANT_LEN}
    sb = {t for t in tb if len(t) >= SIGNIFICANT_LEN}
    if sa and sb:
        shared = sa & sb
        if shared:
            return True, shared
    ca, cb = "".join(ta), "".join(tb)
    if ca and ca == cb:
        return True, {ca}
    if sa and sb:
        return False, set()
    eq = (ta == tb) and bool(ta)
    return eq, set(ta) if eq else set()


def names_match(a, b):
    return name_overlap(a, b)[0]


def best_overlap(comnam, org, edgar):
    """Try the org string, then the EDGAR name. -> (matched, shared, which_side)."""
    ok, sh = name_overlap(comnam, org)
    if ok:
        return True, sh, "org"
    ok, sh = name_overlap(comnam, edgar)
    if ok:
        return True, sh, "edgar"
    return False, set(), ""


def generic_only(shared):
    """True when a match rests entirely on industry words."""
    return bool(shared) and set(shared) <= GENERIC_TOKENS


def documented_identity(evidence):
    """True iff final_evidence carries a Gate 1 / Gate 2 verdict or an EDGAR confirmation.

    That is the whole test. An identity the v3 chain adjudicated is explained, however it
    worded the verdict; anything else is a Stage 3 candidate regardless of how plausible
    the relationship looks to a reader.
    """
    e = str(evidence).upper()
    return bool(GATE_RE.search(e)) or "EDGAR" in e


def main():
    missing = [str(p) for p in (CANON, NOMS,
                                W / "comp_company.csv", W / "comp_security.csv",
                                W / "crsp_stocknames.csv") if not p.exists()]
    if missing:
        sys.exit("missing input file(s); refusing to run with partial inputs:\n  "
                 + "\n  ".join(missing))

    ev = pd.read_csv(CANON, low_memory=False)
    ev["bdt"] = pd.to_datetime(ev["breach_date"], errors="coerce")
    ev["grp"] = ev["fcc_form499"].map({1: "treated", 0: "control"})
    ev["edgar"] = ev["final_evidence"].astype(str).str.extract(
        r"EDGAR name:\s*(.+?)(?:\s*\||$)")[0]

    comp = pd.read_csv(W / "comp_company.csv", low_memory=False)
    sec = pd.read_csv(W / "comp_security.csv", low_memory=False)
    nam = pd.read_csv(W / "crsp_stocknames.csv", low_memory=False)

    nz = lambda s: s.astype(str).str.strip().str.upper().str.lstrip("0").replace("", "0")
    comp["cik_int"] = pd.to_numeric(comp["cik"], errors="coerce")
    comp["pn"] = nz(comp["priusa"])
    sec["iid_n"] = nz(sec["iid"])
    sec["cusip8"] = sec["cusip"].astype(str).str.strip().str.upper().str[:8]
    for c in ("ncusip", "cusip"):
        nam[c] = nam[c].astype(str).str.strip().str.upper()
    nam["namedt"] = pd.to_datetime(nam["namedt"], errors="coerce")
    nam["nameenddt"] = pd.to_datetime(nam["nameenddt"], errors="coerce")

    cik2gv = comp.dropna(subset=["cik_int"]).set_index("cik_int")["gvkey"].to_dict()
    usc = sec[(sec["tpci"].astype(str) == "0") & (sec["excntry"] == "USA")]
    gv2us = usc.groupby("gvkey")["cusip8"].apply(lambda s: sorted(set(s))).to_dict()
    gv2pri = (sec.merge(comp[["gvkey", "pn"]], on="gvkey", how="left")
              .pipe(lambda d: d[d["iid_n"] == d["pn"]])
              .groupby("gvkey")["cusip8"].apply(lambda s: set(s)).to_dict())

    tie_counts = {"priusa": 0, "shrcd": 0, "namedt": 0}

    def pick(cand, gv):
        """Tie-break: priusa issue, then shrcd 11>10, then later namedt."""
        if len(cand) == 1:
            return cand.iloc[0], None
        pri = gv2pri.get(gv, set())
        c = cand.copy()
        c["_pri"] = (~(c["ncusip"].isin(pri) | c["cusip"].isin(pri))).astype(int)
        if c["_pri"].nunique() > 1:
            tie_counts["priusa"] += 1
            c = c[c["_pri"] == 0]
            if c["permno"].nunique() == 1:
                return c.iloc[0], "priusa"
        c = c.assign(_s=c["shrcd"].map({11: 0, 10: 1}).fillna(9))
        if c["_s"].nunique() > 1:
            tie_counts["shrcd"] += 1
            c = c[c["_s"] == c["_s"].min()]
            if c["permno"].nunique() == 1:
                return c.iloc[0], "shrcd"
        tie_counts["namedt"] += 1
        return c.sort_values("namedt", ascending=False).iloc[0], "namedt"

    def resolve(e):
        cik = e["final_cik"]
        gv = cik2gv.get(cik)
        if gv is None:
            return dict(note="no gvkey")
        cus = gv2us.get(gv, [])
        if not cus:
            return dict(gvkey=gv, note="no US common issue")
        b = e["bdt"]
        dated = nam[(nam["namedt"] <= b) & (b <= nam["nameenddt"])]
        # --- ncusip pass (no gate) ---
        c = dated[dated["ncusip"].isin(cus)]
        c_ok = c[c["shrcd"].isin(SHRCD_OK)]
        if len(c_ok):
            r, tb = pick(c_ok, gv)
            nm_ok, shared, side = best_overlap(r["comnam"], e["org_name"], e["edgar"])
            return dict(gvkey=gv, permno=int(r["permno"]), cusip8=r["ncusip"],
                        link_source="cusip_ncusip", comnam=r["comnam"],
                        shrcd=int(r["shrcd"]), namedt=r["namedt"], nameenddt=r["nameenddt"],
                        tie_break=tb, name_ok=nm_ok, shared_tokens="|".join(sorted(shared)),
                        matched_against=side, generic_only=generic_only(shared),
                        n_valid=c_ok["permno"].nunique(), note="")
        # --- header pass (gate applies) ---
        h = dated[dated["cusip"].isin(cus)]
        h_ok = h[h["shrcd"].isin(SHRCD_OK)]
        if len(h_ok):
            r, tb = pick(h_ok, gv)
            nm_ok, shared, side = best_overlap(r["comnam"], e["org_name"], e["edgar"])
            base = dict(gvkey=gv, cusip8=r["cusip"], comnam=r["comnam"],
                        shrcd=int(r["shrcd"]), namedt=r["namedt"], nameenddt=r["nameenddt"],
                        tie_break=tb, name_ok=nm_ok, ncusip_on_row=r["ncusip"],
                        shared_tokens="|".join(sorted(shared)), matched_against=side,
                        generic_only=generic_only(shared))
            if nm_ok:
                return {**base, "permno": int(r["permno"]), "link_source": "cusip_header",
                        "note": ""}
            return {**base, "permno_rejected": int(r["permno"]), "gate_excluded": True,
                    "note": GATE_REASON}
        if len(c) or len(h):
            bad = sorted(set(pd.concat([c, h])["shrcd"].dropna().astype(int)))
            return dict(gvkey=gv, note=f"shrcd not in {{10,11}} ({bad})")
        return dict(gvkey=gv, note="no names row valid on breach_date")

    rows = []
    for _, e in ev.iterrows():
        rows.append({**dict(final_cik=e["final_cik"], org_name=e["org_name"],
                            edgar=e["edgar"], final_evidence=e["final_evidence"],
                            breach_date=e["breach_date"],
                            grp=e["grp"], v3_permno=e["permno"]), **resolve(e)})
    L = pd.DataFrame(rows)
    for col in ("permno", "gate_excluded", "name_ok", "permno_rejected", "link_source",
                "tie_break", "comnam", "note", "shared_tokens", "matched_against",
                "generic_only"):
        if col not in L.columns:
            L[col] = pd.NA
    L["v4_linked"] = L["permno"].notna()
    L["v3_linked"] = L["v3_permno"].notna()

    log("# REBUILD V4 — Stage 2 point-in-time linker (CUSIP route)")
    log("")
    log(f"- run (UTC): {datetime.now(timezone.utc).isoformat(timespec='seconds')}")
    log(f"- events {len(ev)} | comp.company {len(comp)} | comp.security {len(sec)} "
        f"| stocknames {len(nam)}")
    log(f"- rule: all US common issues (tpci=0, excntry=USA), ncusip-first, header "
        f"fallback behind the identity gate")
    log("")

    # ---------- regressions ----------
    log("## Regression tests")
    log("")
    tm = L[(L["final_cik"] == TMOBILE_CIK) & (pd.to_datetime(L["breach_date"]) < TMOBILE_CUTOFF)]
    tm_link = int(tm["v4_linked"].sum())
    tm_gate = int(tm["gate_excluded"].eq(True).sum())
    TM_PASS = tm_link == 0 and tm_gate == len(tm)
    log(f"**T-Mobile before 2013-04-29** — {len(tm)} events, linked {tm_link} (must be 0), "
        f"excluded by the gate {tm_gate}. **{'PASS' if TM_PASS else 'FAIL'}**")
    log("")
    log(md(tm[["breach_date", "comnam", "permno_rejected", "note"]]))
    log("")
    sp = L[L["final_cik"] == SPRINT_CIK].copy()
    sp["pre"] = pd.to_datetime(sp["breach_date"]) < SPRINT_CUTOFF
    sp_pre = sp[sp["pre"]]
    got = set(sp_pre["permno"].dropna().astype(int))
    SP_PASS = bool(got) and got <= SPRINT_V3_PERMNOS
    log(f"**Sprint pre-2013** — {len(sp_pre)} events, permnos reached {sorted(got)}, "
        f"v3 used {sorted(SPRINT_V3_PERMNOS)}. **{'PASS' if SP_PASS else 'FAIL'}**")
    log("")
    log(md(sp[["breach_date", "permno", "v3_permno", "link_source", "comnam"]]))
    log("")

    # ---------- reach ----------
    log("## Linked events, v3 vs v4")
    log("")
    t = pd.DataFrame([{"group": g,
                       "events": int((L["grp"] == g).sum()),
                       "v3 linked": int(L.loc[L["grp"] == g, "v3_linked"].sum()),
                       "v4 linked": int(L.loc[L["grp"] == g, "v4_linked"].sum())}
                      for g in ("treated", "control")])
    t["delta"] = t["v4 linked"] - t["v3 linked"]
    t.loc[len(t)] = ["ALL", len(L), int(L["v3_linked"].sum()), int(L["v4_linked"].sum()),
                     int(L["v4_linked"].sum()) - int(L["v3_linked"].sum())]
    log(md(t))
    log("")
    log("link_source:")
    log("")
    log(md(pd.crosstab(L["link_source"].fillna("(unlinked)"), L["grp"]).reset_index()))
    log("")
    log(f"Tie-break usage: {tie_counts} (priusa resolves the dual-class pairs; the "
        f"shrcd and namedt rules are reported if they ever fire).")
    log("")

    # ---------- every unlinked event by reason ----------
    log("## Every unlinked event, by reason")
    log("")
    un = L[~L["v4_linked"]].copy()
    un["reason"] = un["note"].fillna("(unknown)")
    log(md(pd.crosstab(un["reason"], un["grp"], margins=True).reset_index()))
    log("")

    # ---------- identity gate ----------
    log("## Identity gate (header links only)")
    log("")
    hdr = L[L["link_source"] == "cusip_header"]
    exc = L[L["gate_excluded"].eq(True)]
    log(md(pd.DataFrame([{"outcome": "accepted", "treated": int((hdr["grp"] == "treated").sum()),
                          "control": int((hdr["grp"] == "control").sum()), "total": len(hdr)},
                         {"outcome": "excluded", "treated": int((exc["grp"] == "treated").sum()),
                          "control": int((exc["grp"] == "control").sum()), "total": len(exc)}])))
    log("")
    log("### Every header accept, for audit of the normalisation")
    log("")
    log(md(hdr[["final_cik", "org_name", "comnam", "breach_date", "permno"]]
          .drop_duplicates(["final_cik", "comnam"])))
    log("")
    log("### Every gate exclusion")
    log("")
    log(md(exc[["final_cik", "org_name", "comnam", "breach_date", "permno_rejected"]]))
    log("")

    # ---------- report-only name check on ncusip links ----------
    log("## Report-only: ncusip links whose CRSP name matches neither org nor EDGAR")
    log("")
    nc_bad = L[(L["link_source"] == "cusip_ncusip") & (L["name_ok"] == False)]
    log(f"{len(nc_bad)} of {int((L['link_source']=='cusip_ncusip').sum())} ncusip links. "
        f"**None is excluded** — the CUSIP is authoritative here; a name mismatch means "
        f"the name differs, not that the security is wrong.")
    log("")
    nc_bad = nc_bad.copy()
    nc_bad["documented"] = nc_bad["final_evidence"].apply(documented_identity)
    if len(nc_bad):
        log(md(nc_bad[["final_cik", "org_name", "comnam", "permno", "documented",
                       "final_evidence"]].drop_duplicates(["final_cik", "comnam"])))
    log("")
    nc_s3 = nc_bad[~nc_bad["documented"]]
    log(f"**{int(nc_bad['documented'].sum())}** of the {len(nc_bad)} carry a Gate 1 or "
        f"Gate 2 verdict or an EDGAR confirmation in `final_evidence`: the v3 chain already "
        f"adjudicated the identity, so the differing name is explained. The remaining "
        f"**{len(nc_s3)}** carry neither and go to `stage3_candidates.csv` as "
        f"`ncusip_name_mismatch` — the link stands, but the identity is unadjudicated.")
    log("")
    # The table above is de-duplicated on (final_cik, comnam) to keep it readable, which
    # can HIDE an unadjudicated row behind an adjudicated one sharing the same CIK and
    # CRSP name. The Stage 3 rows are therefore listed in full, no de-duplication.
    if len(nc_s3):
        log(f"### The {len(nc_s3)} unadjudicated mismatch(es), in full")
        log("")
        log(md(nc_s3[["final_cik", "org_name", "comnam", "breach_date", "permno",
                      "final_evidence"]]))
        log("")

    # ---------- v3 agreement ----------
    log("## Agreement with v3")
    log("")
    both = L[L["v3_linked"] & L["v4_linked"]].copy()
    both["agree"] = both["v3_permno"].astype(float) == both["permno"].astype(float)
    a = pd.DataFrame([{"group": g,
                       "v3 linked": int(L.loc[(L["grp"] == g), "v3_linked"].sum()),
                       "both": int((both["grp"] == g).sum()),
                       "same permno": int(both.loc[both["grp"] == g, "agree"].sum()),
                       "different": int((~both.loc[both["grp"] == g, "agree"]).sum())}
                      for g in ("treated", "control")])
    log(md(a))
    log("")
    dis = both[~both["agree"]]
    log(f"### Every disagreement ({len(dis)})")
    log("")
    log(md(dis[["final_cik", "org_name", "breach_date", "v3_permno", "permno", "comnam",
                "link_source"]]) if len(dis) else "None.")
    log("")
    lost = L[L["v3_linked"] & ~L["v4_linked"]]
    gained = L[~L["v3_linked"] & L["v4_linked"]]
    log(f"- v3 linked, v4 not: **{len(lost)}** (treated {int((lost['grp']=='treated').sum())}, "
        f"control {int((lost['grp']=='control').sum())})")
    log(f"- v4 linked, v3 not: **{len(gained)}** (treated {int((gained['grp']=='treated').sum())}, "
        f"control {int((gained['grp']=='control').sum())})")
    log("")
    if len(lost):
        log(md(lost["note"].value_counts().rename_axis("reason").reset_index(name="events")))
        log("")

    # ---------- classify the no-gvkey CIKs ----------
    log("## CIKs with no gvkey, classified")
    log("")
    nog = L[L["note"] == "no gvkey"].groupby("final_cik").agg(
        org=("org_name", "first"), edgar=("edgar", "first"),
        events=("org_name", "size"), grp=("grp", "first")).reset_index()
    nomap = {}
    nm = pd.read_csv(NOMS)
    for _, r in nm.dropna(subset=["cik"]).iterrows():
        nomap.setdefault(int(r["cik"]), (r.get("parent"), str(r.get("basis", ""))))
    conm = comp[["gvkey", "cik_int", "conm"]].dropna(subset=["conm"])

    GENERIC_NOTE = "nomination rested only on an industry word"

    def classify(cik, org, edgar):
        par, basis = nomap.get(int(cik), (None, ""))
        if par and basis.startswith("name knowledge"):
            return "a_subsidiary", par, "", "", False, ""
        for _, cr in conm.iterrows():
            ok, shared, _ = best_overlap(cr["conm"], org, edgar)
            if ok and cr["cik_int"] != cik:
                cand = f"{cr['conm']} (gvkey {cr['gvkey']}, cik {int(cr['cik_int'])})"
                toks = "|".join(sorted(shared))
                if generic_only(shared):
                    # A shared industry word is not evidence of succession. The match is
                    # recorded in the note and the CIK falls through to c_no_compustat;
                    # it is NOT nominated and does NOT reach stage3_candidates.csv.
                    return ("c_no_compustat", "", "", toks, True,
                            f"{GENERIC_NOTE}: rejected {cand} on {toks}")
                return "b_successor_cik", cand, "unverified", toks, False, ""
        if par and basis.startswith("self"):
            return "c_no_compustat", par, "", "", False, ""
        return (("c_no_compustat", "", "", "", False, "") if not par
                else ("d_other", par, "", "", False, ""))

    nog[["candidate_type", "candidate", "confidence", "shared_tokens", "generic_only",
         "note"]] = nog.apply(
        lambda r: pd.Series(classify(r["final_cik"], r["org"], r["edgar"])), axis=1)
    log(md(nog["candidate_type"].value_counts().rename_axis("type").reset_index(name="CIKs")))
    log("")
    log(md(nog[["final_cik", "org", "grp", "events", "candidate_type", "candidate",
                "confidence", "shared_tokens"]]))
    log("")

    # ---------- what the token matches actually rest on ----------
    log("## Shared tokens behind every name match (header accepts + successor nominations)")
    log("")
    log("The rule accepts a match on ONE shared token of length >= 4. That is fine for "
        "`CENTURYLINK` and worthless for `COMMUNICATIONS`. Every match is listed with the "
        "token(s) that produced it; a match resting ONLY on industry words is flagged. "
        "**The rule is unchanged** — nothing below is excluded on this basis.")
    log("")
    ha = hdr[["final_cik", "org_name", "comnam", "shared_tokens", "matched_against",
              "generic_only"]].drop_duplicates(["final_cik", "comnam"])
    log("### Header accepts")
    log("")
    log(md(ha))
    log("")
    bn = nog[nog["candidate_type"] == "b_successor_cik"][
        ["final_cik", "org", "candidate", "shared_tokens"]]
    log("### b_successor_cik nominations that survive")
    log("")
    log(md(bn) if len(bn) else "None.")
    log("")
    rc = nog[nog["generic_only"].eq(True)][
        ["final_cik", "org", "grp", "events", "candidate_type", "shared_tokens", "note"]]
    log(f"### Reclassified to c_no_compustat — {GENERIC_NOTE} ({len(rc)})")
    log("")
    log("These are not nominations and do NOT reach `stage3_candidates.csv`. The rejected "
        "candidate is kept in `note` so the decision is auditable.")
    log("")
    log(md(rc) if len(rc) else "None.")
    log("")
    flag_h = ha[ha["generic_only"].eq(True)]
    log(f"### Header accepts resting on generic tokens only — {len(flag_h)}")
    log("")
    log(md(flag_h) if len(flag_h)
        else "None: every header accept shares a real identity token.")
    log("")

    # ---------- unmatched common-USA CUSIPs ----------
    log("## Unmatched tpci=0 / USA CUSIPs")
    log("")
    matched = set(nam["ncusip"]) | set(nam["cusip"])
    um = usc[~usc["cusip8"].isin(matched)].merge(comp[["gvkey", "conm"]], on="gvkey", how="left")
    log(f"{len(um)} US common issues have no CRSP names row.")
    log("")
    log(md(um[["gvkey", "conm", "cusip8", "exchg", "secstat"]].sort_values("conm")))
    log("")

    # ---------- stage 3 candidates ----------
    s3 = []
    for _, r in exc.iterrows():
        s3.append(dict(candidate_type="gate_exclusion", cik=r["final_cik"], org=r["org_name"],
                       breach_date=r["breach_date"], crsp_permno=r["permno_rejected"],
                       comnam_at_breach=r["comnam"], candidate="", confidence="",
                       reason=GATE_REASON))
    for _, r in nog[nog["candidate_type"].isin(["a_subsidiary", "b_successor_cik"])].iterrows():
        s3.append(dict(candidate_type=r["candidate_type"], cik=r["final_cik"], org=r["org"],
                       breach_date="", crsp_permno="", comnam_at_breach="",
                       candidate=r["candidate"], confidence=r["confidence"],
                       shared_tokens=r["shared_tokens"], generic_only=r["generic_only"],
                       reason="no gvkey in Compustat for this CIK"))
    for _, r in nc_s3.iterrows():
        s3.append(dict(candidate_type="ncusip_name_mismatch", cik=r["final_cik"],
                       org=r["org_name"], breach_date=r["breach_date"],
                       crsp_permno=r["permno"], comnam_at_breach=r["comnam"],
                       candidate="", confidence="", shared_tokens="", generic_only=False,
                       reason="ncusip link accepted; CRSP name matches neither the org "
                              "string nor the EDGAR name, and final_evidence carries no "
                              "Gate 1 / Gate 2 verdict and no EDGAR confirmation"))
    S3 = pd.DataFrame(s3)
    log("## Stage 3 candidates")
    log("")
    log(f"{len(S3)} rows written to `outputs/rebuild_v4/stage3_candidates.csv`.")
    log("")
    if len(S3):
        log(md(S3["candidate_type"].value_counts().rename_axis("type").reset_index(name="rows")))
    log("")

    OUT.mkdir(parents=True, exist_ok=True)
    L.to_csv(OUT / "212_links.csv", index=False)
    dis.to_csv(OUT / "212_v3_disagreements.csv", index=False)
    exc[["final_cik", "org_name", "edgar", "comnam", "cusip8", "ncusip_on_row",
         "breach_date", "namedt", "nameenddt", "permno_rejected", "note"]].to_csv(
        OUT / "212_identity_review.csv", index=False)
    nog.to_csv(OUT / "212_no_gvkey.csv", index=False)
    um.to_csv(OUT / "212_unmatched_cusips.csv", index=False)
    S3.to_csv(OUT / "stage3_candidates.csv", index=False)
    (OUT / "212_link_report.md").write_text("\n".join(LOG) + "\n", encoding="utf-8")
    print(f"\nWROTE {OUT/'212_link_report.md'} + 6 CSVs")
    return 0 if (TM_PASS and SP_PASS) else 1


if __name__ == "__main__":
    sys.exit(main())
