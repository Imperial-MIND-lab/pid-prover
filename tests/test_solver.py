"""Test solver initialization."""
import pytest
import z3
from pid_prover.solver import get_pid_solver
from pid_prover.solver.axioms import P, prop_names


def test_get_pid_solver_bivariate():
    """Test bivariate solver creation."""
    solver = get_pid_solver("bivariate")
    assert isinstance(solver, z3.Solver)


def test_get_pid_solver_multivariate():
    """Test multivariate solver creation."""
    solver = get_pid_solver("multivariate")
    assert isinstance(solver, z3.Solver)


def test_theorem_2_multivariate(multivariate_solver):
    """Test Theorem 2 is enforced for n>=3."""
    # {S0, M0, SR, EI, IID} should be unsat for multivariate
    result = multivariate_solver.check(z3.And([
        P["S0"], P["M0"], P["SR"], P["EI"], P["IID"]
    ]))
    assert result == z3.unsat


def test_theorem_7_bivariate(bivariate_solver):
    """Test Theorem 7 is enforced for n=2."""
    # BP => TE ∧ SE
    bivariate_solver.add(P["BP"])
    bivariate_solver.add(z3.Not(z3.And(P["TE"], P["SE"])))
    assert bivariate_solver.check() == z3.unsat


def test_lemma_1_implication(bivariate_solver):
    """Test Lemma 1: LP1 => LP0."""
    bivariate_solver.add(P["LP1"])
    bivariate_solver.add(z3.Not(P["LP0"]))
    assert bivariate_solver.check() == z3.unsat


def test_lemma_2_implication(bivariate_solver):
    """Test Lemma 2: ID => IID."""
    bivariate_solver.add(P["ID"])
    bivariate_solver.add(z3.Not(P["IID"]))
    assert bivariate_solver.check() == z3.unsat


def test_prop_names_exported():
    """Test that prop_names is properly exported."""
    assert len(prop_names) == 20
    assert "SR" in prop_names
    assert "EI" in prop_names


def test_P_dict_exported():
    """Test that P dict is properly exported."""
    assert len(P) == 20
    assert all(isinstance(P[name], z3.BoolRef) for name in prop_names)
