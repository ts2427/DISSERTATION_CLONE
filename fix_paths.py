#!/usr/bin/env python3
"""
Fix all relative data paths in dashboard pages to use absolute paths.
This ensures Streamlit can find data files regardless of working directory.
"""

import os
import re
from pathlib import Path

# Get root directory
root_dir = Path(__file__).parent

# Files to fix
page_files = [
    'Dashboard/pages/2_Sample_Validation.py',
    'Dashboard/pages/3_Data_Landscape.py',
    'Dashboard/pages/4_Essay3_Volatility.py',
    'Dashboard/pages/5_Essay2_MarketReactions.py',
    'Dashboard/pages/6_Key_Finding.py',
    'Dashboard/pages/8_Moderators.py',
    'Dashboard/pages/9_Raw_Data_Explorer.py',
]

for file_path in page_files:
    full_path = root_dir / file_path
    if not full_path.exists():
        print(f"⚠ File not found: {full_path}")
        continue

    with open(full_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content

    # Fix Data/processed paths
    content = re.sub(
        r"pd\.read_csv\('Data/processed/",
        "pd.read_csv(str(Path(__file__).parent.parent / 'Data' / 'processed' / ",
        content
    )
    content = re.sub(
        r"pd\.read_csv\(\"Data/processed/",
        "pd.read_csv(str(Path(__file__).parent.parent / 'Data' / 'processed' / ",
        content
    )

    # Fix outputs paths
    content = re.sub(
        r"pd\.read_csv\('outputs/",
        "pd.read_csv(str(Path(__file__).parent.parent / 'outputs' / ",
        content
    )
    content = re.sub(
        r"pd\.read_csv\(\"outputs/",
        "pd.read_csv(str(Path(__file__).parent.parent / 'outputs' / ",
        content
    )

    # Fix json file paths
    content = re.sub(
        r"open\('outputs/",
        "open(str(Path(__file__).parent.parent / 'outputs' / ",
        content
    )
    content = re.sub(
        r"open\(\"outputs/",
        "open(str(Path(__file__).parent.parent / 'outputs' / ",
        content
    )

    # Add Path import if needed
    if 'from pathlib import Path' not in content and ('Path(__file__)' in content or content != original_content):
        # Find the imports section and add Path import
        import_match = re.search(r'(import streamlit as st\n)', content)
        if import_match:
            content = content[:import_match.end()] + 'from pathlib import Path\n' + content[import_match.end():]

    if content != original_content:
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"[OK] Fixed: {file_path}")
    else:
        print(f"[--] No changes needed: {file_path}")

print("\nAll paths fixed!")
