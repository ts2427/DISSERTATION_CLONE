"""
ESSAY 3 — QUERY 4, PARTS B AND C: READOUTS OF THE FROZEN SPECIFICATION
=============================================================================
    python scripts/243_essay3_q4_readouts.py

NEW readouts. These refit the FROZEN primary specification and print quantities the
freeze already produced but never wrote to disk: the control coefficients (Part B) and
the logit's convergence diagnostics (Part C). No specification choice is made here.

HOW THE SPECIFICATION IS GUARANTEED IDENTICAL, rather than asserted to be:
  * TREAT, BASE, CTRL and d0 are LIFTED from scripts/227's own source by AST, exactly
    as scripts/241 does. They are not retyped.
  * The design matrix and the CV3 jackknife are rebuilt with the same statements
    scripts/227:90-117 uses. The ONLY difference is that the full diagonal of the
    jackknife covariance is read, where 227 reads the single cell [ti, ti].
  * Part B then ASSERTS the treatment coefficient and its CV3 SE reproduce
    f1_ladder.csv to FULL STORED PRECISION (4 dp). If they differ at all it aborts.
    A passing assertion is the proof the design is the frozen one.
  * Part C ASSERTS the AMEs and SEs reproduce f1_logit_ame.csv, then prints the
    warning and convergence text scripts/227 discards.

No bootstrap, no HC3, no CV1 on the controls - CV3 only, by instruction.
The control family is DESCRIPTIVE: not a hypothesis test, not in the BH count of 31.

Writes ONLY under outputs/essay3_q4/:
    b_control_coefficients.csv  c_logit_diagnostics.csv  243_readouts.log
"""
import ast
import io
import sys
import warnings
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

V4 = Path("outputs/essay3_v4")
OUT = Path("outputs/essay3_q4")
OUT.mkdir(parents=True, exist_ok=True)
SRC227 = Path("scripts/227_essay3_v4_estimation.py")
L = []


def log(m=""):
    print(m, flush=True)
    L.append(str(m))


def hdr(t):
    log("")
    log("=" * 100)
    log(t)
    log("=" * 100)


def abort(msg):
    log("")
    log("ABORT: " + str(msg))
    (OUT / "243_readouts.log").write_text("\n".join(L) + "\n", encoding="utf-8")
    sys.exit("ABORT: " + str(msg))


# ------------------------------------------------------------------ lift from 227
def borrow():
    if not SRC227.exists():
        abort("missing " + str(SRC227))
    src = SRC227.read_text(encoding="utf-8")
    tree = ast.parse(src)
    want = {"TREAT", "BASE", "CTRL", "d0", "OUT"}
    pieces = []
    for node in tree.body:
        if isinstance(node, ast.Assign):
            names = {t.id for t in node.targets if isinstance(t, ast.Name)}
            if names & want:
                pieces.append(ast.get_source_segment(src, node))
    ns = {"np": np, "pd": pd, "sm": sm, "stats": stats, "Path": Path}
    exec("\n".join(pieces), ns)
    missing = want - set(ns)
    if missing:
        abort("could not lift from scripts/227: " + ", ".join(sorted(missing)))
    return ns


ns = borrow()
TREAT, BASE, CTRL, d0 = ns["TREAT"], ns["BASE"], ns["CTRL"], ns["d0"]
log("lifted from scripts/227 by AST: TREAT=%r" % TREAT)
log("  BASE     = %r" % (BASE,))
log("  CTRL[rd] = %r" % (CTRL["rd"],))
log("  d0: %d rows (in_analysis_sample == 1)" % len(d0))

F1 = pd.read_csv(V4 / "f1_ladder.csv")
AME = pd.read_csv(V4 / "f1_logit_ame.csv")


# ------------------------------------------------------------------ PART B
def design(d, ycol, xcols):
    """The same construction as scripts/227:90-96."""
    d = d.dropna(subset=[ycol] + xcols).reset_index(drop=True)
    Xdf = d[xcols].astype(float)
    Xdf = sm.add_constant(Xdf, has_constant="add")
    return d, Xdf


