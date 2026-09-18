"""
REBUILD V4 — OFFLINE TEST SUITE (no WRDS, no SEC, no network of any kind)
=====================================================================================
    python scripts/217_v4_offline_tests.py        # exit 0 iff every test passes

Covers scripts 211 (WRDS pull), 212 (point-in-time linker) and 213 (EDGAR verification).
Every external dependency is mocked: WRDS through a fake connection object whose
raw_sql() returns canned frames, SEC EDGAR through a fake fetch() returning canned bytes.
Nothing here touches the network, WRDS, or any committed data file, and all temporary
output goes to a fresh temp directory that is removed at the end.

WHY THESE TESTS EXIST
---------------------
Each one corresponds to a failure that actually happened, or to a rule that is only
obvious until someone edits the code:

  211  every pull must ABORT on an empty result rather than write a short file; the
       CIK form (zero-padded vs not) must be retried; the sentinels must survive the
       WHOLE chain, because a 9-character Compustat CUSIP silently matches nothing in
       CRSP's 8-character ncusip; hit rates must count distinct keys, not rows; a
       mid-pull exception must still flush a redacted log; a top-up must never clobber.
  212  the identity gate must keep rejecting MetroPCS->T-Mobile and Fox->News Corp even
       as normalisation is loosened; letter-spaced initialisms must match themselves.
  213  a subsidiary that is NOT in the Exhibit 21 must come back UNVERIFIED, a match on
       an industry word alone must not verify, and a 403 must abort loudly instead of
       being recorded as an honest failure to verify.
"""
import importlib.util
import json
import shutil
import sys
import tempfile
from pathlib import Path

import pandas as pd

if not Path("scripts/211_wrds_pull_v4.py").exists():
    sys.exit("run this from the repository root: python scripts/217_v4_offline_tests.py")

TMP = Path(tempfile.mkdtemp(prefix="v4_offline_tests_"))
results = []


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


m = load("scripts/211_wrds_pull_v4.py", "m211")

SENT = [101830, 732717, 1283699]
GV = {101830: "001234", 732717: "002345", 1283699: "003456"}
CU9 = {101830: "85917110 8", 732717: "00206R10 2", 1283699: "87261210 9"}


# --------------------------------------------------------------- 211 fake WRDS frames
def company(ciks, padded=True, priusa=True):
    d = {"cik": [f"{c:010d}" if padded else str(c) for c in ciks],
         "gvkey": [GV.get(c, f"{900000+i:06d}") for i, c in enumerate(ciks)],
         "conm": [f"CO{c}" for c in ciks]}
    if priusa:
        d["priusa"] = ["01"] * len(ciks)
    return pd.DataFrame(d)


def security(ciks, nine_char=True, issues_per_gvkey=1):
    rows = []
    for c in ciks:
        g = GV.get(c, "999999")
        base = CU9.get(c, "12345678 9").replace(" ", "")
        for k in range(issues_per_gvkey):
            rows.append({"gvkey": g, "cusip": base if nine_char else base[:8],
                         "tic": f"T{k}", "exchg": 11})
    return pd.DataFrame(rows)


def stocknames(ciks, via="ncusip"):
    rows = []
    for i, c in enumerate(ciks):
        cu8 = CU9.get(c, "123456789").replace(" ", "")[:8]
        rows.append({"permno": 10000 + i, "namedt": "2005-01-01", "nameenddt": "2025-12-31",
                     "ncusip": cu8 if via == "ncusip" else "ZZZZZZZZ",
                     "cusip": cu8 if via == "cusip" else "YYYYYYYY",
                     "ticker": "X", "comnam": f"CO{c}", "shrcd": 11, "exchcd": 1})
    return pd.DataFrame(rows)


def dsf(n=3):
    return pd.DataFrame({"permno": [10000 + i for i in range(n)] * 2,
                         "date": ["2024-12-30"] * n + ["2024-12-31"] * n,
                         "ret": [0.01] * 2 * n, "retx": [0.01] * 2 * n,
                         "prc": [10.0] * 2 * n, "vol": [100] * 2 * n,
                         "shrout": [1000] * 2 * n})


def dsi():
    return pd.DataFrame({"date": ["2024-12-30", "2024-12-31"],
                         "vwretd": [0.001, 0.002], "ewretd": [0.001, 0.002]})


