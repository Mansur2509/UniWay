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
      className={`grid h-44 shrink-0 place-items-center border border-border bg-white p-5 shadow-2xl shadow-navy/15 transition-transform hover:-translate-y-2 hover:shadow-[0_32px_80px_rgba(24,38,61,0.24)] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-primary ${
        partner.wide ? "w-[25rem]" : "w-72"
      }`}
      tabIndex={decorative ? -1 : 0}
    >
      <Image
        alt={decorative ? "" : name}
        className="max-h-32 w-full object-contain"
        height={160}
        loading="lazy"
        src={partner.src}
        width={partner.wide ? 400 : 280}
      />
    </div>
  );
}

export function PartnersSection() {
  const { t } = useI18n();
  const prefersReducedMotion = usePrefersReducedMotion();

  return (
    <section className="relative overflow-hidden bg-surface py-20 sm:py-24 lg:py-28" id="partners">
      <div aria-hidden className="absolute left-0 top-0 h-full w-[24vw] bg-primary" />
      <div aria-hidden className="absolute right-0 top-12 h-40 w-[34vw] border-y border-primary/20 bg-navy/10" />
      <div className="relative mx-auto w-full max-w-[104rem] px-4 sm:px-6 lg:px-10">
        <MotionReveal>
          <div className="grid gap-6 lg:grid-cols-[0.82fr_1.18fr] lg:items-end">
            <div>
              <p className="text-eyebrow text-primary-foreground lg:text-accent">{t("landing.partners.eyebrow")}</p>
              <h2 className="text-display-condensed-sm mt-4 max-w-4xl">{t("landing.partners.title")}</h2>
            </div>
            <p className="max-w-2xl text-base leading-7 text-muted-foreground lg:justify-self-end">
              {t("landing.partners.description")}
            </p>
          </div>
        </MotionReveal>

        <MotionReveal delayMs={80}>
          <div className="group relative mt-12 overflow-hidden border border-border bg-navy p-5 shadow-2xl shadow-navy/25 sm:p-7">
            <div className="absolute inset-y-0 left-0 w-24 bg-primary" aria-hidden />
            <div className="relative overflow-hidden py-2">
              <div
                className={`flex gap-5 ${
                  prefersReducedMotion
                    ? "flex-wrap justify-center"
                    : "w-max animate-[landing-partner-scroll_38s_linear_infinite] group-hover:[animation-play-state:paused] group-focus-within:[animation-play-state:paused]"
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
          </div>
        </MotionReveal>

        <MotionReveal delayMs={130}>
          <div className="mt-6 hidden grid-cols-6 gap-3 lg:grid" aria-hidden>
            {PARTNERS.map((partner) => (
              <div className="h-2 bg-primary/45" key={`rule-${partner.nameKey}`} />
            ))}
          </div>
        </MotionReveal>
      </div>
    </section>
  );
}
