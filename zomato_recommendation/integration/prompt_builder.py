# integration/prompt_builder.py — Prompt Construction (Phase 3.1)
# Serialises filtered restaurants + user preferences into the LLM prompt.

import pandas as pd
from ui.models import UserPreference
from config import BUDGET_TIERS


def _serialize_restaurants(df: pd.DataFrame) -> str:
    """Convert DataFrame rows into a numbered, human-readable list."""
    lines = []
    for i, row in df.iterrows():
        line = (
            f"{i + 1}. Name: {row['name']} | "
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
    """Return a human-readable budget range string."""
    lo, hi = BUDGET_TIERS[budget]
    if hi == float("inf"):
        return f"above ₹{lo}"
    return f"₹{lo}–₹{int(hi)} for two"


def build_prompt(df: pd.DataFrame, prefs: UserPreference) -> str:
    """
    Build the full LLM prompt from filtered restaurants and user preferences.
    Optional fields (cuisine, rating, extras) are omitted when None to avoid
    blank lines in the prompt.
    """
    restaurant_list = _serialize_restaurants(df)

    # Build optional preference lines — only included when provided
    optional_lines = []
    if prefs.cuisine:
        optional_lines.append(f"- Preferred Cuisine: {prefs.cuisine}")
    if prefs.min_rating is not None:
        optional_lines.append(f"- Minimum Rating: {prefs.min_rating}")
    if prefs.additional_preferences:
        optional_lines.append(f"- Special Preferences: {prefs.additional_preferences}")

    optional_block = "\n".join(optional_lines)

    prompt = f"""You are an expert restaurant recommendation assistant with deep knowledge of dining preferences and restaurant quality.

User Preferences:
- Location: {prefs.location}
- Budget: {prefs.budget} ({_budget_range_str(prefs.budget)})
{optional_block}

Candidate Restaurants:
{restaurant_list}

Task:
Rank the above restaurants from best to worst fit for this user.
For each restaurant in your top 5, provide a 2–3 sentence explanation of why it is a great match.

Respond ONLY as a valid JSON array. Each element must have these exact keys:
rank, name, cuisine, rating, estimated_cost, explanation

Do not include any text outside the JSON array."""

    return prompt.strip()
