# 🧠 Design Notes — `habit-track-cli`

## Overview

This is a lightweight, ADHD-friendly habit and mood tracker designed to be fast, local-first, and friction-free. The project emphasizes a simple CLI interface with a focus on behavioral reinforcement and mental wellness.

---

## Core Goals

- 🧘‍♂️ Make habit logging take < 15 seconds
- 🧠 Build consistent self-reflection loops
- 💾 Own your data locally (no cloud needed)
- 🧰 Keep the stack tiny, extensible, and codex/Copilot-friendly

---

## Current Tech Stack

| Layer | Technology |
|-------|------------|
| CLI Framework | [Typer](https://typer.tiangolo.com/) |
| UI Rendering | [Rich](https://rich.readthedocs.io/) |
| Data Storage | Flat JSON file (`~/.habit_log.json`) |
| Charts (Planned) | [`plotext`](https://github.com/piccolomo/plotext) |
| Notification (Planned) | OS-level (`osascript`, `notify-send`, PowerShell) |
| Future Storage | SQLite via `dataset` |

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
