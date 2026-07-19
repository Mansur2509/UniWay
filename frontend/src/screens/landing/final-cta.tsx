"use client";

import Link from "next/link";
import { ArrowRight } from "lucide-react";

import { useI18n } from "@/shared/i18n";
import { Button } from "@/shared/ui/button";
import { MotionReveal } from "@/shared/ui/motion-reveal";

export function FinalCta() {
  const { t } = useI18n();

  return (
    <section className="relative isolate overflow-hidden bg-primary py-20 text-primary-foreground sm:py-24">
      <div
        aria-hidden
        className="absolute inset-0 -z-10 bg-[radial-gradient(circle_at_18%_28%,hsl(var(--accent)/0.34),transparent_25%),linear-gradient(135deg,hsl(var(--primary-hover)),hsl(var(--primary))_54%,hsl(var(--navy)))]"
      />
      <span
        aria-hidden
        className="absolute left-1/2 top-1/2 -z-10 -translate-x-1/2 -translate-y-1/2 text-display-condensed text-[18rem] leading-none text-white/[0.06] sm:text-[28rem]"
      >
        UNIWAY
      </span>
      <div className="mx-auto w-full max-w-[90rem] px-4 text-center sm:px-6 lg:px-8">
        <MotionReveal>
          <p className="text-eyebrow text-accent">{t("landing.finalCta.eyebrow")}</p>
          <h2 className="text-display-condensed-sm mx-auto mt-4 max-w-4xl text-primary-foreground">
            {t("landing.finalCta.title")}
          </h2>
          <p className="mx-auto mt-5 max-w-2xl text-base leading-7 text-white/[0.78]">
            {t("landing.finalCta.description")}
          </p>
          <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
            <Button asChild className="min-h-12 bg-white px-5 text-primary-hover hover:bg-white/90">
              <Link href="/register">
                {t("landing.hero.primaryCta")}
                <ArrowRight aria-hidden className="ml-2 size-4" />
              </Link>
            </Button>
            <Button asChild className="min-h-12 border-white/25 bg-white/[0.08] px-5 text-primary-foreground hover:bg-white/[0.14]" variant="secondary">
              <Link href="/login">{t("landing.hero.secondaryCta")}</Link>
            </Button>
          </div>
        </MotionReveal>
      </div>
    </section>
  );
}
