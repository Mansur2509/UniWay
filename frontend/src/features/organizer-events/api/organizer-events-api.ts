import type {
  EventCategory,
  EventModerationLog,
  OrganizerEvent,
  OrganizerEventInput,
  OrganizerParticipant,
  PaginatedResponse
} from "@/entities/event";
import { apiRequest } from "@/shared/api/client";

export function getOrganizerEventCategoriesRequest() {
  return apiRequest<EventCategory[]>("/event-categories/", {
    base: "organizer"
  });
}

export function getOrganizerEventsRequest() {
  return apiRequest<PaginatedResponse<OrganizerEvent>>("/events/", {
    base: "organizer"
  });
}

export function createOrganizerEventRequest(input: OrganizerEventInput) {
  return apiRequest<OrganizerEvent>("/events/", {
    base: "organizer",
    method: "POST",
    body: input
  });
}

export function getOrganizerEventRequest(slug: string) {
  return apiRequest<OrganizerEvent>(`/events/${encodeURIComponent(slug)}/`, {
    base: "organizer"
  });
}

export function updateOrganizerEventRequest(
  slug: string,
  input: Partial<OrganizerEventInput>
) {
  return apiRequest<OrganizerEvent>(`/events/${encodeURIComponent(slug)}/`, {
    base: "organizer",
    method: "PATCH",
    body: input
  });
}

function postOrganizerEventAction(slug: string, action: string) {
  return apiRequest<OrganizerEvent>(
    `/events/${encodeURIComponent(slug)}/${action}/`,
    {
      base: "organizer",
      method: "POST"
    }
  );
}

export function submitOrganizerEventRequest(slug: string) {
  return postOrganizerEventAction(slug, "submit");
}

export function archiveOrganizerEventRequest(slug: string) {
  return postOrganizerEventAction(slug, "archive");
}

export function cancelOrganizerEventRequest(slug: string) {
  return postOrganizerEventAction(slug, "cancel");
}

export function getOrganizerEventParticipantsRequest(slug: string) {
  return apiRequest<PaginatedResponse<OrganizerParticipant>>(
    `/events/${encodeURIComponent(slug)}/registrations/`,
    { base: "organizer" }
  );
}

export function getPendingEventsRequest() {
  return apiRequest<PaginatedResponse<OrganizerEvent>>("/pending/", {
    base: "moderation"
  });
}

export function approveEventRequest(slug: string) {
  return apiRequest<OrganizerEvent>(`/${encodeURIComponent(slug)}/approve/`, {
    base: "moderation",
    method: "POST"
  });
}

export function rejectEventRequest(slug: string, reason: string) {
  return apiRequest<OrganizerEvent>(`/${encodeURIComponent(slug)}/reject/`, {
    base: "moderation",
    method: "POST",
    body: { reason }
  });
}

export function archiveModeratedEventRequest(slug: string) {
  return apiRequest<OrganizerEvent>(`/${encodeURIComponent(slug)}/archive/`, {
    base: "moderation",
    method: "POST"
  });
}

export function getEventModerationLogsRequest(slug: string) {
  return apiRequest<EventModerationLog[]>(
    `/${encodeURIComponent(slug)}/logs/`,
    { base: "moderation" }
  );
}
