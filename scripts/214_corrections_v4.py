"""
REBUILD V4 — STAGE 4: RECORD-LEVEL CORRECTIONS (offline; writes only to v4 paths)
=====================================================================================
Applies the corrections Stage 3 produced evidence for, and NOTHING else. Every
correction carries its old value, its new value, and verbatim evidence; anything that
cannot be evidenced is reported and left alone.

    python scripts/214_corrections_v4.py

READS   Data/processed/rebuild/CANONICAL_V3.csv (read-only), the retired upstream
        datasets named in SOURCES, and the Stage 3 EDGAR cache.
WRITES  Data/processed/rebuild_v4/CANONICAL_V4.csv
        outputs/rebuild_v4/214_corrections.csv
        outputs/rebuild_v4/214_corrections.md
Every output path is asserted to be under a v4 prefix before anything is written. v3 is
never touched; the prime directive is that v3 does not change.

THE FOUR CORRECTIONS
--------------------
1. Sprint Nextel (CIK 101830), breach_date 2012-08-01. The record's own fields put the
   event three years earlier: reported_date 2009-03-30, end_breach_date 2009-01-01, and
   incident_details says the New Hampshire DOJ reported it on March 30, 2009 with the
   breach occurring between December 2008 and January 2009. 2012-08-01 is supported by
   nothing in the record. Corrected to the record's own end_breach_date.

   prior_breaches_1yr is recomputed for CIK 101830 only, and ONLY after the recomputation
   is shown to reproduce the stored column exactly under the OLD dates. If it does not,
   the rule differs from v3's and the script aborts rather than write a column computed a
   different way.

2. Malformed reported_date. A truncated "2020-03" is repaired from the upstream record
   that survives in the retired datasets, matched on org_name AND breach_date - there is
   a sibling Carnival record at 2019-04-11 whose reported_date is 2020-03-02, so matching
   on the name alone would take the wrong row. No unique full date -> set missing.

3. International Paper. The assigned CIK 1283246 last filed on 2013-02-01, a decade
   before the 2023-05-30 breach, and filed nothing within two years of it. Exactly one
   other filer normalises to the same name and is active across the window: 51434.

4. Lennar. Applied ONLY if the candidate CIK filed the 10-K covering the breach fiscal
   year and the assigned CIK did not. The condition is re-tested here against the cached
   submissions rather than assumed, and both sides are cited.

REPORT-ONLY, NO CHANGE
----------------------
Dell Inc., Warn Industries and Uber are reported with their evidence and left untouched;
see the generated report.
"""
import importlib.util
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

CANON_V3 = Path("Data/processed/rebuild/CANONICAL_V3.csv")
OUT_DATA = Path("Data/processed/rebuild_v4/CANONICAL_V4.csv")
OUT_CSV = Path("outputs/rebuild_v4/214_corrections.csv")
OUT_MD = Path("outputs/rebuild_v4/214_corrections.md")
V4_PREFIXES = ("Data/processed/rebuild_v4/", "outputs/rebuild_v4/")

# Retired upstream datasets, searched for a record that still carries a full date.
SOURCES = (
    Path("Data/processed/FINAL_DISSERTATION_DATASET_DEDUPLICATED.csv"),
    Path("Data/processed/FINAL_DATASET_ORIGINAL_1054_MISNAMED_RETIRED.csv"),
)

FULL_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}")
SPRINT_CIK, SPRINT_BAD_DATE = 101830, "2012-08-01"
INTL_PAPER_OLD, INTL_PAPER_NEW = 1283246, 51434
LENNAR_OLD, LENNAR_NEW = 58696, 920760
FY_WINDOW_DAYS = 400

LOG = []


def log(m=""):
    print(m, flush=True)
    LOG.append(str(m))


def assert_v4(*paths):
    for p in paths:
        s = Path(p).as_posix()
        if not s.startswith(V4_PREFIXES):
            sys.exit(f"refusing to write outside a v4 path: {s}")


