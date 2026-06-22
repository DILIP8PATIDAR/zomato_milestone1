# output/renderer.py — CLI Renderer (Phase 5.5)
# Uses the `rich` library to display styled restaurant recommendation cards
# in the terminal.

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.rule import Rule

console = Console()


def render_recommendations(recommendations: list[dict], prefs) -> None:
    """
    Render a list of recommendation dicts as styled Rich panels in the terminal.

    Args:
        recommendations: Cleaned, sorted list of recommendation dicts.
        prefs:           UserPreference object (used for the summary header).
    """
    console.print()
    console.print(Rule("[bold red]🍽  Zomato AI Restaurant Recommender[/bold red]"))
    console.print(
        f"[dim]Location:[/dim] [cyan]{prefs.location}[/cyan]  "
        f"[dim]Budget:[/dim] [cyan]{prefs.budget}[/cyan]  "
        f"[dim]Cuisine:[/dim] [cyan]{prefs.cuisine or 'Any'}[/cyan]  "
        f"[dim]Min Rating:[/dim] [cyan]{prefs.min_rating or 'Any'}[/cyan]"
    )
    console.print()

    if not recommendations:
        console.print(
            "[bold red]⚠  No recommendations found.[/bold red]\n"
            "[dim]Try relaxing your preferences — e.g., remove the cuisine filter "
            "or lower the minimum rating.[/dim]"
        )
        return

    console.print(f"[bold green]Top {len(recommendations)} Recommendation(s):[/bold green]\n")

    for rec in recommendations:
        # Star rendering
        full_stars = round(float(rec["rating"]))
        stars = "★" * full_stars + "☆" * (5 - full_stars)

        # Low-vote warning (Phase 5.7)
        low_vote_warning = ""
        votes = rec.get("votes", None)
        if votes is not None:
            try:
                if int(votes) < 50:
                    low_vote_warning = "\n[yellow]⚠  Limited reviews — fewer than 50 votes[/yellow]"
            except (ValueError, TypeError):
                pass

        title = Text()
        title.append(f"#{rec['rank']}  ", style="bold red")
        title.append(rec["name"], style="bold white")

        body = (
            f"[dim]Cuisine:[/dim]    [white]{rec['cuisine']}[/white]\n"
            f"[dim]Rating:[/dim]     [yellow]{stars}[/yellow]  [bold]{rec['rating']}[/bold]\n"
            f"[dim]Est. Cost:[/dim]  [green]{rec['estimated_cost']}[/green]\n\n"
            f"[italic]{rec['explanation']}[/italic]"
            f"{low_vote_warning}"
        )

        console.print(Panel(body, title=title, border_style="cyan", padding=(1, 2)))

    console.print(Rule("[dim]End of Recommendations[/dim]"))
    console.print()
