import pandas as pd

path = 'Data/processed/FINAL_DISSERTATION_DATASET_DEDUPLICATED_ENRICHED.csv'
df = pd.read_csv(path)

print(f"File: {path}")
print(f"Rows: {len(df)}")
print(f"FCC obs: {(df['fcc_reportable'] == True).sum()}")

boost = df[df['org_name'] == 'Boost Mobile']
if len(boost) > 0:
    print(f"Boost Mobile CIK: {boost['cik'].iloc[0]}")

# Check if the file was modified recently
import os
stat = os.stat(path)
from datetime import datetime
mod_time = datetime.fromtimestamp(stat.st_mtime)
print(f"Last modified: {mod_time}")
