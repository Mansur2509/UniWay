# Abuse And Rate Limiting 014

Updated: 2026-07-12. Limits below are application-layer safeguards. Render,
Vercel, a CDN/WAF, and the database must also enforce platform-level traffic
and connection controls. Production must use a shared cache for globally
consistent limits across workers.

| Endpoint or family | Cost | Abuse risk | Scope/rate | User limit | IP limit | Fallback |
|---|---|---|---|---|---|---|
| login | password hash + DB read | credential stuffing | `auth_login` 10/hour | n/a before auth | yes | 429 + `Retry-After`; generic error |
| register | password validation + 4 writes | account flood | `auth_register` 5/hour | n/a | yes | 429; transaction rollback |
| token refresh | JWT verify + blacklist writes | token replay/flood | `auth_refresh` 30/hour | token subject | yes | 401/429; old token blacklisted |
| default anonymous API | low/medium | scraping/flood | `anon` 60/hour | n/a | yes | 429 |
| default authenticated API | low/medium | automation/flood | `user` 500/hour | yes | indirect | 429 |
| essay review/score | AI + DB writes | provider-cost abuse | `ai_essay_score` 30/hour plus monthly quota | yes | default throttle | cached/deterministic status, no endless retry |
| profile assessment refresh | AI + profile aggregation | provider-cost abuse | `ai` 20/day plus cooldown/hash | yes | default throttle | cached deterministic assessment |
| university fit GET | deterministic DB work | expensive repeated GET | default user limit | yes | default throttle | cached status; never calls AI |
| university fit refresh | AI + DB writes | provider-cost abuse | `ai_fit_refresh` 30/hour plus daily semantic quota | yes | yes | deterministic fit remains visible |
| suggestions/roadmap generation | multi-model aggregation + writes | repeated generation | default user limit; dedup keys | yes | default throttle | existing tasks/suggestions retained |
| event registration | transaction + notification/ticket | spam/duplicate registration | `event_registration` 30/hour | yes | default throttle | unique constraint/idempotent conflict |
| organizer submit/update | validation + moderation log | organizer spam | `event_submission` 60/hour | yes | default throttle | draft retained |
| admin moderation | state transitions + logs | accidental automation | `event_moderation` 120/hour | admin | default throttle | unchanged state on validation failure |
| public feedback | one write | anonymous spam | `feedback_submit` 10/hour | authenticated key where present | yes | 429 |
| authenticated reports | one write | report spam | `report_submit` 20/hour | yes | default throttle | 429 |
| university import API | upload/parse/background work | decompression/resource abuse | `university_import` 20/hour; 10 MB archive; one active job | admin | default throttle | reject archive/job; never auto-retry |
| lists/search/filter | DB queries | broad query/sort abuse | page size max 100; compact endpoints max 50 | yes | default throttle | bounded result or validation error |
| analytics ingestion | one bounded write | event flood/metadata abuse | default user limit; metadata allowlist and 200-char values | yes | default throttle | analytics failure never blocks core flow |
| notifications | indexed self queries | poll flood | default user limit; frontend request dedup/cache | yes | default throttle | stale count remains usable |

## Request and resource bounds

- DRF serializers enforce field lengths, enums, URL schemes, and bounded list
  items. Event forms cap fields, choices, and answer lengths.
- Pagination has explicit maximum page sizes. Expensive shortlist/suggestion
  surfaces use the tighter compact paginator.
- XLSX files are size checked before parse and ZIP metadata is checked for
  traversal, encryption, symlinks, macros, entry count, and expansion size.
- AI clients use finite network timeouts and finite output-token limits.
- CSV exports neutralize `=`, `+`, `-`, and `@` after leading whitespace.
- Production quotas are not sufficient with Django's process-local cache.
  Configure Redis (or another shared atomic cache) before horizontal scaling.

## Operational controls still required

1. Put Render behind platform rate limiting/WAF rules for login, registration,
   feedback, AI refresh, and upload routes.
2. Use a shared cache with atomic increments; alert on sustained 429 rates.
3. Cap Gunicorn workers/connections and set request timeouts.
4. Monitor slow-request and AI-call structured logs without request bodies.
5. Never use high-volume attack simulation against production.
