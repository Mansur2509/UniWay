"use client";

import { Bell, CheckSquare, ClipboardType, Download, ShieldCheck, Ticket } from "lucide-react";
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
    <section className="mx-auto w-full max-w-[84rem] px-4 py-16 sm:px-6 lg:px-8" id="organizers">
      <div className="grid gap-10 lg:grid-cols-[1fr_0.9fr] lg:items-center">
        <MotionReveal>
          <p className="text-eyebrow text-event">{t("landing.organizer.eyebrow")}</p>
          <h2 className="text-feature-heading mt-2 max-w-xl">{t("landing.organizer.title")}</h2>
          <p className="mt-3 max-w-xl text-sm leading-6 text-muted-foreground">{t("landing.organizer.description")}</p>

          <ul className="mt-6 grid gap-3 sm:grid-cols-2">
            {CAPABILITIES.map((item) => (
              <li className="flex items-center gap-2.5 text-sm font-semibold text-foreground" key={item.key}>
                <item.icon aria-hidden className="size-4 shrink-0 text-event" />
                {t(item.key)}
              </li>
            ))}
          </ul>

          <Button asChild className="mt-7" variant="secondary">
            <Link href="/events">{t("landing.organizer.cta")}</Link>
          </Button>
        </MotionReveal>

        <MotionReveal delayMs={100}>
          <TiltCard maxTiltDeg={3}>
            <div className="rounded-sm border bg-card p-6 shadow-card">
              <div className="flex items-center justify-between border-b pb-3">
                <div className="h-2.5 w-28 rounded-full bg-event/30" />
                <span className="flex items-center gap-1.5 rounded-sm border border-success/30 bg-success/10 px-2 py-1">
                  <span aria-hidden className="size-1.5 rounded-full bg-success" />
                  <span aria-hidden className="h-1.5 w-10 rounded-full bg-success/40" />
                </span>
              </div>
              <div className="mt-4 grid grid-cols-3 gap-3">
                {[0, 1, 2].map((index) => (
                  <div className="rounded-sm border bg-surface p-3" key={index}>
                    <div className="h-1.5 w-full rounded-full bg-muted" />
                    <div className="mt-2 h-2.5 w-8 font-serif text-lg font-semibold text-event">
                      {index === 0 ? "42" : index === 1 ? "31" : "9"}
                    </div>
                  </div>
                ))}
              </div>
              <div className="mt-4 flex items-center gap-2 rounded-sm border border-event/30 bg-event/10 p-3">
                <Ticket aria-hidden className="size-4 text-event" />
                <div className="h-1.5 w-32 rounded-full bg-event/30" />
              </div>
            </div>
          </TiltCard>
        </MotionReveal>
      </div>
    </section>
  );
}
