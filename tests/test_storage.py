import logging

import storage
from storage import SQLiteBackend, get_backend


def test_sqlite_habit_cycle(tmp_path):
    db = SQLiteBackend(db_path=tmp_path / "t.db")
    db.save_habit("2025-06-19", "med", 10, "note")
    data = db.get_range("2025-06-19", "2025-06-19")
    row = data["2025-06-19"]["med"]
    assert row["duration"] == 10
    assert row["note"] == "note"


def test_sqlite_mood_cycle(tmp_path):
    db = SQLiteBackend(db_path=tmp_path / "m.db")
    db.save_mood("2025-06-19", 4)
    series = db.get_mood_series()
    assert series[-1] == {"date": "2025-06-19", "score": 4}


def test_get_backend_postgres_failure(monkeypatch, caplog):
    """Fallback to SQLite if Postgres connection errors."""
    monkeypatch.setenv("DATABASE_URL", "postgres://bad")

    def fail_backend(url):
        raise Exception("connection failed")

    monkeypatch.setattr(storage, "PostgresBackend", fail_backend)

    if hasattr(get_backend, "_cache"):
        get_backend._cache.clear()

    caplog.set_level(logging.WARNING)
    backend = get_backend()
    assert isinstance(backend, SQLiteBackend)
    assert "connection failed" in caplog.text
