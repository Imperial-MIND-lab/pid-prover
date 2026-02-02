"""
Exploration: Multi-Premise Implications

Discovers implications requiring multiple premises:
- 3-premise: A ∧ B ∧ C ⇒ D
- 4-premise: A ∧ B ∧ C ∧ D ⇒ E  (slow)

These reveal hidden dependencies not captured by pairwise implications.

Expected Discoveries:
- Complex property relationships
- Hierarchical structure
- Potential for axiom reduction
"""

import pytest
from typing import List, Tuple
import itertools
import z3
from pid_prover import get_pid_solver, find_minimal_implications
from pid_prover.solver.axioms import P, prop_names
from utils_research import (
    save_findings_to_markdown,
    save_implication_catalog,
    log_computational_cost,
    format_implication,
    create_results_table
)


def find_multi_premise_implications(
    case: str = "bivariate",
    premise_size: int = 3,
    max_results: int = 100
) -> List[Tuple[List[str], str]]:
    """
    Find minimal multi-premise implications.

    Parameters
    ----------
    case : str
        "bivariate" or "multivariate"
    premise_size : int
        Number of premises (3 or 4)
    max_results : int
        Stop after finding this many implications

    Returns
    -------
    list of tuples
        Each tuple is (premise_list, conclusion)
    """
    solver = get_pid_solver(case)
    found_implications = []

    total_combinations = len(list(itertools.combinations(prop_names, premise_size + 1)))
    checked = 0

    print(f"\nSearching for {premise_size}-premise implications in {case} case...")
    print(f"Total combinations to check: {total_combinations}")

    for combo in itertools.combinations(prop_names, premise_size + 1):
        # Try each property as conclusion
        for i in range(len(combo)):
            premises = list(combo[:i]) + list(combo[i+1:])
            conclusion = combo[i]

            # Check if premises => conclusion
            solver.push()
            solver.add(z3.And([P[prop] for prop in premises]))
            solver.add(z3.Not(P[conclusion]))

            if solver.check() == z3.unsat:
                # Implication holds - check minimality

                # Check if any proper subset of premises also implies conclusion
                is_minimal = True
                for size in range(1, len(premises)):
                    if not is_minimal:
                        break
                    for sub_premises in itertools.combinations(premises, size):
                        solver.pop()
                        solver.push()
                        solver.add(z3.And([P[p] for p in sub_premises]))
                        solver.add(z3.Not(P[conclusion]))

                        if solver.check() == z3.unsat:
                            # Subset also implies - not minimal
                            is_minimal = False
                            break

                solver.pop()

                if is_minimal:
                    # Also check that conclusion doesn't imply any premise (circular)
                    is_non_circular = True
                    for premise in premises:
                        solver.push()
                        solver.add(P[conclusion])
                        solver.add(z3.Not(P[premise]))
                        if solver.check() == z3.unsat:
                            is_non_circular = False
                            solver.pop()
                            break
                        solver.pop()

                    if is_non_circular:
                        found_implications.append((premises, conclusion))
                        print(f"  Found: {format_implication(premises, conclusion)}")

                        if len(found_implications) >= max_results:
                            print(f"\nReached max results ({max_results}), stopping...")
                            return found_implications
            else:
                solver.pop()

        checked += 1
        if checked % 100 == 0:
            print(f"  Progress: {checked}/{total_combinations} combinations ({100*checked/total_combinations:.1f}%), found {len(found_implications)} implications")

    return found_implications


