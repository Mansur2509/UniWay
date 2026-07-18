"use client";

import { useI18n } from "@/shared/i18n";
import { usePrefersReducedMotion } from "@/shared/ui/use-reduced-motion";

import { MARQUEE_UNIVERSITIES } from "./university-marquee-data";

export function UniversityMarquee() {
  const { t } = useI18n();
  const prefersReducedMotion = usePrefersReducedMotion();
  // Under reduced motion, render a single real (non-duplicated) wrapped row
  // instead of the two aria-hidden tracks -- duplicating the list is only
  // meaningful to create the seamless scroll illusion.
  const items = prefersReducedMotion
    ? MARQUEE_UNIVERSITIES
    : [...MARQUEE_UNIVERSITIES, ...MARQUEE_UNIVERSITIES];

  return (
    <section className="border-y bg-surface py-10">
      <div className="mx-auto w-full max-w-[84rem] px-4 sm:px-6 lg:px-8">
        <p className="text-eyebrow text-center text-muted-foreground">{t("landing.marquee.eyebrow")}</p>
      </div>

      <div className="group relative mt-6 overflow-hidden [mask-image:linear-gradient(to_right,transparent,black_8%,black_92%,transparent)]">
        <div
          className={
            prefersReducedMotion
              ? "flex flex-wrap justify-center gap-3 px-4"
              : "flex w-max animate-[landing-marquee-scroll_45s_linear_infinite] gap-3 group-hover:[animation-play-state:paused] group-focus-within:[animation-play-state:paused]"
          }
        >
          {items.map((name, index) => (
            <span
              aria-hidden={!prefersReducedMotion && index >= MARQUEE_UNIVERSITIES.length}
              className="shrink-0 rounded-sm border bg-card px-4 py-2 text-sm font-semibold text-muted-foreground shadow-card"
              key={`${name}-${index}`}
            >
              {name}
            </span>
          ))}
        </div>
      </div>

      <div className="mx-auto mt-6 w-full max-w-[84rem] px-4 sm:px-6 lg:px-8">
        <p className="text-center text-xs leading-5 text-muted-foreground">{t("landing.marquee.description")}</p>
        <p className="sr-only">
          {t("landing.marquee.srIntro")} {MARQUEE_UNIVERSITIES.join(", ")}.
        </p>
      </div>
    </section>
  );
}