class MockDB:
    def __init__(self, **resp):
        self.resp = resp

    def raw_sql(self, sql):
        s = sql.lower()
        if "comp.company" in s:
            key = "company_padded" if "'00" in sql else "company_unpadded"
            return self.resp.get(key, pd.DataFrame()).copy()
        for needle, key in (("comp.security", "security"), ("stocknames", "names"),
                            ("crsp.dsf", "dsf"), ("crsp.dsi", "dsi")):
            if needle in s:
                return self.resp.get(key, pd.DataFrame()).copy()
        return pd.DataFrame()


def run(name, ciks, expect_abort, **resp):
    d = TMP / "pull"
    if d.exists():
        shutil.rmtree(d)
    d.mkdir(parents=True)
    m.reset_state()
    m.OUT_DATA, m.OUT_LOG = d, d / "log.md"
    print(f"\n{'='*70}\nTEST: {name}\n{'='*70}")
    try:
        m.run_pull(MockDB(**resp), ciks)
        got = None
    except SystemExit as e:
        got = str(e)
    ok = (expect_abort in got) if (expect_abort and got) else (expect_abort is None and got is None)
    print(f"  -> {'PASS' if ok else 'FAIL'} | {got or 'completed without abort'}")
    return ok


FULL = dict(company_padded=company(SENT), security=security(SENT),
            names=stocknames(SENT), dsf=dsf(), dsi=dsi())

# 1-5 empty results abort at each of the five pulls
results.append(run("comp.company empty (both forms)", SENT, "comp.company returned no rows",
                   **{**FULL, "company_padded": pd.DataFrame(), "company_unpadded": pd.DataFrame()}))
results.append(run("comp.security empty", SENT, "comp.security returned no rows",
                   **{**FULL, "security": pd.DataFrame()}))
results.append(run("crsp.stocknames empty", SENT, "crsp.stocknames returned no rows",
                   **{**FULL, "names": pd.DataFrame()}))
results.append(run("crsp.dsf empty", SENT, "crsp.dsf returned no rows",
                   **{**FULL, "dsf": pd.DataFrame()}))
results.append(run("crsp.dsi empty", SENT, "crsp.dsi returned no rows",
                   **{**FULL, "dsi": pd.DataFrame()}))

# 6 padded -> unpadded CIK retry
ok = run("padded->unpadded CIK retry", SENT, None,
         **{**FULL, "company_padded": pd.DataFrame(),
            "company_unpadded": company(SENT, padded=False)})
form = any("unpadded" in l for l in m.LOG)
print(f"  -> form logged as unpadded: {form}")
results.append(ok and form)

# 7 the CUSIP-length trap: Compustat 9-char vs CRSP 8-char ncusip
ok = run("CUSIP 9-char trimmed to 8 (the trap)", SENT, None, **FULL)
trimmed = any("trimmed to 8" in l for l in m.LOG)
reached = any("sentinels reached a permno" in l for l in m.LOG)
print(f"  -> trim logged: {trimmed} | sentinels reached permno: {reached}")
results.append(ok and trimmed and reached)

# 8-9 sentinels must break the run at the step where the chain actually breaks
results.append(run("sentinel breaks at CUSIP step", SENT, "reached no CUSIP",
                   **{**FULL, "security": security([101830, 732717])}))
results.append(run("sentinel breaks at permno step", SENT, "reached no permno",
                   **{**FULL, "names": stocknames([101830, 732717])}))

# 10 header-cusip fallback still reaches a permno
results.append(run("header cusip match (ncusip absent)", SENT, None,
                   **{**FULL, "names": stocknames(SENT, via="cusip")}))

# 11 CIK hit rate floor
ten = SENT + [999001, 999002, 999003, 999004, 999005, 999006, 999007]
results.append(run("CIK hit rate below 50%", ten, "below the 50% floor",
                   **{**FULL, "company_padded": company(SENT + [999001])}))

# 12 one gvkey, many issues -> rates count companies, never exceed 100%
ok = run("one-to-many gvkey->issue counted as companies", SENT, None,
         **{**FULL, "security": security(SENT, issues_per_gvkey=3)})
rates = {lab: rate for lab, _, _, rate in m.HIT_RATES}
sane = all(r <= 1.0 for r in rates.values())
print(f"  -> hit rates: { {k: f'{100*v:.0f}%' for k, v in rates.items()} } | all <=100%: {sane}")
results.append(ok and sane)

# 13 exception mid-pull -> abort, flushed log, password redacted
print(f"\n{'='*70}\nTEST: raised exception mid-pull -> abort + flushed redacted log\n{'='*70}")
d = TMP / "pull"
if d.exists():
    shutil.rmtree(d)
