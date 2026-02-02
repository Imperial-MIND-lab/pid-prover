# Usage Examples

Practical examples for common tasks with the PID Theorem Prover.

## Table of Contents
1. [Basic Validation](#basic-validation)
2. [Finding Conflicts](#finding-conflicts)
3. [Finding Implications](#finding-implications)
4. [Property Inference](#property-inference)
5. [Designing New Measures](#designing-new-measures)
6. [Direct Solver Access](#direct-solver-access)
7. [Advanced Z3 Usage](#advanced-z3-usage)
8. [Batch Analysis](#batch-analysis)
9. [Performance Tips](#performance-tips)
10. [Testing Your Code](#testing-your-code)

---

## Basic Validation

### Validate All Measures

```python
from pid_prover import validate_measures

# Validate all 19 measures for both cases
validate_measures()
```

### Validate a Specific Measure

```python
from pid_prover import get_pid_solver
from pid_prover.measures.validation import dataframe_to_property_list
from pid_prover.solver.axioms import P
import z3

# Get properties for I_BROJA (bivariate)
properties = dataframe_to_property_list("I_BROJA", "bivariate")
print(f"I_BROJA properties: {properties}")

# Check consistency
solver = get_pid_solver("bivariate")
solver.push()
solver.add(z3.And([P[prop] for prop in properties]))
is_consistent = solver.check() == z3.sat
solver.pop()

print(f"Consistent: {is_consistent}")
```

### Check Custom Property Set

```python
from pid_prover import get_pid_solver
from pid_prover.solver.axioms import P
import z3

# Test if {SR, GP, IID} is consistent
properties = ['SR', 'GP', 'IID']

solver = get_pid_solver("multivariate")
solver.push()
solver.add(z3.And([P[prop] for prop in properties]))
result = solver.check()
solver.pop()

if result == z3.sat:
    print(f"{properties} is CONSISTENT for n≥3")
else:
    print(f"{properties} is INCONSISTENT for n≥3")
```

---

## Finding Conflicts

### Find Small Conflicts

```python
from pid_prover import find_minimal_conflicts

# Find conflicts up to size 4 for bivariate
conflicts = find_minimal_conflicts("bivariate", max_size=4, filter_reducible=True)

print(f"Found {len(conflicts)} minimal conflicts")
for i, conflict in enumerate(conflicts, 1):
    print(f"{i}. {{{', '.join(conflict)}}}")
```

### Find Theorem 2 (noIIDLyu)

```python
from pid_prover import find_minimal_conflicts

# Theorem 2 is a size-5 conflict in multivariate
conflicts = find_minimal_conflicts("multivariate", max_size=5, filter_reducible=True)

# Look for the specific conflict
theorem_2 = {'SR', 'S0', 'M0', 'EI', 'IID'}

for conflict in conflicts:
    if set(conflict) == theorem_2:
        print(f"Found Theorem 2: {{{', '.join(conflict)}}}")
        break
```

### Find All Conflicts for a Measure

```python
from pid_prover import find_minimal_conflicts
from pid_prover.measures.validation import dataframe_to_property_list

# Get measure properties
measure_props = dataframe_to_property_list("I_CT", "multivariate")

# Find all conflicts
all_conflicts = find_minimal_conflicts("multivariate", max_size=5)

# Check which conflicts the measure violates
violated = []
for conflict in all_conflicts:
    if set(conflict).issubset(set(measure_props)):
        violated.append(conflict)

print(f"I_CT violates {len(violated)} conflicts:")
for conflict in violated:
    print(f"  {{{', '.join(conflict)}}}")
```

---

## Finding Implications

### Find Minimal Implications

```python
from pid_prover import find_minimal_implications

# Find implications for multivariate case
implications = find_minimal_implications("multivariate", premise_size=2)

print(f"Found {len(implications)} minimal implications")
for premises, conclusion in implications:
    print(f"{' ∧ '.join(premises)} ⇒ {conclusion}")
```

### Verify a Specific Implication

```python
from pid_prover import get_pid_solver
from pid_prover.solver.axioms import P
import z3

# Check if SR ∧ M0 ⇒ GP
solver = get_pid_solver("bivariate")
solver.push()

# Add premises
solver.add(P['SR'])
solver.add(P['M0'])

# Try to find counterexample: premises true, conclusion false
solver.add(z3.Not(P['GP']))

if solver.check() == z3.unsat:
    print("✓ SR ∧ M0 ⇒ GP is a valid implication")
else:
    print("✗ SR ∧ M0 ⇒ GP is NOT an implication")

solver.pop()
```

### Find All Implications with a Specific Conclusion

```python
from pid_prover import find_minimal_implications

# Find all implications that conclude GP
implications = find_minimal_implications("bivariate", premise_size=2)

gp_implications = [(premises, conclusion) for premises, conclusion in implications
                   if conclusion == "GP"]

print(f"Implications concluding GP:")
for premises, conclusion in gp_implications:
    print(f"  {' ∧ '.join(premises)} ⇒ {conclusion}")
```

---

## Property Inference

### Find Mandatory Properties

```python
from pid_prover import infer_property_consequences

# Start with desired properties
desired = ['SR', 'S0', 'GP']

# Find what's mandatory/forbidden
mandatory, forbidden = infer_property_consequences(desired, "bivariate")

print(f"Desired: {desired}")
print(f"Mandatory: {mandatory}")
print(f"Forbidden: {forbidden}")
```

### Check if Adding a Property is Safe

```python
from pid_prover import get_pid_solver
from pid_prover.solver.axioms import P
import z3

# Current properties
current = ['SR', 'S0', 'M0', 'GP']

# Want to add IID - is it consistent?
solver = get_pid_solver("multivariate")
solver.push()
solver.add(z3.And([P[prop] for prop in current + ['IID']]))
result = solver.check()
solver.pop()

if result == z3.sat:
    print("✓ Safe to add IID")
else:
    print("✗ Adding IID creates conflict")
```

### Find All Compatible Properties

```python
from pid_prover import get_pid_solver
from pid_prover.solver.axioms import P, prop_names
import z3

# Base properties
base = ['SR', 'S0']

# Find all properties compatible with base
solver = get_pid_solver("bivariate")
compatible = []

for prop in prop_names:
    if prop in base:
        continue

    solver.push()
    solver.add(z3.And([P[p] for p in base + [prop]]))
    if solver.check() == z3.sat:
        compatible.append(prop)
    solver.pop()

print(f"Properties compatible with {base}:")
print(compatible)
```

---

## Designing New Measures

### Step-by-Step Measure Design

```python
from pid_prover import get_pid_solver, infer_property_consequences
from pid_prover.solver.axioms import P, prop_names
import z3

# Step 1: Choose core properties
core_properties = ['SR', 'S0', 'M0']

# Step 2: Check consistency
solver = get_pid_solver("multivariate")
solver.push()
solver.add(z3.And([P[prop] for prop in core_properties]))
if solver.check() != z3.sat:
    print("Core properties are inconsistent!")
    exit()
solver.pop()

print(f"✓ Core properties {core_properties} are consistent")

# Step 3: Find mandatory properties
mandatory, forbidden = infer_property_consequences(core_properties, "multivariate")
print(f"Mandatory: {mandatory}")
print(f"Forbidden: {forbidden}")

# Step 4: Find optional properties
optional = [p for p in prop_names
            if p not in core_properties
            and p not in mandatory
            and p not in forbidden]
print(f"Optional: {optional}")

# Step 5: Try adding optional properties
for prop in optional[:5]:  # Try first 5
    test_set = core_properties + mandatory + [prop]
    solver.push()
    solver.add(z3.And([P[p] for p in test_set]))
    if solver.check() == z3.sat:
        print(f"  ✓ Can add {prop}")
    solver.pop()
```

### Compare with Existing Measures

```python
from pid_prover.measures import measures_df
from pid_prover.measures.validation import dataframe_to_property_list

# Your measure
my_properties = {'SR', 'S0', 'M0', 'GP', 'LP0'}

# Find most similar existing measure
def jaccard_similarity(set1, set2):
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    return intersection / union if union > 0 else 0

similarities = []
for measure_name in measures_df.columns:
    measure_props = set(dataframe_to_property_list(measure_name, "bivariate"))
    sim = jaccard_similarity(my_properties, measure_props)
    similarities.append((measure_name, sim))

similarities.sort(key=lambda x: x[1], reverse=True)

print("Most similar measures:")
for measure, sim in similarities[:5]:
    print(f"  {measure}: {sim:.2f}")
```

---

## Direct Solver Access

### Create and Use a Solver

```python
from pid_prover import get_pid_solver
from pid_prover.solver.axioms import P
import z3

# Create solver with PID axioms loaded
solver = get_pid_solver("bivariate")

# Add constraints
solver.add(P["SR"])
solver.add(P["S0"])

# Check satisfiability
result = solver.check()
print(f"Satisfiable: {result == z3.sat}")
```

### Access the Property Dictionary

```python
from pid_prover.solver.axioms import P, prop_names

# P is a dictionary of Z3 boolean variables
print("Available properties:")
for prop in prop_names:
    print(f"  {prop}: {P[prop]}")

# Use in Z3 expressions
import z3
expr = z3.And(P["SR"], P["GP"])
print(f"Expression: {expr}")
```

### Check Property Set Consistency

```python
from pid_prover import get_pid_solver
from pid_prover.solver.axioms import P
import z3

def check_consistency(props, case="bivariate"):
    """Check if a property set is consistent."""
    solver = get_pid_solver(case)
    result = solver.check(z3.And([P[p] for p in props]))

    if result == z3.sat:
        return True, "Consistent"
    elif result == z3.unsat:
        return False, "Inconsistent (conflict)"
    else:
        return None, "Unknown (timeout or too complex)"

# Test a property set
props = ["SR", "S0", "M0", "GP"]
consistent, msg = check_consistency(props)
print(f"{props}: {msg}")
```

### Access Measures Data

```python
from pid_prover.measures import measures_df

# View all measures
print(measures_df)

# Check specific measure
print(measures_df["I_min"])

# Check specific property for all measures
print(measures_df.loc["SR"])

# Get list of all measure names
from pid_prover.measures.data import measure_names
print(f"Total measures: {len(measure_names)}")
print(measure_names)

# Get bivariate-only measures
from pid_prover.measures.data import bivariate_only_measures
print(f"Bivariate-only: {bivariate_only_measures}")
```

---

## Advanced Z3 Usage

### Check Implication

```python
from pid_prover import get_pid_solver
from pid_prover.solver.axioms import P
import z3

# Check if SR ∧ M0 ⇒ GP
solver = get_pid_solver("bivariate")

# Add premises
solver.push()
solver.add(P['SR'])
solver.add(P['M0'])

# Try to find counterexample: premises true, conclusion false
solver.add(z3.Not(P['GP']))

if solver.check() == z3.unsat:
    print("SR ∧ M0 ⇒ GP is TRUE")
else:
    print("SR ∧ M0 ⇒ GP is FALSE")

solver.pop()
```

### Extract Model (Satisfying Assignment)

```python
from pid_prover import get_pid_solver
from pid_prover.solver.axioms import P, prop_names
import z3

# Find a satisfying assignment for {SR, GP}
solver = get_pid_solver("bivariate")
solver.push()
solver.add(z3.And(P['SR'], P['GP']))

if solver.check() == z3.sat:
    model = solver.model()

    print("Satisfying assignment:")
    for prop in prop_names:
        value = model.eval(P[prop])
        if value:
            print(f"  {prop}: {value}")

solver.pop()
```

### Custom Constraints

```python
from pid_prover import get_pid_solver
from pid_prover.solver.axioms import P
import z3

solver = get_pid_solver("multivariate")

# Add custom constraint: Exactly one of {LP0, LP1, GP}
solver.push()
solver.add(z3.Sum([
    z3.If(P['LP0'], 1, 0),
    z3.If(P['LP1'], 1, 0),
    z3.If(P['GP'], 1, 0)
]) == 1)

# Add other properties
solver.add(P['SR'])
solver.add(P['S0'])

if solver.check() == z3.sat:
    model = solver.model()
    print("Solution found:")
    for prop in ['SR', 'S0', 'LP0', 'LP1', 'GP']:
        print(f"  {prop}: {model.eval(P[prop])}")

solver.pop()
```

---

## Batch Analysis

### Analyze All Measures

```python
from pid_prover.measures import measures_df
from pid_prover.measures.validation import dataframe_to_property_list
from pid_prover import get_pid_solver
from pid_prover.solver.axioms import P
import z3

# Check all measures for both cases
results = {}

for measure_name in measures_df.columns:
    results[measure_name] = {}

    for case in ["bivariate", "multivariate"]:
        # Skip bivariate-only measures for multivariate
        from pid_prover.measures.data import bivariate_only_measures
        if case == "multivariate" and measure_name in bivariate_only_measures:
            results[measure_name][case] = "N/A"
            continue

        properties = dataframe_to_property_list(measure_name, case)
        solver = get_pid_solver(case)
        solver.push()
        solver.add(z3.And([P[prop] for prop in properties]))
        is_consistent = solver.check() == z3.sat
        solver.pop()

        results[measure_name][case] = "✓" if is_consistent else "✗"

# Print results table
print(f"{'Measure':<12} {'Bivariate':<12} {'Multivariate':<12}")
print("-" * 36)
for measure, result in results.items():
    print(f"{measure:<12} {result['bivariate']:<12} {result.get('multivariate', 'N/A'):<12}")
```

### Property Coverage Analysis

```python
from pid_prover.measures import measures_df
from pid_prover.measures.validation import dataframe_to_property_list

# Count how many measures have each property
property_counts = {}

for prop_name in measures_df.index:
    count = 0
    for measure_name in measures_df.columns:
        props = dataframe_to_property_list(measure_name, "bivariate")
        if prop_name in props:
            count += 1
    property_counts[prop_name] = count

# Sort by coverage
sorted_props = sorted(property_counts.items(), key=lambda x: x[1], reverse=True)

print("Property coverage (bivariate):")
for prop, count in sorted_props:
    pct = 100 * count / len(measures_df.columns)
    print(f"  {prop:<5}: {count:>2}/{len(measures_df.columns)} ({pct:>5.1f}%)")
```

### Find Measure Families

```python
from pid_prover.measures import measures_df
from pid_prover.measures.validation import dataframe_to_property_list

def jaccard_similarity(set1, set2):
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    return intersection / union if union > 0 else 0

# Find highly similar measure pairs
threshold = 0.8
similar_pairs = []

measures = list(measures_df.columns)
for i, m1 in enumerate(measures):
    props1 = set(dataframe_to_property_list(m1, "bivariate"))
    for m2 in measures[i+1:]:
        props2 = set(dataframe_to_property_list(m2, "bivariate"))
        sim = jaccard_similarity(props1, props2)

        if sim >= threshold:
            similar_pairs.append((m1, m2, sim))

similar_pairs.sort(key=lambda x: x[2], reverse=True)

print(f"Highly similar measures (≥{threshold}):")
for m1, m2, sim in similar_pairs:
    print(f"  {m1} ~ {m2}: {sim:.3f}")
```

---

## Performance Tips

### Caching Solver Results

```python
from pid_prover import get_pid_solver
from pid_prover.solver.axioms import P
import z3

# Create solver once
solver = get_pid_solver("bivariate")

# Reuse for multiple checks
property_sets = [
    ['SR', 'GP'],
    ['SR', 'GP', 'IID'],
    ['SR', 'S0', 'M0']
]

for props in property_sets:
    solver.push()
    solver.add(z3.And([P[prop] for prop in props]))
    result = solver.check()
    solver.pop()
    print(f"{props}: {result}")
```

### Parallel Analysis (Multiple Processes)

```python
from multiprocessing import Pool
from pid_prover.measures import measures_df
from pid_prover.measures.validation import dataframe_to_property_list
from pid_prover import get_pid_solver
from pid_prover.solver.axioms import P
import z3

def check_measure(measure_name):
    """Check a single measure (for parallel execution)."""
    properties = dataframe_to_property_list(measure_name, "multivariate")
    solver = get_pid_solver("multivariate")
    solver.push()
    solver.add(z3.And([P[prop] for prop in properties]))
    is_consistent = solver.check() == z3.sat
    solver.pop()
    return measure_name, is_consistent

# Run in parallel
if __name__ == '__main__':
    with Pool(4) as pool:
        results = pool.map(check_measure, measures_df.columns)

    for measure, consistent in results:
        status = "✓" if consistent else "✗"
        print(f"{measure}: {status}")
```

---

## Testing Your Code

### Run All Tests

```bash
# Run all tests with verbose output
pytest tests/ -v

# Run tests quietly
pytest tests/
```

### Run Specific Test Modules

```bash
# Test solver functionality
pytest tests/test_solver.py -v

# Test measure validation
pytest tests/test_measures.py -v

# Test analysis functions
pytest tests/test_analysis.py -v

# Test filtering utilities
pytest tests/test_filtering.py -v
```

### Run Tests Matching a Pattern

```bash
# Run only tests with "validation" in the name
pytest tests/ -k "validation"

# Run only bivariate tests
pytest tests/ -k "bivariate"

# Run only multivariate tests
pytest tests/ -k "multivariate"
```

### Run with Coverage Report

```bash
# Generate coverage report
pytest --cov=pid_prover tests/

# Generate coverage with missing lines
pytest --cov=pid_prover --cov-report=term-missing tests/

# Generate HTML coverage report
pytest --cov=pid_prover --cov-report=html tests/
# Then open htmlcov/index.html
```

### Run Specific Test Functions

```bash
# Run a specific test
pytest tests/test_solver.py::test_get_pid_solver -v

# Run a specific test class
pytest tests/test_measures.py::TestMeasureValidation -v
```

### Test Your Custom Code

Use the PID Prover in your own tests:

```python
# test_my_measure.py
import pytest
from pid_prover import get_pid_solver, infer_property_consequences
from pid_prover.solver.axioms import P
import z3

def test_my_measure_is_consistent():
    """Test that my proposed measure is consistent."""
    my_props = ["SR", "S0", "M0", "GP"]

    solver = get_pid_solver("bivariate")
    solver.push()
    solver.add(z3.And([P[prop] for prop in my_props]))
    result = solver.check()
    solver.pop()

    assert result == z3.sat, f"Measure is inconsistent: {my_props}"

def test_my_measure_mandatory_properties():
    """Test that mandatory properties are included."""
    my_props = ["SR", "S0", "M0"]

    results = infer_property_consequences(my_props, "bivariate")
    mandatory = results["Mandatory"]

    # Check that all mandatory properties are in my design
    for prop in mandatory:
        assert prop in my_props, f"Missing mandatory property: {prop}"

@pytest.mark.parametrize("case", ["bivariate", "multivariate"])
def test_my_measure_both_cases(case):
    """Test measure consistency in both cases."""
    my_props = ["SR", "S0", "GP"]

    solver = get_pid_solver(case)
    result = solver.check(z3.And([P[prop] for prop in my_props]))

    assert result == z3.sat, f"Inconsistent for {case}"
```

Run your tests:
```bash
pytest test_my_measure.py -v
```

### Integration Tests

Test complete workflows:

```python
# test_integration.py
from pid_prover import (
    validate_measures,
    find_minimal_conflicts,
    infer_property_consequences
)

def test_full_validation_workflow():
    """Test the complete validation workflow."""
    # This should run without errors
    result = validate_measures()
    assert isinstance(result, bool)

def test_conflict_discovery_workflow():
    """Test conflict discovery workflow."""
    conflicts = find_minimal_conflicts("bivariate", max_size=3)
    assert isinstance(conflicts, list)
    assert len(conflicts) > 0

def test_inference_workflow():
    """Test property inference workflow."""
    results = infer_property_consequences(["SR", "GP"], "bivariate")
    assert "Mandatory" in results
    assert "Forbidden" in results
    assert isinstance(results["Mandatory"], list)
    assert isinstance(results["Forbidden"], list)
```

### Continuous Integration

Example GitHub Actions workflow:

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]

    steps:
    - uses: actions/checkout@v4
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v5
      with:
        python-version: ${{ matrix.python-version }}
    - name: Install dependencies
      run: |
        pip install -e ".[dev]"
    - name: Run tests
      run: |
        pytest tests/ --cov=pid_prover --cov-report=xml
    - name: Upload coverage
      uses: codecov/codecov-action@v4
```

---

## See Also

- [API Reference](API.md) - Complete function signatures and parameters
- [Properties Reference](PROPERTIES.md) - All properties and measures
- [Getting Started](GETTING_STARTED.md) - Introduction for new users
- [Research Findings](../RESEARCH_FINDINGS.md) - Mathematical insights

## More Examples

For more examples, see:
- `notebooks/01_getting_started.ipynb`: Interactive tutorial
- `notebooks/02_reproducing_paper_results.ipynb`: Paper reproduction
- `notebooks/03_measure_design_workshop.ipynb`: Designing measures
- `tests/test_*.py`: Test suite with usage patterns
- `tests/test_exploration_*.py`: Advanced research explorations
