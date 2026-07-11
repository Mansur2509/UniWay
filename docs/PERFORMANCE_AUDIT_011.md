# Performance Audit — EDUVERSE-PERFORMANCE-LOADERS-FIT-AI-HARDENING-011

Full frontend request audit (Phase 1) across every page/screen, plus backend endpoint findings that inform Phases 4-7. Produced by reading every screen's fetch effects and API modules end-to-end (not sampled).

## Headline findings

1. **No shared request/cache layer exists anywhere in the frontend.** Every component calls its own feature API function in its own `useEffect` and manages its own `isLoading`/`hasError` state (confirmed: no react-query/SWR/axios in `package.json`, no cache utility under `frontend/src/shared`). Two pages needing the same data (e.g. Dashboard and Profile both wanting profile-assessment) each issue their own independent HTTP request.
2. **Dashboard fires 13 concurrent requests on mount; Profile fires 13.** Several of these are below-the-fold data (strategy panel, gap recommendations, essay counts) that don't need to block the initial paint.
3. **Profile completion is computed by three separate endpoints that each independently call the same backend function** (`calculate_profile_completion()`): `/api/profile/completion/`, `/api/profile/readiness/`, and `/api/v1/analytics/me/`. Dashboard calls all three; Profile calls one of them again.
4. **`POST /api/suggestions/generate/` fires unconditionally on every Dashboard mount.** It's a write endpoint (upserts `SuggestedItem` rows) that is also wired to an explicit "Refresh" button — and a cheap read-only equivalent (`GET /api/suggestions/`) already exists and goes unused on mount. Confirmed idempotent server-side (dedup-key upsert, no duplicate rows), so this is a wasted-work/wrong-semantics bug, not a data-integrity bug.
5. **University detail's fit endpoint is fetched automatically on mount**, unconditionally, alongside the university detail call. This is the exact problem Phase 5 targets; the endpoint itself is confirmed 100% deterministic today (no AI call in the current code), so no hard-rule violation exists yet — but there's also no cache/status architecture, which Phase 5 adds.
6. **No `AbortController` is usable by any screen.** `shared/api/client.ts`'s `withTimeout` unconditionally overwrites any caller-supplied `signal` with its own internal timeout-abort controller, so no component can cancel an in-flight request on unmount or on a newer request superseding an older one. Several screens use ad-hoc `cancelled` boolean flags instead (suppresses the resulting `setState` but doesn't cancel the network request).
7. **No debounce gap found.** Every filter/search input audited (Universities list, Roadmap's exam filter, Applications' sort/priority controls) either uses an explicit "Apply" submit button or is a pure client-side filter over already-loaded data — no live network-per-keystroke pattern exists today.
8. **The Notifications bell duplicates the Notifications page's own fetch** whenever both are mounted (the bell lives in the persistent app-shell header), and its unread badge is derived from a client-side array slice (`DROPDOWN_ITEM_LIMIT=8`) instead of the paginated envelope's real `count` — so unread counts above 8 under-report and the "9+" badge state is unreachable. There is no dedicated unread-count endpoint on the backend.
9. **Essay AI scoring is fully compliant**: confirmed no AI call on the essay list, no per-card AI call, and the only AI-compute endpoint (`POST /score/`) fires exclusively from an explicit button click with a reentrancy guard. Recommendations/Strategy pages are also confirmed to reuse cached server-side data rather than re-triggering AI compute.
10. Several screens redundantly refetch a whole list/plan after a single-item mutation, because the mutation response doesn't include enough data to patch local state (`handleAddSuggestion` in Roadmap/Applications/Essays; `handleMarkAllRead` in Notifications).

## Page-by-page findings

### Dashboard (`/dashboard`)

13 concurrent requests fire from one `Promise.allSettled` batch in `screens/dashboard/index.tsx`, plus `AnalyticsWidget` as a 14th independent connection.

