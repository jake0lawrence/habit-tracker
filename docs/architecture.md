# 🧠 Design Notes — `habit-track-cli`

## Overview

This is a lightweight, ADHD-friendly habit and mood tracker designed to be fast, local-first, and friction-free. The project emphasizes a simple CLI interface with a focus on behavioral reinforcement and mental wellness.

---

## Core Goals

- 🧘‍♂️ Make habit logging take < 15 seconds  
- 🧠 Build consistent self-reflection loops  
- 💾 Own your data locally (no cloud needed)  
- 🧰 Keep the stack tiny, extensible, and Copilot/Codex-friendly  

---

## Current Tech Stack

| Layer              | Technology                                                |
|--------------------|-----------------------------------------------------------|
| CLI Framework      | [Typer](https://typer.tiangolo.com/)                      |
| UI Rendering       | [Rich](https://rich.readthedocs.io/)                      |
| Data Storage       | Flat JSON file (`~/.habit_log.json`)                      |
| Charts (Planned)   | [`plotext`](https://github.com/piccolomo/plotext)         |
| Notification       | OS-level (`osascript`, `notify-send`, PowerShell)         |
| Future Storage     | SQLite via [`dataset`](https://github.com/pudo/dataset)   |

---

## Habit Data Schema (JSON)

```json
{
  "2025-06-18": {
    "med": 5,
    "grat": 1,
    "mood": 4
  }
}
````

**Schema Notes**

* Keys are stringified dates (`YYYY-MM-DD`)
* Each habit is tracked by its shorthand key (`med`, `grat`, etc.)
* Mood is stored as a 1–5 numeric value

---

## Command Structure

| Command                 | Description                    |
| ----------------------- | ------------------------------ |
| `log <habit> [min]`     | Mark a habit as completed      |
| `mood <score>`          | Record your current mood (1–5) |
| `show`                  | Display the weekly grid        |
| `remind` *(planned)*    | Push a desktop notification    |
| `chart` *(planned)*     | Show weekly mood chart         |
| `dashboard` *(planned)* | Interactive TUI live dashboard |

---

## Roadmap

### ✅ v0.2 (MVP Enhancements)

* [ ] SQLite backend with auto-migration
* [ ] Desktop notification support
* [ ] Basic test suite scaffold (CI-ready)

### 🚧 v0.3

* [ ] Mood trend chart
* [ ] Weekly HTML report generator
* [ ] Rich TUI dashboard

### 🎯 v1.0

* [ ] PyPI packaging and `pipx` support
* [ ] One-file Windows/Mac installer (PyInstaller)
* [ ] Final polish + demo GIF

---

## Contributing

1. Fork and clone this repo
2. Create a virtual environment
3. Install dependencies with:

   ```bash
   pip install -r requirements.txt
   ```
4. Run `habit.py show` to confirm everything works
5. Make your changes
6. Open a Pull Request! 🚀

---

## Licensing

MIT — see [LICENSE](../LICENSE) for details.

---

## Author

**Jake Lawrence**
📫 [jakelawrence.io](https://jakelawrence.io)
🧠 Building tools for calm + clarity
