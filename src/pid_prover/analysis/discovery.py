"""Theorem discovery: conflicts and implications."""
import z3
import itertools
from typing import Literal, List, Tuple
from ..solver import get_pid_solver
from ..solver.axioms import P, prop_names
from ..filtering import strong_weak_reducible


def get_ordered_properties(solver: z3.Solver) -> List[str]:
    """
    Sort properties from weakest to strongest by logical implication.

    A property p1 is "stronger" than p2 if p1 => p2.

    Parameters
    ----------
    solver : z3.Solver
        Solver with axioms loaded

    Returns
    -------
    List[str]
        Property names sorted from weakest to strongest
    """
    def is_stronger(p1: str, p2: str) -> bool:
        """Returns True if p1 => p2 (i.e., p1 is stronger or equal to p2)"""
        solver.push()
        solver.add(P[p1])
        result = solver.check(z3.Not(P[p2])) == z3.unsat
        solver.pop()
        return result

    # Simple bubble sort based on logical implication
    sorted_props = list(prop_names)
    for i in range(len(sorted_props)):
        for j in range(i + 1, len(sorted_props)):
            if is_stronger(sorted_props[i], sorted_props[j]):
                # Move the weaker property to the left
                sorted_props[i], sorted_props[j] = sorted_props[j], sorted_props[i]
    return sorted_props


def find_minimal_conflicts(
    n: Literal["bivariate", "multivariate"] = "bivariate",
    max_size: int = 4,
    filter_reducible: bool = True
) -> List[List[str]]:
    """
    Find minimal, non-trivial conflicts (inconsistent property sets).

    Prioritizes weaker properties to find more general conflicts.

    Parameters
    ----------
    n : {"bivariate", "multivariate"}
        Case to search in
    max_size : int, default=4
        Maximum conflict set size
    filter_reducible : bool, default=True
        Filter out reducible conflicts

    Returns
    -------
    List[List[str]]
        Minimal conflict sets
    """
    solver = get_pid_solver(n)
    ordered_props = get_ordered_properties(solver)
    known_conflicts = []

    print(f"\n--- Searching for Minimal Conflicts (n={n}, max_size={max_size}) ---")

    for size in range(2, max_size + 1):
        # Use ordered_props to ensure we check weaker properties first (IID before ID)
        for combo_names in itertools.combinations(ordered_props, size):

            # Filter 1: Subset - skip if a subset is already a known conflict
            if any(set(prev).issubset(set(combo_names)) for prev in known_conflicts):
                continue

            # Filter 2: Reducibility - skip if conflict is reducible to weaker version
            if filter_reducible and strong_weak_reducible(list(combo_names), solver):
                continue

            # Check for conflict
            if solver.check(z3.And([P[name] for name in combo_names])) == z3.unsat:
                print(f"  NEW CONFLICT: {{{', '.join(combo_names)}}}")
                known_conflicts.append(list(combo_names))

    return known_conflicts


def find_minimal_implications(
    n: Literal["bivariate", "multivariate"] = "bivariate",
    premise_size: int = 2
) -> List[Tuple[Tuple[str, ...], str]]:
    """
    Find minimal implications: (Premises) => Conclusion.

    Filters trivial implications where proper subset proves conclusion
    or conclusion implies a premise (circular logic).

    Parameters
    ----------
    n : {"bivariate", "multivariate"}
        Case to search in
    premise_size : int, default=2
        Number of premises in implication

    Returns
    -------
    List[Tuple[Tuple[str, ...], str]]
        List of (premises, conclusion) tuples
    """
    print(f"\n--- Searching for Minimal Implications (n={n}, premise_size={premise_size}) ---")
    solver = get_pid_solver(n)
    found_implications = []

    for combo in itertools.permutations(prop_names, premise_size + 1):
        premises = combo[:-1]
        conclusion = combo[-1]

        # Check if premises => conclusion
        solver.push()
        solver.add(z3.And([P[name] for name in premises]))
        solver.add(z3.Not(P[conclusion]))

        if solver.check() == z3.unsat:
            # Minimality check: no proper subset of premises should prove conclusion
            is_minimal = True
            for size in range(1, len(premises)):
                if not is_minimal:
                    break
                for sub in itertools.combinations(premises, size):
                    solver.pop()
                    solver.push()
                    solver.add(z3.And([P[s] for s in sub]))
                    solver.add(z3.Not(P[conclusion]))
                    if solver.check() == z3.unsat:
                        is_minimal = False
                        break

            if is_minimal:
                # Filter circular implications: conclusion shouldn't imply any premise
                is_circular = False
                for pre in premises:
                    solver.pop()
                    solver.push()
                    solver.add(P[conclusion])
                    solver.add(z3.Not(P[pre]))
                    if solver.check() == z3.unsat:
                        is_circular = True
                        break

                if not is_circular:
                    print(f"  NEW IMPLICATION: {' ∧ '.join(premises)} => {conclusion}")
                    found_implications.append((premises, conclusion))

        solver.pop()

    return found_implications
