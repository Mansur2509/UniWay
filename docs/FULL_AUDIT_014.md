# UniWay Full Security, Performance, and Quality Audit 014

Audit date: 2026-07-13  
Audited base: `65c0175a69508d15c34b0ac857d97e9441c0a7b8` on `main`  
Remediation state: uncommitted audit worktree; no push or production mutation was authorized.

## 1. Executive summary

The audit found no confirmed unresolved Critical code vulnerability. High-risk session, CSV export, and privileged workflow issues were fixed locally. Authorization tests cover self-only, event-owner, and admin boundaries; public serializers use explicit allowlists; ordinary list/detail/fit GET requests do not call an AI provider; deterministic guidance remains available when AI is disabled.

The release gate is still **HOLD** for an operational High finding: historical git objects contain previously committed `DATABASE_URL` and `DJANGO_SECRET_KEY` material. Current-tree and production-bundle scans are clean, but removal from the current tree does not revoke credentials. The database credential and Django secret must be rotated in their providers before release approval.

The audit also leaves documented Medium operational work: a shared production cache, a durable import worker, complete privacy export/deletion/retention operations, mandatory CI security scans, and real Google-provider end-to-end verification after credentials are configured.

Detailed evidence is split across:

- `docs/ARCHITECTURE_AND_TRUST_BOUNDARIES_014.md`
- `docs/SECURITY_THREAT_MODEL_014.md`
- `docs/API_PERMISSION_MATRIX_014.md`
- `docs/ABUSE_AND_RATE_LIMITING_014.md`
- `docs/PRIVACY_DATA_FLOW_014.md`
- `docs/DEPENDENCY_AND_SECRET_AUDIT_014.md`
- `docs/API_PERFORMANCE_PROFILE_014.md`
- `docs/FRONTEND_PERFORMANCE_PROFILE_014.md`
- `docs/GOOGLE_OAUTH_SETUP_014.md`

All fixed entries below use fix commit `audit worktree (uncommitted)` because this task was explicitly not authorized to commit or push.

## 2. Critical findings

No Critical finding was confirmed. Local authorization, injection, secret, dependency, AI-abuse, migration, build, and browser checks did not prove the application universally secure; they establish the bounded evidence listed in this report.

## 3. High findings

| ID | Severity | Status | Evidence | Affected files/components | Fix commit | Verification |
| --- | --- | --- | --- | --- | --- | --- |
| AUTH-014-001 | High | Fixed | Refresh tokens were JavaScript-readable and persisted in browser storage. | `auth_service` cookie/views; `frontend/src/shared/lib/auth-storage.ts`; auth provider/client | Audit worktree | Cookie flags, response-leak, reload, logout, and rotation tests; browser hard refresh restored the session. |
| AUTH-014-002 | High | Fixed | Refresh lacked a dedicated throttle and explicit inactive/replay lifecycle coverage. | `backend/services/auth_service/views.py`, throttles, auth tests | Audit worktree | Refresh throttle, rotated-token replay, revoked/expired token, logout, and disabled-user tests. |
| API-014-001 | High | Fixed | Participant-controlled CSV cells could begin with `=`, `+`, `-`, or `@`. | `backend/services/event_service/views.py`, event export tests | Audit worktree | Export regression tests cover all dangerous prefixes and normal text. |
| CICD-014-001 | High | Fixed | Workflow-dispatch input was interpolated into a privileged shell block. | `.github/workflows/university-import.yml`, workflow guard tests | Audit worktree | Inputs are environment-passed, allowlisted, quoted, and actions are SHA-pinned. |
| DEP-014-002 | High | **Unresolved operational** | Historical git objects contain credential variable material even though current-tree scans are clean. Values are intentionally omitted. | Git history; Render/Supabase/Vercel operational configuration | None; provider action required | Rotate the database credential and `DJANGO_SECRET_KEY`, redeploy, invalidate old sessions, then run a redacted history scan and smoke test. |

## 4. Medium findings

