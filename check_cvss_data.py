import pandas as pd

df = pd.read_csv('Data/processed/FINAL_DISSERTATION_DATASET_WITH_CVSS.csv')

print("CVSS Complexity Columns Summary:")
print("=" * 80)

# Check key CVSS columns
cvss_cols = ['vendor_max_cvss', 'vendor_mean_cvss', 'has_high_complexity', 'complexity_category', 'severity_score']

for col in cvss_cols:
    if col in df.columns:
        non_null = df[col].notna().sum()
        print(f"\n{col}:")
        print(f"  Non-null count: {non_null:,} / {len(df):,}")
        if col != 'complexity_category':
            try:
                print(f"  Mean: {df[col].mean():.4f}")
                print(f"  Std: {df[col].std():.4f}")
                print(f"  Min/Max: {df[col].min():.2f} / {df[col].max():.2f}")
                print(f"  Sample values: {df[col].dropna().head(3).tolist()}")
            except:
                print(f"  (non-numeric)")
        else:
            print(f"  Value counts:\n{df[col].value_counts()}")

# Check correlation with FCC effect
df_analysis = df[df['has_crsp_data']==1].dropna(subset=['car_30d', 'vendor_max_cvss'])
print(f"\n\nAnalysis sample with CAR and CVSS: {len(df_analysis)} observations")
print(f"Correlation (CAR, CVSS): {df_analysis['car_30d'].corr(df_analysis['vendor_max_cvss']):.4f}")

# Check actual CVSS usage in heterogeneity
print(f"\n\nHigh complexity breaches: {(df['vendor_max_cvss'] >= 7.0).sum():,}")
print(f"Low complexity breaches: {(df['vendor_max_cvss'] < 7.0).sum():,}")
