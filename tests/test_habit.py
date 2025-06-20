from typer.testing import CliRunner
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import habit

runner = CliRunner()


def test_load_data_missing_file(tmp_path):
    """load_data should return empty dict if file doesn't exist."""
    orig_path = habit.DATA_FILE
    habit.DATA_FILE = tmp_path / "habit.json"
    try:
        assert habit.load_data() == {}
    finally:
        habit.DATA_FILE = orig_path


def test_log_unknown_habit(tmp_path):
    """`log` should error when habit key is invalid."""
    orig_path = habit.DATA_FILE
    habit.DATA_FILE = tmp_path / "habit.json"
    try:
        result = runner.invoke(habit.app, ["log", "invalid"])
        assert result.exit_code != 0
        assert "Unknown habit key" in (result.stderr or result.stdout)
    finally:
        habit.DATA_FILE = orig_path
