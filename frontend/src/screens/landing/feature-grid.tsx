"use client";

import {
  BookOpenCheck,
  CalendarRange,
  ClipboardList,
  Compass,
  FileSearch,
  GraduationCap,
  MapPinned,
  Sparkles,
  UsersRound
} from "lucide-react";
import type { LucideIcon } from "lucide-react";

import { useI18n, type TranslationKey } from "@/shared/i18n";
import { Card } from "@/shared/ui/card";
import { StaggerGroup } from "@/shared/ui/stagger-group";

type FeatureTone = "success" | "recommendation" | "info" | "accent" | "event";

const TONE_CLASSES: Record<FeatureTone, string> = {
  success: "border-success/30 bg-success/10 text-success",
  recommendation: "border-recommendation/30 bg-recommendation/10 text-recommendation",
  info: "border-info/30 bg-info/10 text-info",
  accent: "border-accent/30 bg-accent/10 text-accent",
  event: "border-event/30 bg-event/10 text-event"
};

const FEATURES: Array<{
  icon: LucideIcon;
  tone: FeatureTone;
  titleKey: TranslationKey;
  descriptionKey: TranslationKey;
}> = [
  { icon: GraduationCap, tone: "success", titleKey: "landing.features.universityDatabase.title", descriptionKey: "landing.features.universityDatabase.description" },
  { icon: Sparkles, tone: "recommendation", titleKey: "landing.features.recommendations.title", descriptionKey: "landing.features.recommendations.description" },
  { icon: ClipboardList, tone: "info", titleKey: "landing.features.profileBuilding.title", descriptionKey: "landing.features.profileBuilding.description" },
  { icon: Compass, tone: "accent", titleKey: "landing.features.majorDiscovery.title", descriptionKey: "landing.features.majorDiscovery.description" },
  { icon: FileSearch, tone: "recommendation", titleKey: "landing.features.essayChecker.title", descriptionKey: "landing.features.essayChecker.description" },
  { icon: BookOpenCheck, tone: "info", titleKey: "landing.features.applicationTracker.title", descriptionKey: "landing.features.applicationTracker.description" },
  { icon: MapPinned, tone: "event", titleKey: "landing.features.eventMap.title", descriptionKey: "landing.features.eventMap.description" },
  { icon: CalendarRange, tone: "success", titleKey: "landing.features.examTools.title", descriptionKey: "landing.features.examTools.description" },
  { icon: UsersRound, tone: "accent", titleKey: "landing.features.organizerTools.title", descriptionKey: "landing.features.organizerTools.description" }
];

export function FeatureGrid() {
  const { t } = useI18n();

  return (
    <section className="mx-auto w-full max-w-[84rem] px-4 py-16 sm:px-6 lg:px-8" id="features">
      <div className="max-w-2xl">
        <p className="text-eyebrow text-primary-hover">{t("landing.features.eyebrow")}</p>
        <h2 className="text-feature-heading mt-2">{t("landing.features.title")}</h2>
        <p className="mt-3 text-sm leading-6 text-muted-foreground">{t("landing.features.description")}</p>
      </div>

      <StaggerGroup className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-3" staggerMs={50}>
        {FEATURES.map((feature) => (
          <Card className="h-full" interactive key={feature.titleKey}>
            <div className={`grid size-10 place-items-center rounded-sm border ${TONE_CLASSES[feature.tone]}`}>
              <feature.icon aria-hidden className="size-5" />
            </div>
            <h3 className="mt-4 text-sm font-semibold">{t(feature.titleKey)}</h3>
            <p className="mt-2 text-sm leading-6 text-muted-foreground">{t(feature.descriptionKey)}</p>
          </Card>
        ))}
      </StaggerGroup>
    </section>
  );
}
