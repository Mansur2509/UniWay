# Backend service boundaries

Implemented Phase 0 foundations:

- `auth_service` — custom user and roles; JWT registration, login, refresh, logout, and current-user API
- `user_profile_service` — onboarding profile and preferences
- `subscription_service` — plans, usage limits, counters, and reset placeholder
- `university_service` — universities, requirements, scholarships, and source provenance
- `event_service` — moderated events, sources, locations, saves, and moderation logs
- `exam_content_service` — original-content exam catalog and demo question structure
- `ai_gateway_service` — authenticated, throttled provider boundary placeholder

Reserved service boundaries:

- `roadmap_service`
- `essay_service`
- `finance_literacy_service`
- `notification_service`
- `research_service`
- `activity_service`

Reserved modules remain intentionally empty until their Phase 1 task begins. This avoids speculative models while preserving ownership boundaries.
