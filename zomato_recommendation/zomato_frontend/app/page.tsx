"use client";
// app/page.tsx
// Main page — orchestrates form → API → results state machine

import { useState, useRef, useCallback } from "react";
import Navbar from "./components/Navbar";
import MobileNav from "./components/MobileNav";
import PreferenceForm from "./components/PreferenceForm";
import ResultsSection from "./components/ResultsSection";
import { fetchRecommendations } from "./lib/api";
import type { AppState, UserPreference } from "./types";

export default function Home() {
  const [appState, setAppState] = useState<AppState>({ status: "idle" });
  const resultsRef = useRef<HTMLDivElement>(null);

  const handleSubmit = useCallback(async (prefs: UserPreference) => {
    setAppState({ status: "loading", prefs });

    // Smooth scroll down to where results will appear
    setTimeout(() => {
      resultsRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
    }, 200);

    try {
      const data = await fetchRecommendations(prefs);

      if (data.count === 0 || data.recommendations.length === 0) {
        setAppState({ status: "empty", prefs });
      } else {
        setAppState({
          status: "results",
          prefs,
          recommendations: data.recommendations,
          count: data.count,
        });
      }
    } catch (err: unknown) {
      const message =
        err instanceof Error ? err.message : "Unexpected error occurred.";
      setAppState({ status: "error", message });
    }

    // Scroll to results after state update
    setTimeout(() => {
      resultsRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
    }, 100);
  }, []);

  const handleReset = useCallback(() => {
    setAppState({ status: "idle" });
    window.scrollTo({ top: 0, behavior: "smooth" });
  }, []);

  const isLoading = appState.status === "loading";
  const showForm  = appState.status === "idle" || appState.status === "loading";
  const showResults =
    appState.status === "loading" ||
    appState.status === "results" ||
    appState.status === "error" ||
    appState.status === "empty";

  return (
    <>
      <Navbar />

      <main className="min-h-screen pt-24 pb-32 px-5 md:px-10 flex flex-col items-center gap-12">

        {/* ── Hero ── */}
        {appState.status === "idle" && (
          <div className="text-center max-w-2xl animate-fade-in">
            <p className="text-5xl mb-4">🍽️</p>
            <h1
              className="font-outfit font-extrabold text-display-lg-mobile md:text-display-lg leading-tight mb-3"
              style={{ color: "#f9dcda" }}
            >
              Find Your Perfect{" "}
              <span style={{ color: "#ffb3b1" }}>Restaurant</span>
            </h1>
            <p className="text-body-lg text-on-surface-variant font-inter">
              AI-powered picks tailored to your taste, location, and budget.
            </p>
          </div>
        )}

        {/* ── Preference Form ── */}
        {showForm && (
          <PreferenceForm
            onSubmit={handleSubmit}
            loading={isLoading}
            dimmed={isLoading}
            initialValues={
              "prefs" in appState ? appState.prefs : {}
            }
          />
        )}

        {/* ── Results / Loading / Error / Empty ── */}
        {showResults && (
          <div ref={resultsRef} className="w-full max-w-6xl">
            <ResultsSection
              status={appState.status as "loading" | "results" | "error" | "empty"}
              recommendations={
                appState.status === "results" ? appState.recommendations : []
              }
              count={appState.status === "results" ? appState.count : 0}
              prefs={"prefs" in appState ? appState.prefs : undefined}
              errorMessage={appState.status === "error" ? appState.message : undefined}
              onReset={handleReset}
            />
          </div>
        )}

        {/* ── "How it works" — only on idle ── */}
        {appState.status === "idle" && (
          <section className="w-full max-w-3xl animate-fade-in">
            <h2 className="font-outfit font-bold text-headline-md text-center mb-8" style={{ color: "#ffb3b1" }}>
              How It Works
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {[
                { icon: "📍", title: "Tell Us Your Vibe", desc: "Enter location, budget, and cuisine preferences." },
                { icon: "🤖", title: "AI Does the Work",   desc: "Our Groq-powered LLM ranks and explains the best matches." },
                { icon: "🍽️",  title: "Enjoy Your Meal",  desc: "Pick from top-rated, personalised restaurant picks." },
              ].map(({ icon, title, desc }) => (
                <div key={title} className="glass-card p-6 text-center space-y-3">
                  <div className="text-4xl">{icon}</div>
                  <h3 className="font-outfit font-bold text-body-lg text-on-surface">{title}</h3>
                  <p className="text-body-md text-on-surface-variant font-inter">{desc}</p>
                </div>
              ))}
            </div>
          </section>
        )}
      </main>

      <MobileNav />
    </>
  );
}
