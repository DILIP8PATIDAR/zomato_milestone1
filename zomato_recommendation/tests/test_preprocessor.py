# tests/test_preprocessor.py — Phase 5.6
# Verifies preprocessing: type casts, null removal, budget tiers, cuisine lists,
# deduplication, and location normalisation.

import pytest
import pandas as pd
from data.preprocessor import preprocess


def _make_raw_df(**overrides) -> pd.DataFrame:
    """Helper: return a minimal valid raw row as a DataFrame."""
    base = {
        "name": ["Test Restaurant"],
        "location": ["Bangalore"],
        "cuisines": ["Italian, Continental"],
        "approx_cost(for two people)": ["600"],
        "rate": ["4.1/5"],
        "votes": [120],
        "online_order": ["Yes"],
        "book_table": ["No"],
        "rest_type": ["Casual Dining"],
    }
    base.update(overrides)
    return pd.DataFrame(base)


def test_columns_renamed():
    df = preprocess(_make_raw_df())
    assert "approx_cost" in df.columns
    assert "rating" in df.columns
    assert "approx_cost(for two people)" not in df.columns
    assert "rate" not in df.columns


def test_approx_cost_cast_to_numeric():
    df = preprocess(_make_raw_df(**{"approx_cost(for two people)": ["1,200"]}))
    assert df["approx_cost"].iloc[0] == 1200.0


def test_rating_stripped_of_suffix():
    """Rating '4.1/5' should be parsed to float 4.1."""
    df = preprocess(_make_raw_df())
    assert df["rating"].iloc[0] == pytest.approx(4.1)


def test_null_rating_dropped():
    """Rows with 'NEW' or '-' rating should be dropped."""
    raw = _make_raw_df(**{"rate": ["NEW"]})
    df = preprocess(raw)
    assert len(df) == 0


def test_budget_tier_low():
    raw = _make_raw_df(**{"approx_cost(for two people)": ["200"]})
    df = preprocess(raw)
    assert df["budget_tier"].iloc[0] == "low"


def test_budget_tier_medium():
    raw = _make_raw_df(**{"approx_cost(for two people)": ["600"]})
    df = preprocess(raw)
    assert df["budget_tier"].iloc[0] == "medium"


def test_budget_tier_high():
    raw = _make_raw_df(**{"approx_cost(for two people)": ["1200"]})
    df = preprocess(raw)
    assert df["budget_tier"].iloc[0] == "high"


def test_cuisines_list_parsed():
    df = preprocess(_make_raw_df())
    cuisines_list = df["cuisines_list"].iloc[0]
    assert isinstance(cuisines_list, list)
    assert "italian" in cuisines_list
    assert "continental" in cuisines_list


def test_location_lowercased():
    df = preprocess(_make_raw_df(**{"location": ["  BANGALORE  "]}))
    assert df["location"].iloc[0] == "bangalore"


def test_deduplication():
    """Two rows with same name+location should collapse to one."""
    raw = pd.DataFrame({
        "name": ["Cafe A", "Cafe A"],
        "location": ["Bangalore", "Bangalore"],
        "cuisines": ["Italian", "Italian"],
        "approx_cost(for two people)": ["500", "500"],
        "rate": ["4.0/5", "4.0/5"],
        "votes": [100, 100],
        "online_order": ["Yes", "Yes"],
        "book_table": ["No", "No"],
        "rest_type": ["Casual Dining", "Casual Dining"],
    })
    df = preprocess(raw)
    assert len(df) == 1
