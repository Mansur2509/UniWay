export type AuthTokens = {
  access: string;
  refresh: string;
};

const AUTH_STORAGE_KEY = "eduverse.auth.tokens";
export const AUTH_INVALID_EVENT = "eduverse:auth-invalid";

function canUseStorage() {
  return typeof window !== "undefined";
}

export const authStorage = {
  get(): AuthTokens | null {
    if (!canUseStorage()) {
      return null;
    }

    const rawValue = window.localStorage.getItem(AUTH_STORAGE_KEY);
    if (!rawValue) {
      return null;
    }

    try {
      const parsedValue = JSON.parse(rawValue) as Partial<AuthTokens>;
      if (
        typeof parsedValue.access === "string" &&
        typeof parsedValue.refresh === "string"
      ) {
        return {
          access: parsedValue.access,
          refresh: parsedValue.refresh
        };
      }
    } catch {
      // Invalid or manually modified auth state is discarded.
    }

    window.localStorage.removeItem(AUTH_STORAGE_KEY);
    return null;
  },

  set(tokens: AuthTokens) {
    if (canUseStorage()) {
      window.localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(tokens));
    }
  },

  clear() {
    if (canUseStorage()) {
      window.localStorage.removeItem(AUTH_STORAGE_KEY);
    }
  }
};

export function notifyAuthInvalid() {
  if (typeof window !== "undefined") {
    window.dispatchEvent(new Event(AUTH_INVALID_EVENT));
  }
}