| ID | Severity | Status | Evidence | Affected files/components | Fix commit | Verification |
| --- | --- | --- | --- | --- | --- | --- |
| AUTH-014-003 | Medium | Fixed | Logout did not reliably invalidate in-memory auth state in another tab. | `auth-storage.ts`, auth context | Audit worktree | Broadcast/storage logout signaling and server-side refresh revocation tests. |
| WEB-014-001 | Medium | Mitigated | Browser/deployment headers were incomplete. CSP still permits inline Next bootstrap/style behavior. | `frontend/next.config.ts`, `backend/config/settings.py`, middleware | Audit worktree | Header inspection; production-like `check --deploy` has only HSTS-preload warning. |
| PERF-014-001 | Medium | Fixed | Read paths provisioned related records with `get_or_create`. | profile/auth/subscription services and serializers | Audit worktree | Read-only GET and query/write regression tests. |
| ABUSE-014-001 | Medium | Unresolved operational | DRF/cache counters are process-local without a shared cache. Database AI quotas remain authoritative. | Django cache/throttle deployment configuration | None; infrastructure required | Configure Redis-compatible shared cache and run multi-worker limit tests. |
| UPLOAD-014-001 | Medium | Mitigated | XLSX validation initially relied mainly on extension and file size. | university import upload/parser guards | Audit worktree | ZIP magic, entry count, uncompressed size, compression ratio, filename, and malformed-container tests. |
| REL-014-001 | Medium | Accepted temporarily | The admin importer still uses an in-process daemon worker. | university import job runner | Existing heartbeat work plus audit guards | Stale heartbeat/failure and idempotent partial-write tests; durable queue remains required. |
| PRIV-014-001 | Medium | Unresolved product/privacy | Complete account export, deletion, retention, and backup-erasure operations are absent. | Product/privacy operations | None | Required future self-only export and deletion/anonymization tests are documented. |
| AI-014-001 | Medium | Mitigated | User/stored content can attempt prompt injection or invalid model output. | AI gateway, essay/profile/semantic-fit clients and schemas | Audit worktree | Injection text, HTML/script, invalid JSON, oversize, timeout, cache isolation, quota, and provider-failure tests. |
| DEP-014-001 | Medium | Mitigated | Security scans are local and not a mandatory PR/release gate. | Dependencies and GitHub Actions | Audit worktree | Local SCA/SAST/secret scans are green; mandatory hosted CI remains pending. |
| UX-014-001 | Medium | Fixed | Public events without optional location/source records crashed `/events`. | event entity types, map/card/detail UI | Audit worktree | Production-build browser QA loads list/detail with null location/source and no new console error. |
| UX-014-002 | Medium | Fixed | Compact language select retained desktop width and clipped the shared mobile header by 7 px at 375 px. | `frontend/src/shared/ui/language-switcher.tsx` | Audit worktree | 375/390 px route matrix reports zero horizontal overflow. |

## 5. Low findings

| ID | Severity | Status | Evidence | Affected files/components | Fix commit | Verification |
| --- | --- | --- | --- | --- | --- | --- |
| WEB-014-002 | Low | Accepted | HSTS is enabled but preload is intentionally false. Preload is an operational domain-wide commitment. | Production deployment settings | None | `check --deploy` reports only `security.W021`. |
| SAST-014-001 | Low | Accepted | Full-tree Bandit reports 129 Low findings in test password fixtures; production files report zero. | Backend tests | None | Production-only Bandit scan: 0 Medium/High/Low findings. |
| TOOL-014-001 | Low | Unavailable | Semgrep and Gitleaks were not installed in this environment. | Audit tooling | None | Ruff, Bandit, detect-secrets, pip-audit, and npm audit were used; unavailable tools are not marked passed. |

## 6. Performance bottlenecks

- Authenticated route First Load JS fell from roughly 321-347 kB to 167-193 kB by loading only the selected locale and retaining English as the safe fallback.
- Strategy query growth was removed. The isolated fixture measured 78 queries before remediation and 43 cold/30 warm after remediation, with count constant as applications increased.
- Event list/detail registration status fell from 12 queries to 3 through current-user registration prefetching.
- Request deduplication, abort propagation, bounded timeouts, safe GET retry, and stale-data behavior remain in the shared API client.
- Remaining capacity risks are documented in the performance profiles: process-local cache, cold Render starts, no production APM, and no destructive/high-volume production load test.

## 7. Database/query findings

- Strategy prefetches milestones, roadmap tasks, field verifications, scholarships, university programs, and grouped essays instead of querying per application.
- Profile assessment target context prefetches application university programs.
- Event public querysets prefetch the current user's registration and conditionally select ticket data when schema-compatible.
- Paginated exam/question querysets now have deterministic ordering.
- Public GET paths avoid provisioning writes. AI refresh and import operations remain explicit writes.
- Query-count regression tests compare small and larger fixtures to detect N+1 growth.

## 8. Authentication findings

