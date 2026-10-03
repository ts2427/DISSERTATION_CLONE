import subprocess
import time
import os

print("=" * 80)
print(" " * 20 + "DISSERTATION ENRICHMENT PIPELINE")
print("=" * 80)

print("\nThis script will run 6 essential data enrichment scripts.")
print("Total estimated time: 20-25 minutes")
print("\nPress Enter to start, or Ctrl+C to cancel...")
input()

# Define essential enrichment scripts only
pipelines = [
    {
        'number': 1,
        'name': 'Prior Breach History',
        'script': '41_prior_breaches.py',
        'est_time': '1 minute',
        'description': 'Count repeat offenders and breach frequency (H3)'
    },
    {
        'number': 2,
        'name': 'Industry-Adjusted Returns',
        'script': '42_industry_returns.py',
        'est_time': '3 minutes',
        'description': 'Calculate industry-adjusted CARs (Robustness)'
    },
    {
        'number': 3,
        'name': 'Institutional Ownership',
        'script': '44_institutional_ownership.py',
        'est_time': '3 minutes',
        'description': 'Get institutional ownership (Control variable)'
    },
    {
        'number': 4,
        'name': 'Breach Severity Classification',
        'script': '45_breach_severity_nlp.py',
        'est_time': '2 minutes',
        'description': 'NLP classification of breach types (H4)'
    },
    {
        'number': 5,
        'name': 'Executive Turnover',
        'script': '46_executive_changes.py',
        'est_time': '10 minutes',
        'description': 'Detect executive changes from SEC filings (H5)'
    },
    {
        'number': 6,
        'name': 'Regulatory Enforcement',
        'script': '47_regulatory_enforcement.py',
        'est_time': '1 minute',
        'description': 'Check FCC/FTC enforcement actions (H6)'
    }
]

# Track results
results = []
start_time = time.time()

print("\n" + "=" * 80)
print("STARTING ENRICHMENT PIPELINE")
print("=" * 80)

for pipeline in pipelines:
    print("\n" + "=" * 80)
    print(f"SCRIPT {pipeline['number']}/6: {pipeline['name']}")
    print("=" * 80)
    print(f"Description: {pipeline['description']}")
    print(f"Estimated time: {pipeline['est_time']}")
    print(f"Running: scripts/{pipeline['script']}")
    print("-" * 80)
    
    script_start = time.time()
    
    try:
        # Run the script
        result = subprocess.run(
            ['python', f"scripts/{pipeline['script']}"],
            capture_output=False,
            text=True
        )
        
        script_elapsed = time.time() - script_start
        
        if result.returncode == 0:
            status = "✓ SUCCESS"
            success = True
        else:
            status = "✗ FAILED"
            success = False
        
        results.append({
            'script': pipeline['name'],
            'status': status,
            'time': script_elapsed,
            'success': success
        })
        
        print(f"\n{status} - Completed in {script_elapsed/60:.1f} minutes")
        
    except Exception as e:
        script_elapsed = time.time() - script_start
        results.append({
            'script': pipeline['name'],
            'status': "✗ ERROR",
            'time': script_elapsed,
            'success': False
        })
        print(f"\n✗ ERROR: {e}")
    
    print("-" * 80)

total_elapsed = time.time() - start_time

# Summary
print("\n" + "=" * 80)
print("ENRICHMENT PIPELINE COMPLETE")
print("=" * 80)

print(f"\nTotal time: {total_elapsed/60:.1f} minutes")
print(f"Scripts run: {len(results)}")
print(f"Successful: {sum(r['success'] for r in results)}")
print(f"Failed: {sum(not r['success'] for r in results)}")

print("\n" + "-" * 80)
print("SCRIPT RESULTS:")
print("-" * 80)

for r in results:
    print(f"{r['status']:12} {r['script']:40} ({r['time']/60:.1f} min)")

# Check output files
print("\n" + "-" * 80)
print("OUTPUT FILES CREATED:")
print("-" * 80)

enrichment_files = [
    'prior_breach_history.csv',
    'industry_adjusted_returns.csv',
    'institutional_ownership.csv',
    'breach_severity_classification.csv',
    'executive_changes.csv',
    'regulatory_enforcement.csv'
]

for filename in enrichment_files:
    filepath = f'Data/enrichment/{filename}'
    if os.path.exists(filepath):
        size = os.path.getsize(filepath)
        print(f"  ✓ {filename:45} ({size:,} bytes)")
    else:
        print(f"  ✗ {filename:45} (NOT FOUND)")

print("\n" + "=" * 80)

if all(r['success'] for r in results):
    print("✓✓✓ ALL ESSENTIAL ENRICHMENTS COMPLETE ✓✓✓")
    print("\nNext step: Run scripts/merge_enrichments.py")
    print("\nEnrichments mapped to hypotheses:")
    print("  H3: Prior Breach History")
    print("  H4: Breach Severity Classification")
    print("  H5: Executive Turnover")
    print("  H6: Regulatory Enforcement")
    print("  Control: Institutional Ownership")
    print("  Robustness: Industry-Adjusted Returns")
else:
    print("⚠ SOME SCRIPTS FAILED - CHECK LOGS ABOVE")
    print("\nYou can still proceed with merge using successful scripts")

print("=" * 80)