def load_m213():
    """scripts/213 with fetch forced to CACHE ONLY - Stage 4 issues no SEC request."""
    p = Path("scripts/213_stage3_verify.py")
    if not p.exists():
        return None
    spec = importlib.util.spec_from_file_location("m213_for_214", str(p))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)

    def cache_only(url):
        c = m.cache_path(url)
        return c.read_bytes() if c.exists() else None

    m.fetch = cache_only
    return m


def record(rows, kind, cik, org, breach_date, field, old, new, applied, evidence):
    rows.append(dict(kind=kind, cik=cik, org_name=org, breach_date=breach_date,
                     field=field, old_value=old, new_value=new,
                     applied="YES" if applied else "NO", evidence=evidence))


# ------------------------------------------------------------------ prior_breaches_1yr
def prior_1yr(dates):
    """Count of this CIK's earlier breaches within 365 days. -> list aligned to `dates`."""
    d = list(dates)
    return [sum(1 for y in d if y < x and (x - y).days <= 365) for x in d]


def fix_sprint(ev, rows):
    sel = (ev["final_cik"] == SPRINT_CIK) & (ev["breach_date"].astype(str) == SPRINT_BAD_DATE)
    if not sel.any():
        log("- Sprint: no row at the recorded bad date; nothing to correct.")
        return ev, None
    r = ev.loc[sel].iloc[0]
    new_date = pd.to_datetime(r["end_breach_date"], errors="coerce")
    if pd.isna(new_date):
        log("- Sprint: end_breach_date is unusable; correction NOT applied.")
        record(rows, "breach_date", SPRINT_CIK, r["org_name"], SPRINT_BAD_DATE,
               "breach_date", SPRINT_BAD_DATE, "", False,
               "end_breach_date missing or unparseable")
        return ev, None
    detail = str(r.get("incident_details", ""))[:240]
    evid = (f'reported_date={r["reported_date"]}; end_breach_date={r["end_breach_date"]}; '
            f'incident_details="{detail}"')

    s = ev[ev["final_cik"] == SPRINT_CIK].copy()
    s["bd_old"] = pd.to_datetime(s["breach_date"], errors="coerce")
    s = s.sort_values("bd_old")
    check = prior_1yr(list(s["bd_old"]))
    stored = [int(x) for x in s["prior_breaches_1yr"]]
    if check != stored:
        sys.exit("prior_breaches_1yr recomputation does not reproduce the stored column "
                 f"for CIK {SPRINT_CIK} under the ORIGINAL dates "
                 f"(recomputed {check} vs stored {stored}). The rule differs from v3's; "
                 "refusing to rewrite the column.")
    log(f"- Sprint: recomputation reproduces the stored prior_breaches_1yr exactly "
        f"({len(stored)} rows) under the original dates, so the rule matches v3's.")

    new_str = new_date.strftime("%Y-%m-%d")
    ev.loc[sel, "breach_date"] = new_str
    record(rows, "breach_date", SPRINT_CIK, r["org_name"], SPRINT_BAD_DATE,
           "breach_date", SPRINT_BAD_DATE, new_str, True, evid)

    # Keep the stored values keyed by ROW, not by position. The old frame is sorted by the
    # old dates and the new frame by the new ones, and those orders differ as soon as a
    # date moves - pairing them positionally silently attributes one event's old count to
    # another event.
    stored_by_idx = dict(zip(s.index, stored))

    s2 = ev[ev["final_cik"] == SPRINT_CIK].copy()
    s2["bd_new"] = pd.to_datetime(s2["breach_date"], errors="coerce")
    s2 = s2.sort_values("bd_new")
    newvals = prior_1yr(list(s2["bd_new"]))
    ev.loc[s2.index, "prior_breaches_1yr"] = newvals
    oldvals = [stored_by_idx[i] for i in s2.index]
    table = pd.DataFrame({"breach_date": [str(d)[:10] for d in s2["bd_new"]],
                          "prior_breaches_1yr_old": oldvals,
                          "prior_breaches_1yr_new": newvals})
    for bd_s, o, n in zip(table["breach_date"], oldvals, newvals):
        if o != n:
            record(rows, "prior_breaches_1yr", SPRINT_CIK, "Sprint", bd_s,
                   "prior_breaches_1yr", o, n, True,
                   f"mechanical consequence of breach_date {SPRINT_BAD_DATE} -> {new_str}")
    return ev, table


