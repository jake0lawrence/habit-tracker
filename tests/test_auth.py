import datetime
import app
import storage


def make_client(tmp_path, monkeypatch):
    backend = storage.SQLiteBackend(tmp_path / 'db.sqlite')
    if hasattr(storage.get_backend, '_cache'):
        storage.get_backend._cache.clear()
    monkeypatch.setattr(app, 'get_storage_backend', lambda: backend)
    app.app.config['WTF_CSRF_ENABLED'] = False
    app.app.config['LOGIN_DISABLED'] = False
    client = app.app.test_client()
    return client, backend


def test_signup_and_login(tmp_path, monkeypatch):
    client, _ = make_client(tmp_path, monkeypatch)
    resp = client.post(
        '/signup',
        data={'email': 'user@example.com', 'password': 'secret123', 'confirm': 'secret123'},
    )
    assert resp.status_code == 302
    assert resp.headers['Location'].endswith('/')

    client.get('/logout')

    resp = client.post(
        '/login',
        data={'email': 'user@example.com', 'password': 'secret123'},
    )
    assert resp.status_code == 302
    assert resp.headers['Location'].endswith('/')


def test_home_requires_login(tmp_path, monkeypatch):
    client, _ = make_client(tmp_path, monkeypatch)
    resp = client.get('/')
    assert resp.status_code == 302
    assert '/login' in resp.headers['Location']


def test_user_isolation(tmp_path, monkeypatch):
    client, backend = make_client(tmp_path, monkeypatch)
    today = datetime.date.today().isoformat()

    client.post(
        '/signup',
        data={'email': 'a@example.com', 'password': 'pw123456', 'confirm': 'pw123456'},
    )
    client.post(
        '/log',
        data={'habit': 'med', 'duration': '5', 'note': 'userA-note', 'date': today},
    )
    client.get('/logout')

    client.post(
        '/signup',
        data={'email': 'b@example.com', 'password': 'pw654321', 'confirm': 'pw654321'},
    )
    resp = client.get('/')
    assert resp.status_code == 200
    page = resp.get_data(as_text=True)
    assert 'userA-note' not in page

    data = backend.load_all(2)
    assert today not in data or 'med' not in data.get(today, {})
    data_a = backend.load_all(1)
    assert data_a[today]['med']['note'] == 'userA-note'
