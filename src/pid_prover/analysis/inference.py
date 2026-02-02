"""Property consequence inference."""
import z3
from typing import Literal, List, Dict
from ..solver import get_pid_solver
from ..solver.axioms import P, prop_names


def infer_property_consequences(
    intended_props: List[str],
    n: Literal["bivariate", "multivariate"] = "bivariate"
) -> Dict[str, List[str]]:
    """
    Analyze what properties are forced or forbidden.

    Given a set of intended properties, determines which additional
    properties are logically mandatory or forbidden.

    Parameters
    ----------
    intended_props : List[str]
        Properties the measure is intended to satisfy
    n : {"bivariate", "multivariate"}
        Case to analyze

    Returns
    -------
    Dict[str, List[str]]
        Dictionary with "Mandatory" and "Forbidden" keys
    """
    solver = get_pid_solver(n)
    solver.add(z3.And([P[name] for name in intended_props]))

    if solver.check() == z3.unsat:
        print(f"\nERROR: Properties {intended_props} are already inconsistent for n={n}!")
        return {"Mandatory": [], "Forbidden": []}

    results = {"Mandatory": [], "Forbidden": []}
    for name in prop_names:
        if name in intended_props:
            continue

        # Check if forced: (Axioms & Intended) => Property
        solver.push()
        if solver.check(z3.Not(P[name])) == z3.unsat:
            results["Mandatory"].append(name)
        solver.pop()

        # Check if forbidden: (Axioms & Intended & Property) => Conflict
        solver.push()
        if solver.check(P[name]) == z3.unsat:
            results["Forbidden"].append(name)
        solver.pop()

    print(f"\n--- Property Inference for {intended_props} (n={n}) ---")
    print(f"  MUST satisfy: {results['Mandatory'] if results['Mandatory'] else 'None'}")
    print(f"  CANNOT satisfy: {results['Forbidden'] if results['Forbidden'] else 'None'}")

    return results
