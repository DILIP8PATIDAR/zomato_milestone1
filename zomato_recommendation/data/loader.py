# data/loader.py — Dataset Loader (Phase 1.1)
# Loads the Zomato dataset from Hugging Face and caches it in memory for the session.

import config  # noqa: F401 — must load first to set HF cache paths
from datasets import load_dataset
import pandas as pd
from config import HF_DATASET_NAME

_CACHE: pd.DataFrame | None = None

# Actual column names from ManikaSaini/zomato-restaurant-recommendation dataset
# Note: rating column is "rate" (format "4.1/5"), not "aggregate_rating"
REQUIRED_FIELDS = [
    "name", "location", "cuisines", "approx_cost(for two people)",
    "rate", "votes",
    "online_order", "book_table", "rest_type"
]


def load_dataset_as_df() -> pd.DataFrame:
    """Load Zomato dataset from Hugging Face and return as DataFrame. Cached."""
    global _CACHE
    if _CACHE is not None:
        return _CACHE
    try:
        ds = load_dataset(HF_DATASET_NAME, split="train")
        # Select columns before pandas conversion — the full dataset is ~550 MB
        # in memory as a DataFrame, which exceeds Railway's default RAM limit.
        ds = ds.select_columns(REQUIRED_FIELDS)
    except Exception as e:
        raise RuntimeError(
            f"Failed to load dataset '{HF_DATASET_NAME}'. "
            f"Check your internet connection. Error: {e}"
        )
    _CACHE = ds.to_pandas()
    return _CACHE
