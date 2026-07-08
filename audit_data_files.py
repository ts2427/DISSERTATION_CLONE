import os
import re
from pathlib import Path

scripts_dir = Path("scripts")
audit_results = []

for script_file in sorted(scripts_dir.glob("*.py")):
    with open(script_file, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Try to find data loading patterns
    data_file = None
    
    # Pattern 1: Direct pd.read_csv('path...')
    match = re.search(r"pd\.read_csv\(['\"]([^'\"]+\.csv)['\"]", content)
    if match:
        data_file = match.group(1)
    
    # Pattern 2: Direct pd.read_excel('path...')
    if not data_file:
        match = re.search(r"pd\.read_excel\(['\"]([^'\"]+\.xlsx?)['\"]", content)
        if match:
            data_file = match.group(1)
    
    # Pattern 3: DATA_FILE variable
    if not data_file:
        match = re.search(r"DATA_FILE\s*=\s*['\"]([^'\"]+\.csv)['\"]", content)
        if match:
            data_file = match.group(1)
    
    # Pattern 4: data_path variable
    if not data_file:
        match = re.search(r"data_path\s*=\s*['\"]([^'\"]+\.csv)['\"]", content)
        if match:
            data_file = match.group(1)
    
    if data_file:
        audit_results.append((script_file.name, data_file))

print("=" * 100)
print(f"AUDIT: Data File Loading Paths")
print("=" * 100)
print(f"\nTotal scripts with data loading: {len(audit_results)}\n")

# Categorize by data file
by_file = {}
for script, datafile in audit_results:
    if datafile not in by_file:
        by_file[datafile] = []
    by_file[datafile].append(script)

# Sort by frequency
sorted_files = sorted(by_file.items(), key=lambda x: len(x[1]), reverse=True)

for datafile, scripts in sorted_files:
    status = "OK" if "DEDUPLICATED_ENRICHED" in datafile else "FIX"
    print(f"\n[{status}] {datafile} ({len(scripts)} scripts)")
    for script in sorted(scripts):
        print(f"     • {script}")

# Summary stats
print("\n" + "=" * 100)
print("SUMMARY")
print("=" * 100)
total = len(audit_results)
correct = len([s for s, d in audit_results if "DEDUPLICATED_ENRICHED" in d])
print(f"Total analysis scripts: {total}")
print(f"Loading DEDUPLICATED_ENRICHED: {correct}")
print(f"Need fixes: {total - correct}")

