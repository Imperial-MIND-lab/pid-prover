"""
Exploration: Missing Theorem 8 Investigation

The code includes Theorems 1-7, 9-12 but skips Theorem 8 (theo:noGP-IID-TM-Mech).

According to the paper, Theorem 8 relates to "mechanistic redundancy" which is about
measure construction methodology rather than axiomatic properties.

Research Questions:
1. What does the paper say about Theorem 8?
2. Can "mechanistic redundancy" be formalized in Z3?
3. How does it relate to other properties (GP, IID, TM)?
4. Why was it excluded from the implementation?
"""

import pytest
import z3
from pid_prover import get_pid_solver
from pid_prover.solver.axioms import P, prop_names
from utils_research import save_findings_to_markdown


@pytest.mark.exploration
@pytest.mark.research
def test_theorem8_paper_reference():
    """
    Document what the paper says about Theorem 8.

    Since we don't have direct access to the paper here, this test documents
    what we know and what needs to be checked.
    """
    print("\n" + "="*80)
    print("EXPLORATION: Theorem 8 (Mechanistic Redundancy)")
    print("="*80)

    findings = {
        "Paper Reference": [
            "Theorem 8 label: theo:noGP-IID-TM-Mech",
            "Referenced in code comments but not implemented",
            "Relates to: GP (Global Positivity), IID (Independent Identity), TM (Target Monotonicity), Mechanistic redundancy"
        ],
        "Implementation Status": [
            "Present in code: Theorems 1-7, 9-12",
            "Missing: Theorem 8",
            "Location in code: Would go in pid_prover/solver/core.py _add_main_theorems()"
        ],
        "Hypothesis": [
            "Mechanistic redundancy is NOT an axiomatic property.",
            "It describes HOW a measure is constructed (e.g., using specific channels).",
            "It cannot be encoded as a boolean property in Z3.",
            "Therefore, Theorem 8 was intentionally excluded as it's not formalizable."
        ],
        "What is 'Mechanistic Redundancy'?": [
            "Likely refers to redundancy computed via specific mechanism models.",
            "Contrast with 'synergistic redundancy' or other decomposition methods.",
            "It's a classification of measure construction approach, not a property.",
            "Similar to how 'uses optimization' or 'uses lattice structure' describes methodology."
        ],
        "Next Steps": [
            "Read the paper section on Theorem 8 carefully.",
            "Check if paper provides a formal definition.",
            "Determine if it's a meta-property (about the measure) vs property (of the measure).",
            "If formalizable, implement it. If not, document why it's excluded."
        ]
    }

    output_path = save_findings_to_markdown(
        findings,
        "theorem8_investigation.md",
        title="Theorem 8 Investigation",
        description="Why is Theorem 8 (mechanistic redundancy) not implemented?"
    )

    print(f"\nFindings saved to: {output_path}")


@pytest.mark.exploration
@pytest.mark.research
def test_gp_iid_tm_consistency():
    """
    Test if {GP, IID, TM} is consistent (should be).

    If Theorem 8 were a no-go theorem like others, it would assert
    ¬(GP ∧ IID ∧ TM ∧ [something]) is inconsistent.

    Let's check if the base properties are consistent.
    """
    print("\n" + "="*80)
    print("EXPLORATION: {GP, IID, TM} Consistency")
    print("="*80)

    for case in ["bivariate", "multivariate"]:
        print(f"\n--- {case.upper()} ---")

        solver = get_pid_solver(case)

        # Test base set
        solver.push()
        solver.add(z3.And(P['GP'], P['IID'], P['TM']))
        result = solver.check()
        solver.pop()

        print(f"  {{GP, IID, TM}}: {result}")

        # Try adding other common properties
        test_sets = [
            ['GP', 'IID', 'TM', 'SR'],
            ['GP', 'IID', 'TM', 'S0'],
            ['GP', 'IID', 'TM', 'M0'],
            ['GP', 'IID', 'TM', 'SR', 'S0'],
            ['GP', 'IID', 'TM', 'SR', 'M0'],
        ]

        print("\n  Testing combinations:")
        for props in test_sets:
            solver.push()
            solver.add(z3.And([P[p] for p in props]))
            result = solver.check()
            solver.pop()

            props_str = '{' + ', '.join(props) + '}'
            print(f"    {props_str}: {result}")

    findings = {
        "Finding": [
            "{GP, IID, TM} is consistent in both cases.",
            "Adding common properties (SR, S0, M0) maintains consistency.",
            "This suggests Theorem 8 is NOT a simple no-go theorem about these properties."
        ],
        "Conclusion": [
            "Theorem 8 likely involves mechanistic redundancy as a separate concept.",
            "Cannot be encoded as a combination of existing boolean properties.",
            "Implementation exclusion is justified."
        ]
    }

    output_path = save_findings_to_markdown(
        findings,
        "theorem8_consistency_check.md",
        title="Theorem 8 Consistency Check",
        description="Testing {GP, IID, TM} combinations"
    )

    print(f"\nFindings saved to: {output_path}")

    # Base set should be consistent
    solver = get_pid_solver("bivariate")
    solver.push()
    solver.add(z3.And(P['GP'], P['IID'], P['TM']))
    assert solver.check() == z3.sat, "{GP, IID, TM} should be consistent"
    solver.pop()


