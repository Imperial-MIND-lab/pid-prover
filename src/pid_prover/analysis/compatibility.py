"""Maximal compatible property set discovery."""
import z3
from typing import Literal, List
from ..solver import get_pid_solver
from ..solver.axioms import P, prop_names
from ..measures.data import measures_df
from ..measures.validation import dataframe_to_property_list


def find_maximal_compatible_sets(
    n: Literal["bivariate", "multivariate"] = "bivariate",
    min_size: int = 10
) -> List[List[str]]:
    """
    Find maximal sets of mutually compatible properties.

    Parameters
    ----------
    n : {"bivariate", "multivariate"}
        Case to search in
    min_size : int, default=10
        Minimum set size to report

    Returns
    -------
    List[List[str]]
        Maximal compatible property sets
    """
    print(f"\n--- Searching for Maximal Compatible Property Sets (n={n}) ---")
    solver = get_pid_solver(n)
    maximal_sets = []

    # Start with all properties and try to find large consistent subsets
    # Use a greedy approach: start with successful measures and try to extend
    for measure_name in measures_df.columns:
        # Get properties for this measure and case
        measure_props = dataframe_to_property_list(measure_name, n)

        # Check if this measure's properties are consistent
        solver.push()
        constraints = [P[prop] for prop in measure_props if prop in prop_names]
        if solver.check(z3.And(constraints)) == z3.sat:
            # Try to add more properties
            current_set = set(measure_props)
            for prop in prop_names:
                if prop not in current_set:
                    solver.pop()
                    solver.push()
                    test_set = current_set | {prop}
                    if solver.check(z3.And([P[p] for p in test_set if p in prop_names])) == z3.sat:
                        current_set.add(prop)

            if len(current_set) >= min_size:
                # Check if this is truly maximal (not a subset of existing)
                is_maximal = True
                for existing in maximal_sets:
                    existing_set = set(existing)
                    if current_set.issubset(existing_set):
                        is_maximal = False
                        break
                    elif existing_set < current_set:  # existing is proper subset
                        maximal_sets.remove(existing)

                if is_maximal:
                    maximal_sets.append(list(current_set))
                    print(f"  Found compatible set (size {len(current_set)}): {sorted(current_set)}")

        solver.pop()

    return maximal_sets
