"""Shared pytest fixtures for unit tests."""
import pytest
from pid_prover.solver import get_pid_solver


@pytest.fixture
def bivariate_solver():
    """Bivariate solver fixture."""
    return get_pid_solver("bivariate")


@pytest.fixture
def multivariate_solver():
    """Multivariate solver fixture."""
    return get_pid_solver("multivariate")


@pytest.fixture
def sample_properties():
    """Sample property lists for testing."""
    return {
        "valid_bivariate": ["SR", "S0", "M0", "GP"],
        "valid_multivariate": ["SR", "S0", "GP"],
        "invalid": ["SR", "S0", "M0", "EI", "IID"],  # Violates Theorem 2 for n>=3
    }
