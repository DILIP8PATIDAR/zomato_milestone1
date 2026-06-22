# main.py — CLI Entry Point (Phase 5.6)
# Wires all backend phases together for terminal use.
# Collects preferences → runs pipeline → formats → renders results.

from ui.input_collector import collect_preferences
from engine.recommender import recommend
from output.formatter import format_recommendations
from output.renderer import render_recommendations


def main():
    """
    Full CLI flow:
      1. Collect user preferences interactively.
      2. Run the recommendation pipeline (load → filter → prompt → Groq).
      3. Format the LLM output (validate, sort).
      4. Render styled results in the terminal.
    """
    try:
        prefs = collect_preferences()
        raw = recommend(prefs)
        results = format_recommendations(raw)
        render_recommendations(results, prefs)

    except AssertionError as e:
        print(f"\n[Input Error] {e}")
    except RuntimeError as e:
        print(f"\n[API Error] {e}")
    except ValueError as e:
        print(f"\n[Parse Error] {e}")
    except KeyboardInterrupt:
        print("\n\nExiting. Goodbye! 👋")


if __name__ == "__main__":
    main()
