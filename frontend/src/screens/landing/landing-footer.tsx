"use client";

import Link from "next/link";

import { useI18n } from "@/shared/i18n";
import { BrandMark } from "@/shared/ui/brand-mark";
import { SupportLink } from "@/shared/ui/support-link";

export function LandingFooter() {
  const { t } = useI18n();
  const year = new Date().getFullYear();

  return (
    <footer className="border-t bg-card py-8">
      <div className="mx-auto flex w-full max-w-[84rem] flex-col items-center gap-4 px-4 text-center sm:flex-row sm:justify-between sm:text-left sm:px-6 lg:px-8">
        <div className="flex items-center gap-2.5">
          <BrandMark className="size-7 shrink-0 overflow-hidden rounded-sm" />
          <div>
            <p className="font-serif text-sm font-semibold">UniWay</p>
            <p className="text-xs text-muted-foreground">{t("landing.footer.tagline")}</p>
          </div>
        </div>

        <div className="flex items-center gap-4 text-xs text-muted-foreground">
          <Link className="font-semibold hover:text-foreground" href="/login">
            {t("auth.signIn")}
          </Link>
          <Link className="font-semibold hover:text-foreground" href="/register">
            {t("landing.nav.createProfile")}
          </Link>
        </div>

        <p className="text-xs text-muted-foreground">{t("landing.footer.copyright", { year })}</p>
      </div>

      <SupportLink className="fixed bottom-4 right-4 z-30 shadow-card" />
    </footer>
  );
}
