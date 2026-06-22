"use client";
// components/ResultsSection.tsx
// Renders the results grid, loading skeletons, empty state, and error state

import type { Recommendation, UserPreference } from "@/app/types";
import RecommendationCard from "./RecommendationCard";
import SkeletonCard from "./SkeletonCard";

interface Props {
  status: "loading" | "results" | "error" | "empty";
  recommendations?: Recommendation[];
  count?: number;
  prefs?: UserPreference;
  errorMessage?: string;
  onReset: () => void;
}

export default function ResultsSection({
  status,
  recommendations = [],
  count = 0,
  prefs,
  errorMessage,
  onReset,
}: Props) {
  // ── Loading state ──
  if (status === "loading") {
    return (
      <section className="w-full animate-fade-in" aria-live="polite" aria-label="Loading results">
        {/* Spinner + message */}
        <div className="flex flex-col items-center mb-10 gap-4">
          <div className="animate-pulse text-5xl" style={{ color: "#ffb3b1" }}>✨</div>
          <p className="font-outfit font-bold text-headline-md text-on-surface">
            🤖 AI is finding your best matches...
          </p>
        </div>

        {/* Skeleton grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[0, 1, 2].map((i) => (
            <SkeletonCard key={i} delay={i * 200} />
          ))}
        </div>
      </section>
    );
  }

  // ── Error state ──
  if (status === "error") {
    return (
      <section className="w-full flex flex-col items-center py-16 gap-6 animate-fade-in" aria-live="polite">
        <div className="text-6xl">⚠️</div>
        <h3 className="font-outfit font-bold text-headline-md text-on-surface">
          Something went wrong
        </h3>
        <p className="text-body-md text-on-surface-variant text-center max-w-md">
          {errorMessage ?? "An unexpected error occurred. Please try again."}
        </p>
        <button
          onClick={onReset}
          className="budget-chip text-body-md px-6 py-3"
          style={{ borderColor: "#E23744", color: "#ffb3b1" }}
        >
          Try Again
        </button>
      </section>
    );
  }

  // ── Empty state ──
  if (status === "empty") {
    return (
      <section className="w-full flex flex-col items-center py-16 gap-6 animate-fade-in" aria-live="polite">
        <div className="text-6xl">🔍</div>
        <h3 className="font-outfit font-bold text-headline-md text-on-surface">
          No restaurants found
        </h3>
        <p className="text-body-md text-on-surface-variant text-center max-w-md">
          Try removing the cuisine filter, choosing a broader budget, or searching
          in a different location.
        </p>
        <button
          onClick={onReset}
          className="budget-chip text-body-md px-6 py-3"
          style={{ borderColor: "#E23744", color: "#ffb3b1" }}
        >
          Adjust Filters
        </button>
      </section>
    );
  }

  // ── Results ──
  const metaText = [
    `${count} restaurant${count !== 1 ? "s" : ""} found`,
    prefs?.location && `in ${prefs.location}`,
    prefs?.budget && `· ${prefs.budget} budget`,
    prefs?.cuisine && `· ${prefs.cuisine}`,
  ]
    .filter(Boolean)
    .join(" ");

  return (
    <section className="w-full animate-fade-in" aria-live="polite" aria-label="Recommendations">
      {/* Section header */}
      <div className="mb-8">
        <h2 className="font-outfit font-bold text-headline-lg text-on-surface mb-1">
          Your Top Picks 🍽️
        </h2>
        <p className="text-label-md text-on-surface-variant font-inter">{metaText}</p>
      </div>

      {/* Cards grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {recommendations.map((rec, i) => (
          <RecommendationCard key={rec.rank} rec={rec} index={i} />
        ))}
      </div>

      {/* Search again */}
      <div className="mt-10 flex justify-center">
        <button
          onClick={onReset}
          className="budget-chip text-body-md px-8 py-3"
        >
          🔄 Search Again
        </button>
      </div>
    </section>
  );
}
