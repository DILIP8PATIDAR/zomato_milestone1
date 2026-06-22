"use client";
// components/Navbar.tsx

export default function Navbar() {
  return (
    <header className="fixed top-0 w-full z-50 border-b border-white/10 flex justify-between items-center px-5 md:px-10 py-4"
      style={{ background: "rgba(30,15,15,0.85)", backdropFilter: "blur(12px)" }}>
      {/* Logo */}
      <div className="flex items-center gap-2">
        <span className="text-2xl">🍽️</span>
        <span
          className="font-outfit font-extrabold text-2xl tracking-tight"
          style={{ color: "#ffb3b1" }}
        >
          Zomato AI
        </span>
      </div>

      {/* Nav Icons */}
      <div className="flex items-center gap-3">
        <button
          className="p-2 rounded-full transition-all duration-300 hover:bg-white/10 text-on-surface-variant hover:text-primary"
          aria-label="Restaurants"
        >
          🍴
        </button>
        <button
          className="p-2 rounded-full transition-all duration-300 hover:bg-white/10 text-on-surface-variant hover:text-primary"
          aria-label="AI Features"
        >
          ✨
        </button>
      </div>
    </header>
  );
}
