"""Filtering utilities for reducible conflicts."""
import z3
from typing import List
from ..solver.axioms import P, STRONG_WEAK_PAIRS


def strong_weak_reducible(props: List[str], solver: z3.Solver) -> bool:
    """
    Check if property set is reducible to weaker version.

    A conflict is "reducible" if replacing a strong property with its
    weak counterpart still yields a conflict. For example, if
    {SR, ID, TC} is a conflict and {SR, IID, TC} is also a conflict,
    then the first is reducible (since ID => IID).

    Parameters
    ----------
    props : List[str]
        Property names to check
    solver : z3.Solver
        Solver with axioms loaded

    Returns
    -------
    bool
        True if set can be reduced to weaker set
    """
    # Check if any strong property in props can be replaced with its weak version
    for strong, weak in STRONG_WEAK_PAIRS:
        if strong in props and weak not in props:
            # Try replacing strong with weak
            weakened_props = [weak if p == strong else p for p in props]
            # Check if the weakened set is still a conflict
            solver.push()
            result = solver.check(z3.And([P[p] for p in weakened_props]))
            solver.pop()
            if result == z3.unsat:
                # The weakened set is still inconsistent, so original is reducible
                return True

    return False
