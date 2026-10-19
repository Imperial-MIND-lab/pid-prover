"""Tests for the Table 5 data and the validation of measures."""
import pytest

from pid_prover.measures import (
    MEASURES,
    bivariate_only_measures,
    cell_value,
    measure_assignment,
    measure_properties,
    measures_df,
    table5,
    validate_measures,
)
from pid_prover.properties import row_names


def test_table_shape_and_labels():
    assert measures_df.shape == (21, 19)
    assert list(measures_df.index) == row_names
    assert list(measures_df.columns) == list(MEASURES)
    assert "CO∥" in table5.index


def test_bivariate_only_measures():
    assert bivariate_only_measures == [
        "I_BROJA", "I_delta", "I_red", "I_IG", "I_RR", "I_DEP", "I_MES", "I_do"
    ]


@pytest.mark.parametrize("entry, biv, multi", [
    ("✓", True, True), ("✓†", True, False), ("✓*", True, True), ("✓§", True, True),
    ("✗", False, False), ("✗‡", False, False), ("n.a.", None, None),
])
def test_cell_value(entry, biv, multi):
    assert cell_value(entry, "bivariate") is biv
    assert cell_value(entry, "multivariate") is multi


def test_cell_value_rejects_unknown_entries():
    with pytest.raises(ValueError):
        cell_value("Y", "bivariate")


def test_measure_properties():
    assert {"M0", "TE", "LB", "M1", "LP"} <= set(measure_properties("I_RAV", "bivariate"))
    assert "LP" not in measure_properties("I_RAV", "multivariate")  # (LP1) fails
    assert "LP" in measure_properties("I_min", "multivariate")
    assert not {"M0", "TE", "LB", "M1"} & set(measure_properties("I_RAV", "multivariate"))
    assert "LP1" not in measure_assignment("I_min", "bivariate")
    assert measure_assignment("I_min", "multivariate")["LP1"] is True
    with pytest.raises(ValueError):
        measure_assignment("I_BROJA", "multivariate")


def test_all_measures_consistent_with_theorems():
    assert validate_measures(verbose=False)
