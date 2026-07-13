# UniWay Security Threat Model (Audit 014)

## Scope and method

This threat model covers the Django/DRF API, Next.js browser client, PostgreSQL data store, Gemini AI boundary, Vercel/Render deployment, and privileged GitHub Actions workflows at repository snapshot `65c0175`.

The analysis uses STRIDE for security threats, LINDDUN for privacy threats, OWASP ASVS, OWASP Top 10, OWASP API Security Top 10, Django deployment guidance, and current OAuth/OIDC security principles. Findings require code or configuration evidence; a passing scanner is not treated as proof that the platform is secure.

Testing is defensive and authorized. Active simulations are local/test-only. Production verification is low-volume and non-destructive.

## Assets

| Asset | Security objective | Worst credible impact |
| --- | --- | --- |
| Account credentials and JWTs | Confidentiality, integrity, revocation | Account takeover or privilege escalation |
| Student profile/contact data | Self-only confidentiality and accurate updates | Youth/minor privacy breach or harmful admissions guidance |
| Essay drafts and feedback | Strict self-only confidentiality | Disclosure of private original work and personal narrative |
| Applications/roadmap/notifications | Self-only confidentiality and integrity | Cross-user planning disclosure or corrupted deadlines |
| Organizer participant data | Event-owner/admin confidentiality | Contact/custom-answer exposure |
| University source data | Integrity and provenance | Misleading admissions decisions at scale |
| Admin/import/moderation capabilities | Least privilege and auditability | Bulk data corruption, unauthorized publication, private-data access |
| AI provider credentials and prompts | Secret protection and data minimization | Provider abuse, cost loss, sensitive-data disclosure |
| Deployment/database secrets | Confidentiality and rotation | Full application/database compromise |

## Actors

- Anonymous internet user, including bots and credential-stuffing traffic.
- Authenticated student attempting accidental or malicious cross-user access.
- Organizer with access to only their own event and participant data.
- Suspended/rejected organizer attempting to reuse an existing token.
- Admin/moderator with powerful but bounded operational access.
- Compromised browser script or malicious extension operating with the user's session.
- Malicious content embedded in profile, essay, event, university, source, or AI input fields.
- Compromised third-party provider or dependency.
- Privileged repository user making an unsafe workflow-dispatch input.

## Entry points

- Auth endpoints: registration, login, refresh, logout, current user.
- Self-only CRUD APIs: profile items, essays, applications, roadmap, suggestions, notifications.
- Catalog/filter APIs: universities, exams, events, official exam dates.
- Explicit AI actions: profile assessment, essay review, semantic fit refresh.
- Organizer/admin endpoints: events, participants, exports, moderation, analytics, reports, university import.
- Multipart XLSX upload and command-line/workflow import paths.
- Next.js route/query state, local browser storage, and rendered API/AI text.
- Deployment environment, GitHub Actions inputs, and provider responses.

## Severity model

- **Critical**: direct auth bypass, unrestricted cross-user data access, exploitable command/SQL injection, stored XSS with session compromise, or live secret exposure.
- **High**: practical account/session theft, privileged workflow injection, sensitive export injection, broad authorization failure, or unrestricted expensive AI abuse.
- **Medium**: defense-in-depth or scoped abuse weakness requiring meaningful preconditions.
- **Low**: limited impact, operational hardening, or information disclosure with weak exploitability.
- **Informational**: verified control or future readiness item without a current vulnerability.

## Initial findings and remediation requirements

### AUTH-014-001 - JavaScript-readable refresh token

- Severity: **High**
- Final status: **fixed** - refresh token is HttpOnly-cookie-only for new sessions; access token is memory-only.
- Affected component: `frontend/src/shared/lib/auth-storage.ts`, login/register/refresh responses.
- Evidence: both access and seven-day refresh tokens are serialized to `localStorage`.
- Safe exploit scenario: if any stored/DOM XSS or compromised third-party script executes in the application origin, it can read and exfiltrate the refresh token, extending account access beyond the 15-minute access-token lifetime.
- Production risk: student profile, essay, application, and event data could be accessed until token expiry/revocation.
- Remediation: Secure, HttpOnly, SameSite refresh cookie; access token held in memory; rotation and blacklist preserved; no refresh token in JSON responses; origin/content-type protection for ambient-cookie refresh/logout.
- Verification: cookie-flag tests, response-leak test, rotation/replay tests, logout clear/revocation test, browser reload/cross-tab tests.

