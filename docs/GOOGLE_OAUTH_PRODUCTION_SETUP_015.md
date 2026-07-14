# UniWay Google OAuth Production Setup 015

Status checked: 2026-07-13

## Current implementation

UniWay uses a backend-owned OAuth 2.0 Authorization Code flow. The browser is
sent to Django, Django creates state, nonce, and an S256 PKCE challenge, Google
returns the authorization code to Django, and Django exchanges and validates it
server-side. The frontend never receives a Google token, authorization code, or
client secret.

Production endpoints:

- Start: `https://eduverse-vvw2.onrender.com/api/auth/google/start/`
- Exact Google callback: `https://eduverse-vvw2.onrender.com/api/auth/google/callback/`
- Fixed frontend result page: `https://uni-way-beta.vercel.app/login`

The production start endpoint currently returns `302` to
`https://uni-way-beta.vercel.app/login?oauth=unavailable`. That proves the fixed
frontend return URL and its CORS allowlist are configured. It also means at
least one of these Render variables is absent or empty:

- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`
- `GOOGLE_REDIRECT_URI`

Only variable names are reported. Do not paste their values into chat, tickets,
logs, screenshots, or source control.

## Google Auth Platform configuration

1. Open [Google Cloud Console](https://console.cloud.google.com/) and select or
   create the production project.
2. Open **Google Auth Platform > Branding** (called **OAuth consent screen** in
   older console layouts).
3. Set the application name to **UniWay**. Add the real user-support email and
   developer contact email.
4. Select **External** audience unless access is intentionally restricted to one
   Google Workspace organization.
5. During initial verification, keep the app in **Testing** and add only named
   tester Google accounts. Users not on that list cannot complete sign-in.
6. Configure the minimum scopes used by this repository: `openid`, `email`, and
   `profile`. Do not add Drive, Calendar, or other Google API scopes.
7. Add the current application hosts where the console accepts them:
   `uni-way-beta.vercel.app` and `eduverse-vvw2.onrender.com`.
8. Vercel and Render use shared parent domains. Google may require Search
   Console ownership for public branding and may not accept ownership of the
   shared `vercel.app` or `onrender.com` parent domains. Before public release,
   attach and verify a UniWay-owned custom domain, then use it for the homepage,
   privacy policy, support links, and OAuth branding.
9. Open **Google Auth Platform > Clients**, select **Create Client**, choose
   **Web application**, and give it a production-specific name.
10. **Authorized JavaScript origins:** none are required by the current UniWay
    architecture because it does not use the Google JavaScript SDK or One Tap.
    Do not add an origin merely to silence an unrelated console hint.
11. **Authorized redirect URIs:** add exactly:

    `https://eduverse-vvw2.onrender.com/api/auth/google/callback/`

    Scheme, host, path, case, and trailing slash must match. Do not add a
    wildcard, frontend callback, query string, or shortened URL.
12. Create the client. Copy the client ID and client secret directly into the
    Render dashboard. Never download the secret into the repository.

