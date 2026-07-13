# Google OAuth Setup 014

The code implements Google Authorization Code flow with PKCE, state, nonce,
backend token exchange, backend ID-token verification, a signed HttpOnly state
cookie, single-use database state, and fixed frontend redirects. Production
credentials are not present in the repository and were not available during
this audit.

## Google Cloud Console

1. Create or select the UniWay Google Cloud project.
2. Configure the OAuth consent screen. Request only `openid`, `email`, and
   `profile`. Add the real product/privacy/support links before publishing.
3. Create an OAuth 2.0 Client ID with application type **Web application**.
4. Add the exact production backend callback as an authorized redirect URI:
   `https://<backend-host>/api/auth/google/callback/`.
5. Add the controlled preview/local callback only for environments that need
   it. Never use a wildcard redirect URI.
6. Keep test users explicit while the consent screen is in testing mode.
7. Store the generated client secret only in the deployment secret store.

## Render backend variables

Required names:

- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`
- `GOOGLE_REDIRECT_URI`
- `GOOGLE_OAUTH_FRONTEND_URL`

Optional hardening/configuration names:

- `GOOGLE_OAUTH_STATE_COOKIE_NAME`
- `GOOGLE_OAUTH_ATTEMPT_MAX_AGE_SECONDS`

`GOOGLE_REDIRECT_URI` must exactly match the Google Cloud redirect URI.
`GOOGLE_OAUTH_FRONTEND_URL` should be the fixed login/callback-result page on
the production frontend. Its origin must already be present in
`CORS_ALLOWED_ORIGINS`; production requires HTTPS.

The normal production variables remain required, including a strong
`DJANGO_SECRET_KEY`, exact `ALLOWED_HOSTS`, exact `CORS_ALLOWED_ORIGINS`, exact
`CSRF_TRUSTED_ORIGINS`, and the production `DATABASE_URL`. Do not print their
values during setup or diagnosis.

## Vercel frontend

No Google client secret or ID token belongs in the frontend bundle. The button
navigates to the backend start endpoint. The existing public backend base URL
configuration must point to the same Render deployment that owns the callback.

## Account-linking rules

- A new verified Google email creates a normal student with an unusable local
  password and continues through mandatory onboarding.
- A verified email can link to an existing active password-based **student**.
- Organizer, admin, staff, and superuser accounts are never auto-linked by
  matching email.
- Inactive/suspended accounts are blocked.
- Google `sub`, not email, is the stable external identity after linking.
- Reused/expired state, wrong nonce, issuer/audience/expiry failures, missing
  email, and unverified email are rejected.

## Verification checklist

1. Start login and confirm the authorization request contains state, nonce, and
   an S256 PKCE challenge but no client secret.
2. Complete login for a new test student and verify onboarding is still
   required.
3. Complete login for an existing password student with the same verified
   email and verify one account remains.
4. Cancel at Google and verify a localized safe cancellation result.
5. Repeat the callback URL and verify state replay is rejected.
6. Verify suspended and privileged-account conflicts do not create sessions.
7. Inspect the production frontend bundle and logs for secrets/tokens; none
   should appear.
8. Log out and verify the refresh cookie is revoked/cleared.

Actual end-to-end Google provider login remains a deployment check until the
operator supplies the real Google Cloud credentials. Unit/integration tests use
mocked provider responses and never call Google with invented credentials.
