# tests/test_api.py — Phase 5.6
# Tests the Flask REST API endpoints: health check, valid recommend request,
# invalid inputs, and error handling. Uses Flask's test client (no real server needed).

import pytest
import json
from unittest.mock import patch

# Import the Flask app
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from api import app


MOCK_RECOMMENDATIONS = [
    {
        "rank": 1,
        "name": "Italian Bistro",
        "cuisine": "Italian, Continental",
        "rating": 4.3,
        "estimated_cost": "₹600",
        "explanation": "Perfect match for Italian cuisine within your budget."
    }
]


@pytest.fixture
def client():
    """Flask test client."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


# ---------------------------------------------------------------------------
# Health endpoint
# ---------------------------------------------------------------------------

def test_health_returns_ok(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "ok"


# ---------------------------------------------------------------------------
# /api/recommend — valid requests
# ---------------------------------------------------------------------------

@patch("api.recommend", return_value=MOCK_RECOMMENDATIONS)
def test_recommend_valid_request(mock_recommend, client):
    payload = {
        "location": "Bangalore",
        "budget": "medium",
        "cuisine": "Italian",
        "min_rating": 4.0
    }
    response = client.post(
        "/api/recommend",
        data=json.dumps(payload),
        content_type="application/json"
    )
    assert response.status_code == 200
    data = response.get_json()
    assert "recommendations" in data
    assert "count" in data
    assert data["count"] == 1
    assert data["recommendations"][0]["name"] == "Italian Bistro"


@patch("api.recommend", return_value=MOCK_RECOMMENDATIONS)
def test_recommend_without_optional_fields(mock_recommend, client):
    """Minimal request with only required fields should succeed."""
    payload = {"location": "Bangalore", "budget": "low"}
    response = client.post(
        "/api/recommend",
        data=json.dumps(payload),
        content_type="application/json"
    )
    assert response.status_code == 200


# ---------------------------------------------------------------------------
# /api/recommend — invalid requests (400)
# ---------------------------------------------------------------------------

def test_recommend_missing_location(client):
    payload = {"budget": "medium"}
    response = client.post(
        "/api/recommend",
        data=json.dumps(payload),
        content_type="application/json"
    )
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_recommend_invalid_budget(client):
    payload = {"location": "Bangalore", "budget": "super"}
    response = client.post(
        "/api/recommend",
        data=json.dumps(payload),
        content_type="application/json"
    )
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data
    assert "Budget" in data["error"]


def test_recommend_no_body(client):
    """Request with no JSON body returns 400."""
    response = client.post("/api/recommend", content_type="application/json")
    assert response.status_code == 400


def test_recommend_non_json_content_type(client):
    """Non-JSON content type returns 400."""
    response = client.post("/api/recommend", data="location=Bangalore")
    assert response.status_code == 400


# ---------------------------------------------------------------------------
# 404 handler
# ---------------------------------------------------------------------------

def test_unknown_route_returns_json_404(client):
    response = client.get("/api/nonexistent")
    assert response.status_code == 404
    data = response.get_json()
    assert "error" in data
