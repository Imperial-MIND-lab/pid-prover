# Contributing

Bug reports, corrections and new results are welcome: open an issue or a pull request on
[GitHub](https://github.com/Imperial-MIND-lab/pid-prover).

## Setup

```bash
git clone https://github.com/Imperial-MIND-lab/pid-prover.git
cd pid-prover
pip install -e ".[dev]"
pytest
```

## Updating the data

All content comes from three places; the tests and the generated tables in the docs follow
from them. After any change, run `pid-prover sync-docs` and `pytest`.

- **Table 5** ([`src/pid_prover/data/table5.csv`](src/pid_prover/data/table5.csv)): one row
  per property, one column per measure, written with the symbols of the paper
  (see [Table 5 entries](docs/REFERENCE.md#table-5-entries)).
- **Theorems** (`THEOREMS` in [`src/pid_prover/theorems.py`](src/pid_prover/theorems.py)):
  each result is one line, e.g.

  ```python
  T("Theo. 2", "incompatible", ("SR", "S0", "M0", "TC")),
  T("Theo. 5", "implies", ("BP",), ("SE", "TE"), case="bivariate"),
  ```

  Set `derived=True` if the result follows from the others; the tests check this flag in both
  directions, so they also catch results that make an existing one redundant.
- **Properties and measures** (`PROPERTIES` in
  [`properties.py`](src/pid_prover/properties.py), `MEASURES` in
  [`measures.py`](src/pid_prover/measures.py)): a new property also needs a row in the CSV, and
  a new measure a column.

If `validate_measures` fails after a change, it prints a minimal set of contradictory entries,
which points to the table entry or theorem to double-check.

## Code

- Keep functions small and documented with NumPy-style docstrings, with a line length of 100.
- Add a test for every new feature; the paper's results are covered by regression tests in
  `tests/test_analysis.py`.

By contributing, you agree that your contributions will be licensed under the MIT License.
