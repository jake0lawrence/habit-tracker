def test_app_mode_prod_enables_pwa(monkeypatch):
    monkeypatch.setenv("APP_MODE", "prod")
    import importlib
    import app
    importlib.reload(app)
    try:
        assert app.app.config["PWA_ENABLED"] is True
        assert app.app.config["APP_MODE"] == "prod"
    finally:
        monkeypatch.delenv("APP_MODE", raising=False)
        importlib.reload(app)

