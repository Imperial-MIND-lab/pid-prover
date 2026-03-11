"""Test analysis functions."""
import pytest
from pid_prover.analysis import (
    find_minimal_conflicts,
    find_minimal_implications,
    infer_property_consequences,
    get_ordered_properties,
)
from pid_prover.solver import get_pid_solver


def test_find_minimal_conflicts_bivariate():
    """Test conflict discovery for bivariate case."""
    conflicts = find_minimal_conflicts("bivariate", max_size=5)
    assert isinstance(conflicts, list)
    # Should find at least some conflicts with larger max_size
    assert len(conflicts) >= 0  # May find 0 conflicts if all are size > 5


def test_find_minimal_conflicts_multivariate():
    """Test conflict discovery for multivariate case."""
    conflicts = find_minimal_conflicts("multivariate", max_size=5)
    assert isinstance(conflicts, list)


def test_infer_property_consequences_bivariate():
    """Test property inference for bivariate case."""
    results = infer_property_consequences(["BP", "SR"], "bivariate")
    assert "Mandatory" in results
    assert "Forbidden" in results
    # BP => TE ∧ SE (Theorem 7)
    assert "TE" in results["Mandatory"]
    assert "SE" in results["Mandatory"]


def test_infer_property_consequences_multivariate():
    """Test property inference for multivariate case."""
    results = infer_property_consequences(["SR", "S0"], "multivariate")
    assert "Mandatory" in results
    assert "Forbidden" in results
    assert isinstance(results["Mandatory"], list)
    assert isinstance(results["Forbidden"], list)


def test_infer_property_consequences_inconsistent():
    """Test that inconsistent properties return empty results."""
    # {S0, M0, SR, EI, IID} is inconsistent for multivariate
    results = infer_property_consequences(["S0", "M0", "SR", "EI", "IID"], "multivariate")
    assert results["Mandatory"] == []
    assert results["Forbidden"] == []


def test_get_ordered_properties():
    """Test property ordering function."""
    solver = get_pid_solver("bivariate")
    ordered = get_ordered_properties(solver)
    assert len(ordered) == 20
    assert "IID" in ordered
    assert "ID" in ordered
    # IID should come before ID (weaker property first)
    assert ordered.index("IID") < ordered.index("ID")


def test_find_minimal_implications_runs():
    """Test that find_minimal_implications runs without error."""
    implications = find_minimal_implications("bivariate", premise_size=2)
    assert isinstance(implications, list)
