import datetime
import app


def test_log_save(tmp_path):
    orig_data = app.DATA_FILE
    orig_config = app.CONFIG_FILE
    app.DATA_FILE = tmp_path / "data.json"
    app.CONFIG_FILE = tmp_path / "config.json"
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
