"""PID property definitions and Z3 boolean variables."""
import z3
from typing import Dict, List, Tuple

# Property names from the paper
# Note: LP0 is "weak" local positivity (n=2), LP1 is "strong" (n>=3)
prop_names: List[str] = [
    "SR",   # Self-redundancy
    "S0",   # (Weak) Symmetry
    "M0",   # (Weak) Monotonicity
    "GP",   # Global Positivity
    "LP0",  # (Weak) Local Positivity (n=2)
    "LP1",  # Strong Local Positivity (n>=3)
    "ID",   # Identity
    "IID",  # Independent Identity
    "TM",   # Target Monotonicity
    "TC",   # Target Chain rule
    "S1",   # Strong Symmetry
    "M1",   # Strong Monotonicity
    "BP",   # Blackwell Property
    "TE",   # Target Equality
    "BB",   # Blackboard Bold property
    "AD",   # Additivity
    "CO",   # Continuity
    "LB",   # Lower Bound
    "EI",   # Equivalence-class Invariance
    "SE"    # Subset Equality
]

# Z3 Boolean variables for each property
P: Dict[str, z3.BoolRef] = {name: z3.Bool(name) for name in prop_names}

# Strong-weak property pairs for filtering
# Format: (strong, weak) where strong => weak
STRONG_WEAK_PAIRS: List[Tuple[str, str]] = [
    ("ID", "IID"),    # Identity => Independent Identity
    ("LP1", "LP0"),   # Strong => Weak Local Positivity
    ("S1", "S0"),     # Strong => Weak Symmetry
    ("M1", "M0")      # Strong => Weak Monotonicity
]
