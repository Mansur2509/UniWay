import type {
  EventDetails,
  EventFilters,
  EventRegistration,
  ParticipationRecord
} from "@/entities/event";
import { apiRequest, normalizePaginatedResponse } from "@/shared/api/client";

type PaginationParams = {
  page?: number;
  page_size?: number;
};

function buildEventQuery(filters: Record<string, string | number | undefined>) {
  const query = new URLSearchParams();
  for (const [key, value] of Object.entries(filters)) {
    const normalized = typeof value === "number" ? String(value) : value?.trim();
    if (normalized) {
      query.set(key, normalized);
    }
  }
  const queryString = query.toString();
  return queryString ? `?${queryString}` : "";
}

export async function getEventsRequest(
  filters: EventFilters = {},
  pagination: PaginationParams = {}
) {
  const response = await apiRequest<unknown>(
    `/${buildEventQuery({ ...filters, ...pagination })}`,
    { base: "events" }
  );
  return normalizePaginatedResponse<EventDetails>(response, "events");
}

export function getEventRequest(slug: string) {
  return apiRequest<EventDetails>(`/${encodeURIComponent(slug)}/`, {
    base: "events"
  });
}

export function registerForEventRequest(
  slug: string,
  answers?: Record<string, unknown>
) {
  return apiRequest<EventRegistration>(`/${encodeURIComponent(slug)}/register/`, {
    base: "events",
    method: "POST",
    body: answers ? { answers } : undefined
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

export async function getMyEventRegistrationsRequest(pagination: PaginationParams = {}) {
  const response = await apiRequest<unknown>(`/my-registrations/${buildEventQuery(pagination)}`, {
    base: "events"
  });
  return normalizePaginatedResponse<EventRegistration>(response, "event registrations");
}

export async function getParticipationRecordsRequest(pagination: PaginationParams = {}) {
  const response = await apiRequest<unknown>(
    `/participation-records/${buildEventQuery(pagination)}`,
    {
      base: "events"
    }
  );
  return normalizePaginatedResponse<ParticipationRecord>(
    response,
    "participation records"
  );
}
