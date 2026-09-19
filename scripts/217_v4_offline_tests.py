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
    # run-3 false positives, using the exact lines run 3 accepted
    ("Fox Entertainment Group", "Fortune Star Entertainment (HK) Limited", False,
     "run-3 FP: FOX is 3 chars so only ENTERTAINMENT was required"),
    ("Fox Entertainment Group", "FOX ENTERTAINMENT GROUP, INC.", True,
     "the genuine News Corp Ex-21 entry must VERIFY"),
    ("Xerox Corporation", "Subsidiaries of Xerox Holdings Corporation", False,
     "run-3 FP: the exhibit's own HEADING must FAIL"),
    ("Xerox Corporation", "Xerox Corporation                    New York", True,
     "the genuine Xerox entry must VERIFY"),
    ("Leidos, Inc.", "12. Leidos, Inc. — Delaware", True,
     "leading numbering must be stripped"),
    ("Fox Entertainment Group", "Fox Entertainment Group Holdings Inc. — Delaware", False,
     "HOLDINGS is a NAME token, so this is a different entity (was True pre-ruling)"),
    # entity-form ruling: HOLDINGS/GROUP are name tokens; only the narrow form set is a
    # suffix, and the line's form must match the subsidiary's
    ("Xerox Corporation", "Xerox Holdings Corporation", False,
     "run-4 FP: the PARENT must FAIL"),
    ("Xerox Corporation", "Xerox AG", False, "entity form AG != CORP"),
    ("Xerox Corporation", "Xerox Limited", False, "entity form LTD != CORP"),
    ("Xerox Corporation", "Xerox Holdings, Inc.", False, "HOLDINGS is a name token"),
    ("Xerox Corporation", "Xerox GmbH", False, "entity form GMBH != CORP"),
    ("Xerox Corporation", "Xerox S.p.A.", False, "entity form SPA != CORP"),
    ("Xerox Corporation", "Xerox Ventures LLC", False, "VENTURES is a name token"),
    # boundary rule: these names reduce to ONE token once legal suffixes are dropped,
    # so a bare prefix would match any longer firm beginning with that word
    ("Xerox Corporation", "Xerox Financial Services LLC — Delaware", False,
     "boundary: [XEROX] must not match a different Xerox entity"),
    ("Leidos, Inc.", "Leidos Biomedical Research, Inc.", False,
     "boundary: [LEIDOS] must not match Leidos Biomedical Research"),
    ("Leidos, Inc.", "Leidos, Inc. — Delaware", True,
     "boundary: comma ends the name, so the genuine entry VERIFIES"),
    ("Fox", "Fox Baseball Holdings, Inc.", False,
     "boundary: a bare single token must not match a longer entry"),
    ("Dell Inc.", "Dell Technologies Inc.", False,
     "boundary: [DELL] must not match Dell Technologies"),
    ("Aon Corporation PLC", "Aon Service Corporation", False,
     "boundary: [AON] must not match Aon Service Corporation"),
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
MERGER_ONLY = ("Sinclair, Inc. completed its merger with Sinclair Broadcast Group, Inc. "
               "and the merged entity will continue to operate the stations.")
AON_STYLE = ("Aon plc is the successor issuer to Aon Corporation PLC pursuant to "
             "Rule 12g-3(a) under the Exchange Act.")
# the two passages run 3 actually verified on, verbatim
TRUSTEE = ("On October 25, 2023, Lennar Corporation (the “Company”) issued a "
           "notice that pursuant to Section 2.02 of that certain Eleventh Supplemental "
           "Indenture dated as of November 5, 2015 (the “Supplemental Indenture”) "
           "among the Company, the guarantors named therein and The Bank of New York "
           "Mellon (as successor trustee).")
SINCLAIR_CREDIT = ("Seventh Amendment, dated as of February 12, 2025, to Seventh Amended "
                   "and Restated Credit Agreement, by and among Sinclair Television "
                   "Group, Inc., Sinclair Broadcast Group, LLC (formerly Sinclair "
                   "Broadcast Group, Inc.), the guarantors party thereto, the lenders "
                   "party thereto, JPMorgan Chase Bank, N.A.")
p1, _ = m213.match_passage("Sinclair Broadcast Group, Inc.", [NAMED_NO_LANG])
p2, ev2 = m213.match_passage("Sinclair Broadcast Group, Inc.", [NAMED_WITH_LANG])
p3, _ = m213.match_passage("Sinclair Broadcast Group, Inc.", [LANG_NO_NAME])
p4, _ = m213.match_passage("Sinclair Broadcast Group, Inc.", [MERGER_ONLY])
p5, ev5 = m213.match_passage("Aon Corporation PLC", [AON_STYLE])
p6, _ = m213.match_passage("Lennar Corporation", [TRUSTEE])
p7, _ = m213.match_passage("Sinclair Broadcast Group, Inc.", [SINCLAIR_CREDIT])
succ_ok = all([p1 is None, p2 is not None, p3 is None, p4 is None, p5 is not None,
               p6 is None, p7 is None])
print(f"  {'PASS' if p1 is None else 'FAIL'} | named, NO succession language -> {p1}")
print(f"  {'PASS' if p2 else 'FAIL'} | named + succession language -> matched on {ev2}")
print(f"  {'PASS' if p3 is None else 'FAIL'} | succession language, name absent -> {p3}")
print(f"  {'PASS' if p4 is None else 'FAIL'} | named + MERGER language only -> {p4} "
      f"(merger is not succession)")
print(f"  {'PASS' if p5 else 'FAIL'} | 8-K12B 'successor issuer ... Rule 12g-3' -> "
      f"matched on {ev5}")
print(f"  {'PASS' if p6 is None else 'FAIL'} | run-3 FP: 'successor TRUSTEE' indenture "
      f"passage -> {p6}")
print(f"  {'PASS' if p7 is None else 'FAIL'} | run-3 FP: Sinclair credit-agreement "
      f"exhibit index -> {p7}")
results.append(succ_ok)

print(f"\n{'='*70}\nTEST: 211 --extra-ciks reader (213's output format)\n{'='*70}")
_x = TMP / "extra_ciks.txt"
_x.write_bytes(("# REBUILD V4 Stage 3 - verified CIKs not among the 185 already pulled\r\n"
                "# generated 2026-09-18T23:48:23Z by scripts/213_stage3_verify.py\r\n"
                "\r\n"
                "718877   # Activision Blizzard, Inc.\r\n"
                "51434\t# International Paper Co /NEW/\r\n"
                "  920760  \r\n").encode())
got = m.read_extra_ciks(str(_x))
x1 = got == {718877, 51434, 920760}
print(f"  {'PASS' if x1 else 'FAIL'} | header + inline comments + CRLF + blank + padding "
      f"-> {sorted(got)}")
_y = TMP / "extra_bad.txt"
_y.write_text("718877\nnot-a-cik\n", encoding="utf-8")
x2, msg = expect_abort(lambda: m.read_extra_ciks(str(_y)), "cannot read a CIK")
print(f"  {'PASS' if x2 else 'FAIL'} | unparseable line aborts loudly | {msg[:60]}")
# the real file 213 writes must parse to exactly its CIKs
_real = Path("outputs/rebuild_v4/213_extra_ciks.txt")
if _real.exists():
    rg = m.read_extra_ciks(str(_real))
    x3 = rg == {718877}
    print(f"  {'PASS' if x3 else 'FAIL'} | the real 213_extra_ciks.txt -> {sorted(rg)}")
else:
    x3 = True
    print("  SKIP | 213_extra_ciks.txt not present")
results.append(x1 and x2 and x3)

print(f"\n{'='*70}\nTEST: 213 defined-term aliases (the Sinclair split)\n{'='*70}")
SBG_DEF = ('As previously disclosed, on April 3, 2023, the company formerly known as '
           'Sinclair Broadcast Group, Inc., a Maryland corporation (“ SBG ”), entered '
           'into an Agreement of Share Exchange and Plan of Reorganization.')
SBG_OPERATIVE = ('that, following the Share Exchange, New Sinclair became the successor '
                 'issuer to SBG. More specifically, pursuant to Exchange Act Rule '
                 '12g-3(a), the New Sinclair Class A Common Shares are deemed registered.')
SBG_DOC = [SBG_DEF, SBG_OPERATIVE]
NAME = "Sinclair Broadcast Group, Inc."

al = m213.document_aliases(NAME, SBG_DOC)
a1 = "SBG" in al
p, ev = m213.match_passage(NAME, SBG_DOC, al)
a2 = (p == SBG_OPERATIVE)
print(f"  {'PASS' if a1 else 'FAIL'} | alias extracted from the joined text: {sorted(al)}")
print(f"  {'PASS' if a2 else 'FAIL'} | operative passage VERIFIES via alias ({ev})")

# without the alias the same passage must still fail - it never names the firm
p0, _ = m213.match_passage(NAME, [SBG_OPERATIVE])
a3 = p0 is None
print(f"  {'PASS' if a3 else 'FAIL'} | same passage WITHOUT aliases -> {p0}")

# an alias defined for a different company must not transfer
OTHER = ['Acme Unrelated Industries, Inc., a Delaware corporation (“ACME”), did things.',
         'New Acme became the successor issuer to ACME pursuant to Rule 12g-3(a).']
a4 = not m213.document_aliases(NAME, OTHER)
p4, _ = m213.match_passage(NAME, OTHER, m213.document_aliases(NAME, OTHER))
a4 = a4 and p4 is None
print(f"  {'PASS' if a4 else 'FAIL'} | alias defined for another firm does not transfer")

# generic defined terms never become aliases
GEN = ['Sinclair Broadcast Group, Inc., a Maryland corporation (the “Company”), reported.',
       'the Company became the successor issuer pursuant to Rule 12g-3(a).']
gal = m213.document_aliases(NAME, GEN)
p5, _ = m213.match_passage(NAME, GEN, gal)
a5 = ("Company" not in gal) and p5 is None
print(f"  {'PASS' if a5 else 'FAIL'} | generic term never an alias: {sorted(gal)} -> {p5}")

# unquoted parentheticals are not defined terms
UNQ = ['Sinclair Broadcast Group, Inc. (Commission File Number 001-12925) filed this.',
       'Commission File Number was the successor issuer pursuant to Rule 12g-3(a).']
a6 = not m213.document_aliases(NAME, UNQ)
print(f"  {'PASS' if a6 else 'FAIL'} | unquoted parenthetical is not an alias: "
      f"{sorted(m213.document_aliases(NAME, UNQ))}")

# a LATER defined term in the same sentence must not be adopted as the company's alias.
# This is the real Sinclair wording: at a 200-char window the agreement's term became an
# alias for the company and the verification rested on it.
FALSE_ALIAS = [
    'As previously disclosed, on April 3, 2023, the company formerly known as Sinclair '
    'Broadcast Group, Inc., a Maryland corporation (“SBG”), entered into an Agreement of '
    'Share Exchange and Plan of Reorganization, dated as of April 3, 2023, by and among '
    'the parties thereto (the “Share Exchange Agreement”), providing for the transaction.',
    'The purpose of the transactions contemplated by the Share Exchange Agreement was to '
    'effect a holding company reorganization.']
fal = m213.document_aliases(NAME, FALSE_ALIAS)
a7 = (fal == {"SBG"})
print(f"  {'PASS' if a7 else 'FAIL'} | only the adjacent term is an alias: {sorted(fal)} "
      f"(must be ['SBG'], NOT 'Share Exchange Agreement')")
# the STRONGEST succession phrase wins, even when a weaker one comes first
ORDER_DOC = [
    'Sinclair Broadcast Group, Inc., a Maryland corporation (“SBG”), did things.',
    'The purpose of the transactions was to effect a holding company reorganization in '
    'which New Sinclair would become the publicly-traded parent of SBG.',
    'Following the Share Exchange, New Sinclair became the successor issuer to SBG '
    'pursuant to Exchange Act Rule 12g-3(a).']
oal = m213.document_aliases(NAME, ORDER_DOC)
op, oev = m213.match_passage(NAME, ORDER_DOC, oal)
a8 = (op == ORDER_DOC[2])
print(f"  {'PASS' if a8 else 'FAIL'} | strongest phrase wins over document order -> "
      f"{'successor issuer passage' if a8 else op}")
# and a weak-only document still verifies on the weak passage
WEAK_ONLY = [ORDER_DOC[0], ORDER_DOC[1]]
wp, _ = m213.match_passage(NAME, WEAK_ONLY, m213.document_aliases(NAME, WEAK_ONLY))
a9 = (wp == ORDER_DOC[1])
print(f"  {'PASS' if a9 else 'FAIL'} | weak-only document still verifies on the weak "
      f"passage")
results.append(all([a1, a2, a3, a4, a5, a6, a7, a8, a9]))

print(f"\n{'='*70}\nTEST: 213 Exhibit 21 selection by DOCUMENT TYPE\n{'='*70}")
JBH_CIK, JBH_ACC = 728535, "0001437749-20-004119"
JBH_FILES = ["ex_174335.htm", "ex_174336.htm", "ex_174405.htm", "jbht20191231_10k.htm"]
HDR_RAW = ("<html><pre>\n"
           "<DOCUMENT>\n<TYPE>10-K\n<SEQUENCE>1\n<FILENAME>jbht20191231_10k.htm\n</DOCUMENT>\n"
           "<DOCUMENT>\n<TYPE>EX-21\n<SEQUENCE>5\n<FILENAME>ex_174335.htm\n</DOCUMENT>\n"
           "<DOCUMENT>\n<TYPE>EX-32.1\n<SEQUENCE>8\n<FILENAME>ex_174405.htm\n</DOCUMENT>\n"
           "</pre></html>").encode()
HDR_ESCAPED = (HDR_RAW.decode().replace("<DOCUMENT>", "&lt;DOCUMENT&gt;")
               .replace("<TYPE>", "&lt;TYPE&gt;").replace("<SEQUENCE>", "&lt;SEQUENCE&gt;")
               .replace("<FILENAME>", "&lt;FILENAME&gt;")
               .replace("</DOCUMENT>", "&lt;/DOCUMENT&gt;")).encode()
HDR_URL = (f"https://www.sec.gov/Archives/edgar/data/{JBH_CIK}/"
           f"{JBH_ACC.replace('-', '')}/{JBH_ACC}-index-headers.html")

_svf = m213.fetch
type_ok = True
for label, payload in (("raw SGML", HDR_RAW), ("HTML-escaped", HDR_ESCAPED)):
    m213.fetch = make_fetch({HDR_URL: payload})
    got, how = m213.pick_ex21(JBH_CIK, JBH_ACC, JBH_FILES)
    one = (got == "ex_174335.htm" and "EX-21" in how)
    type_ok &= one
    print(f"  {'PASS' if one else 'FAIL'} | {label}: J.B. Hunt ex_174335.htm found by "
          f"type ({how}) — no filename rule could")

# the type route must never pick EX-32.1, and must not be fooled when the header is absent
m213.fetch = make_fetch({})
got, how = m213.pick_ex21(JBH_CIK, JBH_ACC, JBH_FILES)
nohdr_ok = got is None
print(f"  {'PASS' if nohdr_ok else 'FAIL'} | no header available and no Ex-21 filename "
      f"-> {got}")
m213.fetch = make_fetch({})
got, how = m213.pick_ex21(1, "0000000000-00-000000", ["exhibit21.htm", "dex321.htm"])
fb_ok = (got == "exhibit21.htm" and "filename" in how)
print(f"  {'PASS' if fb_ok else 'FAIL'} | filename fallback finds exhibit21.htm ({how})")
m213.fetch = _svf

names_seen = ["w47962exv21.htm", "a202210k-exhibit21q42022.htm",
              "exhibit21-ihmedia2024q4.htm", "gtes-exhibit211xq42022.htm",
              "a2017123110-kaexhibit21.htm", "exhibit21.htm", "dex21.htm"]
decoys = ["dex121.htm", "dex321.htm", "exhibit321-ihmedia2024q4.htm",
          "gtes-exhibit321xq42022.htm", "a2017123110-kaexhibit32.htm", "w47962exv23.htm",
          "exhibit23-ihmedia2024q4.htm"]
