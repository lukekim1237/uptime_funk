# uptime_funk — URL Uptime Monitor with REST API & Live Dashboard

A Django REST Framework app that pings your URLs on a schedule, stores response history in PostgreSQL, and visualizes uptime and response-time trends in a Chart.js dashboard.

**Live demo:** https://uptime-funk.onrender.com

> ⚠️ Render free tier spins down after 15 minutes of inactivity. First request may take ~30 seconds to cold-start.

---

## Dashboard

![Dashboard](screenshot.png)

---

## Architecture

```
Browser (Dashboard)
       │  GET /api/monitors/
       │  GET /api/monitors/<id>/checks/
       ▼
Django + Gunicorn + WhiteNoise   ←→   PostgreSQL (Render)
       │
       │  POST /api/trigger-checks/   ← Authorization: <CRON_SECRET>
       ▼
cron-job.org (every 5 min, free)
  └─ HTTP POST to /api/trigger-checks/
     └─ Runs run_checks management command
        └─ HTTP GET each active Monitor URL (10s timeout)
        └─ Writes CheckResult: status_code, response_time_ms, is_up
```

Scheduled checks run via a cron-job.org webhook trigger, equivalent to an AWS EventBridge rule or Lambda scheduled event. The `POST /api/trigger-checks/` endpoint is protected by a `CRON_SECRET` environment variable — only the cron caller can fire it. Render's free web service spins down after 15 minutes of inactivity — a paid tier or alternative host would keep it always-on.

---

## Local Setup

```bash
# 1. Clone
git clone https://github.com/lukekim1237/uptime_funk.git && cd uptime_funk

# 2. Virtual environment
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Migrate (defaults to SQLite locally)
python manage.py migrate

# 5. Run
python manage.py runserver
```

Create a superuser with `python manage.py createsuperuser`, then visit `http://127.0.0.1:8000/`.

---

## API Endpoints

All endpoints except `/api/token-auth/` and `/api/trigger-checks/` require an `Authorization: Token <token>` header.

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/token-auth/` | Exchange username + password for an auth token |
| `GET / POST` | `/api/monitors/` | List the authenticated user's monitors or add a new one |
| `GET / DELETE` | `/api/monitors/<id>/` | Retrieve or delete a specific monitor |
| `GET` | `/api/monitors/<id>/checks/` | Last 20 check results for a monitor (newest first) |
| `POST` | `/api/trigger-checks/` | Fire all active checks — cron-only; requires `Authorization: <CRON_SECRET>` |

---

## Skills Demonstrated

- **Django REST Framework** — class-based generic views (`ListCreateAPIView`, `RetrieveDestroyAPIView`), custom serializers with `SerializerMethodField` for computed `latest_check` field
- **Token Authentication** — DRF `TokenAuthentication`; `SessionAuthentication` intentionally excluded to avoid CSRF conflicts with JS fetch calls
- **Scheduled Tasks** — custom management command (`run_checks`) invoked by a cron-job.org webhook on a schedule; `CRON_SECRET` header prevents unauthorized triggers
- **PostgreSQL** — `dj-database-url` for env-based DB switching (SQLite local → Render Postgres in prod)
- **Chart.js** — response-time trend line chart rendered from API data; chart instance destroyed and redrawn on monitor switch
- **Docker** — `Dockerfile` using `python:3.11-slim`; containerized local runs with SQLite volume mount
- **GitHub Actions CI** — runs `migrate` + `manage.py test` on every push; HTTP calls mocked with `unittest.mock`
- **Render Deployment** — Gunicorn WSGI, WhiteNoise static serving, auto-deploy on push to `main`, env-var config via Render dashboard

---

## Known Limitations

- **Free tier cold start (~30s):** Render's free web service idles after 15 minutes. First request after inactivity is slow. A paid Render instance or alternative host (Fly.io, Railway) eliminates this.
- **Single-user admin only:** Monitors are scoped to the creating user. No self-registration or multi-tenant UI.
- **Multi-user support is a planned extension:** `Monitor.owner` FK and per-owner queryset filtering are already in place — the groundwork exists for a self-serve signup flow.