# UniWay Architecture and Trust Boundaries (Audit 014)

## Audit snapshot

- Repository state: `main` at `65c0175`; `origin/main` matched and the working tree was clean when the audit began.
- Frontend: Next.js 15 App Router, React 19, TypeScript, Tailwind CSS, and client-side Feature-Sliced Design modules.
- Backend: Django 5.2, Django REST Framework 3.16, SimpleJWT, django-filter, and psycopg.
- Persistent data: managed PostgreSQL through `DATABASE_URL`; local Docker Compose uses PostgreSQL 17.
- Production topology documented in the repository: Vercel frontend, Render backend, and managed PostgreSQL.
- This audit does not run the university importer, mutate university data, delete production data, or perform destructive/high-volume production testing.

## System context

| Zone | Component | Responsibility | Sensitive data handled |
| --- | --- | --- | --- |
| User device | Browser | Authentication UI, onboarding, profile, applications, essays, events, admin/organizer surfaces | JWTs, profile data, essay drafts, contact data |
| Edge/frontend | Next.js application | Route rendering, localization, API orchestration, UI guards | Browser-visible API responses and public runtime configuration |
| Application | Django/DRF API | Authentication, authorization, validation, business rules, AI mediation, admin workflows | All account, admissions, essay, event, and audit data |
| Data | PostgreSQL | Authoritative application records | User records, profiles, essays, applications, events, import/audit records |
| Cache | Django cache API | Analytics summaries, filter options, recommendations, strategy, AI quotas/status | Per-user and aggregate cached response data |
| AI provider | Google Gemini | Explicit profile assessment, essay critique/scoring, and semantic-fit refresh | Minimized prompts derived from user/application data |
| Operations | Render/Vercel/GitHub Actions | Deployment, health checks, manually dispatched maintenance workflows | Deployment configuration and repository/environment secrets |

No explicit `CACHES` setting is present at this snapshot. Django therefore uses its process-local default cache unless production injects a different settings module. Cache-backed quotas and deduplication must not be treated as globally distributed controls until a shared cache is configured.

## Backend service inventory

| Service | Primary responsibility | Main API family |
| --- | --- | --- |
| `auth_service` | User model, registration, login, logout, JWT refresh/current user | `/api/auth/` |
| `user_profile_service` | Student profile, onboarding, readiness, structured profile CRUD | `/api/profile/`, `/api/v1/profiles/` |
| `university_service` | Catalog, detail, fit, shortlist, recommendations, import/moderation | `/api/v1/universities/`, `/api/admin/university-import/`, `/api/admin/universities/` |
| `profile_assessment_service` | Cached profile assessment, recommendations, strategy | `/api/profile/assessment/`, `/api/v1/profile-assessment/`, `/api/v1/recommendations/`, `/api/v1/strategy/` |
| `ai_gateway_service` | Backend-only Gemini/OpenRouter boundaries and provider error handling | `/api/v1/ai/` plus internal clients |
| `essay_service` | Private essay workspaces, explicit feedback/scoring, revision tasks | `/api/essays/` |
| `application_service` | Self-only application trackers, milestones, requirements, documents | `/api/applications/` |
| `roadmap_service` | Self-only deterministic roadmap plans/tasks | `/api/roadmap/`, `/api/v1/roadmaps/` |
| `suggestions_service` | Self-only generated suggestions and dismissal/add actions | `/api/suggestions/` |
| `event_service` | Event catalog, registration, tickets, organizer and moderation flows | `/api/events/`, `/api/organizer/`, `/api/admin/events/` |
| `notification_service` | Self-only notifications and preferences | `/api/v1/notifications/` |
| `activity_service` | Personal analytics and admin aggregate analytics | `/api/v1/analytics/`, `/api/v1/admin/analytics/` |
| `feedback_service` | Tester feedback, user reports, admin review | `/api/feedback/`, `/api/reports/`, `/api/admin/*` |
| `exam_content_service` | Exams, questions, and official exam-date records | `/api/v1/exams/`, `/api/v1/questions/`, `/api/v1/exam-dates/` |
| `subscription_service` | Plan/subscription and usage records | `/api/v1/subscriptions/` |
| `research_service` / `finance_literacy_service` | Service boundaries reserved for research/finance learning | No material public API at this snapshot |

## Frontend route inventory

Public entry routes are `/`, `/login`, and `/register`; the application gate mediates protected product routes. Protected student routes include `/onboarding`, `/dashboard`, `/profile`, `/universities`, `/universities/[slug]`, `/universities/compare`, `/recommendations`, `/strategy`, `/roadmap`, `/essays`, `/applications`, `/events`, `/events/[slug]`, `/events/my`, `/notifications`, `/activities`, `/exams`, `/research`, and `/finance`.

