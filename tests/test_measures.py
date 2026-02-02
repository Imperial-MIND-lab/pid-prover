"""Test measures data and validation."""
import pandas as pd
import pytest
from typing import Literal
from pid_prover.measures import (
    measures_df,
    measure_names,
    bivariate_only_measures,
    dataframe_to_property_list,
    validate_measures,
)


def test_measures_df_shape():
    """Test that measures_df has the correct shape."""
    assert measures_df.shape == (20, 19), f"Expected shape (20, 19), got {measures_df.shape}"


def test_measures_df_columns():
    """Test that measures_df has correct column names."""
    assert list(measures_df.columns) == measure_names


def test_bivariate_only_measures_list():
    """Test that bivariate-only measures list is correct."""
    expected = ["I_BROJA", "I_delta", "I_red", "I_DEP"]
    assert bivariate_only_measures == expected


def test_dataframe_construction():
    """Test that the DataFrame is constructed correctly."""
    # Verify specific values
    assert measures_df.loc["SR", "I_min"] == "Y"
    assert measures_df.loc["M0", "I_RAV"] == "Y_2"
    assert measures_df.loc["M0", "I_CCS"] == "N"


def test_conversion_function_bivariate_only():
    """Test that Y_2 properties are included for bivariate but not multivariate."""
    # Test I_RAV bivariate - should include M0, TE, LB (all Y_2)
    i_rav_biv = dataframe_to_property_list("I_RAV", "bivariate")
    assert "M0" in i_rav_biv, "M0 should be included for bivariate I_RAV"
    assert "TE" in i_rav_biv, "TE should be included for bivariate I_RAV"
    assert "LB" in i_rav_biv, "LB should be included for bivariate I_RAV"

    # Test I_RAV multivariate - should NOT include M0, TE, LB (all Y_2)
    i_rav_multi = dataframe_to_property_list("I_RAV", "multivariate")
    assert "M0" not in i_rav_multi, "M0 should NOT be included for multivariate I_RAV"
    assert "TE" not in i_rav_multi, "TE should NOT be included for multivariate I_RAV"
    assert "LB" not in i_rav_multi, "LB should NOT be included for multivariate I_RAV"


def test_conversion_function_not_applicable():
    """Test that N_A properties are excluded."""
    # Test I_BROJA - should NOT include LP1 (N_A)
    i_broja_biv = dataframe_to_property_list("I_BROJA", "bivariate")
    assert "LP1" not in i_broja_biv, "LP1 should NOT be included for I_BROJA"

    i_broja_multi = dataframe_to_property_list("I_BROJA", "multivariate")
    assert "LP1" not in i_broja_multi, "LP1 should NOT be included for I_BROJA"


def test_conversion_function_empirical():
    """Test that Y_* (empirical) properties are included."""
    # Test I_IG - should include TM (Y_*)
    i_ig_biv = dataframe_to_property_list("I_IG", "bivariate")
    assert "TM" in i_ig_biv, "TM should be included for I_IG (Y_*)"

    i_ig_multi = dataframe_to_property_list("I_IG", "multivariate")
    assert "TM" in i_ig_multi, "TM should be included for I_IG (Y_*)"


def test_conversion_function_negative_values():
    """Test that N, N_dd, N_m are excluded."""
    # Test I_CCS - should NOT include M0 (N)
    i_ccs = dataframe_to_property_list("I_CCS", "bivariate")
    assert "M0" not in i_ccs, "M0 should NOT be included for I_CCS (N)"

    # Test I_PM - should NOT include M0 (N_dd)
    i_pm = dataframe_to_property_list("I_PM", "bivariate")
    assert "M0" not in i_pm, "M0 should NOT be included for I_PM (N_dd)"

    # Test I_red - should NOT include CO (N_m)
    i_red = dataframe_to_property_list("I_red", "bivariate")
    assert "CO" not in i_red, "CO should NOT be included for I_red (N_m)"


def test_validate_measures_runs():
    """Test that validate_measures runs without error."""
    # This is an integration test - just verify it completes
    result = validate_measures()
    assert isinstance(result, bool)
