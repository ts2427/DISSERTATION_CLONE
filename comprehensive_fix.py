#!/usr/bin/env python3
"""
Comprehensive fix for all column names and styling issues
"""

import re
from pathlib import Path

# Comprehensive column name mapping
column_mappings = {
    "['company_name']": "['org_name']",
    '["company_name"]': '["org_name"]',
    "df['company_name']": "df['org_name']",
    'df["company_name"]': 'df["org_name"]',
    "'company_name'": "'org_name'",
    '"company_name"': '"org_name"',

    "['sector_main']": "['organization_type']",
    '["sector_main"]': '["organization_type"]',
    "df['sector_main']": "df['organization_type']",
    'df["sector_main"]': 'df["organization_type"]',
    "'sector_main'": "'organization_type'",
    '"sector_main"': '"organization_type"',

    "['return_volatility_change']": "['volatility_change']",
    '["return_volatility_change"]': '["volatility_change"]',
    "df['return_volatility_change']": "df['volatility_change']",
    'df["return_volatility_change"]': 'df["volatility_change"]',
    "'return_volatility_change'": "'volatility_change'",
    '"return_volatility_change"': '"volatility_change"',

    "['return_volatility_pre']": "['return_volatility_pre']",  # keep same
    "['return_volatility_post']": "['return_volatility_post']",  # keep same

    "'car_5d'": "'car_5d'",  # keep same
    "'car_30d'": "'car_30d'",  # keep same

    "['industry']": "['organization_type']",
    '["industry"]': '["organization_type"]',
}

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

root_dir = Path(__file__).parent

for page_file in page_files:
    full_path = root_dir / page_file
    if not full_path.exists():
        continue

    with open(full_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content

    # Apply all column mappings
    for old, new in column_mappings.items():
        content = content.replace(old, new)

    # Add color: #333; to ALL inline style background-color boxes
    # Match all style attributes with background-color
    content = re.sub(
        r"style='([^']*background-color:\s*#[a-f0-9]{6})([^']*)'",
        r"style='\1; color: #333\2'",
        content
    )

    if content != original:
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"[OK] {page_file}")
    else:
        print(f"[--] {page_file}")

print("Comprehensive fix complete!")
