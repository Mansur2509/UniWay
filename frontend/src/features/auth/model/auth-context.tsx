"use client";

import {
  createContext,
  type ReactNode,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState
} from "react";

import type {
  CurrentUser,
  LoginInput,
  RegisterInput,
  UpdateCurrentUserInput
} from "@/entities/user";
import { ApiError } from "@/shared/api/client";
import {
  AUTH_INVALID_EVENT,
  authStorage
} from "@/shared/lib/auth-storage";

import {
  getCurrentUserRequest,
  loginRequest,
  logoutRequest,
  registerRequest,
  updateCurrentUserRequest
} from "../api/auth-api";

type AuthContextValue = {
  user: CurrentUser | null;
  status: AuthStatus;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (input: LoginInput) => Promise<CurrentUser>;
  register: (input: RegisterInput) => Promise<CurrentUser>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<CurrentUser | null>;
  retrySession: () => Promise<CurrentUser | null>;
  updateUser: (input: UpdateCurrentUserInput) => Promise<CurrentUser>;
};

export type AuthStatus =
  | "checking"
  | "authenticated"
  | "unauthenticated"
  | "offline";

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<CurrentUser | null>(null);
  const [status, setStatus] = useState<AuthStatus>("checking");

  const refreshUser = useCallback(async () => {
    if (!authStorage.get()) {
      setUser(null);
      setStatus("unauthenticated");
      return null;
    }

    setStatus("checking");
    try {
      const currentUser = await getCurrentUserRequest();
      setUser(currentUser);
      setStatus("authenticated");
      return currentUser;
    } catch (error) {
      if (error instanceof ApiError && (error.status === 401 || error.status === 403)) {
        authStorage.clear();
        setUser(null);
        setStatus("unauthenticated");
        return null;
      }

      setStatus("offline");
      return null;
    }
  }, []);

  useEffect(() => {
    void refreshUser();
  }, [refreshUser]);

  useEffect(() => {
    function handleInvalidAuth() {
      authStorage.clear();
      setUser(null);
      setStatus("unauthenticated");
    }

    window.addEventListener(AUTH_INVALID_EVENT, handleInvalidAuth);
    return () => window.removeEventListener(AUTH_INVALID_EVENT, handleInvalidAuth);
  }, []);

  const login = useCallback(async (input: LoginInput) => {
    const response = await loginRequest(input);
    authStorage.set({
      access: response.access,
      refresh: response.refresh
    });
    setUser(response.user);
    setStatus("authenticated");
    return response.user;
  }, []);

  const register = useCallback(async (input: RegisterInput) => {
    const response = await registerRequest(input);
    authStorage.set({
      access: response.access,
      refresh: response.refresh
    });
    setUser(response.user);
    setStatus("authenticated");
    return response.user;
  }, []);

  const logout = useCallback(async () => {
    try {
      if (authStorage.get()) {
        await getCurrentUserRequest();
      }
      const tokens = authStorage.get();
      if (tokens) {
        await logoutRequest(tokens.refresh);
      }
    } catch {
      // Local logout still completes if the API is unavailable.
    } finally {
      authStorage.clear();
      setUser(null);
      setStatus("unauthenticated");
    }
  }, []);

  const updateUser = useCallback(async (input: UpdateCurrentUserInput) => {
    const updatedUser = await updateCurrentUserRequest(input);
    setUser(updatedUser);
    return updatedUser;
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      status,
      isLoading: status === "checking",
      isAuthenticated: status === "authenticated" && user !== null,
      login,
      register,
      logout,
      refreshUser,
      retrySession: refreshUser,
      updateUser
    }),
    [login, logout, refreshUser, register, status, updateUser, user]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider.");
  }
  return context;
}
