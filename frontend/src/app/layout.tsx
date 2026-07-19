import { Analytics } from "@vercel/analytics/next";
import type { Metadata, Viewport } from "next";
import { Inter, Source_Serif_4 } from "next/font/google";
import type { ReactNode } from "react";

import { AuthProvider } from "@/features/auth";
import { I18nProvider } from "@/shared/i18n/provider";
import { ThemeProvider } from "@/shared/theme/provider";
import { MotionProvider } from "@/shared/ui/motion-provider";

import "./globals.css";
import { AppGate } from "./app-gate";

const inter = Inter({
  subsets: ["latin", "cyrillic"],
  variable: "--font-inter",
  display: "swap"
});

const sourceSerif = Source_Serif_4({
  subsets: ["latin", "cyrillic"],
  variable: "--font-source-serif",
  display: "swap",
  weight: ["500", "600", "700"]
});

const shouldRenderVercelAnalytics = Boolean(process.env.VERCEL_ENV);

export const metadata: Metadata = {
  title: {
    default: "UniWay",
    template: "%s · UniWay"
  },
  description:
    "A calm academic workspace for admissions, events, exams, research, and student growth."
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  themeColor: "#f9f6f1"
};

export default function RootLayout({ children }: Readonly<{ children: ReactNode }>) {
  return (
    <html className={`${inter.variable} ${sourceSerif.variable}`} lang="en" suppressHydrationWarning>
      <body>
        <ThemeProvider>
          <I18nProvider>
            <AuthProvider>
              <MotionProvider>
                <AppGate>{children}</AppGate>
              </MotionProvider>
            </AuthProvider>
          </I18nProvider>
        </ThemeProvider>
        {shouldRenderVercelAnalytics ? <Analytics /> : null}
      </body>
    </html>
  );
}
