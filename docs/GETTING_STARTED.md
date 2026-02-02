# Getting Started with PID Prover

This guide will help you get up and running with the PID Theorem Prover.

## Installation

### Prerequisites

- Python 3.10 or higher
- pip package manager

### From PyPI (coming soon)

```bash
pip install pid-prover
```

### From Source

```bash
# Clone the repository
git clone https://github.com/pmediano/pid-prover.git
cd pid-prover

# Install in development mode
pip install -e .

# Install with development dependencies (for testing)
pip install -e ".[dev]"

# Install with notebook support (for Jupyter)
pip install -e ".[notebooks]"
```

### Required Dependencies

The installation will automatically install:
- `z3-solver>=4.8.0` - Z3 theorem prover
- `pandas>=1.5.0` - Data manipulation
- `pytest>=7.0.0` - Testing framework (dev install only)

### Verify Installation

```bash
# Test the CLI tool
pid-prover --help

# Test the Python API
python -c "from pid_prover import validate_measures; print('Installation successful!')"
```

## Your First Validation

Let's validate all PID measures against known theorems. This is the most basic use case.

### Command Line

```bash
# Use the CLI tool
pid-prover --help

# Or call the API directly from command line
python -c "from pid_prover import validate_measures; validate_measures()"
```

### Python Script

Create a file `test_validation.py`:

```python
from pid_prover import validate_measures

# Validate all measures
result = validate_measures()

if result:
    print("✓ All measures passed validation!")
else:
    print("✗ Some measures failed validation")
```

Run it:
```bash
python test_validation.py
```

## Understanding the Output

### Validation Results

When you run `validate_measures()`, the system:

1. **Loads all measures**: Reads the property satisfaction claims for 19 PID measures
2. **Checks bivariate case**: Validates each measure against axioms for n=2
3. **Checks multivariate case**: Validates each measure against axioms for n≥3
4. **Reports failures**: Prints any measures that violate known theorems

### Expected Output

You'll see output like:

```
Validating measures...
Bivariate (n=2): 19/19 passed ✓
Multivariate (n≥3): 14/15 passed ✗

Failed measures (multivariate):
  - I_CT: Claims {S0, M0, SR, EI, IID} (violates Theorem 2)
  - I_RR: Claims {S0, M0, SR, EI, IID} (violates Theorem 2)
  - I_wedge: Claims {S0, M0, SR, EI, IID} (violates Theorem 2)
  - I_alpha: Claims {S0, M0, SR, EI, IID} (violates Theorem 2)
  - I_prec: Claims {S0, M0, SR, EI, IID} (violates Theorem 2)
```

**Note**: These failures are expected and represent a systematic error in the literature. See [RESEARCH_FINDINGS.md](../RESEARCH_FINDINGS.md) for details.

## Basic API Usage

### Import the Functions

```python
from pid_prover import (
    validate_measures,           # Validate all measures
    find_minimal_conflicts,      # Find no-go theorems
    find_minimal_implications,   # Find logical implications
    infer_property_consequences, # Infer mandatory/forbidden properties
    get_pid_solver,              # Access Z3 solver directly
)
```

### Example: Check if Properties are Consistent

```python
from pid_prover import get_pid_solver
from pid_prover.solver.axioms import P
import z3

# Create solver for bivariate case
solver = get_pid_solver("bivariate")

# Check if {SR, S0, GP} is consistent
result = solver.check(z3.And([P["SR"], P["S0"], P["GP"]]))

if result == z3.sat:
    print("✓ These properties are consistent")
else:
    print("✗ These properties form a conflict")
```

### Example: Find What Properties You Must Satisfy

```python
from pid_prover import infer_property_consequences

# I want my measure to satisfy BP and SR
intended_props = ["BP", "SR"]

# Check for bivariate case
results = infer_property_consequences(intended_props, "bivariate")

print("If you satisfy BP and SR, you MUST also satisfy:")
print(results["Mandatory"])

print("\nAnd you CANNOT satisfy:")
print(results["Forbidden"])
```

## Understanding Properties and Measures

The PID Prover analyzes:
- **20 properties** that measures may satisfy (SR, S0, M0, GP, etc.)
- **19 PID measures** from the literature (I_min, I_MMI, I_BROJA, etc.)
- **2 cases**: bivariate (n=2) and multivariate (n≥3)

For complete property and measure definitions, see [PROPERTIES.md](PROPERTIES.md).

## Common Pitfalls

### 1. Case Confusion

Properties may be consistent in one case but not the other:

```python
# Always specify the case explicitly
results_biv = infer_property_consequences(props, "bivariate")
results_multi = infer_property_consequences(props, "multivariate")
```

### 2. Bivariate-Only Measures

Four measures only apply to n=2:
- I_BROJA
- I_delta
- I_red
- I_DEP

These are automatically excluded from multivariate validation.

### 3. Z3 Result Checking

Always compare Z3 results to `z3.sat` and `z3.unsat`:

```python
import z3

result = solver.check()
if result == z3.sat:
    print("Satisfiable")
elif result == z3.unsat:
    print("Unsatisfiable")
else:  # z3.unknown
    print("Unknown (timeout or too complex)")
```

## Quick Reference

### Check Consistency
```python
from pid_prover import get_pid_solver
from pid_prover.solver.axioms import P
import z3

solver = get_pid_solver("bivariate")
props = ["SR", "S0", "M0"]
result = solver.check(z3.And([P[p] for p in props]))
```

### Find Conflicts (No-Go Theorems)
```python
from pid_prover import find_minimal_conflicts

conflicts = find_minimal_conflicts("bivariate", max_size=3)
for conflict in conflicts:
    print(f"Cannot satisfy all of: {conflict}")
```

### Find Implications
```python
from pid_prover import find_minimal_implications

implications = find_minimal_implications("multivariate", premise_size=2)
for premises, conclusion in implications:
    print(f"{premises} implies {conclusion}")
```

### Design a New Measure
```python
from pid_prover import infer_property_consequences

intended = ["SR", "S0", "GP"]
results = infer_property_consequences(intended, "bivariate")

print("Required properties:", results["Mandatory"])
print("Forbidden properties:", results["Forbidden"])
```

## Next Steps

Now that you understand the basics:

1. **Explore examples**: See [EXAMPLES.md](EXAMPLES.md) for comprehensive usage patterns
2. **Read API docs**: Check [API.md](API.md) for detailed function signatures
3. **Learn about properties**: Read [PROPERTIES.md](PROPERTIES.md) for property definitions
4. **Dive deeper**: See [RESEARCH_FINDINGS.md](../RESEARCH_FINDINGS.md) for mathematical insights

## Getting Help

If you encounter issues:

1. **Check the examples**: [EXAMPLES.md](EXAMPLES.md) has solutions to common tasks
2. **Read the API docs**: [API.md](API.md) explains all functions
3. **Review properties**: [PROPERTIES.md](PROPERTIES.md) lists all properties and measures
4. **Run tests**: `pytest tests/ -v` to verify your installation

## Testing Your Installation

Run the test suite to ensure everything works:

```bash
# Run all tests
pytest tests/ -v

# Run specific test modules
pytest tests/test_solver.py -v
pytest tests/test_measures.py -v
pytest tests/test_analysis.py -v

# Run with coverage report
pytest --cov=pid_prover tests/
```

If all tests pass, your installation is ready to use!
