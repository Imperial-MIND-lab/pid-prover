"""Relations among PID properties (Tables 3 and 4 of the paper) and the Z3 solver built on them.

To add or modify a result, edit THEOREMS below: every analysis in the package, the tests,
and the theorem table in docs/REFERENCE.md are derived from this list.
"""
from dataclasses import dataclass
from typing import List, Literal, Tuple

import z3

from .properties import Case, all_of


@dataclass(frozen=True)
class Theorem:
    """A propositional relation among properties.

    kind:
        "implies"      premises => conclusions
        "iff"          premises <=> conclusions
        "incompatible" premises cannot hold together
    case:
        "all", "bivariate" (only proven for n = 2), or "multivariate" (needs n >= 3 sources)
    derived:
        True if the paper derives it from other results (it is still encoded, and the
        tests check that it indeed follows from the remaining theorems)
    """
    name: str
    kind: Literal["implies", "iff", "incompatible"]
    premises: Tuple[str, ...]
    conclusions: Tuple[str, ...] = ()
    case: Literal["all", "bivariate", "multivariate"] = "all"
    derived: bool = False

    def applies_to(self, n: Case) -> bool:
        return self.case in ("all", n)

    def formula(self, n: Case) -> z3.BoolRef:
        lhs = all_of(self.premises, n)
        if self.kind == "incompatible":
            return z3.Not(lhs)
        rhs = all_of(self.conclusions, n)
        return lhs == rhs if self.kind == "iff" else z3.Implies(lhs, rhs)

    def statement(self) -> str:
        lhs = ", ".join(f"({p})" for p in self.premises)
        if self.kind == "incompatible":
            return f"{lhs} are incompatible"
        arrow = "⇔" if self.kind == "iff" else "⇒"
        return f"{lhs} {arrow} " + ", ".join(f"({c})" for c in self.conclusions)


T = Theorem
THEOREMS: List[Theorem] = [
    # Appendix C.1: basic implications
    T("Lemma 1", "implies", ("LP",), ("GP",)),
    T("Lemma 2", "implies", ("ID",), ("IID",)),
    T("Lemma 3", "implies", ("S1",), ("S0",)),
    T("Lemma 4", "implies", ("M0",), ("SE",)),
    T("Lemma 5", "implies", ("DI",), ("CO",)),
    T("Prop. 1", "implies", ("M0", "SR"), ("LB",)),
    T("Prop. 2", "implies", ("SR", "LB"), ("GP",)),
    T("Prop. 3", "implies", ("M0", "SR"), ("GP",), derived=True),
    T("Prop. 4", "implies", ("S0", "LP"), ("M0",)),
    T("Prop. 5", "implies", ("GP", "TC"), ("TM",)),
    T("Prop. 6", "implies", ("SR", "S0", "LP"), ("TE",)),
    T("Prop. 7", "implies", ("SR", "S0", "LP"), ("M1",), derived=True),
    # Appendix C.2: main implications and incompatibilities
    T("Theo. 1", "incompatible", ("S0", "SR", "EI", "LP1", "IID"), case="multivariate"),
    T("Theo. 2", "incompatible", ("SR", "S0", "M0", "TC")),
    T("Cor. 1", "incompatible", ("SR", "S0", "LP", "TC"), derived=True),
    T("Cor. 2", "incompatible", ("SR", "S0", "EI", "LP", "IID", "TC"), derived=True),
    T("Theo. 3", "implies", ("SR", "S0", "TC", "TE"), ("ID",)),
    T("Cor. 3", "implies", ("SR", "S0", "LP", "TC"), ("ID",), derived=True),
    T("Theo. 4", "iff", ("M0", "TE"), ("M1",)),
    T("Theo. 5", "implies", ("BP",), ("SE", "TE"), case="bivariate"),
    # Appendix C.3: strong symmetry
    T("Theo. 7", "implies", ("M0", "S1"), ("TM",)),
    T("Theo. 8", "implies", ("SE", "S1"), ("TE",)),
    T("Theo. 9", "implies", ("SR", "SE", "S1"), ("ID",)),
    T("Theo. 10", "incompatible", ("M0", "SR", "LP1", "S1"), case="multivariate"),
]

# Results of the paper that cannot be expressed as relations among the properties above
NOT_ENCODED = {
    "Prop. 8": "(ID), (TM) ⇒ I∩(X1, X2; f(X1, X2)) ≤ I(X1; X2): an inequality, not a property",
    "Theo. 6": "(GP), (IID), (TM) and mechanistic redundancy are incompatible: "
               "mechanistic redundancy is not one of the properties of Table 5",
}


def theorems_for(n: Case, exclude: Tuple[str, ...] = ()) -> List[Theorem]:
    """Theorems that hold in case n, optionally leaving some out by name."""
    return [t for t in THEOREMS if t.applies_to(n) and t.name not in exclude]


def get_pid_solver(
    n: Case = "bivariate", exclude: Tuple[str, ...] = ()
) -> z3.Solver:
    """
    Z3 solver loaded with all theorems valid for the given case.

    Parameters
    ----------
    n : {"bivariate", "multivariate"}
        "bivariate": properties are required for n = 2 sources only.
        "multivariate": properties are required for any number of sources.
    exclude : tuple of str
        Names of theorems to leave out (e.g. ("Theo. 2",)).
    """
    if n not in ("bivariate", "multivariate"):
        raise ValueError(f"n must be 'bivariate' or 'multivariate', got {n!r}")
    solver = z3.Solver()
    for theorem in theorems_for(n, exclude):
        solver.add(theorem.formula(n))
    return solver


def follows_from_others(theorem: Theorem, n: Case) -> bool:
    """True if the theorem is entailed by the other non-derived theorems of case n."""
    derived = tuple(t.name for t in THEOREMS if t.derived)
    solver = get_pid_solver(n, exclude=(theorem.name,) + derived)
    return solver.check(z3.Not(theorem.formula(n))) == z3.unsat


def redundant_theorems(n: Case) -> List[str]:
    """Names of the theorems of case n that follow from the non-derived ones."""
    return [t.name for t in theorems_for(n) if follows_from_others(t, n)]
