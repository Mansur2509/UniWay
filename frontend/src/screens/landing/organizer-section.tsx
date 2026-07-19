"use client";

import { Bell, CheckSquare, ClipboardType, Download, QrCode, ShieldCheck, Ticket } from "lucide-react";
import type { LucideIcon } from "lucide-react";
import Link from "next/link";

import { useI18n, type TranslationKey } from "@/shared/i18n";
import { Button } from "@/shared/ui/button";
import { MotionReveal } from "@/shared/ui/motion-reveal";
import { TiltCard } from "@/shared/ui/tilt-card";

const CAPABILITIES: Array<{ icon: LucideIcon; key: TranslationKey }> = [
  { icon: ClipboardType, key: "landing.organizer.capability1" },
  { icon: CheckSquare, key: "landing.organizer.capability2" },
  { icon: ShieldCheck, key: "landing.organizer.capability3" },
  { icon: Ticket, key: "landing.organizer.capability4" },
  { icon: Download, key: "landing.organizer.capability5" },
  { icon: Bell, key: "landing.organizer.capability6" }
];

export function OrganizerSection() {
  const { t } = useI18n();

  return (
    <section className="relative overflow-hidden bg-navy py-16 text-navy-foreground sm:py-20" id="organizers">
      <div
        aria-hidden
        className="absolute inset-0 bg-[radial-gradient(circle_at_20%_40%,hsl(var(--event)/0.25),transparent_30%),radial-gradient(circle_at_74%_20%,hsl(var(--info)/0.2),transparent_28%)]"
      />
      <div className="relative mx-auto grid w-full max-w-[90rem] gap-10 px-4 sm:px-6 lg:grid-cols-[0.92fr_1.08fr] lg:items-center lg:px-8">
        <MotionReveal>
          <p className="text-eyebrow text-event">{t("landing.organizer.eyebrow")}</p>
          <h2 className="text-display-condensed-sm mt-3 max-w-2xl text-navy-foreground">
            {t("landing.organizer.title")}
          </h2>
          <p className="mt-4 max-w-xl text-sm leading-6 text-white/[0.74]">{t("landing.organizer.description")}</p>

          <ul className="mt-7 grid gap-3 sm:grid-cols-2">
            {CAPABILITIES.map((item) => (
              <li className="flex items-center gap-2.5 text-sm font-semibold text-white/90" key={item.key}>
                <item.icon aria-hidden className="size-4 shrink-0 text-event" />
                {t(item.key)}
              </li>
            ))}
          </ul>

          <Button asChild className="mt-8 border-white/20 bg-white/[0.08] text-white hover:bg-white/[0.14]" variant="secondary">
            <Link href="/events">{t("landing.organizer.cta")}</Link>
          </Button>
        </MotionReveal>

        <MotionReveal delayMs={100}>
          <TiltCard maxTiltDeg={3}>
            <div className="relative min-h-[28rem] overflow-hidden rounded-sm border border-white/15 bg-white/[0.06] p-5 shadow-2xl shadow-black/30">
              <div className="absolute right-6 top-6 rounded-sm border border-success/30 bg-success/10 px-3 py-2 text-xs font-bold uppercase tracking-[0.14em] text-success">
                {t("landing.organizer.liveLabel")}
              </div>

              <div className="max-w-md rounded-sm border bg-card p-5 text-foreground shadow-2xl dark:bg-elevated">
                <div className="flex items-center justify-between border-b pb-3">
                  <div>
                    <p className="text-[0.65rem] font-bold uppercase tracking-[0.16em] text-event">
                      {t("landing.organizer.sceneDraft")}
                    </p>
                    <p className="mt-2 text-sm font-semibold">{t("landing.organizer.sceneDraftTitle")}</p>
                  </div>
                  <ClipboardType aria-hidden className="size-5 text-event" />
                </div>
                <div className="mt-4 grid gap-3">
                  <div className="rounded-sm border bg-surface p-3">
                    <div className="h-2 w-28 rounded-full bg-muted" />
                    <div className="mt-3 h-9 rounded-sm border border-info/25 bg-info/10" />
                  </div>
                  <div className="rounded-sm border bg-surface p-3">
                    <div className="h-2 w-20 rounded-full bg-muted" />
                    <div className="mt-3 grid grid-cols-3 gap-2">
                      <span className="h-8 rounded-sm border border-primary/25 bg-primary/10" />
                      <span className="h-8 rounded-sm border border-success/25 bg-success/10" />
                      <span className="h-8 rounded-sm border border-accent/25 bg-accent/10" />
                    </div>
                  </div>
                </div>
              </div>

              <div className="absolute bottom-8 right-5 w-56 rotate-[5deg] rounded-sm border border-white/15 bg-navy p-4 text-white shadow-2xl shadow-black/30 sm:right-8">
                <div className="flex items-center justify-between">
                  <Ticket aria-hidden className="size-5 text-event" />
                  <span className="rounded-sm border border-white/20 px-2 py-1 text-[0.62rem] font-bold uppercase tracking-[0.14em]">
                    {t("landing.organizer.sceneTicketStatus")}
                  </span>
                </div>
                <div className="mt-5 grid grid-cols-[auto_1fr] gap-3">
                  <div className="grid size-16 grid-cols-4 gap-1 rounded-sm border border-white/20 p-2" aria-hidden>
                    {Array.from({ length: 16 }).map((_, index) => (
                      <span className={index % 3 === 0 ? "bg-white" : "bg-white/35"} key={index} />
                    ))}
                  </div>
                  <div>
                    <p className="text-sm font-semibold">{t("landing.organizer.sceneTicketTitle")}</p>
                    <p className="mt-2 text-xs leading-5 text-white/[0.62]">{t("landing.organizer.sceneTicketDescription")}</p>
                  </div>
                </div>
              </div>

              <div className="absolute bottom-20 left-4 w-48 -rotate-[7deg] rounded-sm border bg-card p-4 text-foreground shadow-xl dark:bg-elevated sm:left-8">
                <div className="flex items-center gap-2">
                  <QrCode aria-hidden className="size-4 text-info" />
                  <p className="text-xs font-bold uppercase tracking-[0.13em] text-muted-foreground">
                    {t("landing.organizer.sceneCheckIn")}
                  </p>
                </div>
                <div className="mt-3 h-2 rounded-full bg-info/30" />
                <div className="mt-2 h-2 w-2/3 rounded-full bg-muted" />
              </div>

              <div className="absolute right-12 top-28 hidden w-48 rotate-[8deg] rounded-sm border border-accent/25 bg-accent p-4 text-accent-foreground shadow-xl shadow-accent/20 sm:block">
                <Download aria-hidden className="size-5" />
                <p className="mt-4 text-sm font-semibold">{t("landing.organizer.sceneExport")}</p>
              </div>
            </div>
          </TiltCard>
        </MotionReveal>
      </div>
    </section>
  );
}
