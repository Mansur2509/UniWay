"use client";

import { Languages } from "lucide-react";

import {
  localeMetadata,
  supportedLocales,
  type LocaleCode,
  useI18n
} from "@/shared/i18n";

export function LanguageSwitcher({
  compact = false,
  inverse = false
}: {
  compact?: boolean;
  inverse?: boolean;
}) {
  const { locale, setLocale, t } = useI18n();

  return (
    <label
      className={
        compact
          ? "relative grid size-9 shrink-0 place-items-center rounded-sm border bg-surface text-muted-foreground"
          : inverse
            ? "flex items-center gap-3 rounded-sm border border-white/15 bg-white/5 px-3 py-2"
            : "flex items-center gap-3 rounded-sm border bg-elevated/55 px-3 py-2"
      }
      title={compact ? t("locale.label") : undefined}
    >
      <Languages aria-hidden className="size-4 shrink-0 text-accent" />
      {compact ? null : (
        <span className={inverse ? "text-xs font-semibold text-white/55" : "text-xs font-semibold text-muted-foreground"}>
          {t("locale.label")}
        </span>
      )}
      <span className="sr-only">{t("a11y.languageSwitcher")}</span>
      <select
        aria-label={t("locale.select")}
        className={
          compact
            ? "absolute inset-0 size-full cursor-pointer opacity-0"
            : inverse
              ? "min-h-9 min-w-24 cursor-pointer bg-transparent text-xs font-semibold text-white outline-none"
              : "min-h-9 min-w-24 cursor-pointer bg-transparent text-xs font-semibold text-foreground outline-none"
        }
        onChange={(event) => setLocale(event.target.value as LocaleCode)}
        value={locale}
      >
        {supportedLocales.map((localeCode) => (
          <option className="bg-elevated text-foreground" key={localeCode} value={localeCode}>
            {localeMetadata[localeCode].nativeLabel}
          </option>
        ))}
      </select>
    </label>
  );
}
