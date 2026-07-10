"use client";

import { useCallback, useEffect, useState } from "react";

import type {
  OrganizerModerationRow,
  OrganizerModerationStatus
} from "@/entities/admin-moderation";
import { ORGANIZER_MODERATION_STATUSES } from "@/entities/admin-moderation";
import { getAdminOrganizersRequest, updateOrganizerModerationRequest } from "@/features/admin-moderation";
import { useI18n, type TranslationKey } from "@/shared/i18n";
import { formatDateTime } from "@/shared/lib/date-time";
import { Button } from "@/shared/ui/button";
import { Card } from "@/shared/ui/card";
import { fieldClassName } from "@/shared/ui/field";
import { SectionTabs } from "@/shared/ui/section-tabs";

const STATUS_STYLES: Record<OrganizerModerationStatus, string> = {
  pending: "border-muted-foreground/30 bg-surface text-muted-foreground",
  approved: "border-success/35 bg-success/10 text-success",
  rejected: "border-danger/35 bg-danger/10 text-danger",
  suspended: "border-danger/35 bg-danger/10 text-danger"
};

function badgeClass(base: string) {
  return `inline-flex items-center rounded-sm border px-2 py-0.5 text-[0.65rem] font-semibold uppercase tracking-wide ${base}`;
}

export function AdminOrganizersScreen() {
  const { locale, t } = useI18n();
  const [organizers, setOrganizers] = useState<OrganizerModerationRow[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [hasError, setHasError] = useState(false);
  const [savingId, setSavingId] = useState<number | null>(null);
  const [expandedId, setExpandedId] = useState<number | null>(null);
  const [reasonDraft, setReasonDraft] = useState("");

  const loadOrganizers = useCallback(async () => {
    setIsLoading(true);
    setHasError(false);
    try {
      setOrganizers(await getAdminOrganizersRequest());
    } catch {
      setHasError(true);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadOrganizers();
  }, [loadOrganizers]);

  function toggleExpanded(row: OrganizerModerationRow) {
    if (expandedId === row.id) {
      setExpandedId(null);
      return;
    }
    setExpandedId(row.id);
    setReasonDraft(row.moderation_reason);
  }

  async function updateStatus(row: OrganizerModerationRow, status: OrganizerModerationStatus) {
    setSavingId(row.id);
    try {
      const updated = await updateOrganizerModerationRequest(row.id, {
        status,
        reason: reasonDraft.trim()
      });
      setOrganizers((current) => current.map((item) => (item.id === updated.id ? updated : item)));
    } finally {
      setSavingId(null);
    }
  }

  return (
    <div className="space-y-6">
      <section className="rounded-sm border bg-card p-6 shadow-card sm:p-9">
        <p className="text-xs font-bold uppercase tracking-[0.18em] text-primary-hover">
          {t("adminOrganizers.eyebrow")}
        </p>
        <h1 className="mt-2 text-3xl font-semibold sm:text-4xl">{t("adminOrganizers.title")}</h1>
        <p className="mt-3 max-w-2xl text-sm leading-6 text-muted-foreground">
          {t("adminOrganizers.description")}
        </p>
      </section>

      <SectionTabs
        ariaLabel={t("adminModeration.tabs.ariaLabel")}
        items={[
          { href: "/admin/moderation", label: t("adminModeration.tabs.universities") },
          { href: "/admin/reports", label: t("adminModeration.tabs.reports") },
          { href: "/admin/organizers", label: t("adminModeration.tabs.organizers") }
        ]}
      />

      {isLoading ? (
        <Card>
          <p className="text-sm text-muted-foreground">{t("adminOrganizers.states.loading")}</p>
        </Card>
      ) : hasError ? (
        <Card>
          <p className="text-sm text-danger" role="alert">
            {t("adminOrganizers.states.loadError")}
          </p>
          <Button className="mt-4" onClick={() => void loadOrganizers()} type="button">
            {t("essays.actions.retry")}
          </Button>
        </Card>
      ) : organizers.length === 0 ? (
        <Card>
          <p className="text-sm text-muted-foreground">{t("adminOrganizers.states.empty")}</p>
        </Card>
      ) : (
        <div className="space-y-3">
          {organizers.map((row) => (
            <Card key={row.id}>
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div className="min-w-0 flex-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className={badgeClass(STATUS_STYLES[row.moderation_status])}>
                      {t(`adminOrganizers.status.${row.moderation_status}` as TranslationKey)}
                    </span>
                    <span className="text-xs text-muted-foreground">
                      {t("adminOrganizers.eventCount", { count: row.event_count })}
                    </span>
                  </div>
                  <p className="mt-2 font-semibold">{row.email}</p>
                  {row.moderation_reason ? (
                    <p className="mt-1 text-sm text-muted-foreground">{row.moderation_reason}</p>
                  ) : null}
                  {row.reviewed_at ? (
                    <p className="mt-1 text-xs text-muted-foreground">
                      {t("adminOrganizers.reviewedAt", {
                        date: formatDateTime(row.reviewed_at, locale)
                      })}
                    </p>
                  ) : null}
                </div>
                <Button onClick={() => toggleExpanded(row)} size="sm" type="button" variant="ghost">
                  {expandedId === row.id
                    ? t("adminModeration.actions.collapse")
                    : t("adminOrganizers.actions.review")}
                </Button>
              </div>

              {expandedId === row.id ? (
                <div className="mt-4 space-y-3 border-t pt-4">
                  <label className="block">
                    <span className="text-xs font-semibold">{t("adminOrganizers.form.reason")}</span>
                    <textarea
                      className={`${fieldClassName} min-h-16 resize-y py-2 leading-5`}
                      onChange={(event) => setReasonDraft(event.target.value)}
                      value={reasonDraft}
                    />
                  </label>
                  <div className="flex flex-wrap justify-end gap-2">
                    {ORGANIZER_MODERATION_STATUSES.map((option) => (
                      <Button
                        disabled={savingId === row.id}
                        key={option}
                        onClick={() => void updateStatus(row, option)}
                        size="sm"
                        type="button"
                        variant={option === row.moderation_status ? "primary" : "ghost"}
                      >
                        {t(`adminOrganizers.status.${option}` as TranslationKey)}
                      </Button>
                    ))}
                  </div>
                </div>
              ) : null}
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
