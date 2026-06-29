"use client";

import { RefreshCw } from "lucide-react";
import { useEffect } from "react";

import { useI18n } from "@/shared/i18n";
import { Button } from "@/shared/ui/button";
import { Card } from "@/shared/ui/card";

/**
 * Route-segment error boundary. Without this, any render-time exception in a
 * page (for example an unexpected data shape or a missing translation key)
 * unmounts the route into a blank page with no feedback — the "blank Essays
 * page" failure mode. This catches that and shows a clear, retryable error
 * while keeping the surrounding app shell mounted.
 */
export default function RouteError({
  error,
  reset
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  const { t } = useI18n();

  useEffect(() => {
    console.error("Route render error:", error);
  }, [error]);

  return (
    <div className="grid min-h-[60vh] place-items-center px-4">
      <Card className="max-w-lg text-center">
        <h1 className="text-xl font-semibold">{t("errorBoundary.title")}</h1>
        <p className="mt-3 text-sm leading-6 text-muted-foreground">
          {t("errorBoundary.description")}
        </p>
        <div className="mt-6 flex flex-wrap justify-center gap-3">
          <Button onClick={() => reset()} type="button">
            <RefreshCw aria-hidden className="mr-2 size-4" />
            {t("errorBoundary.retry")}
          </Button>
          <Button onClick={() => window.location.reload()} type="button" variant="secondary">
            {t("errorBoundary.reload")}
          </Button>
        </div>
      </Card>
    </div>
  );
}