### AUTH-014-002 - Refresh lifecycle controls incomplete

- Severity: **High**
- Final status: **fixed** - rotation, blacklist logout, replay rejection, inactive-user checks, and origin validation are covered by tests.
- Affected component: `AuthTokenRefreshView`.
- Evidence: refresh inherits only the global anonymous throttle; no dedicated scope is declared, and no application-level active/suspended-user assertion is present before rotation.
- Safe exploit scenario: a stolen refresh token is repeatedly exercised or an inactive account attempts to mint a new access token.
- Production risk: avoidable brute-force/resource pressure and potentially confusing disabled-user lifecycle behavior.
- Remediation: dedicated refresh throttle, active-user validation before rotation, generic errors, and explicit replay/disabled-user tests.
- Verification: local 429 test, inactive-user refresh rejection, rotated-token replay rejection, expired/revoked token tests.

### AUTH-014-003 - Cross-tab session invalidation is incomplete

- Severity: **Medium**
- Final status: **fixed** - tabs receive a non-secret logout signal and clear in-memory access state.
- Affected component: browser auth storage/provider.
- Evidence: a custom same-document event is used; storage changes from another tab do not reliably clear in-memory tokens.
- Safe exploit scenario: a user logs out in one tab while another tab continues using a cached access token.
- Production risk: shared-device users may believe the full browser session ended when another tab remains authenticated.
- Remediation: memory-only access token, server cookie revocation, and BroadcastChannel/storage-event logout propagation.
- Verification: two-tab browser test and unit-level event behavior where available.

### API-014-001 - Participant CSV formula injection

- Severity: **High**
- Final status: **fixed** - exported cells neutralize spreadsheet formula prefixes and regression tests cover dangerous values.
- Affected component: organizer participant CSV export in `event_service/views.py`.
- Evidence: participant-controlled custom answers are written through `csv.writer` without neutralizing values beginning with `=`, `+`, `-`, or `@`.
- Safe exploit scenario: a participant submits a formula-like answer; an organizer opens the exported CSV in spreadsheet software and the formula executes in that local trust context.
- Production risk: spreadsheet-side data exfiltration or malicious links/actions depending on the spreadsheet client.
- Remediation: neutralize dangerous leading characters for every untrusted exported cell, keep CSV quoting, and add regression tests.
- Verification: export test covering all four prefixes and normal text.

### CICD-014-001 - Privileged workflow input interpolation

- Severity: **High**
- Final status: **fixed** - inputs are environment-passed, allowlisted/validated, quoted, and actions are SHA-pinned with least privilege.
- Affected component: `.github/workflows/university-import.yml`.
- Evidence: workflow-dispatch strings are interpolated directly into a Bash `run` block before shell parsing.
- Safe exploit scenario: a repository user with workflow-dispatch rights supplies shell metacharacters in a sheet/path/limit input, causing unintended commands to run in a job that holds `DATABASE_URL`.
- Production risk: database-secret exposure or unauthorized production database actions by a compromised privileged repository account.
- Remediation: pass inputs through environment variables, validate strict formats/allowlisted repository paths, and use Bash arrays without expression interpolation in scripts.
- Verification: static workflow test/inspection with metacharacter inputs rejected before Django is invoked.

### WEB-014-001 - Incomplete browser security headers

- Severity: **Medium**
- Final status: **mitigated** - CSP, frame denial, nosniff, referrer/permissions policy, HSTS, HTTPS/proxy settings, and private cache control are present; CSP still permits inline Next.js bootstrap code.
- Affected component: `frontend/next.config.ts` and Django deployment settings.
- Evidence: no explicit CSP or Permissions-Policy is defined; Django HSTS/referrer/proxy-SSL settings are not explicit.
- Safe exploit scenario: a future injection bug has fewer browser-level containment controls, or a page is delivered without consistent transport/referrer hardening.
- Production risk: larger blast radius for XSS/clickjacking/mixed deployment mistakes.
- Remediation: strict practical CSP, `frame-ancestors`, `nosniff`, referrer and permissions policies, HSTS/HTTPS/proxy settings gated for production.
- Verification: local header tests and low-volume production HEAD requests after deployment.

