"use client";

import { GraduationCap } from "lucide-react";

import type { ApplicationTrackerItem } from "@/entities/application";
import { useI18n, type TranslationKey } from "@/shared/i18n";
import { formatDate } from "@/shared/lib/date-time";
import { Button } from "@/shared/ui/button";
import { Card } from "@/shared/ui/card";

// Mirrors urgencyForDeadline in screens/applications/index.tsx -- kept as a
// small self-contained calc here (rather than a shared import) since this
// card only needs a highlight for near-term deadlines, not the full
// urgency-filter matching logic. Only returns a badge for overdue/critical/
// urgent/soon -- anything further out stays unbadged to keep the card calm.
function urgencyBadge(deadline: string | null): { label: string; classes: string } | null {
  if (!deadline) return null;
  const parsed = new Date(`${deadline}T00:00:00`);
  if (Number.isNaN(parsed.getTime())) return null;
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const days = Math.round((parsed.getTime() - today.getTime()) / 86_400_000);
  if (days < 0) return { label: "overdue", classes: "border-danger/45 bg-danger/10 text-danger" };
  if (days <= 7) return { label: "critical", classes: "border-danger/45 bg-danger/10 text-danger" };
  if (days <= 14) return { label: "urgent", classes: "border-warning/45 bg-warning/10 text-warning" };
  if (days <= 30) return { label: "soon", classes: "border-deadline/45 bg-deadline/10 text-deadline" };
  return null;
}

const PRIORITY_STYLES: Record<string, string> = {
  low: "border-muted-foreground/30 bg-surface text-muted-foreground",
  medium: "border-accent/35 bg-accent/10 text-accent",
  high: "border-warning/35 bg-warning/10 text-warning",
  dream: "border-danger/35 bg-danger/10 text-danger"
};

const FIT_TIER_STYLES: Record<string, string> = {
  reach: "border-danger/35 bg-danger/10 text-danger",
  competitive: "border-warning/35 bg-warning/10 text-warning",
  target: "border-accent/35 bg-accent/10 text-accent",
  safety: "border-success/35 bg-success/10 text-success",
  unknown: "border-muted-foreground/30 bg-surface text-muted-foreground"
};

const DEADLINE_STATUS_STYLES: Record<string, string> = {
  verified: "border-success/35 bg-success/10 text-success",
  estimated: "border-warning/35 bg-warning/10 text-warning",
  not_published: "border-muted-foreground/30 bg-surface text-muted-foreground",
  outdated: "border-danger/35 bg-danger/10 text-danger",
  requires_review: "border-warning/35 bg-warning/10 text-warning"
};

export function ApplicationCard({
  application,
  isSelected,
  onSelect
}: {
  application: ApplicationTrackerItem;
  isSelected?: boolean;
  onSelect: (application: ApplicationTrackerItem) => void;
}) {
  const { locale, t } = useI18n();
  const incompleteCount = [
    application.essays_status !== "submitted" && application.essays_status !== "ready",
    application.recommendations_status !== "submitted" &&
      application.recommendations_status !== "received",
    application.documents_status !== "submitted" && application.documents_status !== "ready"
  ].filter(Boolean).length;
  const progress = application.checklist_progress;
  const deadline =
    application.official_deadline.status === "verified"
      ? application.official_deadline.date
      : application.personal_estimated_deadline || application.deadline;
  const urgency = urgencyBadge(deadline);

  return (
    <Card
      className={`flex min-w-0 flex-col gap-2 p-4 hover:border-application/45 ${isSelected ? "border-primary/60" : ""}`}
      interactive
    >
      <div className="flex flex-wrap items-center gap-2">
        <span
          className={`rounded-sm border px-2 py-0.5 text-[0.65rem] font-semibold uppercase tracking-wide ${PRIORITY_STYLES[application.priority]}`}
        >
          {t(`applications.priority.${application.priority}` as TranslationKey)}
        </span>
        <span
          className={`rounded-sm border px-2 py-0.5 text-[0.65rem] font-semibold uppercase tracking-wide ${FIT_TIER_STYLES[application.fit_tier]}`}
          title={t("applications.card.fitTierHelp")}
        >
          {t(`applications.fitTier.${application.fit_tier}` as TranslationKey)}
        </span>
        <span className="rounded-sm border bg-surface px-2 py-0.5 text-[0.65rem] font-semibold uppercase tracking-wide text-muted-foreground">
          {t(`applications.round.${application.application_round}` as TranslationKey)}
        </span>
      </div>
      <h3 className="flex items-center gap-2 text-base font-semibold break-words">
        <GraduationCap aria-hidden className="size-4 shrink-0 text-accent" />
        {application.university_name}
      </h3>
      {deadline ? (
        <p className="flex flex-wrap items-center gap-1.5 text-xs text-muted-foreground">
          {t("applications.card.deadline", { date: formatDate(deadline, locale) })}
          {urgency ? (
            <span
              className={`rounded-sm border px-1.5 py-0.5 text-[0.6rem] font-bold uppercase tracking-wide ${urgency.classes}`}
            >
              {t(`applications.urgency.${urgency.label}` as TranslationKey)}
            </span>
          ) : null}
        </p>
      ) : (
        <p className="text-xs italic text-muted-foreground">
          {t("applications.card.noDeadline")}
        </p>
      )}
      <span
        className={`w-fit rounded-sm border px-2 py-0.5 text-[0.65rem] font-semibold uppercase tracking-wide ${DEADLINE_STATUS_STYLES[application.official_deadline.status]}`}
      >
        {t(
          `applications.deadlineStatus.${application.official_deadline.status}` as TranslationKey
        )}
      </span>
      <p className="text-xs text-muted-foreground">
        {t("applications.card.incompleteRequirements", { count: incompleteCount })}
      </p>
      {progress.total > 0 ? (
        <div className="flex items-center gap-2">
          <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-muted-foreground/15">
            <div
              className="h-full rounded-full bg-accent"
              style={{ width: `${progress.percent ?? 0}%` }}
            />
          </div>
          <span className="shrink-0 text-[0.65rem] text-muted-foreground">
            {t("applications.card.checklistProgress", {
              completed: progress.completed,
              total: progress.total
            })}
          </span>
        </div>
      ) : null}
      <Button
        className="mt-2"
        onClick={() => onSelect(application)}
        size="sm"
        type="button"
        variant={isSelected ? "secondary" : "primary"}
      >
        {t("applications.card.open")}
      </Button>
    </Card>
  );
}
