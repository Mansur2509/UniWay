import type { NextConfig } from "next";
import { PHASE_DEVELOPMENT_SERVER } from "next/constants";

export default function nextConfig(phase: string): NextConfig {
  const isDevelopment = phase === PHASE_DEVELOPMENT_SERVER;
  let apiOrigin = "http://127.0.0.1:8000";
  try {
    apiOrigin = new URL(
      process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000/api/v1"
    ).origin;
  } catch {
    // The runtime env helper already falls back to local development. Keep the
    // build-time CSP equally predictable instead of widening connect-src.
  }

  const contentSecurityPolicy = [
    "default-src 'self'",
    "base-uri 'self'",
    "form-action 'self'",
    "frame-ancestors 'none'",
    "object-src 'none'",
    `script-src 'self' 'unsafe-inline'${isDevelopment ? " 'unsafe-eval'" : ""}`,
    "style-src 'self' 'unsafe-inline'",
    "img-src 'self' data: blob: https:",
    "font-src 'self' data:",
    `connect-src 'self' ${apiOrigin}${isDevelopment ? " ws: http: https:" : ""}`,
    "frame-src 'none'",
    "worker-src 'self' blob:",
    "manifest-src 'self'",
    ...(isDevelopment ? [] : ["upgrade-insecure-requests"])
  ].join("; ");

  const securityHeaders = [
    { key: "Content-Security-Policy", value: contentSecurityPolicy },
    { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
    { key: "X-Content-Type-Options", value: "nosniff" },
    { key: "X-Frame-Options", value: "DENY" },
    { key: "X-DNS-Prefetch-Control", value: "off" },
    { key: "Cross-Origin-Opener-Policy", value: "same-origin" },
    { key: "Cross-Origin-Resource-Policy", value: "same-site" },
    {
      key: "Permissions-Policy",
      value: "camera=(), microphone=(), geolocation=(), payment=(), usb=()"
    },
    ...(
      isDevelopment
        ? []
        : [
            {
              key: "Strict-Transport-Security",
              value: "max-age=31536000; includeSubDomains"
            }
          ]
    )
  ];

  return {
    compress: true,
    devIndicators: false,
    distDir: isDevelopment ? ".next-dev" : ".next",
    eslint: {
      ignoreDuringBuilds: true
    },
    async headers() {
      return [
        {
          source: "/:path*",
          headers: securityHeaders
        }
      ];
    },
    outputFileTracingRoot: process.cwd(),
    poweredByHeader: false,
    productionBrowserSourceMaps: false,
    reactStrictMode: true
  };
}
