# habit-track-cli
[![CI](https://github.com/jake0lawrence/habit-track-cli/actions/workflows/ci.yml/badge.svg)](https://github.com/jake0lawrence/habit-track-cli/actions)

Tiny, ADHD‑friendly habit & mood tracker built with [Typer](https://typer.tiangolo.com/) and [Rich](https://rich.readthedocs.io/).

## Why?

I needed a friction‑free way to log six core habits and a 1‑5 mood score without app overload:

| Habit | Frequency | “Done” definition |
|-------|-----------|-------------------|
| Meditation | daily | ≥ 2 min timer |
| Gratitude | daily | ≥ 1 sentence |
| Yoga | 3×/wk | ≥ 5 min stretch |
| Cardio | 3×/wk | ≥ 5 min walk |
| Weights | 3×/wk | 1 exercise set |
| Reading | 3×/wk | ≥ 1 page |

The CLI writes plain JSON/SQLite so I own the data and can graph it anywhere.

## Installation

### 🔧 Local Development Setup

```bash
# Clone the repo
git clone https://github.com/jake0lawrence/habit-track-cli.git
cd habit-track-cli

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the app
python habit.py show

# Run the web UI (add --debug or set DEBUG=1 to enable Flask debugging)
python app.py [--debug]
```
## Usage

| Habit | Key | Frequency |
|-------|-----|-----------|
| Meditation | `med` | Daily |
| Gratitude Journal | `grat` | Daily |
| Yoga | `yoga` | 3×/week |
| Cardio | `cardio` | 3×/week |
| Weight Lifting | `weights` | 3×/week |
| Reading | `read` | 3×/week |

### Example commands

```bash
python habit.py log med 5     # ✅ logs 5 mins of meditation
python habit.py mood 4        # 🧠 logs a 4/5 mood
python habit.py show          # 📊 weekly grid
```
## Demo

<!-- TODO: replace with real demo -->
![CLI demo](docs/demo.gif)

## Documentation

- [Design Notes](docs/architecture.md)


