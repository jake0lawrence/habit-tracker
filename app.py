from flask import Flask, render_template, request, redirect
import json, os, datetime, csv
from pathlib import Path
from io import StringIO
from config import DevConfig, ProdConfig
import storage
import openai

app = Flask(__name__)
app.config.from_object(DevConfig)

# Application mode: 'prod', 'dev', or 'test'.
APP_MODE = os.getenv("APP_MODE", "prod")
app.config["APP_MODE"] = APP_MODE
app.config["PWA_ENABLED"] = APP_MODE == "prod"

DATA_FILE = Path.home() / ".habit_log.json"
CONFIG_FILE = Path.home() / ".habit_config.json"
JOURNAL_FILE = Path("journal.md")
HABITS = {
    "med": "Meditation",
    "grat": "Gratitude",
    "yoga": "Yoga",
    "cardio": "Cardio",
    "weights": "Weights",
    "read": "Read",
}


def load_data():
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE) as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def get_week_range():
    today = datetime.date.today()
    start = today - datetime.timedelta(days=today.weekday())
    return [start + datetime.timedelta(days=i) for i in range(7)]


def calculate_habit_stats(data, week):
    stats = {}
    config = load_config()
    for key, info in config.items():
        label = info["label"]
        streak = 0
        total_duration = 0
        count = 0
        streak_broken = False

        for day in reversed(week):
            entry = data.get(str(day), {}).get(key)
            if isinstance(entry, dict) and entry.get("duration"):
                duration = entry["duration"]
                total_duration += duration
                count += 1
                if not streak_broken:
                    streak += 1
            else:
                streak_broken = True

        avg = round(total_duration / count, 1) if count else 0
        stats[key] = {"label": label, "streak": streak, "avg_duration": avg}
    return stats


def calculate_mood_stats(data):
    """Return mood statistics and time series from saved data."""
    today = datetime.date.today()
    entries = []
    for date_str, info in data.items():
        mood = info.get("mood")
        if isinstance(mood, int):
            try:
                date = datetime.date.fromisoformat(date_str)
            except ValueError:
                continue
            entries.append((date, mood))
    entries.sort(key=lambda x: x[0])

    scores = [score for _, score in entries]

    def avg(seq):
        return round(sum(seq) / len(seq), 1) if seq else 0

    week_start = today - datetime.timedelta(days=6)
    month_start = today - datetime.timedelta(days=29)
    weekly_scores = [s for d, s in entries if d >= week_start]
    month_scores = [s for d, s in entries if d >= month_start]

    series = [{"date": d.isoformat(), "score": s} for d, s in entries]

    return {
        "weekly_avg": avg(weekly_scores),
        "30d_avg": avg(month_scores),
        "overall_avg": avg(scores),
        "series": series,
    }


def load_config():
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE) as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {
        key: {"label": label, "default_duration": 15}
        for key, label in HABITS.items()
    }


def save_config(cfg):
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f, indent=2)


def generate_journal_prompt(data):
    today = datetime.date.today()
    last_7 = sorted(
        [(d, entry.get("mood")) for d, entry in data.items() if "mood" in entry]
    )[-7:]

    avg_mood = (
        round(sum(score for _, score in last_7) / len(last_7), 1) if last_7 else "N/A"
    )

    recent_notes = [
        f"{d}: {entry.get(h, {}).get('note')}"
        for d, entry in data.items()
        for h in entry
        if isinstance(entry.get(h), dict) and entry[h].get("note")
    ][-3:]

    summary = f"""
Mood Journal Prompt for {today.strftime('%A, %B %d')}:

- Your 7-day average mood is {avg_mood}/5.
- Recent notes:
{chr(10).join(f'- {note}' for note in recent_notes)}

Reflect on:
- What impacted your best days?
- What would help you reset for tomorrow?
"""
    return summary.strip()


def enrich_prompt_with_ai(prompt):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return prompt
    openai.api_key = api_key
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a thoughtful self-reflection assistant."},
                {"role": "user", "content": prompt + "\nPlease expand this into a personal reflection prompt."},
            ],
        )
        return completion.choices[0].message["content"].strip()
    except Exception:
        return prompt


def get_storage_backend():
    """Return the configured storage backend."""
    return storage.get_backend(json_path=str(DATA_FILE))


