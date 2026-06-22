# tests/test_filter_engine.py — Phase 5.6
# Verifies rule-based filtering: individual filters, combinations,
# empty-result behaviour, and MAX_CANDIDATES cap.

import pytest
import pandas as pd
from data.filter_engine import filter_restaurants


def _make_df() -> pd.DataFrame:
    """Fixture: small preprocessed-style DataFrame for testing."""
    return pd.DataFrame([
        {
            "name": "Italian Bistro", "location": "bangalore",
            "cuisines": "Italian, Continental", "approx_cost": 600,
            "rating": 4.3, "budget_tier": "medium",
            "cuisines_list": ["italian", "continental"],
            "rest_type": "Casual Dining", "online_order": "Yes", "book_table": "No",
        },
        {
            "name": "Dosa Palace", "location": "bangalore",
            "cuisines": "South Indian", "approx_cost": 150,
            "rating": 4.0, "budget_tier": "low",
            "cuisines_list": ["south indian"],
            "rest_type": "Quick Bites", "online_order": "Yes", "book_table": "No",
        },
        {
            "name": "The Grand Feast", "location": "delhi",
            "cuisines": "Mughlai, North Indian", "approx_cost": 1200,
            "rating": 4.5, "budget_tier": "high",
            "cuisines_list": ["mughlai", "north indian"],
            "rest_type": "Fine Dining", "online_order": "No", "book_table": "Yes",
        },
        {
            "name": "Burger Hub", "location": "bangalore",
            "cuisines": "American, Fast Food", "approx_cost": 400,
            "rating": 3.8, "budget_tier": "medium",
            "cuisines_list": ["american", "fast food"],
            "rest_type": "Quick Bites", "online_order": "Yes", "book_table": "No",
        },
    ])


def test_location_filter():
    df = _make_df()
    result = filter_restaurants(df, location="bangalore")
    assert len(result) == 3
    assert all("bangalore" in loc for loc in result["location"])


def test_budget_filter():
    df = _make_df()
    result = filter_restaurants(df, budget="low")
    assert len(result) == 1
    assert result["name"].iloc[0] == "Dosa Palace"


def test_cuisine_filter():
    df = _make_df()
    result = filter_restaurants(df, cuisine="italian")
    assert len(result) == 1
    assert result["name"].iloc[0] == "Italian Bistro"


def test_min_rating_filter():
    df = _make_df()
    result = filter_restaurants(df, min_rating=4.3)
    assert all(result["rating"] >= 4.3)


def test_combined_filters():
    df = _make_df()
    result = filter_restaurants(df, location="bangalore", budget="medium", cuisine="italian")
    assert len(result) == 1
    assert result["name"].iloc[0] == "Italian Bistro"


def test_no_filter_returns_all_sorted():
    df = _make_df()
    result = filter_restaurants(df)
    assert len(result) == len(df)
    # Should be sorted by rating descending
    ratings = result["rating"].tolist()
    assert ratings == sorted(ratings, reverse=True)


def test_no_match_returns_empty():
    df = _make_df()
    result = filter_restaurants(df, location="mumbai")
    assert result.empty


def test_location_partial_match():
    """Partial location string should still match."""
    df = _make_df()
    result = filter_restaurants(df, location="banga")
    assert len(result) == 3
