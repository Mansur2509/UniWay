"use client";

import {
  BookOpenCheck,
  CalendarRange,
  CheckCircle2,
  ClipboardList,
  Compass,
  FileSearch,
  GraduationCap,
  MapPinned,
  Search,
  Sparkles,
  UsersRound
} from "lucide-react";
import type { LucideIcon } from "lucide-react";

import { cn } from "@/shared/lib/cn";
import { useI18n, type TranslationKey } from "@/shared/i18n";
import { Card } from "@/shared/ui/card";
import { MotionReveal } from "@/shared/ui/motion-reveal";

type FeatureTone = "success" | "recommendation" | "info" | "accent" | "event" | "primary";
type FeatureVisual = "search" | "recommendation" | "profile" | "major" | "essay" | "applications" | "event" | "exams" | "organizer";

const TONE_CLASSES: Record<FeatureTone, string> = {
  success: "border-success/35 bg-success/10 text-success",
  recommendation: "border-recommendation/35 bg-recommendation/10 text-recommendation",
  info: "border-info/35 bg-info/10 text-info",
  accent: "border-accent/35 bg-accent/10 text-accent",
  event: "border-event/35 bg-event/10 text-event",
  primary: "border-primary/35 bg-primary/10 text-primary"
};

const FEATURES: Array<{
  icon: LucideIcon;
  tone: FeatureTone;
  visual: FeatureVisual;
  titleKey: TranslationKey;
  descriptionKey: TranslationKey;
  className?: string;
}> = [
  {
    icon: GraduationCap,
    tone: "success",
    visual: "search",
    titleKey: "landing.features.universityDatabase.title",
    descriptionKey: "landing.features.universityDatabase.description",
    className: "lg:col-span-2"
  },
  {
    icon: Sparkles,
    tone: "recommendation",
    visual: "recommendation",
    titleKey: "landing.features.recommendations.title",
    descriptionKey: "landing.features.recommendations.description"
  },
  {
    icon: BookOpenCheck,
    tone: "info",
    visual: "applications",
    titleKey: "landing.features.applicationTracker.title",
    descriptionKey: "landing.features.applicationTracker.description",
    className: "lg:row-span-2"
  },
  {
    icon: ClipboardList,
    tone: "primary",
    visual: "profile",
    titleKey: "landing.features.profileBuilding.title",
    descriptionKey: "landing.features.profileBuilding.description"
  },
  {
    icon: FileSearch,
    tone: "recommendation",
    visual: "essay",
    titleKey: "landing.features.essayChecker.title",
    descriptionKey: "landing.features.essayChecker.description"
  },
  {
    icon: MapPinned,
    tone: "event",
    visual: "event",
    titleKey: "landing.features.eventMap.title",
    descriptionKey: "landing.features.eventMap.description",
    className: "lg:col-span-2"
  },
  {
    icon: CalendarRange,
    tone: "success",
    visual: "exams",
    titleKey: "landing.features.examTools.title",
    descriptionKey: "landing.features.examTools.description"
  },
  {
    icon: Compass,
    tone: "accent",
    visual: "major",
    titleKey: "landing.features.majorDiscovery.title",
    descriptionKey: "landing.features.majorDiscovery.description"
  },
  {
    icon: UsersRound,
    tone: "event",
    visual: "organizer",
    titleKey: "landing.features.organizerTools.title",
    descriptionKey: "landing.features.organizerTools.description",
    className: "lg:col-span-2"
  }
];

