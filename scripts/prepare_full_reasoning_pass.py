"""
Prepare reasoning pass for all unmatched + ambiguous org_names from full dataset
"""

import pandas as pd
from pathlib import Path

print("=" * 100)
print("PREPARE REASONING PASS FOR FULL DATASET")
print("=" * 100)

# Load resolution summary
summary_path = Path("outputs/full_dataset_resolution_summary.csv")
df_summary = pd.read_csv(summary_path)

# Load full dataset for record counts
prc_path = Path("Data/processed/FINAL_DISSERTATION_DATASET_DEDUPLICATED_ENRICHED.csv")
df_prc = pd.read_csv(prc_path)

print(f"\nLoaded resolution summary: {len(df_summary):,} org_names")

# ============================================================================
# Extract unmatched org_names
# ============================================================================
print("\n[1/2] Extracting unmatched org_names...")

unmatched = df_summary[df_summary['cik'].isna()].copy()
print(f"  Unmatched org_names: {len(unmatched)}")

# Get record counts for each
unmatched_org_names = list(unmatched['org_name'].unique())
record_counts = {}
for org_name in unmatched_org_names:
    count = len(df_prc[df_prc['org_name'] == org_name])
    record_counts[org_name] = count

# Sort by record count (prioritize high-volume)
unmatched_sorted = sorted(
    [(org, record_counts[org]) for org in unmatched_org_names],
    key=lambda x: x[1],
    reverse=True
)

print(f"\nTop 20 unmatched org_names by record count:")
for org_name, count in unmatched_sorted[:20]:
    print(f"  {org_name[:55]:55s} ({count:3d} records)")

# ============================================================================
# Prepare reasoning pass input
# ============================================================================
print("\n[2/2] Preparing reasoning pass input...")

reasoning_prompt = """You are resolving SEC CIKs for firms in a data breach dataset. For each org_name, determine the correct CIK.

Firms to resolve (sorted by record count - higher numbers are higher priority):

"""

for idx, (org_name, count) in enumerate(unmatched_sorted, 1):
    reasoning_prompt += f"{idx:3d}. {org_name} ({count} records in dataset)\n"

reasoning_prompt += """
For each firm:
1. Determine the correct SEC CIK using SEC EDGAR or reasoning about company structures
2. If private/nonprofit/not found, return null for CIK
3. Provide your source and reasoning
4. Rate confidence as HIGH, MEDIUM, or LOW

OUTPUT FORMAT:
Return a JSON array with one object per firm:
[
  {
    "org_name": "firm name",
    "correct_cik": 12345 or null,
    "correct_ticker": "TICK" or null,
    "company_type": "parent|subsidiary|private|nonprofit|acquired|other",
    "source": "where you found this",
    "reasoning": "brief explanation",
    "confidence": "HIGH|MEDIUM|LOW"
  },
  ...
]

PRIORITY: Firms with higher record counts (listed first) are most important. Focus on getting those correct.
SUBSIDIARIES: If a firm is a known subsidiary, use parent company's CIK unless it files separately.
BANKRUPTCIES/ACQUISITIONS: Note if firm was acquired or went bankrupt; use appropriate CIK for the period.

Resolve all """ + str(len(unmatched_sorted)) + """ firms."""

# Save prompt to file for reference
prompt_path = Path("outputs/full_reasoning_pass_prompt.txt")
with open(prompt_path, 'w') as f:
    f.write(reasoning_prompt)

print(f"\nReasoning pass prompt saved: {prompt_path}")
print(f"Total org_names to resolve: {len(unmatched_sorted)}")
print(f"Total records affected: {sum(record_counts.values()):,}")

# ============================================================================
# Summary
# ============================================================================
print("\n" + "=" * 100)
print("REASONING PASS READY")
print("=" * 100)

print(f"""
SCOPE:
  Org_names to resolve: {len(unmatched_sorted)}
  Records affected: {sum(record_counts.values()):,} ({sum(record_counts.values())/len(df_prc)*100:.1f}%)
  High-volume targets (>5 records): {len([c for c in record_counts.values() if c > 5])}

NEXT STEP:
  Run Agent with the prepared reasoning prompt to resolve all {len(unmatched_sorted)} org_names
  Agent will output JSON with CIK assignments and confidence levels
  Parse results and apply to dataset
""")

print("=" * 100)
