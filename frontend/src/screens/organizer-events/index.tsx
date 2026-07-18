"use client";

import { Archive, CalendarPlus, Send, Users } from "lucide-react";
import Link from "next/link";
import { useCallback, useEffect, useState } from "react";

import {
  ModerationStatusBadge,
  type OrganizerEvent,
  type OrganizerEventAnalytics,
  type PaginatedResponse
} from "@/entities/event";
import {
  archiveOrganizerEventRequest,
  cancelOrganizerEventRequest,
  getOrganizerEventAnalyticsRequest,
  getOrganizerEventsRequest,
  submitOrganizerEventRequest
} from "@/features/organizer-events";
import { StatValue } from "@/entities/university";
import { useI18n } from "@/shared/i18n";
import { formatDateTime } from "@/shared/lib/date-time";
import { Button } from "@/shared/ui/button";
import { Card } from "@/shared/ui/card";
import { DEFAULT_PAGE_SIZE, PaginationControls } from "@/shared/ui/pagination";
import { Reveal } from "@/shared/ui/reveal";

export function OrganizerEventsScreen() {
  const { locale, t } = useI18n();
  const [events, setEvents] = useState<OrganizerEvent[]>([]);
  const [analytics, setAnalytics] = useState<OrganizerEventAnalytics | null>(null);
  const [totalCount, setTotalCount] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [isLoading, setIsLoading] = useState(true);
  const [hasError, setHasError] = useState(false);
  const [actionSlug, setActionSlug] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);

  const fetchEvents = useCallback(async () => {
    const [response, analyticsResponse]: [
      PaginatedResponse<OrganizerEvent>,
      OrganizerEventAnalytics
    ] = await Promise.all([
      getOrganizerEventsRequest({ page: currentPage, page_size: DEFAULT_PAGE_SIZE }),
      getOrganizerEventAnalyticsRequest()
    ]);
    setEvents(response.results);
    setTotalCount(response.count);
    setAnalytics(analyticsResponse);
  }, [currentPage]);

  const loadEvents = useCallback(async () => {
    setIsLoading(true);
    setHasError(false);
    try {
      await fetchEvents();
    } catch {
      setHasError(true);
    } finally {
      setIsLoading(false);
    }
  }, [fetchEvents]);

  useEffect(() => {
    void loadEvents();
  }, [loadEvents]);

  const statusCounts = {
    pending:
      analytics?.pending_count ??
      events.filter((event) => event.status === "pending_review").length,
    published:
      analytics?.published_count ??
      events.filter((event) => event.status === "published").length,
    needsAction:
      analytics !== null
        ? analytics.draft_count + analytics.rejected_count
        : events.filter((event) => ["draft", "rejected"].includes(event.status)).length
  };
  const totalPages = Math.max(1, Math.ceil(totalCount / DEFAULT_PAGE_SIZE));
  const pageStart = totalCount ? (currentPage - 1) * DEFAULT_PAGE_SIZE + 1 : 0;
  const pageEnd = Math.min(pageStart + Math.max(events.length, 1) - 1, totalCount);

  async function runAction(
    event: OrganizerEvent,
    action: "submit" | "cancel" | "archive"
  ) {
    const confirmationKey =
      action === "submit"
        ? "organizer.confirm.submit"
        : action === "cancel"
          ? "organizer.confirm.cancel"
          : "organizer.confirm.archive";
    if (!window.confirm(t(confirmationKey))) {
      return;
    }

    setActionSlug(event.slug);
    setActionError(null);
    try {
      if (action === "submit") {
        await submitOrganizerEventRequest(event.slug);
      } else if (action === "cancel") {
        await cancelOrganizerEventRequest(event.slug);
      } else {
        await archiveOrganizerEventRequest(event.slug);
      }
      // Refresh in place -- the mutation already succeeded, so re-fetching
      // through loadEvents() (which flips isLoading) would blank the whole
      // analytics summary and event grid for a refresh the user didn't ask
      // to see a loader for.
      await fetchEvents();
    } catch {
      setActionError(event.slug);
    } finally {
      setActionSlug(null);
    }
  }

  return (
    <div className="space-y-6">
      <section className="rounded-sm border bg-card p-6 shadow-card sm:p-9">
        <p className="text-eyebrow text-primary-hover">{t("organizer.list.eyebrow")}</p>
        <div className="mt-3 flex flex-col justify-between gap-5 lg:flex-row lg:items-end">
          <div>
            <h1 className="text-display">{t("organizer.list.title")}</h1>
            <p className="mt-4 max-w-2xl leading-7 text-muted-foreground">
              {t("organizer.list.description")}
            </p>
          </div>
          <Button asChild>
            <Link href="/organizer/events/new">
              <CalendarPlus aria-hidden className="mr-2 size-4" />
              {t("organizer.actions.create")}
            </Link>
          </Button>
        </div>
      </section>

      {!isLoading && !hasError ? (
        <section aria-labelledby="organizer-status-summary">
          <div className="mb-3">
            <h2 className="text-2xl font-semibold" id="organizer-status-summary">
              {t("organizer.statusSummary.title")}
            </h2>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-muted-foreground">
              {t("organizer.statusSummary.guide")}
            </p>
          </div>
          <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
            {(
              [
                { label: t("organizer.statusSummary.total"), value: totalCount, suffix: undefined },
                {
                  label: t("organizer.statusSummary.pending"),
                  value: statusCounts.pending,
                  suffix: undefined
                },
                {
                  label: t("organizer.statusSummary.published"),
                  value: statusCounts.published,
                  suffix: undefined
                },
                {
                  label: t("organizer.statusSummary.registrations"),
                  value: analytics?.total_registrations ?? 0,
                  suffix: undefined
                },
                {
                  label: t("organizer.statusSummary.checkedIn"),
                  value: analytics?.checked_in_count ?? 0,
                  suffix: undefined
                },
                {
                  label: t("organizer.statusSummary.attendanceRate"),
                  value:
                    analytics?.attendance_rate === null || analytics?.attendance_rate === undefined
                      ? t("events.value.notSet")
                      : analytics.attendance_rate,
                  suffix:
                    analytics?.attendance_rate === null || analytics?.attendance_rate === undefined
                      ? undefined
                      : "%"
                },
                {
                  label: t("organizer.statusSummary.needsAction"),
                  value: statusCounts.needsAction,
                  suffix: undefined
                }
              ] as Array<{ label: string; value: string | number; suffix?: string }>
            ).map(({ label, value, suffix }, index) => (
              <Reveal delayMs={index * 30} key={label}>
                <Card className="p-4">
                  <p className="text-eyebrow text-muted-foreground">{label}</p>
                  <p className="text-feature-heading mt-2 text-accent">
                    <StatValue suffix={suffix} value={value} />
                  </p>
                </Card>
              </Reveal>
            ))}
          </div>
        </section>
      ) : null}

      {isLoading ? (
        <Card>
          <p className="text-sm text-muted-foreground">{t("organizer.states.loading")}</p>
        </Card>
      ) : hasError ? (
        <Card className="border-danger/35 bg-danger/10">
          <p className="text-sm text-danger" role="alert">
            {t("organizer.states.loadError")}
          </p>
          <Button className="mt-4" onClick={() => void loadEvents()} type="button">
            {t("events.actions.retry")}
          </Button>
        </Card>
      ) : events.length === 0 ? (
        <Card>
          <h2 className="text-xl font-semibold">{t("organizer.states.emptyTitle")}</h2>
          <p className="mt-2 text-sm text-muted-foreground">
            {t("organizer.states.emptyDescription")}
          </p>
        </Card>
      ) : (
        <div className="space-y-4">
          <p className="text-sm font-semibold text-muted-foreground">
            {t("pagination.showingRange", {
              start: pageStart,
              end: pageEnd,
              total: totalCount
            })}
          </p>
          <section
            aria-label={t("organizer.list.results")}
            className="grid gap-5 xl:grid-cols-2"
          >
            {events.map((event) => (
              <Card className="flex flex-col" key={event.id}>
              <div className="flex flex-wrap items-center justify-between gap-3">
                <ModerationStatusBadge status={event.status} />
                <span className="text-xs text-muted-foreground">
                  {formatDateTime(event.updated_at, locale)}
                </span>
              </div>
              <h2 className="mt-4 text-2xl font-semibold">{event.title}</h2>
              <p className="mt-2 line-clamp-2 text-sm leading-6 text-muted-foreground">
                {event.short_description}
              </p>
              <dl className="mt-5 grid gap-3 text-sm sm:grid-cols-2">
                <div>
                  <dt className="text-xs text-muted-foreground">
                    {t("events.fields.start")}
                  </dt>
                  <dd className="mt-1 font-medium">
                    {formatDateTime(event.start_at, locale)}
                  </dd>
                </div>
                <div>
                  <dt className="text-xs text-muted-foreground">
                    {t("events.fields.location")}
                  </dt>
                  <dd className="mt-1 font-medium">
                    {[event.location.city, event.location.country]
                      .filter(Boolean)
                      .join(", ")}
                  </dd>
                </div>
              </dl>
              {event.moderation_note ? (
                <p className="mt-5 rounded-lg border border-danger/25 bg-danger/10 p-3 text-sm text-danger">
                  {t("organizer.moderationNote", {
                    reason: event.moderation_note
                  })}
                </p>
              ) : null}
              {actionError === event.slug ? (
                <p className="mt-4 text-sm text-danger" role="alert">
                  {t("organizer.states.actionError")}
                </p>
              ) : null}
              <div className="mt-auto flex flex-wrap gap-2 pt-6">
                {event.can_edit ? (
                  <Button asChild variant="secondary">
                    <Link href={`/organizer/events/${event.slug}`}>
                      {t("organizer.actions.edit")}
                    </Link>
                  </Button>
                ) : null}
                {event.can_submit ? (
                  <Button
                    disabled={actionSlug === event.slug}
                    onClick={() => void runAction(event, "submit")}
                    type="button"
                  >
                    <Send aria-hidden className="mr-2 size-4" />
                    {t("organizer.actions.submit")}
                  </Button>
                ) : null}
                {event.can_view_participants ? (
                  <>
                    <Button asChild variant="secondary">
                      <Link href={`/organizer/events/${event.slug}/participants`}>
                        <Users aria-hidden className="mr-2 size-4" />
                        {t("organizer.actions.participants")}
                      </Link>
                    </Button>
                    <Button
                      className="text-danger"
                      disabled={actionSlug === event.slug}
                      onClick={() => void runAction(event, "cancel")}
                      type="button"
                      variant="ghost"
                    >
                      {t("organizer.actions.cancelEvent")}
                    </Button>
                  </>
                ) : null}
                {["draft", "pending_review", "rejected"].includes(event.status) ? (
                  <Button
                    disabled={actionSlug === event.slug}
                    onClick={() => void runAction(event, "archive")}
                    type="button"
                    variant="ghost"
                  >
                    <Archive aria-hidden className="mr-2 size-4" />
                    {t("organizer.actions.archive")}
                  </Button>
                ) : null}
              </div>
              </Card>
            ))}
          </section>
          {totalPages > 1 ? (
            <PaginationControls
              currentPage={currentPage}
              onNext={() => setCurrentPage((page) => page + 1)}
              onPageSelect={setCurrentPage}
              onPrevious={() => setCurrentPage((page) => page - 1)}
              totalPages={totalPages}
            />
          ) : null}
        </div>
      )}
    </div>
  );
}
