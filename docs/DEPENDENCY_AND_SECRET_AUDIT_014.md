# Dependency And Secret Audit 014

Updated: 2026-07-12. Secret values are intentionally omitted. Findings refer
only to variable names, paths, commit IDs, and remediation state.

## Executive result

| Area | Tool/check | Result | Status |
|---|---|---|---|
| Current repository secrets | detect-secrets 1.5.0, all files with build/vendor exclusions | 0 candidates | passed |
| Targeted Git history credentials | history regex scan, no values printed | credential-bearing PostgreSQL URLs and secret-key assignments found in old commits | high, unresolved rotation |
| Python dependencies | pip-audit 2.10.1 against `backend/requirements.txt` | 3 Django advisories found and fixed; final 0 | passed after remediation |
| Python SAST | Bandit 1.9.4 | production code 0 findings; full tree 129 Low test-password fixtures, 0 Medium/High | passed with test-fixture triage |
| Python style/static checks | Ruff | all backend files clean | passed |
| JavaScript dependencies | npm audit | initial 2 Moderate; 0 after PostCSS override | fixed |
| JavaScript tree | npm ls | valid tree; one untracked optional native helper in local `node_modules` only | informational |
| GitHub Actions | manual review | unsafe input interpolation fixed; actions SHA-pinned; permissions minimized | fixed |
| Container | manual review | non-root already; `runserver` replaced with Gunicorn | fixed |

## High finding: historical credentials

**ID:** SECRET-014-001  
**Severity:** High  
**Status:** unresolved operational rotation

History-only scanning found credential-bearing PostgreSQL URL material in:

- commit `e73767743a2cb393443ff81f81d00df0aa0d027b`
- commit `9f0722c5d4bc6533bfc5e4fb73f6a1525461bef4`
- historical paths `backend/.env.example`, `backend/config/settings.py`, and
  `compose.yaml`

It also found long `DJANGO_SECRET_KEY` assignments in historical
`backend/.env.example` revisions. Current tracked files and the current full
working tree have no detect-secrets candidates, but removal from HEAD does not
revoke a credential already present in Git history.

Required before release:

1. Rotate the production database password used by `DATABASE_URL`.
2. Rotate `DJANGO_SECRET_KEY`. Because SimpleJWT uses the Django signing key by
   default, expect this to invalidate existing access/refresh tokens.
3. Rotate related credentials if the exposed material was reused anywhere.
4. Confirm Render, GitHub Actions, local operator stores, and backup jobs use the
   new values. Never paste them into an issue, commit, CI log, or this document.
5. Consider a coordinated history rewrite only after rotation and a repository
   access review. Rotation is mandatory even if history is rewritten.

## JavaScript advisory remediation

Initial `npm audit` found the direct `next` tree affected through a nested
`postcss < 8.5.10` advisory (Moderate, XSS in CSS stringify output). npm's
automatic suggestion was an unsafe Next downgrade and was rejected.

Remediation:

- raised the direct PostCSS floor to `^8.5.10`;
- added an npm override so Next and Tailwind resolve the same safe PostCSS;
- regenerated `frontend/package-lock.json` with lifecycle scripts disabled;
- verified the resolved tree uses PostCSS `8.5.17`;
- reran `npm audit`: 0 vulnerabilities across 422 dependencies.

`npm outdated` shows minor updates inside the current ranges and major updates
for Next, ESLint, Tailwind, TypeScript, Lucide, and tailwind-merge. No major
upgrade was applied during this audit because each changes runtime/build
contracts and needs a dedicated regression cycle. Current installed versions
have a green advisory scan.

## Python dependency policy

Production direct dependencies are now exact-pinned in
`backend/requirements.txt` to the versions audited on 2026-07-12. This removes
the previous deploy-time drift caused by broad ranges. The Python audit found
no known advisories for the resolved dependency graph.

The final rerun first detected `PYSEC-2026-2090`, `PYSEC-2026-2091`, and
`PYSEC-2026-2092` against Django 5.2.15. Django was raised only to the patched
5.2.16 release in the same supported line, the local runtime was rebuilt, and
pip-audit then reported zero known vulnerabilities. No major framework upgrade
was mixed into the audit.

Remaining supply-chain improvement:

- generate and maintain a hash-locked transitive requirements file with a
  reviewed dependency bot workflow;
- rebuild monthly and immediately for Critical/High advisories;
- keep production and CI installation paths on the same lock artifact.

## Static analysis triage

Bandit initially reported:

- three dynamic SQL warnings in the read-only database diagnostic;
- three `urllib.request.urlopen` warnings in Gemini clients;
- four Low findings for a swallowed health exception and known demo/example
  strings.

Actions:

- database diagnostic counts now use Django ORM instead of constructed SQL;
- health-check database failures now emit a generic warning without connection
  details;
- Gemini B310 sites have narrow suppressions because the scheme and hostname
  are fixed to Google's HTTPS API and no user URL is accepted;
- known privileged organizer/admin demo credentials are disabled and receive
  unusable passwords; only the student sample account remains active;
- production rejects the development secret and wildcard host/origin config.

The full-tree Bandit run reports 129 Low-confidence hardcoded-password findings,
all in explicit test fixtures, plus no Medium or High findings. A second run
over production Python files (excluding `tests/`, `tests.py`, and migrations)
reports zero findings. The Google token endpoint has a narrow B105 suppression
because it is a fixed public OAuth URL, not a credential. Existing B310
suppressions remain local to fixed-provider `urlopen` calls and must be revisited
if those URLs ever become input.

## GitHub Actions and build chain

- `university-import.yml` dispatch inputs are passed through environment
  variables, validated, quoted, and constrained to the repository path.
- Workflow token permission is `contents: read`.
- `actions/checkout`, `actions/setup-python`, and `actions/upload-artifact` are
  pinned to full, signed-release commit SHAs.
- The keepalive workflow has no token permission and now fails visibly after a
  non-200 result beyond its cold-start allowance.
- Docker runs as a non-root `uniway` user and now starts Gunicorn rather than
  Django's development server.

Residual container risk: the Python base image is pinned to the Bookworm line,
not an immutable digest. Add digest pinning and scheduled image rebuilds once
the deployment platform's image-update process is documented.

## Release gate

Dependency/SAST status is green. Production release is still blocked until the
operator confirms rotation of `DATABASE_URL` credentials and
`DJANGO_SECRET_KEY`, and the final test/build/deploy checks pass.
