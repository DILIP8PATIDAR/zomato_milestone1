# ui/input_collector.py — CLI Input Collector (Phase 2.2)
# Collects user preferences interactively from the terminal and returns a
# validated UserPreference object.

from ui.models import UserPreference


def collect_preferences() -> UserPreference:
    """
    Prompt the user for restaurant preferences via stdin.
    Returns a validated UserPreference dataclass.
    Raises AssertionError if budget or rating are invalid.
    """
    print("\n🍽  Welcome to the Zomato AI Restaurant Recommender\n")

    location = input("Enter location (e.g., Bangalore, Delhi): ").strip()
    budget   = input("Enter budget [low / medium / high]: ").strip().lower()
    cuisine  = input("Preferred cuisine (press Enter to skip): ").strip() or None

    rating_input = input("Minimum rating (0.0–5.0, press Enter to skip): ").strip()
    min_rating   = float(rating_input) if rating_input else None

    extras = input("Any additional preferences (press Enter to skip): ").strip() or None

    prefs = UserPreference(
        location=location,
        budget=budget,
        cuisine=cuisine,
        min_rating=min_rating,
        additional_preferences=extras,
    )
    prefs.validate()
    return prefs
