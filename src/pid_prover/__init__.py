"""
PID Theorem Prover
==================

A tool for analyzing Partial Information Decomposition (PID) measures
using automated theorem proving with Z3.

Main Components
---------------
- solver: Z3 solver setup with PID axioms
- measures: Measure data and validation
- analysis: Theorem discovery and property inference
- filtering: Conflict reducibility checking
- cli: Command-line interface

Quick Start
-----------
    from pid_prover import validate_measures, find_minimal_conflicts

    # Validate all measures
    validate_measures()

    # Find conflicts for bivariate case
    conflicts = find_minimal_conflicts("bivariate", max_size=3)
"""

__version__ = "0.1.0"

# Public API
from .measures import validate_measures, measures_df
from .analysis import (
    find_minimal_conflicts,
    find_minimal_implications,
    infer_property_consequences,
    find_maximal_compatible_sets,
)
from .solver import get_pid_solver

__all__ = [
    "validate_measures",
    "measures_df",
    "find_minimal_conflicts",
    "find_minimal_implications",
    "infer_property_consequences",
    "find_maximal_compatible_sets",
    "get_pid_solver",
]
