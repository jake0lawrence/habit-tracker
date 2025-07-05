from flask import Flask, render_template, request, redirect, send_file
import json, os, datetime, csv
from pathlib import Path
from io import StringIO
from config import DevConfig, ProdConfig
import storage
import openai

app = Flask(__name__)


def create_app(mode=None):
    """Configure the global Flask app based on APP_MODE."""
    if mode is None:
        mode = os.getenv("APP_MODE", "prod")
    if mode == "prod":
        app.config.from_object(ProdConfig)
    else:
        app.config.from_object(DevConfig)
    app.config["APP_MODE"] = mode
    app.config["PWA_ENABLED"] = mode == "prod"
    return app


# Apply configuration at import so gunicorn sees the correct settings.
create_app()

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


def calculate_habit_stats(all_data, week):
    """Return streak and average duration per habit."""
    stats = {}
    config = load_config()
    today = datetime.date.today()
    for key, info in config.items():
        label = info["label"]
        total_duration = 0
        count = 0

        # Average duration uses only the provided week subset
        for day in week:
            entry = all_data.get(str(day), {}).get(key)
            if isinstance(entry, dict) and entry.get("duration"):
                total_duration += entry["duration"]
                count += 1

        # Compute streak walking backward from today using all loaded data
        streak = 0
        cur = today
        while True:
            # Skip future dates so they don't break the streak
            entry = all_data.get(str(cur), {}).get(key)
            if isinstance(entry, dict) and entry.get("duration"):
                streak += 1
                cur -= datetime.timedelta(days=1)
            else:
                break

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
    openai.api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("AI_MODEL", "gpt-4")
    if not openai.api_key:
        return prompt
    try:
        completion = openai.ChatCompletion.create(
            model=model,
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
    stats = calculate_habit_stats(all_data, week)
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


@app.post("/log")
def log_habit():
    habit = request.form.get("habit")
    duration_str = request.form.get("duration")
    note = request.form.get("note", "").strip()
    target_date = request.form.get("date")

    if not habit or not target_date:
        return {"error": "Missing habit or date"}, 400

    if duration_str is None or str(duration_str).strip() == "":
        return {"error": "Duration required"}, 400

    try:
        duration = int(duration_str)
    except (TypeError, ValueError):
        return {"error": "Duration must be a number"}, 400

    backend = get_storage_backend()
    if request.args.get("delete") == "1":
        backend.delete_habit(target_date, habit)
    else:
        backend.save_habit(target_date, habit, duration, note)

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
    score_str = request.form.get("score")
    if score_str is None:
        return {"status": "error", "message": "score required"}, 400
    try:
        score = int(score_str)
    except (TypeError, ValueError):
        return {"status": "error", "message": "invalid score"}, 400
    if not 1 <= score <= 5:
        return {"status": "error", "message": "invalid score"}, 400
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


@app.route("/download-journal")
def download_journal():
    format = request.args.get("format", "txt")
    path = JOURNAL_FILE

    if not path.exists():
        return "No journal entries yet.", 404

    if format == "zip":
        from zipfile import ZipFile
        zip_path = Path("journal.zip")
        with ZipFile(zip_path, "w") as zipf:
            zipf.write(path)
        return send_file(zip_path, as_attachment=True, mimetype="application/zip")
    else:
        return send_file(path, as_attachment=True, mimetype="text/plain")


@app.route("/journal-entry", methods=["POST"])
def save_journal():
    entry = request.form["entry"]
    today = datetime.date.today().isoformat()
    with open(JOURNAL_FILE, "a") as f:
        f.write(f"\n## {today}\n{entry.strip()}\n")
    return redirect("/journal")


@app.route("/journal-history")
def journal_history():
    if not JOURNAL_FILE.exists():
        return render_template("journal_history.html", entries=[])

    with open(JOURNAL_FILE, "r") as f:
        lines = f.readlines()

    entries = []
    current = {"date": None, "text": ""}

    for line in lines:
        if line.startswith("## "):
            if current["date"]:
                entries.append(current)
            current = {"date": line.replace("##", "").strip(), "text": ""}
        else:
            current["text"] += line

    if current["date"]:
        entries.append(current)

    return render_template("journal_history.html", entries=entries[::-1])


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

    create_app(args.mode)

    env_debug = os.getenv("DEBUG", "").lower() in {"1", "true", "yes"}
    debug = args.debug or env_debug or app.config.get("DEBUG", False)

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=debug)
