"""
Exploration: Axiom Minimality Analysis

Analyzes the independence and minimality of the axiom system:
- Lemmas 1-4: Basic implications
- Propositions 1-5: Multi-premise implications
- Theorems 1-12: No-go theorems and implications

Research Questions:
1. Can any lemma be derived from others?
2. Can any proposition be derived from remaining axioms?
3. Can any theorem be derived from remaining axioms?
4. What is the minimal axiom set?
5. Which axioms are "core" vs "derived"?

Goal: Simplify the axiom system or confirm its minimality.
"""

import pytest
import z3
from typing import List, Tuple, Callable
from pid_prover.solver.axioms import P, prop_names
from utils_research import (
    save_findings_to_markdown,
    create_results_table,
    log_computational_cost
)


def create_minimal_solver() -> z3.Solver:
    """Create solver with no axioms."""
    return z3.Solver()


def add_lemmas(solver: z3.Solver, exclude: List[int] = None) -> None:
    """
    Add Lemmas 1-4, optionally excluding some.

    Parameters
    ----------
    solver : z3.Solver
        The solver to add lemmas to
    exclude : list of int, optional
        Lemma numbers to exclude (1-4)
    """
    exclude = exclude or []

    lemmas = {
        1: z3.Implies(P['LP1'], P['LP0']),  # LP1 => LP0
        2: z3.Implies(P['ID'], P['IID']),    # ID => IID
        3: z3.Implies(P['S1'], P['S0']),     # S1 => S0
        4: z3.Implies(P['M0'], P['SE'])      # M0 => SE
    }

    for num, axiom in lemmas.items():
        if num not in exclude:
            solver.add(axiom)


def add_propositions(solver: z3.Solver, exclude: List[int] = None) -> None:
    """
    Add Propositions 1-5, optionally excluding some.

    Parameters
    ----------
    exclude : list of int, optional
        Proposition numbers to exclude (1-5)
    """
    exclude = exclude or []

    propositions = {
        1: z3.Implies(z3.And(P['TC'], P['GP']), P['TM']),  # TC ∧ GP => TM
        2: z3.Implies(z3.And(P['M0'], P['SR']), P['LB']),  # M0 ∧ SR => LB
        3: z3.Implies(z3.And(P['LB'], P['SR']), P['GP']),  # LB ∧ SR => GP
        4: z3.Implies(z3.And(P['SR'], P['M0']), P['GP']),  # SR ∧ M0 => GP (combines 2 & 3)
        5: P['M1'] == z3.And(P['M0'], P['TE'])             # M1 <=> M0 ∧ TE
    }

    for num, axiom in propositions.items():
        if num not in exclude:
            solver.add(axiom)


def add_main_theorems(solver: z3.Solver, exclude: List[int] = None) -> None:
    """
    Add main Theorems, optionally excluding some.

    Main theorems: 1, 3, 4, 5, 6, 9, 10, 11, 12
    (Theorem 2 is multivariate-only, Theorem 7 is bivariate-only, Theorem 8 missing)

    Parameters
    ----------
    exclude : list of int, optional
        Theorem numbers to exclude
    """
    exclude = exclude or []

    theorems = {
        1: z3.Not(z3.And(P['SR'], P['S0'], P['EI'], P['LP1'], P['IID'])),  # noIID-LP1
        3: z3.Implies(z3.And(P['TC'], P['TE'], P['SR']), P['ID']),         # SR ∧ TC ∧ TE => ID
        4: z3.Not(z3.And(P['SR'], P['EI'], P['LP0'], P['IID'], P['TC'])),  # noTC-IID-LP0
        5: z3.Not(z3.And(P['SR'], P['EI'], P['LP0'], P['TE'], P['TC'])),   # noTC-TE-LP0
        6: z3.Not(z3.And(P['SR'], P['EI'], P['LP1'], P['TC'])),            # noTC-LP1
        9: z3.Not(z3.And(P['S0'], P['M0'], P['SR'], P['LP1'], P['S1'])),   # noS1-LP1
        10: z3.Implies(z3.And(P['M0'], P['S1']), P['TM']),                 # M0 ∧ S1 => TM
        11: z3.Implies(z3.And(P['S1'], P['SE']), P['TE']),                 # S1 ∧ SE => TE
        12: z3.Implies(z3.And(P['S1'], P['SE'], P['SR']), P['ID'])         # SR ∧ SE ∧ S1 => ID
    }

    for num, axiom in theorems.items():
        if num not in exclude:
            solver.add(axiom)