Role-sensitive routes include `/organizer/events/*` and `/admin/*` (analytics, event moderation, feedback, organizers, reports, university moderation/import). Frontend route guards are a usability layer only; backend permission classes, owner-scoped querysets, and serializer validation are the security boundary.

## Authentication and authorization layers

1. The browser stores access and refresh JWTs through `auth-storage.ts` and sends the access token as `Authorization: Bearer`.
2. A 401 may trigger one refresh request; rotating refresh tokens and blacklisting are enabled in SimpleJWT.
3. `AppGate` requires a backend-confirmed `/api/auth/me/` response before protected content mounts.
4. DRF defaults to `IsAuthenticated`; anonymous access is explicitly declared for registration, login, refresh, health, and feedback submission.
5. Role checks use `IsOrganizerOrAdmin`, `IsAdminRole`, and `IsAdminOrReadOnly`.
6. Self-only resources are primarily enforced by user-filtered querysets and server-assigned owner fields.
7. Organizer resources use organizer-scoped querysets; explicitly suspended/rejected organizers are blocked by `IsOrganizerOrAdmin`.

### Roles

| Actor | Intended authority |
| --- | --- |
| Anonymous | Health, registration/login/refresh, and bounded public feedback only |
| Student | Own profile, essays, applications, roadmap, suggestions, notifications, registrations, shortlist, and fit |
| Organizer | Student-safe access plus own draft/submitted events, own participants/tickets/exports |
| Admin/moderator | Moderation, aggregate analytics, organizer review, university import/review, Django admin where separately authorized |
| Superuser | Django administrative authority; also satisfies the application admin-role predicate |

## Data stores and high-value assets

- Credentials and identity: password hashes, email, role, active/staff/superuser state, JWT blacklist records.
- Student admissions profile: grades, exams, preferences, structured activities, volunteering, research, honors, recommenders, and contact fields.
- Essays: private draft text, feedback, AI score reports, and revision tasks.
- Application planning: target universities, intended programs, deadlines, documents, notes, and roadmap tasks.
- Events: organizer records, registration snapshots, custom answers, tickets, attendance, participation records, and moderation logs.
- University database: published records, source verification, system-only guidance/scoring, import jobs, audit rows, and manual-review data.
- AI records: minimized request context, cached assessments/fit, usage metadata, status, and provider diagnostics.
- Operational assets: database URL, Django/JWT signing key, AI provider keys, OAuth credentials (future), deployment credentials, and GitHub Actions secrets.

## External dependencies and calls

| Dependency | Direction | Data/control |
| --- | --- | --- |
| Managed PostgreSQL | Backend -> database | ORM reads/writes over `DATABASE_URL` |
| Google Gemini API | Backend -> provider | Explicit user-triggered or controlled assessment/essay/fit payloads; backend key only |
| OpenRouter | Backend -> provider | Configured placeholder/mentor boundary; no frontend provider calls |
| Vercel | Browser -> frontend | Static/server-rendered frontend delivery |
| Render | Frontend/browser -> backend | HTTPS API hosting and runtime logs |
| GitHub Actions | GitHub -> Render health / database workflow | Keepalive and manually dispatched university-import command |

No production email delivery, Telegram delivery, payment provider, or Google OAuth flow is implemented at the audit snapshot.

## Background and operational work

- `generate_notifications`: management command for notification generation.
- `import_universities_data` and `import_universities_xlsx`: privileged, out-of-band import commands.
- Admin import API: stores a temporary XLSX and starts an in-process worker unless inline mode is explicitly enabled. It is not a durable queue.
- GitHub keepalive workflow: low-volume health ping intended to reduce Render cold starts.
- GitHub university-import workflow: manual-only workflow with production database access. Its inputs are a privileged trust boundary and require strict shell-safe handling.
- Render startup behavior is documented as migrations/bootstrap followed by Gunicorn; repository Docker defaults must not be assumed to match the Render service command.

## Trust boundaries