| Endpoint | Trigger | Duplicate? | Needed above fold? | Cacheable? | Current problem | Fix |
|---|---|---|---|---|---|---|
| `GET /api/profile/completion/` | mount | Yes — recomputed again by readiness and analytics endpoints (server-side) | Yes — hero step + Profile card | Yes, until profile save | Blank `—` until all 13 calls settle | Share via one client cache/hook across Dashboard+Profile; stop recomputing server-side |
| `GET /api/profile/me/` | mount | Cross-page — Profile fetches the same endpoint independently | Partial | Yes, until save | No skeleton, no abort | Shared cache |
| `GET /api/events/my-registrations/` | mount | No | Partial (hero step only) | Yes, until (de)registration | No skeleton | Defer detail cards below the count |
| `GET /api/profile/readiness/` | mount | Yes — internally recomputes profile completion again | No — only feeds below-fold Gaps/Readiness cards | Yes | Fetched eagerly for below-fold content | Lazy-load on scroll-into-view |
| `GET /api/roadmap/` | mount | No | No — 3rd section, likely below fold | Yes, invalidate on task mutation | No skeleton | Defer/skeleton |
| `POST /api/suggestions/generate/` | **mount (unconditional)** | No | No | N/A (write) | Fires on every visit; duplicates the unused `GET /api/suggestions/` read path; also wired to an explicit Refresh button | Use `GET /api/suggestions/` on mount; keep the POST only behind the explicit Refresh action |
| `GET /api/applications/` | mount | No | Partial | Yes, invalidate on Applications mutation | No skeleton | Shared cache |
| `GET /api/essays/` | mount | No (distinct resource from Profile's `/api/profile/essays/`) | No — count card only | Yes | Fetched though below fold | Defer |
| `GET /api/v1/universities/recommendations/` | mount | No | Partial (top-3 in hero) | Yes | Full-catalog fit computed though only top-3 shown | Cache; consider server-side cap |
| `GET /api/profile/assessment/latest/` | mount | **Yes — Profile fetches the identical endpoint independently** | Yes, Profile card | Very — confirmed pure cached-DB read, never triggers AI | Re-fetched over the network on both pages despite being server-cached | Shared client cache keyed by user |
| `GET /api/v1/recommendations/me/` | mount | No | No — below-fold gap panel | Very — deterministic, built from cached assessment only | Fetched eagerly for below-fold content | Defer |
| `GET /api/v1/strategy/me/` | mount | No | No — below-fold panel | Yes | Same as above | Defer |
| `GET /api/v1/analytics/me/` (via `AnalyticsWidget`) | mount of widget | Yes — 3rd redundant recompute of profile completion | No — last section before footer | Yes | Independent 13th connection instead of joining the batch | Lazy-mount on scroll-into-view |

Retry-on-partial-failure re-fires **all 13** calls, not just the ones that failed.

### Profile (`/profile`)

13 concurrent requests: 4 in `loadProfile`, 9 in `loadItems` (one per profile-item type), plus a separate exam-dates effect.

| Endpoint | Trigger | Duplicate? | Needed above fold? | Cacheable? | Current problem | Fix |
|---|---|---|---|---|---|---|
| `GET /api/profile/me/` | mount | Cross-page (Dashboard) | Yes — page can't render without it | Yes | Whole page blocked behind a blank `"profile.loading"` card until this **and** completion resolve; failure blanks the entire page | Real skeleton; don't gate the whole page on both calls |
| `GET /api/profile/completion/` | mount | Cross-page + triple-server-compute | Yes, hero card | Yes | Same page-blocking gate; **also re-fetched after every Save and every profile-item create/update/delete** (~12 extra hits in one edit session) | Derive client-side or return from the mutation response |
| `GET /api/profile/assessment/latest/` | mount | Cross-page duplicate of Dashboard | Partial | Very | Handled well (doesn't block page) but still a redundant round trip | Shared client cache |
| `GET /api/profile/{activities,honors,olympiads,sports,research-projects,essays,portfolio-projects,volunteering,recommenders}/` (9 calls) | mount | Not duplicates of each other, but an uncoordinated 9-way fan-out that could be one aggregate call | Partial (counts feed an overview card) | Yes | One shared `itemsLoading` flag; **failures are silently swallowed**, indistinguishable from "no items" | Lazy-load per-section on expand; surface failures instead of swallowing them |
| `GET /api/v1/exam-dates/?page_size=200` | mount (own effect) | No | No — deep in Tests section | Yes — official dates change rarely, good candidate for a long-TTL shared cache | Fetches up to 200 rows unconditionally for a below-fold form feature; has a `cancelled`-flag guard but not a real abort | Defer until Tests section is focused; ask backend to filter to upcoming dates |

### Universities list (`/universities`)

| Endpoint | Trigger | Duplicate? | Needed above fold? | Cacheable? | Current problem | Fix |
|---|---|---|---|---|---|---|
| `GET /api/v1/universities/` | mount + Apply-filters submit | No | Yes | No — reflects current filters/page | No AbortController; rapid pagination can let a stale response overwrite newer state | Add AbortController/request-id guard |
| `GET /api/v1/universities/filter-options/` | mount | No (distinct endpoint, but a 2nd concurrent request every mount) | No — filter panel defaults collapsed | Yes — reference data, already cached server-side for 600s | Refetched from scratch every mount, no client memory | Cache client-side or defer until filter panel opens |

Confirmed: **no per-row fit/AI call on the list** — `UniversityCard` reads only fields already in the single list response. Search/filter uses an explicit Apply button, no debounce needed.

### University detail (`/universities/[slug]`)

| Endpoint | Trigger | Duplicate? | Needed above fold? | Cacheable? | Current problem | Fix |
|---|---|---|---|---|---|---|
| `GET /api/v1/universities/{slug}/` | mount | No | Yes — gates the full page | Somewhat | Plain-text loading state, not a skeleton; no abort | Skeleton + AbortController |
| `GET /api/v1/universities/{slug}/fit/` | **mount (automatic)**, parallel with detail | No | Yes, sidebar | No — personalized | Fires automatically on every visit; correctly non-blocking today, but no cache/status split (this is what Phase 5 fixes) | Deterministic-first response + cached/explicit-refresh semantic fit (Phase 5) |
| 7 calls for the Requirements tab (profile, 5× profile-item types, essays) | mount (unconditional) | Not duplicates of each other, but **re-run in full for every university visited even though the Requirements tab isn't the default tab** | No — hidden unless the Requirements tab is opened | Yes — this is the student's own data, doesn't vary per university | Browsing 10 universities ⇒ 70 redundant requests for the same profile data | Defer until the Requirements tab is opened; hoist into a per-session cache |
| Roadmap/Applications/Suggestions (3 calls, linked to this university) | effect-dependency-change on the whole `university` object | **Refetch-loop risk**: `toggleShortlist` creates a new `university` object reference, re-firing all 3 on an unrelated shortlist click | Mixed | No, must stay current | Unrelated shortlist toggle causes 3 redundant network calls | Change dependency to `university?.id` |

### University compare (`/universities/compare`)

One batched `GET /api/v1/universities/compare/?ids=...` request — confirmed **good pattern**: no N per-university calls, no fit/AI data requested at all. Remaining gaps: no AbortController, plain-text loading blocks the whole page.

### Recommendations (`/recommendations`)

Single `GET /api/v1/universities/recommendations/` on mount. Confirmed it does **not** independently re-trigger profile-assessment — reuses whatever the backend already has cached. `shortlist`/`track` actions patch local state only, no full refetch. Gap: no AbortController.

### Strategy (`/strategy`)

Single `GET /api/v1/universities/strategy/` on mount — good, no extra calls made directly by this screen. Conceptually overlaps with Dashboard's and Recommendations' own server-side aggregation (expected, each page needs its own view of the same underlying data) but nothing is shared client-side. Gap: no AbortController.

### Roadmap (`/roadmap`)

| Endpoint | Trigger | Duplicate? | Notes |
|---|---|---|---|
| `GET /api/roadmap/` | mount | No | Full page replaced by skeleton until resolved; no unmount cancellation |
| `GET /api/suggestions/` | user-action (panel first expand) | No | Correctly deferred — good pattern |
| `complete`/`skip` task actions | user-action | No | Response merged into local `plan.tasks` — **no full refetch**, good pattern to replicate elsewhere |
| `handleAddSuggestion` → add + full `GET /api/roadmap/` again | user-action | Self-inflicted refetch | Backend only returns `{suggestion, roadmap_task_id}`; return the full task so it can be appended locally instead |

Filter/sort/bucket controls are pure client-side memos over already-loaded data — no debounce needed (one free-text field re-runs the memo chain per keystroke, harmless since there's no network call).

### Essays (`/essays`)

Confirmed **compliant with the AI hard rules**: list mount and each `EssayCard` render only from already-loaded list fields; `GET /score/latest/` (fired on essay selection) is a passive read of an already-computed score row, not new AI compute; the only AI-compute endpoint (`POST /score/`) fires exclusively from an explicit button click with a reentrancy guard.

| Endpoint | Trigger | Problem | Fix |
|---|---|---|---|
| `GET /api/essays/?page_size=100` | mount | Whole page (header, filters) blocked behind `LoadingNotice`, not scoped to the list | Scope loading state to the list region only |
| `generateEssaySuggestionsRequest()` then `getEssaysRequest()` again | user-action | Redundant refetch — the POST response already returns the essay list | Use the response directly |

Serializer note (backend): the essay list serializer includes full `draft_text` for every row — unnecessary for a list view (see Backend findings below).

### Application tracker (`/applications`)

| Endpoint | Trigger | Duplicate? | Problem | Fix |
|---|---|---|---|---|
| `GET /api/applications/?page&page_size=100` | mount + page change | No | First load fully blocks the page; later page changes correctly use an inline indicator already | Apply the same inline-indicator pattern to first load |
| Linked roadmap tasks | effect-dep on whole `selected` object | **Refetch-loop risk** — any patch to the open application creates a new `selected` reference, re-firing this fetch | Change dependency to `[selected?.id, selected?.university]` |
| Requirements / Recommendations / Documents panels (3 calls) | mount of sub-panel, on application select | Distinct endpoints, but an **uncoordinated 4-5-way fan-out** the instant an application is selected, with **zero cancellation guards** on 3 of the 4 | Add cancel guards (mirror the Timeline panel's existing `active`-flag pattern) |
| `handleAddSuggestion` → full refetch of linked tasks | user-action | Self-inflicted, same root cause as Roadmap's equivalent | Return full task from backend |

### Notifications (`/notifications` + header bell)

| Endpoint | Trigger | Duplicate? | Problem | Fix |
|---|---|---|---|---|
| `GET /api/v1/notifications/` (page) | mount + filter tab change | **Yes** — bell (persistent in app shell) and page both call the same endpoint independently whenever both are mounted | Share one fetch/store between bell and page |
| `GET /api/v1/notifications/?status=unread` (bell) | mount of app shell (once per session) + every dropdown re-open | Same as above | Bell's unread badge is derived from a client-side slice (`DROPDOWN_ITEM_LIMIT=8`) instead of the paginated `count` field — undercounts above 8, "9+" branch unreachable | Add a dedicated `GET /notifications/unread-count/` endpoint (does not exist today — see Backend findings); read `count` for the badge |
| `GET /api/v1/notifications/preferences/` | mount | No | Below-fold panel fetched eagerly; failure silently swallowed, stuck on "loading" forever with no retry | Defer until visible; add retry |
| `handleMarkAllRead` → mutation then full refetch | user-action | Self-inflicted | Update local state directly instead of refetching |

No polling (`setInterval`) exists anywhere in the frontend.

### Events (`/events`, `/events/[slug]`, `/events/my`)

| Endpoint | Trigger | Problem | Fix |
|---|---|---|---|
| `GET /api/events/` (list) | mount + filter/page change | No AbortController | Add one |
| `GET /api/events/{slug}/` (detail) | mount | Duplicates data the list already fetched for this event; plain-text loading, no skeleton (list page has one) | Add skeleton; AbortController |
| `handleRegistration` → mutate then re-`GET` detail | user-action | Mutation response discarded, then a full second GET | Use the returned `EventRegistration`/nested `event` to patch state directly |
| `GET /api/events/my-registrations/` | mount + page/view-tab toggle | Toggling List↔Calendar view re-fetches from the server every time (calendar requests up to 200 rows) | Fetch once at a larger page size, derive both views client-side |

### Organizer dashboard (`/organizer/events/*`)

| Endpoint | Trigger | Problem | Fix |
|---|---|---|---|
| `GET /api/organizer/events/` | mount + page change | Plain-text loading despite a stat-tile + card grid | Add skeletons |
| `GET /api/organizer/events/analytics/` | mount + **every page change** (same `useCallback` dep as the list) | Redundant re-fetch of unchanged aggregate data on every pagination click | Split out of the page-scoped callback; load once on mount |
| Status-change action → full list + full analytics refetch | user-action | 1-row change triggers 2 full GETs | Patch the one event's status locally (mirror `AdminReportsScreen`) |
| Event categories (form) | mount of form | Near-static reference list re-fetched from scratch every time the form mounts | Cache client-side |
| Event detail (edit form) | mount | Duplicates data the list already held | Cache by slug |
| Form builder fields | mount of child, gated behind parent's loading gate | **Fetch waterfall** — 3 logically-independent GETs resolve in 2 sequential round trips because of the parent/child mount gate | Fire in a sibling effect keyed only on slug |
| Participants: event + participant list (2 calls) | mount + page change | Confirmed **not** N+1 — answers are embedded per row already | No skeleton, no AbortController |
| Participants: check-in action → full reload of both calls | user-action | 1-row mutation triggers a full 2-call reload | Patch the one participant locally |

### Admin dashboard (moderation, reports, organizers, analytics, feedback, event-moderation, university-import)

Confirmed: the current admin user is fetched exactly once (via `AuthProvider` at the app root) and shared correctly via context — no admin screen re-fetches it. No shared "university list dropdown" pattern exists to deduplicate.

| Endpoint | Trigger | Problem | Fix |
|---|---|---|---|
| `GET /api/admin/universities/review-queue/` | mount | **No pagination at all** — returns a flat, uncapped array; plain-text loading | Add pagination (mirror Admin Reports, which already paginates correctly) |
| `GET /api/admin/organizers/` | mount | Same — **no pagination**, flat array | Add pagination |
| `GET /api/admin/reports/` | mount + filter/page | Correctly paginated already; plain-text loading, no AbortController | Add skeleton |
| `GET /api/v1/admin/analytics/{summary,feature-usage,activity}/` (3 calls) | mount | `Promise.all` means **one failing call blanks all 3 sections** | Use `Promise.allSettled` |
| `GET /api/admin/feedback/` | mount + filter/page | Correctly paginated; plain-text loading | Add skeleton |
| `GET /api/admin/events/pending/` | mount + page | Correctly paginated; plain-text loading | Add skeleton |
| Import job polling | user-action (dry-run/execute), polled every 1500ms up to 80× | **No unmount guard** — navigating away mid-import leaves the poll loop calling `setState` on an unmounted screen | Add a cancelled/mounted ref, break the loop on unmount |

Every Organizer and Admin screen uses a bare "loading..." text card instead of the `SkeletonCard`/`SkeletonRows` components that already exist and are used correctly by Events/My Events.

## Backend findings feeding Phases 4-7

- **`GET /api/v1/universities/`, `.../filter-options/`, `.../{slug}/`** are already well-optimized: `.only()` on the list serializer's field set, `select_related`/`prefetch_related` on detail, filter-options cached via `cache.get_or_set` (600s TTL).
- **`calculate_university_fit`** (the `.../fit/` action) is confirmed **100% deterministic today — no AI call in the request path.** It reads a cached `AIProfileAssessment` row (via `get_current_assessment_for_profile`), never calls Gemini directly. Phase 5 adds a genuinely new "semantic fit" AI layer on top rather than fixing an existing violation.
- **`calculate_university_recommendations`** already bulk-prefetches (`select_related`/`prefetch_related` for programs/rankings/scholarships/sources/verifications) and uses 2 bulk queries instead of per-candidate queries for shortlist/tracked status — good prior optimization.
- **No unread-notification-count endpoint exists.** `notification_service/urls.py` only exposes list/update/mark-all-read/preferences — nothing lightweight for the bell badge, forcing it to fetch (and slice) the full list.
- **Essay list serializer includes full `draft_text`** for every row (no lighter list-only serializer exists, unlike University's `UniversityListSerializer` vs `UniversitySerializer` split).
- **`MyAnalyticsView` and `AdminAnalyticsSummaryView`/`AdminAnalyticsFeatureUsageView`/`AdminAnalyticsActivityView`** recompute all aggregates from scratch on every request with no caching.
- **No `CACHES` setting is configured** — Django defaults to per-process `LocMemCache`. Safe (no cross-user leak risk), but not shared across workers; acceptable for the TTL-based caching this task adds.
- **AI call logging is already a well-established, consistent convention** (profile assessment, essay scoring): a structured `"AI call ai_task_type=... provider=... model=... status=... cache_hit=... duration_ms=..."` line, logged via each feature's own timed wrapper, with sanitized fields only (IDs/counts/enums, never raw text). Phase 6 extracts this into one shared `log_ai_call()` helper (`services/ai_gateway_service/logging.py`) and adds a third caller for semantic fit, without changing the existing log content.
- **Both existing AI features (profile assessment, essay scoring) are already fully compliant** with the Phase 6 hard rules: gated behind explicit user action, strict JSON schema, retry-once-then-deterministic-fallback, daily/quota rate limits, no raw profile/essay text in logs.
