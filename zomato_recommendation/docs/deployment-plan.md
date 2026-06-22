# Deployment Plan — Zomato AI Restaurant Recommender

Deploy the **Flask backend** on [Railway](https://railway.app) and the **Next.js frontend** on [Vercel](https://vercel.com).

```
┌─────────────────────┐         HTTPS          ┌──────────────────────┐
│  Vercel             │  POST /api/recommend   │  Railway             │
│  zomato_frontend    │ ─────────────────────► │  Flask API (api.py)  │
│  (Next.js 16)       │  GET  /api/health      │                      │
└─────────────────────┘                        └──────────┬───────────┘
                                                          │
                              ┌───────────────────────────┼───────────────────────────┐
                              ▼                           ▼                           ▼
                     Hugging Face Hub              Groq API (LLM)              In-memory cache
                     (Zomato dataset)              (llama-3.3-70b)              (dataset + results)
```

---

## Table of contents

1. [Prerequisites](#1-prerequisites)
2. [Pre-deployment code changes](#2-pre-deployment-code-changes)
3. [Deploy backend on Railway](#3-deploy-backend-on-railway)
4. [Deploy frontend on Vercel](#4-deploy-frontend-on-vercel)
5. [Environment variables reference](#5-environment-variables-reference)
6. [Post-deployment verification](#6-post-deployment-verification)
7. [Production considerations](#7-production-considerations)
8. [Troubleshooting](#8-troubleshooting)
9. [Deployment checklist](#9-deployment-checklist)
10. [Pausing when not in use](#10-pausing-when-not-in-use)

---

## 1. Prerequisites

| Item | Details |
|------|---------|
| GitHub repo | Code pushed to `https://github.com/DILIP8PATIDAR/zomato_milestone1` |
| Groq API key | From [console.groq.com](https://console.groq.com/) |
| Railway account | [railway.app](https://railway.app) — connect GitHub |
| Vercel account | [vercel.com](https://vercel.com) — connect GitHub |
| Node.js (local) | 18+ — only needed for local testing before deploy |

**Deploy order:** Railway (backend) first → get the public URL → then Vercel (frontend).

---

## 2. Pre-deployment code changes

The repo is ready for local dev but needs a few production additions before Railway can serve traffic reliably.

### 2.1 Add Gunicorn (production WSGI server)

Flask's built-in server (`app.run()`) is for development only. Add to `zomato_recommendation/requirements.txt`:

```txt
gunicorn>=22.0.0
```

### 2.2 Create a Railway Procfile

Create `zomato_recommendation/Procfile` (no file extension):

```
web: gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 api:app
```

| Flag | Why |
|------|-----|
| `$PORT` | Railway injects this automatically |
| `--workers 2` | Handle concurrent requests |
| `--timeout 120` | First request downloads the Hugging Face dataset (~30–90 s) |

### 2.3 Expose the Flask `app` object for Gunicorn

`api.py` already defines `app = Flask(__name__)` at module level — Gunicorn imports it as `api:app`. No change needed.

The `if __name__ == "__main__"` block is only used locally:

```python
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(debug=True, port=port)
```

Optionally add `import os` at the top if you update the entry point to read `PORT`.

### 2.4 Tighten CORS for production (recommended)

Current code uses `CORS(app)` (allows all origins). For production, restrict to your Vercel domain:

```python
import os
from flask_cors import CORS

ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,http://127.0.0.1:3000",
).split(",")

CORS(app, origins=[o.strip() for o in ALLOWED_ORIGINS])
```

Set `ALLOWED_ORIGINS` on Railway to your Vercel URL, e.g.:

```
https://zomato-frontend.vercel.app,https://your-custom-domain.com
```

### 2.5 Commit and push

```bash
git add zomato_recommendation/requirements.txt zomato_recommendation/Procfile
# plus any api.py CORS changes
git commit -m "Add production server config for Railway deployment"
git push origin main
```

---

## 3. Deploy backend on Railway

### 3.1 Create a new project

1. Go to [railway.app/new](https://railway.app/new)
2. Choose **Deploy from GitHub repo**
3. Select `DILIP8PATIDAR/zomato_milestone1`

### 3.2 Configure the service

| Setting | Value |
|---------|-------|
| **Root directory** | `/` (repo root) — **or** `zomato_recommendation` if you prefer subdirectory deploy |
| **Builder** | Dockerfile (auto-detected from root `Dockerfile`) or Railpack (via root `requirements.txt` + `app.py`) |
| **Start command** | Auto from `Dockerfile` / `railway.toml` |

The repo includes **root-level** `Dockerfile`, `railway.toml`, `app.py`, and `requirements.txt` so Railway can build from the monorepo root without extra dashboard config. Alternatively, set root directory to `zomato_recommendation` to use the backend-local config files.

### 3.3 Set environment variables

In Railway → your service → **Variables**, add:

| Variable | Value | Required |
|----------|-------|----------|
| `GROQ_API_KEY` | Your Groq API key | Yes |
| `GROQ_MODEL` | `llama-3.3-70b-versatile` | No (default) |
| `HF_DATASET_NAME` | `ManikaSaini/zomato-restaurant-recommendation` | Yes |
| `BUDGET_LOW_MAX` | `300` | No |
| `BUDGET_MEDIUM_MAX` | `800` | No |
| `MAX_CANDIDATES` | `20` | No |
| `LLM_TEMPERATURE` | `0.4` | No |
| `LLM_MAX_TOKENS` | `1500` | No |
| `ALLOWED_ORIGINS` | `https://<your-vercel-app>.vercel.app` | Yes (after Vercel deploy) |

> Do **not** set `PORT` manually — Railway provides it.

### 3.4 Generate a public domain

1. Railway → service → **Settings** → **Networking**
2. Click **Generate Domain**
3. Copy the URL, e.g. `https://zomato-api-production.up.railway.app`

### 3.5 Verify the backend

```bash
curl https://<your-railway-domain>/api/health
```

Expected response:

```json
{"status": "ok", "service": "zomato-recommendation-api"}
```

Test a recommendation (first call may take up to 90 seconds while the dataset downloads):

```bash
curl -X POST https://<your-railway-domain>/api/recommend \
  -H "Content-Type: application/json" \
  -d '{"location":"Bangalore","budget":"medium","cuisine":"Italian","min_rating":4.0}'
```

---

## 4. Deploy frontend on Vercel

### 4.1 Import the project

1. Go to [vercel.com/new](https://vercel.com/new)
2. Import `DILIP8PATIDAR/zomato_milestone1` from GitHub

### 4.2 Configure the project

| Setting | Value |
|---------|-------|
| **Framework preset** | Next.js (auto-detected) |
| **Root directory** | `zomato_recommendation/zomato_frontend` |
| **Build command** | `npm run build` (default) |
| **Output directory** | `.next` (default) |
| **Install command** | `npm install` (default) |

### 4.3 Set environment variables

In Vercel → Project → **Settings** → **Environment Variables**:

| Variable | Value | Environments |
|----------|-------|--------------|
| `NEXT_PUBLIC_API_BASE_URL` | `https://<your-railway-domain>` | Production, Preview, Development |

Example:

```
NEXT_PUBLIC_API_BASE_URL=https://zomato-api-production.up.railway.app
```

> **Important:** Use the Railway HTTPS URL with **no trailing slash**. The frontend appends `/api/recommend` automatically.

### 4.4 Deploy

Click **Deploy**. Vercel builds and hosts the app at a URL like:

```
https://zomato-milestone1.vercel.app
```

### 4.5 Update Railway CORS

Go back to Railway and set `ALLOWED_ORIGINS` to your Vercel URL:

```
https://zomato-milestone1.vercel.app
```

Redeploy the Railway service if needed (Railway auto-redeploys on variable change).

### 4.6 Redeploy Vercel (if env var was added after first deploy)

If you set `NEXT_PUBLIC_API_BASE_URL` after the first build, trigger a redeploy so the variable is baked into the client bundle:

Vercel → Deployments → **Redeploy**

---

## 5. Environment variables reference

### Backend (Railway) — `zomato_recommendation/.env.example`

```env
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
HF_DATASET_NAME=ManikaSaini/zomato-restaurant-recommendation
BUDGET_LOW_MAX=300
BUDGET_MEDIUM_MAX=800
MAX_CANDIDATES=20
LLM_TEMPERATURE=0.4
LLM_MAX_TOKENS=1500
ALLOWED_ORIGINS=https://your-app.vercel.app
```

### Frontend (Vercel) — `zomato_frontend/.env.example`

```env
NEXT_PUBLIC_API_BASE_URL=https://your-railway-domain.up.railway.app
```

---

## 6. Post-deployment verification

| Step | Action | Expected result |
|------|--------|-----------------|
| 1 | Open Vercel URL in browser | Preference form loads |
| 2 | Submit a search | Loading state → recommendation cards |
| 3 | `curl <railway>/api/health` | `{"status":"ok"}` |
| 4 | Browser DevTools → Network tab | `POST /api/recommend` returns 200 |
| 5 | Browser DevTools → Console | No CORS errors |

---

## 7. Production considerations

### Dataset loading (production)

Production loads a baked parquet file (`data/zomato.parquet`, ~550 KB) instead of downloading from Hugging Face at runtime. This keeps memory around **~250 MB** and fits Railway's 512 MB hobby tier.

| File | Purpose |
|------|---------|
| `data/zomato.parquet` | Committed snapshot used at runtime on Railway |
| `scripts/bake_dataset.py` | Regenerates parquet from Hugging Face (run locally or during Docker build) |

Local dev without the parquet file falls back to Hugging Face download (cached under `.cache/huggingface/`).

### Cold start

After a deploy or container restart, the first `/api/recommend` request may take a few seconds while the parquet loads into memory. `/api/health` stays fast and does not preload the dataset.

### Memory

Do **not** load the full Hugging Face dataset into pandas on Railway — it peaks above 800 MB and triggers OOM crashes (`Application failed to respond` / `502`). The parquet path is required for production.

### HTTPS

Both Railway and Vercel provide HTTPS by default. Ensure `NEXT_PUBLIC_API_BASE_URL` uses `https://` (not `http://`) to avoid mixed-content browser blocks.

### Secrets

Never commit `.env` files. Set all secrets via Railway and Vercel dashboards only.

### Custom domains (optional)

| Platform | Steps |
|----------|-------|
| Railway | Settings → Networking → Custom Domain → add `api.yourdomain.com` |
| Vercel | Settings → Domains → add `yourdomain.com` |

Update `ALLOWED_ORIGINS` and `NEXT_PUBLIC_API_BASE_URL` accordingly.

---

## 8. Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| `Cannot reach the backend` in UI | Wrong `NEXT_PUBLIC_API_BASE_URL` or backend down | Verify Railway URL; redeploy Vercel after env change |
| CORS error in browser console | `ALLOWED_ORIGINS` missing Vercel URL | Add exact Vercel origin (no trailing slash) on Railway |
| `502` on `/api/recommend` | Groq API key invalid, OOM, or worker crash | Check Railway logs; verify `GROQ_API_KEY`; confirm `data/zomato.parquet` is in the deploy |
| `Cannot reach the backend` (browser) | Railway 502 without CORS headers (worker crashed) | Same as OOM — redeploy with parquet-based loader; check Railway logs |
| Request times out on first search | Cold start after sleep/redeploy | Wait and retry; increase Gunicorn `--timeout` |
| `Application failed to respond` on Railway | Gunicorn not installed or wrong start command | Confirm `Procfile` and `gunicorn` in `requirements.txt` |
| Build fails on Vercel | Wrong root directory | Set root to `zomato_recommendation/zomato_frontend` |
| Build fails on Railway | Wrong root directory | Set root to `zomato_recommendation` |
| `railpack process exited with an error` | Railway building from repo root, not `zomato_recommendation/` | Root `Dockerfile` + `app.py` are included — redeploy from latest `main` |
| `Railpack could not determine how to build` | No Python files at repo root | Same fix — use root `Dockerfile` or set Root Directory to `zomato_recommendation` |
| Railpack still fails after Python pin | Heavy deps or Railpack instability | Switch builder to **Dockerfile** in service settings (repo includes `Dockerfile`) |
| Works locally, fails in prod | Port / URL mismatch | Production uses Railway `$PORT`, not `5001` |

### Viewing logs

```bash
# Railway — via dashboard
Railway → Service → Deployments → View Logs

# Vercel — via dashboard
Vercel → Project → Deployments → select deploy → Build / Runtime logs
```

---

## 9. Deployment checklist

### Before deploy

- [ ] `gunicorn` added to `requirements.txt`
- [ ] `Procfile`, `railway.toml`, `.python-version`, and `Dockerfile` in `zomato_recommendation/`
- [ ] CORS restricted via `ALLOWED_ORIGINS` (optional but recommended)
- [ ] Changes committed and pushed to `main`

### Railway (backend)

- [ ] GitHub repo connected
- [ ] Root directory set to `zomato_recommendation`
- [ ] All backend env vars set (`GROQ_API_KEY`, `HF_DATASET_NAME`, etc.)
- [ ] Public domain generated
- [ ] `/api/health` returns 200

### Vercel (frontend)

- [ ] GitHub repo connected
- [ ] Root directory set to `zomato_recommendation/zomato_frontend`
- [ ] `NEXT_PUBLIC_API_BASE_URL` set to Railway HTTPS URL
- [ ] Deploy succeeded
- [ ] Railway `ALLOWED_ORIGINS` updated with Vercel URL

### After deploy

- [ ] End-to-end search works from Vercel URL
- [ ] No CORS or mixed-content errors in browser console
- [ ] Railway logs show successful Groq responses

---

## Quick reference — final URLs

| Service | Platform | Example URL |
|---------|----------|-------------|
| Frontend | Vercel | `https://zomato-milestone1.vercel.app` |
| Backend API | Railway | `https://zomatomilestone1-production.up.railway.app` |
| Health check | Railway | `https://<railway-url>/api/health` |
| Recommend | Railway | `POST https://<railway-url>/api/recommend` |

---

## 10. Pausing when not in use

Stop billing and public access when you are not actively using the app. Backend and frontend are managed separately.

### Recommended combo

| Goal | Backend (Railway) | Frontend (Vercel) |
|------|-------------------|-------------------|
| Not using for weeks | **Remove deployment** | **Pause project** |
| Occasional use, lower cost | **Enable Serverless** | Leave running (Hobby tier is usually free at low traffic) |
| Prevent surprise bills | Set **usage limit** | Enable **Spend Management** → pause at limit |

Also consider revoking or rotating `GROQ_API_KEY` at [console.groq.com](https://console.groq.com/) so LLM usage cannot accrue if the API is accidentally left reachable.

---

### Backend — Railway

Railway has no one-click “pause”, but these options work:

#### Option A — Remove deployment (best for long idle periods)

Stops compute charges. Service config, env vars, and domain are kept.

1. [railway.app](https://railway.app) → your project → backend service
2. **Deployments** → **⋯** on the active deployment → **Remove**

**Resume:** **Deployments** → **⋯** on the latest deployment → **Redeploy**, or push to `main`.

#### Option B — Enable Serverless (auto-sleep when idle)

1. Service → **Settings** → **Deploy** → **Serverless**
2. Toggle **Enable Serverless**

The service sleeps after ~10 minutes with no outbound traffic. The next request wakes it (expect a short cold start; first hit may briefly return 502).

#### Option C — Usage limit (safety net)

1. Workspace → **Usage** → **Set usage limits**
2. Set an email alert and/or a hard limit

At the hard limit, Railway takes workloads offline for the rest of the billing cycle.

#### CLI (optional)

```bash
npm i -g @railway/cli
railway login
railway link          # select your project + service
railway down          # remove active deployment (same as Option A)
railway up            # redeploy when you want it back
```

Requires a [Railway account token](https://railway.app/account/tokens) or interactive `railway login`.

---

### Frontend — Vercel

#### Option A — Pause project (recommended)

Pauses production. Visitors see **503 DEPLOYMENT_PAUSED**.

**Dashboard**

1. [vercel.com](https://vercel.com) → project **zomato-milestone1**
2. **Settings**
3. Use **Pause** / **Resume Service** (banner appears when paused)

**REST API** (if the dashboard control is unavailable on your plan):

```bash
# Create a token at https://vercel.com/account/tokens
export VERCEL_TOKEN=your_token_here

curl -X POST \
  "https://api.vercel.com/v1/projects/<PROJECT_ID>/pause?teamId=<TEAM_ID>" \
  -H "Authorization: Bearer $VERCEL_TOKEN"
```

**Resume:** Project **Settings** → **Resume Service**, or:

```bash
curl -X POST \
  "https://api.vercel.com/v1/projects/<PROJECT_ID>/unpause?teamId=<TEAM_ID>" \
  -H "Authorization: Bearer $VERCEL_TOKEN"
```

#### Option B — Disconnect Git (deploys only)

Project → **Settings** → **Git** → **Disconnect**

This stops auto-deploys on push; the site stays live until you pause or delete the project.

#### CLI (optional)

```bash
npm i -g vercel
vercel login
vercel project ls
# Pause/unpause is primarily via dashboard or REST API (see above)
```

---

### Restore after pausing

| Step | Action |
|------|--------|
| 1 | Railway: redeploy latest deployment or push to `main` |
| 2 | Vercel: **Resume Service** in project settings |
| 3 | Confirm `NEXT_PUBLIC_API_BASE_URL` on Vercel still matches your Railway URL |
| 4 | Test: `curl https://zomatomilestone1-production.up.railway.app/api/health` |
| 5 | Open the Vercel URL and run a test search |
