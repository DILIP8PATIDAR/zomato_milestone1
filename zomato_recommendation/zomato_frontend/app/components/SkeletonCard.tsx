"use client";
// components/SkeletonCard.tsx
// Animated loading placeholder that matches the real recommendation card layout

export default function SkeletonCard({ delay = 0 }: { delay?: number }) {
  return (
    <div
      className="glass-card overflow-hidden"
      style={{ animationDelay: `${delay}ms` }}
    >
      {/* Image placeholder */}
      <div className="h-48 skeleton-shimmer w-full" />

      <div className="p-6 space-y-4">
        {/* Rank + Name */}
        <div className="flex items-center gap-3">
          <div className="h-8 w-8 skeleton-shimmer rounded-full" />
          <div className="h-6 skeleton-shimmer w-3/5 rounded" />
        </div>

        {/* Cuisine chips */}
        <div className="flex gap-2">
          <div className="h-6 skeleton-shimmer w-20 rounded-full" />
          <div className="h-6 skeleton-shimmer w-24 rounded-full" />
        </div>

        {/* Rating + cost */}
        <div className="flex justify-between items-center">
          <div className="h-5 skeleton-shimmer w-24 rounded" />
          <div className="h-5 skeleton-shimmer w-20 rounded" />
        </div>

        {/* Explanation lines */}
        <div className="space-y-2">
          <div className="h-4 skeleton-shimmer w-full rounded" />
          <div className="h-4 skeleton-shimmer w-5/6 rounded" />
          <div className="h-4 skeleton-shimmer w-4/6 rounded" />
        </div>

        {/* Badges */}
        <div className="flex gap-2 pt-2">
          <div className="h-7 skeleton-shimmer w-28 rounded-full" />
          <div className="h-7 skeleton-shimmer w-28 rounded-full" />
        </div>
      </div>
    </div>
  );
}