def fix_reported_dates(ev, rows):
    bad = ev[~ev["reported_date"].astype(str).str.match(FULL_DATE_RE.pattern, na=False)]
    if bad.empty:
        log("- reported_date: no malformed values.")
        return ev
    srcs = [(p, pd.read_csv(p, low_memory=False)) for p in SOURCES if p.exists()]
    for idx, r in bad.iterrows():
        old = str(r["reported_date"])
        found, srow, evid = None, None, "no upstream record matched on org_name AND breach_date"
        for path, d in srcs:
            if not {"org_name", "breach_date", "reported_date"} <= set(d.columns):
                continue
            hit = d[(d["org_name"].astype(str).str.strip().str.lower()
                     == str(r["org_name"]).strip().lower())
                    & (d["breach_date"].astype(str).str[:10]
                       == str(r["breach_date"])[:10])]
            vals = {str(v)[:10] for v in hit["reported_date"]
                    if FULL_DATE_RE.match(str(v))}
            if len(vals) == 1:
                found = vals.pop()
                srow = hit.iloc[0]
                evid = (f"{path.as_posix()}: org_name={r['org_name']!r}, "
                        f"breach_date={str(r['breach_date'])[:10]}, "
                        f"reported_date={found!r}")
                break
            if len(vals) > 1:
                evid = f"{path.as_posix()}: ambiguous upstream dates {sorted(vals)}"

        if found and day_is_imputed(old, found, srow):
            trunc = [f"{c}={str(srow[c]).strip()!r}" for c in TRUNC_CHECK_COLS
                     if c in srow.index and MONTH_ONLY_RE.fullmatch(str(srow[c]).strip())]
            detail = str(srow.get("incident_details", ""))[:200]
            ev.loc[idx, "reported_date"] = pd.NA
            record(rows, "reported_date_excluded", r["final_cik"], r["org_name"],
                   str(r["breach_date"])[:10], "reported_date", old, "(missing)", True,
                   f"upstream day NOT reported, imputed: {evid}; the same upstream row is "
                   f"still month-truncated at {', '.join(trunc)}, so the record carries "
                   f"month precision and the '-01' was supplied by the pipeline; "
                   f'incident_details="{detail}"')
            continue

        ev.loc[idx, "reported_date"] = found if found else pd.NA
        record(rows, "reported_date", r["final_cik"], r["org_name"],
               str(r["breach_date"])[:10], "reported_date", old,
               found if found else "(missing)", True, evid)
    return ev


MONTH_ONLY_RE = re.compile(r"\d{4}-\d{2}")
TRUNC_CHECK_COLS = ("end_breach_date", "breach_date", "reported_date")


def day_is_imputed(malformed, candidate, srow):
    """Was the upstream day REPORTED, or manufactured from a month-precision record?

    An upstream value that is exactly the truncated value plus "-01" is suspicious but
    not damning - some breaches really are reported on the first. What settles it is a
    SIBLING date in the same upstream row that is still month-truncated: a record whose
    end_breach_date reads "2019-07" carries month precision throughout, so the "-01" on
    its other dates came from a pipeline, not from the notification.

    Carnival is the case: the Maine AG record reads breach_date 2019-04-01,
    reported_date 2020-03-01, end_breach_date 2019-07, while its own narrative says the
    breach ran April 11 to July 23 and notifications went out "in the week of March 2,
    2020" - no day is reported at all. The sibling Washington record, which does carry
    day precision, reads 2019-04-11 / 2020-03-02 / 2019-07-23.
    """
    if srow is None:
        return False
    if not str(candidate).startswith(str(malformed).strip()[:7]):
        return False
    if not str(candidate).endswith("-01"):
        return False
    for c in TRUNC_CHECK_COLS:
        if c in srow.index and MONTH_ONLY_RE.fullmatch(str(srow[c]).strip()):
            return True
    return False


