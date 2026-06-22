# Zomato AI Restaurant Recommender

AI-powered restaurant recommendations using the Zomato dataset (Hugging Face) and Groq LLM.

## Project structure

```
zomato_recommendation/          # Python backend (Flask API + recommendation engine)
zomato_recommendation/zomato_frontend/   # Next.js frontend
```

## Prerequisites

- Python 3.10+
- Node.js 18+
- [Groq API key](https://console.groq.com/)

## Setup

### 1. Backend

```bash
cd zomato_recommendation
python3 -m pip install -r requirements.txt
cp .env.example .env
# Edit .env and set GROQ_API_KEY
```

### 2. Frontend

```bash
cd zomato_recommendation/zomato_frontend
npm install
cp .env.example .env.local
```

## Run locally

**Terminal 1 — Backend (port 5001):**

```bash
cd zomato_recommendation
python3 api.py
```

**Terminal 2 — Frontend (port 3000):**

```bash
cd zomato_recommendation/zomato_frontend
npm run dev
```

Open **http://localhost:3000** in your browser.

> **Note:** The backend uses port **5001** (not 5000) because macOS reserves 5000 for AirPlay Receiver. The Hugging Face dataset is cached under `zomato_recommendation/.cache/huggingface/`.

## API endpoints

| Method | Endpoint           | Description              |
|--------|----------------------|--------------------------|
| GET    | `/api/health`        | Health check             |
| POST   | `/api/recommend`     | Get recommendations      |

## Tests

```bash
cd zomato_recommendation
python3 -m pip install -r requirements-dev.txt
python3 -m pytest
```
