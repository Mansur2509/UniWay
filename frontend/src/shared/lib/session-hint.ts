const SESSION_HINT_COOKIE = "uniway_session_hint";
// Generous upper bound only -- the real session lifetime is enforced by the
// backend's HttpOnly refresh cookie. This is a UX signal only: it lets
// AppGate distinguish "probably a returning authenticated visitor" from
// "genuinely fresh visitor" at "/" without waiting on a network round trip,
// so a returning user never flashes the public landing page while their
// session is being confirmed, while brand-new visitors keep the instant,
// backend-independent landing page. It carries no authorization weight --
// a spoofed or missing value only changes which loading UI is shown, never
// what a request is allowed to do.
const SESSION_HINT_MAX_AGE_SECONDS = 60 * 60 * 24 * 30;

export function setSessionHint() {
  if (typeof document === "undefined") return;
  document.cookie = `${SESSION_HINT_COOKIE}=1; path=/; max-age=${SESSION_HINT_MAX_AGE_SECONDS}; samesite=lax`;
}

export function clearSessionHint() {
  if (typeof document === "undefined") return;
  document.cookie = `${SESSION_HINT_COOKIE}=; path=/; max-age=0; samesite=lax`;
}

export function hasSessionHint(): boolean {
  if (typeof document === "undefined") return false;
  return document.cookie
    .split("; ")
    .some((entry) => entry === `${SESSION_HINT_COOKIE}=1`);
}
