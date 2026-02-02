"""Analysis and theorem discovery for PID properties."""
from .discovery import get_ordered_properties, find_minimal_conflicts, find_minimal_implications
from .inference import infer_property_consequences
from .compatibility import find_maximal_compatible_sets

__all__ = [
    "get_ordered_properties",
    "find_minimal_conflicts",
    "find_minimal_implications",
    "infer_property_consequences",
    "find_maximal_compatible_sets",
]
