"""
Update Dashboard pages with corrected H1 values
Smart replacement to avoid false positives (e.g., enforcement rate)
"""

import os
import re
from pathlib import Path

dashboard_dir = r'C:\Users\mcobp\DISSERTATION_CLONE\Dashboard\pages'

# Files to update (those with H1 coefficient values)
files_to_update = [
    '0_Research_Story.py',
    '4_Essay1_MarketReactions.py',
    '8_Key_Findings.py',
    '9_Conclusion.py',
]

# Patterns to replace (more specific to avoid false positives)
patterns = [
    # H1 coefficient patterns
    (r'Timing effect = \+0\.57%', 'Timing effect = +0.649%'),
    (r'Immediate disclosure coefficient = \+0\.57%', 'Immediate disclosure coefficient = +0.649%'),
    (r'Timing coefficient = \+0\.57%', 'Timing coefficient = +0.649%'),
    (r"'\+0\.57% \(robustly null\)'", "'+0.649% (robustly null)'"),
    (r"'timing is irrelevant to market reactions'\)", "'timing is irrelevant to market reactions')"),

    # P-value patterns
    (r'\(p = 0\.539\)', '(p = 0.443)'),
    (r'p = 0\.539', 'p = 0.443'),
    (r'\(p=0\.539\)', '(p=0.443)'),
]

total_changes = 0

for filename in files_to_update:
    filepath = os.path.join(dashboard_dir, filename)

    if not os.path.exists(filepath):
        print(f"[SKIP] {filename} (file not found)")
        continue

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content

        # Apply regex replacements
        for pattern, replacement in patterns:
            content = re.sub(pattern, replacement, content)

        # Count changes
        if content != original_content:
            changes = sum(1 for old, new in zip(original_content.split('\n'), content.split('\n')) if old != new)

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)

            print(f"[OK] {filename}: updated")
            total_changes += 1
        else:
            print(f"[OK] {filename}: no changes needed")

    except Exception as e:
        print(f"[ERROR] {filename}: {str(e)[:50]}")

print()
print("=" * 80)
print(f"Dashboard Update Complete: {total_changes} files modified")
print("=" * 80)