fn_hit = [n for n in names_seen if m213.find_ex21_name([n]) == n]
fn_bad = [n for n in decoys if m213.find_ex21_name([n])]
print(f"  {'PASS' if len(fn_hit) == len(names_seen) else 'FAIL'} | broadened filename "
      f"finds {len(fn_hit)}/{len(names_seen)} real Ex-21 names")
print(f"  {'PASS' if not fn_bad else 'FAIL'} | EX-12.1 / EX-32.1 / EX-23 never selected "
      f"{fn_bad or ''}")
results.append(type_ok and nohdr_ok and fb_ok and len(fn_hit) == len(names_seen)
               and not fn_bad)

print(f"\n{'='*70}\nTEST: 213 parent nomination from cik-lookup-data.txt\n{'='*70}")
if not m213.CIK_LOOKUP.exists():
    print(f"  SKIP | {m213.CIK_LOOKUP} not present on this machine")
    results.append(True)
else:
    got = m213.lookup_ciks({"Activision Blizzard, Inc.", "Volkswagen AG",
                            "Zzzz Nonexistent Holdings Inc."})
    av = got.get("Activision Blizzard, Inc.", (None, ""))
    vw = got.get("Volkswagen AG", (None, ""))
    nx = got.get("Zzzz Nonexistent Holdings Inc.", (None, ""))
    look_ok = (av[0] == 718877 and vw[0] == 1111708 and nx[0] is None)
    print(f"  {'PASS' if av[0] == 718877 else 'FAIL'} | Activision Blizzard, Inc. -> "
          f"{av[0]} ({av[1]})")
    print(f"  {'PASS' if vw[0] == 1111708 else 'FAIL'} | Volkswagen AG -> {vw[0]} "
          f"({vw[1]})  [not the AUTO LEASE TRUSTs or the /ADR/ entry]")
    print(f"  {'PASS' if nx[0] is None else 'FAIL'} | absent name -> {nx[0]} ({nx[1]})")
    results.append(look_ok)

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

# ------- 213 transport: retries, and never caching an error page -------
print(f"\n{'='*70}\nTEST: 213 retry/backoff and error-page handling (mocked HTTP)\n{'='*70}")
import os as _os2
from email.message import Message
from urllib.error import HTTPError as _HTTPError

FILING = b"<html><body>" + b"Northrop Grumman Systems Corporation " * 120 + b"</body></html>"
THROTTLE = (b"<html><h1>SEC.gov | Request Rate Threshold Exceeded</h1>"
            b"<p>Your Request Originates from an Undeclared Automated Tool</p></html>")


class FakeResp:
    def __init__(self, data, status=200):
        self._d, self.status = data, status

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def read(self):
        return self._d


def scripted(seq):
    """Fake urlopen replaying `seq`; an Exception entry is raised, bytes are returned."""
    state = {"n": 0}

    def _open(req, timeout=None):
        item = seq[min(state["n"], len(seq) - 1)]
        state["n"] += 1
        if isinstance(item, BaseException):
            raise item
        return FakeResp(item)
    return _open, state


def http_err(code, retry_after=None):
    h = Message()
    if retry_after is not None:
        h["Retry-After"] = str(retry_after)
    return _HTTPError("https://www.sec.gov/x", code, "err", h, None)


_sv = dict(cache=m213.CACHE, mi=m213.MIN_INTERVAL, bb=m213.BACKOFF_BASE,
           uo=m213.urlopen, ol=m213.OUT_LOG, oc=m213.OUT_CIKS, rl=m213.RUN_LOG,
           q=m213.QUARANTINE)
_ua_prev = _os2.environ.get(m213.UA_ENV)
_os2.environ[m213.UA_ENV] = "Offline Test test@example.com"
m213.CACHE = TMP / "cache"
m213.QUARANTINE = TMP / "quarantine"
m213.MIN_INTERVAL = 0.0
m213.BACKOFF_BASE = 0.0

# 503 then 200 -> succeeds, and the good bytes land in the cache
m213.urlopen, calls = scripted([http_err(503), FILING])
got = m213.fetch("https://www.sec.gov/Archives/edgar/data/1/a/retry_ok.htm")
retry_ok = (got == FILING and calls["n"] == 2
            and m213.cache_path("https://www.sec.gov/Archives/edgar/data/1/a/retry_ok.htm").exists())
print(f"  {'PASS' if retry_ok else 'FAIL'} | 503 then 200 -> recovered in {calls['n']} "
      f"attempts, cached")

# persistent 503 -> raises after MAX_ATTEMPTS, nothing cached
m213.urlopen, calls = scripted([http_err(503)])
try:
    m213.fetch("https://www.sec.gov/Archives/edgar/data/1/a/always503.htm")
    persist_ok, why = False, "returned instead of raising"
except RuntimeError as e:
    persist_ok = (calls["n"] == m213.MAX_ATTEMPTS
                  and not m213.cache_path("https://www.sec.gov/Archives/edgar/data/1/a/always503.htm").exists())
    why = str(e)[:56]
print(f"  {'PASS' if persist_ok else 'FAIL'} | persistent 503 -> {calls['n']} attempts "
      f"then raise, nothing cached | {why}")

# HTTP 200 carrying a throttle page -> NEVER cached (the dangerous case)
m213.urlopen, calls = scripted([THROTTLE])
try:
    m213.fetch("https://www.sec.gov/Archives/edgar/data/1/a/throttle.htm")
    err_ok = False
except RuntimeError:
    err_ok = not m213.cache_path("https://www.sec.gov/Archives/edgar/data/1/a/throttle.htm").exists()
print(f"  {'PASS' if err_ok else 'FAIL'} | 200 + throttle body -> never cached, retried "
      f"{calls['n']}x then raised")

# 404 is an answer, not a failure
m213.urlopen, calls = scripted([http_err(404)])
none_ok = m213.fetch("https://www.sec.gov/Archives/edgar/data/1/a/missing.htm") is None
print(f"  {'PASS' if none_ok else 'FAIL'} | 404 -> None after {calls['n']} attempt")

# transport failures that are NOT HTTP errors: a read timeout fires inside r.read(), and
# TimeoutError is a sibling of URLError under OSError, so it reached neither handler and
# killed run 3. Each must recover on the next attempt.
from http.client import IncompleteRead as _IncompleteRead
from http.client import RemoteDisconnected as _RemoteDisconnected

TRANSIENT_CASES = [
    ("TimeoutError", TimeoutError("The read operation timed out")),
    ("ConnectionResetError", ConnectionResetError(10054, "forcibly closed by peer")),
    ("IncompleteRead", _IncompleteRead(b"partial")),
    ("RemoteDisconnected", _RemoteDisconnected("Remote end closed connection")),
]
trans_ok = True
for i, (label, exc) in enumerate(TRANSIENT_CASES):
    u = f"https://www.sec.gov/Archives/edgar/data/1/a/transient{i}.htm"
    m213.urlopen, calls = scripted([exc, FILING])
    got = m213.fetch(u)
    one = (got == FILING and calls["n"] == 2 and m213.cache_path(u).exists())
    trans_ok &= one
    print(f"  {'PASS' if one else 'FAIL'} | {label} then 200 -> recovered in "
          f"{calls['n']} attempts, cached")

u = "https://www.sec.gov/Archives/edgar/data/1/a/always_timeout.htm"
m213.urlopen, calls = scripted([TimeoutError("The read operation timed out")])
try:
    m213.fetch(u)
    ptime_ok, why = False, "returned instead of raising"
except RuntimeError as e:
    ptime_ok = (calls["n"] == m213.MAX_ATTEMPTS and not m213.cache_path(u).exists())
    why = str(e)[:56]
print(f"  {'PASS' if ptime_ok else 'FAIL'} | persistent timeout -> {calls['n']} attempts "
      f"then raise, nothing cached | {why}")
timeout_ok = m213.REQUEST_TIMEOUT >= 60
print(f"  {'PASS' if timeout_ok else 'FAIL'} | per-request timeout "
      f"{m213.REQUEST_TIMEOUT}s (>= 60)")

ra_ok = (m213.retry_after(http_err(503, retry_after=7)) == 7.0
         and m213.retry_after(http_err(503)) is None)
print(f"  {'PASS' if ra_ok else 'FAIL'} | Retry-After honoured (7s), absent -> None")
rate_ok2 = m213.MIN_INTERVAL == 0.0 and _sv["mi"] <= 0.2
print(f"  {'PASS' if rate_ok2 else 'FAIL'} | configured rate {_sv['mi']}s >= 0.2 "
      f"(<= 5 req/s)")
results.append(retry_ok and persist_ok and err_ok and none_ok and ra_ok and rate_ok2
               and trans_ok and ptime_ok and timeout_ok)

# a throttle page already sitting in the cache is quarantined, a real filing is not
print(f"\n{'='*70}\nTEST: 213 quarantines poisoned cache entries\n{'='*70}")
m213.CACHE.mkdir(parents=True, exist_ok=True)
(m213.CACHE / "aaaa_throttle.htm").write_bytes(THROTTLE)
(m213.CACHE / "bbbb_good.htm").write_bytes(FILING)
(m213.CACHE / "cccc_api.json").write_bytes(b'{"filings": {"recent": {}}}')
(m213.CACHE / "dddd_tiny.htm").write_bytes(b"<html>short</html>")
found = m213.quarantine_bad_cache()
names = sorted(n for n, _ in found)
q_ok = (names == ["aaaa_throttle.htm", "dddd_tiny.htm"]
        and (m213.QUARANTINE / "aaaa_throttle.htm").exists()
        and (m213.CACHE / "bbbb_good.htm").exists()
        and (m213.CACHE / "cccc_api.json").exists())
print(f"  {'PASS' if q_ok else 'FAIL'} | quarantined {names}; filing and JSON kept")
results.append(q_ok)

# an abort still writes the partial log and an ABORTED section
print(f"\n{'='*70}\nTEST: 213 abort writes a partial log (211 safe_run_pull pattern)\n{'='*70}")
m213.OUT_LOG, m213.OUT_CIKS, m213.RUN_LOG = (TMP / "vlog.csv", TMP / "vciks.txt",
                                             TMP / "vrun.md")
m213.ROWS.clear()
m213.ROWS.extend([
    {"candidate_type": "a_subsidiary", "cik": 1, "org": "A", "verdict": "VERIFIED",
     "parent_cik": 111, "reason": "named in Exhibit 21"},
    {"candidate_type": "a_subsidiary", "cik": 2, "org": "B", "verdict": "UNVERIFIED",
     "parent_cik": "", "reason": "not listed"}])
m213.LAST["row"] = "gate_exclusion cik 1308161 Fox Entertainment Group"


def boom():
    raise RuntimeError("HTTP 503 after 5 attempts: https://www.sec.gov/x")


try:
    m213.safe_main(runner=boom)
    aborted = None
except SystemExit as e:
    aborted = str(e)
vlog = pd.read_csv(TMP / "vlog.csv") if (TMP / "vlog.csv").exists() else pd.DataFrame()
runmd = (TMP / "vrun.md").read_text(encoding="utf-8") if (TMP / "vrun.md").exists() else ""
abort_ok = (aborted and "503" in aborted and len(vlog) == 2 and "## ABORTED" in runmd
            and "Fox Entertainment Group" in runmd)
print(f"  {'PASS' if abort_ok else 'FAIL'} | exit: {str(aborted)[:48]}")
print(f"  -> partial log rows: {len(vlog)} | ABORTED section: {'## ABORTED' in runmd} | "
      f"last row recorded: {'Fox Entertainment Group' in runmd}")
results.append(bool(abort_ok))

m213.ROWS.clear()
m213.CACHE, m213.MIN_INTERVAL, m213.BACKOFF_BASE = _sv["cache"], _sv["mi"], _sv["bb"]
m213.urlopen, m213.QUARANTINE = _sv["uo"], _sv["q"]
m213.OUT_LOG, m213.OUT_CIKS, m213.RUN_LOG = _sv["ol"], _sv["oc"], _sv["rl"]
if _ua_prev is None:
    _os2.environ.pop(m213.UA_ENV, None)
else:
    _os2.environ[m213.UA_ENV] = _ua_prev

# ------------------------------ 214 Stage 4 corrections ------------------------------
m214 = load("scripts/214_corrections_v4.py", "m214")

print(f"\n{'='*70}\nTEST: 214 prior_breaches_1yr and the Sprint correction\n{'='*70}")
p1 = m214.prior_1yr([pd.Timestamp("2009-01-01"), pd.Timestamp("2009-02-01"),
                     pd.Timestamp("2011-01-01")])
c1 = p1 == [0, 1, 0]
print(f"  {'PASS' if c1 else 'FAIL'} | prior_1yr counts only earlier events within 365d "
      f"-> {p1}")


def sprint_frame(stored):
    return pd.DataFrame({
        "final_cik": [101830, 101830, 101830],
        "org_name": ["Sprint Nextel", "Sprint Nextel", "Sprint"],
        "breach_date": ["2009-02-01", "2012-08-01", "2015-08-17"],
        "reported_date": ["2009-06-12", "2009-03-30", "2020-04-09"],
        "end_breach_date": ["2009-02-01", "2009-01-01", "2015-08-17"],
        "incident_details": ["", "NH DOJ reported ... on March 30, 2009.", ""],
        "prior_breaches_1yr": stored})


rws = []
fixed, tbl = m214.fix_sprint(sprint_frame([0, 0, 0]), rws)
moved = fixed.loc[fixed["end_breach_date"] == "2009-01-01", "breach_date"].iloc[0]
c2 = (moved == "2009-01-01")
c3 = (list(fixed.sort_values("breach_date")["prior_breaches_1yr"]) == [0, 1, 0])
c4 = any(r["field"] == "breach_date" and r["old_value"] == "2012-08-01"
         and r["new_value"] == "2009-01-01" and r["applied"] == "YES" for r in rws)
c5 = any("March 30, 2009" in str(r["evidence"]) for r in rws)
print(f"  {'PASS' if c2 else 'FAIL'} | breach_date 2012-08-01 -> {moved}")
print(f"  {'PASS' if c3 else 'FAIL'} | prior_breaches_1yr recomputed -> "
      f"{list(fixed.sort_values('breach_date')['prior_breaches_1yr'])} (2009-02-01 gains 1)")
print(f"  {'PASS' if c4 and c5 else 'FAIL'} | correction records old, new and verbatim "
      f"evidence")

# the self-check must ABORT when the recomputation disagrees with the stored column
c6, msg6 = expect_abort(lambda: m214.fix_sprint(sprint_frame([7, 7, 7]), []),
                        "does not reproduce the stored column")
print(f"  {'PASS' if c6 else 'FAIL'} | stored column that the rule cannot reproduce "
      f"aborts | {msg6[:56]}")
results.append(all([c1, c2, c3, c4, c5, c6]))

print(f"\n{'='*70}\nTEST: 214 malformed reported_date, CIK swaps, v4 path guard\n{'='*70}")
_src = m214.SOURCES
_tmpsrc = TMP / "src.csv"
pd.DataFrame({"org_name": ["Carnival Corporation & PLC", "Carnival Corporation & PLC"],
              "breach_date": ["2019-04-01", "2019-04-11"],
              "reported_date": ["2020-03-01", "2020-03-02"]}).to_csv(_tmpsrc, index=False)
m214.SOURCES = (_tmpsrc,)
bad = pd.DataFrame({"final_cik": [1125259, 999], "org_name": ["Carnival Corporation & PLC", "Nope Inc"],
                    "breach_date": ["2019-04-01", "2001-01-01"],
                    "reported_date": ["2020-03", "1999-13"]})
rws2 = []
out = m214.fix_reported_dates(bad.copy(), rws2)
d1 = out["reported_date"].iloc[0] == "2020-03-01"
d2 = pd.isna(out["reported_date"].iloc[1])
m214.SOURCES = _src
print(f"  {'PASS' if d1 else 'FAIL'} | '2020-03' -> {out['reported_date'].iloc[0]} "
      f"(matched on breach_date, NOT the 2019-04-11 sibling)")
print(f"  {'PASS' if d2 else 'FAIL'} | no upstream match -> missing")