- Access tokens are memory-only; refresh tokens are Secure/HttpOnly cookies in production and are not returned in JSON.
- Refresh rotation, blacklist/revocation, origin/content-type validation, inactive-user checks, and replay rejection are covered.
- Login, register, refresh, and OAuth failure paths have endpoint-specific throttles and generic errors.
- Cross-tab logout sends only a non-secret invalidation signal.
- Privileged demo accounts are disabled/unusable; the student demo uses the canonical UniWay account only.
- Password reset is not implemented, so reset-specific enumeration/abuse controls are not applicable yet and must be designed before adding the flow.

## 9. Authorization/IDOR findings

- Self-only profile, essay, application, roadmap, suggestion, notification, and target-university APIs filter by authenticated owner.
- Organizer participant/export access is event-owner/admin scoped; suspended/rejected organizers are blocked.
- Admin serializers and routes use explicit role permissions; role/owner fields are not writable through ordinary payloads.
- Browser QA as student showed a localized role-denied state on admin import, admin event moderation, and organizer routes.
- The endpoint-by-endpoint evidence and tests are listed in `docs/API_PERMISSION_MATRIX_014.md`.

## 10. Injection/XSS/SSRF findings

- No user input is passed to a shell by application code. Privileged workflow inputs are validated before shell use.
- Django ORM and serializer validation remain the database-write boundary; no confirmed exploitable raw SQL path was found.
- CSV export neutralizes formula prefixes; XLSX inputs receive archive/parser limits and normalized filenames.
- No arbitrary URL-fetch feature was found in user-facing flows. Source URLs are data links, not server-side fetch instructions.
- React renders API/AI text as escaped text. AI schemas reject HTML/script-shaped output and out-of-range data.
- Public serializers do not expose import audit rows, manual-review data, admin notes, raw skipped cells, or AI prompt context.

## 11. DDoS/abuse findings

- Endpoint-specific IP/user throttles cover auth, AI, feedback/reporting, analytics, organizer submission, event registration, and import actions.
- Request-body, uploaded-file, nested-content, and page-size limits are explicit.
- AI calls use database-backed quotas/cooldowns and request timeouts; ordinary GETs never invoke the provider.
- Event registration, exam-roadmap task creation, notifications, usage events, and other repeatable actions use uniqueness or deduplication controls.
- Shared cache enforcement remains an operational requirement; no production flood/stress testing was performed.

## 12. Privacy findings

- Essay text, tokens, raw prompts, and sensitive profile fields are excluded from analytics and normal logs.
- AI prompts use bounded/minimized snapshots and successful usage metadata rather than raw essay logging.
- User caches are keyed by user/profile/input hashes; aggregate admin analytics stay aggregate.
- Contact answers and exports are owner/admin scoped.
- Retention schedule, account export, deletion/anonymization, backup behavior, and processor records remain unresolved and block a claim of mature privacy compliance.

## 13. AI findings

- Provider access is backend-only. Profile assessment, essay review, and semantic fit use explicit POST actions or controlled scheduled paths.
- University list/detail/fit GET, recommendations, and render paths use deterministic/cached data only.
- Inputs are delimited and bounded; outputs use strict schemas, range checks, text/HTML restrictions, and safe error mapping.
- Essay tooling critiques student-authored work and does not return a full rewritten essay.
- Provider failure preserves the deterministic fit or saved draft and exposes a localized, retryable state without raw provider errors.

## 14. Dependency findings

- Django was updated from 5.2.15 to 5.2.16 for `PYSEC-2026-2090`, `PYSEC-2026-2091`, and `PYSEC-2026-2092`.
- `pip-audit`: zero known vulnerabilities after upgrade.
- `npm audit`: zero known vulnerabilities.
- Production-bundle secret-pattern scan: zero matches.
- Current-tree detect-secrets scan: zero findings.
- GitHub Actions are SHA-pinned with reduced permissions. A mandatory CI scan remains pending.

## 15. Frontend UX/motion findings

- Shared motion tokens use restrained durations/easing, stable hover geometry, visible focus, and `prefers-reduced-motion` overrides.
- Locale dictionaries load dynamically; locale change is atomic with safe English fallback.
- Production browser QA covered login/demo session, dashboard, profile, universities/detail/fit, recommendations, strategy, roadmap, essays, applications/targets, exams, events/detail, notifications, and role-denied pages.
- Viewports 375, 390, 768, 1280, and 1440 px showed no horizontal overflow after the compact language-control fix.
- The events null-location crash and a shared 375 px header overflow were discovered by browser QA and fixed.
- Automated color-contrast and full keyboard-screen-reader certification were not available; semantic labels/focus behavior received code and spot-browser review only.

