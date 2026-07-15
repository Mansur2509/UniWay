# Mobile Architecture Decision Record (POST-V1-021 Phase 10)

**Status:** Decided. **Scope:** which client technology a future native
mobile app (Module G of `docs/POST_V1_PRODUCT_ROADMAP_021.md`) should be
built with. **Out of scope:** actually building the app -- this document
is the decision that gates that work, not the work itself. No mobile code
exists in this repository as of this document.

## Context

The product today is a single Next.js 15 / React 19 web app
(`frontend/`) talking to a Django REST API (`backend/`). It is responsive
(verified down to 375px in prior QA phases) but is not installable, has
no push notifications, and has no offline access. Module G's product
problem statement is exactly these three gaps. Before writing a single
line of mobile code, this document picks the technology that closes them.

### Constraints that shape the decision

- **One engineering team, no dedicated native-mobile specialist.** Every
  option below is scored partly on how much of the existing team's
  TypeScript/React/Django knowledge transfers.
- **All business logic must stay server-side.** Fit scoring, roadmap
  generation, essay AI scoring, and entitlement checks already live in
  the Django services and must not be reimplemented on-device in any
  option (this is a hard non-goal in Module G, not specific to one
  option).
- **The REST API is already the contract.** `frontend/src/shared/api/client.ts`
  (522 lines, a single `fetch`-based wrapper used by every screen) has no
  Next.js-specific or browser-only global in its request path -- `fetch`
  itself is available in React Native without a polyfill. This makes API
  reuse a property of *any* option, but code-level reuse of the wrapper
  itself is only possible with a JS/TS-based client.
- **No app-store account exists yet.** Apple Developer Program and Google
  Play Developer registration are business/legal steps (cost + a legal
  entity), not engineering decisions -- see "External dependencies" below.
- **Cost-sensitive.** This is a pre-revenue product (Module F ships no
  live payments yet); the option with the lowest sustained engineering
  and operational cost wins ties.

## Options considered

### Option 1: PWA (installable web app, same Next.js codebase)

Add a `manifest.json` and a service worker to the existing `frontend/`
app. The CSP in `frontend/next.config.ts` already declares
`manifest-src 'self'`, so the app is CSP-ready for this today even though
no manifest exists yet.

- **Code reuse:** Total -- zero new codebase, zero new language/framework.
- **Push notifications:** Web Push works on Android (via FCM) but is
  materially restricted on iOS Safari (iOS 16.4+ only, and only for
  home-screen-installed PWAs, with a history of Apple changing the rules).
  This is the option's biggest weakness given the product's push-driven
  use case (deadline reminders, essay AI completion).
- **Offline access:** Possible via service worker caching, but explicitly
  a non-goal for this product's first mobile version regardless of option.
- **App-store presence:** None -- a PWA is not distributed via the App
  Store or Play Store (a real limitation for discoverability and for
  users who only trust store-installed apps).
- **Engineering cost:** Lowest by a wide margin.
- **Operational cost:** Lowest -- no store review process, no signing
  certificates, ships on every existing Vercel deploy.

### Option 2: Expo / React Native

A new mobile codebase in TypeScript/React, sharing language and much of
the team's existing mental model (component structure, hooks, the
`fetch`-based API client pattern) without sharing the Next.js-specific
UI code directly (React Native does not render HTML/CSS; screens are
rewritten against native primitives).

