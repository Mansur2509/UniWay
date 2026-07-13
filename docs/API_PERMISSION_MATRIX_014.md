# API Permission Matrix 014

Updated: 2026-07-12. `A` means anonymous, `S` student, `O` organizer,
and `D` staff/admin. A check mark means the role is allowed. A dash means
the request must be rejected. `Self` and `Own event` are mandatory queryset
boundaries, not frontend conventions.

| Endpoint | Method | A | S | O | D | Object rule | Verification |
|---|---|---:|---:|---:|---:|---|---|
| `/api/v1/health/` | GET | yes | yes | yes | yes | No user data | health smoke |
| `/api/auth/register/` | POST | yes | yes | yes | yes | Creates student only; role is server-set | `test_auth_api` |
| `/api/auth/login/` | POST | yes | yes | yes | yes | Generic credential error; active users only | `test_auth_api` |
| `/api/auth/token/refresh/` | POST | yes | yes | yes | yes | Valid rotated refresh cookie/body migration token only | `test_auth_api` |
| `/api/auth/logout/` | POST | no | yes | yes | yes | Refresh subject must equal access-token subject | `test_auth_api` |
| `/api/auth/me/` | GET/PATCH | no | yes | yes | yes | Self; role/email read-only | `test_auth_api` |
| `/api/profile/me/` | GET/PATCH | no | yes | yes | yes | Self | `test_profile_api` |
| `/api/profile/completion/` | GET | no | yes | yes | yes | Self | `test_profile_api` |
| `/api/profile/complete-onboarding/` | POST | no | yes | yes | yes | Self; server validates readiness | `test_profile_api` |
| `/api/profile/readiness/` | GET | no | yes | yes | yes | Self | `test_readiness` |
| `/api/profile/{activities,honors,olympiads,sports,research-projects,essays,portfolio-projects,volunteering,recommenders}/` | CRUD | no | yes | yes | yes | Queryset filtered by `user=request.user`; owner is server-set | `test_profile_items` |
| `/api/v1/profiles/me/` | GET/PATCH | no | yes | yes | yes | Self | `test_profile_api` |
| `/api/v1/subscriptions/me/` | GET | no | yes | yes | yes | Self action only; no generic CRUD route | subscription tests |
| `/api/events/` | GET | no | yes | yes | yes | Published/moderated events only | `test_event_registration` |
| `/api/events/{slug}/` | GET | no | yes | yes | yes | Published/moderated event only | `test_event_registration` |
| `/api/events/{slug}/register/` | POST | no | yes | yes | yes | Self registration; database uniqueness prevents duplicate | `test_event_registration` |
| `/api/events/{slug}/cancel-registration/` | POST | no | yes | yes | yes | Self registration only | `test_event_registration` |
| `/api/events/my-registrations/` | GET | no | yes | yes | yes | Self | `test_event_registration` |
| `/api/events/participation-records/` | GET | no | yes | yes | yes | Self | event infrastructure tests |
| `/api/events/my-notifications/` | GET | no | yes | yes | yes | Self | event infrastructure tests |
| `/api/organizer/event-categories/` | GET | no | no | yes | yes | Suspended/rejected organizer blocked | organizer moderation tests |
| `/api/organizer/events/` | GET/POST | no | no | yes | yes | Organizer sees/creates own events; admin may inspect | `test_organizer_workflow` |
| `/api/organizer/events/{slug}/` | GET/PATCH | no | no | yes | yes | Own event or admin | `test_organizer_workflow` |
| `/api/organizer/events/{slug}/form/` | GET/PUT | no | no | yes | yes | Own event or admin | event infrastructure tests |
| `/api/organizer/events/{slug}/submit/` | POST | no | no | yes | yes | Own event; moderation required before public | organizer tests |
| `/api/organizer/events/{slug}/registrations/` | GET | no | no | yes | yes | Own event participants or admin | event infrastructure tests |
| `/api/organizer/events/{slug}/registrations/export/` | GET | no | no | yes | yes | Own event; CSV cells neutralized | event infrastructure tests |
| `/api/organizer/events/{slug}/registrations/{id}/check-in/` | POST | no | no | yes | yes | Registration must belong to own event | event infrastructure tests |
| `/api/organizer/events/{slug}/tickets/verify/` | POST | no | no | yes | yes | Ticket must belong to own event | event infrastructure tests |
| `/api/organizer/events/{slug}/{archive,cancel}/` | POST | no | no | yes | yes | Own event or admin; confirmation in UI | organizer tests |
| `/api/admin/events/*` | GET/POST | no | no | no | yes | Admin moderation only | `test_organizer_workflow` |
| `/api/admin/organizers/*` | GET/PATCH | no | no | no | yes | Admin moderation only | organizer moderation tests |
| `/api/applications/` | CRUD | no | yes | yes | yes | Queryset filtered by self; owner server-set | `test_applications` |
| `/api/applications/{id}/{milestones,requirements,recommendations,documents}/` and child routers | CRUD | no | yes | yes | yes | Parent application and child must belong to self | `test_applications` |
| `/api/essays/` | CRUD | no | yes | yes | yes | Queryset filtered by self; owner server-set | `test_essays` |
| `/api/essays/{id}/{review,score,generate-suggestions}/` | POST | no | yes | yes | yes | Self essay; explicit action only | `test_essays` |
| `/api/essays/revision-tasks/` | CRUD | no | yes | yes | yes | Parent essay belongs to self | `test_essays` |
| `/api/roadmap/` and `/api/v1/roadmaps/me/` | GET | no | yes | yes | yes | Self | `test_roadmap` |
| `/api/roadmap/generate/` and `/api/v1/roadmaps/generate/` | POST | no | yes | yes | yes | Self; deterministic/idempotent generation | `test_roadmap` |
| `/api/roadmap/tasks/` and `/api/v1/roadmaps/tasks/` | CRUD/actions | no | yes | yes | yes | Queryset filtered by self | `test_roadmap` |
| `/api/suggestions/` | GET | no | yes | yes | yes | Self | `test_suggestions` |
| `/api/suggestions/generate/` | POST | no | yes | yes | yes | Self | `test_suggestions` |
| `/api/suggestions/{id}/{add-to-roadmap,dismiss}/` | POST | no | yes | yes | yes | Suggestion and linked objects must belong to self | `test_suggestions` |
| `/api/profile/assessment/{latest,run}/` | GET/POST | no | yes | yes | yes | Self; explicit run only | `test_profile_assessment` |
| `/api/v1/profile-assessment/{me,refresh}/` | GET/POST | no | yes | yes | yes | Self; explicit refresh only | `test_profile_assessment` |
| `/api/v1/recommendations/me/` | GET | no | yes | yes | yes | Self; deterministic/cached | recommendation tests |
| `/api/v1/strategy/me/` | GET | no | yes | yes | yes | Self; deterministic/cached | strategy tests |
| `/api/v1/ai/mentor/` | POST | no | yes | yes | yes | Self quota; no provider credential exposed | AI gateway tests |
| `/api/v1/universities/` and `/{slug}/` | GET | no | yes | yes | yes | Published records for non-admin; AI-only fields excluded | `test_universities` |
| `/api/v1/universities/{slug}/fit/` | GET | no | yes | yes | yes | Self profile plus published university; no AI call | fit tests |
| `/api/v1/universities/{slug}/fit/refresh/` | POST | no | yes | yes | yes | Self, explicit AI refresh, user/IP throttle | semantic fit tests |
| `/api/v1/universities/{filter-options,shortlist,shortlisted,compare,recommendations,strategy}/` | GET/POST/DELETE | no | yes | yes | yes | Self saved rows/profile; published universities only | university tests |
| `/api/v1/universities/` | POST/PATCH/DELETE | no | no | no | yes | Admin only | permission tests |
| `/api/admin/university-import/*` | POST/GET | no | no | no | yes | Admin only; uploaded job metadata only | `test_admin_import_api` |
| `/api/admin/universities/*` | GET/PATCH | no | no | no | yes | Admin moderation only | university moderation tests |
| `/api/v1/exams/` and `/api/v1/exam-dates/` | GET | yes | yes | yes | yes | Published reference data | exam tests |
| `/api/v1/exams/` and `/api/v1/exam-dates/` | write | no | no | no | yes | Admin only | exam tests |
| `/api/v1/questions/` | GET | no | yes | yes | yes | Published questions; answer key excluded | exam tests |
| `/api/v1/questions/{id}/answer/` | POST | no | yes | yes | yes | Server evaluates answer | exam tests |
| `/api/v1/notifications/` and `/unread-count/` | GET | no | yes | yes | yes | Queryset filtered by self | `test_notifications` |
| `/api/v1/notifications/{id}/`, `/mark-all-read/`, `/preferences/` | PATCH/POST/GET | no | yes | yes | yes | Self only | `test_notifications` |
| `/api/v1/analytics/me/` | GET | no | yes | yes | yes | Self aggregate only | `test_analytics` |
| `/api/v1/admin/analytics/*` | GET | no | no | no | yes | Admin aggregate only | `test_analytics` |
| `/api/feedback/` | POST | yes | yes | yes | yes | Public intake; reporter derived when authenticated | `test_feedback` |
| `/api/reports/` | POST | no | yes | yes | yes | Reporter server-set | `test_reports` |
| `/api/admin/{feedback,reports}/*` | GET/PATCH | no | no | no | yes | Admin only | feedback/report tests |

## Rules enforced across the matrix

- Serializer input cannot set `user`, `owner`, `organizer`, `role`, moderation
  state, fit tier, AI report owner, or import owner unless an admin-only route
  explicitly owns that field.
- Self-service viewsets filter before object lookup. Guessed IDs therefore
  produce `404`, not another user's object.
- Organizer event views resolve through an own-event queryset before resolving
  registrations, tickets, exports, or analytics.
- Admin/AI/import fields are excluded through explicit serializer allowlists.
- New endpoints must be added to this table with a positive and negative role
  test before release.
