"""
REBUILD V4 — STAGE 3: EDGAR VERIFICATION OF THE STAGE 2 WORKLIST (run locally)
=====================================================================================
Stage 2 produced outputs/rebuild_v4/stage3_candidates.csv: events whose identity the
linker could not settle by itself. This script tries to settle each one against a FILING,
and records the accession and the matching line. Nothing is verified by name recognition.

    set SEC_EDGAR_USER_AGENT=Your Name your.email@domain
    python scripts/213_stage3_verify.py

WHAT COUNTS AS VERIFIED
-----------------------
a_subsidiary / ncusip_name_mismatch / gate_exclusion
    The parent's 10-K nearest the breach_date (within 18 months either side) must carry
    an Exhibit 21 whose subsidiary list contains a line matching the breached
    organisation under the SAME normalisation Stage 2 used. Record accession + line.

b_successor_cik
    An 8-K (including the 8-K12G3 / 8-K12B succession forms) or a Form 12g-3 filed by
    either the successor or the predecessor must name the other. Record accession + line.

Anything else stays UNVERIFIED, and an UNVERIFIED row stays EXCLUDED — including
ncusip_name_mismatch, whose CUSIP link is sound but whose identity is unadjudicated.
This script NEVER writes a link, a permno or an inclusion decision; it only produces
evidence for one.

ONE ADDITION TO THE MATCH RULE, FLAGGED
---------------------------------------
A line matches under Stage 2's normalisation, AND the shared token must not be an
industry word alone. Without that, "Prime Communications" would verify against any line
reading "<anything> Communications Inc." in Verizon's Exhibit 21 - the exact false
positive that got 10 nominations reclassified. Every match records its shared tokens so
the decision is auditable, and the condition can be dropped by deleting one clause.

WHERE THE PARENT CIK COMES FROM (never from name recognition)
-------------------------------------------------------------
a_subsidiary          the nomination file's parent_cik, joined on cik
b_successor_cik       parsed out of the candidate string Stage 2 wrote ("... cik 1971213")
gate_exclusion,       the REJECTED/linked permno resolved through the local WRDS pulls:
ncusip_name_mismatch  permno -> cusip8 -> gvkey -> cik. No network, fully deterministic.
A row whose parent CIK cannot be resolved is UNVERIFIED with that reason; it is never
guessed.

SEC FAIR ACCESS
---------------
User-Agent from SEC_EDGAR_USER_AGENT (your name and email); the script aborts if it is
unset. At most 10 requests/second. Every fetched document is cached under
Data/edgar/ex21_cache_v4/, so a re-run costs no requests and is reproducible offline.
A 403 aborts loudly rather than being recorded as "not found": the SEC WAF blocks by IP,
and a silent 403 would look exactly like an honest failure to verify.

OUTPUTS (writes nothing else, touches no v3 path)
    outputs/rebuild_v4/213_verification_log.csv  one row per candidate, verdict+evidence
    outputs/rebuild_v4/213_extra_ciks.txt        verified CIKs not among the 185 already
                                                 pulled, ready for 211 --extra-ciks
"""
import html
import hashlib
import importlib.util
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import pandas as pd

S3 = Path("outputs/rebuild_v4/stage3_candidates.csv")
NOMS = Path("outputs/rebuild_v4/inputs/crsp_drop_nominations.csv")
W = Path("Data/wrds_v4")
CACHE = Path("Data/edgar/ex21_cache_v4")
OUT_LOG = Path("outputs/rebuild_v4/213_verification_log.csv")
OUT_CIKS = Path("outputs/rebuild_v4/213_extra_ciks.txt")

UA_ENV = "SEC_EDGAR_USER_AGENT"
MIN_INTERVAL = 0.11          # <= 10 requests/second, with headroom
WINDOW_DAYS = 548            # 18 months either side of breach_date
SUCCESSOR_SCAN_CAP = 40      # bound the 8-K scan; succession forms are tried first

# `ex[-_ ]?21` and NOT `ex.?-?\s?21`. The wildcard let the "1" of "ex121" be consumed, so
# dex121.htm (Exhibit 12.1, ratio of earnings to fixed charges) matched as an Exhibit 21.
# News Corp's 2009 10-K contains dex121.htm, dex21.htm AND dex321.htm; the old pattern
# matched all three and took the first in directory order, i.e. Exhibit 12.1. Fox then
# came back UNVERIFIED because the wrong document was searched.
EX21_RE = re.compile(r"ex[-_ ]?21", re.I)