hdr("PART B — control coefficients, CV3 only (NEW readout; DESCRIPTIVE, not tests)")
rowsB = []
for w in (30, 90, 180):
    ycol = "exec_departure_%d_rd" % w
    xcols = [TREAT] + CTRL["rd"]
    d, Xdf = design(d0, ycol, xcols)
    X, Y = Xdf.to_numpy(), d[ycol].astype(float).to_numpy()
    cols = list(Xdf.columns)
    ti = cols.index(TREAT)
    G_ids, G_inv = np.unique(d["final_cik"].to_numpy(), return_inverse=True)
    G = len(G_ids)
    n, k = X.shape
    XtX_inv = np.linalg.pinv(X.T @ X)
    beta = XtX_inv @ (X.T @ Y)
    # CV3 jackknife, scripts/227:113-117, full covariance rather than one cell
    betas_del = np.zeros((G, k))
    for g in range(G):
        m = G_inv != g
        betas_del[g] = np.linalg.lstsq(X[m], Y[m], rcond=None)[0]
    bbar = betas_del.mean(0)
    Vcv3 = (G - 1) / G * (betas_del - bbar).T @ (betas_del - bbar)
    se = np.sqrt(np.diag(Vcv3))
    df = G - 1
    tcrit = stats.t.ppf(0.975, df)

    # ---- ASSERTION against the committed ladder, full stored precision ----
    ref = F1[F1["window"] == w].iloc[0]
    got_b, got_se = round(float(beta[ti]), 4), round(float(se[ti]), 4)
    log("")
    log("--- %dd | n=%d G=%d k=%d df=%d ---" % (w, n, G, k, df))
    log("ASSERTION vs f1_ladder.csv: coef %.4f vs %.4f | se_cv3 %.4f vs %.4f"
        % (got_b, ref["coef"], got_se, ref["se_cv3"]))
    if got_b != round(float(ref["coef"]), 4) or got_se != round(float(ref["se_cv3"]), 4):
        abort("PART B STOPPED - refit does not reproduce f1_ladder.csv at %dd: "
              "coef %.6f vs %.6f, se_cv3 %.6f vs %.6f"
              % (w, got_b, ref["coef"], got_se, ref["se_cv3"]))
    log("  ASSERTION PASSES - the design is the frozen one.")
    log("")
    log("  %-28s %10s %10s %8s %9s %22s" % ("term", "coef", "se_cv3", "t", "p", "95% CI (CV3)"))
    for i, c in enumerate(cols):
        t_ = beta[i] / se[i] if se[i] > 0 else np.nan
        p_ = 2 * (1 - stats.t.cdf(abs(t_), df)) if np.isfinite(t_) else np.nan
        lo, hi = beta[i] - tcrit * se[i], beta[i] + tcrit * se[i]
        star = "  <-- p < .05" if (np.isfinite(p_) and p_ < .05) else ""
        label = c if c != "const" else "(intercept)"
        log("  %-28s %+10.5f %10.5f %+8.3f %9.4f  [%+8.4f, %+8.4f]%s"
            % (label, beta[i], se[i], t_, p_, lo, hi, star))
        rowsB.append(dict(window=w, term=label, is_treatment=(c == TREAT),
                          coef=round(float(beta[i]), 6), se_cv3=round(float(se[i]), 6),
                          t=round(float(t_), 4), p_cv3=round(float(p_), 4),
                          ci_lo=round(float(lo), 6), ci_hi=round(float(hi), 6),
                          df=df, G=G, n=n,
                          family="DESCRIPTIVE: not a hypothesis test, not in the BH count"))

B = pd.DataFrame(rowsB)
B.to_csv(OUT / "b_control_coefficients.csv", index=False)
sig = B[(B["p_cv3"] < .05) & (~B["is_treatment"]) & (B["term"] != "(intercept)")]
log("")
log("Controls with CV3 p < .05: %d" % len(sig))
if len(sig):
    log(sig[["window", "term", "coef", "se_cv3", "p_cv3"]].to_string(index=False))
