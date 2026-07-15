"use client";

import { useState } from "react";

import type { ReportTargetType } from "@/entities/admin-moderation";
import { createUserReportRequest } from "@/features/reports/api/reports-api";
import { ApiError } from "@/shared/api/client";
import { useI18n, type TranslationKey } from "@/shared/i18n";
import { Button } from "@/shared/ui/button";
import { fieldClassName } from "@/shared/ui/field";

// Curated per-type reason codes shown as a translated picklist. These are
// stable, language-independent values sent as `reason` -- the admin inbox
// filters/reads them as codes, not as whatever language the reporting
// student had selected.
const CATEGORY_CODES: Record<ReportTargetType, string[]> = {
  university: ["incorrect_information", "inappropriate_content", "spam_or_scam", "other"],
  event: [
    "incorrect_information",
    "inappropriate_content",
    "spam_or_scam",
    "suspicious_or_fraudulent",
    "other"
  ],
  organizer: ["suspicious_or_fraudulent", "inappropriate_content", "spam_or_scam", "other"],
  essay_review: ["inaccurate_or_unhelpful", "inappropriate_content", "technical_error", "other"],
  other: ["other"]
};

type Phase = "idle" | "open" | "submitting" | "success" | "duplicate" | "error";

function isDuplicateError(error: unknown): boolean {
  return (
    error instanceof ApiError &&
    typeof error.data === "object" &&
    error.data !== null &&
    "non_field_errors" in error.data
  );
}

export function ReportButton({
  targetType,
  targetId,
  className
}: {
  targetType: ReportTargetType;
  targetId: number;
  className?: string;
}) {
  const { t } = useI18n();
  const categories = CATEGORY_CODES[targetType];
  const [phase, setPhase] = useState<Phase>("idle");
  const [category, setCategory] = useState(categories[0]);
  const [description, setDescription] = useState("");

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setPhase("submitting");
    try {
      await createUserReportRequest({
        target_type: targetType,
        target_id: targetId,
        reason: category,
        description: description.trim() || undefined
      });
      setPhase("success");
    } catch (error) {
      setPhase(isDuplicateError(error) ? "duplicate" : "error");
    }
  }

  if (phase === "success") {
    return (
      <p className={className} role="status">
        <span className="text-xs text-muted-foreground">{t("report.success")}</span>
      </p>
    );
  }

  if (phase === "idle") {
    return (
      <Button
        aria-label={t("report.action")}
        className={className}
        onClick={() => setPhase("open")}
        size="sm"
        type="button"
        variant="ghost"
      >
        {t("report.action")}
      </Button>
    );
  }

  return (
    <form className={className} onSubmit={(event) => void handleSubmit(event)}>
      <div className="space-y-2 rounded-sm border bg-surface p-3">
        <label className="block">
          <span className="text-xs font-semibold">{t("report.categoryLabel")}</span>
          <select
            className={fieldClassName}
            disabled={phase === "submitting"}
            onChange={(event) => setCategory(event.target.value)}
            value={category}
          >
            {categories.map((code) => (
              <option key={code} value={code}>
                {t(`report.category.${code}` as TranslationKey)}
              </option>
            ))}
          </select>
        </label>
        <label className="block">
          <span className="text-xs font-semibold">{t("report.descriptionLabel")}</span>
          <textarea
            className={fieldClassName}
            disabled={phase === "submitting"}
            maxLength={2000}
            onChange={(event) => setDescription(event.target.value)}
            rows={3}
            value={description}
          />
        </label>
        {phase === "duplicate" ? (
          <p className="text-xs text-warning" role="alert">
            {t("report.duplicate")}
          </p>
        ) : phase === "error" ? (
          <p className="text-xs text-danger" role="alert">
            {t("report.error")}
          </p>
        ) : null}
        <div className="flex flex-wrap gap-2">
          <Button disabled={phase === "submitting"} size="sm" type="submit">
            {phase === "submitting" ? t("report.submitting") : t("report.submit")}
          </Button>
          <Button
            disabled={phase === "submitting"}
            onClick={() => setPhase("idle")}
            size="sm"
            type="button"
            variant="ghost"
          >
            {t("common.actions.cancel")}
          </Button>
        </div>
      </div>
    </form>
  );
}
