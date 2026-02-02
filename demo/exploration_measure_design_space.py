"""
Exploration: Measure Design Space

Systematically explores the space of possible PID measures by:
1. Finding all maximal consistent property sets
2. Identifying unexplored regions (consistent sets without measures)
3. Clustering measures by property similarity
4. Analyzing property tradeoffs
5. Finding gaps in coverage

Expected Output: Guide for designing new PID measures and taxonomy of existing ones.
"""

import pytest
from typing import List, Set, Dict
import itertools
import z3
from pid_prover import (
    get_pid_solver,
    find_maximal_compatible_sets,
    measures_df
)
from pid_prover.solver.axioms import P, prop_names
from pid_prover.measures.validation import dataframe_to_property_list
from utils_research import (
    save_findings_to_markdown,
    format_property_set,
    create_results_table,
    log_computational_cost
)


def is_consistent(properties: List[str], case: str = "bivariate") -> bool:
    """Check if a property set is consistent."""
    solver = get_pid_solver(case)
    solver.push()
    solver.add(z3.And([P[prop] for prop in properties]))
    result = solver.check() == z3.sat
    solver.pop()
    return result


def jaccard_similarity(set1: Set[str], set2: Set[str]) -> float:
    """Compute Jaccard similarity between two property sets."""
    if not set1 and not set2:
        return 1.0
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    return intersection / union if union > 0 else 0.0


@pytest.mark.exploration
@pytest.mark.research
@pytest.mark.slow
@log_computational_cost
def test_find_all_maximal_consistent_sets():
    """
    Find all maximal consistent property sets.

    A set is maximal if adding any property makes it inconsistent.

    WARNING: Computationally expensive for exhaustive search.
    This test uses a heuristic approach.
    """
    print("\n" + "="*80)
    print("EXPLORATION: Maximal Consistent Property Sets")
    print("="*80)

    for case in ["bivariate", "multivariate"]:
        print(f"\n--- {case.upper()} ---")

        # Use the built-in function with lower threshold
        maximal_sets = find_maximal_compatible_sets(case, min_size=8)

        print(f"\nFound {len(maximal_sets)} maximal sets (size ≥ 8)")

        # Analyze sizes
        sizes = [len(s) for s in maximal_sets]
        if sizes:
            print(f"Smallest: {min(sizes)} properties")
            print(f"Largest: {max(sizes)} properties")
            print(f"Average: {sum(sizes) / len(sizes):.1f} properties")

        # Show largest sets
        maximal_sets.sort(key=len, reverse=True)
        print("\nTop 5 largest maximal sets:")
        for i, mset in enumerate(maximal_sets[:5], 1):
            print(f"  {i}. Size {len(mset)}: {format_property_set(mset)}")

        # Save findings
        findings = {
            "Summary": {
                "Case": case,
                "Maximal sets found": len(maximal_sets),
                "Smallest set size": min(sizes) if sizes else 0,
                "Largest set size": max(sizes) if sizes else 0
            },
            "Largest Maximal Sets": [
                f"Size {len(mset)}: {format_property_set(mset)}"
                for mset in maximal_sets[:10]
            ] if maximal_sets else ["None found"],
            "Interpretation": [
                "Maximal sets represent the boundaries of the consistent property space.",
                "Each set is a potential candidate for a new PID measure.",
                "Larger sets indicate more constrained but feature-rich measures."
            ]
        }

        output_path = save_findings_to_markdown(
            findings,
            f"maximal_consistent_sets_{case}.md",
            title=f"Maximal Consistent Property Sets ({case})"
        )

        print(f"Saved to: {output_path}")


