"""
Exploration: Property Dependency Graph

Builds complete implication graphs for all 20 properties in both bivariate
and multivariate cases. Discovers:
- All pairwise implications (P1 ⇒ P2)
- Transitive closure
- Equivalence classes
- Topological ordering (weak → strong)
- Visual dependency graphs

Expected Output: Complete property taxonomy and visualizations for paper.
"""

import pytest
from typing import Dict, List, Set, Tuple
import z3
from pid_prover import get_pid_solver
from pid_prover.solver.axioms import P, prop_names
from pid_prover.measures import measures_df
from utils_research import (
    save_findings_to_markdown,
    export_graph_to_dot,
    create_results_table,
    log_computational_cost
)


def check_implication(
    premise: str,
    conclusion: str,
    solver: z3.Solver
) -> bool:
    """Check if premise ⇒ conclusion."""
    solver.push()
    solver.add(P[premise])
    solver.add(z3.Not(P[conclusion]))
    result = solver.check() == z3.unsat  # UNSAT means implication holds
    solver.pop()
    return result


def build_implication_graph(case: str = "bivariate") -> Dict[str, List[str]]:
    """
    Build complete implication graph: prop -> [props it implies].

    Returns adjacency list representation.
    """
    solver = get_pid_solver(case)
    graph = {prop: [] for prop in prop_names}

    total_checks = len(prop_names) * (len(prop_names) - 1)
    checked = 0

    print(f"\nBuilding implication graph for {case}...")
    print(f"Checking {total_checks} implications (20×19)...")

    for premise in prop_names:
        for conclusion in prop_names:
            if premise == conclusion:
                continue

            if check_implication(premise, conclusion, solver):
                graph[premise].append(conclusion)

            checked += 1
            if checked % 50 == 0:
                print(f"  Progress: {checked}/{total_checks} ({100*checked/total_checks:.1f}%)")

    return graph


def transitive_closure(graph: Dict[str, List[str]]) -> Dict[str, Set[str]]:
    """Compute transitive closure: all properties reachable from each property."""
    closure = {prop: set(neighbors) for prop, neighbors in graph.items()}

    # Floyd-Warshall algorithm
    for k in prop_names:
        for i in prop_names:
            for j in prop_names:
                if k in closure[i] and j in closure[k]:
                    closure[i].add(j)

    return closure


def find_equivalence_classes(graph: Dict[str, List[str]]) -> List[Set[str]]:
    """Find equivalence classes: sets of mutually implying properties."""
    equiv_classes = []
    visited = set()

    for prop in prop_names:
        if prop in visited:
            continue

        # Find all properties that mutually imply each other
        equiv_class = {prop}
        for other in prop_names:
            if other != prop and other not in visited:
                # Check if prop ⇔ other (mutual implication)
                if other in graph[prop] and prop in graph[other]:
                    equiv_class.add(other)

        if len(equiv_class) > 1:
            equiv_classes.append(equiv_class)
            visited.update(equiv_class)

    return equiv_classes


def topological_sort(graph: Dict[str, List[str]]) -> List[str]:
    """
    Sort properties from weakest to strongest.

    A property is "stronger" if it implies more properties.
    Uses topological sort on reversed graph (implications flow from strong to weak).
    """
    # Count how many other properties each property implies
    implication_count = {prop: len(neighbors) for prop, neighbors in graph.items()}

    # Sort by implication count (fewer implications = weaker)
    sorted_props = sorted(prop_names, key=lambda p: implication_count[p])

    return sorted_props