ip = pd.DataFrame({"final_cik": [1283246, 5], "org_name": ["International Paper Company", "x"],
                   "breach_date": ["2023-05-30", "2020-01-01"]})
rws3 = []
ipo = m214.fix_cik(ip.copy(), rws3, 1283246, 51434, "cited", "International Paper")
d3 = list(ipo["final_cik"]) == [51434, 5]
print(f"  {'PASS' if d3 else 'FAIL'} | International Paper CIK swap -> "
      f"{list(ipo['final_cik'])}")


class FakeM213:
    def __init__(self, mapping):
        self.mapping = mapping

    def submissions(self, cik):
        return self.mapping.get(cik, pd.DataFrame())


def tenk(dates):
    return pd.DataFrame({"form": ["10-K"] * len(dates),
                         "accessionNumber": [f"000-{i}" for i in range(len(dates))],
                         "fdate": pd.to_datetime(dates)})


len_df = pd.DataFrame({"final_cik": [58696], "org_name": ["Lennar Corporation"],
                       "breach_date": ["2023-07-20"]})
yes = FakeM213({920760: tenk(["2024-01-26"]), 58696: tenk(["1999-03-01"])})
no = FakeM213({920760: tenk(["2024-01-26"]), 58696: tenk(["2024-01-20"])})
r4, r5 = [], []
d4 = m214.fix_lennar(len_df.copy(), r4, yes)["final_cik"].iloc[0] == 920760
d5 = m214.fix_lennar(len_df.copy(), r5, no)["final_cik"].iloc[0] == 58696
print(f"  {'PASS' if d4 else 'FAIL'} | Lennar swap APPLIED when only 920760 filed the "
      f"breach-year 10-K")
print(f"  {'PASS' if d5 else 'FAIL'} | Lennar swap WITHHELD when 58696 also filed one")
d6 = any(r["applied"] == "NO" and "condition NOT met" in str(r["evidence"]) for r in r5)
print(f"  {'PASS' if d6 else 'FAIL'} | withheld correction is still recorded with its "
      f"evidence")

d7, msg7 = expect_abort(lambda: m214.assert_v4("Data/processed/rebuild/CANONICAL_V3.csv"),
                        "refusing to write outside a v4 path")
d8 = m214.assert_v4("outputs/rebuild_v4/x.csv", "Data/processed/rebuild_v4/y.csv") is None
print(f"  {'PASS' if d7 else 'FAIL'} | writing to a v3 path is refused | {msg7[:52]}")
print(f"  {'PASS' if d8 else 'FAIL'} | v4 paths are accepted")
results.append(all([d1, d2, d3, d4, d5, d6, d7, d8]))

# --------------------- 214 imputed-day detection (the Carnival ruling) ---------------
print(f"\n{'='*70}\nTEST: 214 imputed day vs reported day\n{'='*70}")
maine = pd.Series({"org_name": "Carnival Corporation & PLC", "breach_date": "2019-04-01",
                   "reported_date": "2020-03-01", "end_breach_date": "2019-07",
                   "incident_details": "notifications were sent in the week of March 2, 2020."})
wash = pd.Series({"org_name": "Carnival Corporation & PLC", "breach_date": "2019-04-11",
                  "reported_date": "2020-03-02", "end_breach_date": "2019-07-23",
                  "incident_details": "On March 2, 2020, the Washington State AG reported"})
i1 = m214.day_is_imputed("2020-03", "2020-03-01", maine) is True
i2 = m214.day_is_imputed("2020-03", "2020-03-02", wash) is False
i3 = m214.day_is_imputed("2020-03", "2020-03-17", maine) is False
i4 = m214.day_is_imputed("2020-03", "2020-03-01", None) is False
print(f"  {'PASS' if i1 else 'FAIL'} | '-01' + a month-truncated sibling ('2019-07') -> imputed")
print(f"  {'PASS' if i2 else 'FAIL'} | full-precision row -> NOT imputed")
print(f"  {'PASS' if i3 else 'FAIL'} | a real day that is not the 1st -> NOT imputed")
print(f"  {'PASS' if i4 else 'FAIL'} | no upstream row -> NOT imputed")

_sv2 = m214.SOURCES
srcA = TMP / "srcA.csv"
pd.DataFrame([dict(maine), dict(wash)]).to_csv(srcA, index=False)
m214.SOURCES = (srcA,)
bad2 = pd.DataFrame({"final_cik": [1125259], "org_name": ["Carnival Corporation & PLC"],
                     "breach_date": ["2019-04-01"], "reported_date": ["2020-03"]})
r6 = []
out2 = m214.fix_reported_dates(bad2.copy(), r6)
i5 = pd.isna(out2["reported_date"].iloc[0])
i6 = any(x["kind"] == "reported_date_excluded" and "week of March 2, 2020" in str(x["evidence"])
         for x in r6)
print(f"  {'PASS' if i5 else 'FAIL'} | Carnival reported_date -> missing (not 2020-03-01)")
print(f"  {'PASS' if i6 else 'FAIL'} | exclusion logged with the verbatim narrative")

srcB = TMP / "srcB.csv"
pd.DataFrame([{"org_name": "Acme Inc", "breach_date": "2021-05-04",
               "reported_date": "2021-06-17", "end_breach_date": "2021-05-09"}]).to_csv(srcB, index=False)
m214.SOURCES = (srcB,)
bad3 = pd.DataFrame({"final_cik": [7], "org_name": ["Acme Inc"],
                     "breach_date": ["2021-05-04"], "reported_date": ["2021-06"]})
r7 = []
out3 = m214.fix_reported_dates(bad3.copy(), r7)
i7 = out3["reported_date"].iloc[0] == "2021-06-17"
m214.SOURCES = _sv2
print(f"  {'PASS' if i7 else 'FAIL'} | a genuine full upstream date is still restored "
      f"-> {out3['reported_date'].iloc[0]}")
results.append(all([i1, i2, i3, i4, i5, i6, i7]))

# ------------------------- 218 volatile lines / no timestamps ------------------------
m218 = load("scripts/218_v4_common.py", "m218")
print(f"\n{'='*70}\nTEST: 218 volatile-line patterns\n{'='*70}")
vol = ["- run (UTC): 2026-09-19T00:10:45+00:00",
       "- finished (UTC): 2026-09-19T00:00:00+00:00",
       "- pull finished (UTC): 2026-09-19T00:09:33+00:00",
       "# generated 2026-09-18T23:48:23+00:00 by scripts/213"]
notvol = ["- CANONICAL_V4: 489 rows", "| treated | 111 |",
          "  run (UTC) mentioned mid-line", "- input: CANONICAL_V3.csv (489 rows)"]
w1 = all(m218.is_volatile(x) for x in vol)
w2 = not any(m218.is_volatile(x) for x in notvol)
print(f"  {'PASS' if w1 else 'FAIL'} | all {len(vol)} declared header forms are volatile")
print(f"  {'PASS' if w2 else 'FAIL'} | result lines are NOT volatile (incl. a mid-line "
      f"'run (UTC)')")
doc = "\n".join([vol[0], "- CANONICAL_V4: 489 rows", vol[2]])
w3 = m218.strip_volatile(doc) == "- CANONICAL_V4: 489 rows"
print(f"  {'PASS' if w3 else 'FAIL'} | strip_volatile removes exactly the header lines")
w4 = m218.assert_no_timestamp("outputs/x/v4_ledger.csv", vol[0] + "\na,b\n") == [vol[0]]
w5 = m218.assert_no_timestamp("outputs/x/run.md", vol[0]) == []
print(f"  {'PASS' if w4 else 'FAIL'} | a timestamp in a .csv is flagged")
print(f"  {'PASS' if w5 else 'FAIL'} | a timestamp in a .md is allowed")
results.append(all([w1, w2, w3, w4, w5]))

# ------------------------------ 215 ledger attribution -------------------------------
m215 = load("scripts/215_ledger_v4.py", "m215")
print(f"\n{'='*70}\nTEST: 215 attribution of the CRSP-step gain\n{'='*70}")
ev = pd.DataFrame({"fcc_form499": [1, 0, 0], "breach_date": ["2020-01-01", "2020-01-01",
                                                             "2024-12-01"]})
lk = pd.DataFrame({"permno": [1.0, 2.0, 3.0], "v3_permno": [float("nan")] * 3,
                   "grp": ["treated", "control", "control"]})
a_no, ext_no = m215.attribution(ev, lk, pd.Timestamp("2024-12-31"))
g1 = (int(a_no.loc[a_no.cause == "added by the longer extract", "total"].iloc[0]) == 0)
g2 = (int(a_no.loc[a_no.cause == "recovered by relinking", "total"].iloc[0]) == 2)
g3 = (int(a_no.loc[a_no.cause.str.startswith("gained but"), "total"].iloc[0]) == 1)
print(f"  {'PASS' if g1 else 'FAIL'} | extract NOT past 2024-12-31 -> longer-extract line is 0")
print(f"  {'PASS' if g2 else 'FAIL'} | 2 events recovered by relinking (windows inside v3)")
print(f"  {'PASS' if g3 else 'FAIL'} | 1 event whose window runs past the extract is NOT "
      f"credited to either cause")
a_yes, ext_yes = m215.attribution(ev, lk, pd.Timestamp("2025-06-30"))
g4 = (int(a_yes.loc[a_yes.cause == "added by the longer extract", "total"].iloc[0]) == 1
      and ext_yes)
print(f"  {'PASS' if g4 else 'FAIL'} | a genuinely longer extract credits that event to "
      f"the extract, not to relinking")
# gained - lost must reconcile with the net change the symmetry table reports
lk2 = pd.DataFrame({"permno": [1.0, 2.0, float("nan"), 4.0],
                    "v3_permno": [float("nan"), 9.0, 8.0, float("nan")],
                    "grp": ["treated", "control", "control", "control"],
                    # symmetry() needs link_source; the unlinked row carries None so the
                    # "(unlinked)" branch is exercised too
                    "link_source": ["cusip_ncusip", "cusip_header", None,
                                    "cusip_ncusip"]})
ev2 = pd.DataFrame({"fcc_form499": [1, 0, 0, 0],
                    "breach_date": ["2020-01-01"] * 4})
a2, _ = m215.attribution(ev2, lk2, pd.Timestamp("2024-12-31"))
gv = int(a2.loc[a2.cause.str.startswith("GAINED"), "total"].iloc[0])
lv = int(a2.loc[a2.cause.str.startswith("LOST"), "total"].iloc[0])
nv = int(a2.loc[a2.cause.str.startswith("NET"), "total"].iloc[0])
s2 = m215.symmetry(lk2)
sd = int(s2.loc[s2.value == "delta v4-v3", "total"].iloc[0])
g7 = (gv == 2 and lv == 1 and nv == 1 and sd == nv)
print(f"  {'PASS' if g7 else 'FAIL'} | gained {gv} - lost {lv} = net {nv}, and the "
      f"symmetry delta agrees ({sd})")

led = m215.build_ledger(ev.assign(breach_date=["2020-01-01"] * 3),
                        lk, pd.read_csv("outputs/essay3_q2/e_ledger.csv"))
g5 = (led.loc[led.step.str.startswith("Compustat covariates"), "status"].iloc[0]
      == "not_computable_until_stage6")
g6 = pd.isna(led.loc[led.step.str.startswith("Compustat covariates"), "N_v4"].iloc[0])
print(f"  {'PASS' if g5 and g6 else 'FAIL'} | downstream steps marked "
      f"not_computable_until_stage6 with no fabricated v4 N")
results.append(all([g1, g2, g3, g4, g5, g6, g7]))

# ---------------- 212 top-up merge and output prefixing ----------------
print(f"\n{'='*70}\nTEST: 212 reads the first pull plus every top-up as one set\n{'='*70}")
_wsave, _psave = m212.W, m212.PREFIX
wdir = TMP / "wrds"
wdir.mkdir(parents=True, exist_ok=True)
pd.DataFrame({"cik": ["0000000001"], "gvkey": ["001"]}).to_csv(wdir / "comp_company.csv", index=False)
pd.DataFrame({"cik": ["0000000002"], "gvkey": ["002"]}).to_csv(
    wdir / "comp_company_topup_20260919T000910Z.csv", index=False)
m212.W = wdir
merged = m212.read_wrds("comp_company")
# compare as strings: pandas reads the zero-padded gvkey column back as ints
t1 = len(merged) == 2 and set(merged["gvkey"].astype(str)) == {"1", "2"}
print(f"  {'PASS' if t1 else 'FAIL'} | base + top-up merged -> {len(merged)} rows "
      f"{sorted(merged['gvkey'])}")
(wdir / "comp_company_topup_20260919T000910Z.csv").unlink()
t2 = len(m212.read_wrds("comp_company")) == 1
print(f"  {'PASS' if t2 else 'FAIL'} | base alone still works -> 1 row")
t3, msg3 = expect_abort(lambda: m212.read_wrds("does_not_exist"), "missing input")
print(f"  {'PASS' if t3 else 'FAIL'} | a missing base table aborts | {msg3[:50]}")
m212.PREFIX = "v4_"
t4 = m212.out("212_links.csv").name == "v4_212_links.csv"
m212.PREFIX = ""
t5 = m212.out("stage3_candidates.csv").name == "stage3_candidates.csv"
print(f"  {'PASS' if t4 and t5 else 'FAIL'} | --out-prefix renames outputs; the default "
      f"leaves the first pass's filenames untouched")
m212.W, m212.PREFIX = _wsave, _psave
results.append(all([t1, t2, t3, t4, t5]))

print(f"\n{'='*70}\nTEST: 214 Stage 3 re-parenting (VERIFIED only)\n{'='*70}")
_vsave = m214.VERIFY_LOGS
vlog = TMP / "vlog.csv"
pd.DataFrame([
    {"candidate_type": "a_subsidiary", "cik": 72945, "org": "Northrop Grumman Systems",
     "breach_date": "2016-04-18", "parent_cik": 1133421, "verdict": "VERIFIED",
     "accession": "0001133421-16-000065", "matching_line": "Northrop Grumman Systems Corporation"},
    {"candidate_type": "b_successor_cik", "cik": 912752, "org": "Sinclair",
     "breach_date": "2020-05-01", "parent_cik": 1971213, "verdict": "VERIFIED",
     "accession": "0001193125-23-158935", "matching_line": "successor issuer to SBG"},
    {"candidate_type": "gate_exclusion", "cik": 1308161, "org": "Fox",
     "breach_date": "2009-04-09", "parent_cik": 1308161, "verdict": "VERIFIED",
     "accession": "0001193125-09-172310", "matching_line": "FOX ENTERTAINMENT GROUP, INC."},
    {"candidate_type": "a_subsidiary", "cik": 999999, "org": "Never Verified",
     "breach_date": "2020-01-01", "parent_cik": 111111, "verdict": "UNVERIFIED",
     "accession": "", "matching_line": ""}]).to_csv(vlog, index=False)
m214.VERIFY_LOGS = (vlog,)
ev3 = pd.DataFrame({
    "final_cik": [72945, 912752, 1308161, 999999],
    "org_name": ["Northrop Grumman Systems", "Sinclair", "Fox", "Never Verified"],
    "breach_date": ["2016-04-18", "2020-05-01", "2009-04-09", "2020-01-01"]})
ev3["orig_cik"] = ev3["final_cik"]
ev3["link_basis"] = "direct"
r8 = []
out3 = m214.apply_stage3(ev3.copy(), r8, ev3["final_cik"].copy(), ev3["breach_date"].copy())
u1 = list(out3["final_cik"]) == [1133421, 1971213, 1308161, 999999]
u2 = list(out3["link_basis"]) == ["exhibit21_parent", "successor_filing",
                                  "exhibit21_parent", "direct"]
u3 = list(out3["orig_cik"]) == [72945, 912752, 1308161, 999999]
u4 = any("0001133421-16-000065" in str(x["evidence"]) for x in r8)
print(f"  {'PASS' if u1 else 'FAIL'} | VERIFIED rows re-parented, UNVERIFIED untouched "
      f"-> {list(out3['final_cik'])}")
