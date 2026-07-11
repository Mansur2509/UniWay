"use client";

import { useI18n } from "@/shared/i18n";
import { cn } from "@/shared/lib/cn";

/**
 * Small "Updating…" pill for stale-while-revalidate UX: stale data stays on
 * screen while a background refresh runs, instead of the page blanking out
 * to a full loader (PERFORMANCE-011 PART 3).
 */
export function InlineRefreshIndicator({ className }: { className?: string }) {
  const { t } = useI18n();
  return (
    <span
      className={cn("inline-flex items-center gap-1.5 text-xs text-muted-foreground", className)}
      role="status"
    >
      <span aria-hidden className="size-1.5 animate-pulse rounded-full bg-primary" />
      {t("common.updating")}
    </span>
  );
}