# Succession language. Rule 3: naming the other firm is not enough - the SAME passage must
# also say what the relationship is, or any filing that merely mentions the other company
# would verify a succession.
SUCCESSION_RE = re.compile(
    r"successor|predecessor|holding\s+company\s+reorgani[sz]ation|"
    r"rule\s*12\s*g-?\s*3|12\s*g-?\s*3|merger|merged", re.I)

TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
CIK_IN_CAND = re.compile(r"cik\s+(\d+)", re.I)
SUBSIDIARY_TYPES = ("a_subsidiary", "ncusip_name_mismatch", "gate_exclusion")


def _load(path, name):
    p = Path(path)
    if not p.exists():
        sys.exit(f"missing input: {p}")
    spec = importlib.util.spec_from_file_location(name, str(p))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


M212 = _load("scripts/212_pit_linker_v4.py", "m212_for_213")
M211 = _load("scripts/211_wrds_pull_v4.py", "m211_for_213")


# --------------------------------------------------------------------------- network
_last_call = [0.0]


def user_agent():
    ua = os.environ.get(UA_ENV, "").strip()
    if not ua or "@" not in ua:
        sys.exit(
            f"{UA_ENV} is unset or does not look like a contact string.\n"
            f"SEC fair access requires a declared identity. Set it to your name and "
            f"email, e.g.:\n    set {UA_ENV}=Jane Doe jane.doe@university.edu")
    return ua


def cache_path(url):
    h = hashlib.sha256(url.encode("utf-8")).hexdigest()[:24]
    tail = re.sub(r"[^A-Za-z0-9._-]", "_", url.rsplit("/", 1)[-1])[:60] or "doc"
    return CACHE / f"{h}_{tail}"


def fetch(url):
    """Cached, rate-limited GET. Returns bytes, or None if the document is absent.

    Tests replace this wholesale; every network path in the script goes through it.
    """
    p = cache_path(url)
    if p.exists():
        return p.read_bytes()
    dt = time.time() - _last_call[0]
    if dt < MIN_INTERVAL:
        time.sleep(MIN_INTERVAL - dt)
    _last_call[0] = time.time()
    req = Request(url, headers={"User-Agent": user_agent()})
    try:
        with urlopen(req, timeout=30) as r:
            data = r.read()
    except HTTPError as e:
        if e.code == 404:
            return None
        if e.code == 403:
            sys.exit(f"HTTP 403 from SEC for {url}\nThe SEC WAF blocks by IP address. "
                     f"Stopping rather than recording this as a failure to verify.")
        raise
    except URLError as e:
        sys.exit(f"network error for {url}: {e}")
    CACHE.mkdir(parents=True, exist_ok=True)
    p.write_bytes(data)
    return data


def submissions(cik):
    """Every filing for a CIK: the recent block plus the older shards."""
    raw = fetch(f"https://data.sec.gov/submissions/CIK{int(cik):010d}.json")
    if raw is None:
        return pd.DataFrame()
    j = json.loads(raw.decode("utf-8", "replace"))
    filings = j.get("filings", {})
    frames = []
    rec = filings.get("recent")
    if rec:
        frames.append(pd.DataFrame(rec))
    for extra in filings.get("files", []) or []:
        d = fetch(f"https://data.sec.gov/submissions/{extra.get('name','')}")
        if d:
            frames.append(pd.DataFrame(json.loads(d.decode("utf-8", "replace"))))
    frames = [f for f in frames if f is not None and not f.empty]
    if not frames:
        return pd.DataFrame()
    df = pd.concat(frames, ignore_index=True)
    for col in ("form", "accessionNumber", "filingDate", "primaryDocument"):
        if col not in df.columns:
            df[col] = ""
    df["form"] = df["form"].astype(str).str.upper().str.strip()
    df["fdate"] = pd.to_datetime(df["filingDate"], errors="coerce")
    return df


def pick_nearest(df, prefixes, target, window_days=WINDOW_DAYS):
    """The filing of a matching form type closest to `target`, within the window."""
    if df is None or df.empty or pd.isna(target):
        return None
    d = df[df["form"].str.startswith(tuple(prefixes))].dropna(subset=["fdate"]).copy()
    if d.empty:
        return None
    d["gap"] = (d["fdate"] - pd.Timestamp(target)).abs().dt.days
    d = d[d["gap"] <= window_days].sort_values(["gap", "fdate"])
    return None if d.empty else d.iloc[0]


