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
    <section className="mx-auto w-full max-w-[84rem] px-4 py-14 sm:px-6 lg:px-8">
      <MotionReveal>
        <p className="text-eyebrow text-primary-hover">{t("landing.trust.eyebrow")}</p>
      </MotionReveal>
      <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <MotionReveal delayMs={0}>
          <Card className="flex h-full flex-col justify-center gap-1 text-center sm:text-left">
            <p className="text-3xl font-serif font-semibold">
              <CountUp suffix="+" target={UNIVERSITY_COUNT_DISPLAY} />
            </p>
            <p className="text-sm text-muted-foreground">{t("landing.trust.universitiesSuffix")}</p>
          </Card>
        </MotionReveal>
        <MotionReveal delayMs={60}>
          <Card className="flex h-full flex-col justify-center gap-1 text-center sm:text-left">
            <p className="flex items-center justify-center gap-2 text-3xl font-serif font-semibold sm:justify-start">
              <Languages aria-hidden className="size-6 text-info" />
              {t("landing.trust.languagesValue")}
            </p>
            <p className="text-sm text-muted-foreground">{t("landing.trust.languagesSuffix")}</p>
          </Card>
        </MotionReveal>
        <MotionReveal className="sm:col-span-2 lg:col-span-1" delayMs={120}>
          <Card className="flex h-full flex-col gap-2">
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
