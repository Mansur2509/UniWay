import type { RecommendationsResponse } from "@/entities/recommendation";
import type { ApplicationStrategyResponse } from "@/entities/strategy";
import type {
  SavedUniversity,
  SavedUniversityLite,
  StudyDestination,
  UniversityDetails,
  UniversityFilterOptions,
  UniversityFilters,
  UniversityFitAnalysis,
  UniversityFitRefreshResponse
} from "@/entities/university";
import { ApiError, apiRequest, normalizePaginatedResponse } from "@/shared/api/client";
import { env } from "@/shared/config/env";
import { getOrFetch } from "@/shared/lib/request-cache";

export const UNIVERSITY_CATALOG_TIMEOUT_MS = 60_000;

// Filter options are reference data already cached server-side for 600s
// (PERFORMANCE-011 audit item), yet every mount of the Universities list
// still fetched them fresh. A client-side TTL well under the server's window
// avoids the redundant round trip without ever risking stale filter choices
// past what the server itself considers fresh (PERFORMANCE-012 PART 1).
const FILTER_OPTIONS_CACHE_TTL_MS = 300_000;
const FILTER_OPTIONS_CACHE_KEY = "universities:filter-options";
const DESTINATIONS_CACHE_TTL_MS = 300_000;
const DESTINATIONS_CACHE_KEY = "universities:destinations";

type PaginationParams = {
  page?: number;
  page_size?: number;
};

function buildQuery(filters: Record<string, string | number | undefined>) {
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

export async function getUniversitiesRequest(
  filters: UniversityFilters = {},
  pagination: PaginationParams = {}
) {
  const path = `/universities/${buildQuery({ ...filters, ...pagination })}`;
  try {
    const response = await apiRequest<unknown>(path, {
      base: "api",
      timeoutMs: UNIVERSITY_CATALOG_TIMEOUT_MS
    });
    // The catalog endpoint may return a bare array or a DRF `{ results: [...] }`
    // page; normalize both. An empty list yields `{ results: [] }` so the screen
    // shows its empty state rather than an error.
    return normalizePaginatedResponse<UniversityDetails>(response, "universities");
  } catch (error) {
    // Dev-only diagnostics for the most failure-prone call (it is the first
    // `base: "api"` request and the one that broke when the API base URL was
    // misconfigured). Never logs auth tokens.
    if (process.env.NODE_ENV !== "production") {
      console.warn("[universities-api] catalog load failed", {
        requestUrl: `${env.apiBaseUrl}${path}`,
        status: error instanceof ApiError ? error.status : undefined,
        message: error instanceof ApiError ? error.message : String(error),
        // `data` carries the response body preview / content-type that
        // `parseResponse` attaches for non-JSON (e.g. a 404 HTML page).
        responsePreview: error instanceof ApiError ? error.data : undefined
      });
    }
    throw error;
  }
}

export function getUniversityFilterOptionsRequest() {
  return getOrFetch(
    FILTER_OPTIONS_CACHE_KEY,
    () =>
      apiRequest<UniversityFilterOptions>("/universities/filter-options/", {
        base: "api",
        timeoutMs: UNIVERSITY_CATALOG_TIMEOUT_MS
      }),
    FILTER_OPTIONS_CACHE_TTL_MS
  );
}

export function getStudyDestinationsRequest() {
  return getOrFetch(
    DESTINATIONS_CACHE_KEY,
    () =>
      apiRequest<{ results: StudyDestination[] }>("/universities/destinations/", {
        base: "api",
        timeoutMs: UNIVERSITY_CATALOG_TIMEOUT_MS
      }),
    DESTINATIONS_CACHE_TTL_MS
  );
}

export function getUniversityRequest(slug: string) {
  return apiRequest<UniversityDetails>(`/universities/${encodeURIComponent(slug)}/`, {
    base: "api",
    timeoutMs: UNIVERSITY_CATALOG_TIMEOUT_MS
  });
}

export function getUniversityFitRequest(slug: string) {
  return apiRequest<UniversityFitAnalysis>(
    `/universities/${encodeURIComponent(slug)}/fit/`,
    { base: "api" }
  );
}

// Explicit user action only (PERFORMANCE-011 PART 5/6) -- never called on
// page render. Deterministic fit is always fast; this is the one call that
// may invoke AI, so it gets its own longer timeout rather than sharing the
// default REQUEST_TIMEOUT_MS.
export function refreshUniversityFitRequest(slug: string) {
  return apiRequest<UniversityFitRefreshResponse>(
    `/universities/${encodeURIComponent(slug)}/fit/refresh/`,
    { base: "api", method: "POST", timeoutMs: 30_000 }
  );
}

export function compareUniversitiesRequest(ids: number[]) {
  return apiRequest<UniversityDetails[]>(
    `/universities/compare/${buildQuery({ ids: ids.join(",") })}`,
    { base: "api" }
  );
}

export function addToShortlistRequest(slug: string) {
  return apiRequest<SavedUniversity>(
    `/universities/${encodeURIComponent(slug)}/shortlist/`,
    { base: "api", method: "POST" }
  );
}

export function removeFromShortlistRequest(slug: string) {
  return apiRequest<void>(`/universities/${encodeURIComponent(slug)}/shortlist/`, {
    base: "api",
    method: "DELETE"
  });
}

export function getShortlistRequest(
  options: { lite: true }
): Promise<ReturnType<typeof normalizePaginatedResponse<SavedUniversityLite>>>;
export function getShortlistRequest(
  options?: { lite?: false }
): Promise<ReturnType<typeof normalizePaginatedResponse<SavedUniversity>>>;
export async function getShortlistRequest(options: { lite?: boolean } = {}) {
  const path = options.lite ? "/universities/shortlist/?lite=1" : "/universities/shortlist/";
  const response = await apiRequest<unknown>(path, { base: "api" });
  return normalizePaginatedResponse<SavedUniversity | SavedUniversityLite>(
    response,
    "university shortlist"
  );
}

export function getRecommendationsRequest() {
  return apiRequest<RecommendationsResponse>("/universities/recommendations/", { base: "api" });
}

export function getApplicationStrategyRequest() {
  return apiRequest<ApplicationStrategyResponse>("/universities/strategy/", { base: "api" });
}
