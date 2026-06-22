# Railpack entrypoint when deploying from the monorepo root.
import sys
from pathlib import Path

_BACKEND = Path(__file__).resolve().parent / "zomato_recommendation"
sys.path.insert(0, str(_BACKEND))

from api import app  # noqa: E402
