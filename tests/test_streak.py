import json
import datetime
import app


def last_seven_days(end=None):
    if end is None:
        end = datetime.date.today()
    return [end - datetime.timedelta(days=i) for i in range(6, -1, -1)]


def write_data(path, data):
    path.write_text(json.dumps(data))


def test_streak_three_day_run(tmp_path):
    orig_data = app.DATA_FILE
    orig_config = app.CONFIG_FILE
    app.DATA_FILE = tmp_path / "data.json"
    app.CONFIG_FILE = tmp_path / "config.json"
    try:
        week = last_seven_days()
        data = {}
        for i in range(3):
            day = week[-1 - i]
            data.setdefault(str(day), {})["med"] = {"duration": 10}
        write_data(app.DATA_FILE, data)
        loaded = app.load_data()
        stats = app.calculate_habit_stats(loaded, week)
        assert stats["med"]["streak"] == 3
    finally:
        app.DATA_FILE = orig_data
        app.CONFIG_FILE = orig_config


def test_streak_resets_after_gap(tmp_path):
    orig_data = app.DATA_FILE
    orig_config = app.CONFIG_FILE
    app.DATA_FILE = tmp_path / "data.json"
    app.CONFIG_FILE = tmp_path / "config.json"
    try:
        week = last_seven_days()
        data = {}
        data[str(week[-1])] = {"med": {"duration": 5}}
        data[str(week[-3])] = {"med": {"duration": 5}}
        write_data(app.DATA_FILE, data)
        loaded = app.load_data()
        stats = app.calculate_habit_stats(loaded, week)
        assert stats["med"]["streak"] == 1
    finally:
        app.DATA_FILE = orig_data
        app.CONFIG_FILE = orig_config


def test_streak_none_when_no_recent_entry(tmp_path):
    orig_data = app.DATA_FILE
    orig_config = app.CONFIG_FILE
    app.DATA_FILE = tmp_path / "data.json"
    app.CONFIG_FILE = tmp_path / "config.json"
    try:
        week = last_seven_days()
        data = {str(week[-4]): {"med": {"duration": 20}}}
        write_data(app.DATA_FILE, data)
        loaded = app.load_data()
        stats = app.calculate_habit_stats(loaded, week)
        assert stats["med"]["streak"] == 0
    finally:
        app.DATA_FILE = orig_data
        app.CONFIG_FILE = orig_config


def test_streak_full_week(tmp_path):
    orig_data = app.DATA_FILE
    orig_config = app.CONFIG_FILE
    app.DATA_FILE = tmp_path / "data.json"
    app.CONFIG_FILE = tmp_path / "config.json"
    try:
        week = last_seven_days()
        data = {
            str(day): {"med": {"duration": 5}}
            for day in week
        }
        write_data(app.DATA_FILE, data)
        loaded = app.load_data()
        stats = app.calculate_habit_stats(loaded, week)
        assert stats["med"]["streak"] == 7
    finally:
        app.DATA_FILE = orig_data
        app.CONFIG_FILE = orig_config
