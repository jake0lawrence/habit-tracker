import os
import json
import sqlite3
import datetime
import logging
from pathlib import Path
from contextlib import closing


class JSONBackend:
    """Simple JSON file backend compatible with existing CLI data."""

    FILE = Path.home() / ".habit_log.json"

    def __init__(self, file_path=None):
        self.file = Path(file_path) if file_path else self.FILE

    def _load(self):
        if self.file.exists():
            try:
                with open(self.file) as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {}
        return {}

    def _save(self, data):
        with open(self.file, "w") as f:
            json.dump(data, f, indent=2)

    def load_all(self):
        return self._load()

    def save_habit(self, date, habit, duration, note=""):
        data = self._load()
        data.setdefault(date, {})[habit] = {"duration": duration, "note": note}
        self._save(data)

    def delete_habit(self, date, habit):
        data = self._load()
        data.get(date, {}).pop(habit, None)
        self._save(data)

    def save_mood(self, date, score):
        data = self._load()
        data.setdefault(date, {})["mood"] = score
        self._save(data)

    def get_range(self, start_date, end_date):
        all_data = self._load()
        start = datetime.date.fromisoformat(start_date)
        end = datetime.date.fromisoformat(end_date)
        out = {}
        cur = start
        while cur <= end:
            out[str(cur)] = all_data.get(str(cur), {})
            cur += datetime.timedelta(days=1)
        return out

    def get_mood_series(self):
        data = self._load()
        series = []
        for date, info in data.items():
            if isinstance(info, dict) and "mood" in info:
                series.append({"date": date, "score": info["mood"]})
        series.sort(key=lambda x: x["date"])
        return series


class SQLiteBackend:
    def __init__(self, db_path="data/habits.db"):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._init_schema()

    def _init_schema(self):
        with closing(self.conn.cursor()) as cur:
            cur.executescript(
                """
                CREATE TABLE IF NOT EXISTS habit_log (
                  date TEXT,
                  habit TEXT,
                  duration INT,
                  note TEXT,
                  PRIMARY KEY(date, habit)
                );
                CREATE TABLE IF NOT EXISTS mood_log (
                  date TEXT PRIMARY KEY,
                  score INT
                );
                """
            )
            self.conn.commit()

    def load_all(self):
        data = {}
        with closing(self.conn.cursor()) as cur:
            cur.execute("SELECT date, habit, duration, note FROM habit_log")
            for d, h, dur, note in cur.fetchall():
                data.setdefault(d, {})[h] = {"duration": dur, "note": note}
            cur.execute("SELECT date, score FROM mood_log")
            for d, s in cur.fetchall():
                data.setdefault(d, {})["mood"] = s
        return data

    def save_habit(self, date, habit, duration, note=""):
        with closing(self.conn.cursor()) as cur:
            cur.execute(
                """
                INSERT INTO habit_log (date, habit, duration, note)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(date, habit)
                DO UPDATE SET duration=excluded.duration, note=excluded.note
                """,
                (date, habit, duration, note),
            )
            self.conn.commit()

    def delete_habit(self, date, habit):
        with closing(self.conn.cursor()) as cur:
            cur.execute(
                "DELETE FROM habit_log WHERE date = ? AND habit = ?",
                (date, habit),
            )
            self.conn.commit()

    def save_mood(self, date, score):
        with closing(self.conn.cursor()) as cur:
            cur.execute(
                """
                INSERT INTO mood_log (date, score)
                VALUES (?, ?)
                ON CONFLICT(date) DO UPDATE SET score=excluded.score
                """,
                (date, score),
            )
            self.conn.commit()

    def get_range(self, start_date, end_date):
        data = {}
        with closing(self.conn.cursor()) as cur:
            cur.execute(
                "SELECT date, habit, duration, note FROM habit_log WHERE date BETWEEN ? AND ?",
                (start_date, end_date),
            )
            for d, h, dur, note in cur.fetchall():
                data.setdefault(d, {})[h] = {"duration": dur, "note": note}
            cur.execute(
                "SELECT date, score FROM mood_log WHERE date BETWEEN ? AND ?",
                (start_date, end_date),
            )
            for d, s in cur.fetchall():
                data.setdefault(d, {})["mood"] = s
        # ensure keys for each date in range
        start = datetime.date.fromisoformat(start_date)
        end = datetime.date.fromisoformat(end_date)
        cur_date = start
        while cur_date <= end:
            data.setdefault(str(cur_date), {})
            cur_date += datetime.timedelta(days=1)
        return data

    def get_mood_series(self):
        with closing(self.conn.cursor()) as cur:
            cur.execute("SELECT date, score FROM mood_log ORDER BY date")
            return [{"date": d, "score": s} for d, s in cur.fetchall()]