function FeatureVisual({ visual, tone }: { visual: FeatureVisual; tone: FeatureTone }) {
  const chipClass = TONE_CLASSES[tone];

  if (visual === "search") {
    return (
      <div className="mt-6 rounded-sm border bg-surface p-3">
        <div className="flex items-center gap-2 rounded-sm border bg-card px-3 py-2">
          <Search aria-hidden className="size-4 text-muted-foreground" />
          <span className="h-2 w-32 rounded-full bg-muted" />
          <span className="ml-auto h-6 w-16 rounded-sm bg-primary/15" />
        </div>
        <div className="mt-3 grid gap-2 sm:grid-cols-3">
          {["bg-success/15", "bg-info/15", "bg-accent/15"].map((className) => (
            <span className={cn("h-16 rounded-sm border", className)} key={className} />
          ))}
        </div>
      </div>
    );
  }

  if (visual === "applications") {
    return (
      <div className="mt-6 space-y-3">
        {[0, 1, 2, 3].map((index) => (
          <div className="flex items-center gap-3 rounded-sm border bg-surface p-3" key={index}>
            <span className={cn("grid size-8 place-items-center rounded-sm border", index === 0 ? "border-primary/30 bg-primary/10 text-primary" : chipClass)}>
              <CheckCircle2 aria-hidden className="size-4" />
            </span>
            <span className="h-2 flex-1 rounded-full bg-muted" />
          </div>
        ))}
      </div>
    );
  }

  if (visual === "event") {
    return (
      <div className="mt-6 grid gap-3 sm:grid-cols-[1.1fr_0.9fr]">
        <div className="relative min-h-32 overflow-hidden rounded-sm border bg-navy">
          <div className="absolute left-8 top-8 size-24 rounded-full border border-info/25 bg-info/10" />
          <div className="absolute right-8 top-10 size-20 rounded-full border border-event/25 bg-event/15" />
          <MapPinned aria-hidden className="absolute left-1/2 top-1/2 size-8 -translate-x-1/2 -translate-y-1/2 text-event" />
        </div>
        <div className="rounded-sm border bg-surface p-3">
          <div className="h-2 w-24 rounded-full bg-event/30" />
          <div className="mt-4 h-2 rounded-full bg-muted" />
          <div className="mt-2 h-2 w-2/3 rounded-full bg-muted" />
        </div>
      </div>
    );
  }

  return (
    <div className="mt-6 grid grid-cols-3 gap-2" aria-hidden>
      {[0, 1, 2, 3, 4, 5].map((index) => (
        <span
          className={cn(
            "h-12 rounded-sm border",
            index % 3 === 0 ? "bg-primary/10" : index % 3 === 1 ? "bg-info/10" : "bg-accent/10"
          )}
          key={index}
        />
      ))}
    </div>
  );
}

export function FeatureGrid() {
  const { t } = useI18n();

  return (
    <section className="mx-auto w-full max-w-[90rem] px-4 py-16 sm:px-6 sm:py-20 lg:px-8" id="features">
      <div className="grid gap-5 lg:grid-cols-[0.85fr_1.15fr] lg:items-end">
        <div>
          <p className="text-eyebrow text-primary-hover">{t("landing.features.eyebrow")}</p>
          <h2 className="text-display-condensed-sm mt-3 max-w-3xl">{t("landing.features.title")}</h2>
        </div>
        <p className="max-w-2xl text-sm leading-6 text-muted-foreground lg:justify-self-end">
          {t("landing.features.description")}
        </p>
      </div>

      <div className="mt-10 grid gap-4 sm:grid-cols-2 lg:grid-cols-4 lg:auto-rows-[minmax(18rem,auto)]">
        {FEATURES.map((feature, index) => (
          <MotionReveal className={feature.className} delayMs={index * 45} key={feature.titleKey}>
            <Card
              className="group relative h-full overflow-hidden p-5 transition-transform hover:-translate-y-1"
              interactive
            >
              <div
                aria-hidden
                className="absolute right-0 top-0 h-32 w-32 translate-x-10 -translate-y-10 rounded-full bg-primary/10 blur-2xl transition-opacity group-hover:opacity-100"
              />
              <div className="relative">
                <div className={`grid size-10 place-items-center rounded-sm border ${TONE_CLASSES[feature.tone]}`}>
                  <feature.icon aria-hidden className="size-5" />
                </div>
                <h3 className="mt-4 text-base font-semibold">{t(feature.titleKey)}</h3>
                <p className="mt-2 text-sm leading-6 text-muted-foreground">{t(feature.descriptionKey)}</p>
                <FeatureVisual tone={feature.tone} visual={feature.visual} />
              </div>
            </Card>
          </MotionReveal>
        ))}
      </div>
    </section>
  );
}