@pytest.mark.exploration
@pytest.mark.research
@log_computational_cost
def test_build_implication_graph_bivariate():
    """
    Build complete pairwise implication graph for bivariate case.

    Checks all 20×19 = 380 possible implications.
    Expected runtime: 2-5 minutes.
    """
    print("\n" + "="*80)
    print("EXPLORATION: Bivariate Implication Graph")
    print("="*80)

    graph = build_implication_graph("bivariate")

    # Count implications
    total_implications = sum(len(neighbors) for neighbors in graph.values())
    print(f"\nTotal implications found: {total_implications}")

    # Identify properties with most/least implications
    sorted_by_strength = sorted(
        graph.items(),
        key=lambda x: len(x[1]),
        reverse=True
    )

    print("\nStrongest properties (imply the most):")
    for prop, neighbors in sorted_by_strength[:5]:
        print(f"  {prop}: implies {len(neighbors)} properties")

    print("\nWeakest properties (imply the least):")
    for prop, neighbors in sorted_by_strength[-5:]:
        print(f"  {prop}: implies {len(neighbors)} properties")

    # Save graph
    output_path = export_graph_to_dot(
        graph,
        "property_implications_bivariate",
        graph_name="BivariateBivariate_Implications",
        directed=True
    )
    print(f"\nGraph saved to: {output_path}")
    print("Convert to image with: dot -Tpng property_implications_bivariate.dot -o property_implications_bivariate.png")

    # Save findings
    implications_list = []
    for prop, neighbors in sorted(graph.items()):
        if neighbors:
            for neighbor in sorted(neighbors):
                implications_list.append(f"{prop} ⇒ {neighbor}")

    findings = {
        "Summary": {
            "Total properties": len(prop_names),
            "Total implications": total_implications,
            "Average implications per property": f"{total_implications / len(prop_names):.1f}"
        },
        "Strongest Properties": [
            f"{prop} (implies {len(neighbors)} properties)"
            for prop, neighbors in sorted_by_strength[:10]
        ],
        "All Implications": implications_list
    }

    findings_path = save_findings_to_markdown(
        findings,
        "implications_bivariate.md",
        title="Bivariate Implication Graph",
        description="Complete pairwise implications for n=2"
    )

    print(f"Findings saved to: {findings_path}")

    assert total_implications > 0


@pytest.mark.exploration
@pytest.mark.research
@log_computational_cost
def test_build_implication_graph_multivariate():
    """
    Build complete pairwise implication graph for multivariate case.

    Expected runtime: 2-5 minutes.
    """
    print("\n" + "="*80)
    print("EXPLORATION: Multivariate Implication Graph")
    print("="*80)

    graph = build_implication_graph("multivariate")

    # Count implications
    total_implications = sum(len(neighbors) for neighbors in graph.values())
    print(f"\nTotal implications found: {total_implications}")

    # Identify properties with most/least implications
    sorted_by_strength = sorted(
        graph.items(),
        key=lambda x: len(x[1]),
        reverse=True
    )

    print("\nStrongest properties (imply the most):")
    for prop, neighbors in sorted_by_strength[:5]:
        print(f"  {prop}: implies {len(neighbors)} properties")

    print("\nWeakest properties (imply the least):")
    for prop, neighbors in sorted_by_strength[-5:]:
        print(f"  {prop}: implies {len(neighbors)} properties")

    # Save graph
    output_path = export_graph_to_dot(
        graph,
        "property_implications_multivariate",
        graph_name="Multivariate_Implications",
        directed=True
    )
    print(f"\nGraph saved to: {output_path}")

    # Save findings
    implications_list = []
    for prop, neighbors in sorted(graph.items()):
        if neighbors:
            for neighbor in sorted(neighbors):
                implications_list.append(f"{prop} ⇒ {neighbor}")

    findings = {
        "Summary": {
            "Total properties": len(prop_names),
            "Total implications": total_implications,
            "Average implications per property": f"{total_implications / len(prop_names):.1f}"
        },
        "Strongest Properties": [
            f"{prop} (implies {len(neighbors)} properties)"
            for prop, neighbors in sorted_by_strength[:10]
        ],
        "All Implications": implications_list
    }

    findings_path = save_findings_to_markdown(
        findings,
        "implications_multivariate.md",
        title="Multivariate Implication Graph",
        description="Complete pairwise implications for n≥3"
    )

    print(f"Findings saved to: {findings_path}")

    assert total_implications > 0


