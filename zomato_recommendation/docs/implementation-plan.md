# Implementation Plan: AI-Powered Restaurant Recommendation System
## Zomato Use Case — Phase-wise Breakdown

> **Sources:** `context.md`, `architecture.md` | **Date:** 2026-06-22
> **LLM:** Groq (LLaMA 3.3 70B / Mixtral 8x7B)
> **Language:** Python 3.10+ (Backend) · HTML/CSS/JS (Frontend)

---

## Table of Contents

- [Overview](#overview)
- [Phase 5 — Backend Development](#phase-5--backend-development)
  - [Phase 5.0 — Project Setup & Environment](#phase-50--project-setup--environment)
  - [Phase 5.1 — Data Ingestion Layer](#phase-51--data-ingestion-layer)
  - [Phase 5.2 — User Input Layer](#phase-52--user-input-layer)
  - [Phase 5.3 — Integration Layer (Prompt Engineering)](#phase-53--integration-layer-prompt-engineering)
  - [Phase 5.4 — LLM Recommendation Engine (Groq)](#phase-54--llm-recommendation-engine-groq)
  - [Phase 5.5 — Output / API Layer](#phase-55--output--api-layer)
  - [Phase 5.6 — End-to-End Integration & Testing](#phase-56--end-to-end-integration--testing)
  - [Phase 5.7 — Error Handling & Robustness](#phase-57--error-handling--robustness)
- [Phase 6 — Frontend Development](#phase-6--frontend-development)
  - [Phase 6.1 — Design System & Project Setup](#phase-61--design-system--project-setup)
  - [Phase 6.2 — Preference Input UI](#phase-62--preference-input-ui)
  - [Phase 6.3 — Results & Recommendation Display](#phase-63--results--recommendation-display)
  - [Phase 6.4 — API Integration](#phase-64--api-integration)
  - [Phase 6.5 — Polish, Animations & Responsiveness](#phase-65--polish-animations--responsiveness)
- [Phase Summary Table](#phase-summary-table)
- [File Structure After All Phases](#file-structure-after-all-phases)

---

## Overview

The project is split into **two major phases**: a **Backend Phase (5)** that builds the AI recommendation pipeline in Python, and a **Frontend Phase (6)** that wraps it in a premium web interface. Each major phase has numbered sub-phases producing independently testable outputs.

```
Phase 5 (Backend):   User Input → Data Ingestion & Filtering → Prompt → Groq LLM → REST API
Phase 6 (Frontend):  Web UI → Preference Form → API Call → Styled Results Display
```

---

---

# Phase 5 — Backend Development

**Goal:** Build the complete Python-based AI recommendation pipeline — from data ingestion and prompt engineering to the Groq LLM engine — and expose it as a REST API for the frontend to consume.

---

## Phase 5.0 — Project Setup & Environment

### Goal
Establish the project skeleton, dependency environment, and configuration management so all subsequent phases have a consistent foundation.

### Tasks

#### 5.0.1 Initialize Project Structure
```
zomato_recommendation/
├── data/
├── integration/
├── engine/
├── output/
├── ui/
├── tests/
├── frontend/        ← reserved for Phase 6
├── config.py
├── main.py
├── api.py           ← REST API entry point (used in Phase 5.5)
├── requirements.txt
└── .env
```

#### 5.0.2 Install Dependencies
```
# requirements.txt
datasets>=2.18.0        # Hugging Face dataset loader
pandas>=2.0.0           # Data manipulation & filtering
groq>=0.9.0             # Groq Python SDK
python-dotenv>=1.0.0    # Secure API key management
rich>=13.0.0            # CLI output formatting
flask>=3.0.0            # REST API server (for Phase 5.5)
flask-cors>=4.0.0       # CORS headers for frontend requests
```

Install via:
```bash
pip install -r requirements.txt
```

#### 5.0.3 Configure Environment Variables
Create `.env` file:
```
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
HF_DATASET_NAME=ManikaSaini/zomato-restaurant-recommendation
BUDGET_LOW_MAX=300
BUDGET_MEDIUM_MAX=800
MAX_CANDIDATES=20
LLM_TEMPERATURE=0.4
LLM_MAX_TOKENS=1500
```

#### 5.0.4 Create `config.py`
```python
# config.py
import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY     = os.getenv("GROQ_API_KEY")
GROQ_MODEL       = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
HF_DATASET_NAME  = os.getenv("HF_DATASET_NAME")
BUDGET_LOW_MAX   = int(os.getenv("BUDGET_LOW_MAX", 300))
BUDGET_MEDIUM_MAX= int(os.getenv("BUDGET_MEDIUM_MAX", 800))
MAX_CANDIDATES   = int(os.getenv("MAX_CANDIDATES", 20))
LLM_TEMPERATURE  = float(os.getenv("LLM_TEMPERATURE", 0.4))
LLM_MAX_TOKENS   = int(os.getenv("LLM_MAX_TOKENS", 1500))

BUDGET_TIERS = {
    "low":    (0,                BUDGET_LOW_MAX),
    "medium": (BUDGET_LOW_MAX+1, BUDGET_MEDIUM_MAX),
    "high":   (BUDGET_MEDIUM_MAX+1, float("inf")),
}
```

### Deliverables
- `config.py`
- `requirements.txt`
- `.env` (template)
- Project directory skeleton

### Validation
- [ ] `python -c "import config; print(config.GROQ_MODEL)"` prints the model name
- [ ] All dependency imports succeed without errors

---

## Phase 5.1 — Data Ingestion Layer

### Goal
Load the Zomato dataset from Hugging Face, clean/normalize it, and implement the rule-based filtering engine that produces a candidate restaurant list.

### Architecture Reference
→ `architecture.md` §3.2 — Data Ingestion Layer

### Tasks

#### 5.1.1 Dataset Loader (`data/loader.py`)
```python
# data/loader.py
from datasets import load_dataset
import pandas as pd
from config import HF_DATASET_NAME

_CACHE: pd.DataFrame | None = None

REQUIRED_FIELDS = [
    "name", "location", "cuisines", "approx_cost(for two people)",
    "aggregate_rating", "rating_text", "votes",
    "online_order", "book_table", "rest_type"
]

def load_dataset_as_df() -> pd.DataFrame:
    """Load Zomato dataset from Hugging Face and return as DataFrame. Cached."""
    global _CACHE
    if _CACHE is not None:
        return _CACHE
    ds = load_dataset(HF_DATASET_NAME, split="train")
    df = ds.to_pandas()
    _CACHE = df[REQUIRED_FIELDS].copy()
    return _CACHE
```

**Key behaviors:**
- Module-level in-memory cache (`_CACHE`) — dataset loaded once per session
- Only retains required fields to reduce memory footprint

#### 5.1.2 Preprocessor (`data/preprocessor.py`)
Implement the following normalization steps in order:

| Step | Operation | Detail |
|---|---|---|
| 1 | Strip whitespace | All string columns |
| 2 | Rename columns | `approx_cost(for two people)` → `approx_cost`, `aggregate_rating` → `rating` |
| 3 | Type-cast cost | Remove commas, cast to `int`; invalid → `NaN` |
| 4 | Type-cast rating | Cast to `float`; `"NEW"` / `"-"` → `NaN` |
| 5 | Drop nulls | Drop rows missing `name`, `location`, `rating`, or `approx_cost` |
| 6 | Deduplicate | On `name + location` (keep first occurrence) |
| 7 | Budget tier | Map `approx_cost` to `low / medium / high` using thresholds from `config.py` |
| 8 | Parse cuisines | Split comma-separated string → Python list; lowercase each entry |
| 9 | Normalize location | Lowercase, strip whitespace |

```python
# data/preprocessor.py
import pandas as pd
from config import BUDGET_TIERS

def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.rename(columns={"approx_cost(for two people)": "approx_cost",
                        "aggregate_rating": "rating"}, inplace=True)
    df["approx_cost"] = pd.to_numeric(
        df["approx_cost"].astype(str).str.replace(",", ""), errors="coerce"
    )
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
    df.dropna(subset=["name", "location", "rating", "approx_cost"], inplace=True)
    df.drop_duplicates(subset=["name", "location"], keep="first", inplace=True)
    def tier(cost):
        for name, (lo, hi) in BUDGET_TIERS.items():
            if lo <= cost <= hi:
                return name
        return "high"
    df["budget_tier"] = df["approx_cost"].apply(tier)
    df["cuisines_list"] = df["cuisines"].str.lower().str.split(",").apply(
        lambda x: [c.strip() for c in x] if isinstance(x, list) else []
    )
    df["location"] = df["location"].str.lower().str.strip()
    return df.reset_index(drop=True)
```

#### 5.1.3 Filter Engine (`data/filter_engine.py`)
Apply filters sequentially. Each filter is optional — if the user doesn't provide a value, skip that filter.

```python
# data/filter_engine.py
import pandas as pd
from config import MAX_CANDIDATES

def filter_restaurants(
    df: pd.DataFrame,
    location: str | None = None,
    budget: str | None = None,
    cuisine: str | None = None,
    min_rating: float | None = None,
) -> pd.DataFrame:
    result = df.copy()

    if location:
        loc = location.lower().strip()
        result = result[result["location"].str.contains(loc, na=False)]

    if budget:
        result = result[result["budget_tier"] == budget.lower()]

    if cuisine:
        cuis = cuisine.lower().strip()
        result = result[result["cuisines_list"].apply(
            lambda lst: any(cuis in c for c in lst)
        )]

    if min_rating is not None:
        result = result[result["rating"] >= min_rating]

    result = result.sort_values("rating", ascending=False).head(MAX_CANDIDATES)
    return result.reset_index(drop=True)
```

**Filter relaxation logic** (for zero results):
```
1st pass: all filters applied
2nd pass: drop cuisine filter
3rd pass: drop budget filter
4th pass: drop cuisine + budget (location + rating only)
```

### Deliverables
- `data/loader.py`
- `data/preprocessor.py`
- `data/filter_engine.py`

### Validation
```python
from data.loader import load_dataset_as_df
from data.preprocessor import preprocess
from data.filter_engine import filter_restaurants

df = load_dataset_as_df()
df = preprocess(df)
print(f"Total records after preprocessing: {len(df)}")

candidates = filter_restaurants(df, location="Bangalore", budget="medium", cuisine="Italian", min_rating=4.0)
print(f"Filtered candidates: {len(candidates)}")
print(candidates[["name", "location", "budget_tier", "rating", "cuisines"]].head())
```
- [ ] DataFrame loads without error
- [ ] Preprocessing removes nulls and adds `budget_tier`, `cuisines_list`
- [ ] Filtering returns non-empty results for common inputs (e.g., Bangalore, medium)

---

## Phase 5.2 — User Input Layer

### Goal
Collect user preferences via a validated `UserPreference` data model (used by both CLI and the REST API).

### Architecture Reference
→ `architecture.md` §3.1 — User Interface Layer

### Tasks

#### 5.2.1 User Preference Data Class (`ui/models.py`)
```python
# ui/models.py
from dataclasses import dataclass, field

@dataclass
class UserPreference:
    location: str
    budget: str                        # "low" | "medium" | "high"
    cuisine: str | None = None
    min_rating: float | None = None
    additional_preferences: str | None = None

    def validate(self):
        assert self.budget in ("low", "medium", "high"), \
            "Budget must be 'low', 'medium', or 'high'"
        if self.min_rating is not None:
            assert 0.0 <= self.min_rating <= 5.0, \
                "min_rating must be between 0.0 and 5.0"
        assert self.location.strip(), "Location cannot be empty"
```

#### 5.2.2 CLI Input Collector (`ui/input_collector.py`)
```python
# ui/input_collector.py
from ui.models import UserPreference

def collect_preferences() -> UserPreference:
    print("\n🍽  Welcome to the Zomato AI Restaurant Recommender\n")
    location = input("Enter location (e.g., Bangalore, Delhi): ").strip()
    budget   = input("Enter budget [low / medium / high]: ").strip().lower()
    cuisine  = input("Preferred cuisine (press Enter to skip): ").strip() or None
    rating_input = input("Minimum rating (0.0–5.0, press Enter to skip): ").strip()
    min_rating   = float(rating_input) if rating_input else None
    extras   = input("Any additional preferences (press Enter to skip): ").strip() or None

    prefs = UserPreference(
        location=location,
        budget=budget,
        cuisine=cuisine,
        min_rating=min_rating,
        additional_preferences=extras,
    )
    prefs.validate()
    return prefs
```

### Deliverables
- `ui/models.py`
- `ui/input_collector.py`

### Validation
- [ ] Running `collect_preferences()` interactively returns a valid `UserPreference` object
- [ ] `validate()` raises `AssertionError` on invalid budget or rating
- [ ] Skipping optional fields returns `None` (not empty string)

---

## Phase 5.3 — Integration Layer (Prompt Engineering)

### Goal
Take the filtered restaurant list and user preferences, and construct a well-structured prompt ready for the Groq LLM.

### Architecture Reference
→ `architecture.md` §3.3 & §6 — Integration Layer, Prompt Engineering Design

### Tasks

#### 5.3.1 Restaurant Serializer (`integration/prompt_builder.py`)
```python
# integration/prompt_builder.py
import pandas as pd
from ui.models import UserPreference
from config import BUDGET_TIERS

def _serialize_restaurants(df: pd.DataFrame) -> str:
    lines = []
    for i, row in df.iterrows():
        line = (
            f"{i+1}. Name: {row['name']} | "
            f"Cuisine: {row['cuisines']} | "
            f"Rating: {row['rating']} | "
            f"Cost for two: ₹{int(row['approx_cost'])} | "
            f"Type: {row.get('rest_type', 'N/A')} | "
            f"Online Order: {row.get('online_order', 'N/A')} | "
            f"Table Booking: {row.get('book_table', 'N/A')}"
        )
        lines.append(line)
    return "\n".join(lines)

def _budget_range_str(budget: str) -> str:
    lo, hi = BUDGET_TIERS[budget]
    if hi == float("inf"):
        return f"above ₹{lo}"
    return f"₹{lo}–₹{int(hi)} for two"

def build_prompt(df: pd.DataFrame, prefs: UserPreference) -> str:
    restaurant_list = _serialize_restaurants(df)
    cuisine_line = f"- Preferred Cuisine: {prefs.cuisine}" if prefs.cuisine else ""
    rating_line  = f"- Minimum Rating: {prefs.min_rating}" if prefs.min_rating else ""
    extras_line  = f"- Special Preferences: {prefs.additional_preferences}" if prefs.additional_preferences else ""

    prompt = f"""You are an expert restaurant recommendation assistant with deep knowledge of dining preferences and restaurant quality.

User Preferences:
- Location: {prefs.location}
- Budget: {prefs.budget} ({_budget_range_str(prefs.budget)})
{cuisine_line}
{rating_line}
{extras_line}

Candidate Restaurants:
{restaurant_list}

Task:
Rank the above restaurants from best to worst fit for this user.
For each restaurant in your top 5, provide a 2–3 sentence explanation of why it is a great match.

Respond ONLY as a valid JSON array. Each element must have these exact keys:
rank, name, cuisine, rating, estimated_cost, explanation

Do not include any text outside the JSON array."""

    return prompt.strip()
```

### Deliverables
- `integration/prompt_builder.py`

### Validation
- [ ] Prompt contains user preferences section
- [ ] Prompt contains numbered restaurant list
- [ ] Prompt ends with JSON instruction
- [ ] Empty optional fields are not included as blank lines

---

## Phase 5.4 — LLM Recommendation Engine (Groq)

### Goal
Send the constructed prompt to the Groq API and parse the structured JSON response into ranked recommendation objects.

### Architecture Reference
→ `architecture.md` §3.4 — LLM Recommendation Engine

### Tasks

#### 5.4.1 Groq API Client (`integration/llm_client.py`)
```python
# integration/llm_client.py
import json
import re
import time
from groq import Groq
from config import GROQ_API_KEY, GROQ_MODEL, LLM_TEMPERATURE, LLM_MAX_TOKENS

_client = Groq(api_key=GROQ_API_KEY)

def call_groq(prompt: str, retries: int = 3) -> list[dict]:
    for attempt in range(retries):
        try:
            response = _client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=LLM_TEMPERATURE,
                max_tokens=LLM_MAX_TOKENS,
            )
            raw = response.choices[0].message.content
            return _parse_response(raw)
        except Exception as e:
            if attempt < retries - 1:
                wait = 2 ** attempt
                print(f"[Groq] Attempt {attempt+1} failed: {e}. Retrying in {wait}s...")
                time.sleep(wait)
            else:
                raise RuntimeError(f"Groq API failed after {retries} attempts: {e}")

def _parse_response(raw: str) -> list[dict]:
    raw = raw.strip()
    try:
        result = json.loads(raw)
        if isinstance(result, list):
            return result
    except json.JSONDecodeError:
        pass
    match = re.search(r"\[.*\]", raw, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    raise ValueError(f"Could not parse LLM response as JSON array:\n{raw[:500]}")
```

**Groq Model Selection:**
| Scenario | Recommended Model |
|---|---|
| Default / best quality | `llama-3.3-70b-versatile` |
| Fastest response needed | `llama-3.1-8b-instant` |
| Large candidate lists (>15) | `mixtral-8x7b-32768` (32K context) |

#### 5.4.2 Recommender Orchestrator (`engine/recommender.py`)
```python
# engine/recommender.py
import pandas as pd
from ui.models import UserPreference
from data.loader import load_dataset_as_df
from data.preprocessor import preprocess
from data.filter_engine import filter_restaurants
from integration.prompt_builder import build_prompt
from integration.llm_client import call_groq

def recommend(prefs: UserPreference) -> list[dict]:
    raw_df = load_dataset_as_df()
    df     = preprocess(raw_df)
    candidates = _filter_with_relaxation(df, prefs)
    if candidates.empty:
        return []
    prompt = build_prompt(candidates, prefs)
    recommendations = call_groq(prompt)
    return recommendations

def _filter_with_relaxation(df: pd.DataFrame, prefs: UserPreference) -> pd.DataFrame:
    strategies = [
        dict(location=prefs.location, budget=prefs.budget, cuisine=prefs.cuisine, min_rating=prefs.min_rating),
        dict(location=prefs.location, budget=prefs.budget, cuisine=None,          min_rating=prefs.min_rating),
        dict(location=prefs.location, budget=None,          cuisine=None,          min_rating=prefs.min_rating),
        dict(location=prefs.location, budget=None,          cuisine=None,          min_rating=None),
    ]
    for strategy in strategies:
        result = filter_restaurants(df, **strategy)
        if not result.empty:
            return result
    return pd.DataFrame()
```

### Deliverables
- `integration/llm_client.py`
- `engine/recommender.py`

### Validation
- [ ] `recommend()` returns a list of dicts with keys: `rank, name, cuisine, rating, estimated_cost, explanation`
- [ ] Progressive relaxation triggers and logs when strict filters return 0 results
- [ ] Retries fire on transient API errors

---

## Phase 5.5 — Output / API Layer

### Goal
Expose the recommendation engine as a **REST API** (Flask) so the frontend can consume results over HTTP, and retain a CLI renderer for local testing.

### Tasks

#### 5.5.1 Formatter (`output/formatter.py`)
```python
# output/formatter.py
REQUIRED_KEYS = {"rank", "name", "cuisine", "rating", "estimated_cost", "explanation"}

def format_recommendations(raw: list[dict]) -> list[dict]:
    valid = []
    for item in raw:
        if not REQUIRED_KEYS.issubset(item.keys()):
            continue
        item["rank"] = int(item["rank"])
        item["rating"] = float(item["rating"])
        valid.append(item)
    return sorted(valid, key=lambda x: x["rank"])
```

#### 5.5.2 CLI Renderer (`output/renderer.py`)
```python
# output/renderer.py
from rich.console import Console
from rich.panel import Panel

console = Console()

def render_recommendations(recommendations: list[dict], prefs) -> None:
    console.print(f"\n[bold green]🍽  Top Restaurant Recommendations[/bold green]")
    console.print(f"[dim]Location: {prefs.location} | Budget: {prefs.budget} | "
                  f"Cuisine: {prefs.cuisine or 'Any'} | Min Rating: {prefs.min_rating or 'Any'}[/dim]\n")

    if not recommendations:
        console.print("[bold red]No recommendations found. Try relaxing your preferences.[/bold red]")
        return

    for rec in recommendations:
        stars = "⭐" * round(rec["rating"])
        title = f"#{rec['rank']}  {rec['name']}"
        body = (
            f"🍜 Cuisine:    {rec['cuisine']}\n"
            f"⭐ Rating:     {rec['rating']}  {stars}\n"
            f"💰 Est. Cost:  {rec['estimated_cost']}\n\n"
            f"💬 {rec['explanation']}"
        )
        console.print(Panel(body, title=title, border_style="cyan", padding=(1, 2)))
```

#### 5.5.3 Flask REST API (`api.py`)
```python
# api.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from ui.models import UserPreference
from engine.recommender import recommend
from output.formatter import format_recommendations

app = Flask(__name__)
CORS(app)   # Allow cross-origin requests from the frontend

@app.route("/api/recommend", methods=["POST"])
def recommend_endpoint():
    data = request.get_json()
    try:
        prefs = UserPreference(
            location=data["location"],
            budget=data["budget"],
            cuisine=data.get("cuisine") or None,
            min_rating=float(data["min_rating"]) if data.get("min_rating") else None,
            additional_preferences=data.get("additional_preferences") or None,
        )
        prefs.validate()
    except (KeyError, AssertionError) as e:
        return jsonify({"error": str(e)}), 400

    raw = recommend(prefs)
    results = format_recommendations(raw)
    return jsonify({"recommendations": results, "count": len(results)})

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
```

**API Contract:**
```
POST /api/recommend
Content-Type: application/json

Request:
{
  "location": "Bangalore",
  "budget": "medium",
  "cuisine": "Italian",       // optional
  "min_rating": 4.0,          // optional
  "additional_preferences": "rooftop" // optional
}

Response 200:
{
  "count": 5,
  "recommendations": [
    { "rank": 1, "name": "...", "cuisine": "...", "rating": 4.5,
      "estimated_cost": "₹600", "explanation": "..." },
    ...
  ]
}

Response 400:
{ "error": "Budget must be 'low', 'medium', or 'high'" }
```

### Deliverables
- `output/formatter.py`
- `output/renderer.py`
- `api.py`

### Validation
- [ ] `python api.py` starts Flask on port 5000
- [ ] `POST /api/recommend` with valid JSON returns 5 recommendations
- [ ] `GET /api/health` returns `{"status": "ok"}`
- [ ] Invalid payload returns HTTP 400 with error message
- [ ] CLI renderer displays styled cards in terminal

---

## Phase 5.6 — End-to-End Integration & Testing

### Goal
Wire all phases together in `main.py` and run end-to-end tests to verify the complete backend pipeline.

### Tasks

#### 5.6.1 CLI Entry Point (`main.py`)
```python
# main.py
from ui.input_collector import collect_preferences
from engine.recommender import recommend
from output.formatter import format_recommendations
from output.renderer import render_recommendations

def main():
    try:
        prefs   = collect_preferences()
        raw     = recommend(prefs)
        results = format_recommendations(raw)
        render_recommendations(results, prefs)
    except AssertionError as e:
        print(f"\n[Input Error] {e}")
    except RuntimeError as e:
        print(f"\n[API Error] {e}")
    except KeyboardInterrupt:
        print("\n\nExiting. Goodbye! 👋")

if __name__ == "__main__":
    main()
```

#### 5.6.2 Smoke Tests (`tests/`)

| Test | What it verifies |
|---|---|
| `test_loader.py` | Dataset loads; required columns present |
| `test_preprocessor.py` | Budget tier mapping; cuisine parsing; null removal |
| `test_filter_engine.py` | Filter returns expected results; relaxation triggers |
| `test_prompt_builder.py` | Prompt contains user prefs and restaurant list |
| `test_llm_client.py` | JSON parse succeeds; regex fallback works |
| `test_recommender.py` | Full pipeline returns non-empty recommendations |
| `test_api.py` | Flask endpoints return correct HTTP codes & JSON shape |

#### 5.6.3 End-to-End Manual Test Scenarios

| Scenario | Input | Expected Behavior |
|---|---|---|
| Happy path | Bangalore, medium, Italian, 4.0 | 5 ranked Italian restaurants |
| No cuisine match | Delhi, low, Japanese, 4.5 | Relaxed to no cuisine filter; results returned |
| No results at all | XYZCity, high, Korean, 4.9 | Empty result message |
| No optional fields | Mumbai, low | Recommendations without cuisine/rating filters |
| API call | POST /api/recommend | JSON response with 5 recommendations |

### Deliverables
- `main.py`
- `tests/` (all test files including `test_api.py`)

### Validation
- [ ] `python main.py` runs end-to-end without errors on a valid input
- [ ] `python api.py` + `curl` confirms API responses match contract
- [ ] All smoke tests pass

---

## Phase 5.7 — Error Handling & Robustness

### Goal
Implement all error handling and edge-case logic across the backend.

### Tasks

#### 5.7.1 Filter Relaxation Logging
- Log which filter level was used: `print(f"[Filter] Strategy used: {strategy}")`

#### 5.7.2 LLM JSON Parse Failure
- Already handled in `_parse_response()` with regex fallback
- Final fallback: return empty list + log error

#### 5.7.3 Groq API Rate Limit / Timeout
- Exponential backoff (1s → 2s → 4s) in `call_groq()`
- After 3 failures: raise `RuntimeError` with a clear user-facing message

#### 5.7.4 Dataset Cache Failure
```python
try:
    ds = load_dataset(HF_DATASET_NAME, split="train")
except Exception as e:
    raise RuntimeError(
        f"Failed to load dataset '{HF_DATASET_NAME}'. "
        f"Check your internet connection. Error: {e}"
    )
```

#### 5.7.5 Low Vote Count Flag
```python
if row.get("votes", 999) < 50:
    body += "\n⚠️  [dim]Limited reviews — fewer than 50 votes[/dim]"
```

#### 5.7.6 API Error Responses
- All Flask exceptions caught and returned as `{"error": "..."}` JSON — never raw tracebacks

### Deliverables
- Updated `data/loader.py`
- Updated `output/renderer.py`
- Updated `api.py` (global error handler)

### Validation
- [ ] Killing internet mid-run raises clear RuntimeError (not a raw traceback)
- [ ] Invalid Groq API key shows clear auth error message
- [ ] Restaurants with < 50 votes show the warning badge in output
- [ ] Flask returns JSON errors, never HTML 500 pages

---

---

# Phase 6 — Frontend Development

**Goal:** Build a premium, responsive web interface that communicates with the Phase 5 REST API to deliver a delightful restaurant discovery experience. No framework dependency — built with pure **HTML, CSS, and Vanilla JS**.

**Design Principles:**
- Dark glassmorphism aesthetic with vibrant accent colors
- Smooth micro-animations on every interaction
- Fully responsive (mobile → desktop)
- Zero page reloads — single-page app using the Fetch API

---

## Phase 6.1 — Design System & Project Setup

### Goal
Establish the visual design language, CSS custom properties, and typography before building any components.

### Tasks

#### 6.1.1 Frontend Folder Structure
```
frontend/
├── index.html
├── css/
│   ├── reset.css          ← Normalize browser defaults
│   ├── tokens.css         ← CSS custom properties (colors, spacing, type)
│   ├── components.css     ← Reusable component styles
│   └── animations.css     ← Keyframe animations & transitions
├── js/
│   ├── api.js             ← Fetch wrapper for backend API calls
│   ├── ui.js              ← DOM manipulation & rendering helpers
│   └── app.js             ← Main app logic & event listeners
└── assets/
    └── logo.svg           ← App logo / favicon
```

#### 6.1.2 Design Tokens (`css/tokens.css`)
```css
:root {
  /* Color Palette */
  --color-bg:           #0d0f1a;
  --color-surface:      #161926;
  --color-glass:        rgba(255, 255, 255, 0.05);
  --color-glass-border: rgba(255, 255, 255, 0.10);
  --color-primary:      #e23744;   /* Zomato red */
  --color-primary-glow: rgba(226, 55, 68, 0.35);
  --color-accent:       #f5a623;   /* warm amber */
  --color-text-primary: #f0f2f8;
  --color-text-muted:   #8892a4;
  --color-success:      #22c55e;
  --color-warning:      #f59e0b;

  /* Typography */
  --font-sans:   'Inter', system-ui, sans-serif;
  --font-display:'Outfit', sans-serif;
  --fs-xs:   0.75rem;
  --fs-sm:   0.875rem;
  --fs-base: 1rem;
  --fs-lg:   1.125rem;
  --fs-xl:   1.25rem;
  --fs-2xl:  1.5rem;
  --fs-3xl:  1.875rem;
  --fs-4xl:  2.25rem;

  /* Spacing */
  --space-1: 0.25rem;  --space-2: 0.5rem;  --space-3: 0.75rem;
  --space-4: 1rem;     --space-6: 1.5rem;  --space-8: 2rem;
  --space-12: 3rem;    --space-16: 4rem;

  /* Radius */
  --radius-sm: 0.5rem;  --radius-md: 0.75rem;
  --radius-lg: 1rem;    --radius-xl: 1.5rem;

  /* Shadows */
  --shadow-card: 0 8px 32px rgba(0, 0, 0, 0.4);
  --shadow-glow: 0 0 24px var(--color-primary-glow);
  --shadow-hover: 0 12px 40px rgba(0, 0, 0, 0.6);

  /* Transitions */
  --transition-fast: 150ms ease;
  --transition-base: 250ms ease;
  --transition-slow: 400ms cubic-bezier(0.22, 1, 0.36, 1);
}
```

#### 6.1.3 Google Fonts Import
```html
<!-- In <head> of index.html -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Outfit:wght@400;600;700;800&display=swap" rel="stylesheet">
```

### Deliverables
- `frontend/css/tokens.css`
- `frontend/css/reset.css`
- `frontend/index.html` (skeleton with `<head>`)

### Validation
- [ ] Opening `index.html` in browser shows dark background with correct fonts loaded
- [ ] CSS custom properties accessible from browser DevTools

---

## Phase 6.2 — Preference Input UI

### Goal
Build the user-facing preference form — a visually premium card with animated inputs for location, budget, cuisine, rating, and extra preferences.

### Tasks

#### 6.2.1 Hero Section & Form Layout (`index.html`)

The page is structured as:
```
┌─────────────────────────────────────────┐
│  NAVBAR  (logo + tagline)               │
├─────────────────────────────────────────┤
│  HERO    (heading + sub-heading)        │
├─────────────────────────────────────────┤
│  PREFERENCE FORM (glass card)           │
│  ┌──────────────┐  ┌──────────────┐    │
│  │ Location     │  │ Budget       │    │
│  └──────────────┘  └──────────────┘    │
│  ┌──────────────┐  ┌──────────────┐    │
│  │ Cuisine      │  │ Min Rating   │    │
│  └──────────────┘  └──────────────┘    │
│  ┌─────────────────────────────────┐   │
│  │ Additional Preferences          │   │
│  └─────────────────────────────────┘   │
│  [  🔍 Find My Restaurant  ]           │
├─────────────────────────────────────────┤
│  RESULTS SECTION (hidden initially)    │
└─────────────────────────────────────────┘
```

#### 6.2.2 Form Component Styling
Key CSS patterns for the glass-morphism input card:
```css
.form-card {
  background: var(--color-glass);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid var(--color-glass-border);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-card);
  padding: var(--space-8);
}

.form-input {
  background: rgba(255,255,255,0.06);
  border: 1px solid var(--color-glass-border);
  border-radius: var(--radius-md);
  color: var(--color-text-primary);
  transition: border-color var(--transition-base),
              box-shadow var(--transition-base);
}

.form-input:focus {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px var(--color-primary-glow);
  outline: none;
}
```

#### 6.2.3 Budget Selector
Budget uses styled radio-button toggle chips (not a dropdown):
```
[ Low ≤₹300 ]  [ Medium ₹301–800 ]  [ High ₹800+ ]
```
Active chip glows with `--color-primary`.

#### 6.2.4 Star Rating Picker
Interactive 5-star rating input using CSS + JS (no library). Hovering highlights stars; clicking sets the `min_rating` value.

#### 6.2.5 Submit Button
```css
.btn-primary {
  background: linear-gradient(135deg, var(--color-primary), #c0392b);
  color: white;
  font-weight: 600;
  border-radius: var(--radius-md);
  padding: var(--space-4) var(--space-8);
  transition: transform var(--transition-fast),
              box-shadow var(--transition-base);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-glow);
}

.btn-primary:active { transform: translateY(0); }

/* Loading state */
.btn-primary.loading {
  pointer-events: none;
  opacity: 0.7;
}
.btn-primary.loading::after {
  content: "";
  display: inline-block;
  width: 16px; height: 16px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
  margin-left: var(--space-2);
  vertical-align: middle;
}
```

### Deliverables
- `frontend/index.html` (complete form section)
- `frontend/css/components.css` (form + button styles)

### Validation
- [ ] Form renders correctly in Chrome, Firefox, Safari
- [ ] All inputs are focusable and keyboard navigable
- [ ] Budget chips are mutually exclusive (only one selectable)
- [ ] Star picker highlights and sets value correctly
- [ ] Submit button shows loading spinner when clicked

---

## Phase 6.3 — Results & Recommendation Display

### Goal
Build the results section that dynamically renders recommendation cards from the API JSON response, with smooth entrance animations.

### Tasks

#### 6.3.1 Results Section Structure
```html
<!-- Hidden by default; revealed after API response -->
<section id="results-section" class="results-section hidden">
  <div class="results-header">
    <h2 class="results-title">Your Top Picks 🍽</h2>
    <p class="results-meta" id="results-meta"></p>  <!-- "5 restaurants found in Bangalore" -->
  </div>
  <div class="results-grid" id="results-grid">
    <!-- Cards injected by JS -->
  </div>
</section>
```

#### 6.3.2 Recommendation Card Component
Each card is generated by JS (`ui.js → createRestaurantCard(rec)`):
```html
<article class="rec-card" style="--delay: 0.1s">
  <div class="rec-card__rank">#1</div>
  <div class="rec-card__body">
    <h3 class="rec-card__name">Trattoria Italiana</h3>
    <div class="rec-card__meta">
      <span class="chip chip--cuisine">🍝 Italian, Continental</span>
      <span class="chip chip--type">Casual Dining</span>
    </div>
    <div class="rec-card__stats">
      <div class="stat">
        <span class="stat__stars">★★★★½</span>
        <span class="stat__value">4.5</span>
      </div>
      <div class="stat">💰 ₹650 for two</div>
    </div>
    <p class="rec-card__explanation">...</p>
    <div class="rec-card__badges">
      <span class="badge badge--online">📱 Online Order</span>
      <span class="badge badge--booking">📅 Table Booking</span>
    </div>
  </div>
</article>
```

#### 6.3.3 Card CSS (Glassmorphism)
```css
.rec-card {
  background: var(--color-glass);
  border: 1px solid var(--color-glass-border);
  border-radius: var(--radius-lg);
  padding: var(--space-6);
  transition: transform var(--transition-base), box-shadow var(--transition-base);
  animation: slideUp 0.5s var(--transition-slow) var(--delay, 0s) both;
}

.rec-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-hover);
  border-color: rgba(226, 55, 68, 0.3);
}

.rec-card__rank {
  font-family: var(--font-display);
  font-size: var(--fs-3xl);
  font-weight: 800;
  color: var(--color-primary);
  opacity: 0.6;
}
```

#### 6.3.4 Empty State & Error State
```html
<!-- Empty state -->
<div class="empty-state">
  <div class="empty-state__icon">🔍</div>
  <h3>No restaurants found</h3>
  <p>Try relaxing your filters — e.g., remove the cuisine preference.</p>
</div>

<!-- Error state -->
<div class="error-state">
  <div class="error-state__icon">⚠️</div>
  <h3>Something went wrong</h3>
  <p id="error-message"></p>
  <button class="btn-secondary" id="retry-btn">Try Again</button>
</div>
```

### Deliverables
- `frontend/css/components.css` (card + badge styles)
- `frontend/js/ui.js` (`createRestaurantCard()`, `renderResults()`, `showError()`, `showEmpty()`)

### Validation
- [ ] 5 cards render with staggered entrance animation
- [ ] Cards show rank, name, cuisine chips, rating stars, cost, explanation
- [ ] Hovering a card lifts it with shadow
- [ ] Empty and error states render correctly

---

## Phase 6.4 — API Integration

### Goal
Connect the frontend form to the Phase 5 Flask API using the Fetch API with proper loading states and error handling.

### Tasks

#### 6.4.1 API Client (`js/api.js`)
```javascript
// js/api.js
const API_BASE = "http://localhost:5000";

export async function fetchRecommendations(preferences) {
  const response = await fetch(`${API_BASE}/api/recommend`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(preferences),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || "Unexpected server error");
  }

  return data;   // { recommendations: [...], count: N }
}
```

#### 6.4.2 App Logic (`js/app.js`)
```javascript
// js/app.js
import { fetchRecommendations } from "./api.js";
import { renderResults, showLoading, showError, clearResults } from "./ui.js";

document.getElementById("recommend-form").addEventListener("submit", async (e) => {
  e.preventDefault();

  const prefs = collectFormValues();   // reads form inputs
  if (!prefs) return;                  // client-side validation failed

  showLoading(true);
  clearResults();

  try {
    const data = await fetchRecommendations(prefs);
    renderResults(data.recommendations, prefs);
  } catch (err) {
    showError(err.message);
  } finally {
    showLoading(false);
  }
});
```

#### 6.4.3 Client-Side Validation
Before hitting the API, validate in JS:
- Location must not be empty
- Budget must be one of `low / medium / high`
- Min rating, if provided, must be 0–5
- Show inline validation error messages beneath each field

### Deliverables
- `frontend/js/api.js`
- `frontend/js/app.js`

### Validation
- [ ] Submitting form with valid data calls `POST /api/recommend`
- [ ] Loading spinner shows while request is in-flight
- [ ] Successful response renders cards
- [ ] Network error or 400 from API shows the error state
- [ ] Client-side validation prevents form submission with empty location

---

## Phase 6.5 — Polish, Animations & Responsiveness

### Goal
Add the finishing touches: page animations, mobile layout, keyboard accessibility, and a smooth overall UX polish pass.

### Tasks

#### 6.5.1 Keyframe Animations (`css/animations.css`)
```css
@keyframes slideUp {
  from { opacity: 0; transform: translateY(24px); }
  to   { opacity: 1; transform: translateY(0); }
}

@keyframes fadeIn {
  from { opacity: 0; }
  to   { opacity: 1; }
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@keyframes shimmer {
  0%   { background-position: -200% 0; }
  100% { background-position:  200% 0; }
}

/* Skeleton loading shimmer */
.skeleton {
  background: linear-gradient(90deg,
    rgba(255,255,255,0.05) 25%,
    rgba(255,255,255,0.12) 50%,
    rgba(255,255,255,0.05) 75%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: var(--radius-sm);
}
```

#### 6.5.2 Skeleton Loading Cards
While the API is in-flight, show 3 skeleton cards in the results section so the layout doesn't jump.

#### 6.5.3 Responsive Breakpoints
```css
/* Mobile-first grid */
.results-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: var(--space-4);
}

@media (min-width: 640px) {
  .results-grid { grid-template-columns: repeat(2, 1fr); }
}

@media (min-width: 1024px) {
  .results-grid { grid-template-columns: repeat(3, 1fr); }
}

/* Form grid collapses to 1-col on mobile */
.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-4);
}

@media (max-width: 600px) {
  .form-grid { grid-template-columns: 1fr; }
}
```

#### 6.5.4 Scroll-to-Results
After results load, smoothly scroll the page down to the results section:
```javascript
document.getElementById("results-section").scrollIntoView({
  behavior: "smooth", block: "start"
});
```

#### 6.5.5 Accessibility (a11y)
- All form inputs have associated `<label>` elements
- Submit button has `aria-label`
- Results section has `aria-live="polite"` for screen readers
- Focus states use a visible outline (not suppressed)
- Color contrast meets WCAG AA

### Deliverables
- `frontend/css/animations.css` (all keyframes + skeleton)
- Updated `frontend/css/components.css` (responsive breakpoints)
- `frontend/js/ui.js` (skeleton loader, scroll-to-results)

### Validation
- [ ] Page looks correct on 375px (mobile), 768px (tablet), 1280px (desktop)
- [ ] Skeleton cards animate while API is loading
- [ ] Page scrolls to results automatically after load
- [ ] Lighthouse accessibility score ≥ 90
- [ ] No layout shifts (CLS = 0) during loading

---

## Phase Summary Table

| Phase | Name | Key Files | Depends On |
|---|---|---|---|
| **5.0** | Project Setup | `config.py`, `requirements.txt`, `.env` | — |
| **5.1** | Data Ingestion | `data/loader.py`, `preprocessor.py`, `filter_engine.py` | 5.0 |
| **5.2** | User Input Model | `ui/models.py`, `ui/input_collector.py` | 5.0 |
| **5.3** | Prompt Engineering | `integration/prompt_builder.py` | 5.1, 5.2 |
| **5.4** | LLM Engine (Groq) | `integration/llm_client.py`, `engine/recommender.py` | 5.3 |
| **5.5** | Output / API Layer | `output/formatter.py`, `output/renderer.py`, `api.py` | 5.4 |
| **5.6** | E2E Integration | `main.py`, `tests/` | All 5.x |
| **5.7** | Error Handling | Updates across multiple files | All 5.x |
| **6.1** | Design System | `frontend/css/tokens.css`, `index.html` skeleton | 5.5 ready |
| **6.2** | Preference Form | `frontend/index.html`, `css/components.css` | 6.1 |
| **6.3** | Results Display | `frontend/js/ui.js`, card styles | 6.2 |
| **6.4** | API Integration | `frontend/js/api.js`, `js/app.js` | 6.3, 5.5 |
| **6.5** | Polish & Responsive | `css/animations.css`, responsive breakpoints | 6.4 |

---

## File Structure After All Phases

```
zomato_recommendation/
│
├── data/
│   ├── loader.py            ← Phase 5.1: Dataset loader with caching
│   ├── preprocessor.py      ← Phase 5.1: Cleaning & normalization
│   └── filter_engine.py     ← Phase 5.1: Rule-based filtering
│
├── integration/
│   ├── prompt_builder.py    ← Phase 5.3: Constructs Groq LLM prompt
│   └── llm_client.py        ← Phase 5.4: Groq API wrapper + retry logic
│
├── engine/
│   └── recommender.py       ← Phase 5.4: Full pipeline orchestrator
│
├── output/
│   ├── formatter.py         ← Phase 5.5: Validates & sorts LLM response
│   └── renderer.py          ← Phase 5.5: Rich CLI output rendering
│
├── ui/
│   ├── models.py            ← Phase 5.2: UserPreference dataclass
│   └── input_collector.py   ← Phase 5.2: CLI input collection
│
├── tests/
│   ├── test_loader.py
│   ├── test_preprocessor.py
│   ├── test_filter_engine.py
│   ├── test_prompt_builder.py
│   ├── test_llm_client.py
│   ├── test_recommender.py
│   └── test_api.py          ← Phase 5.6: Flask endpoint tests
│
├── frontend/                ← Phase 6: Entire web frontend
│   ├── index.html
│   ├── css/
│   │   ├── reset.css
│   │   ├── tokens.css       ← Phase 6.1: Design tokens
│   │   ├── components.css   ← Phase 6.2–6.3: Component styles
│   │   └── animations.css   ← Phase 6.5: Keyframes & transitions
│   ├── js/
│   │   ├── api.js           ← Phase 6.4: Fetch API wrapper
│   │   ├── ui.js            ← Phase 6.3: DOM rendering helpers
│   │   └── app.js           ← Phase 6.4: Main app logic
│   └── assets/
│       └── logo.svg
│
├── config.py                ← Phase 5.0: Centralized config
├── main.py                  ← Phase 5.6: CLI entry point
├── api.py                   ← Phase 5.5: Flask REST API
├── requirements.txt         ← Phase 5.0: Dependencies
└── .env                     ← Phase 5.0: API keys & thresholds (not committed)
```

---

*Generated from `context.md` + `architecture.md` | Project: Zomato AI Recommendation System | Date: 2026-06-22*
