# tests/test_recommender.py — Phase 5.6
# Tests the recommender pipeline with a mocked Groq client and mocked dataset.

import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from ui.models import UserPreference
from engine.recommender import recommend, _filter_with_relaxation


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

MOCK_DF = pd.DataFrame([
    {
        "name": "Italian Bistro", "location": "bangalore",
        "cuisines": "Italian, Continental", "approx_cost": 600,
        "rating": 4.3, "budget_tier": "medium",
        "cuisines_list": ["italian", "continental"],
        "rest_type": "Casual Dining", "online_order": "Yes", "book_table": "No",
        "votes": 200,
    },
    {
        "name": "Dosa Palace", "location": "bangalore",
        "cuisines": "South Indian", "approx_cost": 150,
        "rating": 4.0, "budget_tier": "low",
        "cuisines_list": ["south indian"],
        "rest_type": "Quick Bites", "online_order": "Yes", "book_table": "No",
        "votes": 80,
    },
])

MOCK_LLM_RESPONSE = [
    {
        "rank": 1,
        "name": "Italian Bistro",
        "cuisine": "Italian, Continental",
        "rating": 4.3,
        "estimated_cost": "₹600",
        "explanation": "Great match for Italian cuisine in medium budget."
    }
]


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_filter_with_relaxation_pass_1():
    """Pass 1 (all filters) returns results when they exist."""
    prefs = UserPreference(location="bangalore", budget="medium", cuisine="italian", min_rating=4.0)
    result = _filter_with_relaxation(MOCK_DF, prefs)
    assert not result.empty
    assert result["name"].iloc[0] == "Italian Bistro"


def test_filter_with_relaxation_pass_2(capsys):
    """Pass 2 (no cuisine) is used and logged when cuisine filter yields nothing."""
    prefs = UserPreference(location="bangalore", budget="medium", cuisine="japanese", min_rating=4.0)
    result = _filter_with_relaxation(MOCK_DF, prefs)
    captured = capsys.readouterr()
    # Should fall through to a relaxed strategy
    assert "Relaxation pass" in captured.out or not result.empty


def test_filter_with_relaxation_returns_empty_for_no_location():
    """No matching location returns an empty DataFrame."""
    prefs = UserPreference(location="xyz_city_does_not_exist", budget="low")
    result = _filter_with_relaxation(MOCK_DF, prefs)
    assert result.empty


@patch("engine.recommender.call_groq", return_value=MOCK_LLM_RESPONSE)
@patch("engine.recommender.preprocess", return_value=MOCK_DF)
@patch("engine.recommender.load_dataset_as_df", return_value=MOCK_DF)
def test_recommend_returns_list(mock_load, mock_preprocess, mock_groq):
    """Full recommend() returns a non-empty list with correct keys."""
    prefs = UserPreference(location="bangalore", budget="medium", cuisine="italian")
    results = recommend(prefs)
    assert isinstance(results, list)
    assert len(results) > 0
    assert "name" in results[0]
    assert "rank" in results[0]
    assert "explanation" in results[0]


@patch("engine.recommender.call_groq", return_value=MOCK_LLM_RESPONSE)
@patch("engine.recommender.preprocess", return_value=MOCK_DF)
@patch("engine.recommender.load_dataset_as_df", return_value=MOCK_DF)
def test_recommend_empty_location_returns_empty(mock_load, mock_preprocess, mock_groq):
    """recommend() returns empty list when no candidates survive filtering."""
    prefs = UserPreference(location="xyz_nowhere", budget="low")
    results = recommend(prefs)
    assert results == []
