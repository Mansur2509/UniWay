"use client";

import { useEffect, useState } from "react";

import type { ApplicationDocument, ApplicationDocumentStatus, ApplicationDocumentType } from "@/entities/application";
import {
  createApplicationDocumentRequest,
  getApplicationDocumentsRequest,
  updateApplicationDocumentRequest
} from "@/features/applications";
import { useI18n, type TranslationKey } from "@/shared/i18n";
import { Button } from "@/shared/ui/button";
import { fieldClassName } from "@/shared/ui/field";

const DOCUMENT_TYPES: ApplicationDocumentType[] = [
  "transcript",
  "passport",
  "certificate",
  "test_report",
  "portfolio",
  "financial_document",
  "other"
];

const DOCUMENT_STATUSES: ApplicationDocumentStatus[] = ["missing", "uploaded", "verified", "rejected"];

export function ApplicationDocumentsPanel({ applicationId }: { applicationId: number }) {
  const { t } = useI18n();
  const [documents, setDocuments] = useState<ApplicationDocument[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [hasError, setHasError] = useState(false);
  const [actionError, setActionError] = useState(false);
  const [newTitle, setNewTitle] = useState("");
  const [newType, setNewType] = useState<ApplicationDocumentType>("other");

  useEffect(() => {
    setIsLoading(true);
    setHasError(false);
    getApplicationDocumentsRequest(applicationId)
      .then(setDocuments)
      .catch(() => setHasError(true))
      .finally(() => setIsLoading(false));
  }, [applicationId]);

  const handleStatusChange = async (id: number, status: ApplicationDocumentStatus) => {
    setActionError(false);
    try {
      const updated = await updateApplicationDocumentRequest(id, { status });
      setDocuments((current) => current.map((item) => (item.id === updated.id ? updated : item)));
    } catch {
      setActionError(true);
    }
  };

  const handleAdd = async () => {
    if (!newTitle.trim()) return;
    setActionError(false);
    try {
      const created = await createApplicationDocumentRequest(applicationId, {
        document_type: newType,
        title: newTitle.trim()
      });
      setDocuments((current) => [...current, created]);
      setNewTitle("");
    } catch {
      setActionError(true);
    }
  };

  if (isLoading) {
    return <p className="text-sm text-muted-foreground">{t("applications.documents.loading")}</p>;
  }
  if (hasError) {
    return <p className="text-sm text-danger">{t("applications.documents.error")}</p>;
  }

  return (
    <div>
      {documents.length === 0 ? (
        <p className="text-sm text-muted-foreground">{t("applications.documents.empty")}</p>
      ) : (
        <ul className="space-y-2">
          {documents.map((document) => (
            <li
              className="flex flex-wrap items-center justify-between gap-3 rounded-sm border bg-surface p-3 text-sm"
              key={document.id}
            >
              <div className="min-w-0">
                <span className="rounded-sm border bg-elevated px-2 py-0.5 text-[0.65rem] font-semibold uppercase tracking-wide text-muted-foreground">
                  {t(`applications.documentType.${document.document_type}` as TranslationKey)}
                </span>
                <p className="mt-1 font-semibold">{document.title}</p>
              </div>
              <select
                className={fieldClassName}
                onChange={(event) =>
                  void handleStatusChange(document.id, event.target.value as ApplicationDocumentStatus)
                }
                value={document.status}
              >
                {DOCUMENT_STATUSES.map((status) => (
                  <option key={status} value={status}>
                    {t(`applications.documentStatus.${status}` as TranslationKey)}
                  </option>
                ))}
              </select>
            </li>
          ))}
        </ul>
      )}

      {actionError ? (
        <p className="mt-2 text-xs text-danger" role="alert">
          {t("applications.states.actionError")}
        </p>
      ) : null}

      <div className="mt-3 flex flex-wrap items-end gap-2">
        <label className="block">
          <span className="text-xs font-semibold">{t("applications.documents.newType")}</span>
          <select
            className={fieldClassName}
            onChange={(event) => setNewType(event.target.value as ApplicationDocumentType)}
            value={newType}
          >
            {DOCUMENT_TYPES.map((type) => (
              <option key={type} value={type}>
                {t(`applications.documentType.${type}` as TranslationKey)}
              </option>
            ))}
          </select>
        </label>
        <label className="block flex-1">
          <span className="text-xs font-semibold">{t("applications.documents.newTitle")}</span>
          <input
            className={fieldClassName}
            onChange={(event) => setNewTitle(event.target.value)}
            type="text"
            value={newTitle}
          />
        </label>
        <Button onClick={() => void handleAdd()} size="sm" type="button">
          {t("applications.documents.add")}
        </Button>
      </div>
    </div>
  );
}