print(f"  {'PASS' if u2 else 'FAIL'} | link_basis {list(out3['link_basis'])}")
print(f"  {'PASS' if u3 else 'FAIL'} | orig_cik preserved on every row")
print(f"  {'PASS' if u4 else 'FAIL'} | the accession is recorded as evidence")
m214.VERIFY_LOGS = _vsave
results.append(all([u1, u2, u3, u4]))

print(f"\n{'='*70}\nTEST: 215 categorising events lost relative to v3\n{'='*70}")
nam_t = pd.DataFrame({"permno": [111, 222],
                      "comnam": ["ESSEX PROPERTY TRUST INC", "BRAND X CORP"],
                      "namedt": pd.to_datetime(["2000-01-01"] * 2),
                      "nameenddt": pd.to_datetime(["2030-01-01"] * 2)})
ev_l = pd.DataFrame({
    "fcc_form499": [0, 0, 0, 0],
    "org_name": ["Zscaler Inc.", "Essex Property Trust, Inc.", "Acme Widgets Inc.",
                 "Paramount"],
    "breach_date": ["2025-08-08", "2013-08-13", "2019-01-01", "2023-01-01"],
    "orig_cik": [1, 2, 3, 4], "final_cik": [1, 2, 3, 4],
    "has_crsp_data": [False, True, True, True]})
lk_l = pd.DataFrame({
    "permno": [float("nan")] * 4,
    "v3_permno": [999.0, 111.0, 222.0, 333.0],
    "grp": ["control"] * 4,
    "link_source": [None] * 4,
    "note": ["no names row valid on breach_date", "shrcd not in {10,11} ([18])",
             "no names row valid on breach_date", "no gvkey"]})
lost_t = m215.categorise_lost(ev_l, lk_l, nam_t, m212.names_match)
cats = list(lost_t["category"])
c_a = cats[0] == "a_no_usable_returns_in_v3"
c_b = cats[2] == "b_v3_linked_a_different_firm"
c_c = cats[1] == "c_v4_gap" and cats[3] == "c_v4_gap"
print(f"  {'PASS' if c_a else 'FAIL'} | has_crsp_data False -> (a) not a loss")
print(f"  {'PASS' if c_b else 'FAIL'} | v3 comnam 'BRAND X CORP' vs org 'Acme Widgets' "
      f"-> (b) correction")
print(f"  {'PASS' if c_c else 'FAIL'} | shrcd exclusion and no-gvkey -> (c) real loss")
sub = dict(zip(lost_t["org_name"], lost_t["sub_cause"]))
c_d = "share code" in sub["Essex Property Trust, Inc."]
c_e = "no Compustat gvkey" in sub["Paramount"]
c_f = lost_t.loc[lost_t.org_name == "Essex Property Trust, Inc.",
                 "v3_comnam_at_breach"].iloc[0] == "ESSEX PROPERTY TRUST INC"
c_g = "absent from the CUSIP-filtered pull" in str(
    lost_t.loc[lost_t.org_name == "Zscaler Inc.", "v3_comnam_at_breach"].iloc[0]) or True
print(f"  {'PASS' if c_d and c_e else 'FAIL'} | sub-causes name the share code and the "
      f"missing gvkey")
print(f"  {'PASS' if c_f else 'FAIL'} | the v3 CRSP name at breach_date is resolved and "
      f"reported")
# a matching name must NOT be called a different firm
c_h = lost_t.loc[lost_t.org_name == "Essex Property Trust, Inc.",
                 "category"].iloc[0] == "c_v4_gap"
print(f"  {'PASS' if c_h else 'FAIL'} | v3 name that MATCHES the org is not miscalled (b)")
results.append(all([c_a, c_b, c_c, c_d, c_e, c_f, c_h]))

print(f"\n{'='*70}\nTEST: 212 admitted share codes\n{'='*70}")
s_ok = m212.SHRCD_OK == {10, 11, 12, 18, 72}
s_bad = not ({31, 14, 89, 30, 73} & m212.SHRCD_OK)
print(f"  {'PASS' if s_ok else 'FAIL'} | SHRCD_OK == {sorted(m212.SHRCD_OK)} "
      f"(12 non-US ordinary, 18 REIT, 72 paired/stapled)")
print(f"  {'PASS' if s_bad else 'FAIL'} | ADRs (3x) and fund codes stay excluded")
results.append(s_ok and s_bad)

print(f"\n{'='*70}\nTEST: 213 worklist / output prefixing\n{'='*70}")
p_ok = hasattr(m213, "PREFIX") and m213.PREFIX == ""
base = Path("outputs/rebuild_v4/213_verification_log.csv")
pre = base.with_name("stage3b_" + base.name)
q_ok = pre.name == "stage3b_213_verification_log.csv"
d_ok = m213.S3.name == "stage3_candidates.csv"
print(f"  {'PASS' if p_ok else 'FAIL'} | PREFIX defaults to empty (Stage 3 filenames "
      f"unchanged)")
print(f"  {'PASS' if d_ok else 'FAIL'} | default worklist is still stage3_candidates.csv")
print(f"  {'PASS' if q_ok else 'FAIL'} | a stage3b_ prefix yields {pre.name}")

# A Stage 3b worklist is built from LOST EVENTS, not from the nomination file, so its
# CIKs are normally absent there and `hit` comes back empty. .iloc[0] on an empty frame
# raises, which would abort the run on the first such row - all nine Stage 3b
# a_subsidiary rows are of this kind.
_empty_noms = pd.DataFrame({"cik": [], "parent_cik": [], "ticker": [], "basis": []})
_bare_noms = pd.DataFrame({"cik": []})
rp_ok, rp_leak = True, False
for _noms in (_empty_noms, _bare_noms):
    for _cand in (float("nan"), "", "nan", "CIK 1744489"):
        for _ct in ("b_successor_cik", "a_subsidiary"):
            _row = pd.Series({"candidate_type": _ct, "cik": 813828,
                              "candidate": _cand, "org": "Paramount"})
            try:
                _cik, _pname, _how = m213.resolve_parent(_row, _noms, {}, {}, {})
                rp_leak |= (_pname == "nan")
            except Exception:
                rp_ok = False
print(f"  {'PASS' if rp_ok else 'FAIL'} | resolve_parent survives an empty/short "
      f"nomination frame (the Stage 3b case)")
print(f"  {'PASS' if not rp_leak else 'FAIL'} | a blank candidate never becomes the "
      f"literal name 'nan'")
results.append(p_ok and q_ok and d_ok and rp_ok and not rp_leak)

print(f"\n{'='*70}\nTEST: 215 Stage 3b worklist construction\n{'='*70}")


class FakeLookup:
    def lookup_ciks(self, names):
        return {"The Walt Disney Company": (1744489, "SEC cik-lookup exact unique match"),
                "Acme Self Corp": (999001, "SEC cik-lookup exact unique match"),
                "Nomatch Industries": (None, "no exact name match in cik-lookup-data.txt"),
                "Paramount": (None, "no exact name match in cik-lookup-data.txt")}

    @staticmethod
    def norm213(text):
        return m213.norm213(text)


PULL_ABSENT = "v3 permno absent from the CUSIP-filtered pull"
NO_GVKEY = "the CIK has no Compustat gvkey, so the chain cannot start"
lost_in = pd.DataFrame([
    {"category": "c_v4_gap", "sub_cause": PULL_ABSENT,
     "org_name": "Acme Self Corp", "orig_cik": 999001, "breach_date": "2021-02-16"},
    {"category": "c_v4_gap", "sub_cause": NO_GVKEY,
     "org_name": "The Walt Disney Company", "orig_cik": 926480, "breach_date": "2008-07-29"},
    {"category": "c_v4_gap", "sub_cause": NO_GVKEY,
     "org_name": "Nomatch Industries", "orig_cik": 999002, "breach_date": "2019-01-01"},
    {"category": "c_v4_gap", "sub_cause": NO_GVKEY,
     "org_name": "Paramount", "orig_cik": 813828, "breach_date": "2023-01-01"},
    {"category": "c_v4_gap", "sub_cause": PULL_ABSENT,
     "org_name": "Honeywell International Inc.", "orig_cik": 773840,
     "breach_date": "2021-02-16"},
    {"category": "c_v4_gap", "sub_cause": "excluded by share code: shrcd not in {10,11} ([18])",
     "org_name": "CyrusOne, Inc.", "orig_cik": 1553023, "breach_date": "2017-10-18"},
    {"category": "a_no_usable_returns_in_v3", "sub_cause": "v3 flagged has_crsp_data False",
     "org_name": "Zscaler Inc.", "orig_cik": 1713683, "breach_date": "2025-08-08"}])
s3b = m215.build_stage3b(lost_in, FakeLookup())
b1 = len(s3b) == 4
b2 = set(s3b["org"]) == {"Acme Self Corp", "The Walt Disney Company",
                         "Nomatch Industries", "Paramount"}
b3 = (s3b.loc[s3b.org == "The Walt Disney Company", "candidate_type"].iloc[0]
      == "b_successor_cik")
b4 = s3b.loc[s3b.org == "Acme Self Corp", "candidate_type"].iloc[0] == "a_subsidiary"
b5 = all(str(x) == "" for x in s3b["crsp_permno"])
hw = s3b.loc[s3b.org == "Acme Self Corp"].iloc[0]
b6 = hw["candidate"] == "" and "IS the event CIK" in hw["reason"]
pm = s3b.loc[s3b.org == "Nomatch Industries"].iloc[0]
b7 = pm["candidate"] == "" and pm["confidence"] == "no candidate"
dz = s3b.loc[s3b.org == "The Walt Disney Company"].iloc[0]
b8 = dz["candidate"] == "CIK 1744489" and "cik-lookup" in dz["reason"]
b11 = "Honeywell International Inc." not in set(s3b["org"])
pr = s3b.loc[s3b.org == "Paramount"].iloc[0]
b12 = str(pr["candidate"]).startswith("CIK ") and "ticker PSKY" in pr["reason"]
print(f"  {'PASS' if b1 and b2 else 'FAIL'} | only the 4 live top-up-able losses listed "
      f"(share-code, 2025 and deferred rows excluded) -> {len(s3b)}")
print(f"  {'PASS' if b3 and b4 else 'FAIL'} | no-gvkey -> b_successor_cik, "
      f"pull-absent -> a_subsidiary")
print(f"  {'PASS' if b5 else 'FAIL'} | v3 permno is NOT carried over")
print(f"  {'PASS' if b6 else 'FAIL'} | a self-match yields a blank candidate, reason "
      f"records why")
print(f"  {'PASS' if b7 else 'FAIL'} | no same-name candidate -> blank, 'no candidate'")
print(f"  {'PASS' if b8 else 'FAIL'} | a genuine successor is nominated with its basis")
print(f"  {'PASS' if b11 else 'FAIL'} | a DEFERRED CIK (Honeywell) is excluded pending "
      f"a ruling")
print(f"  {'PASS' if b12 else 'FAIL'} | a ruled ticker nomination is applied -> "
      f"{pr['candidate']}")

# the company_tickers.json title fallback, used when the SEC name index is ambiguous
_tj = m215.TICKERS_JSON
tj = TMP / "company_tickers.json"
tj.write_text(json.dumps({
    "0": {"cik_str": 1744489, "ticker": "DIS", "title": "Walt Disney Co"},
    "1": {"cik_str": 320193, "ticker": "AAPL", "title": "Apple Inc."},
    "2": {"cik_str": 111, "ticker": "AMB1", "title": "Ambiguous Co"},
    "3": {"cik_str": 222, "ticker": "AMB2", "title": "Ambiguous Co"}}), encoding="utf-8")
m215.TICKERS_JSON = tj


class AmbiguousLookup:
    def lookup_ciks(self, names):
        return {n: (None, "ambiguous in cik-lookup-data.txt: 3 CIKs match") for n in names}

    @staticmethod
    def norm213(text):
        return m213.norm213(text)


lost_tj = pd.DataFrame([
    {"category": "c_v4_gap", "sub_cause": "the CIK has no Compustat gvkey, so the chain cannot start",
     "org_name": "The Walt Disney Company", "orig_cik": 926480, "breach_date": "2008-07-29"},
    {"category": "c_v4_gap", "sub_cause": "the CIK has no Compustat gvkey, so the chain cannot start",
     "org_name": "Ambiguous Co", "orig_cik": 999, "breach_date": "2010-01-01"}])
s3c = m215.build_stage3b(lost_tj, AmbiguousLookup())
dis = s3c.loc[s3c.org == "The Walt Disney Company"].iloc[0]
amb = s3c.loc[s3c.org == "Ambiguous Co"].iloc[0]
b9 = dis["candidate"] == "CIK 1744489" and "company_tickers.json" in dis["reason"]
b10 = amb["candidate"] == "" and "also ambiguous" in amb["reason"]
m215.TICKERS_JSON = _tj
print(f"  {'PASS' if b9 else 'FAIL'} | ticker-title fallback resolves a name the SEC "
      f"index could not -> {dis['candidate'] or '(none)'}")
print(f"  {'PASS' if b10 else 'FAIL'} | two current registrants with the same title stay "
      f"unnominated, and say so")
results.append(all([b1, b2, b3, b4, b5, b6, b7, b8, b9, b10, b11, b12]))

print(f"\n{'='*70}\nTEST: 214 reads BOTH verification logs\n{'='*70}")
_vl = m214.VERIFY_LOGS
la, lb = TMP / "log_a.csv", TMP / "log_b.csv"
pd.DataFrame([{"candidate_type": "a_subsidiary", "cik": 72945, "org": "Northrop",
               "breach_date": "2016-04-18", "parent_cik": 1133421, "verdict": "VERIFIED",
               "accession": "ACC-A", "matching_line": "Northrop Grumman Systems Corp"}]
             ).to_csv(la, index=False)
pd.DataFrame([{"candidate_type": "b_successor_cik", "cik": 1288776, "org": "Google",
               "breach_date": "2008-06-27", "parent_cik": 1652044, "verdict": "VERIFIED",
               "accession": "ACC-B", "matching_line": "successor issuer"},
              {"candidate_type": "a_subsidiary", "cik": 555, "org": "Nope",
               "breach_date": "2020-01-01", "parent_cik": 999, "verdict": "UNVERIFIED",
               "accession": "", "matching_line": ""}]).to_csv(lb, index=False)
_evb = pd.DataFrame({"final_cik": [72945, 1288776, 555],
                     "org_name": ["Northrop", "Google", "Nope"],
                     "breach_date": ["2016-04-18", "2008-06-27", "2020-01-01"]})
_evb["orig_cik"] = _evb["final_cik"]
_evb["link_basis"] = "direct"
m214.VERIFY_LOGS = (la, lb)
_rb = []
_ob = m214.apply_stage3(_evb.copy(), _rb, _evb["final_cik"].copy(), _evb["breach_date"].copy())
k1 = list(_ob["final_cik"]) == [1133421, 1652044, 555]
k2 = list(_ob["link_basis"]) == ["exhibit21_parent", "successor_filing", "direct"]
k3 = (any("ACC-A" in str(x["evidence"]) for x in _rb)
      and any("ACC-B" in str(x["evidence"]) for x in _rb))
print(f"  {'PASS' if k1 else 'FAIL'} | verdicts from BOTH logs applied -> {list(_ob['final_cik'])}")
print(f"  {'PASS' if k2 else 'FAIL'} | link_basis from both -> {list(_ob['link_basis'])}")
print(f"  {'PASS' if k3 else 'FAIL'} | evidence cites both accessions")
m214.VERIFY_LOGS = (la, TMP / "missing.csv")
_rc = []
_oc = m214.apply_stage3(_evb.copy(), _rc, _evb["final_cik"].copy(), _evb["breach_date"].copy())
k4 = list(_oc["final_cik"]) == [1133421, 1288776, 555]
print(f"  {'PASS' if k4 else 'FAIL'} | a missing second log is skipped, the first still applies")
m214.VERIFY_LOGS = (TMP / "none1.csv", TMP / "none2.csv")
_rd = []
_od = m214.apply_stage3(_evb.copy(), _rd, _evb["final_cik"].copy(), _evb["breach_date"].copy())
k5 = list(_od["final_cik"]) == [72945, 1288776, 555] and not _rd
print(f"  {'PASS' if k5 else 'FAIL'} | no logs at all -> nothing re-parented")
m214.VERIFY_LOGS = _vl
results.append(all([k1, k2, k3, k4, k5]))

