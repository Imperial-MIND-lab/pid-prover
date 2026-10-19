"""Tests for the property encoding and the theorems."""
import pytest
import z3

from pid_prover.properties import LP_PARTS, P, case_rows, prop, prop_names, row_names
from pid_prover.theorems import THEOREMS, follows_from_others, get_pid_solver, theorems_for

CASES = ["bivariate", "multivariate"]


def test_properties_and_table5_rows():
    assert len(prop_names) == 20
    assert len(row_names) == 21 and set(P) == set(row_names)
    assert "LP1" not in case_rows("bivariate")
    assert "LP1" in case_rows("multivariate")


def test_lp_alias():
    assert z3.eq(prop("LP", "bivariate"), z3.And(P["LP0"]))
    assert z3.eq(prop("LP", "multivariate"), z3.And(P["LP0"], P["LP1"]))
    with pytest.raises(ValueError):
        prop("XX", "bivariate")


def test_theorem_names_unique_and_properties_known():
    assert len({t.name for t in THEOREMS}) == len(THEOREMS)
    for t in THEOREMS:
        assert set(t.premises + t.conclusions) <= set(prop_names) | set(LP_PARTS), t.name


def test_case_specific_theorems():
    names = {n: {t.name for t in theorems_for(n)} for n in CASES}
    assert "Theo. 5" in names["bivariate"] and "Theo. 5" not in names["multivariate"]
    for name in ("Theo. 1", "Theo. 10"):  # need n >= 3 sources
        assert name in names["multivariate"] and name not in names["bivariate"]


@pytest.mark.parametrize("n", CASES)
def test_axioms_are_consistent(n):
    assert get_pid_solver(n).check() == z3.sat


@pytest.mark.parametrize("n", CASES)
def test_derived_flag_matches_entailment(n):
    """Results marked as derived follow from the others; all the others are independent."""
    for t in theorems_for(n):
        assert follows_from_others(t, n) == t.derived, t.name


def test_invalid_case():
    with pytest.raises(ValueError):
        get_pid_solver("trivariate")
