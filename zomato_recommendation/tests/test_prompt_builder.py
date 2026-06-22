# tests/test_prompt_builder.py — Phase 5.6
# Verifies that build_prompt produces a correctly structured LLM prompt.

import pytest
import pandas as pd
from integration.prompt_builder import build_prompt
from ui.models import UserPreference


def _sample_df() -> pd.DataFrame:
    return pd.DataFrame([{
        "name": "Trattoria Italiana",
        "cuisines": "Italian, Continental",
        "rating": 4.3,
        "approx_cost": 650,
        "rest_type": "Casual Dining",
        "online_order": "Yes",
        "book_table": "No",
    }])


def test_prompt_contains_location():
    prefs = UserPreference(location="Bangalore", budget="medium")
    prompt = build_prompt(_sample_df(), prefs)
    assert "Bangalore" in prompt


def test_prompt_contains_budget():
    prefs = UserPreference(location="Bangalore", budget="medium")
    prompt = build_prompt(_sample_df(), prefs)
    assert "medium" in prompt


def test_prompt_contains_restaurant_name():
    prefs = UserPreference(location="Bangalore", budget="medium")
    prompt = build_prompt(_sample_df(), prefs)
    assert "Trattoria Italiana" in prompt


def test_prompt_contains_json_instruction():
    prefs = UserPreference(location="Bangalore", budget="medium")
    prompt = build_prompt(_sample_df(), prefs)
    assert "JSON" in prompt
    assert "rank" in prompt
    assert "explanation" in prompt


def test_optional_cuisine_included_when_provided():
    prefs = UserPreference(location="Bangalore", budget="medium", cuisine="Italian")
    prompt = build_prompt(_sample_df(), prefs)
    assert "Italian" in prompt
    assert "Preferred Cuisine" in prompt


def test_optional_cuisine_absent_when_none():
    prefs = UserPreference(location="Bangalore", budget="medium", cuisine=None)
    prompt = build_prompt(_sample_df(), prefs)
    assert "Preferred Cuisine" not in prompt


def test_optional_rating_included_when_provided():
    prefs = UserPreference(location="Bangalore", budget="medium", min_rating=4.0)
    prompt = build_prompt(_sample_df(), prefs)
    assert "Minimum Rating" in prompt
    assert "4.0" in prompt


def test_optional_extras_included_when_provided():
    prefs = UserPreference(location="Bangalore", budget="medium",
                           additional_preferences="rooftop seating")
    prompt = build_prompt(_sample_df(), prefs)
    assert "rooftop seating" in prompt
    assert "Special Preferences" in prompt
