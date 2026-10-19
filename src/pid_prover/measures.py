"""PID measures and the properties they satisfy (Table 5 of the paper).

The table lives in data/table5.csv, written with the same symbols as the paper:

    ✓   satisfied                       ✗   not satisfied
    ✓†  satisfied for n = 2 sources only
    ✓*  supported by simulations only   ✓§  holds for full-support distributions only
    ✗‡  holds pointwise, separately on the informative and misinformative lattices
    n.a. not applicable (the measure is only defined for n = 2 sources)

Footnote marks on the row labels (e.g. "CO∥") are kept for display and otherwise ignored.
"""
import csv
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd

from .properties import LP_PARTS, Case, CASES, case_rows, prop_names, row_names

DATA_FILE = Path(__file__).parent / "data" / "table5.csv"
FOOTNOTES = "†*§‡∥"

# Measure key -> (superscript used in the paper, description)
MEASURES: Dict[str, tuple] = {
    "I_min":   ("min", "Williams and Beer's minimum information"),
    "I_MMI":   ("MMI", "Barrett's minimum mutual information"),
    "I_RDR":   ("RDR", "Mages and Rohner's decision reachability redundancy"),
    "I_BROJA": ("BROJA", "Bertschinger et al.'s / Griffith and Koch's constrained "
                "optimisation"),
    "I_delta": ("δ", "Venkatesh and Schamberg's deficiency redundancy"),
    "I_red":   ("red", "Harder et al.'s projected information"),
    "I_IG":    ("IG", "Niu and Quinn's information-geometric redundancy"),
    "I_RR":    ("RR", "Goodwell and Kumar's rescaled redundancy"),
    "I_DEP":   ("DEP", "James et al.'s unique information via dependency constraints"),
    "I_CT":    ("CT", "Sigtermans' redundancy via causal tensors"),
    "I_RAV":   ("RAV", "Redundancy via auxiliary variable (unpublished, in dit)"),
    "I_wedge": ("∧", "Griffith et al.'s common information redundancy"),
    "I_alpha": ("α", "Griffith et al.'s relaxed common information redundancy"),
    "I_prec":  ("≺", "Kolchinsky's Blackwell redundancy"),
    "I_MES":   ("MES", "James et al.'s maximum entropy star"),
    "I_do":    ("do", "Lyu et al.'s do-calculus redundancy"),
    "I_PM":    ("PM", "Finn and Lizier's specificity and ambiguity (pointwise)"),
    "I_SX":    ("SX", "Makkeh et al.'s shared exclusion (pointwise)"),
    "I_CCS":   ("CCS", "Ince's common change in surprisal (pointwise)"),
}


def strip_notes(label: str) -> str:
    """Remove footnote marks from a cell or row label."""
    return label.strip().rstrip(FOOTNOTES)


def load_table(path: Path = DATA_FILE) -> pd.DataFrame:
    """Read Table 5 as a DataFrame (rows: row labels as written, columns: measures)."""
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    header, body = rows[0], rows[1:]
    df = pd.DataFrame([r[1:] for r in body], index=[r[0] for r in body], columns=header[1:])
    unknown_rows = [r for r in df.index if strip_notes(r) not in row_names]
    unknown_cols = [c for c in df.columns if c not in MEASURES]
    if unknown_rows or unknown_cols:
        raise ValueError(f"Unknown properties {unknown_rows} or measures {unknown_cols} in {path}")
    return df


table5: pd.DataFrame = load_table()

# Same table indexed by plain property names
measures_df: pd.DataFrame = table5.rename(index=strip_notes)
measure_names: List[str] = list(measures_df.columns)

# A measure is bivariate-only if some property is not applicable (n.a.) to it
bivariate_only_measures: List[str] = [
    m for m in measure_names if (measures_df[m] == "n.a.").any()
]


def cell_value(cell: str, n: Case) -> Optional[bool]:
    """Truth value of a Table 5 entry in case n (None if not applicable)."""
    if cell == "n.a.":
        return None
    if cell.startswith("✓"):
        return n == "bivariate" or "†" not in cell
    if cell.startswith("✗"):
        return False
    raise ValueError(f"Unrecognised Table 5 entry {cell!r}")


def measure_assignment(measure: str, n: Case) -> Dict[str, bool]:
    """Truth value of every applicable row of Table 5 for a measure in case n."""
    if n == "multivariate" and measure in bivariate_only_measures:
        raise ValueError(f"{measure} is only defined for n = 2 sources")
    values = {r: cell_value(measures_df.at[r, measure], n) for r in case_rows(n)}
    return {p: v for p, v in values.items() if v is not None}


def measure_properties(measure: str, n: Case) -> List[str]:
    """Properties satisfied by a measure in case n ((LP) if all its applicable parts hold)."""
    values = measure_assignment(measure, n)
    values["LP"] = all(values[r] for r in LP_PARTS if r in values)
    return [p for p in prop_names if values[p]]


def validate_measures(verbose: bool = True) -> bool:
    """
    Check every column of Table 5 against the theorems.

    For each measure, the satisfied (✓) properties are set to true and the violated (✗)
    ones to false. A column fails if this assignment contradicts the theorems, i.e. if
    it satisfies an incompatible set or violates a property implied by others. In that
    case a minimal set of contradictory entries is printed.
    """
    from .analysis import explain_assignment

    all_passed = True
    for n in CASES:
        if verbose:
            print(f"\nCase: {n} ({'n = 2' if n == 'bivariate' else 'any n'})")
        for measure in measure_names:
            if n == "multivariate" and measure in bivariate_only_measures:
                if verbose:
                    print(f"  {measure:<10} skipped (only defined for n = 2)")
                continue
            core = explain_assignment(measure_assignment(measure, n), n)
            all_passed &= core is None
            if verbose:
                status = "PASS" if core is None else f"FAIL  contradictory entries: {core}"
                print(f"  {measure:<10} {status}")
    if verbose:
        print("\nAll measures are consistent with the theorems." if all_passed
              else "\nSome measures contradict the theorems (see above).")
    return all_passed
