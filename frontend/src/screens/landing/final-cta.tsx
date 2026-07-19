"use client";

import Link from "next/link";
import { ArrowRight } from "lucide-react";

import { useI18n } from "@/shared/i18n";
import { Button } from "@/shared/ui/button";
import { MotionReveal } from "@/shared/ui/motion-reveal";

export function FinalCta() {
  const { t } = useI18n();

  return (
    <section className="relative isolate overflow-hidden bg-primary py-24 text-primary-foreground sm:py-28 lg:py-32" id="final-cta">
      <div
        aria-hidden
        className="absolute inset-0 -z-10 bg-[linear-gradient(110deg,hsl(var(--primary-hover))_0_60%,hsl(var(--navy))_60%_100%)]"
      />
      <div aria-hidden className="absolute left-[8vw] top-0 -z-10 h-full w-24 -skew-x-12 bg-accent/75" />
      <span
        aria-hidden
        className="absolute left-1/2 top-1/2 -z-10 -translate-x-1/2 -translate-y-1/2 text-display-condensed text-[19rem] leading-none text-white/[0.07] sm:text-[34rem]"
      >
        UNIWAY
      </span>
      <div className="mx-auto w-full max-w-[104rem] px-4 text-center sm:px-6 lg:px-10">
        <MotionReveal>
          <p className="text-eyebrow text-accent">{t("landing.finalCta.eyebrow")}</p>
          <h2 className="text-display-condensed mx-auto mt-5 max-w-6xl text-primary-foreground">
            {t("landing.finalCta.title")}
          </h2>
          <p className="mx-auto mt-6 max-w-3xl text-lg leading-8 text-white/80">
            {t("landing.finalCta.description")}
          </p>
          <div className="mt-10 flex flex-wrap items-center justify-center gap-4">
            <Button asChild className="min-h-14 bg-white px-7 text-base text-primary-hover hover:bg-white/90">
              <Link href="/register">
                {t("landing.hero.primaryCta")}
                <ArrowRight aria-hidden className="ml-2 size-4" />
              </Link>
            </Button>
            <Button asChild className="min-h-14 border-white/25 bg-white/[0.1] px-7 text-base text-primary-foreground hover:bg-white/[0.16]" variant="secondary">
              <Link href="/login">{t("landing.hero.secondaryCta")}</Link>
            </Button>
          </div>
        </MotionReveal>
      </div>
    </section>
  );
}
