"use client";

import { Languages, ShieldCheck } from "lucide-react";

import { useI18n } from "@/shared/i18n";
import { Card } from "@/shared/ui/card";
import { CountUp } from "@/shared/ui/count-up";
import { MotionReveal } from "@/shared/ui/motion-reveal";

import { UNIVERSITY_COUNT_DISPLAY } from "./site-stats";

export function TrustSection() {
  const { t } = useI18n();

  return (
    <section className="mx-auto w-full max-w-[90rem] px-4 py-14 sm:px-6 lg:px-8">
      <MotionReveal>
        <div className="flex flex-col gap-3 border-y py-6 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="text-eyebrow text-primary-hover">{t("landing.trust.eyebrow")}</p>
            <h2 className="text-display-condensed-sm mt-2 max-w-2xl">{t("landing.trust.supportTitle")}</h2>
          </div>
          <p className="max-w-xl text-sm leading-6 text-muted-foreground">{t("landing.trust.supportDescription")}</p>
        </div>
      </MotionReveal>
      <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <MotionReveal delayMs={0}>
          <Card className="relative flex h-full min-h-44 flex-col justify-end overflow-hidden border-primary/25 bg-primary text-primary-foreground text-center sm:text-left">
            <span aria-hidden className="absolute -right-6 -top-10 text-display-condensed-sm text-[9rem] leading-none text-white/10">
              U
            </span>
            <p className="text-display-condensed-sm text-6xl leading-none">
              <CountUp suffix="+" target={UNIVERSITY_COUNT_DISPLAY} />
            </p>
            <p className="mt-2 text-sm text-primary-foreground/80">{t("landing.trust.universitiesSuffix")}</p>
          </Card>
        </MotionReveal>
        <MotionReveal delayMs={60}>
          <Card className="flex h-full min-h-44 flex-col justify-end gap-1 border-info/25 bg-info/10 text-center sm:text-left">
            <p className="flex items-center justify-center gap-2 text-display-condensed-sm text-6xl leading-none sm:justify-start">
              <Languages aria-hidden className="size-6 text-info" />
              {t("landing.trust.languagesValue")}
            </p>
            <p className="text-sm text-muted-foreground">{t("landing.trust.languagesSuffix")}</p>
          </Card>
        </MotionReveal>
        <MotionReveal className="sm:col-span-2 lg:col-span-1" delayMs={120}>
          <Card className="flex h-full min-h-44 flex-col justify-end gap-2 border-success/25 bg-success/10">
            <div className="flex items-center gap-2">
              <ShieldCheck aria-hidden className="size-5 text-success" />
              <h2 className="text-sm font-semibold">{t("landing.trust.supportTitle")}</h2>
            </div>
            <p className="text-sm leading-6 text-muted-foreground">{t("landing.trust.supportDescription")}</p>
          </Card>
        </MotionReveal>
      </div>
    </section>
  );
}