| ID | Boundary | Untrusted input crossing | Primary controls | Audit focus |
| --- | --- | --- | --- | --- |
| TB-01 | Browser -> Next.js | Form fields, route/query state, stored auth state | React escaping, typed forms, route guards, timeouts | XSS, token storage, raw error leakage, open redirects |
| TB-02 | Browser/Next.js -> DRF | JWTs, JSON, multipart XLSX, query/filter parameters | DRF authentication, serializers, throttles, pagination | BOLA/IDOR, mass assignment, injection, payload/resource limits |
| TB-03 | DRF -> PostgreSQL | Validated domain writes and ORM queries | ORM, transactions, constraints, owner scoping | Race conditions, GET writes, N+1, missing constraints/indexes |
| TB-04 | DRF -> Gemini/OpenRouter | Minimized profile/essay/university context | Backend-only key, explicit calls, schema validation, timeout, quotas | Prompt injection, PII leakage, cost abuse, untrusted output |
| TB-05 | DRF -> temporary filesystem | Admin-uploaded XLSX and audit artifacts | Admin role, extension/size checks, temporary path handling | MIME/container validation, zip bombs, cleanup, worker lifecycle |
| TB-06 | Organizer -> participant data | Event forms, participant lists, ticket/check-in actions, CSV | Owner-scoped querysets, role permission, privacy projection | Cross-event IDOR, formula injection, replay/idempotency |
| TB-07 | Admin -> moderation/import | Moderation actions, upload, workflow inputs | Admin role, throttles, audit records | CSRF/session posture, shell/workflow injection, destructive misuse |
| TB-08 | GitHub Actions -> production DB | Manual workflow inputs and repository data | Repository permissions and secrets | Input interpolation, provenance, approval, auditability |
| TB-09 | Cache -> authenticated response | Per-user and aggregate cached objects | Namespaced keys and short TTLs | Cross-user leakage, process-local quotas, stale overwrite |
| TB-10 | Deployment proxy -> Django | Host/origin/protocol headers | allowlists, deploy guards, proxy SSL settings | host-header attacks, HTTPS detection, HSTS/cookie correctness |

## Principal data flows

### Password/JWT sign-in

`Browser -> /api/auth/login/ -> Django authentication -> JWT pair -> browser storage -> authenticated API calls`

At this snapshot the refresh token is JavaScript-readable in `localStorage`. This is an acknowledged high-impact design risk because any successful XSS can steal a seven-day refresh credential. The target architecture is a Secure, HttpOnly, SameSite refresh cookie with a short-lived in-memory access token and explicit CSRF protections for cookie-authenticated writes.

### University fit

`Browser explicit GET -> deterministic fit service -> PostgreSQL/cache -> response`

Ordinary list/detail/fit GET paths must not call AI. An explicit fit-refresh POST may call Gemini, validates structured output, stores a user/university-scoped cached result, and must preserve deterministic fit if the provider fails.

### Essay review

`Browser explicit review POST -> self-owned essay -> bounded prompt -> Gemini -> strict schema/content validation -> private score report`

Essay list/detail reads must not call AI. List serializers must omit draft text. AI output is untrusted and may critique but must not ghostwrite or return a full rewritten admissions essay.

### Event registration/export

`Student -> validated registration -> transactional event capacity/uniqueness -> private snapshot/ticket -> organizer-owner projection/export`

Exports cross from untrusted participant text into spreadsheet software and therefore require formula-injection escaping in addition to CSV quoting.

### University import

`Admin XLSX -> multipart validation -> temporary file -> deterministic parser/validation -> audit/manual review -> optional missing-only writes`

The importer is outside normal user workflows. This audit does not upload, dry-run, execute, or otherwise invoke it.

## Confirmed architecture-level gaps at audit start

These are starting observations, not final findings; severity and remediation status are tracked in `FULL_AUDIT_014.md`.

1. Refresh credentials are persisted in `localStorage`; cross-tab token lifecycle is not a strong session boundary.
2. JWT refresh lacks a dedicated endpoint throttle and requires an explicit inactive-user/replay review.
3. `CurrentUserSerializer` uses `get_or_create` for profile/subscription during representation, causing avoidable writes on a GET path.
4. Default cache-backed quotas are process-local unless production supplies a shared cache.
5. Next.js does not yet define a strict CSP, Permissions-Policy, or complete shared security-header set.
6. Production proxy SSL/HSTS/referrer-policy settings are not explicit in Django settings.
7. Participant CSV export needs explicit spreadsheet formula-injection neutralization.
8. The manually dispatched import workflow interpolates privileged user inputs into a shell script and needs shell-safe validation even though only trusted repository users can dispatch it.
9. The backend Dockerfile defaults to Django `runserver`; production container defaults should use Gunicorn and a health-aware deployment command.
10. No durable distributed job queue exists for admin import execution; daemon-thread work can be lost on restart.
11. Email verification/password reset, account deletion/export, and documented retention/incident-response controls remain incomplete.

## Audit operating rules

- Active attack simulations run only against local/test data.
- Production verification is low-volume, non-destructive, and never includes credential spraying, fuzzing, stress/load tests, guessed-ID enumeration, or provider-token disclosure.
- Reports contain secret variable names only, never values.
- Confirmed vulnerabilities are remediated before public disclosure where practical.
- No release recommendation is issued solely because automated scanners pass.
