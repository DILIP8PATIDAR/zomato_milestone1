# config.py — Central configuration module for Zomato AI Recommendation System
# Loads all settings from .env via python-dotenv.

import os
from dotenv import load_dotenv

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
