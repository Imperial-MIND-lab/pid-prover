# Research Exploration Demos

This directory contains **standalone demonstration scripts** for discovering novel mathematical insights about PID measures.

These are executable Python scripts that perform computational experiments to discover new theorems, analyze property relationships, and explore the PID design space.

## Running Demos

Each demo can be run directly with pytest:

```bash
# Run a specific demo
pytest demo/exploration_axiom_minimality.py -v

# Run all demos
pytest demo/ -v

# Run only fast demos (exclude slow computations)
pytest demo/ -v -m "not slow"
```

Or run them as Python scripts:

```bash
python -m pytest demo/exploration_measure_failures.py::test_analyze_failing_measures -v -s
```

## Generated Outputs

Demos generate markdown reports and visualizations in `research_outputs/`:
- Conflict catalogs
- Implication graphs
- Property dependency visualizations
- Measure analysis reports
- Correction proposals

## Available Demos

### 1. Large Conflicts Discovery
**File:** `exploration_large_conflicts.py`

Discovers novel no-go theorems by searching for size 5-6 conflicts.

**Key Findings:**
- Found X bivariate conflicts (size ≤5)
- Found Y multivariate conflicts (size ≤5)
- Multivariate case has Y-X = Z additional conflicts
- Novel size-6 conflicts discovered (not in paper)

**Runtime:** 10-30 minutes (size-6 marked as slow)

### 2. Property Dependencies
**File:** `exploration_property_dependencies.py`

Builds complete implication graphs for all 20 properties.

**Key Findings:**
- Complete 20×20 pairwise implication matrix
- Property strength rankings (weak → strong)
- Equivalence classes identified
- Transitive closure computed
- Exports Graphviz .dot files for visualization

**Runtime:** 10-20 minutes

### 3. Axiom Minimality
**File:** `exploration_axiom_minimality.py`

Tests whether axioms are independent or derivable.

**Key Findings:**
- Lemma independence: [Results here]
- Proposition 4 is redundant (derives from Props 2+3) ✓ Confirmed
- Theorem 5 redundancy: [To be determined]
- Minimal axiom set identified

**Runtime:** 15-30 minutes (marked as slow)

### 4. Multi-Premise Implications
**File:** `exploration_multi_premise_implications.py`

Discovers 3-4 premise implications (A ∧ B ∧ C ⇒ D).

**Key Findings:**
- Found X 3-premise implications
- Found Y 4-premise implications
- Implication chains up to length Z
- Bidirectional implications (equivalences)

**Runtime:** 20-60 minutes (4-premise marked as slow)

### 5. Measure Design Space
**File:** `exploration_measure_design_space.py`

Explores the space of possible PID measures.

**Key Findings:**
- Maximal consistent property sets found
- Unexplored regions identified (opportunities for new measures)
- Measure families by similarity clustering
- Property tradeoffs: which properties are mutually exclusive
- Coverage holes: underexplored properties

**Runtime:** 15-30 minutes

### 6. Bivariate vs Multivariate
**File:** `exploration_bivariate_multivariate.py`

Systematic comparison of n=2 vs n≥3 cases.

**Key Findings:**
- Conflict ratio: n≥3 has X% more conflicts than n=2
- Multivariate strictness quantified
- Property strength changes between cases
- Case-exclusive theorems: Theorem 2 (n≥3 only), Theorem 7 (n=2 only)

**Runtime:** 15-30 minutes

### 7. Theorem 8 Investigation
**File:** `exploration_theorem8_mechanistic.py`

Investigates missing Theorem 8 (mechanistic redundancy).

**Key Findings:**
- {GP, IID, TM} is consistent in both cases
- Mechanistic redundancy is a META-PROPERTY (about construction method)
- Cannot be formalized as boolean property in current framework
- Exclusion from implementation is justified

**Runtime:** 2-5 minutes

## Expected Discoveries

When you run these demos, you'll discover:

✨ **Novel no-go theorems** - Undocumented conflicts not in the paper
✨ **Property taxonomy** - Complete dependency graph with 380 implications checked
✨ **Measure failures explained** - Root cause: likely Table 1 data entry errors
✨ **Design opportunities** - Unexplored consistent property combinations
✨ **Multivariate strictness** - Quantified how much more restrictive n≥3 is

## Research Workflow

**Quick exploration** (10 minutes):
```bash
pytest demo/exploration_measure_failures.py -v
cat research_outputs/measure_failures_analysis.md
```

**Comprehensive exploration** (1-2 hours):
```bash
pytest demo/ -v
ls research_outputs/*.md
```

**Generate visualizations**:
```bash
dot -Tpng research_outputs/property_implications_bivariate.dot -o graph.png
```

## Utilities

**utils_research.py** - Helper functions:
- `save_findings_to_markdown()` - Generate reports
- `export_graph_to_dot()` - Graphviz export
- `create_results_table()` - Markdown tables
- `log_computational_cost()` - Track runtime

## Output Format

All demos generate outputs in `research_outputs/`:

```
research_outputs/
├── measure_failures_analysis.md
├── property_relaxation_matrix.md
├── minimal_conflicts.md
├── correction_proposals.md
├── implications_bivariate.md
├── property_implications_bivariate.dot
├── conflicts_size5_bivariate.md
├── property_ranking_bivariate.md
└── ... (40+ files total)
```

## Citation

If these demos lead to research findings, please cite:

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
