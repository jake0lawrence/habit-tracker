#!/usr/bin/env python
"""
habit.py — CLI habit & mood tracker
Run `python habit.py --help` to see all commands.
"""

import json
import os
import datetime
import typer
from rich.console import Console
from rich.table import Table

# Initialize Typer app
app = typer.Typer()

# File location for habit data
DATA_FILE = os.path.expanduser("~/.habit_log.json")

# Define trackable habits
HABITS = {
    "med": "Meditation",
    "grat": "Gratitude",
    "yoga": "Yoga",
    "cardio": "Cardio",
    "weights": "Weights",
    "read": "Read"
}


# Load habit data from file
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE) as f:
            return json.load(f)
    return {}


# Save habit data to file
def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)


@app.command()
def log(habit: str, minutes: int = 1):
    """
    Log a habit with optional minutes (default: 1).
    Example: python habit.py log med 5
    """
    if habit not in HABITS:
        typer.echo(f"❌ Unknown habit key: {habit}")
        typer.echo(f"➡️ Valid keys: {', '.join(HABITS)}")
        raise typer.Exit()

    data = load_data()
    today = str(datetime.date.today())
    data.setdefault(today, {})[habit] = minutes
    save_data(data)

    typer.echo(f"✅ Logged {HABITS[habit]} for {minutes} minute(s).")


@app.command()
def mood(score: int = typer.Argument(..., min=1, max=5)):
    """
    Log today's mood on a scale from 1 to 5.
    Example: python habit.py mood 4
    """
    data = load_data()
    today = str(datetime.date.today())
    data.setdefault(today, {})["mood"] = score
    save_data(data)

    typer.echo(f"🧠 Mood logged as {score}/5 for today.")


@app.command()
def show():
    """
    Show this week's habit grid with checkmarks.
    Example: python habit.py show
    """
    data = load_data()
    today = datetime.date.today()
    monday = today - datetime.timedelta(days=today.weekday())
    days = [monday + datetime.timedelta(days=i) for i in range(7)]

    table = Table(title="🗓️ Weekly Habit Tracker")
    table.add_column("Habit", style="bold magenta")

    for day in days:
        table.add_column(day.strftime("%a"), justify="center")

    for key, name in HABITS.items():
        row = [name]
        for day in days:
            entry = data.get(str(day), {}).get(key)
            row.append("🟩" if entry else "⬜")
        table.add_row(*row)

    console = Console()
    console.print(table)


# Run the CLI if executed directly
if __name__ == "__main__":
    app()
