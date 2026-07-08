import os
import re
from pathlib import Path

# Category definitions
ENRICHMENT_SCRIPTS = [41, 42, 43, 44, 45, 46, 47, 48, 49, 53, 3, 4, 5, 6, 9, 12, 13, 15, 20, 24, 30, 31, 32, 40, 54]
DATA_PREP_SCRIPTS = [0, 1, 2, 99]  # Prefix numbers
ANALYSIS_SCRIPTS = [60, 61, 70, 80, 81, 82, 83, 84, 86, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106]

scripts_dir = Path("scripts")
audit = {}

for script_file in sorted(scripts_dir.glob("*.py")):
    # Get prefix number
    prefix = re.match(r'(\d+)', script_file.name)
    if not prefix:
        category = "utility"
        continue
    
    prefix_num = int(prefix.group(1))
    
    with open(script_file, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Find current data file
    data_file = None
    match = re.search(r"pd\.read_csv\(['\"]([^'\"]+\.csv)['\"]", content)
    if match:
        data_file = match.group(1)
    if not data_file:
        match = re.search(r"pd\.read_excel\(['\"]([^'\"]+\.xlsx?)['\"]", content)
        if match:
            data_file = match.group(1)
    if not data_file:
        match = re.search(r"DATA_FILE\s*=\s*['\"]([^'\"]+)['\"]", content)
        if match:
            data_file = match.group(1)
    
    if data_file:
        category = "unknown"
        if prefix_num in [41, 42, 43, 44, 45, 46, 47, 48, 49, 53]:
            category = "enrichment"
        elif prefix_num in [0, 1, 2, 3, 4, 5, 6, 9, 12, 13, 15, 20, 24, 30, 31, 32, 40, 54]:
            category = "data_prep"
        elif prefix_num >= 60:
            category = "analysis"
        
        status = "OK" if "DEDUPLICATED_ENRICHED" in data_file and category == "analysis" else (
            "OK" if category != "analysis" else "FIX"
        )
        
        audit[script_file.name] = {
            'category': category,
            'data_file': data_file,
            'status': status
        }

# Print by category
print("=" * 100)
print("SCRIPT CATEGORIZATION & AUDIT")
print("=" * 100)

categories = {}
for script, info in audit.items():
    cat = info['category']
    if cat not in categories:
        categories[cat] = []
    categories[cat].append(script)

for cat_name in ['analysis', 'enrichment', 'data_prep', 'unknown']:
    if cat_name in categories:
        print(f"\n{cat_name.upper()} SCRIPTS ({len(categories[cat_name])})")
        print("-" * 100)
        for script in sorted(categories[cat_name]):
            info = audit[script]
            status = info['status']
            datafile = info['data_file'].split('/')[-1]
            print(f"  [{status}] {script:40s} -> {datafile}")

# Summary
print("\n" + "=" * 100)
print("ANALYSIS SCRIPTS THAT NEED FIXING")
print("=" * 100)
needs_fix = [s for s, info in audit.items() if info['status'] == 'FIX']
if needs_fix:
    print(f"\nFound {len(needs_fix)} analysis scripts that need fixes:")
    for script in sorted(needs_fix):
        print(f"  • {script}")
else:
    print("\nAll analysis scripts are correctly configured!")

