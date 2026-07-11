import type {
  OrganizerModerationActionInput,
  OrganizerModerationRow,
  ReportStatus,
  ReportTargetType,
  UniversityModerationActionInput,
  UniversityModerationRecord,
  UserReport,
  UserReportInput
} from "@/entities/admin-moderation";
import { apiRequest, normalizePaginatedResponse } from "@/shared/api/client";

type PageParams = { page?: number; page_size?: number };

function buildPageQuery(params: PageParams) {
  const query = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined) {
      query.set(key, String(value));
    }
  }
  const queryString = query.toString();
  return queryString ? `?${queryString}` : "";
}

export async function getUniversityReviewQueueRequest(params: PageParams = {}) {
  const response = await apiRequest<unknown>(`/review-queue/${buildPageQuery(params)}`, {
    base: "universityModeration"
  });
  return normalizePaginatedResponse<UniversityModerationRecord>(response, "university review queue");
}

export function updateUniversityModerationRequest(
  universityId: number,
  input: UniversityModerationActionInput
) {
  return apiRequest<UniversityModerationRecord>(`/${universityId}/moderation/`, {
    base: "universityModeration",
    method: "PATCH",
    body: input
  });
}

export function createUserReportRequest(input: UserReportInput) {
  return apiRequest<UserReport>("/", { base: "reports", method: "POST", body: input });
}

type AdminReportsParams = {
  status?: ReportStatus | "";
  target_type?: ReportTargetType | "";
  page?: number;
  page_size?: number;
};

function buildQuery(params: AdminReportsParams) {
  const query = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== "") {
      query.set(key, String(value));
    }
  }
  const queryString = query.toString();
  return queryString ? `?${queryString}` : "";
}

export async function getAdminReportsRequest(params: AdminReportsParams = {}) {
  const response = await apiRequest<unknown>(buildQuery(params), { base: "adminReports" });
  return normalizePaginatedResponse<UserReport>(response, "admin reports");
}

export function updateAdminReportRequest(id: number, input: { status: ReportStatus }) {
  return apiRequest<UserReport>(`/${id}/`, {
    base: "adminReports",
    method: "PATCH",
    body: input
  });
}

export async function getAdminOrganizersRequest(params: PageParams = {}) {
  const response = await apiRequest<unknown>(`/${buildPageQuery(params)}`, { base: "adminOrganizers" });
  return normalizePaginatedResponse<OrganizerModerationRow>(response, "admin organizers");
}

export function updateOrganizerModerationRequest(
  userId: number,
  input: OrganizerModerationActionInput
) {
  return apiRequest<OrganizerModerationRow>(`/${userId}/moderation/`, {
    base: "adminOrganizers",
    method: "PATCH",
    body: input
  });
}
