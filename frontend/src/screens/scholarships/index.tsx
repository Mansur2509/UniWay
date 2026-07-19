"use client";

import { Award, ExternalLink, GraduationCap, MapPin, ShieldCheck } from "lucide-react";
import Link from "next/link";
import { useEffect, useState } from "react";

import type { UniversityDetails } from "@/entities/university";
import { getUniversitiesRequest, getUniversityFilterOptionsRequest } from "@/features/universities";
import { useI18n } from "@/shared/i18n";
import { formatDate } from "@/shared/lib/date-time";
import { useSlowLoad } from "@/shared/lib/use-slow-load";
import { fieldClassName } from "@/shared/ui/field";
import { Button } from "@/shared/ui/button";
import { Card } from "@/shared/ui/card";
import { EmptyState } from "@/shared/ui/empty-state";
import { IconChip } from "@/shared/ui/icon-chip";
import { DEFAULT_PAGE_SIZE, PaginatedGrid } from "@/shared/ui/pagination";

function ScholarshipUniversityCard({ university }: { university: UniversityDetails }) {
  const { locale, t } = useI18n();
  const scholarships = university.scholarships ?? [];
  return (
    <Card className="flex min-w-0 flex-col gap-2 p-4">
      <h2 className="flex items-center gap-2 text-base font-semibold break-words">
        <IconChip icon={GraduationCap} size="sm" tone="scholarship" />
        <Link className="hover:text-primary-hover" href={`/universities/${university.slug}`}>
          {university.name}
        </Link>
      </h2>
      <p className="flex items-center gap-1.5 text-xs text-muted-foreground">
        <MapPin aria-hidden className="size-3.5 shrink-0" />
        <span className="truncate">
          {[university.city, university.country].filter(Boolean).join(", ")}
        </span>
      </p>
      {scholarships.length === 0 ? (
        <p className="mt-1 text-xs italic text-muted-foreground">
          {t("universities.notVerifiedYet")}
        </p>
      ) : (
        <ul className="mt-1 space-y-2">
          {scholarships.map((scholarship) => (
            <li
              className="rounded-sm border border-l-2 border-l-scholarship bg-surface px-3 py-2 text-sm"
              key={scholarship.id}
            >
              <p className="font-semibold">{scholarship.name}</p>
              {scholarship.summary ? (
                <p className="mt-0.5 line-clamp-2 text-xs text-muted-foreground">
                  {scholarship.summary}
                </p>
              ) : null}
              <div className="mt-1 flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
                {scholarship.deadline ? (
                  <span>{formatDate(scholarship.deadline, locale)}</span>
                ) : null}
                {scholarship.official_url ? (
                  <a
                    className="inline-flex items-center gap-1 font-semibold text-primary hover:text-primary-hover"
                    href={scholarship.official_url}
                    rel="noreferrer"
                    target="_blank"
                  >
                    {t("scholarships.card.officialLink")}
                    <ExternalLink aria-hidden className="size-3" />
                  </a>
                ) : null}
              </div>
            </li>
          ))}
        </ul>
      )}
      <Button asChild className="mt-2 self-start" size="sm" variant="secondary">
        <Link href={`/universities/${university.slug}`}>{t("universities.actions.viewDetails")}</Link>
      </Button>
    </Card>
  );
}

export function ScholarshipsScreen() {
  const { t } = useI18n();
  const [universities, setUniversities] = useState<UniversityDetails[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [countries, setCountries] = useState<string[]>([]);
  const [country, setCountry] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const [isLoading, setIsLoading] = useState(true);
  const [hasError, setHasError] = useState(false);
  const [retryToken, setRetryToken] = useState(0);
  const isSlow = useSlowLoad(isLoading);

  useEffect(() => {
    getUniversityFilterOptionsRequest()
      .then((options) => setCountries(options.countries))
      .catch(() => undefined);
  }, []);

  useEffect(() => {
    let active = true;
    setIsLoading(true);
    setHasError(false);
    getUniversitiesRequest(
      { scholarship_available: "true", country: country || undefined },
      { page: currentPage, page_size: DEFAULT_PAGE_SIZE }
    )
      .then((response) => {
        if (!active) return;
        setUniversities(response.results);
        setTotalCount(response.count);
      })
      .catch(() => {
        if (active) setHasError(true);
      })
      .finally(() => {
        if (active) setIsLoading(false);
      });
    return () => {
      active = false;
    };
  }, [country, currentPage, retryToken]);

  const totalPages = Math.max(1, Math.ceil(totalCount / DEFAULT_PAGE_SIZE));

  return (
    <div className="space-y-5">
      <section className="relative overflow-hidden rounded-sm border bg-card p-6 shadow-card sm:p-9">
        <div
          aria-hidden
          className="pointer-events-none absolute inset-0 bg-gradient-to-br from-scholarship/8 via-transparent to-success/8"
        />
        <div className="relative flex min-w-0 items-start gap-3">
          <IconChip icon={Award} size="lg" tone="scholarship" />
          <div>
            <p className="text-eyebrow text-primary-hover">{t("scholarships.eyebrow")}</p>
            <h1 className="text-display mt-2 max-w-3xl">{t("scholarships.title")}</h1>
            <p className="mt-3 max-w-2xl text-sm leading-6 text-muted-foreground">
              {t("scholarships.description")}
            </p>
          </div>
        </div>
      </section>

      <Card className="flex flex-wrap items-end gap-3 p-4">
        <label className="block">
          <span className="text-xs font-semibold">{t("scholarships.filters.country")}</span>
          <select
            className={fieldClassName}
            onChange={(event) => {
              setCountry(event.target.value);
              setCurrentPage(1);
            }}
            value={country}
          >
            <option value="">{t("scholarships.filters.allCountries")}</option>
            {countries.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        </label>
      </Card>

      {hasError ? (
        <Card className="flex flex-col items-center gap-3 py-8 text-center">
          <p className="text-sm text-danger" role="alert">
            {t("scholarships.states.error")}
          </p>
          <Button onClick={() => setRetryToken((value) => value + 1)} size="sm" type="button">
            {t("common.retry")}
          </Button>
          {isSlow ? (
            <p className="text-xs leading-5 text-muted-foreground" role="status">
              {t("common.wakingUp")}
            </p>
          ) : null}
        </Card>
      ) : (
        <PaginatedGrid
          columnsDesktop={3}
          currentPage={currentPage}
          emptyState={
            <EmptyState
              action={
                <Button asChild size="sm" variant="secondary">
                  <Link href="/universities">{t("scholarships.empty.action")}</Link>
                </Button>
              }
              description={t("scholarships.empty.description")}
              icon={Award}
              title={t("scholarships.empty.title")}
            />
          }
          getItemKey={(item) => item.id}
          isLoading={isLoading}
          items={universities}
          onPageChange={setCurrentPage}
          renderItem={(university) => <ScholarshipUniversityCard university={university} />}
          totalCount={totalCount}
          totalPages={totalPages}
        />
      )}

      <Card className="flex items-start gap-4 bg-muted/45">
        <IconChip icon={ShieldCheck} tone="muted" />
        <div>
          <h2 className="text-sm font-semibold">{t("scholarships.disclaimer.title")}</h2>
          <p className="mt-1 text-sm leading-6 text-muted-foreground">
            {t("scholarships.disclaimer.description")}
          </p>
        </div>
      </Card>
    </div>
  );
}