### PERF-014-001 - Avoidable writes on authentication/profile GET paths

- Severity: **Medium**
- Final status: **fixed** - current-user/profile GET paths use read helpers and regression coverage prevents provisioning writes.
- Affected component: current-user/profile serializers and `ensure_profile_records` read paths.
- Evidence: `get_or_create` provisions profile/subscription/preference records during representation and readiness GETs.
- Safe exploit scenario: repeated GETs for legacy/incomplete users cause write contention or race-driven duplicate attempts.
- Production risk: unnecessary database load and harder-to-reason-about read semantics.
- Remediation: provision records at account creation/data migration or an explicit repair command; keep GET paths read-only with safe representation fallback.
- Verification: query/write-count tests and legacy-user response test.

### ABUSE-014-001 - Process-local cache is used for security-adjacent quotas

- Severity: **Medium**
- Final status: **unresolved operational dependency** - database-backed AI quotas remain authoritative, but DRF/cache counters are process-local until a shared cache is configured.
- Affected component: Django cache-backed AI limits and cached responses.
- Evidence: no repository `CACHES` override; Django defaults to per-process local memory.
- Safe exploit scenario: requests are distributed across multiple workers/instances, each enforcing its own quota counter.
- Production risk: effective AI quota multiplied by worker count; cache invalidation inconsistency.
- Remediation: configure shared Redis-compatible cache in production or move hard quotas to transactional database counters; keep DRF endpoint throttles as defense in depth.
- Verification: multi-worker/staging test or database-backed quota tests.

### UPLOAD-014-001 - Admin XLSX validation is extension/size focused

- Severity: **Medium**
- Final status: **mitigated** - XLSX ZIP magic, entry count, uncompressed size, compression ratio, parser boundaries, and filename checks are enforced locally; durable worker isolation remains separate.
- Affected component: admin university import upload.
- Evidence: `.xlsx` extension and 10 MB size are enforced, while deep MIME/container/bomb checks are documented as absent.
- Safe exploit scenario: a compromised admin submits a malformed or highly compressed workbook that consumes worker CPU/memory.
- Production risk: application worker exhaustion or import-job crash; impact is reduced by admin-only access.
- Remediation: ZIP magic/container validation, entry-count/uncompressed-size/ratio limits, parser timeouts, and durable worker isolation.
- Verification: local malformed/zip-bomb-shaped fixture tests without expanding dangerous payloads.

### REL-014-001 - In-process daemon import worker is not durable

- Severity: **Medium**
- Final status: **accepted temporarily/unresolved** - heartbeat/stale failure handling limits damage, but the daemon worker is not a durable queue.
- Affected component: admin import job runner.
- Evidence: production request starts daemon-thread work rather than a durable external queue.
- Safe exploit scenario: Render restarts or recycles the process mid-job.
- Production risk: partial idempotent writes and stale job state requiring manual review.
- Remediation: durable queue/worker or explicit out-of-band command with lease/heartbeat/recovery semantics.
- Verification: local worker-interruption recovery test and stale-job transition test.

### PRIV-014-001 - Data lifecycle controls are incomplete

- Severity: **Medium**
- Final status: **unresolved product/privacy work** - self-only controls and minimization are improved, but complete export/deletion/retention operations are not implemented.
- Affected component: product/privacy operations.
- Evidence: account deletion/export, retention schedules, backup deletion expectations, and audit-log retention are listed as incomplete.
- Safe exploit scenario: a student cannot exercise deletion/export expectations, or private essay/contact records remain longer than necessary.
- Production risk: privacy, trust, and regulatory exposure, especially for youth users.
- Remediation: data inventory, retention schedule, authenticated export, verified deletion workflow, processor documentation, and minimization review.
- Verification: export completeness/self-only test, deletion cascade/anonymization test, log-content tests.

