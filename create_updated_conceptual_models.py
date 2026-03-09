#!/usr/bin/env python3
"""
Create updated conceptual models incorporating mechanism analysis
- Essay 1: Market Reactions (Timing Irrelevance)
- Essay 2: Information Asymmetry (FCC Effect with Firm-Size Heterogeneity)
- Essay 3: Governance Response (Executive Turnover)
- Dissertation Framework: Three Parallel Mechanisms
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
COLORS = {
    'start': '#FF6B6B',      # Red - event
    'process': '#4ECDC4',    # Teal - process
    'result': '#45B7D1',     # Blue - result
    'null': '#95E1D3',       # Light green - null result
    'positive': '#2ECC71',   # Green - positive finding
    'negative': '#E74C3C',   # Dark red - negative finding
    'moderator': '#F39C12',  # Orange - moderator
    'theory': '#9B59B6'      # Purple - theory
}

# ============================================================================
# MODEL 1: ESSAY 1 - MARKET REACTIONS (Timing Irrelevance)
# ============================================================================

def create_essay1_model():
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')

    # Title
    ax.text(5, 9.5, 'Essay 1: Market Reactions to Data Breach Disclosure',
            fontsize=18, fontweight='bold', ha='center')
    ax.text(5, 9, 'Does Disclosure Timing Affect Stock Market Returns?',
            fontsize=13, ha='center', style='italic', color='#555')

    # Main flow
    # Data Breach
    breach_box = FancyBboxPatch((0.5, 7), 1.5, 1,
                               boxstyle="round,pad=0.1",
                               edgecolor='black', facecolor=COLORS['start'], linewidth=2)
    ax.add_patch(breach_box)
    ax.text(1.25, 7.5, 'Data Breach\nEvent', ha='center', va='center', fontweight='bold', fontsize=10)

    # Arrow
    ax.arrow(2.1, 7.5, 0.8, 0, head_width=0.15, head_length=0.15, fc='black', ec='black')

    # Timing Decision
    timing_box = FancyBboxPatch((3, 7), 1.5, 1,
                               boxstyle="round,pad=0.1",
                               edgecolor='black', facecolor=COLORS['process'], linewidth=2)
    ax.add_patch(timing_box)
    ax.text(3.75, 7.5, 'Timing Decision\n(Days to Disclosure)', ha='center', va='center', fontweight='bold', fontsize=10)

    # Arrow
    ax.arrow(4.6, 7.5, 0.8, 0, head_width=0.15, head_length=0.15, fc='black', ec='black')

    # Market Valuation
    valuation_box = FancyBboxPatch((5.5, 7), 1.8, 1,
                                  boxstyle="round,pad=0.1",
                                  edgecolor='black', facecolor=COLORS['null'], linewidth=2)
    ax.add_patch(valuation_box)
    ax.text(6.4, 7.5, 'CAR-30d\n(Market Return)', ha='center', va='center', fontweight='bold', fontsize=10)

    # Result box
    result_box = FancyBboxPatch((7.6, 6.8), 2, 1.4,
                               boxstyle="round,pad=0.1",
                               edgecolor='#333', facecolor='#FFFFCC', linewidth=3, linestyle='--')
    ax.add_patch(result_box)
    ax.text(8.6, 7.6, 'H1: Timing Effect', ha='center', fontweight='bold', fontsize=10)
    ax.text(8.6, 7.2, 'Coefficient: +0.57%', ha='center', fontsize=9)
    ax.text(8.6, 6.9, 'p = 0.539 (NOT SIGNIFICANT)', ha='center', fontsize=8, color='red', fontweight='bold')

    # What DOES matter
    ax.text(5, 5.5, 'What DOES Affect Market Returns:', fontsize=12, fontweight='bold')

    matters = [
        ('FCC Regulatory Status', '-2.20%***', 'p=0.010', 0.5, 4.8),
        ('Prior Breach History', '-0.22%*** per breach', 'strongest effect', 0.5, 4.2),
        ('Health Data Breach', '-2.51%***', 'p=0.004', 0.5, 3.6),
        ('Firm Size, Leverage, ROA', 'Various', 'All significant', 0.5, 3.0),
    ]

    for label, value, pval, x, y in matters:
        ax.text(x, y, f'• {label}: {value} ({pval})', fontsize=10, family='monospace')

    # Conclusion box
    conclusion = FancyBboxPatch((0.3, 0.5), 9.4, 2,
                               boxstyle="round,pad=0.1",
                               edgecolor=COLORS['negative'], facecolor='#FFE6E6', linewidth=2)
    ax.add_patch(conclusion)
    ax.text(5, 2.1, 'Key Finding: Markets Price Information Environment, NOT Disclosure Speed',
            ha='center', fontsize=12, fontweight='bold')
    ax.text(5, 1.6, 'Interpretation: Whether firms disclose on day 1 or day 30, market reactions are identical.',
            ha='center', fontsize=10)
    ax.text(5, 1.1, 'What matters: FCC regulatory status, breach severity, firm reputation (prior breaches)',
            ha='center', fontsize=10)

    plt.tight_layout()
    return fig

# ============================================================================
# MODEL 2: ESSAY 2 - INFORMATION ASYMMETRY (with Firm-Size Heterogeneity)
# ============================================================================

def create_essay2_model():
    fig, ax = plt.subplots(figsize=(14, 9))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')

    # Title
    ax.text(5, 9.5, 'Essay 2: Information Asymmetry and Market Uncertainty',
            fontsize=18, fontweight='bold', ha='center')
    ax.text(5, 9, 'Does FCC Regulation Increase or Decrease Market Volatility?',
            fontsize=13, ha='center', style='italic', color='#555')

    # Main flow
    # Data Breach
    breach_box = FancyBboxPatch((0.3, 7.8), 1.3, 0.8,
                               boxstyle="round,pad=0.05",
                               edgecolor='black', facecolor=COLORS['start'], linewidth=2)
    ax.add_patch(breach_box)
    ax.text(0.95, 8.2, 'Data Breach', ha='center', va='center', fontweight='bold', fontsize=9)

    # Arrow
    ax.arrow(1.7, 8.2, 0.6, 0, head_width=0.12, head_length=0.12, fc='black', ec='black')

    # FCC 7-day deadline
    fcc_box = FancyBboxPatch((2.4, 7.8), 1.4, 0.8,
                            boxstyle="round,pad=0.05",
                            edgecolor='black', facecolor=COLORS['process'], linewidth=2)
    ax.add_patch(fcc_box)
    ax.text(3.1, 8.2, 'FCC 7-day\nDeadline', ha='center', va='center', fontweight='bold', fontsize=9)

    # Arrow to firm size split
    ax.arrow(3.85, 8.2, 0.6, 0, head_width=0.12, head_length=0.12, fc='black', ec='black')

    # SPLIT: Small Firm Path
    ax.text(4.8, 8.7, 'FIRM SIZE HETEROGENEITY', fontsize=11, fontweight='bold', ha='center')

    # Small Firm Path
    small_label = FancyBboxPatch((4.3, 6.8), 1.2, 0.6,
                                boxstyle="round,pad=0.05",
                                edgecolor=COLORS['moderator'], facecolor='#FFF9E6', linewidth=2)
    ax.add_patch(small_label)
    ax.text(4.9, 7.1, 'Small Firms (Q1)', ha='center', va='center', fontweight='bold', fontsize=9)

    small_mechanism = [
        'Limited Staff',
        'Limited Systems',
        'Tight Constraint',
        'Incomplete Disclosure'
    ]

    y_pos = 6.3
    for item in small_mechanism:
        ax.text(4.9, y_pos, f'↓ {item}', ha='center', fontsize=8)
        y_pos -= 0.35

    # Small firm result
    small_result = FancyBboxPatch((4.2, 4.3), 1.4, 0.7,
                                 boxstyle="round,pad=0.05",
                                 edgecolor='black', facecolor=COLORS['negative'], linewidth=2)
    ax.add_patch(small_result)
    ax.text(4.9, 4.7, '+7.31%***\nVolatility', ha='center', va='center', fontweight='bold', fontsize=10, color='white')

    # Large Firm Path
    large_label = FancyBboxPatch((6.5, 6.8), 1.2, 0.6,
                                boxstyle="round,pad=0.05",
                                edgecolor=COLORS['moderator'], facecolor='#E6F9FF', linewidth=2)
    ax.add_patch(large_label)
    ax.text(7.1, 7.1, 'Large Firms (Q4)', ha='center', va='center', fontweight='bold', fontsize=9)

    large_mechanism = [
        'Dedicated Teams',
        'Advanced Systems',
        'Loose Constraint',
        'Complete Disclosure'
    ]

    y_pos = 6.3
    for item in large_mechanism:
        ax.text(7.1, y_pos, f'↓ {item}', ha='center', fontsize=8)
        y_pos -= 0.35

    # Large firm result
    large_result = FancyBboxPatch((6.4, 4.3), 1.4, 0.7,
                                 boxstyle="round,pad=0.05",
                                 edgecolor='black', facecolor=COLORS['positive'], linewidth=2)
    ax.add_patch(large_result)
    ax.text(7.1, 4.7, '-3.39%**\nVolatility', ha='center', va='center', fontweight='bold', fontsize=10, color='white')

    # Mechanism label
    ax.text(5.5, 3.8, 'Information Processing Capacity Constraint (Tushman & Nadler 1978)',
            ha='center', fontsize=10, fontweight='bold', style='italic', color='#9B59B6')

    # Key statistics
    ax.text(5, 3.1, 'Key Findings:', fontsize=11, fontweight='bold')
    ax.text(0.5, 2.6, f'• Main FCC Effect: +1.83%** (p=0.047) - Opposite of regulatory intent', fontsize=9, family='monospace')
    ax.text(0.5, 2.2, f'• Firm-size differential: 11 percentage points (Q1 vs Q4)', fontsize=9, family='monospace')
    ax.text(0.5, 1.8, f'• Cost per small firm: ~$37M additional annual cost of capital per breach', fontsize=9, family='monospace')
    ax.text(0.5, 1.4, f'• Other mechanisms tested: Complexity (p=0.97), Governance (p=0.84), Info Env (p=0.28) - ALL NOT SIGNIFICANT', fontsize=8, family='monospace')

    # Conclusion
    conclusion = FancyBboxPatch((0.3, 0.1), 9.4, 0.9,
                               boxstyle="round,pad=0.05",
                               edgecolor=COLORS['negative'], facecolor='#FFE6E6', linewidth=2)
    ax.add_patch(conclusion)
    ax.text(5, 0.65, 'Mandatory timing increases market uncertainty through forced incompleteness. Effect strongest for resource-constrained firms.',
            ha='center', fontsize=10, fontweight='bold')

    plt.tight_layout()
    return fig

# ============================================================================
# MODEL 3: ESSAY 3 - GOVERNANCE RESPONSE
# ============================================================================

def create_essay3_model():
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')

    # Title
    ax.text(5, 9.5, 'Essay 3: Governance Response and Executive Turnover',
            fontsize=18, fontweight='bold', ha='center')
    ax.text(5, 9, 'Does Disclosure Timing Trigger Organizational Response?',
            fontsize=13, ha='center', style='italic', color='#555')

    # Timeline flow
    # Data Breach
    breach_box = FancyBboxPatch((0.3, 7.5), 1.4, 0.8,
                               boxstyle="round,pad=0.05",
                               edgecolor='black', facecolor=COLORS['start'], linewidth=2)
    ax.add_patch(breach_box)
    ax.text(1.0, 7.9, 'Data Breach\nOccurs', ha='center', va='center', fontweight='bold', fontsize=9)

    # Arrow
    ax.arrow(1.8, 7.9, 0.5, 0, head_width=0.12, head_length=0.12, fc='black', ec='black')

    # Mandatory Disclosure
    disclosure_box = FancyBboxPatch((2.4, 7.5), 1.5, 0.8,
                                   boxstyle="round,pad=0.05",
                                   edgecolor='black', facecolor=COLORS['process'], linewidth=2)
    ax.add_patch(disclosure_box)
    ax.text(3.15, 7.9, 'Mandatory\nDisclosure\n(FCC: 7-day)', ha='center', va='center', fontweight='bold', fontsize=9)

    # Arrow
    ax.arrow(4.0, 7.9, 0.5, 0, head_width=0.12, head_length=0.12, fc='black', ec='black')

    # Stakeholder Activation
    stakeholder_box = FancyBboxPatch((4.6, 7.5), 1.5, 0.8,
                                    boxstyle="round,pad=0.05",
                                    edgecolor='black', facecolor=COLORS['process'], linewidth=2)
    ax.add_patch(stakeholder_box)
    ax.text(5.35, 7.9, 'Stakeholder\nActivation\n(Investors, Board)', ha='center', va='center', fontweight='bold', fontsize=9)

    # Arrow
    ax.arrow(6.2, 7.9, 0.5, 0, head_width=0.12, head_length=0.12, fc='black', ec='black')

    # Governance Response
    response_box = FancyBboxPatch((6.8, 7.5), 1.5, 0.8,
                                 boxstyle="round,pad=0.05",
                                 edgecolor='black', facecolor=COLORS['positive'], linewidth=2)
    ax.add_patch(response_box)
    ax.text(7.55, 7.9, 'Executive\nTurnover\n+5.3pp***', ha='center', va='center', fontweight='bold', fontsize=9, color='white')

    # Temporal Decay
    ax.text(5, 6.8, 'Temporal Dynamics (Transient Effect)', fontsize=12, fontweight='bold', ha='center')

    # Timeline showing decay
    timeline_y = 6.2
    time_points = [
        ('Day 0', 'Breach'),
        ('Day 7', 'FCC Disclosure'),
        ('Day 30', 'Peak Turnover\n46.4%', COLORS['positive']),
        ('Day 90', 'Effect Decay\n(p > 0.05)'),
        ('Day 180', 'Effect Gone\n(No turnover increase)')
    ]

    x_positions = np.linspace(0.5, 9.5, len(time_points))
    for i, (x, (time, label, *color)) in enumerate(zip(x_positions, time_points)):
        color = color[0] if color else '#CCCCCC'
        circle = plt.Circle((x, timeline_y), 0.2, color=color, ec='black', linewidth=1.5, zorder=3)
        ax.add_patch(circle)
        ax.text(x, timeline_y - 0.6, label, ha='center', fontsize=9)
        if i < len(time_points) - 1:
            ax.plot([x + 0.2, x_positions[i+1] - 0.2], [timeline_y, timeline_y],
                   'k-', linewidth=1, zorder=1)

    # Key findings
    ax.text(5, 4.2, 'Key Findings:', fontsize=11, fontweight='bold')

    findings = [
        'Baseline executive turnover (all breaches): 46.4% within 30 days',
        'FCC effect: +5.3 percentage points** (highly significant)',
        'Effect peaks at 30 days post-disclosure',
        'Effect decays rapidly - NO longer significant by 90 days',
        'Interpretation: Crisis response, not embedded governance reform',
        'Market discipline dominates regulatory discipline'
    ]

    y_pos = 3.8
    for finding in findings:
        ax.text(0.5, y_pos, f'• {finding}', fontsize=9)
        y_pos -= 0.35

    # Conclusion
    conclusion = FancyBboxPatch((0.3, 0.2), 9.4, 0.8,
                               boxstyle="round,pad=0.05",
                               edgecolor=COLORS['positive'], facecolor='#E6F9E6', linewidth=2)
    ax.add_patch(conclusion)
    ax.text(5, 0.75, 'Mandatory disclosure activates stakeholder pressure leading to executive turnover,',
            ha='center', fontsize=10, fontweight='bold')
    ax.text(5, 0.35, 'but this effect is transient - suggesting urgency of response rather than systematic governance reform',
            ha='center', fontsize=10, fontweight='bold')

    plt.tight_layout()
    return fig

# ============================================================================
# MODEL 4: DISSERTATION FRAMEWORK - Three Parallel Mechanisms
# ============================================================================

def create_dissertation_framework():
    fig, ax = plt.subplots(figsize=(16, 10))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')

    # Title
    ax.text(5, 9.6, 'Dissertation Framework: Three Parallel Mechanisms of Disclosure Regulation',
            fontsize=18, fontweight='bold', ha='center')
    ax.text(5, 9.1, 'Natural Experiment: FCC Rule 37.3 (2007) Shock - 1,054 Breaches, 2006-2025',
            fontsize=12, ha='center', style='italic', color='#555')

    # Central stimulus
    stimulus_box = FancyBboxPatch((3.5, 7.8), 3, 0.8,
                                 boxstyle="round,pad=0.1",
                                 edgecolor='black', facecolor='#FFE6E6', linewidth=3)
    ax.add_patch(stimulus_box)
    ax.text(5, 8.2, 'FCC Rule 37.3 (2007)\n7-Day Disclosure Mandate',
            ha='center', va='center', fontweight='bold', fontsize=11)

    # Three branching pathways
    # Arrows branching out
    ax.arrow(3.8, 7.8, -1.3, -1.5, head_width=0.15, head_length=0.15, fc='black', ec='black', linewidth=2)
    ax.arrow(5, 7.8, 0, -1.7, head_width=0.15, head_length=0.15, fc='black', ec='black', linewidth=2)
    ax.arrow(6.2, 7.8, 1.3, -1.5, head_width=0.15, head_length=0.15, fc='black', ec='black', linewidth=2)

    # ============ PATHWAY 1: ESSAY 1 - VALUATION ============
    essay1_header = FancyBboxPatch((0.2, 5.8), 2.2, 0.5,
                                  boxstyle="round,pad=0.05",
                                  edgecolor='black', facecolor=COLORS['null'], linewidth=2)
    ax.add_patch(essay1_header)
    ax.text(1.3, 6.05, 'Essay 1: Market Valuation', ha='center', va='center', fontweight='bold', fontsize=10)

    essay1_items = [
        'Mechanism: Timing Signal',
        'DV: CAR-30d (Stock Returns)',
        'Finding: Timing Effect = 0',
        'H1 Null Result Supported',
        'FCC Effect = -2.20%**',
        '(Regulation matters, not speed)',
        'Robustness: 25+ specifications'
    ]

    y = 5.5
    for item in essay1_items:
        ax.text(1.3, y, item, ha='center', fontsize=8)
        y -= 0.3

    result1_box = FancyBboxPatch((0.3, 2.3), 2, 0.5,
                                boxstyle="round,pad=0.05",
                                edgecolor='black', facecolor=COLORS['null'], linewidth=2)
    ax.add_patch(result1_box)
    ax.text(1.3, 2.6, 'Timing Irrelevant\nfor Valuation', ha='center', va='center', fontweight='bold', fontsize=9)

    # ============ PATHWAY 2: ESSAY 2 - VOLATILITY ============
    essay2_header = FancyBboxPatch((3.9, 5.8), 2.2, 0.5,
                                  boxstyle="round,pad=0.05",
                                  edgecolor='black', facecolor=COLORS['negative'], linewidth=2)
    ax.add_patch(essay2_header)
    ax.text(5, 6.05, 'Essay 2: Information Asymmetry', ha='center', va='center', fontweight='bold', fontsize=10, color='white')

    essay2_items = [
        'Mechanism: Capacity Constraint',
        'DV: Volatility Change (%)',
        'Finding: FCC = +1.83%**',
        '(Opposite of intent)',
        'Firm-Size Heterogeneity:',
        'Q1: +7.31%*** | Q4: -3.39%**',
        'Other mechanisms NOT sig'
    ]

    y = 5.5
    for item in essay2_items:
        ax.text(5, y, item, ha='center', fontsize=8)
        y -= 0.3

    result2_box = FancyBboxPatch((3.8, 2.3), 2.4, 0.5,
                                boxstyle="round,pad=0.05",
                                edgecolor='black', facecolor=COLORS['negative'], linewidth=2)
    ax.add_patch(result2_box)
    ax.text(5, 2.6, 'Timing Increases\nUncertainty (Small Firms)', ha='center', va='center', fontweight='bold', fontsize=9, color='white')

    # ============ PATHWAY 3: ESSAY 3 - GOVERNANCE ============
    essay3_header = FancyBboxPatch((7.6, 5.8), 2.2, 0.5,
                                  boxstyle="round,pad=0.05",
                                  edgecolor='black', facecolor=COLORS['positive'], linewidth=2)
    ax.add_patch(essay3_header)
    ax.text(8.7, 6.05, 'Essay 3: Governance Response', ha='center', va='center', fontweight='bold', fontsize=10, color='white')

    essay3_items = [
        'Mechanism: Stakeholder Activ',
        'DV: Executive Turnover',
        'Finding: FCC = +5.3pp**',
        '(Significant effect)',
        'Peak at 30 days',
        'Decays by 90 days',
        'Transient response'
    ]

    y = 5.5
    for item in essay3_items:
        ax.text(8.7, y, item, ha='center', fontsize=8)
        y -= 0.3

    result3_box = FancyBboxPatch((7.6, 2.3), 2.2, 0.5,
                                boxstyle="round,pad=0.05",
                                edgecolor='black', facecolor=COLORS['positive'], linewidth=2)
    ax.add_patch(result3_box)
    ax.text(8.7, 2.6, 'Timing Activates\nGovernance Response', ha='center', va='center', fontweight='bold', fontsize=9, color='white')

    # Central conclusion
    conclusion_y = 1.8
    ax.text(5, conclusion_y, 'Central Finding: Disclosure Regulation Works Through THREE INDEPENDENT MECHANISMS',
            fontsize=11, fontweight='bold', ha='center')
    ax.text(5, conclusion_y - 0.35, 'Each with different outcomes, dynamics, and policy implications',
            fontsize=10, ha='center', style='italic')

    # Theory box
    theory_box = FancyBboxPatch((0.5, 0.2), 9, 0.9,
                               boxstyle="round,pad=0.05",
                               edgecolor=COLORS['theory'], facecolor='#F0E6FF', linewidth=2)
    ax.add_patch(theory_box)
    ax.text(5, 0.85, 'Theoretical Integration: Akerlof (1970) - Adverse Selection | Spence (1973) - Signaling | Myers & Majluf (1984) - Timing Signals',
            fontsize=9, ha='center', fontweight='bold')
    ax.text(5, 0.5, 'Diamond & Verrecchia (1991) - Forced Disclosure Paradox | Tushman & Nadler (1978) - Information Processing Capacity Constraints',
            fontsize=9, ha='center', fontweight='bold')

    plt.tight_layout()
    return fig

# ============================================================================
# GENERATE AND SAVE ALL MODELS
# ============================================================================

if __name__ == '__main__':
    print("Creating updated conceptual models...")

    # Essay 1
    print("  [1/4] Essay 1: Market Reactions...")
    fig1 = create_essay1_model()
    fig1.savefig('Conceptual_Model_1_Essay1_MarketReactions_UPDATED.png', dpi=300, bbox_inches='tight')
    print("       Saved: Conceptual_Model_1_Essay1_MarketReactions_UPDATED.png")
    plt.close(fig1)

    # Essay 2
    print("  [2/4] Essay 2: Information Asymmetry with Firm-Size Heterogeneity...")
    fig2 = create_essay2_model()
    fig2.savefig('Conceptual_Model_2_Essay2_InformationAsymmetry_UPDATED.png', dpi=300, bbox_inches='tight')
    print("       Saved: Conceptual_Model_2_Essay2_InformationAsymmetry_UPDATED.png")
    plt.close(fig2)

    # Essay 3
    print("  [3/4] Essay 3: Governance Response...")
    fig3 = create_essay3_model()
    fig3.savefig('Conceptual_Model_3_Essay3_GovernanceResponse_UPDATED.png', dpi=300, bbox_inches='tight')
    print("       Saved: Conceptual_Model_3_Essay3_GovernanceResponse_UPDATED.png")
    plt.close(fig3)

    # Dissertation Framework
    print("  [4/4] Dissertation Framework: Three Parallel Mechanisms...")
    fig4 = create_dissertation_framework()
    fig4.savefig('Conceptual_Model_4_DissertationFramework_UPDATED.png', dpi=300, bbox_inches='tight')
    print("       Saved: Conceptual_Model_4_DissertationFramework_UPDATED.png")
    plt.close(fig4)

    print("\n" + "="*80)
    print("SUCCESS: All 4 updated conceptual models generated")
    print("="*80)
    print("\nNew Files Created:")
    print("  1. Conceptual_Model_1_Essay1_MarketReactions_UPDATED.png")
    print("  2. Conceptual_Model_2_Essay2_InformationAsymmetry_UPDATED.png")
    print("  3. Conceptual_Model_3_Essay3_GovernanceResponse_UPDATED.png")
    print("  4. Conceptual_Model_4_DissertationFramework_UPDATED.png")
    print("\nKey Enhancements:")
    print("  [OK] Essay 2 now includes firm-size heterogeneity (Q1: +7.31%, Q4: -3.39%)")
    print("  [OK] All models include updated statistics and findings")
    print("  [OK] Framework model shows three independent mechanisms")
    print("  [OK] High-quality PNG format (300 DPI) for presentations")
