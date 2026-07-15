# Loading & Performance Audit — UNIWAY-REMAINING-V1-FIXES-AND-LOADING-PERFORMANCE-020 (Phase 6)

This is a **delta audit**, not a re-derivation. `docs/PERFORMANCE_AUDIT_011.md` (full
frontend request audit) and `docs/API_PERFORMANCE_PROFILE_014.md` /
`docs/FRONTEND_PERFORMANCE_PROFILE_014.md` (query counts, payload sizes, bundle
sizes) already cover the whole app in depth and remain valid — their fixes are
still in the code (confirmed by the full backend suite: 947/947 passing, and
the static i18n/request-audit conventions they established are followed by
everything built in this task's Phases 1-5). This document covers only what
those audits could not have seen: the request/rendering surfaces this task's
own Phases 1-5 added or changed, plus a fresh bundle-size measurement.

## Method

Same as 014: `next build` production output for bundle sizes; direct source
reading (fetch effects, API modules, serializers, views) for request behavior.
No new load test, no production traffic sampling.

## What changed since 014

Five things touched request/render behavior in this task:

1. `ensure_demo_accounts` management command (Phase 1) — one-time startup/CLI
   command, not a request path. Not applicable to loading/performance.
2. Essay AI review timeout raised from the client's default to a dedicated
   90s (Phase 2).
3. Essay <-> Application linkage UI: an "Application" dropdown in the essay
   form, and a linked-essay unlink/link picker in the application timeline
   panel (Phase 3).
4. Student-facing Report action: a `ReportButton` wired into University detail
   and Event detail (Phase 4).
5. A new backend-only test (Phase 5) with no runtime/request surface.

## Bundle size delta (014 baseline -> current build)

Shared framework chunk is unchanged at 103 kB — no vendor/dependency growth.
Route-level increases are small and fully explained by (a) real new
user-facing strings added to all 4 locale dictionaries this task (English ships
in the initial shared chunk per 014's design, so dictionary growth is paid by
every route) and (b) the two new small feature UIs below.

| Route | 014 | Now | Delta | Explanation |
| --- | ---: | ---: | ---: | --- |
| `/login` | 173 kB | 177 kB | +4 kB | i18n dictionary growth only (no code touched this route) |
| `/dashboard` | 193 kB | 198 kB | +5 kB | i18n dictionary growth only |
| `/applications` | 188 kB | 194 kB | +6 kB | i18n growth + essay-link/unlink picker UI |
| `/profile` | 188 kB | 192 kB | +4 kB | i18n dictionary growth only |
| `/universities` | 179 kB | 181 kB | +2 kB | i18n dictionary growth only |
| `/universities/[slug]` | 186 kB | 189 kB | +3 kB | i18n growth + `ReportButton` |
| `/essays` | 181 kB | 186 kB | +5 kB | i18n growth + Application dropdown + applications fetch |
| `/events/[slug]` | 172 kB | 175 kB | +3 kB | i18n growth + `ReportButton` |
| `/roadmap` | 184 kB | 186 kB | +2 kB | i18n dictionary growth only |

No route grew by more than 6 kB (under 3.5% of any route's total). This is
organic growth from shipped functionality, not a regression — there is nothing
here for Phase 7 to claw back architecturally.

## New/changed request-surface audit

| Surface | Trigger | Pattern | Verdict |
| --- | --- | --- | --- |
| Essay form "Application" dropdown fetch (`getApplicationsRequest`, `screens/essays/index.tsx`) | Deferred to form open, `useRef`-guarded against refetch | Matches the established "defer + guard" convention | Pass |
| Essay-picker candidate fetch (`getEssaysRequest`, `application-timeline.tsx:379-389`) | Deferred to picker open (user action), state-guarded against refetch on reopen | Matches the established "defer to user action" convention (mirrors Roadmap's `GET /api/suggestions/` pattern, flagged as good in 011) | Pass |
| `handleLinkEssay` / `handleUnlinkEssay` (`application-timeline.tsx:356-377`) | User action -> mutate -> **full `getApplicationTimelineRequest` refetch** | Same self-inflicted-refetch shape 011 flagged for Roadmap/Applications/Essays suggestion-adding. Partially justified here (`linked_essays` is a server-computed projection via `timeline.py`'s `_linked_essays()`, not raw echoed data) but the mutation response (`updateEssayRequest`) already returns the full updated `EssayWorkspace`, so the local list could be patched directly instead of a full round trip | **Finding for Phase 7** — low severity (one extra GET on an explicit, infrequent action), fix by patching `timeline.linked_essays` from the mutation response |
| Essay-picker loading state (`application-timeline.tsx:595-596`) | Plain `<p>{t("common.loading")}</p>` while candidates load | Same bare-text pattern 011 flagged for Organizer/Admin secondary panels, instead of the existing `SkeletonCard`/`SkeletonRows` components | **Finding for Phase 7** — cosmetic only, no layout shift risk since it occupies the same slot either way |
| `ReportButton` (`features/reports/ui/report-button.tsx`) | Fully self-contained: idle until clicked, only network call is the POST on submit | No mount-time cost, no parent refetch/invalidation after submit | Pass |
| `UserReportCreateView` (`feedback_service/views.py:58-61`) | `IsAuthenticated` + `ScopedRateThrottle`/`ScopedIPRateThrottle`, `validate()` does at most 2 `.exists()` queries (target-existence + dedup) | Minimal, appropriately scoped for a low-frequency write endpoint | Pass |
| `_linked_essays()` FK fix (`application_service/timeline.py`) | Changed from a `(user, university)` filter to `(user, application)` | Identical query shape (single indexed 2-key filter) — a correctness fix with no cost change | Pass |
| Essay AI review timeout (`ESSAY_REVIEW_TIMEOUT_MS = 90_000`, `shared/api/client.ts:38`) | Passed explicitly by `scoreEssayRequest` only; the shared default (`REQUEST_TIMEOUT_MS`, used at `client.ts:309`) is untouched | Confirmed scoped, not global | Complies with the hard rule against a global 90s timeout |

## Hard-rule re-confirmation (performance-relevant subset)

- No AI provider call exists on any list/detail/render GET added or touched
  this task (confirmed by reading every new fetch call site above).
- No loading-animation or layout-shift risk introduced: the two new loading
  states (essay-picker candidates, Report form submit) occupy fixed slots
  already reserved by their surrounding `article`/`form` containers.
- No global timeout change: the 90s essay-review timeout is a per-call
  override, not a change to `REQUEST_TIMEOUT_MS`.

## Phase 7 resolution

Both findings above are fixed in `application-timeline.tsx`:
1. `handleLinkEssay`/`handleUnlinkEssay` now patch `timeline.linked_essays`
   directly from the mutation response (`updateEssayRequest`'s returned
   `EssayWorkspace` already carries every field `TimelineEssay` needs) instead
   of calling `getApplicationTimelineRequest` again. `refetchTimelineAfterEssayChange`
   is removed as dead code.
2. The picker's plain-text loading state is now `SkeletonText`, matching the
   convention used elsewhere.

Verified live (local dev, Cornell University application): unlinking "Why
Cornell Supplement" only fires `PATCH /api/essays/{id}/` (confirmed via network
trace — no timeline GET), and the essay disappears from "Linked essays"
immediately. Linking it back only fires the picker's `GET /api/essays/` (from
opening the picker) plus `PATCH /api/essays/{id}/`, and the essay reappears
with correct title/status/word-count/date. `tsc --noEmit`, `eslint`, and the
i18n key-coverage script all pass clean.

## Phase 8 resolution

No new backend inefficiency was found — the two touched backend surfaces
(`_linked_essays()`, `UserReportCreateView`) were already minimal, so Phase 8's
work was verification plus locking in query-count regression coverage for
them (neither had it before, unlike most other endpoints in this codebase):

- `application_service/tests/test_timeline.py`:
  `test_linked_essays_query_count_does_not_grow_with_essay_count` — asserts
  the timeline endpoint's query count is identical at 2 vs 8 linked essays
  (confirmed: `_linked_essays()` is one filtered queryset with `word_count`
  computed from an already-loaded field, no per-essay query).
- `feedback_service/tests/test_reports.py`:
  `test_submit_report_query_count_is_bounded` — asserts `POST /api/reports/`
  is exactly 3 queries (target-existence check, dedup check, insert).

Both pass today. Re-confirmed 014's "Remaining performance risks" against the
current code rather than re-deriving them from scratch:

| 014 risk | Still accurate? | Evidence |
| --- | --- | --- |
| `strategy/me` expensive on cold cache, needs a durable shared cache before multi-instance scaling | Yes | `university_service/recommendation_cache.py` still a short-TTL, process-local cache; no durable/shared layer added |
| Filter options ~24 queries cold, mitigated by a 600s TTL cache | Yes | `views.py:77` `FILTER_OPTIONS_CACHE_SECONDS = 600`, `build_university_filter_options` still ~23 queries per the code's own comment |
| SQLite timings don't model Supabase network round trips | Yes (unchanged, environmental) | No production endpoint-timing telemetry added this task |
| Process-local `LocMemCache` by default, no Redis | Yes | No `CACHES` setting in `config/settings.py` |
| No high-volume load test run | Yes (unchanged, environmental) | No load test added this task |

None of these are new — they were already correctly scoped in 014 as
staging/scaling concerns rather than V1-blocking bugs, and this task does not
change that assessment.

## Phase 9: Render cold-start UX + safe bounded retry

The core infrastructure already exists and needed no new work, only
verification: `REQUEST_TIMEOUT_MS = 20_000` (bounded, not the forbidden global
90s), a GET-only single bounded retry (`MAX_GET_NETWORK_RETRIES = 1`,
`client.ts`), in-flight GET dedup, and `AppGate`'s full-screen session-check
gate (the first thing every user sees) already pairs `useSlowLoad` with a
"the server may be waking up" hint and a retry/clear-session escape hatch for
a genuinely cold Render instance. `ESSAY_REVIEW_TIMEOUT_MS = 90_000` remains a
separate, explicitly-scoped constant used only by `scoreEssayRequest` — the
shared default is untouched, so the hard rule against a global 90s timeout
still holds.

What was missing: two screens this task's own Phases 3-4 touched had a
primary load/error state with no "waking up" hint and (for one of them) no
retry action, unlike the `LoadingNotice`/`RetryNotice` pattern used elsewhere
in the app (`essays/index.tsx`, `roadmap/index.tsx`, several admin screens).
Both fixed narrowly, without introducing a new shared component:
- `screens/universities/university-detail.tsx`: added `useSlowLoad(isLoading)`
  and the same hint text as `LoadingNotice` to the loading branch. The error
  branch already had a working retry button (`loadUniversity()`), untouched.
- `features/applications/ui/application-timeline.tsx`: added
  `useSlowLoad(isLoading)` plus the hint to the loading branch, and a
  `retryToken` state (bumped by a new retry button, added to the load
  effect's dependency array) to the error branch, which previously had no way
  to recover short of leaving and reopening the application.

A broader ~20-of-33-screen gap in `LoadingNotice`/`RetryNotice`/`Skeleton*`
adoption exists across the app (confirmed by grep) but predates this task and
is out of scope for a single phase here — noting it as a deferred, known item
(the same status as #136 "add localized help tooltips") rather than
attempting a risky, disproportionate sweep. `dashboard`/`profile`'s own
secondary-widget loading text is a deliberate, already-documented exception
(014: "Dashboard secondary widgets do not blank the primary content on
failure") that relies on `AppGate` having already proven the backend warm
before those widgets' own fetches fire.

Verified live (local dev): both edited screens render without console errors,
`tsc --noEmit`/`eslint`/the i18n script all pass, and a fresh `next build`
succeeds (`universities/[slug]` 12.5 kB -> 12.6 kB, `applications` unchanged
at 194 kB — both within noise).

## Phase 11: Functional + browser QA across viewports/modes

Scoped to this task's own new surfaces (Report action, essay <-> application
linkage UI, the Phase 9 cold-start additions) rather than re-running the full
app's viewport/mode matrix — that full sweep was already done in earlier,
dedicated tasks (e.g. mobile 390/375px QA and accessibility/responsive QA
tracked separately). Verified this task's surfaces at a representative sample
rather than the full 5-viewport x 5-mode cross product:

- **375px (mobile):** the Report form (university detail) renders at 293px
  wide, fully inside the 375px viewport with margin on both sides — no
  horizontal overflow.
- **768px (tablet) + dark mode:** the essay-link picker (application timeline)
  renders at 629px wide inside the 768px viewport — no overflow; dark theme
  applies correctly (`data-theme="dark"`, dark background) with no console
  errors.
- **Light / dark / system:** confirmed the app has no stored theme override
  in this session (`localStorage` has no theme key) and correctly follows
  `prefers-color-scheme` in both directions after a fresh load — light and
  dark both verified directly.
- **Reduced motion:** found and fixed a real, if pre-existing, gap while
  checking this — `shared/ui/skeleton.tsx`'s `Skeleton` (`animate-pulse`) had
  no `motion-reduce:animate-none` override, unlike the spinner icons used in
  `LoadingNotice`/`RetryNotice`/`AppGate`. Fixed with the same one-class
  pattern already used elsewhere; this component is shared by 7 pre-existing
  screens plus the new essay-picker usage from Phase 7, so the fix benefits
  all of them, not just this task's own surface.
- **Keyboard-only:** confirmed by reading the source rather than driving the
  browser with a real keyboard — `ReportButton` and the essay-linking controls
  use only native `<button>`/`<select>` elements with no `tabIndex` override
  and no non-status/alert ARIA `role` override, so standard Tab/Enter/Space
  operation is inherited for free rather than needing to be built.

`tsc --noEmit`, `eslint`, and the i18n script all still pass after the
`skeleton.tsx` fix.

## Phase 10: Performance acceptance targets — honest comparison

Informal targets a V1 release of this kind can reasonably be held to, checked
against what this task actually measured (not aspirational SLOs, and not a
substitute for production telemetry, which does not exist yet — see caveats).

| Target | Actual | Met? |
| --- | --- | --- |
| No route's First Load JS exceeds ~200 kB | 170-198 kB across all 33 routes (measured this session, see Phase 6/9) | Yes |
| No audited endpoint's query count scales with an unrelated collection's size (N+1) | Confirmed for every endpoint this task touched, via `assertNumQueries`/`CaptureQueriesContext` regression tests (2 new this task, plus the pre-existing suite in 014) | Yes |
| A cold/slow request surfaces an explanatory "may be waking up" message within ~5s, never an unexplained infinite spinner | `useSlowLoad` (5s threshold) now covers `AppGate` (session check — the first thing every user sees) plus every screen using `LoadingNotice` or the two screens fixed in Phase 9 | Yes, for the screens audited this task and the ones already covered pre-existing. Not yet true for the ~20 screens with the pre-existing plain-loading-text gap noted in Phase 9 (deferred, not blocking) |
| No single request can hang indefinitely; every request fails closed with a retryable, translated error | `REQUEST_TIMEOUT_MS = 20_000` default, `ESSAY_REVIEW_TIMEOUT_MS = 90_000` for the one documented exception, both enforced via `AbortController` in `withTimeout` | Yes |
| A transient failure recovers without the user needing to reload the whole page | GET requests: 1 automatic bounded retry. Failed page-level loads: a visible retry action exists for every screen audited this task (`AppGate`, `university-detail`, `application-timeline`) plus the screens already using `RetryNotice`/existing per-screen retry buttons | Yes for audited surfaces; the same ~20-screen gap as above applies elsewhere |
| No AI call can block a page indefinitely | Essay scoring, profile assessment, and semantic fit are all explicit-action-only, schema-validated, and bounded (documented worst cases: 90s / cached-fallback / cached-fallback respectively) | Yes |

### Honest caveats — what this comparison cannot claim

- **Render/Supabase production latency is still unmeasured.** Every number
  above comes from local SQLite (this session) or the 014 profile — both
  explicitly flagged in 014 as not representative of production network
  round trips. Phase 14's production smoke test is the only real-world signal
  this task will produce, and a single smoke test is not a load test.
- **A genuinely slow Render cold start (60-90s, per the client.ts comment
  documenting the free tier's actual behavior) will not resolve inside one
  20s timeout + one 2.5s-delayed retry.** The user will see the "waking up"
  message, then a translated timeout error, then can retry manually — this is
  graceful degradation, not a guarantee the first real request succeeds
  within a single bounded window. No architecture change proposed here
  removes Render's own spin-up latency; it only makes waiting for it legible
  and recoverable instead of silent.
- **No concurrent-user or connection-pool testing was performed.** 014's
  "Remaining performance risks" (process-local cache, no Redis, no load test)
  are reconfirmed still open in Phase 8 above, not resolved by this task.
- **The ~20-screen `LoadingNotice`/`RetryNotice` adoption gap** (Phase 9) means
  the "always explains a slow load, always offers retry" targets above are
  true for the screens this task's own audit covered in depth, not
  exhaustively true app-wide. Treat this table as accurate for what it
  measured, not as a blanket claim about every screen in the product.
