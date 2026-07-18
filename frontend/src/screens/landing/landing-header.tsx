"use client";

import { AnimatePresence, m } from "motion/react";
import { Menu, X } from "lucide-react";
import Link from "next/link";
import { useState } from "react";

import { useI18n } from "@/shared/i18n";
import { AppIcon } from "@/shared/ui/icon";
import { BrandMark } from "@/shared/ui/brand-mark";
import { Button } from "@/shared/ui/button";
import { LanguageSwitcher } from "@/shared/ui/language-switcher";
import { ThemeToggleButton } from "@/shared/ui/theme-selector";

const NAV_LINKS = [
  { href: "#features", key: "landing.nav.features" as const },
  { href: "#how-it-works", key: "landing.nav.howItWorks" as const },
  { href: "#organizers", key: "landing.nav.organizers" as const },
  { href: "#languages", key: "landing.nav.languages" as const }
];

export function LandingHeader() {
  const { t } = useI18n();
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <header className="sticky top-0 z-30 border-b bg-card/90 backdrop-blur">
      <div className="mx-auto flex w-full max-w-[84rem] items-center justify-between gap-4 px-4 py-3 sm:px-6 lg:px-8">
        <Link className="flex items-center gap-2.5" href="/">
          <BrandMark className="size-8 shrink-0 overflow-hidden rounded-sm" />
          <span className="font-serif text-lg font-semibold tracking-tight">UniWay</span>
        </Link>

        <nav aria-label={t("shell.primaryNavigation")} className="hidden items-center gap-6 lg:flex">
          {NAV_LINKS.map((link) => (
            <a
              className="text-sm font-semibold text-muted-foreground transition-colors hover:text-foreground"
              href={link.href}
              key={link.href}
            >
              {t(link.key)}
            </a>
          ))}
        </nav>

        <div className="hidden items-center gap-2 lg:flex">
          <LanguageSwitcher compact />
          <ThemeToggleButton />
          <Button asChild size="sm" variant="ghost">
            <Link href="/login">{t("auth.signIn")}</Link>
          </Button>
          <Button asChild size="sm">
            <Link href="/register">{t("landing.nav.createProfile")}</Link>
          </Button>
        </div>

        <button
          aria-expanded={mobileOpen}
          aria-label={t(mobileOpen ? "landing.nav.closeMenu" : "landing.nav.openMenu")}
          className="grid size-10 place-items-center rounded-sm text-muted-foreground hover:bg-muted lg:hidden"
          onClick={() => setMobileOpen((open) => !open)}
          type="button"
        >
          <AppIcon icon={mobileOpen ? X : Menu} />
        </button>
      </div>

      <AnimatePresence>
        {mobileOpen ? (
          <m.div
            animate={{ height: "auto", opacity: 1 }}
            className="overflow-hidden border-t bg-card lg:hidden"
            exit={{ height: 0, opacity: 0 }}
            initial={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.22, ease: [0.16, 1, 0.3, 1] }}
          >
            <div className="flex flex-col gap-4 px-4 py-4 sm:px-6">
              <nav aria-label={t("shell.primaryNavigation")} className="flex flex-col gap-3">
                {NAV_LINKS.map((link) => (
                  <a
                    className="text-sm font-semibold text-muted-foreground hover:text-foreground"
                    href={link.href}
                    key={link.href}
                    onClick={() => setMobileOpen(false)}
                  >
                    {t(link.key)}
                  </a>
                ))}
              </nav>
              <div className="flex items-center gap-2">
                <LanguageSwitcher compact />
                <ThemeToggleButton />
              </div>
              <div className="flex flex-col gap-2">
                <Button asChild variant="secondary">
                  <Link href="/login">{t("auth.signIn")}</Link>
                </Button>
                <Button asChild>
                  <Link href="/register">{t("landing.nav.createProfile")}</Link>
                </Button>
              </div>
            </div>
          </m.div>
        ) : null}
      </AnimatePresence>
    </header>
  );
}