def filing_files(cik, accession):
    """Filenames inside one filing, via its index.json."""
    acc = str(accession).replace("-", "")
    raw = fetch(f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc}/index.json")
    if raw is None:
        return []
    items = json.loads(raw.decode("utf-8", "replace")).get("directory", {}).get("item", [])
    return [str(it.get("name", "")) for it in items if it.get("name")]


def find_ex21_name(names):
    """The Exhibit 21 document among a filing's files, if it is there."""
    for n in names:
        if EX21_RE.search(n) and n.lower().endswith((".htm", ".html", ".txt")):
            return n
    return None


TAG_RE = re.compile(r"<[^>]+>")
BREAK_RE = re.compile(r"(?i)<\s*(br|/p|/tr|/div|/td|/li|/h\d)[^>]*>")
SCRIPT_RE = re.compile(r"(?is)<(script|style).*?</\1>")


def to_lines(raw):
    """Filing bytes -> visible text lines. Exhibit 21 is a list, so lines are the unit."""
    t = raw.decode("utf-8", "replace") if isinstance(raw, (bytes, bytearray)) else str(raw)
    t = SCRIPT_RE.sub(" ", t)
    t = BREAK_RE.sub("\n", t)
    t = TAG_RE.sub(" ", t)
    t = html.unescape(t)
    out = []
    for ln in t.split("\n"):
        ln = re.sub(r"\s+", " ", ln).strip()
        if ln:
            out.append(ln)
    return out


def line_names(name, line):
    """Does this ONE line actually name `name`? -> (bool, evidence_tokens).

    A line names the firm iff it contains EVERY significant token of the name, or its
    space-stripped concatenation equals the name's. One shared token is never enough:
    that standard verified "Brown, Lisle/Cummings, Inc." against a line reading
    "Brown-Forman Corporation", and "Communications & Power Industries LLC" against
    "AMERICAN ELECTRIC POWER COMPANY, INC.", on BROWN and POWER respectively.
    """
    nt = M212.norm_tokens(name)
    sig = {t for t in nt if len(t) >= M212.SIGNIFICANT_LEN}
    lt = M212.norm_tokens(line)
    if sig and sig <= set(lt):
        return True, "|".join(sorted(sig))
    ca, cb = "".join(nt), "".join(lt)
    if ca and ca == cb:
        return True, ca
    return False, ""


def match_line(name, lines):
    """First line that NAMES `name`. -> (line, evidence_tokens)."""
    for ln in lines:
        ok, ev = line_names(name, ln)
        if ok:
            return ln, ev
    return None, None


def match_passage(name, passages):
    """First passage naming `name` AND carrying succession language. -> (passage, ev)."""
    for p in passages:
        ok, ev = line_names(name, p)
        if ok and SUCCESSION_RE.search(p):
            return p, ev
    return None, None


def ticker_to_cik():
    """SEC's own ticker -> CIK table, so a nominated parent is never a CIK from memory."""
    raw = fetch(TICKERS_URL)
    if raw is None:
        return {}
    j = json.loads(raw.decode("utf-8", "replace"))
    out = {}
    for v in j.values():
        t = str(v.get("ticker", "")).strip().upper()
        if t:
            out.setdefault(t, int(v["cik_str"]))
    return out


def doc_url(cik, accession, name):
    return (f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/"
            f"{str(accession).replace('-', '')}/{name}")


# ----------------------------------------------------------------------- verification
def blank(**kw):
    row = dict(verdict="UNVERIFIED", reason="", accession="", form="", filing_date="",
               matching_line="", shared_tokens="", document_url="")
    row.update(kw)
    return row