@pytest.mark.exploration
@pytest.mark.research
def test_unexplored_regions():
    """
    Find consistent property sets not corresponding to any existing measure.

    These are "gaps" in the PID measure landscape - opportunities for new measures.
    """
    print("\n" + "="*80)
    print("EXPLORATION: Unexplored Regions")
    print("="*80)

    for case in ["bivariate", "multivariate"]:
        print(f"\n--- {case.upper()} ---")

        # Get all existing measure property sets
        existing_sets = []
        for measure_name in measures_df.columns:
            if case == "multivariate":
                # Skip bivariate-only measures
                from pid_prover.measures.data import bivariate_only_measures
                if measure_name in bivariate_only_measures:
                    continue

            props = dataframe_to_property_list(measure_name, case)
            existing_sets.append(set(props))

        print(f"Existing measures: {len(existing_sets)}")

        # Find maximal consistent sets
        maximal_sets = find_maximal_compatible_sets(case, min_size=8)

        # Find unexplored sets (not matching any existing measure)
        unexplored = []
        for mset in maximal_sets:
            mset_set = set(mset)

            # Check if this matches any existing measure
            matches_existing = any(
                mset_set == existing for existing in existing_sets
            )

            if not matches_existing:
                unexplored.append(mset)

        print(f"\nUnexplored maximal sets: {len(unexplored)}")

        if unexplored:
            # Sort by size
            unexplored.sort(key=len, reverse=True)

            print("\nTop 10 unexplored regions:")
            for i, uset in enumerate(unexplored[:10], 1):
                print(f"  {i}. Size {len(uset)}: {format_property_set(uset)}")

                # Find closest existing measure
                best_match = None
                best_similarity = 0.0

                for j, existing in enumerate(existing_sets):
                    similarity = jaccard_similarity(set(uset), existing)
                    if similarity > best_similarity:
                        best_similarity = similarity
                        best_match = measures_df.columns[j]

                print(f"      Closest measure: {best_match} (similarity: {best_similarity:.2f})")

        # Save findings
        findings = {
            "Summary": {
                "Case": case,
                "Existing measures": len(existing_sets),
                "Maximal sets found": len(maximal_sets),
                "Unexplored sets": len(unexplored)
            },
            "Unexplored Regions": [
                f"Size {len(uset)}: {format_property_set(uset)}"
                for uset in unexplored[:20]
            ] if unexplored else ["All maximal sets are covered by existing measures"],
            "Opportunities": [
                "Each unexplored set is a candidate for a novel PID measure.",
                "Properties in these sets are logically consistent.",
                "New measures would fill gaps in the landscape.",
                f"{len(unexplored)} potential new measures identified."
            ]
        }

        output_path = save_findings_to_markdown(
            findings,
            f"unexplored_regions_{case}.md",
            title=f"Unexplored Regions ({case})",
            description="Consistent property sets without corresponding measures"
        )

        print(f"Saved to: {output_path}")


