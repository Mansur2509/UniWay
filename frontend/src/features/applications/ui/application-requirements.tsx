"use client";

import { useEffect, useState } from "react";

import type { ApplicationRequirement, RequirementStatus, RequirementType } from "@/entities/application";
import {
  createApplicationRequirementRequest,
  generateApplicationRequirementsRequest,
  getApplicationRequirementsRequest,
  updateApplicationRequirementRequest
} from "@/features/applications";
import { useI18n, type TranslationKey } from "@/shared/i18n";
import { Button } from "@/shared/ui/button";
import { fieldClassName } from "@/shared/ui/field";

const REQUIREMENT_TYPES: RequirementType[] = [
  "transcript",
  "test_scores",
  "english_proof",
  "essay",
  "supplement",
  "recommendation",
  "portfolio",
  "financial_aid",
  "passport",
  "application_fee",
  "interview",
  "other"
];

const REQUIREMENT_STATUSES: RequirementStatus[] = [
  "missing",
  "in_progress",
  "completed",
  "waived",
  "not_required"
];

export function ApplicationRequirementsPanel({ applicationId }: { applicationId: number }) {
  const { t } = useI18n();
  const [requirements, setRequirements] = useState<ApplicationRequirement[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [hasError, setHasError] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [newTitle, setNewTitle] = useState("");
  const [newType, setNewType] = useState<RequirementType>("other");

  const load = () => {
    setIsLoading(true);
    setHasError(false);
    getApplicationRequirementsRequest(applicationId)
      .then(setRequirements)
      .catch(() => setHasError(true))
      .finally(() => setIsLoading(false));
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [applicationId]);

  const handleGenerate = async () => {
    setIsGenerating(true);
    try {
      const generated = await generateApplicationRequirementsRequest(applicationId);
      setRequirements(generated);
    } catch {
      setHasError(true);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleStatusChange = async (requirementId: number, status: RequirementStatus) => {
    const updated = await updateApplicationRequirementRequest(requirementId, { status });
    setRequirements((current) => current.map((item) => (item.id === updated.id ? updated : item)));
  };

  const handleAdd = async () => {
    if (!newTitle.trim()) return;
    const created = await createApplicationRequirementRequest(applicationId, {
      requirement_type: newType,
      title: newTitle.trim()
    });
    setRequirements((current) => [...current, created]);
    setNewTitle("");
  };

  if (isLoading) {
    return <p className="text-sm text-muted-foreground">{t("applications.requirements.loading")}</p>;
  }
  if (hasError) {
    return <p className="text-sm text-danger">{t("applications.requirements.error")}</p>;
  }

  return (
    <div>
      {requirements.length === 0 ? (
        <div className="rounded-sm border bg-surface p-3">
          <p className="text-sm text-muted-foreground">{t("applications.requirements.empty")}</p>
          <Button
            className="mt-2"
            disabled={isGenerating}
            onClick={() => void handleGenerate()}
            size="sm"
            type="button"
          >
            {isGenerating
              ? t("applications.requirements.generating")
              : t("applications.requirements.generate")}
          </Button>
        </div>
      ) : (
        <ul className="space-y-2">
          {requirements.map((requirement) => (
            <li
              className="flex flex-wrap items-center justify-between gap-3 rounded-sm border bg-surface p-3 text-sm"
              key={requirement.id}
            >
              <div className="min-w-0">
                <div className="flex flex-wrap items-center gap-1.5">
                  <span className="rounded-sm border bg-elevated px-2 py-0.5 text-[0.65rem] font-semibold uppercase tracking-wide text-muted-foreground">
                    {t(`applications.requirementType.${requirement.requirement_type}` as TranslationKey)}
                  </span>
                  {!requirement.is_required ? (
                    <span className="rounded-sm border bg-elevated px-2 py-0.5 text-[0.65rem] font-semibold uppercase tracking-wide text-muted-foreground">
                      {t("applications.requirements.optional")}
                    </span>
                  ) : null}
                </div>
                <p className="mt-1 font-semibold">{requirement.title}</p>
                {requirement.description ? (
                  <p className="text-xs text-muted-foreground">{requirement.description}</p>
                ) : null}
              </div>
              <select
                className={fieldClassName}
                onChange={(event) =>
                  void handleStatusChange(requirement.id, event.target.value as RequirementStatus)
                }
                value={requirement.status}
              >
                {REQUIREMENT_STATUSES.map((status) => (
                  <option key={status} value={status}>
                    {t(`applications.requirementStatus.${status}` as TranslationKey)}
                  </option>
                ))}
              </select>
            </li>
          ))}
        </ul>
      )}

      <div className="mt-3 flex flex-wrap items-end gap-2">
        <label className="block">
          <span className="text-xs font-semibold">{t("applications.requirements.newType")}</span>
          <select
            className={fieldClassName}
            onChange={(event) => setNewType(event.target.value as RequirementType)}
            value={newType}
          >
            {REQUIREMENT_TYPES.map((type) => (
              <option key={type} value={type}>
                {t(`applications.requirementType.${type}` as TranslationKey)}
              </option>
            ))}
          </select>
        </label>
        <label className="block flex-1">
          <span className="text-xs font-semibold">{t("applications.requirements.newTitle")}</span>
          <input
            className={fieldClassName}
            onChange={(event) => setNewTitle(event.target.value)}
            type="text"
            value={newTitle}
          />
        </label>
        <Button onClick={() => void handleAdd()} size="sm" type="button">
          {t("applications.requirements.add")}
        </Button>
      </div>
    </div>
  );
}
