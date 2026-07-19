"use client";

import { Archive, GraduationCap, RotateCcw } from "lucide-react";

import type { ApplicationTrackerItem } from "@/entities/application";
import { DEADLINE_STATUS_TONE, FIT_TIER_TONE, PRIORITY_TONE } from "@/entities/application/lib/tone";
import { useI18n, type TranslationKey } from "@/shared/i18n";
import { formatDate } from "@/shared/lib/date-time";
import { Badge } from "@/shared/ui/badge";
import { Button } from "@/shared/ui/button";
import { Card } from "@/shared/ui/card";
import { IconButton } from "@/shared/ui/icon-button";
import { IconChip } from "@/shared/ui/icon-chip";
import { AppIcon } from "@/shared/ui/icon";

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
          <Badge tone={FIT_TIER_TONE[target.fit_tier]}>
            {t(`applications.fitTier.${target.fit_tier}` as TranslationKey)}
          </Badge>
          <Badge tone="muted">
            {t(`applications.round.${target.application_round}` as TranslationKey)}
          </Badge>
          <Badge tone={PRIORITY_TONE[target.priority]}>
            {t(`applications.priority.${target.priority}` as TranslationKey)}
          </Badge>
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
        <IconChip icon={GraduationCap} size="sm" tone="accent" />
        {target.university_name}
      </h3>
      {target.target_program_name ? (
        <p className="text-xs text-muted-foreground">{target.target_program_name}</p>
      ) : null}
      <Badge className="w-fit" tone={DEADLINE_STATUS_TONE[officialDeadline.status]}>
        {t(`applications.deadlineStatus.${officialDeadline.status}` as TranslationKey)}
      </Badge>
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