def fix_cik(ev, rows, old_cik, new_cik, evidence, label):
    sel = ev["final_cik"] == old_cik
    n = int(sel.sum())
    if not n:
        log(f"- {label}: no rows with CIK {old_cik}; nothing to correct.")
        return ev
    org = str(ev.loc[sel, "org_name"].iloc[0])
    ev.loc[sel, "final_cik"] = new_cik
    # Guarded: the offline tests exercise fix_cik on bare frames that carry no link_basis.
    if "link_basis" in ev.columns:
        ev.loc[sel, "link_basis"] = "cik_correction"
    for bd in ev.loc[sel, "breach_date"]:
        record(rows, "final_cik", old_cik, org, str(bd)[:10], "final_cik",
               old_cik, new_cik, True, evidence)
    log(f"- {label}: CIK {old_cik} -> {new_cik} on {n} row(s).")
    return ev


def tenk_after(m213, cik, breach_date, window=FY_WINDOW_DAYS):
    """10-K filings covering the breach fiscal year. -> (list of (form, acc, date), note)."""
    if m213 is None:
        return [], "scripts/213 unavailable"
    df = m213.submissions(cik)
    if df is None or df.empty:
        return [], f"no cached submissions for CIK {cik}"
    k = df[df["form"].astype(str).str.startswith("10-K")].dropna(subset=["fdate"])
    bd = pd.Timestamp(breach_date)
    # pd.Timedelta(days=N) constructs a generic-unit numpy timedelta and is deprecated on
    # numpy 2.x; the unit has to be explicit. The comparison and the datetime64[ns] column
    # were never the problem - the Timedelta constructor was.
    w = k[(k["fdate"] > bd) & (k["fdate"] <= bd + pd.Timedelta(int(window), unit="D"))]
    out = [(str(x["form"]), str(x["accessionNumber"]), str(x["fdate"])[:10])
           for _, x in w.sort_values("fdate").iterrows()]
    last = str(k["fdate"].max())[:10] if len(k) else "none"
    return out, f"{len(k)} 10-K filing(s) in total, most recent {last}"


def fix_lennar(ev, rows, m213):
    sel = ev["final_cik"] == LENNAR_OLD
    if not sel.any():
        log("- Lennar: no rows with CIK 58696; nothing to correct.")
        return ev
    bd = pd.to_datetime(ev.loc[sel, "breach_date"]).min()
    cand, cnote = tenk_after(m213, LENNAR_NEW, bd)
    inc, inote = tenk_after(m213, LENNAR_OLD, bd)
    evid = (f"CIK {LENNAR_NEW}: {cnote}; 10-K within {FY_WINDOW_DAYS}d after "
            f"{bd.date()}: {cand or 'NONE'}. "
            f"CIK {LENNAR_OLD}: {inote}; 10-K within {FY_WINDOW_DAYS}d after "
            f"{bd.date()}: {inc or 'NONE'}.")
    if cand and not inc:
        return fix_cik(ev, rows, LENNAR_OLD, LENNAR_NEW, evid, "Lennar")
    org = str(ev.loc[sel, "org_name"].iloc[0])
    for b in ev.loc[sel, "breach_date"]:
        record(rows, "final_cik", LENNAR_OLD, org, str(b)[:10], "final_cik",
               LENNAR_OLD, LENNAR_NEW, False, "condition NOT met: " + evid)
    log("- Lennar: condition NOT met; correction withheld.")
    return ev


