// app/lib/api.ts
// Fetch wrapper for the Phase 5 Flask backend

import type { UserPreference, ApiResponse } from "@/app/types";

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:5001";

export async function fetchRecommendations(
  prefs: UserPreference
): Promise<ApiResponse> {
  let res: Response;
  try {
    res = await fetch(`${API_BASE}/api/recommend`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(prefs),
    });
  } catch {
    throw new Error(
      `Cannot reach the backend at ${API_BASE}. ` +
      `The Railway service may be down, restarting, or blocking this origin via CORS.`
    );
  }

  let data: unknown;
  try {
    data = await res.json();
  } catch {
    throw new Error(
      `Backend at ${API_BASE} returned an invalid response (HTTP ${res.status}). ` +
      `Check Railway deploy logs — the server may have run out of memory or crashed.`
    );
  }

  if (!res.ok) {
    const payload = data as { error?: string; message?: string };
    throw new Error(
      payload.error ??
        payload.message ??
        `Server error ${res.status}`
    );
  }

  return data as ApiResponse;
}

export async function checkHealth(): Promise<boolean> {
  try {
    const res = await fetch(`${API_BASE}/api/health`, { cache: "no-store" });
    return res.ok;
  } catch {
    return false;
  }
}
