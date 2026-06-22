"use client";
// components/MobileNav.tsx
// Floating glass bottom navigation bar for mobile (hidden on md+)

export default function MobileNav() {
  const items = [
    { icon: "🧭", label: "Discover", active: true },
    { icon: "🕐", label: "History",  active: false },
    { icon: "❤️",  label: "Favorites", active: false },
    { icon: "👤", label: "Account",  active: false },
  ];

  return (
    <nav
      className="md:hidden fixed bottom-0 left-0 right-0 mb-5 mx-5 rounded-full z-50 flex justify-around items-center p-4"
      style={{
        background: "rgba(44,27,27,0.5)",
        backdropFilter: "blur(20px)",
        border: "1px solid rgba(255,255,255,0.1)",
      }}
      aria-label="Mobile navigation"
    >
      {items.map(({ icon, label, active }) => (
        <a
          key={label}
          href="#"
          className={`flex flex-col items-center justify-center gap-0.5 px-3 py-1 rounded-full transition-all ${
            active
              ? "text-primary bg-primary/10 active-tab-glow"
              : "text-on-surface-variant hover:text-primary"
          }`}
          aria-label={label}
          aria-current={active ? "page" : undefined}
        >
          <span className="text-xl">{icon}</span>
          <span className="text-label-sm font-inter">{label}</span>
        </a>
      ))}
    </nav>
  );
}
