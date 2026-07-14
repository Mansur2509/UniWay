"use client";

import { Archive, GraduationCap, RotateCcw } from "lucide-react";

import type { ApplicationTrackerItem } from "@/entities/application";
import { useI18n, type TranslationKey } from "@/shared/i18n";
import { formatDate } from "@/shared/lib/date-time";
import { AppIcon } from "@/shared/ui/icon";
import { IconButton } from "@/shared/ui/icon-button";
import { Button } from "@/shared/ui/button";
import { Card } from "@/shared/ui/card";

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

export function ProspectiveTargetCard({
  isArchived = false,
  onArchive,
  onEdit,
  onRestore,
  onStartApplication,
  target
}: {
  isArchived?: boolean;
  onArchive?: (target: ApplicationTrackerItem) => void;
  onEdit: (target: ApplicationTrackerItem) => void;
  onRestore?: (target: ApplicationTrackerItem) => void;
  onStartApplication?: (target: ApplicationTrackerItem) => void;
  target: ApplicationTrackerItem;
}) {
  const { locale, t } = useI18n();
  const officialDeadline = target.official_deadline;
  const hasOfficialDate = officialDeadline.status === "verified" || officialDeadline.status === "estimated";

  return (
    <Card className="flex min-w-0 flex-col gap-2 p-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="flex flex-wrap items-center gap-2">
          <span
            className={`rounded-sm border px-2 py-0.5 text-[0.65rem] font-semibold uppercase tracking-wide ${FIT_TIER_STYLES[target.fit_tier]}`}
          >
            {t(`applications.fitTier.${target.fit_tier}` as TranslationKey)}
          </span>
          <span className="rounded-sm border bg-surface px-2 py-0.5 text-[0.65rem] font-semibold uppercase tracking-wide text-muted-foreground">
            {t(`applications.round.${target.application_round}` as TranslationKey)}
          </span>
          <span className="rounded-sm border bg-surface px-2 py-0.5 text-[0.65rem] font-semibold uppercase tracking-wide text-muted-foreground">
            {t(`applications.priority.${target.priority}` as TranslationKey)}
          </span>
        </div>
        {isArchived ? (
          <IconButton
            label={t("prospective.card.restore")}
            onClick={() => onRestore?.(target)}
          >
            <AppIcon decorative icon={RotateCcw} size="sm" />
          </IconButton>
        ) : (
          <IconButton label={t("prospective.card.archive")} onClick={() => onArchive?.(target)}>
            <AppIcon decorative icon={Archive} size="sm" />
          </IconButton>
        )}
      </div>
      <h3 className="flex items-center gap-2 text-base font-semibold break-words">
        <AppIcon decorative icon={GraduationCap} className="text-accent" size="sm" />
        {target.university_name}
      </h3>
      {target.target_program_name ? (
        <p className="text-xs text-muted-foreground">{target.target_program_name}</p>
      ) : null}
      <span
        className={`w-fit rounded-sm border px-2 py-0.5 text-[0.65rem] font-semibold uppercase tracking-wide ${DEADLINE_STATUS_STYLES[officialDeadline.status]}`}
      >
        {t(`applications.deadlineStatus.${officialDeadline.status}` as TranslationKey)}
      </span>
      {hasOfficialDate && officialDeadline.date ? (
        <p className="text-xs text-muted-foreground">
          {t("prospective.card.officialDeadline", {
            date: formatDate(officialDeadline.date, locale)
          })}
        </p>
      ) : (
        <p className="text-xs italic text-muted-foreground">
          {t("prospective.card.officialDeadlineUnknown")}
        </p>
      )}
      {target.personal_estimated_deadline ? (
        <p className="text-xs text-muted-foreground">
          {t("prospective.card.personalDeadline", {
            date: formatDate(target.personal_estimated_deadline, locale)
          })}
        </p>
      ) : null}
      {target.notes ? (
        <p className="line-clamp-2 text-xs text-muted-foreground">{target.notes}</p>
      ) : null}
      <div className="mt-2 flex flex-wrap gap-2">
        <Button onClick={() => onEdit(target)} size="sm" type="button" variant="secondary">
          {t("prospective.card.edit")}
        </Button>
        {!isArchived && onStartApplication ? (
          <Button onClick={() => onStartApplication(target)} size="sm" type="button">
            {t("prospective.card.startApplication")}
          </Button>
        ) : null}
      </div>
    </Card>
  );
}
