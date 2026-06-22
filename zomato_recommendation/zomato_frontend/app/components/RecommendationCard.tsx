"use client";
// components/RecommendationCard.tsx
// Displays a single AI restaurant recommendation with glassmorphism styling

import type { Recommendation } from "@/app/types";

interface Props {
  rec: Recommendation;
  index: number;
}

// Cuisine → accent color mapping
const CUISINE_COLORS: Record<string, string> = {
  italian:       "rgba(226,55,68,0.15)",
  chinese:       "rgba(238,194,0,0.15)",
  indian:        "rgba(74,225,118,0.15)",
  continental:   "rgba(255,179,177,0.12)",
  "south indian":"rgba(74,225,118,0.12)",
  mughlai:       "rgba(238,194,0,0.12)",
  default:       "rgba(255,255,255,0.08)",
};

function getCuisineColor(cuisine: string): string {
  const key = cuisine.toLowerCase().trim();
  return CUISINE_COLORS[key] ?? CUISINE_COLORS.default;
}

function renderStars(rating: number): string {
  const full  = Math.floor(rating);
  const half  = rating - full >= 0.5;
  const empty = 5 - full - (half ? 1 : 0);
  return "★".repeat(full) + (half ? "½" : "") + "☆".repeat(empty);
}

export default function RecommendationCard({ rec, index }: Props) {
  const cuisines = rec.cuisine.split(",").map((c) => c.trim()).filter(Boolean);
  const lowVotes = typeof rec.votes === "number" && rec.votes < 50;

  return (
    <article
      className="glass-card glass-card-hover overflow-hidden flex flex-col animate-slide-up"
      style={{ animationDelay: `${index * 100}ms` }}
    >
      {/* Rank banner */}
      <div
        className="px-6 pt-5 pb-3 flex items-start justify-between"
        style={{ borderBottom: "1px solid rgba(255,255,255,0.07)" }}
      >
        <span
          className="font-outfit font-extrabold text-display-lg-mobile leading-none opacity-60"
          style={{ color: "#ffb3b1" }}
        >
          #{rec.rank}
        </span>
        <div className="flex flex-col items-end gap-1">
          <span className="text-yellow-400 font-mono text-lg tracking-wider">
            {renderStars(rec.rating)}
          </span>
          <span className="text-label-md font-inter text-on-surface-variant">
            {rec.rating.toFixed(1)}
          </span>
        </div>
      </div>

      <div className="px-6 py-4 flex flex-col gap-4 flex-1">
        {/* Name */}
        <h3 className="font-outfit font-bold text-headline-md text-on-surface leading-tight">
          {rec.name}
        </h3>

        {/* Cuisine chips */}
        <div className="flex flex-wrap gap-2">
          {cuisines.map((c) => (
            <span
              key={c}
              className="chip"
              style={{ background: getCuisineColor(c) }}
            >
              🍜 {c}
            </span>
          ))}
          {rec.rest_type && (
            <span className="chip">{rec.rest_type}</span>
          )}
        </div>

        {/* Cost */}
        <div className="flex items-center gap-2">
          <span className="text-label-md font-inter text-on-surface-variant">Est. Cost:</span>
          <span className="text-label-md font-inter font-bold" style={{ color: "#4ae176" }}>
            💰 {rec.estimated_cost}
          </span>
        </div>

        {/* Divider */}
        <div className="border-t border-white/10" />

        {/* AI Explanation */}
        <p className="text-body-md font-inter text-on-surface-variant italic leading-relaxed flex-1">
          &ldquo;{rec.explanation}&rdquo;
        </p>

        {/* Badges */}
        <div className="flex flex-wrap gap-2 pt-1">
          {rec.online_order === "Yes" && (
            <span className="chip" style={{ background: "rgba(74,225,118,0.12)", color: "#4ae176" }}>
              📱 Online Order
            </span>
          )}
          {rec.book_table === "Yes" && (
            <span className="chip" style={{ background: "rgba(238,194,0,0.12)", color: "#eec200" }}>
              📅 Table Booking
            </span>
          )}
          {lowVotes && (
            <span className="chip" style={{ background: "rgba(255,180,0,0.12)", color: "#eec200" }}>
              ⚠️ Limited Reviews
            </span>
          )}
        </div>
      </div>
    </article>
  );
}
