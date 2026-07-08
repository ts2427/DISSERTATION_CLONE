"""
Quick diagnostic: Check cell sizes in FCC × CVSS Complexity crosstab
"""
import pandas as pd

# Load data
df = pd.read_csv('Data/processed/FINAL_DISSERTATION_DATASET_WITH_CVSS.csv')

# Create crosstab
print("\n" + "="*60)
print("CROSSTAB: FCC Regulation × High Complexity Breach")
print("="*60 + "\n")

crosstab = pd.crosstab(df['fcc_reportable'], df['has_high_complexity'], margins=True)
print(crosstab)

print("\n" + "="*60)
print("INTERPRETATION")
print("="*60)
print(f"Total observations: {len(df)}")
print(f"FCC-reportable firms: {(df['fcc_reportable']==1).sum()}")
print(f"Non-FCC firms: {(df['fcc_reportable']==0).sum()}")
print(f"High-complexity breaches (CVSS>=7.0): {(df['has_high_complexity']==1).sum()}")
print(f"Low-complexity breaches (CVSS<7.0): {(df['has_high_complexity']==0).sum()}")

# Key cell sizes
fcc_low = ((df['fcc_reportable']==1) & (df['has_high_complexity']==0)).sum()
fcc_high = ((df['fcc_reportable']==1) & (df['has_high_complexity']==1)).sum()
no_fcc_low = ((df['fcc_reportable']==0) & (df['has_high_complexity']==0)).sum()
no_fcc_high = ((df['fcc_reportable']==0) & (df['has_high_complexity']==1)).sum()

print(f"\nCRITICAL CELL SIZES:")
print(f"  FCC × Low-Complexity:  {fcc_low:4d} obs (threshold: ~50+)")
print(f"  FCC × High-Complexity: {fcc_high:4d} obs")
print(f"  Non-FCC × Low-Complexity:  {no_fcc_low:4d} obs")
print(f"  Non-FCC × High-Complexity: {no_fcc_high:4d} obs")

# Check for sparsity
print("\nSPARSITY CHECK:")
if fcc_low < 50:
    print(f"  ⚠️  WARNING: FCC × Low-Complexity cell is thin ({fcc_low} obs)")
    print(f"     This may cause interaction coefficient instability")
else:
    print(f"  ✓ FCC × Low-Complexity cell is adequate ({fcc_low} obs)")