@pytest.mark.exploration
@pytest.mark.research
def test_measure_clustering():
    """
    Cluster measures by property similarity using Jaccard distance.

    Reveals families of related measures.
    """
    print("\n" + "="*80)
    print("EXPLORATION: Measure Clustering")
    print("="*80)

    for case in ["bivariate", "multivariate"]:
        print(f"\n--- {case.upper()} ---")

        # Get measure property sets
        measure_properties = {}
        for measure_name in measures_df.columns:
            if case == "multivariate":
                from pid_prover.measures.data import bivariate_only_measures
                if measure_name in bivariate_only_measures:
                    continue

            props = set(dataframe_to_property_list(measure_name, case))
            measure_properties[measure_name] = props

        print(f"Measures to cluster: {len(measure_properties)}")

        # Compute pairwise similarities
        measures = list(measure_properties.keys())
        similarities = {}

        for i, m1 in enumerate(measures):
            for j, m2 in enumerate(measures):
                if i < j:
                    sim = jaccard_similarity(measure_properties[m1], measure_properties[m2])
                    similarities[(m1, m2)] = sim

        # Find most similar pairs
        sorted_pairs = sorted(similarities.items(), key=lambda x: x[1], reverse=True)

        print("\nTop 10 most similar measure pairs:")
        for (m1, m2), sim in sorted_pairs[:10]:
            print(f"  {m1} ~ {m2}: {sim:.3f}")
            common = measure_properties[m1] & measure_properties[m2]
            diff1 = measure_properties[m1] - measure_properties[m2]
            diff2 = measure_properties[m2] - measure_properties[m1]
            print(f"    Common: {format_property_set(list(common))}")
            if diff1:
                print(f"    Only {m1}: {format_property_set(list(diff1))}")
            if diff2:
                print(f"    Only {m2}: {format_property_set(list(diff2))}")

        # Identify families (similarity > 0.7)
        families = []
        used = set()

        for (m1, m2), sim in sorted_pairs:
            if sim > 0.7 and m1 not in used and m2 not in used:
                # Start a new family
                family = {m1, m2}
                used.add(m1)
                used.add(m2)

                # Try to add more measures to this family
                for m3 in measures:
                    if m3 not in used:
                        # Check similarity with all family members
                        avg_sim = sum(
                            jaccard_similarity(measure_properties[m3], measure_properties[fm])
                            for fm in family
                        ) / len(family)

                        if avg_sim > 0.7:
                            family.add(m3)
                            used.add(m3)

                families.append(family)

        print(f"\nIdentified {len(families)} measure families (similarity > 0.7):")
        for i, family in enumerate(families, 1):
            print(f"  Family {i}: {{{', '.join(sorted(family))}}}")

        # Save findings
        findings = {
            "Summary": {
                "Case": case,
                "Measures analyzed": len(measures),
                "Families identified": len(families)
            },
            "Most Similar Pairs": [
                f"{m1} ~ {m2}: {sim:.3f}" for (m1, m2), sim in sorted_pairs[:20]
            ],
            "Measure Families": [
                f"Family {i}: {{{', '.join(sorted(family))}}}"
                for i, family in enumerate(families, 1)
            ] if families else ["No strong families identified"],
            "Interpretation": [
                "Families represent groups of measures with similar property profiles.",
                "High similarity suggests measures are conceptually related.",
                "Families may share underlying design principles."
            ]
        }

        output_path = save_findings_to_markdown(
            findings,
            f"measure_clustering_{case}.md",
            title=f"Measure Clustering ({case})",
            description="Families of similar measures"
        )

        print(f"Saved to: {output_path}")


@pytest.mark.exploration
@pytest.mark.research
def test_property_tradeoffs():
    """
    Analyze property tradeoffs: If you want property A, what must you sacrifice?

    For each property, find what other properties cannot coexist with it.
    """
    print("\n" + "="*80)
    print("EXPLORATION: Property Tradeoffs")
    print("="*80)

    for case in ["bivariate", "multivariate"]:
        print(f"\n--- {case.upper()} ---")

        solver = get_pid_solver(case)
        tradeoffs = {}

        for prop in prop_names:
            incompatible = []

            for other in prop_names:
                if prop == other:
                    continue

                # Check if {prop, other} is inconsistent
                solver.push()
                solver.add(z3.And(P[prop], P[other]))
                if solver.check() == z3.unsat:
                    incompatible.append(other)
                solver.pop()

            if incompatible:
                tradeoffs[prop] = incompatible

        print(f"\nProperties with tradeoffs: {len(tradeoffs)}")

        if tradeoffs:
            # Sort by number of incompatibilities
            sorted_tradeoffs = sorted(tradeoffs.items(), key=lambda x: len(x[1]), reverse=True)

            print("\nMost constrained properties:")
            for prop, incomp in sorted_tradeoffs[:10]:
                print(f"  {prop}: incompatible with {len(incomp)} properties")
                print(f"    {{{', '.join(sorted(incomp))}}}")

        # Save findings
        table_rows = []
        for prop, incomp in sorted(tradeoffs.items(), key=lambda x: len(x[1]), reverse=True):
            table_rows.append([prop, len(incomp), format_property_set(incomp)])

        table = create_results_table(
            table_rows,
            headers=["Property", "# Incompatible", "Incompatible With"],
            alignment=["center", "center", "left"]
        ) if table_rows else "No pairwise incompatibilities found"

        findings = {
            "Summary": {
                "Case": case,
                "Properties with tradeoffs": len(tradeoffs)
            },
            "Tradeoff Table": [table],
            "Interpretation": [
                "Properties with many incompatibilities are highly constraining.",
                "Choosing such properties severely limits measure design options.",
                "Weaker properties (few incompatibilities) allow more flexibility."
            ]
        }

        output_path = save_findings_to_markdown(
            findings,
            f"property_tradeoffs_{case}.md",
            title=f"Property Tradeoffs ({case})",
            description="Pairwise property incompatibilities"
        )

        print(f"Saved to: {output_path}")


