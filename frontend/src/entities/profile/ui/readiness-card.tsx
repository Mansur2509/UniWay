"use client";

import { ExternalLink, Star } from "lucide-react";

import type { ApplicationReadiness } from "@/entities/profile";
import { useI18n, type TranslationKey } from "@/shared/i18n";
import { Card } from "@/shared/ui/card";

export function ReadinessCard({
  readiness,
  compact = false
}: {
  readiness: ApplicationReadiness;
  compact?: boolean;
}) {
  const { t } = useI18n();

  const componentLabel = (component: string) =>
    t(`admissions.component.${component}` as TranslationKey);

  return (
    <Card>
      <div className="flex flex-col justify-between gap-5 sm:flex-row sm:items-start">
        <div>
          <p className="text-xs font-bold uppercase tracking-[0.16em] text-primary-hover">
            {t("admissions.readiness.title")}
          </p>
          <h2 className="mt-2 text-2xl font-semibold">
            {t(
              `admissions.readiness.level.${readiness.level}` as TranslationKey
            )}
          </h2>
          <p className="mt-2 max-w-2xl text-sm leading-6 text-muted-foreground">
            {t("admissions.readiness.description")}
          </p>
        </div>
        <div
          aria-label={t("admissions.readiness.stars", {
            count: readiness.stars
          })}
          className="flex shrink-0 gap-1"
        >
          {Array.from({ length: 5 }, (_, index) => (
            <Star
              aria-hidden
              className={
                index < readiness.stars
                  ? "size-5 fill-accent text-accent"
                  : "size-5 text-border"
              }
              key={index}
            />
          ))}
        </div>
      </div>

      <div className="mt-6 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {Object.entries(readiness.score_components).map(([component, score]) => (
          <div className="border bg-surface p-3" key={component}>
            <div className="flex items-center justify-between gap-3 text-sm">
              <span className="font-semibold">{componentLabel(component)}</span>
              <span className="text-accent">{score}/5</span>
            </div>
            <div className="mt-2 h-1.5 bg-muted">
              <div
                className="h-full bg-primary"
                style={{ width: `${score * 20}%` }}
              />
            </div>
          </div>
        ))}
      </div>

      {!compact ? (
        <div className="mt-6 grid gap-5 md:grid-cols-2">
          <div>
            <h3 className="text-lg font-semibold">
              {t("admissions.readiness.strengths")}
            </h3>
            <ul className="mt-3 space-y-2 text-sm text-muted-foreground">
              {(readiness.strengths.length
                ? readiness.strengths.map(componentLabel)
                : [t("admissions.readiness.noStrengths")]
              ).map((item) => (
                <li className="border-l-2 border-success pl-3" key={item}>
                  {item}
                </li>
              ))}
            </ul>
          </div>
          <div>
            <h3 className="text-lg font-semibold">
              {t("admissions.readiness.improvements")}
            </h3>
            <ul className="mt-3 space-y-2 text-sm text-muted-foreground">
              {(readiness.improvements.length
                ? readiness.improvements.map(componentLabel)
                : [t("admissions.readiness.noImprovements")]
              ).map((item) => (
                <li className="border-l-2 border-warning pl-3" key={item}>
                  {item}
                </li>
              ))}
            </ul>
          </div>
        </div>
      ) : null}

      <div className="mt-6 border border-warning/30 bg-warning/10 p-4 text-xs leading-5 text-warning">
        <p>
          {readiness.comparison_status === "published_ranges"
            ? t("admissions.readiness.published")
            : t("admissions.readiness.officialNeeded")}
        </p>
        <p className="mt-2">{t("admissions.readiness.disclaimer")}</p>
      </div>

      {readiness.official_sources.length ? (
        <div className="mt-5">
          <h3 className="text-sm font-semibold">
            {t("admissions.readiness.sources")}
          </h3>
          <div className="mt-2 flex flex-wrap gap-2">
            {readiness.official_sources.map((source) => (
              <a
                className="inline-flex items-center gap-2 border bg-surface px-3 py-2 text-xs font-semibold text-primary-hover hover:underline"
                href={source.url}
                key={`${source.university}-${source.url}`}
                rel="noreferrer"
                target="_blank"
              >
                {source.university}: {source.title}
                <ExternalLink aria-hidden className="size-3" />
              </a>
            ))}
          </div>
        </div>
      ) : null}
    </Card>
  );
}
