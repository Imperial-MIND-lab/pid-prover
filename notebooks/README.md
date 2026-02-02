# Jupyter Notebooks

Interactive notebooks for exploring the PID Theorem Prover toolkit.

## Prerequisites

```bash
# Install the package with notebook support
pip install -e ".[notebooks]"
```

This installs: jupyter, matplotlib, seaborn, networkx, graphviz

## Notebooks

### 01_getting_started.ipynb
**Audience:** New users, students, researchers exploring PID

Interactive introduction to the toolkit:
- Validating measures
- Finding conflicts and implications
- Property inference
- Measure analysis
- Visualizations

**Runtime:** ~5-10 minutes
**Prerequisites:** None

---

### 02_reproducing_paper_results.ipynb
**Audience:** Researchers, paper reviewers, reproducibility enthusiasts

Reproduces key results from the paper:
- Table 1: Measure validation results
- Conflict discovery (Theorem 2)
- Implication discovery
- Analysis of 5 multivariate failures
- Comparison with paper claims

**Runtime:** ~10-20 minutes
**Prerequisites:** Basic understanding of PID

---

### 03_measure_design_workshop.ipynb
**Audience:** Researchers designing new PID measures

Step-by-step guide for designing new measures:
1. Start with desired properties
2. Check consistency
3. Find mandatory/forbidden properties
4. Compare with existing measures
5. Identify opportunities for novel measures

**Runtime:** ~15-30 minutes (interactive)
**Prerequisites:** Familiarity with PID properties

## Running the Notebooks

### Local Jupyter
```bash
cd notebooks
jupyter notebook
```

### JupyterLab
```bash
cd notebooks
jupyter lab
```

### VS Code
Open notebooks directly in VS Code with the Jupyter extension.

### Google Colab
Upload notebooks to Colab, then install dependencies:
```python
!pip install git+https://github.com/pmediano/pid-prover.git
```

## Notebook Best Practices

1. **Run in order:** Execute cells sequentially from top to bottom
2. **Restart kernel:** If you encounter errors, try "Kernel → Restart & Clear Output"
3. **Save outputs:** Results can take time to compute - save notebooks with outputs
4. **Explore:** Modify parameters and experiment!

## Outputs

Notebooks generate:
- Visualizations (heatmaps, graphs)
- Analysis reports
- Comparison tables

These complement the paper's findings and support reproducibility.

## Troubleshooting

**Import errors:**
```bash
pip install -e ".[notebooks]"
```

**Z3 not found:**
```bash
pip install z3-solver
```

**Visualization issues:**
```bash
pip install matplotlib seaborn
```

**Long runtimes:**
Some analyses (large conflict searches) can take minutes. Consider:
- Using smaller `max_size` parameters
- Running on a faster machine
- Checking pre-computed results in `research_outputs/`

## Contributing

Suggestions for new notebooks? Open an issue on GitHub!

## Citation

If you use these notebooks in your research, please cite:
```bibtex
@software{mediano2025pid_prover,
  author = {Mediano, Pedro A. M.},
  title = {PID Theorem Prover},
  year = {2025},
  url = {https://github.com/pmediano/pid-prover}
}
```
