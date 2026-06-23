"use client";

import type { EventModerationStatus } from "@/entities/event";
import { useI18n, type TranslationKey } from "@/shared/i18n";
import { cn } from "@/shared/lib/cn";

const statusStyles: Record<EventModerationStatus, string> = {
  draft: "border-border bg-elevated text-muted-foreground",
  pending_review: "border-warning/30 bg-warning/10 text-warning",
  published: "border-success/30 bg-success/10 text-success",
  rejected: "border-danger/30 bg-danger/10 text-danger",
  cancelled: "border-danger/30 bg-danger/10 text-danger",
  archived: "border-border bg-muted text-muted-foreground"
};

export function ModerationStatusBadge({
  status,
  className
}: {
  status: EventModerationStatus;
  className?: string;
}) {
  const { t } = useI18n();

  return (
    <span
      className={cn(
        "inline-flex rounded-sm border px-2.5 py-1 text-xs font-semibold",
        statusStyles[status],
        className
      )}
    >
      {t(`organizer.status.${status}` as TranslationKey)}
    </span>
  );
}
