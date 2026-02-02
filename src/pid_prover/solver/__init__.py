"""Z3 solver setup and axioms for PID theorem proving."""
from .core import get_pid_solver
from .axioms import P, prop_names, STRONG_WEAK_PAIRS

__all__ = ["get_pid_solver", "P", "prop_names", "STRONG_WEAK_PAIRS"]