## 16. Google OAuth status

- Implemented backend Authorization Code flow with PKCE, state, nonce, single-use database attempts, redirect allowlist, verified email requirement, provider token verification, safe account linking, suspended-user blocking, and onboarding continuation.
- Frontend has localized loading/cancel/conflict/unavailable states and never receives the Google client secret.
- Ten focused tests cover valid linking/login and invalid state/provider/account cases.
- Actual provider E2E is **blocked by missing deployment credentials**, not marked passed. Required variable names and console configuration are in `docs/GOOGLE_OAUTH_SETUP_014.md`.

## 17. Prospective universities status

- The canonical target/application model stores intended program, round, intake year, priority, notes, archive state, fit tier, and source-aware official/personal deadline envelopes.
- Create/update/archive/restore actions are self-only and idempotent where applicable.
- The application tracker and `/prospective-universities` share the canonical data instead of creating a second divergent list.
- Missing official deadlines display as not published; personal estimates stay separately labeled and never become official data.

## 18. AP dates status

- Official exam dates store exam year, status, source title/URL, last verification, timezone, regular/late timing where published, and AP subject.
- The public upcoming feed excludes past/outdated rows unless explicitly requested.
- Student plans retain subject, official date, target, registration, progress/result, and notification intervals.
- Roadmap task creation accepts only a verified future official date and is idempotent.
- Only official 2026 College Board dates were available during verification. Exact 2027 dates were not invented; the UI reports that official dates are not yet published.

## 19. Tests and scan results

| Check | Result |
| --- | --- |
| `manage.py check` | Passed, 0 issues. |
| Production-like `manage.py check --deploy` | Passed with one accepted warning: HSTS preload is false. |
| `makemigrations --check --dry-run` | Passed, no changes. |
| `manage.py migrate --noinput` | Passed on isolated local SQLite during audit. |
| `manage.py test --parallel 4` | 895 tests passed on the audit worktree. |
| Ruff | Passed. |
| Bandit | Production code: 0 findings; full tree: 129 Low test-fixture password findings, 0 Medium/High. |
| `pip-audit` | Passed, 0 vulnerabilities. |
| `npm run check:i18n` | Passed, 2998 keys across 4 locales. |
| `npm run typecheck` | Passed. |
| `npm run lint` | Passed. |
| `npm run build` | Passed, 35 routes, Next.js 15.5.19. |
| `npm audit` | Passed, 0 vulnerabilities. |
| detect-secrets/current tree | Passed, 0 findings. |
| Production bundle secret pattern scan | Passed, 0 matches. |
| `git diff --check` | Passed; line-ending warnings only. |
| Semgrep/Gitleaks | Unavailable; not marked passed. |
| Browser QA | Passed locally on production build at 375/390/768/1280/1440 px after two runtime fixes. |
| Production attack/load test | Skipped by design; only low-volume non-destructive checks are permitted. |

## 20. Remaining risks

1. Rotate historical database/Django credentials, invalidate old sessions, and verify the redeploy.
2. Configure a shared production cache and test throttles across multiple workers.
3. Move import execution to a durable queue/worker with leases and recovery.
4. Implement authenticated data export, deletion/anonymization, retention schedules, and backup policy.
5. Add mandatory CI secret, SCA, SAST, migration, backend, and frontend gates.
6. Configure real Google OAuth credentials and run provider E2E without logging tokens.
7. Add production APM/query monitoring and a controlled staging load baseline.
8. Tighten CSP further when Next.js nonce/hash deployment behavior is implemented and tested.

## 21. Production release recommendation

**Recommendation: HOLD before production release/push.**

There is no unresolved Critical code finding and the local regression/build gate is green. Release approval remains withheld until the historical database credential and `DJANGO_SECRET_KEY` are rotated and the resulting deployment/session smoke test passes. Shared cache, privacy lifecycle, durable import-worker, and real OAuth E2E are required follow-up work; their accepted timing must be recorded before claiming production maturity.

Final safety confirmations:

- No university import, upload, dry-run, or execute action was performed.
- No university data or production user data was modified or deleted.
- No secret/token value was printed in this report.
- No destructive or high-volume production testing was performed.
- No admission probability/chance/odds feature was added.
- No AI provider call occurs on ordinary render/list/detail/fit GET.
- No commit or push was performed.
