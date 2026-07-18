"use client";

import { supportedLocales, localeMetadata, useI18n } from "@/shared/i18n";
import { Card } from "@/shared/ui/card";
import { StaggerGroup } from "@/shared/ui/stagger-group";

export function LanguagesSection() {
  const { t } = useI18n();

  return (
    <section className="bg-surface py-16" id="languages">
      <div className="mx-auto w-full max-w-[84rem] px-4 sm:px-6 lg:px-8">
        <div className="max-w-2xl">
          <p className="text-eyebrow text-primary-hover">{t("landing.languages.eyebrow")}</p>
          <h2 className="text-feature-heading mt-2">{t("landing.languages.title")}</h2>
          <p className="mt-3 text-sm leading-6 text-muted-foreground">{t("landing.languages.description")}</p>
        </div>

        <StaggerGroup className="mt-6 grid gap-3 sm:grid-cols-2 lg:grid-cols-4" staggerMs={50}>
          {supportedLocales.map((code) => (
            <Card className="text-center" key={code}>
              <p className="font-serif text-lg font-semibold">{localeMetadata[code].nativeLabel}</p>
              <p className="mt-1 text-xs text-muted-foreground">{localeMetadata[code].label}</p>
            </Card>
          ))}
        </StaggerGroup>
      </div>
    </section>
  );
}
