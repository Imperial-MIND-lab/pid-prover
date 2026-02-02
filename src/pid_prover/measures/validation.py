"""Measure validation against PID axioms."""
from typing import Literal, List
from ..solver import get_pid_solver
from ..solver.axioms import P, prop_names
from .data import measures_df, bivariate_only_measures
import z3


def dataframe_to_property_list(
    measure_name: str,
    n: Literal["bivariate", "multivariate"]
) -> List[str]:
    """
    Convert DataFrame column to list of satisfied properties.

    Parameters
    ----------
    measure_name : str
        Name of the measure (e.g., "I_min")
    n : {"bivariate", "multivariate"}
        The case to consider

    Returns
    -------
    List[str]
        Property names satisfied for this measure and case

    Notes
    -----
    Encoding handling:
    - "Y": Always satisfied
    - "Y_2": Satisfied for bivariate only
    - "Y_*": Empirically supported (treated as satisfied)
    - "N", "N_A", "N_dd", "N_m": Not satisfied (excluded)
    """
    satisfied = []
    for prop, value in measures_df[measure_name].items():
        if value == "Y":
            # Always satisfied
            satisfied.append(prop)
        elif value == "Y_2" and n == "bivariate":
            # Bivariate-only property
            satisfied.append(prop)
        elif value == "Y_*":
            # Empirically supported - treat as satisfied
            satisfied.append(prop)
        # Skip: "N", "N_A", "Y_2" (when multivariate), "N_dd", "N_m"

    return satisfied


def validate_measures() -> bool:
    """
    Validate all measures for logical consistency.

    Validates each measure for both bivariate (n=2) and multivariate
    (n>=3) cases. Bivariate-only measures are skipped for multivariate.

    Returns
    -------
    bool
        True if all measures pass validation, False otherwise

    Notes
    -----
    Known issue: 5 measures fail multivariate validation due to
    Theorem 2 conflict. See measures.data.MULTIVARIATE_CONFLICTS.
    """
    print("\n" + "="*80)
    print("MEASURE VALIDATION")
    print("="*80)

    all_passed = True

    for case in ["bivariate", "multivariate"]:
        print(f"\n{'='*80}")
        print(f"Case: {case.upper()} ({'n=2' if case == 'bivariate' else 'n>=3'})")
        print(f"{'='*80}\n")

        case_passed = True

        for measure_name in measures_df.columns:
            # Skip bivariate-only measures for multivariate case
            if case == "multivariate" and measure_name in bivariate_only_measures:
                print(f"  {measure_name.ljust(12)}: ⊘ SKIP (bivariate-only)")
                continue

            solver = get_pid_solver(case)
            satisfied_props = dataframe_to_property_list(measure_name, case)
            constraints = [P[prop] for prop in satisfied_props if prop in prop_names]

            result = solver.check(z3.And(constraints)) if constraints else z3.sat
            status = "✓ PASS" if result == z3.sat else "✗ FAIL"

            if result != z3.sat:
                case_passed = False
                all_passed = False

            print(f"  {measure_name.ljust(12)}: {status}")

        if not case_passed:
            print(f"\n  WARNING: Some measures failed for {case} case!")

    print("\n" + "="*80)
    if all_passed:
        print("✓ ALL MEASURES PASSED VALIDATION")
    else:
        print("✗ SOME MEASURES FAILED - CHECK OUTPUT ABOVE")
    print("="*80 + "\n")

    return all_passed