### AI-014-001 - Prompt-injection defense must be proven across every AI path

- Severity: **Medium**
- Final status: **mitigated** - every provider path is backend-only, explicit/cached, bounded, schema-validated, prompt-delimited, quota-controlled, and tested against injection/HTML/oversize/provider failure; model behavior is never treated as trusted.
- Affected component: profile assessment, essay review, semantic fit.
- Evidence: backend-only calls, explicit actions, schema validation, timeouts, and deterministic fallback exist; adversarial-content tests and a unified guardrail policy are incomplete in project security documentation.
- Safe exploit scenario: malicious instructions embedded in an essay/profile/university field attempt to override system constraints or induce unsupported admissions claims.
- Production risk: misleading output, ghostwriting, PII leakage, or cost abuse.
- Remediation: explicit untrusted delimiters, fixed capability policy, strict input/output limits, schema validation, HTML/script rejection/encoding, no-tool privilege, per-user quotas, and adversarial regression corpus.
- Verification: malicious prompt, invalid JSON, oversized output, script output, timeout/provider failure, cache isolation, and no-ghostwriting tests.

### DEP-014-001 - Supply-chain controls are not automated in CI

- Severity: **Medium**
- Final status: **mitigated** - direct Python versions are pinned, npm advisories are remediated, actions are SHA-pinned, and local secret/SCA/SAST scans are green; a mandatory hosted CI security gate is still pending.
- Affected component: dependency/build pipeline.
- Evidence: broad Python version ranges, mixed Bun/npm metadata, and no dependency/secret/SAST security workflow.
- Safe exploit scenario: a vulnerable/transitively compromised package or accidentally committed secret reaches `main` without an automated gate.
- Production risk: application compromise or credential exposure.
- Remediation: lock/reproducibility decision, scheduled and PR dependency audits, redacted secret scan, SAST, pinned CI actions, and triaged upgrades.
- Verification: local scans plus CI dry run with known-safe test fixtures.

## STRIDE summary by trust boundary

| Boundary | Spoofing | Tampering | Repudiation | Information disclosure | DoS | Elevation of privilege |
| --- | --- | --- | --- | --- | --- | --- |
| Browser -> API | stolen/replayed JWT | mass assignment | incomplete session/audit context | excessive serializer fields | oversized/high-rate requests | BOLA/BFLA |
| API -> database | forged owner identifiers | race/lost update | missing durable job audit | cross-user query/cache leak | expensive queries/locks | unsafe admin workflow |
| API -> AI | injected identity/instructions | model output manipulation | incomplete provider audit | prompt/PII leakage | repeated costly calls | model output influencing privileged action |
| Admin -> import/workflows | compromised admin/repo account | malicious workbook/input | insufficient approval trail | audit artifact/secret leak | parser/worker exhaustion | workflow shell execution |
| Frontend -> browser APIs | injected script | local auth state mutation | unclear cross-tab logout | token leakage | infinite retry/timers | route-only role guard misuse |

## LINDDUN privacy summary

| Category | Primary concern | Required control |
| --- | --- | --- |
| Linkability | analytics/profile/essay events joined by user ID | purpose limitation and aggregate admin views |
| Identifiability | contact, recommender, essay, event-answer data | self/owner-only APIs and minimization |
| Non-repudiation | moderation/import logs may retain identity indefinitely | documented retention and scoped access |
| Detectability | account/report responses reveal whether a user exists | generic auth/reset errors and bounded registration handling |
| Disclosure | logs, AI prompts, CSV exports, caches | redaction, prompt minimization, export escaping, user-keyed caches |
| Unawareness | young users may not understand AI/analytics processing | plain-language privacy and AI notices |
| Non-compliance | deletion/export/retention remain incomplete | lifecycle implementation and processor records |

## Release blockers

The audit release gate remains closed if any of the following is confirmed and unresolved: authentication bypass, cross-user data access, active secret leak, SQL/command injection, stored XSS, unrestricted AI abuse, unprotected destructive endpoint, failed migration/test/build, or an unresolved Critical finding.