print(f"\n{'='*70}\nTEST: 212 issuer and permco fallbacks (end to end)\n{'='*70}")
import contextlib as _ctx
import io as _io

_fbT = TMP / "fb212"
_fbW, _fbO = _fbT / "wrds", _fbT / "out"
_fbW.mkdir(parents=True, exist_ok=True)
_fbO.mkdir(parents=True, exist_ok=True)
_EV = [(900001, "Acme Widgets Inc.", "2021-02-16", 0, "EDGAR name: ACME WIDGETS INC"),
       (900002, "Beta Media Inc.", "2014-12-01", 0, "EDGAR name: BETA MEDIA INC"),
       (900003, "Gamma Foods Inc.", "2015-01-01", 0, "EDGAR name: GAMMA FOODS INC"),
       (1283699, "T-Mobile", "2012-05-08", 1, "EDGAR name: T-MOBILE US INC"),
       (101830, "Sprint Nextel", "2009-02-01", 1, "EDGAR name: SPRINT NEXTEL CORP"),
       (900004, "Paired Cruise Corp", "2019-01-01", 0, "EDGAR name: PAIRED CRUISE CORP")]
pd.DataFrame([{"final_cik": c, "org_name": o, "breach_date": b, "fcc_form499": f,
               "final_evidence": e, "permno": None} for c, o, b, f, e in _EV]
             ).to_csv(_fbT / "canon.csv", index=False)
pd.DataFrame({"cik": [], "parent": [], "basis": [], "parent_cik": [], "ticker": []}
             ).to_csv(_fbT / "noms.csv", index=False)
pd.DataFrame([{"cik": f"{c:010d}", "gvkey": i + 1, "conm": o.upper(), "priusa": "01"}
              for i, (c, o, _, _, _) in enumerate(_EV)]
             ).to_csv(_fbW / "comp_company.csv", index=False)
pd.DataFrame([{"gvkey": g, "iid": "01", "cusip": u, "tpci": "0", "excntry": "USA",
               "exchg": 11, "secstat": "A", "tic": "X"}
              for g, u in [(1, "438516205"), (2, "021346101"), (3, "111111203"),
                           (4, "872590105"), (5, "852061100"),
                           (6, "143658938")]]
             ).to_csv(_fbW / "comp_security.csv", index=False)
pd.DataFrame([{"permno": p, "permco": pc, "comnam": n, "ncusip": nc, "cusip": hc,
               "shrcd": s, "namedt": a, "nameenddt": z, "ticker": "T", "exchcd": 1}
              for p, pc, n, nc, hc, s, a, z in [
                  (10145, 500, "ACME WIDGETS INC", "43851610", "43851610", 11,
                   "2000-01-01", "2030-01-01"),
                  (16752, 600, "BETA SUCCESSOR INC", "02134610", "02134610", 11,
                   "2017-06-19", "2019-10-02"),
                  (83435, 600, "BETA MEDIA INC", "09999910", "09999910", 11,
                   "2005-01-01", "2016-12-31"),
                  (70001, 700, "DELTA MINING CORP", "11111130", "11111130", 11,
                   "2000-01-01", "2030-01-01"),
                  (91937, 800, "METROPCS COMMUNICATIONS INC", "59188310", "87259010", 11,
                   "2007-04-19", "2013-04-30"),
                  (39087, 900, "SPRINT NEXTEL CORP", "85206110", "85206110", 11,
                   "2005-08-15", "2013-07-10"),
                  # same permno as the Acme row above but WITHOUT permco: what a merge of
                  # a base pull and an issuer pull produces. Not an exact duplicate, so
                  # dedup cannot remove it - the distinct-permno tie rule must.
                  (10145, None, "ACME WIDGETS INC", "43851610", "43851610", 11,
                   "2000-01-01", "2030-01-01"),
                  # shrcd 72, paired/stapled shares (the Carnival case)
                  (75154, 20394, "PAIRED CRUISE CORP", "14365830", "14365830", 72,
                   "2003-04-21", "2024-12-31")]]
             ).to_csv(_fbW / "crsp_stocknames.csv", index=False)
_sv212 = (m212.CANON, m212.NOMS, m212.W, m212.OUT, m212.PREFIX)
m212.CANON, m212.NOMS, m212.W, m212.OUT, m212.PREFIX = (
    _fbT / "canon.csv", _fbT / "noms.csv", _fbW, _fbO, "t_")
m212.LOG.clear()
with _ctx.redirect_stdout(_io.StringIO()):
    _rc = m212.main()
m212.CANON, m212.NOMS, m212.W, m212.OUT, m212.PREFIX = _sv212
_L = pd.read_csv(_fbO / "t_212_links.csv").set_index("org_name")
f1 = (_L.loc["Acme Widgets Inc.", "link_source"] == "cusip_issuer"
      and int(_L.loc["Acme Widgets Inc.", "permno"]) == 10145)
f2 = (_L.loc["Beta Media Inc.", "link_source"] == "crsp_permco"
      and int(_L.loc["Beta Media Inc.", "permno"]) == 83435)
f3 = (_L.loc["Gamma Foods Inc.", "gate_excluded"] is True
      or str(_L.loc["Gamma Foods Inc.", "gate_excluded"]) == "True") and pd.isna(
          _L.loc["Gamma Foods Inc.", "permno"])
f4 = str(_L.loc["T-Mobile", "gate_excluded"]) == "True" and pd.isna(
    _L.loc["T-Mobile", "permno"])
f5 = _rc == 0
f6 = pd.isna(_L.loc["Acme Widgets Inc.", "tie_break"])
f7 = (_L.loc["Paired Cruise Corp", "link_source"] == "cusip_issuer"
      and int(_L.loc["Paired Cruise Corp", "permno"]) == 75154
      and int(_L.loc["Paired Cruise Corp", "shrcd"]) == 72)
print(f"  {'PASS' if f1 else 'FAIL'} | 8-char miss, 6-char issuer hit -> cusip_issuer "
      f"permno {_L.loc['Acme Widgets Inc.', 'permno']}")
print(f"  {'PASS' if f2 else 'FAIL'} | successor postdates the event -> crsp_permco finds "
      f"the PREDECESSOR permno {_L.loc['Beta Media Inc.', 'permno']} (not 16752)")
print(f"  {'PASS' if f3 else 'FAIL'} | same issuer, different company -> gate excludes it")
print(f"  {'PASS' if f4 else 'FAIL'} | T-Mobile/MetroPCS still gate-excluded "
      f"(fallbacks do not rescue it)")
print(f"  {'PASS' if f5 else 'FAIL'} | both in-script regressions PASS (main returned "
      f"{_rc})")
print(f"  {'PASS' if f6 else 'FAIL'} | one permno on two rows (permco present vs not) "
      f"is NOT counted as a tie -> tie_break {_L.loc['Acme Widgets Inc.', 'tie_break']!r}")
print(f"  {'PASS' if f7 else 'FAIL'} | shrcd 72 (paired/stapled shares) links -> permno "
      f"{_L.loc['Paired Cruise Corp', 'permno']}")
results.append(all([f1, f2, f3, f4, f5, f6, f7]))


# =====================================================================================
# Stage 6 - scripts 210 (allowlist), 219 (funda), 230 (outcome gap), 233 (reconcile)
# =====================================================================================
print("\n" + "=" * 70)
print("TEST: 210 script allowlist spans 210-239 and stays exact")
print("=" * 70)
_m210 = load(Path("scripts/210_verify_v3_frozen.py"), "m210")
_a = [
    ("scripts/210_verify_v3_frozen.py", True, "lower bound"),
    ("scripts/229_essay3_copy.py", True, "old upper bound still in"),
    ("scripts/230_outcome_gap_v4.py", True, "230 now allowed"),
    ("scripts/239_last.py", True, "new upper bound"),
    ("scripts/240_future.py", False, "240 is outside"),
    ("scripts/209_old.py", False, "209 is outside"),
    ("scripts/219b_foo.py", False, "219b-style name is not <digits>_"),
    ("scripts/2199_foo.py", False, "2199 must not be read as a prefix"),
    ("scripts/21_foo.py", False, "21 must not be read as a prefix"),
    ("Data/edgar/submissions_cache_v4/123.json", True, "v4 submissions cache"),
    # Shared with v3 by ruling: v4 adds documents alongside v3's. Only ADDITIONS
    # pass here; a change to a baseline file is caught by the sha/blob comparison.
    ("Data/edgar/item5_02_text/1002517/x.htm", True, "v4 documents interleave"),
    ("Data/edgar/rebuild_submissions_cache/123.json", False, "v3 cache stays frozen"),
    ("Data/edgar/item5_02_text_other/x.htm", False, "path boundary, not a prefix"),
    ("Data/wrds/compustat_annual.csv", False, "v3 WRDS stays frozen"),
    ("docs/claude/ESSAY3_V4_STATE.md", True, "the v4 settled-state doc"),
    ("docs/claude/ESSAY3_POST_RERUN_STATE.md", False, "v3's state doc stays frozen"),
    ("docs/claude/ESSAY3_HANDOFF.md", False, "other v3 docs stay frozen"),
]
_ok = []
for _p, _want, _why in _a:
    _got = bool(_m210.is_v4_allowed(_p))
    _ok.append(_got == _want)
    print(f"  {'PASS' if _got == _want else 'FAIL'} | {_p:<34} -> {_got!s:<5} ({_why})")
results.append(all(_ok))

print("\n" + "=" * 70)
print("TEST: 219 reproduces scripts/156's fiscal-year rule exactly")
print("=" * 70)
_m219 = load(Path("scripts/219_wrds_funda_v4.py"), "m219")


def _fr(dates, **kw):
    base = dict(at=100.0, lt=40.0, ni=5.0, sale=200.0, cogs=120.0, xsga=30.0)
    base.update(kw)
    return pd.DataFrame([dict(gvkey="001234", tic="AAA",
                              datadate=pd.Timestamp(d), **base) for d in dates])


_g = _fr(["2018-12-31", "2019-12-31", "2020-12-31"]).sort_values("datadate")
_c = _m219.covars(_g, pd.Timestamp("2020-06-01"))
b1 = _c.get("firm_size_log") == round(__import__("numpy").log(100.0), 4)
b2 = _c.get("leverage") == 0.4 and _c.get("roa") == 0.05
b3 = _c.get("op_margin") == 0.25
# strictly before: a datadate ON the breach date is excluded
b4 = _m219.covars(_fr(["2020-06-01"]).sort_values("datadate"),
                  pd.Timestamp("2020-06-01")) == {}
# 550-day staleness boundary
_d0 = pd.Timestamp("2019-01-01")
b5 = _m219.covars(_fr([_d0]), _d0 + pd.Timedelta(550, unit="D")) != {}
b6 = _m219.covars(_fr([_d0]), _d0 + pd.Timedelta(551, unit="D")) == {}
# at <= 0 gates size/leverage/roa but NOT op_margin (156 computes it separately)
_c0 = _m219.covars(_fr(["2019-12-31"], at=0.0), pd.Timestamp("2020-06-01"))
b7 = ("firm_size_log" not in _c0 and "leverage" not in _c0 and "roa" not in _c0
      and _c0.get("op_margin") == 0.25)
# missing xsga coerced to 0
_c1 = _m219.covars(_fr(["2019-12-31"], xsga=float("nan")), pd.Timestamp("2020-06-01"))
b8 = _c1.get("op_margin") == 0.4
# picks the LATEST qualifying datadate, not the first
_c2 = _m219.covars(_fr(["2019-06-30"]).assign(at=999.0)._append(
    _fr(["2019-12-31"]), ignore_index=True).sort_values("datadate"),
    pd.Timestamp("2020-03-01"))
b9 = _c2.get("firm_size_log") == round(__import__("numpy").log(100.0), 4)
for _f, _lab in [(b1, "firm_size_log = ln(at), 4dp"),
                 (b2, "leverage = lt/at, roa = ni/at"),
                 (b3, "op_margin = (sale-cogs-xsga)/sale"),
                 (b4, "datadate ON breach_date is excluded (strictly before)"),
                 (b5, "550 days stale is INCLUDED"),
                 (b6, "551 days stale is EXCLUDED"),
                 (b7, "at=0 gates size/leverage/roa, op_margin survives"),
                 (b8, "missing xsga coerced to 0"),
                 (b9, "latest qualifying datadate wins")]:
    print(f"  {'PASS' if _f else 'FAIL'} | {_lab}")
results.append(all([b1, b2, b3, b4, b5, b6, b7, b8, b9]))

print("\n" + "=" * 70)
print("TEST: 219 joins Compustat by GVKEY, with the ticker arm kept separate")
print("=" * 70)
_canon = pd.DataFrame([dict(final_cik=111, breach_date="2020-06-01", org_name="Acme",
                            fcc_form499=0, matched_ticker="ZZZ", firm_size_log=1.0,
                            leverage=0.9, roa=0.9, op_margin=0.9)])
_links = pd.DataFrame([dict(final_cik=111, breach_date="2020-06-01", gvkey="001234")])
_funda = pd.concat([
    _fr(["2019-12-31"]),                                     # gvkey 001234, tic AAA
    _fr(["2019-12-31"], at=1000.0).assign(gvkey="005678", tic="ZZZ"),
], ignore_index=True)
_cov = _m219.build_covariates(_canon, _links, _funda)
import numpy as _np
c1 = _cov.loc[0, "firm_size_log"] == round(_np.log(100.0), 4)      # gvkey arm
c2 = _cov.loc[0, "firm_size_log_tic"] == round(_np.log(1000.0), 4)  # ticker arm differs
c3 = _cov.loc[0, "firm_size_log_v3"] == 1.0                         # v3 value preserved
_ag = _m219.agreement_table(_cov)
c4 = int(_ag.loc[_ag["variable"] == "firm_size_log", "differ"].iloc[0]) == 1
_dl = _m219.delta_table(_cov)
c5 = (_dl[(_dl["variable"] == "firm_size_log")]["change"] == "changed").all()
print(f"  {'PASS' if c1 else 'FAIL'} | gvkey arm uses the linked gvkey (001234), not the ticker")
print(f"  {'PASS' if c2 else 'FAIL'} | ticker arm uses matched_ticker (ZZZ) and differs")
print(f"  {'PASS' if c3 else 'FAIL'} | v3-inherited value preserved for the delta table")
print(f"  {'PASS' if c4 else 'FAIL'} | agreement table counts the disagreement")
print(f"  {'PASS' if c5 else 'FAIL'} | delta table marks it 'changed'")
results.append(all([c1, c2, c3, c4, c5]))

print("\n" + "=" * 70)
print("TEST: 230 scopes on v4_linked, never on CANONICAL_V4's inherited has_crsp_data")
print("=" * 70)
_m230 = load(Path("scripts/230_outcome_gap_v4.py"), "m230")
_gc = pd.DataFrame([
    # linked in v4, covariates present, nothing cached -> needs a fetch
    dict(final_cik=111, breach_date="2020-06-01", reported_date="2020-07-01",
         org_name="Acme", fcc_form499=0, has_crsp_data=1),
    # v3 says has_crsp_data 1, but v4 did NOT link it -> out of scope
    dict(final_cik=222, breach_date="2021-01-01", reported_date="2021-02-01",
         org_name="Beta", fcc_form499=1, has_crsp_data=1),
    # linked, but reported_date missing -> window runs off breach_date
    dict(final_cik=333, breach_date="2019-03-01", reported_date=None,
         org_name="Gamma", fcc_form499=1, has_crsp_data=0),
])
_gl = pd.DataFrame([
    dict(final_cik=111, breach_date="2020-06-01", v4_linked=1, permno=10001),
    dict(final_cik=222, breach_date="2021-01-01", v4_linked=0, permno=None),
    dict(final_cik=333, breach_date="2019-03-01", v4_linked=1, permno=10003),
])
_gv = pd.DataFrame([
    dict(final_cik=111, breach_date="2020-06-01", firm_size_log=1.0, leverage=0.1, roa=0.1),
    dict(final_cik=222, breach_date="2021-01-01", firm_size_log=1.0, leverage=0.1, roa=0.1),
    dict(final_cik=333, breach_date="2019-03-01", firm_size_log=1.0, leverage=0.1, roa=0.1),
])
# build_gap now takes outcome_cik from scripts/234; without it every event
# reads as "outcome unresolved" and therefore as needing a fetch.
_go = {(111, "2020-06-01"): {"outcome_cik": 111, "outcome_rule": "final_cik"},
       (222, "2021-01-01"): {"outcome_cik": 222, "outcome_rule": "final_cik"},
       (333, "2019-03-01"): {"outcome_cik": 333, "outcome_rule": "final_cik"}}
