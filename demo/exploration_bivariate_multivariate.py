"""
Exploration: Bivariate vs Multivariate Systematic Comparison

Comprehensive comparison of the logical landscapes for n=2 vs n≥3:
- Total conflicts in each case
- Total implications in each case
- Case-exclusive theorems
- Property strength rankings
- Multivariate strictness quantification

Expected Output: Summary table and analysis for paper.
"""

import pytest
from typing import Dict, List
import z3
from pid_prover import (
    find_minimal_conflicts,
    find_minimal_implications,
    get_pid_solver
)
from pid_prover.solver.axioms import P, prop_names
from utils_research import (
    save_findings_to_markdown,
    create_results_table,
    log_computational_cost
)


@pytest.mark.exploration
@pytest.mark.research
@log_computational_cost
def test_count_conflicts_by_case():
    """
    Count total conflicts in bivariate vs multivariate cases.

    Searches up to size 5 for comprehensive comparison.
    """
    print("\n" + "="*80)
    print("EXPLORATION: Conflict Counts by Case")
    print("="*80)

    print("\nSearching bivariate conflicts (up to size 5)...")
    biv_conflicts = find_minimal_conflicts("bivariate", max_size=5, filter_reducible=True)

    print("\nSearching multivariate conflicts (up to size 5)...")
    multi_conflicts = find_minimal_conflicts("multivariate", max_size=5, filter_reducible=True)

    print(f"\n--- Results ---")
    print(f"Bivariate conflicts: {len(biv_conflicts)}")
    print(f"Multivariate conflicts: {len(multi_conflicts)}")
    print(f"Additional multivariate conflicts: {len(multi_conflicts) - len(biv_conflicts)}")

    # Breakdown by size
    biv_by_size = {}
    multi_by_size = {}

    for c in biv_conflicts:
        size = len(c)
        biv_by_size[size] = biv_by_size.get(size, 0) + 1

    for c in multi_conflicts:
        size = len(c)
        multi_by_size[size] = multi_by_size.get(size, 0) + 1

    print("\nBreakdown by size:")
    for size in range(2, 6):
        biv_count = biv_by_size.get(size, 0)
        multi_count = multi_by_size.get(size, 0)
        print(f"  Size {size}: {biv_count} (biv) vs {multi_count} (multi)")

    # Create table
    table_rows = []
    for size in range(2, 6):
        biv_count = biv_by_size.get(size, 0)
        multi_count = multi_by_size.get(size, 0)
        difference = multi_count - biv_count
        table_rows.append([size, biv_count, multi_count, difference])

    table = create_results_table(
        table_rows,
        headers=["Conflict Size", "Bivariate", "Multivariate", "Difference"],
        alignment=["center", "center", "center", "center"]
    )

    findings = {
        "Summary": {
            "Bivariate total": len(biv_conflicts),
            "Multivariate total": len(multi_conflicts),
            "Difference": len(multi_conflicts) - len(biv_conflicts),
            "Relative increase": f"{((len(multi_conflicts) / max(len(biv_conflicts), 1)) - 1) * 100:.1f}%"
        },
        "Conflicts by Size": [table],
        "Interpretation": [
            f"Multivariate case has {len(multi_conflicts) - len(biv_conflicts)} more conflicts than bivariate.",
            "This quantifies the 'multivariate strictness' phenomenon.",
            "Each additional conflict represents property combinations that work for n=2 but fail for n≥3.",
            "Design space is more restricted for n≥3."
        ]
    }

    output_path = save_findings_to_markdown(
        findings,
        "case_comparison_conflicts.md",
        title="Conflict Comparison: Bivariate vs Multivariate",
        description="Quantifying restrictiveness differences"
    )

    print(f"\nResults saved to: {output_path}")

    assert len(multi_conflicts) >= len(biv_conflicts), "Multivariate should be at least as restrictive"


@pytest.mark.exploration
@pytest.mark.research
def test_count_implications_by_case():
    """
    Count total implications (2-premise) in each case.
    """
    print("\n" + "="*80)
    print("EXPLORATION: Implication Counts by Case")
    print("="*80)

    print("\nSearching bivariate implications...")
    biv_implications = find_minimal_implications("bivariate", premise_size=2)

    print("\nSearching multivariate implications...")
    multi_implications = find_minimal_implications("multivariate", premise_size=2)

    print(f"\n--- Results ---")
    print(f"Bivariate implications: {len(biv_implications)}")
    print(f"Multivariate implications: {len(multi_implications)}")

    findings = {
        "Summary": {
            "Bivariate total": len(biv_implications),
            "Multivariate total": len(multi_implications),
            "Difference": len(multi_implications) - len(biv_implications)
        },
        "Interpretation": [
            f"Multivariate case has {abs(len(multi_implications) - len(biv_implications))} {'more' if len(multi_implications) > len(biv_implications) else 'fewer'} implications.",
            "More implications means more property dependencies.",
            "This affects measure design flexibility."
        ]
    }

    output_path = save_findings_to_markdown(
        findings,
        "case_comparison_implications.md",
        title="Implication Comparison: Bivariate vs Multivariate"
    )

    print(f"\nResults saved to: {output_path}")


