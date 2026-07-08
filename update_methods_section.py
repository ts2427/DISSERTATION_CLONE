#!/usr/bin/env python3
"""
Update Methods Section Paragraph 15 in Dissertation Proposal
Removes references to window length testing and absolute returns
"""

from docx import Document
import re

# Load the dissertation proposal
doc = Document('Dissertation_Proposal_Complete.docx')

changes_made = 0

# Iterate through paragraphs to find and replace text
for para in doc.paragraphs:
    text = para.text

    # Fix 1: Update opening sentence about robustness checks
    if "The robustness checks test whether the result holds across alternative window choices" in text:
        new_text = text.replace(
            "The robustness checks test whether the result holds across alternative window choices, volatility measures, standard-error specifications, and fixed-effects specifications.",
            "The robustness checks test whether the result holds across alternative volatility measures, standard-error specifications, and fixed-effects specifications."
        )
        para.text = new_text
        print(f"[✓] Fixed opening sentence about robustness checks")
        changes_made += 1

    # Fix 2: Remove window-lengths sentence
    if "Window lengths are tested at ten, thirty, and sixty trading days on each side of the event." in text:
        new_text = text.replace(
            "Window lengths are tested at ten, thirty, and sixty trading days on each side of the event. ",
            ""
        )
        para.text = new_text
        print(f"[✓] Removed window-lengths testing sentence")
        changes_made += 1

    # Fix 3: Update volatility-measures sentence
    if "Volatility is also measured using daily absolute returns and a GARCH" in text:
        new_text = text.replace(
            "Volatility is also measured using daily absolute returns and a GARCH(1,1) conditional-volatility specification.",
            "Volatility is also measured using a GARCH(1,1) conditional-volatility specification."
        )
        para.text = new_text
        print(f"[✓] Removed 'daily absolute returns' from volatility-measures sentence")
        changes_made += 1

# Save the updated document
doc.save('Dissertation_Proposal_Complete.docx')

print("\n" + "="*80)
print(f"Methods section updated: {changes_made} changes applied")
print("="*80)
if changes_made == 3:
    print("✓ All three edits completed successfully")
else:
    print(f"⚠ Only {changes_made}/3 edits found and applied")
    print("  Check that the dissertation proposal contains the expected text")