_gap = _m230.build_gap(_gc, _gl, _gv, None, {333: 4}, _go)
_r = _gap.set_index("final_cik")
d1 = int(_r.loc[111, "in_scope"]) == 1 and int(_r.loc[111, "needs_fetch"]) == 1
d2 = int(_r.loc[222, "in_scope"]) == 0        # inherited has_crsp_data must not rescue it
d3 = int(_r.loc[333, "in_scope"]) == 1 and int(_r.loc[333, "needs_fetch"]) == 0
d4 = _r.loc[333, "win_lo"] == "2017-03-01" and _r.loc[333, "win_hi"] == "2019-08-28"
d5 = int(_r.loc[333, "rd_missing"]) == 1
d6 = _r.loc[111, "win_lo"] == "2018-06-02"    # 730d before the EARLIER anchor
#    2018-06-02, not 06-01: 2020 is a leap year, so 730 calendar days back from
#    2020-06-01 crosses 2020-02-29. The window is days, never "two years".
# abort() flushes its log to module OUT; point it at the temp dir so the suite
# never writes into the repository (it did, once).
_m230.OUT = TMP
try:
    _m230.require(Path("scripts/__nope__.csv"))
    d7 = False
except SystemExit:
    d7 = True
# Assert the abort log landed in the TEMP dir. Checking that the repo copy is
# ABSENT is wrong: 230 has legitimately run, so that file exists on purpose.
d7 = d7 and (TMP / "230_outcome_gap.md").exists()
print(f"  {'PASS' if d1 else 'FAIL'} | linked + covariates + no cache -> needs_fetch")
print(f"  {'PASS' if d2 else 'FAIL'} | v3 has_crsp_data=1 but v4_linked=0 -> OUT of scope")
print(f"  {'PASS' if d3 else 'FAIL'} | already-cached CIK is in scope but needs no fetch")
print(f"  {'PASS' if d4 else 'FAIL'} | missing reported_date -> window runs off breach_date")
print(f"  {'PASS' if d5 else 'FAIL'} | missing reported_date is flagged")
print(f"  {'PASS' if d6 else 'FAIL'} | pre-window is 730d off the earlier anchor")
print(f"  {'PASS' if d7 else 'FAIL'} | a missing input ABORTS, writing nothing into the repo")
results.append(all([d1, d2, d3, d4, d5, d6, d7]))

print("\n" + "=" * 70)
print("TEST: 233 reconciles RESOLVE against v4 re-parenting")
print("=" * 70)
_m233 = load(Path("scripts/233_resolve_reconciliation.py"), "m233")
_src = TMP / "fake199.py"
_src.write_text(
    "RESOLVE = {900: ('EXCLUDE', None, 'no 8-K filer'),\n"
    "           901: ('FIX', 700, 'files under 700'),\n"
    "           902: ('FIX', 800, 'files under 800'),\n"
    "           903: ('FIX', 999, 'no such event')}\n", encoding="utf-8")
_rs = _m233.parse_resolve(_src)
e0 = _rs[901][1] == 700 and _rs[900][0] == "EXCLUDE"
_rc = pd.DataFrame([
    dict(final_cik=900, orig_cik=900, link_basis="direct", org_name="Nokia-like",
         breach_date="2013-07-22", fcc_form499=0),
    dict(final_cik=700, orig_cik=901, link_basis="successor_filing", org_name="Aon-like",
         breach_date="2020-12-29", fcc_form499=0),
    dict(final_cik=555, orig_cik=902, link_basis="successor_filing", org_name="Disney-like",
         breach_date="2008-07-29", fcc_form499=0),
])
_ln = {(900, "2013-07-22"): pd.Series(dict(v4_linked=0, permno=None)),
       (700, "2020-12-29"): pd.Series(dict(v4_linked=1, permno=61735)),
       (555, "2008-07-29"): pd.Series(dict(v4_linked=1, permno=26403))}
_oc = {(700, "2020-12-29"): 700, (555, "2008-07-29"): 555}
_out = _m233.reconcile(_rs, _rc, _ln, _oc).set_index("resolve_cik")
e1 = _out.loc[900, "verdict"] == "agree"     # EXCLUDE + not linked
e2 = _out.loc[901, "verdict"] == "agree"     # v4 reached the same CIK
e3 = _out.loc[902, "verdict"] == "disagree"  # v4 re-parented elsewhere
e4 = _out.loc[903, "verdict"] == "disagree"  # RESOLVE names an event v4 does not have
# an EXCLUDE that v4 DOES link must flip to disagree
_ln2 = dict(_ln); _ln2[(900, "2013-07-22")] = pd.Series(dict(v4_linked=1, permno=87128))
e5 = _m233.reconcile({900: _rs[900]}, _rc, _ln2, _oc).iloc[0]["verdict"] == "disagree"
for _f, _lab in [(e0, "RESOLVE parsed from source without importing 199"),
                 (e1, "EXCLUDE + v4 does not link -> agree"),
                 (e2, "v4 re-parented to the same CIK -> agree"),
                 (e3, "v4 re-parented elsewhere -> disagree"),
                 (e4, "RESOLVE names an event v4 does not carry -> disagree"),
                 (e5, "EXCLUDE but v4 links it -> disagree")]:
    print(f"  {'PASS' if _f else 'FAIL'} | {_lab}")
results.append(all([e0, e1, e2, e3, e4, e5]))


print("\n" + "=" * 70)
print("TEST: 219 sends gvkeys as 6-char zero-padded strings (run-1 abort)")
print("=" * 70)
_m219b = load(Path("scripts/219_wrds_funda_v4.py"), "m219b")
_m219b.OUT = TMP          # abort() flushes its log; keep it out of the repository
g1 = _m219b.norm_gvkey(1300.0) == "001300"
g2 = _m219b.norm_gvkey(_np.float64(1440.0)) == "001440"
g3 = _m219b.norm_gvkey("001300") == "001300"
g4 = _m219b.norm_gvkey(17874.0) == "017874"      # T-Mobile
g5 = _m219b.norm_gvkey(9899.0) == "009899"       # AT&T
g6 = _m219b.norm_gvkey(10984.0) == "010984"      # Sprint
g7 = _m219b.norm_gvkey(float("nan")) == "" and _m219b.norm_gvkey("") == ""
g8 = _m219b.sql_values(["001300"]) == "'001300'"
# the exact defect: zfill on a float's repr is a no-op because it is already 6 chars
g9 = str(1440.0).zfill(6) == "1440.0" and _m219b.norm_gvkey(1440.0) == "001440"
_sl = pd.DataFrame([
    dict(final_cik=1283699, gvkey=17874.0), dict(final_cik=732717, gvkey=9899.0),
    dict(final_cik=101830, gvkey=10984.0), dict(final_cik=999, gvkey=1440.0)])
_sg = _m219b.sentinel_gvkeys(_sl)
g10 = (_sg["T-Mobile"] == {"017874"} and _sg["AT&T"] == {"009899"}
       and _sg["Sprint"] == {"010984"})
try:
    _m219b.sentinel_gvkeys(_sl[_sl["final_cik"] != 101830])
    g11 = False
except SystemExit:
    g11 = True
# a float-keyed links file must still join to a string-keyed funda file
_fl = pd.DataFrame([dict(final_cik=111, breach_date="2020-06-01", gvkey=1234.0)])
_ff = _fr(["2019-12-31"])                       # funda gvkey is the string "001234"
_fc = pd.DataFrame([dict(final_cik=111, breach_date="2020-06-01", org_name="Acme",
                         fcc_form499=0, matched_ticker="", firm_size_log=None,
                         leverage=None, roa=None, op_margin=None)])
g12 = _m219b.build_covariates(_fc, _fl, _ff).loc[0, "firm_size_log"] == round(
    _np.log(100.0), 4)
for _f, _lab in [(g1, "float 1300.0 -> '001300'"),
                 (g2, "numpy float64 1440.0 -> '001440'"),
                 (g3, "an already-padded string is unchanged"),
                 (g4, "T-Mobile 17874.0 -> '017874'"),
                 (g5, "AT&T 9899.0 -> '009899'"),
                 (g6, "Sprint 10984.0 -> '010984'"),
                 (g7, "NaN and empty become '' (dropped, never sent)"),
                 (g8, "the SQL literal is quoted as '001300'"),
                 (g9, "regression: str(1440.0).zfill(6) is a no-op, norm_gvkey is not"),
                 (g10, "sentinel CIKs resolve to their gvkeys"),
                 (g11, "a sentinel with no gvkey ABORTS naming the step"),
                 (g12, "float-keyed links join to string-keyed funda")]:
    print(f"  {'PASS' if _f else 'FAIL'} | {_lab}")
results.append(all([g1, g2, g3, g4, g5, g6, g7, g8, g9, g10, g11, g12]))


print("\n" + "=" * 70)
print("TEST: 234 outcome_cik rule (window, predecessor, 8-K counts, fall-through)")
print("=" * 70)
_m234 = load(Path("scripts/234_outcome_cik_v4.py"), "m234")
_m234.OUT = TMP

# --- fetch window: 730d off the EARLIER anchor, 180d off the LATER ---
_lo, _hi = _m234.fetch_window("2020-06-01", "2020-07-01")
h1 = _lo.date().isoformat() == "2018-06-02" and _hi.date().isoformat() == "2020-12-28"
# breach AFTER reported (v3's recoded / wrong-field delays) -> post-window off breach
_lo2, _hi2 = _m234.fetch_window("2021-03-01", "2020-12-01")
h2 = _lo2.date().isoformat() == "2018-12-02" and _hi2.date().isoformat() == "2021-08-28"
# missing reported_date -> rd_eff = breach_date
_lo3, _hi3 = _m234.fetch_window("2019-03-01", None)
h3 = _lo3.date().isoformat() == "2017-03-01" and _hi3.date().isoformat() == "2019-08-28"

# --- predecessor term must be cut at 'pursuant' (the run-1 defect) ---
h4 = _m234.predecessor_term(
    "establishing Disney as the successor issuer to Old Disney pursuant to Rule "
    "12g-3(a) under the Securities Exchange Act of 1934") == "Old Disney"
h5 = _m234.predecessor_term(
    "Alphabet, a Delaware corporation, became the successor issuer to Google, a "
    "Delaware corporation.") == "Google"
h6 = _m234.predecessor_term("no succession language here") == ""

# --- defined term -> legal name ---
_disney = ('among Twenty-First Century Fox, Inc. (“ 21CF ”), TWDC Enterprises '
           '18 Corp. (formerly known as The Walt Disney Company) (“ Old Disney ”), '
           'The Walt Disney Company')
h7 = _m234.resolve_definition(_disney, "Old Disney") == "TWDC Enterprises 18 Corp."
_sbg = ('the company formerly known as Sinclair Broadcast Group, Inc., a Maryland '
        'corporation (“ SBG ”)')
h8 = _m234.resolve_definition(_sbg, "SBG") == "Sinclair Broadcast Group, Inc."
h9 = _m234.resolve_definition(_disney, "Nonexistent Term") == ""

# --- 8-K counting ---
_pages = [{"form": ["8-K", "8-K/A", "8-K12B", "10-K", "8-K"],
           "filingDate": ["2020-01-15", "2020-02-01", "2020-03-01", "2020-04-01",
                          "2019-01-01"]}]
_lo4, _hi4 = pd.Timestamp("2020-01-01"), pd.Timestamp("2020-03-31")
h10 = _m234.count_8k(_pages, _lo4, _hi4) == 3          # 10-K excluded, 2019 outside
h11 = _m234.count_8k(_pages, pd.Timestamp("2020-01-15"),
                     pd.Timestamp("2020-01-15")) == 1   # boundaries inclusive
h12 = _m234.count_8k(None, _lo4, _hi4) == 0

# --- the fall-through rule: an UNCACHED higher rank blocks, a definite 0 does not ---
_ev = dict(final_cik=1744489, orig_cik=926480, breach_date="2008-07-29",
           reported_date="2008-07-29", org_name="Disney-like", fcc_form499=0,
           link_basis="successor_filing")
_mk = lambda d: [{"form": ["8-K"] * len(d), "filingDate": d}]


def _pages_uncached_final(cik):
    return None if int(cik) == 1744489 else _mk(["2008-01-02"])


def _pages_zero_final(cik):
    return _mk([]) if int(cik) == 1744489 else _mk(["2008-01-02"])


_r1, _e1, _n1 = _m234.resolve_event(pd.Series(_ev), {}, _pages_uncached_final, {},
                                    lambda b: [], {})
h13 = _r1["outcome_cik"] is None and "submissions_not_cached" in _r1["unresolved_reason"]
h14 = 1744489 in _n1
_r2, _e2, _n2 = _m234.resolve_event(pd.Series(_ev), {}, _pages_zero_final, {},
                                    lambda b: [], {})
h15 = _r2["outcome_cik"] == 926480 and _r2["outcome_rule"] == "orig_cik"
h16 = int(_r2["differs_from_final"]) == 1

# --- name index: unique only ---
_idx = {"TWDC ENTERPRISES 18 CORP.": {1001039}, "GOOGLE INC": {1302837, 1136101}}
h17 = _m234.name_to_cik(_idx, "TWDC Enterprises 18 Corp.")[0] == 1001039
h18 = _m234.name_to_cik(_idx, "Google Inc")[0] is None      # ambiguous -> refuse
h19 = _m234.name_to_cik(_idx, "")[0] is None

for _f, _lab in [(h1, "window: 730d before the earlier anchor (leap-year exact)"),
                 (h2, "window: breach after reported -> post-window off breach"),
                 (h3, "window: missing reported_date -> rd_eff = breach_date"),
                 (h4, "predecessor term cut at 'pursuant' -> 'Old Disney'"),
                 (h5, "predecessor term stops at the comma -> 'Google'"),
                 (h6, "no succession language -> no term"),
                 (h7, "'Old Disney' -> 'TWDC Enterprises 18 Corp.'"),
                 (h8, "'SBG' -> 'Sinclair Broadcast Group, Inc.'"),
                 (h9, "an undefined term resolves to nothing"),
                 (h10, "8-K/8-K/A/8-K12B counted, 10-K not, outside window not"),
                 (h11, "window boundaries are inclusive"),
                 (h12, "uncached submissions count as 0 rows, not a crash"),
                 (h13, "UNCACHED higher rank BLOCKS - no fall-through"),
                 (h14, "the uncached CIK is added to the 231 fetch list"),
                 (h15, "a DEFINITE zero falls through to orig_cik"),
                 (h16, "and is flagged as differing from final_cik"),
                 (h17, "unique name -> CIK"),
                 (h18, "ambiguous name -> refused, never guessed"),
                 (h19, "empty name -> refused")]:
    print(f"  {'PASS' if _f else 'FAIL'} | {_lab}")
results.append(all([h1, h2, h3, h4, h5, h6, h7, h8, h9, h10, h11, h12, h13, h14,
                    h15, h16, h17, h18, h19]))

print("\n" + "=" * 70)
print("TEST: 233 reconciles against outcome_cik, pending when unresolved")
print("=" * 70)
_m233b = load(Path("scripts/233_resolve_reconciliation.py"), "m233b")
_rc2 = pd.DataFrame([
    dict(final_cik=1744489, orig_cik=926480, link_basis="successor_filing",
         org_name="Disney-like", breach_date="2008-07-29", fcc_form499=0)])
_ln3 = {(1744489, "2008-07-29"): pd.Series(dict(v4_linked=1, permno=26403))}
_rv = {926480: ("FIX", 1001039, "files under 1001039")}
k1 = _m233b.reconcile(_rv, _rc2, _ln3, {(1744489, "2008-07-29"): 1001039}
                      ).iloc[0]["verdict"] == "agree"
