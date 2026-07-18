"use client";

import Link from "next/link";

import { useI18n } from "@/shared/i18n";
import { Button } from "@/shared/ui/button";
import { MotionReveal } from "@/shared/ui/motion-reveal";

export function FinalCta() {
  const { t } = useI18n();

  return (
    <section className="bg-navy py-16 text-navy-foreground">
      <div className="mx-auto w-full max-w-[84rem] px-4 text-center sm:px-6 lg:px-8">
        <MotionReveal>
          <h2 className="text-display max-w-2xl mx-auto text-navy-foreground">{t("landing.finalCta.title")}</h2>
          <p className="mx-auto mt-4 max-w-xl text-base leading-7 text-white/75">
            {t("landing.finalCta.description")}
          </p>
          <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
            <Button asChild size="default">
              <Link href="/register">{t("landing.hero.primaryCta")}</Link>
            </Button>
            <Button asChild className="border-white/25 bg-transparent text-navy-foreground hover:bg-white/10" variant="secondary">
              <Link href="/login">{t("landing.hero.secondaryCta")}</Link>
            </Button>
          </div>
        </MotionReveal>
      </div>
    </section>
  );
}
