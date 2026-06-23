# Security

## Security objectives

Protect student identity and essay content, prevent unauthorized writes and moderation actions, contain third-party AI access, preserve source integrity, and limit abuse.

## Threat model

| Asset | Example threat | Phase 0 control |
| --- | --- | --- |
| Accounts | credential theft, role escalation | Django password validation/hashing, student-only registration, read-only roles |
| Tokens | token theft, replay, refresh reuse | short access lifetime, refresh rotation, blacklist logout, isolated storage helper |
| API | scraping, brute force, abusive writes | authenticated-by-default API and DRF throttles |
| Events | spam, scams, unsafe links, registration abuse | publication gate, official source field, auth-only registration, scoped throttling |
| Essays | private text leakage | private ownership model, minimal logging, no public endpoint |
| Profile/contact data | unauthorized access, over-collection | self-only endpoints, optional contact fields, read-only role/email |
| AI gateway | key exposure, prompt injection, runaway spend | backend-only key, quotas, input validation, usage logs |
| University data | stale or fabricated claims | official source records, retrieval dates, public-data disclaimer |
| Exam content | copyright infringement | original-content flag and provenance workflow |
| Uploads | malware or oversized content | allowlist validation planned before upload endpoints |

## Baseline checklist

- [x] Environment-based secrets
- [x] No provider keys in frontend variables
- [x] CORS and CSRF allowlists
- [x] Secure cookie flags configurable by environment
- [x] DRF authenticated-by-default setting
- [x] Student/organizer/admin role model
- [x] API throttle defaults
- [x] JWT access/refresh flow with rotation and blacklist
- [x] Registration/login scoped throttles
- [x] Tests preventing role escalation through `/api/auth/me/`
- [x] Self-only profile API tests and role escalation protection
- [x] Organizer event moderation states
- [x] Duplicate registration constraint and transactional capacity/deadline checks
- [x] Private profile/contact snapshots for event registrations
- [x] Backend-only AI gateway boundary
- [x] Full-screen frontend auth gate before protected shell/content mounts
- [x] Authenticated catalog reads for events, universities, exams, and questions
- [x] Backend-offline state that does not impersonate logout
- [x] Backend-confirmed mandatory onboarding gate before the app shell mounts
- [x] Final onboarding completion validated by the profile API
- [ ] Email verification and password-reset flow
- [ ] Move browser refresh credentials from localStorage to Secure HttpOnly cookies
- [x] Organizer event ownership and moderation object-permission tests
- [ ] Upload MIME, extension, size, and malware checks
- [ ] AI prompt-injection test suite and content policy layer
- [ ] Audit log retention and privacy policy
- [ ] Dependency, container, and secret scanning in CI
- [ ] Backup, recovery, and incident response runbooks
- [ ] Data deletion and export workflow

## Implementation requirements

- Never rely on UI hiding for authorization.
- Validate on serializers and domain services, not only in forms.
- Never interpolate user input into raw SQL.
- Escape rendered user content and avoid unsafe HTML injection.
- Do not log authorization headers, API keys, full essays, or sensitive profile details.
- Do not expose birth date, phone, Telegram username, test scores, or profile preferences through public catalog APIs.
- Do not expose event registration snapshots through public event endpoints or to other students.
- Require admin permissions for moderation, content publication, and user management.

## Event registration anti-abuse

- Registration and cancellation require authentication and use the `event_registration` throttle scope.
- Event status, visibility, start time, deadline, duplicate active registration, and capacity are checked inside a database transaction.
- A partial unique constraint permits only one active registration per user/event.
- Cancelled registrations can be reactivated; this avoids duplicate active rows while retaining lifecycle history.
- Profile and contact data are copied as a snapshot so later profile edits do not silently alter the submitted registration.
- Capacity is an application/database transaction control, not a distributed reservation system. TICKETS-001 or a future high-scale task must define stronger inventory semantics before paid or high-demand launches.

## Organizer and moderation controls

- Student accounts cannot create or manage organizer events.
- Organizer querysets are owner-scoped; another organizer receives no event object or participant list.
- Organizer creation is always `draft`; only admin moderation can publish.
- Approve and reject actions accept only `pending_review` events and use row locks.
- A moderator cannot approve or reject an event they own.
- Rejection requires a bounded non-empty reason, and every lifecycle transition creates an audit record.
- Submission and moderation endpoints use dedicated scoped throttles.
- Participant responses are privacy projections. They omit phone, academic profile data, and raw JSON snapshots.
- UI role guards are not authorization controls; all enforcement remains in DRF permissions, object-scoped querysets, serializers, and domain services.
- Event URLs and descriptions remain untrusted content. The client does not inject organizer HTML and opens source links separately.

## Browser token storage

AUTH-001 stores access and refresh tokens in localStorage through `frontend/src/shared/lib/auth-storage.ts`. Keeping access centralized prevents token handling from spreading across features, but localStorage remains readable by JavaScript and therefore increases the impact of an XSS vulnerability.

Logout blacklists the refresh token and clears both browser tokens. A previously issued access token remains valid until its short 15-minute expiry, which is standard for stateless JWT access tokens.

The global frontend `AppGate` prevents protected shell/content flash and keeps all product routes behind a backend-confirmed session. This improves confidentiality and user clarity, but backend authentication and object permissions remain the security boundary.

Authenticated accounts also remain behind a backend-confirmed onboarding check. The client cannot mark itself complete through localStorage: it must satisfy required profile fields, record reviewed sections through self-only profile updates, and call the final completion endpoint. sessionStorage preserves unfinished form inputs only and is never authoritative.

Admissions assessment answers and unfinished onboarding drafts in sessionStorage are convenience state only. They cannot grant access, alter roles, or complete onboarding. Selected profile data becomes authoritative only after validation by the authenticated self-only API.

Readiness responses must not expose admission probabilities, guarantees, or invented university thresholds. University-specific comparison requires published requirement records and official source links; missing evidence is represented as `official_data_needed`.

The only anonymous API entry points are health checks, registration, login, and JWT refresh for a client already holding a refresh credential. Logout, current-user, profile, catalogs, registrations, organizer, moderation, subscription, exam-question, and AI endpoints require authentication or a stronger role.

Before production:

1. Move refresh tokens to Secure, HttpOnly, SameSite cookies.
2. Keep access tokens short-lived and preferably in memory.
3. Add a strict Content Security Policy and automated XSS checks.
4. Add email verification, password reset, device/session visibility, and suspicious-login controls.
- Add per-user and per-IP limits to expensive or abuse-prone endpoints.

## AI-specific controls

Before production AI calls:

1. Classify the requested capability.
2. Reject essay ghostwriting and prohibited financial or admission claims.
3. Separate trusted system instructions from untrusted user and retrieved text.
4. Apply plan quota checks before provider invocation.
5. Cap input/output size and timeout.
6. Log model, purpose, token/cost estimate, outcome, and user ID without full private content.
7. Attach the relevant disclaimer to the response.

## Reporting

Security-sensitive design changes must be recorded in `docs/DECISIONS.md`. Confirmed vulnerabilities should not be placed in public issue text before remediation.
