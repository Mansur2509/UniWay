"use client";

import { ArrowRight, Sparkles } from "lucide-react";
import Link from "next/link";

import { useI18n } from "@/shared/i18n";
import { Button } from "@/shared/ui/button";
import { CountUp } from "@/shared/ui/count-up";
import { MotionReveal } from "@/shared/ui/motion-reveal";

import { HeroProductScene } from "./hero-product-scene";
import { UNIVERSITY_COUNT_DISPLAY } from "./site-stats";

export function HeroSection() {
  const { t } = useI18n();

  return (
    <section className="relative isolate overflow-hidden bg-navy text-navy-foreground">
      <div
        aria-hidden
        className="absolute inset-0 -z-10 bg-[radial-gradient(circle_at_18%_18%,hsl(var(--primary)/0.34),transparent_28%),radial-gradient(circle_at_82%_30%,hsl(var(--info)/0.24),transparent_26%),linear-gradient(135deg,hsl(var(--navy)),hsl(var(--navy)/0.9)_45%,hsl(var(--background))_180%)]"
      />
      <div
        aria-hidden
        className="absolute inset-x-0 bottom-0 -z-10 h-36 bg-gradient-to-b from-transparent to-background"
      />
      <div
        aria-hidden
        className="absolute left-1/2 top-16 -z-10 h-[42rem] w-[42rem] -translate-x-1/2 rounded-full border border-white/10"
      />

      <div className="mx-auto grid w-full max-w-[90rem] gap-10 px-4 py-16 sm:px-6 lg:grid-cols-[0.9fr_1.1fr] lg:items-center lg:px-8 lg:py-24 xl:py-28">
        <MotionReveal>
          <p className="text-eyebrow text-accent">{t("landing.hero.eyebrow")}</p>
          <h1 className="text-display-condensed mt-4 max-w-4xl text-navy-foreground">
            <span className="block">{t("landing.hero.titleLead")}</span>
            <span className="block text-primary-hover dark:text-primary">{t("landing.hero.titleAccent")}</span>
            <span className="block">{t("landing.hero.titleTail")}</span>
          </h1>
          <p className="mt-6 max-w-lg text-base leading-7 text-white/[0.76] sm:text-lg">
            {t("landing.hero.subtitle")}
          </p>
          <div className="mt-8 flex flex-wrap items-center gap-3">
            <Button asChild className="min-h-12 px-5 shadow-2xl shadow-primary/30">
              <Link href="/register">
                {t("landing.hero.primaryCta")}
                <ArrowRight aria-hidden className="ml-2 size-4" />
              </Link>
            </Button>
            <Button asChild className="min-h-12 border-white/25 bg-white/[0.08] px-5 text-navy-foreground hover:bg-white/[0.14]" variant="secondary">
              <Link href="/login">{t("landing.hero.secondaryCta")}</Link>
            </Button>
          </div>
          <div className="mt-10 grid gap-3 text-sm font-semibold text-white/[0.76] sm:grid-cols-[auto_auto] sm:items-center">
            <div className="flex items-center gap-2">
              <Sparkles aria-hidden className="size-4 text-accent" />
              <CountUp className="text-white" suffix="+" target={UNIVERSITY_COUNT_DISPLAY} />
              <span>{t("landing.trust.universitiesSuffix")}</span>
            </div>
            <span className="hidden h-px w-16 bg-white/20 sm:block" aria-hidden />
            <span>{t("landing.hero.dataNote")}</span>
          </div>
        </MotionReveal>

        <MotionReveal delayMs={120}>
          <HeroProductScene />
        </MotionReveal>
      </div>
    </section>
  );
}
