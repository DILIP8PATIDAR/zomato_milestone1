# data/loader.py — Dataset Loader (Phase 1.1)
# Loads the Zomato dataset from a baked parquet file (production) or
# Hugging Face (local dev) and caches it in memory for the session.

from pathlib import Path

import config  # noqa: F401 — must load first to set HF cache paths
import pandas as pd
from config import HF_DATASET_NAME

_CACHE: pd.DataFrame | None = None
_PARQUET_PATH = Path(__file__).resolve().parent / "zomato.parquet"

# Actual column names from ManikaSaini/zomato-restaurant-recommendation dataset
# Note: rating column is "rate" (format "4.1/5"), not "aggregate_rating"
REQUIRED_FIELDS = [
    "name", "location", "cuisines", "approx_cost(for two people)",
    "rate", "votes",
    "online_order", "book_table", "rest_type"
]


def _load_from_parquet() -> pd.DataFrame:
    return pd.read_parquet(_PARQUET_PATH)


def _load_from_huggingface() -> pd.DataFrame:
    from datasets import load_dataset

    try:
        ds = load_dataset(HF_DATASET_NAME, split="train")
        ds = ds.select_columns(REQUIRED_FIELDS)
    except Exception as e:
        raise RuntimeError(
            f"Failed to load dataset '{HF_DATASET_NAME}'. "
            f"Check your internet connection. Error: {e}"
        ) from e
    return ds.to_pandas()


def load_dataset_as_df() -> pd.DataFrame:
    """Load Zomato dataset and return as DataFrame. Cached."""
    global _CACHE
    if _CACHE is not None:
        return _CACHE

    if _PARQUET_PATH.exists():
        _CACHE = _load_from_parquet()
    else:
        _CACHE = _load_from_huggingface()

    return _CACHE
