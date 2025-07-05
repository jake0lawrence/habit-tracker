# 📋 Task List — Habit-Track

> **Legend**  
> 🟢 = quick win • 🔶 = medium effort • 🔴 = larger feature

---

## 1 · Core Codebase

- [ ] 🟢 **Migrate remaining `os.path` to `pathlib`**  
  - [ ] Replace path handling in `habit.py` and `storage.py`  
  - [ ] Allow `HABIT_DATA_PATH` env var to override default location  

- [x] 🟢 **Add docstrings + type hints**
  - [x] `get_week_range`
  - [x] `calculate_habit_stats`
  - [x] `load_config` / `save_config`

- [ ] 🔶 **Centralise storage adapter**  
  - [ ] Move JSON + SQLite helpers into `storage.py`  
  - [ ] Re-use in both CLI and Flask routes  

---

## 2 · Testing & CI

- [ ] 🟢 **Increase unit coverage**  
  - [ ] Add tests for `/mood` POST route (happy + edge cases)  
  - [ ] Cover malformed JSON & invalid mood scores (4xx expected)  

- [ ] 🔶 **Playwright expansion**  
  - [ ] Add test for editing an existing habit entry  
  - [ ] Add offline/PWA smoke test (service worker cached)  

- [ ] 🟢 **CI hardening**  
  - [ ] Pin `click==8.1.*` _or_ upgrade `typer>=0.12` in `requirements.txt`  
  - [ ] Enable Dependabot for pip + npm to surface dep updates via PR  

---

## 3 · Web UI / PWA

- [ ] 🔶 **Self-host JS libraries**  
  - [ ] Copy `htmx.min.js` and `alpine.min.js` to `/static/vendor`  
  - [ ] Update `<script src>` paths and CSP headers  

- [ ] 🟢 **Dark-mode polish**  
  - [ ] Add system-prefers detection (`prefers-color-scheme`)  
  - [ ] Smooth CSS transition when toggling  

- [ ] 🔶 **Service-worker push notifications** (roadmap 0.5)  
  - [ ] Notify on habit streak milestones (7-day, 30-day)  
  - [ ] Respect `DoNotDisturb` hours from settings  

---

## 4 · Packaging & Docs

- [ ] 🟢 **Packaging**  
  - [ ] Add `pyproject.toml` with `flit`/`poetry` metadata  
  - [ ] Publish to TestPyPI for CLI install via `pipx`  

- [ ] 🟢 **README / Docs refresh**  
  - [ ] Document how to customise habits (`config.json`)  
  - [ ] Add screenshots / GIF of new modal flow  

---

## 5 · Nice-to-Haves

- [ ] 🔴 **Weekly email report**  
  - [ ] Export CSV → convert to HTML → email via SMTP  

- [ ] 🔴 **Mobile-native wrapper** (Capacitor.js)  
  - [ ] iOS/Android install with home-screen widgets  

---

### Progress at a glance

| Area | Completed | Remaining |
|------|-----------|-----------|
| Core Codebase | 1 / 3 | **2** |
| Tests & CI    | 0 / 3 | **3** |
| Web UI / PWA  | 0 / 3 | **3** |
| Packaging & Docs | 0 / 2 | **2** |
| Nice-to-Haves | 0 / 2 | **2** |

---

> **Tip:** break large tasks into PR-sized chunks; each PR must include unit or e2e coverage where applicable. 🚀

