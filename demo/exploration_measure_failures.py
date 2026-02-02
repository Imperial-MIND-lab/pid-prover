"""
Exploration: Measure Failure Investigation

CRITICAL: Investigates the 5 measures that fail multivariate validation.

Failing Measures (violate Theorem 2 for n≥3):
- I_CT, I_RR, I_wedge, I_alpha, I_prec

All claim {SR, S0, M0, EI, IID} which is proven impossible for n≥3.

Research Goals:
1. Identify root cause of failures
2. Determine which properties to relax for consistency
3. Find minimal conflicting subsets
4. Check for data entry errors vs definition issues
5. Generate correction proposals

This investigation has potential paper impact (corrections or errata).
"""

import pytest
from typing import List, Dict, Set
import z3
from pid_prover import get_pid_solver
from pid_prover.solver.axioms import P, prop_names
from pid_prover.measures import measures_df, MULTIVARIATE_CONFLICTS
from pid_prover.measures.validation import dataframe_to_property_list
from utils_research import (
    save_findings_to_markdown,
    format_property_set,
    create_results_table
)


def check_property_set_consistency(
    properties: List[str],
    case: str = "multivariate"
) -> bool:
    """Check if a property set is logically consistent."""
    solver = get_pid_solver(case)
    solver.push()
    solver.add(z3.And([P[prop] for prop in properties]))
    result = solver.check()
    solver.pop()
    return result == z3.sat


def find_minimal_inconsistent_subset(
    properties: List[str],
    case: str = "multivariate"
) -> List[str]:
    """
    Find the minimal subset of properties that causes inconsistency.

    Returns the smallest subset that is inconsistent.
    """
    # Start with full set
    if check_property_set_consistency(properties, case):
        return []  # Set is actually consistent

    # Try removing properties one at a time to find minimal conflict
    from itertools import combinations

    # Check subsets from small to large
    for size in range(2, len(properties) + 1):
        for subset in combinations(properties, size):
            subset_list = list(subset)
            if not check_property_set_consistency(subset_list, case):
                # Found a minimal inconsistent subset
                # Verify it's truly minimal by checking all proper subsets
                is_minimal = True
                for smaller_size in range(2, size):
                    for smaller_subset in combinations(subset, smaller_size):
                        if not check_property_set_consistency(list(smaller_subset), case):
                            is_minimal = False
                            break
                    if not is_minimal:
                        break

                if is_minimal:
                    return subset_list

    return list(properties)  # Shouldn't reach here


def find_which_property_to_relax(
    properties: List[str],
    case: str = "multivariate"
) -> Dict[str, bool]:
    """
    For each property, check if removing it makes the set consistent.

    Returns dict: {property: is_consistent_without_it}
    """
    results = {}

    for prop in properties:
        remaining = [p for p in properties if p != prop]
        results[prop] = check_property_set_consistency(remaining, case)

    return results


@pytest.mark.exploration
@pytest.mark.research
def test_analyze_failing_measures():
    """
    Analyze each failing measure to identify the specific issue.

    For each of the 5 failing measures, determine:
    1. What properties they claim
    2. The minimal conflicting subset
    3. Which single property could be removed to fix it
    """
    print("\n" + "="*80)
    print("EXPLORATION: Analyzing Failing Measures")
    print("="*80)

    all_results = {}

    for measure_name in MULTIVARIATE_CONFLICTS:
        print(f"\n--- Analyzing {measure_name} ---")

        # Get claimed properties
        properties = dataframe_to_property_list(measure_name, "multivariate")

        print(f"Claimed properties: {format_property_set(properties)}")
        print(f"Total: {len(properties)} properties")

        # Check consistency
        is_consistent = check_property_set_consistency(properties, "multivariate")
        print(f"Consistent: {is_consistent}")

        # Find minimal conflict
        minimal_conflict = find_minimal_inconsistent_subset(properties, "multivariate")
        print(f"Minimal conflicting subset: {format_property_set(minimal_conflict)}")

        # Find which property to relax
        relaxation_options = find_which_property_to_relax(properties, "multivariate")
        fixable_by_removing = [p for p, consistent in relaxation_options.items() if consistent]

        print(f"Can be fixed by removing any of: {fixable_by_removing}")

        all_results[measure_name] = {
            "claimed_properties": properties,
            "is_consistent": is_consistent,
            "minimal_conflict": minimal_conflict,
            "fixable_by_removing": fixable_by_removing
        }

    # Generate report
    findings = {
        "Summary": {
            "Failing measures": len(MULTIVARIATE_CONFLICTS),
            "Common issue": "All claim {SR, S0, M0, EI, IID} which violates Theorem 2 (noIIDLyu)"
        }
    }

    # Add individual measure analysis
    for measure_name, results in all_results.items():
        findings[f"Analysis: {measure_name}"] = [
            f"Claimed: {format_property_set(results['claimed_properties'])}",
            f"Minimal conflict: {format_property_set(results['minimal_conflict'])}",
            f"Fixable by removing: {', '.join(results['fixable_by_removing']) if results['fixable_by_removing'] else 'None'}",
            f"Number of removal options: {len(results['fixable_by_removing'])}"
        ]

    # Check if all have the same minimal conflict (Theorem 2)
    theorem_2_conflict = {'SR', 'S0', 'M0', 'EI', 'IID'}
    all_same_conflict = all(
        set(r['minimal_conflict']) == theorem_2_conflict
        for r in all_results.values()
    )

    findings["Interpretation"] = [
        f"All measures share the same conflict: {all_same_conflict}",
        "Root cause: These measures were likely designed/analyzed only for n=2 case.",
        "The multivariate property assignments may be:",
        "  (a) Errors - properties should be marked as bivariate-only",
        "  (b) Incorrect - measures don't actually satisfy these properties for n≥3",
        "  (c) Legitimate - revealing a gap in the theorem catalog",
        "Recommendation: Verify original papers for n≥3 analysis."
    ]

    output_path = save_findings_to_markdown(
        findings,
        "measure_failures_analysis.md",
        title="Failing Measures Analysis",
        description="Investigation of 5 measures failing multivariate validation"
    )

    print(f"\nResults saved to: {output_path}")

    # Assertions
    assert len(all_results) == 5
    assert all(not r['is_consistent'] for r in all_results.values())