@pytest.mark.exploration
@pytest.mark.research
def test_case_exclusive_theorems():
    """
    Identify theorems that hold in one case but not the other.

    Bivariate-only: Theorem 7
    Multivariate-only: Theorem 2
    """
    print("\n" + "="*80)
    print("EXPLORATION: Case-Exclusive Theorems")
    print("="*80)

    findings = {
        "Bivariate-Only Theorems": [
            "Theorem 7 (BP--TE-SE): BP ⇒ SE ∧ TE",
            "Only holds for n=2",
            "Properties: Blackwell Property, Target Equality, Subset Equality"
        ],
        "Multivariate-Only Theorems": [
            "Theorem 2 (noIIDLyu): ¬(S0 ∧ M0 ∧ SR ∧ EI ∧ IID)",
            "Only holds for n≥3",
            "Properties: Weak Symmetry, Weak Monotonicity, Self-Redundancy, Equivalence Invariance, Independent Identity",
            "This is the conflict causing 5 measure failures"
        ],
        "Universal Theorems": [
            "Theorems 1, 3, 4, 5, 6, 9, 10, 11, 12 apply to both cases",
            "These represent core structural constraints"
        ],
        "Case-Exclusive Property Combinations": [
            "Test if there are property sets consistent for n=2 but not n≥3..."
        ]
    }

    # Test some combinations
    test_sets = [
        ['SR', 'S0', 'M0', 'EI', 'IID'],  # Theorem 2 - should be biv only
        ['BP', 'TE', 'SE'],                # Related to Theorem 7
    ]

    solver_biv = get_pid_solver("bivariate")
    solver_multi = get_pid_solver("multivariate")

    print("\nTesting specific property sets:")
    for props in test_sets:
        # Check bivariate
        solver_biv.push()
        solver_biv.add(z3.And([P[p] for p in props]))
        biv_result = solver_biv.check()
        solver_biv.pop()

        # Check multivariate
        solver_multi.push()
        solver_multi.add(z3.And([P[p] for p in props]))
        multi_result = solver_multi.check()
        solver_multi.pop()

        props_str = '{' + ', '.join(props) + '}'
        print(f"  {props_str}:")
        print(f"    Bivariate: {biv_result}")
        print(f"    Multivariate: {multi_result}")

        if biv_result != multi_result:
            finding_key = f"Exclusive Set: {props_str}"
            if biv_result == z3.sat and multi_result == z3.unsat:
                findings[finding_key] = ["Consistent for n=2, INCONSISTENT for n≥3"]
            elif biv_result == z3.unsat and multi_result == z3.sat:
                findings[finding_key] = ["INCONSISTENT for n=2, consistent for n≥3"]

    output_path = save_findings_to_markdown(
        findings,
        "case_exclusive_theorems.md",
        title="Case-Exclusive Theorems",
        description="Theorems that hold in only one case"
    )

    print(f"\nResults saved to: {output_path}")


@pytest.mark.exploration
@pytest.mark.research
def test_property_strength_ranking_comparison():
    """
    Compare property strength rankings between cases.

    Do weaker/stronger properties change between n=2 and n≥3?
    """
    print("\n" + "="*80)
    print("EXPLORATION: Property Strength Ranking Comparison")
    print("="*80)

    # Count implications for each property in each case
    biv_strength = {}
    multi_strength = {}

    solver_biv = get_pid_solver("bivariate")
    solver_multi = get_pid_solver("multivariate")

    print("\nComputing property strength (# of properties each implies)...")

    for prop in prop_names:
        # Bivariate
        biv_count = 0
        for other in prop_names:
            if prop != other:
                solver_biv.push()
                solver_biv.add(P[prop])
                solver_biv.add(z3.Not(P[other]))
                if solver_biv.check() == z3.unsat:
                    biv_count += 1
                solver_biv.pop()

        biv_strength[prop] = biv_count

        # Multivariate
        multi_count = 0
        for other in prop_names:
            if prop != other:
                solver_multi.push()
                solver_multi.add(P[prop])
                solver_multi.add(z3.Not(P[other]))
                if solver_multi.check() == z3.unsat:
                    multi_count += 1
                solver_multi.pop()

        multi_strength[prop] = multi_count

        print(f"  {prop}: {biv_count} (biv) vs {multi_count} (multi)")

    # Compare rankings
    biv_ranking = sorted(prop_names, key=lambda p: biv_strength[p])
    multi_ranking = sorted(prop_names, key=lambda p: multi_strength[p])

    print("\nWeakest to strongest (bivariate):")
    print(f"  {', '.join(biv_ranking[:5])} ... {', '.join(biv_ranking[-5:])}")

    print("\nWeakest to strongest (multivariate):")
    print(f"  {', '.join(multi_ranking[:5])} ... {', '.join(multi_ranking[-5:])}")

    # Find properties with largest ranking changes
    rank_changes = {}
    for prop in prop_names:
        biv_rank = biv_ranking.index(prop)
        multi_rank = multi_ranking.index(prop)
        rank_changes[prop] = multi_rank - biv_rank

    print("\nLargest ranking changes:")
    for prop, change in sorted(rank_changes.items(), key=lambda x: abs(x[1]), reverse=True)[:5]:
        direction = "stronger" if change > 0 else "weaker"
        print(f"  {prop}: {abs(change)} positions {direction} in multivariate")

    # Create comparison table
    table_rows = []
    for prop in prop_names:
        biv_str_val = biv_strength[prop]
        multi_str_val = multi_strength[prop]
        change = multi_str_val - biv_str_val
        table_rows.append([prop, biv_str_val, multi_str_val, change])

    # Sort by bivariate strength
    table_rows.sort(key=lambda x: x[1])

    table = create_results_table(
        table_rows,
        headers=["Property", "Biv Strength", "Multi Strength", "Change"],
        alignment=["left", "center", "center", "center"]
    )

    findings = {
        "Summary": {
            "Properties analyzed": len(prop_names),
            "Largest strength increase": max(multi_strength[p] - biv_strength[p] for p in prop_names),
            "Largest strength decrease": min(multi_strength[p] - biv_strength[p] for p in prop_names)
        },
        "Strength Comparison Table": [table],
        "Weakest Properties (Bivariate)": biv_ranking[:5],
        "Strongest Properties (Bivariate)": biv_ranking[-5:],
        "Weakest Properties (Multivariate)": multi_ranking[:5],
        "Strongest Properties (Multivariate)": multi_ranking[-5:],
        "Interpretation": [
            "Property strength = number of other properties it implies.",
            "Stronger properties are more restrictive on measure design.",
            "Changes in strength reveal how property relationships shift with n."
        ]
    }

    output_path = save_findings_to_markdown(
        findings,
        "property_strength_comparison.md",
        title="Property Strength Comparison: Bivariate vs Multivariate",
        description="How property strength changes with n"
    )

    print(f"\nResults saved to: {output_path}")


