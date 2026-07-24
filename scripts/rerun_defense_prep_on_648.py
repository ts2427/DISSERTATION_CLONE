"""
Rerun all five defense prep analyses on corrected 648-observation sample
1. Leave-one-out
2. Randomization inference
3. Winsorization
4. H3 power analysis
5. H4 power analysis
"""

import subprocess
import sys

scripts = [
    ("Leave-one-out sensitivity", "scripts/h2_robustness_leave_one_out.py"),
    ("Randomization inference", "scripts/h2_randomization_inference.py"),
    ("Winsorization robustness", "scripts/h2_robustness_winsorization.py"),
    ("H3 power analysis", "scripts/power_analysis_h3_h4.py"),
    ("H4 power analysis", "scripts/power_analysis_h3_h4.py"),
]

print("=" * 100)
print("RERUNNING DEFENSE PREP ANALYSES ON 648-OBSERVATION CORRECTED SAMPLE")
print("=" * 100)

for name, script in scripts:
    print(f"\n[Running] {name}: {script}")
    result = subprocess.run(
        [sys.executable, script],
        cwd="C:\\Users\\mcobp\\DISSERTATION_CLONE",
        capture_output=False
    )

    if result.returncode != 0:
        print(f"[ERROR] {name} failed with exit code {result.returncode}")
    else:
        print(f"[OK] {name} completed successfully")

print("\n" + "=" * 100)
print("DEFENSE PREP RERUN COMPLETE")
print("=" * 100)
print("\nAll analyses now run on corrected 648-observation sample.")
print("Results saved to outputs/defense_prep/")
