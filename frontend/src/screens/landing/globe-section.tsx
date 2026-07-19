"use client";

import { ArrowRight, Globe2, GraduationCap, MapPin, ShieldCheck } from "lucide-react";
import Link from "next/link";
import { useState } from "react";

import { useI18n, type TranslationKey } from "@/shared/i18n";
import { Button } from "@/shared/ui/button";
import { MotionReveal } from "@/shared/ui/motion-reveal";
import { usePrefersReducedMotion } from "@/shared/ui/use-reduced-motion";

import { UNIVERSITY_COUNT_DISPLAY } from "./site-stats";

type Destination = {
  id: string;
  countryKey: TranslationKey;
  regionKey: TranslationKey;
  detailKey: TranslationKey;
  href: string;
  markerClass: string;
};

const DESTINATIONS: Destination[] = [
  {
    id: "us",
    countryKey: "landing.globe.country.us",
    regionKey: "landing.globe.region.northAmerica",
    detailKey: "landing.globe.country.us.detail",
    href: "/universities?country=USA",
    markerClass: "left-[24%] top-[42%]"
  },
  {
    id: "uk",
    countryKey: "landing.globe.country.uk",
    regionKey: "landing.globe.region.europe",
    detailKey: "landing.globe.country.uk.detail",
    href: "/universities?country=United%20Kingdom",
    markerClass: "left-[49%] top-[33%]"
  },
  {
    id: "ca",
    countryKey: "landing.globe.country.ca",
    regionKey: "landing.globe.region.northAmerica",
    detailKey: "landing.globe.country.ca.detail",
    href: "/universities?country=Canada",
    markerClass: "left-[20%] top-[25%]"
  },
  {
    id: "sg",
    countryKey: "landing.globe.country.sg",
    regionKey: "landing.globe.region.asiaPacific",
    detailKey: "landing.globe.country.sg.detail",
    href: "/universities?country=Singapore",
    markerClass: "left-[70%] top-[62%]"
  },
  {
    id: "it",
    countryKey: "landing.globe.country.it",
    regionKey: "landing.globe.region.europe",
    detailKey: "landing.globe.country.it.detail",
    href: "/universities?country=Italy",
    markerClass: "left-[54%] top-[44%]"
  },
  {
    id: "kr",
    countryKey: "landing.globe.country.kr",
    regionKey: "landing.globe.region.asiaPacific",
    detailKey: "landing.globe.country.kr.detail",
    href: "/universities?country=South%20Korea",
    markerClass: "left-[79%] top-[43%]"
  }
];

