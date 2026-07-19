"use client";

import {
  Bell,
  CalendarClock,
  CheckCircle2,
  FileText,
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
    <div className="relative mx-auto min-h-[23rem] w-full max-w-[22rem] sm:min-h-[32rem] sm:max-w-[35rem] lg:min-h-[36rem]">
      <div
        aria-hidden
        className="absolute inset-6 rounded-full bg-[radial-gradient(circle_at_center,hsl(var(--info)/0.28),transparent_58%)] blur-2xl"
      />
      <div
        aria-hidden
        className="absolute right-0 top-8 h-44 w-44 rounded-full border border-info/20 bg-info/10 blur-sm"
      />
      <div
        aria-hidden
        className="absolute bottom-6 left-0 h-40 w-40 rounded-full border border-primary/25 bg-primary/15 blur-sm"
      />

      <ParallaxLayer className="absolute left-2 top-4 z-0 hidden w-44 rotate-[-9deg] sm:block" depth={0.45}>
        <div className="rounded-sm border border-white/15 bg-navy/80 p-4 text-navy-foreground shadow-2xl shadow-black/30">
          <div className="flex items-center justify-between">
            <div className="grid size-9 place-items-center rounded-sm border border-info/40 bg-info/20 text-info">
              <GraduationCap aria-hidden className="size-4" />
            </div>
            <span className="text-display-condensed-sm text-2xl leading-none text-white">
              {UNIVERSITY_COUNT_DISPLAY}+
            </span>
          </div>
          <p className="mt-4 text-xs font-semibold uppercase tracking-[0.16em] text-white/55">
            {t("landing.hero.sceneUniversities")}
          </p>
        </div>
      </ParallaxLayer>

      <ParallaxLayer axis="y" className="absolute right-6 top-0 z-20 w-48 rotate-[5deg] sm:right-0 sm:w-60 sm:rotate-[7deg]" depth={0.28}>
        <div className="rounded-sm border border-white/20 bg-card p-4 text-foreground shadow-2xl shadow-black/25 dark:bg-elevated">
          <div className="flex items-start justify-between gap-3">
            <div>
              <p className="text-[0.65rem] font-bold uppercase tracking-[0.18em] text-primary">
                {t("landing.hero.sceneProfile")}
              </p>
              <p className="mt-2 text-sm font-semibold">{t("landing.hero.sceneProfileTitle")}</p>
            </div>
            <ShieldCheck aria-hidden className="size-5 text-success" />
          </div>
          <div className="mt-4 space-y-2">
            <div className="h-2 rounded-full bg-muted">
              <div className="h-2 w-[78%] rounded-full bg-success" />
            </div>
            <div className="grid grid-cols-3 gap-2">
              <span className="h-7 rounded-sm border border-success/25 bg-success/10" />
              <span className="h-7 rounded-sm border border-info/25 bg-info/10" />
              <span className="h-7 rounded-sm border border-primary/25 bg-primary/10" />
            </div>
          </div>
        </div>
      </ParallaxLayer>

      <TiltCard className="absolute left-1/2 top-20 z-10 w-[18rem] -translate-x-1/2 sm:w-[24rem]" maxTiltDeg={5}>
        <div className="overflow-hidden rounded-sm border border-white/20 bg-card text-foreground shadow-[0_30px_80px_rgba(0,0,0,0.42)] dark:bg-card">
          <div className="flex items-center justify-between border-b bg-elevated px-4 py-3">
            <div className="flex items-center gap-2">
              <span className="size-2 rounded-full bg-danger" />
              <span className="size-2 rounded-full bg-warning" />
              <span className="size-2 rounded-full bg-success" />
            </div>
            <span className="text-[0.65rem] font-bold uppercase tracking-[0.16em] text-muted-foreground">
              {t("landing.hero.sceneCommand")}
            </span>
          </div>
          <div className="grid gap-3 p-4">
            <div className="rounded-sm border bg-surface p-4">
              <div className="flex items-center justify-between gap-3">
                <div>
                  <p className="text-[0.65rem] font-bold uppercase tracking-[0.16em] text-primary">
                    {t("landing.hero.sceneNextMove")}
                  </p>
                  <p className="mt-2 text-sm font-semibold">{t("landing.hero.sceneNextMoveTitle")}</p>
                </div>
                <CalendarClock aria-hidden className="size-6 text-accent" />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="rounded-sm border border-info/30 bg-info/10 p-3">
                <Search aria-hidden className="size-4 text-info" />
                <p className="mt-3 text-xs font-semibold">{t("landing.hero.sceneSearch")}</p>
              </div>
              <div className="rounded-sm border border-primary/30 bg-primary/10 p-3">
                <NotebookPen aria-hidden className="size-4 text-primary" />
                <p className="mt-3 text-xs font-semibold">{t("landing.hero.sceneEssays")}</p>
              </div>
            </div>
            <div className="flex items-center gap-2 rounded-sm border border-success/30 bg-success/10 p-3">
              <CheckCircle2 aria-hidden className="size-4 text-success" />
              <span className="text-xs font-semibold">{t("landing.hero.sceneVerified")}</span>
            </div>
          </div>
        </div>
      </TiltCard>

      <ParallaxLayer className="absolute bottom-3 left-2 z-20 w-44 rotate-[-6deg] sm:bottom-12 sm:left-6 sm:w-48 sm:rotate-[-7deg]" depth={0.32}>
        <div className="rounded-sm border border-primary/25 bg-primary p-4 text-primary-foreground shadow-2xl shadow-primary/25">
          <div className="flex items-center justify-between">
            <Ticket aria-hidden className="size-5" />
            <span className="rounded-sm border border-white/20 px-2 py-1 text-[0.62rem] font-bold uppercase tracking-[0.16em]">
              {t("landing.hero.sceneTicketStatus")}
            </span>
          </div>
          <p className="mt-5 text-sm font-semibold">{t("landing.hero.sceneTicket")}</p>
          <div className="mt-4 grid grid-cols-5 gap-1" aria-hidden>
            {Array.from({ length: 15 }).map((_, index) => (
              <span className="h-2 rounded-[1px] bg-white/45" key={index} />
            ))}
          </div>
        </div>
      </ParallaxLayer>

      <ParallaxLayer axis="y" className="absolute bottom-0 right-2 z-0 hidden w-56 rotate-[5deg] sm:block" depth={0.2}>
        <div className="rounded-sm border bg-card p-4 shadow-xl dark:bg-elevated">
          <div className="flex items-center gap-2">
            <WalletCards aria-hidden className="size-4 text-accent" />
            <p className="text-xs font-bold uppercase tracking-[0.14em] text-muted-foreground">
              {t("landing.hero.sceneScholarship")}
            </p>
          </div>
          <div className="mt-3 space-y-2" aria-hidden>
            <div className="h-2 rounded-full bg-accent/35" />
            <div className="h-2 w-2/3 rounded-full bg-muted" />
          </div>
        </div>
      </ParallaxLayer>

      <ParallaxLayer className="absolute right-10 top-64 z-30 hidden w-48 rotate-[11deg] sm:block" depth={0.5}>
        <div className="rounded-sm border border-info/30 bg-info p-3 text-info-foreground shadow-xl shadow-info/25">
          <div className="flex items-center gap-2">
            <Bell aria-hidden className="size-4" />
            <p className="text-xs font-bold">{t("landing.hero.sceneNotification")}</p>
          </div>
        </div>
      </ParallaxLayer>

      <ParallaxLayer className="absolute bottom-24 right-16 z-30 hidden w-40 rotate-[-10deg] lg:block" depth={0.38}>
        <div className="rounded-sm border bg-card p-3 shadow-xl dark:bg-elevated">
          <div className="flex items-center gap-2">
            <MapPinned aria-hidden className="size-4 text-event" />
            <FileText aria-hidden className="size-4 text-primary" />
          </div>
          <p className="mt-3 text-xs font-semibold">{t("landing.hero.scenePlan")}</p>
        </div>
      </ParallaxLayer>
    </div>
  );
}