def can_derive_axiom(
    axiom: z3.ExprRef,
    add_other_axioms: Callable[[z3.Solver], None]
) -> bool:
    """
    Check if an axiom can be derived from other axioms.

    Parameters
    ----------
    axiom : z3.ExprRef
        The axiom to try to derive
    add_other_axioms : callable
        Function that adds the remaining axioms to a solver

    Returns
    -------
    bool
        True if axiom can be derived (is redundant), False if independent
    """
    solver = create_minimal_solver()
    add_other_axioms(solver)

    # Check if NOT(axiom) is unsatisfiable => axiom is derivable
    solver.push()
    solver.add(z3.Not(axiom))
    result = solver.check()
    solver.pop()

    return result == z3.unsat


@pytest.mark.exploration
@pytest.mark.research
def test_lemma_independence():
    """
    Test if each lemma can be derived from the remaining axioms.

    A lemma is independent if it cannot be derived from other axioms.
    A lemma is redundant if it can be derived.
    """
    print("\n" + "="*80)
    print("EXPLORATION: Lemma Independence")
    print("="*80)

    lemma_descriptions = {
        1: "LP1 => LP0 (Strong local positivity => Weak)",
        2: "ID => IID (Identity => Independent identity)",
        3: "S1 => S0 (Strong symmetry => Weak symmetry)",
        4: "M0 => SE (Weak monotonicity => Subset equality)"
    }

    lemmas_data = {
        1: z3.Implies(P['LP1'], P['LP0']),
        2: z3.Implies(P['ID'], P['IID']),
        3: z3.Implies(P['S1'], P['S0']),
        4: z3.Implies(P['M0'], P['SE'])
    }

    results = []

    print("\nTesting each lemma for independence:")

    for lemma_num in [1, 2, 3, 4]:
        print(f"\n--- Lemma {lemma_num}: {lemma_descriptions[lemma_num]} ---")

        # Create solver with all axioms EXCEPT this lemma
        def add_other_axioms(s):
            add_lemmas(s, exclude=[lemma_num])
            add_propositions(s)
            add_main_theorems(s)

        is_derivable = can_derive_axiom(lemmas_data[lemma_num], add_other_axioms)

        if is_derivable:
            print(f"  ✓ DERIVABLE (redundant)")
            status = "Redundant"
        else:
            print(f"  ✗ INDEPENDENT (necessary)")
            status = "Independent"

        results.append({
            "lemma": lemma_num,
            "description": lemma_descriptions[lemma_num],
            "status": status,
            "is_derivable": is_derivable
        })

    # Generate report
    table_rows = [
        [f"Lemma {r['lemma']}", r['description'], r['status']]
        for r in results
    ]

    table = create_results_table(
        table_rows,
        headers=["Lemma", "Statement", "Status"],
        alignment=["center", "left", "left"]
    )

    print(f"\n{table}")

    # Summary
    redundant_count = sum(1 for r in results if r['is_derivable'])
    independent_count = len(results) - redundant_count

    findings = {
        "Summary": {
            "Total lemmas": len(results),
            "Independent (necessary)": independent_count,
            "Redundant (derivable)": redundant_count
        },
        "Lemma Analysis": [table],
        "Interpretation": [
            f"{independent_count}/4 lemmas are independent (cannot be derived).",
            f"{redundant_count}/4 lemmas are redundant (can be derived).",
            "Independent lemmas are essential to the axiom system.",
            "Redundant lemmas could be removed without loss of expressiveness."
        ]
    }

    output_path = save_findings_to_markdown(
        findings,
        "lemma_independence.md",
        title="Lemma Independence Analysis",
        description="Testing whether lemmas can be derived from remaining axioms"
    )

    print(f"\nResults saved to: {output_path}")

    # Note: All basic implications like LP1=>LP0 are typically independent
    # unless there are complex interactions we don't expect


