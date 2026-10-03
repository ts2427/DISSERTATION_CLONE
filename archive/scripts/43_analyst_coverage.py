import pandas as pd
import numpy as np
import wrds
import os

print("=" * 60)
print("ANALYST COVERAGE DATA (FIXED)")
print("=" * 60)

# Load breach data
df = pd.read_excel('Data/processed/FINAL_DISSERTATION_DATASET.xlsx')
print(f"\n✓ Loaded {len(df)} breach records")

# Find ticker column
ticker_col = None
for col in ['Stock Ticker', 'Map', 'ticker', 'TICKER']:
    if col in df.columns:
        ticker_col = col
        break

if ticker_col is None:
    print("\n✗ ERROR: No ticker column found!")
    print("Available columns:", [col for col in df.columns if 'tick' in col.lower() or 'map' in col.lower()])
    exit()

print(f"✓ Using ticker column: '{ticker_col}'")

# Connect to WRDS
print("\nConnecting to WRDS...")
db = wrds.Connection()
print("✓ Connected")

# Get records with tickers
analysis_df = df[df[ticker_col].notna()].copy()
print(f"✓ {len(analysis_df)} records with stock tickers")

tickers = analysis_df[ticker_col].dropna().unique().tolist()
ticker_list = ','.join([f"'{t}'" for t in tickers])

min_date = analysis_df['breach_date'].min() - pd.DateOffset(years=1)
max_date = analysis_df['breach_date'].max()

print(f"\nQuerying IBES for {len(tickers)} tickers...")
print(f"Date range: {min_date.date()} to {max_date.date()}")

# Query IBES Summary Statistics
try:
    analyst_data = db.raw_sql(f"""
        SELECT ticker, statpers, fpedats, numest, numup, numdown,
               meanest, medest, stdev, highest, lowest
        FROM ibes.statsum_epsus
        WHERE ticker IN ({ticker_list})
        AND statpers >= '{min_date.strftime('%Y-%m-%d')}'
        AND statpers <= '{max_date.strftime('%Y-%m-%d')}'
        AND fpi = '1'
        AND measure = 'EPS'
    """, date_cols=['statpers', 'fpedats'])
    
    print(f"✓ Downloaded {len(analyst_data):,} analyst summary records")
    
    # For each breach, get analyst coverage metrics
    print("\nMatching analyst data to breach dates...")
    
    results = []
    matched = 0
    
    for idx, row in analysis_df.iterrows():
        ticker = row[ticker_col]
        breach_date = pd.to_datetime(row['breach_date'])
        
        # Get analyst data closest to breach date (within 90 days before)
        window_start = breach_date - pd.DateOffset(days=90)
        window_end = breach_date
        
        analyst_window = analyst_data[
            (analyst_data['ticker'] == ticker) &
            (analyst_data['statpers'] >= window_start) &
            (analyst_data['statpers'] <= window_end)
        ].sort_values('statpers')
        
        if len(analyst_window) > 0:
            # Get most recent analyst summary
            recent = analyst_window.iloc[-1]
            
            num_analysts = recent['numest']
            num_upgrades = recent['numup'] if pd.notna(recent['numup']) else 0
            num_downgrades = recent['numdown'] if pd.notna(recent['numdown']) else 0
            mean_estimate = recent['meanest']
            std_estimate = recent['stdev']
            
            # Calculate analyst coverage metrics
            high_coverage = 1 if num_analysts >= 5 else 0
            analyst_dispersion = std_estimate / abs(mean_estimate) if pd.notna(mean_estimate) and mean_estimate != 0 else np.nan
            
            matched += 1
        else:
            num_analysts = 0
            num_upgrades = 0
            num_downgrades = 0
            mean_estimate = np.nan
            std_estimate = np.nan
            high_coverage = 0
            analyst_dispersion = np.nan
        
        results.append({
            'breach_id': idx,
            'ticker': ticker,
            'breach_date': breach_date,
            'num_analysts': num_analysts,
            'num_analyst_upgrades': num_upgrades,
            'num_analyst_downgrades': num_downgrades,
            'analyst_mean_estimate': mean_estimate,
            'analyst_std_estimate': std_estimate,
            'analyst_dispersion': analyst_dispersion,
            'high_analyst_coverage': high_coverage,
            'has_analyst_coverage': 1 if num_analysts > 0 else 0
        })
        
        if (len(results) % 100 == 0):
            print(f"  Processed {len(results)}/{len(analysis_df)} ({matched} matched)")
    
    results_df = pd.DataFrame(results)
    
    # Summary statistics
    print("\n" + "=" * 60)
    print("ANALYST COVERAGE SUMMARY")
    print("=" * 60)
    
    print(f"\nTotal processed: {len(results_df)}")
    print(f"Records with analyst coverage: {results_df['has_analyst_coverage'].sum()} ({results_df['has_analyst_coverage'].mean()*100:.1f}%)")
    print(f"Records with high coverage (5+ analysts): {results_df['high_analyst_coverage'].sum()} ({results_df['high_analyst_coverage'].mean()*100:.1f}%)")
    
    print(f"\nAnalyst count distribution:")
    print(results_df[results_df['num_analysts'] > 0]['num_analysts'].describe())
    
    if results_df['has_analyst_coverage'].sum() > 0:
        print(f"\nTop 10 most covered firms:")
        top_coverage = results_df.nlargest(10, 'num_analysts')[['ticker', 'num_analysts', 'breach_date']]
        print(top_coverage.to_string(index=False))
    
    # Save results
    os.makedirs('Data/enrichment', exist_ok=True)
    
    results_df.to_csv('Data/enrichment/analyst_coverage.csv', index=False)
    print(f"\n✓ Saved to Data/enrichment/analyst_coverage.csv")
    
    print("\n" + "=" * 60)
    print("✓ ANALYST COVERAGE COMPLETE")
    print("=" * 60)
    print(f"\nCreated variables:")
    print("  • num_analysts (count of analysts following the stock)")
    print("  • num_analyst_upgrades (recent upgrades)")
    print("  • num_analyst_downgrades (recent downgrades)")
    print("  • analyst_mean_estimate (consensus EPS estimate)")
    print("  • analyst_std_estimate (estimate dispersion)")
    print("  • analyst_dispersion (coefficient of variation)")
    print("  • high_analyst_coverage (1 if 5+ analysts)")
    print("  • has_analyst_coverage (1 if any analysts)")

except Exception as e:
    print(f"\n✗ Error querying IBES: {e}")
    print(f"  Error type: {type(e).__name__}")
    print("\nThis may mean:")
    print("  1. Your WRDS subscription doesn't include IBES")
    print("  2. IBES data not available for these tickers")
    print("  3. Table name or structure changed")
    print("\nCreating placeholder file...")
    
    # Create placeholder
    results_df = pd.DataFrame({
        'breach_id': range(len(analysis_df)),
        'ticker': analysis_df[ticker_col].values,
        'breach_date': analysis_df['breach_date'].values,
        'num_analysts': 0,
        'num_analyst_upgrades': 0,
        'num_analyst_downgrades': 0,
        'analyst_mean_estimate': np.nan,
        'analyst_std_estimate': np.nan,
        'analyst_dispersion': np.nan,
        'high_analyst_coverage': 0,
        'has_analyst_coverage': 0
    })
    
    os.makedirs('Data/enrichment', exist_ok=True)
    results_df.to_csv('Data/enrichment/analyst_coverage.csv', index=False)
    print("✓ Created placeholder file with zero coverage")

finally:
    db.close()
    print("\n✓ WRDS connection closed")