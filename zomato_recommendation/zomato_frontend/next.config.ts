import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Allow both localhost and 127.0.0.1 in dev (Chrome vs Cursor browser)
  allowedDevOrigins: ["127.0.0.1", "localhost"],
};

export default nextConfig;
