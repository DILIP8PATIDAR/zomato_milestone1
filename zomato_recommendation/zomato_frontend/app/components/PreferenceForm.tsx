"use client";
// components/PreferenceForm.tsx
// User preference form: location dropdown, budget chips, cuisine, star rating, extras

import { useState, FormEvent } from "react";
import type { UserPreference } from "@/app/types";
import StarPicker from "./StarPicker";

interface PreferenceFormProps {
  onSubmit: (prefs: UserPreference) => void;
  loading: boolean;
  dimmed?: boolean;
  initialValues?: Partial<UserPreference>;
}

const BUDGET_OPTIONS: { label: string; value: UserPreference["budget"] }[] = [
  { label: "Low  ≤₹300",      value: "low" },
  { label: "Medium ₹301–800", value: "medium" },
  { label: "High  ₹800+",     value: "high" },
];

// All unique locations from the Zomato Bangalore dataset (title-cased)
const LOCATIONS = [
  "Banashankari",
  "Banaswadi",
  "Bannerghatta Road",
  "Basavanagudi",
  "Basaveshwara Nagar",
  "Bellandur",
  "Bommanahalli",
  "Brigade Road",
  "Brookefield",
  "Btm",
  "Central Bangalore",
  "Church Street",
  "City Market",
  "Commercial Street",
  "Cunningham Road",
  "Cv Raman Nagar",
  "Domlur",
  "East Bangalore",
  "Ejipura",
  "Electronic City",
  "Frazer Town",
  "Hbr Layout",
  "Hebbal",
  "Hennur",
  "Hosur Road",
  "Hsr",
  "Indiranagar",
  "Infantry Road",
  "Itpl Main Road, Whitefield",
  "Jalahalli",
  "Jayanagar",
  "Jeevan Bhima Nagar",
  "Jp Nagar",
  "Kaggadasapura",
  "Kalyan Nagar",
  "Kammanahalli",
  "Kanakapura Road",
  "Kengeri",
  "Koramangala",
  "Koramangala 1St Block",
  "Koramangala 2Nd Block",
  "Koramangala 3Rd Block",
  "Koramangala 4Th Block",
  "Koramangala 5Th Block",
  "Koramangala 6Th Block",
  "Koramangala 7Th Block",
  "Koramangala 8Th Block",
  "Kr Puram",
  "Kumaraswamy Layout",
  "Langford Town",
  "Lavelle Road",
  "Magadi Road",
  "Majestic",
  "Malleshwaram",
  "Marathahalli",
  "Mg Road",
  "Mysore Road",
  "Nagarbhavi",
  "Nagawara",
  "New Bel Road",
  "North Bangalore",
  "Old Airport Road",
  "Old Madras Road",
  "Peenya",
  "Race Course Road",
  "Rajajinagar",
  "Rajarajeshwari Nagar",
  "Rammurthy Nagar",
  "Residency Road",
  "Richmond Road",
  "Rt Nagar",
  "Sadashiv Nagar",
  "Sahakara Nagar",
  "Sanjay Nagar",
  "Sankey Road",
  "Sarjapur Road",
  "Seshadripuram",
  "Shanti Nagar",
  "Shivajinagar",
  "South Bangalore",
  "St. Marks Road",
  "Thippasandra",
  "Ulsoor",
  "Uttarahalli",
  "Varthur Main Road, Whitefield",
  "Vasanth Nagar",
  "Vijay Nagar",
  "West Bangalore",
  "Whitefield",
  "Wilson Garden",
  "Yelahanka",
  "Yeshwantpur",
];

