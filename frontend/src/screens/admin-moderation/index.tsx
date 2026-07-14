"use client";

import { useCallback, useEffect, useState } from "react";
import { Flag, ShieldCheck, UserCog } from "lucide-react";

import type {
  ModerationIssueType,
  ModerationStatus,
  UniversityModerationRecord
} from "@/entities/admin-moderation";
import { MODERATION_ISSUE_TYPES, MODERATION_STATUSES } from "@/entities/admin-moderation";
import {
  getUniversityReviewQueueRequest,
  updateUniversityModerationRequest
} from "@/features/admin-moderation";
import { useI18n, type TranslationKey } from "@/shared/i18n";
import { formatDateTime } from "@/shared/lib/date-time";
import { Button } from "@/shared/ui/button";
import { Card } from "@/shared/ui/card";
import { fieldClassName } from "@/shared/ui/field";
import { DEFAULT_PAGE_SIZE, PaginationControls } from "@/shared/ui/pagination";
import { RetryNotice } from "@/shared/ui/retry-notice";
import { SectionTabs } from "@/shared/ui/section-tabs";
import { SkeletonRows } from "@/shared/ui/skeleton";

const STATUS_STYLES: Record<ModerationStatus, string> = {
  pending_review: "border-warning/35 bg-warning/10 text-warning",
  needs_update: "border-warning/35 bg-warning/10 text-warning",
  verified: "border-success/35 bg-success/10 text-success",
  rejected: "border-danger/35 bg-danger/10 text-danger",
  archived: "border-muted-foreground/30 bg-surface text-muted-foreground"
};

function badgeClass(base: string) {
  return `inline-flex items-center rounded-sm border px-2 py-0.5 text-[0.65rem] font-semibold uppercase tracking-wide ${base}`;
}

