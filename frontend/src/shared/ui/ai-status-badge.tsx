"use client";

import { useI18n, type TranslationKey } from "@/shared/i18n";
import { cn } from "@/shared/lib/cn";

import { Badge } from "./badge";

export type AIStatus = "queued" | "running" | "cached" | "missing" | "failed";

const STATUS_STYLES: Record<AIStatus, string> = {
  queued: "border-muted-foreground/30 bg-surface text-muted-foreground",
  running: "border-accent/35 bg-accent/10 text-accent",
  cached: "border-success/35 bg-success/10 text-success",
  missing: "border-muted-foreground/30 bg-surface text-muted-foreground",
  failed: "border-danger/35 bg-danger/10 text-danger"
};

/** Visual status badge for an AI-backed section (PERFORMANCE-011 PART 3):
 * queued/running while an explicit refresh is in flight, cached once a
 * result exists, missing before the first refresh, failed on error. Never
 * implies AI ran on a normal page render -- callers only show "running"
 * around their own explicit refresh action. */
export function AIStatusBadge({ status, className }: { status: AIStatus; className?: string }) {
  const { t } = useI18n();
  return (
    <Badge className={cn(STATUS_STYLES[status], className)}>
      {t(`common.aiStatus.${status}` as TranslationKey)}
    </Badge>
  );
}
