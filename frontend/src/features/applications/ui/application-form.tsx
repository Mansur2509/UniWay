"use client";

import { useState } from "react";

import type { ApplicationPriority, ApplicationRound } from "@/entities/application";
import type { SavedUniversity, SavedUniversityLite } from "@/entities/university";
import { useI18n, type TranslationKey } from "@/shared/i18n";
import { useUnsavedChangesGuard } from "@/shared/lib/use-unsaved-changes-guard";
import { Button } from "@/shared/ui/button";
import { Card } from "@/shared/ui/card";
import { fieldClassName } from "@/shared/ui/field";
import { UnsavedChangesDialog } from "@/shared/ui/unsaved-changes-dialog";

const ROUNDS: ApplicationRound[] = [
  "early_decision",
  "early_action",
  "restrictive_early_action",
  "regular_decision",
  "rolling",
  "scholarship",
  "other"
];

export type ApplicationFormValues = {
  university: number | null;
  target_program: number | null;
  application_round: ApplicationRound;
  target_intake_year: number | null;
  personal_estimated_deadline: string;
  priority: ApplicationPriority;
  notes: string;
};

export function ApplicationForm({
  shortlist,
  onSubmit,
  onCancel,
  isShortlistLoading = false,
  shortlistLoadError = false,
  isSubmitting
}: {
  shortlist: Array<SavedUniversity | SavedUniversityLite>;
  onSubmit: (values: ApplicationFormValues) => Promise<void>;
  onCancel: () => void;
  isShortlistLoading?: boolean;
  shortlistLoadError?: boolean;
  isSubmitting?: boolean;
}) {
  const { t } = useI18n();
  const [initialValues] = useState<ApplicationFormValues>({
    university: shortlist[0]?.university.id ?? null,
    target_program: null,
    application_round: "regular_decision",
    target_intake_year: null,
    personal_estimated_deadline: "",
    priority: "medium",
    notes: ""
  });
  const [values, setValues] = useState<ApplicationFormValues>(initialValues);
  const [error, setError] = useState<string | null>(null);
  const hasUnsavedChanges = JSON.stringify(values) !== JSON.stringify(initialValues);
  const unsavedGuard = useUnsavedChangesGuard({
    browserMessage: t("common.unsaved.browserMessage"),
    isDirty: hasUnsavedChanges
  });
  const selectedSaved = shortlist.find(
    (saved) => saved.university.id === values.university
  );
  const programOptions =
    selectedSaved && "programs" in selectedSaved.university
      ? selectedSaved.university.programs.filter(
          (program) => !program.degree_level || program.degree_level.toLowerCase().includes("under")
        )
      : [];
  const intakeYears = Array.from({ length: 9 }, (_, index) => new Date().getFullYear() + index);

  async function submitValues() {
    setError(null);
    if (!values.university) {
      setError(t("applications.form.error.universityRequired"));
      return false;
    }
    try {
      await onSubmit(values);
      return true;
    } catch {
      setError(t("applications.form.duplicateError"));
      return false;
    }
  }

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    await submitValues();
  }

  return (
    <Card className="p-4">
      <form className="space-y-3" onSubmit={(event) => void handleSubmit(event)}>
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h2 className="text-base font-semibold">{t("applications.form.createTitle")}</h2>
            <p className="mt-1 text-xs text-muted-foreground">
              {t("applications.form.closeHelp")}
            </p>
          </div>
          <Button
            disabled={isSubmitting}
            onClick={() => unsavedGuard.requestLeave(onCancel)}
            size="sm"
            type="button"
            variant="ghost"
          >
            {t("common.actions.close")}
          </Button>
        </div>
        <label className="block">
          <span className="text-xs font-semibold">
            {t("applications.form.university")}
            <span aria-hidden className="ml-0.5 text-primary-hover">
              *
            </span>
          </span>
          <select
            className={fieldClassName}
            onChange={(event) =>
              setValues((current) => ({
                ...current,
                university: event.target.value ? Number(event.target.value) : null,
                target_program: null
              }))
            }
            value={values.university ?? ""}
          >
            <option value="">{t("applications.form.selectUniversity")}</option>
            {shortlist.map((saved) => (
              <option key={saved.university.id} value={saved.university.id}>
                {saved.university.name}
              </option>
            ))}
          </select>
          {shortlistLoadError ? (
            <p className="mt-1 text-xs text-warning" role="alert">
              {t("applications.form.shortlistLoadError")}
            </p>
          ) : isShortlistLoading ? (
            <p className="mt-1 text-xs text-muted-foreground">
              {t("applications.form.shortlistLoading")}
            </p>
          ) : null}
        </label>
        <label className="block">
          <span className="text-xs font-semibold">{t("applications.form.program")}</span>
          <select
            className={fieldClassName}
            disabled={!values.university || programOptions.length === 0}
            onChange={(event) =>
              setValues((current) => ({
                ...current,
                target_program: event.target.value ? Number(event.target.value) : null
              }))
            }
            value={values.target_program ?? ""}
          >
            <option value="">
              {programOptions.length > 0
                ? t("applications.form.selectProgram")
                : t("applications.form.programUnavailable")}
            </option>
            {programOptions.map((program) => (
              <option key={program.id} value={program.id}>
                {program.display_name || program.name}
              </option>
            ))}
          </select>
        </label>
        <div className="grid gap-3 sm:grid-cols-2">
          <label className="block">
            <span className="text-xs font-semibold">{t("applications.form.round")}</span>
            <select
              className={fieldClassName}
              onChange={(event) =>
                setValues((current) => ({
                  ...current,
                  application_round: event.target.value as ApplicationRound
                }))
              }
              value={values.application_round}
            >
              {ROUNDS.map((round) => (
                <option key={round} value={round}>
                  {t(`applications.round.${round}` as TranslationKey)}
                </option>
              ))}
            </select>
          </label>
          <label className="block">
            <span className="text-xs font-semibold">{t("applications.form.intakeYear")}</span>
            <select
              className={fieldClassName}
              onChange={(event) =>
                setValues((current) => ({
                  ...current,
                  target_intake_year: event.target.value ? Number(event.target.value) : null
                }))
              }
              value={values.target_intake_year ?? ""}
            >
              <option value="">{t("applications.form.selectIntakeYear")}</option>
              {intakeYears.map((year) => (
                <option key={year} value={year}>
                  {year}
                </option>
              ))}
            </select>
          </label>
        </div>
        <div className="grid gap-3 sm:grid-cols-2">
          <label className="block">
            <span className="text-xs font-semibold">{t("applications.form.priority")}</span>
            <select
              className={fieldClassName}
              onChange={(event) =>
                setValues((current) => ({
                  ...current,
                  priority: event.target.value as ApplicationPriority
                }))
              }
              value={values.priority}
            >
              {(["low", "medium", "high", "dream"] as const).map((priority) => (
                <option key={priority} value={priority}>
                  {t(`applications.priority.${priority}` as TranslationKey)}
                </option>
              ))}
            </select>
          </label>
          <label className="block">
            <span className="text-xs font-semibold">
              {t("applications.form.personalDeadline")}
            </span>
            <input
              className={fieldClassName}
              onChange={(event) =>
                setValues((current) => ({
                  ...current,
                  personal_estimated_deadline: event.target.value
                }))
              }
              type="date"
              value={values.personal_estimated_deadline}
            />
            <span className="mt-1 block text-xs text-muted-foreground">
              {t("applications.form.personalDeadlineHelp")}
            </span>
          </label>
        </div>
        <label className="block">
          <span className="text-xs font-semibold">{t("applications.form.notes")}</span>
          <textarea
            className={fieldClassName}
            maxLength={3000}
            onChange={(event) =>
              setValues((current) => ({ ...current, notes: event.target.value }))
            }
            rows={3}
            value={values.notes}
          />
        </label>
        {error ? (
          <p className="text-sm text-danger" role="alert">
            {error}
          </p>
        ) : null}
        <div className="flex gap-2">
          <Button disabled={isSubmitting} size="sm" type="submit">
            {t("applications.form.create")}
          </Button>
          <Button
            disabled={isSubmitting}
            onClick={() => unsavedGuard.requestLeave(onCancel)}
            size="sm"
            type="button"
            variant="ghost"
          >
            {t("common.actions.cancel")}
          </Button>
        </div>
      </form>
      <UnsavedChangesDialog
        description={t("common.unsaved.description")}
        isSaving={isSubmitting}
        leaveWithoutSavingLabel={t("common.unsaved.leaveWithoutSaving")}
        onLeaveWithoutSaving={unsavedGuard.leaveWithoutSaving}
        onSaveAndLeave={submitValues}
        onStay={unsavedGuard.stay}
        open={unsavedGuard.isPromptOpen}
        saveAndLeaveLabel={t("common.unsaved.saveAndLeave")}
        stayLabel={t("common.unsaved.stay")}
        title={t("common.unsaved.title")}
      />
    </Card>
  );
}
