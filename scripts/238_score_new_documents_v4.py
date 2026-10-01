"""
REBUILD V4 - STAGE 6: NEW-DOCUMENT CLASSIFIER ACCURACY
=============================================================================
Scores the frozen classifier (scripts/220, byte-identical to v3's scripts/195)
against the v4 reference codes, and reports the result beside v3's round-2
figures.  Offline.

    python scripts/238_score_new_documents_v4.py

WHAT IS SCORED
--------------
PRIMARY   VALIDATION_REFERENCE_CODES_V4_VERIFIED.psv
SECONDARY VALIDATION_REFERENCE_CODES_V4.psv  (the raw blind codes)

Both were committed BEFORE the classifier was ever run on these documents, so
the ordering is in git history rather than in an assertion.

FLAGGED ROWS ARE REPORTED AS BOUNDS, NOT RESOLVED
-------------------------------------------------
Four rows could not be settled from the filing text or from a reachable source
(5, 8, 21, 28).  Rather than pick a value, each field-level metric is also
reported with every flagged row forced to Y and forced to N.  The truth lies
between the two.

pre_announced
-------------
The pool spans the whole fetch window [min(bd, rd) - 730d, max(bd, rd) + 180d],
so most drawn filings sit in the BASELINE window, years before the event's
reported_date, where round-1 rule 1 makes pre_announced Y mechanically.  The
full-pool figure is therefore reported and LABELLED MECHANICAL, and the
substantive figure is restricted to documents whose filing date falls inside the
outcome window (t0, t0 + 180d].

Method is v3's scripts/197, unchanged: agreement, Cohen's kappa, and precision /
recall with exact (Clopper-Pearson) 95% intervals.

Inputs (missing ABORTS):
    outputs/essay3_v4/validation_ids_v4.csv
    outputs/essay3_v4/VALIDATION_REFERENCE_CODES_V4{,_VERIFIED}.psv
    outputs/essay3_q2/d3_r2_agreement.csv        (v3-era comparison; read-only)
Outputs:
    outputs/essay3_v4/238_new_document_agreement.csv
    outputs/essay3_v4/238_new_document_bounds.csv
    outputs/essay3_v4/238_scoring.md
"""
import importlib.util
import sys
from datetime import timedelta
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import cohen_kappa_score
from statsmodels.stats.proportion import proportion_confint

OUT = Path("outputs/essay3_v4")
IDS = OUT / "validation_ids_v4.csv"
BLIND = OUT / "VALIDATION_REFERENCE_CODES_V4.psv"
VERIFIED = OUT / "VALIDATION_REFERENCE_CODES_V4_VERIFIED.psv"
V3 = Path("outputs/essay3_q2/d3_r2_agreement.csv")

# Rows the verification pass could not settle, and the field in question.
FLAGGED = {5: "exec_departure", 8: "exec_departure",
           21: "exec_departure", 28: "director_only_departure"}
OUTCOME_WINDOW_DAYS = 180

L = []


def log(msg=""):
    print(msg, flush=True)
    L.append(str(msg))


def flush():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "238_scoring.md").write_text(chr(10).join(L) + chr(10), encoding="utf-8")


def abort(msg):
    log("")
    log("ABORT: " + str(msg))
    flush()
    sys.exit("ABORT: " + str(msg))


def require(p):
    if not Path(p).exists():
        abort("missing input: " + str(p))
    return Path(p)


def read_psv(p):
    return pd.read_csv(require(p), sep="|", dtype=str).fillna("")


def cp(k, n):
    if n == 0:
        return (None, None, None)
    lo, hi = proportion_confint(k, n, alpha=0.05, method="beta")
    return (round(k / n, 4), round(lo, 4), round(hi, 4))


def score(label, ref, clf, drop_unclear=True):
    """v3 scripts/197 score(), unchanged."""
    x = pd.DataFrame({"r": list(ref), "c": list(clf)})
    if drop_unclear:
        x = x[x["r"] != "unclear"]
    tp = int(((x.r == "Y") & (x.c == "Y")).sum())
    fp = int(((x.r != "Y") & (x.c == "Y")).sum())
    fn = int(((x.r == "Y") & (x.c != "Y")).sum())
    k = (cohen_kappa_score(x.r, x.c)
         if (x.r.nunique() > 1 or x.c.nunique() > 1) else float("nan"))
    p, r = cp(tp, tp + fp), cp(tp, tp + fn)
    return dict(field=label, n=len(x), agreement=round((x.r == x.c).mean(), 4),
                kappa=round(k, 4), ref_positives=int((x.r == "Y").sum()),
                clf_positives=int((x.c == "Y").sum()), tp=tp, fp=fp, fn=fn,
                precision=p[0],
                precision_ci95=(("[%s, %s]" % (p[1], p[2])) if p[0] is not None
                                else "n/a (no clf positives)"),
                recall=r[0],
                recall_ci95=(("[%s, %s]" % (r[1], r[2])) if r[0] is not None
                             else "n/a (no ref positives)"))


