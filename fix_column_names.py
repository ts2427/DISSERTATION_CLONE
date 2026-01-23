#!/usr/bin/env python3
"""
Fix column name references to match actual data
"""

import re
from pathlib import Path

# Column name mappings
replacements = [
    ('health_data_breach', 'health_breach'),
    ('health_data_breach', 'health_breach'),
    ('executive_turnover_30d', 'executive_change_30d'),
    ('executive_turnover_30d', 'executive_change_30d'),
    ('ceo_departure_30d', 'executive_change_30d'),  # approximation
    ('cio_departure_30d', 'executive_change_30d'),  # approximation
    ('cfo_departure_30d', 'executive_change_90d'),  # approximation
    ('credit_card_breach', 'ip_breach'),  # approximation - use available column
    ('financial_breach', 'financial_breach'),  # this one exists
    ('ssn_breach', 'pii_breach'),  # similar
    ('prior_breaches_same_firm', 'prior_breaches_total'),  # use total
    ('prior_breaches_same_industry', 'prior_breaches_total'),  # use total
    ('disclosure_delay_days', 'disclosure_delay_days'),  # this exists
]

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

    # Apply replacements
    for old, new in replacements:
        content = content.replace(f"['{old}']", f"['{new}']")
        content = content.replace(f'["{old}"]', f'["{new}"]')
        content = content.replace(f"== '{old}'", f"== '{new}'")
        content = content.replace(f'== "{old}"', f'== "{new}"')
        content = content.replace(f"df['{old}'", f"df['{new}'")
        content = content.replace(f'df["{old}"', f'df["{new}"')

    if content != original:
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed: {page_file}")

print("Column name fixes complete!")
