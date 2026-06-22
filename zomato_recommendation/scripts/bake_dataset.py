#!/usr/bin/env python3
"""Bake the Hugging Face dataset to a small parquet file for low-memory deploys."""

from pathlib import Path

from datasets import load_dataset

REQUIRED_FIELDS = [
    "name",
    "location",
    "cuisines",
    "approx_cost(for two people)",
    "rate",
    "votes",
    "online_order",
    "book_table",
    "rest_type",
]

DATASET_NAME = "ManikaSaini/zomato-restaurant-recommendation"
OUTPUT = Path(__file__).resolve().parent.parent / "data" / "zomato.parquet"


def main() -> None:
    ds = load_dataset(DATASET_NAME, split="train").select_columns(REQUIRED_FIELDS)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    ds.to_pandas().to_parquet(OUTPUT, index=False)
    print(f"Baked {len(ds)} rows to {OUTPUT} ({OUTPUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
