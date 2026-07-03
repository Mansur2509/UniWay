import type { OfficialExamDate } from "@/entities/exam";
import { apiRequest, normalizePaginatedResponse } from "@/shared/api/client";

type ExamDateParams = {
  exam_type?: "SAT" | "AP";
  event_kind?: OfficialExamDate["event_kind"];
  page_size?: number;
};

function buildQuery(params: ExamDateParams) {
  const query = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value) {
      query.set(key, String(value));
    }
  });
  const queryString = query.toString();
  return queryString ? `?${queryString}` : "";
}

export async function getOfficialExamDatesRequest(params: ExamDateParams = {}) {
  const response = await apiRequest<unknown>(`/exam-dates/${buildQuery(params)}`, {
    base: "api"
  });
  return normalizePaginatedResponse<OfficialExamDate>(response, "official exam dates");
}
