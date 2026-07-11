"use client";

import { useI18n } from "@/shared/i18n";

import { Button } from "./button";

/**
 * Shown when an explicit AI action (e.g. semantic fit refresh, essay
 * scoring) is taking noticeably longer than expected (PERFORMANCE-011 PART
 * 3). Always offers a retry and, when cached/deterministic results already
 * exist, a way to keep using them instead of waiting.
 */
export function TimeoutNotice({
  onRetry,
  onContinueWithCached
}: {
  onRetry: () => void;
  onContinueWithCached?: () => void;
}) {
  const { t } = useI18n();
  return (
    <div className="rounded-sm border border-warning/35 bg-warning/10 p-3 text-sm text-warning" role="status">
      <p>{t("common.timeoutMessage")}</p>
      <div className="mt-2 flex flex-wrap gap-2">
        <Button onClick={onRetry} size="sm" type="button" variant="secondary">
          {t("common.retry")}
        </Button>
        {onContinueWithCached ? (
          <Button onClick={onContinueWithCached} size="sm" type="button" variant="ghost">
            {t("common.continueWithCached")}
          </Button>
        ) : null}
      </div>
    </div>
  );
}