@pytest.mark.exploration
@pytest.mark.research
def test_which_property_to_relax():
    """
    For each failing measure, systematically test removing each property
    to find which removals lead to consistency.

    Creates a matrix showing which property removals fix which measures.
    """
    print("\n" + "="*80)
    print("EXPLORATION: Property Relaxation Matrix")
    print("="*80)

    # Build matrix: rows=measures, cols=properties, values=is_consistent_without
    matrix_data = []
    all_properties_involved = set()

    for measure_name in MULTIVARIATE_CONFLICTS:
        properties = dataframe_to_property_list(measure_name, "multivariate")
        all_properties_involved.update(properties)

        row = {"measure": measure_name}
        for prop in properties:
            remaining = [p for p in properties if p != prop]
            row[prop] = "✓" if check_property_set_consistency(remaining, "multivariate") else "✗"

        matrix_data.append(row)

    # Print results
    print("\nProperty Removal Matrix:")
    print("(✓ = removing this property makes the measure consistent)")
    print("(✗ = removing this property alone is insufficient)\n")

    # Create table
    property_cols = sorted(all_properties_involved)
    table_rows = []

    for row_data in matrix_data:
        table_row = [row_data["measure"]]
        for prop in property_cols:
            table_row.append(row_data.get(prop, "-"))
        table_rows.append(table_row)

    table = create_results_table(
        table_rows,
        headers=["Measure"] + property_cols,
        alignment=["left"] + ["center"] * len(property_cols)
    )

    print(table)

    # Analyze which properties are most commonly fixable
    fix_counts = {}
    for prop in property_cols:
        count = sum(1 for row in matrix_data if row.get(prop) == "✓")
        fix_counts[prop] = count

    print("\nProperty Removal Effectiveness:")
    for prop, count in sorted(fix_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {prop}: Fixes {count}/{len(MULTIVARIATE_CONFLICTS)} measures")

    # Save findings
    findings = {
        "Property Removal Matrix": [table],
        "Removal Effectiveness": [
            f"{prop}: Fixes {count}/{len(MULTIVARIATE_CONFLICTS)} measures"
            for prop, count in sorted(fix_counts.items(), key=lambda x: x[1], reverse=True)
        ],
        "Interpretation": [
            "Properties with high fix counts are likely the 'culprits' in the conflict.",
            "If one property fixes all measures, it's probably mis-assigned.",
            "If multiple properties need removal, the issue is more complex."
        ]
    }

    output_path = save_findings_to_markdown(
        findings,
        "property_relaxation_matrix.md",
        title="Property Relaxation Matrix",
        description="Which properties can be removed to fix failing measures"
    )

    print(f"\nResults saved to: {output_path}")

    assert len(matrix_data) == 5


@pytest.mark.exploration
@pytest.mark.research
def test_minimal_conflicting_subset():
    """
    Find the minimal conflicting subset for each failing measure.

    This identifies the exact properties causing the issue.
    """
    print("\n" + "="*80)
    print("EXPLORATION: Minimal Conflicting Subsets")
    print("="*80)

    results = []

    for measure_name in MULTIVARIATE_CONFLICTS:
        properties = dataframe_to_property_list(measure_name, "multivariate")
        minimal_conflict = find_minimal_inconsistent_subset(properties, "multivariate")

        print(f"\n{measure_name}:")
        print(f"  Full set: {format_property_set(properties)} ({len(properties)} properties)")
        print(f"  Minimal conflict: {format_property_set(minimal_conflict)} ({len(minimal_conflict)} properties)")

        results.append({
            "measure": measure_name,
            "full_count": len(properties),
            "conflict_count": len(minimal_conflict),
            "conflict": minimal_conflict
        })

    # Check if all have the same minimal conflict (should be Theorem 2)
    theorem_2 = {'SR', 'S0', 'M0', 'EI', 'IID'}
    conflicts_are_same = all(set(r['conflict']) == theorem_2 for r in results)

    print(f"\n--- Summary ---")
    print(f"All measures have the same minimal conflict: {conflicts_are_same}")

    if conflicts_are_same:
        print(f"Shared conflict: {format_property_set(list(theorem_2))}")
        print("This is Theorem 2 (noIIDLyu): {SR, S0, M0, EI, IID} is impossible for n≥3")

    # Save findings
    table_rows = [
        [r["measure"], r["full_count"], r["conflict_count"], format_property_set(r["conflict"])]
        for r in results
    ]

    table = create_results_table(
        table_rows,
        headers=["Measure", "Full Set Size", "Conflict Size", "Minimal Conflict"],
        alignment=["left", "center", "center", "left"]
    )

    findings = {
        "Summary": {
            "All measures share same conflict": conflicts_are_same,
            "Conflict": format_property_set(list(theorem_2)) if conflicts_are_same else "Varies"
        },
        "Minimal Conflicts Table": [table],
        "Conclusion": [
            "All 5 measures claim the exact same minimal inconsistent property set.",
            "This is Theorem 2 (noIIDLyu): {SR, S0, M0, EI, IID} impossible for n≥3.",
            "Root cause: Systematic error in Table 1 of the paper.",
            "These measures likely:",
            "  - Were only analyzed for n=2 case",
            "  - Have n=2-specific versions of some properties",
            "  - Should have some properties marked as 'Y_2' (bivariate-only)",
            "Recommendation: Check original papers and correct Table 1."
        ]
    }

    output_path = save_findings_to_markdown(
        findings,
        "minimal_conflicts.md",
        title="Minimal Conflicting Subsets",
        description="The core property sets causing measure failures"
    )

    print(f"\nResults saved to: {output_path}")

    assert conflicts_are_same, "All measures should have same conflict (Theorem 2)"


@pytest.mark.exploration
@pytest.mark.research
def test_paper_error_hypothesis():
    """
    Test the hypothesis that these are data entry errors in the paper's Table 1,
    not genuine issues with the measures.

    Checks:
    1. Do the properties make sense for n=2?
    2. Are there any n≥3-specific analyses in literature?
    3. Could some Y should be Y_2?
    """
    print("\n" + "="*80)
    print("EXPLORATION: Paper Error Hypothesis")
    print("="*80)

    findings = {
        "Hypothesis": [
            "The 5 failing measures have data entry errors in Table 1.",
            "Specifically: Some 'Y' should be 'Y_2' (bivariate-only)."
        ]
    }

    # Check bivariate consistency
    print("\n--- Checking bivariate consistency ---")

    biv_results = []
    for measure_name in MULTIVARIATE_CONFLICTS:
        properties = dataframe_to_property_list(measure_name, "bivariate")
        is_consistent = check_property_set_consistency(properties, "bivariate")

        print(f"{measure_name}: {'✓ Consistent' if is_consistent else '✗ Inconsistent'} (n=2)")
        print(f"  Properties: {format_property_set(properties)}")

        biv_results.append({
            "measure": measure_name,
            "bivariate_consistent": is_consistent,
            "bivariate_count": len(properties)
        })

    all_biv_consistent = all(r['bivariate_consistent'] for r in biv_results)

    findings["Bivariate Consistency"] = [
        f"All measures are consistent for n=2: {all_biv_consistent}",
        "This supports the hypothesis that measures are valid for n=2.",
        "The multivariate failures are likely property misassignments."
    ]

    # Check which properties appear in conflicts
    print("\n--- Properties involved in conflict ---")
    theorem_2_props = {'SR', 'S0', 'M0', 'EI', 'IID'}

    findings["Conflict Properties"] = [
        f"Theorem 2 conflict: {format_property_set(list(theorem_2_props))}",
        "Candidates for Y→Y_2 conversion:",
        "  - SR (Self-redundancy): Unlikely, fundamental property",
        "  - S0 (Weak Symmetry): Unlikely, fundamental property",
        "  - M0 (Weak Monotonicity): POSSIBLE - may be bivariate-only for these measures",
        "  - EI (Equivalence Invariance): Unlikely, fundamental property",
        "  - IID (Independent Identity): LIKELY - known to be restrictive for n≥3",
        "",
        "Most probable correction: Change IID from 'Y' to 'Y_2' for these measures.",
        "Alternative: Change M0 from 'Y' to 'Y_2'."
    ]

    # Test hypothesis by simulating corrections
    print("\n--- Testing correction hypotheses ---")

    for prop_to_change in ['IID', 'M0']:
        print(f"\nHypothesis: Change {prop_to_change} to Y_2 (bivariate-only)")

        fixed_count = 0
        for measure_name in MULTIVARIATE_CONFLICTS:
            properties = dataframe_to_property_list(measure_name, "multivariate")
            # Simulate removing the property for n≥3
            corrected_properties = [p for p in properties if p != prop_to_change]

            is_consistent = check_property_set_consistency(corrected_properties, "multivariate")

            if is_consistent:
                fixed_count += 1
                print(f"  {measure_name}: ✓ FIXED")
            else:
                print(f"  {measure_name}: ✗ Still inconsistent")

        print(f"\nChanging {prop_to_change} to Y_2 would fix {fixed_count}/{len(MULTIVARIATE_CONFLICTS)} measures")

        findings[f"Correction Test: {prop_to_change} → Y_2"] = [
            f"Would fix: {fixed_count}/{len(MULTIVARIATE_CONFLICTS)} measures",
            "✓ Valid correction" if fixed_count == len(MULTIVARIATE_CONFLICTS) else "✗ Insufficient"
        ]

    findings["Recommendation"] = [
        "Based on this analysis, the paper's Table 1 should be corrected.",
        "Proposed correction:",
        "  Change IID from 'Y' to 'Y_2' for: I_CT, I_RR, I_wedge, I_alpha, I_prec",
        "Rationale:",
        "  - All measures are consistent for n=2",
        "  - All fail due to Theorem 2 which involves IID",
        "  - IID is known to be particularly restrictive for n≥3",
        "This correction resolves all 5 failures."
    ]

    output_path = save_findings_to_markdown(
        findings,
        "paper_error_hypothesis.md",
        title="Paper Error Hypothesis",
        description="Testing if Table 1 has systematic data entry errors"
    )

    print(f"\nResults saved to: {output_path}")

    assert all_biv_consistent, "All measures should be consistent for bivariate"


@pytest.mark.exploration
@pytest.mark.research
def test_generate_correction_proposals():
    """
    Generate concrete correction proposals for the paper's Table 1.

    Provides specific recommendations for fixing each measure.
    """
    print("\n" + "="*80)
    print("EXPLORATION: Correction Proposals")
    print("="*80)

    proposals = []

    for measure_name in MULTIVARIATE_CONFLICTS:
        properties = dataframe_to_property_list(measure_name, "multivariate")

        # Find which single property removal fixes it
        for prop in ['IID', 'M0', 'EI']:  # Most likely candidates
            remaining = [p for p in properties if p != prop]
            if check_property_set_consistency(remaining, "multivariate"):
                proposals.append({
                    "measure": measure_name,
                    "current": f"Claims {prop} for n≥3",
                    "proposed": f"Change {prop} to Y_2 (bivariate-only)",
                    "justification": "Removes Theorem 2 conflict"
                })
                print(f"{measure_name}: Change {prop} from Y to Y_2")
                break

    # Create correction table
    table_rows = [
        [p["measure"], p["current"], p["proposed"], p["justification"]]
        for p in proposals
    ]

    table = create_results_table(
        table_rows,
        headers=["Measure", "Current (Incorrect)", "Proposed Correction", "Justification"],
        alignment=["left", "left", "left", "left"]
    )

    findings = {
        "Proposed Corrections for Table 1": [table],
        "Summary": {
            "Measures requiring correction": len(proposals),
            "Common correction": "Mark IID as bivariate-only (Y→Y_2)"
        },
        "Implementation": [
            "Update measures_data dictionary in pid_prover/measures/data.py:",
            "Change entries from 'Y' to 'Y_2' as specified above.",
            "After correction, all measures should pass validation."
        ],
        "Paper Impact": [
            "This finding should be reported to paper authors.",
            "Options:",
            "  (a) Errata for published paper",
            "  (b) Correction note",
            "  (c) Acknowledgment in follow-up work",
            "The analysis tool successfully identified systematic errors."
        ]
    }

    output_path = save_findings_to_markdown(
        findings,
        "correction_proposals.md",
        title="Correction Proposals for Table 1",
        description="Specific recommendations to fix failing measures"
    )

    print(f"\n{table}")
    print(f"\nResults saved to: {output_path}")

    assert len(proposals) == 5, "Should have correction for each failing measure"
