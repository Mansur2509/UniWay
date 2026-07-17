import type {
  ApplicationReadiness,
  ProfileAssessmentEnvelope,
  ProfileCompletion,
  ProfileRecommendationsResponse,
  ProfileStrategy,
  StudentProfileDetails,
  UpdateStudentProfileInput
} from "@/entities/profile";
import { apiRequest, normalizePaginatedResponse } from "@/shared/api/client";
import { getOrFetch, invalidateCacheByPrefix } from "@/shared/lib/request-cache";

// Dashboard and Profile both independently fetch these three on mount
// (PERFORMANCE-011 PART 2) -- a short client cache with in-flight dedup
// means the second page to mount within the TTL shares the first page's
// result instead of firing its own request. Mutations below invalidate
// explicitly rather than waiting out the TTL.
const PROFILE_CACHE_TTL_MS = 15_000;
const PROFILE_CACHE_PREFIX = "profile:";

export function getProfileRequest() {
  return getOrFetch(
    `${PROFILE_CACHE_PREFIX}me`,
    () => apiRequest<StudentProfileDetails>("/me/", { base: "profile" }),
    PROFILE_CACHE_TTL_MS
  );
}

export async function updateProfileRequest(input: UpdateStudentProfileInput) {
  const result = await apiRequest<StudentProfileDetails>("/me/", {
    base: "profile",
    method: "PATCH",
    body: input
  });
  invalidateCacheByPrefix(PROFILE_CACHE_PREFIX);
  return result;
}

export function getProfileCompletionRequest() {
  return getOrFetch(
    `${PROFILE_CACHE_PREFIX}completion`,
    () => apiRequest<ProfileCompletion>("/completion/", { base: "profile" }),
    PROFILE_CACHE_TTL_MS
  );
}

export async function completeOnboardingRequest() {
  const result = await apiRequest<ProfileCompletion>("/complete-onboarding/", {
    base: "profile",
    method: "POST"
  });
  invalidateCacheByPrefix(PROFILE_CACHE_PREFIX);
  return result;
}

export function getApplicationReadinessRequest() {
  return apiRequest<ApplicationReadiness>("/readiness/", {
    base: "profile"
  });
}

export function getProfileAssessmentLatestRequest() {
  return getOrFetch(
    `${PROFILE_CACHE_PREFIX}assessment-latest`,
    () => apiRequest<ProfileAssessmentEnvelope>("/assessment/latest/", { base: "profile" }),
    PROFILE_CACHE_TTL_MS
  );
}

export async function runProfileAssessmentRequest() {
  const result = await apiRequest<ProfileAssessmentEnvelope>("/assessment/run/", {
    base: "profile",
    method: "POST"
  });
  invalidateCacheByPrefix(PROFILE_CACHE_PREFIX);
  return result;
}

// PROTOCOL-008 PART 7: gap-based recommendations and the time-bucketed
// action plan, both read-only and built purely from the cached assessment --
// never trigger an AI call on render.
export function getProfileRecommendationsRequest() {
  return apiRequest<ProfileRecommendationsResponse>("/recommendations/me/", {
    base: "api"
  });
}

export function getProfileStrategyRequest() {
  return apiRequest<ProfileStrategy>("/strategy/me/", {
    base: "api"
  });
}

// Profile item CRUD endpoints
type ItemType =
  | "activities"
  | "honors"
  | "olympiads"
  | "sports"
  | "research-projects"
  | "essays"
  | "portfolio-projects"
  | "volunteering"
  | "recommenders";

interface ProfileItem {
  id: number;
  created_at: string;
  updated_at: string;
}

// These lists are always scoped to the requesting student's own entries
// (never a shared/catalog dataset), so a generous page size just means every
// entry is visible in the editor -- never a second page a student has to
// know to ask for. 100 comfortably covers the "at least 30 activities"
// requirement with headroom.
const PROFILE_ITEMS_PAGE_SIZE = 100;

export async function getProfileItemsRequest<T extends ProfileItem>(itemType: ItemType) {
  const response = await apiRequest<unknown>(`/${itemType}/?page_size=${PROFILE_ITEMS_PAGE_SIZE}`, {
    base: "profile"
  });
  return normalizePaginatedResponse<T>(response, `profile ${itemType}`);
}

export async function createProfileItemRequest<T extends Partial<ProfileItem>>(itemType: ItemType, data: T) {
  const result = await apiRequest<T & ProfileItem>(`/${itemType}/`, {
    base: "profile",
    method: "POST",
    body: data
  });
  invalidateCacheByPrefix(PROFILE_CACHE_PREFIX);
  return result;
}

export async function updateProfileItemRequest<T extends Partial<ProfileItem>>(
  itemType: ItemType,
  id: number,
  data: T
) {
  const result = await apiRequest<T & ProfileItem>(`/${itemType}/${id}/`, {
    base: "profile",
    method: "PATCH",
    body: data
  });
  invalidateCacheByPrefix(PROFILE_CACHE_PREFIX);
  return result;
}

export async function deleteProfileItemRequest(itemType: ItemType, id: number) {
  const result = await apiRequest<void>(`/${itemType}/${id}/`, {
    base: "profile",
    method: "DELETE"
  });
  invalidateCacheByPrefix(PROFILE_CACHE_PREFIX);
  return result;
}
