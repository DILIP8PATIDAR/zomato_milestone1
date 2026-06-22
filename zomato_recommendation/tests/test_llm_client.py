# tests/test_llm_client.py — Phase 5.6
# Tests the JSON parsing logic of _parse_response without hitting the Groq API.

import pytest
import json
from integration.llm_client import _parse_response


VALID_RESPONSE = json.dumps([
    {
        "rank": 1,
        "name": "Trattoria Italiana",
        "cuisine": "Italian",
        "rating": 4.3,
        "estimated_cost": "₹650",
        "explanation": "Excellent Italian food in the heart of Bangalore."
    }
])


def test_direct_json_parse():
    """Strategy 1: clean JSON array parses directly."""
    result = _parse_response(VALID_RESPONSE)
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["name"] == "Trattoria Italiana"


def test_regex_fallback_with_markdown_fence():
    """Strategy 2: JSON embedded in markdown code fences is extracted via regex."""
    wrapped = f"Here are the results:\n```json\n{VALID_RESPONSE}\n```"
    result = _parse_response(wrapped)
    assert isinstance(result, list)
    assert result[0]["rank"] == 1


def test_regex_fallback_with_preamble():
    """Strategy 2: JSON with leading prose text still parsed correctly."""
    with_preamble = f"Sure! Here are my top picks:\n{VALID_RESPONSE}"
    result = _parse_response(with_preamble)
    assert isinstance(result, list)


def test_raises_on_invalid_json():
    """ValueError raised when response cannot be parsed as a JSON array."""
    with pytest.raises(ValueError, match="Could not parse LLM response"):
        _parse_response("This is not JSON at all.")


def test_raises_on_json_object_not_list():
    """ValueError raised when response is a JSON object (not an array)."""
    with pytest.raises(ValueError):
        _parse_response('{"rank": 1, "name": "Test"}')


def test_whitespace_stripped_before_parse():
    """Leading/trailing whitespace is stripped before parsing."""
    padded = f"  \n{VALID_RESPONSE}\n  "
    result = _parse_response(padded)
    assert isinstance(result, list)
