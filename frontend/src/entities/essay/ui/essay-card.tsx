"use client";

import { ExternalLink, FileText } from "lucide-react";

import type { EssayWorkspace } from "@/entities/essay";
import { useI18n, type TranslationKey } from "@/shared/i18n";
import { formatDate } from "@/shared/lib/date-time";
import { Badge, type BadgeTone } from "@/shared/ui/badge";
import { Button } from "@/shared/ui/button";
import { Card } from "@/shared/ui/card";
import { IconChip } from "@/shared/ui/icon-chip";

const STATUS_TONE: Record<string, BadgeTone> = {
  suggested: "primary",
  planned: "accent",
  not_started: "muted",
  drafting: "accent",
  needs_revision: "warning",
  reviewed: "accent",
  ready: "success",
  submitted: "info",
  skipped: "muted"
};

const VERIFICATION_TONE: Record<string, BadgeTone> = {
  verified: "success",
  needs_verification: "warning",
  missing: "muted"
};

const PRIORITY_TONE: Record<string, BadgeTone> = {
  low: "muted",
  medium: "accent",
  high: "warning",
  urgent: "danger"
};

export function EssayCard({
  essay,
  isSelected,
  onSelect
}: {
  essay: EssayWorkspace;
  isSelected?: boolean;
  onSelect: (essay: EssayWorkspace) => void;
}) {
  const { locale, t } = useI18n();

  return (
    <Card
      className={`flex flex-col gap-2 p-4 hover:border-recommendation/45 ${isSelected ? "border-primary/60" : ""}`}
      interactive
    >
      <div className="flex flex-wrap items-center gap-2">
        <Badge tone="muted">{t(`essays.type.${essay.essay_type}` as TranslationKey)}</Badge>
        <Badge tone={STATUS_TONE[essay.status]}>{t(`essays.status.${essay.status}` as TranslationKey)}</Badge>
        <Badge tone={VERIFICATION_TONE[essay.prompt_verification_status]}>
          {t(`essays.verification.${essay.prompt_verification_status}` as TranslationKey)}
        </Badge>
        {essay.priority !== "low" ? (
          <Badge tone={PRIORITY_TONE[essay.priority]}>
            {t(`essays.priority.${essay.priority}` as TranslationKey)}
          </Badge>
        ) : null}
      </div>
      <h3 className="flex items-center gap-2 text-base font-semibold">
        <IconChip icon={FileText} size="sm" tone="recommendation" />
        {essay.title}
      </h3>
      {essay.university_name ? (
        <p className="text-xs text-muted-foreground">{essay.university_name}</p>
      ) : null}
      {essay.application_round ? (
        <p className="text-xs text-muted-foreground">
          {t("essays.card.applicationRound", { round: essay.application_round })}
        </p>
      ) : null}
      <p className="text-xs text-muted-foreground">
        {essay.word_limit
          ? t("essays.card.wordCountWithLimit", {
              count: essay.word_count,
              limit: essay.word_limit
            })
          : t("essays.card.wordCount", { count: essay.word_count })}
      </p>
      {essay.last_reviewed_at ? (
        <p className="text-xs text-muted-foreground">
          {t("essays.card.lastReviewed", { date: formatDate(essay.last_reviewed_at, locale) })}
        </p>
      ) : null}
      {essay.due_date ? (
        <p className="text-xs text-muted-foreground">
          {t("essays.card.dueDate", { date: formatDate(essay.due_date, locale) })}
        </p>
      ) : null}
      {essay.source_url ? (
        <a
          className="inline-flex items-center gap-1 text-xs font-semibold text-primary hover:text-primary-hover"
          href={essay.source_url}
          rel="noreferrer"
          target="_blank"
        >
          {t("essays.card.source")}
          <ExternalLink aria-hidden className="size-3" />
        </a>
      ) : null}
      <Button
        className="mt-2"
        onClick={() => onSelect(essay)}
        size="sm"
        type="button"
        variant={isSelected ? "secondary" : "primary"}
      >
        {t("essays.card.open")}
      </Button>
    </Card>
  );
}
