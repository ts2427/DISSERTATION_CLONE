import subprocess
import sys

print("=" * 80)
print("RUNNING ALL ROBUSTNESS CHECKS")
print("=" * 80)

scripts = [
    ('scripts/robustness_1_alternative_windows.py', 'Alternative Event Windows'),
    ('scripts/robustness_2_timing_thresholds.py', 'Alternative Timing Thresholds'),
    ('scripts/robustness_3_sample_restrictions.py', 'Sample Restrictions'),
    ('scripts/robustness_4_standard_errors.py', 'Alternative Standard Errors')
]

for script, name in scripts:
    print(f"\n{'='*80}")
    print(f"Running: {name}")
    print(f"{'='*80}\n")
    
    result = subprocess.run([sys.executable, script], capture_output=False)
    
    if result.returncode != 0:
        print(f"\n⚠ {name} failed with return code {result.returncode}")
    else:
        print(f"\n✓ {name} completed successfully")

print("\n" + "=" * 80)
print("✓ ALL ROBUSTNESS CHECKS COMPLETE")
print("=" * 80)
print("\nAll output saved to: outputs/robustness/tables/")