"""Tests for the analyses, including the paper's results as regression checks."""
import pytest

from pid_prover.analysis import (
    explain_assignment,
    find_maximal_compatible_sets,
    find_minimal_conflicts,
    find_minimal_implications,
    get_ordered_properties,
    implies,
    infer_property_consequences,
    is_consistent,
)
from pid_prover.cli import main
from pid_prover.properties import prop_names


def as_sets(conflicts):
    return {frozenset(c) for c in conflicts}


def test_consistency_and_implication():
    assert is_consistent(["SR", "S0", "M0"], "bivariate")
    assert not is_consistent(["SR", "S0", "M0", "TC"], "bivariate")  # Theo. 2
    assert implies(["SR", "S0", "LP"], "M1", "multivariate")  # Prop. 7
    assert not implies(["SR"], "GP", "bivariate")


def test_lyu_claim_is_not_a_theorem():
    """(S0), (M0), (SR), (EI), (IID) are compatible without (LP) (Sec. 3.2 of the paper)."""
    assert is_consistent(["S0", "M0", "SR", "EI", "IID"], "multivariate")
    assert not is_consistent(["S0", "M0", "SR", "EI", "IID", "LP"], "multivariate")


def test_explain_assignment():
    assert explain_assignment({"SR": True, "M0": True}, "bivariate") is None
    core = explain_assignment({"SR": True, "M0": True, "LB": False, "AD": True}, "bivariate")
    assert sorted(core) == sorted(["SR", "M0", "¬LB"])


def test_ordering_puts_weaker_first():
    ordered = get_ordered_properties("bivariate")
    assert ordered.index("IID") < ordered.index("ID")
    assert ordered.index("S0") < ordered.index("S1")


def test_conflicts_bivariate():
    assert as_sets(find_minimal_conflicts("bivariate", max_size=6)) == {
        frozenset({"SR", "S0", "M0", "TC"}),   # Theo. 2
        frozenset({"SR", "S0", "LP", "TC"}),   # Cor. 1
    }


def test_conflicts_multivariate():
    assert as_sets(find_minimal_conflicts("multivariate", max_size=6)) == {
        frozenset({"SR", "S0", "M0", "TC"}),         # Theo. 2
        frozenset({"SR", "S0", "LP", "TC"}),         # Cor. 1
        frozenset({"S0", "SR", "EI", "LP", "IID"}),  # Theo. 1
        frozenset({"SR", "LP", "S1"}),               # Lemma 3, Prop. 4 and Theo. 10
    }


def test_conflicts_unfiltered_include_reducible_ones():
    filtered = find_minimal_conflicts("bivariate", max_size=4)
    unfiltered = find_minimal_conflicts("bivariate", max_size=4, filter_reducible=False)
    assert as_sets(filtered) < as_sets(unfiltered)


def test_implications_recover_paper_results():
    found = {(frozenset(p), c) for p, c in find_minimal_implications("bivariate", 2)}
    assert (frozenset({"M0", "SR"}), "LB") in found   # Prop. 1
    assert (frozenset({"GP", "TC"}), "TM") in found   # Prop. 5
    assert (frozenset({"M0", "TE"}), "M1") in found   # Theo. 4
    assert (frozenset({"S0", "LP"}), "M0") in found   # Prop. 4
    # No duplicates and no vacuous implications from inconsistent premises
    assert len(found) == len(find_minimal_implications("bivariate", 2))


def test_inference():
    result = infer_property_consequences(["BP", "SR"], "bivariate")
    assert result["Consistent"]
    assert {"TE", "SE"} <= set(result["Mandatory"])  # Theo. 5
    result = infer_property_consequences(["SR", "S0", "M0"], "bivariate")
    assert result["Forbidden"] == ["TC"]  # Theo. 2
    result = infer_property_consequences(["SR", "S0", "M0", "TC"], "bivariate")
    assert result == {"Consistent": False, "Mandatory": [], "Forbidden": []}


def test_maximal_compatible_sets():
    biv = find_maximal_compatible_sets("bivariate", required=["SR", "S0", "M0"])
    assert len(biv) == 1 and "TC" not in biv[0] and len(biv[0]) == 19
    multi = find_maximal_compatible_sets("multivariate", required=["SR", "S0", "M0"])
    missing = [{"LP", "TC"}, {"EI", "S1", "TC"}, {"ID", "IID", "S1", "TC"}]
    assert [set(prop_names) - set(s) for s in multi] == missing
    # Without (M0), (LP) and (M1) must go but (TC) becomes possible
    for n in ("bivariate", "multivariate"):
        no_m0 = find_maximal_compatible_sets(n, required=["SR", "S0"], excluded=["M0"])
        assert [set(prop_names) - set(s) for s in no_m0] == [{"M0", "LP", "M1"}]
    assert all(len(s) >= 17 for s in find_maximal_compatible_sets("multivariate", min_size=17))


@pytest.mark.parametrize("argv, code", [
    (["validate"], 0),
    (["infer", "SR", "S0", "LP"], 0),
    (["infer", "SR", "S0", "M0", "TC"], 1),
    (["conflicts", "--max-size", "4"], 0),
    (["implications", "--case", "multivariate", "--premises", "1"], 0),
    (["maximal", "--require", "SR", "S0", "M0"], 0),
    (["maximal", "--require", "SR", "S0", "--exclude", "M0"], 0),
    (["theorems"], 0),
])
def test_cli(argv, code, capsys):
    assert main(argv) == code
    assert capsys.readouterr().out