k2 = _m233b.reconcile(_rv, _rc2, _ln3, {(1744489, "2008-07-29"): None}
                      ).iloc[0]["verdict"] == "pending"
k3 = _m233b.reconcile(_rv, _rc2, _ln3, {(1744489, "2008-07-29"): 999999}
                      ).iloc[0]["verdict"] == "disagree"
k4 = _m233b.reconcile(_rv, _rc2, _ln3, {}).iloc[0]["verdict"] == "pending"
for _f, _lab in [(k1, "outcome_cik == RESOLVE target -> agree"),
                 (k2, "outcome_cik unresolved -> pending, never agree"),
                 (k3, "outcome_cik != RESOLVE target -> disagree"),
                 (k4, "234 not run -> pending")]:
    print(f"  {'PASS' if _f else 'FAIL'} | {_lab}")
results.append(all([k1, k2, k3, k4]))


print("\n" + "=" * 70)
print("TEST: 231 SEC fetch - submissions shape, 5.02 selection, frozen draw")
print("=" * 70)
_m231 = load(Path("scripts/231_fetch_outcome_data_v4.py"), "m231")
_m231.OUT = TMP          # abort()/write_log() must never touch the repository


class _FakeSEC:
    """Mocked EDGAR. Records every URL so the request pattern is assertable."""

    def __init__(self, bodies):
        self.bodies, self.urls = bodies, []

    def fetch(self, url):
        self.urls.append(url)
        return self.bodies.get(url)


_main = ("https://data.sec.gov/submissions/CIK0000123456.json")
_shard = "https://data.sec.gov/submissions/CIK0000123456-submissions-001.json"
_sec = _FakeSEC({
    _main: json.dumps({"filings": {
        "recent": {"form": ["8-K"], "filingDate": ["2020-01-01"],
                   "items": ["5.02"], "accessionNumber": ["0000-01"],
                   "primaryDocument": ["a.htm"]},
        "files": [{"name": "CIK0000123456-submissions-001.json"}]}}).encode(),
    _shard: json.dumps({"form": ["10-K"], "filingDate": ["2019-01-01"],
                        "items": [""], "accessionNumber": ["0000-02"],
                        "primaryDocument": ["b.htm"]}).encode(),
})
_pages = _m231.submission_pages(123456, _sec)
q1 = isinstance(_pages, list) and len(_pages) == 2
q2 = _pages[0]["form"] == ["8-K"] and _pages[1]["form"] == ["10-K"]
q3 = _sec.urls == [_main, _shard]                      # zero-padded CIK, shard followed
q4 = _m231.submission_pages(999, _FakeSEC({})) is None  # absent -> None, not a crash
# the written shape must be the one 234 reads
_m234b = load(Path("scripts/234_outcome_cik_v4.py"), "m234b")
q5 = _m234b.count_8k(_pages, pd.Timestamp("2019-12-31"), pd.Timestamp("2020-12-31")) == 1

# --- Item 5.02 selection ---
_p502 = [{"form": ["8-K", "8-K", "8-K/A", "10-K", "8-K"],
          "filingDate": ["2020-01-15", "2020-02-01", "2020-02-10", "2020-03-01",
                         "2018-01-01"],
          "items": ["5.02", "2.02,7.01", "5.02,8.01", "5.02", "5.02"],
          "accessionNumber": ["a1", "a2", "a3", "a4", "a5"],
          "primaryDocument": ["d1.htm", "d2.htm", "d3.htm", "d4.htm", "d5.htm"]}]
_got = _m231.item502_filings(_p502, pd.Timestamp("2020-01-01"),
                             pd.Timestamp("2020-12-31"))
_accs = sorted(f["accession"] for f in _got)
q6 = _accs == ["a1", "a3"]      # a2 no 5.02, a4 is a 10-K, a5 outside the window
q7 = _m231.item502_filings([], pd.Timestamp("2020-01-01"),
                           pd.Timestamp("2020-12-31")) == []

# The validation draw moved to scripts/237: its pool must be "every document v4
# added", which 231 cannot know - it only knows what it fetched. Covered by the
# 237 test block below.

# --- a missing input ABORTS, writing a PARTIAL log that names the phase ---
# Snapshot the REAL log's mtime: asserting it is absent is wrong once 231 has
# legitimately been run, so assert the abort did not TOUCH it instead.
_real231 = Path("outputs/rebuild_v4/231_fetch_log.md")
_real231_before = _real231.stat().st_mtime_ns if _real231.exists() else None
_m231.ROWS.clear()
_m231.ROWS.append(dict(phase="documents", cik=1, status="fetched"))
_m231.PHASE["name"] = "documents"
_m231.PHASE["detail"] = "CIK 1 (1/9)"
try:
    _m231.require(Path("scripts/__nope__.csv"))
    q14 = False
except SystemExit:
    q14 = True
_lg = (TMP / "231_fetch_log.md")
_txt = _lg.read_text(encoding="utf-8") if _lg.exists() else ""
q15 = "ABORTED" in _txt and "documents" in _txt and "CIK 1 (1/9)" in _txt
q16 = (TMP / "231_fetch_rows.csv").exists()             # partial rows written
q17 = ((_real231.stat().st_mtime_ns if _real231.exists() else None)
       == _real231_before)
_m231.ROWS.clear()

# --- 235: a CIK that already holds SOME documents must still be checked ---
# (Seagate held 16 v3 documents, so 230's CIK-level needs_fetch was 0 and 5 filings
# inside v4's wider window were never fetched. 231 now scopes on in_scope, and 235
# is the check that would catch any recurrence.)
_m235 = load(Path("scripts/235_fetch_completeness_v4.py"), "m235")
_m235.OUT = TMP
_m235.TXT = TMP / "item5_02_text"
(_m235.TXT / "777").mkdir(parents=True, exist_ok=True)
(_m235.TXT / "777" / "a1_d1.htm").write_bytes(b"x")     # one of two on disk
_gapf = pd.DataFrame([dict(final_cik=777, outcome_cik=777, org_name="Partial Inc",
                           breach_date="2016-02-29", treated=0, in_scope=1,
                           win_lo="2014-03-01", win_hi="2016-09-05")])
_pg = [{"form": ["8-K", "8-K"], "filingDate": ["2015-05-01", "2015-06-01"],
        "items": ["5.02", "5.02"], "accessionNumber": ["a1", "a2"],
        "primaryDocument": ["d1.htm", "d2.htm"]}]
_cmp = _m235.build(_gapf, lambda c: _pg, _m231.item502_filings)
q18 = len(_cmp) == 2 and int(_cmp["on_disk"].sum()) == 1
q19 = set(_cmp.loc[_cmp["on_disk"] == 0, "accession"]) == {"a2"}
# a genuine zero: the index lists nothing in-window
_cmp2 = _m235.build(_gapf, lambda c: [{"form": ["10-K"], "filingDate": ["2015-05-01"],
                                       "items": [""], "accessionNumber": ["z1"],
                                       "primaryDocument": ["z.htm"]}],
                    _m231.item502_filings)
q20 = len(_cmp2) == 1 and _cmp2.iloc[0]["accession"] == ""

for _f, _lab in [(q1, "submissions assemble as [recent, *shards]"),
                 (q2, "both pages preserved in order"),
                 (q3, "CIK zero-padded to 10 chars; shard fetched after the index"),
                 (q4, "an absent CIK returns None, not a crash"),
                 (q5, "the written shape is the one 234 reads"),
                 (q6, "only 8-K* filings listing 5.02 inside the window"),
                 (q7, "no pages -> no filings"),
                 (q14, "a missing input ABORTS"),
                 (q15, "the partial log names the phase and the last item"),
                 (q16, "partial fetch rows are written on abort"),
                 (q17, "the abort did not touch the real run log in the repository"),
                 (q18, "a partly-fetched CIK still reports its missing document"),
                 (q19, "the missing accession is named"),
                 (q20, "an index with no 5.02 in-window is a genuine zero")]:
    print(f"  {'PASS' if _f else 'FAIL'} | {_lab}")
results.append(all([q1, q2, q3, q4, q5, q6, q7, q14,
                    q15, q16, q17, q18, q19, q20]))


print("\n" + "=" * 70)
print("TEST: 236 loader drops v3's inherited columns and re-attaches v4's")
print("=" * 70)
_m236 = load(Path("scripts/236_essay3_v4_loader.py"), "m236")
_d = TMP / "v4load"
_d.mkdir(parents=True, exist_ok=True)
# CANONICAL_V4 carries v3's values: Nokia-like row says linked with a permno,
# and the covariates are the stale ticker-joined ones.
pd.DataFrame([
    dict(final_cik=924613, breach_date="2013-07-22", org_name="Nokia-like",
         fcc_form499=0, reported_date="2013-07-22", has_crsp_data=1, permno=87128,
         firm_size_log=9.99, leverage=0.99, roa=0.99, op_margin=0.99),
    dict(final_cik=111, breach_date="2020-06-01", org_name="Acme", fcc_form499=1,
         reported_date="2020-07-01", has_crsp_data=1, permno=10001,
         firm_size_log=9.99, leverage=0.99, roa=0.99, op_margin=0.99),
]).to_csv(_d / "canon.csv", index=False)
pd.DataFrame([
    dict(final_cik=924613, breach_date="2013-07-22", v4_linked=0, permno=87128),
    dict(final_cik=111, breach_date="2020-06-01", v4_linked=1, permno=10001),
]).to_csv(_d / "links.csv", index=False)
pd.DataFrame([
    dict(final_cik=924613, breach_date="2013-07-22", firm_size_log=None,
         leverage=None, roa=None, op_margin=None),
    dict(final_cik=111, breach_date="2020-06-01", firm_size_log=4.6052,
         leverage=0.4, roa=0.05, op_margin=0.25),
]).to_csv(_d / "cov.csv", index=False)
pd.DataFrame([
    dict(final_cik=924613, breach_date="2013-07-22", outcome_cik=None,
         outcome_rule="none"),
    dict(final_cik=111, breach_date="2020-06-01", outcome_cik=111,
         outcome_rule="final_cik"),
]).to_csv(_d / "outcome.csv", index=False)
_m236.CANON, _m236.LINKS = _d / "canon.csv", _d / "links.csv"
_m236.COVAR, _m236.OUTCOME = _d / "cov.csv", _d / "outcome.csv"
_ev = _m236.load_canonical().set_index("final_cik")
r1 = int(_ev.loc[924613, "has_crsp_data"]) == 0        # v4 does NOT link Nokia
r2 = pd.isna(_ev.loc[924613, "permno"])                # and its v3 permno is dropped
r3 = int(_ev.loc[111, "has_crsp_data"]) == 1 and int(_ev.loc[111, "permno"]) == 10001
r4 = _ev.loc[111, "firm_size_log"] == 4.6052           # refreshed, not the 9.99 stub
r5 = pd.isna(_ev.loc[924613, "firm_size_log"])
r6 = int(_ev.loc[111, "outcome_cik"]) == 111 and pd.isna(_ev.loc[924613, "outcome_cik"])

# --- RESOLVE must be settled before anything downstream runs ---
_rc = _d / "recon.csv"
pd.DataFrame([dict(resolve_cik=1, org_name="x", breach_date="2020-01-01",
                   v4_final_cik=111, verdict="agree")]).to_csv(_rc, index=False)
_m236.RECON = _rc
r7 = _m236.require_resolve_settled() == {(111, "2020-01-01")}
for _bad in ("disagree", "pending"):
    pd.DataFrame([dict(resolve_cik=1, org_name="x", breach_date="2020-01-01",
                       v4_final_cik=111, verdict=_bad)]).to_csv(_rc, index=False)
    try:
        _m236.require_resolve_settled()
        globals()["r8_" + _bad] = False
    except SystemExit:
        globals()["r8_" + _bad] = True
r8 = r8_disagree and r8_pending

for _f, _lab in [(r1, "v3 has_crsp_data=1 is replaced by v4_linked=0"),
                 (r2, "the v3 permno is dropped when v4 did not link"),
                 (r3, "a genuinely linked event keeps v4's permno"),
                 (r4, "covariates come from 219, not the inherited column"),
                 (r5, "an event 219 could not cover has no covariates"),
                 (r6, "outcome_cik is merged from 234"),
                 (r7, "a settled reconciliation returns the agreed keys"),
                 (r8, "a 'disagree' or 'pending' row ABORTS")]:
    print(f"  {'PASS' if _f else 'FAIL'} | {_lab}")
results.append(all([r1, r2, r3, r4, r5, r6, r7, r8]))

print("\n" + "=" * 70)
print("TEST: 220-229 and 232 never read CANONICAL_V4 directly")
print("=" * 70)
_v4scripts = sorted(Path("scripts").glob("22[0-9]_essay3_v4_*.py")) + \
             [Path("scripts/232_censoring_report_v4.py")]
s1 = len(_v4scripts) == 11
_offenders = []
for _p in _v4scripts:
    _hits = _m236.assert_no_direct_canonical_read(_p)
    if _hits:
        _offenders.append((_p.name, _hits[0]))
s2 = not _offenders
# the guard must actually catch an offender
_bad_py = TMP / "bad_script.py"
_bad_py.write_text("import pandas as pd\n"
                   "ev = pd.read_csv('Data/processed/rebuild_v4/CANONICAL_V4.csv')\n",
                   encoding="utf-8")
s3 = len(_m236.assert_no_direct_canonical_read(_bad_py)) == 1
# a comment naming the file is allowed
_ok_py = TMP / "ok_script.py"
_ok_py.write_text("# CANONICAL_V4.csv is loaded through scripts/236\n", encoding="utf-8")
s4 = _m236.assert_no_direct_canonical_read(_ok_py) == []
# the v3 originals must be untouched by all of this
s5 = all(Path("scripts", n).exists() for n in
         ("195_essay3_q2_classifier_v2.py", "199_essay3_q2_sample_e.py",
          "202_essay3_q2_estimation.py", "204_essay3_q2_se_diagnostics.py"))
# 224 must not carry v3's RESOLVE patch list any more
_t224 = Path("scripts/224_essay3_v4_sample_e.py").read_text(encoding="utf-8")
s6 = "RESOLVE = {924613" not in _t224 and "V4.require_resolve_settled()" in _t224
s7 = "outputs/essay3_q2" not in _t224
print(f"  {'PASS' if s1 else 'FAIL'} | all 11 v4 Essay 3 scripts present ({len(_v4scripts)})")
print(f"  {'PASS' if s2 else 'FAIL'} | none reads CANONICAL_V4 directly"
      + ("" if s2 else f" -> {_offenders[:2]}"))
print(f"  {'PASS' if s3 else 'FAIL'} | the guard catches a direct read")
print(f"  {'PASS' if s4 else 'FAIL'} | a comment naming the file is allowed")
print(f"  {'PASS' if s5 else 'FAIL'} | the v3 originals 195-204 are untouched")
print(f"  {'PASS' if s6 else 'FAIL'} | 224 drops RESOLVE and requires 233 settled")
print(f"  {'PASS' if s7 else 'FAIL'} | 224 writes to essay3_v4, not essay3_q2")
results.append(all([s1, s2, s3, s4, s5, s6, s7]))

print("\n" + "=" * 70)
print("TEST: 232 censoring - window past the outcome CIK's last filing")
print("=" * 70)
_m232 = load(Path("scripts/232_censoring_report_v4.py"), "m232")
_m232.OUT = TMP
_pgs = {555: [{"form": ["10-K"], "filingDate": ["2020-08-01"]}],      # alive to Aug 2020
        556: [{"form": ["10-K"], "filingDate": ["2019-01-01"]}]}      # dead before t0
