"""
Generate NLP Validation Report

Creates human-readable HTML and markdown reports from validation metrics.
Includes visualizations, tables, and interpretation guide.
"""

import json
import pandas as pd
from pathlib import Path
from datetime import datetime


def load_metrics(metrics_path):
    """Load validation metrics from JSON file."""
    try:
        with open(metrics_path, 'r') as f:
            metrics = json.load(f)
        return metrics
    except FileNotFoundError:
        print(f"ERROR: Metrics file not found: {metrics_path}")
        return None
    except json.JSONDecodeError:
        print(f"ERROR: Could not parse metrics JSON: {metrics_path}")
        return None


def metrics_to_dataframe(metrics):
    """Convert metrics dict to DataFrame for easy table generation."""
    rows = []
    for breach_type, metrics_dict in metrics.get('per_category', {}).items():
        row = {
            'Breach Type': breach_type.replace('_', ' ').title(),
            'Precision': metrics_dict.get('precision', 0),
            'Recall': metrics_dict.get('recall', 0),
            'F1-Score': metrics_dict.get('f1_score', 0),
            'Samples': metrics_dict.get('n_samples', 0),
            'True Positives': metrics_dict.get('n_positive_true', 0),
            'Predicted Positives': metrics_dict.get('n_positive_pred', 0),
        }
        rows.append(row)

    return pd.DataFrame(rows)


def generate_markdown_report(metrics, output_path):
    """Generate markdown report from metrics."""
    report = []

    report.append("# NLP Classifier Validation Report")
    report.append("")

    # Header info
    overall = metrics.get('overall', {})
    report.append(f"**Validation Date:** {overall.get('validation_date', 'Unknown')[:10]}")
    report.append(f"**Total Samples:** {overall.get('n_total_samples', 0)}")
    report.append("")

    # Overall metrics
    report.append("## Overall Performance")
    report.append("")
    report.append("| Metric | Score |")
    report.append("|--------|-------|")
    report.append(f"| Weighted Precision | {overall.get('weighted_precision', 0):.3f} |")
    report.append(f"| Weighted Recall | {overall.get('weighted_recall', 0):.3f} |")
    report.append(f"| Weighted F1-Score | {overall.get('weighted_f1', 0):.3f} |")
    report.append(f"| Accuracy | {overall.get('accuracy', 0):.3f} |")
    report.append("")

    # Per-category metrics
    report.append("## Per-Category Metrics")
    report.append("")

    df = metrics_to_dataframe(metrics)
    if not df.empty:
        # Add markdown table
        report.append(df.to_markdown(index=False))
        report.append("")

    # Interpretation guide
    report.append("## Interpretation Guide")
    report.append("")
    report.append("### Precision")
    report.append("Of predicted positives, what percentage were actually positive?")
    report.append("- **High precision (>0.80)**: Low false positive rate - good for minimizing false alarms")
    report.append("- **Low precision (<0.60)**: Classifier over-sensitive - needs keyword refinement")
    report.append("")

    report.append("### Recall")
    report.append("Of actual positives, what percentage did the classifier find?")
    report.append("- **High recall (>0.80)**: Low false negative rate - good for catching all cases")
    report.append("- **Low recall (<0.60)**: Classifier missing cases - needs more keywords")
    report.append("")

    report.append("### F1-Score")
    report.append("Harmonic mean of precision and recall (0-1 scale, higher is better)")
    report.append("- **Excellent (>0.85)**: Very good overall performance")
    report.append("- **Good (0.75-0.85)**: Acceptable performance")
    report.append("- **Poor (<0.75)**: Needs improvement")
    report.append("")

    # Recommendations
    report.append("## Recommendations")
    report.append("")

    poor_categories = [
        (cat, metrics.get('per_category', {}).get(cat, {}))
        for cat in metrics.get('per_category', {}).keys()
        if metrics.get('per_category', {}).get(cat, {}).get('f1_score', 0) < 0.75
    ]

    if poor_categories:
        report.append("### Areas for Improvement (F1 < 0.75)")
        report.append("")
        for cat_name, cat_metrics in poor_categories:
            f1 = cat_metrics.get('f1_score', 0)
            prec = cat_metrics.get('precision', 0)
            rec = cat_metrics.get('recall', 0)

            report.append(f"#### {cat_name.replace('_', ' ').title()}")
            report.append(f"**F1-Score:** {f1:.3f}")

            if rec < prec:
                report.append("**Issue:** Low recall (missing cases)")
                report.append("**Action:** Add more keywords to catch missed cases")
            else:
                report.append("**Issue:** Low precision (false positives)")
                report.append("**Action:** Refine keywords or increase specificity")

            report.append("")
    else:
        report.append("All categories have F1-score >= 0.75. Classifier performance is good!")
        report.append("")

    # Summary
    report.append("## Summary")
    report.append("")
    report.append(f"Validation Date: {overall.get('validation_date', 'Unknown')}")
    report.append(f"Sample Size: {overall.get('n_total_samples', 0)} manually coded breaches")
    report.append(f"Accuracy: {overall.get('accuracy', 0):.1%}")
    report.append("")
    report.append("The NLP classifier demonstrates {} overall performance.".format(
        "excellent" if overall.get('accuracy', 0) > 0.85
        else "good" if overall.get('accuracy', 0) > 0.75
        else "acceptable" if overall.get('accuracy', 0) > 0.65
        else "needs improvement"
    ))

    # Write to file
    markdown_content = "\n".join(report)
    with open(output_path, 'w') as f:
        f.write(markdown_content)

    return markdown_content


