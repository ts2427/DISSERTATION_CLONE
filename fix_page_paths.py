#!/usr/bin/env python3
"""
Fix data paths in all page files - need 3 levels up, not 2
Page location: Dashboard/pages/X_Page.py
Root location: (3 levels up)
"""

import os
import re
from pathlib import Path

root_dir = Path(__file__).parent

# All page files
page_files = [
    'Dashboard/pages/0_Research_Story.py',
    'Dashboard/pages/1_Natural_Experiment.py',
    'Dashboard/pages/2_Sample_Validation.py',
    'Dashboard/pages/3_Data_Landscape.py',
    'Dashboard/pages/4_Essay3_Volatility.py',
    'Dashboard/pages/5_Essay2_MarketReactions.py',
    'Dashboard/pages/6_Key_Finding.py',
    'Dashboard/pages/7_Conclusion.py',
    'Dashboard/pages/8_Moderators.py',
    'Dashboard/pages/9_Raw_Data_Explorer.py',
    'Dashboard/pages/10_Data_Dictionary.py',
]

for file_path in page_files:
    full_path = root_dir / file_path
    if not full_path.exists():
        print(f"Not found: {file_path}")
        continue

    with open(full_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content

    # Replace .parent.parent with .parent.parent.parent for pages
    # This fixes the path from pages/ to root
    content = content.replace(
        "Path(__file__).parent.parent / 'Data'",
        "Path(__file__).parent.parent.parent / 'Data'"
    )
    content = content.replace(
        "Path(__file__).parent.parent / 'outputs'",
        "Path(__file__).parent.parent.parent / 'outputs'"
    )

    if content != original:
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"[OK] {file_path}")
    else:
        print(f"[--] {file_path}")

print("Done!")