log("These are DESCRIPTIVE. They are not hypothesis tests, are not pre-specified, and are")
log("NOT added to the 31-test BH ledger.")

# ------------------------------------------------------------------ PART C
hdr("PART C — logit convergence and warnings (NEW readout)")
rowsC = []
for w in (30, 90, 180):
    dd = d0.dropna(subset=CTRL["rd"])
    Xl = sm.add_constant(dd[[TREAT] + CTRL["rd"]].astype(float))
    yl = dd["exec_departure_%d_rd" % w].astype(int)
    buf = io.StringIO()
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        with redirect_stdout(buf), redirect_stderr(buf):
            lg = sm.Logit(yl, Xl).fit(cov_type="cluster",
                                      cov_kwds={"groups": dd["final_cik"]})
        mf = lg.get_margeff(at="overall", dummy=True).summary_frame().loc[TREAT]
    ref = AME[AME["window"] == w].iloc[0]
    got_a, got_s = round(float(mf["dy/dx"]), 4), round(float(mf["Std. Err."]), 4)
    log("")
    log("--- %dd ---" % w)
    log("ASSERTION vs f1_logit_ame.csv: AME %.4f vs %.4f | SE %.4f vs %.4f"
        % (got_a, ref["ame"], got_s, ref["se_cluster"]))
    if got_a != round(float(ref["ame"]), 4) or got_s != round(float(ref["se_cluster"]), 4):
        abort("PART C STOPPED - logit refit does not reproduce f1_logit_ame.csv at %dd" % w)
    log("  ASSERTION PASSES.")
    fitted = lg.predict()
    conv = getattr(lg.mle_retvals, "get", lambda *_: None)("converged") \
        if isinstance(lg.mle_retvals, dict) else None
    if isinstance(lg.mle_retvals, dict):
        conv = lg.mle_retvals.get("converged")
        iters = lg.mle_retvals.get("iterations")
    else:
        conv, iters = None, None
    log("  converged            : %s" % conv)
    log("  iterations           : %s" % iters)
    log("  n observations used  : %d of %d (dropped %d)" % (int(lg.nobs), len(dd), len(dd) - int(lg.nobs)))
    log("  max fitted probability: %.6f   min: %.6f" % (fitted.max(), fitted.min()))
    log("  fitted probs within (0,1) - no perfect separation by that test: %s"
        % bool(fitted.max() < 1 - 1e-8 and fitted.min() > 1e-8))
    cap = buf.getvalue().strip()
    log("  solver stdout/stderr : %s" % (repr(cap) if cap else "(empty)"))
    if caught:
        for ww in caught:
            log("  WARNING (verbatim)   : %s: %s" % (ww.category.__name__, str(ww.message)))
    else:
        log("  WARNINGS             : none raised")
    rowsC.append(dict(window=w, ame=got_a, se_cluster=got_s,
                      converged=conv, iterations=iters, nobs=int(lg.nobs),
                      n_supplied=len(dd), dropped=len(dd) - int(lg.nobs),
                      max_fitted_p=round(float(fitted.max()), 6),
                      min_fitted_p=round(float(fitted.min()), 6),
                      separation_flag=bool(fitted.max() >= 1 - 1e-8 or fitted.min() <= 1e-8),
                      n_warnings=len(caught),
                      warnings_verbatim=" | ".join("%s: %s" % (x.category.__name__, x.message) for x in caught),
                      solver_output=cap))
pd.DataFrame(rowsC).to_csv(OUT / "c_logit_diagnostics.csv", index=False)

(OUT / "243_readouts.log").write_text("\n".join(L) + "\n", encoding="utf-8")
print("\nwritten b_control_coefficients.csv, c_logit_diagnostics.csv, 243_readouts.log")
