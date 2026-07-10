"use client";

import { useCallback, useEffect, useState } from "react";

import type { ApplicationStatus } from "@/entities/application";
import { APPLICATION_STATUSES } from "@/entities/application";
import type { UserAnalytics } from "@/entities/analytics";
import { getMyAnalyticsRequest } from "@/features/analytics";
import { useI18n, type TranslationKey } from "@/shared/i18n";
import { Badge } from "@/shared/ui/badge";
import { Button } from "@/shared/ui/button";
import { Card } from "@/shared/ui/card";

const ACTIVITY_DISPLAY_LIMIT = 4;

export function AnalyticsWidget() {
  const { t } = useI18n();
  const [analytics, setAnalytics] = useState<UserAnalytics | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [hasError, setHasError] = useState(false);

  const load = useCallback(async () => {
    setIsLoading(true);
    setHasError(false);
    try {
      setAnalytics(await getMyAnalyticsRequest());
    } catch {
      setHasError(true);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const applicationsByStatus = APPLICATION_STATUSES.map((status) => ({
    status,
    count: analytics?.applications_by_status[status] ?? 0
  })).filter((entry) => entry.count > 0);

  const topActivity = Object.entries(analytics?.activity_by_type ?? {})
    .sort(([, a], [, b]) => b - a)
    .slice(0, ACTIVITY_DISPLAY_LIMIT);

  return (
    <section aria-labelledby="dashboard-analytics">
      <div className="mb-3">
        <p className="text-xs font-bold uppercase tracking-[0.14em] text-primary-hover">
          {t("dashboard.analyticsWidget.eyebrow")}
        </p>
        <h2 className="mt-1 text-lg font-semibold" id="dashboard-analytics">
          {t("dashboard.analyticsWidget.title")}
        </h2>
      </div>

      {isLoading ? (
        <Card className="p-4">
          <p className="text-sm text-muted-foreground">{t("dashboard.analyticsWidget.loading")}</p>
        </Card>
      ) : hasError ? (
        <Card className="p-4">
          <p className="text-sm text-danger" role="alert">
            {t("dashboard.analyticsWidget.error")}
          </p>
          <Button className="mt-3" onClick={() => void load()} size="sm" type="button">
            {t("essays.actions.retry")}
          </Button>
        </Card>
      ) : (
        <div className="space-y-3">
          <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
            <Card className="p-4">
              <p className="text-xs font-bold uppercase tracking-[0.12em] text-muted-foreground">
                {t("dashboard.analyticsWidget.profileCompletion")}
              </p>
              <p className="mt-2 font-serif text-3xl font-semibold text-accent">
                {analytics?.profile_completion_percent ?? 0}%
              </p>
            </Card>
            <Card className="p-4">
              <p className="text-xs font-bold uppercase tracking-[0.12em] text-muted-foreground">
                {t("dashboard.analyticsWidget.roadmapProgress")}
              </p>
              <p className="mt-2 font-serif text-3xl font-semibold text-accent">
                {analytics?.roadmap_tasks_completed ?? 0}/{analytics?.roadmap_tasks_total ?? 0}
              </p>
            </Card>
            <Card className="p-4">
              <p className="text-xs font-bold uppercase tracking-[0.12em] text-muted-foreground">
                {t("dashboard.analyticsWidget.essayReviews")}
              </p>
              <p className="mt-2 font-serif text-3xl font-semibold text-accent">
                {analytics?.essay_reviews_count ?? 0}
              </p>
            </Card>
            <Card className="p-4">
              <p className="text-xs font-bold uppercase tracking-[0.12em] text-muted-foreground">
                {t("dashboard.analyticsWidget.upcomingDeadlines")}
              </p>
              <p className="mt-2 font-serif text-3xl font-semibold text-accent">
                {analytics?.upcoming_deadlines_count ?? 0}
              </p>
            </Card>
          </div>

          <div className="grid gap-3 lg:grid-cols-2">
            <Card className="p-4">
              <p className="text-xs font-bold uppercase tracking-[0.12em] text-muted-foreground">
                {t("dashboard.analyticsWidget.applicationsByStatus")}
              </p>
              {applicationsByStatus.length === 0 ? (
                <p className="mt-2 text-xs text-muted-foreground">
                  {t("dashboard.analyticsWidget.applicationsByStatusEmpty")}
                </p>
              ) : (
                <div className="mt-3 flex flex-wrap gap-2">
                  {applicationsByStatus.map(({ status, count }: { status: ApplicationStatus; count: number }) => (
                    <Badge key={status}>
                      {t(`applications.status.${status}` as TranslationKey)}: {count}
                    </Badge>
                  ))}
                </div>
              )}
            </Card>
            <Card className="p-4">
              <p className="text-xs font-bold uppercase tracking-[0.12em] text-muted-foreground">
                {t("dashboard.analyticsWidget.recentActivity")}
              </p>
              {topActivity.length === 0 ? (
                <p className="mt-2 text-xs text-muted-foreground">
                  {t("dashboard.analyticsWidget.recentActivityEmpty")}
                </p>
              ) : (
                <ul className="mt-3 space-y-1.5 text-xs">
                  {topActivity.map(([eventType, count]) => (
                    <li className="flex items-center justify-between gap-2" key={eventType}>
                      <span className="truncate text-muted-foreground">
                        {t(`analytics.eventType.${eventType}` as TranslationKey)}
                      </span>
                      <span className="shrink-0 rounded-sm border bg-surface px-1.5 py-0.5 text-[0.65rem] font-bold">
                        {count}
                      </span>
                    </li>
                  ))}
                </ul>
              )}
            </Card>
          </div>
        </div>
      )}
    </section>
  );
}
