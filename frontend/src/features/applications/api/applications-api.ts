import type {
  ApplicationDocument,
  ApplicationDocumentInput,
  ApplicationMilestone,
  ApplicationMilestoneInput,
  ApplicationRecommendationRequest,
  ApplicationRecommendationRequestInput,
  ApplicationRequirement,
  ApplicationRequirementInput,
  ApplicationTimeline,
  ApplicationTrackerItem,
  ApplicationTrackerItemInput
} from "@/entities/application";
import type { EssayWorkspace } from "@/entities/essay";
import { apiRequest, normalizePaginatedResponse } from "@/shared/api/client";

type ApplicationListParams = {
  status?: string;
  university?: string;
  page?: number;
  page_size?: number;
  include_archived?: "true";
};

export async function getApplicationsRequest(filters: ApplicationListParams = {}) {
  const query = new URLSearchParams();
  for (const [key, value] of Object.entries(filters)) {
    const normalized = typeof value === "number" ? String(value) : value?.trim();
    if (normalized) {
      query.set(key, normalized);
    }
  }
  const queryString = query.toString();
  const response = await apiRequest<unknown>(`/${queryString ? `?${queryString}` : ""}`, {
    base: "applications"
  });
  return normalizePaginatedResponse<ApplicationTrackerItem>(response, "applications");
}

export function getApplicationRequest(id: number) {
  return apiRequest<ApplicationTrackerItem>(`/${id}/`, { base: "applications" });
}

export function getApplicationTimelineRequest(id: number) {
  return apiRequest<ApplicationTimeline>(`/${id}/timeline/`, { base: "applications" });
}

export function createApplicationRequest(input: ApplicationTrackerItemInput) {
  return apiRequest<ApplicationTrackerItem>("/", {
    base: "applications",
    method: "POST",
    body: input
  });
}

export function updateApplicationRequest(
  id: number,
  input: Partial<ApplicationTrackerItemInput>
) {
  return apiRequest<ApplicationTrackerItem>(`/${id}/`, {
    base: "applications",
    method: "PATCH",
    body: input
  });
}

export function deleteApplicationRequest(id: number) {
  return apiRequest<void>(`/${id}/`, { base: "applications", method: "DELETE" });
}

export function restoreApplicationRequest(id: number) {
  return apiRequest<ApplicationTrackerItem>(`/${id}/restore/`, {
    base: "applications",
    method: "POST"
  });
}

export function createApplicationMilestoneRequest(
  applicationId: number,
  input: ApplicationMilestoneInput
) {
  return apiRequest<ApplicationMilestone>(`/${applicationId}/milestones/`, {
    base: "applications",
    method: "POST",
    body: input
  });
}

export function updateApplicationMilestoneRequest(
  milestoneId: number,
  input: Partial<ApplicationMilestoneInput & { status: string }>
) {
  return apiRequest<ApplicationMilestone>(`/milestones/${milestoneId}/`, {
    base: "applications",
    method: "PATCH",
    body: input
  });
}

export function getApplicationRequirementsRequest(applicationId: number) {
  return apiRequest<ApplicationRequirement[]>(`/${applicationId}/requirements/`, {
    base: "applications"
  });
}

export function generateApplicationRequirementsRequest(applicationId: number) {
  return apiRequest<ApplicationRequirement[]>(`/${applicationId}/generate-requirements/`, {
    base: "applications",
    method: "POST"
  });
}

export function createApplicationRequirementRequest(
  applicationId: number,
  input: ApplicationRequirementInput
) {
  return apiRequest<ApplicationRequirement>(`/${applicationId}/requirements/`, {
    base: "applications",
    method: "POST",
    body: input
  });
}

export function updateApplicationRequirementRequest(
  requirementId: number,
  input: Partial<ApplicationRequirementInput>
) {
  return apiRequest<ApplicationRequirement>(`/requirements/${requirementId}/`, {
    base: "applications",
    method: "PATCH",
    body: input
  });
}

export function getApplicationRecommendationsRequest(applicationId: number) {
  return apiRequest<ApplicationRecommendationRequest[]>(`/${applicationId}/recommendations/`, {
    base: "applications"
  });
}

export function createApplicationRecommendationRequest(
  applicationId: number,
  input: ApplicationRecommendationRequestInput
) {
  return apiRequest<ApplicationRecommendationRequest>(`/${applicationId}/recommendations/`, {
    base: "applications",
    method: "POST",
    body: input
  });
}

export function updateApplicationRecommendationRequest(
  recommendationId: number,
  input: Partial<ApplicationRecommendationRequestInput>
) {
  return apiRequest<ApplicationRecommendationRequest>(`/recommendations/${recommendationId}/`, {
    base: "applications",
    method: "PATCH",
    body: input
  });
}

export function getApplicationDocumentsRequest(applicationId: number) {
  return apiRequest<ApplicationDocument[]>(`/${applicationId}/documents/`, {
    base: "applications"
  });
}

export function createApplicationDocumentRequest(
  applicationId: number,
  input: ApplicationDocumentInput
) {
  return apiRequest<ApplicationDocument>(`/${applicationId}/documents/`, {
    base: "applications",
    method: "POST",
    body: input
  });
}

export function updateApplicationDocumentRequest(
  documentId: number,
  input: Partial<ApplicationDocumentInput>
) {
  return apiRequest<ApplicationDocument>(`/documents/${documentId}/`, {
    base: "applications",
    method: "PATCH",
    body: input
  });
}

export function getApplicationEssaysRequest(applicationId: number) {
  return apiRequest<EssayWorkspace[]>(`/${applicationId}/essays/`, { base: "applications" });
}

export function createApplicationEssayRequest(
  applicationId: number,
  input: { title: string; essay_type?: string }
) {
  return apiRequest<EssayWorkspace>(`/${applicationId}/essays/`, {
    base: "applications",
    method: "POST",
    body: input
  });
}
