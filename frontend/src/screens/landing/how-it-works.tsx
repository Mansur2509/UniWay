"use client";

import type { LucideIcon } from "lucide-react";
import { CalendarDays, ClipboardCheck, Compass, MapPinned, TrendingUp, UserCog } from "lucide-react";

import { useI18n, type TranslationKey } from "@/shared/i18n";
import { Card } from "@/shared/ui/card";
import { StaggerGroup } from "@/shared/ui/stagger-group";

const STEPS: Array<{ icon: LucideIcon; titleKey: TranslationKey; descriptionKey: TranslationKey }> = [
  { icon: UserCog, titleKey: "landing.howItWorks.step1.title", descriptionKey: "landing.howItWorks.step1.description" },
  { icon: Compass, titleKey: "landing.howItWorks.step2.title", descriptionKey: "landing.howItWorks.step2.description" },
  { icon: TrendingUp, titleKey: "landing.howItWorks.step3.title", descriptionKey: "landing.howItWorks.step3.description" },
  { icon: ClipboardCheck, titleKey: "landing.howItWorks.step4.title", descriptionKey: "landing.howItWorks.step4.description" },
  { icon: CalendarDays, titleKey: "landing.howItWorks.step5.title", descriptionKey: "landing.howItWorks.step5.description" }
];

export function HowItWorks() {
  const { t } = useI18n();

  return (
    <section className="relative overflow-hidden bg-surface py-16 sm:py-20" id="how-it-works">
      <div
        aria-hidden
        className="absolute inset-x-0 top-24 h-px bg-gradient-to-r from-transparent via-primary/25 to-transparent"
      />
      <div className="mx-auto w-full max-w-[90rem] px-4 sm:px-6 lg:px-8">
        <div className="grid gap-5 lg:grid-cols-[0.9fr_1.1fr] lg:items-end">
          <div>
            <p className="text-eyebrow text-primary-hover">{t("landing.howItWorks.eyebrow")}</p>
            <h2 className="text-display-condensed-sm mt-3 max-w-3xl">{t("landing.howItWorks.title")}</h2>
          </div>
          <div className="hidden items-center gap-3 rounded-sm border bg-card p-4 shadow-card lg:flex">
            <MapPinned aria-hidden className="size-5 text-event" />
            <span className="text-sm font-semibold text-muted-foreground">{t("landing.howItWorks.pathNote")}</span>
          </div>
        </div>

        <StaggerGroup className="relative mt-10 grid gap-4 md:grid-cols-5" staggerMs={70}>
          <div
            aria-hidden
            className="absolute left-[10%] right-[10%] top-8 hidden h-px bg-gradient-to-r from-primary via-accent to-info md:block"
          />
          {STEPS.map((step, index) => (
            <Card className="relative h-full overflow-hidden p-5" key={step.titleKey}>
              <div
                aria-hidden
                className="absolute right-0 top-0 h-24 w-24 translate-x-8 -translate-y-8 rounded-full bg-primary/10 blur-xl"
              />
              <div className="relative">
                <div className="flex items-center justify-between">
                  <div className="grid size-11 place-items-center rounded-sm border border-primary/25 bg-primary/10 text-primary-hover">
                    <step.icon aria-hidden className="size-5" />
                  </div>
                  <span className="text-display-condensed-sm text-4xl leading-none text-border">
                    {index + 1}
                  </span>
                </div>
                <h3 className="mt-5 text-sm font-semibold">{t(step.titleKey)}</h3>
                <p className="mt-2 text-sm leading-6 text-muted-foreground">{t(step.descriptionKey)}</p>
              </div>
            </Card>
          ))}
        </StaggerGroup>
      </div>
    </section>
  );
}