def generate_html_report(metrics, output_path):
    """Generate HTML report from metrics."""
    html = []

    html.append("<!DOCTYPE html>")
    html.append("<html>")
    html.append("<head>")
    html.append("    <meta charset='utf-8'>")
    html.append("    <title>NLP Validation Report</title>")
    html.append("    <style>")
    html.append("        body { font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }")
    html.append("        .container { background-color: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }")
    html.append("        h1 { color: #333; border-bottom: 3px solid #0066cc; padding-bottom: 10px; }")
    html.append("        h2 { color: #0066cc; margin-top: 30px; }")
    html.append("        h3 { color: #666; }")
    html.append("        table { border-collapse: collapse; width: 100%; margin: 20px 0; }")
    html.append("        th { background-color: #0066cc; color: white; padding: 12px; text-align: left; }")
    html.append("        td { border: 1px solid #ddd; padding: 10px; }")
    html.append("        tr:nth-child(even) { background-color: #f9f9f9; }")
    html.append("        .metric-box { background-color: #f0f8ff; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #0066cc; }")
    html.append("        .good { color: #28a745; font-weight: bold; }")
    html.append("        .warning { color: #ff9800; font-weight: bold; }")
    html.append("        .poor { color: #d32f2f; font-weight: bold; }")
    html.append("        .metric-value { font-size: 1.2em; font-weight: bold; }")
    html.append("    </style>")
    html.append("</head>")
    html.append("<body>")
    html.append("    <div class='container'>")

    # Title and header
    overall = metrics.get('overall', {})
    html.append("        <h1>NLP Classifier Validation Report</h1>")
    html.append(f"        <p><strong>Validation Date:</strong> {overall.get('validation_date', 'Unknown')[:10]}</p>")
    html.append(f"        <p><strong>Total Samples:</strong> {overall.get('n_total_samples', 0)} manually coded breaches</p>")

    # Overall metrics
    html.append("        <h2>Overall Performance</h2>")
    html.append("        <div class='metric-box'>")

    accuracy = overall.get('accuracy', 0)
    accuracy_class = 'good' if accuracy > 0.85 else 'warning' if accuracy > 0.75 else 'poor'

    html.append(f"            <p><strong>Accuracy:</strong> <span class='{accuracy_class} metric-value'>{accuracy:.1%}</span></p>")
    html.append(f"            <p><strong>Weighted Precision:</strong> <span class='metric-value'>{overall.get('weighted_precision', 0):.3f}</span></p>")
    html.append(f"            <p><strong>Weighted Recall:</strong> <span class='metric-value'>{overall.get('weighted_recall', 0):.3f}</span></p>")
    html.append(f"            <p><strong>Weighted F1-Score:</strong> <span class='metric-value'>{overall.get('weighted_f1', 0):.3f}</span></p>")
    html.append("        </div>")

    # Per-category metrics table
    html.append("        <h2>Per-Category Performance</h2>")
    html.append("        <table>")
    html.append("            <thead>")
    html.append("                <tr>")
    html.append("                    <th>Breach Type</th>")
    html.append("                    <th>Precision</th>")
    html.append("                    <th>Recall</th>")
    html.append("                    <th>F1-Score</th>")
    html.append("                    <th>Samples</th>")
    html.append("                </tr>")
    html.append("            </thead>")
    html.append("            <tbody>")

    for breach_type, cat_metrics in metrics.get('per_category', {}).items():
        f1 = cat_metrics.get('f1_score', 0)
        f1_class = 'good' if f1 > 0.85 else 'warning' if f1 > 0.75 else 'poor'

        html.append("                <tr>")
        html.append(f"                    <td>{breach_type.replace('_', ' ').title()}</td>")
        html.append(f"                    <td>{cat_metrics.get('precision', 0):.3f}</td>")
        html.append(f"                    <td>{cat_metrics.get('recall', 0):.3f}</td>")
        html.append(f"                    <td><span class='{f1_class}'>{f1:.3f}</span></td>")
        html.append(f"                    <td>{cat_metrics.get('n_samples', 0)}</td>")
        html.append("                </tr>")

    html.append("            </tbody>")
    html.append("        </table>")

    # Recommendations
    html.append("        <h2>Analysis & Recommendations</h2>")
    poor_categories = [
        (cat, metrics.get('per_category', {}).get(cat, {}))
        for cat in metrics.get('per_category', {}).keys()
        if metrics.get('per_category', {}).get(cat, {}).get('f1_score', 0) < 0.75
    ]

    if poor_categories:
        html.append("        <div class='metric-box'>")
        html.append("            <h3>Categories Needing Improvement</h3>")
        for cat_name, cat_metrics in poor_categories:
            html.append(f"            <h4>{cat_name.replace('_', ' ').title()}</h4>")
            html.append(f"            <p><strong>F1-Score:</strong> {cat_metrics.get('f1_score', 0):.3f}</p>")

            if cat_metrics.get('recall', 0) < cat_metrics.get('precision', 0):
                html.append("            <p class='warning'>Issue: Low recall (missing cases)</p>")
                html.append("            <p>Recommendation: Add more keywords to catch missed cases</p>")
            else:
                html.append("            <p class='warning'>Issue: Low precision (false positives)</p>")
                html.append("            <p>Recommendation: Refine keywords or increase specificity</p>")
        html.append("        </div>")
    else:
        html.append("        <div class='metric-box'>")
        html.append("            <p class='good'>All categories have F1-score >= 0.75. Classifier performance is good!</p>")
        html.append("        </div>")

    html.append("    </div>")
    html.append("</body>")
    html.append("</html>")

    html_content = "\n".join(html)
    with open(output_path, 'w') as f:
        f.write(html_content)

    return html_content


