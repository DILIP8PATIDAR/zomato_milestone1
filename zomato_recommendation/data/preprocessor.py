# data/preprocessor.py — Data Preprocessing (Phase 1.2)
# Normalizes raw Zomato DataFrame: renames columns, casts types,
# drops nulls/duplicates, and adds derived columns (budget_tier, cuisines_list).

import pandas as pd
from config import BUDGET_TIERS


def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply all normalization steps to raw Zomato DataFrame.

    Steps (in order):
      1. Strip whitespace from all string columns
      2. Rename: approx_cost(for two people) → approx_cost, aggregate_rating → rating
      3. Type-cast approx_cost: remove commas, cast to numeric (int); invalid → NaN
      4. Type-cast rating: cast to float; "NEW" / "-" → NaN
      5. Drop rows missing name, location, rating, or approx_cost
      6. Deduplicate on name + location (keep first occurrence)
      7. Add budget_tier column: "low" | "medium" | "high"
      8. Add cuisines_list column: lowercase list from comma-separated cuisines string
      9. Normalize location: lowercase + strip whitespace
    """
    df = df.copy()

    # Step 1: Strip whitespace from all string columns
    str_cols = df.select_dtypes(include="object").columns
    df[str_cols] = df[str_cols].apply(lambda col: col.str.strip())

    # Step 2: Rename columns
    df.rename(
        columns={
            "approx_cost(for two people)": "approx_cost",
            "rate": "rating",   # actual HF dataset uses 'rate', not 'aggregate_rating'
        },
        inplace=True,
    )

    # Step 3: Clean & cast approx_cost
    df["approx_cost"] = pd.to_numeric(
        df["approx_cost"].astype(str).str.replace(",", "", regex=False),
        errors="coerce",
    )

    # Step 4: Clean & cast rating
    # Dataset stores rating as "4.1/5" — strip the "/5" suffix first
    df["rating"] = pd.to_numeric(
        df["rating"].astype(str).str.replace(r"/5$", "", regex=True).str.strip(),
        errors="coerce",
    )

    # Step 5: Drop rows with missing critical fields
    df.dropna(subset=["name", "location", "rating", "approx_cost"], inplace=True)

    # Step 6: Deduplicate on name + location
    df.drop_duplicates(subset=["name", "location"], keep="first", inplace=True)

    # Step 7: Budget tier
    def _tier(cost: float) -> str:
        for tier_name, (lo, hi) in BUDGET_TIERS.items():
            if lo <= cost <= hi:
                return tier_name
        return "high"

    df["budget_tier"] = df["approx_cost"].apply(_tier)

    # Step 8: Parse cuisines → lowercase list
    df["cuisines_list"] = (
        df["cuisines"]
        .str.lower()
        .str.split(",")
        .apply(lambda x: [c.strip() for c in x] if isinstance(x, list) else [])
    )

    # Step 9: Normalize location
    df["location"] = df["location"].str.lower().str.strip()

    return df.reset_index(drop=True)
