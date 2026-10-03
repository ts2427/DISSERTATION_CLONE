"""
Prepare batch of unresolved validation records for reasoning pass
"""

import pandas as pd
from pathlib import Path
import json

print("=" * 100)
print("PREPARE REASONING PASS BATCH")
print("=" * 100)

# Load combined results (exact + subsidiary matches)
combined_path = Path("outputs/exact_and_subsidiary_matches.csv")
df_combined = pd.read_csv(combined_path)

# Load original validation set to identify unresolved
validation_path = Path("Data/validation_set_40_records.csv")
df_validation = pd.read_csv(validation_path)

# Identify unresolved records
resolved_org_names = set(df_combined['org_name'].unique())
unresolved = df_validation[~df_validation['org_name'].isin(resolved_org_names)].copy()

print(f"\nUnresolved records for reasoning pass: {len(unresolved)}")
print()

# Prepare reasoning batch
reasoning_batch = []

for idx, row in unresolved.iterrows():
    reasoning_batch.append({
        'index': idx,
        'org_name': row['org_name'],
        'ticker': row['ticker'],
        'breach_date': row['breach_date'],
        'sic': row['sic'],
        'current_assigned_cik': int(row['cik']) if pd.notna(row['cik']) else None,
        'reasoning_prompt': f"""
Look up the SEC CIK (Central Index Key) for this firm.

Firm: {row['org_name']}
Ticker: {row['ticker']}
Breach Date: {row['breach_date']}
SIC Code: {row['sic']}
Currently assigned CIK (may be incorrect): {int(row['cik']) if pd.notna(row['cik']) else 'Unknown'}

Task:
1. Determine the correct CIK for this firm from SEC EDGAR
2. Provide the correct ticker (verify against provided ticker)
3. Identify the company type (parent/traded company vs subsidiary)
4. Provide your source (URL, reasoning)
5. Confidence level (HIGH, MEDIUM, LOW)

Output as JSON:
{{
  "org_name": "{row['org_name']}",
  "correct_cik": <number or null if not found>,
  "correct_ticker": "<ticker>",
  "company_type": "parent|subsidiary|private|other",
  "source": "<URL or description>",
  "reasoning": "<brief explanation>",
  "confidence": "HIGH|MEDIUM|LOW"
}}

If the firm is private, acquired, or not in SEC, return null for correct_cik and explain why in reasoning.
"""
    })

df_batch = pd.DataFrame(reasoning_batch)

# Save batch for reference
batch_path = Path("outputs/reasoning_pass_batch.csv")
df_batch[['org_name', 'ticker', 'breach_date', 'sic', 'current_assigned_cik']].to_csv(batch_path, index=False)

print("Reasoning batch prepared:")
print(f"  Total unresolved records: {len(df_batch)}")
print(f"  Output file: {batch_path}")

print(f"\nRecords to resolve via reasoning:")
for _, row in df_batch.iterrows():
    print(f"  {row['org_name'][:50]:50s} | ticker: {row['ticker']:6s}")

print(f"\n" + "=" * 100)
print("REASONING PASS INSTRUCTIONS")
print("=" * 100)
print(f"""
For each of the {len(df_batch)} unresolved records:

1. Open SEC EDGAR (https://www.sec.gov/cgi-bin/browse-edgar)
2. Search for the firm by name or ticker
3. Verify the CIK and company details
4. Check if it's a public company, subsidiary, or private
5. Record the correct CIK and source URL

Alternatively, use reasoning to infer:
- Major public companies should have SEC filings
- Subsidiaries may not have separate CIKs (use parent instead)
- If not found in SEC, note in reasoning (private, delisted, acquired, etc.)

Output: Fill in correct CIK for each record in the validation set
- correct_cik: The correct SEC CIK
- correct_permno: CRSP PERMNO (if applicable, from CRSP stocknames)
- source: Where you verified (SEC EDGAR URL or reasoning)
- notes: Any relevant notes
""")