def verify_subsidiary(parent_cik, sub_name, breach_date):
    """Parent's 10-K nearest breach_date -> Exhibit 21 -> a line naming the subsidiary."""
    if not parent_cik:
        return blank(reason="parent CIK could not be resolved without name recognition")
    subs = submissions(parent_cik)
    if subs.empty:
        return blank(reason=f"no EDGAR submissions for CIK {parent_cik}")
    f = pick_nearest(subs, ("10-K",), breach_date)
    if f is None:
        return blank(reason=f"no 10-K within {WINDOW_DAYS} days of {breach_date}")
    acc, form = str(f["accessionNumber"]), str(f["form"])
    fdate = str(f["filingDate"])
    ex = find_ex21_name(filing_files(parent_cik, acc))
    if not ex:
        return blank(reason="no Exhibit 21 in the nearest 10-K", accession=acc,
                     form=form, filing_date=fdate)
    url = doc_url(parent_cik, acc, ex)
    raw = fetch(url)
    if raw is None:
        return blank(reason="Exhibit 21 document could not be retrieved",
                     accession=acc, form=form, filing_date=fdate, document_url=url)
    line, shared = match_line(sub_name, to_lines(raw))
    if not line:
        return blank(reason=f"Exhibit 21 does not list {sub_name!r}", accession=acc,
                     form=form, filing_date=fdate, document_url=url)
    return blank(verdict="VERIFIED", reason="named in Exhibit 21", accession=acc,
                 form=form, filing_date=fdate, matching_line=line[:300],
                 shared_tokens=shared, document_url=url)


def succession_candidates(df):
    """8-K/12g-3 filings, succession forms first, capped."""
    if df is None or df.empty:
        return []
    d = df[df["form"].str.startswith(("8-K", "12G3", "12G-3"))].copy()
    if d.empty:
        return []
    d["prio"] = (~d["form"].str.contains("12G3|12G-3|12B", regex=True)).astype(int)
    d = d.sort_values(["prio", "fdate"], ascending=[True, False])
    return [r for _, r in d.head(SUCCESSOR_SCAN_CAP).iterrows()]


def verify_successor(cik_a, name_a, cik_b, name_b):
    """An 8-K or 12g-3 by either party naming the other."""
    if not cik_a or not cik_b:
        return blank(reason="successor or predecessor CIK could not be resolved")
    for filer_cik, other_name in ((cik_b, name_a), (cik_a, name_b)):
        df = submissions(filer_cik)
        for f in succession_candidates(df):
            acc = str(f["accessionNumber"])
            primary = str(f.get("primaryDocument", "") or "")
            if not primary:
                continue
            url = doc_url(filer_cik, acc, primary)
            raw = fetch(url)
            if raw is None:
                continue
            passage, ev = match_passage(other_name, to_lines(raw))
            if passage:
                return blank(verdict="VERIFIED",
                             reason=f"CIK {filer_cik} filing names {other_name!r} in a "
                                    f"passage carrying succession language",
                             accession=acc, form=str(f["form"]),
                             filing_date=str(f["filingDate"]),
                             matching_line=passage[:300],
                             shared_tokens=ev, document_url=url)
    return blank(reason="no 8-K or 12g-3 by either party names the other in a passage "
                        "carrying succession language")


# ------------------------------------------------------------------- CIK resolution
def permno_to_cik():
    """permno -> cik through the local pulls only. No network, no name matching."""
    comp = pd.read_csv(W / "comp_company.csv", low_memory=False)
    sec = pd.read_csv(W / "comp_security.csv", low_memory=False)
    nam = pd.read_csv(W / "crsp_stocknames.csv", low_memory=False)
    sec["cusip8"] = sec["cusip"].astype(str).str.strip().str.upper().str[:8]
    comp["cik_int"] = pd.to_numeric(comp["cik"], errors="coerce")
    cus2cik = (sec.merge(comp[["gvkey", "cik_int"]], on="gvkey", how="left")
                  .dropna(subset=["cik_int"]).set_index("cusip8")["cik_int"].to_dict())
    out = {}
    for col in ("ncusip", "cusip"):
        s = nam.dropna(subset=[col]).copy()
        s[col] = s[col].astype(str).str.strip().str.upper()
        for pn, cu in zip(s["permno"], s[col]):
            cik = cus2cik.get(cu)
            if cik and int(pn) not in out:
                out[int(pn)] = int(cik)
    return out


