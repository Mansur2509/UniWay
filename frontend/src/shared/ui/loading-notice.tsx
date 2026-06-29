"use client";

import { useI18n } from "@/shared/i18n";
import { useSlowLoad } from "@/shared/lib/use-slow-load";

import { Card } from "./card";

/**
 * Standard loading card. While mounted (i.e. while the caller is loading) it
 * starts a timer and, if the load is taking unusually long, adds a "the server
 * may be waking up" hint — the honest explanation for a Render cold start —
 * instead of an unexplained spinner that looks stuck.
 */
export function LoadingNotice({ message }: { message: string }) {
  const { t } = useI18n();
  const isSlow = useSlowLoad(true);

  return (
    <Card>
      <p className="text-sm text-muted-foreground">{message}</p>
      {isSlow ? (
        <p className="mt-2 text-xs leading-5 text-muted-foreground" role="status">
          {t("common.wakingUp")}
        </p>
      ) : null}
    </Card>
  );
}
