"use client";

import type { LucideIcon } from "lucide-react";
import { ClipboardCheck, Compass, TrendingUp, UserCog } from "lucide-react";

import { useI18n, type TranslationKey } from "@/shared/i18n";
import { Card } from "@/shared/ui/card";
import { StaggerGroup } from "@/shared/ui/stagger-group";

const STEPS: Array<{ icon: LucideIcon; titleKey: TranslationKey; descriptionKey: TranslationKey }> = [
  { icon: UserCog, titleKey: "landing.howItWorks.step1.title", descriptionKey: "landing.howItWorks.step1.description" },
  { icon: Compass, titleKey: "landing.howItWorks.step2.title", descriptionKey: "landing.howItWorks.step2.description" },
  { icon: TrendingUp, titleKey: "landing.howItWorks.step3.title", descriptionKey: "landing.howItWorks.step3.description" },
  { icon: ClipboardCheck, titleKey: "landing.howItWorks.step4.title", descriptionKey: "landing.howItWorks.step4.description" }
];

export function HowItWorks() {
  const { t } = useI18n();

  return (
    <section className="bg-surface py-16" id="how-it-works">
      <div className="mx-auto w-full max-w-[84rem] px-4 sm:px-6 lg:px-8">
        <div className="max-w-2xl">
          <p className="text-eyebrow text-primary-hover">{t("landing.howItWorks.eyebrow")}</p>
          <h2 className="text-feature-heading mt-2">{t("landing.howItWorks.title")}</h2>
        </div>

        <StaggerGroup className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4" staggerMs={70}>
          {STEPS.map((step, index) => (
            <Card className="relative h-full" key={step.titleKey}>
              <span className="absolute right-4 top-4 font-serif text-3xl font-semibold text-border">
                {index + 1}
              </span>
              <div className="grid size-10 place-items-center rounded-sm border border-primary/25 bg-primary/10 text-primary-hover">
                <step.icon aria-hidden className="size-5" />
              </div>
              <h3 className="mt-4 text-sm font-semibold">{t(step.titleKey)}</h3>
              <p className="mt-2 text-sm leading-6 text-muted-foreground">{t(step.descriptionKey)}</p>
            </Card>
          ))}
        </StaggerGroup>
      </div>
    </section>
  );
}
