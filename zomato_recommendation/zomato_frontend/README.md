# Zomato Frontend

Next.js UI for the Zomato AI Restaurant Recommender.

## Setup

```bash
npm install
cp .env.example .env.local
```

## Run

Start the Flask backend first (from `zomato_recommendation/`):

```bash
python3 api.py
```

Then start the frontend:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

The frontend talks to the backend at `http://localhost:5001` by default (configured in `.env.local`).

## Production (Vercel)

Deployed from this directory with root `zomato_recommendation/zomato_frontend`. Set `NEXT_PUBLIC_API_BASE_URL` to your Railway backend URL.

To pause or resume the live site, see [Pausing when not in use](../docs/deployment-plan.md#10-pausing-when-not-in-use) in the deployment plan.
