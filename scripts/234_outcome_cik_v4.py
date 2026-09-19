"""
REBUILD V4 - STAGE 6: OUTCOME CIK RESOLUTION
=============================================================================
v4 carries TWO entity fields per event, because one CIK cannot answer both
questions:

    final_cik    the EQUITY link - whose returns these are.  Set upstream by
                 Stages 3/4; unchanged here.
    outcome_cik  the FILING entity - whose Form 8-Ks are read for Item 5.02.

They diverge whenever an event was re-parented across a succession that
POSTDATES the breach.  Disney is the clean case: v4 re-parents the 2008-07-29
event to CIK 1744489 (The Walt Disney Company, created 2019, permno 26403),
which is right for returns and useless for filings - 1744489 filed nothing in
2008.  The entity that actually filed 8-Ks then is TWDC Enterprises 18 Corp.
(CIK 1001039), named as the predecessor in the very 8-K12B that verified the
succession.

THE RULE (Tim's ruling, applied to EVERY event)
-----------------------------------------------
outcome_cik = the FIRST of these candidates that filed >= 1 Form 8-K inside the
event's fetch window:

    1. final_cik
    2. orig_cik
    3. the predecessor named in the verifying succession filing, resolved to a
       CIK from that filing or from SEC's name index (cik-lookup-data.txt)

    window = [min(bd, rd_eff) - 730d, max(bd, rd_eff) + 180d]
    rd_eff = reported_date, filled by breach_date when missing

The 8-K count for EVERY candidate is recorded as evidence, not just the winner.
If no candidate filed, the event FAILS the outcome-data requirement and is
logged with the reason - it is never silently assigned a CIK.

Candidate 3 is only ever consulted when 1 and 2 both fail, and its name
extraction is heuristic, so it NEVER guesses: the extracted term, the defining
passage, the extracted legal name and the resolution method are all written to
234_candidate_evidence.csv.  A term that cannot be resolved to a unique CIK is
recorded as unresolved and the candidate is skipped.

SUBMISSIONS COVERAGE
--------------------
8-K counts come from the committed submissions cache.  Candidates with no
cached submissions cannot be counted offline; they are written to
234_submissions_needed.txt and folded into the 231 SEC fetch.  Such an event is
left unresolved with reason 'submissions_not_cached', never defaulted.

Offline.  Inputs (missing ABORTS):
    Data/processed/rebuild_v4/CANONICAL_V4.csv
    outputs/rebuild_v4/213_verification_log.csv
    outputs/rebuild_v4/stage3b_213_verification_log.csv
    Data/edgar/rebuild_submissions_cache/          (per-CIK submissions JSON)
    Data/edgar/ex21_cache_v4/                      (cached succession documents)
    Data/edgar/cik-lookup-data.txt                 (SEC name index)
Outputs:
    outputs/rebuild_v4/234_outcome_cik.csv
    outputs/rebuild_v4/234_candidate_evidence.csv
    outputs/rebuild_v4/234_submissions_needed.txt
    outputs/rebuild_v4/234_outcome_cik.md
"""
import json
import re
import sys
from datetime import timedelta
from pathlib import Path

import pandas as pd

CANON = Path("Data/processed/rebuild_v4/CANONICAL_V4.csv")
VERIFY_LOGS = (Path("outputs/rebuild_v4/213_verification_log.csv"),
               Path("outputs/rebuild_v4/stage3b_213_verification_log.csv"))
SUBS = Path("Data/edgar/rebuild_submissions_cache")
SUBS_V4 = Path("Data/edgar/submissions_cache_v4")     # written by 231, optional
DOCS = Path("Data/edgar/ex21_cache_v4")
NAME_INDEX = Path("Data/edgar/cik-lookup-data.txt")
OUT = Path("outputs/rebuild_v4")

PRE_DAYS = 730
POST_DAYS = 180
DEF_WINDOW = 200          # chars before a quoted term to look for its definition

# "... as the successor issuer to Old Disney pursuant to ..."
SUCCESSOR_TO_RE = re.compile(
    r"successor\s+(?:issuer|registrant)\s+to\s+(?:the\s+)?([^,.;:()]{2,70})", re.I)
# "(" Old Disney ")" - the same shape scripts/213 keys its aliases on
QUOTED_TERM_RE = re.compile(r"[\(\[]\s*[“\"']\s*([^”\"')\]]{2,60}?)\s*"
                            r"[”\"']\s*[\)\]]")
# The comma in "Sinclair Broadcast Group, Inc." is part of the name, so both the
# inner tokens and the entity form must tolerate one.
ENTITY_TAIL_RE = re.compile(
    r"([A-Z][A-Za-z0-9&.'\-]*(?:\s+[A-Za-z0-9&.'\-]+,?){0,7}?"
    r"(?:,?\s+(?:Inc|Incorporated|Corp|Corporation|Company|Co|LLC|L\.L\.C|LLP|LP|"
    r"Ltd|Limited|PLC|plc|N\.V|B\.V|S\.A|AG|AB|A/S|GmbH))\.?)\s*$")