@pytest.mark.exploration
@pytest.mark.research
def test_transitive_closure():
    """
    Compute transitive closure for both cases.

    If P1⇒P2 and P2⇒P3, then P1⇒P3 (transitive).
    This finds all indirect implications.
    """
    print("\n" + "="*80)
    print("EXPLORATION: Transitive Closure")
    print("="*80)

    for case in ["bivariate", "multivariate"]:
        print(f"\n--- {case.upper()} ---")

        graph = build_implication_graph(case)
        closure = transitive_closure(graph)

        # Count direct vs indirect implications
        direct_count = sum(len(neighbors) for neighbors in graph.values())
        total_count = sum(len(reachable) for reachable in closure.values())
        indirect_count = total_count - direct_count

        print(f"Direct implications: {direct_count}")
        print(f"Total reachable (with transitive): {total_count}")
        print(f"Indirect implications: {indirect_count}")

        # Find longest implication chains
        print("\nLongest implication chains:")
        # BFS to find longest path from each property
        max_chain_length = 0
        longest_chains = []

        for start in prop_names:
            # Simple BFS
            visited = {start}
            queue = [(start, [start])]

            while queue:
                current, path = queue.pop(0)
                for neighbor in graph[current]:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        new_path = path + [neighbor]
                        queue.append((neighbor, new_path))

                        if len(new_path) > max_chain_length:
                            max_chain_length = len(new_path)
                            longest_chains = [new_path]
                        elif len(new_path) == max_chain_length and new_path not in longest_chains:
                            longest_chains.append(new_path)

        for chain in longest_chains[:5]:  # Show top 5
            chain_str = " ⇒ ".join(chain)
            print(f"  {chain_str}")

    assert indirect_count >= 0


@pytest.mark.exploration
@pytest.mark.research
def test_find_equivalence_classes():
    """
    Find equivalence classes: properties that mutually imply each other (P1⇔P2).

    These are logically equivalent properties.
    """
    print("\n" + "="*80)
    print("EXPLORATION: Property Equivalence Classes")
    print("="*80)

    for case in ["bivariate", "multivariate"]:
        print(f"\n--- {case.upper()} ---")

        graph = build_implication_graph(case)
        equiv_classes = find_equivalence_classes(graph)

        if equiv_classes:
            print(f"Found {len(equiv_classes)} equivalence classes:")
            for i, equiv_class in enumerate(equiv_classes, 1):
                props = sorted(equiv_class)
                print(f"  Class {i}: {{{', '.join(props)}}}")
                print(f"    Size: {len(props)} properties")
        else:
            print("No equivalence classes found (all properties are distinct)")

        # Save findings
        findings = {
            "Summary": {
                "Case": case,
                "Equivalence classes found": len(equiv_classes)
            }
        }

        if equiv_classes:
            for i, equiv_class in enumerate(equiv_classes, 1):
                findings[f"Equivalence Class {i}"] = [
                    f"Properties: {{{', '.join(sorted(equiv_class))}}}",
                    f"Size: {len(equiv_class)}",
                    "All properties in this class are logically equivalent."
                ]
        else:
            findings["Result"] = ["No equivalence classes found.", "All 20 properties are logically distinct."]

        findings_path = save_findings_to_markdown(
            findings,
            f"equivalence_classes_{case}.md",
            title=f"Property Equivalence Classes ({case})",
            description="Mutually implying (equivalent) properties"
        )

        print(f"Saved to: {findings_path}")


@pytest.mark.exploration
@pytest.mark.research
def test_topological_sort():
    """
    Sort properties from weakest to strongest.

    Weaker properties imply fewer other properties.
    Stronger properties imply more other properties.
    """
    print("\n" + "="*80)
    print("EXPLORATION: Property Strength Ranking")
    print("="*80)

    for case in ["bivariate", "multivariate"]:
        print(f"\n--- {case.upper()} ---")

        graph = build_implication_graph(case)
        sorted_props = topological_sort(graph)

        # Create ranking table
        table_rows = []
        for rank, prop in enumerate(sorted_props, 1):
            implication_count = len(graph[prop])
            table_rows.append([rank, prop, implication_count])

        table = create_results_table(
            table_rows,
            headers=["Rank", "Property", "Implies"],
            alignment=["center", "left", "center"]
        )

        print(f"\nProperty Strength Ranking (weak → strong):")
        print(table)

        # Save findings
        findings = {
            "Summary": {
                "Case": case,
                "Weakest property": f"{sorted_props[0]} (implies {len(graph[sorted_props[0]])} properties)",
                "Strongest property": f"{sorted_props[-1]} (implies {len(graph[sorted_props[-1]])} properties)"
            },
            "Complete Ranking": [table],
            "Interpretation": [
                "Rank 1 = Weakest (implies fewest properties)",
                f"Rank {len(sorted_props)} = Strongest (implies most properties)",
                "Strong properties are more restrictive on measure design.",
                "Weak properties provide less constraint."
            ]
        }

        findings_path = save_findings_to_markdown(
            findings,
            f"property_ranking_{case}.md",
            title=f"Property Strength Ranking ({case})",
            description="Properties sorted by logical strength"
        )

        print(f"Saved to: {findings_path}")


