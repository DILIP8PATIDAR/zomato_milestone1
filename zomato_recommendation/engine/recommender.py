# engine/recommender.py — Recommender Orchestrator (Phase 4.2)
# Wires together data loading, preprocessing, filtering, prompt construction,
# and the Groq LLM call into a single recommend() entry point.

import pandas as pd
from ui.models import UserPreference
from data.loader import load_dataset_as_df
from data.preprocessor import preprocess
from data.filter_engine import filter_restaurants
from integration.prompt_builder import build_prompt
from integration.llm_client import call_groq


def recommend(prefs: UserPreference) -> list[dict]:
    """
    Full recommendation pipeline.

    1. Load & preprocess the Zomato dataset (cached after first call).
    2. Filter candidates with progressive relaxation.
    3. Build the LLM prompt.
    4. Call Groq and return ranked recommendation dicts.

    Returns an empty list if no candidates survive all relaxation passes.
    """
    # Step 1: Load & preprocess
    raw_df = load_dataset_as_df()
    df     = preprocess(raw_df)

    # Step 2: Filter with progressive relaxation
    candidates = _filter_with_relaxation(df, prefs)
    if candidates.empty:
        print("[Recommender] No candidates found even after full relaxation.")
        return []

    # Step 3: Build prompt
    prompt = build_prompt(candidates, prefs)

    # Step 4: Call Groq LLM
    recommendations = call_groq(prompt)

    return recommendations


def _filter_with_relaxation(df: pd.DataFrame, prefs: UserPreference) -> pd.DataFrame:
    """
    Try filtering with all constraints; progressively relax if results are empty.

    Pass 1 — all filters (location + budget + cuisine + min_rating)
    Pass 2 — drop cuisine filter
    Pass 3 — drop budget filter
    Pass 4 — location + min_rating only (most relaxed)
    """
    strategies = [
        dict(location=prefs.location, budget=prefs.budget,
             cuisine=prefs.cuisine,   min_rating=prefs.min_rating),
        dict(location=prefs.location, budget=prefs.budget,
             cuisine=None,            min_rating=prefs.min_rating),
        dict(location=prefs.location, budget=None,
             cuisine=None,            min_rating=prefs.min_rating),
        dict(location=prefs.location, budget=None,
             cuisine=None,            min_rating=None),
    ]

    for i, strategy in enumerate(strategies, start=1):
        result = filter_restaurants(df, **strategy)
        if not result.empty:
            if i > 1:
                print(f"[Filter] Relaxation pass {i} used: {strategy}")
            return result

    return pd.DataFrame()