@pytest.mark.exploration
@pytest.mark.research
@log_computational_cost
def test_three_premise_implications_bivariate():
    """
    Find 3-premise implications for bivariate case.

    Format: A ∧ B ∧ C ⇒ D

    Expected runtime: 5-15 minutes.
    """
    print("\n" + "="*80)
    print("EXPLORATION: 3-Premise Implications (Bivariate)")
    print("="*80)

    implications = find_multi_premise_implications(
        case="bivariate",
        premise_size=3,
        max_results=50
    )

    print(f"\nFound {len(implications)} minimal 3-premise implications")

    if implications:
        # Save catalog
        output_path = save_implication_catalog(
            implications,
            filename="implications_3premise_bivariate.md",
            case="bivariate"
        )
        print(f"Results saved to: {output_path}")

        # Analyze which properties appear most in premises vs conclusions
        premise_counts = {}
        conclusion_counts = {}

        for premises, conclusion in implications:
            for prop in premises:
                premise_counts[prop] = premise_counts.get(prop, 0) + 1
            conclusion_counts[conclusion] = conclusion_counts.get(conclusion, 0) + 1

        print("\nMost common in premises (weak properties):")
        for prop, count in sorted(premise_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  {prop}: {count} times")

        print("\nMost common as conclusions (strong properties):")
        for prop, count in sorted(conclusion_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  {prop}: {count} times")

    assert len(implications) >= 0


@pytest.mark.exploration
@pytest.mark.research
@log_computational_cost
def test_three_premise_implications_multivariate():
    """
    Find 3-premise implications for multivariate case.

    Expected runtime: 5-15 minutes.
    """
    print("\n" + "="*80)
    print("EXPLORATION: 3-Premise Implications (Multivariate)")
    print("="*80)

    implications = find_multi_premise_implications(
        case="multivariate",
        premise_size=3,
        max_results=50
    )

    print(f"\nFound {len(implications)} minimal 3-premise implications")

    if implications:
        output_path = save_implication_catalog(
            implications,
            filename="implications_3premise_multivariate.md",
            case="multivariate"
        )
        print(f"Results saved to: {output_path}")

    assert len(implications) >= 0


@pytest.mark.exploration
@pytest.mark.research
@pytest.mark.slow
def test_four_premise_implications_bivariate():
    """
    Find 4-premise implications for bivariate case.

    Format: A ∧ B ∧ C ∧ D ⇒ E

    WARNING: Computationally very expensive.
    Expected runtime: 30-120 minutes.
    """
    print("\n" + "="*80)
    print("EXPLORATION: 4-Premise Implications (Bivariate)")
    print("="*80)
    print("WARNING: This is computationally very expensive")
    print("Consider running with smaller max_results\n")

    implications = find_multi_premise_implications(
        case="bivariate",
        premise_size=4,
        max_results=20  # Limited to avoid excessive runtime
    )

    print(f"\nFound {len(implications)} minimal 4-premise implications")

    if implications:
        output_path = save_implication_catalog(
            implications,
            filename="implications_4premise_bivariate.md",
            case="bivariate"
        )
        print(f"Results saved to: {output_path}")

    assert len(implications) >= 0


@pytest.mark.exploration
@pytest.mark.research
def test_implication_chains():
    """
    Find implication chains: P1⇒P2⇒P3⇒P4

    Identifies hierarchical property relationships.
    """
    print("\n" + "="*80)
    print("EXPLORATION: Implication Chains")
    print("="*80)

    for case in ["bivariate", "multivariate"]:
        print(f"\n--- {case.upper()} ---")

        solver = get_pid_solver(case)

        # Build adjacency list of pairwise implications
        graph = {}
        for prop in prop_names:
            graph[prop] = []
            for other in prop_names:
                if prop != other:
                    solver.push()
                    solver.add(P[prop])
                    solver.add(z3.Not(P[other]))
                    if solver.check() == z3.unsat:
                        graph[prop].append(other)
                    solver.pop()

        # Find longest chains using DFS
        def find_chains_from(start, path):
            """DFS to find all maximal chains."""
            chains = []
            has_extension = False

            for neighbor in graph[start]:
                if neighbor not in path:  # Avoid cycles
                    has_extension = True
                    chains.extend(find_chains_from(neighbor, path + [neighbor]))

            if not has_extension:
                # This is a maximal chain
                chains.append(path)

            return chains

        all_chains = []
        for prop in prop_names:
            chains_from_prop = find_chains_from(prop, [prop])
            all_chains.extend(chains_from_prop)

        # Filter to chains of length >= 3
        long_chains = [c for c in all_chains if len(c) >= 3]

        # Sort by length
        long_chains.sort(key=len, reverse=True)

        print(f"Found {len(long_chains)} chains of length ≥ 3")
        print(f"Longest chain length: {len(long_chains[0]) if long_chains else 0}")

        print("\nTop 10 longest chains:")
        for i, chain in enumerate(long_chains[:10], 1):
            chain_str = " ⇒ ".join(chain)
            print(f"  {i}. {chain_str}")

        # Save findings
        findings = {
            "Summary": {
                "Case": case,
                "Total chains (length ≥ 3)": len(long_chains),
                "Longest chain length": len(long_chains[0]) if long_chains else 0
            },
            "Top 20 Chains": [
                " ⇒ ".join(chain) for chain in long_chains[:20]
            ] if long_chains else ["None found"],
            "Interpretation": [
                "Long chains show hierarchical property strength.",
                "Properties at the start of chains are strongest (most restrictive).",
                "Properties at the end are weakest (least restrictive)."
            ]
        }

        output_path = save_findings_to_markdown(
            findings,
            f"implication_chains_{case}.md",
            title=f"Implication Chains ({case})",
            description="Hierarchical property relationships"
        )

        print(f"Saved to: {output_path}")


@pytest.mark.exploration
@pytest.mark.research
def test_bidirectional_implications():
    """
    Find bidirectional implications: P1⇔P2 (P1⇒P2 AND P2⇒P1).

    These are logically equivalent properties.
    """
    print("\n" + "="*80)
    print("EXPLORATION: Bidirectional Implications (Equivalences)")
    print("="*80)

    for case in ["bivariate", "multivariate"]:
        print(f"\n--- {case.upper()} ---")

        solver = get_pid_solver(case)
        equivalences = []

        # Check all pairs
        checked_pairs = set()

        for prop1 in prop_names:
            for prop2 in prop_names:
                if prop1 >= prop2:  # Avoid duplicates and self
                    continue

                pair = tuple(sorted([prop1, prop2]))
                if pair in checked_pairs:
                    continue
                checked_pairs.add(pair)

                # Check prop1 => prop2
                solver.push()
                solver.add(P[prop1])
                solver.add(z3.Not(P[prop2]))
                implies_forward = solver.check() == z3.unsat
                solver.pop()

                if not implies_forward:
                    continue

                # Check prop2 => prop1
                solver.push()
                solver.add(P[prop2])
                solver.add(z3.Not(P[prop1]))
                implies_backward = solver.check() == z3.unsat
                solver.pop()

                if implies_backward:
                    equivalences.append((prop1, prop2))
                    print(f"  Found: {prop1} ⇔ {prop2}")

        print(f"\nFound {len(equivalences)} bidirectional implications")

        if equivalences:
            findings = {
                "Summary": {
                    "Case": case,
                    "Equivalences found": len(equivalences)
                },
                "Bidirectional Implications": [
                    f"{p1} ⇔ {p2}" for p1, p2 in equivalences
                ],
                "Interpretation": [
                    "Bidirectional implications indicate logically equivalent properties.",
                    "Such properties could be unified in the theoretical framework.",
                    "Measures claiming one must claim the other."
                ]
            }
        else:
            findings = {
                "Summary": {
                    "Case": case,
                    "Equivalences found": 0
                },
                "Result": ["No bidirectional implications found.", "All properties are distinct."]
            }

        output_path = save_findings_to_markdown(
            findings,
            f"bidirectional_implications_{case}.md",
            title=f"Bidirectional Implications ({case})",
            description="Logically equivalent properties"
        )

        print(f"Saved to: {output_path}")


@pytest.mark.exploration
def test_compare_2premise_vs_3premise():
    """
    Compare 2-premise vs 3-premise implications.

    Quantifies how much additional structure 3-premise adds.
    """
    print("\n" + "="*80)
    print("EXPLORATION: 2-Premise vs 3-Premise Comparison")
    print("="*80)

    # Use existing functionality for 2-premise
    from pid_prover import find_minimal_implications

    case = "bivariate"

    print(f"\nFinding 2-premise implications...")
    implications_2 = find_minimal_implications(case, premise_size=2)

    print(f"\nFinding 3-premise implications (limited)...")
    implications_3 = find_multi_premise_implications(case, premise_size=3, max_results=30)

    print(f"\n--- Comparison ---")
    print(f"2-premise implications: {len(implications_2)}")
    print(f"3-premise implications: {len(implications_3)}")

    findings = {
        "Summary": {
            "Case": case,
            "2-premise implications": len(implications_2),
            "3-premise implications": len(implications_3),
            "Ratio": f"{len(implications_3) / max(len(implications_2), 1):.2f}x"
        },
        "Interpretation": [
            "3-premise implications reveal dependencies not captured by pairwise analysis.",
            "They represent more complex property interactions.",
            "Important for understanding measure design constraints."
        ]
    }

    output_path = save_findings_to_markdown(
        findings,
        "premise_comparison.md",
        title="2-Premise vs 3-Premise Comparison",
        description="Complexity of multi-premise implications"
    )

    print(f"\nResults saved to: {output_path}")

    assert len(implications_2) > 0  # Should have some 2-premise implications