# BOTH verification logs. Stage 3b runs with --out-prefix stage3b_, so its verdicts land
# in a separate file; reading only the first would silently discard every Stage 3b result
# while still reporting success.
VERIFY_LOGS = (Path("outputs/rebuild_v4/213_verification_log.csv"),
               Path("outputs/rebuild_v4/stage3b_213_verification_log.csv"))
BASIS_BY_TYPE = {"a_subsidiary": "exhibit21_parent",
                 "gate_exclusion": "exhibit21_parent",
                 "ncusip_name_mismatch": "exhibit21_parent",
                 "b_successor_cik": "successor_filing"}



# ------------------------------------------------------------------ Gate-2 anchor
# FREEZE EXCEPTION 2026-09-24 (second), reason 1, logged in docs/claude/POST_DEFENSE.md
# BEFORE this change.
#
# Defect origin: scripts/153:59, which is v3 and FROZEN. Gate 2 collapses adjacent
# firm-day events by sorting on breach date and keeping m.index[0]. It rewrites
# name_variants, n_source_records, breach_type, multi_type, total_affected_max,
# multi_filing and chain_note on the surviving row - but NOT reported_date. The kept
# event therefore inherits the notification date of the earliest-BREACH component
# rather than the chain minimum, unlike Stage 3, where 152:91 takes
# g['reported_date'].min().
#
# scripts/153 and its outputs are in the v3 freeze manifest, so the defect is repaired
# HERE instead, as ordinary correction-ledger entries. The v3 vintage keeps its
# original anchor.
#
# The chain minimum is computed from the PRC records themselves, via the lineage the
# event already carries: name_variants names the org names it collapsed, and
# chain_note names the firm-day dates. Sprint is the one event whose breach_date this
# script also moves, so its pre-correction date is used to find its records.
CHAIN_DATES_RE = re.compile(r"\[([^\]]+)\]")


def fix_gate2_anchor(ev, rows, v3_breach):
    """reported_date := min(reported_date) across every source record of the chain."""
    s2p = Path("Data/processed/rebuild/stage2_signed.csv")
    if not s2p.exists():
        log("- Gate-2 anchor: stage2_signed.csv absent; correction NOT applied.")
        return ev
    s2 = pd.read_csv(s2p, low_memory=False)
    s2["_rd"] = pd.to_datetime(s2["reported_date"], errors="coerce")
    s2["_bd"] = s2["breach_date"].astype(str).str[:10]
    by_name = {n: g for n, g in s2.groupby(s2["org_name"].astype(str))}

    n_moved = 0
    for i, r in ev.iterrows():
        note = str(r.get("chain_note", "") or "")
        if not note:
            continue                      # only Gate-2 chained events can be affected
        names = {x.strip() for x in str(r.get("name_variants", "")).split("|") if x.strip()}
        dates = {str(r["breach_date"])[:10], str(v3_breach.iloc[i])[:10]}
        m = CHAIN_DATES_RE.search(note)
        if m:
            dates |= {d.strip() for d in m.group(1).split(",")}
        recs = [by_name[n] for n in names if n in by_name]
        if not recs:
            continue
        recs = pd.concat(recs)
        recs = recs[recs["_bd"].isin(dates)]
        rd = recs["_rd"].dropna()
        if not len(rd):
            continue
        cur = pd.to_datetime(r["reported_date"], errors="coerce")
        lo = rd.min()
        if pd.isna(cur) or lo >= cur:
            continue
        ev.at[i, "reported_date"] = str(lo)
        n_moved += 1
        record(rows, "reported_date_gate2_anchor", r["final_cik"], r["org_name"],
               str(r["breach_date"])[:10], "reported_date",
               str(cur)[:10], str(lo)[:10], True,
               f"Gate-2 chain collapsed {len(recs)} source record(s); scripts/153:59 kept "
               f"the earliest-breach component's notification date, not the chain "
               f"minimum. Stage 3 (152:91) takes the minimum, so this restores the "
               f"documented definition. Gap {int((cur - lo).days)} day(s). "
               f"v3 is frozen and keeps the original anchor.")
    log(f"- Gate-2 anchor: {n_moved} event(s) moved to the chain-minimum reported_date.")
    return ev



