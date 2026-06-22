"use client";
// components/StarPicker.tsx
// Interactive 5-star rating picker

import { useState } from "react";

interface StarPickerProps {
  value: number | null;
  onChange: (rating: number | null) => void;
}

export default function StarPicker({ value, onChange }: StarPickerProps) {
  const [hovered, setHovered] = useState<number | null>(null);

  const display = hovered ?? value;

  return (
    <div className="flex items-center gap-1" role="group" aria-label="Minimum star rating">
      {[1, 2, 3, 4, 5].map((star) => {
        const filled = display !== null && star <= display;
        return (
          <button
            key={star}
            type="button"
            aria-label={`${star} star${star > 1 ? "s" : ""}`}
            className={`star-btn ${filled ? "filled" : ""}`}
            onMouseEnter={() => setHovered(star)}
            onMouseLeave={() => setHovered(null)}
            onClick={() => {
              // Clicking same star again clears it
              if (value === star) onChange(null);
              else onChange(star);
            }}
          >
            {filled ? "★" : "☆"}
          </button>
        );
      })}
      {value !== null && (
        <span className="ml-2 text-sm text-on-surface-variant font-inter">
          {value}.0+
        </span>
      )}
    </div>
  );
}