# "Paramount Global, a Delaware corporation" -> strip the trailing descriptor
DESCRIPTOR_RE = re.compile(
    r",\s*an?\s+[A-Za-z ]+?\s*(?:corporation|company|partnership|"
    r"limited liability company)\s*$", re.I)
PARENTHETICAL_RE = re.compile(r"\s*[\(\[][^\)\]]*[\)\]]\s*$")
# Everything from these words on belongs to the sentence, not to the party's name.
TERM_CUT_RE = re.compile(
    r"\s+(?:pursuant|under|in connection|in accordance|for purposes|"
    r"with respect|effective|and thereafter|as successor)\b.*$", re.I)

L = []


def log(msg=""):
    print(msg)
    L.append(str(msg))


def flush():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "234_outcome_cik.md").write_text(chr(10).join(L) + chr(10), encoding="utf-8")


def abort(msg):
    log("")
    log("ABORT: " + str(msg))
    flush()
    sys.exit("ABORT: " + str(msg))


def require(p):
    if not Path(p).exists():
        abort("missing input: " + str(p) + " (no graceful fallback)")
    return Path(p)


# --------------------------------------------------------------- window
def fetch_window(bd, rd):
    """scripts/187 win_lo_ext / win_hi_ext, verbatim."""
    bd = pd.Timestamp(bd)
    rd_eff = bd if (rd is None or pd.isna(rd)) else pd.Timestamp(rd)
    return (min(bd, rd_eff) - timedelta(days=PRE_DAYS),
            max(bd, rd_eff) + timedelta(days=POST_DAYS))


# --------------------------------------------------------------- submissions
def load_pages(cik):
    for root in (SUBS_V4, SUBS):
        fp = root / (str(int(cik)) + ".json")
        if fp.exists():
            try:
                return json.loads(fp.read_text(encoding="utf-8", errors="replace"))
            except json.JSONDecodeError:
                return None
    return None


def count_8k(pages, lo, hi):
    """Form 8-K filings (8-K, 8-K/A, 8-K12B ...) with a filing date inside [lo, hi]."""
    n = 0
    for pg in pages or []:
        forms = pg.get("form") or []
        dates = pg.get("filingDate") or []
        for i, f in enumerate(forms):
            if not str(f).startswith("8-K") or i >= len(dates):
                continue
            d = pd.to_datetime(dates[i], errors="coerce")
            if pd.notna(d) and lo <= d <= hi:
                n += 1
    return n


# --------------------------------------------------------------- candidate 3
def predecessor_term(passage):
    """The party the successor became the successor issuer TO.

    The capture has to be cut: "... successor issuer to Old Disney pursuant to
    Rule 12g-3(a) ..." otherwise yields 'Old Disney pursuant to Rule 12g-3',
    which matches no defined term and no company.
    """
    m = SUCCESSOR_TO_RE.search(str(passage or ""))
    if not m:
        return ""
    term = re.sub(r"\s+", " ", m.group(1)).strip()
    return TERM_CUT_RE.sub("", term).strip(" ,;:“”\"'")


def resolve_definition(joined, term):
    """Legal name a document defines a quoted term to mean, or ''.

    The defining site looks like
        TWDC Enterprises 18 Corp. (formerly known as The Walt Disney Company)
            (" Old Disney ")
    so the window before the quoted term is stripped of trailing parentheticals
    and of a trailing ", a Delaware corporation" descriptor before the entity
    name is taken off the end.
    """
    if not term:
        return ""
    for mm in QUOTED_TERM_RE.finditer(joined):
        if re.sub(r"\s+", " ", mm.group(1)).strip().lower() != term.lower():
            continue
        win = joined[max(0, mm.start() - DEF_WINDOW):mm.start()]
        prev = None
        while prev != win:
            prev = win
            win = PARENTHETICAL_RE.sub("", win).rstrip()
            win = DESCRIPTOR_RE.sub("", win).rstrip()
        win = win.rstrip(" ,;:")
        hit = ENTITY_TAIL_RE.search(win)
        if hit:
            return re.sub(r"\s+", " ", hit.group(1)).strip()
    return ""


def load_name_index(path):
    """SEC cik-lookup-data.txt -> {UPPERCASE NAME: {cik, ...}}."""
    idx = {}
    with open(path, "r", encoding="latin-1", errors="replace") as fh:
        for line in fh:
            parts = line.strip().rstrip(":").rsplit(":", 1)
            if len(parts) != 2 or not parts[1].isdigit():
                continue
            idx.setdefault(parts[0].strip().upper(), set()).add(int(parts[1]))
    return idx


