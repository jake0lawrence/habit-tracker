from typer.testing import CliRunner
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import habit  # noqa: E402

runner = CliRunner()


def test_load_data_missing_file(tmp_path):
    """`load_data` returns an empty dict when the JSON file is absent."""
    orig_file = habit.DATA_FILE
    habit.DATA_FILE = tmp_path / "habit.json"
    try:
        assert habit.load_data() == {}
    finally:
        habit.DATA_FILE = orig_file


def test_log_unknown_habit(tmp_path):
    """`habit log` exits non-zero and prints helpful message for bad key."""
    orig_file = habit.DATA_FILE
    habit.DATA_FILE = tmp_path / "habit.json"
    try:
        # Click < 8.1 merges stderr into .output by default
        result = runner.invoke(habit.app, ["log", "invalid"])
        assert result.exit_code != 0
        assert "Unknown habit key" in result.output
    finally:
        habit.DATA_FILE = orig_file
