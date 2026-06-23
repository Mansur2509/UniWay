# Deployment

## Local development

The supported local topology is:

- frontend on port 3000
- backend on port 8000
- PostgreSQL on port 5432

Use `compose.yaml` after installing Docker, or run services directly using the commands in the root README.

## Environment separation

Maintain separate development, preview, staging, and production settings. Production must use unique credentials, HTTPS, secure cookies, restricted hosts/origins, managed backups, and centralized monitoring.

## Hosting options

Candidate frontend platforms include Vercel, Netlify, and Cloudflare Pages. Candidate backend platforms include Render, Railway, and Fly.io. Candidate PostgreSQL providers include Supabase and Neon.

No provider is selected in Phase 0. Pricing, free tiers, region availability, sleep policies, storage, backup support, network egress, and data-processing terms change over time and must be verified manually before selection.

## Required production variables

Backend:

- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG=false`
- `DJANGO_ALLOWED_HOSTS`
- `DATABASE_URL`
- `CORS_ALLOWED_ORIGINS`
- `CSRF_TRUSTED_ORIGINS`
- `DJANGO_SECURE_COOKIES=true`
- `OPENROUTER_API_KEY`
- `OPENROUTER_BASE_URL`

Frontend:

- `NEXT_PUBLIC_API_BASE_URL`
- `NEXT_PUBLIC_AUTH_API_BASE_URL`
- `NEXT_PUBLIC_PROFILE_API_BASE_URL`
- `NEXT_PUBLIC_EVENTS_API_BASE_URL`
- `NEXT_PUBLIC_ORGANIZER_API_BASE_URL`
- `NEXT_PUBLIC_EVENT_MODERATION_API_BASE_URL`

Only values prefixed with `NEXT_PUBLIC_` are exposed to the browser. Provider secrets must never use that prefix.

## Pre-deploy checklist

1. Run frontend lint, type check, tests, and production build.
2. Run Django checks, migrations, and tests.
3. Run dependency and secret scans.
4. Validate CORS, CSRF, allowed hosts, cookie flags, and admin access.
5. Confirm database backup and recovery procedures.
6. Verify disclaimers, source links, and moderation behavior.
7. Smoke-test anonymous, student, organizer, and admin paths.
