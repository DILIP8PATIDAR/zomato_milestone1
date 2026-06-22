# integration/llm_client.py — Groq API Client (Phase 4.1)
# Sends the prompt to Groq and parses the JSON recommendation response.

import json
import re
import time
from groq import Groq
from config import GROQ_API_KEY, GROQ_MODEL, LLM_TEMPERATURE, LLM_MAX_TOKENS

_client: Groq | None = None


def _get_client() -> Groq:
    """Create the Groq client on first use so the app can boot without the key."""
    global _client
    if _client is None:
        if not GROQ_API_KEY:
            raise RuntimeError(
                "GROQ_API_KEY is not set. Add it in your Railway environment variables."
            )
        _client = Groq(api_key=GROQ_API_KEY)
    return _client


def call_groq(prompt: str, retries: int = 3) -> list[dict]:
    """
    Send prompt to Groq and return a parsed list of recommendation dicts.
    Retries up to `retries` times with exponential backoff (1s → 2s → 4s).
    Raises RuntimeError after all retries are exhausted.
    """
    for attempt in range(retries):
        try:
            response = _get_client().chat.completions.create(
                model=GROQ_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=LLM_TEMPERATURE,
                max_tokens=LLM_MAX_TOKENS,
            )
            raw = response.choices[0].message.content
            return _parse_response(raw)
        except Exception as e:
            if attempt < retries - 1:
                wait = 2 ** attempt          # 1s, 2s, 4s
                print(f"[Groq] Attempt {attempt + 1} failed: {e}. Retrying in {wait}s…")
                time.sleep(wait)
            else:
                raise RuntimeError(f"Groq API failed after {retries} attempts: {e}")


def _parse_response(raw: str) -> list[dict]:
    """
    Parse JSON array from LLM response.
    Strategy 1: Direct json.loads on the full response.
    Strategy 2: Regex extraction of the first [...] block (handles markdown fences).
    Raises ValueError if both strategies fail.
    """
    raw = raw.strip()

    # Strategy 1: direct parse
    try:
        result = json.loads(raw)
        if isinstance(result, list):
            return result
    except json.JSONDecodeError:
        pass

    # Strategy 2: regex fallback — extract first [...] block
    match = re.search(r"\[.*\]", raw, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    raise ValueError(f"Could not parse LLM response as JSON array:\n{raw[:500]}")