def name_to_cik(idx, name):
    """Unique match only. -> (cik, method) or (None, reason)."""
    if not name:
        return None, "no name extracted"
    key = name.strip().upper().rstrip(".")
    for cand in (key, key + ".", key.replace(".", ""), key.replace(",", "")):
        hit = idx.get(cand)
        if hit and len(hit) == 1:
            return next(iter(hit)), "SEC name index exact unique match"
        if hit and len(hit) > 1:
            return None, "SEC name index matched " + str(len(hit)) + " CIKs (ambiguous)"
    return None, "not found in SEC name index"


def doc_text(url, to_lines):
    """The cached document for a succession filing URL, as joined text."""
    if not url or not DOCS.exists():
        return ""
    base = str(url).rsplit("/", 1)[-1]
    for p in DOCS.glob("*_" + base):
        return " ".join(to_lines(p.read_bytes()))
    return ""


# --------------------------------------------------------------- resolution
def resolve_event(ev, succ, pages_of, idx, to_lines, doc_cache):
    """-> (row dict, [evidence dicts], [ciks needing submissions])."""
    lo, hi = fetch_window(ev["breach_date"], ev.get("reported_date"))
    cands = [("final_cik", ev["final_cik"])]
    if pd.notna(ev.get("orig_cik")) and int(ev["orig_cik"]) != int(ev["final_cik"]):
        cands.append(("orig_cik", int(ev["orig_cik"])))

    pred_cik, pred_name, pred_term, pred_method = None, "", "", ""
    # `or` is unusable here: succ values are pandas Series, whose truth value raises.
    bkey = str(ev["breach_date"])[:10]
    s = succ.get((int(ev["final_cik"]), bkey))
    if s is None and pd.notna(ev.get("orig_cik")):
        s = succ.get((int(ev["orig_cik"]), bkey))
    if s is not None:
        pred_term = predecessor_term(s.get("matching_line", ""))
        url = s.get("document_url", "")
        if url not in doc_cache:
            doc_cache[url] = doc_text(url, to_lines)
        pred_name = resolve_definition(doc_cache[url], pred_term)
        if not pred_name and pred_term:
            pred_name = pred_term          # already a literal name, not a defined term
        pred_cik, pred_method = name_to_cik(idx, pred_name)
        if pred_cik is not None and all(int(pred_cik) != int(c) for _, c in cands):
            cands.append(("predecessor", int(pred_cik)))

    # Pass 1: count every candidate, so the evidence file is complete either way.
    evid, need, counts = [], [], {}
    for label, cik in cands:
        pages = pages_of(cik)
        if pages is None:
            counts[label] = None
            need.append(int(cik))
            status = "submissions_not_cached"
            n = None
        else:
            n = count_8k(pages, lo, hi)
            counts[label] = n
            status = "ok"
        evid.append(dict(final_cik=ev["final_cik"], breach_date=str(ev["breach_date"])[:10],
                         org_name=ev.get("org_name", ""), candidate_rank=label,
                         candidate_cik=cik, n_8k_in_window=n, status=status,
                         win_lo=lo.date().isoformat(), win_hi=hi.date().isoformat(),
                         predecessor_term=pred_term if label == "predecessor" else "",
                         predecessor_name=pred_name if label == "predecessor" else "",
                         resolution=pred_method if label == "predecessor" else ""))

    # A succession filing that yielded no usable predecessor still leaves evidence,
    # so a failed extraction is visible instead of simply absent.
    if s is not None and not any(e["candidate_rank"] == "predecessor" for e in evid):
        evid.append(dict(final_cik=ev["final_cik"], breach_date=str(ev["breach_date"])[:10],
                         org_name=ev.get("org_name", ""), candidate_rank="predecessor",
                         candidate_cik=pred_cik, n_8k_in_window=None,
                         status=("duplicate_of_higher_rank" if pred_cik is not None
                                 else "predecessor_unresolved"),
                         win_lo=lo.date().isoformat(), win_hi=hi.date().isoformat(),
                         predecessor_term=pred_term, predecessor_name=pred_name,
                         resolution=pred_method))

    # Pass 2: walk the ranks in order. A candidate is only ruled out by a DEFINITE
    # zero. An uncached candidate blocks the walk - falling past it would hand the
    # event to a lower-ranked CIK purely because the better answer was not on disk,
    # which is how Xerox and J.B. Hunt first resolved to the subsidiary instead of
    # the parent.
    chosen, rule, blocked = None, "none", None
    for label, cik in cands:
        n = counts[label]
        if n is None:
            blocked = (label, int(cik))
            break
        if n >= 1:
            chosen, rule = int(cik), label
            break

    if chosen is not None:
        reason = ""
    elif blocked is not None:
        reason = ("submissions_not_cached for candidate " + blocked[0] + " "
                  + str(blocked[1]) + " - cannot rule it out; resolve after the 231 "
                  "fetch")
    else:
        reason = ("no candidate filed a Form 8-K in [" + lo.date().isoformat()
                  + ", " + hi.date().isoformat() + "] - fails the outcome-data "
                  "requirement")

    row = dict(
        final_cik=ev["final_cik"], breach_date=str(ev["breach_date"])[:10],
        org_name=ev.get("org_name", ""), treated=int(ev.get("fcc_form499", 0) or 0),
        orig_cik=ev.get("orig_cik"), link_basis=ev.get("link_basis", ""),
        outcome_cik=chosen, outcome_rule=rule,
        n_8k_final=counts.get("final_cik"), n_8k_orig=counts.get("orig_cik"),
        n_8k_pred=counts.get("predecessor"),
        predecessor_cik=pred_cik, predecessor_name=pred_name,
        predecessor_term=pred_term, predecessor_resolution=pred_method,
        differs_from_final=int(chosen is not None and int(chosen) != int(ev["final_cik"])),
        win_lo=lo.date().isoformat(), win_hi=hi.date().isoformat(),
        unresolved_reason=reason)
    return row, evid, need