@pytest.mark.exploration
@pytest.mark.research
def test_hole_finding():
    """
    Find "holes" in coverage: property combinations rarely explored by measures.

    Identifies underexplored regions of the property space.
    """
    print("\n" + "="*80)
    print("EXPLORATION: Coverage Holes")
    print("="*80)

    for case in ["bivariate", "multivariate"]:
        print(f"\n--- {case.upper()} ---")

        # Count how many measures have each property
        property_counts = {prop: 0 for prop in prop_names}

        for measure_name in measures_df.columns:
            if case == "multivariate":
                from pid_prover.measures.data import bivariate_only_measures
                if measure_name in bivariate_only_measures:
                    continue

            props = dataframe_to_property_list(measure_name, case)
            for prop in props:
                property_counts[prop] += 1

        total_measures = len([
            m for m in measures_df.columns
            if case == "bivariate" or m not in measures_df.columns[:4]  # Simplified check
        ])

        print(f"\nProperty coverage (out of {total_measures} measures):")

        sorted_props = sorted(property_counts.items(), key=lambda x: x[1])

        for prop, count in sorted_props:
            pct = 100 * count / total_measures if total_measures > 0 else 0
            print(f"  {prop}: {count} measures ({pct:.1f}%)")

        # Identify underexplored properties (coverage < 30%)
        threshold = 0.3 * total_measures
        underexplored = [prop for prop, count in property_counts.items() if count < threshold]

        print(f"\nUnderexplored properties (< 30% coverage):")
        for prop in underexplored:
            count = property_counts[prop]
            pct = 100 * count / total_measures if total_measures > 0 else 0
            print(f"  {prop}: {count} measures ({pct:.1f}%)")

        # For underexplored properties, check if they're consistent with common properties
        if underexplored:
            print("\nChecking consistency with common properties...")

            # Find most common properties
            common_props = [prop for prop, count in sorted_props[-5:]]
            print(f"Common properties: {common_props}")

            for ue_prop in underexplored:
                test_set = common_props + [ue_prop]
                if is_consistent(test_set, case):
                    print(f"  {ue_prop}: ✓ Compatible with common properties")
                    print(f"    Opportunity: Design measure with {format_property_set(test_set)}")
                else:
                    print(f"  {ue_prop}: ✗ Incompatible with common properties")

        # Save findings
        table_rows = [
            [prop, count, f"{100 * count / total_measures:.1f}%"]
            for prop, count in sorted_props
        ]

        table = create_results_table(
            table_rows,
            headers=["Property", "Measure Count", "Coverage %"],
            alignment=["left", "center", "center"]
        )

        findings = {
            "Summary": {
                "Case": case,
                "Total measures": total_measures,
                "Underexplored properties": len(underexplored)
            },
            "Property Coverage Table": [table],
            "Underexplored Properties": [
                f"{prop}: {property_counts[prop]} measures ({100 * property_counts[prop] / total_measures:.1f}%)"
                for prop in underexplored
            ] if underexplored else ["All properties well-covered"],
            "Recommendations": [
                "Properties with low coverage are opportunities for new measures.",
                "Check if underexplored properties can combine with common ones.",
                "Novel measures should target coverage gaps."
            ]
        }

        output_path = save_findings_to_markdown(
            findings,
            f"coverage_holes_{case}.md",
            title=f"Coverage Holes ({case})",
            description="Underexplored properties in the measure landscape"
        )

        print(f"Saved to: {output_path}")
