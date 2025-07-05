import json
import datetime
from pathlib import Path
import pytest

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
        today = datetime.date.today().isoformat()
        resp = client.post("/log", data={"habit":"med", "duration": "15", "note": "test", "date": today})
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
            "/log",
            data={"habit":"med", "duration": "20", "note": "yesterday", "date": custom_date},
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


def test_log_mood(tmp_path):
    client, orig_data, orig_config = make_client(tmp_path)
    try:
        res = client.post("/mood", data={"score": "4"})
        assert res.status_code == 200
        assert res.is_json
        assert res.get_json()["status"] == "ok"
        assert res.get_json()["score"] == 4
    finally:
        restore(orig_data, orig_config)


def test_mood_missing_score(tmp_path):
    client, orig_data, orig_config = make_client(tmp_path)
    try:
        res = client.post("/mood", data={})
        assert res.status_code == 400
    finally:
        restore(orig_data, orig_config)


def test_mood_out_of_range(tmp_path):
    client, orig_data, orig_config = make_client(tmp_path)
    try:
        res = client.post("/mood", data={"score": "10"})
        assert res.status_code == 400
    finally:
        restore(orig_data, orig_config)


def test_mood_invalid_type(tmp_path):
    client, orig_data, orig_config = make_client(tmp_path)
    try:
        res = client.post("/mood", data={"score": "abc"})
        assert res.status_code == 400
    finally:
        restore(orig_data, orig_config)


def test_mood_float_value(tmp_path):
    client, orig_data, orig_config = make_client(tmp_path)
    try:
        res = client.post("/mood", data={"score": "3.5"})
        assert res.status_code == 400
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


def test_mood_average(tmp_path):
    client, orig_data, orig_config = make_client(tmp_path)
    try:
        # seed mood data
        today = datetime.date.today()
        data = {
            str(today): {"mood": 4},
            str(today - datetime.timedelta(days=1)): {"mood": 3},
        }
        (flask_app_module.DATA_FILE).write_text(json.dumps(data))
        stats = flask_app_module.calculate_mood_stats(data)
        assert stats["overall_avg"] == pytest.approx(3.5)
    finally:
        restore(orig_data, orig_config)


def test_homepage_mood_summary(tmp_path):
    client, orig_data, orig_config = make_client(tmp_path)
    try:
        res = client.get("/")
        assert res.status_code == 200
        assert b"Mood Summary" in res.data
    finally:
        restore(orig_data, orig_config)


def test_analytics_mood_route(tmp_path):
    client, orig_data, orig_config = make_client(tmp_path)
    try:
        res = client.get("/analytics")
        assert res.status_code == 200
        assert b"id=\"mood-chart\"" in res.data
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


def test_journal_route(tmp_path, monkeypatch):
    client, orig_data, orig_config = make_client(tmp_path)
    try:
        def fake_enrich(prompt):
            return "Prompt"
        monkeypatch.setattr(flask_app_module, "enrich_prompt_with_ai", fake_enrich)
        res = client.get("/journal")
        assert res.status_code == 200
        assert b"Mood Journal" in res.data
    finally:
        restore(orig_data, orig_config)


def test_download_journal(tmp_path):
    client, orig_data, orig_config = make_client(tmp_path)
    try:
        res = client.get("/download-journal?format=txt")
        assert res.status_code in {200, 404}
    finally:
        restore(orig_data, orig_config)


def test_ai_model_toggle(monkeypatch):
    monkeypatch.setenv("AI_MODEL", "gpt-3.5-turbo")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    called = {}

    class FakeChoice:
        message = {"content": "ok"}

    class FakeResponse:
        choices = [FakeChoice]

    def fake_create(model, messages):
        called["model"] = model
        return FakeResponse()

    monkeypatch.setattr(flask_app_module.openai.ChatCompletion, "create", fake_create)
    result = flask_app_module.enrich_prompt_with_ai("Reflect on your week.")
    assert isinstance(result, str)
    assert called.get("model") == "gpt-3.5-turbo"


def test_journal_history(tmp_path):
    client, orig_data, orig_config = make_client(tmp_path)
    orig_journal = flask_app_module.JOURNAL_FILE
    try:
        flask_app_module.JOURNAL_FILE = tmp_path / "journal.md"
        flask_app_module.JOURNAL_FILE.write_text("## 2023-01-01\nentry\n")
        res = client.get("/journal-history")
        assert res.status_code == 200
    finally:
        flask_app_module.JOURNAL_FILE = orig_journal
        restore(orig_data, orig_config)


def test_grid_previous_week(tmp_path):
    client, orig_data, orig_config = make_client(tmp_path)
    try:
        backend = flask_app_module.get_storage_backend()
        start = flask_app_module.monday_of_current_week() - datetime.timedelta(days=7)
        backend.save_habit(str(start), "med", 42, "note")
        res = client.get("/grid?offset=-7")
        assert res.status_code == 200
        assert "42&nbsp;min" in res.get_data(as_text=True)
    finally:
        restore(orig_data, orig_config)
