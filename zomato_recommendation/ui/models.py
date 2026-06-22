# ui/models.py — User Preference Data Class (Phase 2.1)
# Holds validated user preferences passed through the pipeline.

from dataclasses import dataclass


@dataclass
class UserPreference:
    location: str
    budget: str                         # "low" | "medium" | "high"
    cuisine: str | None = None
    min_rating: float | None = None
    additional_preferences: str | None = None

    def validate(self):
        """Raise AssertionError on invalid inputs."""
        assert self.budget in ("low", "medium", "high"), \
            "Budget must be 'low', 'medium', or 'high'"
        if self.min_rating is not None:
            assert 0.0 <= self.min_rating <= 5.0, \
                "min_rating must be between 0.0 and 5.0"
        assert self.location.strip(), "Location cannot be empty"