export function GlobeSection() {
  const { t } = useI18n();
  const prefersReducedMotion = usePrefersReducedMotion();
  const [activeId, setActiveId] = useState(DESTINATIONS[0].id);
  const active = DESTINATIONS.find((destination) => destination.id === activeId) ?? DESTINATIONS[0];

  return (
    <section className="relative overflow-hidden bg-navy py-16 text-navy-foreground sm:py-20" id="global-path">
      <div
        aria-hidden
        className="absolute inset-0 bg-[radial-gradient(circle_at_24%_28%,hsl(var(--info)/0.25),transparent_30%),radial-gradient(circle_at_78%_56%,hsl(var(--primary)/0.28),transparent_28%)]"
      />
      <div className="relative mx-auto grid w-full max-w-[90rem] gap-10 px-4 sm:px-6 lg:grid-cols-[1.05fr_0.95fr] lg:items-center lg:px-8">
        <MotionReveal>
          <p className="text-eyebrow text-accent">{t("landing.globe.eyebrow")}</p>
          <h2 className="text-display-condensed-sm mt-3 max-w-3xl text-navy-foreground">
            {t("landing.globe.title")}
          </h2>
          <p className="mt-4 max-w-xl text-base leading-7 text-white/75">
            {t("landing.globe.description")}
          </p>

          <div className="mt-8 grid gap-3 sm:grid-cols-3">
            <div className="rounded-sm border border-white/15 bg-white/[0.06] p-4">
              <p className="text-display-condensed-sm text-4xl leading-none text-white">{UNIVERSITY_COUNT_DISPLAY}+</p>
              <p className="mt-2 text-xs font-semibold uppercase tracking-[0.14em] text-white/60">
                {t("landing.globe.statUniversities")}
              </p>
            </div>
            <div className="rounded-sm border border-white/15 bg-white/[0.06] p-4">
              <p className="text-display-condensed-sm text-4xl leading-none text-white">4</p>
              <p className="mt-2 text-xs font-semibold uppercase tracking-[0.14em] text-white/60">
                {t("landing.globe.statLanguages")}
              </p>
            </div>
            <div className="rounded-sm border border-white/15 bg-white/[0.06] p-4">
              <ShieldCheck aria-hidden className="size-8 text-success" />
              <p className="mt-2 text-xs font-semibold uppercase tracking-[0.14em] text-white/60">
                {t("landing.globe.statVerified")}
              </p>
            </div>
          </div>
        </MotionReveal>

        <MotionReveal delayMs={100}>
          <div className="rounded-sm border border-white/15 bg-white/[0.06] p-4 shadow-2xl shadow-black/30 backdrop-blur">
            <div className="grid gap-5 lg:grid-cols-[1fr_0.78fr] lg:items-center">
              <div className="relative mx-auto aspect-square w-full max-w-[29rem] overflow-hidden rounded-full border border-info/25 bg-[radial-gradient(circle_at_35%_35%,hsl(var(--info)/0.38),hsl(var(--navy))_58%,hsl(var(--navy)))] shadow-[inset_0_0_80px_rgba(255,255,255,0.08),0_30px_80px_rgba(0,0,0,0.35)]">
                <div
                  aria-hidden
                  className={`absolute inset-[10%] rounded-full border border-white/10 ${
                    prefersReducedMotion ? "" : "animate-[landing-globe-idle_38s_linear_infinite]"
                  }`}
                />
                <svg
                  aria-hidden
                  className="absolute inset-0 size-full text-white/[0.14]"
                  fill="none"
                  viewBox="0 0 400 400"
                >
                  <circle cx="200" cy="200" r="150" stroke="currentColor" strokeWidth="1" />
                  <ellipse cx="200" cy="200" rx="86" ry="150" stroke="currentColor" strokeWidth="1" />
                  <ellipse cx="200" cy="200" rx="150" ry="54" stroke="currentColor" strokeWidth="1" />
                  <path d="M72 140c56 28 201 28 256 0M72 260c56-28 201-28 256 0" stroke="currentColor" />
                  <path d="M108 98c48 55 48 150 0 204M292 98c-48 55-48 150 0 204" stroke="currentColor" />
                </svg>
                <div
                  aria-hidden
                  className="absolute inset-[18%] rounded-full border border-accent/20"
                />
                {DESTINATIONS.map((destination) => {
                  const selected = destination.id === active.id;
                  return (
                    <button
                      aria-label={t(destination.countryKey)}
                      className={`absolute ${destination.markerClass} grid -translate-x-1/2 -translate-y-1/2 place-items-center rounded-full border transition-transform hover:scale-110 focus-visible:scale-110 ${
                        selected
                          ? "size-8 border-accent bg-accent text-accent-foreground shadow-lg shadow-accent/30"
                          : "size-6 border-white/40 bg-white/[0.16] text-white"
                      }`}
                      key={destination.id}
                      onClick={() => setActiveId(destination.id)}
                      type="button"
                    >
                      <span
                        aria-hidden
                        className={`absolute inset-0 rounded-full border border-current ${
                          selected && !prefersReducedMotion ? "animate-[landing-orbit-pulse_1.9s_ease-in-out_infinite]" : ""
                        }`}
                      />
                      <MapPin aria-hidden className="size-3.5" />
                    </button>
                  );
                })}
              </div>

              <div className="rounded-sm border border-white/15 bg-navy/70 p-5">
                <div className="flex items-center gap-2 text-accent">
                  <Globe2 aria-hidden className="size-5" />
                  <p className="text-eyebrow">{t(active.regionKey)}</p>
                </div>
                <h3 className="mt-3 font-serif text-2xl font-semibold text-white">{t(active.countryKey)}</h3>
                <p className="mt-3 text-sm leading-6 text-white/[0.72]">{t(active.detailKey)}</p>
                <div className="mt-5 flex items-center gap-2 rounded-sm border border-success/25 bg-success/10 p-3 text-sm font-semibold text-white">
                  <GraduationCap aria-hidden className="size-4 text-success" />
                  {t("landing.globe.coverageNote")}
                </div>
                <Button asChild className="mt-5 w-full border-white/20 bg-white/[0.08] text-white hover:bg-white/[0.14]" variant="secondary">
                  <Link href={active.href}>
                    {t("landing.globe.cta")}
                    <ArrowRight aria-hidden className="ml-2 size-4" />
                  </Link>
                </Button>
              </div>
            </div>

            <div className="mt-5 flex flex-wrap gap-2" aria-label={t("landing.globe.countryTabsLabel")} role="group">
              {DESTINATIONS.map((destination) => (
                <button
                  className={`rounded-sm border px-3 py-2 text-xs font-bold uppercase tracking-[0.12em] ${
                    destination.id === active.id
                      ? "border-accent bg-accent text-accent-foreground"
                      : "border-white/15 bg-white/[0.05] text-white/[0.72] hover:bg-white/[0.1] hover:text-white"
                  }`}
                  key={destination.id}
                  onClick={() => setActiveId(destination.id)}
                  type="button"
                >
                  {t(destination.countryKey)}
                </button>
              ))}
            </div>
          </div>
        </MotionReveal>
      </div>
    </section>
  );
}
