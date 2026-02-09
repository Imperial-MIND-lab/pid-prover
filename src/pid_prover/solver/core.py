"""Core Z3 solver initialization with PID axioms and theorems."""
import z3
from typing import Literal
from .axioms import P


def get_pid_solver(n: Literal["bivariate", "multivariate"]) -> z3.Solver:
    """
    Initializes a Z3 solver with PID theorems and propositions.

    Parameters
    ----------
    n : {"bivariate", "multivariate"}
        Number of sources: "bivariate" (n=2) or "multivariate" (n>=3)

    Returns
    -------
    z3.Solver
        Solver with appropriate axioms loaded
    """
    solver = z3.Solver()

    # Add basic implications (Lemmas)
    _add_basic_implications(solver)

    # Add propositions
    _add_propositions(solver)

    # Add main theorems
    _add_main_theorems(solver)

    # Add case-specific theorems
    if n == "bivariate":
        _add_bivariate_theorems(solver)
    elif n == "multivariate":
        _add_multivariate_theorems(solver)

    return solver


def _add_basic_implications(solver: z3.Solver) -> None:
    """Add Lemmas 1-4 (basic implications)."""
    # Lemma 1: LP1 => LP0  (strong local positivity implies weak)
    solver.add(z3.Implies(P['LP1'], P['LP0']))

    # Lemma 2: ID => IID  (identity implies independent identity)
    solver.add(z3.Implies(P['ID'], P['IID']))

    # Lemma 3: S1 => S0  (strong symmetry implies weak symmetry)
    solver.add(z3.Implies(P['S1'], P['S0']))

    # Lemma 4: M0 => SE  (weak monotonicity implies subset equality)
    solver.add(z3.Implies(P['M0'], P['SE']))


def _add_propositions(solver: z3.Solver) -> None:
    """Add Propositions 1-5."""
    # Proposition 1: TC ∧ GP => TM
    solver.add(z3.Implies(z3.And(P['TC'], P['GP']), P['TM']))

    # Proposition 2: M0 ∧ SR => LB
    solver.add(z3.Implies(z3.And(P['M0'], P['SR']), P['LB']))

    # Proposition 3: LB ∧ SR => GP
    solver.add(z3.Implies(z3.And(P['LB'], P['SR']), P['GP']))

    # Proposition 4 (equivalent): M0 ∧ SR => GP (combines Props 2 & 3)
    solver.add(z3.Implies(z3.And(P['SR'], P['M0']), P['GP']))

    # Proposition 5: M0 ∧ TE <=> M1
    solver.add(P['M1'] == z3.And(P['M0'], P['TE']))


def _add_main_theorems(solver: z3.Solver) -> None:
    """Add main theorems (apply to all n)."""
    # Theorem 1 (noIID-LP1): ¬(S0 ∧ SR ∧ EI ∧ LP1 ∧ IID)
    # Note: EI is often implicitly assumed in the literature
    solver.add(z3.Not(z3.And(P['SR'], P['S0'], P['EI'], P['LP1'], P['IID'])))

    # Theorem 3: SR ∧ TC ∧ TE => ID
    solver.add(z3.Implies(z3.And(P['TC'], P['TE'], P['SR']), P['ID']))

    # Theorem 4 (LPz-ID--noTC): ¬(SR ∧ EI ∧ LP0 ∧ IID ∧ TC)
    solver.add(z3.Not(z3.And(P['SR'], P['EI'], P['LP0'], P['IID'], P['TC'])))

    # Theorem 5 (noSR-EI-LPo-TE-TC): ¬(SR ∧ EI ∧ LP0 ∧ TE ∧ TC)
    # This follows from Theorems 3 and 4
    solver.add(z3.Not(z3.And(P['SR'], P['EI'], P['LP0'], P['TE'], P['TC'])))

    # Theorem 6 (noTC-LP1): ¬(SR ∧ EI ∧ LP1 ∧ TC)
    solver.add(z3.Not(z3.And(P['SR'], P['EI'], P['LP1'], P['TC'])))

    # Theorem 9 (noSo): ¬(S0 ∧ M0 ∧ SR ∧ LP1 ∧ S1)
    solver.add(z3.Not(z3.And(P['S0'], P['M0'], P['SR'], P['LP1'], P['S1'])))

    # Theorem 10 (Mz-So--TM): M0 ∧ S1 => TM
    solver.add(z3.Implies(z3.And(P['M0'], P['S1']), P['TM']))

    # Theorem 11 (S1-SE--TE): S1 ∧ SE => TE
    solver.add(z3.Implies(z3.And(P['S1'], P['SE']), P['TE']))

    # Theorem 12 (SR-SE-So--ID): SR ∧ SE ∧ S1 => ID
    solver.add(z3.Implies(z3.And(P['S1'], P['SE'], P['SR']), P['ID']))


def _add_bivariate_theorems(solver: z3.Solver) -> None:
    """Add theorems specific to n=2."""
    # Theorem 7 (BP--TE-SE): BP => SE ∧ TE  (only for n=2)
    solver.add(z3.Implies(P['BP'], z3.And(P['SE'], P['TE'])))


def _add_multivariate_theorems(solver: z3.Solver) -> None:
    """Add theorems specific to n>=3."""
