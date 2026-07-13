# Privacy Data Flow 014

Updated: 2026-07-12. UniWay processes student and youth data. This inventory
is an engineering control map, not a claim of legal compliance.

## Data inventory

| Data | Source | Storage/processor | Purpose | Exposure | Current minimization |
|---|---|---|---|---|---|
| Email, name, role, account state | user/auth | PostgreSQL, JWT claims | authentication and authorization | self; limited admin | password hashed; refresh token HttpOnly; no token logs |
| Birth date, location, school, GPA/curriculum | student | PostgreSQL | profile, readiness, deterministic fit | self; limited admin | nullable; no public profile route |
| Exams and AP plans/results | student/admin source | PostgreSQL | readiness and planning | self; verified reference dates public | missing dates remain missing |
| Activities, honors, research, portfolio, volunteering | student | PostgreSQL | readiness and fit evidence | self | owner-filtered collections |
| Recommender name/contact/status | student | PostgreSQL | application planning | self | never sent to public university APIs |
| Essay draft text | student | PostgreSQL; AI provider only on explicit review | editing and critique | self; explicit AI processor call | list serializer omits draft text; no analytics body |
| Applications, requirements, documents metadata | student | PostgreSQL | tracking | self | owner-filtered parent and children |
| University shortlist/fit cache | student + verified data | PostgreSQL/cache | planning | self | cache keys include user and university |
| Event registration answers/contact | student | PostgreSQL; organizer CSV export | event delivery | self and event owner/admin | organizer scoped to own event; CSV neutralized |
| Feedback/reports and optional contact | tester/user | PostgreSQL | support and moderation | admin | rate limited; reporter server-set |
| Analytics events | app | PostgreSQL | product usage aggregates | self summary/admin aggregate | bounded allowlisted metadata; no essay/profile body |
| Notifications/preferences | app/user | PostgreSQL | reminders | self | owner-filtered and deduplicated |
| AI prompts and outputs | server | Gemini in transit; selected validated result in PostgreSQL | assessment/fit/essay critique | self | IDs/counts in logs; schema validation; finite prompts |
| University import workbook/audit | admin | temporary upload/database job records | verified catalog administration | admin only | archive validation; no public raw/audit fields |

## Trust-boundary flows

1. Browser to Next.js: access token is held in memory. A one-time migration
   removes legacy localStorage tokens. Refresh credentials are unavailable to
   JavaScript.
2. Next.js to Django: HTTPS JSON requests use a short-lived Bearer access token.
   Refresh/logout use an HttpOnly, Secure, SameSite cookie and origin checks.
3. Django to PostgreSQL: ORM/serializer validation is used for writes. Self-only
   querysets prevent cross-user reads and writes.
4. Django to Gemini: only explicit AI actions send bounded task context. Provider
   credentials stay server-side. Ordinary list/detail/render GETs do not call AI.
5. Organizer/admin exports: event-owner/admin authorization occurs before data
   serialization. Untrusted spreadsheet cells are neutralized.

## Logging policy

- Log request method, route, status, duration, object IDs, task type, provider,
  model, cache status, and bounded error classification only.
- Never log access/refresh/OAuth tokens, passwords, API keys, full essays,
  recommender contact details, raw profile prompts, or uploaded workbook cells.
- Avoid query strings for routes that could contain user data; current request
  timing logs use `request.path`, not the full URL.
- Provider failures exposed to users remain generic. Detailed provider response
  bodies must not be returned to clients.

## Retention and user rights gaps

| Control | Status | Required action |
|---|---|---|
| Account/data export | unresolved | Add authenticated export job with identity confirmation and bounded archive lifetime |
| Account deletion | unresolved | Add re-authenticated deletion workflow, grace period, and cascade/anonymization map |
| Retention schedule | unresolved | Define per-table retention for essays, reports, analytics, AI outputs, logs, exports, and backups |
| Backup deletion propagation | unresolved | Document provider retention and maximum backup restoration window |
| Minor consent/age policy | unresolved | Product/legal decision required before broad youth launch |
| AI processor notice/consent | mitigated | Explicit action exists; add durable policy/consent text and processor disclosure |
| Support/admin access audit | partial | Moderation logs exist; add comprehensive sensitive-record access audit |

## Cache isolation requirements

- Every user-derived key includes stable `user_id`; fit keys also include
  `university_id` and profile hash/version.
- Public catalog/filter caches must never include `is_shortlisted`, user budget,
  fit, or profile-derived program matching.
- Authenticated/private responses use `Cache-Control: private, no-store` and vary
  on Authorization/Cookie.
- Use a shared cache only with explicit namespaces, TTLs, bounded values, and
  deletion on relevant profile/security changes.

## Incident priorities

1. Revoke refresh sessions and rotate affected secrets without logging values.
2. Preserve minimal audit evidence; do not copy private essay/profile content.
3. Determine affected users/objects through IDs and timestamps.
4. Rotate any previously exposed `DJANGO_SECRET_KEY`, database password, OAuth
   secret, AI provider key, or deployment token.
5. Document notification and deletion obligations with qualified legal counsel.
