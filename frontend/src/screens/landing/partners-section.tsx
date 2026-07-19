"use client";

import Image from "next/image";

import { useI18n, type TranslationKey } from "@/shared/i18n";
import { MotionReveal } from "@/shared/ui/motion-reveal";
import { usePrefersReducedMotion } from "@/shared/ui/use-reduced-motion";

type Partner = {
  nameKey: TranslationKey;
  src: string;
  wide?: boolean;
};

const PARTNERS: Partner[] = [
  { nameKey: "landing.partners.uniteens", src: "/landing-partners/uniteens.png", wide: true },
  { nameKey: "landing.partners.lexNova", src: "/landing-partners/lex-nova.png" },
  { nameKey: "landing.partners.yrc", src: "/landing-partners/yrc.png" },
  { nameKey: "landing.partners.communityStudent", src: "/landing-partners/community-student.png" },
  { nameKey: "landing.partners.xdebates", src: "/landing-partners/xdebates.png" },
  { nameKey: "landing.partners.nexusVolunteers", src: "/landing-partners/nexus-volunteers.png" }
];

function PartnerLogo({ partner, decorative = false }: { partner: Partner; decorative?: boolean }) {
  const { t } = useI18n();
  const name = t(partner.nameKey);

  return (
    <div
      aria-hidden={decorative ? true : undefined}
      className={`grid h-32 shrink-0 place-items-center rounded-sm border bg-card p-4 shadow-card transition-transform hover:-translate-y-1 hover:shadow-2xl focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-primary ${
        partner.wide ? "w-72" : "w-52"
      }`}
      tabIndex={decorative ? -1 : 0}
    >
      <Image
        alt={decorative ? "" : name}
        className="max-h-24 w-full object-contain"
        height={160}
        loading="lazy"
        src={partner.src}
        width={partner.wide ? 300 : 220}
      />
    </div>
  );
}

export function PartnersSection() {
  const { t } = useI18n();
  const prefersReducedMotion = usePrefersReducedMotion();

  return (
    <section className="relative overflow-hidden bg-surface py-16 sm:py-20" id="partners">
      <div
        aria-hidden
        className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-primary/35 to-transparent"
      />
      <div className="mx-auto w-full max-w-[90rem] px-4 sm:px-6 lg:px-8">
        <MotionReveal>
          <div className="mx-auto max-w-3xl text-center">
            <p className="text-eyebrow text-primary-hover">{t("landing.partners.eyebrow")}</p>
            <h2 className="mt-3 font-serif text-4xl font-semibold leading-tight text-foreground sm:text-5xl">
              {t("landing.partners.title")}
            </h2>
            <p className="mx-auto mt-4 max-w-2xl text-sm leading-6 text-muted-foreground">
              {t("landing.partners.description")}
            </p>
          </div>
        </MotionReveal>

        <MotionReveal delayMs={80}>
          <div className="group relative mt-10 overflow-hidden py-2">
            <div
              className={`flex gap-4 ${
                prefersReducedMotion
                  ? "flex-wrap justify-center"
                  : "w-max animate-[landing-partner-scroll_34s_linear_infinite] group-hover:[animation-play-state:paused] group-focus-within:[animation-play-state:paused]"
              }`}
            >
              {PARTNERS.map((partner) => (
                <PartnerLogo key={partner.nameKey} partner={partner} />
              ))}
              {!prefersReducedMotion
                ? PARTNERS.map((partner) => (
                    <PartnerLogo decorative key={`${partner.nameKey}-duplicate`} partner={partner} />
                  ))
                : null}
            </div>
          </div>
        </MotionReveal>
      </div>
    </section>
  );
}