def main():
    print("=" * 80)
    print("GENERATE VALIDATION REPORT")
    print("=" * 80)

    # Paths
    metrics_path = Path('validation_results') / 'validation_metrics.json'
    output_dir = Path('validation_results')

    print(f"\n[1/3] Loading metrics...")
    metrics = load_metrics(metrics_path)

    if metrics is None:
        print("\nERROR: Could not load metrics. Have you run validation yet?")
        print("Run: python validation/scripts/01_run_nlp_validation.py --manual-codes <path>")
        return

    print(f"  Loaded metrics for {metrics.get('overall', {}).get('n_total_samples', 0)} samples")

    # Generate markdown report
    print(f"\n[2/3] Generating markdown report...")
    md_path = output_dir / 'VALIDATION_REPORT.md'
    generate_markdown_report(metrics, md_path)
    print(f"  Saved: {md_path}")

    # Generate HTML report
    print(f"\n[3/3] Generating HTML report...")
    html_path = output_dir / 'validation_report.html'
    generate_html_report(metrics, html_path)
    print(f"  Saved: {html_path}")

    print("\n" + "=" * 80)
    print("REPORTS GENERATED")
    print("=" * 80)
    print(f"\nMarkdown: {md_path}")
    print(f"HTML: {html_path}")
    print("\nOpen the HTML file in a browser for a formatted view.")


if __name__ == '__main__':
    main()