@pytest.mark.exploration
@pytest.mark.research
def test_multivariate_strictness():
    """
    Quantify how much more restrictive the multivariate case is.

    Metrics:
    - Conflict ratio
    - Implication density
    - Average maximal set size
    """
    print("\n" + "="*80)
    print("EXPLORATION: Multivariate Strictness Quantification")
    print("="*80)

    # Count conflicts (limited search)
    biv_conflicts = find_minimal_conflicts("bivariate", max_size=5, filter_reducible=True)
    multi_conflicts = find_minimal_conflicts("multivariate", max_size=5, filter_reducible=True)

    conflict_ratio = len(multi_conflicts) / max(len(biv_conflicts), 1)

    print(f"\nConflict ratio (multi/biv): {conflict_ratio:.2f}x")

    # Count maximal compatible sets
    from pid_prover import find_maximal_compatible_sets

    biv_maximal = find_maximal_compatible_sets("bivariate", min_size=8)
    multi_maximal = find_maximal_compatible_sets("multivariate", min_size=8)

    biv_avg_size = sum(len(s) for s in biv_maximal) / max(len(biv_maximal), 1)
    multi_avg_size = sum(len(s) for s in multi_maximal) / max(len(multi_maximal), 1)

    print(f"\nAverage maximal set size:")
    print(f"  Bivariate: {biv_avg_size:.1f}")
    print(f"  Multivariate: {multi_avg_size:.1f}")

    size_reduction = ((biv_avg_size - multi_avg_size) / biv_avg_size) * 100 if biv_avg_size > 0 else 0

    # Compile metrics
    findings = {
        "Strictness Metrics": {
            "Conflict ratio (multi/biv)": f"{conflict_ratio:.2f}x",
            "Bivariate conflicts": len(biv_conflicts),
            "Multivariate conflicts": len(multi_conflicts),
            "Additional multivariate conflicts": len(multi_conflicts) - len(biv_conflicts),
            "Avg maximal set size (biv)": f"{biv_avg_size:.1f}",
            "Avg maximal set size (multi)": f"{multi_avg_size:.1f}",
            "Size reduction": f"{size_reduction:.1f}%"
        },
        "Interpretation": [
            f"Multivariate case is {conflict_ratio:.2f}x more restrictive (by conflict count).",
            f"Maximal property sets are {size_reduction:.1f}% smaller on average for n≥3.",
            "This quantifies the design space contraction.",
            "Measure designers have fewer degrees of freedom for n≥3."
        ],
        "Implications for PID Research": [
            "Bivariate analysis may overestimate measure possibilities.",
            "Properties that seem compatible for n=2 may fail for n≥3.",
            "Thorough multivariate analysis is essential.",
            "This explains why some measures only work for n=2."
        ]
    }

    output_path = save_findings_to_markdown(
        findings,
        "multivariate_strictness.md",
        title="Multivariate Strictness Quantification",
        description="How much more restrictive is n≥3 compared to n=2?"
    )

    print(f"\nResults saved to: {output_path}")

    assert conflict_ratio >= 1.0, "Multivariate should have at least as many conflicts"