class PostgresBackend(SQLiteBackend):
    def __init__(self, url):
        import psycopg2

        self.conn = psycopg2.connect(url)
        self._init_schema()

    def _init_schema(self):
        with self.conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS habit_log (
                  date TEXT,
                  habit TEXT,
                  duration INT,
                  note TEXT,
                  PRIMARY KEY(date, habit)
                );
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS mood_log (
                  date TEXT PRIMARY KEY,
                  score INT
                );
                """
            )
            self.conn.commit()

    # Psycopg2 uses %s placeholders
    def save_habit(self, date, habit, duration, note=""):
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO habit_log (date, habit, duration, note)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT(date, habit)
                DO UPDATE SET duration=EXCLUDED.duration, note=EXCLUDED.note
                """,
                (date, habit, duration, note),
            )
            self.conn.commit()

    def delete_habit(self, date, habit):
        with self.conn.cursor() as cur:
            cur.execute(
                "DELETE FROM habit_log WHERE date = %s AND habit = %s",
                (date, habit),
            )
            self.conn.commit()

    def save_mood(self, date, score):
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO mood_log (date, score)
                VALUES (%s, %s)
                ON CONFLICT(date) DO UPDATE SET score=EXCLUDED.score
                """,
                (date, score),
            )
            self.conn.commit()

    def get_range(self, start_date, end_date):
        data = {}
        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT date, habit, duration, note FROM habit_log WHERE date BETWEEN %s AND %s",
                (start_date, end_date),
            )
            for d, h, dur, note in cur.fetchall():
                data.setdefault(d, {})[h] = {"duration": dur, "note": note}
            cur.execute(
                "SELECT date, score FROM mood_log WHERE date BETWEEN %s AND %s",
                (start_date, end_date),
            )
            for d, s in cur.fetchall():
                data.setdefault(d, {})["mood"] = s
        start = datetime.date.fromisoformat(start_date)
        end = datetime.date.fromisoformat(end_date)
        cur_date = start
        while cur_date <= end:
            data.setdefault(str(cur_date), {})
            cur_date += datetime.timedelta(days=1)
        return data

    def get_mood_series(self):
        with self.conn.cursor() as cur:
            cur.execute("SELECT date, score FROM mood_log ORDER BY date")
            return [{"date": d, "score": s} for d, s in cur.fetchall()]


def get_backend(json_path=None):
    key = (os.getenv("DATABASE_URL"), os.getenv("APP_MODE"), json_path)
    if not hasattr(get_backend, "_cache"):
        get_backend._cache = {}
    if key in get_backend._cache:
        return get_backend._cache[key]

    if os.getenv("DATABASE_URL"):
        try:
            backend = PostgresBackend(os.getenv("DATABASE_URL"))
        except Exception as e:  # pragma: no cover - safety net
            logging.warning("Postgres connection failed: %s", e)
            backend = SQLiteBackend("data/habits.db")
    elif os.getenv("APP_MODE") == "prod":
        backend = SQLiteBackend("data/habits.db")
    else:
        backend = JSONBackend(json_path)

    get_backend._cache[key] = backend
    return backend