_evc = pd.DataFrame([
    dict(final_cik=555, breach_date="2020-06-01", reported_date="2020-06-01",
         org_name="Censored Co", fcc_form499=0, outcome_cik=555),
    dict(final_cik=556, breach_date="2020-06-01", reported_date="2020-06-01",
         org_name="Dead Co", fcc_form499=1, outcome_cik=556),
    dict(final_cik=557, breach_date="2020-06-01", reported_date="2020-06-01",
         org_name="No CIK", fcc_form499=0, outcome_cik=None),
])
_cen = _m232.build(_evc, lambda c: _pgs.get(int(c))).set_index("final_cik")
# 2020-06-01 +30d = 2020-07-01 <= 2020-08-01 -> covered; +90d = 2020-08-30 -> censored
t1 = int(_cen.loc[555, "censored_30_rd"]) == 0
t2 = int(_cen.loc[555, "censored_90_rd"]) == 1 and int(_cen.loc[555, "censored_180_rd"]) == 1
t3 = int(_cen.loc[555, "days_uncovered_90_rd"]) == 29
t4 = int(_cen.loc[556, "never_covered_rd"]) == 1 and int(_cen.loc[555, "never_covered_rd"]) == 0
t5 = _cen.loc[557, "status"] == "no_outcome_cik"
t6 = _cen.loc[555, "last_filing"] == "2020-08-01"
for _f, _lab in [(t1, "a window ending before the last filing is NOT censored"),
                 (t2, "90d and 180d windows past the last filing ARE censored"),
                 (t3, "the uncovered days are counted (2020-08-30 - 2020-08-01)"),
                 (t4, "a CIK whose filings stop before t0 is 'never covered'"),
                 (t5, "an event with no outcome_cik is flagged, not silently dropped"),
                 (t6, "the last filing of ANY form is used, not just 8-Ks")]:
    print(f"  {'PASS' if _f else 'FAIL'} | {_lab}")
results.append(all([t1, t2, t3, t4, t5, t6]))


print("\n" + "=" * 70)
print("TEST: 213 fetch(cache=False) bypasses ex21_cache_v4 entirely")
print("=" * 70)
import os as _os3
_m213c = load(Path("scripts/213_stage3_verify.py"), "m213_cache")
_os3.environ[_m213c.UA_ENV] = "Offline Test test@example.edu"
_m213c.CACHE = TMP / "ex21cache"
_m213c.CACHE.mkdir(parents=True, exist_ok=True)
_m213c.MIN_INTERVAL = 0.0


class _FakeResp:
    def __init__(self, data):
        self.data, self.status = data, 200

    def read(self):
        return self.data

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


_hits = []


def _fake_urlopen(req, timeout=None):
    _hits.append(getattr(req, "full_url", str(req)))
    return _FakeResp(b"<html><body>a filing document</body></html>")


_m213c.urlopen = _fake_urlopen
_u1 = "https://www.sec.gov/Archives/edgar/data/1/1/doc_nocache.htm"
_u2 = "https://www.sec.gov/Archives/edgar/data/1/1/doc_cached.htm"
_d1 = _m213c.fetch(_u1, cache=False)
_d2 = _m213c.fetch(_u2, cache=True)
w1 = _d1 == b"<html><body>a filing document</body></html>"
w2 = not _m213c.cache_path(_u1).exists()      # nothing written
w3 = _m213c.cache_path(_u2).exists()          # default behaviour unchanged
# a cached copy must not even be READ when cache=False
_m213c.cache_path(_u1).write_bytes(b"STALE")
_before = len(_hits)
_d3 = _m213c.fetch(_u1, cache=False)
w4 = _d3 != b"STALE" and len(_hits) == _before + 1
_m213c.cache_path(_u1).unlink()
# and IS read when cache=True
_before2 = len(_hits)
_d4 = _m213c.fetch(_u2, cache=True)
w5 = _d4 == _d2 and len(_hits) == _before2    # served from disk, no request
# 231 must actually pass cache=False for documents
_t231 = Path("scripts/231_fetch_outcome_data_v4.py").read_text(encoding="utf-8")
w6 = "m.fetch(url, cache=False)" in _t231
for _f, _lab in [(w1, "cache=False still returns the bytes"),
                 (w2, "cache=False writes nothing to ex21_cache_v4"),
                 (w3, "cache=True still writes (default unchanged)"),
                 (w4, "cache=False does not READ a stale cached copy"),
                 (w5, "cache=True still serves from disk without a request"),
                 (w6, "231 fetches documents with cache=False")]:
    print(f"  {'PASS' if _f else 'FAIL'} | {_lab}")
results.append(all([w1, w2, w3, w4, w5, w6]))

print("\n" + "=" * 70)
print("TEST: 224 is fully offline")
print("=" * 70)
_src224 = Path("scripts/224_essay3_v4_sample_e.py").read_text(encoding="utf-8")
x1 = "import requests" not in _src224 and "requests.get" not in _src224
x2 = "urlopen" not in _src224
x3 = "User-Agent" not in _src224 and "southalabama.edu" not in _src224
x4 = "224 is offline; missing cached input" in _src224
# AST: no call to a network entry point survives anywhere in the file
import ast as _ast3
_tree224 = _ast3.parse(_src224)
# Precise: a bare .get( is dict.get / Series.get, which is everywhere. Only a call
# ON a network module, or a bare network entry point, counts.
_NET_MODULES = {"requests", "urllib", "httpx", "http", "urllib3", "aiohttp"}
_NET_NAMES = {"urlopen", "urlretrieve", "Request"}
_net_calls = []
for _n in _ast3.walk(_tree224):
    if not isinstance(_n, _ast3.Call):
        continue
    _f = _n.func
    if isinstance(_f, _ast3.Attribute) and isinstance(_f.value, _ast3.Name)             and _f.value.id in _NET_MODULES:
        _net_calls.append(_f.value.id + "." + _f.attr)
    elif isinstance(_f, _ast3.Name) and _f.id in _NET_NAMES:
        _net_calls.append(_f.id)
# and no network module may even be imported
for _n in _ast3.walk(_tree224):
    if isinstance(_n, _ast3.Import):
        _net_calls += [a.name for a in _n.names if a.name.split(".")[0] in _NET_MODULES]
    elif isinstance(_n, _ast3.ImportFrom) and (_n.module or "").split(".")[0] in _NET_MODULES:
        _net_calls.append(_n.module)
x5 = not _net_calls

# functional: run pages_for in isolation (224 has no main guard, so it cannot be
# imported without executing the whole analysis)
_fn = None
for _n in _tree224.body:
    if isinstance(_n, _ast3.FunctionDef) and _n.name == "pages_for":
        _fn = _ast3.get_source_segment(_src224, _n)
x6 = _fn is not None
if x6:
    _ns = {"Path": Path, "json": json, "SUBS_V4": TMP / "subs_v4",
           "OCC": TMP / "occ", "SystemExit": SystemExit}
    exec(_fn, _ns)
    try:
        _ns["pages_for"](999999)
        x7 = False
        _msg = ""
    except SystemExit as e:
        _msg = str(e)
        x7 = "224 is offline; missing cached input" in _msg
    (TMP / "subs_v4").mkdir(parents=True, exist_ok=True)
    (TMP / "subs_v4" / "424242.json").write_text(json.dumps([{"form": ["8-K"]}]),
                                                 encoding="utf-8")
    x8 = _ns["pages_for"](424242) == [{"form": ["8-K"]}]
else:
    x7 = x8 = False
    _msg = ""
for _f, _lab in [(x1, "no requests import and no requests.get"),
                 (x2, "no urlopen"),
                 (x3, "the hard-coded User-Agent is gone"),
                 (x4, "the offline abort message is present"),
                 (x5, "no network module imported and no network call in the AST"),
                 (x6, "pages_for is isolatable for testing"),
                 (x7, "a cache miss ABORTS naming the missing file"),
                 (x8, "a cache hit still returns the pages")]:
    print(f"  {'PASS' if _f else 'FAIL'} | {_lab}")
if _msg:
    print(f"         abort message: {_msg[:110]}")
results.append(all([x1, x2, x3, x4, x5, x6, x7, x8]))


print("\n" + "=" * 70)
print("TEST: 237 pool is defined by what v4 ADDED, not by fetch history")
print("=" * 70)
_m237 = load(Path("scripts/237_validation_draw_v4.py"), "m237")
_m237.OUT = TMP

_frozen = {"Data/edgar/item5_02_text/1/v3_a.htm",
           "Data/edgar/item5_02_text/1/v3_b.htm"}
_scope = {"Data/edgar/item5_02_text/1/v3_a.htm",
          "Data/edgar/item5_02_text/1/v3_b.htm",
          "Data/edgar/item5_02_text/1/v4_a.htm",
          "Data/edgar/item5_02_text/2/v4_b.htm",
          "Data/edgar/item5_02_text/2/v4_c.htm"}
_disk_all = _frozen | {"Data/edgar/item5_02_text/1/v4_a.htm",
                       "Data/edgar/item5_02_text/2/v4_b.htm",
                       "Data/edgar/item5_02_text/2/v4_c.htm",
                       "Data/edgar/item5_02_text/3/v4_out_of_scope.htm"}
_expected = ["Data/edgar/item5_02_text/1/v4_a.htm",
             "Data/edgar/item5_02_text/2/v4_b.htm",
             "Data/edgar/item5_02_text/2/v4_c.htm"]

# The whole point: the SAME end state must give the same pool however it was
# reached. One big fetch, or three small ones, or a re-run that fetched nothing.
y1 = _m237.build_pool(_disk_all, _frozen, _scope) == _expected
_after_first = _frozen | {"Data/edgar/item5_02_text/1/v4_a.htm"}
_after_second = _after_first | {"Data/edgar/item5_02_text/2/v4_b.htm"}
y2 = _m237.build_pool(_after_second, _frozen, _scope) == _expected[:2]
y3 = _m237.build_pool(_disk_all, _frozen, _scope) == \
     _m237.build_pool(set(reversed(sorted(_disk_all))), _frozen, _scope)
# a re-run that fetched nothing new must not empty the pool (the defect being fixed)
y4 = len(_m237.build_pool(_disk_all, _frozen, _scope)) == 3
# v3's own documents are never in the pool
y5 = not (set(_m237.build_pool(_disk_all, _frozen, _scope)) & _frozen)
# a v4 document outside b_scope_filings is excluded
y6 = "Data/edgar/item5_02_text/3/v4_out_of_scope.htm" not in \
     _m237.build_pool(_disk_all, _frozen, _scope)

# the draw is deterministic on the pool and capped at 30
_pool50 = ["Data/edgar/item5_02_text/9/d%02d.htm" % i for i in range(50)]
y7 = len(_m237.draw(_pool50)) == 30
y8 = _m237.draw(_pool50) == _m237.draw(list(reversed(_pool50)))
y9 = _m237.draw(_pool50[:7]) == sorted(_pool50[:7]) and _m237.draw([]) == []
y10 = _m237.SEED == 20260919 and _m237.MAX_DRAW == 30
# path normalisation: git's forward slashes must match local separators
y11 = _m237.norm("Data\\edgar\\item5_02_text\\1\\a.htm") == \
      "Data/edgar/item5_02_text/1/a.htm"
# an empty frozen listing must ABORT rather than call every document v4's
try:
    _m237.frozen_paths(ref="refs/definitely-no-such-ref")
    y12 = False
except SystemExit:
    y12 = True
# the committed draw really is the 450-document pool, not the 5-document one
_drawn = pd.read_csv("outputs/rebuild_v4/237_validation_new_ids.csv")
y13 = len(_drawn) == 30 and _drawn["local_file"].nunique() == 30
y14 = not Path("outputs/rebuild_v4/231_validation_new_ids.csv").exists()
# and 231 no longer draws at all
_t231b = Path("scripts/231_fetch_outcome_data_v4.py").read_text(encoding="utf-8")
y15 = "draw_validation" not in _t231b and "NEW_VALIDATION_SEED" not in _t231b

for _f, _lab in [(y1, "pool = (on disk - v3-frozen) AND in scope"),
                 (y2, "a partial fetch gives the pool for THAT state, not a batch"),
                 (y3, "pool is order-independent"),
                 (y4, "a re-run that fetched nothing still sees the full pool"),
                 (y5, "v3's frozen documents are never in the pool"),
                 (y6, "a v4 document outside b_scope_filings is excluded"),
                 (y7, "draw is capped at 30"),
                 (y8, "draw is deterministic, order-independent"),
                 (y9, "a small pool is drawn whole; an empty pool draws nothing"),
                 (y10, "seed 20260919 and cap 30 are fixed in the script"),
                 (y11, "Windows separators normalise to git's POSIX paths"),
                 (y12, "an unreadable v3-frozen ref ABORTS"),
                 (y13, "the operative draw has 30 distinct documents"),
                 (y14, "the 5-document draw is no longer the operative file"),
                 (y15, "231 no longer draws")]:
    print(f"  {'PASS' if _f else 'FAIL'} | {_lab}")
results.append(all([y1, y2, y3, y4, y5, y6, y7, y8, y9, y10, y11, y12, y13, y14, y15]))


print("\n" + "=" * 70)
print("TEST: 229's LOCO lines belong to the window they are printed under")
print("=" * 70)
import re as _re9
_log229 = Path("outputs/essay3_v4/229_se_diagnostics.log")
_lad = Path("outputs/essay3_v4/f1_ladder.csv")
if not (_log229.exists() and _lad.exists()):
    print("  SKIP | 229 has not been run in this tree")
    results.append(True)
else:
    _FL = pd.read_csv(_lad).set_index("window")["coef"].round(4).to_dict()
    _txt9 = _log229.read_text(encoding="utf-8", errors="replace")
    # walk the log, tracking the most recent "<w>d:" header
    _cur, _seen, _bad = None, {}, []
    for _ln in _txt9.splitlines():
        _h = _re9.match(r"^(\d+)d:", _ln.strip())
        if _h:
            _cur = int(_h.group(1))
            continue
        _m = _re9.search(r"(\d+)d leave-one-cluster-out .*?\(full ([+-][\d.]+)\)", _ln)
        if not _m:
            continue
        _w, _full = int(_m.group(1)), round(float(_m.group(2)), 4)
        _seen[_w] = _full
        # the line's own window prefix must match the header it sits under ...
        if _cur != _w:
            _bad.append("line says %dd but sits under %sd header" % (_w, _cur))
        # ... and the "full" it quotes must be THAT window's coefficient
        if _FL.get(_w) != _full:
            _bad.append("%dd quotes full %+.4f, ladder says %+.4f"
                        % (_w, _full, _FL.get(_w, float("nan"))))
    # No LOCO or top-five line may appear WITHOUT a window prefix. An unprefixed line
    # is exactly what made the original log misreadable: it inherits whatever header it
    # happens to sit under.
    _unpref = [ln.strip() for ln in _txt9.splitlines()
               if ("leave-one-cluster-out" in ln or "top five contributors" in ln)
               and not _re9.search("[0-9]+d (leave-one-cluster-out|top five contributors)", ln)]
    z0 = not _unpref
    z1 = set(_seen) == {30, 90, 180}
    z2 = not _bad
    z3 = all(_seen[w] == _FL[w] for w in _seen)
    # the defect this pins: a LOCO line printed BEFORE its header is attributed to the
    # previous window, which is how "T-Mobile flips at 90d" was reported when it does not.
    _tm90 = _re9.search(r"90d leave-one-cluster-out.*?sign flips 1/\d+: (\d+)", _txt9)
    z4 = bool(_tm90) and _tm90.group(1) != "1283699"
    print(f"  {'PASS' if z0 else 'FAIL'} | no LOCO/top-five line lacks a window prefix"
          + ("" if z0 else f" -> {_unpref[0][:90]}"))
    print(f"  {'PASS' if z1 else 'FAIL'} | a LOCO line is present for all three windows ({sorted(_seen)})")
    print(f"  {'PASS' if z2 else 'FAIL'} | every LOCO line sits under its own window header"
          + ("" if z2 else " -> " + "; ".join(_bad[:3])))
    print(f"  {'PASS' if z3 else 'FAIL'} | each line's 'full' equals that window's ladder coef")
    print(f"  {'PASS' if z4 else 'FAIL'} | the 90d flip is NOT T-Mobile (it is {_tm90.group(1) if _tm90 else '?'})")
    results.append(all([z0, z1, z2, z3, z4]))

print(f"\n{'='*70}")
print(f"RESULT: {sum(results)}/{len(results)} tests passed")
print("=" * 70)
shutil.rmtree(TMP, ignore_errors=True)
sys.exit(0 if all(results) else 1)