export default function PreferenceForm({
  onSubmit,
  loading,
  dimmed = false,
  initialValues = {},
}: PreferenceFormProps) {
  const [location,  setLocation]  = useState(initialValues.location ?? "");
  const [budget,    setBudget]    = useState<UserPreference["budget"]>(
    initialValues.budget ?? "medium"
  );
  const [cuisine,   setCuisine]   = useState(initialValues.cuisine ?? "");
  const [minRating, setMinRating] = useState<number | null>(
    initialValues.min_rating ?? null
  );
  const [extras,    setExtras]    = useState(initialValues.additional_preferences ?? "");
  const [locError,  setLocError]  = useState("");

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!location) {
      setLocError("Please select a location.");
      return;
    }
    setLocError("");
    const prefs: UserPreference = {
      location,
      budget,
      cuisine:                location ? cuisine.trim() || undefined : undefined,
      min_rating:             minRating ?? undefined,
      additional_preferences: extras.trim() || undefined,
    };
    onSubmit(prefs);
  }

  return (
    <section
      className={`w-full max-w-2xl transition-opacity duration-500 ${
        dimmed ? "opacity-40 pointer-events-none select-none" : "opacity-100"
      }`}
    >
      <div className="glass-card p-8 space-y-6">
        {/* Header */}
        <div className="space-y-1">
          <h2 className="font-outfit font-bold text-headline-md" style={{ color: "#ffb3b1" }}>
            Find Your Craving
          </h2>
          <p className="text-body-md text-on-surface-variant font-inter">
            Describe the perfect meal, I&apos;ll do the rest.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5" noValidate>
          {/* ── Location Dropdown ── */}
          <div>
            <label
              htmlFor="location"
              className="block text-label-md text-on-surface-variant mb-1.5 font-inter"
            >
              📍 Location <span style={{ color: "#ffb3b1" }}>*</span>
            </label>

            <div className="relative">
              <select
                id="location"
                value={location}
                onChange={(e) => { setLocation(e.target.value); setLocError(""); }}
                aria-required="true"
                aria-describedby={locError ? "loc-error" : undefined}
                className="glass-input h-14 px-4 pr-10 text-body-md appearance-none cursor-pointer"
                style={{
                  background: "rgba(255,255,255,0.03)",
                  color: location ? "#f9dcda" : "#ab8987",
                }}
              >
                <option value="" disabled style={{ background: "#2c1b1b", color: "#ab8987" }}>
                  Select a neighbourhood…
                </option>
                {LOCATIONS.map((loc) => (
                  <option
                    key={loc}
                    value={loc}
                    style={{ background: "#2c1b1b", color: "#f9dcda" }}
                  >
                    {loc}
                  </option>
                ))}
              </select>

              {/* Custom chevron */}
              <span
                className="pointer-events-none absolute right-4 top-1/2 -translate-y-1/2 text-on-surface-variant text-sm"
                aria-hidden="true"
              >
                ▾
              </span>
            </div>

            {locError && (
              <p id="loc-error" role="alert" className="mt-1.5 text-label-sm" style={{ color: "#ffb4ab" }}>
                {locError}
              </p>
            )}
          </div>

          {/* ── Budget chips ── */}
          <div>
            <label className="block text-label-md text-on-surface-variant mb-2 font-inter">
              💰 Budget
            </label>
            <div className="flex flex-wrap gap-2" role="radiogroup" aria-label="Budget">
              {BUDGET_OPTIONS.map((opt) => (
                <button
                  key={opt.value}
                  type="button"
                  role="radio"
                  aria-checked={budget === opt.value}
                  onClick={() => setBudget(opt.value)}
                  className={`budget-chip ${budget === opt.value ? "active" : ""}`}
                >
                  {opt.label}
                </button>
              ))}
            </div>
          </div>

          {/* ── Cuisine + Rating ── */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label
                htmlFor="cuisine"
                className="block text-label-md text-on-surface-variant mb-1.5 font-inter"
              >
                🍜 Cuisine{" "}
                <span className="text-on-surface-variant text-label-sm">(optional)</span>
              </label>
              <input
                id="cuisine"
                type="text"
                value={cuisine}
                onChange={(e) => setCuisine(e.target.value)}
                placeholder="e.g. Italian, Chinese"
                className="glass-input h-14 px-4 text-body-md"
              />
            </div>

            <div>
              <label className="block text-label-md text-on-surface-variant mb-1.5 font-inter">
                ⭐ Min Rating{" "}
                <span className="text-on-surface-variant text-label-sm">(optional)</span>
              </label>
              <div className="glass-input h-14 px-4 flex items-center">
                <StarPicker value={minRating} onChange={setMinRating} />
              </div>
            </div>
          </div>

          {/* ── Additional Preferences ── */}
          <div>
            <label
              htmlFor="extras"
              className="block text-label-md text-on-surface-variant mb-1.5 font-inter"
            >
              💬 Additional Preferences{" "}
              <span className="text-on-surface-variant text-label-sm">(optional)</span>
            </label>
            <textarea
              id="extras"
              value={extras}
              onChange={(e) => setExtras(e.target.value)}
              placeholder="e.g. rooftop seating, family-friendly, quick service..."
              rows={3}
              className="glass-input px-4 py-3 text-body-md resize-none"
            />
          </div>

          {/* ── Submit ── */}
          <button
            type="submit"
            disabled={loading}
            className="btn-primary w-full h-14 text-body-lg tracking-wide flex items-center justify-center gap-3"
            aria-label="Find restaurants"
          >
            {loading ? (
              <>
                <span className="inline-block w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                SEARCHING...
              </>
            ) : (
              <>🔍 Find My Restaurant</>
            )}
          </button>
        </form>
      </div>
    </section>
  );
}
