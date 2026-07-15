import type { UserReport, UserReportInput } from "@/entities/admin-moderation";
import { apiRequest } from "@/shared/api/client";

export function createUserReportRequest(input: UserReportInput) {
  return apiRequest<UserReport>("/", { base: "reports", method: "POST", body: input });
}
