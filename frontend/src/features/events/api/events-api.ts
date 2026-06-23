import type {
  EventDetails,
  EventFilters,
  EventRegistration,
  PaginatedResponse
} from "@/entities/event";
import { apiRequest } from "@/shared/api/client";

function buildEventQuery(filters: EventFilters) {
  const query = new URLSearchParams();
  for (const [key, value] of Object.entries(filters)) {
    if (value?.trim()) {
      query.set(key, value.trim());
    }
  }
  const queryString = query.toString();
  return queryString ? `?${queryString}` : "";
}

export function getEventsRequest(filters: EventFilters = {}) {
  return apiRequest<PaginatedResponse<EventDetails>>(
    `/${buildEventQuery(filters)}`,
    { base: "events" }
  );
}

export function getEventRequest(slug: string) {
  return apiRequest<EventDetails>(`/${encodeURIComponent(slug)}/`, {
    base: "events"
  });
}

export function registerForEventRequest(slug: string) {
  return apiRequest<EventRegistration>(`/${encodeURIComponent(slug)}/register/`, {
    base: "events",
    method: "POST"
  });
}

export function cancelEventRegistrationRequest(slug: string) {
  return apiRequest<EventRegistration>(
    `/${encodeURIComponent(slug)}/cancel-registration/`,
    {
      base: "events",
      method: "POST"
    }
  );
}

export function getMyEventRegistrationsRequest() {
  return apiRequest<PaginatedResponse<EventRegistration>>("/my-registrations/", {
    base: "events"
  });
}

