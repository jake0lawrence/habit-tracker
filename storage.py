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

    def load_all(self, user_id=None):
        return self._load()

    def save_habit(self, date, habit, duration, note="", user_id=None):
        data = self._load()
        data.setdefault(date, {})[habit] = {"duration": duration, "note": note}
        self._save(data)

    def delete_habit(self, date, habit, user_id=None):
        data = self._load()
        data.get(date, {}).pop(habit, None)
        self._save(data)

    def save_mood(self, date, score, user_id=None):
        data = self._load()
        data.setdefault(date, {})["mood"] = score
        self._save(data)

    def get_range(self, start_date, end_date, user_id=None):
        all_data = self._load()
        start = datetime.date.fromisoformat(start_date)
        end = datetime.date.fromisoformat(end_date)
        out = {}
        cur = start
        while cur <= end:
            out[str(cur)] = all_data.get(str(cur), {})
            cur += datetime.timedelta(days=1)
        return out

    def get_mood_series(self, user_id=None):
        data = self._load()
        series = []
        for date, info in data.items():
            if isinstance(info, dict) and "mood" in info:
                series.append({"date": date, "score": info["mood"]})
        series.sort(key=lambda x: x["date"])
        return series

    # --- account helpers -------------------------------------------------
    def create_user(self, email, password_hash):
        """Unsupported helper for parity with DB backends."""
        raise NotImplementedError(
            "JSON backend does not support user accounts. "
            "Run with APP_MODE=prod for SQLite/Postgres."
        )

    def get_user(self, user_id):
        """Unsupported helper for parity with DB backends."""
        raise NotImplementedError(
            "JSON backend does not support user accounts. "
            "Run with APP_MODE=prod for SQLite/Postgres."
        )

    def get_user_by_email(self, email):
        """Unsupported helper for parity with DB backends."""
        raise NotImplementedError(
            "JSON backend does not support user accounts. "
            "Run with APP_MODE=prod for SQLite/Postgres."
        )