# ------------------------------------------------------------------ health indicator
# FREEZE EXCEPTION 2026-09-25 (third), reason 1, logged in docs/claude/POST_DEFENSE.md
# BEFORE this change.
#
# Defect origin: scripts/152:93 and scripts/153:62-71, both v3 and FROZEN.
# health_breach (scripts/156:144-146) tests ONE information_affected per event. Stage 3
# picks that one at 152:93 as the source record with the LONGEST string
#   g.loc[g['information_affected'].astype(str).str.len().idxmax(), ...]
# rather than as a union over the firm-day's records, and Gate 2 rewrites seven fields on
# the surviving row at 153:62-71 but NOT information_affected. So an event whose health
# mention sits in a shorter record of the same firm-day, or in another chain component,
# is coded 0.
#
# The methods define the indicator as ANY record describing health data, so the rule is
# restored HERE, over every source record of the event, as ordinary correction-ledger
# entries. scripts/152 and scripts/153 are in the v3 freeze manifest; the v3 vintage
# keeps its original values.
#
# Direction: this only ever RAISES 0 -> 1. The stored information_affected is itself one
# of the event's records, so a flagged event always has a matching record; the function
# asserts that and never lowers a flag.
HEALTH_RE = re.compile(r"medical|health", re.I)


def fix_health_any_record(ev, rows, v3_breach):
    """health_breach := 1 if ANY source record's information_affected matches."""
    s2p = Path("Data/processed/rebuild/stage2_signed.csv")
    if not s2p.exists():
        log("- health indicator: stage2_signed.csv absent; correction NOT applied.")
        return ev
    s2 = pd.read_csv(s2p, low_memory=False)
    s2["_bd"] = s2["breach_date"].astype(str).str[:10]
    s2["_ia"] = s2["information_affected"].astype(str)
    s2["_h"] = s2["_ia"].str.contains(HEALTH_RE, na=False)
    by_name = {n: g for n, g in s2.groupby(s2["org_name"].astype(str))}

    n_raised = n_nolineage = 0
    for i, r in ev.iterrows():
        names = {x.strip() for x in str(r.get("name_variants", "")).split("|") if x.strip()}
        names.add(str(r["org_name"]))
        dates = {str(r["breach_date"])[:10], str(v3_breach.iloc[i])[:10]}
        m = CHAIN_DATES_RE.search(str(r.get("chain_note", "") or ""))
        if m:
            dates |= {d.strip() for d in m.group(1).split(",")}
        recs = [by_name[n] for n in names if n in by_name]
        if not recs:
            n_nolineage += 1
            continue
        recs = pd.concat(recs)
        recs = recs[recs["_bd"].isin(dates)]
        if not len(recs):
            n_nolineage += 1
            continue
        hits = recs[recs["_h"]]
        cur = int(r["health_breach"])
        if cur == 1 and not len(hits):
            # the stored value is one of these records, so this cannot happen
            sys.exit("ABORT 214: health_breach=1 with no matching source record for "
                     + str(r["org_name"]) + " " + str(r["breach_date"])[:10])
        if cur == 1 or not len(hits):
            continue
        ev.at[i, "health_breach"] = 1
        n_raised += 1
        where = "; ".join(sorted({str(x["_bd"]) + " / " + str(x["org_name"]) for _, x in hits.iterrows()}))
        chained = "Gate-2 chained (" + str(m.group(1)) + ")" if m else "single firm-day"
        record(rows, "health_breach_any_record", r["final_cik"], r["org_name"],
               str(r["breach_date"])[:10], "health_breach", "0", "1", True,
               str(len(hits)) + " of " + str(len(recs)) + " source record(s) match "
               "medical|health (case-insensitive) in information_affected: " + where
               + ". " + chained + ". scripts/152:93 keeps only the longest-string record "
               "and scripts/153:62-71 does not re-aggregate across chain components, so "
               "the mention was dropped. The methods define the indicator as ANY record "
               "describing health data. v3 is frozen and keeps the original value.")
    log("- health indicator: " + str(n_raised) + " event(s) raised 0 -> 1 on the "
        "any-record rule (" + str(n_nolineage) + " without resolvable lineage).")
    return ev


