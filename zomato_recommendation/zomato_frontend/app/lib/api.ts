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
      `Ensure the Railway backend is deployed and CORS allows your Vercel domain.`
    );
  }

  const data = await res.json();

  if (!res.ok) {
    throw new Error(
      (data as { error?: string }).error ?? `Server error ${res.status}`
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
