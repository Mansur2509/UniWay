"use client";

import { useEffect, useState } from "react";

import type {
  ApplicationRecommendationRequest,
  RecommendationRequestStatus
} from "@/entities/application";
import {
  createApplicationRecommendationRequest,
  getApplicationRecommendationsRequest,
  updateApplicationRecommendationRequest
} from "@/features/applications";
import { useI18n, type TranslationKey } from "@/shared/i18n";
import { formatDate } from "@/shared/lib/date-time";
import { Button } from "@/shared/ui/button";
import { fieldClassName } from "@/shared/ui/field";

const RECOMMENDATION_REQUEST_STATUSES: RecommendationRequestStatus[] = [
  "not_requested",
  "requested",
  "agreed",
  "submitted",
  "unavailable"
];

export function ApplicationRecommendationsPanel({ applicationId }: { applicationId: number }) {
  const { locale, t } = useI18n();
  const [recommendations, setRecommendations] = useState<ApplicationRecommendationRequest[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [hasError, setHasError] = useState(false);
  const [newName, setNewName] = useState("");
  const [newRole, setNewRole] = useState("");

  useEffect(() => {
    setIsLoading(true);
    setHasError(false);
    getApplicationRecommendationsRequest(applicationId)
      .then(setRecommendations)
      .catch(() => setHasError(true))
      .finally(() => setIsLoading(false));
  }, [applicationId]);

  const handleStatusChange = async (id: number, status: RecommendationRequestStatus) => {
    const updated = await updateApplicationRecommendationRequest(id, { status });
    setRecommendations((current) => current.map((item) => (item.id === updated.id ? updated : item)));
  };

  const handleAdd = async () => {
    if (!newName.trim()) return;
    const created = await createApplicationRecommendationRequest(applicationId, {
      recommender_name: newName.trim(),
      recommender_role: newRole.trim()
    });
    setRecommendations((current) => [...current, created]);
    setNewName("");
    setNewRole("");
  };

  if (isLoading) {
    return <p className="text-sm text-muted-foreground">{t("applications.recommendationRequests.loading")}</p>;
  }
  if (hasError) {
    return <p className="text-sm text-danger">{t("applications.recommendationRequests.error")}</p>;
  }

  return (
    <div>
      {recommendations.length === 0 ? (
        <p className="text-sm text-muted-foreground">{t("applications.recommendationRequests.empty")}</p>
      ) : (
        <ul className="space-y-2">
          {recommendations.map((recommendation) => (
            <li
              className="flex flex-wrap items-center justify-between gap-3 rounded-sm border bg-surface p-3 text-sm"
              key={recommendation.id}
            >
              <div className="min-w-0">
                <p className="font-semibold">
                  {recommendation.recommender_display_name ?? recommendation.recommender_name}
                </p>
                {recommendation.recommender_role ? (
                  <p className="text-xs text-muted-foreground">{recommendation.recommender_role}</p>
                ) : null}
                {recommendation.due_date ? (
                  <p className="text-xs text-muted-foreground">
                    {formatDate(recommendation.due_date, locale)}
                  </p>
                ) : null}
              </div>
              <select
                className={fieldClassName}
                onChange={(event) =>
                  void handleStatusChange(
                    recommendation.id,
                    event.target.value as RecommendationRequestStatus
                  )
                }
                value={recommendation.status}
              >
                {RECOMMENDATION_REQUEST_STATUSES.map((status) => (
                  <option key={status} value={status}>
                    {t(`applications.recommendationRequestStatus.${status}` as TranslationKey)}
                  </option>
                ))}
              </select>
            </li>
          ))}
        </ul>
      )}

      <div className="mt-3 flex flex-wrap items-end gap-2">
        <label className="block flex-1">
          <span className="text-xs font-semibold">{t("applications.recommendationRequests.newName")}</span>
          <input
            className={fieldClassName}
            onChange={(event) => setNewName(event.target.value)}
            type="text"
            value={newName}
          />
        </label>
        <label className="block flex-1">
          <span className="text-xs font-semibold">{t("applications.recommendationRequests.newRole")}</span>
          <input
            className={fieldClassName}
            onChange={(event) => setNewRole(event.target.value)}
            type="text"
            value={newRole}
          />
        </label>
        <Button onClick={() => void handleAdd()} size="sm" type="button">
          {t("applications.recommendationRequests.add")}
        </Button>
      </div>
    </div>
  );
}
