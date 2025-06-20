# 🌐 Deploy Habit‑Track to Render

This guide walks you through spinning up a production instance of **Habit‑Track** on [Render.com](https://render.com/). Expect a 5‑minute button‑click deployment, plus optional tweaks for Postgres, PWA, and OpenAI prompts.

---

## 1 · One‑Click Deploy

> **Quick start:** click the badge below and follow Render’s UI prompts.
>
> [![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)
>
> <details>
> <summary>What the button does</summary>
> It forks this repo, provisions a free Web Service, attaches a Postgres instance (if you leave `DATABASE_URL` blank it uses on‑disk SQLite), and sets the default start command.
> </details>

---

## 2 · Manual Setup (if you prefer fine‑grained control)

### 2.1 Create a new *Web Service*

| Field             | Value                                   |
| ----------------- | --------------------------------------- |
| **Environment**   | `Python 3`                              |
| **Build Command** | `pip install -r requirements.txt`       |
| **Start Command** | `gunicorn app:app --bind 0.0.0.0:$PORT` |
| **Instance Type** | Starter (0.5 GB) is fine for hobby use  |
| **Region**        | Your choice                             |

### 2.2 Environment Variables

| Key              | Example                              | Notes                                    |
| ---------------- | ------------------------------------ | ---------------------------------------- |
| `FLASK_ENV`      | `production`                         | Ensures debug mode off                   |
| `ENABLE_PWA`     | `1`                                  | Serves manifest & service‑worker         |
| `DATABASE_URL`   | (auto‑populated if you add Postgres) | Leave blank to use SQLite on Render Disk |
| `OPENAI_API_KEY` | `sk‑******`                          | Optional — enables AI journal prompts    |

### 2.3 Persistent Disk (SQLite only)

If you stick with SQLite, attach a **Render Disk**:

1. *Add Disk* → size **1 GB** is plenty.
2. Mount path: `/data` (the app resolves relative to this path).

### 2.4 Post‑Deploy Health Check

Render auto‑pings `/` by default. The app returns **200** when the UI loads.

---

## 3 · Optional Tweaks

* **Custom Domain** → Render → *Settings* → Domains → add CNAME.
* **SSL** is automatic via Let’s Encrypt.
* **Autoscale** → upgrade plan or enable background workers for heavy AI usage.
* **CRON Jobs** → schedule weekly CSV exports or cleanup scripts.

---

## 4 · Troubleshooting

| Symptom                      | Fix                                                          |
| ---------------------------- | ------------------------------------------------------------ |
| `ModuleNotFoundError: flask` | Ensure the build command installs `requirements.txt`.        |
| 502 error after deploy       | Check the *Logs* tab — likely bad env var or port not bound. |
| AI journal prompt fails      | Confirm `OPENAI_API_KEY` is set & account has quota.         |

---

### Enjoy your cloud‑hosted Habit‑Track! 🎉

Need help? Open an issue or ping @jake0lawrence.
