/**
 * Minimal in-memory request cache with in-flight de-duplication.
 *
 * This codebase has no react-query/SWR, so every component independently
 * calls its own API function on mount -- when two components on the same
 * page (or two pages navigated within a few seconds) want the same data
 * (e.g. Dashboard and Profile both fetching /me/, /completion/, and
 * /assessment/latest/), that used to mean two separate network requests.
 *
 * `getOrFetch` fixes the two costly cases:
 *  - Two callers within the same tick share one in-flight promise instead
 *    of firing two identical requests.
 *  - A repeat call within `ttlMs` is served from memory instead of
 *    hitting the network again.
 *
 * State lives in a module-level Map, so it resets on a full page reload --
 * that's intentional, this is a short-lived session cache, not persistence.
 */

type CacheEntry<T> = {
  value?: T;
  promise?: Promise<T>;
  cachedAt: number;
};

// Next.js's per-route client chunking can end up instantiating this module
// more than once (each route's bundle gets its own copy unless the bundler
// merges it into a shared chunk), which would silently give Dashboard and
// Profile two separate Maps instead of one shared cache -- defeating the
// entire point. Parking the store on `globalThis` guarantees every caller
// resolves to the exact same Map no matter how the module got bundled, the
// same defensive pattern Next.js itself recommends for dev-mode singletons.
const GLOBAL_KEY = Symbol.for("uniway.requestCache");

type GlobalWithStore = typeof globalThis & {
  [GLOBAL_KEY]?: Map<string, CacheEntry<unknown>>;
};

const globalWithStore = globalThis as GlobalWithStore;
const store = globalWithStore[GLOBAL_KEY] ?? new Map<string, CacheEntry<unknown>>();
globalWithStore[GLOBAL_KEY] = store;

export function getOrFetch<T>(key: string, fetcher: () => Promise<T>, ttlMs: number): Promise<T> {
  const entry = store.get(key) as CacheEntry<T> | undefined;
  const now = Date.now();

  if (entry?.promise) {
    return entry.promise;
  }
  if (entry && entry.value !== undefined && now - entry.cachedAt < ttlMs) {
    return Promise.resolve(entry.value);
  }

  const promise = fetcher()
    .then((value) => {
      store.set(key, { value, cachedAt: Date.now() });
      return value;
    })
    .catch((error: unknown) => {
      store.delete(key);
      throw error;
    });

  store.set(key, { promise, cachedAt: now });
  return promise;
}

export function invalidateCache(key: string): void {
  store.delete(key);
}

export function invalidateCacheByPrefix(prefix: string): void {
  for (const key of store.keys()) {
    if (key.startsWith(prefix)) {
      store.delete(key);
    }
  }
}
