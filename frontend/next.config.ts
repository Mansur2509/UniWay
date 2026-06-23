import type { NextConfig } from "next";
import { PHASE_DEVELOPMENT_SERVER } from "next/constants";

export default function nextConfig(phase: string): NextConfig {
  return {
    devIndicators: false,
    distDir: phase === PHASE_DEVELOPMENT_SERVER ? ".next-dev" : ".next",
    eslint: {
      ignoreDuringBuilds: true
    },
    outputFileTracingRoot: process.cwd(),
    poweredByHeader: false,
    reactStrictMode: true
  };
}
