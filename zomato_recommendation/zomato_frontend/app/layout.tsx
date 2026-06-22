import type { Metadata } from "next";
import { Outfit, Inter } from "next/font/google";
import "./globals.css";

const outfit = Outfit({
  subsets: ["latin"],
  variable: "--font-outfit",
  weight: ["400", "600", "700", "800"],
  display: "swap",
});

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  weight: ["400", "500", "600"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "Zomato AI — Find Your Perfect Restaurant",
  description:
    "AI-powered restaurant recommendations tailored to your taste. Enter your location, budget, and cuisine preferences to get personalized dining suggestions.",
  keywords: ["restaurant", "AI recommendations", "Zomato", "dining", "food"],
  openGraph: {
    title: "Zomato AI Recommender",
    description: "Find your perfect restaurant with AI",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className="dark" suppressHydrationWarning>
      <body
        className={`${outfit.variable} ${inter.variable} font-inter bg-background text-on-surface antialiased`}
        suppressHydrationWarning
      >
        {children}
      </body>
    </html>
  );
}
