# Properties and Measures Reference

This document provides a comprehensive reference for all properties and measures used in the PID Theorem Prover.

## Properties

The system analyzes **20 properties** that PID measures may or may not satisfy. These properties describe various desirable characteristics of information decomposition measures.

### Property List

| Code | Full Name | Description |
|------|-----------|-------------|
| **SR** | Self-redundancy | The redundancy between a source and itself equals the mutual information |
| **S0** | Weak Symmetry | Measure is invariant under permutations of sources |
| **S1** | Strong Symmetry | Stronger form of symmetry including all source permutations |
| **M0** | Weak Monotonicity | Adding sources does not decrease redundancy |
| **M1** | Strong Monotonicity | Stronger form of monotonicity constraint |
| **GP** | Global Positivity | All atoms are non-negative |
| **LP0** | Weak Local Positivity | Local positivity in weak form |
| **LP1** | Strong Local Positivity | All partial information atoms are non-negative |
| **ID** | Identity | Identity property for trivial decompositions |
| **IID** | Independent Identity | Identity holds even when sources are independent |
| **TM** | Target Monotonicity | Redundancy increases with target refinement |
| **TC** | Target Chain Rule | Chain rule holds for target variables |
| **BP** | Blackwell Property | Respects Blackwell ordering of experiments |
| **TE** | Target Equality | Equal targets yield equal redundancy |
| **BB** | Blackboard Bold | Blackboard property for information processing |
| **AD** | Additivity | Decomposition is additive across independent components |
| **CO** | Continuity | Measure varies continuously with distributions |
| **LB** | Lower Bound | Redundancy provides lower bound on mutual information |
| **EI** | Equivalence-class Invariance | Invariant under equivalence class transformations |
| **SE** | Subset Equality | Redundancy equals mutual information for single sources |

### Property Relationships

Some properties have logical relationships:

- **Strong implies Weak**: S1 → S0, M1 → M0, LP1 → LP0
- **Known conflicts**: Certain property combinations are impossible (see no-go theorems in [RESEARCH_FINDINGS.md](../RESEARCH_FINDINGS.md))
- **Known implications**: Some properties necessarily imply others

For detailed analysis of property conflicts and implications, see the research findings.

## Measures

The system validates **19 PID measures** from the literature. Each measure specifies which properties it claims to satisfy.

### Measure List

| Measure | Full Name | Notes |
|---------|-----------|-------|
| **I_min** | Williams & Beer minimum | Original PID measure |
| **I_MMI** | Maximum Mutual Information | Griffith et al. |
| **I_RDR** | Redundancy-Diamond-Redundancy | Kolchinsky |
| **I_BROJA*** | BROJA measure | Bivariate only |
| **I_delta*** | Delta measure | Bivariate only |
| **I_red*** | Redundancy measure | Bivariate only |
| **I_IG** | Information Gain | Finn & Lizier |
| **I_RAV** | RAV measure | Rauh et al. |
| **I_CT** | Consistent Transfer | Chicharro & Panzeri |
| **I_RR** | Reconnoiter-Redundancy | |
| **I_DEP*** | Dependency measure | Bivariate only |
| **I_CCS** | CCS measure | James et al. |
| **I_PM** | Parity Monotonicity | |
| **I_SX** | SX measure | |
| **I_MES** | MES measure | |
| **I_do** | Do-calculus measure | |
| **I_wedge** | Wedge measure | Harder et al. |
| **I_alpha** | Alpha measure | Barrett |
| **I_prec** | Precision measure | |

**Note**: Measures marked with * are **bivariate-only** (n=2 only) and are not evaluated in multivariate cases (n≥3).

### Measure Data Access

All measure property satisfaction data is available via the Python API:

```python
from pid_prover.measures import measures_df

# View all measures and their properties
print(measures_df)

# Check specific measure
print(measures_df["I_min"])

# Check specific property across all measures
print(measures_df.loc["SR"])
```

## Cases: Bivariate vs Multivariate

The PID framework distinguishes between two cases:

### Bivariate (n=2)
- **Definition**: Exactly two sources (X₁, X₂) and one target (T)
- **Measure count**: All 19 measures apply
- **Property landscape**: Some property combinations possible only for n=2

### Multivariate (n≥3)
- **Definition**: Three or more sources (X₁, X₂, ..., Xₙ) and one target (T)
- **Measure count**: 15 measures (excludes 4 bivariate-only measures)
- **Property landscape**: More constrained; some property sets become impossible

**Important**: Some theorems only apply to multivariate cases. For example, Theorem 2 (noIIDLyu) proves that {S0, M0, SR, EI, IID} is impossible for n≥3 but may be consistent for n=2.

## Known Issues

### Multivariate Validation Failures

Five measures fail multivariate validation due to an inconsistency with Theorem 2 (noIIDLyu):

- **I_CT** (Consistent Transfer)
- **I_RR** (Reconnoiter-Redundancy)
- **I_wedge** (Wedge measure)
- **I_alpha** (Alpha measure)
- **I_prec** (Precision measure)

**Issue**: These measures claim to satisfy {S0, M0, SR, EI, IID}, which is proven impossible for n≥3 by Theorem 2.

**Root cause**: Systematic error in the literature's Table 1 property attributions.

**Details**: See [RESEARCH_FINDINGS.md](../RESEARCH_FINDINGS.md#multivariate-validation-failures) for comprehensive analysis, correction proposals, and mathematical proofs.

## See Also

- [API Reference](API.md) - Function signatures and usage
- [Examples Guide](EXAMPLES.md) - Practical usage examples
- [Research Findings](../RESEARCH_FINDINGS.md) - Detailed mathematical analysis
- [Getting Started](GETTING_STARTED.md) - Introduction for new users
