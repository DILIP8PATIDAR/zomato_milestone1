# tests/test_loader.py — Phase 5.6
# Verifies that the dataset loads correctly and required columns are present.

import pytest
import pandas as pd
from data.loader import load_dataset_as_df, REQUIRED_FIELDS


def test_load_returns_dataframe():
    """Dataset loader returns a non-empty pandas DataFrame."""
    df = load_dataset_as_df()
    assert isinstance(df, pd.DataFrame), "Expected a DataFrame"
    assert len(df) > 0, "DataFrame should not be empty"


def test_required_columns_present():
    """All REQUIRED_FIELDS are present in the loaded DataFrame."""
    df = load_dataset_as_df()
    for field in REQUIRED_FIELDS:
        assert field in df.columns, f"Missing column: {field}"


def test_cache_returns_same_object():
    """Second call to load_dataset_as_df() returns the cached object (same id)."""
    df1 = load_dataset_as_df()
    df2 = load_dataset_as_df()
    assert df1 is df2, "Expected the same cached DataFrame object"