def classifier_answers(ids):
    spec = importlib.util.spec_from_file_location(
        "clf_v4", "scripts/220_essay3_v4_classifier_v2.py")
    clf = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(clf)
    rows = []
    for _, r in ids.iterrows():
        fp = Path(str(r["local_file"]))
        if not fp.exists():
            abort("missing document: " + str(fp))
        t = clf.to_text(fp.read_bytes())
        raw = clf.section_502(t)
        sec = clf.strip_caption(raw if raw else t[:20000])
        codes, persons, refs = clf.classify(sec)
        deps = [p for p in persons if p["action"] == "departure"]
        ref_rd = pd.Timestamp(str(r["reference_date_for_pre_announced"])[:10])
        rows.append(dict(
            sheet_id=int(r["sheet_id"]), accession=r["accession"],
            filing_date=str(r["filing_date"])[:10],
            reference_date=ref_rd.date().isoformat(),
            clf_exec_departure="Y" if codes["exec_departure"] else "N",
            clf_exec_departure_new="Y" if codes["exec_departure_new"] else "N",
            clf_ceo_departure="Y" if codes["ceo_departure"] else "N",
            clf_ceo_departure_new="Y" if codes["ceo_departure_new"] else "N",
            clf_director_only_departure="Y" if codes["director_departure"] else "N",
            clf_pre_announced=(clf.pre_announced(codes, refs, ref_rd) if deps else "N"),
            clf_action=codes["action"]))
    return pd.DataFrame(rows)


def restated_to_N(df):
    """v3's 'B' variant: a restated departure is not a NEW departure."""
    B = df.copy()
    m = B["restates_prior_disclosure"] == "Y"
    for f in ("exec_departure", "ceo_departure", "director_only_departure"):
        B.loc[m, f] = "N"
    return B


def main():
    ids = pd.read_csv(require(IDS), dtype=str)
    ver = read_psv(VERIFIED)
    bli = read_psv(BLIND)
    C = classifier_answers(ids)
    C["sheet_id"] = C["sheet_id"].astype(int)
    for D in (ver, bli):
        D["sheet_id"] = D["sheet_id"].astype(int)

    P = ver.merge(C, on="sheet_id").sort_values("sheet_id")
    S = bli.merge(C, on="sheet_id").sort_values("sheet_id")
    if len(P) != 30 or len(S) != 30:
        abort("expected 30 scored rows, got %d / %d" % (len(P), len(S)))

    log("# REBUILD V4 - new-document classifier accuracy (scripts/238)")
    log("")
    log("PRIMARY = verified reference codes; SECONDARY = raw blind codes.")
    log("Both were committed before the classifier was run on these documents.")
    log("")

    rows = []
    for tag, D in (("PRIMARY (verified)", P), ("SECONDARY (blind)", S)):
        B = restated_to_N(D)
        rows += [
            score(tag + " | exec departure (A: any)",
                  D["exec_departure"], D["clf_exec_departure"]),
            score(tag + " | exec departure (B: new only)",
                  B["exec_departure"], D["clf_exec_departure_new"]),
            score(tag + " | CEO departure (A: any)",
                  D["ceo_departure"], D["clf_ceo_departure"]),
            score(tag + " | CEO departure (B: new only)",
                  B["ceo_departure"], D["clf_ceo_departure_new"]),
            score(tag + " | director-only departure",
                  D["director_only_departure"], D["clf_director_only_departure"]),
            score(tag + " | pre-announced (FULL POOL - MECHANICAL)",
                  D["pre_announced"], D["clf_pre_announced"], False),
        ]
        w = D[(pd.to_datetime(D["filing_date_y"] if "filing_date_y" in D.columns
                              else D["filing_date"]) > pd.to_datetime(D["reference_date"]))
              & (pd.to_datetime(D["filing_date_y"] if "filing_date_y" in D.columns
                                else D["filing_date"])
                 <= pd.to_datetime(D["reference_date"])
                 + timedelta(days=OUTCOME_WINDOW_DAYS))]
        rows.append(score(tag + " | pre-announced (OUTCOME WINDOW ONLY)",
                          w["pre_announced"], w["clf_pre_announced"], False))
    A = pd.DataFrame(rows)
    A.to_csv(OUT / "238_new_document_agreement.csv", index=False)
    log("## Agreement")
    log(A.to_string(index=False))

    # ---- bounds over the still-flagged rows ----
    brows = []
    for forced in ("Y", "N"):
        D = P.copy()
        for sid, field in FLAGGED.items():
            D.loc[D["sheet_id"] == sid, field] = forced
        B = restated_to_N(D)
        brows += [
            score("flagged forced %s | exec departure (A: any)" % forced,
                  D["exec_departure"], D["clf_exec_departure"]),
            score("flagged forced %s | exec departure (B: new only)" % forced,
                  B["exec_departure"], D["clf_exec_departure_new"]),
            score("flagged forced %s | director-only departure" % forced,
                  D["director_only_departure"], D["clf_director_only_departure"]),
        ]
    BD = pd.DataFrame(brows)
    BD.to_csv(OUT / "238_new_document_bounds.csv", index=False)
    log("")
    log("## Bounds - every flagged row (5, 8, 21, 28) forced Y, then forced N")
    log(BD.to_string(index=False))

    # ---- v3-era comparison ----
    if V3.exists():
        v3 = pd.read_csv(V3)
        log("")
        log("## v3-era round 2, for comparison (outputs/essay3_q2/d3_r2_agreement.csv)")
        log(v3.to_string(index=False))
    else:
        log("")
        log("NOTE: " + str(V3) + " absent; no v3-era comparison printed.")

    log("")
    log("## Reading these numbers")
    log("The classifier is FROZEN: scripts/220 is byte-identical to v3's scripts/195.")
    log("No result here may retune it. n is 30 documents, so every interval is wide;")
    log("the exact intervals are reported rather than point estimates alone.")
    log("")
    log("written 238_new_document_agreement.csv, 238_new_document_bounds.csv")
    flush()


if __name__ == "__main__":
    main()