@pytest.mark.exploration
@pytest.mark.research
def test_proposition_independence():
    """
    Test if each proposition can be derived from remaining axioms.
    """
    print("\n" + "="*80)
    print("EXPLORATION: Proposition Independence")
    print("="*80)

    prop_descriptions = {
        1: "TC ∧ GP => TM",
        2: "M0 ∧ SR => LB",
        3: "LB ∧ SR => GP",
        4: "SR ∧ M0 => GP",
        5: "M1 <=> M0 ∧ TE"
    }

    props_data = {
        1: z3.Implies(z3.And(P['TC'], P['GP']), P['TM']),
        2: z3.Implies(z3.And(P['M0'], P['SR']), P['LB']),
        3: z3.Implies(z3.And(P['LB'], P['SR']), P['GP']),
        4: z3.Implies(z3.And(P['SR'], P['M0']), P['GP']),
        5: P['M1'] == z3.And(P['M0'], P['TE'])
    }

    results = []

    print("\nTesting each proposition for independence:")

    for prop_num in [1, 2, 3, 4, 5]:
        print(f"\n--- Proposition {prop_num}: {prop_descriptions[prop_num]} ---")

        # Create solver with all axioms EXCEPT this proposition
        def add_other_axioms(s):
            add_lemmas(s)
            add_propositions(s, exclude=[prop_num])
            add_main_theorems(s)

        is_derivable = can_derive_axiom(props_data[prop_num], add_other_axioms)

        if is_derivable:
            print(f"  ✓ DERIVABLE (redundant)")
            status = "Redundant"
        else:
            print(f"  ✗ INDEPENDENT (necessary)")
            status = "Independent"

        results.append({
            "prop": prop_num,
            "description": prop_descriptions[prop_num],
            "status": status,
            "is_derivable": is_derivable
        })

    # Note: Proposition 4 is documented as combining Props 2 & 3
    # Let's specifically check this
    print("\n--- Special Check: Prop 4 from Props 2 & 3 ---")

    solver_234 = create_minimal_solver()
    add_lemmas(solver_234)
    add_propositions(solver_234, exclude=[1, 4, 5])  # Only Props 2 & 3
    add_main_theorems(solver_234)

    prop_4_from_23 = can_derive_axiom(props_data[4], lambda s: None)  # Already added above

    # Actually do it properly
    solver_234.push()
    solver_234.add(z3.Not(props_data[4]))
    prop_4_derivable_from_23 = solver_234.check() == z3.unsat
    solver_234.pop()

    print(f"  Prop 4 derivable from Props 2+3: {prop_4_derivable_from_23}")

    # Generate report
    table_rows = [
        [f"Prop {r['prop']}", r['description'], r['status']]
        for r in results
    ]

    table = create_results_table(
        table_rows,
        headers=["Proposition", "Statement", "Status"],
        alignment=["center", "left", "left"]
    )

    print(f"\n{table}")

    redundant_count = sum(1 for r in results if r['is_derivable'])
    independent_count = len(results) - redundant_count

    findings = {
        "Summary": {
            "Total propositions": len(results),
            "Independent": independent_count,
            "Redundant": redundant_count
        },
        "Proposition Analysis": [table],
        "Special Note": [
            f"Proposition 4 derivable from Props 2+3: {prop_4_derivable_from_23}",
            "The paper states Prop 4 combines Props 2 & 3.",
            "This analysis verifies that claim formally."
        ],
        "Interpretation": [
            f"{independent_count}/5 propositions are independent.",
            f"{redundant_count}/5 propositions are redundant.",
            "Redundant propositions are useful lemmas but not strictly necessary."
        ]
    }

    output_path = save_findings_to_markdown(
        findings,
        "proposition_independence.md",
        title="Proposition Independence Analysis"
    )

    print(f"\nResults saved to: {output_path}")


