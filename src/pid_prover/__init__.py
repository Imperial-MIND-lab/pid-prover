"""
PID Theorem Prover
==================

Automated reasoning on the properties of Partial Information Decomposition (PID)
redundancy measures with the Z3 theorem prover, following
"The mathematical landscape of partial information decomposition" (Liardi et al., 2026).

Modules
-------
- properties: property symbols (Table 2) and their Z3 variables
- theorems:   implications and incompatibilities (Tables 3-4) and the Z3 solver
- measures:   properties satisfied by each measure (Table 5) and their validation
- analysis:   consistency checks, conflicts, implications, inference, maximal sets
- render:     Markdown rendering of Table 5 and the theorems for the docs
"""

__version__ = "0.2.0"

from .analysis import (
    explain_assignment,
    find_maximal_compatible_sets,
    find_minimal_conflicts,
    find_minimal_implications,
    implies,
    infer_property_consequences,
    is_consistent,
)
from .measures import measure_properties, measures_df, validate_measures
from .properties import P, prop_names
from .theorems import THEOREMS, get_pid_solver, redundant_theorems

__all__ = [
    "P",
    "THEOREMS",
    "explain_assignment",
    "find_maximal_compatible_sets",
    "find_minimal_conflicts",
    "find_minimal_implications",
    "get_pid_solver",
    "implies",
    "infer_property_consequences",
    "is_consistent",
    "measure_properties",
    "measures_df",
    "prop_names",
    "redundant_theorems",
    "validate_measures",
]
