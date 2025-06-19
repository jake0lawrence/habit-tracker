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
        assert resp.status_code == 204
        data = read_json(flask_app_module.DATA_FILE)
        today = str(datetime.date.today())
        assert data[today]["med"]["duration"] == 15
        assert data[today]["med"]["note"] == "test"
    finally:
        restore(orig_data, orig_config)


def test_post_mood_route(tmp_path):
    client, orig_data, orig_config = make_client(tmp_path)
    try:
        resp = client.post("/mood", data={"score": "3"})
        assert resp.status_code == 204
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
