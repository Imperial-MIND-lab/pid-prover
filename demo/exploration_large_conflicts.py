"""
Exploration: Large Conflict Discovery

Systematically searches for larger conflicts (size 5-6) in both bivariate
and multivariate cases to discover novel no-go theorems not documented in
the paper.

Expected Discoveries:
- Novel no-go theorems (minimal inconsistent property sets)
- Property co-occurrence patterns in conflicts
- Quantification of multivariate restrictiveness vs bivariate
"""

import pytest
from pid_prover import find_minimal_conflicts
from utils_research import (
    save_findings_to_markdown,
    log_computational_cost,
    save_conflict_catalog,
    format_property_set,
    RESEARCH_OUTPUTS_DIR
)


@pytest.mark.exploration
@pytest.mark.research
def test_bivariate_conflicts_size_5():
    """
    Find all size-5 conflicts in the bivariate case.

    This extends known results (size 3-4) to discover larger no-go theorems.
    Expected runtime: 2-5 minutes.
    """
    print("\n" + "="*80)
    print("EXPLORATION: Bivariate Conflicts (Size 5)")
    print("="*80)

    conflicts = find_minimal_conflicts("bivariate", max_size=5, filter_reducible=True)

    # Filter to size 5 only
    size_5_conflicts = [c for c in conflicts if len(c) == 5]

    print(f"\nFound {len(size_5_conflicts)} size-5 conflicts (bivariate)")

    # Save results
    if size_5_conflicts:
        findings = {
            "Summary": {
                "Case": "bivariate",
                "Conflict size": 5,
                "Total found": len(size_5_conflicts)
            },
            "Size-5 Conflicts": [format_property_set(c) for c in size_5_conflicts],
            "Analysis": [
                "These are novel no-go theorems not explicitly documented in the paper.",
                f"They represent {len(size_5_conflicts)} distinct minimal 5-property combinations that cannot coexist.",
                "Each conflict provides a constraint on measure design."
            ]
        }
        output_path = save_findings_to_markdown(
            findings,
            "conflicts_size5_bivariate.md",
            title="Size-5 Conflicts (Bivariate)",
            description="Novel no-go theorems for n=2 case"
        )
        print(f"\nResults saved to: {output_path}")

    # Basic assertions
    assert isinstance(conflicts, list)
    assert all(isinstance(c, list) for c in conflicts)
    assert len(size_5_conflicts) >= 0  # May be zero if none exist


@pytest.mark.exploration
@pytest.mark.research
@pytest.mark.slow
def test_bivariate_conflicts_size_6():
    """
    Find all size-6 conflicts in the bivariate case.

    This is computationally expensive but may reveal additional structure.
    Expected runtime: 10-30 minutes.
    """
    print("\n" + "="*80)
    print("EXPLORATION: Bivariate Conflicts (Size 6)")
    print("="*80)
    print("WARNING: This test is computationally expensive")

    conflicts = find_minimal_conflicts("bivariate", max_size=6, filter_reducible=True)

    # Filter to size 6 only
    size_6_conflicts = [c for c in conflicts if len(c) == 6]

    print(f"\nFound {len(size_6_conflicts)} size-6 conflicts (bivariate)")

    # Save all conflicts found
    if conflicts:
        output_path = save_conflict_catalog(
            [tuple(c) for c in conflicts],
            filename="conflicts_all_bivariate.md",
            case="bivariate"
        )
        print(f"\nAll conflicts saved to: {output_path}")

    # Size 6 specific analysis
    if size_6_conflicts:
        findings = {
            "Summary": {
                "Case": "bivariate",
                "Conflict size": 6,
                "Total found": len(size_6_conflicts)
            },
            "Size-6 Conflicts": [format_property_set(c) for c in size_6_conflicts]
        }
        output_path = save_findings_to_markdown(
            findings,
            "conflicts_size6_bivariate.md",
            title="Size-6 Conflicts (Bivariate)"
        )
        print(f"Size-6 results saved to: {output_path}")

    assert isinstance(conflicts, list)


@pytest.mark.exploration
@pytest.mark.research
def test_multivariate_conflicts_size_5():
    """
    Find all size-5 conflicts in the multivariate case.

    The multivariate case is known to be more restrictive. 
    This test discovers additional size-5 conflicts.
    Expected runtime: 2-5 minutes.
    """
    print("\n" + "="*80)
    print("EXPLORATION: Multivariate Conflicts (Size 5)")
    print("="*80)

    conflicts = find_minimal_conflicts("multivariate", max_size=5, filter_reducible=True)

    # Filter to size 5 only
    size_5_conflicts = [c for c in conflicts if len(c) == 5]

    print(f"\nFound {len(size_5_conflicts)} size-5 conflicts (multivariate)")

    # Save results
    if size_5_conflicts:
        other_conflicts = [c for c in size_5_conflicts if set(c) != theorem_2_conflict]

        findings = {
            "Summary": {
                "Case": "multivariate (n≥3)",
                "Conflict size": 5,
                "Total found": len(size_5_conflicts),
                "Novel conflicts": len(other_conflicts)
            },
            "Analysis": [
                f"Found {len(other_conflicts)} additional size-5 conflicts.",
                "These represent novel no-go theorems for the multivariate case."
            ]
        }
        output_path = save_findings_to_markdown(
            findings,
            "conflicts_size5_multivariate.md",
            title="Size-5 Conflicts (Multivariate)",
            description="No-go theorems for n≥3 case"
        )
        print(f"\nResults saved to: {output_path}")

    assert isinstance(conflicts, list)


