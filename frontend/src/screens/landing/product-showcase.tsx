"use client";

import { BookOpenCheck, ClipboardList, LayoutDashboard, MapPinned, School } from "lucide-react";
import type { LucideIcon } from "lucide-react";

import { useI18n, type TranslationKey } from "@/shared/i18n";
import { MotionReveal } from "@/shared/ui/motion-reveal";
import { TiltCard } from "@/shared/ui/tilt-card";

import { MockupFrame } from "./mockup-frame";

const SHOWCASE: Array<{
  icon: LucideIcon;
  tone: "success" | "info" | "event" | "accent" | "recommendation";
  titleKey: TranslationKey;
  descriptionKey: TranslationKey;
}> = [
  { icon: LayoutDashboard, tone: "accent", titleKey: "landing.showcase.dashboard.title", descriptionKey: "landing.showcase.dashboard.description" },
  { icon: School, tone: "success", titleKey: "landing.showcase.universities.title", descriptionKey: "landing.showcase.universities.description" },
  { icon: MapPinned, tone: "event", titleKey: "landing.showcase.events.title", descriptionKey: "landing.showcase.events.description" },
  { icon: ClipboardList, tone: "info", titleKey: "landing.showcase.applications.title", descriptionKey: "landing.showcase.applications.description" },
  { icon: BookOpenCheck, tone: "recommendation", titleKey: "landing.showcase.essays.title", descriptionKey: "landing.showcase.essays.description" }
];

const TONE_BAR: Record<(typeof SHOWCASE)[number]["tone"], string> = {
  success: "bg-success/35",
  info: "bg-info/35",
  event: "bg-event/35",
  accent: "bg-accent/35",
  recommendation: "bg-recommendation/35"
};

export function ProductShowcase() {
  const { t } = useI18n();

  return (
    <section className="mx-auto w-full max-w-[84rem] px-4 py-16 sm:px-6 lg:px-8">
      <div className="max-w-2xl">
        <p className="text-eyebrow text-primary-hover">{t("landing.showcase.eyebrow")}</p>
        <h2 className="text-feature-heading mt-2">{t("landing.showcase.title")}</h2>
      </div>

      <div className="mt-8 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
        {SHOWCASE.map((item, index) => (
          <MotionReveal delayMs={index * 60} key={item.titleKey}>
            <TiltCard maxTiltDeg={3}>
              <MockupFrame label={t(item.titleKey)}>
                <div className="space-y-2.5">
                  <div className="flex items-center gap-2">
                    <item.icon aria-hidden className="size-4 text-muted-foreground" />
                    <div className={`h-2 w-20 rounded-full ${TONE_BAR[item.tone]}`} />
                  </div>
                  <div className="h-1.5 w-full rounded-full bg-muted" />
                  <div className="h-1.5 w-2/3 rounded-full bg-muted" />
                </div>
              </MockupFrame>
              <p className="mt-3 text-sm leading-6 text-muted-foreground">{t(item.descriptionKey)}</p>
            </TiltCard>
          </MotionReveal>
        ))}
      </div>
    </section>
  );
}