def main():
    import importlib.util
    require(CANON)
    require(NAME_INDEX)
    for p in VERIFY_LOGS:
        require(p)
    spec = importlib.util.spec_from_file_location("m213", "scripts/213_stage3_verify.py")
    m213 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m213)

    canon = pd.read_csv(CANON, low_memory=False)
    vlog = pd.concat([pd.read_csv(p, low_memory=False) for p in VERIFY_LOGS],
                     ignore_index=True)
    succ = {}
    for _, r in vlog.iterrows():
        if str(r.get("verdict", "")).upper() != "VERIFIED":
            continue
        if str(r.get("candidate_type", "")) != "b_successor_cik":
            continue
        succ[(int(r["parent_cik"]), str(r["breach_date"])[:10])] = r
        succ[(int(r["cik"]), str(r["breach_date"])[:10])] = r

    log("# REBUILD V4 - outcome CIK resolution (scripts/234)")
    log("")
    log("Loading SEC name index ...")
    idx = load_name_index(NAME_INDEX)
    log("  names indexed: " + str(len(idx)))

    cache = {}

    def pages_of(cik):
        cik = int(cik)
        if cik not in cache:
            cache[cik] = load_pages(cik)
        return cache[cik]

    rows, evid, need, doc_cache = [], [], set(), {}
    for _, ev in canon.iterrows():
        r, e, n = resolve_event(ev, succ, pages_of, idx, m213.to_lines, doc_cache)
        rows.append(r)
        evid.extend(e)
        need.update(n)

    R = pd.DataFrame(rows)
    E = pd.DataFrame(evid)
    OUT.mkdir(parents=True, exist_ok=True)
    R.to_csv(OUT / "234_outcome_cik.csv", index=False)
    E.to_csv(OUT / "234_candidate_evidence.csv", index=False)
    need_sorted = sorted(need)
    (OUT / "234_submissions_needed.txt").write_text(
        chr(10).join(str(c) for c in need_sorted) + (chr(10) if need_sorted else ""),
        encoding="utf-8")

    log("")
    log("## Resolution")
    log("events                          : " + str(len(R)))
    log(R["outcome_rule"].value_counts().to_string())
    log("")
    log("outcome_cik != final_cik        : " + str(int(R["differs_from_final"].sum())))
    log("unresolved                      : " + str(int(R["outcome_cik"].isna().sum())))
    log("CIKs needing a submissions fetch: " + str(len(need_sorted)))

    d = R[R["differs_from_final"] == 1]
    if len(d):
        log("")
        log("## Events where outcome_cik != final_cik")
        log(d[["final_cik", "orig_cik", "outcome_cik", "outcome_rule", "org_name",
               "breach_date", "treated", "n_8k_final", "n_8k_orig",
               "n_8k_pred"]].sort_values(["org_name", "breach_date"]).to_string(index=False))

    u = R[R["outcome_cik"].isna()]
    if len(u):
        log("")
        log("## Unresolved")
        log(u[["final_cik", "org_name", "breach_date", "treated",
               "unresolved_reason"]].to_string(index=False))

    p = R[R["predecessor_cik"].notna()]
    if len(p):
        log("")
        log("## Predecessors extracted from succession filings")
        log(p[["final_cik", "org_name", "breach_date", "predecessor_term",
               "predecessor_name", "predecessor_cik",
               "predecessor_resolution"]].drop_duplicates().to_string(index=False))

    log("")
    log("written 234_outcome_cik.csv, 234_candidate_evidence.csv, "
        "234_submissions_needed.txt")
    flush()


if __name__ == "__main__":
    main()
