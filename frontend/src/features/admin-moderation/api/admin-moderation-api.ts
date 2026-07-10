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

export function getUniversityReviewQueueRequest() {
  return apiRequest<UniversityModerationRecord[]>("/review-queue/", {
    base: "universityModeration"
  });
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

export function getAdminOrganizersRequest() {
  return apiRequest<OrganizerModerationRow[]>("/", { base: "adminOrganizers" });
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
