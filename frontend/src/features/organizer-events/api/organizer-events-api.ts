import type {
  EventCategory,
  EventModerationLog,
  EventFormField,
  OrganizerEventAnalytics,
  OrganizerEventForm,
  OrganizerEvent,
  OrganizerEventInput,
  OrganizerParticipant
} from "@/entities/event";
import { apiRequest, normalizePaginatedResponse } from "@/shared/api/client";

type PaginationParams = {
  page?: number;
  page_size?: number;
};

function buildQuery(params: PaginationParams) {
  const query = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined) {
      query.set(key, String(value));
    }
  }
  const queryString = query.toString();
  return queryString ? `?${queryString}` : "";
}

export function getOrganizerEventCategoriesRequest() {
  return apiRequest<EventCategory[]>("/event-categories/", {
    base: "organizer"
  });
}

export async function getOrganizerEventsRequest(params: PaginationParams = {}) {
  const response = await apiRequest<unknown>(`/events/${buildQuery(params)}`, {
    base: "organizer"
  });
  return normalizePaginatedResponse<OrganizerEvent>(response, "organizer events");
}

export function getOrganizerEventAnalyticsRequest() {
  return apiRequest<OrganizerEventAnalytics>("/events/analytics/", {
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

export function getOrganizerEventFormRequest(slug: string) {
  return apiRequest<OrganizerEventForm>(`/events/${encodeURIComponent(slug)}/form/`, {
    base: "organizer"
  });
}

export function saveOrganizerEventFormRequest(
  slug: string,
  fields: EventFormField[]
) {
  return apiRequest<OrganizerEventForm>(`/events/${encodeURIComponent(slug)}/form/`, {
    base: "organizer",
    method: "PUT",
    body: { fields }
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

export async function getOrganizerEventParticipantsRequest(
  slug: string,
  params: PaginationParams = {}
) {
  const response = await apiRequest<unknown>(
    `/events/${encodeURIComponent(slug)}/registrations/${buildQuery(params)}`,
    { base: "organizer" }
  );
  return normalizePaginatedResponse<OrganizerParticipant>(response, "event participants");
}

export function checkInParticipantRequest(slug: string, registrationId: number) {
  return apiRequest<OrganizerParticipant>(
    `/events/${encodeURIComponent(slug)}/registrations/${registrationId}/check-in/`,
    {
      base: "organizer",
      method: "POST"
    }
  );
}

export function verifyEventTicketRequest(slug: string, code: string) {
  return apiRequest<OrganizerParticipant>(
    `/events/${encodeURIComponent(slug)}/tickets/verify/`,
    {
      base: "organizer",
      method: "POST",
      body: { code }
    }
  );
}

export function exportOrganizerEventParticipantsRequest(slug: string) {
  return apiRequest<Blob>(
    `/events/${encodeURIComponent(slug)}/registrations/export/`,
    {
      base: "organizer",
      responseType: "blob"
    }
  );
}

export async function getPendingEventsRequest(params: PaginationParams = {}) {
  const response = await apiRequest<unknown>(`/pending/${buildQuery(params)}`, {
    base: "moderation"
  });
  return normalizePaginatedResponse<OrganizerEvent>(response, "moderation events");
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
