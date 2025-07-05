import datetime
import app


def test_log_save(tmp_path):
    orig_data = app.DATA_FILE
    orig_config = app.CONFIG_FILE
    orig_login_disabled = app.app.config.get("LOGIN_DISABLED")
    app.DATA_FILE = tmp_path / "data.json"
    app.CONFIG_FILE = tmp_path / "config.json"
    app.app.config["LOGIN_DISABLED"] = True
    client = app.app.test_client()
    try:
        rv = client.post('/log', data={
            'habit': 'Meditation',
            'duration': 5,
            'note': 'unit test',
            'date': '2030-01-01'
        })
        assert rv.status_code == 200
        assert b'Meditation' in rv.data
    finally:
        app.DATA_FILE = orig_data
        app.CONFIG_FILE = orig_config
        app.app.config["LOGIN_DISABLED"] = orig_login_disabled


def test_log_missing_duration(tmp_path):
    orig_data = app.DATA_FILE
    orig_config = app.CONFIG_FILE
    orig_login_disabled = app.app.config.get("LOGIN_DISABLED")
    app.DATA_FILE = tmp_path / "data.json"
    app.CONFIG_FILE = tmp_path / "config.json"
    app.app.config["LOGIN_DISABLED"] = True
    client = app.app.test_client()
    try:
        rv = client.post(
            '/log',
            data={'habit': 'Meditation', 'note': 'fail', 'date': '2030-01-01'},
        )
        assert rv.status_code == 400
    finally:
        app.DATA_FILE = orig_data
        app.CONFIG_FILE = orig_config
        app.app.config["LOGIN_DISABLED"] = orig_login_disabled


def test_log_invalid_duration(tmp_path):
    orig_data = app.DATA_FILE
    orig_config = app.CONFIG_FILE
    orig_login_disabled = app.app.config.get("LOGIN_DISABLED")
    app.DATA_FILE = tmp_path / "data.json"
    app.CONFIG_FILE = tmp_path / "config.json"
    app.app.config["LOGIN_DISABLED"] = True
    client = app.app.test_client()
    try:
        rv = client.post(
            '/log',
            data={
                'habit': 'Meditation',
                'duration': 'abc',
                'date': '2030-01-01',
            },
        )
        assert rv.status_code == 400
    finally:
        app.DATA_FILE = orig_data
        app.CONFIG_FILE = orig_config
        app.app.config["LOGIN_DISABLED"] = orig_login_disabled


def test_log_update_entry(tmp_path):
    orig_data = app.DATA_FILE
    orig_config = app.CONFIG_FILE
    orig_login_disabled = app.app.config.get("LOGIN_DISABLED")
    app.DATA_FILE = tmp_path / "data.json"
    app.CONFIG_FILE = tmp_path / "config.json"
    app.app.config["LOGIN_DISABLED"] = True
    client = app.app.test_client()
    try:
        date = "2030-01-02"
        backend = app.get_storage_backend()
        backend.save_habit(date, "Meditation", 5, "old")

        rv = client.post(
            "/log",
            data={
                "habit": "Meditation",
                "duration": "10",
                "note": "updated",
                "date": date,
                "entry_id": f"{date}_Meditation",
            },
        )
        assert rv.status_code == 200
        data = backend.load_all()
        assert data[date]["Meditation"]["duration"] == 10
        assert data[date]["Meditation"]["note"] == "updated"
    finally:
        app.DATA_FILE = orig_data
        app.CONFIG_FILE = orig_config
        app.app.config["LOGIN_DISABLED"] = orig_login_disabled