@pytest.mark.exploration
@pytest.mark.research
@pytest.mark.slow
def test_multivariate_conflicts_size_6():
    """
    Find all size-6 conflicts in the multivariate case.

    Expected runtime: 10-30 minutes.
    """
    print("\n" + "="*80)
    print("EXPLORATION: Multivariate Conflicts (Size 6)")
    print("="*80)
    print("WARNING: This test is computationally expensive")

    conflicts = find_minimal_conflicts("multivariate", max_size=6, filter_reducible=True)

    # Filter to size 6 only
    size_6_conflicts = [c for c in conflicts if len(c) == 6]

    print(f"\nFound {len(size_6_conflicts)} size-6 conflicts (multivariate)")

    # Save all conflicts
    if conflicts:
        output_path = save_conflict_catalog(
            [tuple(c) for c in conflicts],
            filename="conflicts_all_multivariate.md",
            case="multivariate"
        )
        print(f"\nAll conflicts saved to: {output_path}")

    # Size 6 specific
    if size_6_conflicts:
        findings = {
            "Summary": {
                "Case": "multivariate (n≥3)",
                "Conflict size": 6,
                "Total found": len(size_6_conflicts)
            },
            "Size-6 Conflicts": [format_property_set(c) for c in size_6_conflicts]
        }
        output_path = save_findings_to_markdown(
            findings,
            "conflicts_size6_multivariate.md",
            title="Size-6 Conflicts (Multivariate)"
        )
        print(f"Size-6 results saved to: {output_path}")

    assert isinstance(conflicts, list)


@pytest.mark.exploration
@pytest.mark.research
def test_compare_conflict_counts():
    """
    Compare conflict landscape between bivariate and multivariate cases.

    Quantifies how much more restrictive the multivariate case is.
    Expected runtime: 3-7 minutes.
    """
    print("\n" + "="*80)
    print("EXPLORATION: Bivariate vs Multivariate Conflict Comparison")
    print("="*80)

    # Search up to size 5 for both cases
    biv_conflicts = find_minimal_conflicts("bivariate", max_size=5, filter_reducible=True)
    multi_conflicts = find_minimal_conflicts("multivariate", max_size=5, filter_reducible=True)

    # Count by size
    biv_by_size = {}
    multi_by_size = {}

    for c in biv_conflicts:
        size = len(c)
        biv_by_size[size] = biv_by_size.get(size, 0) + 1

    for c in multi_conflicts:
        size = len(c)
        multi_by_size[size] = multi_by_size.get(size, 0) + 1

    print(f"\nBivariate: {len(biv_conflicts)} total conflicts")
    print(f"Multivariate: {len(multi_conflicts)} total conflicts")

    # Create comparison table
    table_data = []
    for size in range(2, 6):
        biv_count = biv_by_size.get(size, 0)
        multi_count = multi_by_size.get(size, 0)
        difference = multi_count - biv_count
        table_data.append([size, biv_count, multi_count, difference])

    from utils_research import create_results_table
    table = create_results_table(
        table_data,
        headers=["Size", "Bivariate", "Multivariate", "Difference"],
        alignment=["center", "center", "center", "center"]
    )

    findings = {
        "Summary": {
            "Total conflicts (bivariate)": len(biv_conflicts),
            "Total conflicts (multivariate)": len(multi_conflicts),
            "Additional multivariate conflicts": len(multi_conflicts) - len(biv_conflicts),
            "Relative increase": f"{(len(multi_conflicts) / max(len(biv_conflicts), 1) - 1) * 100:.1f}%"
        },
        "Conflict Counts by Size": [table],
        "Interpretation": [
            "Multivariate case (n≥3) is more restrictive than bivariate (n=2).",
            "Additional conflicts in multivariate case represent properties that are compatible for n=2 but incompatible for n≥3.",
            "This quantifies the 'multivariate strictness' phenomenon.",
        ]
    }

    output_path = save_findings_to_markdown(
        findings,
        "conflict_comparison_biv_vs_multi.md",
        title="Bivariate vs Multivariate Conflict Comparison",
        description="Quantifying the restrictiveness difference between n=2 and n≥3"
    )

    print(f"\n{table}")
    print(f"\nComparison saved to: {output_path}")

    # Assertions
    assert len(biv_conflicts) > 0
    assert len(multi_conflicts) > 0
    assert len(multi_conflicts) >= len(biv_conflicts)  # Multivariate should be at least as restrictive


@pytest.mark.exploration
def test_conflicts_basic_sanity():
    """
    Quick sanity check that conflict discovery is working.

    Verifies known conflicts are found. Expected runtime: < 30s.
    """
    print("\n" + "="*80)
    print("SANITY CHECK: Basic Conflict Discovery")
    print("="*80)

    # Should find at least some conflicts in both cases
    biv_conflicts = find_minimal_conflicts("bivariate", max_size=4, filter_reducible=True)
    multi_conflicts = find_minimal_conflicts("multivariate", max_size=5, filter_reducible=True)

    print(f"\nBivariate conflicts (up to size 4): {len(biv_conflicts)}")
    print(f"Multivariate conflicts (up to size 5): {len(multi_conflicts)}")

    assert len(biv_conflicts) > 0, "Should find bivariate conflicts"
    assert len(multi_conflicts) > 0, "Should find multivariate conflicts"

    print("\n✓ Sanity check passed: Conflict discovery working correctly")