d.mkdir(parents=True)
m.reset_state()
m.OUT_DATA, m.OUT_LOG = d, d / "log.md"


class Raising(MockDB):
    def raw_sql(self, sql):
        if "comp.security" in sql.lower():
            raise RuntimeError("InsufficientPrivilege: denied password=hunter2")
        return super().raw_sql(sql)


try:
    m.safe_run_pull(Raising(**FULL), SENT)
    got = None
except SystemExit as e:
    got = str(e)
txt = (d / "log.md").read_text(encoding="utf-8") if (d / "log.md").exists() else ""
ok = bool(got and "unhandled RuntimeError" in got and "## ABORTED" in txt
          and "hunter2" not in txt and "REDACTED" in txt)
print(f"  -> {'PASS' if ok else 'FAIL'} | {got}")
print(f"  -> log written: {bool(txt)} | redacted: {'hunter2' not in txt}")
results.append(ok)

# 14 top-up suffix and no-clobber guard
print(f"\n{'='*70}\nTEST: top-up suffix and no-clobber\n{'='*70}")
d = TMP / "pull2"
d.mkdir(parents=True)
m.reset_state()
m.OUT_DATA, m.OUT_LOG = d, d / "log.md"
one = pd.DataFrame({"a": [1]})
m.SUFFIX = ""
m.write(one, "crsp_dsf.csv")
m.SUFFIX = "_topup_20261001T120000Z"
m.write(one, "crsp_dsf.csv")
names_ = sorted(p.name for p in d.iterdir() if p.suffix == ".csv")
coexist = names_ == ["crsp_dsf.csv", "crsp_dsf_topup_20261001T120000Z.csv"]
m.SUFFIX = ""
try:
    m.write(one, "crsp_dsf.csv")
    guard = False
except SystemExit as e:
    guard = "refusing to overwrite" in str(e)
print(f"  files: {names_}\n  -> coexist: {coexist} | clobber guard: {guard}")
results.append(coexist and guard)

# 15-17 required inputs ABORT in both scripts: no graceful fallback
print(f"\n{'='*70}\nTEST: missing required input aborts (211 CANON, 211 NOMS, 212 NOMS)\n{'='*70}")
GONE = Path("does/not/exist/crsp_drop_nominations.csv")


def expect_abort(fn, needle):
    try:
        fn()
        return False, "completed without abort"
    except SystemExit as e:
        return (needle in str(e)), str(e).replace("\n", " ")


_canon, _noms = m.CANON, m.NOMS
m.NOMS = GONE
ok_noms, msg_noms = expect_abort(m.load_base_ciks, "missing input")
m.NOMS = _noms
m.CANON = Path("does/not/exist/CANONICAL_V3.csv")
ok_canon, msg_canon = expect_abort(m.load_base_ciks, "missing input")
m.CANON = _canon
print(f"  211 NOMS missing  -> {'PASS' if ok_noms else 'FAIL'} | {msg_noms}")
print(f"  211 CANON missing -> {'PASS' if ok_canon else 'FAIL'} | {msg_canon}")
results += [ok_noms, ok_canon]

m212 = load("scripts/212_pit_linker_v4.py", "m212")
m212.NOMS = GONE
ok_212, msg_212 = expect_abort(m212.main, "missing input")
print(f"  212 NOMS missing  -> {'PASS' if ok_212 else 'FAIL'} | {msg_212}")
results.append(ok_212)

# 18 normalisation: initialism runs, concatenations, and the gate's negatives
print(f"\n{'='*70}\nTEST: 212 normalisation\n{'='*70}")
cases = [
    ("AT&T", "A T & T INC", True, "letter-spaced initialism"),
    ("EMC Corporation", "E M C CORP", True, "letter-spaced initialism"),
    ("TimeWarner", "TIME WARNER INC NEW", True, "space-stripped concatenation"),
    ("CenturyLink Communications", "CENTURYLINK INC", True, "same firm renamed"),
    ("T-Mobile", "METROPCS COMMUNICATIONS INC", False, "gate must still exclude"),
    ("Fox Entertainment Group", "NEWS CORP", False, "gate must still exclude"),
]
norm_ok = True
for a, b, want, why in cases:
    got = m212.names_match(a, b)
    norm_ok &= (got == want)
    print(f"  {'PASS' if got == want else 'FAIL'} | {a!r} vs {b!r} -> {got} ({why})")
results.append(norm_ok)

