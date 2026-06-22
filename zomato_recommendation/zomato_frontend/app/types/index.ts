// app/types/index.ts
// Shared TypeScript types for the Zomato AI Recommender frontend

export interface UserPreference {
  location: string;
  budget: "low" | "medium" | "high";
  cuisine?: string;
  min_rating?: number;
  additional_preferences?: string;
}

export interface Recommendation {
  rank: number;
  name: string;
  cuisine: string;
  rating: number;
  estimated_cost: string;
  explanation: string;
  votes?: number;
  online_order?: string;
  book_table?: string;
  rest_type?: string;
}

export interface ApiResponse {
  count: number;
  recommendations: Recommendation[];
}

export interface ApiError {
  error: string;
}

export type AppState =
  | { status: "idle" }
  | { status: "loading"; prefs: UserPreference }
  | { status: "results"; prefs: UserPreference; recommendations: Recommendation[]; count: number }
  | { status: "error"; message: string }
  | { status: "empty"; prefs: UserPreference };