export function AdminModerationScreen() {
  const { locale, t } = useI18n();
  const [records, setRecords] = useState<UniversityModerationRecord[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [isLoading, setIsLoading] = useState(true);
  const [hasError, setHasError] = useState(false);
  const [expandedId, setExpandedId] = useState<number | null>(null);
  const [savingId, setSavingId] = useState<number | null>(null);
  const [actionErrorId, setActionErrorId] = useState<number | null>(null);
  const [draftStatus, setDraftStatus] = useState<ModerationStatus>("verified");
  const [draftIssueType, setDraftIssueType] = useState<ModerationIssueType>("admin_note");
  const [draftDescription, setDraftDescription] = useState("");

  const loadQueue = useCallback(async () => {
    setIsLoading(true);
    setHasError(false);
    try {
      const response = await getUniversityReviewQueueRequest({
        page: currentPage,
        page_size: DEFAULT_PAGE_SIZE
      });
      setRecords(response.results);
      setTotalCount(response.count);
    } catch {
      setHasError(true);
    } finally {
      setIsLoading(false);
    }
  }, [currentPage]);

  useEffect(() => {
    void loadQueue();
  }, [loadQueue]);

  const totalPages = Math.max(1, Math.ceil(totalCount / DEFAULT_PAGE_SIZE));

  function toggleExpanded(record: UniversityModerationRecord) {
    if (expandedId === record.university) {
      setExpandedId(null);
      return;
    }
    setExpandedId(record.university);
    setDraftStatus("verified");
    setDraftIssueType("admin_note");
    setDraftDescription("");
  }

  async function submitAction(record: UniversityModerationRecord) {
    setSavingId(record.university);
    setActionErrorId(null);
    try {
      await updateUniversityModerationRequest(record.university, {
        status: draftStatus,
        issue_type: draftIssueType,
        description: draftDescription.trim()
      });
      setExpandedId(null);
      await loadQueue();
    } catch {
      setActionErrorId(record.university);
    } finally {
      setSavingId(null);
    }
  }

  return (
    <div className="space-y-6">
      <section className="rounded-sm border bg-card p-6 shadow-card sm:p-9">
        <p className="text-xs font-bold uppercase tracking-[0.18em] text-primary-hover">
          {t("adminModeration.eyebrow")}
        </p>
        <h1 className="mt-2 text-3xl font-semibold sm:text-4xl">{t("adminModeration.title")}</h1>
        <p className="mt-3 max-w-2xl text-sm leading-6 text-muted-foreground">
          {t("adminModeration.description")}
        </p>
      </section>

      <SectionTabs
        ariaLabel={t("adminModeration.tabs.ariaLabel")}
        items={[
          {
            href: "/admin/moderation",
            icon: ShieldCheck,
            label: t("adminModeration.tabs.universities")
          },
          { href: "/admin/reports", icon: Flag, label: t("adminModeration.tabs.reports") },
          {
            href: "/admin/organizers",
            icon: UserCog,
            label: t("adminModeration.tabs.organizers")
          }
        ]}
      />

      {isLoading ? (
        <div className="space-y-3">
          <SkeletonRows count={5} />
        </div>
      ) : hasError ? (
        <RetryNotice message={t("adminModeration.states.loadError")} onRetry={() => void loadQueue()} />
      ) : records.length === 0 ? (
        <Card>
          <p className="text-sm text-muted-foreground">{t("adminModeration.states.empty")}</p>
        </Card>
      ) : (
        <div className="space-y-3">
          {records.map((record) => (
            <Card key={record.university}>
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div className="min-w-0 flex-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className={badgeClass(STATUS_STYLES[record.status])}>
                      {t(`adminModeration.status.${record.status}` as TranslationKey)}
                    </span>
                    <span className="text-xs text-muted-foreground">
                      {t(`adminModeration.issueType.${record.issue_type}` as TranslationKey)}
                    </span>
                  </div>
                  <p className="mt-2 font-semibold">{record.university_name}</p>
                  {record.description ? (
                    <p className="mt-1 text-sm text-muted-foreground">{record.description}</p>
                  ) : null}
                  <p className="mt-1 text-xs text-muted-foreground">
                    {formatDateTime(record.created_at, locale)}
                  </p>
                </div>
                <Button
                  onClick={() => toggleExpanded(record)}
                  size="sm"
                  type="button"
                  variant="ghost"
                >
                  {expandedId === record.university
                    ? t("adminModeration.actions.collapse")
                    : t("adminModeration.actions.review")}
                </Button>
              </div>

              {expandedId === record.university ? (
                <div className="mt-4 space-y-3 border-t pt-4">
                  <div className="grid gap-3 sm:grid-cols-2">
                    <label className="block">
                      <span className="text-xs font-semibold">
                        {t("adminModeration.form.status")}
                      </span>
                      <select
                        className={fieldClassName}
                        onChange={(event) =>
                          setDraftStatus(event.target.value as ModerationStatus)
                        }
                        value={draftStatus}
                      >
                        {MODERATION_STATUSES.map((option) => (
                          <option key={option} value={option}>
                            {t(`adminModeration.status.${option}` as TranslationKey)}
                          </option>
                        ))}
                      </select>
                    </label>
                    <label className="block">
                      <span className="text-xs font-semibold">
                        {t("adminModeration.form.issueType")}
                      </span>
                      <select
                        className={fieldClassName}
                        onChange={(event) =>
                          setDraftIssueType(event.target.value as ModerationIssueType)
                        }
                        value={draftIssueType}
                      >
                        {MODERATION_ISSUE_TYPES.map((option) => (
                          <option key={option} value={option}>
                            {t(`adminModeration.issueType.${option}` as TranslationKey)}
                          </option>
                        ))}
                      </select>
                    </label>
                  </div>
                  <label className="block">
                    <span className="text-xs font-semibold">
                      {t("adminModeration.form.description")}
                    </span>
                    <textarea
                      className={`${fieldClassName} min-h-20 resize-y py-2 leading-5`}
                      onChange={(event) => setDraftDescription(event.target.value)}
                      value={draftDescription}
                    />
                  </label>
                  {actionErrorId === record.university ? (
                    <p className="text-xs text-danger" role="alert">
                      {t("adminModeration.states.actionError")}
                    </p>
                  ) : null}
                  <div className="flex justify-end gap-2">
                    <Button
                      disabled={savingId === record.university}
                      onClick={() => void submitAction(record)}
                      size="sm"
                      type="button"
                    >
                      {savingId === record.university
                        ? t("adminModeration.actions.saving")
                        : t("adminModeration.actions.submit")}
                    </Button>
                  </div>
                </div>
              ) : null}
            </Card>
          ))}
          {totalPages > 1 ? (
            <PaginationControls
              currentPage={currentPage}
              itemsOnPage={records.length}
              onPageChange={setCurrentPage}
              pageSize={DEFAULT_PAGE_SIZE}
              totalCount={totalCount}
              totalPages={totalPages}
            />
          ) : null}
        </div>
      )}
    </div>
  );
}