class SQLiteBackend:
    def __init__(self, db_path="data/habits.db"):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._init_schema()

    def _init_schema(self):
        with closing(self.conn.cursor()) as cur:
            cur.executescript(
                """
                CREATE TABLE IF NOT EXISTS users (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  email TEXT UNIQUE NOT NULL,
                  password_hash TEXT NOT NULL,
                  created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS habit_log (
                  user_id INTEGER NOT NULL,
                  date TEXT,
                  habit TEXT,
                  duration INT,
                  note TEXT,
                  PRIMARY KEY(user_id, date, habit),
                  FOREIGN KEY(user_id) REFERENCES users(id)
                );
                CREATE TABLE IF NOT EXISTS mood_log (
                  user_id INTEGER NOT NULL,
                  date TEXT,
                  score INT,
                  PRIMARY KEY(user_id, date),
                  FOREIGN KEY(user_id) REFERENCES users(id)
                );
                """
            )

            # --- migration: add user_id columns if missing ---
            cur.execute("PRAGMA table_info(habit_log)")
            cols = [r[1] for r in cur.fetchall()]
            if "user_id" not in cols:
                cur.execute(
                    "ALTER TABLE habit_log ADD COLUMN user_id INTEGER REFERENCES users(id)"
                )
                cur.execute(
                    "UPDATE habit_log SET user_id = 1 WHERE user_id IS NULL"
                )

            cur.execute("PRAGMA table_info(mood_log)")
            cols = [r[1] for r in cur.fetchall()]
            if "user_id" not in cols:
                cur.execute(
                    "ALTER TABLE mood_log ADD COLUMN user_id INTEGER REFERENCES users(id)"
                )
                cur.execute("UPDATE mood_log SET user_id = 1 WHERE user_id IS NULL")

            self.conn.commit()

    def load_all(self, user_id=1):
        data = {}
        with closing(self.conn.cursor()) as cur:
            cur.execute(
                "SELECT date, habit, duration, note FROM habit_log WHERE user_id=?",
                (user_id,),
            )
            for d, h, dur, note in cur.fetchall():
                data.setdefault(d, {})[h] = {"duration": dur, "note": note}
            cur.execute(
                "SELECT date, score FROM mood_log WHERE user_id=?", (user_id,)
            )
            for d, s in cur.fetchall():
                data.setdefault(d, {})["mood"] = s
        return data

    def save_habit(self, date, habit, duration, note="", user_id=1):
        with closing(self.conn.cursor()) as cur:
            cur.execute(
                """
                INSERT INTO habit_log (user_id, date, habit, duration, note)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(user_id, date, habit)
                DO UPDATE SET duration=excluded.duration, note=excluded.note
                """,
                (user_id, date, habit, duration, note),
            )
            self.conn.commit()

    def delete_habit(self, date, habit, user_id=1):
        with closing(self.conn.cursor()) as cur:
            cur.execute(
                "DELETE FROM habit_log WHERE user_id = ? AND date = ? AND habit = ?",
                (user_id, date, habit),
            )
            self.conn.commit()

    def save_mood(self, date, score, user_id=1):
        with closing(self.conn.cursor()) as cur:
            cur.execute(
                """
                INSERT INTO mood_log (user_id, date, score)
                VALUES (?, ?, ?)
                ON CONFLICT(user_id, date) DO UPDATE SET score=excluded.score
                """,
                (user_id, date, score),
            )
            self.conn.commit()

    def get_range(self, start_date, end_date, user_id=1):
        data = {}
        with closing(self.conn.cursor()) as cur:
            cur.execute(
                "SELECT date, habit, duration, note FROM habit_log WHERE user_id=? AND date BETWEEN ? AND ?",
                (user_id, start_date, end_date),
            )
            for d, h, dur, note in cur.fetchall():
                data.setdefault(d, {})[h] = {"duration": dur, "note": note}
            cur.execute(
                "SELECT date, score FROM mood_log WHERE user_id=? AND date BETWEEN ? AND ?",
                (user_id, start_date, end_date),
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

    def get_mood_series(self, user_id=1):
        with closing(self.conn.cursor()) as cur:
            cur.execute(
                "SELECT date, score FROM mood_log WHERE user_id=? ORDER BY date",
                (user_id,),
            )
            return [{"date": d, "score": s} for d, s in cur.fetchall()]

    # ----- User management -----
    def create_user(self, email, password_hash):
        with closing(self.conn.cursor()) as cur:
            cur.execute(
                "INSERT INTO users (email, password_hash) VALUES (?, ?)",
                (email, password_hash),
            )
            self.conn.commit()
            return cur.lastrowid

    def get_user(self, user_id):
        with closing(self.conn.cursor()) as cur:
            cur.execute(
                "SELECT id, email, password_hash FROM users WHERE id=?",
                (user_id,),
            )
            row = cur.fetchone()
            if row:
                return {"id": row[0], "email": row[1], "password_hash": row[2]}
            return None

    def get_user_by_email(self, email):
        with closing(self.conn.cursor()) as cur:
            cur.execute(
                "SELECT id, email, password_hash FROM users WHERE email=?",
                (email,),
            )
            row = cur.fetchone()
            if row:
                return {"id": row[0], "email": row[1], "password_hash": row[2]}
            return None


class PostgresBackend(SQLiteBackend):
    def __init__(self, url):
        import psycopg2

        self.conn = psycopg2.connect(url)
        self._init_schema()

    def _init_schema(self):
        with self.conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                  id SERIAL PRIMARY KEY,
                  email TEXT UNIQUE NOT NULL,
                  password_hash TEXT NOT NULL,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS habit_log (
                  user_id INTEGER NOT NULL REFERENCES users(id),
                  date TEXT,
                  habit TEXT,
                  duration INT,
                  note TEXT,
                  PRIMARY KEY(user_id, date, habit)
                );
                CREATE TABLE IF NOT EXISTS mood_log (
                  user_id INTEGER NOT NULL REFERENCES users(id),
                  date TEXT,
                  score INT,
                  PRIMARY KEY(user_id, date)
                );
                """
            )

            # --- migration: add user_id columns if missing ---
            cur.execute(
                "SELECT column_name FROM information_schema.columns WHERE table_name='habit_log'"
            )
            cols = {r[0] for r in cur.fetchall()}
            if "user_id" not in cols:
                cur.execute(
                    "ALTER TABLE habit_log ADD COLUMN user_id INTEGER REFERENCES users(id)"
                )
                cur.execute(
                    "UPDATE habit_log SET user_id = 1 WHERE user_id IS NULL"
                )

            cur.execute(
                "SELECT column_name FROM information_schema.columns WHERE table_name='mood_log'"
            )
            cols = {r[0] for r in cur.fetchall()}
            if "user_id" not in cols:
                cur.execute(
                    "ALTER TABLE mood_log ADD COLUMN user_id INTEGER REFERENCES users(id)"
                )
                cur.execute(
                    "UPDATE mood_log SET user_id = 1 WHERE user_id IS NULL"
                )

            self.conn.commit()

    # Psycopg2 uses %s placeholders
    def save_habit(self, date, habit, duration, note="", user_id=1):
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO habit_log (user_id, date, habit, duration, note)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT(user_id, date, habit)
                DO UPDATE SET duration=EXCLUDED.duration, note=EXCLUDED.note
                """,
                (user_id, date, habit, duration, note),
            )
            self.conn.commit()

    def delete_habit(self, date, habit, user_id=1):
        with self.conn.cursor() as cur:
            cur.execute(
                "DELETE FROM habit_log WHERE user_id = %s AND date = %s AND habit = %s",
                (user_id, date, habit),
            )
            self.conn.commit()

    def save_mood(self, date, score, user_id=1):
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO mood_log (user_id, date, score)
                VALUES (%s, %s, %s)
                ON CONFLICT(user_id, date) DO UPDATE SET score=EXCLUDED.score
                """,
                (user_id, date, score),
            )
            self.conn.commit()

    def get_range(self, start_date, end_date, user_id=1):
        data = {}
        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT date, habit, duration, note FROM habit_log WHERE user_id=%s AND date BETWEEN %s AND %s",
                (user_id, start_date, end_date),
            )
            for d, h, dur, note in cur.fetchall():
                data.setdefault(d, {})[h] = {"duration": dur, "note": note}
            cur.execute(
                "SELECT date, score FROM mood_log WHERE user_id=%s AND date BETWEEN %s AND %s",
                (user_id, start_date, end_date),
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

    def get_mood_series(self, user_id=1):
        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT date, score FROM mood_log WHERE user_id=%s ORDER BY date",
                (user_id,),
            )
            return [{"date": d, "score": s} for d, s in cur.fetchall()]

    # ----- User management -----
    def create_user(self, email, password_hash):
        with self.conn.cursor() as cur:
            cur.execute(
                "INSERT INTO users (email, password_hash) VALUES (%s, %s) RETURNING id",
                (email, password_hash),
            )
            user_id = cur.fetchone()[0]
            self.conn.commit()
            return user_id

    def get_user(self, user_id):
        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT id, email, password_hash FROM users WHERE id=%s",
                (user_id,),
            )
            row = cur.fetchone()
            if row:
                return {"id": row[0], "email": row[1], "password_hash": row[2]}
            return None

    def get_user_by_email(self, email):
        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT id, email, password_hash FROM users WHERE email=%s",
                (email,),
            )
            row = cur.fetchone()
            if row:
                return {"id": row[0], "email": row[1], "password_hash": row[2]}
            return None


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