def apply_stage3(ev, rows, v3_cik, v3_breach):
    """Re-parent every VERIFIED Stage 3 event; leave every UNVERIFIED one alone.

    A subsidiary's own CIK has no Compustat gvkey, so the linker could never reach a
    permno through it. Stage 3 established, against an Exhibit 21 or a succession filing,
    which registrant the event belongs to; this points the event at that registrant so
    the second linker pass can find it.

    UNVERIFIED rows are NOT re-parented. They stay on their original CIK and stay
    excluded, which is the whole point of having required evidence.

    Matching uses the ORIGINAL CIK and breach_date, because Stage 4's own corrections may
    already have moved either one.
    """
    present = [p for p in VERIFY_LOGS if p.exists()]
    if not present:
        log(f"- Stage 3: none of {[p.name for p in VERIFY_LOGS]} present; "
            f"no re-parenting applied.")
        return ev
    v = pd.concat([pd.read_csv(p, low_memory=False) for p in present], ignore_index=True)
    log(f"- Stage 3: read {len(v)} verdict row(s) from "
        f"{', '.join(p.name for p in present)}.")
    ver = v[v["verdict"] == "VERIFIED"]
    key = {}
    for _, r in ver.iterrows():
        pc = pd.to_numeric(pd.Series([r.get("parent_cik")]), errors="coerce").iloc[0]
        if pd.isna(pc):
            continue
        key[(int(r["cik"]), str(r["breach_date"])[:10])] = (
            int(pc), str(r["candidate_type"]), str(r.get("accession", "")),
            str(r.get("matching_line", ""))[:120])
    changed = basis_only = 0
    for i in ev.index:
        k = (int(v3_cik[i]), str(v3_breach[i])[:10])
        if k not in key:
            continue
        new_cik, ctype, acc, line = key[k]
        basis = BASIS_BY_TYPE.get(ctype, "direct")
        ev.at[i, "link_basis"] = basis
        old = int(ev.at[i, "final_cik"])
        if new_cik != old:
            ev.at[i, "final_cik"] = new_cik
            changed += 1
            record(rows, f"stage3_{ctype}", old, ev.at[i, "org_name"],
                   str(ev.at[i, "breach_date"])[:10], "final_cik", old, new_cik, True,
                   f"Stage 3 VERIFIED ({ctype}); accession {acc}; "
                   f"matching line/passage: {line!r}")
        else:
            basis_only += 1
    log(f"- Stage 3: {changed} event(s) re-parented, {basis_only} verified without a CIK "
        f"change (the verified registrant was already the event CIK); "
        f"{len(v) - len(ver)} UNVERIFIED row(s) left untouched and excluded.")
    return ev


REPORT_ONLY = [
    ("Dell Inc.", 826083,
     "EDGAR registrant DELL INC; 533 filings within +/-2 years of the 2013-02-26 breach; "
     "no other filer normalises to the same name. The CIK is active and correct - the "
     "row is excluded for want of a Compustat gvkey, which is a coverage limit, not a "
     "CIK error."),
    ("Warn Industries, Inc.", 1984463,
     "Dover Corporation's Exhibit 21 (CIK 29905, accession 0000029905-18-000019, "
     "selected by document type EX-21) contains exactly one line matching WARN: "
     "'Warn Automotive, LLC'. 'Warn Industries, Inc.' is not listed. Documented "
     "exclusion, not a matcher failure."),
    ("Uber", 1431473,
     "Stage 2 nominated UBER TECHNOLOGIES INC (cik 1543151) on the shared token UBER. "
     "No Exhibit 21 or succession filing has been produced for the identity, so the row "
     "stays excluded and the CIK is left as recorded."),
]


