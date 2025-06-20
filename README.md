# Habit-Track — ADHD-Friendly Habit, Mood & Journal Tracker

[![CI](https://github.com/jake0lawrence/habit-track-cli/actions/workflows/ci.yml/badge.svg)](https://github.com/jake0lawrence/habit-track-cli/actions)
[![Live on Render](https://img.shields.io/badge/%E2%9C%85%20LIVE%20on%20Render-00c7b7?style=flat-square&logo=render&logoColor=white)](https://habit-track-cli.onrender.com)

A tiny, distraction-free tracker built with **Flask + htmx + Alpine.js**.  
Log habits & moods in seconds, jot AI-seeded journal entries, and review analytics—all offline-capable via PWA.

---

## ✨ Feature Matrix (June 2025)

| Category | Feature | Details |
|----------|---------|---------|
| **Habits** | Modal logging | “Log / Edit” auto-prefilled from `localStorage`. |
| | Static `/log` endpoint | Eliminates Alpine/htmx timing bugs. |
| **Mood** | 1–5 slider | Instant ✅ indicator, rolling averages in summary tiles. |
| **Journal** | OpenAI prompt *(opt-in)* | Generates a reflective writing prompt based on today’s mood & streaks. |
| | `/journal-entry` save | Saves entry to DB/JSON; auto-redirects to “Journal History”. |
| | `/journal-history` page | Chronological reader with export buttons (`.txt` / `.zip`). |
| **Analytics** | `/analytics` dashboard | Bar charts per habit + line chart of mood over time (Chart.js). |
| **UX** | Dark mode toggle | Persists via `localStorage`. |
| | Toast notifications | Green “Saved ✔️” & red error toasts (htmx hooks). |
| **Offline** | PWA | `ENABLE_PWA=1` serves manifest & Workbox service-worker. |
| **Data** | Local JSON → SQLite/Postgres (prod) | Own your data; easy to back up. |
| **Quality** | Tests | Pytest unit + Playwright E2E (“Log → Save → ✅”). |
| | CI | GitHub Actions runs both suites on every push. |

---

## 🗺️ Default Habits

| Habit | Frequency | “Done” definition |
|-------|-----------|-------------------|
| Meditation | Daily | ≥ 2 min timer |
| Gratitude | Daily | ≥ 1 sentence |
| Yoga | 3× / week | ≥ 5 min |
| Cardio | 3× / week | ≥ 5 min |
| Weights | 3× / week | ≥ 1 set |
| Reading | 3× / week | ≥ 1 page |

*(Customise names & defaults in **⚙️ Settings** or edit `config.json`.)*

---

## 💻 Local Setup

```bash
git clone https://github.com/jake0lawrence/habit-track-cli.git
cd habit-track-cli
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# ⬇️ Optional: enable AI journal prompts
export OPENAI_API_KEY=sk-********************************

python app.py   # auto-reload + debug if FLASK_DEBUG=1
````

Open [http://localhost:5000](http://localhost:5000) & start tracking.

---

## 🧪 Tests

```bash
pytest -q                     # unit tests
npm ci && npx playwright test # E2E smoke
```

---

## 🚀 Deployment (Render/Heroku/Fly)

| Variable         | Purpose                    | Default                   |
| ---------------- | -------------------------- | ------------------------- |
| `DATABASE_URL`   | Postgres connection        | uses SQLite file if unset |
| `ENABLE_PWA`     | `1` to serve manifest & SW | `0`                       |
| `OPENAI_API_KEY` | Enables journal prompt     | prompts disabled if empty |

Start command:

```bash
gunicorn app:app --bind 0.0.0.0:$PORT
```

Need one-click? See `/docs/deploy-render.md`.

---

## 🔬 More Docs

* **[docs/architecture.md](docs/architecture.md)** — data model, request flow, PWA notes  
* **[docs/tasks.md](docs/tasks.md)** — open roadmap with emoji effort tags  
* **[docs/deploy-render.md](docs/deploy-render.md)** — one-click & manual deploy steps for Render  
* **[tests/](tests/)** — Pytest & Playwright specs  
* **[.github/workflows/ci.yml](.github/workflows/ci.yml)** — full CI pipeline

---

## 🔧 Tech Stack

| Layer             | Library                             |
| ----------------- | ----------------------------------- |
| Backend           | Flask 2.x                           |
| Frontend micro-JS | htmx 1.9 • Alpine 3.13              |
| Charts            | Chart.js 4 (deferred import)        |
| Styling           | Vanilla CSS (dark-mode class)       |
| AI Journal        | OpenAI GPT-4o via `/journal-prompt` |
| PWA               | Workbox service-worker              |
| Tests             | Pytest • Playwright                 |

---

## ❓ FAQ

**How do AI journal prompts work?**
If `OPENAI_API_KEY` is present, opening the Journal page (`/journal`) calls
OpenAI with today’s mood & streak data and displays a tailored writing prompt.

**What if I don’t want AI at all?**
Leave `OPENAI_API_KEY` unset; you can still type entries manually.

**CLI still supported?**
Yes—`habit.py` offers `log`, `mood`, `show` commands for terminal fans,
backed by the same JSON/DB layer.

---

Happy tracking & journaling!
*PRs and issue reports are welcome.* 🌱


## Key additions

* New **Journal** section in the feature table + env var note  
* `/journal`, `/journal-history`, `/analytics` explained  
* Toasts & Chart.js called out  
* OpenAI API setup documented  
* FAQ updated accordingly
