"""PID properties (Table 2 of the paper) and their Z3 encoding.

The paper considers 20 properties. Local Positivity (LP) is a single property, but Table 5
reports it separately for n = 2 sources (LP0) and n >= 3 sources (LP1), so the solver has one
Boolean variable per row of Table 5, and (LP) is expressed through them (see prop()).
"""
from typing import Dict, List, Literal

import z3

Case = Literal["bivariate", "multivariate"]
CASES: List[Case] = ["bivariate", "multivariate"]

# The 20 properties, in the order of Table 5: symbol -> (name, description)
PROPERTIES: Dict[str, tuple] = {
    "SR":   ("Self-redundancy", "I∩ of a single source equals its mutual information."),
    "S0":   ("(Weak) Symmetry", "I∩ is invariant under any permutation of the sources."),
    "M0":   ("(Weak) Monotonicity", "Adding a source does not increase I∩ (equality if a "
             "less informative source is already present)."),
    "GP":   ("Global Positivity", "I∩ is non-negative."),
    "LP":   ("Local Positivity", "All I∂ atoms are non-negative. Table 5 reports it separately "
             "for n = 2 sources (LP0) and n ≥ 3 sources (LP1)."),
    "IID":  ("Independent Identity", "In the TBC, independent sources provide vanishing I∩."),
    "ID":   ("Identity", "In the TBC, I∩ equals the mutual information between sources."),
    "TM":   ("Target Monotonicity", "Adding a target does not decrease I∩."),
    "TC":   ("Target Chain rule", "The chain rule for I∩ holds for the target variables."),
    "SE":   ("Subset Equality", "Removing a source more informative than another preserves I∩."),
    "LB":   ("Lower Bound", "A variable less informative than all sources lower-bounds I∩."),
    "TE":   ("Target Equality", "Adding the target to the sources does not change I∩."),
    "M1":   ("Strong Monotonicity", "As (M0), with equality also when a source is more "
             "informative than the target."),
    "S1":   ("Strong Symmetry", "I∩ is invariant under any permutation of sources or target."),
    "STAR": ("Assumption (∗)", "Redundancy and unique information only depend on the "
             "pairwise source-target marginals."),
    "BP":   ("Blackwell Property", "Unique information vanishes iff one source "
             "Blackwell-precedes another."),
    "AD":   ("Additivity", "I∩ of two independent subsystems equals the sum of their I∩."),
    "CO":   ("Continuity", "I∩ is continuous under small changes in the probability distribution."),
    "DI":   ("Differentiability", "I∩ is differentiable with respect to the probability "
             "distribution."),
    "EI":   ("Equivalence-class Invariance", "I∩ is invariant under relabellings "
             "(bijections) of the variables."),
}

prop_names: List[str] = list(PROPERTIES)

# (LP) for n = 2 sources and for n >= 3 sources, as in the rows of Table 5
LP_PARTS = {"LP0": "n = 2", "LP1": "n ≥ 3"}

# Rows of Table 5: the properties, with (LP) split into its two parts
row_names: List[str] = [r for p in prop_names for r in (LP_PARTS if p == "LP" else [p])]

# Z3 boolean variable for each row of Table 5
P: Dict[str, z3.BoolRef] = {name: z3.Bool(name) for name in row_names}


def case_rows(n: Case) -> List[str]:
    """Rows of Table 5 that are meaningful in a given case ((LP1) needs n >= 3 sources)."""
    if n == "bivariate":
        return [r for r in row_names if r != "LP1"]
    return list(row_names)


def prop(name: str, n: Case) -> z3.BoolRef:
    """
    Z3 expression for a property in case n.

    (LP) is (LP0) for n = 2 sources, and (LP0) and (LP1) together for any number of sources.
    The parts (LP0) and (LP1) can also be used directly.
    """
    if name == "LP":
        return z3.And([P[r] for r in LP_PARTS if r in case_rows(n)])
    if name not in P:
        raise ValueError(f"Unknown property {name!r}; valid names: {prop_names + list(LP_PARTS)}")
    return P[name]


def all_of(names, n: Case) -> z3.BoolRef:
    """Conjunction of the given properties."""
    return z3.And([prop(name, n) for name in names])
