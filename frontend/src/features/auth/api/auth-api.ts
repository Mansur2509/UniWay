import type {
  AuthResponse,
  CurrentUser,
  LoginInput,
  RegisterInput,
  UpdateCurrentUserInput
} from "@/entities/user";
import { apiRequest } from "@/shared/api/client";

export function loginRequest(input: LoginInput) {
  return apiRequest<AuthResponse>("/login/", {
    base: "auth",
    auth: false,
    method: "POST",
    body: input
  });
}

export function registerRequest(input: RegisterInput) {
  return apiRequest<AuthResponse>("/register/", {
    base: "auth",
    auth: false,
    method: "POST",
    body: input
  });
}

export function logoutRequest(refresh: string) {
  return apiRequest<void>("/logout/", {
    base: "auth",
    method: "POST",
    body: { refresh }
  });
}

export function getCurrentUserRequest() {
  return apiRequest<CurrentUser>("/me/", { base: "auth" });
}

export function updateCurrentUserRequest(input: UpdateCurrentUserInput) {
  return apiRequest<CurrentUser>("/me/", {
    base: "auth",
    method: "PATCH",
    body: input
  });
}
