"use client";

import { GraduationCap, Plus, Sparkles, Target, Waypoints } from "lucide-react";
import { useCallback, useEffect, useMemo, useState } from "react";

import {
  type ApplicationTrackerItem,
  type ApplicationTrackerItemInput,
  ProspectiveTargetCard
} from "@/entities/application";
import {
  createApplicationRequest,
  deleteApplicationRequest,
  getApplicationsRequest,
  restoreApplicationRequest,
  updateApplicationRequest
} from "@/features/applications";
import { ApplicationForm, type ApplicationFormValues } from "@/features/applications/ui/application-form";
import { getShortlistRequest } from "@/features/universities";
import type { SavedUniversity, SavedUniversityLite } from "@/entities/university";
import { useI18n } from "@/shared/i18n";
import { AppIcon } from "@/shared/ui/icon";
import { Button } from "@/shared/ui/button";
import { Card } from "@/shared/ui/card";
import { LoadingNotice } from "@/shared/ui/loading-notice";
import { RetryNotice } from "@/shared/ui/retry-notice";
import { SectionTabs } from "@/shared/ui/section-tabs";

const PROSPECTIVE_STATUSES = new Set(["researching", "shortlisted"]);
const START_APPLICATION_STATUS = "preparing";
const PAGE_SIZE = 100;

