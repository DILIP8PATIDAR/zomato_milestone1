# config.py — Central configuration module for Zomato AI Recommendation System
# Loads all settings from .env via python-dotenv.

import os
from pathlib import Path

from dotenv import load_dotenv

# Use a project-local Hugging Face cache so dataset downloads work in
# restricted environments (e.g. Cursor sandbox) that block ~/.cache writes.
_PROJECT_ROOT = Path(__file__).resolve().parent
_HF_CACHE_DIR = _PROJECT_ROOT / ".cache" / "huggingface"
_HF_CACHE_DIR.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("HF_HOME", str(_HF_CACHE_DIR))
os.environ.setdefault("HF_DATASETS_CACHE", str(_HF_CACHE_DIR / "datasets"))
os.environ.setdefault("HUGGINGFACE_HUB_CACHE", str(_HF_CACHE_DIR / "hub"))

load_dotenv()

GROQ_API_KEY      = os.getenv("GROQ_API_KEY")
GROQ_MODEL        = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
HF_DATASET_NAME   = os.getenv("HF_DATASET_NAME")
BUDGET_LOW_MAX    = int(os.getenv("BUDGET_LOW_MAX", 300))
BUDGET_MEDIUM_MAX = int(os.getenv("BUDGET_MEDIUM_MAX", 800))
MAX_CANDIDATES    = int(os.getenv("MAX_CANDIDATES", 20))
LLM_TEMPERATURE   = float(os.getenv("LLM_TEMPERATURE", 0.4))
LLM_MAX_TOKENS    = int(os.getenv("LLM_MAX_TOKENS", 1500))

BUDGET_TIERS = {
    "low":    (0,                  BUDGET_LOW_MAX),
    "medium": (BUDGET_LOW_MAX + 1, BUDGET_MEDIUM_MAX),
    "high":   (BUDGET_MEDIUM_MAX + 1, float("inf")),
}
