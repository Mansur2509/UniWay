# Frontend Performance Profile 014

Updated: 2026-07-12.

## Production build result

The profile uses `next build` (Next.js 15.5.19), not the development server.
The optimized build compiled in 8.7 seconds, generated all 35 static pages,
type-checked successfully, and emitted no browser source maps.

The shared framework baseline is 103 kB First Load JS. Route totals after the
i18n split range from 167 kB to 193 kB.

## Largest fixed bottleneck: all locales in every route

Before this audit, the root i18n provider statically imported all four
dictionaries. Their source files total roughly 780 kB, so every authenticated
route paid for English, Russian, Uzbek Latin, and Uzbek Cyrillic even though one
locale was active.

The provider now ships English as the safe initial dictionary and dynamically
loads only the requested non-English locale. It keeps the last complete
dictionary active during the async switch, so users do not see raw keys or a
mixed partially loaded dictionary. Failed locale chunks fall back to English.

Measured build impact:

| Route | Before | After | Reduction |
| --- | ---: | ---: | ---: |
| `/dashboard` | 347 kB | 193 kB | 154 kB (44%) |
| `/applications` | 342 kB | 188 kB | 154 kB (45%) |
| `/profile` | 342 kB | 188 kB | 154 kB (45%) |
| `/universities` | 333 kB | 179 kB | 154 kB (46%) |
| `/universities/[slug]` | 340 kB | 186 kB | 154 kB (45%) |
| `/essays` | 335 kB | 181 kB | 154 kB (46%) |
| `/events` | 334 kB | 180 kB | 154 kB (46%) |
| `/roadmap` | 338 kB | 184 kB | 154 kB (46%) |
| `/login` | 327 kB | 173 kB | 154 kB (47%) |

## Route profile

| Route/group | Route JS | First Load JS | Initial data behavior | Duplicate-call control | Main residual cost |
| --- | ---: | ---: | --- | --- | --- |
| `/login`, `/register` | 2.47 kB | 173 kB | no protected data before action | auth request guard | shared auth/i18n shell |
| `/dashboard` | 9.16 kB | 193 kB | above-fold first; secondary widgets settle independently | global GET in-flight dedupe | broad command-center data |
| `/profile` | 14.1 kB | 188 kB | aggregate plus structured sections | profile short cache/dedupe | largest route component |
| `/onboarding` | 1.45 kB | 191 kB | profile and verified exam dates | shared request dedupe | reused profile/form modules |
| `/universities` | 6.02 kB | 179 kB | paginated list plus cached filter options | debounced filters and GET dedupe | filter controls |
| `/universities/[slug]` | 10.9 kB | 186 kB | detail and deterministic fit; AI only on explicit POST | fit refresh button lock | rich detail tabs |
| `/recommendations` | 7.86 kB | 175 kB | deterministic/cached data only | backend short TTL + GET dedupe | card/filter UI |
| `/strategy` | 4.53 kB | 172 kB | one strategy aggregate | backend bounded queries | timeline rendering |
| `/applications`, `/prospective-universities` | 143 B | 188 kB | shared canonical tracker screen | shared API/cache | application editor |
| `/essays` | 11 kB | 181 kB | list excludes drafts; detail loaded on selection; AI only on click | action state and server quota | editor/review panel |
| `/roadmap` | 9.95 kB | 184 kB | task list first; secondary suggestions on demand | GET dedupe | list/timeline modes |
| `/events` | 3.51 kB | 180 kB | paginated catalog | request dedupe | Leaflet loaded by map view path |
| `/events/[slug]` | 5 kB | 172 kB | one event detail | request dedupe | registration form/ticket state |
| `/exams` | 6.48 kB | 170 kB | profile plus verified-date catalogue in parallel | one combined load | AP planner controls |
| organizer routes | 3.37-3.57 kB | 176-180 kB | owner-scoped paginated data | request/action locks | form and participant tools |
| admin routes | 2.67-4.28 kB | 175-176 kB | paginated queues/aggregates | cached aggregates | moderation tables |

## Request and rendering safeguards

- Shared API reads have timeout, one controlled network retry, caller abort
  propagation, and in-flight GET deduplication keyed by URL and user session.
- Auth and route gates have explicit timeout/error/retry outcomes; no protected
  route is allowed to remain on an infinite session spinner.
- Dashboard secondary widgets do not blank the primary content on failure.
- University filter options and unread counts use bounded caches.
- Search/filter input is debounced where it would otherwise request per key.
- List endpoints are paginated and normalize DRF/array response shapes.
- AI fit/essay/profile assessment calls require an explicit POST action; render,
  list, and detail GETs do not invoke providers.
- The motion system uses 140/220/320 ms tokens, no layout-shifting scale, visible
  focus, and `prefers-reduced-motion` overrides.

## Remaining risks

1. Authenticated pages still share a substantial client shell. The next safe
   reduction is to move route-independent static layout back to server
   components and dynamically load genuinely heavy tools (map/editor) only when
   their view opens.
2. A non-English session downloads one locale chunk after hydration. This is a
   deliberate tradeoff for a much smaller universal bundle; the active complete
   dictionary remains visible during the switch.
3. Browser p75 LCP, INP, memory, and long-task data are not available from this
   local build. Add privacy-safe web-vitals telemetry before claiming a field
   performance SLO.
4. Route-level data timing still depends on Render cold starts and Supabase
   network latency. The frontend degrades with timeout/retry UI but cannot remove
   infrastructure spin-up time.
5. No heavy animation library was introduced. This preserves low-end-device
   behavior but means complex transitions remain intentionally simple.
