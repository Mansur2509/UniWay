"use client";

import { CalendarClock, GraduationCap, MapPinned, Sparkles } from "lucide-react";
import Link from "next/link";

import { useI18n } from "@/shared/i18n";
import { Button } from "@/shared/ui/button";
import { CountUp } from "@/shared/ui/count-up";
import { MotionReveal } from "@/shared/ui/motion-reveal";
import { ParallaxLayer } from "@/shared/ui/parallax-layer";
import { TiltCard } from "@/shared/ui/tilt-card";

import { MockupFrame } from "./mockup-frame";
import { UNIVERSITY_COUNT_DISPLAY } from "./site-stats";

export function HeroSection() {
  const { t } = useI18n();

  return (
    <section className="relative overflow-hidden bg-gradient-to-b from-navy via-navy to-background text-navy-foreground">
      <div className="mx-auto grid w-full max-w-[84rem] gap-10 px-4 py-16 sm:px-6 lg:grid-cols-[1.1fr_0.9fr] lg:items-center lg:px-8 lg:py-24">
        <MotionReveal>
          <p className="text-eyebrow text-accent">{t("landing.hero.eyebrow")}</p>
          <h1 className="text-display mt-3 max-w-2xl text-navy-foreground">{t("landing.hero.title")}</h1>
          <p className="mt-5 max-w-xl text-base leading-7 text-white/75">{t("landing.hero.subtitle")}</p>
          <div className="mt-8 flex flex-wrap items-center gap-3">
            <Button asChild size="default">
              <Link href="/register">{t("landing.hero.primaryCta")}</Link>
            </Button>
            <Button asChild className="border-white/25 bg-transparent text-navy-foreground hover:bg-white/10" variant="secondary">
              <Link href="/login">{t("landing.hero.secondaryCta")}</Link>
            </Button>
          </div>
          <div className="mt-10 flex items-center gap-2 text-sm font-semibold text-white/70">
            <Sparkles aria-hidden className="size-4 text-accent" />
            <CountUp className="text-white" durationMs={1200} suffix="+" target={UNIVERSITY_COUNT_DISPLAY} />
            <span>{t("landing.trust.universitiesSuffix")}</span>
          </div>
        </MotionReveal>

        <MotionReveal delayMs={120}>
          <div className="relative mx-auto max-w-md">
            <TiltCard maxTiltDeg={4}>
              <MockupFrame className="relative z-10" label={t("landing.hero.mockupDashboardLabel")}>
                <div className="space-y-3">
                  <div className="flex items-center gap-2">
                    <GraduationCap aria-hidden className="size-4 text-recommendation" />
                    <div className="h-2 w-32 rounded-full bg-muted" />
                  </div>
                  <div className="grid grid-cols-2 gap-2">
                    <div className="rounded-sm border border-success/30 bg-success/10 p-2.5">
                      <div className="h-1.5 w-12 rounded-full bg-success/40" />
                      <div className="mt-2 h-2 w-16 rounded-full bg-success/30" />
                    </div>
                    <div className="rounded-sm border border-info/30 bg-info/10 p-2.5">
                      <div className="h-1.5 w-12 rounded-full bg-info/40" />
                      <div className="mt-2 h-2 w-16 rounded-full bg-info/30" />
                    </div>
                  </div>
                  <div className="flex items-center gap-2 rounded-sm border border-accent/30 bg-accent/10 p-2.5">
                    <CalendarClock aria-hidden className="size-4 text-accent" />
                    <div className="h-2 w-24 rounded-full bg-accent/30" />
                  </div>
                </div>
              </MockupFrame>
            </TiltCard>

            <ParallaxLayer className="absolute -left-8 top-10 z-0 hidden w-40 rotate-[-6deg] sm:block" depth={0.35}>
              <MockupFrame label={t("landing.hero.mockupProfileLabel")}>
                <div className="space-y-2">
                  <div className="h-1.5 w-full rounded-full bg-recommendation/30" />
                  <div className="h-1.5 w-3/4 rounded-full bg-muted" />
                  <div className="h-1.5 w-1/2 rounded-full bg-muted" />
                </div>
              </MockupFrame>
            </ParallaxLayer>

            <ParallaxLayer axis="y" className="absolute -right-6 -bottom-8 z-0 hidden w-36 rotate-[7deg] sm:block" depth={0.25}>
              <MockupFrame label={t("landing.hero.mockupUniversitiesLabel")}>
                <div className="flex items-center gap-2">
                  <MapPinned aria-hidden className="size-4 text-event" />
                  <div className="h-1.5 w-16 rounded-full bg-event/30" />
                </div>
              </MockupFrame>
            </ParallaxLayer>
          </div>
        </MotionReveal>
      </div>
    </section>
  );
}
