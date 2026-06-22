# output/formatter.py — Recommendation Formatter (Phase 5.5)
# Validates and normalises LLM output records, silently dropping malformed ones.

REQUIRED_KEYS = {"rank", "name", "cuisine", "rating", "estimated_cost", "explanation"}


def format_recommendations(raw: list[dict]) -> list[dict]:
    """
    Validate, clean, and sort LLM recommendation records.

    - Records missing any of REQUIRED_KEYS are silently dropped.
    - `rank` is cast to int, `rating` is cast to float.
    - Results are sorted ascending by rank.

    Args:
        raw: List of raw dicts returned by the LLM.

    Returns:
        Cleaned, sorted list of recommendation dicts.
    """
    valid = []
    for item in raw:
        if not REQUIRED_KEYS.issubset(item.keys()):
            print(f"[Formatter] Dropping malformed record (missing keys): {item.keys()}")
            continue
        try:
            item["rank"] = int(item["rank"])
            item["rating"] = float(item["rating"])
        except (ValueError, TypeError) as e:
            print(f"[Formatter] Dropping record with bad rank/rating: {e}")
            continue
        valid.append(item)

    return sorted(valid, key=lambda x: x["rank"])
