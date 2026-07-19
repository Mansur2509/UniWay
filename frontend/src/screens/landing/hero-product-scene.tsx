"use client";

import {
  CalendarClock,
  CheckCircle2,
  FileText,
  Globe2,
  GraduationCap,
  MapPinned,
  NotebookPen,
  Search,
  ShieldCheck,
  Ticket,
  WalletCards
} from "lucide-react";

import { useI18n } from "@/shared/i18n";
import { ParallaxLayer } from "@/shared/ui/parallax-layer";
import { TiltCard } from "@/shared/ui/tilt-card";

import { UNIVERSITY_COUNT_DISPLAY } from "./site-stats";

export function HeroProductScene() {
  const { t } = useI18n();

  return (
    <div className="landing-poster-frame relative mx-auto min-h-[34rem] w-full max-w-[28rem] sm:min-h-[42rem] sm:max-w-[44rem] lg:min-h-[48rem] lg:max-w-[52rem]">
      <div
        aria-hidden
        className="absolute -left-8 top-10 h-[78%] w-[62%] -rotate-6 bg-primary shadow-2xl shadow-black/30"
      />
      <div
        aria-hidden
        className="absolute bottom-10 right-0 h-[64%] w-[58%] rotate-6 bg-info/75 shadow-2xl shadow-black/20"
      />
      <div
        aria-hidden
        className="absolute left-8 top-20 h-[70%] w-[76%] border border-white/20"
      />

      <TiltCard className="absolute inset-x-4 top-10 z-20 sm:inset-x-10 lg:top-12" maxTiltDeg={6}>
        <div className="landing-poster-object animate-[landing-poster-enter_700ms_cubic-bezier(0.16,1,0.3,1)_both]">
          <div className="landing-poster-paper relative min-h-[29rem] overflow-hidden border border-border bg-surface p-5 text-foreground sm:min-h-[36rem] sm:p-7 lg:min-h-[39rem]">
            <span
              aria-hidden
              className="absolute -right-5 top-5 text-display-condensed text-[7rem] leading-none text-primary/[0.08] sm:text-[10rem]"
            >
              UNI
            </span>
            <div className="relative z-10 flex items-center justify-between gap-4 border-b border-foreground/15 pb-5">
              <div>
                <p className="text-eyebrow text-primary">{t("landing.hero.sceneCommand")}</p>
                <h3 className="mt-2 max-w-sm font-serif text-2xl font-semibold leading-tight sm:text-4xl">
                  {t("landing.hero.sceneNextMoveTitle")}
                </h3>
              </div>
              <div className="grid size-16 shrink-0 place-items-center border border-success/35 bg-success/15 text-success">
                <ShieldCheck aria-hidden className="size-8" />
              </div>
            </div>

            <div className="relative z-10 mt-6 grid gap-4 sm:grid-cols-[1.08fr_0.92fr]">
              <div className="border border-primary/30 bg-primary/10 p-4">
                <div className="flex items-center justify-between">
                  <div className="grid size-12 place-items-center bg-primary text-primary-foreground">
                    <GraduationCap aria-hidden className="size-6" />
                  </div>
                  <p className="text-display-condensed-sm text-5xl leading-none text-primary">
                    {UNIVERSITY_COUNT_DISPLAY}+
                  </p>
                </div>
                <p className="mt-5 text-sm font-bold uppercase tracking-[0.12em] text-primary-hover">
                  {t("landing.hero.sceneUniversities")}
                </p>
              </div>

              <div className="border bg-card p-4 shadow-card">
                <div className="flex items-center gap-2">
                  <Search aria-hidden className="size-5 text-info" />
                  <p className="text-sm font-semibold">{t("landing.hero.sceneSearch")}</p>
                </div>
                <div className="mt-4 space-y-2" aria-hidden>
                  <span className="block h-3 w-full bg-muted" />
                  <span className="block h-3 w-4/5 bg-muted" />
                  <span className="block h-9 border border-info/25 bg-info/10" />
                </div>
              </div>
            </div>

            <div className="relative z-10 mt-4 grid gap-4 sm:grid-cols-3">
              <div className="border bg-card p-4">
                <NotebookPen aria-hidden className="size-6 text-recommendation" />
                <p className="mt-4 text-sm font-semibold">{t("landing.hero.sceneEssays")}</p>
              </div>
              <div className="border bg-card p-4">
                <CalendarClock aria-hidden className="size-6 text-accent" />
                <p className="mt-4 text-sm font-semibold">{t("landing.hero.sceneNotification")}</p>
              </div>
              <div className="border bg-card p-4">
                <WalletCards aria-hidden className="size-6 text-success" />
                <p className="mt-4 text-sm font-semibold">{t("landing.hero.sceneScholarship")}</p>
              </div>
            </div>

            <div className="relative z-10 mt-5 border border-success/30 bg-success/10 p-4">
              <div className="flex items-center gap-3">
                <CheckCircle2 aria-hidden className="size-5 text-success" />
                <p className="text-sm font-semibold">{t("landing.hero.sceneVerified")}</p>
              </div>
              <div className="mt-4 grid grid-cols-5 gap-2" aria-hidden>
                {Array.from({ length: 10 }).map((_, index) => (
                  <span
                    className={index % 3 === 0 ? "h-2 bg-success/45" : "h-2 bg-foreground/15"}
                    key={index}
                  />
                ))}
              </div>
            </div>
          </div>
        </div>
      </TiltCard>

      <ParallaxLayer
        className="absolute -left-1 top-24 z-30 w-36 -rotate-[13deg] sm:left-0 sm:top-28 sm:w-44"
        depth={0.38}
      >
        <div className="border border-white/20 bg-navy p-4 text-white shadow-2xl shadow-black/35">
          <Globe2 aria-hidden className="size-7 text-info" />
          <p className="mt-5 text-sm font-semibold">{t("landing.hero.scenePlan")}</p>
        </div>
      </ParallaxLayer>

      <ParallaxLayer
        axis="y"
        className="absolute right-0 top-4 z-30 w-44 rotate-[9deg] sm:right-3 sm:w-56"
        depth={0.28}
      >
        <div className="border border-accent/35 bg-accent p-4 text-accent-foreground shadow-2xl shadow-accent/25">
          <div className="flex items-center justify-between">
            <Ticket aria-hidden className="size-6" />
            <span className="border border-current/30 px-2 py-1 text-[0.62rem] font-bold uppercase tracking-[0.14em]">
              {t("landing.hero.sceneTicketStatus")}
            </span>
          </div>
          <p className="mt-5 text-sm font-bold leading-5">{t("landing.hero.sceneTicket")}</p>
        </div>
      </ParallaxLayer>

      <ParallaxLayer
        className="absolute bottom-5 left-4 z-30 hidden w-52 -rotate-[8deg] border bg-card p-4 text-foreground shadow-2xl sm:block"
        depth={0.5}
      >
        <div className="flex items-center gap-3">
          <MapPinned aria-hidden className="size-6 text-event" />
          <FileText aria-hidden className="size-6 text-primary" />
        </div>
        <div className="mt-5 space-y-2" aria-hidden>
          <span className="block h-2 bg-muted" />
          <span className="block h-2 w-3/4 bg-muted" />
        </div>
      </ParallaxLayer>
    </div>
  );
}
