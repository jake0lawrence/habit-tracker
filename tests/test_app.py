import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import app


def test_load_data_malformed(tmp_path):
    orig = app.DATA_FILE
    bad = tmp_path / "bad.json"
    bad.write_text('{ "invalid": }')
    app.DATA_FILE = bad
    try:
        assert app.load_data() == {}
    finally:
        app.DATA_FILE = orig


def test_load_config_malformed(tmp_path):
    orig = app.CONFIG_FILE
    bad = tmp_path / "bad_config.json"
    bad.write_text('{ "invalid": }')
    app.CONFIG_FILE = bad
    try:
        assert app.load_config() == {}
    finally:
        app.CONFIG_FILE = orig
