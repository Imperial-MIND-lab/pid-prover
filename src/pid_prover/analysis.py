"""Automated reasoning on PID properties: consistency, conflicts, implications, inference."""
import itertools
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import z3

from .properties import Case, P, prop, prop_names
from .theorems import get_pid_solver


def is_consistent(props: Iterable[str], n: Case = "bivariate") -> bool:
    """True if the properties can hold together given the theorems."""
    return get_pid_solver(n).check([prop(p, n) for p in props]) == z3.sat


def implies(premises: Iterable[str], conclusion: str, n: Case = "bivariate") -> bool:
    """True if the premises entail the conclusion given the theorems."""
    solver = get_pid_solver(n)
    return solver.check([prop(p, n) for p in premises] + [z3.Not(prop(conclusion, n))]) == z3.unsat


def explain_assignment(assignment: Dict[str, bool], n: Case = "bivariate") -> Optional[List[str]]:
    """
    Check a (partial) truth assignment of properties against the theorems.

    Returns None if it is consistent, otherwise a minimal list of contradictory
    literals, e.g. ["SR", "M0", "¬LB"].
    """
    solver = get_pid_solver(n)
    literals = {(p if v else f"¬{p}"): (P[p] if v else z3.Not(P[p])) for p, v in assignment.items()}
    if solver.check(list(literals.values())) == z3.sat:
        return None
    # Deletion-based minimisation of the unsatisfiable core
    core = list(literals)
    for lit in list(core):
        rest = [literals[c] for c in core if c != lit]
        if solver.check(rest) == z3.unsat:
            core.remove(lit)
    return core


def implied_pairs(n: Case = "bivariate") -> Dict[str, List[str]]:
    """For each property, the other properties it implies on its own."""
    return {p: [q for q in prop_names if q != p and implies([p], q, n)] for p in prop_names}


def get_ordered_properties(n: Case = "bivariate") -> List[str]:
    """Properties sorted from weakest to strongest (by how many properties each implies)."""
    pairs = implied_pairs(n)
    return sorted(prop_names, key=lambda p: len(pairs[p]))


def find_minimal_conflicts(
    n: Case = "bivariate", max_size: int = 4, filter_reducible: bool = True, verbose: bool = False
) -> List[List[str]]:
    """
    Minimal sets of properties that cannot hold together (no-go theorems).

    Weaker properties are tried first. With filter_reducible, a conflict is dropped if
    replacing one of its properties with a strictly weaker one still gives a conflict,
    so that only the most general version is reported.
    """
    solver = get_pid_solver(n)
    pairs = implied_pairs(n)
    weaker = {p: [q for q in qs if p not in pairs[q]] for p, qs in pairs.items()}
    ordered = get_ordered_properties(n)

    def conflicting(names: Sequence[str]) -> bool:
        return solver.check([prop(x, n) for x in names]) == z3.unsat

    def reducible(names: Sequence[str]) -> bool:
        return any(
            conflicting([w if x == p else x for x in names])
            for p in names for w in weaker[p] if w not in names
        )

    conflicts: List[List[str]] = []
    for size in range(2, max_size + 1):
        for combo in itertools.combinations(ordered, size):
            if any(set(c) <= set(combo) for c in conflicts) or not conflicting(combo):
                continue
            if filter_reducible and reducible(combo):
                continue
            conflicts.append(list(combo))
            if verbose:
                print(f"  conflict: {{{', '.join(combo)}}}")
    return conflicts


def find_minimal_implications(
    n: Case = "bivariate", premise_size: int = 2, verbose: bool = False
) -> List[Tuple[Tuple[str, ...], str]]:
    """
    Implications premises => conclusion with exactly premise_size premises.

    Only minimal implications are returned: the premises are consistent and no proper
    subset of them implies the conclusion.
    """
    solver = get_pid_solver(n)

    def entails(premises: Sequence[str], conclusion: str) -> bool:
        return solver.check([prop(p, n) for p in premises] + [z3.Not(prop(conclusion, n))]) == z3.unsat

    found = []
    for premises in itertools.combinations(prop_names, premise_size):
        if solver.check([prop(p, n) for p in premises]) == z3.unsat:
            continue
        for conclusion in prop_names:
            if conclusion in premises or not entails(premises, conclusion):
                continue
            if any(entails(sub, conclusion)
                   for k in range(1, premise_size)
                   for sub in itertools.combinations(premises, k)):
                continue
            found.append((premises, conclusion))
            if verbose:
                print(f"  implication: {' ∧ '.join(premises)} ⇒ {conclusion}")
    return found


def infer_property_consequences(
    intended_props: Iterable[str], n: Case = "bivariate", verbose: bool = False
) -> Dict[str, object]:
    """
    Properties forced or ruled out by a set of intended properties.

    Returns {"Consistent": bool, "Mandatory": [...], "Forbidden": [...]}. If the intended
    properties are themselves inconsistent, both lists are empty.
    """
    intended = list(intended_props)
    solver = get_pid_solver(n)
    solver.add([prop(p, n) for p in intended])
    results: Dict[str, object] = {"Consistent": solver.check() == z3.sat,
                                  "Mandatory": [], "Forbidden": []}
    if results["Consistent"]:
        for name in prop_names:
            if name in intended:
                continue
            if solver.check(z3.Not(prop(name, n))) == z3.unsat:
                results["Mandatory"].append(name)
            elif solver.check(prop(name, n)) == z3.unsat:
                results["Forbidden"].append(name)
    if verbose:
        print(f"Intended {intended} (n={n}):")
        if not results["Consistent"]:
            print("  inconsistent!")
        else:
            print(f"  must satisfy:   {results['Mandatory'] or 'none'}")
            print(f"  cannot satisfy: {results['Forbidden'] or 'none'}")
    return results


def find_maximal_compatible_sets(
    n: Case = "bivariate",
    required: Iterable[str] = (),
    excluded: Iterable[str] = (),
    min_size: int = 0,
) -> List[List[str]]:
    """
    All maximal sets of mutually compatible properties (exact enumeration).

    A set is maximal if adding any other property makes it inconsistent. Only sets that
    contain all the required properties and none of the excluded ones are considered, and
    only those with at least min_size properties are returned, sorted by size.
    """
    excluded = list(excluded)
    candidates = [p for p in prop_names if p not in excluded]
    solver = get_pid_solver(n)
    solver.add([prop(p, n) for p in required] + [z3.Not(prop(p, n)) for p in excluded])
    maximal = []
    while solver.check() == z3.sat:
        model = solver.model()
        current = [p for p in candidates
                   if z3.is_true(model.eval(prop(p, n), model_completion=True))]
        for p in candidates:
            if p not in current and solver.check([prop(q, n) for q in current + [p]]) == z3.sat:
                current.append(p)
        maximal.append([p for p in candidates if p in current])
        # Exclude this set and all its subsets from future solutions
        solver.add(z3.Or([prop(p, n) for p in candidates if p not in current]))
    return sorted((s for s in maximal if len(s) >= min_size), key=len, reverse=True)