# 19 documented-identity test
print(f"\n{'='*70}\nTEST: 212 documented_identity\n{'='*70}")
doc_cases = [
    ("Gate1-A: active registrant", True),
    ("Gate1-G rescue: acronym defeated exact match", True),
    ("Gate2 CH-21: TALX filings end 2007", True),
    ("EDGAR name: EMC CORP", True),
    ("SEC EDGAR: Block Inc. (formerly Square Inc.)", True),
    ("AT&T Inc. - Cricket Communications FRN 0004321139; LLC variant", False),
    ("", False),
]
doc_ok = True
for ev, want in doc_cases:
    got = m212.documented_identity(ev)
    doc_ok &= (got == want)
    print(f"  {'PASS' if got == want else 'FAIL'} | {ev[:52]!r} -> {got}")
results.append(doc_ok)

# 20 generic-token guard
print(f"\n{'='*70}\nTEST: 212 generic-token guard\n{'='*70}")
gen_cases = [("Prime Communications", "VERIZON COMMUNICATIONS INC", True),
             ("CenturyLink Communications", "CENTURYLINK INC", False),
             ("Vulcan Industries", "ABM INDUSTRIES INC", True)]
gen_ok = True
for a, b, want_generic in gen_cases:
    _, shared = m212.name_overlap(a, b)
    got = m212.generic_only(shared)
    gen_ok &= (got == want_generic)
    print(f"  {'PASS' if got == want_generic else 'FAIL'} | {a!r} vs {b!r} -> "
          f"shared={sorted(shared)} generic_only={got}")
results.append(gen_ok)

# ----------------------------------------------------------- 213 with mocked EDGAR
m213 = load("scripts/213_stage3_verify.py", "m213")

PARENT_CIK, SUB_CIK = 1000045, 2000045
ACC = "0001047469-10-000123"
EX21_HTML = (b"<html><body><p>Subsidiaries of the Registrant</p>"
             b"<p>Northrop Grumman Systems Corporation &#8212; Delaware</p>"
             b"<p>Vinnell Corporation &#8212; Delaware</p>"
             b"<p>Verizon Communications Inc. &#8212; New York</p>"
             b"</body></html>")


def subs_json(form="10-K", fdate="2010-02-15", primary="a10k.htm", acc=ACC):
    return json.dumps({"filings": {"recent": {
        "form": [form], "accessionNumber": [acc], "filingDate": [fdate],
        "primaryDocument": [primary]}}}).encode()


def index_json(files):
    return json.dumps({"directory": {"item": [{"name": f} for f in files]}}).encode()


def make_fetch(pages):
    def _fetch(url):
        return pages.get(url)
    return _fetch


SUBS_URL = f"https://data.sec.gov/submissions/CIK{PARENT_CIK:010d}.json"
IDX_URL = (f"https://www.sec.gov/Archives/edgar/data/{PARENT_CIK}/"
           f"{ACC.replace('-', '')}/index.json")
EX_URL = m213.doc_url(PARENT_CIK, ACC, "ex21.htm")

BASE_PAGES = {SUBS_URL: subs_json(), IDX_URL: index_json(["a10k.htm", "ex21.htm"]),
              EX_URL: EX21_HTML}

print(f"\n{'='*70}\nTEST: 213 Exhibit 21 verification (mocked EDGAR)\n{'='*70}")
_real_fetch = m213.fetch
sub_ok = True

m213.fetch = make_fetch(BASE_PAGES)
r = m213.verify_subsidiary(PARENT_CIK, "Northrop Grumman Systems Corporation", "2010-03-01")
hit = (r["verdict"] == "VERIFIED" and r["accession"] == ACC and "Northrop" in r["matching_line"])
sub_ok &= hit
print(f"  {'PASS' if hit else 'FAIL'} | listed subsidiary -> {r['verdict']} "
      f"acc={r['accession']} line={r['matching_line'][:48]!r}")

# THE ONE THAT MATTERS: a subsidiary that is NOT in the Exhibit 21
r = m213.verify_subsidiary(PARENT_CIK, "Acme Unrelated Holdings", "2010-03-01")
miss = (r["verdict"] == "UNVERIFIED" and "does not list" in r["reason"])
sub_ok &= miss
print(f"  {'PASS' if miss else 'FAIL'} | NOT-listed subsidiary -> {r['verdict']} "
      f"| {r['reason'][:60]}")

