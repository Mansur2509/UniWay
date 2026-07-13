# API Performance Profile 014

Updated: 2026-07-12.

## Method

Measurements were taken with Django's `APIClient`, `CaptureQueriesContext`, and
`perf_counter` against an isolated migrated SQLite database. The fixture had 12
published universities, 12 tracked applications, 12 essays, 10 events, 10
roadmap tasks, 10 notifications, and sanitized analytics rows. No production
load test, university import, provider call, or private user data was used.

Times below are local diagnostic samples, not production SLOs. Query and
payload regressions are the durable gates; Render/Supabase latency must be
measured separately with low-volume production telemetry. `Cold` means the
endpoint cache was cleared. `Warm` is the immediate second request.

## Results

| Endpoint | Cold queries | Warm queries | Local ms cold/warm | Payload | Cache | N+1 | AI | Result |
| --- | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| `GET /api/auth/me/` | 2 | 2 | 417 / 4 | 370 B | no | no | no | pass |
| `GET /api/profile/me/` | 5 | 5 | 6 / 5 | 2.0 KB | no | no | no | read-only pass |
| `GET /api/profile/completion/` | 5 | 5 | 8 / 5 | 705 B | no | no | no | read-only pass |
| `GET /api/v1/universities/` | 3 | 3 | 11 / 8 | 12.5 KB | DB/page | guarded | no | compact list pass |
| `GET /api/v1/universities/filter-options/` | 24 | 0 | 14 / 1 | 1.4 KB | shared TTL | no | no | cold aggregate, warm pass |
| `GET /api/v1/universities/{slug}/` | 15 | 8 | 29 / 64 | 2.5 KB | related caches | no | no | full detail pass |
| `GET /api/v1/universities/{slug}/fit/` | 16 | 16 | 27 / 19 | 10.2 KB | semantic read only | no | **no** | deterministic pass |
| `GET /api/v1/recommendations/me/` | 1 | 1 | 3 / 2 | 46 B | assessment lookup | no | no | safe missing-cache response |
| `GET /api/v1/strategy/me/` | 43 | 30 | 58 / 61 | 4.2 KB | 20 s university sub-plan | fixed | no | bounded; see note |
| `GET /api/roadmap/` | 2 | 2 | 10 / 10 | 7.0 KB | no | guarded | no | pass |
| `GET /api/roadmap/tasks/` | 2 | 2 | 10 / 9 | 6.8 KB | no | guarded | no | pass |
| `GET /api/applications/` | 6 | 6 | 14 / 13 | 11.6 KB | no | guarded | no | pass |
| `GET /api/essays/` | 4 | 4 | 15 / 19 | 6.7 KB | no | guarded | no | draft text excluded |
| `GET /api/essays/{id}/` | 3 | 3 | 10 / 7 | 619 B | no | no | no | self-only detail pass |
| `GET /api/events/` | 3 | 3 | 11 / 7 | 6.9 KB | no | fixed | no | pass |
| `GET /api/organizer/events/` | 4 | 4 | 12 / 9 | 7.9 KB | no | no | no | owner-scoped pass |
| `GET /api/v1/notifications/` | 2 | 2 | 6 / 3 | 2.7 KB | no | guarded | no | pass |
| `GET /api/v1/notifications/unread-count/` | 1 | 1 | 2 / 2 | 12 B | client short TTL | no | no | pass |
| `GET /api/v1/analytics/me/` | 8 | 8 | 11 / 7 | 227 B | aggregate | no | no | pass |
| `GET /api/admin/events/pending/` | 1 | 1 | 5 / 3 | 52 B | paginated | no | no | pass |
| `GET /api/admin/universities/review-queue/` | 1 | 1 | 4 / 3 | 52 B | paginated | no | no | pass |
| `GET /api/v1/admin/analytics/summary/` | 12 | 0 | 15 / 1 | 321 B | shared TTL | no | no | pass |

The first `auth/me` timing includes one-time Python/Django process warm-up. It
must not be read as steady-state endpoint latency.

## Fixed bottlenecks

### Strategy timeline N+1

Before remediation, 12 applications produced 78 queries. Each application
reloaded milestones, roadmap tasks, university verification/scholarship data,
essays, exam dates, and in one snapshot path university programs.

The strategy builder now:

- prefetches milestones, roadmap tasks, field verifications, scholarships, and
  application-university programs;
- loads the user's essays once and groups them by university;
- loads the next SAT/AP records once and reuses them across applications;
- reuses the existing short-TTL university-strategy cache.

After remediation, the same local fixture is bounded at 43 cold queries and 30
on an immediate warm request. A regression test compares one and eight tracked
applications and requires equal query counts. The remaining fixed cost is the
full profile snapshot and catalog recommendation calculation, not per-row I/O.

### Event registration-status N+1

The event serializer previously queried the current user's registration once
per event card. The list/detail querysets now prefetch the user's active
registration into a dedicated attribute; detail includes the ticket only when
the optional event-infrastructure tables are available. The 10-event local list
dropped from 12 to 3 queries. A regression test requires query-count stability
as event count grows.

### Other guards already present

- University cards use a compact list serializer, `.only(...)`, page-size caps,
  a payload ceiling regression, and no nested detail collections.
- Applications, roadmap tasks, notifications, analytics, and shortlist payloads
  have constant-query regression tests.
- Essay list uses a list-only serializer and never returns `draft_text`.
- Filter options and admin aggregates use bounded TTL caches.
- Ordinary list/detail/fit GETs do not call an AI provider.
- Profile/subscription representation no longer provisions rows on GET.

## Remaining performance risks

1. `strategy/me` remains intentionally expensive on a cold cache because the
   profile-snapshot hash covers structured admissions evidence and target
   context. A durable shared cache is required before multi-instance scaling.
2. Filter options use about 24 distinct aggregate queries on a cold miss. The
   TTL makes repeat cost negligible, but catalog-changing admin actions should
   invalidate it deliberately.
3. SQLite timings do not model Supabase network round trips. Production should
   emit redacted endpoint duration, query count, cache status, and response size
   histograms.
4. The repository still uses Django's process-local cache by default. AI quota
   enforcement and cache behavior across multiple workers require Redis or
   transactional database counters.
5. No high-volume load test was run. Capacity, connection-pool, and p95/p99
   behavior remain staging tasks.
