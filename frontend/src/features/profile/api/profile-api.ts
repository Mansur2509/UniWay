import type {
  ApplicationReadiness,
  ProfileCompletion,
  StudentProfileDetails,
  UpdateStudentProfileInput
} from "@/entities/profile";
import { apiRequest } from "@/shared/api/client";

export function getProfileRequest() {
  return apiRequest<StudentProfileDetails>("/me/", {
    base: "profile"
  });
}

export function updateProfileRequest(input: UpdateStudentProfileInput) {
  return apiRequest<StudentProfileDetails>("/me/", {
    base: "profile",
    method: "PATCH",
    body: input
  });
}

export function getProfileCompletionRequest() {
  return apiRequest<ProfileCompletion>("/completion/", {
    base: "profile"
  });
}

export function completeOnboardingRequest() {
  return apiRequest<ProfileCompletion>("/complete-onboarding/", {
    base: "profile",
    method: "POST"
  });
}

export function getApplicationReadinessRequest() {
  return apiRequest<ApplicationReadiness>("/readiness/", {
    base: "profile"
  });
}
