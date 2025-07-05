import datetime
import app


def set_today(monkeypatch, target):
    class FixedDate(datetime.date):
        @classmethod
        def today(cls):
            return target
    monkeypatch.setattr(app.datetime, "date", FixedDate)


def base_config():
    return {"med": {"label": "Meditation"}}


def test_single_day_streak(monkeypatch):
    today = datetime.date(2025, 1, 7)
    set_today(monkeypatch, today)
    monkeypatch.setattr(app, "load_config", base_config)
    week = app.get_week_range()
    data = {str(today): {"med": {"duration": 10}}}
    stats = app.calculate_habit_stats(data, week)
    assert stats["med"]["streak"] == 1
    assert stats["med"]["avg_duration"] == 10


def test_cross_week_streak(monkeypatch):
    today = datetime.date(2025, 1, 7)
    set_today(monkeypatch, today)
    monkeypatch.setattr(app, "load_config", base_config)
    week = app.get_week_range()
    data = {
        "2025-01-05": {"med": {"duration": 5}},
        "2025-01-06": {"med": {"duration": 5}},
        "2025-01-07": {"med": {"duration": 5}},
    }
    stats = app.calculate_habit_stats(data, week)
    assert stats["med"]["streak"] == 3
    assert stats["med"]["avg_duration"] == 5


def test_streak_reset_after_gap(monkeypatch):
    today = datetime.date(2025, 1, 7)
    set_today(monkeypatch, today)
    monkeypatch.setattr(app, "load_config", base_config)
    week = app.get_week_range()
    data = {
        "2025-01-05": {"med": {"duration": 5}},
        "2025-01-07": {"med": {"duration": 5}},
    }
    stats = app.calculate_habit_stats(data, week)
    assert stats["med"]["streak"] == 1
    assert stats["med"]["avg_duration"] == 5