@pytest.mark.exploration
@pytest.mark.research
@log_computational_cost
def test_visualize_dependency_dag():
    """
    Create visual dependency DAG for both cases.

    Exports Graphviz DOT files for paper figures.
    """
    print("\n" + "="*80)
    print("EXPLORATION: Dependency DAG Visualization")
    print("="*80)

    for case in ["bivariate", "multivariate"]:
        print(f"\n--- {case.upper()} ---")

        graph = build_implication_graph(case)

        # Export full graph
        full_path = export_graph_to_dot(
            graph,
            f"dependency_dag_{case}_full",
            graph_name=f"{case.capitalize()}_Dependencies",
            directed=True
        )
        print(f"Full graph saved to: {full_path}")

        # Export reduced graph (transitive reduction to make it cleaner)
        # For now, just filter to "interesting" implications (non-trivial)
        interesting_graph = {}
        for prop, neighbors in graph.items():
            # Include if has at least one implication
            if neighbors:
                interesting_graph[prop] = neighbors

        if interesting_graph:
            reduced_path = export_graph_to_dot(
                interesting_graph,
                f"dependency_dag_{case}_reduced",
                graph_name=f"{case.capitalize()}_Dependencies_Reduced",
                directed=True
            )
            print(f"Reduced graph saved to: {reduced_path}")

        print(f"\nTo generate images, run:")
        print(f"  dot -Tpng {full_path.name} -o dependency_dag_{case}_full.png")
        if interesting_graph:
            print(f"  dot -Tpng {reduced_path.name} -o dependency_dag_{case}_reduced.png")


@pytest.mark.exploration
def test_compare_bivariate_multivariate_implications():
    """
    Compare implication structures between bivariate and multivariate.

    Identifies implications that exist in one case but not the other.
    """
    print("\n" + "="*80)
    print("EXPLORATION: Bivariate vs Multivariate Implication Comparison")
    print("="*80)

    biv_graph = build_implication_graph("bivariate")
    multi_graph = build_implication_graph("multivariate")

    # Convert to sets of (premise, conclusion) pairs
    biv_implications = {
        (prop, neighbor)
        for prop, neighbors in biv_graph.items()
        for neighbor in neighbors
    }

    multi_implications = {
        (prop, neighbor)
        for prop, neighbors in multi_graph.items()
        for neighbor in neighbors
    }

    # Find differences
    biv_only = biv_implications - multi_implications
    multi_only = multi_implications - biv_implications
    common = biv_implications & multi_implications

    print(f"\nCommon implications: {len(common)}")
    print(f"Bivariate-only implications: {len(biv_only)}")
    print(f"Multivariate-only implications: {len(multi_only)}")

    if biv_only:
        print("\nBivariate-only implications:")
        for premise, conclusion in sorted(biv_only)[:10]:
            print(f"  {premise} ⇒ {conclusion}")

    if multi_only:
        print("\nMultivariate-only implications:")
        for premise, conclusion in sorted(multi_only)[:10]:
            print(f"  {premise} ⇒ {conclusion}")

    # Save findings
    findings = {
        "Summary": {
            "Total bivariate implications": len(biv_implications),
            "Total multivariate implications": len(multi_implications),
            "Common to both": len(common),
            "Bivariate-only": len(biv_only),
            "Multivariate-only": len(multi_only)
        },
        "Bivariate-Only Implications": [
            f"{premise} ⇒ {conclusion}" for premise, conclusion in sorted(biv_only)
        ] if biv_only else ["None"],
        "Multivariate-Only Implications": [
            f"{premise} ⇒ {conclusion}" for premise, conclusion in sorted(multi_only)
        ] if multi_only else ["None"],
        "Interpretation": [
            "Implications that exist in one case but not the other reveal structural differences.",
            "Multivariate-only implications: Properties become more related for n≥3.",
            "Bivariate-only implications: Properties that decouple for n≥3."
        ]
    }

    findings_path = save_findings_to_markdown(
        findings,
        "implication_comparison.md",
        title="Implication Comparison: Bivariate vs Multivariate",
        description="Differences in implication structure between n=2 and n≥3"
    )

    print(f"\nFindings saved to: {findings_path}")

    assert len(common) > 0  # Should have some common implications
