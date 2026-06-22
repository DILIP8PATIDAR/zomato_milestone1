# Architecture: AI-Powered Restaurant Recommendation System (Zomato Use Case)

> **Source:** `context.md` | **Date:** 2026-06-22

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [High-Level Architecture Diagram](#2-high-level-architecture-diagram)
3. [Layer-by-Layer Breakdown](#3-layer-by-layer-breakdown)
   - 3.1 [User Interface Layer](#31-user-interface-layer)
   - 3.2 [Data Ingestion Layer](#32-data-ingestion-layer)
   - 3.3 [Integration Layer](#33-integration-layer)
   - 3.4 [LLM Recommendation Engine](#34-llm-recommendation-engine)
   - 3.5 [Output Display Layer](#35-output-display-layer)
4. [Data Flow](#4-data-flow)
5. [Component Design](#5-component-design)
6. [Prompt Engineering Design](#6-prompt-engineering-design)
7. [Data Schema](#7-data-schema)
8. [Technology Stack](#8-technology-stack)
9. [Error Handling & Edge Cases](#9-error-handling--edge-cases)
10. [Scalability & Extensibility](#10-scalability--extensibility)

---

## 1. System Overview

The system is an **AI-powered restaurant recommendation engine** that combines:
- **Structured data filtering** (rule-based, deterministic) — to narrow down restaurants from a large dataset based on user preferences
- **LLM reasoning** (generative, contextual) — to rank, explain, and personalize the filtered results

The pipeline is linear and sequential: user preferences flow through data filtering → prompt construction → LLM inference → formatted output.

---

## 2. High-Level Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────────┐
│                        USER INTERFACE LAYER                          │
│                                                                      │
│   Location │ Budget │ Cuisine │ Min Rating │ Additional Preferences  │
└───────────────────────────────┬──────────────────────────────────────┘
                                │  User Preference Object
                                ▼
┌──────────────────────────────────────────────────────────────────────┐
│                       DATA INGESTION LAYER                           │
│                                                                      │
│  ┌─────────────────────┐      ┌──────────────────────────────────┐  │
│  │  Hugging Face       │ ───► │  Preprocessing & Normalization   │  │
│  │  Zomato Dataset     │      │  (clean, type-cast, deduplicate) │  │
│  └─────────────────────┘      └────────────────┬─────────────────┘  │
│                                                │                    │
│                               ┌────────────────▼─────────────────┐  │
│                               │  Rule-based Filtering Engine      │  │
│                               │  (location, budget, cuisine,      │  │
│                               │   rating threshold)               │  │
│                               └────────────────┬─────────────────┘  │
└────────────────────────────────────────────────┼────────────────────┘
                                                 │  Filtered Restaurant List
                                                 ▼
┌──────────────────────────────────────────────────────────────────────┐
│                       INTEGRATION LAYER                              │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  Prompt Builder                                              │   │
│  │  - Serialize filtered restaurants into structured text       │   │
│  │  - Inject user preferences as context                        │   │
│  │  - Append task instruction (rank + explain)                  │   │
│  └──────────────────────────────────┬───────────────────────────┘   │
└─────────────────────────────────────┼────────────────────────────────┘
                                      │  Constructed LLM Prompt
                                      ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    LLM RECOMMENDATION ENGINE                         │
│                                                                      │
│   Model: Groq (e.g., LLaMA 3, Mixtral via Groq API)                  │
│                                                                      │
│   Tasks:                                                             │
│   ├── Rank restaurants based on preference fit                       │
│   ├── Generate per-restaurant natural language explanation            │
│   └── (Optional) Produce an overall summary of choices               │
└─────────────────────────────────────┬────────────────────────────────┘
                                      │  Structured LLM Response
                                      ▼
┌──────────────────────────────────────────────────────────────────────┐
│                       OUTPUT DISPLAY LAYER                           │
│                                                                      │
│   Top-N Recommendation Cards:                                        │
│   ┌──────────────────────────────────────────────────┐              │
│   │  🍽 Restaurant Name   ⭐ Rating   💰 Est. Cost   │              │
│   │  🍜 Cuisine           📍 Location                │              │
│   │  💬 AI Explanation                               │              │
│   └──────────────────────────────────────────────────┘              │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 3. Layer-by-Layer Breakdown

### 3.1 User Interface Layer

**Purpose:** Collect structured user preferences before any data processing begins.

**Inputs collected:**

| Input Field | Type | Example Values | Required |
|---|---|---|---|
| Location | String | `Delhi`, `Bangalore`, `Mumbai` | Yes |
| Budget | Enum | `low`, `medium`, `high` | Yes |
| Cuisine | String | `Italian`, `Chinese`, `Indian` | Optional |
| Minimum Rating | Float | `3.5`, `4.0`, `4.5` | Optional |
| Additional Preferences | Free text | `family-friendly`, `quick service`, `outdoor seating` | Optional |

**Output:** A **User Preference Object** passed to the Data Ingestion Layer.

---

### 3.2 Data Ingestion Layer

**Purpose:** Load, clean, and filter the raw Zomato dataset down to a relevant candidate set.

#### Sub-components:

**a) Dataset Loader**
- Source: [Hugging Face — ManikaSaini/zomato-restaurant-recommendation](https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation)
- Method: Load via `datasets` library (Python) or direct CSV/Parquet download
- Fields to retain:

| Field | Description |
|---|---|
| `name` | Restaurant name |
| `location` / `city` | City or area |
| `cuisines` | Cuisine types served |
| `approx_cost` | Approximate cost for two people |
| `aggregate_rating` | Overall customer rating |
| `rating_text` | Textual rating label (e.g., "Good", "Excellent") |
| `votes` | Number of customer votes |
| `online_order` | Whether online ordering is available |
| `book_table` | Whether table booking is available |
| `rest_type` | Type of restaurant (e.g., Casual Dining, Café) |

**b) Preprocessing & Normalization**
- Strip whitespace, fix encoding issues
- Normalize cost: map `approx_cost` ranges to `low / medium / high` budget tiers
  - `low`: ≤ ₹300
  - `medium`: ₹301–₹800
  - `high`: > ₹800
- Parse `cuisines` string into a list for multi-value matching
- Drop rows with null `name`, `location`, or `aggregate_rating`
- Deduplicate on `name + location`

**c) Rule-based Filtering Engine**
- Apply filters sequentially:
  1. **Location filter** — exact or fuzzy match on city/area
  2. **Budget filter** — match normalized cost tier
  3. **Cuisine filter** — check if requested cuisine appears in the restaurant's cuisine list
  4. **Rating filter** — `aggregate_rating >= min_rating`
- Output: filtered list (target: top 10–20 candidates for LLM)

---

### 3.3 Integration Layer

**Purpose:** Bridge structured data and the LLM by constructing a high-quality, context-rich prompt.

#### Responsibilities:
1. **Serialize** filtered restaurants into a structured text block
2. **Inject** user preferences as a clear context statement
3. **Frame** the task instruction for the LLM (rank + explain)

#### Prompt Construction Logic:
```
[System Role]
  You are an expert restaurant recommendation assistant.

[User Preferences Context]
  The user is looking for restaurants in {location} with a {budget} budget,
  preferring {cuisine} cuisine, with a minimum rating of {min_rating}.
  Additional preferences: {additional_preferences}.

[Candidate Restaurants]
  Here are the filtered restaurants:
  1. Name: {name} | Cuisine: {cuisines} | Rating: {rating} | Cost: {cost} | Type: {rest_type}
  2. ...

[Task Instruction]
  Based on the user preferences above, rank these restaurants from best to worst fit.
  For each recommendation, provide:
  - A rank (1 = best)
  - A 2–3 sentence explanation of why it suits the user
  Output as a JSON array.
```

---

### 3.4 LLM Recommendation Engine

**Purpose:** Apply AI reasoning to rank and explain restaurant options.

**Supported Models:**
| Model | Provider | Notes |
|---|---|---|
| LLaMA 3.3 70B (`llama-3.3-70b-versatile`) | Groq | Preferred; ultra-low latency inference |
| Mixtral 8x7B (`mixtral-8x7b-32768`) | Groq | Alternative; strong reasoning, large context window |
| LLaMA 3.1 8B (`llama-3.1-8b-instant`) | Groq | Lightweight; fastest response times for simpler queries |

**LLM Tasks:**
1. **Ranking** — order restaurants by best fit to user preferences
2. **Explanation** — generate a natural-language justification per restaurant
3. **Summarization** *(optional)* — produce a short overall summary of the recommendation set

**Output format (expected from LLM):**
```json
[
  {
    "rank": 1,
    "name": "Restaurant Name",
    "cuisine": "Italian",
    "rating": 4.5,
    "estimated_cost": "₹600 for two",
    "explanation": "This restaurant excels at Italian cuisine with a cozy ambiance perfect for family dining, well within your medium budget."
  },
  ...
]
```

**LLM Configuration:**
- `temperature`: `0.4` — balanced creativity vs. consistency
- `max_tokens`: `1500` — sufficient for top-5 recommendations
- `response_format`: JSON (structured output mode where supported)

---

### 3.5 Output Display Layer

**Purpose:** Render the LLM response into a clean, user-friendly format.

**Recommendation Card fields:**

| Field | Source |
|---|---|
| Restaurant Name | Dataset + LLM rank |
| Cuisine | Dataset |
| Rating | Dataset |
| Estimated Cost | Dataset (normalized) |
| AI-generated Explanation | LLM output |

**Display options:**
- **CLI:** Formatted table / numbered list
- **Web UI:** Card-based layout with badges for cuisine, rating stars, cost tier
- **API Response:** JSON array (for integration with front-end clients)

---

## 4. Data Flow

```
User Preferences
       │
       ▼
User Preference Object {location, budget, cuisine, min_rating, extras}
       │
       ▼
Dataset Load → Raw DataFrame (all restaurants)
       │
       ▼
Preprocess → Clean DataFrame (normalized fields)
       │
       ▼
Filter → Candidate List (10–20 restaurants)
       │
       ▼
Prompt Builder → LLM Prompt String
       │
       ▼
LLM API Call → Raw JSON Response
       │
       ▼
Response Parser → Ranked Recommendation Objects
       │
       ▼
Renderer → User-facing Output (CLI / Web / API)
```

---

## 5. Component Design

```
zomato_recommendation/
│
├── data/
│   ├── loader.py            # Hugging Face dataset download & caching
│   ├── preprocessor.py      # Cleaning, normalization, deduplication
│   └── filter_engine.py     # Rule-based filtering logic
│
├── integration/
│   ├── prompt_builder.py    # Constructs LLM prompt from data + preferences
│   └── llm_client.py       # Wrapper for Groq API calls
│
├── engine/
│   └── recommender.py       # Orchestrates the full pipeline end-to-end
│
├── output/
│   ├── formatter.py         # Parses LLM JSON response
│   └── renderer.py          # CLI / Web output rendering
│
├── ui/
│   └── input_collector.py   # CLI or web form for collecting user preferences
│
├── config.py                # API keys, model config, budget thresholds
└── main.py                  # Entry point
```

---

## 6. Prompt Engineering Design

### Design Principles
- **Role assignment** — set the LLM as an expert assistant to anchor its persona
- **Structured data injection** — pass restaurant data in a numbered, readable format (not raw JSON) to maximize LLM comprehension
- **Explicit task framing** — clearly state the output format to minimize parsing errors
- **Preference grounding** — always include user preferences in the prompt so the LLM has full context

### Prompt Template

```
System: You are an expert restaurant recommendation assistant with deep knowledge of dining preferences and restaurant quality.

User Preferences:
- Location: {location}
- Budget: {budget} (approx. cost for two: {cost_range})
- Preferred Cuisine: {cuisine}
- Minimum Rating: {min_rating}
- Special Preferences: {additional_preferences}

Candidate Restaurants:
{numbered_restaurant_list}

Task:
Rank the above restaurants from best to worst fit for this user.
For each restaurant in your top 5, provide:
1. Rank number
2. Restaurant name
3. A 2–3 sentence explanation of why it's a good fit

Respond ONLY as a valid JSON array with keys: rank, name, cuisine, rating, estimated_cost, explanation.
```

---

## 7. Data Schema

### User Preference Object
```json
{
  "location": "Bangalore",
  "budget": "medium",
  "cuisine": "Italian",
  "min_rating": 4.0,
  "additional_preferences": "family-friendly, quiet ambiance"
}
```

### Restaurant Record (after preprocessing)
```json
{
  "name": "Trattoria Italiana",
  "location": "Bangalore",
  "cuisines": ["Italian", "Continental"],
  "approx_cost": 650,
  "budget_tier": "medium",
  "aggregate_rating": 4.3,
  "rating_text": "Very Good",
  "votes": 1200,
  "rest_type": "Casual Dining",
  "online_order": true,
  "book_table": false
}
```

### LLM Output Record
```json
{
  "rank": 1,
  "name": "Trattoria Italiana",
  "cuisine": "Italian",
  "rating": 4.3,
  "estimated_cost": "₹650 for two",
  "explanation": "Trattoria Italiana is an excellent match — it offers authentic Italian cuisine in a casual dining setting, within your medium budget, and its 4.3 rating reflects consistently positive customer experiences."
}
```

---

## 8. Technology Stack

| Layer | Technology | Rationale |
|---|---|---|
| Language | Python 3.10+ | Ecosystem support for ML/data/LLM libraries |
| Dataset | Hugging Face `datasets` | Easy access to Zomato dataset; caching support |
| Data Processing | `pandas` | Efficient filtering and normalization |
| LLM API | `groq` (Python SDK) | Ultra-fast inference via Groq Cloud API; supports LLaMA 3, Mixtral |
| Prompt Management | Custom `PromptBuilder` class | Keeps prompts versioned and testable |
| Output Parsing | `json` stdlib + fallback regex | Parse LLM structured responses robustly |
| CLI UI | `argparse` or `rich` | Developer-friendly interface |
| Web UI *(optional)* | `Streamlit` or `FastAPI + React` | Rapid prototype or production-grade frontend |
| Config Management | `python-dotenv` | Secure API key management |

---

## 9. Error Handling & Edge Cases

| Scenario | Handling Strategy |
|---|---|
| No restaurants match filters | Relax filters progressively (drop cuisine → drop budget → drop location) and inform user |
| LLM returns malformed JSON | Retry with explicit format reminder; fallback to regex extraction |
| Dataset unavailable | Cache dataset locally on first load; raise clear error if cache missing |
| Empty `additional_preferences` | Omit that section from the prompt to avoid confusing the LLM |
| Very low vote count restaurants | Flag with a "limited reviews" warning in output |
| API rate limit / timeout | Exponential backoff with max 3 retries |

---

## 10. Scalability & Extensibility

### Scaling Considerations
- **Dataset size:** Pre-filter and index the dataset at startup (not per-request) to reduce latency
- **Caching:** Cache LLM responses for identical preference objects (hash-based key)
- **Async:** Use async LLM API calls if processing multiple user requests concurrently

### Extension Points
| Feature | How to Add |
|---|---|
| Multiple cities / regions | Extend location filter with fuzzy matching or geo-coordinates |
| Real-time data | Replace static Hugging Face dataset with a live restaurant API (e.g., Zomato API) |
| User history | Add a user profile store; inject past orders into the prompt |
| Multi-language support | Translate preferences and output via LLM translation step |
| Feedback loop | Collect user ratings on recommendations; use to fine-tune prompt or ranking heuristics |
| Vector search | Embed restaurant descriptions; use semantic similarity for better candidate retrieval |

---

*Generated from `context.md` | Project: Zomato AI Recommendation System | Date: 2026-06-22*
