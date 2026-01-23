#!/usr/bin/env python3
"""
Add dark text color to all light background boxes in all pages
"""

import re
from pathlib import Path

pages_to_fix = [
    'Dashboard/pages/4_Essay3_Volatility.py',
    'Dashboard/pages/6_Key_Finding.py',
    'Dashboard/pages/7_Conclusion.py',
]

root_dir = Path(__file__).parent

for page_file in pages_to_fix:
    full_path = root_dir / page_file
    if not full_path.exists():
        print(f"Not found: {page_file}")
        continue

    with open(full_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content

    # Add color: #333; to inline background-color styles for light colors
    content = re.sub(
        r"style='background-color: #e6f2ff;",
        "style='background-color: #e6f2ff; color: #333;",
        content
    )
    content = re.sub(
        r"style='background-color: #ffe6e6;",
        "style='background-color: #ffe6e6; color: #333;",
        content
    )
    content = re.sub(
        r"style='background-color: #fff4e6;",
        "style='background-color: #fff4e6; color: #333;",
        content
    )
    content = re.sub(
        r"style='background-color: #e6ffe6;",
        "style='background-color: #e6ffe6; color: #333;",
        content
    )
    content = re.sub(
        r"style='background-color: #f0f0f0;",
        "style='background-color: #f0f0f0; color: #333;",
        content
    )
    content = re.sub(
        r"style='background-color: #f5f5f5;",
        "style='background-color: #f5f5f5; color: #333;",
        content
    )

    # Add inline h3 color styling when in light boxes
    content = re.sub(
        r"<h3>(\w+)",
        r"<h3 style='color: inherit;'>\1",
        content
    )

    if content != original:
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"[OK] {page_file}")
    else:
        print(f"[--] {page_file}")

print("Text color fixes complete!")
