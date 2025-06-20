# Habit Tracker — ADHD-Friendly Habit & Mood Tracker

[![CI](https://github.com/jake0lawrence/habit-track-cli/actions/workflows/ci.yml/badge.svg)](https://github.com/jake0lawrence/habit-track-cli/actions)
[![Live on Render](https://img.shields.io/badge/%E2%9C%85%20LIVE%20on%20Render-00c7b7?style=flat-square&logo=render&logoColor=white)](https://habit-track-cli.onrender.com)

A tiny, distraction-free habit & mood tracker built with **Flask + htmx + Alpine.js** and packaged as an optional PWA for offline use.

---

## ✨ Features (June 2025)

| Feature | Details |
|---------|---------|
| Fast ✨ | Single-page UI—htmx swaps only the habit grid, no full reloads. |
| Modal logging | “Log” / “Edit” buttons open a modal pre-filled from `localStorage`. |
| Static `/log` endpoint | Form always posts to `/log`; the habit key is sent as a hidden field—no Alpine/htmx race conditions. |
| Mood tracking | 1-5 slider with live ✅ indicator and rolling averages. |
| Dark mode | Persists via `localStorage`. |
| PWA | Optional service worker & manifest (`ENABLE_PWA` toggle in settings). |
| Data ownership | JSON on localhost, SQLite or Postgres in production. |
| Tests | Pytest unit coverage **+** Playwright end-to-end smoke. |
| CI | GitHub Actions runs unit & e2e tests on every push. |

---

## 🗺️ Current Habit Roster

| Habit | Frequency | “Done” definition |
|-------|-----------|-------------------|
| Meditation | Daily | ≥ 2 min timer |
| Gratitude | Daily | ≥ 1 sentence |
| Yoga | 3 × / week | ≥ 5 min |
| Cardio | 3 × / week | ≥ 5 min |
| Weights | 3 × / week | ≥ 1 set |
| Reading | 3 × / week | ≥ 1 page |

*(You can rename habits and default durations in **⚙️ Settings**.)*

---

## 💻 Local Setup

```bash
# 1 · Clone
git clone https://github.com/jake0lawrence/habit-track-cli.git
cd habit-track-cli

# 2 · Python venv
python -m venv .venv && source .venv/bin/activate

# 3 · Install deps (Typer optional; web UI has no CLI dep)
pip install -r requirements.txt

# 4 · Run dev server (auto-reload + debug)
python app.py            # or: FLASK_DEBUG=1 python app.py
````

Open [http://localhost:5000](http://localhost:5000) and start logging.

### 🧪 Tests

```bash
# Unit tests
pytest -q

# Playwright smoke test
npm ci
npx playwright install --with-deps
npx playwright test
```

---

## 🚀 Deployment (Heroku/Render/Fly)

1. Set **`DATABASE_URL`** (optional) for Postgres; otherwise the app falls back to SQLite on disk.
2. Flip **`ENABLE_PWA=1`** to serve the manifest & service worker.
3. Start command:

   ```bash
   gunicorn app:app --bind 0.0.0.0:$PORT
   ```

A “Deploy to Render” button is in `/docs/deploy-render.md` if you prefer one-click.

---

## 🔬 Design & Architecture

* **docs/architecture.md** — data model, template flow, PWA notes
* **tests/** — Pytest & Playwright specs
* **ci.yml** — unit + e2e pipeline

---

## 🛠 Tech Stack

| Layer             | Library                       |
| ----------------- | ----------------------------- |
| Backend           | Flask 2                       |
| Frontend micro-JS | htmx 1.9 • Alpine 3.13        |
| Styling           | vanilla CSS (dark-mode class) |
| PWA               | Service worker via Workbox    |
| Tests             | Pytest • Playwright           |

---

## ❓ FAQ

**Why is the Save button finally reliable?**
The modal form now posts to a *fixed* `/log` URL and passes `habit` in a hidden field, so htmx binds once at page-load—no dynamic attribute binding races.

**CLI still supported?**
Yes, but it’s optional. The Typer commands live in `habit.py`; they log to the
same JSON/DB backend the web UI uses.

---

Happy tracking!
*PRs and issue reports are welcome.* 🎉

```

---

### What changed vs. the old README

| Section | Change |
|---------|--------|
| Badges & tagline | Switched wording to *Flask + htmx* (no longer Typer-only). |
| Features | Added static `/log`, modal, PWA, tests, CI. |
| Installation | Removed `python habit.py show` from the quick-start; CLI now optional. |
| Usage demo | Dropped the outdated Rich GIF placeholder (you can add new screenshots later). |
| Docs / Design links | Point to `docs/architecture.md`. |
| FAQ | Explains the “Save button reliability” refactor. |

If you have any project-specific links (e.g., updated architecture doc filename), tweak those paths before committing.
```
