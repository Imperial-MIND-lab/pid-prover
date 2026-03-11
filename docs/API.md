# PID Prover API Reference

## Overview
Python API for the PID Theorem Prover module.

## Import Structure

```python
from pid_prover import (
    validate_measures,           # Main validation function
    find_minimal_conflicts,      # Conflict discovery
    find_minimal_implications,   # Implication discovery
    infer_property_consequences, # Property inference
    get_pid_solver,              # Direct solver access
    measures_df,                 # Measures DataFrame
)
```

## Core Functions

### `validate_measures()`
Validate all measures for both bivariate and multivariate cases.

**Returns:** `bool` - True if all pass, False otherwise

**Example:**
```python
from pid_prover import validate_measures
passed = validate_measures()
```

**See also:** [Basic Validation examples](EXAMPLES.md#basic-validation)

### `find_minimal_conflicts(n, max_size=4, filter_reducible=True)`
Find minimal inconsistent property sets.

**Parameters:**
- `n`: `"bivariate"` or `"multivariate"`
- `max_size`: Maximum conflict set size (default: 4)
- `filter_reducible`: Filter reducible conflicts (default: True)

**Returns:** `List[List[str]]` - List of conflict sets

**Example:**
```python
from pid_prover import find_minimal_conflicts
conflicts = find_minimal_conflicts("bivariate", max_size=3)
```

**See also:** [Finding Conflicts examples](EXAMPLES.md#finding-conflicts)

### `find_minimal_implications(n, premise_size=2)`
Find minimal logical implications.

**Parameters:**
- `n`: `"bivariate"` or `"multivariate"`
- `premise_size`: Number of premises (default: 2)

**Returns:** `List[Tuple[Tuple[str, ...], str]]` - List of (premises, conclusion)

**Example:**
```python
from pid_prover import find_minimal_implications
implications = find_minimal_implications("multivariate", premise_size=2)
```

**See also:** [Finding Implications examples](EXAMPLES.md#finding-implications)

### `infer_property_consequences(intended_props, n)`
Infer which properties are mandatory or forbidden.

**Parameters:**
- `intended_props`: List of property names
- `n`: `"bivariate"` or `"multivariate"`

**Returns:** `Dict[str, List[str]]` - {"Mandatory": [...], "Forbidden": [...]}

**Example:**
```python
from pid_prover import infer_property_consequences
results = infer_property_consequences(["BP", "SR"], "bivariate")
```

**See also:** [Property Inference examples](EXAMPLES.md#property-inference)

### `get_pid_solver(n)`
Create Z3 solver with PID axioms.

**Parameters:**
- `n`: `"bivariate"` or `"multivariate"`

**Returns:** `z3.Solver`

**Example:**
```python
from pid_prover import get_pid_solver
solver = get_pid_solver("bivariate")
```

**See also:** [Direct Solver Access examples](EXAMPLES.md#direct-solver-access), [Advanced Z3 Usage](EXAMPLES.md#advanced-z3-usage)

## Data Structures

### `measures_df`
Pandas DataFrame containing property satisfaction for all measures.

**Structure:**
- Rows: Properties (SR, S0, M0, ..., EI)
- Columns: Measures (I_min, I_MMI, ..., I_prec)
- Values: Y, N, Y_2, N_A, Y_*, N_dd, N_m

**Example:**
```python
from pid_prover.measures import measures_df
print(measures_df["I_min"])  # Properties for I_min
```

**See also:** [Direct Solver Access examples](EXAMPLES.md#direct-solver-access), [Batch Analysis examples](EXAMPLES.md#batch-analysis)

## Module Organization

### `pid_prover.solver`
- `core.py`: Solver initialization
- `axioms.py`: Property definitions and Z3 variables

### `pid_prover.measures`
- `data.py`: Measures DataFrame
- `validation.py`: Validation functions

### `pid_prover.analysis`
- `discovery.py`: Conflict and implication finding
- `inference.py`: Property consequence inference
- `compatibility.py`: Compatible property sets

### `pid_prover.filtering`
- `reducibility.py`: Conflict reducibility checking

### `pid_prover.cli`
- Command-line interface

## Property Names

The system analyzes **20 properties**. For complete property definitions, descriptions, and relationships, see [PROPERTIES.md](PROPERTIES.md).

Quick reference:
- `SR`, `S0`, `S1`, `M0`, `M1`, `GP`, `LP0`, `LP1`
- `ID`, `IID`, `TM`, `TC`, `BP`, `TE`, `BB`
- `AD`, `CO`, `LB`, `EI`, `SE`

## Measure Names

The system validates **19 PID measures**. For complete measure list and descriptions, see [PROPERTIES.md](PROPERTIES.md#measures).

Quick reference:
- `I_min`, `I_MMI`, `I_RDR`, `I_BROJA*`, `I_delta*`, `I_red*`
- `I_IG`, `I_RAV`, `I_CT`, `I_RR`, `I_DEP*`, `I_CCS`
- `I_PM`, `I_SX`, `I_MES`, `I_do`, `I_wedge`, `I_alpha`, `I_prec`

(*bivariate-only)
