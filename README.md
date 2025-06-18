# habit-track-cli

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

## Quick start

```bash
git clone https://github.com/jake0lawrence/habit-track-cli.git
cd habit-track-cli
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python habit.py show     # view the weekly grid

