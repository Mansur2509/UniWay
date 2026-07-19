"use client";

import { AnimatePresence, m } from "motion/react";
import { Menu, X } from "lucide-react";
import Link from "next/link";
import { type MouseEvent, useCallback, useEffect, useRef, useState } from "react";

import { useI18n } from "@/shared/i18n";
import { AppIcon } from "@/shared/ui/icon";
import { BrandMark } from "@/shared/ui/brand-mark";
import { Button } from "@/shared/ui/button";
import { LanguageSwitcher } from "@/shared/ui/language-switcher";
import { ThemeToggleButton } from "@/shared/ui/theme-selector";
import { usePrefersReducedMotion } from "@/shared/ui/use-reduced-motion";

const NAV_LINKS = [
  { href: "#features", id: "features", key: "landing.nav.features" as const },
  { href: "#global-path", id: "global-path", key: "landing.nav.globalPath" as const },
  { href: "#how-it-works", id: "how-it-works", key: "landing.nav.howItWorks" as const },
  { href: "#partners", id: "partners", key: "landing.nav.partners" as const },
  { href: "#organizers", id: "organizers", key: "landing.nav.organizers" as const },
  { href: "#languages", id: "languages", key: "landing.nav.languages" as const }
];

export function LandingHeader() {
  const { t } = useI18n();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [activeId, setActiveId] = useState(NAV_LINKS[0].id);
  const [scrolled, setScrolled] = useState(false);
  const manualNavUntilRef = useRef(0);
  const prefersReducedMotion = usePrefersReducedMotion();

  useEffect(() => {
    function updateScrolled() {
      setScrolled(window.scrollY > 12);
    }

    updateScrolled();
    window.addEventListener("scroll", updateScrolled, { passive: true });
    return () => window.removeEventListener("scroll", updateScrolled);
  }, []);

  useEffect(() => {
    let frame = 0;

    function updateActiveSection() {
      window.cancelAnimationFrame(frame);
      frame = window.requestAnimationFrame(() => {
        if (Date.now() < manualNavUntilRef.current) return;
        const headerOffset = 96;
        const viewportProbe = window.scrollY + headerOffset + window.innerHeight * 0.18;
        let currentId = NAV_LINKS[0].id;

        for (const link of NAV_LINKS) {
          const section = document.getElementById(link.id);
          if (!section) continue;
          if (section.offsetTop <= viewportProbe) {
            currentId = link.id;
          }
        }

        setActiveId(currentId);
      });
    }

    updateActiveSection();
    window.addEventListener("scroll", updateActiveSection, { passive: true });
    window.addEventListener("resize", updateActiveSection);
    window.addEventListener("hashchange", updateActiveSection);
    return () => {
      window.cancelAnimationFrame(frame);
      window.removeEventListener("scroll", updateActiveSection);
      window.removeEventListener("resize", updateActiveSection);
      window.removeEventListener("hashchange", updateActiveSection);
    };
  }, []);

  const handleNavClick = useCallback(
    (event: MouseEvent<HTMLAnchorElement>, id: string, href: string) => {
      const target = document.getElementById(id);
      if (!target) return;
      event.preventDefault();
      setMobileOpen(false);
      setActiveId(id);
      manualNavUntilRef.current = Date.now() + (prefersReducedMotion ? 250 : 1200);
      window.history.pushState(null, "", href);
      target.scrollIntoView({
        behavior: prefersReducedMotion ? "auto" : "smooth",
        block: "start"
      });
      window.setTimeout(() => {
        target.focus({ preventScroll: true });
      }, prefersReducedMotion ? 0 : 320);
    },
    [prefersReducedMotion]
  );

  return (
    <header
      className={`sticky top-0 z-30 border-b backdrop-blur transition-colors ${
        scrolled
          ? "border-border bg-card/[0.96] shadow-[0_18px_44px_hsl(var(--navy)/0.08)]"
          : "border-transparent bg-card/[0.82]"
      }`}
    >
      <div className="mx-auto flex w-full max-w-[98rem] items-center justify-between gap-4 px-4 py-3.5 sm:px-6 lg:px-10">
        <Link className="flex items-center gap-2.5" href="/">
          <BrandMark className="size-8 shrink-0 overflow-hidden rounded-sm" />
          <span className="font-serif text-xl font-semibold tracking-tight">UniWay</span>
        </Link>

        <nav aria-label={t("shell.primaryNavigation")} className="hidden items-center gap-7 xl:flex">
          {NAV_LINKS.map((link) => (
            <a
              aria-current={activeId === link.id ? "page" : undefined}
              className={`relative py-2 text-sm font-bold uppercase tracking-[0.08em] transition-colors hover:text-foreground ${
                activeId === link.id ? "text-foreground" : "text-muted-foreground"
              }`}
              href={link.href}
              key={link.href}
              onClick={(event) => handleNavClick(event, link.id, link.href)}
            >
              {t(link.key)}
              <span
                aria-hidden
                className={`absolute inset-x-0 -bottom-0.5 h-0.5 origin-left bg-primary transition-transform ${
                  activeId === link.id ? "scale-x-100" : "scale-x-0"
                }`}
              />
            </a>
          ))}
        </nav>

        <div className="hidden items-center gap-2 xl:flex">
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
          className="grid size-10 place-items-center rounded-sm text-muted-foreground hover:bg-muted xl:hidden"
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
            className="overflow-hidden border-t bg-card xl:hidden"
            exit={{ height: 0, opacity: 0 }}
            initial={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.22, ease: [0.16, 1, 0.3, 1] }}
          >
            <div className="flex flex-col gap-4 px-4 py-4 sm:px-6">
              <nav aria-label={t("shell.primaryNavigation")} className="flex flex-col gap-3">
                {NAV_LINKS.map((link) => (
                  <a
                    aria-current={activeId === link.id ? "page" : undefined}
                    className={`border-l-2 px-3 py-2 text-sm font-semibold ${
                      activeId === link.id
                        ? "border-primary bg-primary/10 text-foreground"
                        : "border-transparent text-muted-foreground hover:text-foreground"
                    }`}
                    href={link.href}
                    key={link.href}
                    onClick={(event) => handleNavClick(event, link.id, link.href)}
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
