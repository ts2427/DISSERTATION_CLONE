"""
RETIRED AND QUARANTINED (2026-08-30) — DO NOT USE.

This script generated Dissertation_Regression_Formulas.docx, a documentation
artifact that carried four factual errors the pipeline never implemented:
  1. "FCC Rule 37.3" — no such rule exists (the rule is 47 CFR 64.2011).
  2. SIC-code treatment (4813, 4841, 4899) — treatment is Form 499
     registration status, never SIC.
  3. "January 1, 2007" effective date — the rule's effective date is
     December 8, 2007 (2007 CPNI Order; FR publication June 8, 2007,
     72 FR 31948 — publication only).
  4. Volatility windows [-25,-5]/[+5,+25] — described but NEVER computed by
     any analysis script; the old code used breach-anchored calendar
     [-40,-1]/[0,+30] annualized SD (script 20). See
     scripts/163_essay2_rerun_form499.py, which implements and tests both.

No script imports this module and run_all.py never called it; its only output
was an untracked root-level docx. The original source is preserved in git
history (see the commit that introduced this stub).
"""

raise RuntimeError(
    'create_regression_formulas_document.py is RETIRED: it documented a '
    'specification ("Rule 37.3", SIC treatment, Jan 1 2007, [-25,-5]/[+5,+25] '
    'windows) that the pipeline never implemented. See the module docstring '
    'and scripts/163_essay2_rerun_form499.py.'
)
