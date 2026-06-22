# api.py — Flask REST API (Phase 5.5)
# Exposes the recommendation engine as a JSON API so the Phase 6 frontend
# can communicate with the backend over HTTP.
#
# Endpoints:
#   GET  /api/health        → health check
#   POST /api/recommend     → returns ranked restaurant recommendations

from flask import Flask, request, jsonify
from flask_cors import CORS

from ui.models import UserPreference
from engine.recommender import recommend
from output.formatter import format_recommendations

app = Flask(__name__)
CORS(app)   # Allow cross-origin requests from the frontend (Phase 6)


# ---------------------------------------------------------------------------
# Global error handlers — always return JSON, never HTML tracebacks (Phase 5.7)
# ---------------------------------------------------------------------------

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found", "status": 404}), 404


@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({"error": "Method not allowed", "status": 405}), 405


@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "Internal server error", "status": 500}), 500


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/api/health", methods=["GET"])
def health():
    """Health check endpoint — used by the frontend to verify the server is up."""
    return jsonify({"status": "ok", "service": "zomato-recommendation-api"})


@app.route("/api/recommend", methods=["POST"])
def recommend_endpoint():
    """
    Main recommendation endpoint.

    Request body (JSON):
    {
        "location": "Bangalore",          // required
        "budget": "medium",               // required: "low" | "medium" | "high"
        "cuisine": "Italian",             // optional
        "min_rating": 4.0,               // optional: float 0.0–5.0
        "additional_preferences": "..."   // optional: free text
    }

    Response 200 (JSON):
    {
        "count": 5,
        "recommendations": [
            { "rank": 1, "name": "...", "cuisine": "...", "rating": 4.5,
              "estimated_cost": "₹650", "explanation": "..." },
            ...
        ]
    }

    Response 400 (JSON):
    { "error": "<validation message>" }
    """
    data = request.get_json(silent=True)

    # Guard: require JSON body
    if not data:
        return jsonify({"error": "Request body must be valid JSON"}), 400

    # Build and validate UserPreference
    try:
        min_rating = data.get("min_rating")
        if min_rating is not None:
            min_rating = float(min_rating)

        prefs = UserPreference(
            location=data.get("location", "").strip(),
            budget=data.get("budget", "").strip().lower(),
            cuisine=data.get("cuisine") or None,
            min_rating=min_rating,
            additional_preferences=data.get("additional_preferences") or None,
        )
        prefs.validate()

    except (AssertionError, ValueError) as e:
        return jsonify({"error": str(e)}), 400

    # Run the recommendation pipeline
    try:
        raw = recommend(prefs)
    except RuntimeError as e:
        # Groq API failure or dataset load failure
        return jsonify({"error": str(e)}), 502

    results = format_recommendations(raw)

    return jsonify({
        "count": len(results),
        "recommendations": results,
    })


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("🚀  Starting Zomato Recommendation API on http://localhost:5001")
    app.run(debug=True, port=5001)
