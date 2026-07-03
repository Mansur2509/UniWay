"use client";

import { CalendarClock, ExternalLink, RefreshCw } from "lucide-react";
import { useCallback, useEffect, useMemo, useState } from "react";

import type { OfficialExamDate } from "@/entities/exam";
import { getOfficialExamDatesRequest } from "@/features/exams";
import { useI18n, type TranslationKey } from "@/shared/i18n";
import { formatDate } from "@/shared/lib/date-time";
import { Badge } from "@/shared/ui/badge";
import { Button } from "@/shared/ui/button";
import { Card } from "@/shared/ui/card";
import { LoadingNotice } from "@/shared/ui/loading-notice";

const PAGE_SIZE = 200;

function ExamDateRow({ item }: { item: OfficialExamDate }) {
  const { locale, t } = useI18n();
  return (
    <li className="rounded-sm border bg-surface px-3 py-2 text-sm">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="font-semibold">{item.name}</p>
          <p className="mt-0.5 text-xs text-muted-foreground">
            {t(`exams.eventKind.${item.event_kind}` as TranslationKey)}
            {" / "}
            {formatDate(item.test_date, locale)}
            {item.test_time ? ` / ${item.test_time}` : ""}
          </p>
        </div>
        <Badge className="text-xs">
          {t(`exams.verification.${item.verification_status}` as TranslationKey)}
        </Badge>
      </div>
      <div className="mt-2 flex flex-wrap gap-x-4 gap-y-1 text-xs text-muted-foreground">
        {item.registration_deadline ? (
          <span>
            {t("exams.registrationDeadline", {
              date: formatDate(item.registration_deadline, locale)
            })}
          </span>
        ) : null}
        {item.late_registration_deadline ? (
          <span>
            {t("exams.lateDeadline", {
              date: formatDate(item.late_registration_deadline, locale)
            })}
          </span>
        ) : null}
        {item.late_test_date ? (
          <span>
            {t("exams.lateTesting", {
              date: formatDate(item.late_test_date, locale),
              time: item.late_test_time || "-"
            })}
          </span>
        ) : null}
      </div>
      {item.source_url ? (
        <a
          className="mt-2 inline-flex items-center gap-1 text-xs font-semibold text-primary hover:text-primary-hover"
          href={item.source_url}
          rel="noreferrer"
          target="_blank"
        >
          {t("exams.source")}
          <ExternalLink aria-hidden className="size-3" />
        </a>
      ) : null}
    </li>
  );
}

export function ExamsScreen() {
  const { t } = useI18n();
  const [dates, setDates] = useState<OfficialExamDate[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [hasError, setHasError] = useState(false);

  const loadDates = useCallback(async () => {
    setIsLoading(true);
    setHasError(false);
    try {
      const response = await getOfficialExamDatesRequest({ page_size: PAGE_SIZE });
      setDates(response.results);
    } catch {
      setHasError(true);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadDates();
  }, [loadDates]);

  const satDates = useMemo(
    () => dates.filter((item) => item.exam_type === "SAT" && item.event_kind === "exam"),
    [dates]
  );
  const apExamDates = useMemo(
    () => dates.filter((item) => item.exam_type === "AP" && item.event_kind === "exam"),
    [dates]
  );
  const apDeadlineDates = useMemo(
    () => dates.filter((item) => item.exam_type === "AP" && item.event_kind !== "exam"),
    [dates]
  );

  if (isLoading) {
    return <LoadingNotice message={t("exams.states.loading")} />;
  }

  if (hasError) {
    return (
      <Card className="border-danger/35 bg-danger/10">
        <p className="text-sm text-danger" role="alert">
          {t("exams.states.loadError")}
        </p>
        <Button className="mt-4" onClick={() => void loadDates()} type="button">
          <RefreshCw aria-hidden className="mr-2 size-4" />
          {t("universities.actions.retry")}
        </Button>
      </Card>
    );
  }

  return (
    <div className="space-y-5">
      <section className="rounded-sm border bg-card p-6 shadow-card sm:p-8">
        <p className="text-xs font-bold uppercase tracking-[0.18em] text-primary-hover">
          {t("exams.eyebrow")}
        </p>
        <div className="mt-3 flex flex-col justify-between gap-4 lg:flex-row lg:items-end">
          <div>
            <h1 className="max-w-3xl text-3xl font-semibold sm:text-4xl">
              {t("exams.title")}
            </h1>
            <p className="mt-3 max-w-2xl text-sm leading-6 text-muted-foreground">
              {t("exams.description")}
            </p>
          </div>
          <Badge className="text-xs">{t("exams.datasetBadge")}</Badge>
        </div>
      </section>

      <Card className="border-warning/35 bg-warning/10 p-4">
        <p className="text-sm font-semibold text-warning">{t("exams.warningTitle")}</p>
        <p className="mt-1 text-xs leading-5 text-muted-foreground">
          {t("exams.warningDescription")}
        </p>
      </Card>

      <section className="grid gap-4 xl:grid-cols-[0.95fr_1.05fr]">
        <Card className="p-4">
          <div className="flex items-center gap-2">
            <CalendarClock aria-hidden className="size-5 text-accent" />
            <h2 className="text-lg font-semibold">{t("exams.sat.title")}</h2>
          </div>
          <ul className="mt-4 space-y-2">
            {satDates.map((item) => (
              <ExamDateRow item={item} key={item.id} />
            ))}
          </ul>
        </Card>

        <Card className="p-4">
          <div className="flex items-center gap-2">
            <CalendarClock aria-hidden className="size-5 text-accent" />
            <h2 className="text-lg font-semibold">{t("exams.ap.title")}</h2>
          </div>
          <div className="mt-4 max-h-[34rem] space-y-2 overflow-y-auto pr-1 scrollbar-quiet">
            {apExamDates.map((item) => (
              <ExamDateRow item={item} key={item.id} />
            ))}
          </div>
        </Card>
      </section>

      <Card className="p-4">
        <h2 className="text-lg font-semibold">{t("exams.ap.deadlineTitle")}</h2>
        <ul className="mt-4 grid gap-2 md:grid-cols-2">
          {apDeadlineDates.map((item) => (
            <ExamDateRow item={item} key={item.id} />
          ))}
        </ul>
      </Card>
    </div>
  );
}
