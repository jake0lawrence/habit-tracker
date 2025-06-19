import json
import datetime
from pathlib import Path

import app as flask_app_module


def make_client(tmp_path):
    orig_data = flask_app_module.DATA_FILE
    orig_config = flask_app_module.CONFIG_FILE
    flask_app_module.DATA_FILE = tmp_path / "data.json"
    flask_app_module.CONFIG_FILE = tmp_path / "config.json"
    client = flask_app_module.app.test_client()
    return client, orig_data, orig_config


def restore(orig_data, orig_config):
    flask_app_module.DATA_FILE = orig_data
    flask_app_module.CONFIG_FILE = orig_config


def read_json(path: Path):
    if path.exists():
        return json.loads(path.read_text())
    return {}


def test_post_log_route(tmp_path):
    client, orig_data, orig_config = make_client(tmp_path)
    try:
        resp = client.post("/log/med", data={"duration": "15", "note": "test"})
        assert resp.status_code == 200
        assert "<table" in resp.get_data(as_text=True)
        data = read_json(flask_app_module.DATA_FILE)
        today = str(datetime.date.today())
        assert data[today]["med"]["duration"] == 15
        assert data[today]["med"]["note"] == "test"
    finally:
        restore(orig_data, orig_config)


def test_post_log_custom_date(tmp_path):
    client, orig_data, orig_config = make_client(tmp_path)
    try:
        custom_date = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
        resp = client.post(
            "/log/med",
            data={"duration": "20", "note": "yesterday", "date": custom_date},
        )
        assert resp.status_code == 200
        data = read_json(flask_app_module.DATA_FILE)
        assert data[custom_date]["med"]["duration"] == 20
        assert data[custom_date]["med"]["note"] == "yesterday"
    finally:
        restore(orig_data, orig_config)


def test_post_mood_route(tmp_path):
    client, orig_data, orig_config = make_client(tmp_path)
    try:
        resp = client.post("/mood", data={"score": "3"})
        assert resp.status_code == 200
        assert resp.is_json
        assert resp.get_json()["score"] == 3
        data = read_json(flask_app_module.DATA_FILE)
        today = str(datetime.date.today())
        assert data[today]["mood"] == 3
    finally:
        restore(orig_data, orig_config)


def test_homepage(tmp_path):
    client, orig_data, orig_config = make_client(tmp_path)
    try:
        resp = client.get("/")
        assert resp.status_code == 200
        text = resp.get_data(as_text=True)
        assert "Meditation" in text or "Gratitude" in text
    finally:
        restore(orig_data, orig_config)

def test_analytics_page(tmp_path):
    client, orig_data, orig_config = make_client(tmp_path)
    try:
        resp = client.get("/analytics")
        assert resp.status_code == 200
        text = resp.get_data(as_text=True)
        assert "chart.min.js" in text or "<canvas" in text
    finally:
        restore(orig_data, orig_config)


def test_pwa_toggle(tmp_path):
    client, orig_data, orig_config = make_client(tmp_path)
    original = flask_app_module.app.config.get("PWA_ENABLED")
    try:
        flask_app_module.app.config["PWA_ENABLED"] = False
        resp = client.get("/")
        assert "manifest.json" not in resp.get_data(as_text=True)
        flask_app_module.app.config["PWA_ENABLED"] = True
        resp = client.get("/")
        assert "manifest.json" in resp.get_data(as_text=True)
    finally:
        flask_app_module.app.config["PWA_ENABLED"] = original
        restore(orig_data, orig_config)