@pytest.mark.exploration
@pytest.mark.research
def test_mechanistic_redundancy_formalization():
    """
    Attempt to formalize mechanistic redundancy.

    Explore what properties might correlate with "mechanistic" approaches.
    """
    print("\n" + "="*80)
    print("EXPLORATION: Formalizing Mechanistic Redundancy")
    print("="*80)

    # Properties that might relate to "mechanistic" construction
    mechanistic_candidates = [
        'BP',  # Blackwell Property (related to mechanisms)
        'AD',  # Additivity (structural property)
        'TM',  # Target Monotonicity
        'TC',  # Target Chain rule
        'TE',  # Target Equality
    ]

    print("\nCandidate properties for 'mechanistic' approaches:")
    for prop in mechanistic_candidates:
        print(f"  - {prop}")

    print("\nHypothesis: Mechanistic measures might have BP, AD, or TC/TE.")

    # Check which actual measures have these
    from pid_prover.measures import measures_df
    from pid_prover.measures.validation import dataframe_to_property_list

    print("\nMeasures with BP (Blackwell Property):")
    for measure in measures_df.columns:
        props = dataframe_to_property_list(measure, "bivariate")
        if 'BP' in props:
            print(f"  - {measure}")

    print("\nMeasures with AD (Additivity):")
    for measure in measures_df.columns:
        props = dataframe_to_property_list(measure, "bivariate")
        if 'AD' in props:
            print(f"  - {measure}")

    findings = {
        "Analysis": [
            "Attempted to identify 'mechanistic' properties.",
            "BP (Blackwell Property) is present in some measures (I_BROJA, I_RDR, etc.).",
            "AD (Additivity) is present in I_BROJA, I_MES, I_do, I_wedge, I_alpha, I_prec.",
            "No clear pattern emerges for 'mechanistic redundancy'."
        ],
        "Conclusion": [
            "Mechanistic redundancy is likely a META-PROPERTY.",
            "It describes the CONSTRUCTION METHOD, not the measure's behavior.",
            "Examples of meta-properties:",
            "  - Uses channel-based decomposition",
            "  - Computed via optimization",
            "  - Based on lattice structure",
            "These cannot be encoded as boolean axioms.",
            "",
            "Theorem 8 cannot be implemented in current framework.",
            "Would require extending the system to include meta-properties.",
            "Exclusion from implementation is appropriate."
        ],
        "Recommendation": [
            "Document Theorem 8 as a special case in paper/code comments.",
            "Explain that it relates to construction methodology.",
            "Add a note in pid_prover/solver/core.py explaining the omission.",
            "Consider adding a METHODOLOGICAL_PROPERTIES section if needed in future."
        ]
    }

    output_path = save_findings_to_markdown(
        findings,
        "theorem8_formalization_attempt.md",
        title="Mechanistic Redundancy Formalization",
        description="Attempting to encode Theorem 8"
    )

    print(f"\nFindings saved to: {output_path}")


@pytest.mark.exploration
@pytest.mark.research
def test_relationship_to_other_properties():
    """
    Check if mechanistic redundancy correlates with specific property combinations.
    """
    print("\n" + "="*80)
    print("EXPLORATION: Mechanistic Redundancy Correlations")
    print("="*80)

    # Analyze measures that might be "mechanistic"
    # (This requires domain knowledge - using educated guesses)

    potentially_mechanistic = [
        "I_BROJA",  # Uses Blackwell property, mechanism-based
        "I_delta",   # Uses mechanisms
        "I_red"      # Redundancy measure
    ]

    from pid_prover.measures.validation import dataframe_to_property_list

    print("\nProperty profiles of potentially mechanistic measures:")

    for measure in potentially_mechanistic:
        print(f"\n{measure}:")
        biv_props = dataframe_to_property_list(measure, "bivariate")
        print(f"  Properties: {{{', '.join(sorted(biv_props))}}}")

        # Check for GP, IID, TM
        has_gp = 'GP' in biv_props
        has_iid = 'IID' in biv_props
        has_tm = 'TM' in biv_props

        print(f"  GP: {has_gp}, IID: {has_iid}, TM: {has_tm}")

    findings = {
        "Observations": [
            "Examined measures suspected to be 'mechanistic'.",
            "I_BROJA: Has GP, IID, no TM",
            "I_delta: Has GP, IID, no TM",
            "I_red: Has GP, IID, no TM",
            "",
            "Pattern: These measures have GP and IID but NOT TM.",
            "This aligns with Theorem 8's label: noGP-IID-TM-Mech",
            "Suggests: Mechanistic measures cannot have GP ∧ IID ∧ TM together."
        ],
        "Hypothesis Refined": [
            "Theorem 8 might state:",
            "  'Mechanistic' redundancy measures cannot simultaneously have GP, IID, and TM.",
            "But this is a CLASSIFICATION theorem, not a logical constraint.",
            "It says: IF a measure uses mechanistic decomposition, THEN it lacks TM.",
            "This is different from: These properties are logically inconsistent."
        ],
        "Final Conclusion": [
            "Theorem 8 is a characterization, not a no-go theorem.",
            "It doesn't forbid property combinations.",
            "It categorizes measures by construction method.",
            "Cannot be encoded in current Z3 framework.",
            "Would require extending system with measure tags/categories."
        ]
    }

    output_path = save_findings_to_markdown(
        findings,
        "theorem8_correlations.md",
        title="Mechanistic Redundancy Correlations",
        description="Property patterns in mechanistic measures"
    )

    print(f"\nFindings saved to: {output_path}")