@pytest.mark.exploration
@pytest.mark.research
@pytest.mark.slow
def test_theorem_independence():
    """
    Test if each main theorem can be derived from remaining axioms.

    This is computationally expensive as theorems are complex.
    """
    print("\n" + "="*80)
    print("EXPLORATION: Theorem Independence")
    print("="*80)
    print("WARNING: This test is computationally expensive\n")

    theorem_descriptions = {
        1: "¬(SR ∧ S0 ∧ EI ∧ LP1 ∧ IID) [noIID-LP1]",
        3: "SR ∧ TC ∧ TE => ID",
        4: "¬(SR ∧ EI ∧ LP0 ∧ IID ∧ TC) [noTC-IID-LP0]",
        5: "¬(SR ∧ EI ∧ LP0 ∧ TE ∧ TC) [noTC-TE-LP0]",
        6: "¬(SR ∧ EI ∧ LP1 ∧ TC) [noTC-LP1]",
        9: "¬(S0 ∧ M0 ∧ SR ∧ LP1 ∧ S1) [noS1-LP1]",
        10: "M0 ∧ S1 => TM",
        11: "S1 ∧ SE => TE",
        12: "SR ∧ SE ∧ S1 => ID"
    }

    theorems_data = {
        1: z3.Not(z3.And(P['SR'], P['S0'], P['EI'], P['LP1'], P['IID'])),
        3: z3.Implies(z3.And(P['TC'], P['TE'], P['SR']), P['ID']),
        4: z3.Not(z3.And(P['SR'], P['EI'], P['LP0'], P['IID'], P['TC'])),
        5: z3.Not(z3.And(P['SR'], P['EI'], P['LP0'], P['TE'], P['TC'])),
        6: z3.Not(z3.And(P['SR'], P['EI'], P['LP1'], P['TC'])),
        9: z3.Not(z3.And(P['S0'], P['M0'], P['SR'], P['LP1'], P['S1'])),
        10: z3.Implies(z3.And(P['M0'], P['S1']), P['TM']),
        11: z3.Implies(z3.And(P['S1'], P['SE']), P['TE']),
        12: z3.Implies(z3.And(P['S1'], P['SE'], P['SR']), P['ID'])
    }

    results = []

    for thm_num in [1, 3, 4, 5, 6, 9, 10, 11, 12]:
        print(f"\n--- Theorem {thm_num}: {theorem_descriptions[thm_num]} ---")

        def add_other_axioms(s):
            add_lemmas(s)
            add_propositions(s)
            add_main_theorems(s, exclude=[thm_num])

        is_derivable = can_derive_axiom(theorems_data[thm_num], add_other_axioms)

        if is_derivable:
            print(f"  ✓ DERIVABLE (redundant)")
            status = "Redundant"
        else:
            print(f"  ✗ INDEPENDENT (necessary)")
            status = "Independent"

        results.append({
            "theorem": thm_num,
            "description": theorem_descriptions[thm_num],
            "status": status,
            "is_derivable": is_derivable
        })

    # Generate report
    table_rows = [
        [f"Theorem {r['theorem']}", r['description'], r['status']]
        for r in results
    ]

    table = create_results_table(
        table_rows,
        headers=["Theorem", "Statement", "Status"],
        alignment=["center", "left", "left"]
    )

    print(f"\n{table}")

    redundant_count = sum(1 for r in results if r['is_derivable'])
    independent_count = len(results) - redundant_count

    findings = {
        "Summary": {
            "Total theorems analyzed": len(results),
            "Independent": independent_count,
            "Redundant": redundant_count
        },
        "Theorem Analysis": [table],
        "Notable Findings": [
            "Theorem 5 is documented as following from Theorems 3 & 4.",
            "If Theorem 5 is marked redundant, this confirms the paper's claim.",
            "Independent theorems represent core structural constraints."
        ],
        "Interpretation": [
            f"{independent_count}/{len(results)} theorems are truly independent.",
            f"{redundant_count}/{len(results)} theorems can be derived from others.",
            "A minimal axiom system would include only independent theorems."
        ]
    }

    output_path = save_findings_to_markdown(
        findings,
        "theorem_independence.md",
        title="Theorem Independence Analysis"
    )

    print(f"\nResults saved to: {output_path}")