Google requires an exact redirect-URI match for web-server clients and advises
keeping the client secret outside public source code:
[OAuth web-server applications](https://developers.google.com/identity/protocols/oauth2/web-server).
The server validates issuer, audience, expiration, nonce, and verified email as
described in Google's
[OpenID Connect guidance](https://developers.google.com/identity/openid-connect/openid-connect).

## Render environment

Set these on the production backend service:

| Variable | Required value/shape |
| --- | --- |
| `GOOGLE_CLIENT_ID` | Client ID from the Web application credential |
| `GOOGLE_CLIENT_SECRET` | Client secret from the same credential; secret value |
| `GOOGLE_REDIRECT_URI` | `https://eduverse-vvw2.onrender.com/api/auth/google/callback/` |
| `GOOGLE_OAUTH_FRONTEND_URL` | `https://uni-way-beta.vercel.app/login` |

Existing deployment variables must also contain:

- `DJANGO_ALLOWED_HOSTS=eduverse-vvw2.onrender.com`
- `CORS_ALLOWED_ORIGINS=https://uni-way-beta.vercel.app`
- `CSRF_TRUSTED_ORIGINS=https://uni-way-beta.vercel.app`
- `DJANGO_SECURE_COOKIES=true`
- `AUTH_REFRESH_COOKIE_SAMESITE=None`

`GOOGLE_OAUTH_ALLOWED_REDIRECTS` is not used. UniWay has no request-controlled
post-login redirect: `GOOGLE_OAUTH_FRONTEND_URL` is one fixed URL whose origin
must already exist in `CORS_ALLOWED_ORIGINS`. `FRONTEND_URL` is also not used by
the OAuth implementation.

Save the variables and redeploy the Render backend. A successful configuration
changes the start endpoint from a redirect to `?oauth=unavailable` into a
redirect to `https://accounts.google.com/o/oauth2/v2/auth`.

## Vercel environment

The existing server-owned flow does **not** require either
`NEXT_PUBLIC_GOOGLE_CLIENT_ID` or `NEXT_PUBLIC_APP_URL`. Do not expose the
Google client secret through any `NEXT_PUBLIC_*` variable.

The frontend needs its normal API configuration:

- `NEXT_PUBLIC_API_BASE_URL=https://eduverse-vvw2.onrender.com/api/v1`
- `NEXT_PUBLIC_AUTH_API_BASE_URL=https://eduverse-vvw2.onrender.com/api/auth`
  is optional because it is derived from `NEXT_PUBLIC_API_BASE_URL`.

Redeploy Vercel only when frontend code or these public API variables changed.

## Verification after redeploy

1. Open a private browser window on `https://uni-way-beta.vercel.app/login`.
2. Select **Continue with Google** once.
3. Confirm the browser goes to `accounts.google.com`, not another host.
4. Cancel once and confirm UniWay returns to login with a generic cancellation
   message and no session.
5. Sign in with an allowlisted test account.
6. Confirm a new Google user reaches mandatory onboarding.
7. Confirm an existing ordinary student with the same verified email is linked
   without creating a second user.
8. Confirm inactive users and privileged admin/organizer email collisions are
   blocked.
9. Log out and hard-refresh; the UniWay session must remain logged out.
10. Check browser Network and deployment logs without copying tokens. No Google
    token, authorization code, client secret, or raw provider response may
    appear in frontend responses, analytics, or application logs.

## Testing versus public access

- **Testing:** only accounts added under **Audience > Test users** can sign in.
- **In production:** Google accounts outside the test list can sign in, subject
  to Workspace and account policies. Publish the app from the Audience page.
- Public branding may require verified app domains, homepage, privacy policy,
  support contact, and brand verification. Sensitive or restricted scopes need
  additional verification; UniWay currently requests only identity scopes.

See Google's current guidance for
[audience and publishing status](https://support.google.com/cloud/answer/15549945)
and [OAuth app verification](https://support.google.com/cloud/answer/13463073).

## Troubleshooting

| Symptom | Safe check |
| --- | --- |
| `oauth=unavailable` | Confirm all four Render OAuth variables are non-empty, without printing values. |
| `redirect_uri_mismatch` | Compare the Google Client redirect URI and `GOOGLE_REDIRECT_URI` character-for-character, including trailing slash. |
| Google returns to `oauth=invalid` | Start a fresh flow; state is single-use and expires after ten minutes. Confirm client ID and callback belong to the same Google client. |
| Only some people can sign in | Add them as test users or publish the External app. |
| Cookies disappear after callback | Confirm HTTPS, `DJANGO_SECURE_COOKIES=true`, `AUTH_REFRESH_COOKIE_SAMESITE=None`, and exact CORS/CSRF origins. |
| Branding/domain verification fails | Use a UniWay-owned custom domain rather than attempting to verify shared hosting parent domains. |
