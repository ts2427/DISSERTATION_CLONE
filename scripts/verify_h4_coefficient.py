import pandas as pd
import statsmodels.api as sm
import numpy as np

df = pd.read_csv('Data/processed/FINAL_DISSERTATION_DATASET_DEDUPLICATED_ENRICHED.csv')
df = df.dropna(subset=['car_30d', 'firm_size_log', 'leverage', 'roa',
                        'immediate_disclosure', 'fcc_reportable',
                        'prior_breaches_1yr', 'health_breach'])

# Ensure all numeric columns
numeric_cols = ['immediate_disclosure', 'fcc_reportable', 'prior_breaches_1yr',
                'health_breach', 'firm_size_log', 'leverage', 'roa', 'car_30d']
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce')

df = df.dropna(subset=numeric_cols)

X = sm.add_constant(df[['immediate_disclosure', 'fcc_reportable',
                          'prior_breaches_1yr', 'health_breach',
                          'firm_size_log', 'leverage', 'roa']].astype(float))
y = df['car_30d'].astype(float)

model = sm.OLS(y, X).fit(cov_type='HC3')

print(f"H4 health_breach coefficient: {model.params['health_breach']:.4f}%")
print(f"H4 SE: {model.bse['health_breach']:.4f}")
print(f"H4 p-value: {model.pvalues['health_breach']:.4f}")
print(f"N total: {len(df)}")
print(f"N health breach: {df['health_breach'].sum()}")
print(f"MDE at 80% power: {(1.96 + 0.842) * model.bse['health_breach']:.4f}%")