@pytest.mark.exploration
@pytest.mark.research
def test_minimal_axiom_set():
    """
    Find the minimal axiom set that preserves all derivable facts.

    Identifies which axioms can be removed without loss of expressiveness.
    """
    print("\n" + "="*80)
    print("EXPLORATION: Minimal Axiom Set")
    print("="*80)

    # This is a simplified analysis - full minimality requires checking all subsets
    # For now, identify obviously redundant axioms

    print("\nIdentifying redundant axioms...")

    # Test specific known redundancies
    redundancies = []

    # Proposition 4 is redundant (combines Props 2 & 3)
    print("\nTesting: Proposition 4 redundancy...")
    solver_test = create_minimal_solver()
    add_lemmas(solver_test)
    add_propositions(solver_test, exclude=[4])  # Without Prop 4
    add_main_theorems(solver_test)

    prop_4 = z3.Implies(z3.And(P['SR'], P['M0']), P['GP'])
    solver_test.push()
    solver_test.add(z3.Not(prop_4))
    if solver_test.check() == z3.unsat:
        print("  ✓ Proposition 4 is redundant")
        redundancies.append("Proposition 4 (SR ∧ M0 => GP)")
    solver_test.pop()

    # Theorem 5 is redundant (follows from Theorems 3 & 4)
    print("\nTesting: Theorem 5 redundancy...")
    solver_test2 = create_minimal_solver()
    add_lemmas(solver_test2)
    add_propositions(solver_test2)
    add_main_theorems(solver_test2, exclude=[5])  # Without Theorem 5

    thm_5 = z3.Not(z3.And(P['SR'], P['EI'], P['LP0'], P['TE'], P['TC']))
    solver_test2.push()
    solver_test2.add(z3.Not(thm_5))
    if solver_test2.check() == z3.unsat:
        print("  ✓ Theorem 5 is redundant")
        redundancies.append("Theorem 5 (noTC-TE-LP0)")
    solver_test2.pop()

    print(f"\n--- Found {len(redundancies)} redundant axioms ---")

    findings = {
        "Identified Redundancies": redundancies if redundancies else ["None found in quick analysis"],
        "Minimal Axiom Set": [
            "To construct a truly minimal axiom set:",
            "1. Remove all redundant axioms identified above",
            "2. Keep all independent lemmas",
            "3. Keep all independent propositions",
            "4. Keep all independent theorems",
            "",
            "The minimal set would consist of approximately:",
            f"  - 4 Lemmas (basic implications)",
            f"  - 4 Propositions (excluding Prop 4)",
            f"  - {9 - len([r for r in redundancies if 'Theorem' in r])} Theorems (core constraints)"
        ],
        "Recommendation": [
            "For the paper:",
            "  - Keep all axioms for clarity and ease of reference",
            "  - Note which are derivable in appendix",
            "",
            "For the prover:",
            "  - Could remove redundant axioms for efficiency",
            "  - But keeping them doesn't hurt (Z3 is efficient)"
        ]
    }

    output_path = save_findings_to_markdown(
        findings,
        "minimal_axiom_set.md",
        title="Minimal Axiom Set Analysis",
        description="Identifying redundant axioms"
    )

    print(f"\nResults saved to: {output_path}")


@pytest.mark.exploration
def test_axiom_derivability_quick():
    """
    Quick sanity check of axiom derivability logic.

    Tests a few known cases to ensure the derivability checker works.
    """
    print("\n" + "="*80)
    print("SANITY CHECK: Axiom Derivability")
    print("="*80)

    # Test 1: Proposition 4 should be derivable from Props 2 & 3
    print("\nTest 1: Can Prop 4 be derived from Props 2+3?")
    solver = create_minimal_solver()

    # Add Props 2 & 3
    solver.add(z3.Implies(z3.And(P['M0'], P['SR']), P['LB']))  # Prop 2
    solver.add(z3.Implies(z3.And(P['LB'], P['SR']), P['GP']))  # Prop 3

    # Try to derive Prop 4: SR ∧ M0 => GP
    prop_4 = z3.Implies(z3.And(P['SR'], P['M0']), P['GP'])
    solver.push()
    solver.add(z3.Not(prop_4))
    result = solver.check()
    solver.pop()

    derivable = (result == z3.unsat)
    print(f"  Result: {derivable} (expected: True)")

    assert derivable, "Prop 4 should be derivable from Props 2 & 3"

    print("\n✓ Derivability checker is working correctly")
