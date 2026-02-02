# Contributing to PID Theorem Prover

Thank you for your interest in contributing! This project welcomes contributions from the research community.

## Development Setup

For basic installation instructions, see [Getting Started Guide](docs/GETTING_STARTED.md).

### 1. Fork and Clone

```bash
git clone https://github.com/pmediano/pid-prover.git
cd pid-prover
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install in Development Mode

```bash
pip install -e ".[dev]"
```

This installs the package with development dependencies:
- pytest: Testing framework
- pytest-cov: Coverage reporting
- black: Code formatting
- mypy: Type checking

## Development Workflow

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=pid_prover tests/

# Run specific test file
pytest tests/test_measures.py -v

# Run only fast tests (exclude slow exploration tests)
pytest tests/ -m "not slow"
```

### Code Formatting

We use Black for consistent formatting:

```bash
# Format all code
black pid_prover/ tests/

# Check formatting without changes
black --check pid_prover/ tests/
```

### Type Checking

```bash
# Run mypy
mypy pid_prover/
```

## Contributing Guidelines

### Code Style

- Follow PEP 8 guidelines
- Use Black for formatting (line length: 100)
- Add type hints to function signatures
- Write clear docstrings (NumPy style)

### Testing

- Write tests for new features
- Maintain or improve code coverage
- Mark slow tests with `@pytest.mark.slow`
- Mark exploration tests with `@pytest.mark.exploration`

### Documentation

- Update README.md for new features
- Add docstrings to all public functions
- Create or update notebooks for significant features
- Document any new properties or theorems

### Commit Messages

Use clear, descriptive commit messages:

```
Add support for custom property definitions

- Extend axioms.py to support user-defined properties
- Add validation for custom property syntax
- Update tests and documentation
```

### Pull Request Process

1. **Create a branch** for your feature:
   ```bash
   git checkout -b feature/my-new-feature
   ```

2. **Make your changes** and commit:
   ```bash
   git add .
   git commit -m "Add my new feature"
   ```

3. **Push to your fork**:
   ```bash
   git push origin feature/my-new-feature
   ```

4. **Open a Pull Request** on GitHub:
   - Describe the changes
   - Reference related issues
   - Include test results

5. **Address review feedback** if any

6. **Merge** once approved

## Types of Contributions

### 1. Bug Reports

Found a bug? Open an issue with:
- Description of the problem
- Steps to reproduce
- Expected vs actual behavior
- System information (Python version, OS)

### 2. Feature Requests

Have an idea? Open an issue describing:
- The feature or enhancement
- Use case and motivation
- Proposed implementation (if any)

### 3. New Measures

Adding a new PID measure:

1. Add measure data to `src/pid_prover/measures/data.py`:
   ```python
   # In measures_data dictionary
   "NEW_PROPERTY": ["Y", "N", "Y", ...]  # 19 values
   ```

2. Add to measure_names list

3. Document the source in `src/pid_prover/measures/SOURCES.md`

4. Run validation: `pytest tests/test_measures.py`

### 4. New Properties

For a list of all current properties, see [Properties Reference](docs/PROPERTIES.md).

Adding a new property:

1. Add to `src/pid_prover/solver/axioms.py`:
   ```python
   prop_names.append("NEW_PROP")
   P["NEW_PROP"] = z3.Bool("NEW_PROP")
   ```

2. Add axioms/theorems involving the property to `src/pid_prover/solver/core.py`

3. Update all existing measures in `src/pid_prover/measures/data.py`

4. Update [Properties Reference](docs/PROPERTIES.md) with the new property description

5. Add tests

### 5. New Theorems

Adding a new theorem:

1. Add to appropriate function in `src/pid_prover/solver/core.py`:
   - `_add_main_theorems()` for universal theorems
   - `_add_bivariate_theorems()` for n=2 only
   - `_add_multivariate_theorems()` for n≥3 only

2. Document the theorem with comments:
   ```python
   # Theorem X (label): Description
   solver.add(z3.Not(z3.And(P['PROP1'], P['PROP2'])))
   ```

3. Add test in `tests/test_solver.py`

### 6. Documentation

- Fix typos or unclear explanations
- Add examples to docstrings
- Improve notebook clarity
- Add new notebooks for specific use cases

## Getting Help

- **Questions:** Open a GitHub issue
- **Discussion:** Start a GitHub Discussion
- **Bugs:** Open an issue with "bug" label
- **Features:** Open an issue with "enhancement" label

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

Thank you for contributing to PID research!
