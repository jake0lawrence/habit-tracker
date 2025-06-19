# 📋 Task List

The following improvements were suggested for the project. Each item below represents a task to be completed.

- [ ] **Improve path handling in `habit.py`**
  - Use `pathlib.Path` for better cross-platform support
  - Allow the data file path to be overridden via an environment variable
- [ ] **Add docstrings and type hints**
  - Document functions like `get_week_range`, `calculate_habit_stats`, and `load_config`
  - Add type hints across the codebase
- [ ] **Increase test coverage**
  - Add tests for the `mood` command and Flask routes
  - Cover edge cases like malformed JSON and invalid mood scores
- [ ] **Refactor common functionality**
  - Centralize data load/save logic in a shared module used by both CLI and web
- [ ] **Packaging and configuration**
  - Provide a `setup.cfg` or setup script for installation
  - Document how to customize habits or the data path in `README.md`
- [ ] **Review web assets**
  - Self-host external libraries referenced by the service worker or adjust caching strategy