def resolve_parent(row, noms, pn2cik, tick2cik):
    """-> (parent_cik or None, parent_name, how)."""
    ct = row["candidate_type"]
    if ct == "b_successor_cik":
        m = CIK_IN_CAND.search(str(row.get("candidate", "")))
        return (int(m.group(1)) if m else None, str(row.get("candidate", "")),
                "parsed from the Stage 2 candidate string")
    if ct == "a_subsidiary":
        hit = noms[noms["cik"] == row["cik"]]
        pname = str(row.get("candidate", ""))
        pc = pd.to_numeric(hit["parent_cik"], errors="coerce").dropna()
        if len(pc):
            return int(pc.iloc[0]), pname, "nomination file parent_cik"
        # Name knowledge may NOMINATE a parent, never verify one. The ticker comes from
        # the nomination file and the CIK from SEC's own table, so no CIK originates in
        # anybody's memory - and the Exhibit 21 still decides. Volkswagen (VWAGY) and
        # Activision (ATVI) reach a parent CIK only by this route.
        tick = hit["ticker"].dropna().astype(str).str.strip().str.upper()
        if len(tick) and tick.iloc[0] in tick2cik:
            basis = str(hit["basis"].iloc[0]) if "basis" in hit.columns else ""
            return (tick2cik[tick.iloc[0]], pname,
                    f"NOMINATED: ticker {tick.iloc[0]} -> CIK via SEC "
                    f"company_tickers.json; basis: {basis[:80]}")
        return None, pname, "no parent_cik and no usable ticker in the nomination file"
    pn = pd.to_numeric(pd.Series([row.get("crsp_permno")]), errors="coerce").iloc[0]
    if pd.isna(pn):
        return None, str(row.get("comnam_at_breach", "")), "no permno on the row"
    return (pn2cik.get(int(pn)), str(row.get("comnam_at_breach", "")),
            f"permno {int(pn)} -> cusip8 -> gvkey -> cik via the local pulls")


# ------------------------------------------------------------------------------ main
def main():
    for p in (S3, NOMS, W / "comp_company.csv", W / "comp_security.csv",
              W / "crsp_stocknames.csv"):
        if not p.exists():
            sys.exit(f"missing input: {p}")
    user_agent()          # fail before the first request, not after

    cand = pd.read_csv(S3)
    noms = pd.read_csv(NOMS)
    pn2cik = permno_to_cik()
    tick2cik = ticker_to_cik()
    base_ciks, _, _ = M211.load_base_ciks()

    print(f"stage 3 worklist: {len(cand)} rows")
    print(f"already pulled  : {len(base_ciks)} CIKs")
    print(f"cache           : {CACHE}")
    print()

    rows = []
    for _, r in cand.iterrows():
        pcik, pname, how = resolve_parent(r, noms, pn2cik, tick2cik)
        if r["candidate_type"] == "b_successor_cik":
            res = verify_successor(int(r["cik"]), str(r["org"]), pcik, pname)
        else:
            res = verify_subsidiary(pcik, str(r["org"]),
                                    pd.to_datetime(r.get("breach_date"), errors="coerce"))
        rows.append({"candidate_type": r["candidate_type"], "cik": r["cik"],
                     "org": r["org"], "breach_date": r.get("breach_date", ""),
                     "candidate": r.get("candidate", ""), "parent_cik": pcik or "",
                     "parent_name": pname, "cik_resolved_by": how, **res})
        print(f"  {res['verdict']:<10} {r['candidate_type']:<21} {str(r['org'])[:38]:<38} "
              f"{res['reason'][:60]}")

    log = pd.DataFrame(rows)
    OUT_LOG.parent.mkdir(parents=True, exist_ok=True)
    log.to_csv(OUT_LOG, index=False)

    ver = log[log["verdict"] == "VERIFIED"]
    new = sorted({int(c) for c in pd.to_numeric(ver["parent_cik"], errors="coerce")
                  .dropna()} - set(base_ciks))
    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    OUT_CIKS.write_text(
        "\n".join([f"# REBUILD V4 Stage 3 - verified CIKs not among the "
                   f"{len(base_ciks)} already pulled",
                   f"# generated {stamp} by scripts/213_stage3_verify.py",
                   "# feed to: python scripts/211_wrds_pull_v4.py --extra-ciks "
                   f"{OUT_CIKS.as_posix()}"] + [str(c) for c in new]) + "\n",
        encoding="utf-8")

    print()
    print(log["verdict"].value_counts().to_string())
    print()
    print(pd.crosstab(log["candidate_type"], log["verdict"]).to_string())
    print()
    print(f"WROTE {OUT_LOG}")
    print(f"WROTE {OUT_CIKS}  ({len(new)} CIK(s) not already pulled)")
    print()
    print("UNVERIFIED rows stay EXCLUDED, ncusip_name_mismatch included.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
