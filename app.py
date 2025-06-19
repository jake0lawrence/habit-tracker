from flask import Flask, render_template, request
import json, os, datetime, csv
from pathlib import Path
from io import StringIO

app = Flask(__name__)

DATA_FILE = Path.home() / ".habit_log.json"
CONFIG_FILE = Path.home() / ".habit_config.json"
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


@app.route("/")
def index():
    today = datetime.date.today()
    week = get_week_range()
    data = load_data()
    mood = data.get(str(today), {}).get("mood")
    config = load_config()
    stats = calculate_habit_stats(data, week)
    return render_template(
        "index.html",
        habits=config,
        data=data,
        today=str(today),
        mood=mood,
        week=week,
        stats=stats,
    )


@app.route("/log/<habit>", methods=["POST"])
def log_habit(habit):
    data = load_data()
    today = str(datetime.date.today())
    data.setdefault(today, {})[habit] = {
        "duration": int(request.form.get("duration", 1)),
        "note": request.form.get("note", ""),
    }
    save_data(data)
    return ("", 204)


@app.route("/mood", methods=["POST"])
def log_mood():
    score = int(request.form["score"])
    data = load_data()
    today = str(datetime.date.today())
    data.setdefault(today, {})["mood"] = score
    save_data(data)
    return ("", 204)


@app.route("/export")
def export_csv():
    data = load_data()
    week = get_week_range()
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
    week = get_week_range()
    data = load_data()
    config = load_config()

    chart_data = []
    for key, info in config.items():
        bars = []
        for day in week:
            entry = data.get(str(day), {}).get(key)
            val = entry.get("duration", 0) if isinstance(entry, dict) else 0
            bars.append(val)
        chart_data.append({"label": info["label"], "data": bars})

    labels = [d.strftime("%a") for d in week]
    return render_template("analytics.html", chart_data=chart_data, labels=labels)


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
        save_config(config)
        return render_template(
            "settings.html", config=config, message="✅ Settings saved."
        )
    return render_template("settings.html", config=config, message=None)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run the Flask web UI")
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable Flask debug mode (overrides $DEBUG)",
    )
    args = parser.parse_args()

    env_debug = os.getenv("DEBUG", "").lower() in {"1", "true", "yes"}
    debug = args.debug or env_debug
    app.run(debug=debug)