@app.route("/")
def index():
    debug_mode = request.args.get("debug") == "true"
    today = datetime.date.today()
    week = get_week_range()
    backend = get_storage_backend()
    data = backend.get_range(str(week[0]), str(week[-1]))
    all_data = backend.load_all()
    mood = data.get(str(today), {}).get("mood")
    mood_stats = calculate_mood_stats(all_data)
    config = load_config()
    stats = calculate_habit_stats(data, week)
    return render_template(
        "index.html",
        habits=config,
        data=data,
        today=str(today),
        mood=mood,
        mood_stats=mood_stats,
        week=week,
        stats=stats,
        debug=debug_mode,
    )


@app.route("/log/<habit>", methods=["POST"])
def log_habit(habit):
    backend = get_storage_backend()
    target_date = request.form.get("date", str(datetime.date.today()))
    if request.args.get("delete") == "1":
        backend.delete_habit(target_date, habit)
    else:
        backend.save_habit(
            target_date,
            habit,
            int(request.form.get("duration", 1)),
            request.form.get("note", ""),
        )

    week = get_week_range()
    data = backend.get_range(str(week[0]), str(week[-1]))
    config = load_config()
    grid = render_template(
        "_habit_row.html",
        habits=config,
        data=data,
        week=week,
        today=str(datetime.date.today()),
    )
    return f'<div id="habit-grid">{grid}</div>'


@app.route("/mood", methods=["POST"])
def log_mood():
    score = int(request.form["score"])
    backend = get_storage_backend()
    today = str(datetime.date.today())
    backend.save_mood(today, score)
    return {"status": "ok", "score": score}


@app.route("/export")
def export_csv():
    backend = get_storage_backend()
    week = get_week_range()
    data = backend.get_range(str(week[0]), str(week[-1]))
    config = load_config()

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["Habit"] + [d.strftime("%Y-%m-%d") for d in week])

    for key, info in config.items():
        row = [info["label"]]
        for day in week:
            val = data.get(str(day), {}).get(key)
            row.append("✓" if val else "")
        writer.writerow(row)

    output.seek(0)
    return app.response_class(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=habit_week.csv"},
    )


@app.route("/analytics")
def analytics():
    debug_mode = request.args.get("debug") == "true"
    backend = get_storage_backend()
    week = get_week_range()
    data = backend.get_range(str(week[0]), str(week[-1]))
    config = load_config()
    all_data = backend.load_all()
    mood_series = [
        {"date": d, "score": entry["mood"]}
        for d, entry in all_data.items()
        if "mood" in entry
    ]
    mood_series.sort(key=lambda x: x["date"])

    chart_data = []
    for key, info in config.items():
        bars = []
        for day in week:
            entry = data.get(str(day), {}).get(key)
            val = entry.get("duration", 0) if isinstance(entry, dict) else 0
            bars.append(val)
        chart_data.append({"label": info["label"], "data": bars})

    labels = [d.strftime("%a") for d in week]
    return render_template(
        "analytics.html",
        chart_data=chart_data,
        labels=labels,
        mood_series=mood_series,
        debug=debug_mode,
    )


@app.route("/journal")
def journal():
    data = load_data()
    base_prompt = generate_journal_prompt(data)
    ai_prompt = enrich_prompt_with_ai(base_prompt)
    return render_template("journal.html", prompt=ai_prompt)


@app.route("/journal-entry", methods=["POST"])
def save_journal():
    entry = request.form["entry"]
    today = datetime.date.today().isoformat()
    with open(JOURNAL_FILE, "a") as f:
        f.write(f"\n## {today}\n{entry.strip()}\n")
    return redirect("/journal")


@app.route("/settings", methods=["GET", "POST"])
def settings():
    config = load_config()
    if request.method == "POST":
        for key in HABITS.keys():
            config[key]["label"] = request.form.get(
                f"label_{key}", config[key]["label"]
            )
            config[key]["default_duration"] = int(
                request.form.get(f"duration_{key}", config[key]["default_duration"])
            )
        app.config["PWA_ENABLED"] = request.form.get("pwa_enabled") == "on"
        save_config(config)
        return render_template(
            "settings.html", config=config, message="✅ Settings saved."
        )
    return render_template("settings.html", config=config, message=None)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run the Flask web UI")
    parser.add_argument(
        "--mode",
        choices=["prod", "dev", "test"],
        default=os.environ.get("APP_MODE", "prod"),
        help="Execution mode; disables PWA unless 'prod'"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable Flask debug mode (overrides $DEBUG)"
    )
    args = parser.parse_args()

    if args.mode == "prod":
        app.config.from_object(ProdConfig)

    env_debug = os.getenv("DEBUG", "").lower() in {"1", "true", "yes"}
    debug = args.debug or env_debug or app.config.get("DEBUG", False)

    app.config["APP_MODE"] = args.mode
    app.config["PWA_ENABLED"] = args.mode == "prod"

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=debug)