def main():
    if not CANON_V3.exists():
        sys.exit(f"missing input: {CANON_V3}")
    assert_v4(OUT_DATA, OUT_CSV, OUT_MD)
    m213 = load_m213()
    ev = pd.read_csv(CANON_V3, low_memory=False)
    before = ev.copy()
    # Captured BEFORE any correction. Stage 3's worklist is keyed to the v3 CIK and
    # breach_date, and Stage 4 moves both - International Paper's and Lennar's CIK, and
    # Sprint's date - so matching on the corrected values would miss those rows.
    v3_cik = ev["final_cik"].copy()
    v3_breach = ev["breach_date"].copy()
    ev["orig_cik"] = v3_cik
    ev["link_basis"] = "direct"
    rows = []

    log("# REBUILD V4 — Stage 4 corrections")
    log("")
    log(f"- run (UTC): {datetime.now(timezone.utc).isoformat(timespec='seconds')}")
    log(f"- input: `{CANON_V3.as_posix()}` ({len(ev)} rows, read-only)")
    log("- Stage 4 issues no SEC request; the EDGAR cache is read, never written.")
    log("")
    log("## Corrections applied")
    log("")

    sprint_tbl = None
    ev, sprint_tbl = fix_sprint(ev, rows)
    ev = fix_reported_dates(ev, rows)
    ev = fix_cik(ev, rows, INTL_PAPER_OLD, INTL_PAPER_NEW,
                 "assigned CIK 1283246 last filed 2013-02-01 and filed nothing within "
                 "+/-2 years of the 2023-05-30 breach; CIK 51434 (INTERNATIONAL PAPER CO "
                 "/NEW/) is the only other filer with the same normalised name and is "
                 "active across the window (365 filings)", "International Paper")
    ev = fix_lennar(ev, rows, m213)
    ev = fix_gate2_anchor(ev, rows, v3_breach)
    ev = fix_health_any_record(ev, rows, v3_breach)
    ev = apply_stage3(ev, rows, v3_cik, v3_breach)

    C = pd.DataFrame(rows)
    log("")
    if len(C):
        log(md_table(C[["kind", "cik", "org_name", "breach_date", "old_value",
                        "new_value", "applied"]]))
    log("")
    if sprint_tbl is not None:
        log("### Sprint — prior_breaches_1yr, every event")
        log("")
        log(md_table(sprint_tbl))
        log("")
    log("## Report-only (no change)")
    log("")
    for name, cik, why in REPORT_ONLY:
        log(f"- **{name}** (CIK {cik}): {why}")
    log("")

    changed = int((before["final_cik"] != ev["final_cik"]).sum()
                  + (before["breach_date"].astype(str) != ev["breach_date"].astype(str)).sum())
    log(f"Rows differing from CANONICAL_V3 on final_cik or breach_date: {changed}")
    log("")

    OUT_DATA.parent.mkdir(parents=True, exist_ok=True)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    ev.to_csv(OUT_DATA, index=False)
    C.to_csv(OUT_CSV, index=False)
    OUT_MD.write_text("\n".join(LOG) + "\n", encoding="utf-8")
    print(f"\nWROTE {OUT_DATA}\nWROTE {OUT_CSV}\nWROTE {OUT_MD}")
    return 0


def md_table(df):
    cols = [str(c) for c in df.columns]
    out = ["| " + " | ".join(cols) + " |", "|" + "|".join("---" for _ in cols) + "|"]
    for _, r in df.iterrows():
        out.append("| " + " | ".join("" if pd.isna(v) else str(v)[:90] for v in r) + " |")
    return "\n".join(out)


if __name__ == "__main__":
    sys.exit(main())
