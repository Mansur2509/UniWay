"use client";

import {
  ArrowRight,
  BookOpenCheck,
  CalendarClock,
  CalendarDays,
  CircleDollarSign,
  FilePenLine,
  GraduationCap,
  Map,
  Route,
  Sparkles,
  type LucideIcon
} from "lucide-react";
import Link from "next/link";
import { useCallback, useEffect, useState } from "react";

import type { EventRegistration } from "@/entities/event";
import {
  classCatalog,
  ReadinessCard,
  type ApplicationReadiness,
  type ProfileCompletion,
  type StudentProfileDetails
} from "@/entities/profile";
import { useAuth } from "@/features/auth";
import { getMyEventRegistrationsRequest } from "@/features/events";
import {
  getApplicationReadinessRequest,
  getProfileCompletionRequest,
  getProfileRequest
} from "@/features/profile";
import { useI18n, type TranslationKey } from "@/shared/i18n";
import { formatDateTime } from "@/shared/lib/date-time";
import { Badge } from "@/shared/ui/badge";
import { Button } from "@/shared/ui/button";
import { Card } from "@/shared/ui/card";

export function DashboardScreen() {
  const { user } = useAuth();
  const { locale, t } = useI18n();
  const [completion, setCompletion] = useState<ProfileCompletion | null>(null);
  const [profile, setProfile] = useState<StudentProfileDetails | null>(null);
  const [readiness, setReadiness] = useState<ApplicationReadiness | null>(null);
  const [registrations, setRegistrations] = useState<EventRegistration[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [hasPartialError, setHasPartialError] = useState(false);

  const loadDashboard = useCallback(async () => {
    setIsLoading(true);
    setHasPartialError(false);
    const [
      completionResult,
      profileResult,
      registrationsResult,
      readinessResult
    ] = await Promise.allSettled([
      getProfileCompletionRequest(),
      getProfileRequest(),
      getMyEventRegistrationsRequest(),
      getApplicationReadinessRequest()
    ]);

    if (completionResult.status === "fulfilled") {
      setCompletion(completionResult.value);
    } else {
      setHasPartialError(true);
    }
    if (registrationsResult.status === "fulfilled") {
      setRegistrations(registrationsResult.value.results);
    } else {
      setHasPartialError(true);
    }
    if (profileResult.status === "fulfilled") {
      setProfile(profileResult.value);
    } else {
      setHasPartialError(true);
    }
    if (readinessResult.status === "fulfilled") {
      setReadiness(readinessResult.value);
    } else {
      setHasPartialError(true);
    }
    setIsLoading(false);
  }, []);

  useEffect(() => {
    void loadDashboard();
  }, [loadDashboard]);

  const firstName = user?.full_name.trim().split(/\s+/)[0] || t("dashboard.student");
  const planKey = user
    ? (`plans.${user.subscription.tier}` as TranslationKey)
    : "plans.free";
  const completionPercentage = completion?.percentage ?? 0;
  const plannedExams = (profile?.exam_plans.planned ?? [])
    .filter((exam) => exam.date)
    .map((exam) => ({
      ...exam,
      daysLeft: Math.ceil(
        (new Date(`${exam.date}T00:00:00`).getTime() - Date.now()) / 86_400_000
      )
    }))
    .filter((exam) => exam.daysLeft >= 0)
    .sort((left, right) => left.daysLeft - right.daysLeft);
  const selectedClasses = profile?.interested_classes ?? [];
  const nextClass = classCatalog.find((item) =>
    selectedClasses.includes(item.value)
  );

  return (
    <div className="space-y-6">
      <section className="overflow-hidden rounded-sm border bg-card shadow-card">
        <div className="grid lg:grid-cols-[1.35fr_0.65fr]">
          <div className="p-6 sm:p-9">
            <Badge>{t("dashboard.betaBadge")}</Badge>
            <p className="mt-5 text-xs font-bold uppercase tracking-[0.18em] text-primary-hover">
              {t("dashboard.eyebrow")}
            </p>
            <h1 className="mt-2 max-w-3xl text-3xl font-semibold sm:text-5xl">
              {t("dashboard.welcome", { name: firstName })}
            </h1>
            <p className="mt-4 max-w-2xl text-base leading-7 text-muted-foreground">
              {t("dashboard.commandCenterDescription")}
            </p>
            <div className="mt-7 flex flex-wrap gap-3">
              <Button asChild>
                <Link href="/events">
                  <Map aria-hidden className="mr-2 size-4" />
                  {t("dashboard.openEventMap")}
                </Link>
              </Button>
              <Button asChild variant="secondary">
                <Link href="/profile">{t("dashboard.reviewProfile")}</Link>
              </Button>
            </div>
          </div>
          <div className="border-t bg-surface p-6 lg:border-l lg:border-t-0 lg:p-8">
            <p className="text-xs font-bold uppercase tracking-[0.16em] text-muted-foreground">
              {t("dashboard.nextAction.label")}
            </p>
            <h2 className="mt-3 text-2xl font-semibold">
              {completionPercentage < 70
                ? t("dashboard.nextAction.profile")
                : registrations.length === 0
                  ? t("dashboard.nextAction.event")
                  : t("dashboard.nextAction.roadmap")}
            </h2>
            <p className="mt-3 text-sm leading-6 text-muted-foreground">
              {t("dashboard.nextAction.description")}
            </p>
          </div>
        </div>
      </section>

      {hasPartialError ? (
        <Card className="flex items-center justify-between gap-4 border-warning/30 bg-warning/10">
          <p className="text-sm text-warning">{t("dashboard.partialError")}</p>
          <Button onClick={() => void loadDashboard()} type="button" variant="ghost">
            {t("events.actions.retry")}
          </Button>
        </Card>
      ) : null}

      <section className="grid gap-5 xl:grid-cols-[0.75fr_1.25fr]">
        <Card>
          <div className="flex items-start justify-between gap-4">
            <div>
              <p className="text-xs font-bold uppercase tracking-[0.14em] text-primary-hover">
                {t("dashboard.profile.eyebrow")}
              </p>
              <h2 className="mt-2 text-2xl font-semibold">
                {t("dashboard.profile.title")}
              </h2>
            </div>
            <span className="text-2xl font-semibold text-accent">
              {isLoading ? "—" : `${completionPercentage}%`}
            </span>
          </div>
          <div
            aria-label={t("a11y.profileCompletion", {
              percentage: completionPercentage
            })}
            aria-valuemax={100}
            aria-valuemin={0}
            aria-valuenow={completionPercentage}
            className="mt-6 h-2 overflow-hidden rounded-sm bg-elevated"
            role="progressbar"
          >
            <div
              className="h-full bg-primary transition-[width]"
              style={{ width: `${completionPercentage}%` }}
            />
          </div>
          <p className="mt-4 text-sm leading-6 text-muted-foreground">
            {completion
              ? t("dashboard.profile.summary", {
                  completed: completion.completed_fields,
                  total: completion.total_fields
                })
              : t("dashboard.profile.loading")}
          </p>
          <Button asChild className="mt-5" variant="secondary">
            <Link href="/profile">
              {t("dashboard.profile.action")}
              <ArrowRight aria-hidden className="ml-2 size-4" />
            </Link>
          </Button>
        </Card>

        <Card>
          <div className="flex flex-wrap items-end justify-between gap-4">
            <div>
              <p className="text-xs font-bold uppercase tracking-[0.14em] text-primary-hover">
                {t("dashboard.events.eyebrow")}
              </p>
              <h2 className="mt-2 text-2xl font-semibold">
                {t("dashboard.events.title")}
              </h2>
            </div>
            <Button asChild variant="ghost">
              <Link href="/events/my">{t("dashboard.events.viewAll")}</Link>
            </Button>
          </div>
          {isLoading ? (
            <p className="mt-6 text-sm text-muted-foreground">
              {t("dashboard.events.loading")}
            </p>
          ) : registrations.length === 0 ? (
            <div className="mt-6 rounded-sm border border-dashed bg-elevated/35 p-5">
              <p className="font-semibold">{t("dashboard.events.emptyTitle")}</p>
              <p className="mt-2 text-sm text-muted-foreground">
                {t("dashboard.events.emptyDescription")}
              </p>
              <Button asChild className="mt-4">
                <Link href="/events">{t("dashboard.openEventMap")}</Link>
              </Button>
            </div>
          ) : (
            <div className="mt-6 grid gap-3 sm:grid-cols-2">
              {registrations.slice(0, 2).map((registration) => (
                <Link
                  className="rounded-sm border bg-elevated/45 p-4 transition-colors hover:bg-elevated"
                  href={`/events/${registration.event.slug}`}
                  key={registration.id}
                >
                  <p className="text-xs font-semibold uppercase tracking-[0.12em] text-success">
                    {t(
                      `events.registration.status.${registration.status}` as TranslationKey
                    )}
                  </p>
                  <h3 className="mt-2 font-semibold">{registration.event.title}</h3>
                  <p className="mt-2 text-xs text-muted-foreground">
                    {formatDateTime(registration.event.start_at, locale)}
                  </p>
                </Link>
              ))}
            </div>
          )}
        </Card>
      </section>

      <section className="grid gap-5 xl:grid-cols-[1.2fr_0.8fr]">
        {readiness ? (
          <ReadinessCard compact readiness={readiness} />
        ) : (
          <Card>
            <p className="text-sm text-muted-foreground">
              {t("profile.loading")}
            </p>
          </Card>
        )}
        <Card>
          <p className="text-xs font-bold uppercase tracking-[0.14em] text-primary-hover">
            {t("dashboard.learning.title")}
          </p>
          <h2 className="mt-2 text-2xl font-semibold">
            {nextClass ? t(nextClass.labelKey) : t("dashboard.learning.empty")}
          </h2>
          <p className="mt-3 text-sm leading-6 text-muted-foreground">
            {t("dashboard.learning.description")}
          </p>
          {selectedClasses.length ? (
            <div className="mt-5 flex flex-wrap gap-2">
              {selectedClasses.slice(0, 6).map((value) => {
                const catalogItem = classCatalog.find(
                  (item) => item.value === value
                );
                return (
                  <Badge key={value}>
                    {catalogItem ? t(catalogItem.labelKey) : value}
                  </Badge>
                );
              })}
            </div>
          ) : null}
          <Button asChild className="mt-5" variant="secondary">
            <Link href="/profile">
              {t("dashboard.readiness.action")}
              <ArrowRight aria-hidden className="ml-2 size-4" />
            </Link>
          </Button>
        </Card>
      </section>

      <Card>
        <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
          <div>
            <p className="text-xs font-bold uppercase tracking-[0.14em] text-primary-hover">
              {t("dashboard.examCountdown.eyebrow")}
            </p>
            <h2 className="mt-2 text-2xl font-semibold">
              {t("dashboard.examCountdown.title")}
            </h2>
            <p className="mt-2 text-sm leading-6 text-muted-foreground">
              {t("dashboard.examCountdown.description")}
            </p>
          </div>
          <Button asChild variant="secondary">
            <Link href="/profile">{t("dashboard.examCountdown.manage")}</Link>
          </Button>
        </div>
        {plannedExams.length ? (
          <div className="mt-6 grid gap-3 md:grid-cols-2 xl:grid-cols-3">
            {plannedExams.slice(0, 3).map((exam) => (
              <div className="border-l-4 border-primary bg-surface p-4" key={`${exam.name}-${exam.date}`}>
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <p className="font-serif text-xl font-semibold">{exam.name}</p>
                    <p className="mt-1 text-xs text-muted-foreground">{exam.date}</p>
                  </div>
                  <CalendarClock aria-hidden className="size-5 text-accent" />
                </div>
                <p className="mt-5 text-3xl font-semibold text-primary-hover">
                  {t("dashboard.examCountdown.days", { count: exam.daysLeft })}
                </p>
                {exam.target_score ? (
                  <p className="mt-2 text-sm text-muted-foreground">
                    {t("dashboard.examCountdown.target", { score: exam.target_score })}
                  </p>
                ) : null}
                <p className="mt-4 border-t pt-3 text-xs leading-5 text-muted-foreground">
                  {nextClass
                    ? `${t("dashboard.learning.next")}: ${t(nextClass.labelKey)}`
                    : t("dashboard.examCountdown.nextAction")}
                </p>
              </div>
            ))}
          </div>
        ) : (
          <div className="mt-6 border border-dashed bg-elevated/35 p-5">
            <p className="font-semibold">{t("dashboard.examCountdown.emptyTitle")}</p>
            <p className="mt-2 text-sm text-muted-foreground">
              {t("dashboard.examCountdown.emptyDescription")}
            </p>
          </div>
        )}
      </Card>

      <section aria-labelledby="dashboard-workspace">
        <div className="mb-4 flex items-end justify-between gap-4">
          <div>
            <p className="text-xs font-bold uppercase tracking-[0.14em] text-primary-hover">
              {t("dashboard.workspace.eyebrow")}
            </p>
            <h2 className="mt-1 text-2xl font-semibold" id="dashboard-workspace">
              {t("dashboard.workspace.title")}
            </h2>
          </div>
          <span className="hidden text-sm text-muted-foreground sm:block">
            {t("dashboard.workspace.betaNote")}
          </span>
        </div>
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          <DashboardModuleCard
            detail={t("dashboard.roadmap.detail")}
            href="/roadmap"
            icon={Route}
            title={t("dashboard.roadmap.title")}
          />
          <DashboardModuleCard
            detail={t("dashboard.universities.detail")}
            disclaimer={t("beta.disclaimer.admissions")}
            href="/universities"
            icon={GraduationCap}
            title={t("dashboard.universities.title")}
          />
          <DashboardModuleCard
            detail={t("dashboard.exams.detail")}
            href="/exams"
            icon={BookOpenCheck}
            title={t("dashboard.exams.title")}
          />
          {profile?.onboarding_completed_at ? (
            <DashboardModuleCard
              detail={t("dashboard.essays.detail")}
              disclaimer={t("beta.disclaimer.essays")}
              href="/essays"
              icon={FilePenLine}
              title={t("dashboard.essays.title")}
            />
          ) : null}
          <DashboardModuleCard
            detail={t("dashboard.finance.detail")}
            disclaimer={t("beta.disclaimer.finance")}
            href="/finance"
            icon={CircleDollarSign}
            title={t("dashboard.finance.title")}
          />
          <DashboardModuleCard
            detail={t("dashboard.activities.detail")}
            href="/activities"
            icon={CalendarDays}
            title={t("dashboard.activities.title")}
          />
        </div>
      </section>

      <section className="grid gap-5 lg:grid-cols-[1.2fr_0.8fr]">
        <Card>
          <div className="flex items-start gap-4">
            <Sparkles aria-hidden className="mt-1 size-5 shrink-0 text-accent" />
            <div>
              <Badge>{t("dashboard.assistant.badge")}</Badge>
              <h2 className="mt-3 text-xl font-semibold">
                {t("dashboard.assistant.title")}
              </h2>
              <p className="mt-2 text-sm leading-6 text-muted-foreground">
                {t("dashboard.assistant.description")}
              </p>
            </div>
          </div>
        </Card>

        <Card>
          <p className="text-xs font-bold uppercase tracking-[0.14em] text-primary-hover">
            {t("dashboard.subscription.eyebrow")}
          </p>
          <div className="mt-3 flex items-center justify-between gap-4">
            <h2 className="text-2xl font-semibold">{t(planKey)}</h2>
            <Badge>{t("dashboard.subscription.mock")}</Badge>
          </div>
          <dl className="mt-5 grid grid-cols-2 gap-4 text-sm">
            <div>
              <dt className="text-muted-foreground">
                {t("dashboard.subscription.aiUsage")}
              </dt>
              <dd className="mt-1 font-semibold">
                {user?.subscription.ai_message_count ?? 0}
              </dd>
            </div>
            <div>
              <dt className="text-muted-foreground">
                {t("dashboard.subscription.essayUsage")}
              </dt>
              <dd className="mt-1 font-semibold">
                {user?.subscription.essay_review_count ?? 0}
              </dd>
            </div>
          </dl>
          <Button asChild className="mt-5" variant="secondary">
            <Link href="/pricing">{t("dashboard.subscription.action")}</Link>
          </Button>
        </Card>
      </section>

      <p className="text-xs leading-5 text-muted-foreground">
        {t("dashboard.disclaimer")}
      </p>
    </div>
  );
}

function DashboardModuleCard({
  icon: Icon,
  title,
  detail,
  href,
  disclaimer
}: {
  icon: LucideIcon;
  title: string;
  detail: string;
  href: string;
  disclaimer?: string;
}) {
  const { t } = useI18n();

  return (
    <Card className="flex flex-col">
      <Icon aria-hidden className="size-5 text-accent" />
      <h3 className="mt-4 text-lg font-semibold">{title}</h3>
      <p className="mt-2 text-sm leading-6 text-muted-foreground">{detail}</p>
      {disclaimer ? (
        <p className="mt-3 text-xs leading-5 text-muted-foreground">{disclaimer}</p>
      ) : null}
      <Link
        className="mt-auto inline-flex items-center gap-2 pt-5 text-sm font-semibold text-primary-hover hover:underline"
        href={href}
      >
        {t("dashboard.workspace.openModule")}
        <ArrowRight aria-hidden className="size-4" />
      </Link>
    </Card>
  );
}