# a match on an industry word alone must not verify
r = m213.verify_subsidiary(PARENT_CIK, "Prime Communications", "2010-03-01")
gen = (r["verdict"] == "UNVERIFIED")
sub_ok &= gen
print(f"  {'PASS' if gen else 'FAIL'} | generic-token-only line -> {r['verdict']} "
      f"| {r['reason'][:60]}")

# no 10-K inside the 18-month window
r = m213.verify_subsidiary(PARENT_CIK, "Northrop Grumman Systems Corporation", "2020-03-01")
win = (r["verdict"] == "UNVERIFIED" and "within" in r["reason"])
sub_ok &= win
print(f"  {'PASS' if win else 'FAIL'} | 10-K outside 18 months -> {r['verdict']} "
      f"| {r['reason'][:60]}")

# a 10-K with no Exhibit 21
m213.fetch = make_fetch({**BASE_PAGES, IDX_URL: index_json(["a10k.htm"])})
r = m213.verify_subsidiary(PARENT_CIK, "Northrop Grumman Systems Corporation", "2010-03-01")
noex = (r["verdict"] == "UNVERIFIED" and "Exhibit 21" in r["reason"])
sub_ok &= noex
print(f"  {'PASS' if noex else 'FAIL'} | no Exhibit 21 -> {r['verdict']} | {r['reason'][:60]}")

# unresolved parent CIK is never guessed
r = m213.verify_subsidiary(None, "Anything", "2010-03-01")
nocik = (r["verdict"] == "UNVERIFIED" and "could not be resolved" in r["reason"])
sub_ok &= nocik
print(f"  {'PASS' if nocik else 'FAIL'} | unresolved parent CIK -> {r['reason'][:60]}")
results.append(sub_ok)

print(f"\n{'='*70}\nTEST: 213 successor verification (mocked EDGAR)\n{'='*70}")
SACC = "0001047469-13-000999"
S_SUBS = f"https://data.sec.gov/submissions/CIK{SUB_CIK:010d}.json"
S_DOC = m213.doc_url(SUB_CIK, SACC, "d8k.htm")
succ_pages = {
    S_SUBS: subs_json(form="8-K12G3", fdate="2013-04-30", primary="d8k.htm", acc=SACC),
    S_DOC: b"<html><body><p>successor issuer to Sinclair Broadcast Group, Inc.</p></body></html>",
    f"https://data.sec.gov/submissions/CIK{PARENT_CIK:010d}.json": subs_json(),
}
m213.fetch = make_fetch(succ_pages)
r = m213.verify_successor(PARENT_CIK, "Sinclair Broadcast Group, Inc.", SUB_CIK, "SINCLAIR INC")
sok = (r["verdict"] == "VERIFIED" and r["accession"] == SACC and "12G3" in r["form"])
print(f"  {'PASS' if sok else 'FAIL'} | 8-K12G3 names predecessor -> {r['verdict']} "
      f"acc={r['accession']} form={r['form']}")

m213.fetch = make_fetch({S_SUBS: succ_pages[S_SUBS],
                         S_DOC: b"<html><body><p>unrelated announcement</p></body></html>",
                         f"https://data.sec.gov/submissions/CIK{PARENT_CIK:010d}.json": subs_json()})
r = m213.verify_successor(PARENT_CIK, "Sinclair Broadcast Group, Inc.", SUB_CIK, "SINCLAIR INC")
snone = (r["verdict"] == "UNVERIFIED" and "no 8-K or 12g-3" in r["reason"])
print(f"  {'PASS' if snone else 'FAIL'} | no filing names the other -> {r['verdict']} "
      f"| {r['reason'][:60]}")
results.append(sok and snone)

print(f"\n{'='*70}\nTEST: 213 helpers and fair-access guards\n{'='*70}")
m213.fetch = _real_fetch
lines = m213.to_lines(EX21_HTML)
lines_ok = any("Vinnell Corporation" in l for l in lines)
ex_ok = m213.find_ex21_name(["a10k.htm", "dex211.htm"]) == "dex211.htm"
none_ok = m213.find_ex21_name(["a10k.htm", "graphic.jpg"]) is None
rate_ok = m213.MIN_INTERVAL >= 0.1
import os as _os
_saved_ua = _os.environ.pop(m213.UA_ENV, None)
ua_ok, ua_msg = expect_abort(m213.user_agent, m213.UA_ENV)
if _saved_ua is not None:
    _os.environ[m213.UA_ENV] = _saved_ua