- **Code reuse:** High at the *pattern* and *business-logic-shape* level
  (the API client's request/response/error-handling logic can be ported
  nearly as-is; i18n dictionaries in `frontend/src/shared/i18n/` are
  plain TS objects and can be imported directly), low at the *UI
  component* level (no shared JSX between Next.js DOM components and
  React Native's native components).
- **Push notifications:** Full native push on both iOS (APNs) and
  Android (FCM), abstracted behind Expo's push service -- the strongest
  option for this product's push-driven use case.
- **Offline access:** Available if pursued later; not required for v1.
  Still a non-goal for the first mobile release.
- **App-store presence:** Yes, once Apple/Google developer accounts exist.
  Expo also supports internal test distribution (Expo Go, internal
  builds) with no store account at all, so architecture work and QA can
  proceed before any business/legal step completes.
- **Engineering cost:** Medium -- a real second codebase, but the team's
  existing TypeScript fluency, component-thinking, and familiarity with
  the API contract transfer directly. No new language to learn, which is
  the deciding factor below compared with Flutter or fully native.
- **Operational cost:** Medium -- OTA updates for JS-only changes via
  Expo Updates reduce store-review friction for most releases; native
  binary changes (new native modules, OS-version bumps) still go through
  full store review.

### Option 3: Flutter

A new mobile codebase in Dart, with its own widget system, fully
independent of the existing TypeScript/React frontend.

- **Code reuse:** None at the language level -- Dart shares no syntax,
  tooling, or package ecosystem with the existing stack. i18n
  dictionaries, the API client, and every UI pattern would need a
  full rewrite in a language nobody on the team currently uses daily.
- **Push notifications:** Comparable to React Native (Firebase-based,
  mature).
- **Engineering cost:** Highest realistic option (excluding fully
  native) specifically because of the language switch -- Flutter's own
  technical quality is not in question, but it asks the team to
  maintain fluency in a second language/ecosystem with zero transfer
  from the day job.
- **Operational cost:** Comparable to React Native for store submission;
  no Expo-equivalent managed workflow, so more of the native build
  tooling is the team's own responsibility.

### Option 4: Fully native (separate Swift/iOS and Kotlin/Android codebases)

- **Code reuse:** None, and worse: two separate codebases to maintain in
  parallel, doubling ongoing cost for every feature.
- **Engineering cost:** Highest overall, requires two specialists (iOS
  and Android) the team does not currently have.
- Rejected without a detailed scorecard -- for a team this size building
  a thin client over an already-complete REST API, maintaining two
  fully native codebases has no offsetting benefit over Expo/React
  Native that would justify roughly double the ongoing engineering cost.

## Decision

**Build the mobile client with Expo / React Native.**

Reasoning, in priority order:

1. **Push notification quality is a product requirement, not a nice-to-have.**
   Deadline reminders and essay-AI-ready notifications are core to the
   product's value; the PWA option's iOS push restrictions make it the
   weakest option for exactly the feature this product needs most from
   "mobile." This rules out Option 1 as the *only* mobile investment,
   though it does not rule out doing both eventually (see "Revisit
   triggers").
2. **Team fluency transfers.** Every engineer who has worked on
   `frontend/` already knows TypeScript, React component patterns, and
   the shape of the API client. Flutter and fully-native both discard
   that investment. Expo does not.
3. **Expo's managed workflow minimizes new operational surface.** Expo
   Go and internal builds let the team build and QA the entire
   acceptance-criteria list in Module G (login, dashboard, universities,
   applications, deadlines, notifications, events against the real
   production API) *before* any Apple/Google developer account exists,
   so the business/legal blocker does not block engineering.
4. **OTA updates reduce the ongoing cost of the option's one real
   downside** (a second codebase to maintain) by letting most releases
   skip store review entirely.

## Consequences

- A new `mobile/` (or similarly named) Expo project will be created
  when Module G work actually begins -- not before, and not as part of
  this task (021 Phases 4-9 are backend/web-only; Module G is future
  work per the roadmap doc).
- The mobile client will **never** reimplement fit scoring, roadmap
  generation, essay scoring, or entitlement checks -- every one of those
  stays a call to the existing REST API. This is enforced by code review
  at build time, per Module G's own acceptance criteria.
- The mobile client will **not** attempt offline-first data in its first
  version, matching the web app's current network-required model.
- A `PushToken` model (already specified in Module G) will be added to
  `backend/services/` only when Module G build work starts, not as part
  of this decision document.

## External dependencies (business/legal, not engineering)

- **Apple Developer Program membership** (paid, requires a legal entity)
  -- required for TestFlight and App Store distribution.
- **Google Play Developer account** (paid, one-time) -- required for
  Play Store distribution (internal testing tracks are available sooner).
- **Push credentials**: Apple Push Notification service key/certificate,
  Firebase Cloud Messaging project -- both provisioned once the developer
  accounts above exist.
- **If any of the above is unavailable when Module G build work starts:**
  build and verify against Expo Go / internal test builds only, do not
  submit to either store, and report exactly which account/credential is
  the blocker -- do not claim a store release happened without one.

## Revisit triggers

This decision should be revisited, not treated as permanent, if any of
the following happen:

- The product later needs deep offline-first support or heavy native
  device integration (e.g., background location, complex native
  animations) that Expo's managed workflow cannot comfortably provide --
  at that point, "eject" to a bare React Native workflow first before
  considering a framework change, since that alone recovers most native
  capability without discarding the existing codebase.
- The team gains a dedicated Flutter or native mobile specialist and
  installs become a large enough fraction of usage to justify a rewrite.
- iOS Web Push restrictions are lifted enough that a PWA alone would
  satisfy the push-notification requirement -- in that case, a PWA could
  still be added *alongside* the Expo app cheaply (Option 1's cost is low
  enough that it is not mutually exclusive with Option 2), primarily for
  users who prefer not to install a store app at all.

## Next steps

See `docs/POST_V1_PRODUCT_ROADMAP_021.md`, Module G, for the concrete
data model, API additions (`PushToken`, push dispatch), acceptance
criteria, and deployment/rollback strategy that this decision unlocks.
Module G remains unbuilt as of this document; it depends on Modules A/B
being stable first, per the roadmap's own dependency ordering.