export function ProspectiveUniversitiesScreen() {
  const { t } = useI18n();
  const [items, setItems] = useState<ApplicationTrackerItem[]>([]);
  const [archivedItems, setArchivedItems] = useState<ApplicationTrackerItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [hasError, setHasError] = useState(false);
  const [showArchived, setShowArchived] = useState(false);
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingTarget, setEditingTarget] = useState<ApplicationTrackerItem | null>(null);
  const [actionError, setActionError] = useState(false);
  const [shortlist, setShortlist] = useState<SavedUniversity[]>([]);
  const [shortlistRequested, setShortlistRequested] = useState(false);
  const [isShortlistLoading, setIsShortlistLoading] = useState(false);
  const [shortlistLoadError, setShortlistLoadError] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const loadTargets = useCallback(async () => {
    setIsLoading(true);
    setHasError(false);
    try {
      const [active, archived] = await Promise.all([
        getApplicationsRequest({ page_size: PAGE_SIZE }),
        getApplicationsRequest({ page_size: PAGE_SIZE, include_archived: "true" })
      ]);
      setItems(active.results.filter((item) => PROSPECTIVE_STATUSES.has(item.status)));
      setArchivedItems(
        archived.results.filter(
          (item) => item.archived_at && PROSPECTIVE_STATUSES.has(item.status)
        )
      );
    } catch {
      setHasError(true);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadTargets();
  }, [loadTargets]);

  const loadShortlist = useCallback(async () => {
    if (shortlistRequested && !shortlistLoadError) return;
    setShortlistRequested(true);
    setIsShortlistLoading(true);
    setShortlistLoadError(false);
    try {
      const response = await getShortlistRequest({ lite: false });
      setShortlist(response.results);
    } catch {
      setShortlistLoadError(true);
    } finally {
      setIsShortlistLoading(false);
    }
  }, [shortlistLoadError, shortlistRequested]);

  useEffect(() => {
    if (isFormOpen) {
      void loadShortlist();
    }
  }, [isFormOpen, loadShortlist]);

  const shortlistForForm = useMemo<Array<SavedUniversity | SavedUniversityLite>>(() => {
    if (!editingTarget) return shortlist;
    const alreadyListed = shortlist.some(
      (saved) => saved.university.id === editingTarget.university
    );
    if (alreadyListed) return shortlist;
    const fallbackEntry: SavedUniversityLite = {
      id: editingTarget.id,
      university: {
        id: editingTarget.university,
        name: editingTarget.university_name,
        slug: editingTarget.university_slug,
        country: "",
        city: ""
      },
      created_at: editingTarget.created_at
    };
    return [fallbackEntry, ...shortlist];
  }, [editingTarget, shortlist]);

  const editInitialValues = useMemo<Partial<ApplicationFormValues> | undefined>(() => {
    if (!editingTarget) return undefined;
    return {
      university: editingTarget.university,
      target_program: editingTarget.target_program,
      application_round: editingTarget.application_round,
      target_intake_year: editingTarget.target_intake_year,
      personal_estimated_deadline: editingTarget.personal_estimated_deadline ?? "",
      priority: editingTarget.priority,
      notes: editingTarget.notes
    };
  }, [editingTarget]);

  function closeForm() {
    setIsFormOpen(false);
    setEditingTarget(null);
  }

  async function handleSubmit(values: ApplicationFormValues) {
    setIsSubmitting(true);
    setActionError(false);
    try {
      const payload: ApplicationTrackerItemInput = {
        university: values.university ?? undefined,
        target_program: values.target_program,
        application_round: values.application_round,
        target_intake_year: values.target_intake_year,
        personal_estimated_deadline: values.personal_estimated_deadline || null,
        priority: values.priority,
        notes: values.notes
      };
      if (editingTarget) {
        const updated = await updateApplicationRequest(editingTarget.id, payload);
        setItems((current) =>
          current.map((item) => (item.id === updated.id ? updated : item))
        );
      } else {
        await createApplicationRequest(payload);
        await loadTargets();
      }
      closeForm();
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleArchive(target: ApplicationTrackerItem) {
    setActionError(false);
    try {
      await deleteApplicationRequest(target.id);
      setItems((current) => current.filter((item) => item.id !== target.id));
      setArchivedItems((current) => [
        { ...target, archived_at: new Date().toISOString() },
        ...current
      ]);
    } catch {
      setActionError(true);
    }
  }

  async function handleRestore(target: ApplicationTrackerItem) {
    setActionError(false);
    try {
      const restored = await restoreApplicationRequest(target.id);
      setArchivedItems((current) => current.filter((item) => item.id !== target.id));
      setItems((current) => [restored, ...current]);
    } catch {
      setActionError(true);
    }
  }

  async function handleStartApplication(target: ApplicationTrackerItem) {
    setActionError(false);
    try {
      const updated = await updateApplicationRequest(target.id, {
        status: START_APPLICATION_STATUS
      });
      setItems((current) => current.filter((item) => item.id !== updated.id));
    } catch {
      setActionError(true);
    }
  }

  if (isLoading) {
    return <LoadingNotice message={t("prospective.states.loading")} />;
  }

  if (hasError) {
    return (
      <Card>
        <RetryNotice bare message={t("prospective.states.loadError")} onRetry={() => void loadTargets()} />
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="flex items-center gap-2 text-xs font-bold uppercase tracking-[0.16em] text-primary-hover">
            <AppIcon decorative icon={Target} size="sm" />
            {t("prospective.eyebrow")}
          </p>
          <h1 className="mt-2 text-2xl font-semibold">{t("prospective.title")}</h1>
          <p className="mt-1 max-w-2xl text-sm text-muted-foreground">
            {t("prospective.description")}
          </p>
        </div>
        <Button
          className="gap-2"
          onClick={() => {
            setEditingTarget(null);
            setIsFormOpen(true);
          }}
          size="sm"
          type="button"
        >
          <AppIcon decorative icon={Plus} size="sm" />
          {t("prospective.addTarget")}
        </Button>
      </div>

      <SectionTabs
        ariaLabel={t("universities.tabs.ariaLabel")}
        items={[
          { href: "/universities", icon: GraduationCap, label: t("universities.tabs.browse") },
          {
            href: "/recommendations",
            icon: Sparkles,
            label: t("universities.tabs.recommendations")
          },
          { href: "/strategy", icon: Waypoints, label: t("universities.tabs.strategy") },
          {
            href: "/prospective-universities",
            icon: Target,
            label: t("universities.tabs.prospective")
          }
        ]}
      />

      {actionError ? (
        <p className="text-sm text-danger" role="alert">
          {t("prospective.states.actionError")}
        </p>
      ) : null}

      {isFormOpen ? (
        <ApplicationForm
          initialValues={editInitialValues}
          isShortlistLoading={isShortlistLoading}
          isSubmitting={isSubmitting}
          onCancel={closeForm}
          onSubmit={handleSubmit}
          shortlist={shortlistForForm}
          shortlistLoadError={shortlistLoadError}
          submitLabel={editingTarget ? t("prospective.form.save") : t("prospective.form.create")}
          title={editingTarget ? t("prospective.form.editTitle") : t("prospective.form.createTitle")}
        />
      ) : null}

      {items.length === 0 ? (
        <Card className="p-6 text-center">
          <p className="text-sm text-muted-foreground">{t("prospective.states.empty")}</p>
        </Card>
      ) : (
        <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
          {items.map((target) => (
            <ProspectiveTargetCard
              key={target.id}
              onArchive={() => void handleArchive(target)}
              onEdit={() => {
                setEditingTarget(target);
                setIsFormOpen(true);
              }}
              onStartApplication={() => void handleStartApplication(target)}
              target={target}
            />
          ))}
        </div>
      )}

      {archivedItems.length > 0 ? (
        <div className="space-y-3">
          <Button
            onClick={() => setShowArchived((current) => !current)}
            size="sm"
            type="button"
            variant="ghost"
          >
            {showArchived
              ? t("prospective.archived.hide")
              : t("prospective.archived.show", { count: archivedItems.length })}
          </Button>
          {showArchived ? (
            <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
              {archivedItems.map((target) => (
                <ProspectiveTargetCard
                  isArchived
                  key={target.id}
                  onEdit={() => {
                    setEditingTarget(target);
                    setIsFormOpen(true);
                  }}
                  onRestore={() => void handleRestore(target)}
                  target={target}
                />
              ))}
            </div>
          ) : null}
        </div>
      ) : null}
    </div>
  );
}
