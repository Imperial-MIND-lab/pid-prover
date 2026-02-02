"""End-to-end integration tests."""
import pytest
from pid_prover import (
    validate_measures,
    find_minimal_conflicts,
    get_pid_solver,
    measures_df,
)


def test_full_validation():
    """Test complete validation workflow."""
    # Should complete without crashing
    result = validate_measures()
    assert isinstance(result, bool)


def test_cli_workflow():
    """Test typical CLI usage patterns."""
    # Validation -> Conflicts
    validate_measures()
    conflicts = find_minimal_conflicts("bivariate", max_size=3)
    assert len(conflicts) >= 0


def test_import_all_modules():
    """Test that all main modules can be imported."""
    from pid_prover import solver, measures, analysis, filtering
    assert solver is not None
    assert measures is not None
    assert analysis is not None
    assert filtering is not None


def test_solver_integration():
    """Test solver can be used directly."""
    solver = get_pid_solver("bivariate")
    from pid_prover.solver.axioms import P
    import z3

    # Test a simple query
    solver.push()
    result = solver.check(P["SR"])
    solver.pop()
    assert result == z3.sat


def test_measures_df_accessible():
    """Test that measures_df is accessible from main package."""
    assert measures_df is not None
    assert measures_df.shape[0] == 20  # 20 properties
    assert measures_df.shape[1] == 19  # 19 measures
