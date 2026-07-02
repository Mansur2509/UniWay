"use client";

import { ExternalLink, FileText } from "lucide-react";

import type { EssayWorkspace } from "@/entities/essay";
import { useI18n, type TranslationKey } from "@/shared/i18n";
import { formatDate } from "@/shared/lib/date-time";
import { Button } from "@/shared/ui/button";
import { Card } from "@/shared/ui/card";

const STATUS_STYLES: Record<string, string> = {
  suggested: "border-primary/35 bg-primary/10 text-primary",
  planned: "border-accent/35 bg-accent/10 text-accent",
  not_started: "border-muted-foreground/30 bg-surface text-muted-foreground",
  drafting: "border-accent/35 bg-accent/10 text-accent",
  needs_revision: "border-warning/35 bg-warning/10 text-warning",
  reviewed: "border-accent/35 bg-accent/10 text-accent",
  ready: "border-success/35 bg-success/10 text-success",
  submitted: "border-navy/35 bg-navy/10 text-navy",
  skipped: "border-muted-foreground/30 bg-surface text-muted-foreground"
};

const VERIFICATION_STYLES: Record<string, string> = {
  verified: "border-success/35 bg-success/10 text-success",
  needs_verification: "border-warning/35 bg-warning/10 text-warning",
  missing: "border-muted-foreground/30 bg-surface text-muted-foreground"
};

const PRIORITY_STYLES: Record<string, string> = {
  low: "border-muted-foreground/30 bg-surface text-muted-foreground",
  medium: "border-accent/35 bg-accent/10 text-accent",
  high: "border-warning/35 bg-warning/10 text-warning",
  urgent: "border-danger/35 bg-danger/10 text-danger"
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
      className={`flex flex-col gap-2 p-4 ${isSelected ? "border-primary/60" : ""}`}
    >
      <div className="flex flex-wrap items-center gap-2">
        <span className="rounded-sm border bg-surface px-2 py-0.5 text-[0.65rem] font-semibold uppercase tracking-wide text-muted-foreground">
          {t(`essays.type.${essay.essay_type}` as TranslationKey)}
        </span>
        <span
          className={`rounded-sm border px-2 py-0.5 text-[0.65rem] font-semibold uppercase tracking-wide ${STATUS_STYLES[essay.status]}`}
        >
          {t(`essays.status.${essay.status}` as TranslationKey)}
        </span>
        <span
          className={`rounded-sm border px-2 py-0.5 text-[0.65rem] font-semibold uppercase tracking-wide ${VERIFICATION_STYLES[essay.prompt_verification_status]}`}
        >
          {t(`essays.verification.${essay.prompt_verification_status}` as TranslationKey)}
        </span>
        {essay.priority !== "low" ? (
          <span
            className={`rounded-sm border px-2 py-0.5 text-[0.65rem] font-semibold uppercase tracking-wide ${PRIORITY_STYLES[essay.priority]}`}
          >
            {t(`essays.priority.${essay.priority}` as TranslationKey)}
          </span>
        ) : null}
      </div>
      <h3 className="flex items-center gap-2 text-base font-semibold">
        <FileText aria-hidden className="size-4 shrink-0 text-accent" />
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
