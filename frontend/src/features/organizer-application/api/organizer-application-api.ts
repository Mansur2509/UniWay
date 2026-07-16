import type {
  OrganizerApplication,
  OrganizerApplicationInput,
  OrganizerApplicationStatusSummary
} from "@/entities/organizer-application";
import { apiRequest } from "@/shared/api/client";

export function createOrganizerApplicationRequest(input: OrganizerApplicationInput) {
  return apiRequest<OrganizerApplication>("/", {
    base: "organizerApplications",
    method: "POST",
    body: input
  });
}

export async function getMyOrganizerApplicationRequest() {
  try {
    return await apiRequest<OrganizerApplicationStatusSummary>("/mine/", {
      base: "organizerApplications"
    });
  } catch {
    // No application yet (404) or a transient failure -- either way the UI
    // falls back to showing the "apply" button rather than blocking on it.
    return null;
  }
}