print(f"  {'PASS' if lines_ok else 'FAIL'} | to_lines splits the exhibit into lines")
print(f"  {'PASS' if ex_ok and none_ok else 'FAIL'} | find_ex21_name picks dex211.htm, "
      f"None when absent")
print(f"  {'PASS' if rate_ok else 'FAIL'} | MIN_INTERVAL {m213.MIN_INTERVAL}s <= 10 req/s")
print(f"  {'PASS' if ua_ok else 'FAIL'} | missing {m213.UA_ENV} aborts | {ua_msg[:60]}")
results.append(lines_ok and ex_ok and none_ok and rate_ok and ua_ok)

# ------- the run-1 failures, as permanent regression tests -------
print(f"\n{'='*70}\nTEST: 213 evidence standard (the run-1 canaries)\n{'='*70}")
name_cases = [
    # (subsidiary/firm name, candidate line, must_match, why)
    ("Brown, Lisle/Cummings, Inc.", "Brown-Forman Corporation", False,
     "single SURNAME overlap must FAIL (run-1 canary)"),
    ("Communications & Power Industries LLC", "AMERICAN ELECTRIC POWER COMPANY, INC.",
     False, "single WORD overlap (POWER) must FAIL (run-1 canary)"),
    ("Cricket Wireless LLC", "New Cingular Wireless", False,
     "single word (WIRELESS) must FAIL"),
    ("Northrop Grumman Systems Corporation",
     "Northrop Grumman Systems Corporation — Delaware", True,
     "exact listing line must VERIFY"),
    ("TimeWarner", "Time Warner Inc.", True,
     "space-stripped concatenation must VERIFY"),
    ("International Paper Company", "International Paper Company", True,
     "full-name listing must VERIFY"),
]
ev_ok = True
for nm, line, want, why in name_cases:
    got, tokens = m213.line_names(nm, line)
    ev_ok &= (got == want)
    print(f"  {'PASS' if got == want else 'FAIL'} | {nm[:34]!r} vs {line[:38]!r} -> {got}"
          f"  ({why})")
results.append(ev_ok)

print(f"\n{'='*70}\nTEST: 213 succession language required in the same passage\n{'='*70}")
NAMED_NO_LANG = "Sinclair Broadcast Group, Inc. reported quarterly results today."
NAMED_WITH_LANG = ("Sinclair, Inc. is the successor issuer to Sinclair Broadcast Group, "
                   "Inc. pursuant to Rule 12g-3(a).")
LANG_NO_NAME = "The registrant is the successor issuer pursuant to Rule 12g-3(a)."
p1, _ = m213.match_passage("Sinclair Broadcast Group, Inc.", [NAMED_NO_LANG])
p2, ev2 = m213.match_passage("Sinclair Broadcast Group, Inc.", [NAMED_WITH_LANG])
p3, _ = m213.match_passage("Sinclair Broadcast Group, Inc.", [LANG_NO_NAME])
succ_ok = (p1 is None) and (p2 is not None) and (p3 is None)
print(f"  {'PASS' if p1 is None else 'FAIL'} | named, NO succession language -> {p1}")
print(f"  {'PASS' if p2 else 'FAIL'} | named + succession language -> matched on {ev2}")
print(f"  {'PASS' if p3 is None else 'FAIL'} | succession language, name absent -> {p3}")
results.append(succ_ok)

print(f"\n{'='*70}\nTEST: 213 exhibit selection (the Fox false negative)\n{'='*70}")
NEWSCORP_FILES = ["d10k.htm", "dex106.htm", "dex121.htm", "dex21.htm", "dex231.htm",
                  "dex311.htm", "dex312.htm", "dex321.htm"]
picked = m213.find_ex21_name(NEWSCORP_FILES)
fox_ok = picked == "dex21.htm"
print(f"  {'PASS' if fox_ok else 'FAIL'} | News Corp 2009 10-K files -> picked {picked!r} "
      f"(must be dex21.htm, NOT dex121.htm = Exhibit 12.1)")
also_ok = (m213.find_ex21_name(["dex121.htm"]) is None
           and m213.find_ex21_name(["dex321.htm"]) is None)
print(f"  {'PASS' if also_ok else 'FAIL'} | Exhibit 12.1 and 32.1 alone -> None")
results.append(fox_ok and also_ok)

print(f"\n{'='*70}")
print(f"RESULT: {sum(results)}/{len(results)} tests passed")
print("=" * 70)
shutil.rmtree(TMP, ignore_errors=True)
sys.exit(0 if all(results) else 1)
