# data/filter_engine.py — Rule-Based Filter Engine (Phase 1.3)
# Applies optional filters sequentially on the preprocessed DataFrame
# and returns the top MAX_CANDIDATES restaurants sorted by rating (desc).

import pandas as pd
from config import MAX_CANDIDATES


def filter_restaurants(
    df: pd.DataFrame,
    location: str | None = None,
    budget: str | None = None,
    cuisine: str | None = None,
    min_rating: float | None = None,
) -> pd.DataFrame:
    """
    Filter the preprocessed DataFrame by user preferences.
    Each parameter is optional — if None, that filter is skipped.

    Filter order:
      1. Location  — substring match on normalized location column
      2. Budget    — exact match on budget_tier ("low" | "medium" | "high")
      3. Cuisine   — substring match within cuisines_list entries
      4. Min rating — minimum aggregate rating threshold

    Results are sorted by rating (desc) and capped at MAX_CANDIDATES rows.
    """
    result = df.copy()

    # 1. Location filter (substring, case-insensitive — location already lowercased)
    if location:
        loc = location.lower().strip()
        result = result[result["location"].str.contains(loc, na=False)]

    # 2. Budget tier filter (exact match)
    if budget:
        result = result[result["budget_tier"] == budget.lower()]

    # 3. Cuisine filter (substring match within each cuisine entry)
    if cuisine:
        cuis = cuisine.lower().strip()
        result = result[
            result["cuisines_list"].apply(
                lambda lst: any(cuis in c for c in lst)
            )
        ]

    # 4. Minimum rating filter
    if min_rating is not None:
        result = result[result["rating"] >= min_rating]

    # Sort by rating descending and cap to MAX_CANDIDATES
    result = result.sort_values("rating", ascending=False).head(MAX_CANDIDATES)
    return result.reset_index(drop=True)
