from flask import Flask, render_template, request, redirect, url_for
import json, os, datetime
from pathlib import Path

app = Flask(__name__)

DATA_FILE = Path.home() / ".habit_log.json"
HABITS = {
    "med": "Meditation",
    "grat": "Gratitude",
    "yoga": "Yoga",
    "cardio": "Cardio",
    "weights": "Weights",
    "read": "Read"
}

# Load/save functions
def load_data():
    if DATA_FILE.exists():
        with open(DATA_FILE) as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

# Routes
@app.route("/")
def index():
    today = str(datetime.date.today())
    data = load_data()
    mood = data.get(today, {}).get("mood")
    return render_template("index.html", habits=HABITS, data=data, today=today, mood=mood)

@app.route("/log/<habit>", methods=["POST"])
def log_habit(habit):
    data = load_data()
    today = str(datetime.date.today())
    data.setdefault(today, {})[habit] = 1
    save_data(data)
    return render_template("_habit_row.html", habits=HABITS, data=data, today=today)

@app.route("/mood", methods=["POST"])
def log_mood():
    score = int(request.form["score"])
    data = load_data()
    today = str(datetime.date.today())
    data.setdefault(today, {})["mood"] = score
    save_data(data)
    return ("", 204)

if __name__ == "__main__":
    app.run(debug=True)
