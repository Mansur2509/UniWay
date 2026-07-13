export type AuthTokens = {
  access: string;
  // Transitional only: an already-issued pre-migration refresh token may be
  // read once from legacy storage and exchanged for an HttpOnly cookie.
  refresh?: string;
};

const AUTH_STORAGE_KEY = "uniway.auth.tokens";
const LEGACY_AUTH_STORAGE_KEYS = ["eduverse.auth.tokens"];
export const AUTH_INVALID_STORAGE_KEY = "uniway.auth.invalidated-at";
export const AUTH_INVALID_EVENT = "uniway:auth-invalid";
const AUTH_BROADCAST_CHANNEL = "uniway:auth";

let memoryTokens: AuthTokens | null = null;
let legacyStorageChecked = false;

function getBrowserStorage(): Storage | null {
  if (typeof window === "undefined") {
    return null;
  }

  try {
    return window.localStorage;
  } catch {
    return null;
  }
}

function removeStoredTokens(storage: Storage | null) {
  try {
    storage?.removeItem(AUTH_STORAGE_KEY);
    for (const legacyKey of LEGACY_AUTH_STORAGE_KEYS) {
      storage?.removeItem(legacyKey);
    }
  } catch {
    // Storage can be unavailable in hardened/incognito browser contexts.
  }
}

function readStoredTokens(storage: Storage | null): string | null {
  try {
    const currentValue = storage?.getItem(AUTH_STORAGE_KEY) ?? null;
    if (currentValue) {
      return currentValue;
    }

    for (const legacyKey of LEGACY_AUTH_STORAGE_KEYS) {
      const legacyValue = storage?.getItem(legacyKey) ?? null;
      if (legacyValue) {
        return legacyValue;
      }
    }
  } catch {
    return null;
  }
  return null;
}

export const authStorage = {
  get(): AuthTokens | null {
    if (memoryTokens) {
      return memoryTokens;
    }

    if (legacyStorageChecked) {
      return null;
    }
    legacyStorageChecked = true;

    const storage = getBrowserStorage();

    const rawValue = readStoredTokens(storage);
    if (!rawValue) {
      return null;
    }

    try {
      const parsedValue = JSON.parse(rawValue) as Partial<AuthTokens>;
      if (typeof parsedValue.access === "string") {
        memoryTokens = {
          access: parsedValue.access,
          ...(typeof parsedValue.refresh === "string"
            ? { refresh: parsedValue.refresh }
            : {})
        };
        removeStoredTokens(storage);
        return memoryTokens;
      }
    } catch {
      // Invalid or manually modified auth state is discarded.
    }

    memoryTokens = null;
    removeStoredTokens(storage);
    return null;
  },

  set(tokens: AuthTokens) {
    memoryTokens = tokens;
    legacyStorageChecked = true;
    removeStoredTokens(getBrowserStorage());
  },

  clear() {
    memoryTokens = null;
    legacyStorageChecked = true;
    removeStoredTokens(getBrowserStorage());
  }
};

export function notifyAuthInvalid() {
  if (typeof window !== "undefined") {
    window.dispatchEvent(new Event(AUTH_INVALID_EVENT));
    try {
      window.localStorage.setItem(
        AUTH_INVALID_STORAGE_KEY,
        `${Date.now()}:${Math.random()}`
      );
    } catch {
      // Cross-tab storage can be unavailable in hardened browser contexts.
    }
    try {
      const channel = new BroadcastChannel(AUTH_BROADCAST_CHANNEL);
      channel.postMessage("invalid");
      channel.close();
    } catch {
      // BroadcastChannel is optional; the same-tab event remains authoritative.
    }
  }
}

export function subscribeToAuthInvalid(callback: () => void) {
  if (typeof window === "undefined") {
    return () => undefined;
  }

  const handleEvent = () => callback();
  const handleStorage = (event: StorageEvent) => {
    if (event.key === AUTH_INVALID_STORAGE_KEY) callback();
  };
  let channel: BroadcastChannel | null = null;

  window.addEventListener(AUTH_INVALID_EVENT, handleEvent);
  window.addEventListener("storage", handleStorage);
  try {
    channel = new BroadcastChannel(AUTH_BROADCAST_CHANNEL);
    channel.addEventListener("message", handleEvent);
  } catch {
    channel = null;
  }

  return () => {
    window.removeEventListener(AUTH_INVALID_EVENT, handleEvent);
    window.removeEventListener("storage", handleStorage);
    channel?.removeEventListener("message", handleEvent);
    channel?.close();
  };
}
