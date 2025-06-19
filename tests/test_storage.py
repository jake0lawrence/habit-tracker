from storage import SQLiteBackend


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
