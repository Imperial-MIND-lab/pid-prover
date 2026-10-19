# Guide

All functions take the case `n` as `"bivariate"` (properties required for n = 2 sources, the
default) or `"multivariate"` (properties required for any number of sources); see
[cases](REFERENCE.md#cases). Properties are referred to by their codes (`SR`, `S0`, `LP`, `STAR`,
...), listed in the [reference](REFERENCE.md#properties). All searches run over these 20
properties. The two rows of Table 5 for (LP), `LP0` (n = 2 sources) and `LP1` (n ≥ 3 sources),
can also be used in queries.

## Checking properties

```python
from pid_prover import explain_assignment, implies, is_consistent

is_consistent(["SR", "S0", "M0", "TC"])                  # False: Theo. 2
is_consistent(["S0", "M0", "SR", "EI", "IID"], "multivariate")  # True: needs (LP) to conflict
implies(["SR", "S0", "LP"], "M1")                        # True: Prop. 7

# Check a partial truth assignment; returns None or a minimal contradictory subset
explain_assignment({"SR": True, "M0": True, "LB": False})  # ['SR', 'M0', '¬LB']
```

## Designing a measure

`infer_property_consequences` lists the properties that a set of intended properties forces
(`Mandatory`) or rules out (`Forbidden`):

```python
from pid_prover import infer_property_consequences

infer_property_consequences(["BP", "SR"], "bivariate")
# {'Consistent': True, 'Mandatory': ['SE', 'TE'], 'Forbidden': []}   (Theo. 5)
```

`find_maximal_compatible_sets` enumerates every maximal set of properties that can hold
together, optionally restricted to sets containing some required properties:

```python
from pid_prover import find_maximal_compatible_sets

for s in find_maximal_compatible_sets("multivariate", required=["SR", "S0", "M0"]):
    print(len(s), s)
```

## Discovering relations

```python
from pid_prover import find_minimal_conflicts, find_minimal_implications

# Minimal incompatible sets up to a given size. By default, a conflict is not reported if
# replacing one of its properties with a weaker one still gives a conflict.
find_minimal_conflicts("multivariate", max_size=6)

# Minimal implications with a given number of premises
find_minimal_implications("bivariate", premise_size=2)
```

Both searches are exhaustive up to the given size and take a few seconds for the sizes above.

## Measures

```python
from pid_prover import measure_properties, measures_df, validate_measures

measures_df                                   # Table 5 as a DataFrame (entries as in the paper)
measure_properties("I_RAV", "bivariate")      # properties satisfied for n = 2
validate_measures()                           # check every measure against the theorems
```

`validate_measures` sets each measure's ✓ properties to true and its ✗ properties to false. A
measure fails if this contradicts a theorem, and the contradictory entries are printed.

## Using Z3 directly

`get_pid_solver(n)` returns a `z3.Solver` loaded with the theorems of case `n`, and `P` maps
property codes to their Z3 variables, so any propositional query can be written directly:

```python
from pid_prover import P, get_pid_solver

solver = get_pid_solver("multivariate")
solver.check(P["SR"], P["S1"], P["LP0"], P["LP1"])   # unsat: Lemma 3, Prop. 4, Theo. 10

# Leave a result out to see what depends on it
solver = get_pid_solver("bivariate", exclude=("Theo. 2",))
solver.check(P["SR"], P["S0"], P["M0"], P["TC"])     # sat
```

The `THEOREMS` list holds the encoded results, and `redundant_theorems(n)` returns those that
follow from the others.

## Command line

```bash
pid-prover validate                                    # check Table 5
pid-prover theorems                                    # list theorems and derivable ones
pid-prover conflicts --case multivariate --max-size 6  # --keep-reducible to skip filtering
pid-prover implications --premises 3
pid-prover infer SR S0 LP --case multivariate          # exit code 1 if inconsistent
pid-prover maximal --require SR S0 M0
pid-prover sync-docs                                   # regenerate tables in the docs
```
