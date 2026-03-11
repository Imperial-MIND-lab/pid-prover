# PID Theorem Prover

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.XXXXXXX.svg)](https://doi.org/10.5281/zenodo.XXXXXXX)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](tests/)

A tool for analyzing Partial Information Decomposition (PID) measures using automated theorem proving with Z3.

## Overview

This project uses the Z3 Theorem Prover to explore the logical landscape of Partial Information Decomposition. It encodes properties as boolean variables and uses known theorems from the literature as axioms to:

1. Validate consistency of existing PID measures
2. Discover new minimal implications (Theorems)
3. Identify minimal inconsistent sets of properties (No-go Theorems)
4. Infer mandatory and forbidden properties for proposed measures

### Validation
Validates 19 PID measures against 20 properties for both bivariate (n=2) and multivariate (n≥3) cases.

### Conflict Discovery
Finds minimal inconsistent property sets (no-go theorems) using systematic search with reducibility filtering.

### Implication Discovery
Discovers minimal logical implications between properties.

### Property Inference
Given a set of intended properties, determines what additional properties are mandatory or forbidden.

### Research Explorations
The `demo/` folder contains research exploration tests that discover novel mathematical insights:
- Novel no-go theorems (size 5-6 conflicts)
- Complete property dependency graphs
- Measure failure root cause analysis
- Design space exploration
- Multivariate strictness quantification

See [demo/README.md](demo/README.md) for details.

## Installation

```bash
# From source
git clone https://github.com/pmediano/pid-prover.git
cd pid-prover
pip install -e .
```

For detailed installation instructions, see [Getting Started Guide](docs/GETTING_STARTED.md).

## Quick Start

```python
from pid_prover import validate_measures

# Validate all PID measures
validate_measures()
```

```python
from pid_prover import infer_property_consequences

# Design a new measure
results = infer_property_consequences(["SR", "S0", "GP"], "bivariate")
print("Must satisfy:", results["Mandatory"])
print("Cannot satisfy:", results["Forbidden"])
```

For more examples, see the [Examples Guide](docs/EXAMPLES.md).

## Documentation

Choose your path based on your needs:

**New to PID Prover?**
- [Getting Started Guide](docs/GETTING_STARTED.md) - Installation and first steps

**Using the API?**
- [Examples Guide](docs/EXAMPLES.md) - Comprehensive usage examples
- [API Reference](docs/API.md) - Function signatures and parameters

**Looking for reference material?**
- [Properties Reference](docs/PROPERTIES.md) - All properties and measures

**Contributing?**
- [Contributing Guide](CONTRIBUTING.md) - How to contribute

## Repository Structure

```
pid-prover/
├── src/
│   └── pid_prover/      # Main package
│       ├── solver/      # Z3 solver setup with PID axioms
│       ├── measures/    # Measure data and validation
│       ├── analysis/    # Theorem discovery and inference
│       ├── filtering/   # Conflict reducibility checking
│       └── cli.py       # Command-line interface
├── tests/               # Unit tests and validation tests
├── demo/                # Research exploration demos
├── docs/                # Documentation
└── notebooks/           # Jupyter notebooks
```

## Properties and Measures

The system analyzes **20 properties** that PID measures may satisfy and validates **19 measures** from the literature.

For complete property definitions, measure descriptions, and known issues, see [Properties Reference](docs/PROPERTIES.md).

## Citation

If you use this software in your research, please cite the accompanying [paper](https://arxiv.org/abs/2603.06678):

```bibtex
@article{liardi2026mathematical,
      title={The mathematical landscape of partial information decomposition: A comprehensive review of properties and measures}, 
      author={Alberto Liardi and Keenan J. A. Down and George Blackburne and Matteo Neri and Pedro A. M. Mediano},
      year={2026},
      eprint={2603.06678},
      archivePrefix={arXiv},
      primaryClass={cs.IT},
      url={https://arxiv.org/abs/2603.06678}, 
}
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

Special thanks to the Z3 theorem prover team and the PID research community.
